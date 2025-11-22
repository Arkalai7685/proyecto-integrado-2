from django.contrib import admin
from .models import Service, Price, Customer, Order


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ['service', 'plan', 'price', 'currency', 'created_at']
    list_filter = ['service', 'currency']
    search_fields = ['plan', 'description']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'created_at']
    search_fields = ['name', 'email', 'phone']
    list_filter = ['created_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'service', 'price', 'status', 'created_at']
    list_filter = ['status', 'service', 'created_at']
    search_fields = ['customer__name', 'customer__email', 'notes']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']

