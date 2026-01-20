# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountMove(models.Model):
    """
    Extensión del modelo account.move para integración con tesorería.
    Agrega tracking de planillas de reparto y estado de cobranza.
    """
    _inherit = 'account.move'
    
    # ========== PLANILLA DE REPARTO ==========
    settlement_sheet_id = fields.Many2one(
        'treasury.settlement.sheet',
        string='Planilla de Reparto',
        compute='_compute_settlement_sheet',
        store=True,
        help='Planilla en la que está incluida esta factura'
    )
    
    settlement_sheet_line_id = fields.Many2one(
        'treasury.settlement.sheet.line',
        string='Línea de Planilla',
        help='Línea específica de planilla'
    )
    
    in_settlement = fields.Boolean(
        string='En Planilla',
        compute='_compute_in_settlement',
        store=True,
        help='Indica si está incluida en una planilla activa'
    )
    
    sheet_state = fields.Selection(
        related='settlement_sheet_id.state',
        string='Estado de Planilla',
        store=True,
        readonly=True
    )
    
    # ========== ESTADO DE COBRANZA ==========
    collection_status = fields.Selection([
        ('not_collected', 'No Cobrado'),
        ('partial', 'Cobro Parcial'),
        ('collected', 'Cobrado Total'),
    ], string='Estado de Cobranza',
       compute='_compute_collection_status',
       store=True,
       help='Estado de cobranza según liquidación')
    
    amount_collected = fields.Monetary(
        string='Monto Cobrado',
        currency_field='currency_id',
        default=0.0,
        help='Monto cobrado según liquidación aprobada'
    )
    
    collection_date = fields.Date(
        string='Fecha de Cobro',
        help='Fecha en que se cobró según liquidación'
    )
    
    collection_method = fields.Selection([
        ('cash', 'Efectivo'),
        ('transfer', 'Transferencia'),
        ('card', 'Tarjeta'),
        ('mixed', 'Mixto'),
    ], string='Método de Cobro',
       help='Método utilizado para el cobro')
    
    # ========== ENTREGA ==========
    delivery_status = fields.Selection([
        ('pending', 'Pendiente'),
        ('delivered', 'Entregado'),
        ('not_delivered', 'No Entregado'),
    ], string='Estado de Entrega',
       default='pending',
       help='Estado de entrega del producto')
    
    delivery_notes = fields.Text(
        string='Notas de Entrega',
        help='Observaciones sobre la entrega'
    )
    
    # ========== HOJA DE COBRANZA POR VENDEDOR ==========
    collection_sheet_ids = fields.Many2many(
        'treasury.collection.sheet',
        'collection_sheet_invoice_rel',
        'invoice_id',
        'sheet_id',
        string='Hojas de Cobranza',
        help='Hojas de cobranza donde está incluida'
    )
    
    collection_sheet_count = fields.Integer(
        string='Hojas de Cobranza',
        compute='_compute_collection_sheet_count',
        help='Número de hojas de cobranza'
    )
    
    @api.depends('settlement_sheet_line_id', 'settlement_sheet_line_id.sheet_id')
    def _compute_settlement_sheet(self):
        """Calcula la planilla asociada"""
        for move in self:
            if move.settlement_sheet_line_id:
                move.settlement_sheet_id = move.settlement_sheet_line_id.sheet_id
            else:
                move.settlement_sheet_id = False
    
    @api.depends('settlement_sheet_id', 'settlement_sheet_id.state')
    def _compute_in_settlement(self):
        """Verifica si está en una planilla activa"""
        for move in self:
            move.in_settlement = bool(
                move.settlement_sheet_id and 
                move.settlement_sheet_id.state not in ['cancelled', 'closed']
            )
    
    @api.depends('amount_collected', 'amount_total')
    def _compute_collection_status(self):
        """Calcula el estado de cobranza"""
        for move in self:
            if move.amount_collected <= 0:
                move.collection_status = 'not_collected'
            elif move.amount_collected >= move.amount_total:
                move.collection_status = 'collected'
            else:
                move.collection_status = 'partial'
    
    @api.depends('collection_sheet_ids')
    def _compute_collection_sheet_count(self):
        """Cuenta las hojas de cobranza"""
        for move in self:
            move.collection_sheet_count = len(move.collection_sheet_ids)
    
    def action_view_settlement_sheet(self):
        """Ver planilla de reparto"""
        self.ensure_one()
        
        if not self.settlement_sheet_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Sin Planilla'),
                    'message': _('Esta factura no está incluida en ninguna planilla de reparto.'),
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
        return {
            'name': _('Planilla de Reparto'),
            'type': 'ir.actions.act_window',
            'res_model': 'treasury.settlement.sheet',
            'res_id': self.settlement_sheet_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_view_collection_sheets(self):
        """Ver hojas de cobranza"""
        self.ensure_one()
        
        return {
            'name': _('Hojas de Cobranza'),
            'type': 'ir.actions.act_window',
            'res_model': 'treasury.collection.sheet',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.collection_sheet_ids.ids)],
        }
    
    def action_add_to_settlement_sheet(self):
        """Abre wizard para agregar a una planilla"""
        self.ensure_one()
        
        if self.move_type != 'out_invoice':
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Error'),
                    'message': _('Solo las facturas de cliente pueden agregarse a planillas.'),
                    'type': 'danger',
                    'sticky': False,
                }
            }
        
        if self.state != 'posted':
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Error'),
                    'message': _('Solo las facturas confirmadas pueden agregarse a planillas.'),
                    'type': 'danger',
                    'sticky': False,
                }
            }
        
        if self.in_settlement:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Error'),
                    'message': _('Esta factura ya está en la planilla %s.') % self.settlement_sheet_id.name,
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
        # Buscar planillas en borrador
        sheets = self.env['treasury.settlement.sheet'].search([
            ('state', '=', 'draft')
        ], order='date desc')
        
        if not sheets:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Sin Planillas'),
                    'message': _('No hay planillas en borrador disponibles. Cree una nueva planilla primero.'),
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
        return {
            'name': _('Agregar a Planilla'),
            'type': 'ir.actions.act_window',
            'res_model': 'treasury.add.invoice.to.sheet.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_invoice_id': self.id,
            }
        }


class TreasuryAddInvoiceToSheetWizard(models.TransientModel):
    """
    Wizard para agregar una factura individual a una planilla.
    """
    _name = 'treasury.add.invoice.to.sheet.wizard'
    _description = 'Agregar Factura a Planilla'
    
    invoice_id = fields.Many2one(
        'account.move',
        string='Factura',
        required=True,
        readonly=True
    )
    
    sheet_id = fields.Many2one(
        'treasury.settlement.sheet',
        string='Planilla',
        required=True,
        domain=[('state', '=', 'draft')],
        help='Planilla a la que se agregará la factura'
    )
    
    def action_add(self):
        """Agrega la factura a la planilla"""
        self.ensure_one()
        
        # Obtener última secuencia
        last_sequence = 0
        if self.sheet_id.line_ids:
            last_sequence = max(self.sheet_id.line_ids.mapped('sequence'))
        
        # Crear línea
        self.env['treasury.settlement.sheet.line'].create({
            'sheet_id': self.sheet_id.id,
            'invoice_id': self.invoice_id.id,
            'sequence': last_sequence + 10,
        })
        
        return {'type': 'ir.actions.act_window_close'}

