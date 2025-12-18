# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountMove(models.Model):
    """
    Extensión del modelo de facturas para integración con planillas de despacho.
    """
    _inherit = 'account.move'
    
    # ========== RELACIÓN CON PLANILLAS ==========
    dispatch_sheet_ids = fields.Many2many(
        'dispatch.sheet',
        'dispatch_sheet_invoice_rel',
        'invoice_id',
        'sheet_id',
        string='Planillas de Despacho',
        help='Planillas en las que está incluida esta factura'
    )
    
    dispatch_sheet_count = fields.Integer(
        string='Cantidad de Planillas',
        compute='_compute_dispatch_sheet_count',
        help='Número de planillas asociadas a esta factura'
    )
    
    @api.depends('dispatch_sheet_ids')
    def _compute_dispatch_sheet_count(self):
        """Calcula la cantidad de planillas"""
        for move in self:
            move.dispatch_sheet_count = len(move.dispatch_sheet_ids)
    
    def action_view_dispatch_sheets(self):
        """Ver planillas asociadas a esta factura"""
        self.ensure_one()
        return {
            'name': _('Planillas de %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'dispatch.sheet',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.dispatch_sheet_ids.ids)],
        }

