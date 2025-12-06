from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, FileResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User, Group
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta, time
import json

from .models import Service, Price, Customer, Order, ClientAssignment, Session, FileUpload, AuditLog


def index(request):
    """Página principal"""
    from django.core.cache import cache
    
    # Intentar obtener desde cache
    cached_data = cache.get('index_services_data')
    
    if cached_data is None:
        # Obtener servicios con sus precios destacados o los primeros 3
        tutoria_service = Service.objects.filter(slug='tutoria').first()
        terapia_service = Service.objects.filter(slug='terapia').first()
        plan_estudiante_service = Service.objects.filter(slug='plan-estudiante').first()
        
        # Para tutoría: priorizar planes destacados
        if tutoria_service:
            tutoria_prices = list(tutoria_service.prices.filter(is_featured=True)[:3])
            if not tutoria_prices:
                tutoria_prices = list(tutoria_service.prices.all()[:3])
        else:
            tutoria_prices = []
        
        # Para terapia: priorizar planes destacados
        if terapia_service:
            terapia_prices = list(terapia_service.prices.filter(is_featured=True)[:3])
            if not terapia_prices:
                terapia_prices = list(terapia_service.prices.all()[:3])
        else:
            terapia_prices = []
        
        # Para Plan Estudiante: solo planes destacados
        if plan_estudiante_service:
            plan_estudiante_prices = list(plan_estudiante_service.prices.filter(is_featured=True)[:3])
        else:
            plan_estudiante_prices = []
        
        cached_data = {
            'tutoria_service': tutoria_service,
            'terapia_service': terapia_service,
            'plan_estudiante_service': plan_estudiante_service,
            'tutoria_prices': tutoria_prices,
            'terapia_prices': terapia_prices,
            'plan_estudiante_prices': plan_estudiante_prices,
        }
        
        # Cachear por 15 minutos
        cache.set('index_services_data', cached_data, 60 * 15)
    
    context = cached_data
    return render(request, 'index.html', context)


def quienes_somos(request):
    """Página quiénes somos"""
    return render(request, 'quienes-somos.html')


def testimonios(request):
    """Página de testimonios"""
    return render(request, 'testimonios.html')


def tutoria(request):
    """Página de tutoría"""
    try:
        service = Service.objects.get(slug='tutoria')
        prices = service.prices.all()
    except Service.DoesNotExist:
        service = None
        prices = []
    return render(request, 'tutoria.html', {'service': service, 'prices': prices})


def terapia(request):
    """Página de terapia"""
    try:
        service = Service.objects.get(slug='terapia')
        prices = service.prices.all()
    except Service.DoesNotExist:
        service = None
        prices = []
    return render(request, 'terapia.html', {'service': service, 'prices': prices})


def plan_estudiante(request):
    """Página de Plan Estudiante con planes destacados o todos"""
    try:
        plan_estudiante = Service.objects.get(slug='plan-estudiante')
        # Primero intentar obtener solo planes destacados
        prices = plan_estudiante.prices.filter(is_featured=True)
        # Si no hay planes destacados, mostrar todos
        if not prices.exists():
            prices = plan_estudiante.prices.all()
    except Service.DoesNotExist:
        plan_estudiante = None
        prices = []
    
    return render(request, 'plan-estudiante.html', {
        'service': plan_estudiante,
        'prices': prices
    })


def solicitar_servicio(request):
    """Formulario de solicitud de servicio (genérico para todos los servicios)"""
    # Verificar si el usuario está autenticado
    if not request.user.is_authenticated:
        # Guardar información del servicio en la sesión
        service_slug = request.GET.get('service', '')
        plan_name = request.GET.get('plan', '')
        
        if service_slug:
            request.session['pending_service'] = service_slug
        if plan_name:
            request.session['pending_plan'] = plan_name
        
        # Agregar mensaje informativo
        messages.info(request, 'Por favor, inicia sesión o regístrate para solicitar este servicio.')
        
        # Redirigir al registro con next parameter
        from django.urls import reverse
        register_url = reverse('register')
        return redirect(f'{register_url}?next=/solicitar-servicio/')
    
    # Obtener parámetros de la URL
    service_slug = request.GET.get('service', '')
    plan_name = request.GET.get('plan', '')
    
    service = None
    price = None
    
    if service_slug:
        try:
            service = Service.objects.get(slug=service_slug)
            if plan_name:
                price = service.prices.get(plan=plan_name)
        except (Service.DoesNotExist, Price.DoesNotExist):
            pass
    
    return render(request, 'solicitar-servicio.html', {
        'service': service,
        'price': price,
        'service_slug': service_slug,
        'plan_name': plan_name
    })


@require_http_methods(["POST"])
def submit_order(request):
    """Endpoint para recibir solicitudes de servicio"""
    try:
        data = json.loads(request.body)
        
        # Validaciones
        service_slug = data.get('service', '').strip()
        plan_name = data.get('plan', '').strip()
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        message = data.get('message', '').strip()
        
        # Nuevos campos para programación
        preferred_employee_id = data.get('preferred_employee')
        start_date_str = data.get('start_date')  # Formato: "2025-11-25"
        preferred_days = data.get('preferred_days', [])  # Lista de días: ['monday', 'wednesday']
        preferred_time = data.get('preferred_time')  # Formato: "14:00"
        number_of_sessions = data.get('number_of_sessions')  # Número de sesiones del formulario

        if not all([service_slug, plan_name, name, email]):
            return JsonResponse({
                'success': False,
                'message': 'Faltan campos requeridos'
            }, status=400)
        
        # Validar número de sesiones
        if number_of_sessions:
            try:
                number_of_sessions = int(number_of_sessions)
                if number_of_sessions < 1 or number_of_sessions > 50:
                    return JsonResponse({
                        'success': False,
                        'message': 'El número de sesiones debe estar entre 1 y 50'
                    }, status=400)
            except (ValueError, TypeError):
                return JsonResponse({
                    'success': False,
                    'message': 'El número de sesiones debe ser un valor numérico válido'
                }, status=400)
        else:
            # Si no se especifica, usar valor por defecto
            number_of_sessions = 4

        # Buscar servicio y precio
        try:
            service = Service.objects.get(slug=service_slug)
            price = service.prices.get(plan=plan_name)
        except (Service.DoesNotExist, Price.DoesNotExist):
            return JsonResponse({
                'success': False,
                'message': 'Servicio o plan no encontrado'
            }, status=404)
        
        # Usar el número de sesiones configurado en el Price por el admin
        number_of_sessions = price.number_of_sessions
        
        # Buscar o crear cliente
        customer, created = Customer.objects.get_or_create(
            email=email,
            defaults={'name': name, 'phone': phone}
        )
        
        # Si el cliente ya existe, actualizar datos
        if not created:
            customer.name = name
            customer.phone = phone
            customer.save()
        
        # Validar empleado si se proporcionó
        preferred_employee = None
        if preferred_employee_id:
            try:
                preferred_employee = User.objects.get(id=preferred_employee_id)
            except User.DoesNotExist:
                pass
        
        # Convertir hora a objeto time
        preferred_time_obj = None
        if preferred_time:
            try:
                hour, minute = preferred_time.split(':')
                preferred_time_obj = time(int(hour), int(minute))
            except (ValueError, AttributeError):
                pass

        # Procesar y validar fecha de inicio
        start_date_obj = None
        if start_date_str:
            try:
                start_date_obj = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                # Validar que la fecha no sea en el pasado
                if start_date_obj < timezone.now().date():
                    return JsonResponse({
                        'success': False,
                        'message': 'La fecha de inicio no puede ser en el pasado'
                    }, status=400)
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'Formato de fecha inválido'
                }, status=400)

        # Crear orden
        order = Order.objects.create(
            customer=customer,
            service=service,
            price=price,
            notes=message,
            status='pending',
            preferred_employee=preferred_employee,
            start_date=start_date_obj,
            preferred_days=preferred_days,
            preferred_time=preferred_time_obj,
            number_of_sessions=number_of_sessions
        )

        return JsonResponse({
            'success': True,
            'order_id': order.id,
            'message': 'Solicitud enviada correctamente. En breve nos pondremos en contacto contigo.'
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'JSON inválido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error del servidor: {str(e)}'
        }, status=500)


def extract_sessions_from_plan(plan_name):
    """Extrae el número de sesiones del nombre del plan"""
    # Buscar números en el nombre del plan
    import re
    numbers = re.findall(r'\d+', plan_name)
    if numbers:
        return int(numbers[0])
    return 1  # Por defecto 1 sesión


@require_http_methods(["GET"])
def get_available_employees(request):
    """Obtener empleados disponibles para un servicio"""
    service_slug = request.GET.get('service')
    
    if not service_slug:
        return JsonResponse({
            'success': False,
            'message': 'Servicio no especificado'
        }, status=400)
    
    try:
        service = Service.objects.get(slug=service_slug)
        
        # Determinar el grupo según el servicio
        if service_slug == 'tutoria':
            group_name = 'Tutor'
        elif service_slug == 'terapia':
            group_name = 'Psicologo'
        else:
            return JsonResponse({
                'success': False,
                'message': 'Servicio no soportado'
            }, status=400)
        
        # Obtener empleados del grupo
        try:
            group = Group.objects.get(name=group_name)
            employees = User.objects.filter(groups=group, is_active=True)
            
            # Contar clientes activos por empleado
            employees_data = []
            for emp in employees:
                active_clients = ClientAssignment.objects.filter(
                    employee=emp,
                    is_active=True
                ).count()
                
                employees_data.append({
                    'id': emp.id,
                    'name': emp.get_full_name() or emp.username,
                    'username': emp.username,
                    'active_clients': active_clients
                })
            
            # Ordenar por menor carga de trabajo
            employees_data.sort(key=lambda x: x['active_clients'])
            
            return JsonResponse({
                'success': True,
                'employees': employees_data
            })
            
        except Group.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': f'Grupo {group_name} no encontrado'
            }, status=404)
            
    except Service.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Servicio no encontrado'
        }, status=404)


