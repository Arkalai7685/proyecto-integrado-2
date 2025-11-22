# Funcionalidades Avanzadas del Dashboard de Administrador

## Resumen de Nuevas Características

Se han agregado funcionalidades avanzadas al dashboard de administrador para permitir una mejor supervisión y auditoría de clientes.

## Nuevas Funcionalidades Implementadas

### 1. Tab de Clientes (Monitoreo de Progreso)

**Ubicación:** Dashboard Admin → Tab "👤 Clientes"

**Características:**
- Vista en tarjetas de todos los clientes registrados
- Búsqueda en tiempo real por nombre, usuario o email
- Estadísticas individuales por cliente:
  - **Asignaciones activas:** Número de empleados asignados actualmente
  - **Sesiones totales:** Cantidad de sesiones programadas/completadas
  - **Archivos:** Cantidad de archivos compartidos
  - **Actividad:** Registros de auditoría del cliente

**Funciones de Monitoreo:**
- **Ver Progreso:** Redirige al tab de sesiones para ver el historial completo
- **Ver Archivos:** Redirige al tab de archivos para revisar documentos compartidos

**Lista de Asignaciones:**
- Muestra las asignaciones activas del cliente
- Indica el empleado asignado y el servicio contratado
- Badge verde para asignaciones activas

### 2. Tab de Panel Empleado (Auditoría)

**Ubicación:** Dashboard Admin → Tab "📋 Panel Empleado"

**Características:**
- Acceso completo al dashboard de empleado desde la vista de administrador
- Dos opciones de visualización:
  1. **Cargar Panel de Empleado:** Integra el dashboard dentro de un iframe
  2. **Abrir en Nueva Pestaña:** Abre el dashboard en una ventana separada

**Propósito:**
- Permite al administrador auditar la vista que tienen los empleados
- Verificar estudiantes asignados a empleados
- Revisar solicitudes pendientes
- Supervisar el flujo de trabajo desde la perspectiva del empleado

### 3. Estadísticas Mejoradas

**Cambios en el Backend:**

Se modificó la vista `admin_dashboard` en `servicios/views.py` para calcular estadísticas de forma eficiente:

```python
clients = User.objects.filter(groups__name='Cliente').annotate(
    active_assignments_count=Count(
        'client_assignments',
        filter=Q(client_assignments__is_active=True)
    ),
    total_sessions=Count('client_assignments__sessions'),
    files_count=Count('client_assignments__files'),
    audit_count=Count('audit_logs')
)
```

**Ventajas:**
- Consultas optimizadas con anotaciones de Django ORM
- Cálculo en una sola query usando `Count` y filtros `Q`
- Evita múltiples queries N+1
- Datos precisos desde la base de datos

### 4. Funciones JavaScript Agregadas

**Búsqueda de Clientes:**
```javascript
// Búsqueda en tiempo real en tarjetas de clientes
document.getElementById('buscar-cliente').addEventListener('input', function() {
    const busqueda = this.value.toLowerCase();
    const clienteCards = document.querySelectorAll('.cliente-card');
    
    clienteCards.forEach(card => {
        const texto = card.textContent.toLowerCase();
        if (texto.includes(busqueda)) {
            card.style.display = '';
        } else {
            card.style.display = 'none';
        }
    });
});
```

**Ver Progreso del Cliente:**
```javascript
function verProgresoCliente(clienteId) {
    // Cambia al tab de sesiones automáticamente
    // Permite ver el historial completo de sesiones del cliente
}
```

**Ver Archivos del Cliente:**
```javascript
function verArchivosCliente(clienteId) {
    // Cambia al tab de archivos automáticamente
    // Muestra todos los archivos relacionados con el cliente
}
```

**Cargar Panel de Empleado:**
```javascript
function cargarPanelEmpleado() {
    // Carga el dashboard de empleado en un iframe
    // Permite auditar la vista sin salir del dashboard de admin
}
```

## Arquitectura de Datos

### Relaciones de Modelos Utilizadas

```
User (Cliente)
├── client_assignments (ClientAssignment) [FK: client]
│   ├── sessions (Session) [FK: assignment]
│   └── files (FileUpload) [FK: assignment]
└── audit_logs (AuditLog) [FK: user]
```

### Queries Optimizadas

- **Select Related:** Para precarga de relaciones ForeignKey
- **Prefetch Related:** Para relaciones ManyToMany
- **Annotate + Count:** Para estadísticas agregadas
- **Filter con Q Objects:** Para condiciones complejas

## Seguridad Implementada

1. **Decoradores de Acceso:**
   - `@login_required`: Requiere autenticación
   - `@user_passes_test(is_admin)`: Solo administradores

2. **Validación de Permisos:**
   - Solo usuarios con `is_staff=True` o superusuarios
   - Verificación en cada vista de administración

