from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, FileResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User, Group
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime
import json

from .models import Service, Price, Customer, Order, ClientAssignment, Session, FileUpload, AuditLog


def index(request):
    """Página principal"""
    # Obtener servicios con sus precios
    tutoria_service = Service.objects.filter(slug='tutoria').first()
    terapia_service = Service.objects.filter(slug='terapia').first()
    
    # Limitar a 3 planes de cada servicio
    tutoria_prices = tutoria_service.prices.all()[:3] if tutoria_service else []
    terapia_prices = terapia_service.prices.all()[:3] if terapia_service else []
    
    context = {
        'tutoria_service': tutoria_service,
        'terapia_service': terapia_service,
        'tutoria_prices': tutoria_prices,
        'terapia_prices': terapia_prices,
    }
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
    """Página de Plan Estudiante con todos los planes"""
    try:
        plan_estudiante = Service.objects.get(slug='plan-estudiante')
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

        if not all([service_slug, plan_name, name, email]):
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

        # Crear orden
        order = Order.objects.create(
            customer=customer,
            service=service,
            price=price,
            notes=message,
            status='pending'
        )

        return JsonResponse({
            'success': True,
            'order_id': order.id,
            'message': 'Solicitud enviada correctamente'
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


# @login_required  # Comentado temporalmente para desarrollo
def cliente_dashboard(request):
    """Dashboard del cliente"""
    # Obtener órdenes del cliente
    orders = []
    if request.user.is_authenticated:
        try:
            customer = Customer.objects.get(email=request.user.email)
            orders = customer.orders.all()
        except Customer.DoesNotExist:
            orders = []
    
    return render(request, 'cliente-dashboard.html', {'orders': orders})


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
    
    # Obtener todas las sesiones del cliente
    sessions = Session.objects.filter(
        assignment__client=client
    ).select_related('assignment__employee', 'assignment__service').order_by('-scheduled_date')
    
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
        'progress': round(progress, 1),
        'main_assignment': main_assignment,
    }
    
    return render(request, 'auditoria-estudiante.html', context)


def get_client_details(request, client_id):
    """API para obtener detalles de un cliente en formato JSON"""
    try:
        client = User.objects.get(id=client_id)
        
        # Obtener asignaciones del cliente
        assignments = ClientAssignment.objects.filter(
            client=client,
            is_active=True
        ).select_related('employee', 'service')
        
        # Obtener sesiones
        sessions = Session.objects.filter(
            assignment__client=client
        ).select_related('assignment__service', 'assignment__employee').order_by('-scheduled_date')
        
        # Calcular estadísticas
        total_sessions = sessions.count()
        completed_sessions = sessions.filter(status='completed').count()
        scheduled_sessions = sessions.filter(Q(status='scheduled') | Q(status='confirmed')).count()
        progress = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
        
        # Obtener última sesión
        last_session = sessions.filter(status='completed').first()
        
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


# @login_required  # Comentado temporalmente para desarrollo
def psicologo_dashboard(request):
    """Dashboard del psicólogo"""
    # Obtener clientes asignados al psicólogo actual
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
    
    return render(request, 'psicologo-dashboard.html', context)


# @login_required  # Comentado temporalmente para desarrollo
def tutor_dashboard(request):
    """Dashboard del tutor"""
    # Obtener clientes asignados al tutor actual
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
    
    return render(request, 'tutor-dashboard.html', context)


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
    # Obtener todos los datos necesarios
    services = Service.objects.all()
    groups = Group.objects.all()
    employees = User.objects.filter(Q(is_staff=True) | Q(groups__isnull=False)).distinct()
    
    # Obtener clientes con estadísticas anotadas
    clients = User.objects.filter(groups__name='Cliente').annotate(
        active_assignments_count=Count(
            'client_assignments',
            filter=Q(client_assignments__is_active=True)
        ),
        total_sessions=Count('client_assignments__sessions'),
        files_count=Count('client_assignments__files'),
        audit_count=Count('audit_logs')
    )
    
    assignments = ClientAssignment.objects.select_related('client', 'employee', 'service').all()
    sessions = Session.objects.select_related('assignment__client', 'assignment__employee').all()[:50]
    files = FileUpload.objects.select_related('assignment', 'uploaded_by').all()[:50]
    audit_logs = AuditLog.objects.select_related('user').all()[:100]
    
    context = {
        'services': services,
        'groups': groups,
        'employees': employees,
        'clients': clients,
        'assignments': assignments,
        'sessions': sessions,
        'files': files,
        'audit_logs': audit_logs,
    }
    
    return render(request, 'admin-dashboard.html', context)


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def admin_create_price(request):
    """Crear un nuevo precio"""
    try:
        servicio_id = request.POST.get('servicio')
        plan = request.POST.get('plan', '').strip()
        precio = request.POST.get('precio')
        moneda = request.POST.get('moneda', 'CLP')
        descripcion = request.POST.get('descripcion', '').strip()
        
        if not all([servicio_id, plan, precio]):
            messages.error(request, 'Faltan campos requeridos')
            return redirect('admin_dashboard')
        
        service = get_object_or_404(Service, id=servicio_id)
        
        price = Price.objects.create(
            service=service,
            plan=plan,
            price=precio,
            currency=moneda,
            description=descripcion
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
        
        messages.success(request, f'Precio "{plan}" creado exitosamente')
        
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
            
            if not all([servicio_id, plan, precio]):
                messages.error(request, 'Faltan campos requeridos')
                return redirect('admin_dashboard')
            
            service = get_object_or_404(Service, id=servicio_id)
            
            old_info = f"{price.plan} - ${price.price} {price.currency}"
            
            price.service = service
            price.plan = plan
            price.price = precio
            price.currency = moneda
            price.description = descripcion
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
