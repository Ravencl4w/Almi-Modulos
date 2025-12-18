# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class ProductTemplate(models.Model):
    """
    Extensión del modelo product.template para agregar campos específicos
    de productos farmacéuticos.
    """
    _inherit = 'product.template'
    
    # ========== MARCA ==========
    brand_id = fields.Many2one(
        'product.brand',
        string='Marca',
        tracking=True,
        help='Marca comercial del producto'
    )
    
    brand_name = fields.Char(
        string='Nombre de Marca',
        related='brand_id.name',
        readonly=True
    )
    
    # ========== LABORATORIO FABRICANTE ==========
    laboratory_id = fields.Many2one(
        'product.laboratory',
        string='Laboratorio Fabricante',
        tracking=True,
        help='Laboratorio que fabrica el producto'
    )
    
    laboratory_name = fields.Char(
        string='Nombre del Laboratorio',
        related='laboratory_id.name',
        store=True,
        readonly=True
    )
    
    laboratory_short_name = fields.Char(
        string='Código de Laboratorio',
        related='laboratory_id.short_name',
        store=True,
        readonly=True
    )
    
    # ========== LÍNEA DE LABORATORIO ==========
    laboratory_line_id = fields.Many2one(
        'product.laboratory.line',
        string='Línea de Laboratorio',
        domain="[('laboratory_id', '=', laboratory_id)]",
        tracking=True,
        help='Línea de producto dentro del laboratorio (ej: LAB1, LAB2)'
    )
    
    laboratory_line_code = fields.Char(
        string='Código de Línea',
        related='laboratory_line_id.code',
        store=True,
        readonly=True
    )
    
    # ========== PROVEEDOR PRINCIPAL ==========
    main_supplier_id = fields.Many2one(
        'res.partner',
        string='Proveedor Principal',
        compute='_compute_main_supplier',
        store=True,
        readonly=False,
        domain="[('supplier_rank', '>', 0)]",
        tracking=True,
        help='Proveedor preferido para este producto'
    )
    
    main_supplier_price = fields.Float(
        string='Precio Proveedor Principal',
        compute='_compute_main_supplier',
        store=True,
        readonly=True,
        help='Precio del proveedor principal'
    )
    
    # ========== REGISTRO SANITARIO ==========
    sanitary_registration = fields.Char(
        string='Registro Sanitario',
        tracking=True,
        help='Número de registro sanitario emitido por la autoridad competente (DIGEMID, INVIMA, etc.)'
    )
    
    sanitary_registration_date = fields.Date(
        string='Fecha de Emisión',
        tracking=True,
        help='Fecha de emisión del registro sanitario'
    )
    
    sanitary_registration_expiry = fields.Date(
        string='Fecha de Vencimiento',
        tracking=True,
        help='Fecha de vencimiento del registro sanitario'
    )
    
    sanitary_registration_status = fields.Selection([
        ('vigente', 'Vigente'),
        ('por_vencer', 'Por Vencer (60 días)'),
        ('vencido', 'Vencido'),
        ('no_aplica', 'No Aplica'),
    ], string='Estado del Registro',
       compute='_compute_sanitary_registration_status',
       store=True,
       help='Estado actual del registro sanitario')
    
    sanitary_registration_file = fields.Binary(
        string='Archivo del Registro',
        help='Archivo PDF o imagen del registro sanitario'
    )
    
    sanitary_registration_filename = fields.Char(
        string='Nombre del Archivo'
    )
    
    sanitary_authority = fields.Char(
        string='Autoridad Sanitaria',
        help='Entidad que emitió el registro (ej: DIGEMID-Perú, INVIMA-Colombia, ANVISA-Brasil)'
    )
    
    requires_sanitary_registration = fields.Boolean(
        string='Requiere Registro Sanitario',
        default=False,
        help='Indica si este producto requiere registro sanitario para su comercialización'
    )
    
    sanitary_notes = fields.Text(
        string='Notas Sanitarias',
        help='Observaciones sobre el registro sanitario y requisitos'
    )
    
    # ========== PRODUCTOS RELACIONADOS (Mejorados) ==========
    # Definimos estos campos si no existen (pueden venir del módulo 'sale')
    alternative_product_ids = fields.Many2many(
        'product.template',
        'product_alternative_rel',
        'src_id',
        'dest_id',
        string='Productos Alternativos',
        help='Productos que pueden sustituir a este producto'
    )
    
    optional_product_ids = fields.Many2many(
        'product.template',
        'product_optional_rel',
        'src_id',
        'dest_id',
        string='Productos Opcionales',
        help='Productos complementarios que se pueden ofrecer junto con este'
    )
    
    accessory_product_ids = fields.Many2many(
        'product.template',
        'product_accessory_rel',
        'src_id',
        'dest_id',
        string='Accesorios',
        help='Productos accesorios relacionados'
    )
    
    has_related_products = fields.Boolean(
        string='Tiene Productos Relacionados',
        compute='_compute_has_related_products',
        help='Indica si el producto tiene alternativos, opcionales o accesorios'
    )
    
    related_products_count = fields.Integer(
        string='Total Productos Relacionados',
        compute='_compute_has_related_products',
        help='Cantidad total de productos relacionados'
    )
    
    # ========== INFORMACIÓN ADICIONAL FARMACÉUTICA ==========
    active_ingredient = fields.Char(
        string='Principio Activo',
        help='Componente activo del medicamento'
    )
    
    concentration = fields.Char(
        string='Concentración',
        help='Concentración del principio activo (ej: 500mg, 10ml)'
    )
    
    pharmaceutical_form = fields.Selection([
        ('tablet', 'Tableta'),
        ('capsule', 'Cápsula'),
        ('syrup', 'Jarabe'),
        ('suspension', 'Suspensión'),
        ('solution', 'Solución'),
        ('injection', 'Inyectable'),
        ('cream', 'Crema'),
        ('ointment', 'Ungüento'),
        ('drops', 'Gotas'),
        ('spray', 'Spray'),
        ('inhaler', 'Inhalador'),
        ('patch', 'Parche'),
        ('suppository', 'Supositorio'),
        ('powder', 'Polvo'),
        ('gel', 'Gel'),
        ('other', 'Otro'),
    ], string='Forma Farmacéutica',
       help='Presentación física del medicamento')
    
    therapeutic_group = fields.Char(
        string='Grupo Terapéutico',
        help='Clasificación terapéutica del producto (ej: Analgésico, Antibiótico)'
    )
    
    controlled_substance = fields.Boolean(
        string='Sustancia Controlada',
        default=False,
        help='Indica si el producto es una sustancia controlada que requiere receta especial'
    )
    
    requires_prescription = fields.Boolean(
        string='Requiere Receta Médica',
        default=False,
        help='Indica si el producto requiere receta médica para su venta'
    )
    
    cold_chain = fields.Boolean(
        string='Cadena de Frío',
        default=False,
        help='Indica si el producto requiere refrigeración (cadena de frío)'
    )
    
    storage_temperature = fields.Char(
        string='Temperatura de Almacenamiento',
        help='Temperatura requerida para almacenar el producto (ej: 2-8°C)'
    )
    
    # ========== CAMPOS COMPUTADOS ==========
    
    @api.depends('seller_ids', 'seller_ids.partner_id')
    def _compute_main_supplier(self):
        """Determina el proveedor principal (primer proveedor de la lista o el marcado)"""
        for product in self:
            if product.seller_ids:
                # El primer proveedor de la lista es el principal por defecto
                main_seller = product.seller_ids[0]
                product.main_supplier_id = main_seller.partner_id
                product.main_supplier_price = main_seller.price
            else:
                product.main_supplier_id = False
                product.main_supplier_price = 0.0
    
    @api.depends('sanitary_registration_expiry', 'requires_sanitary_registration')
    def _compute_sanitary_registration_status(self):
        """Calcula el estado del registro sanitario"""
        today = fields.Date.today()
        for product in self:
            if not product.requires_sanitary_registration:
                product.sanitary_registration_status = 'no_aplica'
            elif not product.sanitary_registration_expiry:
                if product.sanitary_registration:
                    product.sanitary_registration_status = 'vigente'
                else:
                    product.sanitary_registration_status = 'no_aplica'
            else:
                days_to_expiry = (product.sanitary_registration_expiry - today).days
                if days_to_expiry < 0:
                    product.sanitary_registration_status = 'vencido'
                elif days_to_expiry <= 60:
                    product.sanitary_registration_status = 'por_vencer'
                else:
                    product.sanitary_registration_status = 'vigente'
    
    @api.depends('alternative_product_ids', 'optional_product_ids', 'accessory_product_ids')
    def _compute_has_related_products(self):
        """Verifica si el producto tiene productos relacionados"""
        for product in self:
            count = (len(product.alternative_product_ids) + 
                    len(product.optional_product_ids) + 
                    len(product.accessory_product_ids))
            product.has_related_products = count > 0
            product.related_products_count = count
    
    # ========== VALIDACIONES ==========
    
    @api.constrains('sanitary_registration_date', 'sanitary_registration_expiry')
    def _check_sanitary_dates(self):
        """Valida que las fechas del registro sanitario sean coherentes"""
        for product in self:
            if product.sanitary_registration_date and product.sanitary_registration_expiry:
                if product.sanitary_registration_expiry < product.sanitary_registration_date:
                    raise ValidationError(
                        _('La fecha de vencimiento del registro sanitario no puede ser anterior a la fecha de emisión.')
                    )
    
    @api.onchange('laboratory_id')
    def _onchange_laboratory_id(self):
        """Limpia la línea de laboratorio al cambiar el laboratorio"""
        if self.laboratory_id and self.laboratory_line_id:
            if self.laboratory_line_id.laboratory_id != self.laboratory_id:
                self.laboratory_line_id = False
    
    # ========== MÉTODOS DE NEGOCIO ==========
    
    def action_view_related_products(self):
        """Acción para ver todos los productos relacionados"""
        self.ensure_one()
        
        related_ids = (self.alternative_product_ids.ids + 
                      self.optional_product_ids.ids + 
                      self.accessory_product_ids.ids)
        
        return {
            'name': _('Productos Relacionados de %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'product.template',
            'view_mode': 'list,form,kanban',
            'domain': [('id', 'in', related_ids)],
            'context': {'create': False}
        }
    
    def action_set_main_supplier(self):
        """Permite seleccionar manualmente el proveedor principal"""
        self.ensure_one()
        if not self.seller_ids:
            raise UserError(_('Este producto no tiene proveedores configurados.'))
        
        return {
            'name': _('Seleccionar Proveedor Principal'),
            'type': 'ir.actions.act_window',
            'res_model': 'product.template',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
        }
    
    def _get_sanitary_warning(self):
        """Retorna un mensaje de advertencia sobre el registro sanitario"""
        self.ensure_one()
        if self.sanitary_registration_status == 'vencido':
            return _('⚠️ REGISTRO VENCIDO: El registro sanitario ha expirado.')
        elif self.sanitary_registration_status == 'por_vencer':
            days = (self.sanitary_registration_expiry - fields.Date.today()).days
            return _('⚠️ REGISTRO POR VENCER: El registro expira en %d días.') % days
        elif self.requires_sanitary_registration and not self.sanitary_registration:
            return _('⚠️ SIN REGISTRO: Este producto requiere registro sanitario.')
        return ''
    
    def action_view_same_laboratory(self):
        """Ver productos del mismo laboratorio"""
        self.ensure_one()
        if not self.laboratory_id:
            raise UserError(_('Este producto no tiene laboratorio asignado.'))
        
        return self.laboratory_id.action_view_products()
    
    def action_view_same_brand(self):
        """Ver productos de la misma marca"""
        self.ensure_one()
        if not self.brand_id:
            raise UserError(_('Este producto no tiene marca asignada.'))
        
        return self.brand_id.action_view_products()

