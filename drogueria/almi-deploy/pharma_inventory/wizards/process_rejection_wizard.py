# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ProcessRejectionWizard(models.TransientModel):
    """
    Wizard para procesar rechazos de productos.
    """
    _name = 'process.rejection.wizard'
    _description = 'Procesar Rechazo'
    
    lot_id = fields.Many2one(
        'stock.lot',
        string='Lote',
        required=True
    )
    
    rejection_reason = fields.Text(
        string='Motivo de Rechazo',
        required=True
    )
    
    def action_confirm(self):
        """Confirma el rechazo"""
        self.lot_id.write({
            'quality_state': 'rejected',
            'rejection_reason': self.rejection_reason,
        })
        
        return {'type': 'ir.actions.act_window_close'}

