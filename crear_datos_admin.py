"""
Script para crear datos de prueba para el sistema de administración
Ejecutar con: python crear_datos_admin.py
"""

import os
import django
from datetime import datetime, timedelta
from random import randint, choice

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ImpulsaMente_project.settings')
django.setup()

from django.contrib.auth.models import User
from django.db.models import Q
from servicios.models import Service, ClientAssignment, Session, FileUpload, AuditLog


def crear_asignaciones():
    """Crear asignaciones de clientes a empleados"""
    print('\n=== Creando Asignaciones Cliente-Empleado ===\n')
    
    try:
        # Obtener TODOS los clientes reales del sistema
        clientes = User.objects.filter(groups__name='Cliente')
        
        if not clientes.exists():
            print('❌ No hay clientes en el sistema. Por favor crea clientes primero.')
            return []
        
        print(f'📋 Clientes encontrados: {clientes.count()}')
        for cliente in clientes:
            nombre_completo = f"{cliente.first_name} {cliente.last_name}".strip() or cliente.username
            print(f'   • {cliente.username} - {nombre_completo} ({cliente.email})')
        
        # Obtener empleados
        tutores = User.objects.filter(groups__name='Tutor')
        psicologos = User.objects.filter(groups__name='Psicologo')
        
        if not tutores.exists() and not psicologos.exists():
            print('❌ No hay tutores ni psicólogos en el sistema.')
            return []
        
        print(f'\n👥 Empleados disponibles:')
        print(f'   • Tutores: {tutores.count()}')
        print(f'   • Psicólogos: {psicologos.count()}')
        
        # Obtener servicios
        tutoria = Service.objects.filter(slug='tutoria').first()
        terapia = Service.objects.filter(slug='terapia').first()
        
        if not tutoria or not terapia:
            print('❌ Los servicios no están configurados correctamente.')
            return []
        
        created_assignments = []
        
        # Crear asignaciones para CADA cliente real
        for cliente in clientes:
            asignaciones_cliente = []
            
            # Asignar un tutor si hay tutores disponibles
            if tutores.exists():
                tutor = choice(list(tutores))
                asignaciones_cliente.append({
                    'client': cliente,
                    'employee': tutor,
                    'service': tutoria,
                    'notes': f'Tutoría académica para {cliente.username} - Apoyo en metodología y técnicas de estudio'
                })
            
            # Asignar un psicólogo si hay psicólogos disponibles
            if psicologos.exists() and randint(0, 1):  # 50% de probabilidad
                psicologo = choice(list(psicologos))
                asignaciones_cliente.append({
                    'client': cliente,
                    'employee': psicologo,
                    'service': terapia,
                    'notes': f'Terapia psicológica para {cliente.username} - Manejo de estrés y ansiedad académica'
                })
            
            # Crear las asignaciones
            for data in asignaciones_cliente:
                assignment, created = ClientAssignment.objects.get_or_create(
                    client=data['client'],
                    employee=data['employee'],
                    service=data['service'],
                    defaults={'notes': data['notes']}
                )
                
                if created:
                    print(f'✓ Asignación creada: {assignment.client.username} → {assignment.employee.username} ({assignment.service.name})')
                    created_assignments.append(assignment)
                else:
                    print(f'⚠ Asignación ya existe: {assignment.client.username} → {assignment.employee.username}')
                    created_assignments.append(assignment)
        
        return created_assignments
        
    except Exception as e:
        print(f'❌ Error al crear asignaciones: {str(e)}')
        import traceback
        traceback.print_exc()
        return []


def crear_sesiones(assignments):
    """Crear sesiones de prueba"""
    print('\n=== Creando Sesiones ===\n')
    
    if not assignments:
        print('⚠ No hay asignaciones disponibles')
        return []
    
    created_sessions = []
    now = datetime.now()
    
    # Crear 5 sesiones para cada asignación
    for assignment in assignments:
        for i in range(5):
            # Algunas sesiones en el pasado, otras en el futuro
            days_offset = randint(-30, 30)
            hour = randint(9, 17)
            
            fecha_hora = now + timedelta(days=days_offset, hours=hour-now.hour, minutes=0, seconds=0)
            
            # Estado basado en la fecha
            if days_offset < -2:
                estado = 'completed'
            elif days_offset < 0:
                estado = choice(['completed', 'cancelled', 'no_show'])
            elif days_offset == 0:
                estado = 'confirmed'
            else:
                estado = choice(['scheduled', 'confirmed'])
            
            session, created = Session.objects.get_or_create(
                assignment=assignment,
                scheduled_date=fecha_hora,
                defaults={
                    'duration_minutes': choice([45, 60, 90]),
                    'status': estado,
                    'notes': f'Sesión #{i+1} - {assignment.service.name}',
                }
            )
            
            if created:
                print(f'✓ Sesión creada: {assignment.client.username} - {fecha_hora.strftime("%Y-%m-%d %H:%M")} ({estado})')
                created_sessions.append(session)
            else:
                print(f'⚠ Sesión ya existe: {assignment.client.username} - {fecha_hora.strftime("%Y-%m-%d %H:%M")}')
    
    return created_sessions


