"""Script para verificar los clientes asignados al psicólogo"""
from servicios.models import ClientAssignment
from django.contrib.auth.models import User

# Verificar psicologo1
psicologo = User.objects.get(username='psicologo1')
assigned_clients = ClientAssignment.objects.filter(
    employee=psicologo,
    is_active=True
).select_related('client', 'service')

print("=" * 60)
print("VERIFICANDO DATOS PARA PSICOLOGO1")
print("=" * 60)
print(f"Total asignaciones activas: {assigned_clients.count()}")
print()

for assignment in assigned_clients:
    print(f"Cliente: {assignment.client.username} ({assignment.client.get_full_name()})")
    print(f"  Servicio: {assignment.service.name}")
    print(f"  Asignado el: {assignment.assigned_at}")
    print(f"  Activo: {assignment.is_active}")
    print()

print("=" * 60)
