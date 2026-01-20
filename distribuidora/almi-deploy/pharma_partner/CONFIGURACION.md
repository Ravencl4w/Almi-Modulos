# Guía de Configuración - Gestión de Contactos Farmacéuticos

## 📋 Índice
1. [Configuración Inicial](#configuración-inicial)
2. [Gestión de Zonas de Venta](#gestión-de-zonas-de-venta)
3. [Configuración de Giros de Negocio](#configuración-de-giros-de-negocio)
4. [Sistema de Créditos](#sistema-de-créditos)
5. [Control de Resoluciones](#control-de-resoluciones)
6. [Listas de Precios](#listas-de-precios)
7. [Permisos y Seguridad](#permisos-y-seguridad)
8. [Mejores Prácticas](#mejores-prácticas)

---

## 🚀 Configuración Inicial

### Primer Paso: Verificar Instalación
1. Ir a **Contactos** en el menú principal
2. Verificar que existe el menú **Configuración** → **Zonas de Venta**
3. Abrir un contacto y verificar las pestañas:
   - "Información Comercial"
   - "Resolución de Droguería"

### Segundo Paso: Revisar Zonas Predefinidas
1. Ir a **Contactos** → **Configuración** → **Zonas de Venta**
2. Revisar las zonas que se crearon automáticamente
3. Editar o eliminar según necesidad de tu empresa

---

## 📍 Gestión de Zonas de Venta

### Crear una Nueva Zona

#### Paso 1: Acceder al Menú
- **Contactos** → **Configuración** → **Zonas de Venta**
- Clic en **"Crear"**

#### Paso 2: Completar Información
```
┌─────────────────────────────────────┐
│ Nombre de Zona: Lima Este          │
│ Código: LIM-EST                     │
│ Ejecutivo de Venta: [Seleccionar]  │
│ Activo: ☑                           │
│                                     │
│ Descripción:                        │
│ Zona este de Lima Metropolitana...  │
└─────────────────────────────────────┘
```

**Campos Obligatorios**:
- ✅ **Nombre de Zona**: Descriptivo y claro
- ✅ **Código**: Único, corto (máx. 10 caracteres)

**Campos Opcionales**:
- **Ejecutivo de Venta**: Responsable de la zona
- **Descripción**: Límites geográficos, características
- **Color**: Para visualización en kanban

#### Paso 3: Guardar
- Clic en **"Guardar"**
- La zona estará disponible para asignar a clientes

### Editar Zonas Existentes

1. **Contactos** → **Configuración** → **Zonas de Venta**
2. Seleccionar la zona a editar
3. Modificar campos necesarios
4. Guardar

### Asignar Ejecutivos a Zonas

**¿Por qué es importante?**
- Permite a cada vendedor ver sus clientes
- Facilita seguimiento y reportes
- Optimiza gestión de rutas

**Cómo hacerlo**:
1. Abrir la **Zona de Venta**
2. En **"Ejecutivo de Venta"** seleccionar el usuario
3. Guardar
4. Automáticamente, todos los clientes de esa zona tendrán ese ejecutivo asociado

### Ver Clientes por Zona

**Opción 1: Desde la Zona**
1. Abrir la **Zona de Venta**
2. Ver el contador **"Número de Clientes"**
3. Ir a la pestaña **"Clientes"**
4. Visualizar lista completa

**Opción 2: Desde Contactos**
1. **Contactos** → Vista de Lista
2. Filtrar por **"Zona de Venta"**
3. Agrupar por **"Zona de Venta"** (menú Agrupar)

### Desactivar una Zona

1. Abrir la **Zona de Venta**
2. Desmarcar **"Activo"**
3. La zona no estará disponible para nuevos clientes
4. Los clientes existentes conservan la zona asignada

---

## 💼 Configuración de Giros de Negocio

### Giros Disponibles

Los giros están predefinidos en el sistema:
- 🏥 **Farmacia**
- 🏥 **Botica**
- 🏥 **Clínica**
- 🏥 **Hospital**
- 🔬 **Laboratorio**
- 🚚 **Distribuidor**
- 🏭 **Droguería**
- 🏪 **Cadena de Farmacias**
- 👨‍⚕️ **Consultorio Médico**
- 🐾 **Veterinaria**
- 📋 **Otro** (con campo de texto libre)

### Asignar Giro a un Cliente

1. Abrir el **Contacto**
2. Ir a pestaña **"Información Comercial"**
3. Seleccionar **"Giro del Negocio"**
4. Si selecciona "Otro", completar **"Otro Giro"**
5. Guardar

### Buscar por Giro

**Filtros Rápidos**:
- En Contactos, usar filtros predefinidos:
  - "Farmacias"
  - "Boticas"
  - "Droguerías"
  - "Clínicas/Hospitales"

**Agrupar por Giro**:
1. Vista de Lista de Contactos
2. Menú **"Agrupar Por"**
3. Seleccionar **"Giro del Negocio"**

---

## 💳 Sistema de Créditos

### Configurar Límite de Crédito

#### Para un Cliente Individual

1. Abrir el **Contacto**
2. Ir a **"Información Comercial"**
3. En **"Gestión de Crédito"**:
   - Ingresar **"Límite de Crédito"** (ej: 10,000.00)
   - Agregar **"Notas de Crédito"** si es necesario
4. Clic en **"Aprobar Crédito"**
5. El sistema registra automáticamente:
   - Usuario que aprobó
   - Fecha de aprobación

#### Campos Calculados Automáticamente

El sistema calcula en tiempo real:
- ✅ **Crédito Usado**: Suma de facturas pendientes
- ✅ **Crédito Disponible**: Límite - Crédito usado
- ✅ **Porcentaje Usado**: Visual con barra de progreso

### Alertas de Crédito

El sistema muestra alertas automáticas cuando:

| Porcentaje Usado | Alerta | Color |
|------------------|--------|-------|
| < 75% | ✅ Normal | Verde |
| 75% - 89% | ⚠️ Advertencia | Amarillo |
| 90% - 99% | ⚠️ Crítico | Naranja |
| ≥ 100% | 🚫 Agotado | Rojo |

### Ver Facturas Pendientes

1. En el contacto con crédito
2. Clic en **"Ver Facturas Pendientes"**
3. Se abre lista de facturas sin pagar
4. Permite gestionar cobros

### Monitoreo de Créditos

**Filtros para Control**:
- **"Con Crédito"**: Clientes con límite asignado
- **"Crédito Agotado"**: Clientes que excedieron el límite
- **"Crédito Crítico (>90%)"**: Clientes por agotar crédito

**Uso en Cobranzas**:
```
Contactos → Filtro "Crédito Crítico"
→ Ver clientes que requieren gestión
→ Contactar para pago o ampliar crédito
```

### Workflow de Aprobación

**Proceso Recomendado**:
1. Cliente solicita crédito
2. Gerente evalúa:
   - Historial de pagos
   - Referencias comerciales
   - Estados financieros
3. Gerente ingresa límite en Odoo
4. Clic en **"Aprobar Crédito"**
5. Quedan registrados: Gerente + Fecha + Monto
6. Cliente habilitado para compras a crédito

---

## 📜 Control de Resoluciones

### ¿Quién Necesita Resolución?

Clientes con giro:
- 🏥 Farmacia
- 🏥 Botica
- 🏭 Droguería
- 🏪 Cadena de Farmacias

**Nota**: La pestaña "Resolución de Droguería" solo se muestra para estos giros.

### Registrar una Resolución

#### Paso 1: Activar Resolución
1. Abrir **Contacto** con giro farmacéutico
2. Ir a pestaña **"Resolución de Droguería"**
3. Activar **"Tiene Resolución de Droguería"** ☑

#### Paso 2: Completar Datos
```
┌──────────────────────────────────────────┐
│ Número de Resolución: RD-2024-0001      │
│ Fecha de Emisión: 01/01/2024            │
│ Fecha de Vencimiento: 01/01/2025        │
│ Autoridad Emisora: DIGEMID              │
│ Archivo: [Cargar PDF]                   │
│                                          │
│ Notas:                                   │
│ Resolución actualizada en enero 2024... │
└──────────────────────────────────────────┘
```

#### Paso 3: Cargar Archivo
1. Clic en **"Archivo de Resolución"**
2. Seleccionar PDF o imagen
3. El archivo queda adjunto al contacto

### Estados de Resolución

El sistema calcula automáticamente:

| Estado | Descripción | Cuando |
|--------|-------------|--------|
| ✅ **Vigente** | Todo en orden | Vence en más de 30 días |
| ⚠️ **Por Vencer** | Renovar pronto | Vence en ≤ 30 días |
| ❌ **Vencida** | Requiere renovación | Ya venció |
| ⚪ **No Aplica** | Sin resolución | No activado |

### Alertas Visuales

**En el Formulario del Contacto**:
- 🔴 Alerta roja superior: Resolución vencida
- 🟡 Alerta amarilla: Por vencer en X días

**En Vista de Lista**:
- Badge de color según estado
- Columna "Estado de Resolución" (opcional)

### Gestión de Vencimientos

**Ver Resoluciones por Vencer**:
```
Contactos 
→ Filtro "Resolución por Vencer"
→ Lista de clientes a contactar
→ Solicitar renovación
```

**Renovar una Resolución**:
1. Abrir el **Contacto**
2. Ir a **"Resolución de Droguería"**
3. Actualizar:
   - Nuevo número (si cambió)
   - Nueva fecha de emisión
   - Nueva fecha de vencimiento
4. Cargar nuevo archivo
5. Guardar

### Workflow de Control

**Proceso Mensual Recomendado**:
1. Primer día del mes:
   - Filtrar "Resolución por Vencer"
   - Exportar lista a Excel
2. Contactar clientes:
   - Solicitar documentos actualizados
3. Al recibir documentos:
   - Actualizar datos en Odoo
   - Cargar nuevo PDF
4. Cliente queda habilitado automáticamente

---

## 💰 Listas de Precios

### Crear Listas por Tipo de Cliente

**Ejemplo: Precio para Farmacias**
1. Ir a **Ventas** → **Configuración** → **Listas de Precios**
2. Crear nueva lista:
   - Nombre: "Farmacias - Precio Público"
   - Moneda: PEN
3. Configurar reglas de precio
4. Guardar

**Ejemplo: Precio para Droguerías**
```
Nombre: Droguerías - Precio Mayorista
Descuento: 15% sobre precio público
Cantidad mínima: 10 unidades
```

### Asignar Lista a un Cliente

**Opción 1: Manual**
1. Abrir **Contacto**
2. Pestaña **"Ventas y Compras"**
3. Campo **"Lista de precios"**
4. Seleccionar la lista apropiada

**Opción 2: Por Defecto según Giro**
_(Requiere personalización adicional o acción automatizada)_

### Relacionar con Giro de Negocio

**Estrategia Recomendada**:
```
Farmacia → Lista "Precio Público"
Droguería → Lista "Mayorista -15%"
Hospital → Lista "Institucional -20%"
Cadena → Lista "Corporativo - Negociado"
```

---

## 🔒 Permisos y Seguridad

### Grupos de Acceso

El módulo respeta los grupos estándar de Odoo:

| Grupo | Acceso a Zonas | Descripción |
|-------|----------------|-------------|
| **Usuario Base** | Solo lectura | Ver información |
| **Vendedor** | Lectura/Escritura | Gestionar zonas |
| **Gerente Ventas** | Control total | Crear/Editar/Eliminar zonas |
| **Administrador** | Control total | Acceso completo |

### Configurar Permisos

1. Ir a **Configuración** → **Usuarios y Compañías** → **Usuarios**
2. Seleccionar usuario
3. En **"Derechos de Acceso"**:
   - **Ventas**: Elegir nivel (Vendedor/Gerente)
4. Guardar

### Restricciones de Edición

**Campos Sensibles** (requieren permisos):
- ✅ Límite de crédito: Solo Gerentes o Contabilidad
- ✅ Aprobación de crédito: Registra usuario automáticamente
- ✅ Zonas de venta: Solo Gerentes pueden crear/eliminar

### Auditoría de Cambios

Campos con **tracking habilitado**:
- Giro del negocio
- Zona de venta
- Límite de crédito
- Estado de resolución
- Datos de resolución

**Ver Historial**:
1. Abrir contacto
2. Botón superior derecho → **"Log"**
3. Ver todos los cambios con:
   - Usuario que hizo el cambio
   - Fecha y hora
   - Valores anteriores y nuevos

---

## ✅ Mejores Prácticas

### Gestión de Zonas

✅ **Recomendado**:
- Códigos cortos y claros (LIM-NOR, AQP, CUS)
- Asignar un ejecutivo por zona
- Mantener descripciones actualizadas
- Revisar distribución trimestral

❌ **Evitar**:
- Zonas demasiado grandes (dificulta gestión)
- Códigos confusos o muy largos
- Dejar zonas sin ejecutivo asignado

### Gestión de Créditos

✅ **Recomendado**:
- Establecer política de crédito por giro
- Revisar mensualmente clientes críticos
- Documentar aprobaciones en notas
- Usar filtros para seguimiento

❌ **Evitar**:
- Créditos sin aprobación formal
- Ignorar alertas de crédito agotado
- No actualizar límites según crecimiento

### Control de Resoluciones

✅ **Recomendado**:
- Revisar vencimientos al inicio de mes
- Mantener PDFs actualizados
- Bloquear ventas a clientes vencidos
- Proceso de renovación proactivo

❌ **Evitar**:
- Vender sin verificar vigencia
- No cargar archivos de respaldo
- Ignorar alertas de vencimiento

### Clasificación de Clientes

✅ **Recomendado**:
- Clasificar todos los clientes por giro
- Asignar zona geográfica
- Mantener datos actualizados
- Usar campos de notas para contexto

❌ **Evitar**:
- Dejar giro sin asignar
- Clientes sin zona (dificulta gestión)
- Datos obsoletos

---

## 📊 Reportes y Análisis

### Reportes Disponibles

#### 1. Distribución Geográfica
```
Contactos → Agrupar por "Zona de Venta"
→ Ver cantidad de clientes por zona
→ Exportar a Excel para análisis
```

#### 2. Análisis por Giro
```
Contactos → Agrupar por "Giro del Negocio"
→ Ver composición de cartera
→ Identificar segmentos principales
```

#### 3. Control de Créditos
```
Contactos → Filtro "Crédito Crítico"
→ Lista de clientes en riesgo
→ Gestión de cobranzas prioritaria
```

#### 4. Vencimientos de Resoluciones
```
Contactos → Filtro "Resolución por Vencer"
→ Calendario de renovaciones
→ Plan de seguimiento
```

### Exportar Datos

1. Ir a vista de **Lista** de Contactos
2. Aplicar filtros necesarios
3. Clic en **⋮** (menú)
4. **"Exportar"**
5. Seleccionar campos a exportar
6. Formato Excel/CSV

---

## 🔧 Configuración Avanzada

### Multi-Compañía

Si tienes varias compañías en Odoo:
- Las zonas son **por compañía**
- Código de zona único **dentro de cada compañía**
- Configuración independiente por compañía

### Integración con Geolocalización

Para optimización de rutas:
1. Instalar módulo de geolocalización de Odoo
2. Configurar API de Google Maps
3. Las zonas se pueden visualizar en mapa
4. Planificar rutas de visita óptimas

### Automatizaciones

**Ideas para Acciones Automatizadas**:
```python
# Ejemplo: Alerta cuando crédito > 90%
trigger: Crédito usado > 90%
action: Enviar email a gerente
```

```python
# Ejemplo: Recordatorio resolución por vencer
trigger: 30 días antes de vencimiento
action: Enviar email a cliente y vendedor
```

---

## 🆘 Preguntas Frecuentes

### ¿Puedo modificar los giros de negocio?
Sí, pero requiere editar el código Python en `models/res_partner.py`, campo `business_sector`.

### ¿Cómo elimino una zona con clientes asignados?
No se puede eliminar directamente. Primero reasigna los clientes a otra zona, luego elimina.

### ¿El crédito se actualiza automáticamente?
Sí, se calcula en tiempo real según facturas pendientes del cliente.

### ¿Puedo tener zonas sin ejecutivo?
Sí, el ejecutivo es opcional, pero recomendamos asignarlo para mejor gestión.

### ¿Las alertas envían emails automáticamente?
No en la versión básica. Se pueden configurar acciones automatizadas si lo necesitas.

---

## 📝 Checklist de Configuración

- [ ] Zonas de venta revisadas/editadas
- [ ] Ejecutivos asignados a zonas
- [ ] Clientes clasificados por giro
- [ ] Zonas asignadas a clientes
- [ ] Política de créditos definida
- [ ] Límites de crédito configurados
- [ ] Listas de precios creadas y asignadas
- [ ] Resoluciones registradas (clientes aplicables)
- [ ] Permisos de usuario configurados
- [ ] Equipo capacitado en uso del módulo

---

**¡Configuración Completada!** 🎉

El módulo está listo para usar. Consulta el [README.md](README.md) para más información sobre características y uso diario.

