# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class DispatchRouteLine(models.Model):
    """
    Líneas de ruta de reparto.
    Cada línea representa un pedido en la ruta.
    """
    _name = 'dispatch.route.line'
    _description = 'Línea de Ruta de Reparto'
    _order = 'sequence, id'
    
    # ========== RELACIÓN CON RUTA ==========
    route_id = fields.Many2one(
        'dispatch.route',
        string='Ruta',
        required=True,
        ondelete='cascade',
        help='Ruta a la que pertenece esta línea'
    )
    
    route_state = fields.Selection(
        related='route_id.state',
        string='Estado de Ruta',
        store=True,
        readonly=True
    )
    
    # ========== SECUENCIA ==========
    sequence = fields.Integer(
        string='Secuencia',
        default=10,
        help='Orden de entrega en la ruta'
    )
    
    # ========== PEDIDO ==========
    order_id = fields.Many2one(
        'sale.order',
        string='Pedido',
        required=True,
        domain="[('state', 'in', ['sale', 'done'])]",
        help='Pedido de venta a entregar'
    )
    
    order_name = fields.Char(
        related='order_id.name',
        string='Número de Pedido',
        readonly=True,
        store=True
    )
    
    # ========== CLIENTE ==========
    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        related='order_id.partner_id',
        store=True,
        readonly=True
    )
    
    partner_name = fields.Char(
        related='partner_id.name',
        string='Nombre del Cliente',
        readonly=True
    )
    
    partner_address = fields.Char(
        related='partner_id.street',
        string='Dirección',
        readonly=True
    )
    
    partner_phone = fields.Char(
        related='partner_id.phone',
        string='Teléfono',
        readonly=True
    )
    
    # ========== ZONA DE VENTA ==========
    sale_zone_id = fields.Many2one(
        'sale.zone',
        string='Zona de Venta',
        related='partner_id.sale_zone_id',
        store=True,
        readonly=True,
        help='Zona de venta del cliente'
    )
    
    # ========== ESTADO DE ENTREGA ==========
    state = fields.Selection([
        ('pending', 'Pendiente'),
        ('delivered', 'Entregado'),
        ('failed', 'No Entregado'),
    ], string='Estado',
       default='pending',
       required=True,
       help='Estado de la entrega')
    
    delivery_datetime = fields.Datetime(
        string='Fecha/Hora de Entrega',
        help='Momento en que se realizó o intentó la entrega'
    )
    
    # ========== OBSERVACIONES ==========
    notes = fields.Text(
        string='Observaciones',
        help='Notas sobre la entrega (ej: motivo de no entrega)'
    )
    
    failure_reason = fields.Selection([
        ('customer_absent', 'Cliente Ausente'),
        ('address_incorrect', 'Dirección Incorrecta'),
        ('customer_refused', 'Cliente Rechazó'),
        ('address_not_found', 'Dirección No Encontrada'),
        ('closed_business', 'Negocio Cerrado'),
        ('payment_issue', 'Problema con el Pago'),
        ('other', 'Otro'),
    ], string='Motivo de Fallo',
       help='Razón por la cual no se pudo entregar')
    
    # ========== FIRMA ==========
    signature = fields.Binary(
        string='Firma',
        attachment=True,
        help='Firma del cliente al recibir'
    )
    
    receiver_name = fields.Char(
        string='Recibido por',
        help='Nombre de quien recibió el pedido'
    )
    
    # ========== CAMPOS RELACIONADOS ==========
    order_amount_total = fields.Monetary(
        related='order_id.amount_total',
        string='Monto Total',
        readonly=True
    )
    
    currency_id = fields.Many2one(
        related='order_id.currency_id',
        string='Moneda',
        readonly=True
    )
    
    _sql_constraints = [
        ('order_unique_per_route', 'UNIQUE(route_id, order_id)',
         'Un pedido no puede estar duplicado en la misma ruta.')
    ]
    
    @api.constrains('order_id')
    def _check_order_state(self):
        """Valida que el pedido esté confirmado"""
        for line in self:
            if line.order_id.state not in ['sale', 'done']:
                raise ValidationError(_(
                    'Solo se pueden agregar pedidos confirmados a una ruta. '
                    'El pedido %s está en estado %s.'
                ) % (line.order_id.name, line.order_id.state))
    
    @api.constrains('order_id', 'route_id')
    def _check_order_not_in_other_active_route(self):
        """Valida que el pedido no esté en otra ruta activa"""
        for line in self:
            other_lines = self.search([
                ('id', '!=', line.id),
                ('order_id', '=', line.order_id.id),
                ('route_id.state', 'in', ['draft', 'assigned', 'in_progress']),
            ])
            
            if other_lines:
                route = other_lines[0].route_id
                raise ValidationError(_(
                    'El pedido %s ya está asignado a la ruta %s (estado: %s).'
                ) % (line.order_id.name, route.name, route.state))
    
    def action_mark_delivered(self):
        """Marca la entrega como exitosa y valida los pickings"""
        for line in self:
            if line.route_state != 'in_progress':
                raise ValidationError(_('Solo se pueden marcar entregas en rutas En Progreso.'))
            
            # Validar los pickings asociados al pedido
            pickings = line.order_id.picking_ids.filtered(
                lambda p: p.picking_type_code == 'outgoing' and 
                         p.state in ['confirmed', 'assigned', 'waiting']
            )
            
            for picking in pickings:
                try:
                    # Validar el picking (esto marca la entrega física)
                    picking.button_validate()
                    
                    # Enviar GRE a SUNAT si está configurado
                    if picking.is_electronic_guide and hasattr(picking, 'action_send_gre_to_sunat'):
                        try:
                            picking.action_send_gre_to_sunat()
                        except Exception as e:
                            # Si falla el envío a SUNAT, continuar
                            pass
                    
                except Exception as e:
                    raise ValidationError(_(
                        'Error al validar el picking %s: %s'
                    ) % (picking.name, str(e)))
            
            line.write({
                'state': 'delivered',
                'delivery_datetime': fields.Datetime.now(),
            })
    
    def action_mark_failed(self):
        """Marca la entrega como fallida"""
        for line in self:
            if line.route_state != 'in_progress':
                raise ValidationError(_('Solo se pueden marcar entregas en rutas En Progreso.'))
            
            line.write({
                'state': 'failed',
                'delivery_datetime': fields.Datetime.now(),
            })
    
    def action_reset_to_pending(self):
        """Reinicia la línea a pendiente"""
        for line in self:
            line.write({
                'state': 'pending',
                'delivery_datetime': False,
                'failure_reason': False,
                'notes': False,
            })
    
    def action_view_order(self):
        """Ver el pedido"""
        self.ensure_one()
        return {
            'name': _('Pedido %s') % self.order_name,
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id': self.order_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

