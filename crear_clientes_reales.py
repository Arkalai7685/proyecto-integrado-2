"""
Script para crear clientes reales en el sistema
Ejecutar con: python crear_clientes_reales.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ImpulsaMente_project.settings')
django.setup()

from django.contrib.auth.models import User, Group


def crear_clientes_reales():
    """Crear clientes reales para el sistema"""
    print('=' * 60)
    print('CREANDO CLIENTES REALES EN EL SISTEMA')
    print('=' * 60)
    
    # Obtener o crear el grupo Cliente
    grupo_cliente, created = Group.objects.get_or_create(name='Cliente')
    if created:
        print('✓ Grupo "Cliente" creado')
    else:
        print('✓ Grupo "Cliente" ya existe')
    
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
        {
            'username': 'carlos.rodriguez',
            'email': 'carlos.rodriguez@estudiante.com',
            'first_name': 'Carlos',
            'last_name': 'Rodríguez',
            'password': 'Carlos@2025!'
        },
        {
            'username': 'laura.fernandez',
            'email': 'laura.fernandez@estudiante.com',
            'first_name': 'Laura',
            'last_name': 'Fernández',
            'password': 'Laura@2025!'
        },
        {
            'username': 'pedro.sanchez',
            'email': 'pedro.sanchez@estudiante.com',
            'first_name': 'Pedro',
            'last_name': 'Sánchez',
            'password': 'Pedro@2025!'
        },
        {
            'username': 'sofia.torres',
            'email': 'sofia.torres@estudiante.com',
            'first_name': 'Sofía',
            'last_name': 'Torres',
            'password': 'Sofia@2025!'
        },
        {
            'username': 'diego.ramirez',
            'email': 'diego.ramirez@estudiante.com',
            'first_name': 'Diego',
            'last_name': 'Ramírez',
            'password': 'Diego@2025!'
        },
    ]
    
    print(f'\n🔄 Intentando crear {len(clientes)} clientes...\n')
    
    creados = 0
    ya_existen = 0
    
    for cliente_data in clientes:
        try:
            # Verificar si el usuario ya existe
            if User.objects.filter(username=cliente_data['username']).exists():
                print(f'⚠ Cliente ya existe: {cliente_data["username"]} - {cliente_data["first_name"]} {cliente_data["last_name"]}')
                ya_existen += 1
                continue
            
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
            
            print(f'✓ Cliente creado: {user.username} - {user.first_name} {user.last_name} ({user.email})')
            creados += 1
            
        except Exception as e:
            print(f'❌ Error creando {cliente_data["username"]}: {str(e)}')
    
    # Resumen
    print('\n' + '=' * 60)
    print('✅ PROCESO COMPLETADO')
    print('=' * 60)
    
    total_clientes = User.objects.filter(groups__name='Cliente').count()
    
    print(f'\n📊 Resumen:')
    print(f'   • Clientes nuevos creados: {creados}')
    print(f'   • Clientes que ya existían: {ya_existen}')
    print(f'   • Total de clientes en el sistema: {total_clientes}')
    
    # Listar todos los clientes
    print(f'\n👥 Lista de todos los clientes:')
    clientes_sistema = User.objects.filter(groups__name='Cliente').order_by('username')
    for idx, cliente in enumerate(clientes_sistema, 1):
        nombre_completo = f"{cliente.first_name} {cliente.last_name}".strip() or cliente.username
        print(f'   {idx}. {cliente.username} - {nombre_completo} ({cliente.email})')
    
    print('\n💡 Próximo paso:')
    print('   Ejecuta: python crear_datos_admin.py')
    print('   Para crear asignaciones, sesiones y logs para todos los clientes')


if __name__ == '__main__':
    crear_clientes_reales()
