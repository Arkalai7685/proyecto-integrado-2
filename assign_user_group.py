"""
Script para asignar un usuario a un grupo
Uso desde shell de Django:
    from assign_user_group import asignar_grupo
    asignar_grupo('nombre_usuario', 'Psicólogo')
"""

from django.contrib.auth.models import User, Group

def asignar_grupo(username, nombre_grupo):
    """Asignar un usuario a un grupo"""
    try:
        user = User.objects.get(username=username)
        grupo = Group.objects.get(name=nombre_grupo)
        user.groups.add(grupo)
        print(f'✓ Usuario "{username}" agregado al grupo "{nombre_grupo}"')
        print(f'  Grupos actuales: {", ".join([g.name for g in user.groups.all()])}')
    except User.DoesNotExist:
        print(f'✗ Usuario "{username}" no encontrado')
    except Group.DoesNotExist:
        print(f'✗ Grupo "{nombre_grupo}" no encontrado')
        print(f'  Grupos disponibles: {", ".join([g.name for g in Group.objects.all()])}')

def listar_usuarios():
    """Listar todos los usuarios y sus grupos"""
    print('\n=== Usuarios y sus grupos ===')
    for user in User.objects.all():
        grupos = ', '.join([g.name for g in user.groups.all()]) or 'Sin grupo'
        tipo = 'Staff' if user.is_staff else 'Normal'
        print(f'- {user.username} ({tipo}): {grupos}')

# Si se ejecuta directamente, mostrar ayuda
if __name__ == '__main__':
    print('=== Asignación de Grupos ===')
    print('\nGrupos disponibles:')
    for g in Group.objects.all():
        print(f'  - {g.name}')
    print('\nEjemplos de uso:')
    print('  asignar_grupo("usuario1", "Psicólogo")')
    print('  asignar_grupo("usuario2", "Tutor")')
    print('  listar_usuarios()')
    print('\n')
    listar_usuarios()
