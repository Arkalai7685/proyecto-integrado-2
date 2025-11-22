# 🛠️ Panel de Administrador - ImpulsaMente

## 📋 Descripción

El Panel de Administrador es un sistema completo de gestión que permite a los administradores controlar todos los aspectos de ImpulsaMente, incluyendo precios, empleados, asignaciones, sesiones, archivos y auditoría de clientes.

---

## ✨ Funcionalidades Implementadas

### 1. 📊 Gestión de Precios
- ✅ **Crear precios** asignándoles categorías (Tutoría, Terapia, Plan Estudiante)
- ✅ Ver todos los precios organizados por servicio
- ✅ Editar precios existentes
- ✅ Eliminar precios
- ✅ Campos: Servicio, Plan, Precio, Moneda (CLP/USD), Descripción

### 2. 👥 Gestión de Empleados
- ✅ **Crear cuentas de empleados** con validación de contraseñas seguras
- ✅ Asignar roles/grupos (Psicólogo, Tutor, etc.)
- ✅ Dar permisos de staff
- ✅ Ver listado de empleados con sus datos
- ✅ Activar/desactivar cuentas de empleados
- ✅ Campos: Username, Email, Nombre, Apellido, Contraseña, Grupo, Staff

### 3. 🔗 Asignación Cliente-Empleado
- ✅ **Asignar clientes a empleados** para servicios específicos
- ✅ Ver todas las asignaciones activas e inactivas
- ✅ Consultar qué empleados están asignados a cada cliente
- ✅ Desactivar asignaciones
- ✅ Campos: Cliente, Empleado, Servicio, Notas, Estado

### 4. 📅 Gestión de Sesiones
- ✅ **Ver todas las fechas de sesión** programadas
- ✅ Programar nuevas sesiones
- ✅ Ver sesiones pasadas y futuras
- ✅ Estados: Programada, Confirmada, Completada, Cancelada, No Asistió
- ✅ Campos: Asignación, Fecha/Hora, Duración, Estado, Notas

### 5. 📁 Archivos Compartidos
- ✅ **Ver archivos enviados entre clientes y empleados**
- ✅ Filtrar archivos por asignación
- ✅ Descargar archivos
- ✅ Eliminar archivos
- ✅ Ver detalles: Nombre, Tipo, Tamaño, Usuario que subió, Fecha
- ✅ Información de qué cliente envió a qué empleado

### 6. 🔍 Auditoría de Clientes
- ✅ **Registro completo de actividades** de los usuarios
- ✅ Filtrar por usuario y tipo de acción
- ✅ Ver detalles: Fecha/Hora, Usuario, Acción, Descripción, IP
- ✅ Acciones registradas:
  - Inicio/Cierre de Sesión
  - Actualización de Perfil
  - Órdenes Creadas/Actualizadas
  - Sesiones Programadas/Completadas
  - Archivos Subidos/Descargados

---

## 🎨 Interfaz

### Navegación por Tabs
El dashboard utiliza un sistema de tabs para organizar todas las funcionalidades:

```
┌─────────────────────────────────────────────────────────────┐
│  🛠️ Panel de Administración                                 │
├─────────────────────────────────────────────────────────────┤
│  [📊 Precios] [👥 Empleados] [🔗 Asignaciones]              │
│  [📅 Sesiones] [📁 Archivos] [🔍 Auditoría]                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Contenido del Tab Activo                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Diseño Visual
- **Gradiente morado**: Fondo atractivo con gradiente de #667eea a #764ba2
- **Tabs interactivos**: Cambio visual al hacer hover y al estar activo
- **Tablas responsivas**: Datos organizados en tablas con hover effects
- **Formularios modernos**: Campos con validación visual en tiempo real
- **Badges de estado**: Colores distintos para cada estado (activo, inactivo, etc.)

---

## 🗄️ Modelos de Base de Datos

### ClientAssignment (Asignaciones)
```python
- client: FK a User (cliente)
- employee: FK a User (empleado)
- service: FK a Service
- assigned_at: DateTime
- is_active: Boolean
- notes: Text
```

### Session (Sesiones)
```python
- assignment: FK a ClientAssignment
- scheduled_date: DateTime
- duration_minutes: Integer
- status: Choice (scheduled, confirmed, completed, cancelled, no_show)
- notes: Text
- employee_notes: Text
- created_at: DateTime
- updated_at: DateTime
```

### FileUpload (Archivos)
```python
- assignment: FK a ClientAssignment
- session: FK a Session (opcional)
- uploaded_by: FK a User
- file: FileField
- file_name: CharField
- file_type: Choice (document, image, audio, video, other)
- file_size: BigInteger
- description: Text
- uploaded_at: DateTime
```

### AuditLog (Auditoría)
```python
- user: FK a User
- action: Choice (login, logout, profile_update, order_created, etc.)
- description: Text
- ip_address: GenericIPAddress
- user_agent: Text
- timestamp: DateTime
- related_object_type: CharField
- related_object_id: Integer
```

---

## 🔧 Archivos Implementados

### Templates
```
templates/
└── admin-dashboard.html     ← Dashboard completo con 6 tabs
```

### Estilos
```
assets/css/
└── admin-dashboard.css      ← Estilos modernos con gradientes y animaciones
```

### Scripts
```
assets/js/
└── admin-dashboard.js       ← Lógica de tabs, validaciones y filtros
```

### Views y URLs
```
servicios/
├── models.py                ← 4 nuevos modelos agregados
├── views.py                 ← 5 nuevas vistas de administración
└── urls.py                  ← 5 nuevas rutas agregadas
```

### Scripts de Datos
```
crear_datos_admin.py         ← Script para crear datos de prueba
```

---

## 🚀 Cómo Usar

### 1. Acceder al Panel

**Opción A: Iniciar sesión como Admin**
```
1. Ir a http://localhost:8000/login/
2. Ingresar:
   Usuario: Admin
   Contraseña: admin123
