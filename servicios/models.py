from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator, RegexValidator
from django.core.exceptions import ValidationError

# Validador de teléfono
phone_validator = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Número de teléfono debe tener formato: '+999999999'. Entre 9 y 15 dígitos."
)


class Service(models.Model):
    """Modelo para los servicios (Tutoría, Terapia)"""
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'services'
        verbose_name = 'Servicio'
        verbose_name_plural = 'Servicios'

    def __str__(self):
        return self.name


class Price(models.Model):
    """Modelo para los planes y precios de servicios"""
    CURRENCY_CHOICES = [
        ('CLP', 'Peso Chileno'),
        ('USD', 'Dólar Estadounidense'),
    ]

    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='prices')
    plan = models.CharField(max_length=80)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='CLP', choices=CURRENCY_CHOICES)
    description = models.TextField(blank=True, null=True)
    
    # Campos para número de sesiones
    number_of_sessions = models.IntegerField(
        default=4, 
        help_text='Número de sesiones para servicios individuales (tutoría o terapia)'
    )
    tutoring_sessions = models.IntegerField(
        default=8,
        help_text='Número de sesiones de tutoría para Plan Estudiante'
    )
    therapy_sessions = models.IntegerField(
        default=8,
        help_text='Número de sesiones de terapia para Plan Estudiante'
    )
    
    # Campo para marcar planes destacados
    is_featured = models.BooleanField(
        default=False,
        verbose_name='Plan Destacado',
        help_text='Marcar este plan para mostrarlo como destacado en la página principal'
    )
    
    # Campo para la imagen del servicio
    image = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Imagen del servicio',
        help_text='Nombre del archivo de imagen en assets/images/'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'prices'
        verbose_name = 'Precio'
        verbose_name_plural = 'Precios'

    def save(self, *args, **kwargs):
        """Asignar automáticamente la imagen según el tipo de servicio si no tiene una"""
        if not self.image:
            service_slug = self.service.slug.lower()
            service_name = self.service.name.lower()
            plan_lower = self.plan.lower()
            
            if 'plan' in service_name and 'estudiante' in service_name:
                self.image = 'plan estudiante.jpg'
            elif 'plan' in plan_lower and 'estudiante' in plan_lower:
                self.image = 'plan estudiante.jpg'
            elif 'tutoria' in service_slug or 'tutor' in service_slug:
                self.image = 'imagen tutir.jpg'
            elif 'terapia' in service_slug or 'psicolog' in service_slug:
                self.image = 'imagen terapia.jpg'
            else:
                # Imagen por defecto
                self.image = 'Illustration.png'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.service.name} - {self.plan} (${self.price} {self.currency})"


