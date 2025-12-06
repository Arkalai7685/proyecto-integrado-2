from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from cuentas.models import UserProfile
from servicios.models import ClientAssignment

User = get_user_model()

class Command(BaseCommand):
    help = 'Verifica y corrige los tipos de usuario basándose en las asignaciones'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Verificando tipos de usuario...'))
        
        correcciones = 0
        advertencias = 0
        
        # Obtener todos los perfiles
        profiles = UserProfile.objects.all()
        
        for profile in profiles:
            user = profile.user
            
            # Verificar si es empleado
            is_employee = ClientAssignment.objects.filter(employee=user).exists()
            # Verificar si es cliente
            is_client = ClientAssignment.objects.filter(client=user).exists()
            
            tipo_correcto = None
            
            if is_employee and profile.user_type not in ['tutor', 'psicologo', 'admin']:
                # Determinar tipo correcto basándose en el servicio
                first_assignment = ClientAssignment.objects.filter(employee=user).first()
                if first_assignment:
                    if 'terapia' in first_assignment.service.name.lower() or 'psico' in first_assignment.service.name.lower():
                        tipo_correcto = 'psicologo'
                    else:
                        tipo_correcto = 'tutor'
                    
                    self.stdout.write(
                        self.style.WARNING(
                            f'❌ {user.username}: tipo actual "{profile.user_type}" pero es empleado ({first_assignment.service.name})'
                        )
                    )
                    
                    profile.user_type = tipo_correcto
                    profile.save()
                    correcciones += 1
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'   ✓ Corregido a: {tipo_correcto}')
                    )
            
            elif is_client and not is_employee and profile.user_type != 'cliente':
                self.stdout.write(
                    self.style.WARNING(
                        f'❌ {user.username}: tipo actual "{profile.user_type}" pero solo es cliente'
                    )
                )
                
                profile.user_type = 'cliente'
                profile.save()
                correcciones += 1
                
                self.stdout.write(
                    self.style.SUCCESS(f'   ✓ Corregido a: cliente')
                )
            
            elif is_employee and is_client:
                advertencias += 1
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠️  {user.username}: es AMBOS (empleado Y cliente) - tipo actual: {profile.user_type}'
                    )
                )
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'✓ Proceso completado'))
        self.stdout.write(f'  - Correcciones realizadas: {correcciones}')
        self.stdout.write(f'  - Advertencias (usuarios duales): {advertencias}')
