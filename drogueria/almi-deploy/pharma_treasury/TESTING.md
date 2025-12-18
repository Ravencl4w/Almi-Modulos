# Guía de Pruebas - Módulo Liquidación y Tesorería

Esta guía contiene los casos de prueba para validar todas las funcionalidades del módulo `pharma_treasury`.

## Requisitos Previos

### Instalación
1. Instalar dependencias:
   - `account` (Contabilidad)
   - `sale` (Ventas)
   - `pharma_dispatch` (Despacho y Logística)

2. Instalar el módulo `pharma_treasury`

3. Verificar que se hayan creado:
   - ✅ Secuencias automáticas (PLN, LIQ, COB)
   - ✅ Menú "Tesorería" bajo "Despacho"
   - ✅ Permisos de acceso configurados

### Configuración Inicial
1. Crear conductores y vehículos en `pharma_dispatch`
2. Crear facturas de cliente confirmadas (posted)
3. Asignar zonas de venta a clientes
4. Crear usuarios con roles apropiados

---

## Caso de Prueba 1: Planilla de Reparto - Selección Masiva

### Objetivo
Validar la creación de planillas y selección masiva de facturas.

### Pasos
1. **Crear Facturas de Prueba:**
   - Crear 5 facturas de cliente
   - Confirmar todas las facturas (Estado: Posted)
   - Asignar diferentes clientes y zonas

2. **Crear Planilla:**
   - Ir a: Tesorería → Planillas de Reparto
   - Click en "Crear"
   - Fecha: Hoy
   - Guardar (Estado: Borrador)
   - ✅ Verificar que se genera número PLN00001

3. **Seleccionar Facturas Masivamente:**
   - Click en "Seleccionar Facturas"
   - Aplicar filtros:
     - Fecha desde: Hace 30 días
     - Fecha hasta: Hoy
     - Estado de pago: No Pagadas
   - Click en "Aplicar Filtros"
   - ✅ Verificar que aparecen facturas disponibles
   - Click en "Seleccionar Todas"
   - ✅ Verificar que se muestran en "Facturas Seleccionadas"
   - ✅ Verificar que se muestra el total seleccionado
   - Click en "Agregar a Planilla"

4. **Verificar Planilla:**
   - ✅ Verificar que las 5 facturas aparecen en la pestaña "Facturas"
   - ✅ Verificar que se calculan los totales correctamente
   - ✅ Verificar que todas están en estado "Pendiente"

### Resultado Esperado
- Planilla creada con número secuencial
- Facturas agregadas correctamente
- Totales calculados automáticamente
- Estado: Borrador

---

## Caso de Prueba 2: Asignación de Planilla a Ruta

### Objetivo
Validar la asignación de planillas a rutas existentes y nuevas.

### Pasos - Opción A: Ruta Existente
1. **Crear Ruta en pharma_dispatch:**
   - Ir a: Despacho → Rutas de Reparto
   - Crear ruta para hoy
   - Asignar conductor y vehículo
   - Estado: Borrador

2. **Asignar Planilla a Ruta:**
   - Abrir planilla del Caso 1
   - Click en "Confirmar"
   - ✅ Verificar que estado cambia a "Confirmada"
   - Click en "Asignar a Ruta"
   - Seleccionar "Asignar a Ruta Existente"
   - Seleccionar la ruta creada
   - Click en "Asignar"
   - ✅ Verificar que estado cambia a "En Ruta"
   - ✅ Verificar que se muestra conductor y vehículo

### Pasos - Opción B: Crear Nueva Ruta
1. **Crear Planilla y Confirmar:**
   - Crear nueva planilla con facturas
   - Confirmar planilla

2. **Crear Ruta desde Planilla:**
   - Click en "Asignar a Ruta"
   - Seleccionar "Crear Nueva Ruta"
   - Fecha de ruta: Hoy
   - Seleccionar conductor
   - Seleccionar vehículo
   - Click en "Asignar"
   - ✅ Verificar que se crea la ruta automáticamente
   - ✅ Verificar que planilla está vinculada

### Resultado Esperado
- Planilla asignada a ruta correctamente
- Estado: En Ruta
- Conductor y vehículo visibles en planilla
- Desde la ruta se puede ver la planilla

---

## Caso de Prueba 3: Liquidación Manual (Interfaz Web)

