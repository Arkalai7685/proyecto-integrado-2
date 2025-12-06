from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db.models.signals import post_save
from django.dispatch import receiver

# Validador de teléfono
phone_validator = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Número de teléfono debe tener formato: '+999999999'. Entre 9 y 15 dígitos."
)


class UserProfile(models.Model):
    """Perfil extendido de usuario"""
    USER_TYPE_CHOICES = [
        ('cliente', 'Cliente'),
        ('empleado', 'Empleado'),
        ('estudiante', 'Estudiante'),
        ('admin', 'Administrador'),
        ('tutor', 'Tutor'),
        ('psicologo', 'Psicólogo'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='cliente')
    phone = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        validators=[phone_validator],
        help_text="Formato: '+999999999' (9-15 dígitos)"
    )
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'

    def __str__(self):
        return f"{self.user.username} - {self.get_user_type_display()}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Crear UserProfile automáticamente cuando se crea un nuevo usuario"""
    if created:
        # Determinar el tipo de usuario
        user_type = 'cliente'  # Por defecto
        
        if instance.is_superuser:
            user_type = 'admin'
        elif instance.is_staff:
            # Verificar grupos
            if instance.groups.filter(name__in=['Psicólogo', 'Psicologo']).exists():
                user_type = 'psicologo'
            elif instance.groups.filter(name='Tutor').exists():
                user_type = 'tutor'
            else:
                user_type = 'empleado'
        
        UserProfile.objects.create(
            user=instance,
            user_type=user_type
        )
