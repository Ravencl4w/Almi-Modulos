# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    """
    Extensión del modelo sale.order para agregar funcionalidad de
    recojo en local con workflow de reserva y notificación.
    """
    _inherit = 'sale.order'
    
    # ========== TIPO DE ENTREGA ==========
    delivery_type = fields.Selection([
        ('delivery', 'Entrega a Domicilio'),
        ('pickup', 'Recojo en Local'),
    ], string='Tipo de Entrega',
       default='delivery',
       required=True,
       tracking=True,
       help='Método de entrega del pedido')
    
    # ========== ESTADO DE RECOJO ==========
    pickup_state = fields.Selection([
        ('not_applicable', 'No Aplica'),
        ('reserved', 'Reservado'),
        ('ready', 'Listo para Recoger'),
        ('picked_up', 'Recogido'),
        ('expired', 'Expirado'),
    ], string='Estado de Recojo',
       default='not_applicable',
       tracking=True,
       help='Estado del proceso de recojo en local')
    
    # ========== FECHAS ==========
    pickup_reservation_date = fields.Datetime(
        string='Fecha de Reserva',
        readonly=True,
        help='Fecha y hora en que se reservó el pedido'
    )
    
    pickup_ready_date = fields.Datetime(
        string='Fecha Listo para Recoger',
        readonly=True,
        help='Fecha y hora en que se marcó como listo'
    )
    
    pickup_date = fields.Datetime(
        string='Fecha de Recojo',
        readonly=True,
        help='Fecha y hora en que se recogió el pedido'
    )
    
    pickup_deadline = fields.Date(
        string='Fecha Límite de Recojo',
        help='Fecha límite para recoger el pedido'
    )
    
    # ========== NOTIFICACIONES ==========
    customer_notified = fields.Boolean(
        string='Cliente Notificado',
        default=False,
        help='Indica si se notificó al cliente que puede recoger'
    )
    
    notification_sent_date = fields.Datetime(
        string='Fecha de Notificación',
        readonly=True,
        help='Fecha y hora en que se notificó al cliente'
    )
    
    # ========== UBICACIÓN DE RECOJO ==========
    pickup_location_id = fields.Many2one(
        'stock.location',
        string='Ubicación de Recojo',
        domain="[('usage', '=', 'internal')]",
        help='Ubicación donde se aparta el stock para recojo'
    )
    
    # ========== RUTA DE REPARTO (para delivery) ==========
    route_id = fields.Many2one(
        'dispatch.route',
        string='Ruta de Reparto',
        help='Ruta asignada para entrega a domicilio'
    )
    
    route_line_id = fields.Many2one(
        'dispatch.route.line',
        string='Línea de Ruta',
        help='Línea específica en la ruta'
    )
    
    # ========== INFORMACIÓN ADICIONAL ==========
    pickup_notes = fields.Text(
        string='Notas de Recojo',
        help='Notas adicionales sobre el recojo'
    )
    
    picked_up_by = fields.Char(
        string='Recogido por',
        help='Nombre de la persona que recogió el pedido'
    )
    
    pickup_dni = fields.Char(
        string='DNI de quien recoge',
        help='Documento de identidad de quien recoge'
    )
    
    @api.onchange('delivery_type')
    def _onchange_delivery_type(self):
        """Actualiza el estado de recojo según el tipo de entrega"""
        if self.delivery_type == 'pickup':
            if self.pickup_state == 'not_applicable':
                self.pickup_state = 'reserved'
        else:
            self.pickup_state = 'not_applicable'
    
    @api.constrains('delivery_type', 'pickup_location_id')
    def _check_pickup_location(self):
        """Valida que se haya seleccionado ubicación para recojo en local"""
        for order in self:
            if order.delivery_type == 'pickup' and order.state in ['sale', 'done']:
                if not order.pickup_location_id:
                    # Intentar obtener la ubicación por defecto
                    default_location = self.env['stock.location'].search([
                        ('name', '=', 'Para Recoger'),
                        ('usage', '=', 'internal')
                    ], limit=1)
                    
                    if default_location:
                        order.pickup_location_id = default_location
                    else:
                        raise ValidationError(_(
                            'Debe configurar la ubicación "Para Recoger" para pedidos de recojo en local.'
                        ))
    
    def action_confirm(self):
        """Sobrescribe la confirmación para manejar recojo en local"""
        res = super(SaleOrder, self).action_confirm()
        
        for order in self:
            if order.delivery_type == 'pickup':
                # Marcar como reservado y registrar fecha
                order.write({
                    'pickup_state': 'reserved',
                    'pickup_reservation_date': fields.Datetime.now(),
                })
                
                # Asignar ubicación de recojo por defecto si no existe
                if not order.pickup_location_id:
                    default_location = self.env['stock.location'].search([
                        ('name', '=', 'Para Recoger'),
                        ('usage', '=', 'internal')
                    ], limit=1)
                    
                    if default_location:
                        order.pickup_location_id = default_location
                
                # Calcular fecha límite (7 días por defecto)
                if not order.pickup_deadline:
                    order.pickup_deadline = fields.Date.add(
                        fields.Date.today(),
                        days=7
                    )
        
        return res
    
    def action_mark_ready_for_pickup(self):
        """Marca el pedido como listo para recoger y notifica al cliente"""
        for order in self:
            if order.delivery_type != 'pickup':
                raise UserError(_('Este pedido no es para recojo en local.'))
            
            if order.pickup_state != 'reserved':
                raise UserError(_(
                    'Solo se pueden marcar como listos los pedidos en estado Reservado. '
                    'Estado actual: %s'
                ) % dict(order._fields['pickup_state'].selection).get(order.pickup_state))
            
            # Verificar que el picking esté validado
            if not all(picking.state == 'done' for picking in order.picking_ids):
                raise UserError(_(
                    'Debe validar todas las operaciones de stock antes de marcar como listo.'
                ))
            
            # Actualizar estado
            order.write({
                'pickup_state': 'ready',
                'pickup_ready_date': fields.Datetime.now(),
            })
            
            # Enviar notificación al cliente
            order._send_pickup_notification()
    
    def action_mark_picked_up(self):
        """Marca el pedido como recogido"""
        for order in self:
            if order.delivery_type != 'pickup':
                raise UserError(_('Este pedido no es para recojo en local.'))
            
            if order.pickup_state != 'ready':
                raise UserError(_(
                    'Solo se pueden marcar como recogidos los pedidos listos. '
                    'Estado actual: %s'
                ) % dict(order._fields['pickup_state'].selection).get(order.pickup_state))
            
            # Actualizar estado
            order.write({
                'pickup_state': 'picked_up',
                'pickup_date': fields.Datetime.now(),
            })
    
    def action_reset_pickup_state(self):
        """Reinicia el estado de recojo a reservado"""
        for order in self:
            if order.delivery_type != 'pickup':
                raise UserError(_('Este pedido no es para recojo en local.'))
            
            if order.pickup_state == 'picked_up':
                raise UserError(_('No se puede reiniciar un pedido ya recogido.'))
            
            order.write({
                'pickup_state': 'reserved',
                'pickup_ready_date': False,
                'customer_notified': False,
                'notification_sent_date': False,
            })
    
    def _send_pickup_notification(self):
        """
        Envía notificación al cliente de que el pedido está listo.
        Puede ser extendido para enviar email o SMS.
        """
        self.ensure_one()
        
        if not self.partner_id.email:
            return
        
        # Preparar contexto para el email
        template = self.env.ref(
            'pharma_dispatch.email_template_pickup_ready',
            raise_if_not_found=False
        )
        
        if template:
            template.send_mail(self.id, force_send=True)
            
            self.write({
                'customer_notified': True,
                'notification_sent_date': fields.Datetime.now(),
            })
        else:
            # Marcar como notificado aunque no se envíe el template
            self.write({
                'customer_notified': True,
                'notification_sent_date': fields.Datetime.now(),
            })
    
    def _cron_check_expired_pickups(self):
        """
        Cron para verificar pedidos de recojo que pasaron su fecha límite.
        Debe ser configurado en el sistema.
        """
        today = fields.Date.today()
        expired_orders = self.search([
            ('delivery_type', '=', 'pickup'),
            ('pickup_state', 'in', ['reserved', 'ready']),
            ('pickup_deadline', '<', today),
        ])
        
        for order in expired_orders:
            order.write({'pickup_state': 'expired'})

