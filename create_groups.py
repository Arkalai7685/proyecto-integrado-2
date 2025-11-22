"""
Script para crear grupos de usuarios en Django
Ejecutar con: python manage.py shell < create_groups.py
O desde el shell de Django: exec(open('create_groups.py').read())
"""

from django.contrib.auth.models import Group

# Crear grupos si no existen
grupos = ['Psicólogo', 'Tutor', 'Cliente']

for nombre_grupo in grupos:
    grupo, created = Group.objects.get_or_create(name=nombre_grupo)
    if created:
        print(f'✓ Grupo "{nombre_grupo}" creado exitosamente')
    else:
        print(f'• Grupo "{nombre_grupo}" ya existe')

print('\n=== Grupos disponibles ===')
for grupo in Group.objects.all():
    print(f'- {grupo.name}')
