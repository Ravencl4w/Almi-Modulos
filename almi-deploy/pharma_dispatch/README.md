# Gestión de Despacho y Logística Farmacéutica

Módulo completo para gestión de despacho, rutas de reparto, guías de remisión electrónica y recojo en local para empresas farmacéuticas en Odoo 18.

## 🚀 Características

### 1. Maestro de Conductores y Vehículos
- ✅ Gestión de conductores con DNI, licencia y contacto
- ✅ Catálogo de vehículos con placa, capacidad y estado
- ✅ Asignación dinámica de conductores a vehículos
- ✅ Control de disponibilidad y estado activo

### 2. Planificación de Rutas de Reparto
- ✅ Creación manual de rutas diarias/semanales
- ✅ Asignación de pedidos a rutas por zona
- ✅ Vista kanban y calendario para planificación
- ✅ Seguimiento de entregas (pendiente/entregado/fallido)
- ✅ Integración con zonas de venta del módulo pharma_partner

### 3. Guías de Remisión Electrónica (GRE)
- ✅ Generación automática desde operaciones de stock
- ✅ Envío a SUNAT mediante NubeFact
- ✅ Catálogo completo de motivos de traslado SUNAT
- ✅ Validación de datos obligatorios (RUC, dirección, peso)
- ✅ Descarga de PDF, XML y CDR
- ✅ Consulta de estado en SUNAT
- ✅ Cumplimiento regulatorio total

### 4. Recojo en Local
- ✅ Cliente selecciona "Recojo en local" al hacer pedido
- ✅ Sistema aparta stock en ubicación especial
- ✅ Notificación automática cuando está listo
- ✅ Vista kanban de pedidos para recoger
- ✅ Control de estados: Reservado → Listo → Recogido

## 📦 Instalación

### Requisitos Previos
- Odoo 18.0
- Módulos instalados:
  - `sale` (Ventas)
  - `stock` (Inventario)
  - `pharma_partner` (Gestión de Contactos Farmacéuticos)
  - `nubefact_sunat` (opcional, para GRE)

### Pasos de Instalación

1. Copiar el módulo a la carpeta de addons:
```bash
cp -r pharma_dispatch /ruta/a/odoo/addons/
```

2. Actualizar lista de aplicaciones en Odoo

3. Instalar el módulo "Gestión de Despacho y Logística Farmacéutica"

4. Configurar ubicación "Para Recoger" (se crea automáticamente)

5. Si usa GRE, configurar credenciales NubeFact en el módulo `nubefact_sunat`

## 🔧 Configuración

### 1. Conductores y Vehículos

**Ir a:** Inventario → Despacho → Conductores

- Registrar conductores con datos completos
- Agregar foto (opcional)
- Verificar licencia y vigencia

**Ir a:** Inventario → Despacho → Vehículos

- Registrar vehículos de la flota
- Configurar capacidad en kg y m³
- Asignar conductor por defecto

### 2. Rutas de Reparto

**Ir a:** Inventario → Despacho → Rutas de Reparto

1. Crear nueva ruta
2. Seleccionar fecha y conductor
3. Asignar vehículo
4. Agregar pedidos (sale.order) manualmente
5. Confirmar ruta
6. Marcar entregas como completadas

### 3. Guías de Remisión Electrónica

**Desde Stock Picking:**

1. Validar operación de stock
2. Completar datos de GRE:
   - Motivo de traslado (catálogo SUNAT)
   - Punto de partida y llegada
   - Conductor y vehículo
   - Peso total (calculado automáticamente)
3. Click en "Enviar a SUNAT"
4. Esperar respuesta de NubeFact
5. Descargar PDF/XML

**Motivos de Traslado SUNAT:**
- 01: Venta
- 02: Compra
- 04: Traslado entre establecimientos de la misma empresa
- 08: Importación
- 09: Exportación
- 13: Otros
- 14: Venta sujeta a confirmación del comprador
- 18: Traslado emisor itinerante CP
- 19: Traslado a zona primaria