def crear_logs_auditoria():
    """Crear registros de auditoría de ejemplo"""
    print('\n=== Creando Registros de Auditoría ===\n')
    
    try:
        # Obtener TODOS los clientes reales
        clientes = list(User.objects.filter(groups__name='Cliente'))
        
        # Obtener empleados reales
        empleados = list(User.objects.filter(Q(groups__name='Tutor') | Q(groups__name='Psicologo')))
        
        # Obtener admin
        admin = User.objects.filter(is_superuser=True).first()
        
        if not admin:
            admin = User.objects.filter(is_staff=True).first()
        
        logs = []
        
        # Crear logs para cada cliente
        for cliente in clientes:
            logs.extend([
                {
                    'user': cliente,
                    'action': 'login',
                    'description': f'{cliente.username} inició sesión desde navegador web',
                    'ip_address': f'192.168.1.{randint(100, 200)}'
                },
                {
                    'user': cliente,
                    'action': 'order_created',
                    'description': f'{cliente.username} solicitó servicio - Plan {choice(["Básico", "Intermedio", "Premium"])}',
                    'ip_address': f'192.168.1.{randint(100, 200)}'
                },
            ])
            
            # Algunos clientes tienen más actividad
            if randint(0, 1):
                logs.append({
                    'user': cliente,
                    'action': 'profile_update',
                    'description': f'{cliente.username} actualizó información de perfil',
                    'ip_address': f'192.168.1.{randint(100, 200)}'
                })
        
        # Crear logs para empleados
        for empleado in empleados[:3]:  # Primeros 3 empleados
            logs.extend([
                {
                    'user': empleado,
                    'action': 'login',
                    'description': f'{empleado.username} inició sesión',
                    'ip_address': f'192.168.1.{randint(50, 99)}'
                },
                {
                    'user': empleado,
                    'action': 'session_completed',
                    'description': f'{empleado.username} completó sesión con cliente',
                    'ip_address': f'192.168.1.{randint(50, 99)}'
                },
            ])
        
        # Log del admin
        if admin:
            logs.append({
                'user': admin,
                'action': 'login',
                'description': f'{admin.username} (Admin) inició sesión en panel de administración',
                'ip_address': '192.168.1.1'
            })
        
        # Crear los logs en la base de datos
        for log_data in logs:
            log = AuditLog.objects.create(**log_data)
            print(f'✓ Log creado: {log.user.username} - {log.get_action_display()}')
        
        print(f'\n✓ {len(logs)} registros de auditoría creados')
        
    except Exception as e:
        print(f'❌ Error al crear logs: {str(e)}')
        import traceback
        traceback.print_exc()


def main():
    print('=' * 60)
    print('CREANDO DATOS DE PRUEBA PARA PANEL DE ADMINISTRADOR')
    print('=' * 60)
    
    # Crear asignaciones
    assignments = crear_asignaciones()
    
    # Crear sesiones
    if assignments:
        crear_sesiones(assignments)
    
    # Crear logs de auditoría
    crear_logs_auditoria()
    
    print('\n' + '=' * 60)
    print('✅ DATOS DE PRUEBA CREADOS EXITOSAMENTE')
    print('=' * 60)
    
    print('\n📋 Resumen:')
    print(f'   • Asignaciones: {ClientAssignment.objects.count()}')
    print(f'   • Sesiones: {Session.objects.count()}')
    print(f'   • Logs de Auditoría: {AuditLog.objects.count()}')
    
    print('\n🔑 Para acceder al panel de administrador:')
    print('   1. Inicia sesión con: Admin / admin123')
    print('   2. Accede a: http://localhost:8000/admin/dashboard/')
    print('   3. O haz clic en "🛠️ Panel Administrador" en el menú de usuario')


if __name__ == '__main__':
    main()
