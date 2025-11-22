from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import SecureUserCreationForm


def login_view(request):
    """Vista de login"""
    # Obtener información del servicio pendiente
    pending_service = request.session.get('pending_service')
    pending_plan = request.session.get('pending_plan')
    
    if request.user.is_authenticated:
        # Verificar si hay un servicio pendiente antes de redirigir
        if pending_service:
            redirect_url = '/solicitar-servicio/'
            params = []
            
            if pending_service:
                params.append(f'service={pending_service}')
            if pending_plan:
                params.append(f'plan={pending_plan}')
            
            if params:
                redirect_url += '?' + '&'.join(params)
            
            # Limpiar la sesión
            request.session.pop('pending_service', None)
            request.session.pop('pending_plan', None)
            
            messages.info(request, 'Ahora puedes completar tu solicitud de servicio.')
            return redirect(redirect_url)
        
        # Redirigir según el tipo de usuario
        return _redirect_user_dashboard(request.user)
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenido {username}!')
                
                # Verificar si hay un servicio pendiente
                if pending_service:
                    redirect_url = '/solicitar-servicio/'
                    params = []
                    
                    if pending_service:
                        params.append(f'service={pending_service}')
                    if pending_plan:
                        params.append(f'plan={pending_plan}')
                    
                    if params:
                        redirect_url += '?' + '&'.join(params)
                    
                    # Limpiar la sesión
                    request.session.pop('pending_service', None)
                    request.session.pop('pending_plan', None)
                    
                    messages.info(request, 'Ahora puedes completar tu solicitud de servicio.')
                    return redirect(redirect_url)
                
                # Redirigir según el tipo de usuario
                return _redirect_user_dashboard(user)
            else:
                messages.error(request, 'Usuario o contraseña incorrectos')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    else:
        form = AuthenticationForm()
    
    # Formatear nombres de servicio y plan para mostrar
    service_name = None
    if pending_service:
        service_mapping = {
            'tutoria': 'Tutoría',
            'terapia': 'Terapia',
            'plan-estudiante': 'Plan Estudiante'
        }
        service_name = service_mapping.get(pending_service, pending_service)
    
    context = {
        'form': form,
        'pending_service': service_name,
        'pending_plan': pending_plan.capitalize() if pending_plan else None
    }
    
    return render(request, 'login.html', context)


def _redirect_user_dashboard(user):
    """Función auxiliar para redirigir al dashboard correcto según el rol del usuario"""
    # Verificar si es superusuario
    if user.is_superuser:
        return redirect('admin_dashboard')
    
    # Verificar grupos del usuario
    if user.groups.filter(name__in=['Psicólogo', 'Psicologo']).exists():
        return redirect('psicologo_dashboard')
    elif user.groups.filter(name='Tutor').exists():
        return redirect('tutor_dashboard')
    elif user.is_staff:
        return redirect('empleado_dashboard')
    else:
        return redirect('cliente_dashboard')


def logout_view(request):
    """Vista de logout"""
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente')
    return redirect('login')


def register_view(request):
    """Vista de registro de nuevos usuarios con validación de contraseñas seguras"""
    if request.user.is_authenticated:
        return _redirect_user_dashboard(request.user)
    
    # Obtener información del servicio pendiente para mostrarla
    pending_service = request.session.get('pending_service')
    pending_plan = request.session.get('pending_plan')
    
    if request.method == 'POST':
        form = SecureUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'¡Cuenta creada exitosamente para {username}!')
            login(request, user)
            
            # Verificar si hay un servicio pendiente en la sesión
            if pending_service:
                # Construir URL de redirección con los parámetros del servicio
                redirect_url = '/solicitar-servicio/'
                params = []
                
                if pending_service:
                    params.append(f'service={pending_service}')
                if pending_plan:
                    params.append(f'plan={pending_plan}')
                
                if params:
                    redirect_url += '?' + '&'.join(params)
                
                # Limpiar la sesión
                request.session.pop('pending_service', None)
                request.session.pop('pending_plan', None)
                
                messages.info(request, 'Ahora puedes completar tu solicitud de servicio.')
                return redirect(redirect_url)
            
            # Si no hay servicio pendiente, ir al dashboard del cliente
            return redirect('cliente_dashboard')
        else:
            # Mostrar errores de validación de forma más amigable
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, error)
                    else:
                        field_label = form.fields[field].label or field
                        messages.error(request, f"{field_label}: {error}")
    else:
        form = SecureUserCreationForm()
    
    # Formatear nombres de servicio y plan para mostrar
    service_name = None
    if pending_service:
        service_mapping = {
            'tutoria': 'Tutoría',
            'terapia': 'Terapia',
            'plan-estudiante': 'Plan Estudiante'
        }
        service_name = service_mapping.get(pending_service, pending_service)
    
    context = {
        'form': form,
        'pending_service': service_name,
        'pending_plan': pending_plan.capitalize() if pending_plan else None
    }
    
    return render(request, 'register.html', context)

