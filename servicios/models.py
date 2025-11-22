from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


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
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'prices'
        verbose_name = 'Precio'
        verbose_name_plural = 'Precios'

    def __str__(self):
        return f"{self.service.name} - {self.plan} (${self.price} {self.currency})"


class Customer(models.Model):
    """Modelo para clientes"""
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=200)
    phone = models.CharField(max_length=50, blank=True, null=True)
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

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    price = models.ForeignKey(Price, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, default='pending', choices=STATUS_CHOICES)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'orders'
        verbose_name = 'Orden'
        verbose_name_plural = 'Órdenes'
        ordering = ['-created_at']

    def __str__(self):
        return f"Orden #{self.id} - {self.customer.name} - {self.service.name}"


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
    scheduled_date = models.DateTimeField()
    duration_minutes = models.IntegerField(default=60)
    status = models.CharField(max_length=50, default='scheduled', choices=STATUS_CHOICES)
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
    file = models.FileField(upload_to='uploads/%Y/%m/%d/')
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
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    related_object_type = models.CharField(max_length=100, blank=True, null=True)
    related_object_id = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'audit_logs'
        verbose_name = 'Registro de Auditoría'
        verbose_name_plural = 'Registros de Auditoría'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} - {self.get_action_display()} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

