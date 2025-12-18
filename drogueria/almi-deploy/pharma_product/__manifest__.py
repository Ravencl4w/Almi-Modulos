# -*- coding: utf-8 -*-
{
    'name': 'Gestión de Productos Farmacéuticos',
    'version': '18.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Extensión del módulo de productos para empresas farmacéuticas con campos específicos del sector',
    'description': """
        Módulo de Gestión de Productos Farmacéuticos
        =============================================
        
        Este módulo extiende el módulo de productos de Odoo para agregar campos
        específicos necesarios para empresas farmacéuticas, distribuidoras y droguerías.
        
        Características principales:
        * Gestión de Marcas: Catálogo completo de marcas farmacéuticas
        * Laboratorios Fabricantes: Control de fabricantes y sus líneas de producto
        * Líneas de Laboratorio: Códigos simplificados por laboratorio (LAB1, LAB2, etc.)
        * Registro Sanitario: Control de registros con fechas de vencimiento
        * Proveedor Principal: Identificación rápida del proveedor preferido
        * Productos Relacionados: Visualización mejorada de complementarios y alternativos
        * Categorización Avanzada: Categorías jerárquicas con filtros especializados
        
        Casos de uso:
        * Control de registros sanitarios vigentes
        * Búsqueda rápida por laboratorio o marca
        * Identificación de productos por línea de laboratorio
        * Gestión de proveedores principales
        * Trazabilidad completa del producto
    """,
    'author': 'SSE',
    'depends': ['product', 'stock', 'purchase'],
    'data': [
        'security/ir.model.access.csv',
        'data/product_brand_data.xml',
        'data/product_laboratory_data.xml',
        'views/product_brand_views.xml',
        'views/product_laboratory_views.xml',
        'views/product_laboratory_line_views.xml',
        'views/product_template_views.xml',
        'views/menu_items.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}

