# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleZone(models.Model):
    """
    Modelo para gestionar zonas de venta geográficas.
    Permite organizar clientes por ubicación y asignar ejecutivos de venta.
    """
    _name = 'sale.zone'
    _description = 'Zona de Venta'
    _order = 'code, name'
    _rec_name = 'complete_name'
    
    name = fields.Char(
        string='Nombre de Zona',
        required=True,
        help='Nombre descriptivo de la zona de venta'
    )
    
    code = fields.Char(
        string='Código',
        required=True,
        size=10,
        help='Código único de la zona (ej: ZONA-01, LIM-SUR)'
    )
    
    complete_name = fields.Char(
        string='Nombre Completo',
        compute='_compute_complete_name',
        store=True,
        help='Código y nombre completo de la zona'
    )
    
    active = fields.Boolean(
        string='Activo',
        default=True,
        help='Si está inactivo, la zona no estará disponible para nuevos clientes'
    )
    
    user_id = fields.Many2one(
        'res.users',
        string='Ejecutivo de Venta',
        help='Usuario responsable de esta zona de venta',
        tracking=True
    )
    
    partner_ids = fields.One2many(
        'res.partner',
        'sale_zone_id',
        string='Clientes',
        help='Clientes asignados a esta zona'
    )
    
    partner_count = fields.Integer(
        string='Número de Clientes',
        compute='_compute_partner_count',
        store=True,
        help='Cantidad total de clientes en esta zona'
    )
    
    description = fields.Text(
        string='Descripción',
        help='Descripción detallada de la zona, límites geográficos, etc.'
    )
    
    color = fields.Integer(
        string='Color',
        help='Color para identificar la zona en kanban/mapa'
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        default=lambda self: self.env.company,
        required=True
    )
    
    @api.depends('code', 'name')
    def _compute_complete_name(self):
        """Genera el nombre completo con código y nombre"""
        for record in self:
            if record.code and record.name:
                record.complete_name = f"[{record.code}] {record.name}"
            elif record.name:
                record.complete_name = record.name
            else:
                record.complete_name = record.code or ''
    
    @api.depends('partner_ids')
    def _compute_partner_count(self):
        """Calcula el número de clientes en la zona"""
        for record in self:
            record.partner_count = len(record.partner_ids)
    
    @api.constrains('code')
    def _check_code_unique(self):
        """Valida que el código sea único por compañía"""
        for record in self:
            if record.code:
                domain = [
                    ('code', '=', record.code),
                    ('company_id', '=', record.company_id.id),
                    ('id', '!=', record.id)
                ]
                if self.search_count(domain) > 0:
                    raise ValidationError(
                        _('Ya existe una zona con el código "%s" en esta compañía.') % record.code
                    )
    
    def action_view_partners(self):
        """Acción para ver los clientes de esta zona"""
        self.ensure_one()
        return {
            'name': _('Clientes de %s') % self.complete_name,
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'view_mode': 'list,form',
            'domain': [('sale_zone_id', '=', self.id)],
            'context': {'default_sale_zone_id': self.id}
        }
    
    _sql_constraints = [
        ('code_company_unique', 
         'UNIQUE(code, company_id)', 
         'El código de zona debe ser único por compañía.')
    ]

