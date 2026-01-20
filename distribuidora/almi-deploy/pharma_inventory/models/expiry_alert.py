# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class StockExpiryAlert(models.Model):
    """
    Modelo para gestionar alertas de productos próximos a vencer.
    """
    _name = 'stock.expiry.alert'
    _description = 'Alerta de Vencimiento'
    _order = 'priority desc, expiry_date asc, id desc'
    _rec_name = 'display_name'
    
    display_name = fields.Char(
        string='Nombre',
        compute='_compute_display_name'
    )
    
    lot_id = fields.Many2one(
        'stock.lot',
        string='Lote',
        required=True,
        ondelete='cascade'
    )
    
    product_id = fields.Many2one(
        'product.product',
        string='Producto',
        required=True
    )
    
    expiry_date = fields.Date(
        string='Fecha de Vencimiento',
        required=True
    )
    
    days_to_expiry = fields.Integer(
        string='Días para Vencer',
        help='Días restantes hasta el vencimiento'
    )
    
    priority = fields.Selection([
        ('low', 'Baja (90 días)'),
        ('medium', 'Media (60 días)'),
        ('high', 'Alta (30 días)'),
        ('critical', 'Crítica (Vencido)'),
    ], string='Prioridad',
       required=True,
       default='low')
    
    state = fields.Selection([
        ('pending', 'Pendiente'),
        ('in_process', 'En Proceso'),
        ('resolved', 'Resuelto'),
        ('cancelled', 'Cancelado'),
    ], string='Estado',
       default='pending',
       required=True,
       tracking=True)
    
    action_taken = fields.Selection([
        ('none', 'Sin Acción'),
        ('exchange_requested', 'Canje Solicitado'),
        ('sold', 'Vendido'),
        ('discarded', 'Descartado'),
        ('transferred', 'Transferido'),
    ], string='Acción Tomada',
       default='none')
    
    responsible_id = fields.Many2one(
        'res.users',
        string='Responsable',
        help='Usuario responsable de gestionar la alerta'
    )
    
    notes = fields.Text(
        string='Notas'
    )
    
    resolution_date = fields.Date(
        string='Fecha de Resolución'
    )
    
    @api.depends('lot_id', 'product_id', 'expiry_date')
    def _compute_display_name(self):
        for alert in self:
            if alert.lot_id and alert.product_id:
                alert.display_name = f"{alert.product_id.display_name} - Lote {alert.lot_id.name}"
            else:
                alert.display_name = _('Nueva Alerta')
    
    def action_request_exchange(self):
        """Solicitar canje del lote"""
        self.ensure_one()
        self.lot_id.action_request_exchange()
        self.write({
            'state': 'in_process',
            'action_taken': 'exchange_requested',
        })
    
    def action_mark_resolved(self):
        """Marcar alerta como resuelta"""
        self.write({
            'state': 'resolved',
            'resolution_date': fields.Date.today(),
        })

