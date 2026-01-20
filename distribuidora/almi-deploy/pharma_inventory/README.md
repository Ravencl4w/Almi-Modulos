# Gestión de Inventario Farmacéutico

## 📋 Descripción

Módulo avanzado para Odoo 18 que extiende el sistema de inventario estándar con funcionalidades específicas para el sector farmacéutico, incluyendo control de vencimientos, temperatura, calidad y cumplimiento regulatorio.

## ✨ Características Principales

### 1. Sistema de Alertas de Vencimiento ⏰
**Gestión automática de productos próximos a vencer:**
- Estados automáticos por días restantes:
  - ✅ OK (> 90 días)
  - 🟡 Alerta 90 días
  - 🟠 Alerta 60 días  
  - 🔴 Alerta 30 días
  - ❌ Vencido
- Dashboard de alertas pendientes
- Cron job diario automático
- Gestión de canjes con laboratorios

### 2. Gestión de Canjes con Laboratorios 🔄
**Workflow completo de canje:**
- Estados: Pendiente → En Proceso → Canjeado/Rechazado
- Solicitud de canje automática
- Seguimiento de referencias
- Responsables asignados
- Historial de canjes

### 3. Control de Temperatura 🌡️
**Monitoreo de condiciones de almacenamiento:**
- Registro de temperatura por ubicación/almacén
- Rangos mínimo/máximo configurables
- Estados: OK / Fuera de Rango / Crítico
- Histórico completo con gráficos
- Alertas automáticas a responsables
- Registro de humedad (opcional)
- Soporte para cadena de frío

### 4. Gestión de Rechazos y Calidad 🚫
**Control de productos no conformes:**
- Estados de calidad: Aprobado / Cuarentena / Rechazado
- Motivos de rechazo predefinidos (5 categorías)
- Ubicaciones especiales (cuarentena/rechazo)
- Trazabilidad completa
- Workflow de aprobaciones

### 5. Mejoras en Lotes (stock.lot) 📦
**Campos y funcionalidades añadidos:**
- Estado de vencimiento (calculado automáticamente)
- Días para vencer
- Estado y gestión de canjes
- Estado de calidad
- Requiere cadena de frío
- Alertas enviadas
- Botones de acción rápida

### 6. Control de Ubicaciones 📍
**Tipos especializados:**
- Normal
- Cámara Fría
- Congelador
- **Cuarentena**
- **Rechazados**
- **Vencidos**

Con control de temperatura configurable

### 7. Kardex Mejorado 📊
**Vista mejorada de movimientos:**
- Filtros por lote y vencimiento
- Estado de vencimiento visible
- Información de cadena de frío
- Export especializado

## 🔧 Requisitos Técnicos

- **Odoo**: Versión 18.0
- **Dependencias**:
  - `stock` (Inventario) ✅
  - `product` (Productos) ✅
  - `pharma_product` (Módulo de productos farmacéuticos)

## 📦 Instalación

```bash
# Copiar módulo a addons
cp -r pharma_inventory /ruta/a/odoo/addons/

# Windows
Copy-Item -Path "pharma_inventory" -Destination "C:\ruta\a\odoo\addons\" -Recurse

# Actualizar lista de módulos en Odoo
# Instalar desde Aplicaciones
```

## ⚙️ Configuración Inicial

### 1. Configurar Ubicaciones con Temperatura
1. Ir a **Inventario** → **Configuración** → **Ubicaciones**
2. Abrir una ubicación (ej: Cámara Fría)
3. Activar **"Requiere Control de Temperatura"**
4. Configurar:
   - Temperatura Mínima: 2°C
   - Temperatura Máxima: 8°C
   - Tipo de Ubicación: Cámara Fría
   - Responsable de Alertas

### 2. Crear Ubicaciones Especiales
```
Almacén Principal/
├── Producto Terminado/
├── Cámara Fría/ (2-8°C)
├── Congelador/ (-18°C)
├── Cuarentena/
├── Rechazados/
└── Vencidos/
```

