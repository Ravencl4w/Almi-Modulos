# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class DispatchRoute(models.Model):
    """
    Extensión del modelo dispatch.route para integración con tesorería.
    Agrega campos para vincular con planillas de reparto y liquidaciones.
    """
    _inherit = 'dispatch.route'
    
    # ========== PLANILLA DE REPARTO ==========
    settlement_sheet_id = fields.Many2one(
        'treasury.settlement.sheet',
        string='Planilla de Reparto',
        tracking=True,
        help='Planilla de cobranza asignada a esta ruta'
    )
    
    has_settlement_sheet = fields.Boolean(
        string='Tiene Planilla',
        compute='_compute_has_settlement_sheet',
        store=True,
        help='Indica si esta ruta tiene una planilla asignada'
    )
    
    # ========== LIQUIDACIONES ==========
    settlement_ids = fields.One2many(
        'treasury.settlement',
        'route_id',
        string='Liquidaciones',
        help='Liquidaciones asociadas a esta ruta'
    )
    
    settlement_count = fields.Integer(
        string='Cantidad de Liquidaciones',
        compute='_compute_settlement_count',
        help='Número de liquidaciones'
    )
    
    has_approved_settlement = fields.Boolean(
        string='Tiene Liquidación Aprobada',
        compute='_compute_settlement_status',
        store=True,
        help='Indica si tiene al menos una liquidación aprobada'
    )
    
    # ========== TOTALES DE COBRANZA ==========
    sheet_total_amount = fields.Monetary(
        string='Total en Planilla',
        related='settlement_sheet_id.total_amount',
        currency_field='currency_id',
        help='Monto total de la planilla'
    )
    
    sheet_total_collected = fields.Monetary(
        string='Total Cobrado',
        related='settlement_sheet_id.total_collected',
        currency_field='currency_id',
        help='Total cobrado según planilla'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        default=lambda self: self.env.company.currency_id
    )
    
    @api.depends('settlement_sheet_id')
    def _compute_has_settlement_sheet(self):
        """Verifica si la ruta tiene planilla asignada"""
        for route in self:
            route.has_settlement_sheet = bool(route.settlement_sheet_id)
    
    @api.depends('settlement_ids')
    def _compute_settlement_count(self):
        """Cuenta las liquidaciones asociadas"""
        for route in self:
            route.settlement_count = len(route.settlement_ids)
    
    @api.depends('settlement_ids', 'settlement_ids.state')
    def _compute_settlement_status(self):
        """Verifica si tiene liquidación aprobada"""
        for route in self:
            route.has_approved_settlement = any(
                s.state == 'approved' for s in route.settlement_ids
            )
    
    def action_view_settlement_sheet(self):
        """Ver planilla de reparto"""
        self.ensure_one()
        
        if not self.settlement_sheet_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Sin Planilla'),
                    'message': _('Esta ruta no tiene una planilla de reparto asignada.'),
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
        return {
            'name': _('Planilla de Reparto'),
            'type': 'ir.actions.act_window',
            'res_model': 'treasury.settlement.sheet',
            'res_id': self.settlement_sheet_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_view_settlements(self):
        """Ver liquidaciones de la ruta"""
        self.ensure_one()
        
        return {
            'name': _('Liquidaciones de %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'treasury.settlement',
            'view_mode': 'list,form',
            'domain': [('route_id', '=', self.id)],
            'context': {
                'default_route_id': self.id,
                'default_sheet_id': self.settlement_sheet_id.id if self.settlement_sheet_id else False,
            }
        }
    
    def action_create_settlement(self):
        """Crea una liquidación para esta ruta"""
        self.ensure_one()
        
        if not self.settlement_sheet_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Error'),
                    'message': _('Debe asignar una planilla de reparto a esta ruta antes de crear una liquidación.'),
                    'type': 'danger',
                    'sticky': False,
                }
            }
        
        # Delegar al método de la planilla
        return self.settlement_sheet_id.action_create_settlement()

