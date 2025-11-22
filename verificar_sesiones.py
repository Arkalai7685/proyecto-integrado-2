"""Script para verificar el estado de las sesiones de un cliente"""
from servicios.models import Session, ClientAssignment
from django.contrib.auth.models import User

client = User.objects.get(id=13)  # Diego Ramírez
sessions = Session.objects.filter(assignment__client=client)

print(f'Cliente: {client.username} ({client.get_full_name()})')
print(f'Total sesiones: {sessions.count()}')
print(f'Completadas: {sessions.filter(status="completed").count()}')
print(f'Programadas: {sessions.filter(status="scheduled").count()}')
print(f'Confirmadas: {sessions.filter(status="confirmed").count()}')
print('\nDetalle de sesiones:')
for s in sessions.order_by('scheduled_date'):
    print(f'  - ID {s.id}: {s.status:12s} - {s.scheduled_date} - Asignación: {s.assignment.service.name}')

# Calcular progreso
total = sessions.count()
completed = sessions.filter(status='completed').count()
progress = (completed / total * 100) if total > 0 else 0
print(f'\nProgreso calculado: {completed}/{total} = {progress:.1f}%')
