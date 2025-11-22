// Admin Dashboard JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Tabs functionality
    initTabs();
    
    // Form submissions
    initForms();
    
    // Filters
    initFilters();
});

// Inicializar tabs
function initTabs() {
    const tabButtons = document.querySelectorAll('.admin-tab-btn');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetTab = this.dataset.tab;
            
            // Remover clase active de todos los botones
            tabButtons.forEach(btn => btn.classList.remove('active'));
            
            // Agregar clase active al botón clickeado
            this.classList.add('active');
            
            // Ocultar todos los paneles
            document.querySelectorAll('.tab-panel').forEach(panel => {
                panel.classList.remove('active');
            });
            
            // Mostrar el panel correspondiente
            const targetPanel = document.getElementById(targetTab + '-tab');
            if (targetPanel) {
                targetPanel.classList.add('active');
            }
        });
    });
}

// Inicializar formularios
function initForms() {
    // Formulario de Precios
    const precioForm = document.getElementById('precioForm');
    if (precioForm) {
        precioForm.addEventListener('submit', function(e) {
            if (!validarFormularioPrecio()) {
                e.preventDefault();
                return false;
            }
        });
    }
    
    // Formulario de Empleados
    const empleadoForm = document.getElementById('empleadoForm');
    if (empleadoForm) {
        empleadoForm.addEventListener('submit', function(e) {
            if (!validarFormularioEmpleado()) {
                e.preventDefault();
                return false;
            }
        });
    }
    
    // Formulario de Asignación
    const asignacionForm = document.getElementById('asignacionForm');
    if (asignacionForm) {
        asignacionForm.addEventListener('submit', function(e) {
            if (!validarFormularioAsignacion()) {
                e.preventDefault();
                return false;
            }
        });
    }
    
    // Formulario de Sesión
    const sesionForm = document.getElementById('sesionForm');
    if (sesionForm) {
        sesionForm.addEventListener('submit', function(e) {
            if (!validarFormularioSesion()) {
                e.preventDefault();
                return false;
            }
        });
    }
}

// Validaciones de formularios
function validarFormularioPrecio() {
    const servicio = document.getElementById('servicio').value;
    const plan = document.getElementById('plan').value.trim();
    const precio = document.getElementById('precio').value;
    
    if (!servicio) {
        alert('Por favor selecciona una categoría/servicio');
        return false;
    }
    
    if (!plan) {
        alert('Por favor ingresa el nombre del plan');
        return false;
    }
    
    if (!precio || parseFloat(precio) <= 0) {
        alert('Por favor ingresa un precio válido');
        return false;
    }
    
    return true;
}

