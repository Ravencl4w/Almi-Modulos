# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class TreasurySettlementSheetLine(models.Model):
    """
    Modelo para líneas de planilla de reparto.
    Cada línea representa una factura incluida en la planilla.
    """
    _name = 'treasury.settlement.sheet.line'
    _description = 'Línea de Planilla de Reparto'
    _order = 'sequence, id'
    
    # ========== RELACIÓN CON PLANILLA ==========
    sheet_id = fields.Many2one(
        'treasury.settlement.sheet',
        string='Planilla',
        required=True,
        ondelete='cascade',
        index=True,
        help='Planilla a la que pertenece esta línea'
    )
    
    sheet_state = fields.Selection(
        related='sheet_id.state',
        string='Estado de Planilla',
        store=True,
        readonly=True
    )
    
    sequence = fields.Integer(
        string='Secuencia',
        default=10,
        help='Orden de entrega'
    )
    
    # ========== FACTURA ==========
    invoice_id = fields.Many2one(
        'account.move',
        string='Factura',
        required=True,
        domain="[('move_type', '=', 'out_invoice'), ('state', '=', 'posted'), ('payment_state', 'in', ['not_paid', 'partial'])]",
        index=True,
        help='Factura a cobrar'
    )
    
    invoice_name = fields.Char(
        related='invoice_id.name',
        string='Número de Factura',
        store=True,
        readonly=True
    )
    
    invoice_date = fields.Date(
        related='invoice_id.invoice_date',
        string='Fecha de Factura',
        store=True,
        readonly=True
    )
    
    # ========== CLIENTE ==========
    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        related='invoice_id.partner_id',
        store=True,
        readonly=True,
        help='Cliente de la factura'
    )
    
    partner_street = fields.Char(
        related='partner_id.street',
        string='Dirección',
        readonly=True
    )
    
    partner_city = fields.Char(
        related='partner_id.city',
        string='Ciudad',
        readonly=True
    )
    
    partner_phone = fields.Char(
        related='partner_id.phone',
        string='Teléfono',
        readonly=True
    )
    
    sale_zone_id = fields.Many2one(
        'sale.zone',
        string='Zona de Venta',
        related='partner_id.sale_zone_id',
        store=True,
        readonly=True
    )
    
    # ========== MONTOS ==========
    amount_total = fields.Monetary(
        string='Monto Total',
        related='invoice_id.amount_total',
        store=True,
        readonly=True,
        currency_field='currency_id',
        help='Monto total de la factura'
    )
    
    amount_residual = fields.Monetary(
        string='Saldo Pendiente',
        related='invoice_id.amount_residual',
        store=True,
        readonly=True,
        currency_field='currency_id',
        help='Saldo pendiente de pago'
    )
    
    amount_collected = fields.Monetary(
        string='Monto Cobrado',
        currency_field='currency_id',
        default=0.0,
        help='Monto efectivamente cobrado por el transportista'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        related='invoice_id.currency_id',
        store=True,
        readonly=True
    )
    
    # ========== ESTADO DE ENTREGA ==========
    delivery_status = fields.Selection([
        ('pending', 'Pendiente'),
        ('delivered', 'Entregado'),
        ('not_delivered', 'No Entregado'),
    ], string='Estado de Entrega',
       default='pending',
       required=True,
       help='Estado de la entrega del pedido')
    
    delivery_notes = fields.Text(
        string='Observaciones de Entrega',
        help='Notas sobre la entrega o motivo de no entrega'
    )
    
    # ========== ESTADO DE COBRANZA ==========
    collection_status = fields.Selection([
        ('not_collected', 'No Cobrado'),
        ('partial', 'Cobrado Parcial'),
        ('collected', 'Cobrado Total'),
    ], string='Estado de Cobranza',
       compute='_compute_collection_status',
       store=True,
       help='Estado de la cobranza')
    
    # ========== MÉTODO DE PAGO ==========
    payment_method = fields.Selection([
        ('cash', 'Efectivo'),
        ('transfer', 'Transferencia'),
        ('card', 'Tarjeta'),
        ('mixed', 'Mixto'),
        ('none', 'Sin Cobro'),
    ], string='Método de Pago',
       help='Método utilizado para el pago')
    
    payment_reference = fields.Char(
        string='Referencia de Pago',
        help='Número de operación, voucher, etc.'
    )
    
    # ========== PEDIDO DE VENTA ==========
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Pedido de Venta',
        compute='_compute_sale_order',
        store=True,
        help='Pedido de venta asociado a la factura'
    )
    
    # ========== OTROS CAMPOS ==========
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        related='sheet_id.company_id',
        store=True,
        readonly=True
    )
    
    notes = fields.Text(
        string='Notas',
        help='Notas adicionales sobre esta línea'
    )
    
    @api.depends('invoice_id')
    def _compute_sale_order(self):
        """Obtiene el pedido de venta relacionado con la factura"""
        for line in self:
            if line.invoice_id:
                # Buscar el pedido de venta a través de invoice_line_ids
                sale_order = self.env['sale.order'].search([
                    ('invoice_ids', 'in', line.invoice_id.ids)
                ], limit=1)
                line.sale_order_id = sale_order
            else:
                line.sale_order_id = False
    
    @api.depends('amount_total', 'amount_collected')
    def _compute_collection_status(self):
        """Calcula el estado de cobranza según el monto cobrado"""
        for line in self:
            if line.amount_collected <= 0:
                line.collection_status = 'not_collected'
            elif line.amount_collected >= line.amount_total:
                line.collection_status = 'collected'
            else:
                line.collection_status = 'partial'
    
    @api.constrains('invoice_id', 'sheet_id')
    def _check_invoice_unique(self):
        """Valida que una factura no esté en múltiples planillas activas"""
        for line in self:
            if line.sheet_id.state not in ['cancelled']:
                # Buscar otras planillas activas con la misma factura
                other_lines = self.search([
                    ('id', '!=', line.id),
                    ('invoice_id', '=', line.invoice_id.id),
                    ('sheet_id.state', 'not in', ['cancelled', 'closed'])
                ])
                
                if other_lines:
                    raise ValidationError(_(
                        'La factura %s ya está incluida en la planilla %s. '
                        'Una factura no puede estar en múltiples planillas activas.'
                    ) % (line.invoice_name, other_lines[0].sheet_id.name))
    
    @api.constrains('invoice_id')
    def _check_invoice_state(self):
        """Valida que la factura esté confirmada"""
        for line in self:
            if line.invoice_id.state != 'posted':
                raise ValidationError(_(
                    'Solo se pueden agregar facturas confirmadas (posted) a la planilla. '
                    'Estado actual de %s: %s'
                ) % (line.invoice_name, line.invoice_id.state))
    
    @api.constrains('amount_collected')
    def _check_amount_collected(self):
        """Valida que el monto cobrado no sea negativo ni mayor al total"""
        for line in self:
            if line.amount_collected < 0:
                raise ValidationError(_(
                    'El monto cobrado no puede ser negativo.'
                ))
            
            # Permitir cobros mayores al total (por ejemplo, si hay intereses)
            # pero mostrar advertencia
            if line.amount_collected > line.amount_total * 1.1:  # 10% de margen
                raise ValidationError(_(
                    'El monto cobrado (%s) es significativamente mayor al total de la factura (%s). '
                    'Verifique que sea correcto.'
                ) % (line.amount_collected, line.amount_total))
    
    def action_mark_delivered(self):
        """Marca la línea como entregada"""
        for line in self:
            line.write({'delivery_status': 'delivered'})
    
    def action_mark_not_delivered(self):
        """Marca la línea como no entregada"""
        for line in self:
            line.write({'delivery_status': 'not_delivered'})
    
    def action_view_invoice(self):
        """Abre la factura asociada"""
        self.ensure_one()
        return {
            'name': _('Factura'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': self.invoice_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_view_sale_order(self):
        """Abre el pedido de venta asociado"""
        self.ensure_one()
        if not self.sale_order_id:
            raise ValidationError(_('Esta factura no tiene un pedido de venta asociado.'))
        
        return {
            'name': _('Pedido de Venta'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id': self.sale_order_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