def generate_sessions_for_order(order, user_account=None):
    """
    Genera sesiones automáticamente para una orden confirmada
    
    Args:
        order: Objeto Order
        user_account: Cuenta de usuario del cliente (opcional)
    
    Returns:
        dict con información sobre las sesiones generadas
    """
    if order.sessions_generated:
        return {
            'success': False,
            'message': 'Las sesiones ya fueron generadas para esta orden'
        }
    
    if not order.preferred_employee:
        return {
            'success': False,
            'message': 'No se ha asignado un empleado a esta orden'
        }
    
    if not order.preferred_days or len(order.preferred_days) == 0:
        return {
            'success': False,
            'message': 'No se han especificado días preferidos'
        }
    
    if not order.preferred_time:
        return {
            'success': False,
            'message': 'No se ha especificado hora preferida'
        }
    
    # Crear o buscar el usuario del cliente
    client_user = user_account
    if not client_user:
        # Intentar encontrar por email
        try:
            client_user = User.objects.get(email=order.customer.email)
        except User.DoesNotExist:
            # Crear usuario para el cliente
            username = order.customer.email.split('@')[0]
            # Asegurarse de que el username sea único
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            client_user = User.objects.create_user(
                username=username,
                email=order.customer.email,
                first_name=order.customer.name.split()[0] if order.customer.name else '',
                last_name=' '.join(order.customer.name.split()[1:]) if len(order.customer.name.split()) > 1 else ''
            )
            # Asignar al grupo Cliente
            try:
                cliente_group = Group.objects.get(name='Cliente')
                client_user.groups.add(cliente_group)
            except Group.DoesNotExist:
                pass
    
    # Crear o buscar asignación
    assignment, created = ClientAssignment.objects.get_or_create(
        client=client_user,
        employee=order.preferred_employee,
        service=order.service,
        defaults={'is_active': True}
    )
    
    # Mapeo de días de la semana
    weekday_map = {
        'monday': 0,
        'tuesday': 1,
        'wednesday': 2,
        'thursday': 3,
        'friday': 4,
        'saturday': 5,
        'sunday': 6
    }
    
    # Obtener números de días de la semana preferidos
    preferred_weekdays = [weekday_map[day] for day in order.preferred_days if day in weekday_map]
    
    if not preferred_weekdays:
        return {
            'success': False,
            'message': 'Días de la semana inválidos'
        }
    
    # Generar sesiones
    sessions_created = []
    # Usar la fecha de inicio especificada por el usuario, o mañana si no se especificó
    if order.start_date:
        current_date = order.start_date
    else:
        current_date = timezone.now().date() + timedelta(days=1)
    
    sessions_count = 0
    day_index = 0
    
    # Buscar el próximo día disponible
    while sessions_count < order.number_of_sessions:
        # Calcular el siguiente día
        days_ahead = (preferred_weekdays[day_index % len(preferred_weekdays)] - current_date.weekday()) % 7
        if days_ahead == 0 and sessions_count > 0:
            days_ahead = 7
        
        next_date = current_date + timedelta(days=days_ahead if days_ahead > 0 else 7)
        
        # Combinar fecha y hora
        session_datetime = timezone.make_aware(
            datetime.combine(next_date, order.preferred_time)
        )
        
        # Crear sesión
        session = Session.objects.create(
            assignment=assignment,
            scheduled_date=session_datetime,
            duration_minutes=60,
            status='scheduled',
            notes=f'Sesión {sessions_count + 1} de {order.number_of_sessions} - Generada automáticamente'
        )
        
        sessions_created.append({
            'id': session.id,
            'date': session_datetime.strftime('%Y-%m-%d'),
            'time': session_datetime.strftime('%H:%M'),
            'weekday': session_datetime.strftime('%A')
        })
        
        sessions_count += 1
        current_date = next_date
        day_index += 1
    
    # Marcar orden como con sesiones generadas
    order.sessions_generated = True
    order.status = 'confirmed'
    order.save()
    
    return {
        'success': True,
        'message': f'Se generaron {sessions_count} sesiones correctamente',
        'sessions': sessions_created,
        'assignment_id': assignment.id,
        'client_username': client_user.username
    }


