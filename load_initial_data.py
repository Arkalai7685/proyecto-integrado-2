"""
Script para cargar datos iniciales en la base de datos Django
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ImpulsaMente_project.settings')
django.setup()

from servicios.models import Service, Price

def load_initial_data():
    """Carga servicios y precios iniciales"""
    
    print("=== Cargando datos iniciales ===\n")
    
    # Crear servicio de Tutoría
    tutoria, created = Service.objects.get_or_create(
        slug='tutoria',
        defaults={
            'name': 'Tutoría',
            'description': 'Apoyo académico y acompañamiento en tesis y estudios'
        }
    )
    
    if created:
        print(f"✓ Servicio creado: {tutoria.name}")
    else:
        print(f"  El servicio {tutoria.name} ya existe")
    
    # Crear o actualizar planes de Tutoría
    planes_tutoria = [
        {
            'plan': 'Sesión Puntual',
            'price': 12000.00,
            'description': '60 minutos de orientación puntual sobre dudas concretas (metodología, estructura, referencias).'
        },
        {
            'plan': 'Paquete 6 sesiones',
            'price': 65000.00,
            'description': '6 sesiones programadas de 60 minutos c/u para seguimiento continuo.'
        },
        {
            'plan': 'Plan Completo',
            'price': 120000.00,
            'description': '12 sesiones para acompañamiento integral desde inicio hasta entrega final.'
        }
    ]
    
    for plan_data in planes_tutoria:
        plan, plan_created = Price.objects.get_or_create(
            service=tutoria,
            plan=plan_data['plan'],
            defaults={
                'price': plan_data['price'],
                'currency': 'CLP',
                'description': plan_data['description']
            }
        )
        if plan_created:
            print(f"  ✓ Plan creado: {plan.plan} - ${plan.price:,.0f} COP")
        else:
            print(f"  • Plan ya existe: {plan.plan}")
    
    # Crear servicio de Terapia
    terapia, created = Service.objects.get_or_create(
        slug='terapia',
        defaults={
            'name': 'Terapia',
            'description': 'Atención psicológica individual y grupal'
        }
    )
    
    if created:
        print(f"✓ Servicio creado: {terapia.name}")
    else:
        print(f"  El servicio {terapia.name} ya existe")
    
    # Crear o actualizar planes de Terapia
    planes_terapia = [
        {
            'plan': 'Consulta Inicial',
            'price': 15000.00,
            'description': '50 minutos: evaluación psicológica y plan de tratamiento personalizado.'
        },
        {
            'plan': 'Paquete 4 sesiones',
            'price': 55000.00,
            'description': '4 sesiones de 50 minutos para intervención breve en estrés, ansiedad o duelo.'
        },
        {
            'plan': 'Acompañamiento Semestral',
            'price': 200000.00,
            'description': '12 sesiones distribuidas en 6 meses para procesos terapéuticos profundos.'
        }
    ]
    
    for plan_data in planes_terapia:
        plan, plan_created = Price.objects.get_or_create(
            service=terapia,
            plan=plan_data['plan'],
            defaults={
                'price': plan_data['price'],
                'currency': 'CLP',
                'description': plan_data['description']
            }
        )
        if plan_created:
            print(f"  ✓ Plan creado: {plan.plan} - ${plan.price:,.0f} COP")
        else:
            print(f"  • Plan ya existe: {plan.plan}")
    
    # Crear servicio Plan Estudiante
    plan_estudiante, created = Service.objects.get_or_create(
        slug='plan-estudiante',
        defaults={
            'name': 'Plan Estudiante',
            'description': 'Planes combinados de tutoría y terapia para estudiantes'
        }
    )
    
    if created:
        print(f"✓ Servicio creado: {plan_estudiante.name}")
    else:
        print(f"  El servicio {plan_estudiante.name} ya existe")
    
    # Crear o actualizar planes de Plan Estudiante
    planes_estudiante = [
        {
            'plan': 'Plan Estudiante Básico',
            'price': 80000.00,
            'description': 'Incluye 3 sesiones de tutoría + 2 sesiones de terapia mensuales.'
        },
        {
            'plan': 'Plan Estudiante Estándar',
            'price': 150000.00,
            'description': 'Incluye 6 sesiones de tutoría + 4 sesiones de terapia mensuales.'
        },
        {
            'plan': 'Plan Estudiante Premium',
            'price': 250000.00,
            'description': 'Acceso ilimitado a tutoría y terapia durante todo el semestre académico.'
        }
    ]
    
    for plan_data in planes_estudiante:
        plan, plan_created = Price.objects.get_or_create(
            service=plan_estudiante,
            plan=plan_data['plan'],
            defaults={
                'price': plan_data['price'],
                'currency': 'CLP',
                'description': plan_data['description']
            }
        )
        if plan_created:
            print(f"  ✓ Plan creado: {plan.plan} - ${plan.price:,.0f} COP")
        else:
            print(f"  • Plan ya existe: {plan.plan}")
    
    print("\n=== Resumen ===")
    print(f"Total servicios: {Service.objects.count()}")
    print(f"Total planes: {Price.objects.count()}")
    
    print("\n=== Todos los planes disponibles ===")
    for service in Service.objects.all():
        print(f"\n{service.name}:")
        for price in service.prices.all():
            print(f"  • {price.plan}: ${price.price:,.0f} {price.currency} - {price.description}")
    
    print("\n✓ Datos iniciales cargados correctamente")

if __name__ == '__main__':
    load_initial_data()
