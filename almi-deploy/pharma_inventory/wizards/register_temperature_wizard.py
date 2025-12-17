# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class RegisterTemperatureWizard(models.TransientModel):
    """
    Wizard para registro rápido de temperatura.
    """
    _name = 'register.temperature.wizard'
    _description = 'Registrar Temperatura'
    
    location_id = fields.Many2one(
        'stock.location',
        string='Ubicación',
        required=True
    )
    
    temperature = fields.Float(
        string='Temperatura (°C)',
        required=True,
        digits=(5, 2)
    )
    
    humidity = fields.Float(
        string='Humedad (%)',
        digits=(5, 2)
    )
    
    notes = fields.Text(
        string='Observaciones'
    )
    
    equipment = fields.Char(
        string='Equipo/Termómetro'
    )
    
    def action_register(self):
        """Registra la temperatura"""
        self.env['stock.temperature.record'].create({
            'location_id': self.location_id.id,
            'temperature': self.temperature,
            'humidity': self.humidity,
            'notes': self.notes,
            'equipment': self.equipment,
        })
        
        return {'type': 'ir.actions.act_window_close'}

