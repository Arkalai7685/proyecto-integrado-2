from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('quienes-somos/', views.quienes_somos, name='quienes_somos'),
    path('testimonios/', views.testimonios, name='testimonios'),
    path('tutoria/', views.tutoria, name='tutoria'),
    path('terapia/', views.terapia, name='terapia'),
    path('plan-estudiante/', views.plan_estudiante, name='plan_estudiante'),
    path('solicitar-servicio/', views.solicitar_servicio, name='solicitar_servicio'),
    path('api/submit-order/', views.submit_order, name='submit_order'),
    path('cliente/dashboard/', views.cliente_dashboard, name='cliente_dashboard'),
    path('empleado/dashboard/', views.empleado_dashboard, name='empleado_dashboard'),
    path('psicologo/dashboard/', views.psicologo_dashboard, name='psicologo_dashboard'),
    path('tutor/dashboard/', views.tutor_dashboard, name='tutor_dashboard'),
    path('auditoria-estudiante/', views.auditoria_estudiante, name='auditoria_estudiante'),
    path('api/client/<int:client_id>/details/', views.get_client_details, name='get_client_details'),
    path('api/session/<int:session_id>/update-status/', views.update_session_status, name='update_session_status'),
    
    # Admin Dashboard URLs
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/precio/crear/', views.admin_create_price, name='admin_create_price'),
    path('admin/precio/editar/<int:price_id>/', views.admin_edit_price, name='admin_edit_price'),
    path('admin/precio/eliminar/<int:price_id>/', views.admin_delete_price, name='admin_delete_price'),
    path('admin/empleado/crear/', views.admin_create_employee, name='admin_create_employee'),
    path('admin/empleado/toggle/<int:employee_id>/', views.admin_toggle_employee, name='admin_toggle_employee'),
    path('admin/asignacion/crear/', views.admin_create_assignment, name='admin_create_assignment'),
    path('admin/asignacion/toggle/<int:assignment_id>/', views.admin_toggle_assignment, name='admin_toggle_assignment'),
    path('admin/sesion/crear/', views.admin_create_session, name='admin_create_session'),
    path('admin/archivo/eliminar/<int:file_id>/', views.admin_delete_file, name='admin_delete_file'),
]
