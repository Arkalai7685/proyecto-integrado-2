from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re


class SecurePasswordValidator:
    """Validador personalizado para contraseñas seguras"""
    
    @staticmethod
    def validate(password):
        """
        Valida que la contraseña cumpla con los requisitos de seguridad:
        - Mínimo 8 caracteres
        - Al menos una letra mayúscula
        - Al menos una letra minúscula
        - Al menos un número
        - Al menos un caracter especial
        """
        errors = []
        
        if len(password) < 8:
            errors.append("La contraseña debe tener al menos 8 caracteres.")
        
        if not re.search(r'[A-Z]', password):
            errors.append("La contraseña debe contener al menos una letra mayúscula.")
        
        if not re.search(r'[a-z]', password):
            errors.append("La contraseña debe contener al menos una letra minúscula.")
        
        if not re.search(r'\d', password):
            errors.append("La contraseña debe contener al menos un número.")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/;~`]', password):
            errors.append("La contraseña debe contener al menos un caracter especial (!@#$%^&*(),.?\":{}|<>_-+=[]\\\/;~`).")
        
        return errors


class SecureUserCreationForm(UserCreationForm):
    """Formulario de registro con validación de contraseñas seguras"""
    
    email = forms.EmailField(
        required=True,
        help_text="Requerido. Ingresa un email válido.",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com'
        })
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=False,
        help_text="Opcional.",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu nombre'
        })
    )
    
    last_name = forms.CharField(
        max_length=150,
        required=False,
        help_text="Opcional.",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu apellido'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de usuario'
            }),
        }
        help_texts = {
            'username': 'Requerido. 150 caracteres o menos. Letras, dígitos y @/./+/-/_ únicamente.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirma tu contraseña'
        })
        self.fields['password1'].help_text = (
            "Tu contraseña debe cumplir con los siguientes requisitos:\n"
            "• Mínimo 8 caracteres\n"
            "• Al menos una letra mayúscula\n"
            "• Al menos una letra minúscula\n"
            "• Al menos un número\n"
            "• Al menos un caracter especial (!@#$%^&*(),.?\":{}|<>_-+=[]\\\/;~`)"
        )

    def clean_password1(self):
        """Valida la primera contraseña con los requisitos de seguridad"""
        password1 = self.cleaned_data.get('password1')
        
        if password1:
            errors = SecurePasswordValidator.validate(password1)
            if errors:
                raise ValidationError(errors)
        
        return password1

    def clean_email(self):
        """Valida que el email no esté ya registrado"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Este correo electrónico ya está registrado.")
        return email

    def save(self, commit=True):
        """Guarda el usuario con el email"""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if self.cleaned_data.get('first_name'):
            user.first_name = self.cleaned_data['first_name']
        if self.cleaned_data.get('last_name'):
            user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
        return user
