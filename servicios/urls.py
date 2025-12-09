from django.urls import path
from . import views
from . import file_views
from . import chat_views

urlpatterns = [
    path('', views.index, name='index'),
    path('quienes-somos/', views.quienes_somos, name='quienes_somos'),
    path('testimonios/', views.testimonios, name='testimonios'),
    path('tutoria/', views.tutoria, name='tutoria'),
    path('terapia/', views.terapia, name='terapia'),
    path('plan-estudiante/', views.plan_estudiante, name='plan_estudiante'),
    path('solicitar-servicio/', views.solicitar_servicio, name='solicitar_servicio'),
    path('solicitar-plan-estudiante/', views.solicitar_plan_estudiante, name='solicitar_plan_estudiante'),
    path('api/submit-order/', views.submit_order, name='submit_order'),
    path('api/submit-student-plan/', views.submit_student_plan, name='submit_student_plan'),
    path('api/available-employees/', views.get_available_employees, name='get_available_employees'),
    path('cliente/dashboard/', views.cliente_dashboard, name='cliente_dashboard'),
    path('cliente/perfil/', views.cliente_perfil, name='cliente_perfil'),
    path('api/cliente/actualizar-perfil/', views.update_client_profile, name='update_client_profile'),
    path('api/cliente/cambiar-contrasena/', views.change_client_password, name='change_client_password'),
    path('empleado/dashboard/', views.empleado_dashboard, name='empleado_dashboard'),
    path('psicologo/dashboard/', views.psicologo_dashboard, name='psicologo_dashboard'),
    path('tutor/dashboard/', views.tutor_dashboard, name='tutor_dashboard'),
    path('auditoria-estudiante/', views.auditoria_estudiante, name='auditoria_estudiante'),
    path('api/client/<int:client_id>/details/', views.get_client_details, name='get_client_details'),
    path('api/client/<int:client_id>/assignment/', views.get_client_assignment, name='get_client_assignment'),
    path('api/session/<int:session_id>/update-status/', views.update_session_status, name='update_session_status'),
    
    # Admin Dashboard URLs
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/servicio/crear/', views.admin_create_service, name='admin_create_service'),
    path('admin/servicio/eliminar/<int:service_id>/', views.admin_delete_service, name='admin_delete_service'),
    path('admin/precio/crear/', views.admin_create_price, name='admin_create_price'),
    path('admin/precio/editar/<int:price_id>/', views.admin_edit_price, name='admin_edit_price'),
    path('admin/precio/eliminar/<int:price_id>/', views.admin_delete_price, name='admin_delete_price'),
    path('admin/precio/toggle-featured/<int:price_id>/', views.admin_toggle_featured, name='admin_toggle_featured'),
    path('admin/empleado/crear/', views.admin_create_employee, name='admin_create_employee'),
    path('admin/empleado/toggle/<int:employee_id>/', views.admin_toggle_employee, name='admin_toggle_employee'),
    path('admin/empleado/editar/<int:employee_id>/', views.admin_edit_employee, name='admin_edit_employee'),
    path('admin/empleado/eliminar/<int:employee_id>/', views.admin_delete_employee, name='admin_delete_employee'),
    path('admin/empleado/datos/<int:employee_id>/', views.admin_get_employee_data, name='admin_get_employee_data'),
    path('admin/cliente/editar/<int:client_id>/', views.admin_edit_client, name='admin_edit_client'),
    path('admin/cliente/eliminar/<int:client_id>/', views.admin_delete_client, name='admin_delete_client'),
    path('admin/cliente/datos/<int:client_id>/', views.admin_get_client_data, name='admin_get_client_data'),
    path('admin/asignacion/crear/', views.admin_create_assignment, name='admin_create_assignment'),
    path('admin/asignacion/toggle/<int:assignment_id>/', views.admin_toggle_assignment, name='admin_toggle_assignment'),
    path('admin/sesion/crear/', views.admin_create_session, name='admin_create_session'),
    path('admin/archivo/eliminar/<int:file_id>/', views.admin_delete_file, name='admin_delete_file'),
    path('admin/orden/<int:order_id>/generar-sesiones/', views.admin_generate_sessions, name='admin_generate_sessions'),
    
    # File Management URLs (legacy - from file_views)
    path('api/file/download/<int:file_id>/', file_views.download_file, name='download_file'),
    path('api/file/delete/<int:file_id>/', file_views.delete_file, name='delete_file'),
    path('api/file/list/', file_views.list_files, name='list_files'),
    
    # Employee Request Management URLs
    path('accept-request/<int:order_id>/', views.accept_request, name='accept_request'),
    path('reject-request/<int:order_id>/', views.reject_request, name='reject_request'),
    
    # Chat URLs
    path('api/chat/conversations/', chat_views.get_chat_conversations, name='get_chat_conversations'),
    path('api/chat/<int:assignment_id>/messages/', chat_views.get_chat_messages, name='get_chat_messages'),
    path('api/chat/<int:assignment_id>/send/', chat_views.send_chat_message, name='send_chat_message'),
    path('api/chat/unread-count/', chat_views.get_unread_messages_count, name='get_unread_messages_count'),
    path('api/chat/upload-file/', chat_views.upload_file_to_client, name='upload_file_to_client'),
    
    # Assignment Files URLs (new - client and employee file management)
    path('api/assignment/<int:assignment_id>/files/', views.get_assignment_files, name='get_assignment_files'),
    path('api/file/upload/', views.upload_file_view, name='upload_file'),
    path('api/file/delete/<int:file_id>/', views.delete_file_view, name='delete_file_view'),
]