### Objetivo
Validar la creación y aprobación de liquidaciones desde la interfaz web.

### Pasos
1. **Crear Liquidación:**
   - Abrir planilla en estado "En Ruta"
   - Click en "Crear Liquidación"
   - ✅ Verificar que se crea con número LIQ00001
   - ✅ Verificar que se cargan todas las facturas de la planilla

2. **Registrar Cobros:**
   - En pestaña "Detalle de Cobros":
     - Factura 1:
       - Estado de entrega: Entregado
       - Monto cobrado: (monto completo de factura)
       - Método de pago: Efectivo
     - Factura 2:
       - Estado de entrega: Entregado
       - Monto cobrado: (monto parcial)
       - Método de pago: Transferencia
       - Referencia: OP-12345
     - Factura 3:
       - Estado de entrega: No Entregado
       - Monto cobrado: 0
   - ✅ Verificar que se calculan las diferencias
   - ✅ Verificar que "Total Cobrado" se actualiza

3. **Enviar para Revisión:**
   - Agregar notas del transportista
   - Click en "Enviar para Revisión"
   - ✅ Verificar que estado cambia a "En Revisión"
   - ✅ Verificar que se registra fecha de envío
   - ✅ Verificar que se crea actividad para liquidador

4. **Aprobar Liquidación (como Liquidador):**
   - Cambiar a usuario con rol "Administrador de Contabilidad"
   - Ir a: Tesorería → Liquidaciones
   - Filtro: "En Revisión"
   - Abrir la liquidación
   - Revisar montos y observaciones
   - Click en "Aprobar"
   - ✅ Verificar que estado cambia a "Aprobada"
   - ✅ Verificar que se actualizan las líneas de planilla
   - ✅ Verificar que planilla cambia a "Liquidada"

### Resultado Esperado
- Liquidación creada correctamente
- Cobros registrados
- Proceso de aprobación funcional
- Estados actualizados en cascada

---

## Caso de Prueba 4: Liquidación vía API Móvil

### Objetivo
Validar los endpoints REST para app móvil.

### Requisitos
- Usuario asociado a un conductor
- Token de autenticación

### Pasos

#### 1. Consultar Rutas (GET /api/settlement/my_routes)
```json
Request:
POST /api/settlement/my_routes
Headers: {
  "Authorization": "Bearer <token>"
}

Response esperada:
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "RUT00001",
      "date": "2025-11-05",
      "state": "in_progress",
      "has_settlement_sheet": true,
      "settlement_sheet": {
        "id": 1,
        "name": "PLN00001",
        "total_invoices": 5,
        "total_amount": 1500.00
      }
    }
  ],
  "total": 1
}
```
- ✅ Verificar que retorna las rutas del conductor
- ✅ Verificar estructura del JSON

#### 2. Detalle de Ruta (GET /api/settlement/route/<id>)
```json
Request:
POST /api/settlement/route/1
Headers: {
  "Authorization": "Bearer <token>"
}

Response esperada:
{
  "success": true,
  "data": {
    "id": 1,
    "name": "RUT00001",
    "settlement_sheet": {...},
    "invoices": [
      {
        "invoice_id": 10,
        "invoice_name": "FACT/2025/00001",
        "customer": {
          "name": "Cliente ABC",
          "street": "Av. Principal 123"
        },
        "amount_total": 300.00,
        "delivery_status": "pending"
      }
    ]
  }
}
```
- ✅ Verificar que retorna detalle completo
- ✅ Verificar lista de facturas

#### 3. Enviar Liquidación (POST /api/settlement/submit)
```json
Request:
POST /api/settlement/submit
Headers: {
  "Authorization": "Bearer <token>"
}
Body: {
  "route_id": 1,
  "sheet_id": 1,
  "driver_notes": "Ruta completada sin problemas",
  "collections": [
    {
      "invoice_id": 10,
      "amount_collected": 300.00,
      "payment_method": "cash",
      "delivery_status": "delivered",
      "notes": "Cliente pagó completo",
      "evidence_base64": "data:image/jpeg;base64,/9j/4AAQ...",
      "latitude": -12.046374,
      "longitude": -77.042793
    },
    {
      "invoice_id": 11,
      "amount_collected": 0.00,
      "payment_method": "none",
      "delivery_status": "not_delivered",
      "notes": "Cliente no estaba en el domicilio"
    }
  ]
}

Response esperada:
{
  "success": true,
  "message": "Settlement submitted successfully",
  "data": {
    "settlement_id": 5,
    "settlement_name": "LIQ00005",
    "state": "submitted",
    "total_collected": 300.00
  }
}
```
- ✅ Verificar que crea la liquidación
- ✅ Verificar que cambia a estado "En Revisión"
- ✅ Verificar que se guardan evidencias

