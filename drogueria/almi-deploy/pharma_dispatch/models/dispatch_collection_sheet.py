# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class DispatchCollectionSheet(models.Model):
    """
    Modelo para gestionar hojas de cobranzas.
    Registra todos los pagos recibidos por el conductor durante la ruta.
    El liquidador luego asigna estos pagos a las facturas correspondientes.
    """
    _name = 'dispatch.collection.sheet'
    _description = 'Hoja de Cobranzas'
    _order = 'create_date desc, id desc'
    
    # ========== INFORMACIÓN BÁSICA ==========
    name = fields.Char(
        string='Número de Hoja',
        required=True,
        copy=False,
        readonly=True,
        default='Nuevo',
        help='Número identificador de la hoja de cobranzas'
    )
    
    # ========== RELACIÓN CON LIQUIDACIÓN ==========
    settlement_id = fields.Many2one(
        'dispatch.settlement',
        string='Liquidación',
        required=True,
        ondelete='cascade',
        readonly=True,
        help='Liquidación a la que pertenece esta hoja'
    )
    
    sheet_id = fields.Many2one(
        'dispatch.sheet',
        string='Planilla',
        related='settlement_id.sheet_id',
        store=True,
        readonly=True,
        help='Planilla de despacho'
    )
    
    driver_id = fields.Many2one(
        'dispatch.driver',
        string='Conductor',
        related='settlement_id.driver_id',
        store=True,
        readonly=True,
        help='Conductor que realizó los cobros'
    )
    
    # ========== ESTADO ==========
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('validated', 'Validado'),
        ('cancelled', 'Cancelado'),
    ], string='Estado',
       default='draft',
       required=True,
       tracking=True,
       help='Estado actual de la hoja de cobranzas')
    
    # ========== LIQUIDADOR ==========
    liquidator_id = fields.Many2one(
        'res.users',
        string='Liquidador',
        help='Usuario responsable de asignar los pagos',
        tracking=True
    )
    
    # ========== LÍNEAS DE COBRANZA ==========
    collection_line_ids = fields.One2many(
        'dispatch.collection.line',
        'collection_sheet_id',
        string='Líneas de Cobranza',
        help='Pagos registrados en esta hoja'
    )
    
    # ========== MONTOS ==========
    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        default=lambda self: self.env.company.currency_id,
        required=True
    )
    
    total_collected = fields.Monetary(
        string='Total Cobrado',
        compute='_compute_totals',
        store=True,
        help='Suma total de las líneas de cobranza'
    )
    
    total_pending = fields.Monetary(
        string='Total Pendiente',
        compute='_compute_totals',
        store=True,
        help='Total de líneas pendientes de asignar'
    )
    
    total_assigned = fields.Monetary(
        string='Total Asignado',
        compute='_compute_totals',
        store=True,
        help='Total de líneas asignadas'
    )
    
    total_paid = fields.Monetary(
        string='Total Pagado',
        compute='_compute_totals',
        store=True,
        help='Total de líneas con pago creado'
    )
    
    # ========== CONTADORES ==========
    line_count = fields.Integer(
        string='Total Líneas',
        compute='_compute_line_counts',
        store=True
    )
    
    pending_count = fields.Integer(
        string='Líneas Pendientes',
        compute='_compute_line_counts',
        store=True
    )
    
    assigned_count = fields.Integer(
        string='Líneas Asignadas',
        compute='_compute_line_counts',
        store=True
    )
    
    paid_count = fields.Integer(
        string='Líneas Pagadas',
        compute='_compute_line_counts',
        store=True
    )
    
    # ========== FECHAS ==========
    validation_date = fields.Datetime(
        string='Fecha de Validación',
        readonly=True,
        help='Fecha en que se validó la hoja'
    )
    
    # ========== NOTAS ==========
    notes = fields.Text(
        string='Observaciones',
        help='Notas sobre la hoja de cobranzas'
    )
    
    _sql_constraints = [
        ('settlement_unique', 'UNIQUE(settlement_id)',
         'Ya existe una hoja de cobranzas para esta liquidación.')
    ]
    
    @api.model_create_multi
    def create(self, vals_list):
        """Genera número secuencial al crear"""
        for vals in vals_list:
            if vals.get('name', 'Nuevo') == 'Nuevo':
                vals['name'] = self.env['ir.sequence'].next_by_code('dispatch.collection.sheet') or 'Nuevo'
        return super(DispatchCollectionSheet, self).create(vals_list)
    
    @api.depends('collection_line_ids', 'collection_line_ids.amount', 
                 'collection_line_ids.state')
    def _compute_totals(self):
        """Calcula totales de la hoja de cobranzas"""
        for sheet in self:
            # Total cobrado (todas las líneas no canceladas)
            active_lines = sheet.collection_line_ids.filtered(lambda l: l.state != 'cancelled')
            sheet.total_collected = sum(active_lines.mapped('amount'))
            
            # Total pendiente
            pending_lines = sheet.collection_line_ids.filtered(lambda l: l.state == 'pending')
            sheet.total_pending = sum(pending_lines.mapped('amount'))
            
            # Total asignado
            assigned_lines = sheet.collection_line_ids.filtered(lambda l: l.state == 'assigned')
            sheet.total_assigned = sum(assigned_lines.mapped('amount'))
            
            # Total pagado
            paid_lines = sheet.collection_line_ids.filtered(lambda l: l.state == 'paid')
            sheet.total_paid = sum(paid_lines.mapped('amount'))
    
    @api.depends('collection_line_ids', 'collection_line_ids.state')
    def _compute_line_counts(self):
        """Calcula contadores de líneas"""
        for sheet in self:
            sheet.line_count = len(sheet.collection_line_ids)
            sheet.pending_count = len(sheet.collection_line_ids.filtered(lambda l: l.state == 'pending'))
            sheet.assigned_count = len(sheet.collection_line_ids.filtered(lambda l: l.state == 'assigned'))
            sheet.paid_count = len(sheet.collection_line_ids.filtered(lambda l: l.state == 'paid'))
    
    def action_validate(self):
        """Valida la hoja de cobranzas"""
        for sheet in self:
            if sheet.state != 'draft':
                raise UserError(_('Solo se pueden validar hojas en estado Borrador.'))
            
            # Verificar que todas las líneas estén asignadas o pagadas
            pending = sheet.collection_line_ids.filtered(lambda l: l.state == 'pending')
            if pending:
                raise UserError(_(
                    'Hay %s línea(s) pendientes de asignar. '
                    'Asigne todos los pagos antes de validar.'
                ) % len(pending))
            
            sheet.write({
                'state': 'validated',
                'validation_date': fields.Datetime.now(),
            })
    
    def action_cancel(self):
        """Cancela la hoja de cobranzas"""
        for sheet in self:
            if sheet.state == 'validated':
                raise UserError(_('No se puede cancelar una hoja validada.'))
            
            # Verificar que no haya pagos creados
            paid_lines = sheet.collection_line_ids.filtered(lambda l: l.payment_id)
            if paid_lines:
                raise UserError(_(
                    'No se puede cancelar una hoja con pagos ya creados. '
                    'Cancele primero los pagos.'
                ))
            
            sheet.write({'state': 'cancelled'})
    
    def action_reset_to_draft(self):
        """Reinicia la hoja a borrador"""
        for sheet in self:
            if sheet.state not in ['validated', 'cancelled']:
                raise UserError(_('Solo se pueden reiniciar hojas Validadas o Canceladas.'))
            
            # Verificar que no haya líneas pagadas
            paid_lines = sheet.collection_line_ids.filtered(lambda l: l.state == 'paid')
            if paid_lines:
                raise UserError(_(
                    'No se puede reiniciar una hoja con líneas pagadas. '
                    'Revierta primero los pagos.'
                ))
            
            sheet.write({
                'state': 'draft',
                'validation_date': False,
            })
    
    def action_assign_liquidator(self):
        """Asigna el usuario actual como liquidador"""
        for sheet in self:
            sheet.write({'liquidator_id': self.env.user.id})
    
    def action_view_settlement(self):
        """Ver la liquidación"""
        self.ensure_one()
        return {
            'name': _('Liquidación'),
            'type': 'ir.actions.act_window',
            'res_model': 'dispatch.settlement',
            'res_id': self.settlement_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

