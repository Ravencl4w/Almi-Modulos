# Guía de Pruebas - Módulo Despacho y Logística

Esta guía contiene los casos de prueba para validar todas las funcionalidades del módulo `pharma_dispatch`.

## Requisitos Previos

### Instalación
1. Instalar dependencias:
   - `sale` (Ventas)
   - `stock` (Inventario)
   - `pharma_partner` (Contactos Farmacéuticos)

2. Instalar el módulo `pharma_dispatch`

3. Verificar que se hayan creado:
   - ✅ Ubicación "Para Recoger" en Inventario
   - ✅ Secuencia para rutas (RUT00001)
   - ✅ Menú "Despacho" en navegación principal

### Configuración Inicial
1. Configurar credenciales NubeFact (si se va a probar GRE):
   - Ir a: Contabilidad → Configuración → NubeFact
   - Ingresar RUC, Token y URL API
   - Probar conexión

2. Verificar ubicación "Para Recoger":
   - Ir a: Inventario → Configuración → Ubicaciones
   - Buscar "Para Recoger"
   - Verificar que sea de tipo "Ubicación Interna"

---

## Caso de Prueba 1: Maestros de Conductores y Vehículos

### Objetivo
Validar la creación y gestión de conductores y vehículos.

### Pasos
1. **Crear Conductor:**
   - Ir a: Despacho → Configuración → Conductores
   - Click en "Crear"
   - Completar datos:
     - Nombre: Juan Pérez
     - DNI: 12345678
     - Licencia: A-III-a
     - Número de licencia: L12345678
     - Fecha de vencimiento: (fecha futura)
     - Teléfono: 987654321
   - Guardar
   - ✅ Verificar que aparece en lista kanban

2. **Crear Vehículo:**
   - Ir a: Despacho → Configuración → Vehículos
   - Click en "Crear"
   - Completar datos:
     - Placa: ABC-123
     - Tipo: Furgoneta
     - Marca: Toyota
     - Modelo: Hiace
     - Capacidad (kg): 1000
     - Conductor: Juan Pérez
     - Estado: Disponible
   - Guardar
   - ✅ Verificar que aparece en lista kanban
   - ✅ Verificar que el conductor muestra 1 vehículo asignado

### Resultado Esperado
- Conductor y vehículo creados correctamente
- Relación conductor-vehículo funcional
- Validaciones de DNI y placa funcionando

---

## Caso de Prueba 2: Planificación de Rutas

### Objetivo
Validar la creación y gestión de rutas de reparto.

### Pasos
1. **Preparar Pedidos:**
   - Crear 3 pedidos de venta confirmados con diferentes clientes
   - Asegurarse de que tengan zonas de venta asignadas
   - Estado: Confirmado

2. **Crear Ruta:**
   - Ir a: Despacho → Operaciones → Rutas de Reparto
   - Click en "Crear"
   - Completar:
     - Fecha: Hoy
     - Conductor: Juan Pérez
     - Vehículo: ABC-123
   - Guardar
   - ✅ Verificar que se genera número automático (RUT00001)

3. **Agregar Pedidos a la Ruta:**
   - En pestaña "Pedidos", agregar los 3 pedidos creados
   - Ordenar usando drag & drop (secuencia)
   - ✅ Verificar que se calculan totales automáticamente
   - ✅ Verificar que se muestran las zonas

4. **Asignar Ruta:**
   - Click en botón "Asignar Ruta"
   - ✅ Verificar que el estado cambia a "Asignado"
   - ✅ Verificar que el vehículo cambia a "En Uso"

5. **Iniciar Ruta:**
   - Click en "Iniciar Ruta"
   - ✅ Verificar que el estado cambia a "En Progreso"
   - ✅ Verificar que se registra hora de inicio

6. **Marcar Entregas:**
   - Marcar primer pedido como "Entregado"
   - Marcar segundo pedido como "Entregado"
   - Marcar tercer pedido como "No Entregado" con motivo
   - ✅ Verificar que se actualizan contadores

7. **Completar Ruta:**
   - Click en "Completar Ruta"
   - ✅ Verificar que el estado cambia a "Completado"
   - ✅ Verificar que el vehículo vuelve a "Disponible"
   - ✅ Verificar que se registra hora de fin

### Resultado Esperado
- Ruta creada y gestionada correctamente
- Estados cambian según workflow
- Validaciones funcionan (no permite completar con pedidos pendientes)
- Vehículo se marca correctamente como "En Uso" / "Disponible"

