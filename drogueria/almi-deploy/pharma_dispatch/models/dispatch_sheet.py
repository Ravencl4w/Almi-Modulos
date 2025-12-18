# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class DispatchSheet(models.Model):
    """
    Modelo para gestionar planillas de despacho.
    Agrupa múltiples facturas de venta para generar rutas de reparto.
    """
    _name = 'dispatch.sheet'
    _description = 'Planilla de Despacho'
    _order = 'sheet_date desc, id desc'
    
    # ========== INFORMACIÓN BÁSICA ==========
    name = fields.Char(
        string='Número de Planilla',
        required=True,
        copy=False,
        readonly=True,
        default='Nuevo',
        help='Número identificador de la planilla'
    )
    
    sheet_date = fields.Date(
        string='Fecha de Planilla',
        required=True,
        default=fields.Date.today,
        tracking=True,
        help='Fecha programada para el despacho'
    )
    
    # ========== ASIGNACIÓN ==========
    driver_id = fields.Many2one(
        'dispatch.driver',
        string='Conductor',
        required=True,
        tracking=True,
        help='Conductor asignado a esta planilla'
    )
    
    vehicle_id = fields.Many2one(
        'dispatch.vehicle',
        string='Vehículo',
        required=True,
        tracking=True,
        help='Vehículo asignado a esta planilla'
    )
    
    # ========== ESTADO ==========
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmado'),
        ('processed', 'Procesado'),
        ('cancelled', 'Cancelado'),
    ], string='Estado',
       default='draft',
       required=True,
       tracking=True,
       help='Estado actual de la planilla')
    
    # ========== FACTURAS ==========
    invoice_ids = fields.Many2many(
        'account.move',
        'dispatch_sheet_invoice_rel',
        'sheet_id',
        'invoice_id',
        string='Facturas',
        domain="[('move_type', '=', 'out_invoice'), ('state', '=', 'posted')]",
        help='Facturas de venta incluidas en esta planilla'
    )
    
    invoice_count = fields.Integer(
        string='Cantidad de Facturas',
        compute='_compute_invoice_count',
        store=True,
        help='Número total de facturas en la planilla'
    )
    
    # ========== RUTA GENERADA ==========
    route_id = fields.Many2one(
        'dispatch.route',
        string='Ruta Generada',
        readonly=True,
        help='Ruta de reparto generada desde esta planilla'
    )
    
    route_state = fields.Selection(
        related='route_id.state',
        string='Estado de Ruta',
        readonly=True
    )
    
    # ========== LIQUIDACIÓN ==========
    settlement_id = fields.One2many(
        'dispatch.settlement',
        'sheet_id',
        string='Liquidación',
        readonly=True,
        help='Liquidación generada para esta planilla'
    )
    
    has_settlement = fields.Boolean(
        string='Tiene Liquidación',
        compute='_compute_has_settlement',
        store=True,
        help='Indica si la planilla tiene liquidación'
    )
    
    # ========== CAMPOS COMPUTADOS ==========
    total_amount = fields.Monetary(
        string='Monto Total',
        compute='_compute_totals',
        store=True,
        help='Suma total de las facturas'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        default=lambda self: self.env.company.currency_id,
        required=True
    )
    
    partner_count = fields.Integer(
        string='Cantidad de Clientes',
        compute='_compute_totals',
        store=True,
        help='Número de clientes únicos en las facturas'
    )
    
    # ========== NOTAS ==========
    notes = fields.Text(
        string='Notas',
        help='Observaciones sobre la planilla'
    )
    
    @api.model_create_multi
    def create(self, vals_list):
        """Genera número secuencial al crear"""
        for vals in vals_list:
            if vals.get('name', 'Nuevo') == 'Nuevo':
                vals['name'] = self.env['ir.sequence'].next_by_code('dispatch.sheet') or 'Nuevo'
        return super(DispatchSheet, self).create(vals_list)
    
    @api.depends('invoice_ids')
    def _compute_invoice_count(self):
        """Calcula la cantidad de facturas"""
        for sheet in self:
            sheet.invoice_count = len(sheet.invoice_ids)
    
    @api.depends('invoice_ids', 'invoice_ids.amount_total', 'invoice_ids.partner_id')
    def _compute_totals(self):
        """Calcula totales de la planilla"""
        for sheet in self:
            sheet.total_amount = sum(sheet.invoice_ids.mapped('amount_total'))
            sheet.partner_count = len(sheet.invoice_ids.mapped('partner_id'))
    
    @api.depends('settlement_id')
    def _compute_has_settlement(self):
        """Verifica si tiene liquidación"""
        for sheet in self:
            sheet.has_settlement = bool(sheet.settlement_id)
    
    @api.constrains('invoice_ids')
    def _check_invoices(self):
        """Valida que todas las facturas sean de venta y estén confirmadas"""
        for sheet in self:
            for invoice in sheet.invoice_ids:
                if invoice.move_type != 'out_invoice':
                    raise ValidationError(_(
                        'Solo se pueden agregar facturas de venta a la planilla. '
                        'La factura %s es de tipo %s.'
                    ) % (invoice.name, invoice.move_type))
                
                if invoice.state != 'posted':
                    raise ValidationError(_(
                        'Solo se pueden agregar facturas confirmadas. '
                        'La factura %s está en estado %s.'
                    ) % (invoice.name, invoice.state))
    
    @api.constrains('driver_id')
    def _check_driver_license(self):
        """Valida que el conductor tenga licencia vigente"""
        for sheet in self:
            if sheet.driver_id and sheet.driver_id.license_expired:
                raise ValidationError(_(
                    'El conductor %s tiene la licencia vencida. '
                    'No se puede asignar a la planilla.'
                ) % sheet.driver_id.name)
    
    def action_confirm(self):
        """Confirma la planilla y crea la ruta automáticamente"""
        for sheet in self:
            if not sheet.invoice_ids:
                raise UserError(_('No se puede confirmar una planilla sin facturas.'))
            
            if sheet.state != 'draft':
                raise UserError(_('Solo se pueden confirmar planillas en estado Borrador.'))
            
            sheet.write({'state': 'confirmed'})
            
            # Crear la ruta automáticamente
            sheet.action_create_route()
    
    def action_create_route(self):
        """Crea una ruta de reparto desde la planilla y genera GRE automáticamente"""
        self.ensure_one()
        
        if self.state not in ['confirmed', 'processed']:
            raise UserError(_('Solo se pueden crear rutas desde planillas confirmadas.'))
        
        if self.route_id:
            raise UserError(_(
                'Esta planilla ya tiene una ruta asociada: %s'
            ) % self.route_id.name)
        
        if not self.invoice_ids:
            raise UserError(_('La planilla no tiene facturas asociadas.'))
        
        # Crear la ruta
        route_vals = {
            'route_date': self.sheet_date,
            'driver_id': self.driver_id.id,
            'vehicle_id': self.vehicle_id.id,
            'sheet_id': self.id,
            'notes': _('Ruta generada desde planilla %s') % self.name,
        }
        
        route = self.env['dispatch.route'].create(route_vals)
        
        # Crear líneas de ruta y generar GRE por cada pedido de las facturas
        sequence = 10
        pickings_to_process = self.env['stock.picking']
        
        for invoice in self.invoice_ids:
            # Obtener el pedido de venta asociado a la factura
            sale_order = invoice.invoice_line_ids.mapped('sale_line_ids.order_id')
            
            if not sale_order:
                # Si no hay pedido asociado, continuar con la siguiente factura
                continue
            
            # Si hay múltiples pedidos, tomar el primero
            if len(sale_order) > 1:
                sale_order = sale_order[0]
            
            # Verificar que el pedido esté confirmado
            if sale_order.state not in ['sale', 'done']:
                continue
            
            # Crear línea de ruta
            self.env['dispatch.route.line'].create({
                'route_id': route.id,
                'order_id': sale_order.id,
                'sequence': sequence,
            })
            sequence += 10
            
            # Obtener pickings del pedido para generar GRE
            # Buscamos pickings de tipo delivery que estén listos o confirmados
            pickings = sale_order.picking_ids.filtered(
                lambda p: p.picking_type_code == 'outgoing' and 
                         p.state in ['confirmed', 'assigned', 'waiting']
            )
            pickings_to_process |= pickings
        
        # Generar GRE automáticamente para todos los pickings
        if pickings_to_process:
            self._generate_gre_for_pickings(pickings_to_process, route)
        
        # Crear liquidación y hoja de cobranzas
        settlement = self._create_settlement()
        
        # Actualizar planilla
        self.write({
            'route_id': route.id,
            'state': 'processed',
        })
        
        # Retornar acción para ver la ruta creada
        return {
            'name': _('Ruta de Reparto'),
            'type': 'ir.actions.act_window',
            'res_model': 'dispatch.route',
            'res_id': route.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def _generate_gre_for_pickings(self, pickings, route):
        """Prepara los pickings para GRE (sin validarlos aún)"""
        for picking in pickings:
            try:
                # Asignar conductor y vehículo al picking para GRE
                picking.write({
                    'driver_id': route.driver_id.id,
                    'vehicle_id': route.vehicle_id.id,
                    'is_electronic_guide': True,
                    'transfer_reason': '01',  # Venta por defecto
                })
                
                # Verificar que el picking tenga los datos necesarios para GRE
                if not picking.partner_id:
                    continue
                
                # Preparar las cantidades (pero no validar aún)
                if picking.state in ['confirmed', 'assigned', 'waiting']:
                    # Reservar disponibilidad si es necesario
                    if picking.state == 'confirmed':
                        picking.action_assign()
                    
                    # Asignar cantidades done = cantidades demand
                    for move in picking.move_ids:
                        if not move.move_line_ids:
                            continue
                        for move_line in move.move_line_ids:
                            if not move_line.quantity:
                                move_line.quantity = move_line.reserved_uom_qty
                
            except Exception as e:
                # Si hay error, continuar con los demás
                continue
    
    def _create_settlement(self):
        """Crea la liquidación y hoja de cobranzas para esta planilla"""
        self.ensure_one()
        
        # Crear liquidación
        settlement_vals = {
            'sheet_id': self.id,
        }
        settlement = self.env['dispatch.settlement'].create(settlement_vals)
        
        # Crear hoja de cobranzas
        collection_sheet_vals = {
            'settlement_id': settlement.id,
        }
        collection_sheet = self.env['dispatch.collection.sheet'].create(collection_sheet_vals)
        
        # Actualizar referencia en la liquidación
        settlement.write({'collection_sheet_id': collection_sheet.id})
        
        # Crear líneas de cobranza por cada factura con monto 0
        # El transportista luego asignará el monto recibido
        for invoice in self.invoice_ids:
            # Determinar el tipo de cobranza según el tipo de factura
            collection_type = 'cash'  # Por defecto al contado
            
            # Verificar si es al crédito
            if invoice.invoice_payment_term_id:
                term_name = (invoice.invoice_payment_term_id.name or '').lower()
                if 'credito' in term_name or 'credit' in term_name:
                    collection_type = 'credit'
                elif not ('inmediato' in term_name or 'contado' in term_name or 'immediate' in term_name):
                    # Si tiene término de pago y no es inmediato/contado, asumimos crédito
                    collection_type = 'credit'
            
            # Crear línea de cobranza
            line_vals = {
                'collection_sheet_id': collection_sheet.id,
                'invoice_id': invoice.id,
                'amount': 0.0,  # Monto inicial en 0, el transportista lo actualizará
                'collection_type': collection_type,
                'payment_method': 'cash',  # Método por defecto
                'state': 'pending',
                'registered_by': self.driver_id.id,
                'notes': _('Línea creada automáticamente para factura %s') % invoice.name,
            }
            self.env['dispatch.collection.line'].create(line_vals)
        
        return settlement
    
    def action_cancel(self):
        """Cancela la planilla"""
        for sheet in self:
            if sheet.state == 'processed' and sheet.route_id:
                raise UserError(_(
                    'No se puede cancelar una planilla que ya tiene una ruta generada. '
                    'Cancele primero la ruta %s.'
                ) % sheet.route_id.name)
            
            sheet.write({'state': 'cancelled'})
    
    def action_reset_to_draft(self):
        """Reinicia la planilla a borrador"""
        for sheet in self:
            if sheet.state == 'processed' and sheet.route_id:
                raise UserError(_(
                    'No se puede reiniciar una planilla que tiene una ruta generada.'
                ))
            
            sheet.write({'state': 'draft'})
    
    def action_view_route(self):
        """Ver la ruta generada"""
        self.ensure_one()
        if not self.route_id:
            raise UserError(_('Esta planilla no tiene una ruta generada todavía.'))
        
        return {
            'name': _('Ruta de Reparto'),
            'type': 'ir.actions.act_window',
            'res_model': 'dispatch.route',
            'res_id': self.route_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_view_invoices(self):
        """Ver facturas de la planilla"""
        self.ensure_one()
        return {
            'name': _('Facturas de %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.invoice_ids.ids)],
        }
    
    def action_view_settlement(self):
        """Ver la liquidación"""
        self.ensure_one()
        if not self.settlement_id:
            raise UserError(_('Esta planilla no tiene una liquidación generada todavía.'))
        
        return {
            'name': _('Liquidación'),
            'type': 'ir.actions.act_window',
            'res_model': 'dispatch.settlement',
            'res_id': self.settlement_id[0].id,
            'view_mode': 'form',
            'target': 'current',
        }

