"""Test para verificar el estado de sesión"""
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session as DjangoSession
from django.utils import timezone
import datetime

print("=" * 60)
print("VERIFICANDO SESIONES ACTIVAS")
print("=" * 60)

# Ver todas las sesiones activas
active_sessions = DjangoSession.objects.filter(expire_date__gte=timezone.now())
print(f"Total sesiones activas: {active_sessions.count()}")
print()

for session in active_sessions:
    session_data = session.get_decoded()
    user_id = session_data.get('_auth_user_id')
    if user_id:
        try:
            user = User.objects.get(id=user_id)
            print(f"Usuario en sesión: {user.username}")
            print(f"  ID de sesión: {session.session_key[:20]}...")
            print(f"  Expira: {session.expire_date}")
            print()
        except User.DoesNotExist:
            print(f"Sesión sin usuario válido")

print("=" * 60)
print("\nINSTRUCCIONES:")
print("Si NO ves 'psicologo1' en la lista, necesitas:")
print("1. Ir a http://127.0.0.1:8000/login/")
print("2. Iniciar sesión con usuario: psicologo1, contraseña: Admin123!")
print("3. Luego ir a http://127.0.0.1:8000/psicologo/dashboard/")
print("=" * 60)