### 3. Configurar Lotes con Vencimiento
1. En productos, activar **"Trazabilidad por Lote/Serie"**
2. Al recibir productos, crear lotes con **Fecha de Vencimiento**
3. El sistema calculará automáticamente el estado

## 📊 Uso Diario

### Registrar Temperatura
1. Ir a ubicación (ej: Cámara Fría)
2. Clic en **"Registrar Temperatura"**
3. Ingresar temperatura actual
4. El sistema alertará si está fuera de rango

### Ver Alertas de Vencimiento
1. **Inventario** → **Farmacia Inventario** → **Dashboard**
2. Ver alertas por prioridad:
   - 🔴 Críticas (vencidos)
   - 🟠 Altas (30 días)
   - 🟡 Medias (60 días)
   - 🟢 Bajas (90 días)

### Solicitar Canje
1. Desde alerta o desde lote
2. Clic en **"Solicitar Canje"**
3. Asignar responsable
4. Seguimiento hasta completar

### Mover a Cuarentena
1. Abrir lote
2. Clic en **"Mover a Cuarentena"**
3. El sistema actualiza estado

## 🎯 Casos de Uso

### Distribuidora Farmacéutica
- Control de 10,000+ lotes
- Alertas automáticas de vencimiento
- Gestión de canjes masivos
- Temperatura en 5 almacenes

### Droguería con Cadena de Frío
- 3 cámaras frías monitoreadas
- Registro temperatura 3 veces al día
- Alertas automáticas fuera de rango
- Cumplimiento regulatorio

### Farmacia Hospitalaria
- Control de cuarentena estricto
- Gestión de rechazos documentada
- Kardex completo por producto
- Trazabilidad total

## 📈 Reportes Disponibles

1. **Histórico de Temperaturas** (gráfico de líneas)
2. **Alertas de Vencimiento** (lista priorizada)
3. **Kardex por Producto** (movimientos detallados)
4. **Inventario Valorizado** (con vencimientos)
5. **Productos en Cuarentena** (filtro)
6. **Dashboard Ejecutivo** (resumen)

## 🔒 Seguridad y Cumplimiento

### Trazabilidad Completa
- Todos los cambios quedan registrados
- Usuario y fecha en cada acción
- Historial de temperaturas
- Registro de canjes y rechazos

### Cumplimiento Regulatorio
✅ Buenas Prácticas de Almacenamiento (BPA)  
✅ Control de Cadena de Frío  
✅ Trazabilidad de Lotes  
✅ Gestión de No Conformes  
✅ Registros para Auditorías

## 🚀 Funcionalidades Futuras

- [ ] Notificaciones por email automáticas
- [ ] Integración con sensores IoT
- [ ] Dashboard avanzado con KPIs
- [ ] Reportes PDF personalizados
- [ ] App móvil para registro de temperatura
- [ ] Workflow de aprobación multi-nivel
- [ ] Integración con laboratorios (API)

## 📝 Diferencias con Odoo Estándar

### ✅ Lo que Odoo YA tiene:
- Gestión de almacenes y ubicaciones
- Lotes con fecha de vencimiento
- Trazabilidad de movimientos
- Kardex básico
- Inventario valorizado

### ➕ Lo que este módulo AGREGA:
- Sistema de alertas automáticas de vencimiento
- Control de temperatura por ubicación
- Gestión completa de canjes
- Estados de calidad y cuarentena
- Dashboard de vencimientos
- Workflow de rechazos
- Tipos de ubicación especializa dos
- Cron jobs automáticos
- Badges y alertas visuales

## 👥 Autor

**SSE** - Sistema Especializado en Soluciones

## 📄 Licencia

LGPL-3

---

**Versión**: 18.0.1.0.0  
**Última actualización**: 2025

**¿Listo para comenzar?** Instala el módulo y configura tus primeras ubicaciones con control de temperatura.

