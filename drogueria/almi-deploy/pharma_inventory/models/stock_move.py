# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class StockMove(models.Model):
    """
    Extensión de stock.move para gestión de rechazos y control de calidad.
    """
    _inherit = 'stock.move'
    
    # ========== GESTIÓN DE RECHAZOS ==========
    quality_check = fields.Selection([
        ('pending', 'Pendiente'),
        ('passed', 'Aprobado'),
        ('failed', 'Rechazado'),
    ], string='Control de Calidad',
       default='pending',
       help='Estado del control de calidad')
    
    rejection_reason_id = fields.Many2one(
        'stock.rejection.reason',
        string='Motivo de Rechazo',
        help='Razón del rechazo del producto'
    )
    
    rejection_notes = fields.Text(
        string='Notas de Rechazo',
        help='Observaciones sobre el rechazo'
    )
    
    rejected_by = fields.Many2one(
        'res.users',
        string='Rechazado Por',
        help='Usuario que rechazó el movimiento'
    )
    
    rejection_date = fields.Datetime(
        string='Fecha de Rechazo',
        help='Fecha y hora del rechazo'
    )
    
    # ========== INFORMACIÓN DE LOTE/VENCIMIENTO ==========
    lot_expiry_state = fields.Selection(
        related='lot_ids.expiry_state',
        string='Estado de Vencimiento del Lote',
        readonly=True
    )
    
    lot_days_to_expiry = fields.Integer(
        related='lot_ids.days_to_expiry',
        string='Días para Vencer',
        readonly=True
    )
    
    requires_cold_chain = fields.Boolean(
        related='product_id.cold_chain',
        string='Requiere Cadena de Frío',
        readonly=True
    )


class StockRejectionReason(models.Model):
    """
    Catálogo de motivos de rechazo de productos.
    """
    _name = 'stock.rejection.reason'
    _description = 'Motivo de Rechazo'
    _order = 'name'
    
    name = fields.Char(
        string='Motivo',
        required=True,
        translate=True
    )
    
    code = fields.Char(
        string='Código',
        help='Código del motivo de rechazo'
    )
    
    description = fields.Text(
        string='Descripción',
        help='Descripción detallada del motivo'
    )
    
    active = fields.Boolean(
        string='Activo',
        default=True
    )
    
    category = fields.Selection([
        ('quality', 'Defecto de Calidad'),
        ('damage', 'Daño Físico'),
        ('expiry', 'Vencimiento'),
        ('documentation', 'Documentación'),
        ('other', 'Otro'),
    ], string='Categoría',
       required=True,
       default='quality')

