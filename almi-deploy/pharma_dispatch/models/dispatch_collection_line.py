# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class DispatchCollectionLine(models.Model):
    """
    Modelo para gestionar líneas de cobranza.
    Cada línea representa un pago recibido por el conductor que luego
    el liquidador asigna a una factura específica.
    """
    _name = 'dispatch.collection.line'
    _description = 'Línea de Cobranza'
    _order = 'payment_date desc, id desc'
    
    # ========== RELACIÓN CON HOJA ==========
    collection_sheet_id = fields.Many2one(
        'dispatch.collection.sheet',
        string='Hoja de Cobranzas',
        required=True,
        ondelete='cascade',
        help='Hoja de cobranzas a la que pertenece esta línea'
    )
    
    settlement_id = fields.Many2one(
        'dispatch.settlement',
        string='Liquidación',
        related='collection_sheet_id.settlement_id',
        store=True,
        readonly=True,
        help='Liquidación asociada'
    )
    
    # ========== FACTURA ==========
    invoice_id = fields.Many2one(
        'account.move',
        string='Factura',
        domain="[('move_type', '=', 'out_invoice'), ('state', '=', 'posted')]",
        help='Factura a la que se asigna este pago'
    )
    
    invoice_name = fields.Char(
        related='invoice_id.name',
        string='Número de Factura',
        readonly=True,
        store=True
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        related='invoice_id.partner_id',
        store=True,
        readonly=True
    )
    
    # ========== MONTOS ==========
    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        default=lambda self: self.env.company.currency_id,
        required=True
    )
    
    invoice_amount_total = fields.Monetary(
        string='Monto de Factura',
        related='invoice_id.amount_total',
        store=True,
        readonly=True,
        help='Monto total de la factura'
    )
    
    amount = fields.Monetary(
        string='Monto Cobrado',
        required=True,
        help='Monto del pago recibido por el transportista'
    )
    
    # ========== TIPO DE COBRANZA ==========
    collection_type = fields.Selection([
        ('cash', 'Efectivo/Al Contado'),
        ('credit', 'Al Crédito'),
        ('deposit', 'Depósito Bancario'),
    ], string='Tipo de Cobranza',
       required=True,
       default='cash',
       help='Tipo de pago recibido')
    
    payment_method = fields.Selection([
        ('cash', 'Efectivo'),
        ('transfer', 'Transferencia'),
        ('deposit', 'Depósito Bancario'),
        ('check', 'Cheque'),
        ('card', 'Tarjeta'),
    ], string='Método de Pago',
       required=True,
       default='cash',
       help='Método con el que se recibió el pago')
    
    # ========== ESTADO ==========
    state = fields.Selection([
        ('pending', 'Pendiente'),
        ('assigned', 'Asignado'),
        ('paid', 'Pagado'),
        ('cancelled', 'Cancelado'),
    ], string='Estado',
       default='pending',
       required=True,
       tracking=True,
       help='Estado del pago')
    
    # ========== FECHAS ==========
    payment_date = fields.Datetime(
        string='Fecha de Registro',
        default=fields.Datetime.now,
        required=True,
        help='Fecha en que el conductor registró el pago'
    )
    
    assignment_date = fields.Datetime(
        string='Fecha de Asignación',
        readonly=True,
        help='Fecha en que el liquidador asignó el pago'
    )
    
    # ========== CONDUCTOR ==========
    registered_by = fields.Many2one(
        'dispatch.driver',
        string='Registrado por',
        help='Conductor que registró el pago desde la app móvil'
    )
    
    # ========== PAGO EN ODOO ==========
    payment_id = fields.Many2one(
        'account.payment',
        string='Pago',
        readonly=True,
        help='Pago creado en Odoo cuando se asigna esta línea'
    )
    
    payment_state = fields.Selection(
        related='payment_id.state',
        string='Estado del Pago',
        readonly=True
    )
    
    # ========== DATOS BANCARIOS ==========
    bank_reference = fields.Char(
        string='Referencia Bancaria',
        help='Número de operación o referencia bancaria'
    )
    
    bank_id = fields.Many2one(
        'res.bank',
        string='Banco',
        help='Banco donde se realizó el depósito'
    )
    
    # ========== OBSERVACIONES ==========
    notes = fields.Text(
        string='Observaciones',
        help='Notas sobre el pago'
    )
    
    # ========== CAMPOS RELACIONADOS ==========
    route_line_id = fields.Many2one(
        'dispatch.route.line',
        string='Línea de Ruta',
        help='Línea de ruta asociada a este pago (si aplica)'
    )
    
    @api.constrains('amount')
    def _check_amount(self):
        """Valida que el monto sea positivo o cero"""
        for line in self:
            if line.amount < 0:
                raise ValidationError(_('El monto no puede ser negativo.'))
    
    @api.constrains('invoice_id', 'state')
    def _check_invoice_assignment(self):
        """Valida que la factura sea válida al asignar"""
        for line in self:
            if line.state in ['assigned', 'paid'] and not line.invoice_id:
                raise ValidationError(_('Debe seleccionar una factura para asignar el pago.'))
            
            # Verificar que la factura esté en la liquidación
            if line.invoice_id and line.settlement_id:
                if line.invoice_id not in line.settlement_id.invoice_ids:
                    raise ValidationError(_(
                        'La factura %s no está incluida en la liquidación de esta hoja de cobranzas.'
                    ) % line.invoice_id.name)
    
    def action_assign_payment(self):
        """
        Asigna el pago a una factura y crea el pago en Odoo.
        Este método debe ser llamado por el liquidador.
        """
        for line in self:
            if line.state != 'pending':
                raise UserError(_('Solo se pueden asignar pagos en estado Pendiente.'))
            
            if not line.invoice_id:
                raise UserError(_('Debe seleccionar una factura antes de asignar el pago.'))
            
            # Verificar que el monto sea mayor a 0
            if line.amount <= 0:
                raise UserError(_('El monto del pago debe ser mayor a cero para asignarlo.'))
            
            # Verificar que la factura no esté completamente pagada
            if line.invoice_id.payment_state == 'paid':
                raise UserError(_(
                    'La factura %s ya está completamente pagada.'
                ) % line.invoice_id.name)
            
            # Verificar que el monto no exceda el saldo pendiente
            residual = line.invoice_id.amount_residual
            if line.amount > residual:
                raise UserError(_(
                    'El monto del pago (%.2f) excede el saldo pendiente de la factura (%.2f).'
                ) % (line.amount, residual))
            
            # Crear el pago en Odoo
            payment_vals = line._prepare_payment_vals()
            payment = self.env['account.payment'].create(payment_vals)
            
            # Confirmar el pago
            payment.action_post()
            
            # Actualizar la línea
            line.write({
                'payment_id': payment.id,
                'state': 'assigned',
                'assignment_date': fields.Datetime.now(),
            })
            
            # Si el pago cubre el total de la factura, marcar como pagado
            if line.invoice_id.payment_state == 'paid':
                line.write({'state': 'paid'})
    
    def _prepare_payment_vals(self):
        """Prepara los valores para crear el pago en Odoo"""
        self.ensure_one()
        
        # Mapear método de pago a journal
        journal_type = 'cash'
        if self.payment_method in ['transfer', 'deposit']:
            journal_type = 'bank'
        
        # Buscar el diario apropiado
        journal = self.env['account.journal'].search([
            ('type', '=', journal_type),
            ('company_id', '=', self.env.company.id),
        ], limit=1)
        
        if not journal:
            raise UserError(_(
                'No se encontró un diario de tipo %s para registrar el pago.'
            ) % journal_type)
        
        payment_vals = {
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': self.invoice_id.partner_id.id,
            'amount': self.amount,
            'currency_id': self.currency_id.id,
            'journal_id': journal.id,
            'date': fields.Date.context_today(self),
            'ref': _('Pago ruta %s - %s') % (
                self.settlement_id.sheet_id.name,
                self.invoice_id.name
            ),
            'reconciled_invoice_ids': [(6, 0, [self.invoice_id.id])],
        }
        
        # Agregar referencia bancaria si existe
        if self.bank_reference:
            payment_vals['ref'] = '%s - Ref: %s' % (payment_vals['ref'], self.bank_reference)
        
        return payment_vals
    
    def action_cancel_assignment(self):
        """Cancela la asignación del pago"""
        for line in self:
            if line.state == 'pending':
                raise UserError(_('Esta línea no está asignada.'))
            
            if line.state == 'paid':
                raise UserError(_(
                    'No se puede cancelar una línea con pago confirmado. '
                    'Cancele primero el pago en Odoo.'
                ))
            
            # Si hay un pago creado, cancelarlo
            if line.payment_id:
                if line.payment_id.state == 'posted':
                    raise UserError(_(
                        'El pago está confirmado. Debe cancelarlo desde el módulo de contabilidad.'
                    ))
                line.payment_id.action_cancel()
            
            line.write({
                'state': 'pending',
                'payment_id': False,
                'assignment_date': False,
            })
    
    def action_cancel(self):
        """Cancela la línea de cobranza"""
        for line in self:
            if line.payment_id and line.payment_id.state == 'posted':
                raise UserError(_(
                    'No se puede cancelar una línea con pago confirmado. '
                    'Cancele primero el pago en Odoo.'
                ))
            
            line.write({'state': 'cancelled'})
    
    def action_reset_to_pending(self):
        """Reinicia la línea a pendiente"""
        for line in self:
            if line.state not in ['assigned', 'cancelled']:
                raise UserError(_('Solo se pueden reiniciar líneas Asignadas o Canceladas.'))
            
            if line.payment_id:
                raise UserError(_(
                    'No se puede reiniciar una línea con pago creado. '
                    'Cancele primero la asignación.'
                ))
            
            line.write({
                'state': 'pending',
                'invoice_id': False,
                'assignment_date': False,
            })
    
    def action_view_payment(self):
        """Ver el pago en Odoo"""
        self.ensure_one()
        if not self.payment_id:
            raise UserError(_('Esta línea no tiene un pago creado todavía.'))
        
        return {
            'name': _('Pago'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'res_id': self.payment_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_view_invoice(self):
        """Ver la factura"""
        self.ensure_one()
        if not self.invoice_id:
            raise UserError(_('Esta línea no tiene una factura asignada.'))
        
        return {
            'name': _('Factura'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': self.invoice_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

