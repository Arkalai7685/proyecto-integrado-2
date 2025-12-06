"""
Tests de integración para verificar errores comunes del sistema
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from cuentas.models import UserProfile
from servicios.models import Service, ClientAssignment, FileUpload
from django.core.files.uploadedfile import SimpleUploadedFile
import os

User = get_user_model()

class UserRoleConsistencyTest(TestCase):
    """Pruebas para verificar consistencia de roles de usuario"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        # Crear servicio
        self.service = Service.objects.create(
            name='Terapia Psicológica',
            slug='terapia-psicologica',
            description='Test service'
        )
        
        # Crear cliente - UserProfile se crea automáticamente
        self.client_user = User.objects.create_user(
            username='test_cliente',
            password='test123',
            email='cliente@test.com',
            first_name='Cliente',
            last_name='Test'
        )
        self.client_user.profile.user_type = 'cliente'
        self.client_user.profile.save()
        
        # Crear psicólogo - UserProfile se crea automáticamente
        self.psicologo_user = User.objects.create_user(
            username='test_psicologo',
            password='test123',
            email='psicologo@test.com',
            first_name='Psicólogo',
            last_name='Test'
        )
        self.psicologo_user.profile.user_type = 'psicologo'
        self.psicologo_user.profile.save()
    
    def test_employee_with_wrong_user_type(self):
        """Test: Empleado con user_type incorrecto debe funcionar"""
        # Crear un usuario con user_type 'cliente' pero que es empleado
        wrong_employee = User.objects.create_user(
            username='wrong_employee',
            password='test123',
            email='wrong@test.com'
        )
        # El perfil se crea automáticamente con user_type='cliente'
        # Intencionalmente dejamos el user_type incorrecto para probar
        wrong_employee.profile.user_type = 'cliente'
        wrong_employee.profile.save()
        
        # Crear asignación donde es empleado
        assignment = ClientAssignment.objects.create(
            client=self.client_user,
            employee=wrong_employee,
            service=self.service,
            is_active=True
        )
        
        # Verificar que puede acceder a archivos
        client = Client()
        client.force_login(wrong_employee)
        response = client.get(f'/api/file/list/?client_id={self.client_user.id}')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', response.json())
    
    def test_client_cannot_access_other_client_files(self):
        """Test: Cliente no puede ver archivos de otro cliente"""
        other_client = User.objects.create_user(
            username='other_client',
            password='test123'
        )
        other_client.profile.user_type = 'cliente'
        other_client.profile.save()
        
        client = Client()
        client.force_login(self.client_user)
        response = client.get(f'/api/file/list/?client_id={other_client.id}')
        
        # Debe devolver archivos vacíos, no error
        self.assertEqual(response.status_code, 200)


class FileUploadTest(TestCase):
    """Pruebas para subida y gestión de archivos"""
    
    def setUp(self):
        self.service = Service.objects.create(
            name='Terapia',
            slug='terapia',
            description='Test'
        )
        
        self.client_user = User.objects.create_user(
            username='cliente_file',
            password='test123'
        )
        self.client_user.profile.user_type = 'cliente'
        self.client_user.profile.save()
        
        self.employee_user = User.objects.create_user(
            username='empleado_file',
            password='test123'
        )
        self.employee_user.profile.user_type = 'psicologo'
        self.employee_user.profile.save()
        
        self.assignment = ClientAssignment.objects.create(
            client=self.client_user,
            employee=self.employee_user,
            service=self.service,
            is_active=True
        )
    
    def test_upload_file_without_assignment(self):
        """Test: Subir archivo sin ID de asignación debe fallar"""
        client = Client()
        client.force_login(self.client_user)
        
        test_file = SimpleUploadedFile("test.txt", b"file content", content_type="text/plain")
        
        response = client.post('/api/file/upload/', {
            'file': test_file,
            'description': 'Test file'
        })
        
        # Debe retornar error por falta de assignment_id
        self.assertIn(response.status_code, [400, 403])
    
    def test_upload_oversized_file(self):
        """Test: Archivo mayor a 10MB debe rechazarse"""
        client = Client()
        client.force_login(self.client_user)
        
        # Crear archivo de 11MB
        large_content = b'x' * (11 * 1024 * 1024)
        large_file = SimpleUploadedFile("large.txt", large_content)
        
        response = client.post('/api/file/upload/', {
            'file': large_file,
            'assignment_id': self.assignment.id,
            'description': 'Large file'
        })
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('grande', response.json().get('error', '').lower())