function validarFormularioEmpleado() {
    const username = document.getElementById('username').value.trim();
    const email = document.getElementById('email').value.trim();
    const firstName = document.getElementById('first_name').value.trim();
    const lastName = document.getElementById('last_name').value.trim();
    const password1 = document.getElementById('password1').value;
    const password2 = document.getElementById('password2').value;
    const grupo = document.getElementById('grupo').value;
    
    if (!username || !email || !firstName || !lastName) {
        alert('Por favor completa todos los campos obligatorios');
        return false;
    }
    
    // Validar email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        alert('Por favor ingresa un email válido');
        return false;
    }
    
    // Validar contraseña
    if (password1.length < 8) {
        alert('La contraseña debe tener al menos 8 caracteres');
        return false;
    }
    
    if (!/[A-Z]/.test(password1)) {
        alert('La contraseña debe contener al menos una letra mayúscula');
        return false;
    }
    
    if (!/[a-z]/.test(password1)) {
        alert('La contraseña debe contener al menos una letra minúscula');
        return false;
    }
    
    if (!/\d/.test(password1)) {
        alert('La contraseña debe contener al menos un número');
        return false;
    }
    
    if (!/[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/;~`]/.test(password1)) {
        alert('La contraseña debe contener al menos un caracter especial');
        return false;
    }
    
    if (password1 !== password2) {
        alert('Las contraseñas no coinciden');
        return false;
    }
    
    if (!grupo) {
        alert('Por favor selecciona un rol/grupo');
        return false;
    }
    
    return true;
}

function validarFormularioAsignacion() {
    const cliente = document.getElementById('cliente').value;
    const empleado = document.getElementById('empleado').value;
    const servicio = document.getElementById('servicio_asignacion').value;
    
    if (!cliente) {
        alert('Por favor selecciona un cliente');
        return false;
    }
    
    if (!empleado) {
        alert('Por favor selecciona un empleado');
        return false;
    }
    
    if (!servicio) {
        alert('Por favor selecciona un servicio');
        return false;
    }
    
    if (cliente === empleado) {
        alert('El cliente y el empleado no pueden ser la misma persona');
        return false;
    }
    
    return true;
}

function validarFormularioSesion() {
    const asignacion = document.getElementById('asignacion').value;
    const fecha = document.getElementById('fecha').value;
    const hora = document.getElementById('hora').value;
    const duracion = document.getElementById('duracion').value;
    
    if (!asignacion) {
        alert('Por favor selecciona una asignación');
        return false;
    }
    
    if (!fecha) {
        alert('Por favor selecciona una fecha');
        return false;
    }
    
    if (!hora) {
        alert('Por favor selecciona una hora');
        return false;
    }
    
    // Validar que la fecha no sea en el pasado
    const fechaSeleccionada = new Date(fecha + 'T' + hora);
    const ahora = new Date();
    
    if (fechaSeleccionada < ahora) {
        if (!confirm('La fecha seleccionada está en el pasado. ¿Deseas continuar?')) {
            return false;
        }
    }
    
    if (!duracion || parseInt(duracion) < 15) {
        alert('La duración debe ser al menos 15 minutos');
        return false;
    }
    
    return true;
}

// Inicializar filtros
function initFilters() {
    // Filtro de asignación en archivos
    const filtroAsignacion = document.getElementById('filtro-asignacion');
    if (filtroAsignacion) {
        filtroAsignacion.addEventListener('change', function() {
            filtrarTabla('archivos-tab', 4, this.value);
        });
    }
    
    // Filtro de usuario en auditoría
    const filtroUsuario = document.getElementById('filtro-usuario');
    if (filtroUsuario) {
        filtroUsuario.addEventListener('change', function() {
            filtrarTabla('auditoria-tab', 1, this.value);
        });
    }
    
    // Filtro de acción en auditoría
    const filtroAccion = document.getElementById('filtro-accion');
    if (filtroAccion) {
        filtroAccion.addEventListener('change', function() {
            filtrarTabla('auditoria-tab', 2, this.value, true);
        });
    }
}

// Función para filtrar tablas
function filtrarTabla(tabId, columna, valor, parcial = false) {
    const tab = document.getElementById(tabId);
    if (!tab) return;
    
    const tabla = tab.querySelector('.data-table tbody');
    if (!tabla) return;
    
    const filas = tabla.querySelectorAll('tr');
    
    filas.forEach(fila => {
        if (fila.cells.length === 1) return; // Skip empty state row
        
        const celda = fila.cells[columna];
        if (!celda) return;
        
        const texto = celda.textContent.trim();
        
        if (!valor) {
            fila.style.display = '';
        } else {
            if (parcial) {
                fila.style.display = texto.toLowerCase().includes(valor.toLowerCase()) ? '' : 'none';
            } else {
                fila.style.display = texto.includes(valor) ? '' : 'none';
            }
        }
    });
}

// Función para formatear fecha
function formatearFecha(fecha) {
    const d = new Date(fecha);
    const dia = String(d.getDate()).padStart(2, '0');
    const mes = String(d.getMonth() + 1).padStart(2, '0');
    const anio = d.getFullYear();
    return `${dia}/${mes}/${anio}`;
}

// Función para formatear hora
function formatearHora(fecha) {
    const d = new Date(fecha);
    const hora = String(d.getHours()).padStart(2, '0');
    const minutos = String(d.getMinutes()).padStart(2, '0');
    return `${hora}:${minutos}`;
}

// Función para confirmar eliminación
function confirmarEliminacion(tipo) {
    return confirm(`¿Estás seguro de que deseas eliminar este ${tipo}? Esta acción no se puede deshacer.`);
}

// Función para mostrar notificaciones
function mostrarNotificacion(mensaje, tipo = 'success') {
    const notificacion = document.createElement('div');
    notificacion.className = `notificacion notificacion-${tipo}`;
    notificacion.textContent = mensaje;
    notificacion.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 25px;
        border-radius: 8px;
        background: ${tipo === 'success' ? '#28a745' : '#dc3545'};
        color: white;
        font-weight: 600;
        z-index: 10000;
        animation: slideIn 0.3s;
    `;
    
    document.body.appendChild(notificacion);
    
    setTimeout(() => {
        notificacion.style.animation = 'slideOut 0.3s';
        setTimeout(() => notificacion.remove(), 300);
    }, 3000);
}

// Animaciones CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