### 4. Recojo en Local

**Configuración inicial:**
- Verificar que existe la ubicación "Para Recoger" en Inventario → Configuración → Ubicaciones

**Flujo de uso:**

1. Cliente hace pedido y selecciona "Recojo en local"
2. Sistema crea picking interno a ubicación "Para Recoger"
3. Personal de almacén prepara pedido
4. Click en "Marcar como Listo para Recoger"
5. Sistema notifica al cliente (email)
6. Cliente recoge en tienda
7. Validar picking de entrega

**Vista Kanban:**
- Ir a: Ventas → Pedidos → Pedidos para Recojo
- Filtrar por estado
- Gestionar entregas pendientes

## 📊 Reportes y Vistas

### Vista Kanban de Rutas
- Tarjetas con información del conductor, vehículo y pedidos
- Arrastre de pedidos entre rutas
- Código de colores por estado

### Vista Calendario de Rutas
- Visualización mensual/semanal
- Asignación rápida de recursos

### Dashboard de GRE
- Estado de envíos a SUNAT
- Guías pendientes de envío
- Resumen de rechazos

## 🔐 Permisos y Seguridad

El módulo incluye control de acceso para:
- `dispatch.driver`: Conductores
- `dispatch.vehicle`: Vehículos
- `dispatch.route`: Rutas
- `dispatch.route.line`: Líneas de ruta

Por defecto, usuarios con rol de "Inventario / Usuario" tienen acceso de lectura/escritura.

## 🧪 Pruebas

### Caso de Prueba 1: Ruta de Reparto
1. Crear conductor y vehículo
2. Crear 3 pedidos de venta confirmados
3. Crear ruta y asignar conductor/vehículo
4. Agregar los 3 pedidos a la ruta
5. Confirmar ruta
6. Marcar entregas como completadas

### Caso de Prueba 2: GRE a SUNAT
1. Crear pedido de venta
2. Confirmar y validar entrega (picking)
3. Completar datos de GRE
4. Enviar a SUNAT vía NubeFact
5. Verificar respuesta exitosa
6. Descargar PDF

### Caso de Prueba 3: Recojo en Local
1. Crear pedido con "Recojo en local"
2. Confirmar pedido
3. Verificar picking a ubicación "Para Recoger"
4. Marcar como "Listo para recoger"
5. Verificar notificación enviada
6. Validar entrega

## 🐛 Solución de Problemas

### Error: "No se encontró configuración de NubeFact"
**Solución:** Instalar y configurar el módulo `nubefact_sunat` con credenciales válidas

### Error: "Falta peso total para GRE"
**Solución:** Completar campo `weight` en productos (product.template)

### Error: "Ubicación Para Recoger no existe"
**Solución:** Reinstalar el módulo para crear ubicación automáticamente, o crearla manualmente

### GRE rechazada por SUNAT
**Verificar:**
- RUC del cliente es válido
- Dirección completa del cliente
- Ubigeo correcto
- Peso total > 0

## 📝 Notas Técnicas

### Integración con NubeFact
- Reutiliza modelo `nubefact.config` del módulo `nubefact_sunat`
- Endpoint: `{api_url}/guias`
- Formato JSON según especificación NubeFact v1

### Ubicación "Para Recoger"
- Tipo: Ubicación interna
- Usage: Internal Location
- No debe ser de tipo Cliente ni Proveedor

### Cálculo de Peso Total
- Se suma el peso de todos los productos en el picking
- Fórmula: `sum(move.product_id.weight * move.quantity_done for move in picking.move_ids)`

## 🤝 Soporte

Para soporte técnico o consultas:
- Email: soporte@sse.com.pe
- Documentación: Ver carpeta /docs del módulo

## 📄 Licencia

LGPL-3

---

**Versión:** 18.0.1.0.0  
**Autor:** SSE  
**Última actualización:** 2025

