# -*- coding: utf-8 -*-

from odoo import api, fields, models


class StockQuant(models.Model):
    """
    Extensión de stock.quant para mostrar información de vencimiento.
    """
    _inherit = 'stock.quant'
    
    lot_expiry_date = fields.Datetime(
        related='lot_id.expiration_date',
        string='Fecha de Vencimiento',
        readonly=True,
        store=True
    )
    
    lot_expiry_state = fields.Selection(
        related='lot_id.expiry_state',
        string='Estado de Vencimiento',
        readonly=True,
        store=True
    )
    
    lot_days_to_expiry = fields.Integer(
        related='lot_id.days_to_expiry',
        string='Días para Vencer',
        readonly=True,
        store=True
    )
    
    lot_exchange_state = fields.Selection(
        related='lot_id.exchange_state',
        string='Estado de Canje',
        readonly=True
    )
    
    requires_cold_chain = fields.Boolean(
        related='product_id.cold_chain',
        string='Cadena de Frío',
        readonly=True
    )

