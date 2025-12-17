# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class CreateSheetWizard(models.TransientModel):
    """
    Wizard para crear planillas de despacho desde facturas seleccionadas.
    """
    _name = 'create.sheet.wizard'
    _description = 'Wizard de Creación de Planilla'
    
    # ========== CAMPOS BÁSICOS ==========
    sheet_date = fields.Date(
        string='Fecha de Despacho',
        required=True,
        default=fields.Date.today,
        help='Fecha programada para el despacho'
    )
    
    driver_id = fields.Many2one(
        'dispatch.driver',
        string='Conductor',
        required=True,
        domain="[('active', '=', True)]",
        help='Conductor asignado a la planilla'
    )
    
    vehicle_id = fields.Many2one(
        'dispatch.vehicle',
        string='Vehículo',
        required=True,
        domain="[('status', '=', 'available')]",
        help='Vehículo asignado a la planilla'
    )
    
    invoice_ids = fields.Many2many(
        'account.move',
        string='Facturas Seleccionadas',
        help='Facturas que se incluirán en la planilla'
    )
    
    invoice_count = fields.Integer(
        string='Cantidad de Facturas',
        compute='_compute_invoice_count',
        help='Número de facturas seleccionadas'
    )
    
    notes = fields.Text(
        string='Notas',
        help='Observaciones adicionales'
    )
    
    @api.depends('invoice_ids')
    def _compute_invoice_count(self):
        """Calcula la cantidad de facturas"""
        for wizard in self:
            wizard.invoice_count = len(wizard.invoice_ids)
    
    @api.model
    def default_get(self, fields_list):
        """Obtiene las facturas seleccionadas del contexto"""
        res = super(CreateSheetWizard, self).default_get(fields_list)
        
        # Obtener IDs de facturas desde el contexto
        invoice_ids = self.env.context.get('active_ids', [])
        
        if invoice_ids:
            # Validar que sean facturas de venta
            invoices = self.env['account.move'].browse(invoice_ids)
            
            invalid_invoices = invoices.filtered(lambda inv: inv.move_type != 'out_invoice')
            if invalid_invoices:
                raise UserError(_(
                    'Solo se pueden seleccionar facturas de venta. '
                    'Las siguientes no son facturas de venta: %s'
                ) % ', '.join(invalid_invoices.mapped('name')))
            
            unposted_invoices = invoices.filtered(lambda inv: inv.state != 'posted')
            if unposted_invoices:
                raise UserError(_(
                    'Solo se pueden seleccionar facturas confirmadas. '
                    'Las siguientes no están confirmadas: %s'
                ) % ', '.join(unposted_invoices.mapped('name')))
            
            res['invoice_ids'] = [(6, 0, invoice_ids)]
        else:
            raise UserError(_('Debe seleccionar al menos una factura.'))
        
        return res
    
    @api.constrains('driver_id')
    def _check_driver_license(self):
        """Valida que el conductor tenga licencia vigente"""
        for wizard in self:
            if wizard.driver_id and wizard.driver_id.license_expired:
                raise ValidationError(_(
                    'El conductor %s tiene la licencia vencida. '
                    'Seleccione otro conductor.'
                ) % wizard.driver_id.name)
    
    def action_create_sheet(self):
        """Crea la planilla de despacho"""
        self.ensure_one()
        
        if not self.invoice_ids:
            raise UserError(_('Debe agregar al menos una factura a la planilla.'))
        
        # Crear la planilla
        sheet_vals = {
            'sheet_date': self.sheet_date,
            'driver_id': self.driver_id.id,
            'vehicle_id': self.vehicle_id.id,
            'invoice_ids': [(6, 0, self.invoice_ids.ids)],
            'notes': self.notes or '',
        }
        
        sheet = self.env['dispatch.sheet'].create(sheet_vals)
        
        # Retornar acción para ver la planilla creada
        return {
            'name': _('Planilla de Despacho'),
            'type': 'ir.actions.act_window',
            'res_model': 'dispatch.sheet',
            'res_id': sheet.id,
            'view_mode': 'form',
            'target': 'current',
        }

