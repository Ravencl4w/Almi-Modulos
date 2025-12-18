# Gestión de Productos Farmacéuticos

## 📋 Descripción

Módulo de extensión para Odoo 18 que agrega funcionalidades específicas para la gestión de productos en empresas farmacéuticas, distribuidoras y droguerías. Este módulo extiende el módulo base de productos de Odoo con campos y características diseñadas para el sector farmacéutico.

## ✨ Características Principales

### 1. Gestión de Marcas (product.brand)
Catálogo completo de marcas farmacéuticas:
- Nombre y código de marca
- Logo de la marca
- Propietario/Contacto de la marca
- Contador de productos por marca
- Búsqueda y filtrado por marca
- Vista Kanban visual

### 2. Laboratorios Fabricantes (product.laboratory)
Control completo de laboratorios:
- Nombre completo y nombre corto (código simplificado)
- País de origen
- Contacto y sitio web
- Logo del laboratorio
- Líneas de producto por laboratorio
- Estadísticas de productos y líneas
- Gestión de múltiples líneas de producto

### 3. Líneas de Laboratorio (product.laboratory.line)
Organización por líneas dentro de cada laboratorio:
- Código simplificado (ej: LAB1, LAB2, ONCO, CARDIO)
- Nombre descriptivo de la línea
- Relación con el laboratorio padre
- Contador de productos por línea
- **Ejemplo**: Laboratorio Jimenez → Línea LAB1, LAB2

### 4. Campos Farmacéuticos en Productos

#### Información Básica
- **Marca**: Marca comercial del producto
- **Laboratorio Fabricante**: Fabricante del producto
- **Línea de Laboratorio**: Línea específica dentro del laboratorio
- **Proveedor Principal**: Proveedor preferido (calculado automáticamente)
- **Precio del Proveedor Principal**

#### Información Farmacéutica
- **Principio Activo**: Componente activo del medicamento
- **Concentración**: Dosis (ej: 500mg, 10ml)
- **Forma Farmacéutica**: Tableta, Cápsula, Jarabe, Inyectable, etc. (16 opciones)
- **Grupo Terapéutico**: Clasificación terapéutica
- **Requiere Receta Médica**: Control booleano
- **Sustancia Controlada**: Control booleano
- **Cadena de Frío**: Control booleano
- **Temperatura de Almacenamiento**: Rango de temperatura

#### Registro Sanitario
Sistema completo de control de registros:
- **Número de Registro**
- **Autoridad Sanitaria** (DIGEMID, INVIMA, ANVISA, etc.)
- **Fecha de Emisión**
- **Fecha de Vencimiento**
- **Estado Automático**:
  - ✅ **Vigente**: Vence en más de 60 días
  - ⚠️ **Por Vencer**: Vence en ≤ 60 días
  - ❌ **Vencido**: Ya expiró
  - ⚪ **No Aplica**: No requiere registro
- **Archivo PDF/Imagen**: Adjuntar documento
- **Notas Adicionales**

#### Productos Relacionados (Mejorados)
Visualización mejorada de:
- **Productos Alternativos** (ya existente en Odoo)
- **Productos Opcionales/Complementarios** (ya existente en Odoo)
- **Accesorios** (ya existente en Odoo)
- Contador total de productos relacionados
- Vista consolidada en una pestaña

### 5. Campos que YA tiene Odoo (no duplicados)
- **Código del producto (SKU)**: Campo `default_code`
- **Descripción**: Campo `name`
- **Categoría**: Campo `categ_id` (jerárquica)
- **Unidades de Medida**: Campos `uom_id` y `uom_po_id`
- **Peso**: Campo `weight`
- **Volumen**: Campo `volume`
- **Archivar**: Campo `active`
- **Proveedores**: Campo `seller_ids` (One2many)

## 🔧 Requisitos Técnicos

- **Odoo**: Versión 18.0
- **Dependencias**:
  - `product` (Productos)
  - `stock` (Inventario)
  - `purchase` (Compras - para proveedores)

## 📦 Instalación

Ver archivo [INSTALACION.md](INSTALACION.md) para instrucciones detalladas.

## ⚙️ Configuración

Ver archivo [CONFIGURACION.md](CONFIGURACION.md) para guía de configuración paso a paso.

## 📊 Uso

### Configurar Catálogos Base

1. **Crear Marcas**:
   - Ir a **Inventario** → **Farmacia** → **Catálogos** → **Marcas**
   - Crear marcas comerciales de tus productos
   - Cargar logos si es necesario

2. **Crear Laboratorios**:
   - Ir a **Inventario** → **Farmacia** → **Catálogos** → **Laboratorios**
   - Registrar laboratorios fabricantes
   - Configurar nombre corto/código
   - Agregar información de contacto

