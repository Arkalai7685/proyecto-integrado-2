#!/usr/bin/env python
"""
Script de pruebas completas del sistema ImpulsaMente
Verifica que todos los componentes funcionen correctamente
"""
import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ImpulsaMente_project.settings')
django.setup()

from django.contrib.auth.models import User, Group
from servicios.models import Service, Price, Customer, Order, ClientAssignment, Session, FileUpload
from cuentas.models import UserProfile


def print_header(text):
    """Imprimir encabezado decorado"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)


def print_success(text):
    """Imprimir mensaje de éxito"""
    print(f"✓ {text}")


def print_error(text):
    """Imprimir mensaje de error"""
    print(f"✗ {text}")


def print_info(text):
    """Imprimir mensaje informativo"""
    print(f"ℹ {text}")


def test_models():
    """Probar que los modelos están correctamente configurados"""
    print_header("PROBANDO MODELOS")
    
    try:
        # Probar Service
        services = Service.objects.all()
        print_success(f"Servicios encontrados: {services.count()}")
        for service in services:
            print_info(f"  - {service.name} ({service.slug})")
        
        # Probar Price
        prices = Price.objects.all()
        print_success(f"Precios encontrados: {prices.count()}")
        
        # Probar Users
        users = User.objects.all()
        print_success(f"Usuarios encontrados: {users.count()}")
        
        # Probar Groups
        groups = Group.objects.all()
        print_success(f"Grupos encontrados: {groups.count()}")
        for group in groups:
            print_info(f"  - {group.name}: {group.user_set.count()} usuarios")
        
        # Probar ClientAssignments
        assignments = ClientAssignment.objects.all()
        print_success(f"Asignaciones encontradas: {assignments.count()}")
        
        # Probar Sessions
        sessions = Session.objects.all()
        print_success(f"Sesiones encontradas: {sessions.count()}")
        
        # Probar Files
        files = FileUpload.objects.all()
        print_success(f"Archivos encontrados: {files.count()}")
        
        return True
        
    except Exception as e:
        print_error(f"Error al probar modelos: {str(e)}")
        return False


def test_user_profiles():
    """Verificar que todos los usuarios tengan perfiles"""
    print_header("VERIFICANDO PERFILES DE USUARIO")
    
    users_without_profile = []
    users_with_profile = []
    
    for user in User.objects.all():
        try:
            profile = user.profile
            users_with_profile.append(user.username)
        except UserProfile.DoesNotExist:
            users_without_profile.append(user.username)
    
    if users_without_profile:
        print_error(f"Usuarios sin perfil: {len(users_without_profile)}")
        for username in users_without_profile:
            print_info(f"  - {username}")
        return False
    else:
        print_success(f"Todos los usuarios tienen perfil ({len(users_with_profile)} usuarios)")
        return True


def test_featured_prices():
    """Verificar precios destacados"""
    print_header("VERIFICANDO PRECIOS DESTACADOS")
    
    services = Service.objects.all()
    
    for service in services:
        featured_prices = service.prices.filter(is_featured=True)
        total_prices = service.prices.count()
        
        print_info(f"{service.name}:")
        print_info(f"  - Total de precios: {total_prices}")
        print_info(f"  - Precios destacados: {featured_prices.count()}")
        
        if featured_prices.count() > 0:
            for price in featured_prices:
                print_success(f"    ✓ {price.plan} - ${price.price}")
        else:
            print_error(f"    ¡Sin precios destacados!")
    
    return True


def test_client_assignments():
    """Verificar asignaciones de clientes"""
    print_header("VERIFICANDO ASIGNACIONES DE CLIENTES")
    
    # Obtener empleados (psicólogos y tutores)
    psychologists = User.objects.filter(groups__name='Psicólogo').distinct()
    tutors = User.objects.filter(groups__name='Tutor').distinct()
    
    print_info(f"Psicólogos registrados: {psychologists.count()}")
    for psy in psychologists:
        assignments = ClientAssignment.objects.filter(employee=psy, is_active=True)
        print_success(f"  - {psy.get_full_name() or psy.username}: {assignments.count()} clientes asignados")
    
    print_info(f"Tutores registrados: {tutors.count()}")
    for tutor in tutors:
        assignments = ClientAssignment.objects.filter(employee=tutor, is_active=True)
        print_success(f"  - {tutor.get_full_name() or tutor.username}: {assignments.count()} clientes asignados")
    
    return True


def test_orders_status():
    """Verificar estado de las órdenes"""
    print_header("VERIFICANDO ESTADO DE ÓRDENES")
    
    orders = Order.objects.all()
    
    if orders.count() == 0:
        print_info("No hay órdenes en el sistema")
        return True
    
    status_counts = {}
    for order in orders:
        status = order.status
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print_info(f"Total de órdenes: {orders.count()}")
    for status, count in status_counts.items():
        print_success(f"  - {status}: {count} órdenes")
    
    return True


def test_database_integrity():
    """Verificar integridad de la base de datos"""
    print_header("VERIFICANDO INTEGRIDAD DE BASE DE DATOS")
    
    issues = []
    
    # Verificar sesiones sin asignación
    orphan_sessions = Session.objects.filter(assignment__isnull=True)
    if orphan_sessions.exists():
        issues.append(f"Sesiones huérfanas (sin asignación): {orphan_sessions.count()}")
    
    # Verificar archivos sin asignación
    orphan_files = FileUpload.objects.filter(assignment__isnull=True)
    if orphan_files.exists():
        issues.append(f"Archivos huérfanos (sin asignación): {orphan_files.count()}")
    
    # Verificar precios sin servicio
    orphan_prices = Price.objects.filter(service__isnull=True)
    if orphan_prices.exists():
        issues.append(f"Precios huérfanos (sin servicio): {orphan_prices.count()}")
    
    if issues:
        print_error("Se encontraron problemas de integridad:")
        for issue in issues:
            print_info(f"  - {issue}")
        return False
    else:
        print_success("✓ Base de datos íntegra, sin problemas detectados")
        return True


def main():
    """Función principal de pruebas"""
    print("\n" + "█"*70)
    print(" "*15 + "PRUEBAS DEL SISTEMA IMPULSAMENTE")
    print("█"*70)
    
    results = []
    
    # Ejecutar todas las pruebas
    results.append(("Modelos", test_models()))
    results.append(("Perfiles de Usuario", test_user_profiles()))
    results.append(("Precios Destacados", test_featured_prices()))
    results.append(("Asignaciones de Clientes", test_client_assignments()))
    results.append(("Estado de Órdenes", test_orders_status()))
    results.append(("Integridad de Base de Datos", test_database_integrity()))
    
    # Resumen final
    print_header("RESUMEN DE PRUEBAS")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        if result:
            print_success(f"{test_name}: PASÓ")
        else:
            print_error(f"{test_name}: FALLÓ")
    
    print("\n" + "="*70)
    print(f"  RESULTADO: {passed}/{total} pruebas pasaron")
    print("="*70 + "\n")
    
    if passed == total:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON! El sistema está funcionando correctamente.")
        return 0
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa los detalles arriba.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
