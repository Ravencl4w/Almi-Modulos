# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class TreasuryCollectionSheet(models.Model):
    """
    Modelo para gestionar hojas de cobranza por vendedor.
    Permite seguimiento de facturas asignadas y su estado de cobro.
    """
    _name = 'treasury.collection.sheet'
    _description = 'Hoja de Cobranza por Vendedor'
    _order = 'date_from desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    # ========== INFORMACIÓN BÁSICA ==========
    name = fields.Char(
        string='Número de Hoja',
        required=True,
        copy=False,
        readonly=True,
        default='Nuevo',
        tracking=True,
        help='Número identificador de la hoja de cobranza'
    )
    
    # ========== VENDEDOR ==========
    salesperson_id = fields.Many2one(
        'res.users',
        string='Vendedor',
        required=True,
        domain=[('share', '=', False)],
        tracking=True,
        help='Vendedor responsable de las cobranzas'
    )
    
    # ========== PERIODO ==========
    date_from = fields.Date(
        string='Fecha Inicio',
        required=True,
        default=fields.Date.today,
        tracking=True,
        help='Fecha de inicio del periodo'
    )
    
    date_to = fields.Date(
        string='Fecha Fin',
        required=True,
        tracking=True,
        help='Fecha de fin del periodo'
    )
    
    # ========== ESTADO ==========
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('active', 'Activa'),
        ('closed', 'Cerrada'),
    ], string='Estado',
       default='draft',
       required=True,
       tracking=True,
       help='Estado de la hoja de cobranza')
    
    # ========== FACTURAS ==========
    invoice_ids = fields.Many2many(
        'account.move',
        'collection_sheet_invoice_rel',
        'sheet_id',
        'invoice_id',
        string='Facturas Asignadas',
        domain="[('move_type', '=', 'out_invoice'), ('state', '=', 'posted'), ('invoice_user_id', '=', salesperson_id)]",
        help='Facturas asignadas al vendedor para cobrar'
    )
    
    # ========== TOTALES ==========
    total_assigned = fields.Monetary(
        string='Total Asignado',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
        help='Suma total de facturas asignadas'
    )
    
    total_collected = fields.Monetary(
        string='Total Cobrado',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
        help='Total efectivamente cobrado'
    )
    
    pending_amount = fields.Monetary(
        string='Pendiente de Cobro',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
        help='Saldo pendiente de cobro'
    )
    
    # ========== ESTADÍSTICAS ==========
    total_invoices = fields.Integer(
        string='Total Facturas',
        compute='_compute_stats',
        store=True,
        help='Número total de facturas'
    )
    
    paid_invoices = fields.Integer(
        string='Facturas Pagadas',
        compute='_compute_stats',
        store=True,
        help='Número de facturas completamente pagadas'
    )
    
    partial_invoices = fields.Integer(
        string='Facturas Pago Parcial',
        compute='_compute_stats',
        store=True,
        help='Número de facturas con pago parcial'
    )
    
    unpaid_invoices = fields.Integer(
        string='Facturas Sin Pagar',
        compute='_compute_stats',
        store=True,
        help='Número de facturas sin cobro'
    )
    
    collection_rate = fields.Float(
        string='Tasa de Cobranza (%)',
        compute='_compute_stats',
        store=True,
        help='Porcentaje de efectividad en la cobranza'
    )
    
    # ========== FECHAS ==========
    activation_date = fields.Date(
        string='Fecha de Activación',
        readonly=True,
        help='Fecha en que se activó la hoja'
    )
    
    closing_date = fields.Date(
        string='Fecha de Cierre',
        readonly=True,
        help='Fecha en que se cerró la hoja'
    )
    
    # ========== OTROS ==========
    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        default=lambda self: self.env.company.currency_id,
        required=True
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        default=lambda self: self.env.company,
        required=True
    )
    
    notes = fields.Text(
        string='Observaciones',
        help='Notas sobre la hoja de cobranza'
    )
    
    @api.model
    def create(self, vals):
        """Genera número secuencial al crear"""
        if vals.get('name', 'Nuevo') == 'Nuevo':
            vals['name'] = self.env['ir.sequence'].next_by_code('treasury.collection.sheet') or 'Nuevo'
        return super(TreasuryCollectionSheet, self).create(vals)
    
    @api.depends('invoice_ids', 'invoice_ids.amount_total', 'invoice_ids.amount_residual')
    def _compute_totals(self):
        """Calcula totales de la hoja"""
        for sheet in self:
            sheet.total_assigned = sum(sheet.invoice_ids.mapped('amount_total'))
            # Total cobrado = Total - Residual
            sheet.total_collected = sum([
                inv.amount_total - inv.amount_residual 
                for inv in sheet.invoice_ids
            ])
            sheet.pending_amount = sum(sheet.invoice_ids.mapped('amount_residual'))
    
    @api.depends('invoice_ids', 'invoice_ids.payment_state', 'total_assigned', 'total_collected')
    def _compute_stats(self):
        """Calcula estadísticas de la hoja"""
        for sheet in self:
            sheet.total_invoices = len(sheet.invoice_ids)
            sheet.paid_invoices = len(sheet.invoice_ids.filtered(
                lambda i: i.payment_state in ['paid', 'in_payment']
            ))
            sheet.partial_invoices = len(sheet.invoice_ids.filtered(
                lambda i: i.payment_state == 'partial'
            ))
            sheet.unpaid_invoices = len(sheet.invoice_ids.filtered(
                lambda i: i.payment_state in ['not_paid']
            ))
            
            # Calcular tasa de cobranza
            if sheet.total_assigned > 0:
                sheet.collection_rate = (sheet.total_collected / sheet.total_assigned) * 100
            else:
                sheet.collection_rate = 0.0
    
    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        """Valida que las fechas sean coherentes"""
        for sheet in self:
            if sheet.date_from and sheet.date_to and sheet.date_from > sheet.date_to:
                raise ValidationError(_(
                    'La fecha de inicio no puede ser mayor que la fecha de fin.'
                ))
    
    def action_activate(self):
        """Activa la hoja de cobranza"""
        for sheet in self:
            if sheet.state != 'draft':
                raise UserError(_(
                    'Solo se pueden activar hojas en estado Borrador.'
                ))
            
            if not sheet.invoice_ids:
                raise UserError(_(
                    'Debe asignar al menos una factura antes de activar la hoja.'
                ))
            
            sheet.write({
                'state': 'active',
                'activation_date': fields.Date.today(),
            })
            
            sheet.message_post(
                body=_('Hoja de cobranza activada con %s facturas por un total de %s') % (
                    sheet.total_invoices,
                    sheet.total_assigned
                )
            )
    
    def action_close(self):
        """Cierra la hoja de cobranza"""
        for sheet in self:
            if sheet.state != 'active':
                raise UserError(_(
                    'Solo se pueden cerrar hojas activas.'
                ))
            
            sheet.write({
                'state': 'closed',
                'closing_date': fields.Date.today(),
            })
            
            sheet.message_post(
                body=_('Hoja cerrada. Tasa de cobranza: %.2f%% (%s cobrado de %s)') % (
                    sheet.collection_rate,
                    sheet.total_collected,
                    sheet.total_assigned
                )
            )
    
    def action_reset_to_draft(self):
        """Reinicia la hoja a borrador"""
        for sheet in self:
            if sheet.state not in ['active']:
                raise UserError(_(
                    'Solo se pueden reiniciar hojas Activas.'
                ))
            
            sheet.write({
                'state': 'draft',
                'activation_date': False,
            })
            
            sheet.message_post(body=_('Hoja reiniciada a borrador'))
    
    def action_load_invoices(self):
        """Carga facturas del vendedor en el periodo"""
        self.ensure_one()
        
        if self.state != 'draft':
            raise UserError(_(
                'Solo se pueden cargar facturas en hojas en estado Borrador.'
            ))
        
        # Buscar facturas del vendedor en el periodo
        domain = [
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('invoice_user_id', '=', self.salesperson_id.id),
            ('invoice_date', '>=', self.date_from),
            ('invoice_date', '<=', self.date_to),
            ('payment_state', 'in', ['not_paid', 'partial']),
        ]
        
        invoices = self.env['account.move'].search(domain)
        
        if not invoices:
            raise UserError(_(
                'No se encontraron facturas pendientes para el vendedor %s en el periodo especificado.'
            ) % self.salesperson_id.name)
        
        # Agregar facturas
        self.invoice_ids = [(6, 0, invoices.ids)]
        
        self.message_post(
            body=_('Se cargaron %s facturas automáticamente') % len(invoices)
        )
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Facturas Cargadas'),
                'message': _('Se cargaron %s facturas por un total de %s') % (
                    len(invoices),
                    sum(invoices.mapped('amount_total'))
                ),
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_view_invoices(self):
        """Ver facturas de la hoja"""
        self.ensure_one()
        
        return {
            'name': _('Facturas de %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.invoice_ids.ids)],
            'context': {'create': False},
        }
    
    def action_view_paid_invoices(self):
        """Ver solo facturas pagadas"""
        self.ensure_one()
        paid_invoices = self.invoice_ids.filtered(
            lambda i: i.payment_state in ['paid', 'in_payment']
        )
        
        return {
            'name': _('Facturas Pagadas'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [('id', 'in', paid_invoices.ids)],
            'context': {'create': False},
        }
    
    def action_view_unpaid_invoices(self):
        """Ver solo facturas no pagadas"""
        self.ensure_one()
        unpaid_invoices = self.invoice_ids.filtered(
            lambda i: i.payment_state in ['not_paid', 'partial']
        )
        
        return {
            'name': _('Facturas Pendientes'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [('id', 'in', unpaid_invoices.ids)],
            'context': {'create': False},
        }
    
    def action_generate_report(self):
        """Genera reporte de cobranza"""
        self.ensure_one()
        # Aquí se podría implementar un reporte PDF personalizado
        return self.env.ref('treasury.action_report_collection_sheet').report_action(self)

