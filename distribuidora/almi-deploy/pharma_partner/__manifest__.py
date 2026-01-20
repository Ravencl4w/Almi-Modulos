# -*- coding: utf-8 -*-
{
    'name': 'Gestión de Contactos Farmacéuticos',
    'version': '18.0.1.0.0',
    'category': 'Sales/CRM',
    'summary': 'Extensión del módulo de contactos para empresas farmacéuticas con distribuidora y droguería',
    'description': """
        Módulo de Gestión de Contactos para Empresas Farmacéuticas
        ===========================================================
        
        Este módulo extiende el módulo de contactos de Odoo para agregar campos
        específicos necesarios para una empresa farmacéutica con operaciones de
        distribución y droguería.
        
        Características principales:
        * Giro del negocio: Clasificación de clientes por actividad comercial
        * Zona de venta: Asignación geográfica de clientes por ejecutivo
        * Lista de precios: Asignación automática de precios según tipo de cliente
        * Gestión de créditos: Sistema completo de líneas de crédito con límites
        * Resolución de droguería: Control de permisos y licencias vigentes
        * Geolocalización: Integrada con Google Maps para optimización de rutas
        
        Casos de uso:
        * Distribuidora: Control de zonas de venta y créditos
        * Droguería: Verificación de resoluciones y permisos
        * Comercial: Segmentación de clientes por giro y zona
    """,
    'author': 'SSE',
    'depends': ['base', 'contacts', 'account', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'data/sale_zone_data.xml',
        'data/business_sector_data.xml',
        'views/sale_zone_views.xml',
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}

