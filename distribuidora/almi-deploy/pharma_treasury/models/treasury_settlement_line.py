# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class TreasurySettlementLine(models.Model):
    """
    Modelo para líneas de liquidación.
    Cada línea representa el detalle de cobro de una factura específica.
    """
    _name = 'treasury.settlement.line'
    _description = 'Línea de Liquidación'
    _order = 'settlement_id, sequence, id'
    
    # ========== RELACIÓN CON LIQUIDACIÓN ==========
    settlement_id = fields.Many2one(
        'treasury.settlement',
        string='Liquidación',
        required=True,
        ondelete='cascade',
        index=True,
        help='Liquidación a la que pertenece esta línea'
    )
    
    settlement_state = fields.Selection(
        related='settlement_id.state',
        string='Estado de Liquidación',
        store=True,
        readonly=True
    )
    
    sequence = fields.Integer(
        string='Secuencia',
        default=10,
        help='Orden de visualización'
    )
    
    # ========== RELACIÓN CON PLANILLA ==========
    sheet_line_id = fields.Many2one(
        'treasury.settlement.sheet.line',
        string='Línea de Planilla',
        help='Línea de planilla asociada'
    )
    
    sheet_id = fields.Many2one(
        'treasury.settlement.sheet',
        string='Planilla',
        related='sheet_line_id.sheet_id',
        store=True,
        readonly=True
    )
    
    # ========== FACTURA ==========
    invoice_id = fields.Many2one(
        'account.move',
        string='Factura',
        required=True,
        domain="[('move_type', '=', 'out_invoice'), ('state', '=', 'posted')]",
        help='Factura cobrada'
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
        readonly=True
    )
    
    partner_street = fields.Char(
        related='partner_id.street',
        string='Dirección',
        readonly=True
    )
    
    # ========== MONTOS ==========
    amount_invoice = fields.Monetary(
        string='Monto Factura',
        required=True,
        currency_field='currency_id',
        help='Monto total de la factura'
    )
    
    amount_collected = fields.Monetary(
        string='Monto Cobrado',
        currency_field='currency_id',
        default=0.0,
        help='Monto efectivamente cobrado'
    )
    
    amount_difference = fields.Monetary(
        string='Diferencia',
        compute='_compute_difference',
        store=True,
        currency_field='currency_id',
        help='Diferencia entre factura y cobrado'
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
        ('delivered', 'Entregado'),
        ('not_delivered', 'No Entregado'),
    ], string='Estado de Entrega',
       default='delivered',
       required=True,
       help='Indica si se entregó el producto')
    
    delivery_notes = fields.Text(
        string='Observaciones de Entrega',
        help='Notas sobre la entrega o motivo de no entrega'
    )
    
    delivery_datetime = fields.Datetime(
        string='Fecha/Hora de Entrega',
        help='Momento en que se realizó la entrega'
    )
    
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
    
    # ========== EVIDENCIA ==========
    collection_evidence = fields.Binary(
        string='Evidencia de Cobro',
        attachment=True,
        help='Foto de comprobante, firma del cliente, etc.'
    )
    
    collection_evidence_filename = fields.Char(
        string='Nombre de Archivo'
    )
    
    signature = fields.Binary(
        string='Firma del Cliente',
        attachment=True,
        help='Firma digital del cliente'
    )
    
    # ========== OBSERVACIONES ==========
    notes = fields.Text(
        string='Notas',
        help='Observaciones adicionales'
    )
    
    # ========== GEOLOCALIZACIÓN (para app móvil) ==========
    latitude = fields.Float(
        string='Latitud',
        digits=(10, 6),
        help='Coordenada de latitud donde se realizó el cobro'
    )
    
    longitude = fields.Float(
        string='Longitud',
        digits=(10, 6),
        help='Coordenada de longitud donde se realizó el cobro'
    )
    
    # ========== OTROS ==========
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        related='settlement_id.company_id',
        store=True,
        readonly=True
    )
    
    @api.depends('amount_invoice', 'amount_collected')
    def _compute_difference(self):
        """Calcula la diferencia entre lo esperado y lo cobrado"""
        for line in self:
            line.amount_difference = line.amount_invoice - line.amount_collected
    
    @api.constrains('amount_collected')
    def _check_amount_collected(self):
        """Valida que el monto cobrado sea válido"""
        for line in self:
            if line.amount_collected < 0:
                raise ValidationError(_(
                    'El monto cobrado no puede ser negativo.'
                ))
            
            # Si está entregado pero el monto es 0, mostrar advertencia
            if line.delivery_status == 'delivered' and line.amount_collected == 0:
                # Permitir pero registrar en el chatter
                if line.settlement_id:
                    line.settlement_id.message_post(
                        body=_('⚠️ La factura %s está marcada como entregada pero sin cobro') % line.invoice_name
                    )
    
    @api.constrains('delivery_status', 'amount_collected')
    def _check_delivery_collection_consistency(self):
        """Valida consistencia entre entrega y cobro"""
        for line in self:
            # Si no se entregó, el monto cobrado debería ser 0
            if line.delivery_status == 'not_delivered' and line.amount_collected > 0:
                raise ValidationError(_(
                    'Si la factura %s no fue entregada, el monto cobrado debe ser 0.'
                ) % line.invoice_name)
    
    @api.onchange('delivery_status')
    def _onchange_delivery_status(self):
        """Ajusta el monto cobrado según el estado de entrega"""
        if self.delivery_status == 'not_delivered':
            self.amount_collected = 0.0
            self.payment_method = 'none'
        elif self.delivery_status == 'delivered' and self.amount_collected == 0:
            # Sugerir el monto total
            self.amount_collected = self.amount_invoice
    
    @api.onchange('invoice_id')
    def _onchange_invoice_id(self):
        """Carga datos de la factura al seleccionarla"""
        if self.invoice_id:
            self.amount_invoice = self.invoice_id.amount_total
            # Sugerir cobro total
            if not self.amount_collected:
                self.amount_collected = self.amount_invoice
    
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
    
    def action_mark_delivered(self):
        """Marca como entregado"""
        for line in self:
            line.write({
                'delivery_status': 'delivered',
                'delivery_datetime': fields.Datetime.now(),
            })
    
    def action_mark_not_delivered(self):
        """Marca como no entregado"""
        for line in self:
            line.write({
                'delivery_status': 'not_delivered',
                'amount_collected': 0.0,
                'payment_method': 'none',
            })


class TreasurySettlementRejectWizard(models.TransientModel):
    """
    Wizard para rechazar una liquidación con motivo.
    """
    _name = 'treasury.settlement.reject.wizard'
    _description = 'Wizard de Rechazo de Liquidación'
    
    settlement_id = fields.Many2one(
        'treasury.settlement',
        string='Liquidación',
        required=True,
        readonly=True
    )
    
    rejection_reason = fields.Text(
        string='Motivo de Rechazo',
        required=True,
        help='Explique por qué se rechaza esta liquidación'
    )
    
    def action_reject(self):
        """Rechaza la liquidación con el motivo especificado"""
        self.ensure_one()
        
        self.settlement_id.write({
            'rejection_reason': self.rejection_reason
        })
        
        self.settlement_id.action_reject()
        
        return {'type': 'ir.actions.act_window_close'}

