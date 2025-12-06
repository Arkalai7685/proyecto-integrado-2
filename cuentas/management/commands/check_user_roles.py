from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from cuentas.models import UserProfile
from servicios.models import ClientAssignment

User = get_user_model()

class Command(BaseCommand):
    help = 'Verifica la consistencia de los roles de usuario (sin hacer cambios)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('=== VERIFICACIÓN DE ROLES DE USUARIO ===\n'))
        
        problemas = []
        
        profiles = UserProfile.objects.all()
        
        for profile in profiles:
            user = profile.user
            
            is_employee = ClientAssignment.objects.filter(employee=user).exists()
            is_client = ClientAssignment.objects.filter(client=user).exists()
            
            # Verificar inconsistencias
            if is_employee and profile.user_type not in ['tutor', 'psicologo', 'admin']:
                first_assignment = ClientAssignment.objects.filter(employee=user).first()
                tipo_esperado = 'psicologo' if 'terapia' in first_assignment.service.name.lower() else 'tutor'
                problemas.append({
                    'usuario': user.username,
                    'problema': f'Es empleado pero tiene user_type="{profile.user_type}"',
                    'esperado': tipo_esperado
                })
            
            elif is_client and not is_employee and profile.user_type != 'cliente':
                problemas.append({
                    'usuario': user.username,
                    'problema': f'Es solo cliente pero tiene user_type="{profile.user_type}"',
                    'esperado': 'cliente'
                })
            
            elif is_employee and is_client:
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠️  {user.username}: Usuario dual (empleado Y cliente) - tipo: {profile.user_type}'
                    )
                )
        
        if problemas:
            self.stdout.write(self.style.ERROR(f'\n❌ Se encontraron {len(problemas)} problema(s):\n'))
            for p in problemas:
                self.stdout.write(f'  • {p["usuario"]}: {p["problema"]}')
                self.stdout.write(f'    Debería ser: {p["esperado"]}\n')
            
            self.stdout.write(self.style.WARNING('\nPara corregir estos problemas, ejecuta:'))
            self.stdout.write('  python manage.py fix_user_type\n')
        else:
            self.stdout.write(self.style.SUCCESS('✓ Todos los roles de usuario son consistentes\n'))
