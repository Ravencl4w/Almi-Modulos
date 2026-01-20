# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class TreasurySettlementSheet(models.Model):
    """
    Modelo para gestionar planillas de reparto.
    Agrupa facturas confirmadas para asignar a un transportista/ruta.
    """
    _name = 'treasury.settlement.sheet'
    _description = 'Planilla de Reparto'
    _order = 'date desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    # ========== INFORMACIÓN BÁSICA ==========
    name = fields.Char(
        string='Número de Planilla',
        required=True,
        copy=False,
        readonly=True,
        default='Nuevo',
        tracking=True,
        help='Número identificador de la planilla'
    )
    
    date = fields.Date(
        string='Fecha',
        required=True,
        default=fields.Date.today,
        tracking=True,
        help='Fecha de creación de la planilla'
    )
    
    # ========== ESTADO ==========
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmada'),
        ('in_route', 'En Ruta'),
        ('settled', 'Liquidada'),
        ('closed', 'Cerrada'),
        ('cancelled', 'Cancelada'),
    ], string='Estado',
       default='draft',
       required=True,
       tracking=True,
       help='Estado actual de la planilla')
    
    # ========== LÍNEAS DE PLANILLA ==========
    line_ids = fields.One2many(
        'treasury.settlement.sheet.line',
        'sheet_id',
        string='Facturas',
        help='Facturas incluidas en esta planilla'
    )
    
    # ========== ASIGNACIÓN A RUTA ==========
    route_id = fields.Many2one(
        'dispatch.route',
        string='Ruta Asignada',
        tracking=True,
        help='Ruta de reparto a la que está asignada esta planilla'
    )
    
    driver_id = fields.Many2one(
        'dispatch.driver',
        string='Conductor',
        related='route_id.driver_id',
        store=True,
        readonly=True,
        help='Conductor asignado a la ruta'
    )
    
    vehicle_id = fields.Many2one(
        'dispatch.vehicle',
        string='Vehículo',
        related='route_id.vehicle_id',
        store=True,
        readonly=True,
        help='Vehículo asignado a la ruta'
    )
    
    # ========== CAMPOS COMPUTADOS - TOTALES ==========
    total_amount = fields.Monetary(
        string='Monto Total',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
        help='Suma total de las facturas'
    )
    
    total_invoices = fields.Integer(
        string='Total de Facturas',
        compute='_compute_totals',
        store=True,
        help='Número total de facturas en la planilla'
    )
    
    total_collected = fields.Monetary(
        string='Total Cobrado',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
        help='Total cobrado hasta el momento'
    )
    
    total_pending = fields.Monetary(
        string='Total Pendiente',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
        help='Total pendiente de cobro'
    )
    
    # ========== ESTADÍSTICAS ==========
    delivered_count = fields.Integer(
        string='Entregados',
        compute='_compute_totals',
        store=True,
        help='Cantidad de facturas con producto entregado'
    )
    
    not_delivered_count = fields.Integer(
        string='No Entregados',
        compute='_compute_totals',
        store=True,
        help='Cantidad de facturas no entregadas'
    )
    
    pending_count = fields.Integer(
        string='Pendientes',
        compute='_compute_totals',
        store=True,
        help='Cantidad de facturas pendientes'
    )
    
    # ========== LIQUIDACIÓN ==========
    settlement_ids = fields.One2many(
        'treasury.settlement',
        'sheet_id',
        string='Liquidaciones',
        help='Liquidaciones asociadas a esta planilla'
    )
    
    settlement_count = fields.Integer(
        string='Cantidad de Liquidaciones',
        compute='_compute_settlement_count',
        help='Número de liquidaciones creadas'
    )
    
    has_approved_settlement = fields.Boolean(
        string='Tiene Liquidación Aprobada',
        compute='_compute_settlement_status',
        store=True,
        help='Indica si tiene al menos una liquidación aprobada'
    )
    
    # ========== OTROS CAMPOS ==========
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
        string='Notas',
        help='Notas adicionales sobre la planilla'
    )
    
    @api.model
    def create(self, vals):
        """Genera número secuencial al crear"""
        if vals.get('name', 'Nuevo') == 'Nuevo':
            vals['name'] = self.env['ir.sequence'].next_by_code('treasury.settlement.sheet') or 'Nuevo'
        return super(TreasurySettlementSheet, self).create(vals)
    
    @api.depends('line_ids', 'line_ids.amount_total', 'line_ids.amount_collected',
                 'line_ids.delivery_status')
    def _compute_totals(self):
        """Calcula totales de la planilla"""
        for sheet in self:
            sheet.total_invoices = len(sheet.line_ids)
            sheet.total_amount = sum(sheet.line_ids.mapped('amount_total'))
            sheet.total_collected = sum(sheet.line_ids.mapped('amount_collected'))
            sheet.total_pending = sheet.total_amount - sheet.total_collected
            
            # Estadísticas de entrega
            sheet.delivered_count = len(sheet.line_ids.filtered(
                lambda l: l.delivery_status == 'delivered'
            ))
            sheet.not_delivered_count = len(sheet.line_ids.filtered(
                lambda l: l.delivery_status == 'not_delivered'
            ))
            sheet.pending_count = len(sheet.line_ids.filtered(
                lambda l: l.delivery_status == 'pending'
            ))
    
    @api.depends('settlement_ids')
    def _compute_settlement_count(self):
        """Cuenta las liquidaciones asociadas"""
        for sheet in self:
            sheet.settlement_count = len(sheet.settlement_ids)
    
    @api.depends('settlement_ids', 'settlement_ids.state')
    def _compute_settlement_status(self):
        """Verifica si tiene liquidación aprobada"""
        for sheet in self:
            sheet.has_approved_settlement = any(
                s.state == 'approved' for s in sheet.settlement_ids
            )
    
    @api.constrains('line_ids')
    def _check_line_ids(self):
        """Valida que la planilla tenga al menos una factura"""
        for sheet in self:
            if sheet.state not in ['draft', 'cancelled'] and not sheet.line_ids:
                raise ValidationError(_(
                    'La planilla debe tener al menos una factura antes de confirmar.'
                ))
    
    def action_confirm(self):
        """Confirma la planilla"""
        for sheet in self:
            if not sheet.line_ids:
                raise UserError(_('No se puede confirmar una planilla sin facturas.'))
            
            if sheet.state != 'draft':
                raise UserError(_('Solo se pueden confirmar planillas en estado Borrador.'))
            
            sheet.write({'state': 'confirmed'})
            sheet.message_post(
                body=_('Planilla confirmada con %s facturas por un total de %s') % (
                    sheet.total_invoices,
                    sheet.total_amount
                )
            )
    
    def action_assign_to_route(self):
        """Abre wizard para asignar a ruta"""
        self.ensure_one()
        
        if self.state not in ['confirmed', 'in_route']:
            raise UserError(_(
                'Solo se pueden asignar a ruta las planillas confirmadas. '
                'Estado actual: %s'
            ) % dict(self._fields['state'].selection).get(self.state))
        
        return {
            'name': _('Asignar Planilla a Ruta'),
            'type': 'ir.actions.act_window',
            'res_model': 'treasury.settlement.sheet.assign.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_sheet_id': self.id,
            }
        }
    
    def action_create_settlement(self):
        """Crea una nueva liquidación para esta planilla"""
        self.ensure_one()
        
        if self.state not in ['in_route', 'settled']:
            raise UserError(_(
                'Solo se pueden crear liquidaciones para planillas en ruta.'
            ))
        
        if not self.route_id:
            raise UserError(_(
                'Debe asignar la planilla a una ruta antes de crear una liquidación.'
            ))
        
        # Crear liquidación
        settlement = self.env['treasury.settlement'].create({
            'sheet_id': self.id,
            'date': fields.Date.today(),
        })
        
        # Crear líneas de liquidación desde líneas de planilla
        for line in self.line_ids:
            self.env['treasury.settlement.line'].create({
                'settlement_id': settlement.id,
                'sheet_line_id': line.id,
                'invoice_id': line.invoice_id.id,
                'amount_invoice': line.amount_total,
                'amount_collected': 0.0,
            })
        
        return {
            'name': _('Liquidación'),
            'type': 'ir.actions.act_window',
            'res_model': 'treasury.settlement',
            'res_id': settlement.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_mark_in_route(self):
        """Marca la planilla como en ruta"""
        for sheet in self:
            if not sheet.route_id:
                raise UserError(_('Debe asignar la planilla a una ruta primero.'))
            
            if sheet.state != 'confirmed':
                raise UserError(_(
                    'Solo se pueden marcar en ruta las planillas confirmadas.'
                ))
            
            sheet.write({'state': 'in_route'})
            sheet.message_post(body=_('Planilla marcada como En Ruta'))
    
    def action_close(self):
        """Cierra la planilla"""
        for sheet in self:
            if sheet.state != 'settled':
                raise UserError(_(
                    'Solo se pueden cerrar planillas liquidadas.'
                ))
            
            if not sheet.has_approved_settlement:
                raise UserError(_(
                    'La planilla debe tener al menos una liquidación aprobada para cerrarla.'
                ))
            
            sheet.write({'state': 'closed'})
            sheet.message_post(body=_('Planilla cerrada'))
    
    def action_cancel(self):
        """Cancela la planilla"""
        for sheet in self:
            if sheet.state == 'closed':
                raise UserError(_('No se puede cancelar una planilla cerrada.'))
            
            if sheet.settlement_ids.filtered(lambda s: s.state == 'approved'):
                raise UserError(_(
                    'No se puede cancelar una planilla con liquidaciones aprobadas.'
                ))
            
            sheet.write({'state': 'cancelled'})
            sheet.message_post(body=_('Planilla cancelada'))
    
    def action_reset_to_draft(self):
        """Reinicia la planilla a borrador"""
        for sheet in self:
            if sheet.state not in ['confirmed', 'cancelled']:
                raise UserError(_(
                    'Solo se pueden reiniciar planillas Confirmadas o Canceladas.'
                ))
            
            if sheet.settlement_ids:
                raise UserError(_(
                    'No se puede reiniciar una planilla que ya tiene liquidaciones. '
                    'Elimine las liquidaciones primero.'
                ))
            
            sheet.write({'state': 'draft', 'route_id': False})
            sheet.message_post(body=_('Planilla reiniciada a borrador'))
    
    def action_view_invoices(self):
        """Ver facturas de la planilla"""
        self.ensure_one()
        invoice_ids = self.line_ids.mapped('invoice_id').ids
        
        return {
            'name': _('Facturas de %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [('id', 'in', invoice_ids)],
            'context': {'create': False},
        }
    
    def action_view_settlements(self):
        """Ver liquidaciones de la planilla"""
        self.ensure_one()
        
        return {
            'name': _('Liquidaciones de %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'treasury.settlement',
            'view_mode': 'list,form',
            'domain': [('sheet_id', '=', self.id)],
            'context': {'default_sheet_id': self.id},
        }
    
    def action_open_mass_invoice_selection(self):
        """Abre wizard para selección masiva de facturas"""
        self.ensure_one()
        
        if self.state != 'draft':
            raise UserError(_(
                'Solo se pueden agregar facturas a planillas en estado Borrador.'
            ))
        
        return {
            'name': _('Seleccionar Facturas'),
            'type': 'ir.actions.act_window',
            'res_model': 'treasury.invoice.selection.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_sheet_id': self.id,
            }
        }

