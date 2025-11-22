# Gestión de Clientes Reales en el Sistema

## 📋 Estado Actual del Sistema

El script `crear_datos_admin.py` ahora está configurado para trabajar con **TODOS los clientes reales** registrados en el sistema.

### Clientes Actuales:
```
• cliente1 (cliente1@example.com)
```

### Empleados Actuales:
```
• Tutores: tutor1
• Psicólogos: psicologo1
```

## 🔄 Cómo Funciona el Script Actualizado

### Cambios Realizados:

1. **Detección Automática de Clientes Reales**
   ```python
   clientes = User.objects.filter(groups__name='Cliente')
   ```
   - Busca TODOS los usuarios que pertenecen al grupo "Cliente"
   - No requiere usernames hardcodeados
   - Se adapta automáticamente a nuevos clientes

2. **Asignación Inteligente**
   - Cada cliente real recibe:
     * 1 tutor asignado (si hay tutores disponibles)
     * 1 psicólogo asignado (50% de probabilidad, si hay psicólogos disponibles)
   - Las asignaciones se crean solo si no existen previamente

3. **Generación de Sesiones**
   - Cada asignación genera 5 sesiones de prueba
   - Mezcla de sesiones pasadas y futuras
   - Estados variados: completed, scheduled, confirmed, cancelled, no_show

4. **Logs de Auditoría**
   - Genera logs para CADA cliente real
   - Logs para empleados (tutores y psicólogos)
   - Logs del administrador

## 📊 Datos Generados Actualmente

```
• Asignaciones: 2 (cliente1 → tutor1, cliente1 → psicologo1)
• Sesiones: 15 (5 sesiones por asignación)
• Logs de Auditoría: 16
```

## ➕ Agregar Más Clientes Reales

### Opción 1: Registro Normal
1. Ir a http://localhost:8000/register/
2. Completar el formulario con:
   - Username
   - Email
   - Nombre y Apellido
   - Contraseña segura (8+ caracteres, mayúsculas, números, caracteres especiales)
3. El sistema automáticamente asigna el grupo "Cliente"

### Opción 2: Crear Clientes desde Admin
1. Acceder al dashboard de admin: http://localhost:8000/admin/dashboard/
2. Ir al tab "Empleados"
3. Usar el formulario de creación (seleccionar grupo "Cliente")

### Opción 3: Script de Python
Crear un script `crear_clientes_reales.py`:

```python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ImpulsaMente_project.settings')
django.setup()

from django.contrib.auth.models import User, Group

# Obtener o crear el grupo Cliente
grupo_cliente, _ = Group.objects.get_or_create(name='Cliente')

# Lista de clientes a crear
clientes = [
    {
        'username': 'maria.garcia',
        'email': 'maria.garcia@estudiante.com',
        'first_name': 'María',
        'last_name': 'García',
        'password': 'Maria@2025!'
    },
    {
        'username': 'juan.martinez',
        'email': 'juan.martinez@estudiante.com',
        'first_name': 'Juan',
        'last_name': 'Martínez',
        'password': 'Juan@2025!'
    },
    {
        'username': 'ana.lopez',
        'email': 'ana.lopez@estudiante.com',
        'first_name': 'Ana',
        'last_name': 'López',
        'password': 'Ana@2025!'
    },
]

for cliente_data in clientes:
    try:
        # Crear usuario
        user = User.objects.create_user(
            username=cliente_data['username'],
            email=cliente_data['email'],
            first_name=cliente_data['first_name'],
            last_name=cliente_data['last_name'],
            password=cliente_data['password']
        )
        
        # Asignar al grupo Cliente
        user.groups.add(grupo_cliente)
        
        print(f'✓ Cliente creado: {user.username} - {user.first_name} {user.last_name}')
        
    except Exception as e:
        print(f'❌ Error creando {cliente_data["username"]}: {str(e)}')

print(f'\n✅ Total de clientes en el sistema: {User.objects.filter(groups__name="Cliente").count()}')
```

Ejecutar:
```bash
python crear_clientes_reales.py
```

## 🔄 Regenerar Datos con Nuevos Clientes

Después de agregar nuevos clientes:

```bash
python crear_datos_admin.py
```

