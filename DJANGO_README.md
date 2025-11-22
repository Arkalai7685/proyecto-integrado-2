# Proyecto Django - ImpulsaMente

Este proyecto ha sido desarrollado en Django para gestionar servicios de psicología y tutoría.

## 🚀 Configuración Inicial

### 1. Requisitos previos
- Python 3.11 o superior
- MySQL 8.0 o superior
- Git (opcional)

### 2. Instalación

#### Clonar el repositorio (si aplica)
```bash
git clone <url-del-repositorio>
cd proyecto-integrado-main
```

#### Crear entorno virtual
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Si tienes problemas con la ejecución de scripts en PowerShell, ejecuta:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Instalar dependencias
```powershell
pip install -r requirements.txt
```

### 3. Configurar Base de Datos

#### Crear la base de datos MySQL
```powershell
mysql -u root -p < sql\create_db.sql
```

O desde MySQL CLI:
```sql
CREATE DATABASE mente_libre CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### Configurar variables de entorno
Copia el archivo `.env.example` a `.env` y edita las credenciales:

```powershell
Copy-Item .env.example .env
```

Edita `.env` con tus credenciales:
```
DB_NAME=mente_libre
DB_USER=root
DB_PASSWORD=tu_password
DB_HOST=127.0.0.1
DB_PORT=3306
```

### 4. Migraciones de Django

#### Crear las migraciones
```powershell
python manage.py makemigrations
```

#### Aplicar las migraciones
```powershell
python manage.py migrate
```

### 5. Crear superusuario
```powershell
python manage.py createsuperuser
```

Sigue las instrucciones para crear el usuario administrador.

### 6. Cargar datos iniciales (opcional)

Puedes usar el script SQL existente o crear fixtures de Django:

```powershell
python manage.py loaddata servicios/fixtures/initial_data.json
```

### 7. Ejecutar el servidor de desarrollo

```powershell
python manage.py runserver
```

El servidor estará disponible en: `http://127.0.0.1:8000/`

## 📁 Estructura del Proyecto Django

```
proyecto-integrado-main/
├── ImpulsaMente_project/      # Configuración del proyecto Django
│   ├── settings.py            # Configuración principal
│   ├── urls.py                # URLs principales
│   └── wsgi.py                # Configuración WSGI
├── servicios/                 # App de servicios
│   ├── models.py              # Modelos: Service, Price, Customer, Order
│   ├── views.py               # Vistas de servicios
│   ├── urls.py                # URLs de servicios
│   └── admin.py               # Configuración del admin
├── cuentas/                   # App de usuarios
│   ├── models.py              # Modelo UserProfile
│   ├── views.py               # Vistas de autenticación
│   └── urls.py                # URLs de autenticación
├── templates/                 # Plantillas HTML
│   ├── index.html
│   ├── login.html
│   ├── tutoria.html
│   ├── terapia.html
│   ├── solicitar-servicio.html
│   ├── cliente-dashboard.html
│   └── empleado-dashboard.html
├── assets/                    # Archivos estáticos
│   ├── css/
│   ├── js/
│   └── images/
├── sql/                       # Scripts SQL
│   └── create_db.sql
├── .env                       # Variables de entorno (no versionar)
├── .env.example               # Ejemplo de variables de entorno
├── requirements.txt           # Dependencias Python
└── manage.py                  # Script de gestión de Django
```

## 🔐 Panel de Administración

Accede al panel de administración de Django en:
`http://127.0.0.1:8000/admin/`

Desde aquí puedes gestionar:
- Servicios y precios
- Clientes y órdenes
- Usuarios y perfiles

## 🌐 URLs Principales

- `/` - Página principal
- `/quienes-somos/` - Quiénes somos
- `/tutoria/` - Servicios de tutoría
- `/terapia/` - Servicios de terapia
- `/solicitar-servicio/` - Formulario de solicitud
- `/cuentas/login/` - Login
- `/cuentas/logout/` - Logout
- `/cuentas/register/` - Registro
- `/cliente/dashboard/` - Dashboard del cliente
- `/empleado/dashboard/` - Dashboard del empleado
- `/admin/` - Panel de administración

## 📊 Modelos de Datos

### Service (Servicio)
- name: Nombre del servicio
- slug: Identificador único
- description: Descripción

### Price (Precio)
- service: Relación con Service
- plan: Nombre del plan
- price: Precio
- currency: Moneda (COP/USD)
- description: Descripción

### Customer (Cliente)
- name: Nombre completo
- email: Correo electrónico
- phone: Teléfono

### Order (Orden)
- customer: Relación con Customer
- service: Relación con Service
- price: Relación con Price
- status: Estado (pending, confirmed, in_progress, completed, cancelled)
- notes: Notas adicionales

### UserProfile (Perfil de Usuario)
- user: Relación con User de Django
- user_type: Tipo (cliente, empleado, estudiante)
- phone: Teléfono
- address: Dirección

## 🔧 Comandos Útiles

### Crear migraciones
```powershell
python manage.py makemigrations
```

### Aplicar migraciones
```powershell
python manage.py migrate
```

### Crear superusuario
```powershell
python manage.py createsuperuser
```

### Ejecutar servidor
```powershell
python manage.py runserver
```

### Shell de Django
```powershell
python manage.py shell
```

### Recopilar archivos estáticos (producción)
```powershell
python manage.py collectstatic
```

## 🐛 Solución de Problemas

### Error de conexión a MySQL
Verifica que:
1. MySQL está ejecutándose
2. Las credenciales en `.env` son correctas
3. La base de datos `mente_libre` existe
4. El usuario tiene permisos

### Módulo mysqlclient no encontrado
```powershell
pip install mysqlclient
```

Si hay errores de compilación en Windows, instala el binario:
```powershell
pip install mysqlclient-2.2.7-cp311-cp311-win_amd64.whl
```

### Archivos estáticos no se cargan
En desarrollo, Django sirve automáticamente los archivos estáticos.
En producción, ejecuta:
```powershell
python manage.py collectstatic
```

## 📝 Notas del Proyecto

Este proyecto fue desarrollado con Django. Los archivos PHP antiguos (`api/`) han sido eliminados y reemplazados por vistas Django.

Cambios principales:
1. **Backend**: Django (Python) con ORM
2. **Autenticación**: Django Authentication System
3. **Base de datos**: MySQL con migraciones Django
4. **Templates**: Django Templates
5. **API**: Views de Django con JsonResponse
6. **CSRF**: Token Django automático

## 🚀 Próximos Pasos

1. Implementar Django Rest Framework para API RESTful
2. Agregar autenticación por token (JWT)
3. Implementar tests unitarios
4. Configurar CI/CD
5. Dockerizar la aplicación
6. Implementar notificaciones por email
7. Agregar sistema de pagos

## 📞 Soporte

Para problemas o preguntas, contacta al equipo de desarrollo.
