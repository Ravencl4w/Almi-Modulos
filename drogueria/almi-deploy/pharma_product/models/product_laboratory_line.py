# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductLaboratoryLine(models.Model):
    """
    Modelo para gestionar líneas de producto dentro de cada laboratorio.
    Ejemplo: LAB1, LAB2 para Laboratorio Jimenez.
    """
    _name = 'product.laboratory.line'
    _description = 'Línea de Laboratorio'
    _order = 'laboratory_id, code, name'
    _rec_name = 'complete_name'
    
    name = fields.Char(
        string='Nombre de la Línea',
        required=True,
        help='Nombre descriptivo de la línea de producto'
    )
    
    code = fields.Char(
        string='Código',
        required=True,
        help='Código simplificado de la línea (ej: LAB1, LAB2, ONCO, CARDIO)'
    )
    
    complete_name = fields.Char(
        string='Nombre Completo',
        compute='_compute_complete_name',
        store=True,
        help='Código y nombre completo de la línea'
    )
    
    laboratory_id = fields.Many2one(
        'product.laboratory',
        string='Laboratorio',
        required=True,
        ondelete='cascade',
        help='Laboratorio al que pertenece esta línea'
    )
    
    laboratory_name = fields.Char(
        string='Nombre del Laboratorio',
        related='laboratory_id.name',
        store=True,
        readonly=True
    )
    
    active = fields.Boolean(
        string='Activo',
        default=True,
        help='Si está inactivo, la línea no estará disponible para nuevos productos'
    )
    
    description = fields.Text(
        string='Descripción',
        help='Descripción de la línea de producto, productos que incluye, características'
    )
    
    product_count = fields.Integer(
        string='Número de Productos',
        compute='_compute_product_count',
        store=True,
        help='Cantidad total de productos en esta línea'
    )
    
    product_ids = fields.One2many(
        'product.template',
        'laboratory_line_id',
        string='Productos',
        help='Productos de esta línea'
    )
    
    color = fields.Integer(
        string='Color',
        help='Color para visualización en kanban'
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        default=lambda self: self.env.company
    )
    
    @api.depends('code', 'name', 'laboratory_id.short_name', 'laboratory_id.name')
    def _compute_complete_name(self):
        """Genera el nombre completo con laboratorio, código y nombre"""
        for record in self:
            lab_name = record.laboratory_id.short_name or record.laboratory_id.name
            if lab_name and record.code and record.name:
                record.complete_name = f"{lab_name} - [{record.code}] {record.name}"
            elif record.code and record.name:
                record.complete_name = f"[{record.code}] {record.name}"
            elif record.name:
                record.complete_name = record.name
            else:
                record.complete_name = record.code or ''
    
    @api.depends('product_ids')
    def _compute_product_count(self):
        """Calcula el número de productos en la línea"""
        for record in self:
            record.product_count = len(record.product_ids)
    
    @api.constrains('code', 'laboratory_id')
    def _check_code_unique(self):
        """Valida que el código sea único por laboratorio"""
        for record in self:
            if record.code and record.laboratory_id:
                domain = [
                    ('code', '=', record.code),
                    ('laboratory_id', '=', record.laboratory_id.id),
                    ('id', '!=', record.id)
                ]
                if self.search_count(domain) > 0:
                    raise ValidationError(
                        _('Ya existe una línea con el código "%s" en el laboratorio %s.') 
                        % (record.code, record.laboratory_id.name)
                    )
    
    def action_view_products(self):
        """Acción para ver los productos de esta línea"""
        self.ensure_one()
        return {
            'name': _('Productos de %s') % self.complete_name,
            'type': 'ir.actions.act_window',
            'res_model': 'product.template',
            'view_mode': 'list,form,kanban',
            'domain': [('laboratory_line_id', '=', self.id)],
            'context': {'default_laboratory_line_id': self.id, 'default_laboratory_id': self.laboratory_id.id}
        }
    
    _sql_constraints = [
        ('code_laboratory_unique', 
         'UNIQUE(code, laboratory_id)', 
         'El código de línea debe ser único por laboratorio.')
    ]

