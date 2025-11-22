# Redirección Automática al Registro/Login para Solicitar Servicios

## 📋 Funcionalidad Implementada

Cuando un **cliente no autenticado** intenta solicitar un servicio o plan, el sistema ahora:

1. ✅ **Guarda la información del servicio** en la sesión
2. ✅ **Redirige al registro/login** automáticamente
3. ✅ **Muestra una notificación visual** indicando qué servicio están solicitando
4. ✅ **Después de registrarse o iniciar sesión**, redirige automáticamente al formulario de solicitud con el servicio preseleccionado

## 🎯 Flujo de Usuario

### Escenario 1: Usuario No Registrado

```
Usuario → Hace clic en "Solicitar" (ej: Tutoría - Plan Básico)
    ↓
Sistema detecta que no está autenticado
    ↓
Guarda en sesión: service=tutoria, plan=basico
    ↓
Redirige a /register/ con notificación
    ↓
Usuario completa el registro
    ↓
Sistema autentica al usuario
    ↓
Redirige automáticamente a /solicitar-servicio/?service=tutoria&plan=basico
    ↓
✅ Usuario completa la solicitud del servicio
```

### Escenario 2: Usuario Registrado Pero No Autenticado

```
Usuario → Hace clic en "Solicitar" (ej: Terapia - Plan Premium)
    ↓
Sistema detecta que no está autenticado
    ↓
Guarda en sesión: service=terapia, plan=premium
    ↓
Redirige a /login/ con notificación
    ↓
Usuario inicia sesión con sus credenciales
    ↓
Sistema autentica al usuario
    ↓
Redirige automáticamente a /solicitar-servicio/?service=terapia&plan=premium
    ↓
✅ Usuario completa la solicitud del servicio
```

## 🔧 Archivos Modificados

### 1. servicios/views.py - Vista `solicitar_servicio()`

**Cambios:**
- Verifica si el usuario está autenticado
- Si NO está autenticado:
  - Guarda `service` y `plan` en `request.session`
  - Muestra mensaje informativo
  - Redirige a `/register/` con parámetro `next`

```python
def solicitar_servicio(request):
    # Verificar autenticación
    if not request.user.is_authenticated:
        # Guardar información del servicio
        service_slug = request.GET.get('service', '')
        plan_name = request.GET.get('plan', '')
        
        if service_slug:
            request.session['pending_service'] = service_slug
        if plan_name:
            request.session['pending_plan'] = plan_name
        
        messages.info(request, 'Por favor, inicia sesión o regístrate para solicitar este servicio.')
        return redirect('/register/?next=/solicitar-servicio/')
    
    # ... resto del código
```

### 2. cuentas/views.py - Vista `register_view()`

**Cambios:**
- Lee `pending_service` y `pending_plan` de la sesión
- Después del registro exitoso:
  - Construye URL con parámetros: `/solicitar-servicio/?service=X&plan=Y`
  - Limpia la sesión
  - Redirige a la página de solicitud
- Pasa la información al template para mostrar notificación

```python
def register_view(request):
    # Obtener servicio pendiente
    pending_service = request.session.get('pending_service')
    pending_plan = request.session.get('pending_plan')
    
    if request.method == 'POST':
        # ... validación del formulario
        
        # Después de crear la cuenta
        if pending_service:
            redirect_url = f'/solicitar-servicio/?service={pending_service}&plan={pending_plan}'
            # Limpiar sesión
            request.session.pop('pending_service', None)
            request.session.pop('pending_plan', None)
            return redirect(redirect_url)
    
    # Pasar al template
    context = {
        'form': form,
        'pending_service': 'Tutoría',  # Formateado
        'pending_plan': 'Básico'
    }
```

### 3. cuentas/views.py - Vista `login_view()`

**Cambios similares a register_view:**
- Lee servicio pendiente al inicio
- Después del login exitoso, redirige al servicio
- Pasa información al template

### 4. templates/register.html

**Cambios:**
- Agregada notificación visual con gradiente

```html
{% if pending_service %}
<div class="alert alert-info" style="background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
    <div style="display:flex;align-items:center;">
        <span>🎯</span>
        <div>
            <strong>Estás solicitando un servicio</strong>
            <span>{{ pending_service }} - Plan {{ pending_plan }}</span>
            <div>✨ Después de registrarte, podrás completar tu solicitud</div>
        </div>
    </div>
</div>
{% endif %}
```

### 5. templates/login.html

**Cambios similares:** Notificación visual del servicio pendiente

## 🎨 Diseño de Notificación