---

## Caso de Prueba 3: Guías de Remisión Electrónica (GRE)

### Objetivo
Validar la generación y envío de GRE a SUNAT vía NubeFact.

### Requisitos Previos
- NubeFact configurado
- Productos con peso configurado
- Cliente con RUC o DNI válido

### Pasos
1. **Crear y Validar Picking:**
   - Crear pedido de venta
   - Confirmar pedido
   - Validar operación de stock (picking)
   - ✅ Verificar que el picking esté en estado "Hecho"

2. **Marcar como Guía Electrónica:**
   - Abrir el picking
   - Click en "Marcar como Guía Electrónica"
   - ✅ Verificar que aparece pestaña "Guía de Remisión Electrónica"
   - ✅ Verificar que estado GRE es "Borrador"

3. **Completar Datos de GRE:**
   - En pestaña "Guía de Remisión Electrónica":
     - Serie: T001
     - Número: 1
     - Motivo de traslado: 01 - Venta
     - Modalidad: Transporte Privado
     - Dirección de partida: (tu almacén)
     - Ubigeo de partida: 150101
     - Dirección de llegada: (dirección del cliente)
     - Ubigeo de llegada: (ubigeo del cliente)
     - Conductor: Juan Pérez
     - Vehículo: ABC-123
     - Número de bultos: 1
   - ✅ Verificar que peso total se calcula automáticamente

4. **Preparar GRE:**
   - Click en "Preparar GRE"
   - ✅ Verificar que pasa validaciones
   - ✅ Verificar que estado cambia a "Listo para Enviar"

5. **Enviar a SUNAT:**
   - Click en "Enviar a SUNAT"
   - Esperar respuesta (puede tardar 5-10 segundos)
   - ✅ Verificar que estado cambia a "Aceptado por SUNAT"
   - ✅ Verificar que se muestran enlaces PDF, XML, CDR
   - ✅ Verificar que se registra número de ticket

6. **Descargar Documentos:**
   - Click en "Descargar PDF"
   - ✅ Verificar que se descarga el PDF
   - Click en "Descargar XML"
   - ✅ Verificar que se descarga el XML

7. **Consultar Estado:**
   - Click en "Consultar Estado"
   - ✅ Verificar que muestra estado actual en SUNAT

### Resultado Esperado
- GRE se genera correctamente con todos los datos
- Envío a SUNAT exitoso
- Documentos PDF, XML y CDR disponibles
- Validaciones funcionan (peso, conductor, vehículo, etc.)

### Manejo de Errores
Si el envío falla:
- ✅ Verificar que se muestra mensaje de error claro
- ✅ Verificar que estado cambia a "Rechazado"
- ✅ Verificar que se puede reintentar después de corregir

---

## Caso de Prueba 4: Recojo en Local

### Objetivo
Validar el workflow completo de recojo en local con notificaciones.

### Pasos
1. **Crear Pedido para Recojo:**
   - Crear nuevo pedido de venta
   - Seleccionar "Tipo de Entrega": Recojo en Local
   - Agregar productos
   - Confirmar pedido
   - ✅ Verificar que estado de recojo es "Reservado"
   - ✅ Verificar que se registra fecha de reserva
   - ✅ Verificar que se calcula fecha límite (7 días)

2. **Verificar Picking:**
   - Ir a operaciones de stock del pedido
   - ✅ Verificar que ubicación de destino es "Para Recoger"
   - Validar el picking
   - ✅ Verificar que productos se mueven a ubicación "Para Recoger"

3. **Marcar como Listo:**
   - En el pedido, click en "Marcar Listo para Recoger"
   - ✅ Verificar que estado cambia a "Listo para Recoger"
   - ✅ Verificar que se registra fecha
   - ✅ Verificar que cliente se marca como "Notificado"
   - ✅ Verificar que se envía notificación (check en chatter)

4. **Vista Kanban de Recojo:**
   - Ir a: Despacho → Operaciones → Pedidos para Recojo
   - ✅ Verificar que el pedido aparece en columna "Listo para Recoger"
   - ✅ Verificar que muestra información: monto, fecha límite, ubicación
   - ✅ Verificar badge "Cliente notificado"

5. **Registrar Recojo:**
   - En el pedido, click en "Registrar Recojo"
   - Completar:
     - Recogido por: María López
     - DNI de quien recoge: 87654321
   - ✅ Verificar que estado cambia a "Recogido"
   - ✅ Verificar que se registra fecha de recojo
   - ✅ Verificar que se registra en chatter

