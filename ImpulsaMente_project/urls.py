"""
Configuración de URLs para ImpulsaMente.

Incluye las URLs de las apps servicios y cuentas, además del panel de administración.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Personalizar el admin
admin.site.site_header = 'ImpulsaMente - Administración'
admin.site.site_title = 'ImpulsaMente Admin'
admin.site.index_title = 'Panel de Administración'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('servicios.urls')),
    path('cuentas/', include('cuentas.urls')),
]

# Servir archivos estáticos y media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else None)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