# @login_required  # Comentado temporalmente para desarrollo
def cliente_dashboard(request):
    """Dashboard del cliente"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Obtener asignaciones activas del cliente con prefetch
    assignments = ClientAssignment.objects.filter(
        client=request.user,
        is_active=True
    ).select_related('employee', 'service').prefetch_related('sessions')
    
    # Obtener sesiones del cliente ordenadas por fecha con prefetch
    sessions = Session.objects.filter(
        assignment__client=request.user
    ).select_related(
        'assignment__employee', 'assignment__service'
    ).prefetch_related(
        'files'
    ).order_by('scheduled_date')
    
    # Calcular estadísticas
    total_sessions = sessions.count()
    completed_sessions = sessions.filter(status='completed').count()
    scheduled_sessions = sessions.filter(Q(status='scheduled') | Q(status='confirmed')).count()
    progress = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
    
    # Obtener próxima sesión
    next_session = sessions.filter(
        Q(status='scheduled') | Q(status='confirmed'),
        scheduled_date__gte=timezone.now()
    ).first()
    
    # Calcular días hasta próxima sesión
    days_until_next = None
    if next_session:
        days_until_next = (next_session.scheduled_date.date() - timezone.now().date()).days
    
    # Obtener archivos del cliente
    files = FileUpload.objects.filter(
        assignment__client=request.user
    ).select_related('uploaded_by', 'assignment__service').order_by('-uploaded_at')[:10]
    
    context = {
        'assignments': assignments,
        'sessions': sessions,
        'files': files,
        'total_sessions': total_sessions,
        'completed_sessions': completed_sessions,
        'scheduled_sessions': scheduled_sessions,
        'progress': round(progress, 1),
        'next_session': next_session,
        'days_until_next': days_until_next,
    }
    
    return render(request, 'cliente-dashboard.html', context)


# @login_required  # Comentado temporalmente para desarrollo
def empleado_dashboard(request):
    """Dashboard del empleado"""
    # if not request.user.is_staff:
    #     messages.error(request, 'No tienes permisos para acceder a esta página')
    #     return redirect('index')
    
    # Obtener clientes asignados al empleado actual
    assigned_clients = ClientAssignment.objects.filter(
        employee=request.user,
        is_active=True
    ).select_related('client', 'service')
    
    # Calcular estadísticas para cada cliente
    clients_data = []
    for assignment in assigned_clients:
        # Contar TODAS las sesiones del cliente (no solo de esta asignación)
        all_sessions = Session.objects.filter(assignment__client=assignment.client)
        total_sessions = all_sessions.count()
        completed_sessions = all_sessions.filter(status='completed').count()
        progress = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
        
        clients_data.append({
            'assignment': assignment,
            'client': assignment.client,
            'service': assignment.service,
            'total_sessions': total_sessions,
            'completed_sessions': completed_sessions,
            'progress': round(progress, 1)
        })
    
    orders = Order.objects.all()
    
    context = {
        'orders': orders,
        'clients_data': clients_data,
        'total_clients': len(clients_data)
    }
    
    return render(request, 'empleado-dashboard.html', context)


# @login_required  # Comentado temporalmente para desarrollo
def auditoria_estudiante(request):
    """Página de auditoría para estudiantes/clientes"""
    # Obtener el cliente específico si viene por parámetro
    client_id = request.GET.get('client')
    
    if client_id:
        try:
            client = User.objects.get(id=client_id)
        except User.DoesNotExist:
            client = None
    else:
        # Si no viene parámetro, intentar obtener el primer cliente asignado al empleado actual
        if request.user.is_authenticated:
            assignment = ClientAssignment.objects.filter(
                employee=request.user,
                is_active=True
            ).select_related('client').first()
            client = assignment.client if assignment else None
        else:
            client = None
    
    if not client:
        # Si no hay cliente, mostrar mensaje
        context = {
            'client': None,
            'assignments': [],
            'sessions': [],
            'files': [],
            'audit_logs': [],
        }
        return render(request, 'auditoria-estudiante.html', context)
    
    # Obtener todas las asignaciones del cliente
    assignments = ClientAssignment.objects.filter(
        client=client,
        is_active=True
    ).select_related('employee', 'service').prefetch_related('sessions')
    
    # Obtener todas las sesiones del cliente ordenadas por fecha (ascendente)
    sessions = Session.objects.filter(
        assignment__client=client
    ).select_related('assignment__employee', 'assignment__service').order_by('scheduled_date')
    
    # Obtener archivos del cliente
    files = FileUpload.objects.filter(
        assignment__client=client
    ).select_related('uploaded_by', 'assignment__service').order_by('-uploaded_at')
    
    # Obtener logs de auditoría del cliente
    audit_logs = AuditLog.objects.filter(
        Q(user=client) | Q(related_object_id=str(client.id))
    ).order_by('-timestamp')[:50]
    
    # Calcular estadísticas
    total_sessions = sessions.count()
    completed_sessions = sessions.filter(status='completed').count()
    scheduled_sessions = sessions.filter(Q(status='scheduled') | Q(status='confirmed')).count()
    progress = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
    
    # Obtener la asignación principal (la más reciente)
    main_assignment = assignments.first()
    
    context = {
        'client': client,
        'assignments': assignments,
        'sessions': sessions,
        'files': files,
        'audit_logs': audit_logs,
        'total_sessions': total_sessions,
        'completed_sessions': completed_sessions,
        'scheduled_sessions': scheduled_sessions,
        'progress': round(progress, 1),
        'main_assignment': main_assignment,
    }
    
    return render(request, 'auditoria-estudiante.html', context)


def get_client_details(request, client_id):
    """API para obtener detalles de un cliente en formato JSON"""
    try:
        client = User.objects.get(id=client_id)
        
        # Obtener perfil del cliente
        from cuentas.models import UserProfile
        profile = None
        try:
            profile = UserProfile.objects.get(user=client)
        except UserProfile.DoesNotExist:
            pass
        
        # Obtener asignaciones del cliente
        assignments = ClientAssignment.objects.filter(
            client=client,
            is_active=True
        ).select_related('employee', 'service')
        
        # Obtener sesiones ordenadas por fecha (más recientes primero para detalles, pero próximas primero para lista)
        sessions = Session.objects.filter(
            assignment__client=client
        ).select_related('assignment__service', 'assignment__employee').order_by('scheduled_date')
        
        # Calcular estadísticas
        total_sessions = sessions.count()
        completed_sessions = sessions.filter(status='completed').count()
        scheduled_sessions = sessions.filter(Q(status='scheduled') | Q(status='confirmed')).count()
        progress = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
        
        # Obtener última sesión completada (más reciente)
        last_session = sessions.filter(status='completed').order_by('-scheduled_date').first()
        
        # Obtener próxima cita
        next_session = sessions.filter(
            Q(status='scheduled') | Q(status='confirmed'),
            scheduled_date__gte=timezone.now()
        ).order_by('scheduled_date').first()
        
        # Calcular días desde última sesión
        last_session_days = None
        if last_session:
            last_session_days = (timezone.now().date() - last_session.scheduled_date.date()).days
        
        # Formatear próxima cita
        next_appointment_text = None
        if next_session:
            months = {
                1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril',
                5: 'mayo', 6: 'junio', 7: 'julio', 8: 'agosto',
                9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
            }
            month_name = months.get(next_session.scheduled_date.month, '')
            next_appointment_text = f"{next_session.scheduled_date.day} de {month_name}, {next_session.scheduled_date.year}"
        
        # Construir lista de asignaciones
        assignments_list = []
        for a in assignments:
            assignments_list.append({
                'service': a.service.name,
                'employee': a.employee.get_full_name() or a.employee.username,
                'assigned_date': a.assigned_at.strftime('%Y-%m-%d')
            })
        
        # Preparar respuesta
        data = {
            'success': True,
            'client': {
                'id': client.id,
                'name': client.get_full_name() or client.username,
                'email': client.email,
                'username': client.username,
                'date_joined': client.date_joined.strftime('%Y-%m-%d'),
                'phone': profile.phone if profile else None,
                'address': profile.address if profile else None,
            },
            'progress': int(round(progress, 0)),
            'last_session': last_session.scheduled_date.strftime('%Y-%m-%d') if last_session else None,
            'last_session_days': last_session_days,
            'next_appointment': next_appointment_text,
            'status': 'Activo' if assignments.exists() else 'Inactivo',
            'total_sessions': total_sessions,
            'completed_sessions': completed_sessions,
            'scheduled_sessions': scheduled_sessions,
            'assignments': assignments_list
        }
        
        return JsonResponse(data)
        
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Cliente no encontrado'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ============================================
# EMPLOYEE DASHBOARD HELPER FUNCTION
# ============================================

def _get_employee_dashboard_data(user, request=None):
    """
    Función auxiliar para obtener datos comunes de dashboards de empleados.
    Evita duplicación de código entre psicólogo, tutor y empleado dashboards.
    
    Args:
        user: Usuario empleado actual
        request: Objeto request para obtener parámetros de filtrado
        
    Returns:
        dict: Diccionario con clients_data, total_clients y filtros aplicados
    """
    # Obtener parámetros de filtrado/ordenamiento
    search_query = request.GET.get('search', '').strip() if request else ''
    order_by = request.GET.get('order_by', 'recent_activity') if request else 'recent_activity'
    
    # Obtener clientes asignados al empleado actual
    assigned_clients = ClientAssignment.objects.filter(
        employee=user,
        is_active=True
    ).select_related('client', 'service').prefetch_related(
        'sessions',
        'sessions__files',
        'files'
    )
    
    # Calcular estadísticas para cada cliente
    clients_data = []
    for assignment in assigned_clients:
        client = assignment.client
        
        # Filtro por nombre/email
        if search_query:
            client_name = f"{client.first_name} {client.last_name}".lower()
            username = client.username.lower()
            email = client.email.lower()
            
            if not (search_query.lower() in client_name or 
                    search_query.lower() in username or 
                    search_query.lower() in email):
                continue
        
        # Contar TODAS las sesiones del cliente
        all_sessions = Session.objects.filter(assignment__client=client)
        total_sessions = all_sessions.count()
        completed_sessions = all_sessions.filter(status='completed').count()
        progress = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
        
        # Obtener última actividad (última sesión o archivo subido)
        last_session = all_sessions.order_by('-scheduled_date').first()
        last_file = FileUpload.objects.filter(
            assignment__client=client
        ).order_by('-uploaded_at').first()
        
        # Determinar la actividad más reciente
        last_activity = None
        if last_session and last_file:
            last_activity = max(last_session.scheduled_date, last_file.uploaded_at)
        elif last_session:
            last_activity = last_session.scheduled_date
        elif last_file:
            last_activity = last_file.uploaded_at
        
        # Próxima cita (sesión pendiente más cercana)
        next_appointment = all_sessions.filter(
            status='pending',
            scheduled_date__gte=timezone.now()
        ).order_by('scheduled_date').first()
        
        # Contar archivos nuevos (últimos 7 días)
        recent_files_count = FileUpload.objects.filter(
            assignment__client=client,
            uploaded_at__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        clients_data.append({
            'assignment': assignment,
            'client': client,
            'service': assignment.service,
            'total_sessions': total_sessions,
            'completed_sessions': completed_sessions,
            'progress': round(progress, 1),
            'last_activity': last_activity,
            'next_appointment': next_appointment,
            'recent_files_count': recent_files_count
        })
    
    # Aplicar ordenamiento
    if order_by == 'recent_activity':
        # Ordenar por última actividad (más reciente primero)
        clients_data.sort(key=lambda x: x['last_activity'] or timezone.datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    elif order_by == 'next_appointment':
        # Ordenar por próxima cita (más cercana primero)
        clients_data.sort(key=lambda x: (
            x['next_appointment'].scheduled_date if x['next_appointment'] 
            else timezone.datetime.max.replace(tzinfo=timezone.utc)
        ))
    elif order_by == 'name':
        # Ordenar alfabéticamente por nombre
        clients_data.sort(key=lambda x: (
            f"{x['client'].first_name} {x['client'].last_name}".lower() 
            if x['client'].first_name else x['client'].username.lower()
        ))
    elif order_by == 'progress':
        # Ordenar por progreso (mayor primero)
        clients_data.sort(key=lambda x: x['progress'], reverse=True)
    elif order_by == 'new_files':
        # Ordenar por archivos recientes (más primero)
        clients_data.sort(key=lambda x: x['recent_files_count'], reverse=True)
    
    # Obtener solicitudes asignadas al empleado que están confirmadas (aprobadas por admin)
    pending_requests = Order.objects.filter(
        Q(preferred_employee=user) | Q(preferred_tutor=user) | Q(preferred_therapist=user),
        status='confirmed'  # Solo mostrar las aprobadas por admin
    ).select_related('customer', 'service', 'price').order_by('-created_at')
    
    orders = Order.objects.all()
    
    return {
        'orders': orders,
        'clients_data': clients_data,
        'total_clients': len(clients_data),
        'search_query': search_query,
        'order_by': order_by,
        'pending_requests': pending_requests,
        'pending_requests_count': pending_requests.count()
    }


# ============================================
# EMPLOYEE DASHBOARD VIEWS
# ============================================

# @login_required  # Comentado temporalmente para desarrollo
def psicologo_dashboard(request):
    """Dashboard del psicólogo con filtrado y ordenamiento"""
    context = _get_employee_dashboard_data(request.user, request)
    return render(request, 'psicologo-dashboard.html', context)


# @login_required  # Comentado temporalmente para desarrollo
def tutor_dashboard(request):
    """Dashboard del tutor con filtrado y ordenamiento"""
    context = _get_employee_dashboard_data(request.user, request)
    return render(request, 'tutor-dashboard.html', context)


# @login_required  # Comentado temporalmente para desarrollo  
def empleado_dashboard(request):
    """Dashboard del empleado general con filtrado y ordenamiento"""
    context = _get_employee_dashboard_data(request.user, request)
    return render(request, 'empleado-dashboard.html', context)


# ============================================
# ADMIN DASHBOARD VIEWS
# ============================================

def is_admin(user):
    """Verificar si el usuario es administrador o superusuario"""
    return user.is_superuser or user.is_staff


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Dashboard principal del administrador"""
    from django.core.cache import cache
    
    # Intentar obtener servicios y grupos desde cache
    services = cache.get('all_services')
    if services is None:
        services = list(Service.objects.all())
        cache.set('all_services', services, 60 * 15)  # 15 minutos
    
    groups = cache.get('all_groups')
    if groups is None:
        groups = list(Group.objects.all())
        cache.set('all_groups', groups, 60 * 15)
    
    # Obtener solo empleados (staff o con grupos de Psicólogo/Tutor, excluyendo Cliente)
    employees = User.objects.filter(
        Q(is_staff=True) | 
        Q(groups__name='Psicólogo') | 
        Q(groups__name='Tutor')
    ).exclude(groups__name='Cliente').distinct().prefetch_related('groups')
    
    # Obtener clientes con estadísticas anotadas
    clients = User.objects.filter(groups__name='Cliente').distinct().annotate(
        active_assignments_count=Count(
            'client_assignments',
            filter=Q(client_assignments__is_active=True),
            distinct=True
        ),
        total_sessions=Count('client_assignments__sessions', distinct=True),
        files_count=Count('client_assignments__files', distinct=True),
        audit_count=Count('audit_logs', distinct=True)
    ).prefetch_related('groups', 'client_assignments')
    
    # Obtener órdenes/solicitudes con prefetch
    orders = Order.objects.select_related(
        'customer', 'service', 'price', 'preferred_employee', 
        'preferred_tutor', 'preferred_therapist'
    ).prefetch_related(
        'service__prices'
    ).order_by('-created_at')[:50]
    
    assignments = ClientAssignment.objects.select_related(
        'client', 'employee', 'service'
    ).prefetch_related(
        'sessions', 'files'
    ).all()
    
    # Obtener sesiones ordenadas de más reciente a más antigua (para ver las nuevas primero)
    sessions = Session.objects.select_related(
        'assignment__client', 'assignment__employee', 'assignment__service'
    ).prefetch_related(
        'files'
    ).order_by('-scheduled_date')[:100]
    
    files = FileUpload.objects.select_related(
        'assignment', 'assignment__client', 'assignment__employee', 'uploaded_by'
    ).order_by('-uploaded_at')[:50]
    
    # Obtener logs de auditoría ordenados por fecha descendente (más recientes primero)
    audit_logs = AuditLog.objects.select_related('user').order_by('-timestamp')[:100]
    
    context = {
        'services': services,
        'groups': groups,
        'employees': employees,
        'clients': clients,
        'orders': orders,
        'assignments': assignments,
        'sessions': sessions,
        'files': files,
        'audit_logs': audit_logs,
    }
    
    return render(request, 'admin-dashboard.html', context)


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def admin_create_service(request):
    """Crear un nuevo servicio"""
    try:
        service_name = request.POST.get('service_name', '').strip()
        service_slug = request.POST.get('service_slug', '').strip().lower()
        service_description = request.POST.get('service_description', '').strip()
        
        if not all([service_name, service_slug]):
            messages.error(request, 'El nombre y el slug son campos requeridos')
            return redirect('admin_dashboard')
        
        # Validar que el slug solo contenga caracteres permitidos
        import re
        if not re.match(r'^[a-z0-9-]+$', service_slug):
            messages.error(request, 'El slug solo puede contener letras minúsculas, números y guiones')
            return redirect('admin_dashboard')
        
        # Verificar que el slug no exista
        if Service.objects.filter(slug=service_slug).exists():
            messages.error(request, f'Ya existe un servicio con el slug "{service_slug}"')
            return redirect('admin_dashboard')
        
        # Crear servicio
        service = Service.objects.create(
            name=service_name,
            slug=service_slug,
            description=service_description
        )
        
        # Registrar en auditoría
        AuditLog.objects.create(
            user=request.user,
            action='other',
            description=f'Servicio creado: {service_name} ({service_slug})',
            ip_address=get_client_ip(request),
            related_object_type='Service',
            related_object_id=service.id
        )
        
        # Limpiar caché
        from django.core.cache import cache
        cache.clear()
        
        messages.success(request, f'Servicio "{service_name}" creado exitosamente')
        
    except Exception as e:
        messages.error(request, f'Error al crear servicio: {str(e)}')
    
    return redirect('admin_dashboard')


