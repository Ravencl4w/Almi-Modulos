# Guía de Configuración - Gestión de Productos Farmacéuticos

## 📋 Índice
1. [Configuración Inicial](#configuración-inicial)
2. [Gestión de Marcas](#gestión-de-marcas)
3. [Gestión de Laboratorios](#gestión-de-laboratorios)
4. [Líneas de Laboratorio](#líneas-de-laboratorio)
5. [Configuración de Productos](#configuración-de-productos)
6. [Registro Sanitario](#registro-sanitario)
7. [Productos Relacionados](#productos-relacionados)
8. [Mejores Prácticas](#mejores-prácticas)

---

## 🚀 Configuración Inicial

### Primer Paso: Revisar Datos Iniciales
1. Ir a **Inventario** → **Farmacia** → **Catálogos** → **Marcas**
2. Revisar marcas precargadas
3. Editar o eliminar según tu negocio

### Segundo Paso: Revisar Laboratorios
1. Ir a **Inventario** → **Farmacia** → **Catálogos** → **Laboratorios**
2. Revisar laboratorios predefinidos
3. Agregar tus laboratorios específicos

---

## 🏷️ Gestión de Marcas

### Crear una Nueva Marca

1. **Acceder al Menú**:
   - **Inventario** → **Farmacia** → **Catálogos** → **Marcas**
   - Clic en **"Crear"**

2. **Completar Información**:
```
Nombre de la Marca: Aspirina
Código: ASP (opcional)
Propietario: [Seleccionar contacto]
Logo: [Cargar imagen]
Activo: ☑
```

3. **Guardar**

### Asignar Marca a Productos

1. Abrir un **Producto**
2. En la sección principal, campo **"Marca"**
3. Seleccionar la marca
4. Guardar

### Ver Productos por Marca

**Opción 1**: Desde la Marca
- Abrir la marca → Ver estadísticas → Pestaña "Productos"

**Opción 2**: Desde Productos
- Productos → Agrupar por "Marca"

---

## 🔬 Gestión de Laboratorios

### Crear un Laboratorio

1. **Acceder**:
   - **Inventario** → **Farmacia** → **Catálogos** → **Laboratorios**
   - Clic en **"Crear"**

2. **Completar**:
```
┌────────────────────────────────────────┐
│ Nombre: Laboratorios XYZ S.A.         │
│ Nombre Corto: XYZ                      │
│ Código: LAB-XYZ                        │
│ País: Perú                             │
│ Contacto: [Seleccionar partner]        │
│ Sitio Web: www.labxyz.com              │
│ Logo: [Cargar]                         │
└────────────────────────────────────────┘
```

3. **Crear Líneas** (opcional):
   - Pestaña "Líneas de Producto"
   - Agregar líneas (LAB1, LAB2, ONCO, etc.)

---

## 📊 Líneas de Laboratorio

### ¿Qué son las Líneas?

Identificadores simplificados para organizar productos dentro de cada laboratorio.

**Ejemplo**: Laboratorio Jimenez
- LAB1: Línea General
- LAB2: Oncología
- LAB3: Cardiología

### Crear una Línea

1. **Desde el Laboratorio**:
   - Abrir laboratorio → Pestaña "Líneas de Producto" → Agregar

2. **O desde el Menú**:
   - **Inventario** → **Farmacia** → **Catálogos** → **Líneas de Laboratorio**

3. **Completar**:
```
Laboratorio: [Seleccionar]
Código: LAB1
Nombre: Línea General
Descripción: Productos de uso general...
```

---

## 💊 Configuración de Productos

### Registrar un Producto Farmacéutico Completo

#### 1. Información Básica

**Inventario** → **Productos** → **Crear**

```
┌─────────────────────────────────────────┐
│ Nombre: Paracetamol 500mg Tabletas     │
│ Código (SKU): PARA-500-TAB              │
│ Categoría: Medicamentos                 │
│ Tipo: Producto Almacenable              │
│ Marca: Panadol                          │
│ Laboratorio: GSK                        │
│ Línea: LAB1                             │
└─────────────────────────────────────────┘
```

#### 2. Pestaña "Información Farmacéutica"

**Clasificación**:
```
Principio Activo: Paracetamol
Concentración: 500mg
Forma Farmacéutica: Tableta
Grupo Terapéutico: Analgésico/Antipirético
```

**Características Especiales**:
```
☐ Requiere Receta Médica
☐ Sustancia Controlada
☐ Cadena de Frío
```

#### 3. Registro Sanitario

```
☑ Requiere Registro Sanitario

Número de Registro: RD-2024-0001
Autoridad Sanitaria: DIGEMID
Fecha de Emisión: 01/01/2024
Fecha de Vencimiento: 01/01/2029
Archivo: [Cargar PDF]

Estado: ✅ Vigente (calculado automáticamente)
```

#### 4. Proveedores

Pestaña "Proveedores":
1. Agregar proveedores con sus precios
2. El primer proveedor será el **Proveedor Principal** automáticamente
3. Ver precio destacado

#### 5. Productos Relacionados

Pestaña "Productos Relacionados":
- **Alternativos**: Ibuprofeno 400mg (sustituto)
- **Opcionales**: Vitamina C (complemento)
- **Accesorios**: Jeringa dosificadora

---

## 📜 Registro Sanitario

### Workflow de Registro

#### Productos Nuevos
1. Crear producto con información básica
2. Ir a **"Información Farmacéutica"**
3. Activar **"Requiere Registro Sanitario"** ☑
4. Completar datos del registro
5. Cargar archivo PDF
6. El estado se calcula automáticamente

#### Estados del Registro

| Estado | Cuando | Acción |
|--------|--------|--------|
| ✅ **Vigente** | Vence en > 60 días | Ninguna |
| ⚠️ **Por Vencer** | Vence en ≤ 60 días | Iniciar renovación |
| ❌ **Vencido** | Ya venció | No comercializar, renovar urgente |
| ⚪ **No Aplica** | No requiere o sin datos | N/A |

### Gestión de Vencimientos

**Proceso Mensual Recomendado**:

1. **Primer día del mes**:
```
Productos → Filtro "Registro por Vencer"
→ Exportar lista
```

2. **Contactar a Laboratorios**:
   - Solicitar renovación de registros

3. **Actualizar Datos**:
   - Al recibir nuevo registro, actualizar fechas
   - Cargar nuevo PDF
   - Estado se actualiza automáticamente

### Renovar un Registro

1. Abrir el **Producto**
2. Pestaña **"Información Farmacéutica"**
3. Actualizar:
   - Nuevo número (si cambió)
   - Nueva fecha de emisión
   - Nueva fecha de vencimiento
4. Cargar nuevo archivo
5. Guardar

---

## 🔗 Productos Relacionados

### Tipos de Relaciones

#### 1. Productos Alternativos
**Uso**: Sustitutos del producto principal

**Ejemplo**:
```
Producto: Paracetamol 500mg (Panadol)
Alternativos:
  - Paracetamol 500mg (Genérico)
  - Ibuprofeno 400mg
  - Dolex 500mg
```

#### 2. Productos Opcionales/Complementarios
**Uso**: Productos que se venden juntos

**Ejemplo**:
```
Producto: Antibiótico en polvo
Opcionales:
  - Jeringa dosificadora
  - Agua destilada
  - Algodón
```

#### 3. Accesorios
**Uso**: Complementos necesarios

**Ejemplo**:
```
Producto: Insulina
Accesorios:
  - Agujas para insulina
  - Lancetas
  - Glucómetro
```

### Configurar Relaciones

1. Abrir el **Producto**
2. Pestaña **"Productos Relacionados"**
3. En cada sección, clic en **"Agregar una línea"**
4. Seleccionar productos
5. Guardar

**Beneficio**: Al vender el producto, Odoo sugerirá los relacionados.

---

## 🔍 Búsqueda y Filtrado

### Filtros Rápidos

En la vista de lista de productos:

**Por Características**:
- "Con Marca"
- "Con Laboratorio"
- "Requiere Receta"
- "Sustancia Controlada"
- "Cadena de Frío"

**Por Registro**:
- "Registro Vigente"
- "Registro Vencido"
- "Registro por Vencer"

### Agrupaciones Útiles

**Agrupar por Marca**:
```
Productos → Agrupar Por → Marca
→ Ver productos organizados por marca
```

**Agrupar por Laboratorio**:
```
Productos → Agrupar Por → Laboratorio
→ Ver productos por fabricante
```

**Agrupar por Forma Farmacéutica**:
```
Productos → Agrupar Por → Forma Farmacéutica
→ Tabletas, Jarabes, Inyectables, etc.
```

---

## ✅ Mejores Prácticas

### Nomenclatura

✅ **Recomendado**:
- **Marcas**: Nombres comerciales claros
- **Laboratorios**: Nombre completo + código corto
- **Líneas**: Códigos simples (LAB1, LAB2, ONCO)
- **Productos**: Nombre + Concentración + Forma

❌ **Evitar**:
- Nombres ambiguos
- Códigos muy largos
- Abreviaturas confusas

### Gestión de Catálogos

✅ **Recomendado**:
- Mantener catálogos actualizados
- Desactivar en vez de eliminar
- Logos en marcas y laboratorios principales
- Revisar catálogos trimestralmente

❌ **Evitar**:
- Duplicar marcas/laboratorios
- Eliminar registros en uso
- Catálogos desorganizados

### Registro Sanitario

✅ **Recomendado**:
- Registrar todos los productos aplicables
- Cargar PDFs de respaldo
- Revisar vencimientos mensualmente
- Proceso de renovación 90 días antes

❌ **Evitar**:
- Vender productos vencidos
- Ignorar alertas
- No cargar documentos de respaldo

---

## 📊 Reportes Útiles

### 1. Productos por Vencer (Mensual)
```
Productos → Filtro "Registro por Vencer"
→ Exportar a Excel
→ Enviar a responsables
```

### 2. Inventario por Laboratorio
```
Productos → Agrupar por "Laboratorio"
→ Analizar distribución
→ Identificar laboratorios principales
```

### 3. Productos sin Registro
```
Productos → Filtro personalizado:
"Requiere Registro = Sí" Y "Número Registro = Vacío"
→ Completar registros faltantes
```

---

## 🔧 Configuración Avanzada

### Integración con Ventas

Los productos relacionados aparecerán automáticamente como sugerencias al:
- Crear cotizaciones
- Crear pedidos de venta
- En el punto de venta (si está instalado)

### Integración con Compras

El proveedor principal se pre-seleccionará al:
- Crear solicitudes de compra
- Generar órdenes de compra
- Reaprovisionar productos

---

## 📝 Checklist de Configuración

- [ ] Marcas revisadas/creadas
- [ ] Laboratorios registrados
- [ ] Líneas de laboratorio definidas
- [ ] Productos clasificados por marca
- [ ] Productos asignados a laboratorio
- [ ] Registros sanitarios completados
- [ ] Productos con proveedores
- [ ] Productos relacionados configurados
- [ ] Filtros y búsquedas probadas
- [ ] Equipo capacitado

---

## 🆘 Preguntas Frecuentes

### ¿Puedo modificar las formas farmacéuticas?
Sí, editando el campo Selection en `models/product_template.py`.

### ¿Cómo cambio el proveedor principal?
Reordena la lista de proveedores. El primero siempre es el principal.

### ¿Se pueden importar productos masivamente?
Sí, usando la función de importación de Odoo (CSV/Excel).

### ¿Las alertas envían emails automáticamente?
No por defecto. Puedes configurar acciones automatizadas.

---

**¡Configuración Completada!** 🎉

Consulta el [README.md](README.md) para más información sobre el uso diario del módulo.

