# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductLaboratory(models.Model):
    """
    Modelo para gestionar laboratorios fabricantes de productos farmacéuticos.
    Permite organizar productos por laboratorio y sus líneas de producto.
    """
    _name = 'product.laboratory'
    _description = 'Laboratorio Fabricante'
    _order = 'name'
    _rec_name = 'name'
    
    name = fields.Char(
        string='Nombre del Laboratorio',
        required=True,
        help='Nombre completo del laboratorio fabricante'
    )
    
    code = fields.Char(
        string='Código',
        help='Código de identificación del laboratorio (ej: LAB-001)'
    )
    
    short_name = fields.Char(
        string='Nombre Corto',
        help='Nombre abreviado del laboratorio (ej: LAB1, BAYER, PFIZER)'
    )
    
    active = fields.Boolean(
        string='Activo',
        default=True,
        help='Si está inactivo, el laboratorio no estará disponible para nuevos productos'
    )
    
    description = fields.Text(
        string='Descripción',
        help='Información del laboratorio, especialidades, certificaciones, etc.'
    )
    
    logo = fields.Binary(
        string='Logo',
        help='Logo del laboratorio'
    )
    
    logo_filename = fields.Char(
        string='Nombre del Archivo de Logo'
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Contacto del Laboratorio',
        domain="[('is_company', '=', True)]",
        help='Contacto asociado al laboratorio en el sistema'
    )
    
    country_id = fields.Many2one(
        'res.country',
        string='País de Origen',
        help='País donde se encuentra el laboratorio'
    )
    
    website = fields.Char(
        string='Sitio Web',
        help='URL del sitio web del laboratorio'
    )
    
    product_count = fields.Integer(
        string='Número de Productos',
        compute='_compute_product_count',
        store=True,
        help='Cantidad total de productos de este laboratorio'
    )
    
    product_ids = fields.One2many(
        'product.template',
        'laboratory_id',
        string='Productos',
        help='Productos fabricados por este laboratorio'
    )
    
    line_ids = fields.One2many(
        'product.laboratory.line',
        'laboratory_id',
        string='Líneas de Producto',
        help='Líneas de producto del laboratorio'
    )
    
    line_count = fields.Integer(
        string='Número de Líneas',
        compute='_compute_line_count',
        store=True,
        help='Cantidad de líneas de producto'
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
    
    notes = fields.Text(
        string='Notas',
        help='Notas adicionales sobre el laboratorio'
    )
    
    @api.depends('product_ids')
    def _compute_product_count(self):
        """Calcula el número de productos del laboratorio"""
        for record in self:
            record.product_count = len(record.product_ids)
    
    @api.depends('line_ids')
    def _compute_line_count(self):
        """Calcula el número de líneas del laboratorio"""
        for record in self:
            record.line_count = len(record.line_ids)
    
    @api.constrains('name')
    def _check_name_unique(self):
        """Valida que el nombre del laboratorio sea único"""
        for record in self:
            if record.name:
                domain = [
                    ('name', '=ilike', record.name),
                    ('id', '!=', record.id)
                ]
                if self.search_count(domain) > 0:
                    raise ValidationError(
                        _('Ya existe un laboratorio con el nombre "%s".') % record.name
                    )
    
    def action_view_products(self):
        """Acción para ver los productos de este laboratorio"""
        self.ensure_one()
        return {
            'name': _('Productos de %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'product.template',
            'view_mode': 'list,form,kanban',
            'domain': [('laboratory_id', '=', self.id)],
            'context': {'default_laboratory_id': self.id}
        }
    
    def action_view_lines(self):
        """Acción para ver las líneas de producto del laboratorio"""
        self.ensure_one()
        return {
            'name': _('Líneas de %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'product.laboratory.line',
            'view_mode': 'list,form',
            'domain': [('laboratory_id', '=', self.id)],
            'context': {'default_laboratory_id': self.id}
        }

