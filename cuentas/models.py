from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """Perfil extendido de usuario"""
    USER_TYPE_CHOICES = [
        ('cliente', 'Cliente'),
        ('empleado', 'Empleado'),
        ('estudiante', 'Estudiante'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='cliente')
    phone = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'

    def __str__(self):
        return f"{self.user.username} - {self.get_user_type_display()}"