#### 4. Consultar Estado (GET /api/settlement/status/<id>)
```json
Request:
POST /api/settlement/status/5
Headers: {
  "Authorization": "Bearer <token>"
}

Response esperada:
{
  "success": true,
  "data": {
    "id": 5,
    "name": "LIQ00005",
    "state": "approved",
    "collection_rate": 60.0,
    "liquidator": "Juan Pérez"
  }
}
```
- ✅ Verificar que retorna estado actual
- ✅ Verificar que muestra liquidador

### Resultado Esperado
- Todos los endpoints funcionan correctamente
- Autenticación valida tokens
- Datos se guardan en la base de datos
- Errores se manejan apropiadamente

---

## Caso de Prueba 5: Hoja de Cobranza por Vendedor

### Objetivo
Validar hojas de cobranza y dashboard de efectividad.

### Pasos
1. **Crear Facturas con Vendedor:**
   - Crear 10 facturas de cliente
   - Asignar a vendedor "Vendedor A"
   - 5 facturas pagadas
   - 3 facturas pago parcial
   - 2 facturas sin pagar

2. **Crear Hoja de Cobranza:**
   - Ir a: Tesorería → Hojas de Cobranza
   - Click en "Crear"
   - Vendedor: Vendedor A
   - Fecha inicio: Hace 30 días
   - Fecha fin: Hoy
   - Guardar (Estado: Borrador)
   - ✅ Verificar número COB00001

3. **Cargar Facturas Automáticamente:**
   - Click en "Cargar Facturas"
   - ✅ Verificar que se cargan automáticamente
   - ✅ Verificar mensaje de confirmación
   - ✅ Verificar que se muestran las 10 facturas

4. **Activar Hoja:**
   - Click en "Activar"
   - ✅ Verificar que estado cambia a "Activa"
   - ✅ Verificar que se registra fecha de activación

5. **Revisar Dashboard:**
   - Ir a pestaña "Análisis"
   - ✅ Verificar totales:
     - Total asignado
     - Total cobrado
     - Pendiente
   - ✅ Verificar distribución:
     - 5 Pagadas
     - 3 Parciales
     - 2 Sin pagar
   - ✅ Verificar tasa de efectividad se calcula correctamente
   - ✅ Verificar alerta según desempeño

6. **Ver Reportes:**
   - Click en "Pivot"
   - ✅ Verificar análisis por vendedor
   - Click en "Gráfico"
   - ✅ Verificar visualización de cobranza

7. **Cerrar Hoja:**
   - Click en "Cerrar"
   - ✅ Verificar que estado cambia a "Cerrada"
   - ✅ Verificar mensaje con tasa final

### Resultado Esperado
- Hoja de cobranza creada
- Facturas cargadas automáticamente
- Dashboard muestra métricas correctas
- Reportes funcionan
- Cierre registra fecha y bloquea edición

---

## Caso de Prueba 6: Validaciones y Restricciones

### Objetivo
Validar que las restricciones de negocio funcionan correctamente.

### Escenarios a Probar

1. **Factura en Múltiples Planillas:**
   - Crear planilla A con factura X
   - Intentar agregar factura X a planilla B
   - ✅ Debe mostrar error: "Factura ya está en otra planilla"

2. **Confirmar Planilla Vacía:**
   - Crear planilla sin facturas
   - Intentar confirmar
   - ✅ Debe mostrar error: "Debe tener al menos una factura"

3. **Monto Cobrado Negativo:**
   - En liquidación, ingresar monto negativo
   - ✅ Debe mostrar error: "No puede ser negativo"

4. **No Entregado con Cobro:**
   - Marcar factura como "No Entregado"
   - Ingresar monto cobrado > 0
   - ✅ Debe mostrar error: "Si no fue entregada, monto debe ser 0"

5. **Liquidación sin Líneas:**
   - Crear liquidación vacía
   - Intentar enviar para revisión
   - ✅ Debe mostrar error: "Debe registrar al menos un cobro"