3. Serás redirigido automáticamente al Panel de Administrador
```

**Opción B: Desde el menú de usuario**
```
1. Iniciar sesión con cuenta de administrador
2. Click en tu nombre de usuario (esquina superior derecha)
3. Click en "🛠️ Panel Administrador"
```

**Opción C: URL directa**
```
http://localhost:8000/admin/dashboard/
(Requiere estar autenticado como superusuario)
```

### 2. Crear un Nuevo Precio

```
1. Click en tab "📊 Precios"
2. Click botón "➕ Nuevo Precio"
3. Completar formulario:
   - Categoría/Servicio: Tutoría / Terapia / Plan Estudiante
   - Nombre del Plan: Ej. "Plan Premium"
   - Precio: Ej. 50000
   - Moneda: CLP o USD
   - Descripción: Detalles del plan
4. Click "💾 Guardar"
```

### 3. Crear una Cuenta de Empleado

```
1. Click en tab "👥 Empleados"
2. Click botón "➕ Nuevo Empleado"
3. Completar formulario:
   - Nombre de Usuario: Ej. "psicologo2"
   - Email: Ej. "psicologo2@example.com"
   - Nombre: Ej. "María"
   - Apellido: Ej. "González"
   - Contraseña: DEBE cumplir requisitos de seguridad
   - Confirmar Contraseña
   - Rol/Grupo: Psicólogo / Tutor / etc.
   - ☑ Dar permisos de staff (opcional)
4. Click "👤 Crear Empleado"
```

**⚠️ Importante**: La contraseña debe cumplir:
- Mínimo 8 caracteres
- Al menos 1 mayúscula
- Al menos 1 minúscula
- Al menos 1 número
- Al menos 1 caracter especial

### 4. Asignar Cliente a Empleado

```
1. Click en tab "🔗 Asignaciones"
2. Click botón "➕ Nueva Asignación"
3. Completar formulario:
   - Cliente: Seleccionar de la lista
   - Empleado: Seleccionar de la lista
   - Servicio: Tutoría / Terapia / Plan Estudiante
   - Notas: Información adicional (opcional)
4. Click "🔗 Crear Asignación"
```

### 5. Programar una Sesión

```
1. Click en tab "📅 Sesiones"
2. Click botón "➕ Nueva Sesión"
3. Completar formulario:
   - Asignación Cliente-Empleado: Seleccionar asignación existente
   - Fecha: Seleccionar del calendario
   - Hora: Ej. 14:00
   - Duración: En minutos, ej. 60
   - Estado: Programada / Confirmada / etc.
   - Notas: Información sobre la sesión (opcional)
4. Click "📅 Crear Sesión"
```

### 6. Ver Archivos Compartidos

```
1. Click en tab "📁 Archivos"
2. (Opcional) Filtrar por asignación específica
3. Ver listado de archivos con:
   - Nombre del archivo
   - Tipo de archivo
   - Tamaño
   - Usuario que lo subió
   - Relación Cliente → Empleado
   - Fecha de subida
4. Opciones:
   - ⬇️ Descargar archivo
   - 🗑️ Eliminar archivo
```

### 7. Revisar Auditoría

```
1. Click en tab "🔍 Auditoría"
2. (Opcional) Filtrar por:
   - Usuario específico
   - Tipo de acción
