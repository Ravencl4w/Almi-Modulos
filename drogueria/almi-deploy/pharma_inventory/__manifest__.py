# -*- coding: utf-8 -*-
{
    'name': 'Gestión de Inventario Farmacéutico',
    'version': '18.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Control avanzado de inventario para empresas farmacéuticas con trazabilidad, vencimientos y temperatura',
    'description': """
        Módulo de Gestión de Inventario Farmacéutico
        =============================================
        
        Extensión del módulo de inventario de Odoo para agregar funcionalidades
        específicas del sector farmacéutico y cumplimiento regulatorio.
        
        Características principales:
        * Sistema de Alertas de Vencimiento: Control automático de productos próximos a vencer
        * Control de Temperatura: Registro y monitoreo de temperatura por almacén/ubicación
        * Gestión de Canjes: Workflow completo para canje con laboratorios
        * Gestión de Rechazos: Control de productos no conformes y cuarentena
        * Kardex Farmacéutico: Vista mejorada de movimientos por producto
        * Trazabilidad por Lote: Mejoras visuales y alertas automáticas
        * Dashboard de Vencimientos: Panel de control ejecutivo
        * Reportes Especializados: Inventario valorizado, temperaturas, rechazos
        
        Cumplimiento regulatorio:
        * Control de cadena de frío
        * Trazabilidad completa de lotes
        * Registro de temperatura para auditorías
        * Gestión de productos vencidos y canjes
        * Control de calidad y rechazos
        
        Casos de uso:
        * Distribuidoras farmacéuticas
        * Droguerías con productos refrigerados
        * Farmacias con control de temperatura
        * Cumplimiento de BPM (Buenas Prácticas de Manufactura)
    """,
    'author': 'SSE',
    'depends': ['stock', 'product', 'pharma_product'],
    'data': [
        'security/ir.model.access.csv',
        'data/expiry_alert_data.xml',
        'data/rejection_reason_data.xml',
        'views/stock_lot_views.xml',
        'views/stock_location_views.xml',
        'views/temperature_record_views.xml',
        'views/stock_move_views.xml',
        'views/expiry_alert_views.xml',
        'views/stock_quant_views.xml',
        'views/dashboard_views.xml',
        'views/menu_items.xml',
        'wizards/register_temperature_views.xml',
        'wizards/process_rejection_views.xml',
        'report/kardex_report.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}

