#  ImpulsaMente - Sistema de Gestión de Apoyo Estudiantil

[![Django](https://img.shields.io/badge/Django-3.1.12-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)

> Plataforma web integral para la gestión de servicios de apoyo académico y psicológico para estudiantes.

---

##  Descripción

**ImpulsaMente** conecta a estudiantes con profesionales de apoyo educativo (psicólogos y tutores) mediante una plataforma web moderna que facilita:

-  Gestión de sesiones y citas
-  Seguimiento del progreso estudiantil
-  Intercambio de archivos educativos
-  Sistema de chat en tiempo real
-  Auditoría y reportes completos

---

##  Inicio Rápido

### Requisitos Previos
- Python 3.8+
- MySQL
- pip

### Instalación Rápida

```powershell
# 1. Activar entorno virtual
.\.venv\Scripts\Activate.ps1

# 2. Instalar dependencias (si es necesario)
pip install -r requirements.txt

# 3. Iniciar servidor
python manage.py runserver
```

### Acceso
- **URL:** http://127.0.0.1:8000/
- **Admin:** http://127.0.0.1:8000/admin/dashboard/

---

##  Usuarios del Sistema

**Consulta `DOCUMENTACION_COMPLETA.md` para ver las credenciales de acceso completas**

Roles disponibles:
-  **Administrador** - Gestión completa del sistema
-  **Psicólogo** - Gestión de clientes de terapia
-  **Tutor** - Gestión de estudiantes de tutoría
-  **Cliente** - Acceso a servicios y seguimiento

---

##  Estructura del Proyecto

```
proyecto-integrado-main/
 manage.py                    # Comando principal Django
 requirements.txt             # Dependencias Python
 README.md                    # Este archivo
 DOCUMENTACION_COMPLETA.md    # Documentación detallada
 ImpulsaMente_project/        # Configuración del proyecto
 cuentas/                     # App de autenticación
 servicios/                   # App principal de servicios
 assets/                      # Archivos estáticos (CSS, JS, imágenes)
 templates/                   # Plantillas HTML
 media/                       # Archivos subidos por usuarios
 logs/                        # Logs del sistema
 sql/                         # Scripts SQL
```

---

##  Características Principales

### Para Administradores
- Gestión completa de servicios, precios y usuarios
- Asignación de clientes a empleados
- Generación automática de sesiones
- Panel de auditoría completo

### Para Psicólogos/Tutores
- Vista de clientes asignados con métricas
- Gestión de sesiones y progreso
- Sistema de chat con clientes
- Subida/descarga de archivos
- Auditoría por estudiante

### Para Clientes
- Solicitud de servicios
- Seguimiento de sesiones
- Chat con profesionales asignados
- Gestión de archivos
- Perfil editable

---

##  Tecnologías Utilizadas

- **Backend:** Django 3.1.12, Python 3.8+
- **Base de Datos:** MySQL
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
- **Estilos:** CSS personalizado con gradientes y animaciones
- **Arquitectura:** MVT (Model-View-Template)

---

##  Documentación Completa

Para información detallada sobre:
-  Credenciales de acceso
-  Funcionalidades por rol
-  Guía de instalación completa
-  Arquitectura del sistema
-  Flujos de trabajo
-  API endpoints

**Consulta:** [`DOCUMENTACION_COMPLETA.md`](DOCUMENTACION_COMPLETA.md)

---

##  Soporte

Para problemas o consultas:
1. Revisar la documentación completa
2. Verificar los logs en la carpeta `logs/`
3. Consultar la consola del navegador (F12) para errores frontend

---

##  Licencia

Este proyecto es parte de un trabajo académico.

---

**ImpulsaMente** - Impulsando el éxito estudiantil 
