# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class TreasurySettlement(models.Model):
    """
    Modelo para gestionar liquidaciones de transportistas.
    Registra los cobros realizados y el proceso de aprobación por el liquidador.
    """
    _name = 'treasury.settlement'
    _description = 'Liquidación de Transportista'
    _order = 'date desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    # ========== INFORMACIÓN BÁSICA ==========
    name = fields.Char(
        string='Número de Liquidación',
        required=True,
        copy=False,
        readonly=True,
        default='Nuevo',
        tracking=True,
        help='Número identificador de la liquidación'
    )
    
    date = fields.Date(
        string='Fecha',
        required=True,
        default=fields.Date.today,
        tracking=True,
        help='Fecha de la liquidación'
    )
    
    # ========== ESTADO ==========
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('submitted', 'En Revisión'),
        ('approved', 'Aprobada'),
        ('rejected', 'Rechazada'),
    ], string='Estado',
       default='draft',
       required=True,
       tracking=True,
       help='Estado actual de la liquidación')
    
    # ========== RELACIÓN CON PLANILLA Y RUTA ==========
    sheet_id = fields.Many2one(
        'treasury.settlement.sheet',
        string='Planilla',
        required=True,
        ondelete='restrict',
        tracking=True,
        help='Planilla de reparto asociada'
    )
    
    route_id = fields.Many2one(
        'dispatch.route',
        string='Ruta',
        related='sheet_id.route_id',
        store=True,
        readonly=True,
        help='Ruta de reparto asociada'
    )
    
    driver_id = fields.Many2one(
        'dispatch.driver',
        string='Conductor',
        related='sheet_id.driver_id',
        store=True,
        readonly=True,
        help='Conductor que realizó las entregas'
    )
    
    vehicle_id = fields.Many2one(
        'dispatch.vehicle',
        string='Vehículo',
        related='sheet_id.vehicle_id',
        store=True,
        readonly=True,
        help='Vehículo utilizado'
    )
    
    # ========== LÍNEAS DE LIQUIDACIÓN ==========
    line_ids = fields.One2many(
        'treasury.settlement.line',
        'settlement_id',
        string='Detalle de Cobros',
        help='Detalle de cobros por factura'
    )
    
    # ========== MONTOS ==========
    total_to_collect = fields.Monetary(
        string='Total a Cobrar',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
        help='Total según planilla'
    )
    
    total_collected = fields.Monetary(
        string='Total Cobrado',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
        help='Total cobrado por el transportista'
    )
    
    difference = fields.Monetary(
        string='Diferencia',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
        help='Diferencia entre lo esperado y lo cobrado'
    )
    
    collection_rate = fields.Float(
        string='Porcentaje de Cobranza',
        compute='_compute_totals',
        store=True,
        help='Porcentaje cobrado del total'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        default=lambda self: self.env.company.currency_id,
        required=True
    )
    
    # ========== ESTADÍSTICAS DE ENTREGA ==========
    total_deliveries = fields.Integer(
        string='Total Entregas',
        compute='_compute_delivery_stats',
        store=True
    )
    
    delivered_count = fields.Integer(
        string='Entregados',
        compute='_compute_delivery_stats',
        store=True
    )
    
    not_delivered_count = fields.Integer(
        string='No Entregados',
        compute='_compute_delivery_stats',
        store=True
    )
    
    delivery_rate = fields.Float(
        string='Tasa de Entrega',
        compute='_compute_delivery_stats',
        store=True,
        help='Porcentaje de entregas exitosas'
    )
    
    # ========== USUARIOS ==========
    driver_user_id = fields.Many2one(
        'res.users',
        string='Transportista (Usuario)',
        help='Usuario transportista que registra la liquidación'
    )
    
    liquidator_user_id = fields.Many2one(
        'res.users',
        string='Liquidador',
        tracking=True,
        help='Usuario liquidador que aprueba/rechaza'
    )
    
    # ========== FECHAS ==========
    submission_date = fields.Datetime(
        string='Fecha de Envío',
        readonly=True,
        tracking=True,
        help='Fecha y hora de envío a revisión'
    )
    
    approval_date = fields.Datetime(
        string='Fecha de Aprobación/Rechazo',
        readonly=True,
        tracking=True,
        help='Fecha y hora de aprobación o rechazo'
    )
    
    # ========== OBSERVACIONES ==========
    rejection_reason = fields.Text(
        string='Motivo de Rechazo',
        tracking=True,
        help='Razón por la que se rechazó la liquidación'
    )
    
    notes = fields.Text(
        string='Observaciones',
        help='Observaciones generales sobre la liquidación'
    )
    
    driver_notes = fields.Text(
        string='Notas del Transportista',
        help='Comentarios del transportista sobre la jornada'
    )
    
    # ========== OTROS ==========
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        default=lambda self: self.env.company,
        required=True
    )
    
    @api.model
    def create(self, vals):
        """Genera número secuencial al crear"""
        if vals.get('name', 'Nuevo') == 'Nuevo':
            vals['name'] = self.env['ir.sequence'].next_by_code('treasury.settlement') or 'Nuevo'
        return super(TreasurySettlement, self).create(vals)
    
    @api.depends('line_ids', 'line_ids.amount_invoice', 'line_ids.amount_collected')
    def _compute_totals(self):
        """Calcula totales y diferencias"""
        for settlement in self:
            settlement.total_to_collect = sum(settlement.line_ids.mapped('amount_invoice'))
            settlement.total_collected = sum(settlement.line_ids.mapped('amount_collected'))
            settlement.difference = settlement.total_to_collect - settlement.total_collected
            
            # Calcular porcentaje de cobranza
            if settlement.total_to_collect > 0:
                settlement.collection_rate = (settlement.total_collected / settlement.total_to_collect) * 100
            else:
                settlement.collection_rate = 0.0
    
    @api.depends('line_ids', 'line_ids.delivery_status')
    def _compute_delivery_stats(self):
        """Calcula estadísticas de entregas"""
        for settlement in self:
            settlement.total_deliveries = len(settlement.line_ids)
            settlement.delivered_count = len(settlement.line_ids.filtered(
                lambda l: l.delivery_status == 'delivered'
            ))
            settlement.not_delivered_count = len(settlement.line_ids.filtered(
                lambda l: l.delivery_status == 'not_delivered'
            ))
            
            # Calcular tasa de entrega
            if settlement.total_deliveries > 0:
                settlement.delivery_rate = (settlement.delivered_count / settlement.total_deliveries) * 100
            else:
                settlement.delivery_rate = 0.0
    
    @api.constrains('line_ids')
    def _check_line_ids(self):
        """Valida que la liquidación tenga líneas"""
        for settlement in self:
            if settlement.state != 'draft' and not settlement.line_ids:
                raise ValidationError(_(
                    'La liquidación debe tener al menos una línea antes de enviar.'
                ))
    
    def action_submit_for_review(self):
        """Transportista envía liquidación para revisión"""
        for settlement in self:
            if settlement.state != 'draft':
                raise UserError(_(
                    'Solo se pueden enviar liquidaciones en estado Borrador.'
                ))
            
            if not settlement.line_ids:
                raise UserError(_(
                    'Debe registrar al menos un cobro antes de enviar.'
                ))
            
            settlement.write({
                'state': 'submitted',
                'submission_date': fields.Datetime.now(),
                'driver_user_id': self.env.user.id,
            })
            
            # Actualizar estado de planilla
            if settlement.sheet_id.state == 'in_route':
                settlement.sheet_id.write({'state': 'settled'})
            
            settlement.message_post(
                body=_('Liquidación enviada para revisión por %s') % self.env.user.name
            )
            
            # Crear actividad para el grupo de liquidadores
            liquidators = self.env.ref('account.group_account_manager', raise_if_not_found=False)
            if liquidators:
                settlement.activity_schedule(
                    'mail.mail_activity_data_todo',
                    summary=_('Revisar Liquidación %s') % settlement.name,
                    note=_('Nueva liquidación pendiente de revisión'),
                    user_id=liquidators.users[0].id if liquidators.users else self.env.user.id,
                )
    
    def action_approve(self):
        """Liquidador aprueba la liquidación"""
        for settlement in self:
            if settlement.state != 'submitted':
                raise UserError(_(
                    'Solo se pueden aprobar liquidaciones en revisión.'
                ))
            
            settlement.write({
                'state': 'approved',
                'approval_date': fields.Datetime.now(),
                'liquidator_user_id': self.env.user.id,
            })
            
            # Actualizar estados en líneas de planilla
            for line in settlement.line_ids:
                if line.sheet_line_id:
                    line.sheet_line_id.write({
                        'amount_collected': line.amount_collected,
                        'delivery_status': line.delivery_status,
                        'payment_method': line.payment_method,
                    })
            
            # Marcar actividades como completadas
            settlement.activity_feedback(['mail.mail_activity_data_todo'])
            
            settlement.message_post(
                body=_('Liquidación aprobada por %s. Total cobrado: %s') % (
                    self.env.user.name,
                    settlement.total_collected
                )
            )
    
    def action_reject(self):
        """Liquidador rechaza la liquidación"""
        for settlement in self:
            if settlement.state != 'submitted':
                raise UserError(_(
                    'Solo se pueden rechazar liquidaciones en revisión.'
                ))
            
            if not settlement.rejection_reason:
                raise UserError(_(
                    'Debe especificar el motivo del rechazo.'
                ))
            
            settlement.write({
                'state': 'rejected',
                'approval_date': fields.Datetime.now(),
                'liquidator_user_id': self.env.user.id,
            })
            
            # Marcar actividades como completadas
            settlement.activity_feedback(['mail.mail_activity_data_todo'])
            
            settlement.message_post(
                body=_('Liquidación rechazada por %s. Motivo: %s') % (
                    self.env.user.name,
                    settlement.rejection_reason
                )
            )
    
    def action_reset_to_draft(self):
        """Reinicia la liquidación a borrador"""
        for settlement in self:
            if settlement.state not in ['submitted', 'rejected']:
                raise UserError(_(
                    'Solo se pueden reiniciar liquidaciones En Revisión o Rechazadas.'
                ))
            
            if settlement.state == 'submitted':
                # Verificar permiso de liquidador
                if not self.env.user.has_group('account.group_account_manager'):
                    raise UserError(_(
                        'Solo los liquidadores pueden cancelar una liquidación en revisión.'
                    ))
            
            settlement.write({
                'state': 'draft',
                'submission_date': False,
                'approval_date': False,
                'rejection_reason': False,
            })
            
            settlement.message_post(body=_('Liquidación reiniciada a borrador'))
    
    def action_view_sheet(self):
        """Ver planilla asociada"""
        self.ensure_one()
        return {
            'name': _('Planilla'),
            'type': 'ir.actions.act_window',
            'res_model': 'treasury.settlement.sheet',
            'res_id': self.sheet_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_view_route(self):
        """Ver ruta asociada"""
        self.ensure_one()
        if not self.route_id:
            raise UserError(_('Esta liquidación no tiene una ruta asociada.'))
        
        return {
            'name': _('Ruta'),
            'type': 'ir.actions.act_window',
            'res_model': 'dispatch.route',
            'res_id': self.route_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_open_rejection_wizard(self):
        """Abre wizard para rechazar con motivo"""
        self.ensure_one()
        return {
            'name': _('Rechazar Liquidación'),
            'type': 'ir.actions.act_window',
            'res_model': 'treasury.settlement.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_settlement_id': self.id,
            }
        }

