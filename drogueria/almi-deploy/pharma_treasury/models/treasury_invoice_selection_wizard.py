# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class TreasuryInvoiceSelectionWizard(models.TransientModel):
    """
    Wizard para selección masiva de facturas para agregar a una planilla.
    Permite filtrar por fecha, cliente, zona, estado SUNAT, etc.
    """
    _name = 'treasury.invoice.selection.wizard'
    _description = 'Wizard de Selección de Facturas'
    
    # ========== PLANILLA DESTINO ==========
    sheet_id = fields.Many2one(
        'treasury.settlement.sheet',
        string='Planilla',
        required=True,
        readonly=True,
        help='Planilla a la que se agregarán las facturas'
    )
    
    # ========== FILTROS ==========
    date_from = fields.Date(
        string='Desde Fecha',
        help='Fecha inicial de búsqueda'
    )
    
    date_to = fields.Date(
        string='Hasta Fecha',
        default=fields.Date.today,
        help='Fecha final de búsqueda'
    )
    
    partner_ids = fields.Many2many(
        'res.partner',
        string='Clientes',
        help='Filtrar por clientes específicos'
    )
    
    zone_ids = fields.Many2many(
        'sale.zone',
        string='Zonas de Venta',
        help='Filtrar por zonas de venta'
    )
    
    salesperson_ids = fields.Many2many(
        'res.users',
        string='Vendedores',
        help='Filtrar por vendedor'
    )
    
    payment_state = fields.Selection([
        ('all', 'Todas'),
        ('not_paid', 'No Pagadas'),
        ('partial', 'Pago Parcial'),
    ], string='Estado de Pago',
       default='not_paid',
       help='Estado de pago de las facturas')
    
    sunat_estado = fields.Selection([
        ('all', 'Todas'),
        ('accepted', 'Aceptadas por SUNAT'),
        ('sent', 'Enviadas a SUNAT'),
    ], string='Estado SUNAT',
       default='all',
       help='Estado en SUNAT (si aplica)')
    
    amount_min = fields.Monetary(
        string='Monto Mínimo',
        currency_field='currency_id',
        help='Monto mínimo de factura'
    )
    
    amount_max = fields.Monetary(
        string='Monto Máximo',
        currency_field='currency_id',
        help='Monto máximo de factura'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        default=lambda self: self.env.company.currency_id
    )
    
    # ========== FACTURAS DISPONIBLES ==========
    invoice_ids = fields.Many2many(
        'account.move',
        'wizard_invoice_rel',
        'wizard_id',
        'invoice_id',
        string='Facturas Disponibles',
        compute='_compute_available_invoices',
        help='Facturas que coinciden con los filtros'
    )
    
    selected_invoice_ids = fields.Many2many(
        'account.move',
        'wizard_invoice_selected_rel',
        'wizard_id',
        'invoice_id',
        string='Facturas Seleccionadas',
        help='Facturas seleccionadas para agregar'
    )
    
    # ========== ESTADÍSTICAS ==========
    total_available = fields.Integer(
        string='Total Disponibles',
        compute='_compute_stats'
    )
    
    total_selected = fields.Integer(
        string='Total Seleccionadas',
        compute='_compute_stats'
    )
    
    total_amount_selected = fields.Monetary(
        string='Monto Total Seleccionado',
        compute='_compute_stats',
        currency_field='currency_id'
    )
    
    @api.depends('date_from', 'date_to', 'partner_ids', 'zone_ids', 
                 'salesperson_ids', 'payment_state', 'sunat_estado',
                 'amount_min', 'amount_max')
    def _compute_available_invoices(self):
        """Calcula las facturas disponibles según los filtros"""
        for wizard in self:
            domain = [
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
            ]
            
            # Filtro de fecha
            if wizard.date_from:
                domain.append(('invoice_date', '>=', wizard.date_from))
            if wizard.date_to:
                domain.append(('invoice_date', '<=', wizard.date_to))
            
            # Filtro de clientes
            if wizard.partner_ids:
                domain.append(('partner_id', 'in', wizard.partner_ids.ids))
            
            # Filtro de zonas
            if wizard.zone_ids:
                domain.append(('partner_id.sale_zone_id', 'in', wizard.zone_ids.ids))
            
            # Filtro de vendedores
            if wizard.salesperson_ids:
                domain.append(('invoice_user_id', 'in', wizard.salesperson_ids.ids))
            
            # Filtro de estado de pago
            if wizard.payment_state != 'all':
                domain.append(('payment_state', '=', wizard.payment_state))
            
            # Filtro de estado SUNAT (si el campo existe)
            if wizard.sunat_estado != 'all':
                domain.append(('sunat_estado', '=', wizard.sunat_estado))
            
            # Filtro de montos
            if wizard.amount_min:
                domain.append(('amount_total', '>=', wizard.amount_min))
            if wizard.amount_max:
                domain.append(('amount_total', '<=', wizard.amount_max))
            
            # Excluir facturas que ya están en planillas activas
            existing_invoice_ids = self.env['treasury.settlement.sheet.line'].search([
                ('sheet_id.state', 'not in', ['cancelled', 'closed'])
            ]).mapped('invoice_id').ids
            
            if existing_invoice_ids:
                domain.append(('id', 'not in', existing_invoice_ids))
            
            invoices = self.env['account.move'].search(domain, order='invoice_date desc')
            wizard.invoice_ids = invoices
    
    @api.depends('invoice_ids', 'selected_invoice_ids')
    def _compute_stats(self):
        """Calcula estadísticas de las facturas"""
        for wizard in self:
            wizard.total_available = len(wizard.invoice_ids)
            wizard.total_selected = len(wizard.selected_invoice_ids)
            wizard.total_amount_selected = sum(wizard.selected_invoice_ids.mapped('amount_total'))
    
    def action_select_all(self):
        """Selecciona todas las facturas disponibles"""
        self.ensure_one()
        self.selected_invoice_ids = [(6, 0, self.invoice_ids.ids)]
        return self._reopen_wizard()
    
    def action_clear_selection(self):
        """Limpia la selección"""
        self.ensure_one()
        self.selected_invoice_ids = [(5, 0, 0)]
        return self._reopen_wizard()
    
    def action_apply_filters(self):
        """Re-aplica los filtros (re-calcula invoice_ids)"""
        self.ensure_one()
        # Forzar re-cálculo
        self._compute_available_invoices()
        return self._reopen_wizard()
    
    def action_add_to_sheet(self):
        """Agrega las facturas seleccionadas a la planilla"""
        self.ensure_one()
        
        if not self.selected_invoice_ids:
            raise UserError(_('Debe seleccionar al menos una factura.'))
        
        if self.sheet_id.state != 'draft':
            raise UserError(_(
                'Solo se pueden agregar facturas a planillas en estado Borrador.'
            ))
        
        # Obtener la última secuencia
        last_sequence = 0
        if self.sheet_id.line_ids:
            last_sequence = max(self.sheet_id.line_ids.mapped('sequence'))
        
        # Crear líneas para cada factura seleccionada
        lines_created = 0
        for invoice in self.selected_invoice_ids:
            last_sequence += 10
            self.env['treasury.settlement.sheet.line'].create({
                'sheet_id': self.sheet_id.id,
                'invoice_id': invoice.id,
                'sequence': last_sequence,
            })
            lines_created += 1
        
        # Mensaje de éxito
        self.sheet_id.message_post(
            body=_('Se agregaron %s facturas a la planilla por un total de %s') % (
                lines_created,
                self.total_amount_selected
            )
        )
        
        return {'type': 'ir.actions.act_window_close'}
    
    def _reopen_wizard(self):
        """Re-abre el wizard para mostrar cambios"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }


class TreasurySettlementSheetAssignWizard(models.TransientModel):
    """
    Wizard para asignar una planilla a una ruta existente o crear una nueva.
    """
    _name = 'treasury.settlement.sheet.assign.wizard'
    _description = 'Wizard de Asignación de Planilla a Ruta'
    
    sheet_id = fields.Many2one(
        'treasury.settlement.sheet',
        string='Planilla',
        required=True,
        readonly=True
    )
    
    assignment_type = fields.Selection([
        ('existing', 'Asignar a Ruta Existente'),
        ('new', 'Crear Nueva Ruta'),
    ], string='Tipo de Asignación',
       default='existing',
       required=True)
    
    # Para ruta existente
    route_id = fields.Many2one(
        'dispatch.route',
        string='Ruta',
        domain="[('state', 'in', ['draft', 'assigned']), ('settlement_sheet_id', '=', False)]",
        help='Ruta a la que se asignará la planilla'
    )
    
    # Para nueva ruta
    route_date = fields.Date(
        string='Fecha de Ruta',
        default=fields.Date.today
    )
    
    driver_id = fields.Many2one(
        'dispatch.driver',
        string='Conductor'
    )
    
    vehicle_id = fields.Many2one(
        'dispatch.vehicle',
        string='Vehículo'
    )
    
    def action_assign(self):
        """Asigna la planilla a la ruta"""
        self.ensure_one()
        
        if self.assignment_type == 'existing':
            if not self.route_id:
                raise UserError(_('Debe seleccionar una ruta.'))
            
            if self.route_id.settlement_sheet_id:
                raise UserError(_(
                    'La ruta %s ya tiene una planilla asignada.'
                ) % self.route_id.name)
            
            # Asignar a ruta existente
            self.route_id.write({'settlement_sheet_id': self.sheet_id.id})
            self.sheet_id.write({
                'route_id': self.route_id.id,
                'state': 'in_route'
            })
            
            message = _('Planilla asignada a la ruta existente %s') % self.route_id.name
            
        else:  # new
            if not self.driver_id or not self.vehicle_id:
                raise UserError(_('Debe seleccionar conductor y vehículo.'))
            
            # Crear nueva ruta
            route = self.env['dispatch.route'].create({
                'route_date': self.route_date,
                'driver_id': self.driver_id.id,
                'vehicle_id': self.vehicle_id.id,
                'settlement_sheet_id': self.sheet_id.id,
            })
            
            self.sheet_id.write({
                'route_id': route.id,
                'state': 'in_route'
            })
            
            message = _('Se creó la ruta %s y se asignó la planilla') % route.name
        
        self.sheet_id.message_post(body=message)
        
        return {'type': 'ir.actions.act_window_close'}

