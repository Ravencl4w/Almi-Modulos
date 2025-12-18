# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class StockTemperatureRecord(models.Model):
    """
    Modelo para registrar lecturas de temperatura en ubicaciones de almacén.
    Permite trazabilidad y cumplimiento regulatorio.
    """
    _name = 'stock.temperature.record'
    _description = 'Registro de Temperatura'
    _order = 'record_date desc, id desc'
    _rec_name = 'display_name'
    
    display_name = fields.Char(
        string='Nombre',
        compute='_compute_display_name',
        store=True
    )
    
    location_id = fields.Many2one(
        'stock.location',
        string='Ubicación',
        required=True,
        ondelete='cascade',
        help='Ubicación donde se registró la temperatura'
    )
    
    location_name = fields.Char(
        string='Nombre de Ubicación',
        related='location_id.display_name',
        store=True,
        readonly=True
    )
    
    record_date = fields.Datetime(
        string='Fecha y Hora',
        required=True,
        default=fields.Datetime.now,
        help='Fecha y hora del registro'
    )
    
    temperature = fields.Float(
        string='Temperatura (°C)',
        required=True,
        digits=(5, 2),
        help='Temperatura registrada en grados Celsius'
    )
    
    humidity = fields.Float(
        string='Humedad (%)',
        digits=(5, 2),
        help='Humedad relativa registrada (opcional)'
    )
    
    temperature_min = fields.Float(
        string='Temp. Mínima Permitida',
        related='location_id.temperature_min',
        readonly=True
    )
    
    temperature_max = fields.Float(
        string='Temp. Máxima Permitida',
        related='location_id.temperature_max',
        readonly=True
    )
    
    state = fields.Selection([
        ('ok', 'OK'),
        ('warning', 'Fuera de Rango'),
        ('critical', 'Crítico'),
    ], string='Estado',
       compute='_compute_state',
       store=True,
       help='Estado del registro según temperatura')
    
    recorded_by = fields.Many2one(
        'res.users',
        string='Registrado Por',
        default=lambda self: self.env.user,
        required=True,
        help='Usuario que registró la temperatura'
    )
    
    notes = fields.Text(
        string='Observaciones',
        help='Observaciones sobre la lectura'
    )
    
    corrective_action = fields.Text(
        string='Acción Correctiva',
        help='Acción correctiva tomada si la temperatura está fuera de rango'
    )
    
    equipment = fields.Char(
        string='Equipo/Termómetro',
        help='Identificación del equipo utilizado para medir'
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        default=lambda self: self.env.company,
        required=True
    )
    
    alert_sent = fields.Boolean(
        string='Alerta Enviada',
        default=False,
        help='Indica si se envió alerta por temperatura fuera de rango'
    )
    
    @api.depends('location_id', 'record_date', 'temperature')
    def _compute_display_name(self):
        """Genera el nombre descriptivo del registro"""
        for record in self:
            if record.location_id and record.record_date:
                date_str = fields.Datetime.context_timestamp(
                    record, record.record_date
                ).strftime('%d/%m/%Y %H:%M')
                record.display_name = f"{record.location_id.display_name} - {date_str} - {record.temperature}°C"
            else:
                record.display_name = _('Nuevo Registro')
    
    @api.depends('temperature', 'temperature_min', 'temperature_max')
    def _compute_state(self):
        """Calcula el estado según la temperatura"""
        for record in self:
            if record.temperature_min and record.temperature_max:
                temp = record.temperature
                margin = 2.0  # Margen de tolerancia
                
                if temp < (record.temperature_min - margin) or temp > (record.temperature_max + margin):
                    record.state = 'critical'
                elif temp < record.temperature_min or temp > record.temperature_max:
                    record.state = 'warning'
                else:
                    record.state = 'ok'
            else:
                record.state = 'ok'
    
    @api.constrains('temperature')
    def _check_temperature(self):
        """Valida que la temperatura sea un valor razonable"""
        for record in self:
            if record.temperature < -100 or record.temperature > 100:
                raise ValidationError(
                    _('La temperatura debe estar entre -100°C y 100°C.')
                )
    
    @api.constrains('humidity')
    def _check_humidity(self):
        """Valida que la humedad esté en rango válido"""
        for record in self:
            if record.humidity and (record.humidity < 0 or record.humidity > 100):
                raise ValidationError(
                    _('La humedad debe estar entre 0% y 100%.')
                )
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override create para enviar alertas si es necesario"""
        records = super().create(vals_list)
        
        for record in records:
            if record.state in ['warning', 'critical']:
                record._send_temperature_alert()
        
        return records
    
    def _send_temperature_alert(self):
        """Envía alerta si la temperatura está fuera de rango"""
        self.ensure_one()
        
        if self.alert_sent:
            return
        
        # Enviar alerta al responsable de la ubicación
        if self.location_id.alert_responsible_id:
            self.env['mail.activity'].create({
                'activity_type_id': self.env.ref('mail.mail_activity_data_warning').id,
                'note': _(
                    'Temperatura fuera de rango en %s:\n'
                    'Temperatura registrada: %.1f°C\n'
                    'Rango permitido: %.1f - %.1f°C\n'
                    'Estado: %s'
                ) % (
                    self.location_id.display_name,
                    self.temperature,
                    self.temperature_min,
                    self.temperature_max,
                    dict(self._fields['state'].selection).get(self.state)
                ),
                'user_id': self.location_id.alert_responsible_id.id,
                'res_model_id': self.env['ir.model']._get('stock.temperature.record').id,
                'res_id': self.id,
            })
            
            self.alert_sent = True

