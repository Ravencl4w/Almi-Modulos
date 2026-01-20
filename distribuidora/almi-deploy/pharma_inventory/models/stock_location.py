# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class StockLocation(models.Model):
    """
    Extensión del modelo stock.location para control de temperatura
    en almacenes y ubicaciones farmacéuticas.
    """
    _inherit = 'stock.location'
    
    # ========== CONTROL DE TEMPERATURA ==========
    requires_temperature_control = fields.Boolean(
        string='Requiere Control de Temperatura',
        default=False,
        help='Indica si esta ubicación requiere monitoreo de temperatura'
    )
    
    temperature_min = fields.Float(
        string='Temperatura Mínima (°C)',
        help='Temperatura mínima permitida en esta ubicación'
    )
    
    temperature_max = fields.Float(
        string='Temperatura Máxima (°C)',
        help='Temperatura máxima permitida en esta ubicación'
    )
    
    current_temperature = fields.Float(
        string='Temperatura Actual (°C)',
        compute='_compute_current_temperature',
        help='Última temperatura registrada'
    )
    
    temperature_state = fields.Selection([
        ('ok', 'OK'),
        ('warning', 'Fuera de Rango'),
        ('critical', 'Crítico'),
        ('no_control', 'Sin Control'),
    ], string='Estado de Temperatura',
       compute='_compute_temperature_state',
       help='Estado del control de temperatura')
    
    last_temperature_check = fields.Datetime(
        string='Última Verificación',
        compute='_compute_current_temperature',
        help='Fecha y hora de la última lectura de temperatura'
    )
    
    temperature_record_ids = fields.One2many(
        'stock.temperature.record',
        'location_id',
        string='Registros de Temperatura',
        help='Histórico de registros de temperatura'
    )
    
    temperature_record_count = fields.Integer(
        string='Registros de Temperatura',
        compute='_compute_temperature_record_count',
        store=True,
        help='Cantidad de registros de temperatura'
    )
    
    # ========== TIPO DE UBICACIÓN ==========
    location_type = fields.Selection([
        ('normal', 'Normal'),
        ('cold_storage', 'Cámara Fría'),
        ('freezer', 'Congelador'),
        ('quarantine', 'Cuarentena'),
        ('rejected', 'Rechazados'),
        ('expired', 'Vencidos'),
    ], string='Tipo de Ubicación',
       default='normal',
       help='Tipo especializado de ubicación')
    
    is_quarantine = fields.Boolean(
        string='Es Cuarentena',
        compute='_compute_is_quarantine',
        store=True,
        help='Indica si es una ubicación de cuarentena'
    )
    
    is_rejection_area = fields.Boolean(
        string='Es Área de Rechazo',
        compute='_compute_is_rejection_area',
        store=True,
        help='Indica si es una ubicación para productos rechazados'
    )
    
    # ========== ALERTAS ==========
    alert_email = fields.Char(
        string='Email de Alerta',
        help='Email para enviar alertas de temperatura'
    )
    
    alert_responsible_id = fields.Many2one(
        'res.users',
        string='Responsable de Alertas',
        help='Usuario responsable de monitorear esta ubicación'
    )
    
    # ========== CAMPOS COMPUTADOS ==========
    
    @api.depends('temperature_record_ids')
    def _compute_current_temperature(self):
        """Obtiene la temperatura más reciente"""
        for location in self:
            if location.temperature_record_ids:
                last_record = location.temperature_record_ids[0]  # Ordenado por fecha desc
                location.current_temperature = last_record.temperature
                location.last_temperature_check = last_record.record_date
            else:
                location.current_temperature = 0.0
                location.last_temperature_check = False
    
    @api.depends('requires_temperature_control', 'current_temperature', 'temperature_min', 'temperature_max')
    def _compute_temperature_state(self):
        """Calcula el estado de temperatura"""
        for location in self:
            if not location.requires_temperature_control:
                location.temperature_state = 'no_control'
            elif not location.current_temperature and not location.last_temperature_check:
                location.temperature_state = 'no_control'
            elif location.temperature_min and location.temperature_max:
                temp = location.current_temperature
                
                # Margen de tolerancia
                margin = 2.0
                
                if temp < (location.temperature_min - margin) or temp > (location.temperature_max + margin):
                    location.temperature_state = 'critical'
                elif temp < location.temperature_min or temp > location.temperature_max:
                    location.temperature_state = 'warning'
                else:
                    location.temperature_state = 'ok'
            else:
                location.temperature_state = 'no_control'
    
    @api.depends('location_type')
    def _compute_is_quarantine(self):
        """Determina si es ubicación de cuarentena"""
        for location in self:
            location.is_quarantine = location.location_type == 'quarantine'
    
    @api.depends('location_type')
    def _compute_is_rejection_area(self):
        """Determina si es área de rechazo"""
        for location in self:
            location.is_rejection_area = location.location_type in ['rejected', 'expired']
    
    @api.depends('temperature_record_ids')
    def _compute_temperature_record_count(self):
        """Cuenta los registros de temperatura"""
        for location in self:
            location.temperature_record_count = len(location.temperature_record_ids)
    
    # ========== VALIDACIONES ==========
    
    @api.constrains('temperature_min', 'temperature_max')
    def _check_temperature_range(self):
        """Valida que el rango de temperatura sea coherente"""
        for location in self:
            if location.requires_temperature_control:
                if location.temperature_min and location.temperature_max:
                    if location.temperature_min >= location.temperature_max:
                        raise ValidationError(
                            _('La temperatura mínima debe ser menor que la máxima.')
                        )
    
    # ========== MÉTODOS DE NEGOCIO ==========
    
    def action_register_temperature(self):
        """Abre el wizard para registrar temperatura"""
        self.ensure_one()
        
        return {
            'name': _('Registrar Temperatura'),
            'type': 'ir.actions.act_window',
            'res_model': 'register.temperature.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_location_id': self.id,
                'default_temperature_min': self.temperature_min,
                'default_temperature_max': self.temperature_max,
            }
        }
    
    def action_view_temperature_history(self):
        """Ver el histórico de temperaturas"""
        self.ensure_one()
        
        return {
            'name': _('Histórico de Temperatura - %s') % self.display_name,
            'type': 'ir.actions.act_window',
            'res_model': 'stock.temperature.record',
            'view_mode': 'list,form,graph',
            'domain': [('location_id', '=', self.id)],
            'context': {'default_location_id': self.id}
        }
    
    def _check_temperature_alerts(self):
        """Verifica si hay alertas de temperatura pendientes"""
        for location in self:
            if location.temperature_state in ['warning', 'critical']:
                # Enviar notificación
                if location.alert_responsible_id:
                    location._send_temperature_alert()
    
    def _send_temperature_alert(self):
        """Envía alerta de temperatura"""
        self.ensure_one()
        
        # Aquí se podría implementar el envío de email o notificación
        # Por ahora, crear una actividad para el responsable
        if self.alert_responsible_id:
            self.env['mail.activity'].create({
                'activity_type_id': self.env.ref('mail.mail_activity_data_warning').id,
                'note': _('Alerta de temperatura en %s: Temperatura actual %.1f°C (Rango: %.1f - %.1f°C)') % (
                    self.display_name,
                    self.current_temperature,
                    self.temperature_min,
                    self.temperature_max
                ),
                'user_id': self.alert_responsible_id.id,
                'res_model_id': self.env['ir.model']._get('stock.location').id,
                'res_id': self.id,
            })

