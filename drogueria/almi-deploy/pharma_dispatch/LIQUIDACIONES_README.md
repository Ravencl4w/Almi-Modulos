# Sistema de Liquidaciones y Cobranzas - Pharma Dispatch

## Resumen de la Implementación

Se ha implementado exitosamente el sistema de liquidaciones para el módulo `pharma_dispatch` de Odoo 18, que permite gestionar los cobros realizados por los conductores durante sus rutas de entrega.

## Componentes Implementados

### 1. Modelos de Datos

#### 1.1 `dispatch.settlement` (Liquidación)
- **Archivo**: `models/dispatch_settlement.py`
- **Propósito**: Gestiona las liquidaciones de planillas de despacho
- **Relación**: 1:1 con `dispatch.sheet`
- **Características**:
  - Clasificación automática de facturas en contado y crédito
  - Cálculo de totales: cobrado, depositado, faltante
  - Estados: draft → in_progress → validated
  - Integración con hoja de cobranzas

#### 1.2 `dispatch.collection.sheet` (Hoja de Cobranzas)
- **Archivo**: `models/dispatch_collection_sheet.py`
- **Propósito**: Registro central de todos los pagos recibidos
- **Características**:
  - Asignación de liquidador responsable
  - Totales por estado (pendiente, asignado, pagado)
  - Validación completa de líneas antes de confirmar

#### 1.3 `dispatch.collection.line` (Línea de Cobranza)
- **Archivo**: `models/dispatch_collection_line.py`
- **Propósito**: Registro individual de cada pago recibido
- **Características**:
  - Tipos de cobranza: efectivo, crédito, depósito
  - Métodos de pago: efectivo, transferencia, depósito, cheque, tarjeta
  - Creación automática de `account.payment` al asignar
  - Reconciliación automática con facturas
  - Registrado por conductor desde app móvil

### 2. API REST para Aplicación Móvil

#### 2.1 Endpoints Implementados
- **Archivo**: `controllers/dispatch_api.py`

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/dispatch/route/<id>` | GET | Obtener detalles de ruta |
| `/api/dispatch/route/line/<id>/deliver` | POST | Marcar entrega exitosa |
| `/api/dispatch/route/line/<id>/fail` | POST | Marcar entrega fallida |
| `/api/dispatch/collection/register` | POST | Registrar pago recibido |
| `/api/dispatch/driver/<id>/routes` | GET | Listar rutas del conductor |

#### 2.2 Autenticación
- Autenticación simple por `driver_id`
- Formato de respuesta JSON consistente
- Manejo de errores con códigos descriptivos

### 3. Vistas e Interfaz de Usuario

#### 3.1 Vistas de Liquidación
- **Archivo**: `views/dispatch_settlement_views.xml`
- Vista formulario con pestañas:
  - Información General
  - Depósitos (depositados/faltantes)
  - Facturas al Contado
  - Facturas al Crédito
  - Hoja de Cobranzas
- Vista lista con totales
- Smart button en planilla para acceder

#### 3.2 Vistas de Hoja de Cobranzas
- **Archivo**: `views/dispatch_collection_sheet_views.xml`
- Vista formulario con líneas editables
- Botón "Asignar Pago" en cada línea
- Smart buttons para ver estadísticas
- Vista de líneas individuales con detalle completo

#### 3.3 Menús
- **Liquidaciones** → Sección principal
  - Liquidaciones
  - Hojas de Cobranzas

### 4. Flujo de Trabajo

#### 4.1 Creación Automática
1. Usuario crea planilla de despacho
2. Usuario confirma planilla → se crea ruta
3. **AUTOMÁTICO**: Se crea liquidación + hoja de cobranzas
4. Estado inicial: Borrador

#### 4.2 Registro de Pagos (App Móvil)
1. Conductor marca entrega como exitosa
2. Conductor registra pago recibido vía API:
   - Monto
   - Tipo de cobranza (efectivo/crédito/depósito)
   - Método de pago
   - Referencia bancaria (opcional)
3. Se crea línea de cobranza en estado "Pendiente"

#### 4.3 Asignación de Pagos (Liquidador)
1. Liquidador abre hoja de cobranzas
2. Revisa líneas pendientes
3. Asigna cada línea a una factura
4. Sistema crea `account.payment` automáticamente
5. Sistema reconcilia pago con factura
6. Factura se marca como pagada en Odoo
7. Línea cambia a estado "Pagado"

#### 4.4 Validación
1. Todas las líneas deben estar asignadas
2. Liquidador valida la hoja de cobranzas
3. Liquidador valida la liquidación
4. Proceso finalizado

## Archivos Creados/Modificados

### Nuevos Archivos
```
pharma_dispatch/
├── models/
│   ├── dispatch_settlement.py          ✓ NUEVO
│   ├── dispatch_collection_sheet.py    ✓ NUEVO
│   └── dispatch_collection_line.py     ✓ NUEVO
├── controllers/
│   ├── __init__.py                     ✓ NUEVO
│   └── dispatch_api.py                 ✓ NUEVO
├── views/
│   ├── dispatch_settlement_views.xml   ✓ NUEVO
│   └── dispatch_collection_sheet_views.xml ✓ NUEVO
└── data/
    └── dispatch_settlement_sequence_data.xml ✓ NUEVO
