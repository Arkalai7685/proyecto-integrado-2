"""
Vistas para el sistema de chat interno
"""
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count, Max
from .models import ChatMessage, ClientAssignment, FileUpload
from django.core.files.uploadedfile import InMemoryUploadedFile
import os


@login_required
def get_chat_conversations(request):
    """Obtener lista de conversaciones del usuario (empleado o cliente)"""
    try:
        user = request.user
        
        # Verificar si es empleado o cliente
        employee_assignments = ClientAssignment.objects.filter(
            employee=user, 
            is_active=True
        ).select_related('client', 'service')
        
        client_assignments = ClientAssignment.objects.filter(
            client=user,
            is_active=True
        ).select_related('employee', 'service')
        
        conversations = []
        
        # Si es empleado, listar sus clientes
        if employee_assignments.exists():
            for assignment in employee_assignments:
                unread_count = ChatMessage.objects.filter(
                    assignment=assignment,
                    is_read=False
                ).exclude(sender=user).count()
                
                last_message = ChatMessage.objects.filter(
                    assignment=assignment
                ).order_by('-created_at').first()
                
                conversations.append({
                    'assignment_id': assignment.id,
                    'client_id': assignment.client.id,
                    'client_name': assignment.client.get_full_name() or assignment.client.username,
                    'service_name': assignment.service.name,
                    'unread_count': unread_count,
                    'last_message': last_message.message[:50] if last_message else '',
                    'last_message_time': last_message.created_at.strftime('%d/%m/%Y %H:%M') if last_message else ''
                })
        
        # Si es cliente, listar sus empleados
        elif client_assignments.exists():
            for assignment in client_assignments:
                unread_count = ChatMessage.objects.filter(
                    assignment=assignment,
                    is_read=False
                ).exclude(sender=user).count()
                
                last_message = ChatMessage.objects.filter(
                    assignment=assignment
                ).order_by('-created_at').first()
                
                conversations.append({
                    'assignment_id': assignment.id,
                    'employee_id': assignment.employee.id,
                    'employee_name': assignment.employee.get_full_name() or assignment.employee.username,
                    'service_name': assignment.service.name,
                    'unread_count': unread_count,
                    'last_message': last_message.message[:50] if last_message else '',
                    'last_message_time': last_message.created_at.strftime('%d/%m/%Y %H:%M') if last_message else ''
                })
        
        return JsonResponse({
            'success': True,
            'conversations': conversations
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def get_chat_messages(request, assignment_id):
    """Obtener mensajes de una conversación específica"""
    try:
        assignment = get_object_or_404(ClientAssignment, id=assignment_id)
        
        # Verificar que el usuario tiene acceso a esta conversación
        if request.user != assignment.client and request.user != assignment.employee:
            return JsonResponse({
                'success': False,
                'error': 'No tienes permiso para ver esta conversación'
            }, status=403)
        
        # Obtener mensajes
        messages = ChatMessage.objects.filter(
            assignment=assignment
        ).select_related('sender').order_by('created_at')
        
        messages_data = []
        for msg in messages:
            messages_data.append({
                'id': msg.id,
                'sender_id': msg.sender.id,
                'sender_name': msg.sender.get_full_name() or msg.sender.username,
                'message': msg.message,
                'is_read': msg.is_read,
                'created_at': msg.created_at.strftime('%d/%m/%Y %H:%M'),
                'is_mine': msg.sender == request.user
            })
        
        # Marcar mensajes como leídos
        ChatMessage.objects.filter(
            assignment=assignment,
            is_read=False
        ).exclude(sender=request.user).update(is_read=True)
        
        # Información del interlocutor
        other_user = assignment.employee if request.user == assignment.client else assignment.client
        
        return JsonResponse({
            'success': True,
            'messages': messages_data,
            'other_user': {
                'id': other_user.id,
                'name': other_user.get_full_name() or other_user.username
            },
            'service_name': assignment.service.name
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def send_chat_message(request, assignment_id):
    """Enviar un mensaje de chat"""
    try:
        assignment = get_object_or_404(ClientAssignment, id=assignment_id)
        
        # Verificar permisos
        if request.user != assignment.client and request.user != assignment.employee:
            return JsonResponse({
                'success': False,
                'error': 'No tienes permiso para enviar mensajes en esta conversación'
            }, status=403)
        
        import json
        data = json.loads(request.body)
        message_text = data.get('message', '').strip()
        
        if not message_text:
            return JsonResponse({
                'success': False,
                'error': 'El mensaje no puede estar vacío'
            }, status=400)
        
        # Crear mensaje
        message = ChatMessage.objects.create(
            assignment=assignment,
            sender=request.user,
            message=message_text
        )
        
        return JsonResponse({
            'success': True,
            'message': {
                'id': message.id,
                'sender_id': message.sender.id,
                'sender_name': message.sender.get_full_name() or message.sender.username,
                'message': message.message,
                'created_at': message.created_at.strftime('%d/%m/%Y %H:%M'),
                'is_mine': True
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def get_unread_messages_count(request):
    """Obtener contador de mensajes no leídos"""
    try:
        unread_count = ChatMessage.objects.filter(
            Q(assignment__client=request.user) | Q(assignment__employee=request.user),
            is_read=False
        ).exclude(sender=request.user).count()
        
        return JsonResponse({
            'success': True,
            'unread_count': unread_count
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def upload_file_to_client(request):
    """Empleado sube archivo para cliente"""
    try:
        # Verificar que es empleado
        user_profile = request.user.profile
        if user_profile.user_type not in ['tutor', 'psicologo', 'admin']:
            return JsonResponse({
                'success': False,
                'error': 'Solo empleados pueden subir archivos'
            }, status=403)
        
        assignment_id = request.POST.get('assignment_id')
        description = request.POST.get('description', '').strip()
        uploaded_file = request.FILES.get('file')
        
        if not assignment_id or not uploaded_file:
            return JsonResponse({
                'success': False,
                'error': 'Faltan campos requeridos'
            }, status=400)
        
        # Verificar asignación
        assignment = get_object_or_404(ClientAssignment, id=assignment_id)
        
        if assignment.employee != request.user:
            return JsonResponse({
                'success': False,
                'error': 'No tienes permiso para subir archivos a esta asignación'
            }, status=403)
        
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
        
        # Validar tamaño (10MB)
        max_size = 10 * 1024 * 1024
        if uploaded_file.size > max_size:
            return JsonResponse({
                'success': False,
                'error': 'El archivo es demasiado grande. Tamaño máximo: 10MB'
            }, status=400)
        
        # Crear registro de archivo
        file_upload = FileUpload.objects.create(
            assignment=assignment,
            uploaded_by=request.user,
            file=uploaded_file,
            file_name=uploaded_file.name,
            file_type=file_type,
            file_size=uploaded_file.size,
            description=description or f'Archivo compartido por {request.user.get_full_name() or request.user.username}'
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Archivo subido exitosamente',
            'file': {
                'id': file_upload.id,
                'file_name': file_upload.file_name,
                'file_size': file_upload.get_file_size_display(),
                'uploaded_at': file_upload.uploaded_at.strftime('%d/%m/%Y %H:%M')
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