3. Ver registros con:
   - Fecha y hora exacta
   - Usuario que realizó la acción
   - Tipo de acción
   - Descripción detallada
   - Dirección IP
4. Click en 👁️ para ver detalles completos
```

---

## 📊 Datos de Prueba

El sistema incluye datos de prueba creados automáticamente:

### Asignaciones
- **cliente1 → tutor1** (Tutoría)
- **cliente1 → psicologo1** (Terapia)

### Sesiones
- 10 sesiones creadas (5 por asignación)
- Mezcla de sesiones pasadas, presentes y futuras
- Estados variados (completadas, programadas, confirmadas)

### Logs de Auditoría
- 6 registros de ejemplo
- Acciones de login, órdenes, sesiones

**Para recrear datos de prueba:**
```bash
python crear_datos_admin.py
```

---

## 🔐 Seguridad

### Control de Acceso
- ✅ Requiere autenticación (`@login_required`)
- ✅ Solo superusuarios pueden acceder (`@user_passes_test(is_admin)`)
- ✅ Redirección automática al login si no está autenticado
- ✅ Mensaje de error si no tiene permisos

### Validaciones
- ✅ Validación de contraseñas seguras al crear empleados
- ✅ Verificación de campos requeridos en formularios
- ✅ Validación de fechas (no programar sesiones muy atrás en el pasado)
- ✅ CSRF protection en todos los formularios

### Auditoría
- ✅ Registro automático de IP del usuario
- ✅ Timestamp preciso de cada acción
- ✅ Descripción detallada de cambios
- ✅ Relación con objetos modificados

---

## 🎯 Rutas (URLs)

```python
# Dashboard principal
/admin/dashboard/                    → admin_dashboard

# Acciones de precios
/admin/precio/crear/                 → admin_create_price

# Acciones de empleados
/admin/empleado/crear/               → admin_create_employee

# Acciones de asignaciones
/admin/asignacion/crear/             → admin_create_assignment

# Acciones de sesiones
/admin/sesion/crear/                 → admin_create_session
```

---

## 📱 Responsive

El dashboard es completamente responsive:

### Desktop (> 1024px)
- Tabs en línea horizontal
- Tablas con todas las columnas visibles
- Formularios en 2 columnas

### Tablet (768px - 1024px)
- Tabs ajustados
- Tablas con scroll horizontal
- Formularios adaptados

### Mobile (< 768px)
- Tabs en columna vertical
- Tablas con scroll
- Formularios en 1 columna
- Botones más grandes

---

## 🐛 Solución de Problemas

### Problema: "No tienes permisos para acceder"
**Solución**: Asegúrate de estar logueado con cuenta de superusuario (Admin)

### Problema: "Error al crear empleado - Contraseña insegura"
**Solución**: La contraseña debe cumplir TODOS los requisitos de seguridad

### Problema: "No aparecen datos en las tablas"
**Solución**: Ejecuta `python crear_datos_admin.py` para crear datos de prueba

### Problema: Tabs no cambian al hacer click
**Solución**: Verifica que `admin-dashboard.js` se esté cargando correctamente

---

## 🔄 Migraciones de Base de Datos

Las migraciones ya están aplicadas. Si necesitas recrearlas:

```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate
```

---

## 📈 Próximas Mejoras (Opcionales)

Posibles funcionalidades futuras:

- [ ] Exportar datos a Excel/PDF
- [ ] Gráficos y estadísticas
- [ ] Notificaciones por email
- [ ] Calendario visual de sesiones
- [ ] Upload de archivos desde el admin
- [ ] Edición en línea (inline editing)
- [ ] Búsqueda avanzada y filtros múltiples
- [ ] Historial de cambios
- [ ] Roles personalizados con permisos granulares
- [ ] Dashboard de métricas (KPIs)

---

## 📞 Soporte

Si encuentras algún problema:
1. Verifica que estés logueado como Admin
2. Revisa la consola del navegador (F12) para errores JavaScript
3. Verifica logs de Django en el terminal
4. Asegúrate de que todas las migraciones estén aplicadas

---

**Desarrollado por**: GitHub Copilot  
**Fecha**: Noviembre 22, 2025  
**Versión**: 1.0  
**Estado**: ✅ Completamente Funcional

---

## 🎉 ¡Listo para Usar!

El Panel de Administrador está completamente implementado y listo para gestionar todos los aspectos de ImpulsaMente. Inicia sesión como Admin y comienza a administrar precios, empleados, asignaciones, sesiones y más.