3. **Crear Líneas de Laboratorio**:
   - Desde un laboratorio, ir a pestaña "Líneas de Producto"
   - O ir a **Inventario** → **Farmacia** → **Catálogos** → **Líneas de Laboratorio**
   - Crear códigos simplificados (LAB1, LAB2, etc.)

### Registrar Productos

1. **Crear/Editar Producto**:
   - Ir a **Inventario** → **Productos** → **Productos**
   - En el formulario:
     - Completar **Código del Producto (SKU)** (campo estándar)
     - Completar **Nombre**
     - Seleccionar **Marca**
     - Seleccionar **Laboratorio Fabricante**
     - Seleccionar **Línea de Laboratorio** (se filtra por laboratorio)

2. **Información Farmacéutica**:
   - Ir a pestaña **"Información Farmacéutica"**
   - Completar:
     - Principio Activo
     - Concentración
     - Forma Farmacéutica
     - Grupo Terapéutico
   - Activar checkboxes según corresponda:
     - Requiere Receta
     - Sustancia Controlada
     - Cadena de Frío

3. **Registro Sanitario**:
   - En la misma pestaña, sección "Registro Sanitario"
   - Activar **"Requiere Registro Sanitario"**
   - Completar:
     - Número de Registro
     - Autoridad Sanitaria
     - Fechas de emisión y vencimiento
   - Cargar archivo PDF del registro
   - El estado se calcula automáticamente

4. **Proveedores**:
   - Ir a pestaña **"Proveedores"**
   - Agregar proveedores en la lista
   - El **Proveedor Principal** se asigna automáticamente (el primero de la lista)
   - Ver precio del proveedor principal

5. **Productos Relacionados**:
   - Ir a pestaña **"Productos Relacionados"**
   - Agregar:
     - Productos Alternativos (sustitutos)
     - Productos Opcionales (complementarios)
     - Accesorios

### Búsquedas y Filtros

El módulo agrega múltiples filtros en la lista de productos:

**Filtros por Características**:
- Con Marca
- Con Laboratorio
- Requiere Receta
- Sustancia Controlada
- Cadena de Frío

**Filtros por Registro Sanitario**:
- Registro Vigente
- Registro Vencido
- Registro por Vencer

**Agrupar Por**:
- Marca
- Laboratorio
- Línea de Laboratorio
- Forma Farmacéutica
- Estado de Registro

### Alertas Automáticas

El sistema muestra alertas visuales en el formulario del producto:

🔴 **Alerta Roja** - Registro Vencido:
- "El registro sanitario ha expirado. No se puede comercializar..."

🟡 **Alerta Amarilla** - Por Vencer:
- "El registro sanitario vence pronto. Iniciar renovación..."

🟡 **Alerta Amarilla** - Sin Registro:
- "Este producto requiere registro pero no tiene uno asignado..."

## 📈 Reportes y Análisis

### Análisis por Marca
```
Productos → Agrupar por "Marca"
→ Ver distribución de productos por marca
→ Identificar marcas principales
```

### Análisis por Laboratorio
```
Productos → Agrupar por "Laboratorio"
→ Ver distribución por fabricante
→ Análisis de proveedores principales
```

### Control de Registros Sanitarios
```
Productos → Filtro "Registro por Vencer"
→ Lista de productos a renovar
→ Plan de acción mensual
```

### Vista Kanban por Marca
```
Productos → Vista Kanban
→ Agrupación automática por marca
→ Badges de estado de registro
→ Indicadores de receta/controlado
```

## 🎨 Vistas y Visualizaciones

### Vista de Lista Mejorada
Columnas adicionales opcionales:
- Marca
- Laboratorio
- Código de Línea
- Principio Activo
- Registro Sanitario
- Estado del Registro (con badges de color)
- Proveedor Principal

### Vista de Formulario Extendida
Pestañas adicionales:
1. **Información Farmacéutica**: Clasificación y características
2. **Productos Relacionados**: Vista consolidada y mejorada
3. **Proveedores**: Con proveedor principal destacado

### Vista Kanban Mejorada
- Agrupación automática por marca
- Badges de estado de registro
- Iconos para receta médica
- Información de laboratorio

## 🔒 Seguridad y Permisos

### Grupos de Acceso

| Grupo | Acceso | Descripción |
|-------|--------|-------------|
| **Usuario Base** | Solo lectura | Ver catálogos |
| **Usuario de Inventario** | Lectura/Escritura | Gestionar productos y catálogos |
| **Gerente de Inventario** | Control total | Crear/Editar/Eliminar todo |

