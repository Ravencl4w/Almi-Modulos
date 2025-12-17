# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class DispatchDriver(models.Model):
    """
    Modelo para gestionar conductores de reparto.
    Almacena información personal, licencia y disponibilidad.
    """
    _name = 'dispatch.driver'
    _description = 'Conductor de Reparto'
    _order = 'name'
    _rec_name = 'name'
    
    # ========== INFORMACIÓN BÁSICA ==========
    name = fields.Char(
        string='Nombre Completo',
        required=True,
        help='Nombre completo del conductor'
    )
    
    code = fields.Char(
        string='Código',
        copy=False,
        help='Código interno del conductor'
    )
    
    active = fields.Boolean(
        string='Activo',
        default=True,
        help='Si está inactivo, no aparecerá en selecciones'
    )
    
    # ========== DOCUMENTO DE IDENTIDAD ==========
    document_type = fields.Selection([
        ('dni', 'DNI'),
        ('ce', 'Carnet de Extranjería'),
        ('passport', 'Pasaporte'),
    ], string='Tipo de Documento',
       default='dni',
       required=True)
    
    document_number = fields.Char(
        string='Número de Documento',
        required=True,
        help='DNI, CE o Pasaporte'
    )
    
    # ========== LICENCIA DE CONDUCIR ==========
    license_number = fields.Char(
        string='Número de Licencia',
        help='Número de licencia de conducir'
    )
    
    license_category = fields.Selection([
        ('A-I', 'A-I (Motocicletas)'),
        ('A-II-a', 'A-II-a (Mototaxi)'),
        ('A-II-b', 'A-II-b (Triciclos motorizados)'),
        ('A-III-a', 'A-III-a (Vehículos hasta 3,500 kg)'),
        ('A-III-b', 'A-III-b (Taxis)'),
        ('A-III-c', 'A-III-c (Ambulancias)'),
        ('B-I', 'B-I (Vehículos pesados)'),
        ('B-II-a', 'B-II-a (Buses y ómnibus)'),
        ('B-II-b', 'B-II-b (Camiones)'),
        ('B-II-c', 'B-II-c (Remolques)'),
    ], string='Categoría de Licencia',
       help='Categoría según MTC Perú')
    
    license_expiry_date = fields.Date(
        string='Fecha de Vencimiento',
        help='Fecha de vencimiento de la licencia'
    )
    
    license_expired = fields.Boolean(
        string='Licencia Vencida',
        compute='_compute_license_expired',
        store=True,
        help='Indica si la licencia está vencida'
    )
    
    # ========== CONTACTO ==========
    phone = fields.Char(
        string='Teléfono',
        help='Número de teléfono de contacto'
    )
    
    mobile = fields.Char(
        string='Móvil',
        help='Número de celular'
    )
    
    email = fields.Char(
        string='Email',
        required=True,
        help='Correo electrónico (requerido para acceso a la aplicación)'
    )
    
    # ========== USUARIO DE ODOO ==========
    user_id = fields.Many2one(
        'res.users',
        string='Usuario de Sistema',
        readonly=True,
        copy=False,
        help='Usuario de Odoo asociado para acceso a la aplicación móvil'
    )
    
    has_user = fields.Boolean(
        string='Tiene Usuario',
        compute='_compute_has_user',
        store=True,
        help='Indica si el conductor tiene un usuario de sistema asociado'
    )
    
    # ========== FOTO ==========
    image = fields.Binary(
        string='Foto',
        attachment=True,
        help='Foto del conductor'
    )
    
    # ========== DIRECCIÓN ==========
    address = fields.Text(
        string='Dirección',
        help='Dirección completa del conductor'
    )
    
    # ========== INFORMACIÓN ADICIONAL ==========
    notes = fields.Text(
        string='Notas',
        help='Notas adicionales sobre el conductor'
    )
    
    # ========== RELACIONES ==========
    vehicle_ids = fields.One2many(
        'dispatch.vehicle',
        'driver_id',
        string='Vehículos Asignados',
        help='Vehículos asignados a este conductor'
    )
    
    route_ids = fields.One2many(
        'dispatch.route',
        'driver_id',
        string='Rutas Asignadas',
        help='Rutas de reparto asignadas'
    )
    
    # ========== CAMPOS COMPUTADOS ==========
    vehicle_count = fields.Integer(
        string='Cantidad de Vehículos',
        compute='_compute_vehicle_count'
    )
    
    route_count = fields.Integer(
        string='Cantidad de Rutas',
        compute='_compute_route_count'
    )
    
    _sql_constraints = [
        ('document_number_unique', 'UNIQUE(document_number)', 
         'Ya existe un conductor con este número de documento.')
    ]
    
    @api.model_create_multi
    def create(self, vals_list):
        """Crea conductores y sus usuarios asociados automáticamente"""
        drivers = super().create(vals_list)
        
        # Para cada conductor creado, crear su usuario si tiene email
        for driver in drivers:
            if driver.email and not driver.user_id:
                try:
                    driver._create_user_for_driver()
                except Exception as e:
                    # Si falla la creación del usuario, registrar el error pero no bloquear
                    # la creación del conductor
                    import logging
                    _logger = logging.getLogger(__name__)
                    _logger.warning(
                        f'No se pudo crear usuario para conductor {driver.name}: {str(e)}'
                    )
        
        return drivers
    
    def write(self, vals):
        """Sincroniza cambios del conductor con su usuario asociado"""
        result = super().write(vals)
        
        # Sincronizar cambios con el usuario asociado
        for driver in self:
            if driver.user_id:
                user_vals = {}
                
                # Sincronizar estado activo/inactivo
                if 'active' in vals:
                    user_vals['active'] = vals['active']
                
                # Sincronizar email/login
                if 'email' in vals:
                    user_vals['login'] = vals['email']
                    user_vals['email'] = vals['email']
                
                # Sincronizar nombre
                if 'name' in vals:
                    user_vals['name'] = vals['name']
                
                # Actualizar el usuario si hay cambios
                if user_vals:
                    try:
                        driver.user_id.sudo().write(user_vals)
                    except Exception as e:
                        import logging
                        _logger = logging.getLogger(__name__)
                        _logger.warning(
                            f'No se pudo sincronizar usuario para conductor {driver.name}: {str(e)}'
                        )
        
        return result
    
    @api.depends('license_expiry_date')
    def _compute_license_expired(self):
        """Calcula si la licencia está vencida"""
        today = fields.Date.today()
        for driver in self:
            if driver.license_expiry_date:
                driver.license_expired = driver.license_expiry_date < today
            else:
                driver.license_expired = False
    
    def _compute_vehicle_count(self):
        """Cuenta vehículos asignados"""
        for driver in self:
            driver.vehicle_count = len(driver.vehicle_ids)
    
    def _compute_route_count(self):
        """Cuenta rutas asignadas"""
        for driver in self:
            driver.route_count = len(driver.route_ids)
    
    @api.depends('user_id')
    def _compute_has_user(self):
        """Calcula si el conductor tiene usuario asociado"""
        for driver in self:
            driver.has_user = bool(driver.user_id)
    
    @api.constrains('document_number')
    def _check_document_number(self):
        """Valida el número de documento"""
        for driver in self:
            if driver.document_number:
                if driver.document_type == 'dni' and len(driver.document_number) != 8:
                    raise ValidationError(_('El DNI debe tener 8 dígitos.'))
                if driver.document_type == 'dni' and not driver.document_number.isdigit():
                    raise ValidationError(_('El DNI debe contener solo números.'))
    
    @api.constrains('email')
    def _check_email(self):
        """Valida el email del conductor"""
        for driver in self:
            if driver.email:
                # Validar formato básico de email
                import re
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, driver.email):
                    raise ValidationError(_('El formato del email no es válido.'))
                
                # Validar que el email no esté en uso por otro usuario (excepto el asociado a este conductor)
                existing_user = self.env['res.users'].sudo().search([
                    ('login', '=', driver.email),
                    ('id', '!=', driver.user_id.id if driver.user_id else False)
                ], limit=1)
                if existing_user:
                    raise ValidationError(_(
                        'El email "%s" ya está en uso por otro usuario del sistema.'
                    ) % driver.email)
    
    @api.constrains('license_expiry_date')
    def _check_license_expiry(self):
        """Valida que la licencia no esté vencida al asignar"""
        today = fields.Date.today()
        for driver in self:
            if driver.license_expiry_date and driver.license_expiry_date < today:
                if driver.active:
                    raise ValidationError(_(
                        'No se puede activar un conductor con licencia vencida. '
                        'Por favor, actualice la fecha de vencimiento.'
                    ))
    
    def _create_user_for_driver(self):
        """Crea un usuario de Odoo para el conductor"""
        self.ensure_one()
        
        if not self.email:
            raise ValidationError(_('El conductor debe tener un email para crear el usuario.'))
        
        if self.user_id:
            raise ValidationError(_('Este conductor ya tiene un usuario asociado.'))
        
        # Verificar que el email no esté en uso
        existing_user = self.env['res.users'].sudo().search([('login', '=', self.email)], limit=1)
        if existing_user:
            raise ValidationError(_(
                'Ya existe un usuario con el email "%s". '
                'Por favor use otro email o asocie el usuario existente.'
            ) % self.email)
        
        # Obtener el grupo de conductores
        group_driver = self.env.ref('pharma_dispatch.group_pharma_dispatch_driver', raise_if_not_found=False)
        group_portal = self.env.ref('base.group_portal')
        
        groups = [group_portal.id]
        if group_driver:
            groups.append(group_driver.id)
        
        # Crear el usuario
        user_vals = {
            'name': self.name,
            'login': self.email,
            'email': self.email,
            'active': self.active,
            'groups_id': [(6, 0, groups)],
            'company_id': self.env.company.id,
            'company_ids': [(6, 0, [self.env.company.id])],
        }
        
        user = self.env['res.users'].sudo().create(user_vals)
        
        # Vincular el usuario al conductor
        self.user_id = user.id
        
        return user
    
    def action_reset_password(self):
        """Envía un email para resetear la contraseña del usuario"""
        self.ensure_one()
        
        if not self.user_id:
            raise ValidationError(_('Este conductor no tiene un usuario asociado.'))
        
        # Usar el wizard estándar de Odoo para resetear contraseña
        return {
            'type': 'ir.actions.act_window',
            'name': _('Resetear Contraseña'),
            'res_model': 'change.password.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'active_model': 'res.users',
                'active_id': self.user_id.id,
                'active_ids': [self.user_id.id],
            },
        }
    
    def action_view_vehicles(self):
        """Acción para ver vehículos asignados"""
        self.ensure_one()
        return {
            'name': _('Vehículos de %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'dispatch.vehicle',
            'view_mode': 'tree,form',
            'domain': [('driver_id', '=', self.id)],
            'context': {'default_driver_id': self.id},
        }
    
    def action_view_routes(self):
        """Acción para ver rutas asignadas"""
        self.ensure_one()
        return {
            'name': _('Rutas de %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'dispatch.route',
            'view_mode': 'tree,form,kanban,calendar',
            'domain': [('driver_id', '=', self.id)],
            'context': {'default_driver_id': self.id},
        }