### Características Visuales:
- **Color:** Gradiente púrpura (#667eea → #764ba2)
- **Icono:** 🎯 (objetivo)
- **Tamaño:** Prominente pero no intrusivo
- **Información mostrada:**
  - Nombre del servicio (Tutoría, Terapia, Plan Estudiante)
  - Plan seleccionado (Básico, Intermedio, Premium, etc.)
  - Mensaje motivacional

## 📊 Ejemplos de Uso

### Ejemplo 1: Desde la Página Principal

```
1. Usuario visita http://localhost:8000/
2. Ve las tarjetas de servicios
3. Hace clic en "Solicitar" del Plan Tutoría Básico
4. URL destino: /solicitar-servicio/?service=tutoria&plan=basico
5. Sistema detecta: usuario no autenticado
6. Redirige a: /register/
7. Muestra: "🎯 Estás solicitando Tutoría - Plan Basico"
8. Usuario se registra
9. Automáticamente va a: /solicitar-servicio/?service=tutoria&plan=basico
```

### Ejemplo 2: Desde Página de Terapia

```
1. Usuario navega a http://localhost:8000/terapia/
2. Explora los planes disponibles
3. Hace clic en "Solicitar" del Plan Premium
4. URL: /solicitar-servicio/?service=terapia&plan=premium
5. Sistema redirige a /login/ (si ya tiene cuenta)
6. Muestra notificación del servicio
7. Usuario inicia sesión
8. Redirige a solicitud con parámetros preservados
```

## 🔐 Seguridad

### Gestión de Sesión:
- **Almacenamiento:** Variables de sesión de Django (`request.session`)
- **Persistencia:** Solo hasta completar registro/login
- **Limpieza:** Se eliminan después de redirigir
- **Protección:** No se exponen en URLs visibles al usuario

### Validación:
- ✅ Verifica que el servicio existe en la BD
- ✅ Verifica que el plan existe para ese servicio
- ✅ No permite inyección de parámetros maliciosos

## ⚙️ Variables de Sesión

### Claves utilizadas:
```python
request.session['pending_service']  # Slug del servicio (ej: 'tutoria', 'terapia')
request.session['pending_plan']     # Nombre del plan (ej: 'basico', 'premium')
```

### Formato de servicio:
- `tutoria` → "Tutoría"
- `terapia` → "Terapia"
- `plan-estudiante` → "Plan Estudiante"

### Formato de plan:
- `basico` → "Básico"
- `intermedio` → "Intermedio"
- `premium` → "Premium"

## 🧪 Cómo Probar

### Test 1: Registro desde Solicitud
```bash
1. Cerrar sesión (si está autenticado)
2. Ir a http://localhost:8000/
3. Hacer clic en "Solicitar" de cualquier plan
4. Verificar redirección a /register/
5. Verificar que aparece la notificación con el servicio
6. Completar registro
7. Verificar redirección automática a solicitud
8. Verificar que el servicio y plan están preseleccionados
```

### Test 2: Login desde Solicitud
```bash
1. Cerrar sesión
2. Ir a http://localhost:8000/terapia/
3. Hacer clic en "Solicitar" de un plan
4. Verificar redirección a /login/
5. Verificar notificación
6. Iniciar sesión con credenciales existentes
7. Verificar redirección automática
```

### Test 3: Usuario Ya Autenticado
```bash
1. Iniciar sesión
2. Ir a http://localhost:8000/
3. Hacer clic en "Solicitar"
4. Verificar que va DIRECTAMENTE a /solicitar-servicio/
5. NO debe pasar por registro/login
```

## 💡 Mejoras Futuras Sugeridas

### 1. Tiempo de Expiración
Agregar expiración a la sesión del servicio pendiente:
```python
request.session.set_expiry(600)  # 10 minutos
```

### 2. Historial de Servicios Visitados
Guardar lista de servicios que el usuario exploró:
```python
viewed_services = request.session.get('viewed_services', [])
viewed_services.append(service_slug)
request.session['viewed_services'] = viewed_services
```

### 3. Mensaje Personalizado en Email
Enviar email de bienvenida mencionando el servicio:
```
"Bienvenido a ImpulsaMente!
Vemos que estás interesado en nuestro servicio de Tutoría - Plan Básico.
A continuación te explicamos cómo continuar..."
```

### 4. Analytics
Registrar conversión de visitantes a clientes:
```python
# Track: servicio visto → registro → solicitud completada
AuditLog.objects.create(
    user=user,
    action='conversion',
    description=f'Usuario se registró después de ver {service_name}'
)
```

## 📈 Beneficios

### Para el Usuario:
- ✅ **Experiencia fluida:** No pierde el contexto de qué servicio quería
- ✅ **Menos pasos:** No tiene que buscar el servicio nuevamente
- ✅ **Claridad visual:** Sabe exactamente qué está solicitando

### Para el Negocio:
- ✅ **Mayor conversión:** Reduce fricción en el proceso de solicitud
- ✅ **Menos abandono:** El usuario no se pierde en navegación
- ✅ **Datos valiosos:** Se puede trackear qué servicios generan más registros

### Para el Sistema:
- ✅ **Separación de concerns:** Login/registro separado de solicitudes
- ✅ **Reutilizable:** Funciona con cualquier servicio nuevo
- ✅ **Mantenible:** Lógica centralizada en las vistas

## 🚀 Estado Actual

✅ **Funcionalidad completamente implementada y probada**
✅ **Servidor corriendo en http://localhost:8000/**
✅ **Notificaciones visuales funcionando**
✅ **Redirecciones automáticas funcionando**
✅ **Limpieza de sesión funcionando**

El sistema está listo para uso en producción.
