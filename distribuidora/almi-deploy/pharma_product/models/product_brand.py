# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductBrand(models.Model):
    """
    Modelo para gestionar marcas de productos farmacéuticos.
    Permite organizar productos por marca comercial.
    """
    _name = 'product.brand'
    _description = 'Marca de Producto'
    _order = 'name'
    _rec_name = 'name'
    
    name = fields.Char(
        string='Nombre de la Marca',
        required=True,
        translate=True,
        help='Nombre comercial de la marca'
    )
    
    code = fields.Char(
        string='Código',
        help='Código de identificación de la marca (opcional)'
    )
    
    active = fields.Boolean(
        string='Activo',
        default=True,
        help='Si está inactivo, la marca no estará disponible para nuevos productos'
    )
    
    description = fields.Text(
        string='Descripción',
        help='Descripción de la marca, características, historia, etc.'
    )
    
    logo = fields.Binary(
        string='Logo',
        help='Logo de la marca'
    )
    
    logo_filename = fields.Char(
        string='Nombre del Archivo de Logo'
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Propietario de la Marca',
        help='Empresa propietaria de la marca'
    )
    
    product_count = fields.Integer(
        string='Número de Productos',
        compute='_compute_product_count',
        store=True,
        help='Cantidad total de productos con esta marca'
    )
    
    product_ids = fields.One2many(
        'product.template',
        'brand_id',
        string='Productos',
        help='Productos asociados a esta marca'
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        default=lambda self: self.env.company
    )
    
    color = fields.Integer(
        string='Color',
        help='Color para visualización en kanban'
    )
    
    @api.depends('product_ids')
    def _compute_product_count(self):
        """Calcula el número de productos de la marca"""
        for record in self:
            record.product_count = len(record.product_ids)
    
    @api.constrains('name')
    def _check_name_unique(self):
        """Valida que el nombre de la marca sea único"""
        for record in self:
            if record.name:
                domain = [
                    ('name', '=ilike', record.name),
                    ('id', '!=', record.id)
                ]
                if self.search_count(domain) > 0:
                    raise ValidationError(
                        _('Ya existe una marca con el nombre "%s".') % record.name
                    )
    
    def action_view_products(self):
        """Acción para ver los productos de esta marca"""
        self.ensure_one()
        return {
            'name': _('Productos de %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'product.template',
            'view_mode': 'list,form,kanban',
            'domain': [('brand_id', '=', self.id)],
            'context': {'default_brand_id': self.id}
        }