```

### Archivos Modificados
```
pharma_dispatch/
├── __init__.py                         ✓ MODIFICADO (import controllers)
├── __manifest__.py                     ✓ MODIFICADO (data files)
├── models/
│   ├── __init__.py                     ✓ MODIFICADO (import nuevos modelos)
│   └── dispatch_sheet.py               ✓ MODIFICADO (crear liquidación)
├── views/
│   ├── dispatch_sheet_views.xml        ✓ MODIFICADO (smart button)
│   └── menu_items.xml                  ✓ MODIFICADO (nuevos menús)
└── security/
    └── ir.model.access.csv             ✓ MODIFICADO (permisos)
```

## Configuración de Seguridad

### Permisos de Acceso
- **Usuarios de Stock**: Lectura, escritura, creación
- **Gerentes de Stock**: Todos los permisos incluyendo eliminación
- **Portal**: Solo lectura (para conductores)

## Consideraciones Técnicas

### 1. Clasificación de Facturas
Las facturas se clasifican automáticamente en:
- **Al Contado**: Sin plazo de pago o plazo = 0 días
- **Al Crédito**: Con plazo de pago > 0 días

### 2. Depósitos vs Faltantes
- **Total Depositado**: Suma de líneas tipo "deposit"
- **Total Faltante**: Total Cobrado - Total Depositado

### 3. Creación de Pagos en Odoo
Cuando el liquidador asigna un pago:
1. Se crea `account.payment` con tipo "inbound"
2. Se busca el diario apropiado (cash/bank)
3. Se reconcilia automáticamente con la factura
4. Si la factura queda pagada completa, se marca como tal

### 4. Validaciones Implementadas
- Monto de pago no puede exceder saldo pendiente de factura
- Factura debe estar en la liquidación
- No se puede validar con líneas pendientes
- No se puede cancelar con pagos creados

## Pruebas Recomendadas

### Escenario 1: Flujo Completo
1. Crear planilla con 3 facturas (2 contado, 1 crédito)
2. Confirmar planilla → verificar creación de liquidación
3. Simular registro de pagos desde API
4. Asignar pagos a facturas como liquidador
5. Validar hoja de cobranzas y liquidación

### Escenario 2: API Móvil
1. GET `/api/dispatch/route/<id>?driver_id=X`
2. POST marcar entrega exitosa
3. POST registrar pago recibido
4. Verificar línea en hoja de cobranzas

### Escenario 3: Depósitos Bancarios
1. Registrar pagos con tipo "deposit"
2. Agregar referencias bancarias
3. Verificar totales de depositado vs faltante

## Próximos Pasos (Opcionales)

### Mejoras Sugeridas
1. **Autenticación Mejorada**: Implementar JWT tokens
2. **Notificaciones**: Email/SMS al liquidador cuando hay pagos pendientes
3. **Reportes**: Dashboard con estadísticas de cobranzas
4. **Fotos**: Permitir adjuntar fotos de comprobantes
5. **Geolocalización**: Registrar ubicación al recibir pago
6. **Firma Digital**: Captura de firma desde app móvil

### Integraciones
1. Integración con pasarelas de pago
2. Exportación a sistemas contables externos
3. Sincronización con aplicaciones bancarias

## Soporte

Para dudas o problemas, revisar:
1. Logs de Odoo: `/var/log/odoo/`
2. Logs de API: Buscar por "dispatch_api" en logs
3. Estados de modelos en BD

## Conclusión

El sistema de liquidaciones está completamente funcional y listo para usar. Todos los componentes han sido implementados según las especificaciones:

✅ Modelos de datos creados
✅ Relaciones 1:1 implementadas
✅ API REST funcional
✅ Vistas e interfaz completas
✅ Flujo de trabajo implementado
✅ Integración con sistema de pagos de Odoo
✅ Permisos de seguridad configurados
✅ Secuencias automáticas configuradas

El módulo está listo para ser actualizado en Odoo 18.

