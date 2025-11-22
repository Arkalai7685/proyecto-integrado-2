# ImpulsaMente - Sistema de Gestión de Servicios

Sistema web desarrollado con Django para la gestión de servicios de tutoría y terapia psicológica.

## 🚀 Inicio Rápido

### Requisitos Previos
- Python 3.11+
- MySQL 8.0+
- pip

### Instalación

1. **Clonar y configurar entorno virtual**
```powershell
cd proyecto-integrado-main
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. **Configurar base de datos**
Edita `.env` con tus credenciales:
```env
DB_NAME=mente_libre
DB_USER=root
DB_PASSWORD=tu_password
DB_HOST=127.0.0.1
DB_PORT=3306
```

3. **Crear base de datos MySQL**
```powershell
mysql -u root -p -e "CREATE DATABASE mente_libre CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

4. **Aplicar migraciones**
```powershell
python manage.py migrate
python manage.py load_services
python manage.py createsuperuser
```

5. **Iniciar servidor**
```powershell
python manage.py runserver
```

## 🌐 URLs del Sistema

- **Inicio**: http://127.0.0.1:8000/
- **Admin**: http://127.0.0.1:8000/admin/
- **Login**: http://127.0.0.1:8000/cuentas/login/
- **Tutoría**: http://127.0.0.1:8000/tutoria/
- **Terapia**: http://127.0.0.1:8000/terapia/
- **Solicitar Servicio**: http://127.0.0.1:8000/solicitar-servicio/

## 📁 Estructura del Proyecto

```
proyecto-integrado-main/
├── ImpulsaMente_project/      # Configuración del proyecto
│   ├── settings.py            # Configuración principal
│   └── urls.py                # URLs principales
├── servicios/                 # App de servicios
│   ├── models.py              # Service, Price, Customer, Order
│   ├── views.py               # Vistas de servicios
│   ├── admin.py               # Panel de administración
│   └── management/            # Comandos personalizados
│       └── commands/
│           └── load_services.py
├── cuentas/                   # App de usuarios
│   ├── models.py              # UserProfile
│   ├── views.py               # Login, logout, registro
│   └── urls.py
├── templates/                 # Plantillas HTML
├── assets/                    # CSS, JS, imágenes
├── sql/                       # Scripts SQL
├── .env                       # Variables de entorno
├── requirements.txt           # Dependencias
└── manage.py                  # Gestor Django
```

## 🔧 Comandos Útiles

```powershell
# Migraciones
python manage.py makemigrations
python manage.py migrate

# Datos iniciales
python manage.py load_services

# Usuarios
python manage.py createsuperuser

# Servidor
python manage.py runserver

# Shell
python manage.py shell
```

## 📊 Modelos de Datos

### servicios
- **Service**: Servicios (Tutoría, Terapia)
- **Price**: Planes y precios
- **Customer**: Clientes
- **Order**: Órdenes/solicitudes

### cuentas
- **UserProfile**: Perfil extendido de usuario (cliente, empleado, estudiante)

## 🔐 Panel de Administración

Accede a http://127.0.0.1:8000/admin/ para gestionar:
- Servicios y precios
- Clientes y órdenes
- Usuarios y perfiles

## 📝 Documentación

- `INICIO_RAPIDO.md` - Guía rápida de configuración
- `DJANGO_README.md` - Documentación detallada
- `MIGRACION_RESUMEN.md` - Resumen de la migración

## 🔒 Seguridad

Django proporciona automáticamente:
- Protección CSRF
- Prevención SQL Injection (ORM)
- Protección XSS
- Hashing seguro de contraseñas
- Middleware de seguridad

## 🚀 Despliegue

Para producción:
```powershell
# Configurar DEBUG=False en .env
python manage.py collectstatic
python manage.py check --deploy
```

---

**ImpulsaMente** - Sistema de Gestión de Servicios de Tutoría y Terapia
