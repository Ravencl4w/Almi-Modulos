# Guía de Instalación - Gestión de Contactos Farmacéuticos

## 📋 Requisitos Previos

### Requisitos del Sistema
- **Odoo 18.0** instalado y funcionando
- Acceso de administrador al sistema Odoo
- Módulos base de Odoo instalados:
  - `base` (Contactos)
  - `contacts`
  - `account` (Contabilidad)
  - `product` (Productos)

### Permisos Necesarios
- Permisos de escritura en la carpeta de addons de Odoo
- Acceso de administrador a la interfaz de Odoo
- Permisos para instalar módulos

## 📦 Instalación Paso a Paso

### Opción 1: Instalación Manual

#### Paso 1: Copiar el Módulo
```bash
# Copiar la carpeta del módulo a la ruta de addons de Odoo
cp -r pharma_partner /ruta/a/odoo/addons/
```

En Windows (PowerShell):
```powershell
Copy-Item -Path "pharma_partner" -Destination "C:\ruta\a\odoo\addons\" -Recurse
```

#### Paso 2: Establecer Permisos (Linux)
```bash
# Asegurarse de que Odoo puede leer los archivos
sudo chown -R odoo:odoo /ruta/a/odoo/addons/pharma_partner
sudo chmod -R 755 /ruta/a/odoo/addons/pharma_partner
```

#### Paso 3: Actualizar Lista de Módulos
1. Acceder a Odoo como **Administrador**
2. Ir a **Aplicaciones** (Apps)
3. Clic en el menú superior derecho (⋮)
4. Seleccionar **"Actualizar lista de aplicaciones"**
5. Clic en **"Actualizar"** en el diálogo de confirmación

#### Paso 4: Instalar el Módulo
1. En **Aplicaciones**, remover el filtro "Apps"
2. Buscar: `pharma_partner` o `Gestión de Contactos Farmacéuticos`
3. Clic en **"Instalar"**
4. Esperar a que complete la instalación

### Opción 2: Instalación desde Línea de Comandos

```bash
# Actualizar lista de módulos
odoo-bin -c /etc/odoo/odoo.conf -u all -d nombre_de_tu_bd --stop-after-init

# Instalar el módulo
odoo-bin -c /etc/odoo/odoo.conf -i pharma_partner -d nombre_de_tu_bd --stop-after-init

# Reiniciar Odoo
sudo systemctl restart odoo
```

### Opción 3: Docker

Si estás usando Odoo en Docker:

```bash
# Copiar módulo al contenedor
docker cp pharma_partner nombre_contenedor:/mnt/extra-addons/

# Reiniciar el contenedor
docker restart nombre_contenedor

# Actualizar lista de módulos desde la interfaz
# Instalar desde Aplicaciones
```

## ✅ Verificación de Instalación

### 1. Verificar Archivos
Asegurarse de que existen estos archivos en la ruta de addons:
```
pharma_partner/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── sale_zone.py
│   └── res_partner.py
├── views/
│   ├── sale_zone_views.xml
│   └── res_partner_views.xml
├── security/
│   └── ir.model.access.csv
├── data/
│   ├── sale_zone_data.xml
│   └── business_sector_data.xml
├── README.md
├── INSTALACION.md
└── CONFIGURACION.md
```

### 2. Verificar en la Interfaz
Después de la instalación, verificar:

✅ **Menú de Zonas de Venta**:
- Ir a **Contactos** → **Configuración** → **Zonas de Venta**
- Debería aparecer el menú y mostrar las zonas predefinidas

✅ **Campos en Contactos**:
- Abrir cualquier contacto
- Verificar que existan las pestañas:
  - "Información Comercial"
  - "Resolución de Droguería"

✅ **Datos Iniciales**:
- En **Zonas de Venta** deberían aparecer las zonas predefinidas:
  - Lima Norte, Lima Sur, Lima Este, Lima Centro, Lima Moderna
  - Callao
  - Provincias (Arequipa, Cusco, Trujillo, etc.)

### 3. Verificar Logs
Revisar el log de Odoo para asegurarse de que no hay errores:
```bash
# Linux
tail -f /var/log/odoo/odoo-server.log

# Docker
docker logs -f nombre_contenedor
```

Buscar líneas como:
```
INFO nombre_bd odoo.modules.loading: Module pharma_partner loaded
```

## 🔧 Configuración Post-Instalación

