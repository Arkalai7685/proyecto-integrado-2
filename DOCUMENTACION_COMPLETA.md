# 📚 IMPULSAMENTE - DOCUMENTACIÓN COMPLETA DEL PROYECTO

**Versión:** 1.0  
**Fecha:** Diciembre 2025  
**Estado:** Producción

---

## 📋 ÍNDICE

1. [Descripción del Proyecto](#descripción-del-proyecto)
2. [Credenciales de Acceso](#credenciales-de-acceso)
3. [Características Principales](#características-principales)
4. [Arquitectura del Sistema](#arquitectura-del-sistema)
5. [Funcionalidades por Rol](#funcionalidades-por-rol)
6. [Guía de Uso](#guía-de-uso)
7. [Instalación y Configuración](#instalación-y-configuración)
8. [Tecnologías Utilizadas](#tecnologías-utilizadas)

---

## 🎯 DESCRIPCIÓN DEL PROYECTO

**ImpulsaMente** es una plataforma web integral diseñada para la gestión de servicios de **apoyo académico y psicológico** para estudiantes. El sistema conecta a profesionales (psicólogos y tutores) con estudiantes que requieren asesoramiento, terapia o tutoría académica.

### Objetivo Principal
Facilitar la coordinación, seguimiento y comunicación entre estudiantes y profesionales de apoyo educativo y psicológico, proporcionando herramientas para:
- Gestión de sesiones y citas
- Seguimiento del progreso del estudiante
- Intercambio de archivos educativos
- Sistema de chat en tiempo real
- Auditoría y reportes de actividades

### ¿Para Quién es ImpulsaMente?

#### 👨‍🎓 Estudiantes
- Solicitar servicios de tutoría académica
- Agendar sesiones de terapia psicológica
- Contratar planes estudiantiles completos
- Comunicarse con sus asesores
- Subir y descargar material educativo

#### 🧠 Psicólogos y 📚 Tutores
- Gestionar sus clientes asignados
- Programar y realizar seguimiento de sesiones
- Compartir recursos educativos
- Comunicarse mediante chat
- Generar reportes de progreso

#### 👨‍💼 Administradores
- Gestión completa de usuarios y servicios
- Asignación de clientes a profesionales
- Generación automática de sesiones
- Auditoría completa del sistema
- Gestión de precios y planes

---

## 🔐 CREDENCIALES DE ACCESO

### 🔴 USUARIOS ACTIVOS EN EL SISTEMA

#### 👨‍💼 ADMINISTRADOR (Superusuario)
```
Usuario: Manuel
Contraseña: [Contactar al administrador del sistema]
Email: manuel@gmail.com
URL: http://127.0.0.1:8000/admin/dashboard/
Permisos: Acceso total al sistema
```

#### 🧠 PSICÓLOGO
```
Usuario: Cote
Nombre: Francisca Cote
Contraseña: [Contactar al administrador del sistema]
Email: fran@gmail.com
URL: http://127.0.0.1:8000/psicologo/dashboard/
Clientes Asignados: 1
```

#### 👨‍🎓 CLIENTE/ESTUDIANTE
```
Usuario: alvaro.cas
Nombre: Alvaro Castillo Arancibia
Contraseña: [Contactar al administrador del sistema]
Email: alavaro.m.castillo@gmail.com
URL: http://127.0.0.1:8000/cliente/dashboard/
```

### 🌐 ACCESOS PRINCIPALES

- **Página Principal:** http://127.0.0.1:8000/
- **Login:** http://127.0.0.1:8000/login/
- **Registro:** http://127.0.0.1:8000/register/
- **Admin Django:** http://127.0.0.1:8000/admin/ (Django admin nativo)

### 🔑 NOTA DE SEGURIDAD
> Por motivos de seguridad, las contraseñas reales no se incluyen en este documento. 
> Contactar al administrador del sistema para obtener acceso.

---

## ✨ CARACTERÍSTICAS PRINCIPALES

### 1. 🎨 Interfaz Moderna y Responsive
- Diseño moderno con gradientes y animaciones
- Totalmente responsive (desktop, tablet, móvil)
- UX intuitiva con navegación por tabs
- Sistema de notificaciones visuales

### 2. 👥 Gestión Multi-Rol
- **Clientes/Estudiantes:** Dashboard personalizado con sus servicios
- **Psicólogos:** Gestión de pacientes y sesiones terapéuticas
- **Tutores:** Seguimiento académico de estudiantes
- **Administradores:** Control total del sistema

### 3. 📅 Sistema de Sesiones
- Programación de citas
- Estados: Programada, Confirmada, Completada, Cancelada
- Notas del empleado y del cliente
- Seguimiento de asistencia
- Generación automática de sesiones desde órdenes

### 4. 📁 Gestión de Archivos
- Subida de documentos (PDF, Word, imágenes, videos)
- Límite de 10MB por archivo
- Descarga segura con permisos
- Organización por cliente y sesión
- Validación de tipos de archivo

### 5. 💬 Sistema de Chat
- Chat en tiempo real entre cliente y empleado
- Indicadores de mensajes no leídos
- Historial de conversaciones
- Envío de archivos por chat

### 6. 🔍 Búsqueda y Filtrado Avanzado
- Búsqueda por nombre, email
- Ordenamiento por:
  - Actividad reciente
  - Próxima cita
  - Nombre alfabético
  - Progreso
  - Archivos nuevos

### 7. 📊 Seguimiento de Progreso
- Barras de progreso visuales
- Cálculo basado en sesiones completadas
- Estadísticas por cliente
- Reportes de actividad

### 8. 🔐 Auditoría Completa
- Registro de todas las acciones importantes
- IP y User-Agent tracking
- Timestamps de actividades
- Historial completo por usuario

### 9. 🛒 Sistema de Órdenes/Solicitudes
- Los clientes solicitan servicios
- Flujo: Pendiente → Confirmado → En Progreso → Completado
- Asignación de empleados preferidos
- Notas y preferencias

### 10. 💰 Gestión de Precios
- Planes flexibles por servicio
- Precios destacados (featured)
- Duraciones personalizables
- Descripciones detalladas

---

## 🏗️ ARQUITECTURA DEL SISTEMA

### Stack Tecnológico

#### Backend
```
- Framework: Django 3.1.12
- Base de Datos: SQLite3 (desarrollo) / PostgreSQL (producción)
- ORM: Django ORM
- Autenticación: Django Auth + Custom User Profiles
```

#### Frontend
```
- HTML5 + CSS3
- JavaScript Vanilla (sin frameworks)
- Django Templates
- Diseño Responsive con Flexbox/Grid
```

#### Seguridad
```
- CSRF Protection
- Rate Limiting (django-ratelimit)
- Secure Password Validation
- File Upload Validation
- SQL Injection Protection (ORM)
```

### Estructura de Módulos

```
ImpulsaMente/
├── ImpulsaMente_project/    # Configuración principal
│   ├── settings.py           # Configuración Django
│   ├── urls.py               # URLs principales
│   └── wsgi.py               # WSGI config
│
├── cuentas/                  # App de usuarios
│   ├── models.py             # UserProfile
│   ├── views.py              # Login, Register, Logout
│   └── forms.py              # Formularios de auth
│
├── servicios/                # App principal
│   ├── models.py             # Service, Price, Order, Assignment, Session, FileUpload, ChatMessage, AuditLog
│   ├── views.py              # Vistas principales y dashboards
│   ├── file_views.py         # Gestión de archivos
│   ├── chat_views.py         # Sistema de chat
│   └── admin.py              # Admin de Django
│
├── templates/                # Templates HTML
│   ├── base.html             # Template base
│   ├── index.html            # Página principal
│   ├── login.html            # Login
│   ├── register.html         # Registro
│   ├── cliente-dashboard.html
│   ├── psicologo-dashboard.html
│   ├── tutor-dashboard.html
│   ├── admin-dashboard.html
│   └── ...
│
├── assets/                   # Archivos estáticos
│   ├── css/                  # Estilos
│   ├── js/                   # JavaScript
│   └── images/               # Imágenes
│
└── media/                    # Archivos subidos
    └── uploads/              # Archivos de usuarios
```

---

## 👤 FUNCIONALIDADES POR ROL

### 🔴 ADMINISTRADOR

#### Panel Principal
- Vista general de todos los servicios, usuarios, órdenes
- Estadísticas en tiempo real
- Acceso rápido a todas las funcionalidades

#### Gestión de Servicios
```
✓ Crear nuevos servicios
✓ Editar servicios existentes
✓ Eliminar servicios
✓ Configurar precios por servicio
✓ Marcar precios como destacados
```

#### Gestión de Usuarios
```
✓ Ver todos los usuarios (clientes y empleados)
✓ Crear nuevos empleados (psicólogos, tutores)
✓ Editar información de usuarios
✓ Activar/desactivar usuarios
✓ Eliminar usuarios
✓ Asignar grupos y permisos
```

#### Gestión de Asignaciones
```
✓ Asignar clientes a empleados
✓ Ver todas las asignaciones activas
✓ Activar/desactivar asignaciones
✓ Crear asignaciones manuales
```

#### Gestión de Órdenes
```
✓ Ver todas las solicitudes
✓ Aprobar o rechazar órdenes
✓ Asignar empleados a órdenes
✓ Generar sesiones automáticamente
✓ Cambiar estados de órdenes
```

#### Gestión de Sesiones
```
✓ Ver todas las sesiones programadas
✓ Crear sesiones manualmente
✓ Editar sesiones existentes
✓ Cancelar sesiones
✓ Ver historial de sesiones
```

#### Auditoría
```
✓ Ver log completo de actividades
✓ Filtrar por usuario, acción, fecha
✓ Exportar reportes
✓ Tracking de IP y dispositivos
```

### 🟢 PSICÓLOGO / TUTOR (EMPLEADO)

#### Dashboard Principal
```
✓ Ver todos los clientes asignados
✓ Buscar clientes por nombre/email
✓ Ordenar clientes por múltiples criterios
✓ Ver progreso de cada cliente
✓ Acceso rápido a archivos del cliente
```

#### Gestión de Clientes
```
✓ Ver detalles completos del cliente
✓ Ver progreso y estadísticas
✓ Ver última sesión realizada
✓ Ver próxima cita programada
✓ Acceder a auditoría del cliente
```

#### Sistema de Archivos
```
✓ Ver archivos del cliente
✓ Subir archivos (materiales, recursos)
✓ Descargar archivos
✓ Eliminar archivos propios
✓ Organización por sesión
```

#### Chat
```
✓ Ver conversaciones activas
✓ Enviar mensajes en tiempo real
✓ Ver contador de mensajes no leídos
✓ Compartir archivos por chat
✓ Historial de mensajes
```

#### Solicitudes
```
✓ Ver nuevas solicitudes asignadas
✓ Aceptar solicitudes
✓ Rechazar solicitudes (con razón)
✓ Ver detalles de cada solicitud
```

#### Sesiones
```
✓ Ver sesiones programadas
✓ Actualizar estado de sesiones
✓ Agregar notas de sesión
✓ Marcar asistencia
```

### 🔵 CLIENTE / ESTUDIANTE

#### Dashboard Principal
```
✓ Ver servicios contratados
✓ Ver empleados asignados
✓ Ver próximas sesiones
✓ Ver progreso personal
✓ Estadísticas de sesiones
```

#### Solicitar Servicios
```
✓ Ver catálogo de servicios
✓ Seleccionar plan
✓ Elegir empleado preferido (opcional)
✓ Agregar notas o preferencias
✓ Enviar solicitud
```

#### Servicios Disponibles
```
1. Tutoría Académica
   - Apoyo en materias específicas
   - Planes de 6 o 12 meses
   - Seguimiento personalizado

2. Terapia Psicológica
   - Apoyo emocional
   - Planes mensuales
   - Sesiones individuales

3. Plan Estudiante
   - Combinación de tutoría y terapia
   - Plan integral
   - Seguimiento completo
```

#### Gestión de Archivos
```
✓ Subir tareas, trabajos, documentos
✓ Ver archivos compartidos por el empleado
✓ Descargar materiales de estudio
✓ Organizar por sesión
```

#### Chat
```
✓ Comunicarse con su psicólogo/tutor
✓ Hacer consultas rápidas
✓ Recibir notificaciones
✓ Compartir archivos
```

#### Perfil
```
✓ Ver información personal
✓ Editar perfil
✓ Cambiar contraseña
✓ Actualizar datos de contacto
```

---

## 📖 GUÍA DE USO

### Para Iniciar el Sistema

#### 1. Preparar el Entorno
```powershell
# Activar entorno virtual (si existe)
.\.venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt
```

#### 2. Aplicar Migraciones
```powershell
python manage.py migrate
```

#### 3. Iniciar el Servidor
```powershell
python manage.py runserver
```

#### 4. Acceder al Sistema
```
Abrir navegador en: http://127.0.0.1:8000/
```

### Flujo Típico de Uso

#### Como Cliente:
1. **Registrarse** en el sistema
2. **Explorar servicios** disponibles
3. **Solicitar un servicio** (tutoría, terapia o plan completo)
4. **Esperar confirmación** del administrador
5. **Comunicarse** con el empleado asignado
6. **Asistir a sesiones** programadas
7. **Compartir archivos** necesarios
8. **Ver progreso** en el dashboard

#### Como Empleado (Psicólogo/Tutor):
1. **Login** con credenciales
2. **Ver solicitudes** pendientes
3. **Aceptar solicitud** de cliente
4. **Programar sesiones** con el cliente
5. **Realizar seguimiento** del progreso
6. **Compartir recursos** educativos
7. **Comunicarse por chat**
8. **Actualizar notas** de sesión

#### Como Administrador:
1. **Login** con credenciales de admin
2. **Revisar órdenes** pendientes
3. **Asignar empleados** a solicitudes
4. **Aprobar órdenes** (cambiar a "confirmed")
5. **Generar sesiones** automáticamente
6. **Monitorear actividad** del sistema
7. **Gestionar usuarios** y permisos
8. **Revisar auditoría**

---

## 🛠️ INSTALACIÓN Y CONFIGURACIÓN

### Requisitos Previos
```
- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- SQLite3 (incluido en Python)
- Git (opcional)
```

### Instalación Paso a Paso

#### 1. Clonar o Descargar el Proyecto
```bash
# Si usas Git
git clone [URL_DEL_REPOSITORIO]
cd proyecto-integrado-main
```

#### 2. Crear Entorno Virtual
```powershell
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

#### 3. Instalar Dependencias
```powershell
pip install -r requirements.txt
```

#### 4. Configurar Base de Datos
```powershell
# Aplicar migraciones
python manage.py migrate

# Crear superusuario (opcional, si no existe)
python manage.py createsuperuser
```

#### 5. Cargar Datos Iniciales (Opcional)
```powershell
# Ejecutar script de pruebas para verificar
python test_sistema_completo.py

# Configurar precios destacados
python configurar_precios_destacados.py
```

#### 6. Iniciar Servidor
```powershell
python manage.py runserver
```

### Variables de Entorno (.env)
```env
# Ejemplo de configuración
SECRET_KEY=tu-secret-key-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de datos (si usas PostgreSQL)
DB_NAME=impulsamente
DB_USER=usuario
DB_PASSWORD=contraseña
DB_HOST=localhost
DB_PORT=5432
```

---

## 🔧 TECNOLOGÍAS UTILIZADAS

### Backend
| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| Django | 3.1.12 | Framework web principal |
| Python | 3.8+ | Lenguaje de programación |
| SQLite3 | - | Base de datos (desarrollo) |
| Pillow | - | Procesamiento de imágenes |
| django-ratelimit | - | Control de rate limiting |

### Frontend
| Tecnología | Propósito |
|------------|-----------|
| HTML5 | Estructura |
| CSS3 | Estilos y diseño |
| JavaScript | Interactividad |
| Django Templates | Renderizado dinámico |

### Seguridad
```
✓ CSRF Protection (Django middleware)
✓ Password Hashing (PBKDF2)
✓ Rate Limiting (django-ratelimit)
✓ XSS Protection (Django templates)
✓ SQL Injection Protection (Django ORM)
✓ File Upload Validation
✓ Session Management
```

### Características Adicionales
```
✓ Responsive Design
✓ Lazy Loading de imágenes
✓ Caché de consultas
✓ Compresión de archivos estáticos
✓ Logging de errores
✓ Auditoría de acciones
```

---

## 📊 ESTADÍSTICAS DEL SISTEMA

### Base de Datos Actual
```
Servicios: 3
Precios: 3
Usuarios: 3
Grupos: 3 (Cliente, Psicólogo, Tutor)
Asignaciones: 1
Sesiones: 4
Archivos: 3
Órdenes: 1
```

### Modelos Principales
```
1. User (Django Auth)
2. UserProfile (Extensión de User)
3. Service (Servicios ofrecidos)
4. Price (Planes de precios)
5. Customer (Información de cliente)
6. Order (Solicitudes de servicio)
7. ClientAssignment (Asignaciones cliente-empleado)
8. Session (Sesiones/citas)
9. FileUpload (Archivos compartidos)
10. ChatMessage (Mensajes de chat)
11. AuditLog (Log de auditoría)
```

---

## 🎓 SERVICIOS DISPONIBLES

### 1. 📚 TUTORÍA ACADÉMICA
```
Descripción:
Apoyo personalizado en materias académicas, técnicas de estudio,
preparación de exámenes y desarrollo de habilidades de aprendizaje.

Planes Disponibles:
- 6 meses: $80,000
- 12 meses: $150,000

Beneficios:
✓ Sesiones individuales
✓ Material de estudio personalizado
✓ Seguimiento de progreso
✓ Apoyo en materias específicas
```

### 2. 🧠 TERAPIA PSICOLÓGICA
```
Descripción:
Apoyo emocional y psicológico para estudiantes, manejo de estrés,
ansiedad académica y desarrollo personal.

Planes Disponibles:
- 1 mes: $15,000

Beneficios:
✓ Sesiones terapéuticas individuales
✓ Espacio confidencial y seguro
✓ Técnicas de manejo emocional
✓ Seguimiento personalizado
```

### 3. 🎯 PLAN ESTUDIANTE
```
Descripción:
Plan integral que combina tutoría académica y apoyo psicológico
para un desarrollo completo del estudiante.

Beneficios:
✓ Tutoría + Terapia combinadas
✓ Seguimiento integral
✓ Precio especial
✓ Atención completa
```

---

## 📞 SOPORTE Y CONTACTO

### Información del Proyecto
```
Nombre: ImpulsaMente
Versión: 1.0
Estado: Producción
Fecha: Diciembre 2025
```

### Administración del Sistema
```
Administrador: Manuel
Email: manuel@gmail.com
```

### Para Reportar Problemas
1. Verificar logs del sistema en `/logs/`
2. Contactar al administrador
3. Incluir información de error y pasos para reproducir

---

## 🚀 PRÓXIMAS MEJORAS

### En Desarrollo
```
⬜ Notificaciones por email
⬜ Sistema de recordatorios automáticos
⬜ Videollamadas integradas
⬜ Pago en línea
⬜ App móvil
⬜ Dashboard con gráficos avanzados
⬜ Exportación de reportes PDF
⬜ Integración con calendario (Google Calendar)
```

---

## 📄 LICENCIA

Este proyecto es propiedad de ImpulsaMente y está protegido por derechos de autor.
Uso exclusivo para fines educativos y de gestión interna.

---

## ✅ CHECKLIST DE VERIFICACIÓN

### Sistema Operativo
- [x] Servidor Django funciona correctamente
- [x] Base de datos configurada
- [x] Migraciones aplicadas
- [x] Archivos estáticos cargados
- [x] Media files configurados

### Funcionalidades
- [x] Login/Logout/Registro
- [x] Dashboards por rol
- [x] Sistema de archivos
- [x] Chat en tiempo real
- [x] Gestión de sesiones
- [x] Auditoría completa
- [x] Búsqueda y filtrado
- [x] Solicitud de servicios

### Seguridad
- [x] CSRF Protection activo
- [x] Rate Limiting configurado
- [x] Validación de archivos
- [x] Permisos por rol
- [x] Logging de actividades

---

**Documento generado el 5 de Diciembre de 2025**  
**ImpulsaMente v1.0 - Sistema de Gestión de Apoyo Estudiantil**
