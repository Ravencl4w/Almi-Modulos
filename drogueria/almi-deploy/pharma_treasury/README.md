# Módulo de Liquidación y Tesorería - pharma_treasury

## Descripción

Módulo completo de gestión de liquidaciones y tesorería para empresas farmacéuticas, integrado con el módulo `pharma_dispatch`. Permite gestionar planillas de reparto, liquidaciones de transportistas y hojas de cobranza por vendedor.

## Características Principales

### 1. Planillas de Reparto
- **Selección masiva de facturas** con filtros avanzados (fecha, cliente, zona, vendedor, estado SUNAT)
- Asignación a rutas de reparto existentes o creación de nuevas rutas
- Seguimiento de estado de cobranza por factura
- Estados: Borrador → Confirmada → En Ruta → Liquidada → Cerrada

### 2. Liquidaciones de Transportista
- Registro de cobros por factura desde app móvil
- Proceso de aprobación por liquidador
- Tracking de montos, métodos de pago y evidencias
- Estados: Borrador → En Revisión → Aprobada/Rechazada
- Geolocalización de cobros
- Soporte para evidencia fotográfica

### 3. Hojas de Cobranza por Vendedor
- Seguimiento de facturas asignadas a cada vendedor
- Dashboard de efectividad de cobranza
- Carga automática de facturas por periodo
- Análisis con gráficos y pivot tables
- Reportes de desempeño

### 4. API REST para App Móvil
Endpoints disponibles:
- `GET /api/settlement/my_routes` - Consultar rutas asignadas
- `GET /api/settlement/route/<id>` - Detalle de ruta con facturas
- `POST /api/settlement/submit` - Enviar liquidación
- `GET /api/settlement/status/<id>` - Consultar estado de liquidación

## Instalación

### Dependencias
- `account` - Contabilidad
- `sale` - Ventas
- `pharma_dispatch` - Despacho y Logística

### Pasos de Instalación
1. Copiar el módulo a la carpeta de addons de Odoo
2. Actualizar lista de aplicaciones
3. Instalar el módulo `pharma_treasury`
4. Verificar que se hayan creado las secuencias automáticamente

## Configuración Inicial

### Permisos de Usuario
El módulo usa los grupos de seguridad estándar de Odoo:

- **Usuario de Inventario** (`stock.group_stock_user`):
  - Crear y editar planillas
  - Ver liquidaciones
  
- **Usuario de Contabilidad** (`account.group_account_user`):
  - Ver planillas y liquidaciones
  - Crear hojas de cobranza
  
- **Administrador de Contabilidad** (`account.group_account_manager`):
  - Aprobar/rechazar liquidaciones
  - Cerrar planillas y hojas de cobranza
  - Todos los permisos

- **Portal** (`base.group_portal`):
  - Solo lectura (para transportistas vía API)

### API Móvil
Para usar la API REST:
1. El transportista debe tener un usuario en Odoo
2. Asociar el usuario al conductor en: Despacho → Configuración → Conductores
3. Autenticarse usando token Bearer estándar de Odoo
4. Usar los endpoints documentados

## Flujo de Trabajo Completo

### 1. Creación de Planilla
```
Tesorero:
1. Ir a: Tesorería → Planillas de Reparto
2. Crear nueva planilla
3. Click en "Seleccionar Facturas"
4. Aplicar filtros (fecha, zona, etc.)
5. Seleccionar facturas
6. Confirmar planilla
```

### 2. Asignación a Ruta
```
Tesorero:
1. Click en "Asignar a Ruta"
2. Opción A: Seleccionar ruta existente
   Opción B: Crear nueva ruta (seleccionar conductor y vehículo)
3. La planilla cambia a estado "En Ruta"
```

### 3. Liquidación por Transportista
```
Transportista (vía app móvil):
1. Consultar rutas asignadas (GET /api/settlement/my_routes)
2. Ver detalle de ruta con facturas (GET /api/settlement/route/<id>)
3. Entregar pedidos y cobrar
4. Registrar cobros por factura:
   - Monto cobrado
   - Método de pago
   - Estado de entrega
   - Evidencia (foto)
   - Geolocalización
5. Enviar liquidación (POST /api/settlement/submit)
```

### 4. Aprobación de Liquidación
```
Liquidador:
1. Ir a: Tesorería → Liquidaciones
2. Abrir liquidación "En Revisión"
3. Verificar montos y evidencias
4. Opción A: Aprobar (actualiza estados de pago)
   Opción B: Rechazar con motivo (transportista debe corregir)
```