@login_required
@user_passes_test(is_admin)
def admin_delete_service(request, service_id):
    """Eliminar un servicio y todos sus precios asociados"""
    try:
        service = get_object_or_404(Service, id=service_id)
        service_name = service.name
        prices_count = service.prices.count()
        
        # Registrar en auditoría antes de eliminar
        AuditLog.objects.create(
            user=request.user,
            action='other',
            description=f'Servicio eliminado: {service_name} ({service.slug}) con {prices_count} precio(s)',
            ip_address=get_client_ip(request),
            related_object_type='Service',
            related_object_id=service.id
        )
        
        # Eliminar servicio (los precios se eliminan en cascada)
        service.delete()
        
        # Limpiar caché
        from django.core.cache import cache
        cache.clear()
        
        messages.success(request, f'Servicio "{service_name}" y {prices_count} precio(s) eliminados exitosamente')
        
    except Exception as e:
        messages.error(request, f'Error al eliminar servicio: {str(e)}')
    
    return redirect('admin_dashboard')


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def admin_create_price(request):
    """Crear un nuevo precio y opcionalmente un nuevo servicio"""
    from django.core.cache import cache
    
    try:
        servicio_id = request.POST.get('servicio')
        plan = request.POST.get('plan', '').strip()
        precio = request.POST.get('precio')
        moneda = request.POST.get('moneda', 'CLP')
        descripcion = request.POST.get('descripcion', '').strip()
        
        # Campos de sesiones
        number_of_sessions = request.POST.get('number_of_sessions', 4)
        tutoring_sessions = request.POST.get('tutoring_sessions', 8)
        therapy_sessions = request.POST.get('therapy_sessions', 8)
        
        # Validación de campos básicos
        if not all([servicio_id, plan, precio]):
            messages.error(request, 'Faltan campos requeridos')
            return redirect('admin_dashboard')
        
        # Si se seleccionó "nuevo", crear el servicio primero
        if servicio_id == 'nuevo':
            new_service_name = request.POST.get('new_service_name', '').strip()
            new_service_slug = request.POST.get('new_service_slug', '').strip()
            new_service_description = request.POST.get('new_service_description', '').strip()
            
            if not all([new_service_name, new_service_slug]):
                messages.error(request, 'Debes proporcionar nombre y slug para el nuevo servicio')
                return redirect('admin_dashboard')
            
            # Validar que el slug sea válido (solo lowercase, números y guiones)
            import re
            if not re.match(r'^[a-z0-9-]+$', new_service_slug):
                messages.error(request, 'El slug solo puede contener letras minúsculas, números y guiones')
                return redirect('admin_dashboard')
            
            # Verificar que no exista un servicio con ese slug
            if Service.objects.filter(slug=new_service_slug).exists():
                messages.error(request, f'Ya existe un servicio con el slug "{new_service_slug}"')
                return redirect('admin_dashboard')
            
            # Crear el nuevo servicio
            service = Service.objects.create(
                name=new_service_name,
                slug=new_service_slug,
                description=new_service_description or f'Servicio de {new_service_name}'
            )
            
            # Registrar creación de servicio en auditoría
            AuditLog.objects.create(
                user=request.user,
                action='other',
                description=f'Servicio creado: {new_service_name} (slug: {new_service_slug})',
                ip_address=get_client_ip(request),
                related_object_type='Service',
                related_object_id=service.id
            )
            
            messages.success(request, f'Servicio "{new_service_name}" creado exitosamente')
        else:
            # Obtener el servicio existente
            service = get_object_or_404(Service, id=servicio_id)
        
        # Convertir sesiones a enteros
        try:
            number_of_sessions = int(number_of_sessions)
            tutoring_sessions = int(tutoring_sessions)
            therapy_sessions = int(therapy_sessions)
        except (ValueError, TypeError):
            messages.error(request, 'El número de sesiones debe ser un valor numérico')
            return redirect('admin_dashboard')
        
        price = Price.objects.create(
            service=service,
            plan=plan,
            price=precio,
            currency=moneda,
            description=descripcion,
            number_of_sessions=number_of_sessions,
            tutoring_sessions=tutoring_sessions,
            therapy_sessions=therapy_sessions
        )
        
        # Registrar en auditoría
        AuditLog.objects.create(
            user=request.user,
            action='other',
            description=f'Precio creado: {plan} - ${precio} {moneda} para {service.name}',
            ip_address=get_client_ip(request),
            related_object_type='Price',
            related_object_id=price.id
        )
        
        # Limpiar cache
        cache.clear()
        
        messages.success(request, f'Precio "{plan}" creado exitosamente para {service.name}')
        
    except Exception as e:
        messages.error(request, f'Error al crear precio: {str(e)}')
    
    return redirect('admin_dashboard')


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def admin_create_employee(request):
    """Crear una cuenta de empleado"""
    try:
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        grupo_id = request.POST.get('grupo')
        is_staff = request.POST.get('is_staff') == '1'
        
        # Validaciones
        if not all([username, email, first_name, last_name, password1, grupo_id]):
            messages.error(request, 'Faltan campos requeridos')
            return redirect('admin_dashboard')
        
        if password1 != password2:
            messages.error(request, 'Las contraseñas no coinciden')
            return redirect('admin_dashboard')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya existe')
            return redirect('admin_dashboard')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'El email ya está registrado')
            return redirect('admin_dashboard')
        
        # Crear usuario
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name,
            is_staff=is_staff
        )
        
        # Asignar grupo
        group = get_object_or_404(Group, id=grupo_id)
        user.groups.add(group)
        
        # Registrar en auditoría
        AuditLog.objects.create(
            user=request.user,
            action='other',
            description=f'Empleado creado: {username} ({first_name} {last_name}) - Grupo: {group.name}',
            ip_address=get_client_ip(request),
            related_object_type='User',
            related_object_id=user.id
        )
        
        messages.success(request, f'Empleado "{username}" creado exitosamente')
        
    except Exception as e:
        messages.error(request, f'Error al crear empleado: {str(e)}')
    
    return redirect('admin_dashboard')


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def admin_create_assignment(request):
    """Crear una asignación cliente-empleado"""
    try:
        cliente_id = request.POST.get('cliente')
        empleado_id = request.POST.get('empleado')
        servicio_id = request.POST.get('servicio')
        notas = request.POST.get('notas', '').strip()
        
        if not all([cliente_id, empleado_id, servicio_id]):
            messages.error(request, 'Faltan campos requeridos')
            return redirect('admin_dashboard')
        
        cliente = get_object_or_404(User, id=cliente_id)
        empleado = get_object_or_404(User, id=empleado_id)
        servicio = get_object_or_404(Service, id=servicio_id)
        
        assignment = ClientAssignment.objects.create(
            client=cliente,
            employee=empleado,
            service=servicio,
            notes=notas
        )
        
        # Registrar en auditoría
        AuditLog.objects.create(
            user=request.user,
            action='other',
            description=f'Asignación creada: {cliente.username} → {empleado.username} ({servicio.name})',
            ip_address=get_client_ip(request),
            related_object_type='ClientAssignment',
            related_object_id=assignment.id
        )
        
        messages.success(request, 'Asignación creada exitosamente')
        
    except Exception as e:
        messages.error(request, f'Error al crear asignación: {str(e)}')
    
    return redirect('admin_dashboard')


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def admin_create_session(request):
    """Crear una sesión"""
    try:
        asignacion_id = request.POST.get('asignacion')
        fecha = request.POST.get('fecha')
        hora = request.POST.get('hora')
        duracion = request.POST.get('duracion', 60)
        estado = request.POST.get('estado', 'scheduled')
        notas = request.POST.get('notas', '').strip()
        
        if not all([asignacion_id, fecha, hora]):
            messages.error(request, 'Faltan campos requeridos')
            return redirect('admin_dashboard')
        
        assignment = get_object_or_404(ClientAssignment, id=asignacion_id)
        
        # Combinar fecha y hora
        fecha_hora = datetime.strptime(f'{fecha} {hora}', '%Y-%m-%d %H:%M')
        
        session = Session.objects.create(
            assignment=assignment,
            scheduled_date=fecha_hora,
            duration_minutes=int(duracion),
            status=estado,
            notes=notas
        )
        
        # Registrar en auditoría
        AuditLog.objects.create(
            user=request.user,
            action='session_scheduled',
            description=f'Sesión programada: {assignment.client.username} - {fecha_hora.strftime("%Y-%m-%d %H:%M")}',
            ip_address=get_client_ip(request),
            related_object_type='Session',
            related_object_id=session.id
        )
        
        messages.success(request, 'Sesión creada exitosamente')
        
    except Exception as e:
        messages.error(request, f'Error al crear sesión: {str(e)}')
    
    return redirect('admin_dashboard')


