# -*- coding: utf-8 -*-
{
    'name': 'Gestión de Liquidación y Tesorería Farmacéutica',
    'version': '18.0.1.0.0',
    'category': 'Accounting/Treasury',
    'summary': 'Planillas de reparto, liquidaciones de transportistas y hojas de cobranza',
    'description': """
        Módulo de Gestión de Liquidación y Tesorería
        ============================================
        
        Sistema completo de gestión de cobranzas y liquidaciones para empresas farmacéuticas
        integrado con el módulo de despacho y logística.
        
        Características principales:
        * Planillas de Reparto: Agrupación de facturas para asignar a rutas
        * Liquidaciones: Proceso de registro y aprobación de cobros del transportista
        * Hojas de Cobranza: Seguimiento de cobranza por vendedor
        * API REST: Endpoints para app móvil de transportistas
        * Integración completa con pharma_dispatch
        
        Workflows principales:
        1. Planillas de Reparto:
           - Selección masiva de facturas confirmadas
           - Asignación a rutas de reparto existentes o nuevas
           - Seguimiento de estado de cobranza por factura
           
        2. Liquidación de Transportista:
           - Transportista registra cobros por factura vía app móvil
           - Envío de liquidación para revisión
           - Liquidador aprueba o rechaza
           - Actualización automática de estados de pago
           
        3. Hoja de Cobranza por Vendedor:
           - Seguimiento de facturas asignadas a cada vendedor
           - Dashboard de efectividad de cobranza
           - Reportes y análisis por periodo
        
        Integraciones:
        * pharma_dispatch: Rutas, conductores, vehículos
        * account: Facturas y pagos
        * sale: Pedidos de venta
    """,
    'author': 'SSE',
    'depends': [
        'account',
        'sale',
        'pharma_dispatch',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/treasury_sequence_data.xml',
        'views/treasury_settlement_sheet_views.xml',
        'views/treasury_settlement_views.xml',
        'views/treasury_collection_sheet_views.xml',
        'views/menu_items.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}