6. **Verificar en Kanban:**
   - Volver a: Pedidos para Recojo
   - ✅ Verificar que el pedido se movió a columna "Recogido"

### Resultado Esperado
- Workflow completo funciona correctamente
- Stock se aparta en ubicación "Para Recoger"
- Notificaciones se envían automáticamente
- Vista kanban muestra estados correctamente
- Fechas se registran en cada etapa

---

## Caso de Prueba 5: Integración Entre Módulos

### Objetivo
Validar que los diferentes componentes trabajan juntos correctamente.

### Pasos
1. **Ruta con Pedido para Delivery:**
   - Crear pedido con tipo "Entrega a Domicilio"
   - Confirmar pedido
   - Crear ruta y agregar el pedido
   - ✅ Verificar que el pedido muestra la ruta asignada
   - ✅ Verificar que desde la ruta se puede ver el pedido

2. **GRE desde Ruta:**
   - Validar picking del pedido en ruta
   - Marcar como guía electrónica
   - Enviar a SUNAT
   - ✅ Verificar que todo funciona correctamente

3. **Pedido Mixto:**
   - Crear 2 pedidos: uno delivery, uno pickup
   - ✅ Verificar que se gestionan independientemente
   - ✅ Verificar que cada uno sigue su workflow correcto

### Resultado Esperado
- Módulos se integran sin conflictos
- Datos se comparten correctamente
- Workflows no se interfieren entre sí

---

## Validaciones de Seguridad y Permisos

### Usuario con Rol "Inventario / Usuario"
- ✅ Puede ver conductores y vehículos
- ✅ Puede crear y editar rutas
- ✅ Puede marcar entregas
- ✅ Puede gestionar pedidos de recojo
- ❌ No puede eliminar conductores ni vehículos

### Usuario con Rol "Inventario / Administrador"
- ✅ Puede hacer todo lo anterior
- ✅ Puede eliminar conductores y vehículos
- ✅ Puede eliminar rutas

---

## Checklist Final

Antes de dar por terminada la implementación, verificar:

### Maestros
- [x] Conductores: crear, editar, ver, kanban
- [x] Vehículos: crear, editar, ver, kanban
- [x] Relación conductor-vehículo funciona

### Rutas
- [x] Crear ruta con conductor y vehículo
- [x] Agregar pedidos a ruta
- [x] Workflow completo (draft → assigned → in_progress → done)
- [x] Vista kanban funcional
- [x] Vista calendario funcional
- [x] Validaciones de disponibilidad
- [x] Cálculos automáticos (peso, totales)

### GRE
- [x] Marcar picking como guía electrónica
- [x] Completar datos de transporte
- [x] Enviar a SUNAT vía NubeFact
- [x] Descargar PDF, XML, CDR
- [x] Consultar estado
- [x] Manejo de errores
- [x] Validaciones de datos obligatorios

### Recojo en Local
- [x] Crear pedido para recojo
- [x] Stock se aparta en "Para Recoger"
- [x] Workflow (reservado → listo → recogido)
- [x] Notificaciones al cliente
- [x] Vista kanban de recojo
- [x] Registro de quien recoge

### Integraciones
- [x] Integración con pharma_partner (zonas)
- [x] Integración con nubefact_sunat
- [x] Permisos de seguridad
- [x] Menús y navegación

---

## Problemas Conocidos y Soluciones

### Problema: "No se encontró ubicación Para Recoger"
**Solución:** Reinstalar el módulo o crear manualmente la ubicación en Inventario → Configuración → Ubicaciones

### Problema: "Error al enviar a SUNAT"
**Solución:** Verificar credenciales de NubeFact, verificar que todos los campos obligatorios estén completos

### Problema: "Licencia vencida" no permite asignar conductor
**Solución:** Actualizar fecha de vencimiento de licencia del conductor

### Problema: Peso total = 0
**Solución:** Configurar peso en los productos (product.template)

---

## Reporte de Bugs

Si encuentras algún bug durante las pruebas, reportar con:
1. Descripción del problema
2. Pasos para reproducir
3. Resultado esperado vs resultado obtenido
4. Logs de error (si hay)
5. Screenshots (si aplica)

---

**Fecha de última actualización:** Noviembre 2025  
**Versión del módulo:** 18.0.1.0.0  
**Estado:** Completo y listo para pruebas

