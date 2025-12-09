"""
Vistas para el sistema de gestión de archivos
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, FileResponse
from django.views.decorators.http import require_http_methods
from .models import FileUpload, ClientAssignment, Session, AuditLog


def get_client_ip(request):
    """Obtener IP del cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@login_required
@require_http_methods(["POST"])
def upload_file(request):
    """Subir un archivo (cliente o empleado)"""
    try:
        assignment_id = request.POST.get('assignment_id')
        session_id = request.POST.get('session_id')
        description = request.POST.get('description', '').strip()
        uploaded_file = request.FILES.get('file')
        
        if not assignment_id or not uploaded_file:
            return JsonResponse({'success': False, 'error': 'Faltan campos requeridos'}, status=400)
        
        # Verificar que el usuario tiene acceso a esta asignación
        assignment = get_object_or_404(ClientAssignment, id=assignment_id)
        
        # Verificar permisos
        user_profile = request.user.profile
        if user_profile.user_type == 'cliente':
            if assignment.client != request.user:
                return JsonResponse({'success': False, 'error': 'No tienes permiso para subir archivos a esta asignación'}, status=403)
        elif user_profile.user_type in ['tutor', 'psicologo']:
            if assignment.employee != request.user:
                return JsonResponse({'success': False, 'error': 'No tienes permiso para subir archivos a esta asignación'}, status=403)
        else:
            return JsonResponse({'success': False, 'error': 'Rol no autorizado'}, status=403)
        
        # Verificar sesión si se proporcionó
        session = None
        if session_id:
            session = get_object_or_404(Session, id=session_id, assignment=assignment)
        
        # Determinar tipo de archivo
        file_extension = uploaded_file.name.split('.')[-1].lower()
        file_type = 'other'
        if file_extension in ['pdf', 'doc', 'docx', 'txt', 'odt', 'rtf']:
            file_type = 'document'
        elif file_extension in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp']:
            file_type = 'image'
        elif file_extension in ['mp3', 'wav', 'ogg', 'm4a', 'flac']:
            file_type = 'audio'
        elif file_extension in ['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm']:
            file_type = 'video'
        
        # Validar tamaño (10MB máximo)
        max_size = 10 * 1024 * 1024  # 10MB
        if uploaded_file.size > max_size:
            return JsonResponse({
                'success': False, 
                'error': f'Archivo demasiado grande. Máximo permitido: 10MB. Tamaño actual: {uploaded_file.size / (1024*1024):.2f}MB'
            }, status=400)
        
        # Validar extensión de archivo
        allowed_extensions = ['pdf', 'doc', 'docx', 'txt', 'odt', 'rtf', 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp', 'mp3', 'wav', 'ogg', 'm4a', 'flac', 'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'zip', 'rar']
        if file_extension not in allowed_extensions:
            return JsonResponse({
                'success': False,
                'error': f'Tipo de archivo no permitido. Extensión "{file_extension}" no está en la lista de formatos aceptados.'
            }, status=400)
        
        # Crear el registro de archivo
        file_upload = FileUpload.objects.create(
            assignment=assignment,
            session=session,
            uploaded_by=request.user,
            file=uploaded_file,
            file_name=uploaded_file.name,
            file_type=file_type,
            file_size=uploaded_file.size,
            description=description
        )
        
        # Registrar en auditoría
        AuditLog.objects.create(
            user=request.user,
            action='other',
            description=f'Archivo subido: {uploaded_file.name} ({file_upload.get_file_size_display()}) a {assignment.client.get_full_name() or assignment.client.username}',
            ip_address=get_client_ip(request),
            related_object_type='FileUpload',
            related_object_id=file_upload.id
        )
        
        messages.success(request, f'Archivo "{uploaded_file.name}" subido exitosamente')
        
        return JsonResponse({
            'success': True,
            'file_id': file_upload.id,
            'file_name': file_upload.file_name,
            'file_size': file_upload.get_file_size_display(),
            'uploaded_at': file_upload.uploaded_at.strftime('%d/%m/%Y %H:%M')
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def download_file(request, file_id):
    """Descargar un archivo"""
    try:
        file_upload = get_object_or_404(FileUpload, id=file_id)
        
        # Verificar permisos
        assignment = file_upload.assignment
        
        has_permission = False
        
        # Cliente: puede descargar si es su asignación
        if assignment.client == request.user:
            has_permission = True
        # Empleado: puede descargar si es el empleado asignado
        elif assignment.employee == request.user:
            has_permission = True
        # Admin/Staff: puede descargar todo
        elif request.user.is_staff or request.user.is_superuser:
            has_permission = True
        
        if not has_permission:
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden('No tienes permiso para descargar este archivo')
        
        # Registrar descarga en auditoría
        AuditLog.objects.create(
            user=request.user,
            action='other',
            description=f'Archivo descargado: {file_upload.file_name}',
            ip_address=get_client_ip(request),
            related_object_type='FileUpload',
            related_object_id=file_upload.id
        )
        
        # Servir el archivo
        response = FileResponse(file_upload.file.open('rb'), as_attachment=True, filename=file_upload.file_name)
        return response
        
    except FileUpload.DoesNotExist:
        from django.http import HttpResponseNotFound
        return HttpResponseNotFound('Archivo no encontrado')
    except Exception as e:
        from django.http import HttpResponseServerError
        return HttpResponseServerError(f'Error al descargar archivo: {str(e)}')


@login_required
@require_http_methods(["POST"])
def delete_file(request, file_id):
    """Eliminar un archivo"""
    try:
        file_upload = get_object_or_404(FileUpload, id=file_id)
        
        # Solo el que subió el archivo o admin puede eliminarlo
        user_profile = request.user.profile
        if file_upload.uploaded_by != request.user and user_profile.user_type != 'admin':
            return JsonResponse({'success': False, 'error': 'No tienes permiso para eliminar este archivo'}, status=403)
        
        file_name = file_upload.file_name
        
        # Eliminar el archivo físico
        if file_upload.file:
            file_upload.file.delete()
        
        # Registrar en auditoría antes de eliminar
        AuditLog.objects.create(
            user=request.user,
            action='other',
            description=f'Archivo eliminado: {file_name}',
            ip_address=get_client_ip(request)
        )
        
        file_upload.delete()
        
        return JsonResponse({'success': True, 'message': f'Archivo "{file_name}" eliminado'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def list_files(request):
    """Listar archivos del usuario (cliente o empleado)"""
    try:
        # Asegurar que existe el perfil
        try:
            user_profile = request.user.profile
        except:
            from cuentas.models import UserProfile
            user_profile = UserProfile.objects.create(user=request.user, user_type='cliente')
        
        client_id = request.GET.get('client_id')
        
        # Validar client_id si se proporciona
        if client_id:
            try:
                client_id = int(client_id)
            except (ValueError, TypeError):
                return JsonResponse({
                    'success': False, 
                    'error': 'ID de cliente inválido'
                }, status=400)
        
        # Detectar el rol real basándose en las asignaciones
        is_employee = ClientAssignment.objects.filter(employee=request.user).exists()
        is_client = ClientAssignment.objects.filter(client=request.user).exists()
        
        # Validar y corregir inconsistencias
        if is_employee and user_profile.user_type not in ['tutor', 'psicologo', 'admin']:
            print(f"WARNING: Usuario {request.user.username} es empleado pero tiene user_type='{user_profile.user_type}'")
            # Determinar el tipo correcto
            first_assignment = ClientAssignment.objects.filter(employee=request.user).first()
            if first_assignment:
                correct_type = 'tutor' if first_assignment.service.name in ['Tutoría', 'Tutoria'] else 'psicologo'
                print(f"   Tipo correcto debería ser: {correct_type}")
        
        # Obtener archivos según el rol real (priorizar empleado sobre cliente)
        if is_employee:
            assignments = ClientAssignment.objects.filter(employee=request.user)
            
            if client_id:
                try:
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    client = User.objects.get(id=client_id)
                    assignments = assignments.filter(client=client)
                except (User.DoesNotExist, ValueError, TypeError):
                    # client_id inválido - devolver lista vacía en lugar de error
                    return JsonResponse({'success': True, 'files': []})
            
            files = FileUpload.objects.filter(assignment__in=assignments).select_related(
                'uploaded_by', 'assignment', 'session'
            ).order_by('-uploaded_at')
            
        elif is_client:
            assignments = ClientAssignment.objects.filter(client=request.user)
            files = FileUpload.objects.filter(assignment__in=assignments).select_related(
                'uploaded_by', 'assignment', 'session'
            ).order_by('-uploaded_at')
        else:
            # Usuario sin asignaciones - devolver lista vacía
            return JsonResponse({'success': True, 'files': []})
        
        files_data = []
        for file in files:
            files_data.append({
                'id': file.id,
                'file_name': file.file_name,
                'file_type': file.file_type,
                'file_size': file.get_file_size_display(),
                'description': file.description or '',
                'uploaded_by': file.uploaded_by.get_full_name() or file.uploaded_by.username,
                'uploaded_at': file.uploaded_at.strftime('%d/%m/%Y %H:%M'),
                'can_delete': file.uploaded_by == request.user,
                'assignment_client': file.assignment.client.get_full_name() or file.assignment.client.username,
                'assignment_service': file.assignment.service.name
            })
        
        return JsonResponse({'success': True, 'files': files_data})
        
    except Exception as e:
        # Log del error para debugging
        import traceback
        print(f"ERROR en list_files: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
