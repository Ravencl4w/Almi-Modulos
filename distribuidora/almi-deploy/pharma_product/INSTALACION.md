# Guía de Instalación - Gestión de Productos Farmacéuticos

## 📋 Requisitos Previos

### Requisitos del Sistema
- **Odoo 18.0** instalado y funcionando
- Módulos base de Odoo instalados:
  - `product` (Productos) ✅
  - `stock` (Inventario) ✅
  - `purchase` (Compras) ✅

### Permisos Necesarios
- Acceso de administrador a Odoo
- Permisos de escritura en la carpeta de addons

## 📦 Instalación Paso a Paso

### Paso 1: Copiar el Módulo
```bash
# Linux/Mac
cp -r pharma_product /ruta/a/odoo/addons/

# Windows (PowerShell)
Copy-Item -Path "pharma_product" -Destination "C:\ruta\a\odoo\addons\" -Recurse
```

### Paso 2: Permisos (Linux)
```bash
sudo chown -r odoo:odoo /ruta/a/odoo/addons/pharma_product
sudo chmod -R 755 /ruta/a/odoo/addons/pharma_product
```

### Paso 3: Actualizar Lista de Módulos
1. Acceder a Odoo como **Administrador**
2. Ir a **Aplicaciones**
3. Menú superior derecho → **"Actualizar lista de aplicaciones"**
4. Confirmar

### Paso 4: Instalar el Módulo
1. En **Aplicaciones**, buscar: `pharma_product`
2. Clic en **"Instalar"**
3. Esperar a que complete

## ✅ Verificación de Instalación

### 1. Verificar Estructura de Archivos
```
pharma_product/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── product_brand.py
│   ├── product_laboratory.py
│   ├── product_laboratory_line.py
│   └── product_template.py
├── views/
│   ├── product_brand_views.xml
│   ├── product_laboratory_views.xml
│   ├── product_laboratory_line_views.xml
│   ├── product_template_views.xml
│   └── menu_items.xml
├── security/
│   └── ir.model.access.csv
├── data/
│   ├── product_brand_data.xml
│   └── product_laboratory_data.xml
├── README.md
├── INSTALACION.md
└── CONFIGURACION.md
```

### 2. Verificar Menús
Después de la instalación, verificar que aparezcan:

✅ **Menú Principal**:
- **Inventario** → **Farmacia**

✅ **Submenús**:
- Inventario → Farmacia → Catálogos → **Marcas**
- Inventario → Farmacia → Catálogos → **Laboratorios**
- Inventario → Farmacia → Catálogos → **Líneas de Laboratorio**

### 3. Verificar Campos en Productos
Abrir cualquier producto:
- ✅ Campo "Marca" visible
- ✅ Campo "Laboratorio Fabricante" visible
- ✅ Campo "Línea de Laboratorio" visible
- ✅ Pestaña "Información Farmacéutica" presente
- ✅ Pestaña "Productos Relacionados" mejorada
- ✅ Pestaña "Proveedores" con proveedor principal

### 4. Verificar Datos Iniciales
En **Marcas** deberían aparecer:
- Panadol
- Dolex
- Mejoral
- Genérico
- etc.

En **Laboratorios** deberían aparecer:
- Bayer
- Pfizer
- Novartis
- GSK
- etc.

## ⚠️ Solución de Problemas

### Problema: Módulo no aparece
**Solución**:
1. Verificar ruta correcta de addons
2. Actualizar lista de aplicaciones
3. Revisar logs: `tail -f /var/log/odoo/odoo-server.log`

### Problema: Error al instalar
**Solución**:
1. Verificar que `product`, `stock` y `purchase` estén instalados
2. Revisar permisos de archivos
3. Verificar logs de Odoo

### Problema: Campos no aparecen
**Solución**:
1. Limpiar caché del navegador (Ctrl + F5)
2. Cerrar sesión y volver a iniciar
3. Verificar que el módulo esté instalado correctamente
4. Actualizar el módulo si hiciste cambios

## 🔄 Actualización del Módulo

### Desde la Interfaz
1. Ir a **Aplicaciones**
2. Buscar `pharma_product`
3. Clic en **"Actualizar"**

### Desde Línea de Comandos
```bash
odoo-bin -c /etc/odoo/odoo.conf -u pharma_product -d nombre_bd --stop-after-init
sudo systemctl restart odoo
```

## 📝 Notas Importantes

### Backup
**SIEMPRE** hacer backup antes de instalar:
```bash
pg_dump nombre_bd > backup_$(date +%Y%m%d).sql
```

### Modo Desarrollador
Para troubleshooting, activar modo desarrollador:
- Configuración → Activar modo desarrollador
- O agregar `?debug=1` a la URL

## ✅ Checklist de Instalación

- [ ] Odoo 18.0 funcionando
- [ ] Módulos dependientes instalados
- [ ] Módulo copiado a addons
- [ ] Permisos correctos
- [ ] Lista de módulos actualizada
- [ ] Módulo instalado
- [ ] Menús visibles
- [ ] Campos en productos visibles
- [ ] Datos iniciales cargados
- [ ] Sin errores en logs

## 🆘 Soporte

Si encuentras problemas:
1. Revisar logs de Odoo
2. Verificar versión de Odoo (debe ser 18.0)
3. Verificar dependencias instaladas
4. Contactar al equipo de desarrollo con:
   - Versión de Odoo
   - Sistema operativo
   - Logs de error completos

---

**¡Instalación Completada!** 🎉

Continúa con [CONFIGURACION.md](CONFIGURACION.md) para configurar el módulo.

