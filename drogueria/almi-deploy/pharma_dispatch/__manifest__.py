# -*- coding: utf-8 -*-
{
    'name': 'Gestión de Despacho y Logística Farmacéutica',
    'version': '18.0.1.0.0',
    'category': 'Inventory/Delivery',
    'summary': 'Planificación de rutas, guías de remisión electrónica y recojo en local para farmacéuticas',
    'description': """
        Módulo de Gestión de Despacho y Logística
        ==========================================
        
        Sistema completo de despacho y logística para empresas farmacéuticas
        con integración a SUNAT para guías de remisión electrónica.
        
        Características principales:
        * Maestro de Conductores: Gestión completa de conductores con licencias
        * Maestro de Vehículos: Control de flota con capacidades y asignaciones
        * Planificación de Rutas: Asignación manual de pedidos a rutas de reparto
        * Guías de Remisión Electrónica (GRE): Envío automático a SUNAT vía NubeFact
        * Recojo en Local: Workflow de reserva, apartado y notificación al cliente
        * Integración con Zonas de Venta: Organización geográfica de entregas
        
        Workflows principales:
        1. Planificación de Reparto:
           - Crear ruta diaria/semanal
           - Asignar conductor y vehículo
           - Agregar pedidos manualmente
           - Seguimiento en tiempo real
           
        2. Guías de Remisión Electrónica:
           - Generación automática desde picking
           - Envío a SUNAT mediante NubeFact
           - Descarga de PDF, XML y CDR
           - Cumplimiento regulatorio total
           
        3. Recojo en Local:
           - Cliente reserva pedido
           - Sistema aparta stock
           - Notificación cuando está listo
           - Confirmación de recojo
        
        Cumplimiento SUNAT:
        * Catálogo de motivos de traslado (01-19)
        * Validación de datos obligatorios
        * Trazabilidad completa de guías
        * Integración con facturación electrónica
    """,
    'author': 'SSE',
    'depends': [
        'sale',
        'stock',
        'account',
        'pharma_partner',
    ],
    'data': [
        'security/pharma_dispatch_security.xml',
        'security/ir.model.access.csv',
        'data/dispatch_sequence_data.xml',
        'data/dispatch_sheet_sequence_data.xml',
        'data/dispatch_settlement_sequence_data.xml',
        'data/dispatch_motivo_traslado_data.xml',
        'data/stock_location_data.xml',
        'views/dispatch_driver_views.xml',
        'views/dispatch_vehicle_views.xml',
        'views/dispatch_sheet_views.xml',
        'views/dispatch_route_views.xml',
        'views/dispatch_settlement_views.xml',
        'views/dispatch_collection_sheet_views.xml',
        'views/account_move_views.xml',
        'views/stock_picking_views.xml',
        'views/sale_order_views.xml',
        'wizard/create_sheet_wizard_views.xml',
        'views/menu_items.xml',
        'security/pharma_dispatch_rules.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}

