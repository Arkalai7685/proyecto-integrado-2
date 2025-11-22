"""
Script para crear usuarios de prueba en Django con contraseñas seguras
Ejecutar con: python crear_usuarios.py
"""

import os
import django
import re

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ImpulsaMente_project.settings')
django.setup()

from django.contrib.auth.models import User, Group


def validar_contrasena_segura(password):
    """
    Valida que la contraseña cumpla con los requisitos de seguridad:
    - Mínimo 8 caracteres
    - Al menos una letra mayúscula
    - Al menos una letra minúscula
    - Al menos un número
    - Al menos un caracter especial
    """
    errores = []
    
    if len(password) < 8:
        errores.append("❌ La contraseña debe tener al menos 8 caracteres.")
    
    if not re.search(r'[A-Z]', password):
        errores.append("❌ La contraseña debe contener al menos una letra mayúscula.")
    
    if not re.search(r'[a-z]', password):
        errores.append("❌ La contraseña debe contener al menos una letra minúscula.")
    
    if not re.search(r'\d', password):
        errores.append("❌ La contraseña debe contener al menos un número.")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/;~`]', password):
        errores.append("❌ La contraseña debe contener al menos un caracter especial (!@#$%^&*(),.?\":{}|<>_-+=[]\\\/;~`).")
    
    return errores


def crear_usuario(username, password, email='', es_staff=False, grupo=None):
    """Crear un usuario con contraseña hasheada correctamente y validación de seguridad"""
    
    # Validar contraseña
    errores = validar_contrasena_segura(password)
    if errores:
        print(f'\n⚠ ADVERTENCIA: La contraseña para "{username}" NO es segura:')
        for error in errores:
            print(f'  {error}')
        print('  💡 Ejemplo de contraseña segura: Cliente123! o Empleado@2025')
        respuesta = input(f'  ¿Deseas continuar con esta contraseña insegura? (s/n): ')
        if respuesta.lower() != 's':
            print(f'  ⏭ Usuario "{username}" omitido\n')
            return None
    
    # Verificar si el usuario ya existe
    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
        print(f'⚠ Usuario "{username}" ya existe, actualizando...')
        # Actualizar contraseña
        user.set_password(password)
        user.is_staff = es_staff
        user.email = email if email else user.email
        user.save()
        print(f'✓ Usuario "{username}" actualizado')
    else:
        # Crear nuevo usuario
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            is_staff=es_staff
        )
        print(f'✓ Usuario "{username}" creado exitosamente')
    
    # Asignar grupo si se especifica
    if grupo:
        try:
            group = Group.objects.get(name=grupo)
            user.groups.clear()  # Limpiar grupos anteriores
            user.groups.add(group)
            print(f'  → Agregado al grupo "{grupo}"')
        except Group.DoesNotExist:
            print(f'  ⚠ Grupo "{grupo}" no existe')
    
    return user


# Crear usuarios de prueba con contraseñas seguras
print('=== Creando usuarios de prueba con contraseñas seguras ===\n')
print('📋 Requisitos de contraseña:')
print('   • Mínimo 8 caracteres')
print('   • Al menos una letra mayúscula (A-Z)')
print('   • Al menos una letra minúscula (a-z)')
print('   • Al menos un número (0-9)')
print('   • Al menos un caracter especial (!@#$%^&*...)\n')

# Cliente - Contraseña segura sugerida
crear_usuario(
    username='cliente1',
    password='Cliente123!',  # Contraseña SEGURA
    email='cliente1@example.com',
    es_staff=False,
    grupo='Cliente'
)

# Empleado/Staff - Contraseña segura sugerida
crear_usuario(
    username='empleado1',
    password='Empleado@2025',  # Contraseña SEGURA
    email='empleado1@example.com',
    es_staff=True
)

# Psicólogo - Contraseña segura sugerida
crear_usuario(
    username='psicologo1',
    password='Psicologo#123',  # Contraseña SEGURA
    email='psicologo1@example.com',
    es_staff=False,
    grupo='Psicólogo'
)

# Tutor - Contraseña segura sugerida
crear_usuario(
    username='tutor1',
    password='Tutor$2025',  # Contraseña SEGURA
    email='tutor1@example.com',
    es_staff=False,
    grupo='Tutor'
)

print('\n=== Resumen de usuarios ===')
for user in User.objects.all():
    grupos = ', '.join([g.name for g in user.groups.all()]) or 'Sin grupo'
    tipo = 'Staff' if user.is_staff else 'Usuario'
    print(f'Usuario: {user.username:<15} | Tipo: {tipo:<10} | Grupos: {grupos}')

print('\n=== 🔑 Credenciales de acceso (CONTRASEÑAS SEGURAS) ===')
print('Cliente:    usuario=cliente1    | contraseña=Cliente123!')
print('Empleado:   usuario=empleado1   | contraseña=Empleado@2025')
print('Psicólogo:  usuario=psicologo1  | contraseña=Psicologo#123')
print('Tutor:      usuario=tutor1      | contraseña=Tutor$2025')
print('\n💡 Todas las contraseñas cumplen con los requisitos de seguridad.')