El script:
- Detectará automáticamente los nuevos clientes
- Creará asignaciones para cada uno
- Generará sesiones y logs de auditoría
- Mostrará un resumen completo

## 📈 Visualización en el Dashboard

### Tab de Clientes
Una vez ejecutado el script, en el dashboard de admin verás:

```
+--------------------------------+
| 👤 Cliente: cliente1           |
| 📧 cliente1@example.com        |
|--------------------------------|
| Asignaciones: 2                |
| Sesiones: 15                   |
| Archivos: 0                    |
| Actividad: 3 logs              |
|--------------------------------|
| Asignado a:                    |
| • tutor1 (Tutoría)            |
| • psicologo1 (Terapia)        |
|--------------------------------|
| [📊 Ver Progreso]             |
| [📁 Ver Archivos]             |
+--------------------------------+
```

### Estadísticas Actualizadas
- Las estadísticas se calculan automáticamente desde la base de datos
- Los contadores son precisos y en tiempo real
- No requiere actualización manual

## 🛠️ Flujo de Trabajo Recomendado

### Para un Proyecto Real:

1. **Crear Clientes Reales**
   ```bash
   python crear_clientes_reales.py
   ```

2. **Crear Más Empleados si es Necesario**
   - Tutores especializados en diferentes áreas
   - Psicólogos con diferentes enfoques terapéuticos

3. **Generar Datos de Prueba**
   ```bash
   python crear_datos_admin.py
   ```

4. **Verificar en el Dashboard**
   - Acceder a http://localhost:8000/admin/dashboard/
   - Revisar tab "Clientes"
   - Verificar asignaciones, sesiones y actividad

5. **Ajustar según Necesidades**
   - Modificar número de sesiones por asignación
   - Ajustar probabilidad de asignación de psicólogos
   - Personalizar estados de sesiones

## 🔍 Consultas Útiles

### Ver Todos los Clientes desde Terminal:
```bash
python manage.py shell -c "from django.contrib.auth.models import User; [print(f'{c.username} - {c.email}') for c in User.objects.filter(groups__name='Cliente')]"
```

### Ver Asignaciones de un Cliente:
```bash
python manage.py shell -c "from servicios.models import ClientAssignment; from django.contrib.auth.models import User; cliente = User.objects.get(username='cliente1'); [print(f'{a.employee.username} → {a.service.name}') for a in cliente.client_assignments.all()]"
```

### Ver Sesiones de un Cliente:
```bash
python manage.py shell -c "from servicios.models import Session; from django.contrib.auth.models import User; cliente = User.objects.get(username='cliente1'); [print(f'{s.scheduled_date} - {s.status}') for a in cliente.client_assignments.all() for s in a.sessions.all()]"
```

## ⚠️ Notas Importantes

1. **Contraseñas Seguras**
   - El sistema requiere contraseñas con:
     * Mínimo 8 caracteres
     * Al menos 1 mayúscula
     * Al menos 1 minúscula
     * Al menos 1 número
     * Al menos 1 carácter especial (!@#$%^&*)

2. **Grupos Requeridos**
   - Los clientes DEBEN pertenecer al grupo "Cliente"
   - Los tutores al grupo "Tutor"
   - Los psicólogos al grupo "Psicologo"

3. **Unicidad de Asignaciones**
   - El script NO crea asignaciones duplicadas
   - Verifica si ya existe la combinación cliente-empleado-servicio

4. **Fechas de Sesiones**
   - Las sesiones usan timezone-aware datetimes
   - Configuración en `settings.py`: `USE_TZ = True`

## 🎯 Próximos Pasos

Para un sistema de producción, considera:

1. **Importación Masiva de Clientes**
   - Desde archivo CSV
   - Integración con sistemas universitarios
   - API de registro externo

2. **Validación de Datos**
   - Verificar emails válidos
   - Confirmar identidad de estudiantes
   - Validar información académica

3. **Notificaciones**
   - Email de bienvenida al crear cuenta
   - Notificación de asignación de tutor/psicólogo
   - Recordatorios de sesiones programadas

4. **Dashboard Personalizado**
   - Vista específica para cada cliente
   - Historial completo de sesiones
   - Métricas de progreso académico