3. **Auditoría:**
   - Todos los accesos al panel de empleado se registran
   - IP tracking en logs de auditoría

## Uso del Dashboard

### Para Ver Progreso de un Cliente:

1. Ir al Dashboard de Admin (`/admin/dashboard/`)
2. Hacer clic en el tab "👤 Clientes"
3. Buscar el cliente deseado (opcional)
4. Revisar las estadísticas en su tarjeta:
   - Asignaciones activas
   - Total de sesiones
   - Archivos compartidos
   - Actividad reciente
5. Hacer clic en "📊 Ver Progreso" para ver sesiones detalladas
6. Hacer clic en "📁 Ver Archivos" para ver documentos

### Para Auditar el Panel de Empleado:

1. Ir al Dashboard de Admin
2. Hacer clic en el tab "📋 Panel Empleado"
3. Opciones:
   - **Opción A:** Clic en "🔄 Cargar Panel de Empleado" para verlo integrado
   - **Opción B:** Clic en "🔗 Abrir en Nueva Pestaña" para vista completa
4. Revisar:
   - Estudiantes asignados a empleados
   - Solicitudes pendientes de servicios
   - Información que ven los tutores/psicólogos

## Estructura Visual

### Tab de Clientes
```
+------------------------------------------+
| [Buscar cliente...]                      |
+------------------------------------------+
| +--------+  +--------+  +--------+       |
| | Avatar |  | Avatar |  | Avatar |       |
| | Nombre |  | Nombre |  | Nombre |       |
| | Email  |  | Email  |  | Email  |       |
| |--------|  |--------|  |--------|       |
| | Stats: |  | Stats: |  | Stats: |       |
| | 2 Asig |  | 1 Asig |  | 3 Asig |       |
| | 5 Ses  |  | 3 Ses  |  | 8 Ses  |       |
| | 2 Arch |  | 1 Arch |  | 4 Arch |       |
| | 12 Act |  | 5 Act  |  | 20 Act |       |
| |--------|  |--------|  |--------|       |
| |Asignado|  |Asignado|  |Asignado|       |
| |a: Tutor|  |a: Psic |  |a: Ambos|       |
| |--------|  |--------|  |--------|       |
| |[Progr]|  |[Progr]|  |[Progr]|       |
| |[Archv]|  |[Archv]|  |[Archv]|       |
| +--------+  +--------+  +--------+       |
+------------------------------------------+
```

### Tab de Panel Empleado
```
+------------------------------------------+
| Panel de Empleado (Auditoría)           |
+------------------------------------------+
| [🔄 Cargar Panel] [🔗 Nueva Pestaña]    |
+------------------------------------------+
| +--------------------------------------+ |
| |                                      | |
| |   [Iframe: Dashboard de Empleado]   | |
| |                                      | |
| |   - Estudiantes Asignados            | |
| |   - Solicitudes Pendientes           | |
| |   - Información de Contacto          | |
| |                                      | |
| +--------------------------------------+ |
+------------------------------------------+
```

## Próximas Mejoras Sugeridas

1. **Filtros Avanzados:**
   - Filtrar clientes por número de asignaciones
   - Filtrar por último acceso
   - Filtrar por servicios contratados

2. **Gráficos de Progreso:**
   - Gráfico de línea de sesiones completadas vs tiempo
   - Gráfico de pastel de distribución de servicios
   - Estadísticas de asistencia a sesiones

3. **Exportación de Datos:**
   - Exportar lista de clientes a Excel/CSV
   - Generar reportes PDF de progreso individual
   - Descargar logs de auditoría

4. **Notificaciones:**
   - Alertas de clientes inactivos
   - Recordatorios de sesiones próximas
   - Notificaciones de archivos nuevos

## Archivos Modificados

1. **templates/admin-dashboard.html**
   - Agregado tab "Clientes" (líneas ~250-340)
   - Agregado tab "Panel Empleado" (líneas ~580-620)
   - Agregadas funciones JavaScript para interacción
   - Sistema de búsqueda en tiempo real

2. **servicios/views.py**
   - Modificada función `admin_dashboard()`
   - Agregadas anotaciones para estadísticas de clientes
   - Import de `Count` desde `django.db.models`

3. **servicios/urls.py**
   - No se requirieron cambios adicionales
   - Las rutas existentes ya soportan las nuevas funcionalidades

## Conclusión

El dashboard de administrador ahora proporciona herramientas completas para:
- ✅ Monitorear el progreso de cada cliente con estadísticas en tiempo real
- ✅ Ver archivos compartidos entre clientes y empleados
- ✅ Auditar la vista de empleados para supervisión completa
- ✅ Búsqueda rápida de clientes
- ✅ Navegación intuitiva entre tabs relacionados

Todas las funcionalidades están optimizadas con queries eficientes y protegidas con controles de acceso basados en roles.
