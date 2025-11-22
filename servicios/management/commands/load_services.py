from django.core.management.base import BaseCommand
from servicios.models import Service, Price


class Command(BaseCommand):
    help = 'Carga datos iniciales de servicios y precios'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Cargando datos iniciales...'))
        
        # Crear servicio de Tutoría
        tutoria, created = Service.objects.get_or_create(
            slug='tutoria',
            defaults={
                'name': 'Tutoría',
                'description': 'Apoyo académico y acompañamiento en tesis y estudios'
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Servicio creado: {tutoria.name}'))
            
            # Crear precios para Tutoría
            Price.objects.create(
                service=tutoria,
                plan='basico',
                price=15000.00,
                currency='COP',
                description='Sesión única de 60 minutos'
            )
            
            Price.objects.create(
                service=tutoria,
                plan='estandar',
                price=80000.00,
                currency='COP',
                description='Paquete de 6 sesiones'
            )
            
            Price.objects.create(
                service=tutoria,
                plan='premium',
                price=150000.00,
                currency='COP',
                description='Paquete de 12 sesiones con recursos adicionales'
            )
            
            self.stdout.write(self.style.SUCCESS('  ✓ 3 planes de precio creados para Tutoría'))
        else:
            self.stdout.write(self.style.WARNING(f'  El servicio {tutoria.name} ya existe'))
        
        # Crear servicio de Terapia
        terapia, created = Service.objects.get_or_create(
            slug='terapia',
            defaults={
                'name': 'Terapia',
                'description': 'Atención psicológica individual y grupal'
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Servicio creado: {terapia.name}'))
            
            # Crear precios para Terapia
            Price.objects.create(
                service=terapia,
                plan='individual',
                price=30000.00,
                currency='COP',
                description='Sesión individual de 60 minutos'
            )
            
            Price.objects.create(
                service=terapia,
                plan='10sesiones',
                price=280000.00,
                currency='COP',
                description='Programa de 10 sesiones'
            )
            
            Price.objects.create(
                service=terapia,
                plan='familiar',
                price=45000.00,
                currency='COP',
                description='Sesión grupal / familiar'
            )
            
            self.stdout.write(self.style.SUCCESS('  ✓ 3 planes de precio creados para Terapia'))
        else:
            self.stdout.write(self.style.WARNING(f'  El servicio {terapia.name} ya existe'))
        
        self.stdout.write(self.style.SUCCESS('\n✓ Datos iniciales cargados correctamente'))