### Campos con Tracking

Campos que registran cambios en el log:
- `brand_id`
- `laboratory_id`
- `laboratory_line_id`
- `main_supplier_id`
- `sanitary_registration`
- `sanitary_registration_date`
- `sanitary_registration_expiry`

## 🚀 Casos de Uso

### 1. Distribuidora Farmacéutica
**Necesidad**: Organizar 5,000+ productos por marca y laboratorio

**Solución**:
- Catálogo de 50+ marcas
- 30+ laboratorios con sus líneas
- Búsqueda rápida por marca o laboratorio
- Filtros avanzados para ubicar productos

### 2. Control de Registros Sanitarios
**Necesidad**: Evitar vender productos con registro vencido

**Solución**:
- Registro de todos los productos con fecha de vencimiento
- Alertas automáticas 60 días antes
- Filtro de productos vencidos
- Reporte mensual de renovaciones

### 3. Droguería con Productos Controlados
**Necesidad**: Identificar productos que requieren receta

**Solución**:
- Marcar productos que requieren receta
- Identificar sustancias controladas
- Filtro rápido para verificación
- Badges visibles en Kanban

### 4. Gestión de Cadena de Frío
**Necesidad**: Identificar productos que requieren refrigeración

**Solución**:
- Campo "Cadena de Frío" booleano
- Temperatura de almacenamiento
- Filtro rápido de productos refrigerados
- Visibilidad en logística y almacén

## 🔌 Integraciones

### Con Otros Módulos de Odoo

| Módulo | Integración |
|--------|-------------|
| **Ventas** | Productos relacionados en cotizaciones |
| **Compras** | Proveedor principal en órdenes |
| **Inventario** | Control de peso y temperatura |
| **Facturación** | Compatible con nubefact_sunat |
| **E-commerce** | Marcas y laboratorios en tienda online |

### Compatible Con

- 🏥 **pharma_partner**: Integración con gestión de clientes
- 📄 **nubefact_sunat**: Facturación electrónica
- 📦 **stock**: Módulo de inventario estándar
- 💰 **purchase**: Módulo de compras estándar

## 📝 Diferencias con Odoo Estándar

### ✅ Campos que Odoo YA tiene (no duplicados):
- Código del producto (SKU): `default_code`
- Categoría y Subcategoría: `categ_id` (jerárquica)
- Unidades de Medida: `uom_id`, `uom_po_id`
- Peso: `weight`
- Proveedores: `seller_ids`
- Productos Relacionados: `alternative_product_ids`, `optional_product_ids`, `accessory_product_ids`

### ➕ Campos NUEVOS agregados:
- Marca (`brand_id`)
- Laboratorio Fabricante (`laboratory_id`)
- Línea de Laboratorio (`laboratory_line_id`)
- Proveedor Principal (`main_supplier_id`) - calculado
- Registro Sanitario completo
- Información farmacéutica (principio activo, concentración, forma)
- Características especiales (receta, controlado, cadena de frío)

## 🎓 Capacitación del Equipo

### Usuarios de Inventario
- ✅ Crear y mantener catálogos (marcas, laboratorios, líneas)
- ✅ Registrar productos con información farmacéutica
- ✅ Actualizar registros sanitarios
- ✅ Gestionar proveedores

### Gerentes
- ✅ Todo lo anterior +
- ✅ Analizar distribución de productos
- ✅ Monitorear vencimientos de registros
- ✅ Optimizar catálogos

### Ventas/Compras
- ✅ Buscar productos por marca/laboratorio
- ✅ Verificar registros vigentes
- ✅ Identificar productos especiales (receta, controlados)
- ✅ Ver proveedor principal

## 📞 Soporte y Ayuda

### Documentación
- 📄 **README.md**: Este documento
- 📄 **INSTALACION.md**: Guía de instalación
- 📄 **CONFIGURACION.md**: Configuración detallada
- 📄 **RESUMEN.md**: Vista técnica rápida

## ✅ Próximas Mejoras

- [ ] Dashboard de registros por vencer
- [ ] Notificaciones automáticas de vencimiento
- [ ] Importación masiva de productos con datos farmacéuticos
- [ ] Generación de etiquetas con código de barras
- [ ] Reportes de productos por grupo terapéutico
- [ ] Integración con sistemas de farmacovigilancia
- [ ] Historial de cambios de registro sanitario

## 👥 Autor

**SSE** - Sistema Especializado en Soluciones

## 📄 Licencia

LGPL-3

---

**Versión**: 18.0.1.0.0  
**Última actualización**: 2025

**¿Listo para comenzar?** Consulta [INSTALACION.md](INSTALACION.md) para instalar el módulo.

