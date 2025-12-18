# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class DispatchVehicle(models.Model):
    """
    Modelo para gestionar vehículos de reparto.
    Almacena información de la flota, capacidades y asignación.
    """
    _name = 'dispatch.vehicle'
    _description = 'Vehículo de Reparto'
    _order = 'license_plate'
    _rec_name = 'license_plate'
    
    # ========== INFORMACIÓN BÁSICA ==========
    license_plate = fields.Char(
        string='Placa',
        required=True,
        help='Placa de rodaje del vehículo'
    )
    
    active = fields.Boolean(
        string='Activo',
        default=True,
        help='Si está inactivo, no aparecerá en selecciones'
    )
    
    # ========== TIPO DE VEHÍCULO ==========
    vehicle_type = fields.Selection([
        ('motorcycle', 'Motocicleta'),
        ('mototaxi', 'Mototaxi'),
        ('van', 'Furgoneta'),
        ('truck_small', 'Camioneta'),
        ('truck_medium', 'Camión Mediano'),
        ('truck_large', 'Camión Grande'),
        ('other', 'Otro'),
    ], string='Tipo de Vehículo',
       default='van',
       required=True,
       tracking=True)
    
    # ========== INFORMACIÓN DEL VEHÍCULO ==========
    brand = fields.Char(
        string='Marca',
        help='Marca del vehículo (ej: Toyota, Nissan)'
    )
    
    model = fields.Char(
        string='Modelo',
        help='Modelo del vehículo'
    )
    
    year = fields.Integer(
        string='Año',
        help='Año de fabricación'
    )
    
    color = fields.Char(
        string='Color',
        help='Color del vehículo'
    )
    
    # ========== CAPACIDADES ==========
    capacity_kg = fields.Float(
        string='Capacidad (kg)',
        help='Capacidad de carga en kilogramos',
        digits=(10, 2)
    )
    
    capacity_m3 = fields.Float(
        string='Capacidad (m³)',
        help='Capacidad volumétrica en metros cúbicos',
        digits=(10, 2)
    )
    
    # ========== ESTADO DEL VEHÍCULO ==========
    status = fields.Selection([
        ('available', 'Disponible'),
        ('in_use', 'En Uso'),
        ('maintenance', 'En Mantenimiento'),
        ('inactive', 'Inactivo'),
    ], string='Estado',
       default='available',
       required=True,
       help='Estado operativo del vehículo')
    
    # ========== CONDUCTOR ASIGNADO ==========
    driver_id = fields.Many2one(
        'dispatch.driver',
        string='Conductor Asignado',
        help='Conductor principal asignado a este vehículo'
    )
    
    driver_name = fields.Char(
        string='Nombre del Conductor',
        related='driver_id.name',
        readonly=True
    )
    
    # ========== DOCUMENTACIÓN ==========
    soat_expiry_date = fields.Date(
        string='Vencimiento SOAT',
        help='Fecha de vencimiento del Seguro Obligatorio de Accidentes de Tránsito'
    )
    
    soat_expired = fields.Boolean(
        string='SOAT Vencido',
        compute='_compute_soat_expired',
        store=True
    )
    
    technical_review_date = fields.Date(
        string='Revisión Técnica',
        help='Fecha de última o próxima revisión técnica'
    )
    
    # ========== INFORMACIÓN ADICIONAL ==========
    notes = fields.Text(
        string='Notas',
        help='Notas adicionales sobre el vehículo'
    )
    
    image = fields.Binary(
        string='Foto',
        attachment=True,
        help='Foto del vehículo'
    )
    
    # ========== RELACIONES ==========
    route_ids = fields.One2many(
        'dispatch.route',
        'vehicle_id',
        string='Rutas Asignadas',
        help='Rutas en las que se ha usado este vehículo'
    )
    
    # ========== CAMPOS COMPUTADOS ==========
    route_count = fields.Integer(
        string='Cantidad de Rutas',
        compute='_compute_route_count'
    )
    
    _sql_constraints = [
        ('license_plate_unique', 'UNIQUE(license_plate)', 
         'Ya existe un vehículo con esta placa.')
    ]
    
    @api.depends('soat_expiry_date')
    def _compute_soat_expired(self):
        """Calcula si el SOAT está vencido"""
        today = fields.Date.today()
        for vehicle in self:
            if vehicle.soat_expiry_date:
                vehicle.soat_expired = vehicle.soat_expiry_date < today
            else:
                vehicle.soat_expired = False
    
    def _compute_route_count(self):
        """Cuenta rutas asignadas"""
        for vehicle in self:
            vehicle.route_count = len(vehicle.route_ids)
    
    @api.constrains('license_plate')
    def _check_license_plate(self):
        """Valida el formato de la placa"""
        for vehicle in self:
            if vehicle.license_plate:
                # Validación básica: debe tener al menos 6 caracteres (sin contar espacios)
                plate_clean = vehicle.license_plate.strip()
                if len(plate_clean) < 6:
                    raise ValidationError(_('La placa debe tener al menos 6 caracteres.'))
    
    @api.model_create_multi
    def create(self, vals_list):
        """Normaliza la placa al crear"""
        for vals in vals_list:
            if 'license_plate' in vals and vals['license_plate']:
                vals['license_plate'] = vals['license_plate'].strip().upper()
        return super(DispatchVehicle, self).create(vals_list)
    
    def write(self, vals):
        """Normaliza la placa al actualizar"""
        if 'license_plate' in vals and vals['license_plate']:
            vals['license_plate'] = vals['license_plate'].strip().upper()
        return super(DispatchVehicle, self).write(vals)
    
    @api.constrains('capacity_kg', 'capacity_m3')
    def _check_capacity(self):
        """Valida que las capacidades sean positivas"""
        for vehicle in self:
            if vehicle.capacity_kg and vehicle.capacity_kg < 0:
                raise ValidationError(_('La capacidad en kg debe ser un valor positivo.'))
            if vehicle.capacity_m3 and vehicle.capacity_m3 < 0:
                raise ValidationError(_('La capacidad en m³ debe ser un valor positivo.'))
    
    @api.constrains('year')
    def _check_year(self):
        """Valida que el año sea razonable"""
        for vehicle in self:
            if vehicle.year:
                current_year = fields.Date.today().year
                if vehicle.year < 1900 or vehicle.year > current_year + 1:
                    raise ValidationError(_(
                        'El año debe estar entre 1900 y %s.'
                    ) % (current_year + 1))
    
    def action_view_routes(self):
        """Acción para ver rutas del vehículo"""
        self.ensure_one()
        return {
            'name': _('Rutas de %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'dispatch.route',
            'view_mode': 'tree,form,kanban,calendar',
            'domain': [('vehicle_id', '=', self.id)],
            'context': {'default_vehicle_id': self.id},
        }
    
    def action_set_available(self):
        """Marca el vehículo como disponible"""
        self.write({'status': 'available'})
    
    def action_set_maintenance(self):
        """Marca el vehículo en mantenimiento"""
        self.write({'status': 'maintenance'})
    
    def action_set_inactive(self):
        """Marca el vehículo como inactivo"""
        self.write({'status': 'inactive'})

