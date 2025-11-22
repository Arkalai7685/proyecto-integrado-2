# 🔒 Política de Contraseñas Seguras - ImpulsaMente

## Requisitos de Contraseña

Para garantizar la seguridad de tu cuenta, todas las contraseñas deben cumplir con los siguientes requisitos:

### ✅ Requisitos Obligatorios

1. **Longitud Mínima**: Al menos 8 caracteres
2. **Letra Mayúscula**: Al menos una letra mayúscula (A-Z)
3. **Letra Minúscula**: Al menos una letra minúscula (a-z)
4. **Número**: Al menos un dígito (0-9)
5. **Caracter Especial**: Al menos un caracter especial: `!@#$%^&*(),.?":{}|<>_-+=[]\/;~\``

### ❌ Ejemplos de Contraseñas INSEGURAS

- `cliente123` - Falta mayúscula y caracter especial
- `CLIENTE123` - Falta minúscula y caracter especial
- `Cliente` - Muy corta, falta número y caracter especial
- `cliente123!` - Falta mayúscula
- `Cliente!` - Muy corta, falta número

### ✅ Ejemplos de Contraseñas SEGURAS

- `Cliente123!` ✓
- `Empleado@2025` ✓
- `Psicologo#123` ✓
- `Tutor$2025` ✓
- `MiClave2025!` ✓
- `Segura#Pass99` ✓

## 📋 Validación en Tiempo Real

Cuando crees tu cuenta en ImpulsaMente, verás indicadores visuales que te mostrarán si tu contraseña cumple con cada requisito:

- ○ Requisito no cumplido (rojo)
- ✓ Requisito cumplido (verde)

## 🔑 Usuarios de Prueba Actualizados

Los usuarios de prueba ahora tienen contraseñas seguras:

| Usuario | Contraseña | Rol |
|---------|------------|-----|
| `cliente1` | `Cliente123!` | Cliente |
| `empleado1` | `Empleado@2025` | Empleado/Staff |
| `psicologo1` | `Psicologo#123` | Psicólogo |
| `tutor1` | `Tutor$2025` | Tutor |

## 🛠️ Para Desarrolladores

### Actualizar Usuarios Existentes

Si necesitas actualizar las contraseñas de los usuarios existentes a contraseñas seguras, ejecuta:

```bash
python crear_usuarios.py
```

Este script:
1. Valida que las contraseñas cumplan con los requisitos de seguridad
2. Advierte si una contraseña es insegura
3. Solicita confirmación antes de crear usuarios con contraseñas débiles
4. Actualiza las contraseñas usando hash PBKDF2 de Django

### Validación Programática

El formulario de registro (`cuentas/forms.py`) incluye la clase `SecurePasswordValidator` que valida automáticamente todas las contraseñas nuevas.

```python
from cuentas.forms import SecurePasswordValidator

# Validar una contraseña
errores = SecurePasswordValidator.validate("micontraseña")
if errores:
    print("Contraseña insegura:")
    for error in errores:
        print(f"  - {error}")
```

## 🚀 Implementación

### Backend (Django)

- **Formulario**: `cuentas/forms.py` - `SecureUserCreationForm`
- **Validador**: `cuentas/forms.py` - `SecurePasswordValidator`
- **Vista**: `cuentas/views.py` - `register_view`

### Frontend

- **Plantilla**: `templates/register.html`
- **Validación en Tiempo Real**: JavaScript que actualiza indicadores visuales mientras el usuario escribe

## 💡 Buenas Prácticas

1. **No reutilices contraseñas** entre diferentes servicios
2. **Usa un gestor de contraseñas** para recordar tus contraseñas seguras
3. **Cambia tu contraseña regularmente** (cada 3-6 meses)
4. **No compartas tu contraseña** con nadie
5. **Cierra sesión** cuando uses computadoras públicas

## 🔐 Seguridad Adicional

- Todas las contraseñas se almacenan usando **PBKDF2** con hash SHA256
- Django genera automáticamente un **salt único** para cada contraseña
- Las contraseñas **nunca se almacenan en texto plano**
- Los intentos de login son validados contra el hash almacenado

## 📞 Soporte

Si tienes problemas para crear una contraseña segura o necesitas restablecer tu contraseña, contacta a soporte en:
- Email: soporte@impulsamente.com
- Teléfono: +56 9 XXXX XXXX

---

**Última actualización**: Noviembre 2025  
**Versión**: 1.0
