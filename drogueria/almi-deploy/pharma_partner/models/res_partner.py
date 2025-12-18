# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class ResPartner(models.Model):
    """
    Extensión del modelo res.partner para agregar campos específicos
    de empresas farmacéuticas con operaciones de distribución y droguería.
    """
    _inherit = 'res.partner'
    
    # ========== GIRO DEL NEGOCIO ==========
    business_sector = fields.Selection([
        ('farmacia', 'Farmacia'),
        ('botica', 'Botica'),
        ('clinica', 'Clínica'),
        ('hospital', 'Hospital'),
        ('laboratorio', 'Laboratorio'),
        ('distribuidor', 'Distribuidor'),
        ('drogueria', 'Droguería'),
        ('cadena_farmacias', 'Cadena de Farmacias'),
        ('consultorio', 'Consultorio Médico'),
        ('veterinaria', 'Veterinaria'),
        ('otro', 'Otro'),
    ], string='Giro del Negocio', 
       tracking=True,
       help='Actividad comercial principal del cliente')
    
    business_sector_other = fields.Char(
        string='Otro Giro',
        help='Especifique el giro si seleccionó "Otro"'
    )
    
    # ========== ZONA DE VENTA ==========
    sale_zone_id = fields.Many2one(
        'sale.zone',
        string='Zona de Venta',
        tracking=True,
        help='Zona geográfica asignada a este cliente para organización de ventas'
    )
    
    sale_zone_code = fields.Char(
        string='Código de Zona',
        related='sale_zone_id.code',
        store=True,
        readonly=True,
        help='Código de la zona de venta asignada'
    )
    
    sale_zone_user_id = fields.Many2one(
        'res.users',
        string='Ejecutivo de Zona',
        related='sale_zone_id.user_id',
        store=True,
        readonly=True,
        help='Ejecutivo responsable de la zona asignada'
    )
    
    # ========== GESTIÓN DE CRÉDITOS ==========
    credit_limit_custom = fields.Monetary(
        string='Límite de Crédito',
        currency_field='currency_id',
        tracking=True,
        help='Límite máximo de crédito autorizado para este cliente'
    )
    
    credit_available = fields.Monetary(
        string='Crédito Disponible',
        compute='_compute_credit_available',
        store=True,
        currency_field='currency_id',
        help='Crédito disponible = Límite - Crédito usado'
    )
    
    credit_used_percent = fields.Float(
        string='Crédito Utilizado (%)',
        compute='_compute_credit_available',
        store=True,
        help='Porcentaje del límite de crédito utilizado'
    )
    
    has_credit = fields.Boolean(
        string='Tiene Crédito',
        compute='_compute_has_credit',
        search='_search_has_credit',
        help='Indica si el cliente tiene un límite de crédito asignado'
    )
    
    credit_approved_by = fields.Many2one(
        'res.users',
        string='Crédito Aprobado Por',
        tracking=True,
        help='Usuario que aprobó el límite de crédito'
    )
    
    credit_approved_date = fields.Date(
        string='Fecha de Aprobación',
        tracking=True,
        help='Fecha en que se aprobó el crédito'
    )
    
    credit_notes = fields.Text(
        string='Notas de Crédito',
        help='Observaciones sobre el crédito del cliente'
    )
    
    # ========== RESOLUCIÓN DE DROGUERÍA ==========
    has_drugstore_resolution = fields.Boolean(
        string='Tiene Resolución de Droguería',
        default=False,
        tracking=True,
        help='Indica si el cliente cuenta con resolución/permiso de droguería vigente'
    )
    
    drugstore_resolution_number = fields.Char(
        string='Número de Resolución',
        tracking=True,
        help='Número de la resolución de droguería emitida por la autoridad competente'
    )
    
    drugstore_resolution_date = fields.Date(
        string='Fecha de Emisión',
        tracking=True,
        help='Fecha de emisión de la resolución'
    )
    
    drugstore_resolution_expiry = fields.Date(
        string='Fecha de Vencimiento',
        tracking=True,
        help='Fecha de vencimiento de la resolución'
    )
    
    drugstore_resolution_status = fields.Selection([
        ('vigente', 'Vigente'),
        ('por_vencer', 'Por Vencer (30 días)'),
        ('vencida', 'Vencida'),
        ('no_aplica', 'No Aplica'),
    ], string='Estado de Resolución',
       compute='_compute_drugstore_resolution_status',
       store=True,
       help='Estado actual de la resolución de droguería')
    
    drugstore_resolution_file = fields.Binary(
        string='Archivo de Resolución',
        help='Archivo PDF o imagen de la resolución'
    )
    
    drugstore_resolution_filename = fields.Char(
        string='Nombre del Archivo'
    )
    
    drugstore_authority = fields.Char(
        string='Autoridad Emisora',
        help='Entidad que emitió la resolución (ej: DIGEMID, MINSA)'
    )
    
    drugstore_notes = fields.Text(
        string='Notas de Droguería',
        help='Observaciones sobre la resolución y permisos de droguería'
    )
    
    # ========== CAMPOS COMPUTADOS ==========
    
    @api.depends('credit_limit_custom', 'credit')
    def _compute_credit_available(self):
        """Calcula el crédito disponible y porcentaje usado"""
        for partner in self:
            if partner.credit_limit_custom > 0:
                partner.credit_available = partner.credit_limit_custom - partner.credit
                partner.credit_used_percent = (partner.credit / partner.credit_limit_custom) * 100
            else:
                partner.credit_available = 0.0
                partner.credit_used_percent = 0.0
    
    @api.depends('credit_limit_custom')
    def _compute_has_credit(self):
        """Determina si el cliente tiene crédito asignado"""
        for partner in self:
            partner.has_credit = partner.credit_limit_custom > 0
    
    def _search_has_credit(self, operator, value):
        """Permite buscar clientes con/sin crédito"""
        if operator == '=' and value:
            return [('credit_limit_custom', '>', 0)]
        elif operator == '=' and not value:
            return [('credit_limit_custom', '<=', 0)]
        elif operator == '!=' and value:
            return [('credit_limit_custom', '<=', 0)]
        else:
            return [('credit_limit_custom', '>', 0)]
    
    @api.depends('has_drugstore_resolution', 'drugstore_resolution_expiry')
    def _compute_drugstore_resolution_status(self):
        """Calcula el estado de la resolución de droguería"""
        today = fields.Date.today()
        for partner in self:
            if not partner.has_drugstore_resolution:
                partner.drugstore_resolution_status = 'no_aplica'
            elif not partner.drugstore_resolution_expiry:
                partner.drugstore_resolution_status = 'vigente'
            else:
                days_to_expiry = (partner.drugstore_resolution_expiry - today).days
                if days_to_expiry < 0:
                    partner.drugstore_resolution_status = 'vencida'
                elif days_to_expiry <= 30:
                    partner.drugstore_resolution_status = 'por_vencer'
                else:
                    partner.drugstore_resolution_status = 'vigente'
    
    # ========== VALIDACIONES ==========
    
    @api.constrains('credit_limit_custom')
    def _check_credit_limit(self):
        """Valida que el límite de crédito sea positivo"""
        for partner in self:
            if partner.credit_limit_custom < 0:
                raise ValidationError(
                    _('El límite de crédito no puede ser negativo.')
                )
    
    @api.constrains('drugstore_resolution_date', 'drugstore_resolution_expiry')
    def _check_drugstore_dates(self):
        """Valida que las fechas de la resolución sean coherentes"""
        for partner in self:
            if partner.drugstore_resolution_date and partner.drugstore_resolution_expiry:
                if partner.drugstore_resolution_expiry < partner.drugstore_resolution_date:
                    raise ValidationError(
                        _('La fecha de vencimiento no puede ser anterior a la fecha de emisión.')
                    )
    
    # ========== MÉTODOS DE NEGOCIO ==========
    
    def action_approve_credit(self):
        """Aprueba el crédito del cliente"""
        self.ensure_one()
        if not self.credit_limit_custom or self.credit_limit_custom <= 0:
            raise UserError(_('Debe establecer un límite de crédito mayor a cero.'))
        
        self.write({
            'credit_approved_by': self.env.user.id,
            'credit_approved_date': fields.Date.today(),
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Crédito Aprobado'),
                'message': _('Se aprobó un crédito de %s para %s') % (
                    self.credit_limit_custom, self.name
                ),
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_renew_drugstore_resolution(self):
        """Acción para renovar la resolución de droguería"""
        self.ensure_one()
        return {
            'name': _('Renovar Resolución de Droguería'),
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
        }
    
    def action_view_invoices_with_credit(self):
        """Ver facturas pendientes de pago (que usan el crédito)"""
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('account.action_move_out_invoice_type')
        action['domain'] = [
            ('partner_id', 'child_of', self.id),
            ('move_type', '=', 'out_invoice'),
            ('payment_state', 'in', ['not_paid', 'partial']),
            ('state', '=', 'posted')
        ]
        action['context'] = {
            'default_partner_id': self.id,
            'default_move_type': 'out_invoice',
        }
        return action
    
    def _get_credit_warning(self):
        """Retorna un mensaje de advertencia si el crédito está por agotarse"""
        self.ensure_one()
        if self.credit_limit_custom > 0:
            if self.credit_used_percent >= 100:
                return _('⚠️ CRÉDITO AGOTADO: El cliente ha excedido su límite de crédito.')
            elif self.credit_used_percent >= 90:
                return _('⚠️ CRÉDITO CRÍTICO: El cliente ha usado el %.0f%% de su crédito.') % self.credit_used_percent
            elif self.credit_used_percent >= 75:
                return _('⚠️ CRÉDITO ALTO: El cliente ha usado el %.0f%% de su crédito.') % self.credit_used_percent
        return ''
    
    def _get_drugstore_warning(self):
        """Retorna un mensaje de advertencia sobre el estado de la resolución"""
        self.ensure_one()
        if self.drugstore_resolution_status == 'vencida':
            return _('⚠️ RESOLUCIÓN VENCIDA: La resolución de droguería ha expirado.')
        elif self.drugstore_resolution_status == 'por_vencer':
            days = (self.drugstore_resolution_expiry - fields.Date.today()).days
            return _('⚠️ RESOLUCIÓN POR VENCER: La resolución expira en %d días.') % days
        return ''