class Customer(models.Model):
    """Modelo para clientes"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='customer_profile')
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=200, unique=True)
    phone = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        validators=[phone_validator],
        help_text="Formato: '+999999999' (9-15 dígitos)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'customers'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return f"{self.name} ({self.email})"


class Order(models.Model):
    """Modelo para órdenes/solicitudes de servicio"""
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('confirmed', 'Confirmado'),
        ('in_progress', 'En Progreso'),
        ('completed', 'Completado'),
        ('cancelled', 'Cancelado'),
    ]
    
    WEEKDAY_CHOICES = [
        ('monday', 'Lunes'),
        ('tuesday', 'Martes'),
        ('wednesday', 'Miércoles'),
        ('thursday', 'Jueves'),
        ('friday', 'Viernes'),
        ('saturday', 'Sábado'),
        ('sunday', 'Domingo'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    price = models.ForeignKey(Price, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, default='pending', choices=STATUS_CHOICES, db_index=True)
    notes = models.TextField(blank=True, null=True)
    
    # Campos para programación de sesiones (servicios individuales)
    preferred_employee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                          related_name='service_requests',
                                          help_text='Tutor o terapeuta preferido')
    start_date = models.DateField(null=True, blank=True, 
                                  help_text='Fecha de inicio de las sesiones')
    preferred_days = models.JSONField(default=list, blank=True, 
                                     help_text='Días de la semana preferidos (lista de weekdays)')
    preferred_time = models.TimeField(null=True, blank=True, 
                                     help_text='Hora preferida para las sesiones')
    number_of_sessions = models.IntegerField(default=1, 
                                            help_text='Número total de sesiones del plan')
    sessions_generated = models.BooleanField(default=False, 
                                            help_text='Indica si ya se generaron las sesiones')
    
    # Campos adicionales para Plan Estudiante (requiere tutor Y terapeuta)
    preferred_tutor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='tutoring_requests',
                                       help_text='Tutor asignado para plan estudiante')
    preferred_therapist = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                           related_name='therapy_requests',
                                           help_text='Terapeuta asignado para plan estudiante')
    tutoring_start_date = models.DateField(null=True, blank=True,
                                          help_text='Fecha de inicio de tutorias')
    therapy_start_date = models.DateField(null=True, blank=True,
                                         help_text='Fecha de inicio de terapias')
    tutoring_time = models.TimeField(null=True, blank=True,
                                    help_text='Hora para sesiones de tutoría')
    therapy_time = models.TimeField(null=True, blank=True,
                                   help_text='Hora para sesiones de terapia')
    tutoring_sessions = models.IntegerField(default=0,
                                           help_text='Número de sesiones de tutoría')
    therapy_sessions = models.IntegerField(default=0,
                                          help_text='Número de sesiones de terapia')
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'orders'
        verbose_name = 'Orden'
        verbose_name_plural = 'Órdenes'
        ordering = ['-created_at']

    def __str__(self):
        return f"Orden #{self.id} - {self.customer.name} - {self.service.name}"
    
    def clean(self):
        """Validar que las fechas no sean en el pasado"""
        today = timezone.now().date()
        if self.start_date and self.start_date < today:
            raise ValidationError({'start_date': 'La fecha de inicio no puede ser en el pasado'})
        if self.tutoring_start_date and self.tutoring_start_date < today:
            raise ValidationError({'tutoring_start_date': 'La fecha de inicio de tutoría no puede ser en el pasado'})
        if self.therapy_start_date and self.therapy_start_date < today:
            raise ValidationError({'therapy_start_date': 'La fecha de inicio de terapia no puede ser en el pasado'})


class ClientAssignment(models.Model):
    """Modelo para asignar empleados a clientes"""
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client_assignments')
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='employee_assignments')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'client_assignments'
        verbose_name = 'Asignación de Cliente'
        verbose_name_plural = 'Asignaciones de Clientes'
        ordering = ['-assigned_at']

    def __str__(self):
        return f"{self.client.username} → {self.employee.username} ({self.service.name})"


class Session(models.Model):
    """Modelo para sesiones/citas entre clientes y empleados"""
    STATUS_CHOICES = [
        ('scheduled', 'Programada'),
        ('confirmed', 'Confirmada'),
        ('completed', 'Completada'),
        ('cancelled', 'Cancelada'),
        ('no_show', 'No Asistió'),
    ]

    assignment = models.ForeignKey(ClientAssignment, on_delete=models.CASCADE, related_name='sessions')
    scheduled_date = models.DateTimeField(db_index=True)
    duration_minutes = models.IntegerField(
        default=60,
        validators=[
            MinValueValidator(15, message='La duración mínima es 15 minutos'),
            MaxValueValidator(480, message='La duración máxima es 8 horas')
        ]
    )
    status = models.CharField(max_length=50, default='scheduled', choices=STATUS_CHOICES, db_index=True)
    notes = models.TextField(blank=True, null=True)
    employee_notes = models.TextField(blank=True, null=True, verbose_name='Notas del Empleado')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sessions'
        verbose_name = 'Sesión'
        verbose_name_plural = 'Sesiones'
        ordering = ['scheduled_date']

    def __str__(self):
        return f"Sesión {self.id} - {self.assignment.client.username} - {self.scheduled_date.strftime('%Y-%m-%d %H:%M')}"


class FileUpload(models.Model):
    """Modelo para archivos compartidos entre clientes y empleados"""
    FILE_TYPE_CHOICES = [
        ('document', 'Documento'),
        ('image', 'Imagen'),
        ('audio', 'Audio'),
        ('video', 'Video'),
        ('other', 'Otro'),
    ]

    assignment = models.ForeignKey(ClientAssignment, on_delete=models.CASCADE, related_name='files')
    session = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True, blank=True, related_name='files')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(
        upload_to='uploads/%Y/%m/%d/',
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf', 'doc', 'docx', 'txt', 'jpg', 'jpeg', 'png', 'gif', 'mp3', 'mp4', 'zip'],
                message='Tipo de archivo no permitido. Extensiones permitidas: pdf, doc, docx, txt, jpg, jpeg, png, gif, mp3, mp4, zip'
            )
        ],
        help_text='Tamaño máximo: 10MB. Formatos permitidos: documentos, imágenes, audio, video'
    )
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50, choices=FILE_TYPE_CHOICES, default='document')
    file_size = models.BigIntegerField(help_text='Tamaño en bytes')
    description = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'file_uploads'
        verbose_name = 'Archivo'
        verbose_name_plural = 'Archivos'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.file_name} - {self.uploaded_by.username}"
    
    def clean(self):
        """Validar tamaño de archivo (máximo 10MB)"""
        if self.file:
            if hasattr(self.file, 'size'):
                max_size = 10 * 1024 * 1024  # 10 MB en bytes
                if self.file.size > max_size:
                    raise ValidationError(
                        f'El archivo es demasiado grande. Tamaño máximo: 10MB. Tamaño actual: {self.get_file_size_display()}'
                    )

    def get_file_size_display(self):
        """Retorna el tamaño del archivo en formato legible"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"


class AuditLog(models.Model):
    """Modelo para registro de auditoría de clientes"""
    ACTION_CHOICES = [
        ('login', 'Inicio de Sesión'),
        ('logout', 'Cierre de Sesión'),
        ('profile_update', 'Actualización de Perfil'),
        ('order_created', 'Orden Creada'),
        ('order_updated', 'Orden Actualizada'),
        ('session_scheduled', 'Sesión Programada'),
        ('session_completed', 'Sesión Completada'),
        ('file_uploaded', 'Archivo Subido'),
        ('file_downloaded', 'Archivo Descargado'),
        ('other', 'Otra Acción'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES, db_index=True)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    related_object_type = models.CharField(max_length=100, blank=True, null=True)
    related_object_id = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'audit_logs'
        verbose_name = 'Registro de Auditoría'
        verbose_name_plural = 'Registros de Auditoría'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} - {self.get_action_display()} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"


class ChatMessage(models.Model):
    """Modelo para mensajes de chat entre cliente y empleado"""
    assignment = models.ForeignKey(ClientAssignment, on_delete=models.CASCADE, related_name='chat_messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    message = models.TextField()
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'chat_messages'
        verbose_name = 'Mensaje de Chat'
        verbose_name_plural = 'Mensajes de Chat'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.sender.username} -> {self.assignment} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    def mark_as_read(self):
        """Marcar mensaje como leído"""
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])

