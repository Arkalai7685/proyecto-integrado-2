"""Test para verificar qué está retornando la vista del psicólogo"""
from django.contrib.auth.models import User
from servicios.models import ClientAssignment, Session
from servicios.views import psicologo_dashboard
from django.test import RequestFactory

# Crear un request falso
factory = RequestFactory()
request = factory.get('/psicologo-dashboard/')

# Obtener el usuario psicólogo
psicologo = User.objects.get(username='psicologo1')
request.user = psicologo

# Simular la lógica de la vista
assigned_clients = ClientAssignment.objects.filter(
    employee=request.user,
    is_active=True
).select_related('client', 'service')

print("=" * 60)
print("TEST DE VISTA PSICOLOGO_DASHBOARD")
print("=" * 60)
print(f"Usuario: {request.user.username}")
print(f"Clientes asignados encontrados: {assigned_clients.count()}")
print()

# Calcular estadísticas para cada cliente
clients_data = []
for assignment in assigned_clients:
    all_sessions = Session.objects.filter(assignment__client=assignment.client)
    total_sessions = all_sessions.count()
    completed_sessions = all_sessions.filter(status='completed').count()
    progress = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
    
    client_dict = {
        'assignment': assignment,
        'client': assignment.client,
        'service': assignment.service,
        'total_sessions': total_sessions,
        'completed_sessions': completed_sessions,
        'progress': round(progress, 1)
    }
    clients_data.append(client_dict)
    
    print(f"Cliente: {assignment.client.username}")
    print(f"  Nombre: {assignment.client.get_full_name()}")
    print(f"  Servicio: {assignment.service.name}")
    print(f"  Total sesiones: {total_sessions}")
    print(f"  Sesiones completadas: {completed_sessions}")
    print(f"  Progreso: {round(progress, 1)}%")
    print()

print(f"Total clients_data para el template: {len(clients_data)}")
print("=" * 60)
