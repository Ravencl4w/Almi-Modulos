# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta


class StockLot(models.Model):
    """
    Extensión del modelo stock.lot para gestión de vencimientos y canjes
    específicos del sector farmacéutico.
    """
    _inherit = 'stock.lot'
    
    # ========== GESTIÓN DE VENCIMIENTO ==========
    expiry_state = fields.Selection([
        ('ok', 'OK'),
        ('alert_90', 'Alerta 90 días'),
        ('alert_60', 'Alerta 60 días'),
        ('alert_30', 'Alerta 30 días'),
        ('expired', 'Vencido'),
        ('no_expiry', 'Sin Vencimiento'),
    ], string='Estado de Vencimiento',
       compute='_compute_expiry_state',
       store=True,
       help='Estado del lote según fecha de vencimiento')
    
    days_to_expiry = fields.Integer(
        string='Días para Vencer',
        compute='_compute_expiry_state',
        store=True,
        help='Días restantes hasta el vencimiento'
    )
    
    # ========== GESTIÓN DE CANJES ==========
    exchange_state = fields.Selection([
        ('no_exchange', 'No Aplica'),
        ('pending', 'Pendiente de Canje'),
        ('in_process', 'En Proceso'),
        ('exchanged', 'Canjeado'),
        ('rejected', 'Rechazado por Lab'),
    ], string='Estado de Canje',
       default='no_exchange',
       tracking=True,
       help='Estado del proceso de canje con el laboratorio')
    
    exchange_date = fields.Date(
        string='Fecha de Canje',
        tracking=True,
        help='Fecha en que se realizó el canje'
    )
    
    exchange_reference = fields.Char(
        string='Referencia de Canje',
        tracking=True,
        help='Número de referencia del canje con el laboratorio'
    )
    
    exchange_notes = fields.Text(
        string='Notas de Canje',
        help='Observaciones sobre el proceso de canje'
    )
    
    exchange_responsible_id = fields.Many2one(
        'res.users',
        string='Responsable del Canje',
        tracking=True,
        help='Usuario responsable de gestionar el canje'
    )
    
    can_be_exchanged = fields.Boolean(
        string='Puede Canjearse',
        compute='_compute_can_be_exchanged',
        store=True,
        help='Indica si el lote cumple las condiciones para canje'
    )
    
    # ========== INFORMACIÓN ADICIONAL ==========
    requires_cold_chain = fields.Boolean(
        string='Requiere Cadena de Frío',
        related='product_id.cold_chain',
        store=True,
        help='Indica si el producto requiere refrigeración'
    )
    
    quality_state = fields.Selection([
        ('pass', 'Aprobado'),
        ('quarantine', 'En Cuarentena'),
        ('rejected', 'Rechazado'),
    ], string='Estado de Calidad',
       default='pass',
       tracking=True,
       help='Estado de calidad del lote')
    
    rejection_reason = fields.Text(
        string='Motivo de Rechazo',
        help='Razón por la que se rechazó el lote'
    )
    
    alert_sent = fields.Boolean(
        string='Alerta Enviada',
        default=False,
        help='Indica si ya se envió alerta de vencimiento'
    )
    
    # ========== CAMPOS COMPUTADOS ==========
    
    @api.depends('expiration_date')
    def _compute_expiry_state(self):
        """Calcula el estado de vencimiento según días restantes"""
        today = fields.Date.today()
        
        for lot in self:
            if not lot.expiration_date:
                lot.expiry_state = 'no_expiry'
                lot.days_to_expiry = 0
            else:
                # Convertir expiration_date a date si es datetime
                expiry_date = lot.expiration_date
                if isinstance(expiry_date, datetime):
                    expiry_date = expiry_date.date()
                
                days_diff = (expiry_date - today).days
                lot.days_to_expiry = days_diff
                
                if days_diff < 0:
                    lot.expiry_state = 'expired'
                elif days_diff <= 30:
                    lot.expiry_state = 'alert_30'
                elif days_diff <= 60:
                    lot.expiry_state = 'alert_60'
                elif days_diff <= 90:
                    lot.expiry_state = 'alert_90'
                else:
                    lot.expiry_state = 'ok'
    
    @api.depends('expiry_state', 'quality_state', 'exchange_state')
    def _compute_can_be_exchanged(self):
        """Determina si el lote puede ser canjeado"""
        for lot in self:
            # Condiciones para canje:
            # - Estado de vencimiento en alerta o vencido
            # - Calidad aprobada (no rechazado)
            # - No está ya en proceso o canjeado
            lot.can_be_exchanged = (
                lot.expiry_state in ['alert_90', 'alert_60', 'alert_30', 'expired'] and
                lot.quality_state == 'pass' and
                lot.exchange_state in ['no_exchange', 'pending']
            )
    
    # ========== MÉTODOS DE NEGOCIO ==========
    
    def action_request_exchange(self):
        """Solicita el canje del lote con el laboratorio"""
        self.ensure_one()
        
        if not self.can_be_exchanged:
            raise UserError(_('Este lote no cumple las condiciones para canje.'))
        
        self.write({
            'exchange_state': 'pending',
            'exchange_responsible_id': self.env.user.id,
        })
        
        # Crear alerta de vencimiento si no existe
        self._create_expiry_alert()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Solicitud de Canje'),
                'message': _('Se ha solicitado el canje del lote %s') % self.name,
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_mark_as_exchanged(self):
        """Marca el lote como canjeado"""
        self.ensure_one()
        
        self.write({
            'exchange_state': 'exchanged',
            'exchange_date': fields.Date.today(),
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Canje Completado'),
                'message': _('El lote %s ha sido marcado como canjeado') % self.name,
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_reject_exchange(self):
        """Marca el canje como rechazado por el laboratorio"""
        self.ensure_one()
        
        self.write({
            'exchange_state': 'rejected',
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Canje Rechazado'),
                'message': _('El laboratorio rechazó el canje del lote %s') % self.name,
                'type': 'warning',
                'sticky': True,
            }
        }
    
    def action_move_to_quarantine(self):
        """Mueve el lote a cuarentena"""
        self.ensure_one()
        
        self.write({
            'quality_state': 'quarantine',
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Lote en Cuarentena'),
                'message': _('El lote %s ha sido movido a cuarentena') % self.name,
                'type': 'warning',
                'sticky': False,
            }
        }
    
    def _create_expiry_alert(self):
        """Crea una alerta de vencimiento para el lote"""
        self.ensure_one()
        
        if self.alert_sent:
            return
        
        alert_obj = self.env['stock.expiry.alert']
        
        # Verificar si ya existe una alerta para este lote
        existing_alert = alert_obj.search([
            ('lot_id', '=', self.id),
            ('state', 'in', ['pending', 'in_process'])
        ], limit=1)
        
        if existing_alert:
            return
        
        # Crear nueva alerta
        alert_obj.create({
            'lot_id': self.id,
            'product_id': self.product_id.id,
            'expiry_date': self.expiration_date,
            'days_to_expiry': self.days_to_expiry,
            'priority': self._get_alert_priority(),
            'state': 'pending',
        })
        
        self.alert_sent = True
    
    def _get_alert_priority(self):
        """Determina la prioridad de la alerta según días para vencer"""
        if self.days_to_expiry < 0:
            return 'critical'
        elif self.days_to_expiry <= 30:
            return 'high'
        elif self.days_to_expiry <= 60:
            return 'medium'
        else:
            return 'low'
    
    @api.model
    def _cron_check_expiry_dates(self):
        """Cron job para verificar fechas de vencimiento y crear alertas"""
        today = fields.Datetime.now()
        threshold_date = today + timedelta(days=90)
        
        # Buscar lotes que vencen en los próximos 90 días y no tienen alerta
        lots = self.search([
            ('expiration_date', '<=', threshold_date),
            ('expiration_date', '>=', today),
            ('alert_sent', '=', False),
            ('quality_state', '=', 'pass'),
        ])
        
        for lot in lots:
            lot._create_expiry_alert()
        
        return True
    
    def get_expiry_warning(self):
        """Retorna un mensaje de advertencia sobre el vencimiento"""
        self.ensure_one()
        
        if self.expiry_state == 'expired':
            return _('⚠️ LOTE VENCIDO: Este lote expiró el %s') % self.expiration_date
        elif self.expiry_state == 'alert_30':
            return _('⚠️ VENCE PRONTO: Este lote vence en %d días') % self.days_to_expiry
        elif self.expiry_state == 'alert_60':
            return _('⚠️ ALERTA: Este lote vence en %d días') % self.days_to_expiry
        elif self.expiry_state == 'alert_90':
            return _('ℹ️ ATENCIÓN: Este lote vence en %d días') % self.days_to_expiry
        
        return ''