6. **Cerrar Planilla sin Liquidación:**
   - Intentar cerrar planilla sin liquidación aprobada
   - ✅ Debe mostrar error: "Debe tener liquidación aprobada"

### Resultado Esperado
- Todas las validaciones funcionan
- Mensajes de error son claros
- No se permite bypass de restricciones

---

## Caso de Prueba 7: Integración con pharma_dispatch

### Objetivo
Validar integración con el módulo de despacho.

### Pasos
1. **Desde Ruta → Ver Planilla:**
   - Abrir una ruta con planilla asignada
   - ✅ Verificar botón inteligente "Ver Planilla"
   - Click en el botón
   - ✅ Verificar que abre la planilla correcta

2. **Desde Ruta → Ver Liquidaciones:**
   - ✅ Verificar botón inteligente muestra cantidad
   - Click en "Ver Liquidaciones"
   - ✅ Verificar que filtra por la ruta

3. **Desde Ruta → Crear Liquidación:**
   - Click en "Crear Liquidación"
   - ✅ Verificar que valida existencia de planilla
   - ✅ Verificar que pre-llena datos de ruta

4. **Desde Factura → Ver Planilla:**
   - Abrir factura incluida en planilla
   - ✅ Verificar badge "En Planilla"
   - Click en "Ver Planilla"
   - ✅ Verificar que abre la planilla

5. **Desde Factura → Agregar a Planilla:**
   - Abrir factura no incluida
   - Click en "Agregar a Planilla"
   - Seleccionar planilla en borrador
   - ✅ Verificar que se agrega correctamente

### Resultado Esperado
- Navegación fluida entre módulos
- Botones inteligentes funcionan
- Datos se comparten correctamente

---

## Checklist Final

Antes de dar por terminada la validación, verificar:

### Modelos
- [x] Planilla de Reparto: crear, editar, confirmar, asignar, cerrar
- [x] Líneas de Planilla: agregar facturas, ordenar
- [x] Liquidación: crear, enviar, aprobar, rechazar
- [x] Líneas de Liquidación: registrar cobros, evidencias
- [x] Hoja de Cobranza: crear, cargar facturas, analizar

### Vistas
- [x] Todas las vistas list funcionan
- [x] Todas las vistas form son editables
- [x] Vistas kanban son visuales y funcionales
- [x] Pivot y graph muestran datos correctos
- [x] Botones inteligentes funcionan

### Wizards
- [x] Selección masiva de facturas
- [x] Asignar planilla a ruta
- [x] Rechazar liquidación con motivo
- [x] Agregar factura individual

### API REST
- [x] Endpoint de rutas funciona
- [x] Endpoint de detalle funciona
- [x] Endpoint de envío funciona
- [x] Endpoint de estado funciona
- [x] Autenticación valida tokens

### Permisos
- [x] Usuario de inventario: acceso correcto
- [x] Usuario de contabilidad: acceso correcto
- [x] Administrador: todos los permisos
- [x] Portal: solo lectura

### Validaciones
- [x] No permite facturas duplicadas en planillas
- [x] Valida montos correctamente
- [x] Valida estados de entrega
- [x] Valida existencia de liquidación para cerrar

### Integraciones
- [x] Con pharma_dispatch: rutas y conductores
- [x] Con account: facturas y pagos
- [x] Con sale: pedidos y vendedores
- [x] Botones de navegación entre módulos

---

## Problemas Conocidos y Soluciones

### Problema: "Sequence not found"
**Solución:** Reinstalar el módulo para crear las secuencias automáticamente

### Problema: "Invoice already in another sheet"
**Solución:** La factura está en una planilla activa. Cerrar o cancelar esa planilla primero

### Problema: "Authentication required" en API
**Solución:** Verificar que el token Bearer es válido y está en el header

### Problema: No aparece menú Tesorería
**Solución:** Verificar que pharma_dispatch está instalado (es el menú padre)

---

## Reporte de Bugs

Si encuentras algún bug durante las pruebas, reportar con:
1. Descripción del problema
2. Pasos para reproducir
3. Resultado esperado vs resultado obtenido
4. Logs de error (modo debug activado)
5. Screenshots (si aplica)

---

**Fecha de última actualización:** Noviembre 2025  
**Versión del módulo:** 18.0.1.0.0  
**Estado:** Completo y listo para pruebas

