# Script de configuración inicial del proyecto Django ImpulsaMente

Write-Host "=== Configuración Inicial del Proyecto Django ImpulsaMente ===" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar que estamos en el directorio correcto
if (-not (Test-Path "manage.py")) {
    Write-Host "Error: Este script debe ejecutarse desde el directorio raíz del proyecto" -ForegroundColor Red
    exit 1
}

# 2. Activar entorno virtual
Write-Host "1. Activando entorno virtual..." -ForegroundColor Yellow
if (Test-Path ".venv\Scripts\Activate.ps1") {
    & .\.venv\Scripts\Activate.ps1
    Write-Host "   Entorno virtual activado" -ForegroundColor Green
} else {
    Write-Host "   Error: No se encontró el entorno virtual en .venv" -ForegroundColor Red
    Write-Host "   Crea uno con: python -m venv .venv" -ForegroundColor Yellow
    exit 1
}

# 3. Instalar dependencias
Write-Host ""
Write-Host "2. Instalando dependencias..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "   Dependencias instaladas correctamente" -ForegroundColor Green
} else {
    Write-Host "   Error al instalar dependencias" -ForegroundColor Red
    exit 1
}

# 4. Verificar archivo .env
Write-Host ""
Write-Host "3. Verificando configuración..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Write-Host "   Creando archivo .env desde .env.example..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "   IMPORTANTE: Edita el archivo .env con tus credenciales de MySQL" -ForegroundColor Yellow
    Write-Host "   Presiona Enter después de configurar .env..." -ForegroundColor Yellow
    Read-Host
}

# 5. Crear migraciones
Write-Host ""
Write-Host "4. Creando migraciones de Django..." -ForegroundColor Yellow
python manage.py makemigrations
if ($LASTEXITCODE -eq 0) {
    Write-Host "   Migraciones creadas correctamente" -ForegroundColor Green
} else {
    Write-Host "   Error al crear migraciones" -ForegroundColor Red
}

# 6. Aplicar migraciones
Write-Host ""
Write-Host "5. Aplicando migraciones a la base de datos..." -ForegroundColor Yellow
python manage.py migrate
if ($LASTEXITCODE -eq 0) {
    Write-Host "   Migraciones aplicadas correctamente" -ForegroundColor Green
} else {
    Write-Host "   Error al aplicar migraciones. Verifica la configuración de MySQL en .env" -ForegroundColor Red
    exit 1
}

# 7. Crear superusuario
Write-Host ""
Write-Host "6. Creando superusuario..." -ForegroundColor Yellow
Write-Host "   (Puedes omitir esto con Ctrl+C y hacerlo más tarde con: python manage.py createsuperuser)" -ForegroundColor Cyan
python manage.py createsuperuser

# 8. Finalización
Write-Host ""
Write-Host "=== Configuración completada ===" -ForegroundColor Green
Write-Host ""
Write-Host "Para iniciar el servidor de desarrollo:" -ForegroundColor Cyan
Write-Host "  python manage.py runserver" -ForegroundColor White
Write-Host ""
Write-Host "URLs importantes:" -ForegroundColor Cyan
Write-Host "  - Sitio: http://127.0.0.1:8000/" -ForegroundColor White
Write-Host "  - Admin: http://127.0.0.1:8000/admin/" -ForegroundColor White
Write-Host ""