Ver archivo [CONFIGURACION.md](CONFIGURACION.md) para:
- Configuración de zonas de venta
- Asignación de ejecutivos
- Configuración de listas de precios
- Ajustes de permisos

## ⚠️ Solución de Problemas

### Problema: El módulo no aparece en la lista
**Solución**:
1. Verificar que la carpeta esté en la ruta correcta de addons
2. Verificar permisos de lectura
3. Actualizar lista de aplicaciones
4. Revisar logs de Odoo para errores de sintaxis

### Problema: Error al instalar - Dependencias faltantes
**Solución**:
1. Instalar primero los módulos requeridos:
   - `account` (Contabilidad)
   - `product` (Productos)
2. Reintentar la instalación

### Problema: No aparecen los campos en el formulario
**Solución**:
1. Limpiar caché del navegador (Ctrl + F5)
2. Cerrar sesión y volver a iniciar
3. Verificar permisos de usuario
4. Revisar que el módulo esté instalado correctamente

### Problema: Error "Access Denied"
**Solución**:
1. Verificar que el archivo `ir.model.access.csv` exista
2. Actualizar el módulo:
   ```bash
   odoo-bin -c config.conf -u pharma_partner -d bd_nombre
   ```
3. Asignar permisos desde Configuración → Usuarios y Compañías → Grupos

### Problema: Las zonas no se cargan
**Solución**:
1. Verificar que el archivo `sale_zone_data.xml` exista
2. Cargar datos manualmente:
   - Ir a Configuración → Datos técnicos → Secuencias e Identificadores
   - Buscar registros de `sale.zone`
3. O actualizar el módulo con:
   ```bash
   odoo-bin -c config.conf -u pharma_partner -d bd_nombre
   ```

## 🔄 Actualización del Módulo

Si necesitas actualizar el módulo después de cambios:

### Desde la Interfaz
1. Ir a **Aplicaciones**
2. Buscar `pharma_partner`
3. Clic en **"Actualizar"**

### Desde Línea de Comandos
```bash
odoo-bin -c /etc/odoo/odoo.conf -u pharma_partner -d nombre_bd --stop-after-init
sudo systemctl restart odoo
```

### Con Docker
```bash
# Copiar archivos actualizados
docker cp pharma_partner/. nombre_contenedor:/mnt/extra-addons/pharma_partner/

# Actualizar módulo
docker exec -it nombre_contenedor odoo -u pharma_partner -d nombre_bd --stop-after-init

# Reiniciar
docker restart nombre_contenedor
```

## 📝 Notas Importantes

### Modo Desarrollador
Para habilitar el modo desarrollador (útil para troubleshooting):
1. Ir a **Configuración** → **Activar el modo de desarrollador**
2. O agregar `?debug=1` a la URL

### Backup Antes de Instalar
**IMPORTANTE**: Siempre hacer backup de la base de datos antes de instalar módulos nuevos:
```bash
# Backup de la base de datos
pg_dump nombre_bd > backup_$(date +%Y%m%d).sql

# O desde la interfaz de Odoo
# Configuración → Base de Datos → Respaldar
```

### Entorno de Producción
Para entornos de producción:
1. Probar primero en entorno de desarrollo/staging
2. Hacer backup completo
3. Instalar en horario de bajo tráfico
4. Verificar funcionamiento antes de comunicar cambios

## ✅ Checklist de Instalación

- [ ] Odoo 18.0 instalado y funcionando
- [ ] Módulos dependientes instalados
- [ ] Módulo copiado a la carpeta de addons
- [ ] Permisos correctos establecidos
- [ ] Lista de módulos actualizada
- [ ] Módulo instalado exitosamente
- [ ] Verificación de menús y vistas
- [ ] Zonas de venta cargadas
- [ ] Campos visibles en contactos
- [ ] Logs revisados sin errores
- [ ] Configuración post-instalación completada

## 🆘 Soporte

Si encuentras problemas durante la instalación:
1. Revisar los logs de Odoo
2. Consultar la documentación de Odoo 18
3. Verificar permisos de archivos y base de datos
4. Contactar al equipo de desarrollo con:
   - Versión de Odoo
   - Sistema operativo
   - Logs de error completos
   - Pasos realizados antes del error

---

**¡Instalación Completada!** 🎉

Continúa con [CONFIGURACION.md](CONFIGURACION.md) para configurar el módulo según tus necesidades.

