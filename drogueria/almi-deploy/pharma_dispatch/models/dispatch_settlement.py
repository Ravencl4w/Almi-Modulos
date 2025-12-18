# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class DispatchSettlement(models.Model):
    """
    Modelo para gestionar liquidaciones de planillas de despacho.
    Cada planilla genera automáticamente una liquidación donde se registran
    los cobros realizados por el conductor durante la ruta.
    """
    _name = 'dispatch.settlement'
    _description = 'Liquidación de Planilla'
    _order = 'create_date desc, id desc'
    
    # ========== INFORMACIÓN BÁSICA ==========
    name = fields.Char(
        string='Número de Liquidación',
        required=True,
        copy=False,
        readonly=True,
        default='Nuevo',
        help='Número identificador de la liquidación'
    )
    
    # ========== RELACIÓN CON PLANILLA ==========
    sheet_id = fields.Many2one(
        'dispatch.sheet',
        string='Planilla de Despacho',
        required=True,
        ondelete='cascade',
        readonly=True,
        help='Planilla desde la cual se generó esta liquidación'
    )
    
    driver_id = fields.Many2one(
        'dispatch.driver',
        string='Conductor',
        related='sheet_id.driver_id',
        store=True,
        readonly=True,
        help='Conductor asignado a la planilla'
    )
    
    vehicle_id = fields.Many2one(
        'dispatch.vehicle',
        string='Vehículo',
        related='sheet_id.vehicle_id',
        store=True,
        readonly=True,
        help='Vehículo asignado a la planilla'
    )
    
    sheet_date = fields.Date(
        string='Fecha de Planilla',
        related='sheet_id.sheet_date',
        store=True,
        readonly=True,
        help='Fecha de la planilla'
    )
    
    # ========== ESTADO ==========
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('in_progress', 'En Progreso'),
        ('validated', 'Validado'),
        ('cancelled', 'Cancelado'),
    ], string='Estado',
       default='draft',
       required=True,
       tracking=True,
       help='Estado actual de la liquidación')
    
    # ========== HOJA DE COBRANZAS ==========
    collection_sheet_id = fields.Many2one(
        'dispatch.collection.sheet',
        string='Hoja de Cobranzas',
        readonly=True,
        help='Hoja de cobranzas asociada a esta liquidación'
    )
    
    # ========== FACTURAS ==========
    invoice_ids = fields.Many2many(
        'account.move',
        related='sheet_id.invoice_ids',
        string='Facturas',
        readonly=True,
        help='Facturas incluidas en la planilla'
    )
    
    cash_invoice_ids = fields.Many2many(
        'account.move',
        'settlement_cash_invoice_rel',
        'settlement_id',
        'invoice_id',
        string='Facturas al Contado',
        compute='_compute_invoice_types',
        store=True,
        help='Facturas con plazo de pago inmediato'
    )
    
    credit_invoice_ids = fields.Many2many(
        'account.move',
        'settlement_credit_invoice_rel',
        'settlement_id',
        'invoice_id',
        string='Facturas al Crédito',
        compute='_compute_invoice_types',
        store=True,
        help='Facturas con plazo de pago a crédito'
    )
    
    # ========== MONTOS ==========
    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        default=lambda self: self.env.company.currency_id,
        required=True
    )
    
    total_amount = fields.Monetary(
        string='Monto Total',
        compute='_compute_totals',
        store=True,
        help='Suma total de las facturas de la planilla'
    )
    
    total_collected = fields.Monetary(
        string='Total Cobrado',
        compute='_compute_collection_totals',
        store=True,
        help='Total de pagos registrados en la hoja de cobranzas'
    )
    
    total_deposited = fields.Monetary(
        string='Total Depositado',
        compute='_compute_deposit_totals',
        store=True,
        help='Total de depósitos efectuados'
    )
    
    total_missing = fields.Monetary(
        string='Total Faltante',
        compute='_compute_deposit_totals',
        store=True,
        help='Diferencia entre lo cobrado y lo depositado'
    )
    
    cash_total = fields.Monetary(
        string='Total al Contado',
        compute='_compute_totals',
        store=True,
        help='Total de facturas al contado'
    )
    
    credit_total = fields.Monetary(
        string='Total al Crédito',
        compute='_compute_totals',
        store=True,
        help='Total de facturas al crédito'
    )
    
    # ========== CONTADORES ==========
    invoice_count = fields.Integer(
        string='Total Facturas',
        compute='_compute_invoice_counts',
        store=True
    )
    
    cash_invoice_count = fields.Integer(
        string='Facturas al Contado',
        compute='_compute_invoice_counts',
        store=True
    )
    
    credit_invoice_count = fields.Integer(
        string='Facturas al Crédito',
        compute='_compute_invoice_counts',
        store=True
    )
    
    # ========== NOTAS ==========
    notes = fields.Text(
        string='Observaciones',
        help='Notas sobre la liquidación'
    )
    
    _sql_constraints = [
        ('sheet_unique', 'UNIQUE(sheet_id)',
         'Ya existe una liquidación para esta planilla.')
    ]
    
    @api.model_create_multi
    def create(self, vals_list):
        """Genera número secuencial al crear"""
        for vals in vals_list:
            if vals.get('name', 'Nuevo') == 'Nuevo':
                vals['name'] = self.env['ir.sequence'].next_by_code('dispatch.settlement') or 'Nuevo'
        return super(DispatchSettlement, self).create(vals_list)
    
    @api.depends('invoice_ids', 'invoice_ids.invoice_payment_term_id')
    def _compute_invoice_types(self):
        """Clasifica las facturas en contado y crédito"""
        for settlement in self:
            cash_invoices = self.env['account.move']
            credit_invoices = self.env['account.move']
            
            for invoice in settlement.invoice_ids:
                # Si no tiene plazo de pago, es al contado
                # Si tiene plazo de pago y el nombre contiene "Inmediato" o "Contado", es al contado
                is_cash = False
                
                if not invoice.invoice_payment_term_id:
                    is_cash = True
                else:
                    term_name = (invoice.invoice_payment_term_id.name or '').lower()
                    if 'inmediato' in term_name or 'contado' in term_name or 'immediate' in term_name:
                        is_cash = True
                    # Verificar si todas las líneas del término de pago tienen días en 0
                    elif invoice.invoice_payment_term_id.line_ids:
                        # Obtener el campo correcto (puede ser nb_days, days, o delay)
                        try:
                            all_zero = all(
                                getattr(line, 'nb_days', getattr(line, 'days', 999)) == 0 
                                for line in invoice.invoice_payment_term_id.line_ids
                            )
                            if all_zero:
                                is_cash = True
                        except:
                            # Si hay error, asumir que no es al contado
                            pass
                
                if is_cash:
                    cash_invoices |= invoice
                else:
                    credit_invoices |= invoice
            
            settlement.cash_invoice_ids = [(6, 0, cash_invoices.ids)]
            settlement.credit_invoice_ids = [(6, 0, credit_invoices.ids)]
    
    @api.depends('invoice_ids', 'cash_invoice_ids', 'credit_invoice_ids')
    def _compute_totals(self):
        """Calcula totales de facturas"""
        for settlement in self:
            settlement.total_amount = sum(settlement.invoice_ids.mapped('amount_total'))
            settlement.cash_total = sum(settlement.cash_invoice_ids.mapped('amount_total'))
            settlement.credit_total = sum(settlement.credit_invoice_ids.mapped('amount_total'))
    
    @api.depends('collection_sheet_id', 'collection_sheet_id.collection_line_ids',
                 'collection_sheet_id.collection_line_ids.amount',
                 'collection_sheet_id.collection_line_ids.state')
    def _compute_collection_totals(self):
        """Calcula el total cobrado desde la hoja de cobranzas"""
        for settlement in self:
            if settlement.collection_sheet_id:
                # Sumar todas las líneas que no estén canceladas
                lines = settlement.collection_sheet_id.collection_line_ids.filtered(
                    lambda l: l.state != 'cancelled'
                )
                settlement.total_collected = sum(lines.mapped('amount'))
            else:
                settlement.total_collected = 0.0
    
    @api.depends('collection_sheet_id', 'collection_sheet_id.collection_line_ids',
                 'collection_sheet_id.collection_line_ids.amount',
                 'collection_sheet_id.collection_line_ids.collection_type',
                 'collection_sheet_id.collection_line_ids.state')
    def _compute_deposit_totals(self):
        """Calcula totales de depósitos y faltantes"""
        for settlement in self:
            if settlement.collection_sheet_id:
                deposit_lines = settlement.collection_sheet_id.collection_line_ids.filtered(
                    lambda l: l.collection_type == 'deposit' and l.state != 'cancelled'
                )
                settlement.total_deposited = sum(deposit_lines.mapped('amount'))
                settlement.total_missing = settlement.total_collected - settlement.total_deposited
            else:
                settlement.total_deposited = 0.0
                settlement.total_missing = 0.0
    
    @api.depends('invoice_ids', 'cash_invoice_ids', 'credit_invoice_ids')
    def _compute_invoice_counts(self):
        """Calcula contadores de facturas"""
        for settlement in self:
            settlement.invoice_count = len(settlement.invoice_ids)
            settlement.cash_invoice_count = len(settlement.cash_invoice_ids)
            settlement.credit_invoice_count = len(settlement.credit_invoice_ids)
    
    def action_start_progress(self):
        """Inicia el progreso de la liquidación"""
        for settlement in self:
            if settlement.state != 'draft':
                raise UserError(_('Solo se pueden iniciar liquidaciones en estado Borrador.'))
            
            settlement.write({'state': 'in_progress'})
    
    def action_validate(self):
        """Valida la liquidación"""
        for settlement in self:
            if settlement.state != 'in_progress':
                raise UserError(_('Solo se pueden validar liquidaciones en estado En Progreso.'))
            
            # Verificar que todas las líneas de cobranza estén asignadas
            if settlement.collection_sheet_id:
                pending_lines = settlement.collection_sheet_id.collection_line_ids.filtered(
                    lambda l: l.state == 'pending'
                )
                if pending_lines:
                    raise UserError(_(
                        'Hay %s línea(s) de cobranza pendientes de asignar. '
                        'Asigne todos los pagos antes de validar.'
                    ) % len(pending_lines))
            
            settlement.write({'state': 'validated'})
    
    def action_cancel(self):
        """Cancela la liquidación"""
        for settlement in self:
            if settlement.state == 'validated':
                raise UserError(_('No se puede cancelar una liquidación validada.'))
            
            settlement.write({'state': 'cancelled'})
    
    def action_reset_to_draft(self):
        """Reinicia la liquidación a borrador"""
        for settlement in self:
            if settlement.state not in ['in_progress', 'cancelled']:
                raise UserError(_('Solo se pueden reiniciar liquidaciones En Progreso o Canceladas.'))
            
            settlement.write({'state': 'draft'})
    
    def action_view_collection_sheet(self):
        """Ver la hoja de cobranzas"""
        self.ensure_one()
        if not self.collection_sheet_id:
            raise UserError(_('Esta liquidación no tiene una hoja de cobranzas generada todavía.'))
        
        return {
            'name': _('Hoja de Cobranzas'),
            'type': 'ir.actions.act_window',
            'res_model': 'dispatch.collection.sheet',
            'res_id': self.collection_sheet_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_view_cash_invoices(self):
        """Ver facturas al contado"""
        self.ensure_one()
        return {
            'name': _('Facturas al Contado'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.cash_invoice_ids.ids)],
        }
    
    def action_view_credit_invoices(self):
        """Ver facturas al crédito"""
        self.ensure_one()
        return {
            'name': _('Facturas al Crédito'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.credit_invoice_ids.ids)],
        }

