#!/usr/bin/env python
"""Script para configurar precios destacados"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ImpulsaMente_project.settings')
django.setup()

from servicios.models import Price

# Marcar todos los precios existentes como destacados
tutoria_prices = Price.objects.filter(service__slug='tutoria')
for price in tutoria_prices:
    price.is_featured = True
    price.save()
    print(f"✓ Tutoría - {price.plan}: Marcado como destacado")

terapia_prices = Price.objects.filter(service__slug='terapia')
for price in terapia_prices:
    price.is_featured = True
    price.save()
    print(f"✓ Terapia - {price.plan}: Marcado como destacado")

plan_prices = Price.objects.filter(service__slug='plan-estudiante')
for price in plan_prices:
    price.is_featured = True
    price.save()
    print(f"✓ Plan Estudiante - {price.plan}: Marcado como destacado")

print("\n✅ Todos los precios han sido marcados como destacados")
