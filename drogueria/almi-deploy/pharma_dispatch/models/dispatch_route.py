# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class DispatchRoute(models.Model):
    """
    Modelo para gestionar rutas de reparto.
    Agrupa múltiples pedidos para un conductor en una fecha específica.
    """
    _name = 'dispatch.route'
    _description = 'Ruta de Reparto'
    _order = 'route_date desc, id desc'
    
    # ========== INFORMACIÓN BÁSICA ==========
    name = fields.Char(
        string='Número de Ruta',
        required=True,
        copy=False,
        readonly=True,
        default='Nuevo',
        help='Número identificador de la ruta'
    )
    
    route_date = fields.Date(
        string='Fecha de Ruta',
        required=True,
        default=fields.Date.today,
        help='Fecha programada para la ruta'
    )
    
    # ========== ASIGNACIÓN ==========
    driver_id = fields.Many2one(
        'dispatch.driver',
        string='Conductor',
        required=True,
        help='Conductor asignado a esta ruta'
    )
    
    vehicle_id = fields.Many2one(
        'dispatch.vehicle',
        string='Vehículo',
        required=True,
        help='Vehículo asignado a esta ruta'
    )
    
    # ========== PLANILLA ==========
    sheet_id = fields.Many2one(
        'dispatch.sheet',
        string='Planilla de Despacho',
        readonly=True,
        help='Planilla desde la cual se generó esta ruta'
    )
    
    # ========== ESTADO ==========
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('assigned', 'Asignado'),
        ('in_progress', 'En Progreso'),
        ('done', 'Completado'),
        ('cancelled', 'Cancelado'),
    ], string='Estado',
       default='draft',
       required=True,
       help='Estado actual de la ruta')
    
    # ========== LÍNEAS DE RUTA ==========
    line_ids = fields.One2many(
        'dispatch.route.line',
        'route_id',
        string='Pedidos',
        help='Pedidos incluidos en esta ruta'
    )
    
    # ========== CAMPOS COMPUTADOS ==========
    total_orders = fields.Integer(
        string='Total de Pedidos',
        compute='_compute_totals',
        store=True,
        help='Número total de pedidos en la ruta'
    )
    
    pending_orders = fields.Integer(
        string='Pedidos Pendientes',
        compute='_compute_totals',
        store=True,
        help='Número de pedidos pendientes de entrega'
    )
    
    delivered_orders = fields.Integer(
        string='Pedidos Entregados',
        compute='_compute_totals',
        store=True,
        help='Número de pedidos entregados'
    )
    
    failed_orders = fields.Integer(
        string='Pedidos Fallidos',
        compute='_compute_totals',
        store=True,
        help='Número de pedidos no entregados'
    )
    
    total_weight = fields.Float(
        string='Peso Total (kg)',
        compute='_compute_totals',
        store=True,
        digits=(10, 2),
        help='Peso total de todos los pedidos'
    )
    
    zone_ids = fields.Many2many(
        'sale.zone',
        string='Zonas',
        compute='_compute_zones',
        store=True,
        help='Zonas de venta cubiertas en esta ruta'
    )
    
    # ========== FECHAS ==========
    start_datetime = fields.Datetime(
        string='Hora de Inicio',
        help='Hora en que se inició la ruta'
    )
    
    end_datetime = fields.Datetime(
        string='Hora de Fin',
        help='Hora en que se completó la ruta'
    )
    
    # ========== NOTAS ==========
    notes = fields.Text(
        string='Notas',
        help='Notas adicionales sobre la ruta'
    )
    
    @api.model_create_multi
    def create(self, vals_list):
        """Genera número secuencial al crear"""
        for vals in vals_list:
            if vals.get('name', 'Nuevo') == 'Nuevo':
                vals['name'] = self.env['ir.sequence'].next_by_code('dispatch.route') or 'Nuevo'
        return super(DispatchRoute, self).create(vals_list)
    
    @api.depends('line_ids', 'line_ids.state', 'line_ids.order_id')
    def _compute_totals(self):
        """Calcula totales de la ruta"""
        for route in self:
            route.total_orders = len(route.line_ids)
            route.pending_orders = len(route.line_ids.filtered(lambda l: l.state == 'pending'))
            route.delivered_orders = len(route.line_ids.filtered(lambda l: l.state == 'delivered'))
            route.failed_orders = len(route.line_ids.filtered(lambda l: l.state == 'failed'))
            
            # Calcular peso total desde los pedidos
            total_weight = 0.0
            for line in route.line_ids:
                if line.order_id:
                    for order_line in line.order_id.order_line:
                        if order_line.product_id.weight:
                            total_weight += order_line.product_id.weight * order_line.product_uom_qty
            route.total_weight = total_weight
    
    @api.depends('line_ids', 'line_ids.partner_id', 'line_ids.partner_id.sale_zone_id')
    def _compute_zones(self):
        """Calcula las zonas cubiertas en la ruta"""
        for route in self:
            zones = route.line_ids.mapped('partner_id.sale_zone_id')
            route.zone_ids = [(6, 0, zones.ids)]
    
    @api.constrains('driver_id', 'vehicle_id', 'route_date', 'state')
    def _check_driver_vehicle_availability(self):
        """Valida que el conductor y vehículo no estén asignados a otra ruta el mismo día"""
        for route in self:
            if route.state not in ['draft', 'cancelled']:
                # Buscar otras rutas del mismo día con el mismo conductor o vehículo
                overlapping_routes = self.search([
                    ('id', '!=', route.id),
                    ('route_date', '=', route.route_date),
                    ('state', 'not in', ['draft', 'cancelled']),
                    '|',
                    ('driver_id', '=', route.driver_id.id),
                    ('vehicle_id', '=', route.vehicle_id.id),
                ])
                
                if overlapping_routes:
                    conflicting = overlapping_routes[0]
                    raise ValidationError(_(
                        'El conductor o vehículo ya está asignado a la ruta %s para la fecha %s.'
                    ) % (conflicting.name, conflicting.route_date))
    
    def action_assign(self):
        """Confirma la asignación de la ruta"""
        for route in self:
            if not route.line_ids:
                raise UserError(_('No se puede asignar una ruta sin pedidos.'))
            if route.state != 'draft':
                raise UserError(_('Solo se pueden asignar rutas en estado Borrador.'))
            
            # Verificar que el conductor tenga licencia vigente
            if route.driver_id.license_expired:
                raise UserError(_(
                    'El conductor %s tiene la licencia vencida. '
                    'No se puede asignar a la ruta.'
                ) % route.driver_id.name)
            
            # Actualizar estado del vehículo
            route.vehicle_id.write({'status': 'in_use'})
            
            route.write({'state': 'assigned'})
    
    def action_start(self):
        """Inicia la ruta"""
        for route in self:
            if route.state != 'assigned':
                raise UserError(_('Solo se pueden iniciar rutas en estado Asignado.'))
            
            route.write({
                'state': 'in_progress',
                'start_datetime': fields.Datetime.now(),
            })
    
    def action_complete(self):
        """Completa la ruta"""
        for route in self:
            if route.state != 'in_progress':
                raise UserError(_('Solo se pueden completar rutas en estado En Progreso.'))
            
            # Verificar si hay pedidos pendientes
            pending = route.line_ids.filtered(lambda l: l.state == 'pending')
            if pending:
                raise UserError(_(
                    'Hay %s pedido(s) pendientes. '
                    'Marque todos los pedidos como entregados o fallidos antes de completar.'
                ) % len(pending))
            
            # Actualizar estado del vehículo
            route.vehicle_id.write({'status': 'available'})
            
            route.write({
                'state': 'done',
                'end_datetime': fields.Datetime.now(),
            })
    
    def action_cancel(self):
        """Cancela la ruta"""
        for route in self:
            if route.state == 'done':
                raise UserError(_('No se puede cancelar una ruta completada.'))
            
            # Liberar el vehículo si estaba en uso
            if route.state == 'in_progress' and route.vehicle_id.status == 'in_use':
                route.vehicle_id.write({'status': 'available'})
            
            route.write({'state': 'cancelled'})
    
    def action_reset_to_draft(self):
        """Reinicia la ruta a borrador"""
        for route in self:
            if route.state not in ['assigned', 'cancelled']:
                raise UserError(_('Solo se pueden reiniciar rutas Asignadas o Canceladas.'))
            
            # Liberar el vehículo
            if route.vehicle_id.status == 'in_use':
                route.vehicle_id.write({'status': 'available'})
            
            route.write({'state': 'draft'})
    
    def action_view_orders(self):
        """Ver pedidos de la ruta"""
        self.ensure_one()
        order_ids = self.line_ids.mapped('order_id').ids
        return {
            'name': _('Pedidos de %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'list,form',
            'domain': [('id', 'in', order_ids)],
        }