@login_required
@user_passes_test(is_admin)
@csrf_exempt
@require_http_methods(["POST"])
def admin_generate_sessions(request, order_id):
    """Generar sesiones automáticamente para una orden"""
    try:
        order = get_object_or_404(Order, id=order_id)
        
        # Verificar si es Plan Estudiante (requiere tutor y terapeuta)
        if order.service.slug == 'plan-estudiante':
            result = generate_student_plan_sessions(order)
        else:
            # Servicios regulares (tutoría o terapia individual)
            result = generate_sessions_for_order(order)
        
        if result['success']:
            messages.success(request, result['message'])
            
            # Registrar en auditoría
            AuditLog.objects.create(
                user=request.user,
                action='other',
                description=f'Sesiones generadas para orden #{order.id} - {result["message"]}',
                ip_address=get_client_ip(request),
                related_object_type='Order',
                related_object_id=order.id
            )
        else:
            messages.error(request, result['message'])
            
        return JsonResponse(result)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)


def get_client_ip(request):
    """Obtener la IP del cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@login_required
@user_passes_test(is_admin)
def admin_edit_price(request, price_id):
    """Editar un precio existente"""
    price = get_object_or_404(Price, id=price_id)
    
    if request.method == 'POST':
        try:
            servicio_id = request.POST.get('servicio')
            plan = request.POST.get('plan', '').strip()
            precio = request.POST.get('precio')
            moneda = request.POST.get('moneda', 'CLP')
            descripcion = request.POST.get('descripcion', '').strip()
            
            # Campos de sesiones
            number_of_sessions = request.POST.get('number_of_sessions', 4)
            tutoring_sessions = request.POST.get('tutoring_sessions', 8)
            therapy_sessions = request.POST.get('therapy_sessions', 8)
            
            if not all([servicio_id, plan, precio]):
                messages.error(request, 'Faltan campos requeridos')
                return redirect('admin_dashboard')
            
            service = get_object_or_404(Service, id=servicio_id)
            
            # Convertir sesiones a enteros
            try:
                number_of_sessions = int(number_of_sessions)
                tutoring_sessions = int(tutoring_sessions)
                therapy_sessions = int(therapy_sessions)
            except (ValueError, TypeError):
                messages.error(request, 'El número de sesiones debe ser un valor numérico')
                return redirect('admin_dashboard')
            
            old_info = f"{price.plan} - ${price.price} {price.currency}"
            
            price.service = service
            price.plan = plan
            price.price = precio
            price.currency = moneda
            price.description = descripcion
            price.number_of_sessions = number_of_sessions
            price.tutoring_sessions = tutoring_sessions
            price.therapy_sessions = therapy_sessions
            price.save()
            
            # Registrar en auditoría
            AuditLog.objects.create(
                user=request.user,
                action='other',
                description=f'Precio editado: {old_info} → {plan} - ${precio} {moneda}',
                ip_address=get_client_ip(request),
                related_object_type='Price',
                related_object_id=price.id
            )
            
            messages.success(request, f'Precio "{plan}" actualizado exitosamente')
            
        except Exception as e:
            messages.error(request, f'Error al editar precio: {str(e)}')
    
    return redirect('admin_dashboard')


@login_required
@user_passes_test(is_admin)
def admin_delete_price(request, price_id):
    """Eliminar un precio"""
    try:
        price = get_object_or_404(Price, id=price_id)
        info = f"{price.plan} - ${price.price} {price.currency} ({price.service.name})"
        
        # Registrar en auditoría antes de eliminar
        AuditLog.objects.create(
            user=request.user,
            action='other',
            description=f'Precio eliminado: {info}',
            ip_address=get_client_ip(request),
            related_object_type='Price',
            related_object_id=price.id
        )
        
        price.delete()
        messages.success(request, f'Precio "{price.plan}" eliminado exitosamente')
        
    except Exception as e:
        messages.error(request, f'Error al eliminar precio: {str(e)}')
    
    return redirect('admin_dashboard')


@login_required
@user_passes_test(is_admin)
def admin_toggle_featured(request, price_id):
    """Marcar/desmarcar un plan como destacado"""
    if request.method == 'POST':
        try:
            price = get_object_or_404(Price, id=price_id)
            data = json.loads(request.body)
            is_featured = data.get('is_featured', False)
            
            price.is_featured = is_featured
            price.save()
            
            # Registrar en auditoría
            AuditLog.objects.create(
                user=request.user,
                action='other',
                description=f'Plan {"marcado como destacado" if is_featured else "desmarcado como destacado"}: {price.plan} ({price.service.name})',
                ip_address=get_client_ip(request),
                related_object_type='Price',
                related_object_id=price.id
            )
            
            # Limpiar caché para reflejar cambios inmediatamente
            from django.core.cache import cache
            cache.delete('index_services_data')
            
            return JsonResponse({
                'success': True,
                'message': f'Plan {"destacado" if is_featured else "no destacado"} actualizado correctamente'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)


@login_required
@user_passes_test(is_admin)
def admin_toggle_employee(request, employee_id):
    """Activar/Desactivar un empleado"""
    try:
        employee = get_object_or_404(User, id=employee_id)
        
        # No permitir desactivar al propio usuario
        if employee.id == request.user.id:
            messages.error(request, 'No puedes desactivar tu propia cuenta')
            return redirect('admin_dashboard')
        
        employee.is_active = not employee.is_active
        employee.save()
        
        estado = 'activado' if employee.is_active else 'desactivado'
        
        # Registrar en auditoría
        AuditLog.objects.create(
            user=request.user,
            action='other',
            description=f'Empleado {estado}: {employee.username}',
            ip_address=get_client_ip(request),
            related_object_type='User',
            related_object_id=employee.id
        )
        
        messages.success(request, f'Empleado "{employee.username}" {estado} exitosamente')
        
    except Exception as e:
        messages.error(request, f'Error al cambiar estado del empleado: {str(e)}')
    
    return redirect('admin_dashboard')


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def admin_edit_employee(request, employee_id):
    """Editar datos de un empleado"""
    try:
        employee = get_object_or_404(User, id=employee_id)
        
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        grupo_id = request.POST.get('grupo')
        is_staff = request.POST.get('is_staff') == '1'
        new_password = request.POST.get('new_password', '').strip()
        
        # Validaciones
        if not all([username, email, first_name, last_name, grupo_id]):
            return JsonResponse({'success': False, 'message': 'Faltan campos requeridos'})
        
        # Verificar username único (excepto el actual)
        if User.objects.filter(username=username).exclude(id=employee_id).exists():
            return JsonResponse({'success': False, 'message': 'El nombre de usuario ya existe'})
        
        # Verificar email único (excepto el actual)
        if User.objects.filter(email=email).exclude(id=employee_id).exists():
            return JsonResponse({'success': False, 'message': 'El email ya está registrado'})
        
        # Actualizar datos
        employee.username = username
        employee.email = email
        employee.first_name = first_name
        employee.last_name = last_name
        employee.is_staff = is_staff
        
        # Cambiar contraseña si se proporcionó
        if new_password:
            employee.set_password(new_password)
        
        employee.save()
        
        # Actualizar grupo
        employee.groups.clear()
        group = get_object_or_404(Group, id=grupo_id)
        employee.groups.add(group)
        
        # Registrar en auditoría
        AuditLog.objects.create(
            user=request.user,
            action='other',
            description=f'Empleado editado: {username} ({first_name} {last_name}) - Grupo: {group.name}',
            ip_address=get_client_ip(request),
            related_object_type='User',
            related_object_id=employee.id
        )
        
        return JsonResponse({'success': True, 'message': 'Empleado actualizado exitosamente'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error al editar empleado: {str(e)}'})


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def admin_delete_employee(request, employee_id):
    """Eliminar un empleado"""
    try:
        employee = get_object_or_404(User, id=employee_id)
        
        # No permitir eliminar superusuarios
        if employee.is_superuser:
            return JsonResponse({'success': False, 'message': 'No se puede eliminar un superusuario'})
        
        # No permitir auto-eliminación
        if employee.id == request.user.id:
            return JsonResponse({'success': False, 'message': 'No puedes eliminarte a ti mismo'})
        
        username = employee.username
        
        # Registrar en auditoría antes de eliminar
        AuditLog.objects.create(
            user=request.user,
            action='other',
            description=f'Empleado eliminado: {username} ({employee.first_name} {employee.last_name})',
            ip_address=get_client_ip(request),
            related_object_type='User',
            related_object_id=employee.id
        )
        
        employee.delete()
        
        return JsonResponse({'success': True, 'message': f'Empleado "{username}" eliminado exitosamente'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error al eliminar empleado: {str(e)}'})


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def admin_edit_client(request, client_id):
    """Editar datos de un cliente"""
    try:
        client = get_object_or_404(User, id=client_id)
        
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        new_password = request.POST.get('new_password', '').strip()
        
        # Validaciones
        if not all([username, email, first_name, last_name]):
            return JsonResponse({'success': False, 'message': 'Faltan campos requeridos'})
        
        # Verificar username único (excepto el actual)
        if User.objects.filter(username=username).exclude(id=client_id).exists():
            return JsonResponse({'success': False, 'message': 'El nombre de usuario ya existe'})
        
        # Verificar email único (excepto el actual)
        if User.objects.filter(email=email).exclude(id=client_id).exists():
            return JsonResponse({'success': False, 'message': 'El email ya está registrado'})
        
        # Actualizar datos
        client.username = username
        client.email = email
        client.first_name = first_name
        client.last_name = last_name
        
        # Cambiar contraseña si se proporcionó
        if new_password:
            client.set_password(new_password)
        
        client.save()
        
        # Registrar en auditoría
        AuditLog.objects.create(
            user=request.user,
            action='other',
            description=f'Cliente editado: {username} ({first_name} {last_name})',
            ip_address=get_client_ip(request),
            related_object_type='User',
            related_object_id=client.id
        )
        
        return JsonResponse({'success': True, 'message': 'Cliente actualizado exitosamente'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error al editar cliente: {str(e)}'})


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def admin_delete_client(request, client_id):
    """Eliminar un cliente"""
    try:
        client = get_object_or_404(User, id=client_id)
        
        # No permitir eliminar al propio usuario
        if client.id == request.user.id:
            return JsonResponse({'success': False, 'message': 'No puedes eliminarte a ti mismo'})
        
        username = client.username
        
        # Registrar en auditoría antes de eliminar
        AuditLog.objects.create(
            user=request.user,
            action='other',
            description=f'Cliente eliminado: {username} ({client.first_name} {client.last_name})',
            ip_address=get_client_ip(request),
            related_object_type='User',
            related_object_id=client.id
        )
        
        client.delete()
        
        return JsonResponse({'success': True, 'message': f'Cliente "{username}" eliminado exitosamente'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error al eliminar cliente: {str(e)}'})


@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET"])
def admin_get_employee_data(request, employee_id):
    """Obtener datos de un empleado para edición"""
    try:
        employee = get_object_or_404(User, id=employee_id)
        
        data = {
            'success': True,
            'employee': {
                'id': employee.id,
                'username': employee.username,
                'email': employee.email,
                'first_name': employee.first_name,
                'last_name': employee.last_name,
                'is_staff': employee.is_staff,
                'is_active': employee.is_active,
                'grupo_id': employee.groups.first().id if employee.groups.exists() else None,
                'grupo_name': employee.groups.first().name if employee.groups.exists() else 'Sin grupo',
            }
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error al obtener datos: {str(e)}'})


@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET"])
def admin_get_client_data(request, client_id):
    """Obtener datos de un cliente para edición"""
    try:
        client = get_object_or_404(User, id=client_id)
        
        data = {
            'success': True,
            'client': {
                'id': client.id,
                'username': client.username,
                'email': client.email,
                'first_name': client.first_name,
                'last_name': client.last_name,
                'is_active': client.is_active,
            }
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error al obtener datos: {str(e)}'})



@login_required
@user_passes_test(is_admin)
def admin_toggle_assignment(request, assignment_id):
    """Activar/Desactivar una asignación"""
    try:
        assignment = get_object_or_404(ClientAssignment, id=assignment_id)
        
        assignment.is_active = not assignment.is_active
        assignment.save()
        
        estado = 'activada' if assignment.is_active else 'desactivada'
        
        # Registrar en auditoría
        AuditLog.objects.create(
            user=request.user,
            action='other',
            description=f'Asignación {estado}: {assignment.client.username} → {assignment.employee.username}',
            ip_address=get_client_ip(request),
            related_object_type='ClientAssignment',
            related_object_id=assignment.id
        )
        
        messages.success(request, f'Asignación {estado} exitosamente')
        
    except Exception as e:
        messages.error(request, f'Error al cambiar estado de asignación: {str(e)}')
    
    return redirect('admin_dashboard')


@login_required
@user_passes_test(is_admin)
def admin_delete_file(request, file_id):
    """Eliminar un archivo"""
    try:
        file = get_object_or_404(FileUpload, id=file_id)
        info = f"{file.file_name} ({file.uploaded_by.username})"
        
        # Registrar en auditoría antes de eliminar
        AuditLog.objects.create(
            user=request.user,
            action='other',
            description=f'Archivo eliminado: {info}',
            ip_address=get_client_ip(request),
            related_object_type='FileUpload',
            related_object_id=file.id
        )
        
        # Eliminar archivo físico
        if file.file:
            file.file.delete()
        
        file.delete()
        messages.success(request, f'Archivo "{file.file_name}" eliminado exitosamente')
        
    except Exception as e:
        messages.error(request, f'Error al eliminar archivo: {str(e)}')
    
    return redirect('admin_dashboard')


@csrf_exempt
@require_http_methods(["POST"])
def update_session_status(request, session_id):
    """API para actualizar el estado de una sesión"""
    try:
        session = Session.objects.get(id=session_id)
        data = json.loads(request.body)
        new_status = data.get('status')
        
        if new_status not in ['completed', 'cancelled', 'scheduled', 'confirmed', 'no_show']:
            return JsonResponse({'success': False, 'error': 'Estado inválido'}, status=400)
        
        session.status = new_status
        session.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Sesión actualizada a {new_status}',
            'session_id': session.id,
            'new_status': new_status
        })
        
    except Session.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Sesión no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def solicitar_plan_estudiante(request):
    """Formulario específico para solicitar Plan Estudiante"""
    # Obtener parámetros de la URL
    service_slug = request.GET.get('service', '')
    plan_name = request.GET.get('plan', '')
    
    # Buscar el servicio y precio
    service = None
    price = None
    
    if service_slug and plan_name:
        try:
            service = Service.objects.get(slug=service_slug)
            price = service.prices.get(plan=plan_name)
        except (Service.DoesNotExist, Price.DoesNotExist):
            pass
    
    return render(request, 'solicitar-plan-estudiante.html', {
        'service': service,
        'price': price
    })


def extract_student_plan_sessions(plan_name, price_obj=None):
    """
    Extrae el número de sesiones de tutoría y terapia del plan de estudiante
    
    Args:
        plan_name: Nombre del plan (ej. "Plan Estudiante Básico")
        price_obj: Objeto Price (opcional) para buscar en la descripción
    
    Returns:
        tuple: (tutoring_sessions, therapy_sessions)
    """
    import re
    
    # Patrones para extraer números
    # "3 sesiones de tutoría + 2 sesiones de terapia"
    # "4 tutorías + 3 terapias"
    # "12 sesiones tutoria, 8 sesiones terapia"
    # "1 sesion terapeutica + 1 sesion de tutoria"
    tutoring_match = re.search(r'(\d+)\s+(?:sesiones?\s+)?(?:de\s+)?tutor[ií]a', plan_name.lower())
    # Buscar "terapeutica" o "terapia"
    therapy_match = re.search(r'(\d+)\s+(?:sesiones?\s+)?(?:de\s+)?terap[ée]utic[oa]?|(\d+)\s+(?:sesiones?\s+)?(?:de\s+)?terapia', plan_name.lower())
    
    tutoring_sessions = int(tutoring_match.group(1)) if tutoring_match else 0
    therapy_sessions = int(therapy_match.group(1) or therapy_match.group(2)) if therapy_match else 0
    
    # Si no se encuentran en el nombre, buscar en la descripción
    if (tutoring_sessions == 0 or therapy_sessions == 0) and price_obj and price_obj.description:
        description = price_obj.description.lower()
        
        if tutoring_sessions == 0:
            tutoring_match = re.search(r'(\d+)\s+(?:sesiones?\s+)?(?:de\s+)?tutor[ií]a', description)
            tutoring_sessions = int(tutoring_match.group(1)) if tutoring_match else 0
        
        if therapy_sessions == 0:
            therapy_match = re.search(r'(\d+)\s+(?:sesiones?\s+)?(?:de\s+)?terap[ée]utic[oa]?|(\d+)\s+(?:sesiones?\s+)?(?:de\s+)?terapia', description)
            therapy_sessions = int(therapy_match.group(1) or therapy_match.group(2)) if therapy_match else 0
    
    # Si aún no se encuentran, intentar buscar el objeto price desde la base de datos
    if tutoring_sessions == 0 or therapy_sessions == 0:
        try:
            service = Service.objects.get(slug='plan-estudiante')
            price = service.prices.get(plan=plan_name)
            description = price.description.lower() if price.description else ""
            
            if tutoring_sessions == 0:
                tutoring_match = re.search(r'(\d+)\s+(?:sesiones?\s+)?(?:de\s+)?tutor[ií]a', description)
                tutoring_sessions = int(tutoring_match.group(1)) if tutoring_match else 0
            
            if therapy_sessions == 0:
                therapy_match = re.search(r'(\d+)\s+(?:sesiones?\s+)?(?:de\s+)?terap[ée]utic[oa]?|(\d+)\s+(?:sesiones?\s+)?(?:de\s+)?terapia', description)
                therapy_sessions = int(therapy_match.group(1) or therapy_match.group(2)) if therapy_match else 0
        except:
            pass
    
    # Valores por defecto si no se encuentran
    # Basados en planes típicos de estudiantes
    if tutoring_sessions == 0 and therapy_sessions == 0:
        # Determinar por palabras clave en el nombre del plan
        plan_lower = plan_name.lower()
        if 'básico' in plan_lower or 'basico' in plan_lower:
            tutoring_sessions = 4
            therapy_sessions = 4
        elif 'completo' in plan_lower or 'premium' in plan_lower or 'intensivo' in plan_lower:
            tutoring_sessions = 12
            therapy_sessions = 12
        elif 'intermedio' in plan_lower or 'medio' in plan_lower or 'estándar' in plan_lower or 'estandar' in plan_lower:
            tutoring_sessions = 8
            therapy_sessions = 8
        else:
            # Valores por defecto genéricos (2 meses)
            tutoring_sessions = 8
            therapy_sessions = 8
    
    return (tutoring_sessions, therapy_sessions)


@csrf_exempt
@require_http_methods(["POST"])
def submit_student_plan(request):
    """
    Procesa la solicitud de Plan Estudiante (con tutor y terapeuta)
    """
    try:
        data = json.loads(request.body)
        
        # Datos básicos
        service_slug = data.get('service')
        plan_name = data.get('plan')
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone', '')
        message = data.get('message', '')
        
        # Datos de programación
        preferred_tutor_id = data.get('preferred_tutor')
        preferred_therapist_id = data.get('preferred_therapist')
        tutoring_start_date_str = data.get('tutoring_start_date')
        therapy_start_date_str = data.get('therapy_start_date')
        tutoring_time = data.get('tutoring_time')
        therapy_time = data.get('therapy_time')
        
        # Ya no se reciben del formulario, se obtienen del Price
        # tutoring_sessions y therapy_sessions se obtendrán del price
        
        # Validaciones básicas
        if not all([service_slug, plan_name, name, email, preferred_tutor_id, 
                   preferred_therapist_id, tutoring_start_date_str, therapy_start_date_str,
                   tutoring_time, therapy_time]):
            return JsonResponse({
                'success': False,
                'message': 'Faltan campos requeridos'
            }, status=400)
        
        # Buscar servicio y precio
        try:
            service = Service.objects.get(slug=service_slug)
            price = service.prices.get(plan=plan_name)
        except (Service.DoesNotExist, Price.DoesNotExist):
            return JsonResponse({
                'success': False,
                'message': 'Servicio o plan no encontrado'
            }, status=404)
        
        # Usar el número de sesiones configurado en el Price por el admin
        tutoring_sessions = price.tutoring_sessions
        therapy_sessions = price.therapy_sessions
        
        # Buscar o crear cliente
        customer, created = Customer.objects.get_or_create(
            email=email,
            defaults={'name': name, 'phone': phone}
        )
        
        if not created:
            customer.name = name
            customer.phone = phone
            customer.save()
        
        # Validar tutor
        try:
            tutor = User.objects.get(id=preferred_tutor_id)
            tutor_group = Group.objects.get(name='Tutor')
            if tutor_group not in tutor.groups.all():
                return JsonResponse({
                    'success': False,
                    'message': 'El usuario seleccionado no es un tutor'
                }, status=400)
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Tutor no encontrado'
            }, status=404)
        
        # Validar terapeuta
        try:
            therapist = User.objects.get(id=preferred_therapist_id)
            # Buscar grupo Psicólogo o Terapeuta
            therapist_groups = Group.objects.filter(name__in=['Psicólogo', 'Terapeuta'])
            if not any(group in therapist.groups.all() for group in therapist_groups):
                return JsonResponse({
                    'success': False,
                    'message': 'El usuario seleccionado no es un terapeuta'
                }, status=400)
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Terapeuta no encontrado'
            }, status=404)
        
        # Procesar fechas
        try:
            tutoring_start_date = datetime.strptime(tutoring_start_date_str, '%Y-%m-%d').date()
            therapy_start_date = datetime.strptime(therapy_start_date_str, '%Y-%m-%d').date()
            
            # Validar que no sean fechas pasadas
            today = timezone.now().date()
            if tutoring_start_date < today or therapy_start_date < today:
                return JsonResponse({
                    'success': False,
                    'message': 'Las fechas de inicio no pueden ser en el pasado'
                }, status=400)
        except ValueError:
            return JsonResponse({
                'success': False,
                'message': 'Formato de fecha inválido'
            }, status=400)
        
        # Procesar horas
        try:
            hour, minute = tutoring_time.split(':')
            tutoring_time_obj = time(int(hour), int(minute))
            
            hour, minute = therapy_time.split(':')
            therapy_time_obj = time(int(hour), int(minute))
        except (ValueError, AttributeError):
            return JsonResponse({
                'success': False,
                'message': 'Formato de hora inválido'
            }, status=400)
        
        # Crear orden
        order = Order.objects.create(
            customer=customer,
            service=service,
            price=price,
            notes=message,
            status='pending',
            preferred_tutor=tutor,
            preferred_therapist=therapist,
            tutoring_start_date=tutoring_start_date,
            therapy_start_date=therapy_start_date,
            tutoring_time=tutoring_time_obj,
            therapy_time=therapy_time_obj,
            tutoring_sessions=tutoring_sessions,
            therapy_sessions=therapy_sessions
        )
        
        return JsonResponse({
            'success': True,
            'order_id': order.id,
            'message': f'Solicitud enviada correctamente. Se programarán {tutoring_sessions} sesiones de tutoría y {therapy_sessions} sesiones de terapia.',
            'tutoring_sessions': tutoring_sessions,
            'therapy_sessions': therapy_sessions
        })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Error en el formato de los datos'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al procesar la solicitud: {str(e)}'
        }, status=500)


def generate_student_plan_sessions(order, user_account=None):
    """
    Genera sesiones semanales para un Plan Estudiante
    - Crea sesiones de tutoría (1 por semana)
    - Crea sesiones de terapia (1 por semana)
    - Usa las fechas y horas específicas configuradas
    
    Args:
        order: Objeto Order de tipo Plan Estudiante
        user_account: Cuenta de usuario del cliente (opcional)
    
    Returns:
        dict con información sobre las sesiones generadas
    """
    if order.sessions_generated:
        return {
            'success': False,
            'message': 'Las sesiones ya fueron generadas para esta orden'
        }
    
    if not order.preferred_tutor or not order.preferred_therapist:
        return {
            'success': False,
            'message': 'No se han asignado tutor y terapeuta a esta orden'
        }
    
    if not order.tutoring_start_date or not order.therapy_start_date:
        return {
            'success': False,
            'message': 'No se han especificado fechas de inicio'
        }
    
    if not order.tutoring_time or not order.therapy_time:
        return {
            'success': False,
            'message': 'No se han especificado horas'
        }
    
    # Crear o buscar el usuario del cliente
    client_user = user_account
    if not client_user:
        try:
            client_user = User.objects.get(email=order.customer.email)
        except User.DoesNotExist:
            # Crear usuario para el cliente
            username = order.customer.email.split('@')[0]
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            client_user = User.objects.create_user(
                username=username,
                email=order.customer.email,
                first_name=order.customer.name.split()[0] if order.customer.name else '',
                last_name=' '.join(order.customer.name.split()[1:]) if len(order.customer.name.split()) > 1 else ''
            )
            # Asignar al grupo Cliente
            try:
                cliente_group = Group.objects.get(name='Cliente')
                client_user.groups.add(cliente_group)
            except Group.DoesNotExist:
                pass
    
    # Obtener servicios de tutoría y terapia
    try:
        tutoria_service = Service.objects.get(slug='tutoria')
        terapia_service = Service.objects.get(slug='terapia')
    except Service.DoesNotExist:
        return {
            'success': False,
            'message': 'No se encontraron los servicios de tutoría o terapia'
        }
    
    # Crear asignación con tutor
    tutoring_assignment, _ = ClientAssignment.objects.get_or_create(
        client=client_user,
        employee=order.preferred_tutor,
        service=tutoria_service,
        defaults={'is_active': True}
    )
    
    # Crear asignación con terapeuta
    therapy_assignment, _ = ClientAssignment.objects.get_or_create(
        client=client_user,
        employee=order.preferred_therapist,
        service=terapia_service,
        defaults={'is_active': True}
    )
    
    tutoring_sessions_created = []
    therapy_sessions_created = []
    
    # Generar sesiones de tutoría (1 por semana)
    current_date = order.tutoring_start_date
    for i in range(order.tutoring_sessions):
        session_datetime = timezone.make_aware(
            datetime.combine(current_date, order.tutoring_time)
        )
        
        session = Session.objects.create(
            assignment=tutoring_assignment,
            scheduled_date=session_datetime,
            duration_minutes=60,
            status='scheduled',
            notes=f'Sesión de tutoría {i + 1} de {order.tutoring_sessions} - Plan Estudiante'
        )
        
        tutoring_sessions_created.append({
            'id': session.id,
            'date': session_datetime.strftime('%Y-%m-%d'),
            'time': session_datetime.strftime('%H:%M'),
            'weekday': session_datetime.strftime('%A')
        })
        
        # Avanzar 1 semana
        current_date += timedelta(weeks=1)
    
    # Generar sesiones de terapia (1 por semana)
    current_date = order.therapy_start_date
    for i in range(order.therapy_sessions):
        session_datetime = timezone.make_aware(
            datetime.combine(current_date, order.therapy_time)
        )
        
        session = Session.objects.create(
            assignment=therapy_assignment,
            scheduled_date=session_datetime,
            duration_minutes=60,
            status='scheduled',
            notes=f'Sesión de terapia {i + 1} de {order.therapy_sessions} - Plan Estudiante'
        )
        
        therapy_sessions_created.append({
            'id': session.id,
            'date': session_datetime.strftime('%Y-%m-%d'),
            'time': session_datetime.strftime('%H:%M'),
            'weekday': session_datetime.strftime('%A')
        })
        
        # Avanzar 1 semana
        current_date += timedelta(weeks=1)
    
    # Marcar orden como con sesiones generadas
    order.sessions_generated = True
    order.status = 'confirmed'
    order.save()
    
    return {
        'success': True,
        'message': f'Se generaron {len(tutoring_sessions_created)} sesiones de tutoría y {len(therapy_sessions_created)} sesiones de terapia',
        'tutoring_sessions': tutoring_sessions_created,
        'therapy_sessions': therapy_sessions_created,
        'tutoring_assignment_id': tutoring_assignment.id,
        'therapy_assignment_id': therapy_assignment.id,
        'client_username': client_user.username
    }


@login_required
def cliente_perfil(request):
    """Vista del perfil del cliente"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Obtener o crear perfil
    from cuentas.models import UserProfile
    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={'user_type': 'cliente'}
    )
    
    context = {
        'user': request.user,
        'profile': profile
    }
    
    return render(request, 'cliente-perfil.html', context)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def update_client_profile(request):
    """API para actualizar el perfil del cliente"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'No autenticado'}, status=401)
    
    try:
        data = json.loads(request.body)
        
        # Actualizar datos del usuario
        user = request.user
        old_data = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
        }
        
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        email = data.get('email', user.email)
        
        # Verificar que el email no esté en uso por otro usuario
        if email != user.email:
            if User.objects.filter(email=email).exclude(id=user.id).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'El correo electrónico ya está en uso'
                }, status=400)
            user.email = email
        
        user.save()
        
        # Actualizar o crear perfil
        from cuentas.models import UserProfile
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={'user_type': 'cliente'}
        )
        
        old_data['phone'] = profile.phone
        old_data['address'] = profile.address
        
        profile.phone = data.get('phone', profile.phone)
        profile.address = data.get('address', profile.address)
        profile.save()
        
        # Registrar en audit log
        changes = []
        new_data = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'phone': profile.phone,
            'address': profile.address,
        }
        
        for key, old_value in old_data.items():
            new_value = new_data.get(key)
            if old_value != new_value:
                changes.append(f"{key}: '{old_value}' → '{new_value}'")
        
        if changes:
            # Obtener IP y User Agent
            ip_address = request.META.get('REMOTE_ADDR')
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            AuditLog.objects.create(
                user=user,
                action='profile_update',
                description=f"Perfil actualizado. Cambios: {', '.join(changes)}",
                ip_address=ip_address,
                user_agent=user_agent,
                related_object_type='User',
                related_object_id=user.id
            )
        
        return JsonResponse({
            'success': True,
            'message': 'Perfil actualizado correctamente',
            'data': {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'phone': profile.phone,
                'address': profile.address,
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Datos inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def change_client_password(request):
    """API para cambiar la contraseña del cliente con validación de seguridad"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'No autenticado'}, status=401)
    
    try:
        data = json.loads(request.body)
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        
        # Validar que todos los campos estén presentes
        if not all([current_password, new_password, confirm_password]):
            return JsonResponse({
                'success': False,
                'error': 'Todos los campos son requeridos'
            }, status=400)
        
        # Verificar contraseña actual
        user = request.user
        if not user.check_password(current_password):
            return JsonResponse({
                'success': False,
                'error': 'La contraseña actual es incorrecta'
            }, status=400)
        
        # Verificar que las contraseñas nuevas coincidan
        if new_password != confirm_password:
            return JsonResponse({
                'success': False,
                'error': 'Las contraseñas nuevas no coinciden'
            }, status=400)
        
        # Validar requisitos de seguridad
        from cuentas.forms import SecurePasswordValidator
        errors = SecurePasswordValidator.validate(new_password)
        if errors:
            return JsonResponse({
                'success': False,
                'error': 'La contraseña no cumple con los requisitos de seguridad',
                'validation_errors': errors
            }, status=400)
        
        # Verificar que la nueva contraseña sea diferente a la actual
        if user.check_password(new_password):
            return JsonResponse({
                'success': False,
                'error': 'La nueva contraseña debe ser diferente a la actual'
            }, status=400)
        
        # Cambiar contraseña
        user.set_password(new_password)
        user.save()
        
        # Registrar en audit log
        ip_address = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        AuditLog.objects.create(
            user=user,
            action='profile_update',
            description='Contraseña cambiada exitosamente',
            ip_address=ip_address,
            user_agent=user_agent,
            related_object_type='User',
            related_object_id=user.id
        )
        
        # Actualizar sesión para mantener al usuario logueado
        from django.contrib.auth import update_session_auth_hash
        update_session_auth_hash(request, user)
        
        return JsonResponse({
            'success': True,
            'message': 'Contraseña actualizada correctamente'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Datos inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ============================================
# EMPLOYEE REQUEST MANAGEMENT
# ============================================

@login_required
@require_http_methods(["POST"])
def accept_request(request, order_id):
    """Empleado acepta una solicitud asignada"""
    try:
        order = get_object_or_404(Order, id=order_id)
        user = request.user
        
        # Verificar que el empleado está asignado a esta orden
        is_assigned = False
        service_type = None
        
        # Verificar si es el empleado preferido (servicios individuales)
        if order.preferred_employee == user:
            is_assigned = True
            service_type = order.service.slug
        
        # Verificar si es el tutor asignado (plan estudiante)
        if order.preferred_tutor == user:
            is_assigned = True
            service_type = 'tutoria'
        
        # Verificar si es el terapeuta asignado (plan estudiante)
        if order.preferred_therapist == user:
            is_assigned = True
            service_type = 'terapia'
        
        if not is_assigned:
            return JsonResponse({
                'success': False,
                'error': 'No tienes permiso para aceptar esta solicitud'
            }, status=403)
        
        # Verificar que la orden esté en estado confirmado (aprobada por admin)
        if order.status != 'confirmed':
            return JsonResponse({
                'success': False,
                'error': 'Solo puedes aceptar solicitudes que han sido aprobadas por administración'
            }, status=400)
        
        # Cambiar estado a "en progreso"
        order.status = 'in_progress'
        order.save()
        
        # Crear o actualizar la asignación cliente-empleado
        customer_user = order.customer.user if hasattr(order.customer, 'user') else None
        
        if customer_user:
            assignment, created = ClientAssignment.objects.get_or_create(
                client=customer_user,
                employee=user,
                service=order.service,
                defaults={'is_active': True}
            )
            
            if not created and not assignment.is_active:
                assignment.is_active = True
                assignment.save()
        
        # Registrar en auditoría
        AuditLog.objects.create(
            user=user,
            action='order_updated',
            description=f'Solicitud #{order.id} aceptada por {user.get_full_name() or user.username}',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            related_object_type='Order',
            related_object_id=order.id
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Solicitud aceptada exitosamente',
            'order_id': order.id,
            'new_status': order.status
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al aceptar la solicitud: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def reject_request(request, order_id):
    """Empleado rechaza una solicitud asignada"""
    try:
        data = json.loads(request.body)
        rejection_reason = data.get('reason', 'Sin razón especificada')
        
        order = get_object_or_404(Order, id=order_id)
        user = request.user
        
        # Verificar que el empleado está asignado a esta orden
        is_assigned = False
        
        if order.preferred_employee == user or order.preferred_tutor == user or order.preferred_therapist == user:
            is_assigned = True
        
        if not is_assigned:
            return JsonResponse({
                'success': False,
                'error': 'No tienes permiso para rechazar esta solicitud'
            }, status=403)
        
        # Verificar que la orden esté en estado confirmado
        if order.status != 'confirmed':
            return JsonResponse({
                'success': False,
                'error': 'Solo puedes rechazar solicitudes que han sido aprobadas por administración'
            }, status=400)
        
        # Quitar la asignación del empleado
        if order.preferred_employee == user:
            order.preferred_employee = None
        if order.preferred_tutor == user:
            order.preferred_tutor = None
        if order.preferred_therapist == user:
            order.preferred_therapist = None
        
        # Volver a estado pendiente para que admin reasigne
        order.status = 'pending'
        order.notes = f"{order.notes or ''}\n\n[RECHAZADO por {user.get_full_name() or user.username}]: {rejection_reason}".strip()
        order.save()
        
        # Registrar en auditoría
        AuditLog.objects.create(
            user=user,
            action='order_updated',
            description=f'Solicitud #{order.id} rechazada por {user.get_full_name() or user.username}. Razón: {rejection_reason}',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            related_object_type='Order',
            related_object_id=order.id
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Solicitud rechazada. La orden volverá a estado pendiente para reasignación',
            'order_id': order.id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Datos inválidos'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al rechazar la solicitud: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_assignment_files(request, assignment_id):
    """API para obtener archivos de una asesoría específica"""
    try:
        assignment = get_object_or_404(ClientAssignment, id=assignment_id)
        
        # Verificar que el usuario tenga acceso a esta asesoría
        user_role = getattr(request.user, 'role', None)
        
        # Verificar acceso: debe ser el cliente o el empleado asignado
        if assignment.client != request.user and assignment.employee != request.user:
            # Si no es admin, denegar acceso
            if not (user_role == 'admin' or request.user.is_superuser):
                return JsonResponse({'success': False, 'error': 'No autorizado'}, status=403)
        
        # Obtener archivos de esta asesoría
        files = FileUpload.objects.filter(
            assignment=assignment
        ).select_related('uploaded_by').order_by('-uploaded_at')
        
        files_data = []
        for file in files:
            files_data.append({
                'id': file.id,
                'file_name': file.file_name,
                'file_url': file.file.url if file.file else '',
                'file_size': file.get_file_size_display(),
                'description': file.description or '',
                'uploaded_by': file.uploaded_by.get_full_name() or file.uploaded_by.username,
                'uploaded_at': file.uploaded_at.strftime('%d/%m/%Y %H:%M'),
                'can_delete': request.user == file.uploaded_by or user_role == 'admin' or request.user.is_superuser
            })
        
        return JsonResponse({
            'success': True,
            'files': files_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al cargar archivos: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def upload_file_view(request):
    """Vista para subir archivos"""
    try:
        assignment_id = request.POST.get('assignment_id')
        uploaded_file = request.FILES.get('file')
        description = request.POST.get('description', '')
        
        if not assignment_id or not uploaded_file:
            return JsonResponse({
                'success': False,
                'error': 'Faltan datos requeridos'
            }, status=400)
        
        assignment = get_object_or_404(ClientAssignment, id=assignment_id)
        
        # Verificar que el usuario tenga acceso a esta asesoría
        user_role = getattr(request.user, 'role', None)
        
        # Verificar acceso: debe ser el cliente o el empleado asignado
        if assignment.client != request.user and assignment.employee != request.user:
            # Si no es admin, denegar acceso
            if not (user_role == 'admin' or request.user.is_superuser):
                return JsonResponse({'success': False, 'error': 'No autorizado'}, status=403)
        
        # Verificar tamaño del archivo (máximo 10MB)
        if uploaded_file.size > 10 * 1024 * 1024:
            return JsonResponse({
                'success': False,
                'error': 'El archivo es demasiado grande (máximo 10MB)'
            }, status=400)
        
        # Crear el registro de archivo
        file_upload = FileUpload.objects.create(
            assignment=assignment,
            uploaded_by=request.user,
            file=uploaded_file,
            file_name=uploaded_file.name,
            file_size=uploaded_file.size,  # En bytes
            description=description
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Archivo subido exitosamente',
            'file_id': file_upload.id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al subir archivo: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def delete_file_view(request, file_id):
    """Vista para eliminar archivos"""
    try:
        file = get_object_or_404(FileUpload, id=file_id)
        
        # Verificar permisos
        user_role = getattr(request.user, 'role', None)
        if request.user != file.uploaded_by and not (user_role == 'admin' or request.user.is_superuser):
            return JsonResponse({
                'success': False,
                'error': 'No tienes permiso para eliminar este archivo'
            }, status=403)
        
        # Eliminar archivo físico
        if file.file:
            file.file.delete()
        
        # Registrar en auditoría
        AuditLog.objects.create(
            user=request.user,
            action='other',
            description=f'Archivo eliminado: {file.file_name}',
            ip_address=get_client_ip(request),
            related_object_type='FileUpload',
            related_object_id=file.id
        )
        
        file.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Archivo eliminado exitosamente'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al eliminar archivo: {str(e)}'
        }, status=500)
