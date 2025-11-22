# ⚡ Inicio Rápido - ImpulsaMente

## 🚀 Configuración en 5 Pasos

### 1️⃣ Clonar y Configurar Entorno
```powershell
cd d:\proyecto_integrado\proyecto-integrado-main\proyecto-integrado-main
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2️⃣ Configurar Base de Datos
Edita `.env` con tus credenciales de MySQL:
```env
DB_NAME=mente_libre
DB_USER=root
DB_PASSWORD=tu_password
DB_HOST=127.0.0.1
DB_PORT=3306
```

### 3️⃣ Crear Base de Datos (MySQL)
```powershell
mysql -u root -p -e "CREATE DATABASE mente_libre CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

### 4️⃣ Migrar Base de Datos
```powershell
python manage.py migrate
python manage.py load_services
python manage.py createsuperuser
```

### 5️⃣ Iniciar Servidor
```powershell
python manage.py runserver
```

## 🌐 URLs Principales

- **Sitio Web**: http://127.0.0.1:8000/
- **Admin**: http://127.0.0.1:8000/admin/
- **Login**: http://127.0.0.1:8000/cuentas/login/
- **Tutoría**: http://127.0.0.1:8000/tutoria/
- **Terapia**: http://127.0.0.1:8000/terapia/

## 📋 Comandos Útiles

```powershell
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Cargar datos iniciales
python manage.py load_services

# Crear superusuario
python manage.py createsuperuser

# Shell interactivo
python manage.py shell

# Ejecutar tests
python manage.py test
```

## 🔧 Solución Rápida de Problemas

### Error de MySQL
```powershell
# Verifica que MySQL esté corriendo
Get-Service MySQL*

# Si no está corriendo
Start-Service MySQL80
```

### Error "Module not found"
```powershell
pip install -r requirements.txt
```

### Error de permisos PowerShell
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 📚 Documentación Completa

- Ver `DJANGO_README.md` para documentación detallada
- Ver `MIGRACION_RESUMEN.md` para resumen de la migración

---

**¿Necesitas ayuda?** Revisa la documentación completa o contacta al equipo de desarrollo.