### 5. Cierre de Planilla
```
Tesorero:
1. Una vez aprobada la liquidación
2. Click en "Cerrar" en la planilla
3. La planilla queda cerrada y bloqueada
```

### 6. Hoja de Cobranza por Vendedor
```
Tesorero:
1. Ir a: Tesorería → Hojas de Cobranza
2. Crear nueva hoja
3. Seleccionar vendedor y periodo
4. Click en "Cargar Facturas" (carga automática)
5. Activar hoja
6. Hacer seguimiento de efectividad
7. Cerrar al finalizar el periodo
```

## Integraciones

### Con pharma_dispatch
- Extiende `dispatch.route` con campos de planilla y liquidación
- Botones inteligentes para ver planillas desde rutas
- Vinculación automática de conductor y vehículo

### Con account (Facturas)
- Extiende `account.move` con tracking de planillas
- Badges que indican si factura está en planilla
- Estado de cobranza y entrega
- Botones para agregar facturas a planillas

### Con sale (Ventas)
- Vinculación con pedidos de venta
- Acceso a datos de cliente y zona de venta
- Seguimiento de vendedor por factura

## Vistas Principales

### Planillas de Reparto
- **List View**: Con totales y estados
- **Form View**: Con wizard de selección masiva
- **Kanban View**: Por estado con totales
- **Search View**: Filtros por conductor, fecha, estado

### Liquidaciones
- **List View**: Con montos y diferencias
- **Form View**: Botones según rol (transportista/liquidador)
- **Kanban View**: Por estado con alertas
- **Search View**: Filtros por estado, conductor, diferencias

### Hojas de Cobranza
- **List View**: Por vendedor con efectividad
- **Form View**: Dashboard con indicadores
- **Kanban View**: Con gráficos de desempeño
- **Pivot View**: Para análisis
- **Graph View**: Visualización de cobranza

## Secuencias Automáticas

- **Planillas**: PLN00001, PLN00002, ...
- **Liquidaciones**: LIQ00001, LIQ00002, ...
- **Hojas de Cobranza**: COB00001, COB00002, ...

## Campos Principales

### Planilla de Reparto
- Número, fecha, estado
- Ruta asignada (conductor, vehículo)
- Líneas con facturas
- Totales: asignado, cobrado, pendiente
- Estadísticas de entrega

### Liquidación
- Número, fecha, estado
- Planilla y ruta asociadas
- Conductor y liquidador
- Totales y diferencias
- Tasa de cobranza
- Fechas de envío y aprobación

### Hoja de Cobranza
- Número, vendedor, periodo
- Facturas asignadas
- Totales y pendientes
- Tasa de efectividad
- Distribución: pagadas, parciales, sin pagar

## Validaciones Implementadas

- Una factura no puede estar en múltiples planillas activas
- Solo facturas confirmadas (posted) pueden agregarse
- No se puede aprobar liquidación con montos negativos
- El monto cobrado no puede ser significativamente mayor al total
- Si no se entregó, el monto cobrado debe ser 0
- No se puede cerrar planilla sin liquidación aprobada

## Notificaciones y Actividades

- Mensaje en chatter al confirmar planilla
- Mensaje al asignar a ruta
- Actividad para liquidador al enviar liquidación
- Mensaje al aprobar/rechazar liquidación
- Mensaje al cerrar planilla o hoja de cobranza

## Mejoras Futuras (Opcionales)

- Dashboard general de tesorería con KPIs
- Reportes PDF personalizados
- Integración con pasarelas de pago
- Notificaciones push para app móvil
- Firma digital en dispositivo móvil
- Mapa con tracking GPS en tiempo real
- Exportación a Excel de hojas de cobranza
- Análisis predictivo de cobranza

## Soporte Técnico

### Logs y Debugging
El módulo usa logging estándar de Odoo:
```python
_logger = logging.getLogger(__name__)
```

Para activar modo debug:
1. Configuración → Activar modo desarrollador
2. Ver logs en: `~/.odoo/odoo-server.log`

### Problemas Comunes

**Error: "No se encontró secuencia"**
- Solución: Reinstalar el módulo para crear secuencias

**Error: "Factura ya está en otra planilla"**
- Solución: La factura está en una planilla activa, cerrar o cancelar esa planilla primero

**Error: "Authentication required" en API**
- Solución: Verificar token de autenticación Bearer

## Créditos

**Desarrollado por:** SSE  
**Versión:** 18.0.1.0.0  
**Licencia:** LGPL-3  
**Compatibilidad:** Odoo 18.0 Community/Enterprise

---

¿Tienes preguntas? Consulta el archivo TESTING.md para casos de prueba detallados.

