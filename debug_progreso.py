"""Script para verificar qué progreso se está enviando al template"""
from servicios.models import Session, ClientAssignment
from django.contrib.auth.models import User

# Verificar tutor1
tutor = User.objects.get(username='tutor1')
assigned_clients = ClientAssignment.objects.filter(
    employee=tutor,
    is_active=True
).select_related('client', 'service')

print("=" * 60)
print("VERIFICANDO DATOS PARA TUTOR1")
print("=" * 60)

for assignment in assigned_clients:
    all_sessions = Session.objects.filter(assignment__client=assignment.client)
    total_sessions = all_sessions.count()
    completed_sessions = all_sessions.filter(status='completed').count()
    progress = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
    
    print(f"\nCliente: {assignment.client.username} ({assignment.client.get_full_name()})")
    print(f"  Servicio: {assignment.service.name}")
    print(f"  Total sesiones: {total_sessions}")
    print(f"  Completadas: {completed_sessions}")
    print(f"  Progreso: {round(progress, 1)}%")
    print(f"  Progreso sin redondear: {progress}%")

print("\n" + "=" * 60)