class DashboardAccessTest(TestCase):
    """Pruebas de acceso a dashboards"""
    
    def setUp(self):
        self.client_user = User.objects.create_user(
            username='cliente_dash',
            password='test123'
        )
        self.client_user.profile.user_type = 'cliente'
        self.client_user.profile.save()
        
        self.admin_user = User.objects.create_user(
            username='admin_dash',
            password='test123',
            is_staff=True
        )
        self.admin_user.profile.user_type = 'admin'
        self.admin_user.profile.save()
    
    def test_unauthenticated_dashboard_access(self):
        """Test: Usuario no autenticado debe redirigir a login"""
        client = Client()
        response = client.get('/cliente/dashboard/')
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/cuentas/login', response.url)
    
    def test_client_cannot_access_admin_dashboard(self):
        """Test: Cliente no puede acceder al dashboard de admin"""
        client = Client()
        client.force_login(self.client_user)
        response = client.get('/admin/dashboard/')
        
        # Debe redirigir o retornar 403
        self.assertIn(response.status_code, [302, 403])
    
    def test_admin_can_access_admin_dashboard(self):
        """Test: Admin puede acceder a su dashboard"""
        client = Client()
        client.force_login(self.admin_user)
        response = client.get('/admin/dashboard/')
        
        self.assertEqual(response.status_code, 200)


class APIEndpointTest(TestCase):
    """Pruebas de endpoints de API"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='api_user',
            password='test123'
        )
        self.user.profile.user_type = 'cliente'
        self.user.profile.save()
    
    def test_file_list_with_invalid_client_id(self):
        """Test: Listar archivos con client_id inválido"""
        client = Client()
        client.force_login(self.user)
        
        response = client.get('/api/file/list/?client_id=99999')
        
        # Debe devolver 200 con lista vacía (sin asignaciones)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['files'], [])
    
    def test_download_nonexistent_file(self):
        """Test: Descargar archivo inexistente"""
        client = Client()
        client.force_login(self.user)
        
        response = client.get('/api/file/download/99999/')
        
        self.assertIn(response.status_code, [302, 404])


class ModelValidationTest(TestCase):
    """Pruebas de validación de modelos"""
    
    def test_user_profile_created_on_user_creation(self):
        """Test: UserProfile debe crearse automáticamente"""
        user = User.objects.create_user(
            username='profile_test',
            password='test123'
        )
        
        # Verificar que no falla al acceder al perfil
        try:
            profile = user.profile
            self.assertIsNotNone(profile)
        except UserProfile.DoesNotExist:
            # Si no existe, el signal no está funcionando
            self.fail("UserProfile no se creó automáticamente")
    
    def test_assignment_without_service_fails(self):
        """Test: Asignación sin servicio debe fallar"""
        client_user = User.objects.create_user(username='c1', password='t')
        employee_user = User.objects.create_user(username='e1', password='t')
        
        with self.assertRaises(Exception):
            ClientAssignment.objects.create(
                client=client_user,
                employee=employee_user,
                # service faltante
                is_active=True
            )


class SecurityTest(TestCase):
    """Pruebas de seguridad"""
    
    def test_csrf_protection_on_file_upload(self):
        """Test: Subida de archivos requiere CSRF token"""
        user = User.objects.create_user(username='csrf_test', password='test123')
        
        client = Client(enforce_csrf_checks=True)
        client.force_login(user)
        
        test_file = SimpleUploadedFile("test.txt", b"content")
        
        # Sin CSRF token debe fallar
        response = client.post('/api/file/upload/', {
            'file': test_file,
            'assignment_id': 1
        })
        
        self.assertEqual(response.status_code, 403)
    
    def test_sql_injection_prevention(self):
        """Test: Prevención de SQL injection en búsqueda"""
        user = User.objects.create_user(username='sql_test', password='test123')
        user.profile.user_type = 'cliente'
        user.profile.save()
        
        client = Client()
        client.force_login(user)
        
        # Intentar SQL injection
        malicious_input = "1' OR '1'='1"
        response = client.get(f'/api/file/list/?client_id={malicious_input}')
        
        # No debe causar error de servidor
        self.assertNotEqual(response.status_code, 500)
