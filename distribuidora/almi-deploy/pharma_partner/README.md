# Gestión de Contactos Farmacéuticos

## 📋 Descripción

Módulo de extensión para Odoo 18 que agrega funcionalidades específicas para empresas farmacéuticas con operaciones de distribución y droguería. Este módulo extiende el módulo base de contactos (`res.partner`) con campos y funcionalidades diseñadas para el sector farmacéutico peruano.

## ✨ Características Principales

### 1. Clasificación por Giro del Negocio
- **Farmacias** y **Boticas**
- **Clínicas** y **Hospitales**
- **Laboratorios**
- **Distribuidores** y **Droguerías**
- **Cadenas de Farmacias**
- **Consultorios Médicos**
- **Veterinarias**
- Campo abierto para **Otros** giros

### 2. Gestión de Zonas de Venta
- Organización geográfica de clientes
- Asignación de ejecutivos de venta por zona
- Zonas predefinidas para Perú:
  - Lima Norte, Sur, Este, Centro, Moderna
  - Callao
  - Provincias principales (Arequipa, Cusco, Trujillo, Chiclayo, Piura, Iquitos)
- Códigos únicos por zona para fácil identificación
- Contador de clientes por zona
- Compatible con geolocalización de Odoo

### 3. Sistema de Gestión de Créditos
- **Límite de crédito** personalizado por cliente
- **Crédito disponible** calculado automáticamente
- **Porcentaje de uso** del crédito con indicadores visuales
- Sistema de **aprobación de créditos** con seguimiento de:
  - Usuario que aprobó
  - Fecha de aprobación
  - Notas y observaciones
- **Alertas automáticas** cuando el crédito:
  - Supera el 75% (Advertencia)
  - Supera el 90% (Crítico)
  - Supera el 100% (Bloqueado)
- Acceso rápido a facturas pendientes de pago

### 4. Control de Resoluciones de Droguería
- Registro de **número de resolución**
- **Fechas de emisión y vencimiento**
- **Estado automático** de la resolución:
  - ✅ Vigente
  - ⚠️ Por Vencer (30 días antes)
  - ❌ Vencida
  - ⚪ No Aplica
- Campo para **autoridad emisora** (DIGEMID, MINSA, etc.)
- Carga de **archivo PDF/imagen** de la resolución
- **Alertas visuales** para resoluciones vencidas o por vencer
- Notas y observaciones adicionales
- Visibilidad automática solo para clientes del sector farmacéutico

### 5. Integraciones con Odoo Base
- **Listas de precios**: Asignación por tipo de cliente
- **Geolocalización**: Compatible con Google Maps
- **Multi-compañía**: Soporte completo
- **Seguimiento de cambios**: Todos los campos críticos tienen tracking
- **Permisos de acceso**: Configurados por roles de usuario

## 🔧 Requisitos Técnicos

- **Odoo**: Versión 18.0
- **Dependencias**:
  - `base` (Contactos)
  - `contacts` (Módulo de contactos)
  - `account` (Contabilidad - para créditos)
  - `product` (Productos - para listas de precios)

## 📦 Instalación

Ver archivo [INSTALACION.md](INSTALACION.md) para instrucciones detalladas de instalación.

## ⚙️ Configuración

Ver archivo [CONFIGURACION.md](CONFIGURACION.md) para guía de configuración paso a paso.

## 📊 Uso

### Clasificación de Clientes
1. Ir a **Contactos** → Abrir un cliente
2. En la pestaña **"Información Comercial"**:
   - Seleccionar el **Giro del Negocio**
   - Asignar una **Zona de Venta**
   - Configurar el **Límite de Crédito**

### Gestión de Zonas de Venta
1. Ir a **Contactos** → **Configuración** → **Zonas de Venta**
2. Crear o editar zonas según necesidad
3. Asignar ejecutivos responsables
4. Ver clientes por zona

### Asignación de Créditos
1. En el contacto, ir a **Información Comercial**
2. Ingresar el **Límite de Crédito**
3. Clic en **"Aprobar Crédito"** (registra usuario y fecha)
4. El sistema calcula automáticamente:
   - Crédito usado
   - Crédito disponible
   - Porcentaje de uso

### Control de Resoluciones
1. Para clientes de tipo Farmacia/Droguería
2. Ir a la pestaña **"Resolución de Droguería"**
3. Activar **"Tiene Resolución de Droguería"**
4. Completar datos:
   - Número de resolución
   - Fechas de emisión y vencimiento
   - Autoridad emisora
   - Cargar archivo PDF

### Filtros y Búsquedas Avanzadas
En la vista de lista de contactos, usar filtros predefinidos:
- Por giro de negocio
- Por zona de venta
- Con/sin crédito
- Crédito agotado o crítico
- Resolución vigente/vencida/por vencer
- Agrupar por giro, zona o estado de resolución

## 📈 Reportes y Análisis

El módulo permite análisis avanzados mediante:
- **Agrupación por zona de venta**: Visualizar distribución geográfica
- **Agrupación por giro**: Análisis por sector
- **Filtros de crédito**: Identificar clientes en riesgo
- **Vista Kanban**: Visualización rápida con badges de estado

## 🔒 Seguridad y Permisos

### Niveles de Acceso
- **Usuario base**: Solo lectura
- **Vendedor**: Lectura y escritura de zonas
- **Gerente de Ventas**: Control total de zonas
- **Administrador del Sistema**: Acceso completo

### Validaciones
- Límite de crédito no puede ser negativo
- Fecha de vencimiento debe ser posterior a fecha de emisión
- Códigos de zona únicos por compañía
- Campos requeridos según contexto

## 🚀 Próximas Mejoras (Roadmap)

- [ ] Dashboard de gestión de créditos
- [ ] Notificaciones automáticas de resoluciones por vencer
- [ ] Integración con Google Maps para rutas de visita
- [ ] Reportes PDF de estado de clientes por zona
- [ ] Histórico de cambios de límite de crédito
- [ ] Workflow de aprobación de créditos por niveles
- [ ] Cálculo automático de límite de crédito basado en historial

## 📝 Notas

### Para Distribuidoras
- Usar zonas de venta para optimizar rutas de entrega
- Monitorear créditos para gestión de cobranzas
- Segmentar por giro para estrategias comerciales

### Para Droguerías
- Control estricto de resoluciones vigentes
- Alertas automáticas de vencimiento
- Filtro rápido de clientes habilitados

### Integración con Facturación Electrónica
Este módulo está diseñado para trabajar junto con el módulo `nubefact_sunat` para facturación electrónica SUNAT.

## 👥 Autor

**SSE** - Sistema Especializado en Soluciones

## 📄 Licencia

LGPL-3

## 🆘 Soporte

Para soporte técnico o consultas:
- Revisar la documentación en `/docs`
- Verificar logs de Odoo para errores
- Contactar al equipo de desarrollo

---

**Versión**: 18.0.1.0.0  
**Última actualización**: 2025

