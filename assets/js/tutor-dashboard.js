document.addEventListener('DOMContentLoaded', () => {
    initializeTabs();
    initializeStudentProgressBars();
    // initializeTutorCalendar(); // Comentado temporalmente
    initializeFolders();
    initializeSolicitudes();
    initializeStudentCards();
    
    // Event delegation para botones ARCHIVOS
    document.body.addEventListener('click', (e) => {
        if (e.target.classList.contains('btn-ver-archivos')) {
            e.preventDefault();
            const clientId = e.target.getAttribute('data-client-id');
            console.log('Click en ARCHIVOS, clientId:', clientId);
            if (clientId) {
                verArchivosCliente(parseInt(clientId));
            }
        }
    });
});

function initializeTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.getAttribute('data-tab');
            
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            btn.classList.add('active');
            document.getElementById(targetTab + '-tab').classList.add('active');
            
            btn.style.transform = 'scale(0.95)';
            setTimeout(() => {
                btn.style.transform = '';
            }, 150);
        });
    });
}

function initializeStudentProgressBars() {
    // Establecer el width correcto desde data-progress FORZANDO con !important
    const progressBars = document.querySelectorAll('.student-card .progress-bar');
    progressBars.forEach((bar) => {
        const correctProgress = bar.getAttribute('data-progress');
        // Usar setProperty con 'important' para sobrescribir cualquier CSS
        bar.style.setProperty('width', correctProgress + '%', 'important');
    });
}

function initializeTutorCalendar() {
    const calendarDays = document.getElementById('calendarDays');
    const monthSelect = document.querySelector('.month-select');
    const yearSelect = document.querySelector('.year-select');
    const prevBtn = document.querySelector('[data-dir="prev"]');
    const nextBtn = document.querySelector('[data-dir="next"]');
    
    let currentDate = new Date();
    let currentMonth = currentDate.getMonth();
    let currentYear = currentDate.getFullYear();
    
    const appointments = {
        '2025-10-23': [
            { time: '10:00', student: 'María García', type: 'tutoría' },
            { time: '14:30', student: 'Carlos López', type: 'revisión tesis' }
        ],
        '2025-10-25': [
            { time: '11:00', student: 'Ana Martínez', type: 'asesoría' }
        ],
        '2025-10-28': [
            { time: '09:00', student: 'Pedro Rodríguez', type: 'metodología' },
            { time: '15:00', student: 'Laura Silva', type: 'correcciones' }
        ],
        '2025-11-02': [
            { time: '10:30', student: 'Miguel Torres', type: 'marco teórico' }
        ],
        '2025-11-05': [
            { time: '13:00', student: 'Sofia Mendez', type: 'análisis de datos' }
        ]
    };
    
    function renderCalendar() {
        const firstDay = new Date(currentYear, currentMonth, 1);
        const lastDay = new Date(currentYear, currentMonth + 1, 0);
        const firstDayWeek = firstDay.getDay() === 0 ? 7 : firstDay.getDay();
        const daysInMonth = lastDay.getDate();
        
        monthSelect.value = currentMonth;
        yearSelect.value = currentYear;
        
        calendarDays.innerHTML = '';
        
        for (let i = 1; i < firstDayWeek; i++) {
            const dayEl = createDayElement('', true);
            calendarDays.appendChild(dayEl);
        }
        
        for (let day = 1; day <= daysInMonth; day++) {
            const dateStr = `${currentYear}-${String(currentMonth + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
            const isToday = isCurrentDay(day);
            const dayAppointments = appointments[dateStr];
            
            const dayEl = createDayElement(day, false, isToday, dayAppointments);
            calendarDays.appendChild(dayEl);
        }
        
        const totalCells = calendarDays.children.length;
        const remainingCells = 42 - totalCells;
        for (let i = 0; i < remainingCells; i++) {
            const dayEl = createDayElement('', true);
            calendarDays.appendChild(dayEl);
        }
    }
    
    function createDayElement(day, isOtherMonth = false, isToday = false, dayAppointments = null) {
        const dayEl = document.createElement('div');
        dayEl.className = 'calendar-day';
        dayEl.textContent = day;
        
        if (isOtherMonth) {
            dayEl.classList.add('other-month');
        }
        
        if (isToday) {
            dayEl.classList.add('today');
        }
        
        if (dayAppointments && dayAppointments.length > 0) {
            dayEl.classList.add('has-appointment');
            dayEl.title = `${dayAppointments.length} cita(s) programada(s)`;
            
            dayEl.addEventListener('click', () => {
                showAppointmentDetails(day, dayAppointments);
            });
        }
        
        return dayEl;
    }
    
    function isCurrentDay(day) {
        const today = new Date();
        return day === today.getDate() && 
               currentMonth === today.getMonth() && 
               currentYear === today.getFullYear();
    }
    
    function showAppointmentDetails(day, dayAppointments) {
        const modal = createAppointmentModal(day, dayAppointments);
        document.body.appendChild(modal);
        
        setTimeout(() => {
            modal.style.opacity = '1';
            modal.querySelector('.appointment-modal-content').style.transform = 'scale(1)';
        }, 10);
    }
    
    function createAppointmentModal(day, dayAppointments) {
        const modal = document.createElement('div');
        modal.className = 'appointment-modal';
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            z-index: 3000;
            opacity: 0;
            transition: opacity 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
        `;
        
        const appointmentsList = dayAppointments.map(apt => `
            <div style="
                padding: 15px;
                background: #f8f9fa;
                border-radius: 10px;
                margin-bottom: 10px;
                border-left: 4px solid #f39c12;
            ">
                <strong style="color: #2c3e50;">${apt.time}</strong> - ${apt.student}
                <br>
                <small style="color: #7f8c8d; text-transform: uppercase;">${apt.type}</small>
            </div>
        `).join('');
        
        modal.innerHTML = `
            <div class="appointment-modal-content" style="
                background: white;
                padding: 30px;
                border-radius: 15px;
                max-width: 400px;
                width: 90%;
                transform: scale(0.9);
                transition: transform 0.3s ease;
            ">
                <h3 style="margin: 0 0 20px 0; color: #2c3e50;">Citas del ${day}</h3>
                ${appointmentsList}
                <button onclick="this.closest('.appointment-modal').remove()" style="
                    background: #f39c12;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 8px;
                    cursor: pointer;
                    font-weight: 600;
                    width: 100%;
                    margin-top: 10px;
                ">Cerrar</button>
            </div>
        `;
        
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
        
        return modal;
    }
    
    prevBtn.addEventListener('click', () => {
        currentMonth--;
        if (currentMonth < 0) {
            currentMonth = 11;
            currentYear--;
        }
        renderCalendar();
    });
    
    nextBtn.addEventListener('click', () => {
        currentMonth++;
        if (currentMonth > 11) {
            currentMonth = 0;
            currentYear++;
        }
        renderCalendar();
    });
    
    monthSelect.addEventListener('change', (e) => {
        currentMonth = parseInt(e.target.value);
        renderCalendar();
    });
    
    yearSelect.addEventListener('change', (e) => {
        currentYear = parseInt(e.target.value);
        renderCalendar();
    });
    
    renderCalendar();
}

function initializeFolders() {
    const folders = document.querySelectorAll('.folder-item');
    
    folders.forEach((folder, index) => {
        folder.addEventListener('click', () => {
            folder.style.transform = 'scale(0.95)';
            setTimeout(() => {
                folder.style.transform = '';
            }, 150);
            
            const folderName = folder.querySelector('span').textContent;
            showNotification(`Abriendo ${folderName}...`, 'info');
        });
        
        setTimeout(() => {
            folder.style.opacity = '1';
            folder.style.transform = 'translateY(0)';
        }, index * 50);
    });
}

function initializeSolicitudes() {
    // Las solicitudes ahora se manejan con las funciones globales acceptRequest y rejectRequest
    // que están definidas más abajo
}

// Función global para aceptar solicitud
function acceptRequest(orderId) {
    if (!confirm('¿Estás seguro de que deseas aceptar esta solicitud?')) {
        return;
    }
    
    fetch(`/accept-request/${orderId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const solicitudItem = document.querySelector(`[data-order-id="${orderId}"]`);
            if (solicitudItem) {
                solicitudItem.style.transform = 'translateX(-100%)';
                solicitudItem.style.opacity = '0';
                
                setTimeout(() => {
                    solicitudItem.remove();
                    updateSolicitudesCount();
                    showNotification(data.message || 'Solicitud aceptada exitosamente', 'success');
                }, 300);
            }
        } else {
            showNotification(data.error || 'Error al aceptar la solicitud', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error de conexión al aceptar la solicitud', 'error');
    });
}

// Función global para rechazar solicitud
function rejectRequest(orderId) {
    const reason = prompt('Por favor, indica la razón del rechazo:');
    
    if (reason === null) {
        return; // Usuario canceló
    }
    
    if (!reason.trim()) {
        showNotification('Debes proporcionar una razón para el rechazo', 'error');
        return;
    }
    
    fetch(`/reject-request/${orderId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({
            reason: reason
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const solicitudItem = document.querySelector(`[data-order-id="${orderId}"]`);
            if (solicitudItem) {
                solicitudItem.style.transform = 'translateX(100%)';
                solicitudItem.style.opacity = '0';
                
                setTimeout(() => {
                    solicitudItem.remove();
                    updateSolicitudesCount();
                    showNotification(data.message || 'Solicitud rechazada', 'success');
                }, 300);
            }
        } else {
            showNotification(data.error || 'Error al rechazar la solicitud', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error de conexión al rechazar la solicitud', 'error');
    });
}

// Función auxiliar para obtener el token CSRF
function getCsrfToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function updateSolicitudesCount() {
    const remainingItems = document.querySelectorAll('.solicitud-item').length;
    const countElement = document.querySelector('.solicitudes-count');
    countElement.textContent = `${remainingItems} pendientes`;
    
    if (remainingItems === 0) {
        const container = document.querySelector('.solicitudes-list');
        container.innerHTML = `
            <div style="text-align: center; padding: 40px; color: #7f8c8d;">
                <div style="font-size: 48px; margin-bottom: 15px;">✅</div>
                <h4 style="color: #27ae60; margin: 0;">¡Todas las solicitudes procesadas!</h4>
                <p style="margin: 10px 0 0 0;">No hay solicitudes pendientes por revisar.</p>
            </div>
        `;
    }
}

function initializeStudentCards() {
    const studentCards = document.querySelectorAll('.student-card');
    const verBtns = document.querySelectorAll('.ver-btn');
    
    studentCards.forEach((card, index) => {
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 200);
    });
    
    verBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const studentCard = btn.closest('.student-card');
            const studentNameElement = studentCard.querySelector('.student-name');
            const studentName = studentNameElement ? studentNameElement.textContent.trim() : 'Cliente';
            
            showStudentDetails(studentName, studentCard);
        });
    });
}

function showStudentDetails(studentName, studentCard) {
    const progressBar = studentCard.querySelector('.progress-bar');
    const progress = progressBar.getAttribute('data-progress');
    
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        z-index: 3000;
        display: flex;
        align-items: center;
        justify-content: center;
    `;
    
    modal.innerHTML = `
        <div style="
            background: white;
            padding: 30px;
            border-radius: 15px;
            max-width: 500px;
            width: 90%;
        ">
            <h3 style="margin: 0 0 20px 0; color: #2c3e50;">Detalles de ${studentName}</h3>
            <div style="margin-bottom: 15px;">
                <strong>Progreso actual:</strong> ${progress}%
            </div>
            <div style="margin-bottom: 15px;">
                <strong>Última sesión:</strong> Hace 3 días
            </div>
            <div style="margin-bottom: 15px;">
                <strong>Próxima cita:</strong> 25 de octubre, 2025
            </div>
            <div style="margin-bottom: 20px;">
                <strong>Estado:</strong> <span style="color: #27ae60;">Activo</span>
            </div>
            <button onclick="this.closest('div').parentElement.remove()" style="
                background: #f39c12;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 600;
                width: 100%;
            ">Cerrar</button>
        </div>
    `;
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
    
    document.body.appendChild(modal);
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 2000;
        max-width: 300px;
        transform: translateY(100%);
        transition: transform 0.3s ease;
    `;
    
    switch (type) {
        case 'success':
            notification.style.background = 'linear-gradient(135deg, #27ae60, #2ecc71)';
            break;
        case 'error':
            notification.style.background = 'linear-gradient(135deg, #e74c3c, #c0392b)';
            break;
        default:
            notification.style.background = 'linear-gradient(135deg, #f39c12, #e67e22)';
    }
    
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.transform = 'translateY(0)';
    }, 100);
    
    setTimeout(() => {
        notification.style.transform = 'translateY(100%)';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}
function animateStats() {
    const statNumbers = document.querySelectorAll('.stat-info h4');
    
    statNumbers.forEach(stat => {
        const target = parseInt(stat.textContent);
        let current = 0;
        const increment = target / 50;
        
        const counter = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(counter);
            }
            
            if (stat.textContent.includes('%')) {
                stat.textContent = Math.round(current) + '%';
            } else {
                stat.textContent = Math.round(current);
            }
        }, 30);
    });
}

// Función para cargar archivos de clientes
// Función para ver archivos de un cliente específico
function verArchivosCliente(clientId) {
    // Crear modal
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.7);
        z-index: 3000;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
    `;
    
    const modalContent = document.createElement('div');
    modalContent.style.cssText = `
        background: white;
        padding: 30px;
        border-radius: 15px;
        max-width: 900px;
        width: 100%;
        max-height: 85vh;
        overflow-y: auto;
        position: relative;
    `;
    
    // Crear header del modal
    const modalHeader = document.createElement('div');
    modalHeader.style.cssText = 'display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 2px solid #667eea; padding-bottom: 15px;';
    
    const modalTitle = document.createElement('h3');
    modalTitle.style.cssText = 'margin: 0; color: #2c3e50;';
    modalTitle.textContent = '📎 Archivos del Cliente';
    
    const closeButton = document.createElement('button');
    closeButton.style.cssText = 'background: #e74c3c; color: white; border: none; width: 35px; height: 35px; border-radius: 50%; cursor: pointer; font-size: 20px; line-height: 1; font-weight: bold;';
    closeButton.innerHTML = '&times;';
    closeButton.onclick = () => modal.remove();
    
    modalHeader.appendChild(modalTitle);
    modalHeader.appendChild(closeButton);
    
    // Crear contenedor de archivos
    const filesList = document.createElement('div');
    filesList.id = 'modal-files-list';
    filesList.style.minHeight = '200px';
    filesList.innerHTML = `
        <div style="text-align: center; padding: 40px 20px;">
            <div style="font-size: 48px; animation: spin 1s linear infinite;">⌛</div>
            <p style="color: #666; margin-top: 15px;">Cargando archivos...</p>
        </div>
    `;
    
    modalContent.appendChild(modalHeader);
    modalContent.appendChild(filesList);
    
    modal.appendChild(modalContent);
    document.body.appendChild(modal);
    
    // Cerrar modal al hacer clic fuera
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
    
    // Cargar archivos del cliente específico
    fetch(`/api/file/list/?client_id=${clientId}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log('Respuesta de API:', data);
        const filesList = document.getElementById('modal-files-list');
        filesList.innerHTML = '';
        
        if (data.files && data.files.length > 0) {
            const container = document.createElement('div');
            container.style.cssText = 'display: grid; gap: 12px;';
            
            data.files.forEach(file => {
                const fileCard = document.createElement('div');
                fileCard.style.cssText = 'background: #f8f9fa; padding: 18px; border-radius: 12px; border-left: 4px solid #667eea; transition: all 0.3s; cursor: pointer;';
                fileCard.addEventListener('mouseover', () => {
                    fileCard.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
                    fileCard.style.transform = 'translateY(-2px)';
                });
                fileCard.addEventListener('mouseout', () => {
                    fileCard.style.boxShadow = '';
                    fileCard.style.transform = '';
                });
                
                const flexContainer = document.createElement('div');
                flexContainer.style.cssText = 'display: flex; gap: 15px; align-items: start;';
                
                const iconDiv = document.createElement('div');
                iconDiv.style.cssText = 'font-size: 36px; flex-shrink: 0;';
                iconDiv.textContent = getFileIcon(file.file_type);
                
                const contentDiv = document.createElement('div');
                contentDiv.style.cssText = 'flex: 1; min-width: 0;';
                
                const headerDiv = document.createElement('div');
                headerDiv.style.cssText = 'display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;';
                
                const fileName = document.createElement('h4');
                fileName.style.cssText = 'margin: 0; color: #2c3e50; font-size: 15px; word-break: break-word;';
                fileName.textContent = file.file_name;
                
                const fileSize = document.createElement('span');
                fileSize.style.cssText = 'background: #667eea; color: white; padding: 3px 10px; border-radius: 20px; font-size: 11px; white-space: nowrap; margin-left: 10px;';
                fileSize.textContent = file.file_size;
                
                headerDiv.appendChild(fileName);
                headerDiv.appendChild(fileSize);
                
                const serviceDiv = document.createElement('div');
                serviceDiv.style.cssText = 'color: #666; font-size: 13px; margin-bottom: 8px;';
                serviceDiv.innerHTML = '<strong>Servicio:</strong> ' + file.assignment_service;
                
                const actionsDiv = document.createElement('div');
                actionsDiv.style.cssText = 'display: flex; gap: 10px; align-items: center; flex-wrap: wrap;';
                
                const dateSpan = document.createElement('span');
                dateSpan.style.cssText = 'color: #999; font-size: 12px;';
                dateSpan.textContent = '📅 ' + file.uploaded_at;
                
                const userSpan = document.createElement('span');
                userSpan.style.cssText = 'color: #999; font-size: 12px;';
                userSpan.textContent = '👤 ' + file.uploaded_by;
                
                const downloadBtn = document.createElement('button');
                downloadBtn.style.cssText = 'background: #27ae60; color: white; border: none; padding: 7px 14px; border-radius: 6px; cursor: pointer; font-size: 12px; font-weight: 600; margin-left: auto;';
                downloadBtn.textContent = '⬇️ Descargar';
                downloadBtn.addEventListener('click', () => downloadFile(file.id));
                
                actionsDiv.appendChild(dateSpan);
                actionsDiv.appendChild(userSpan);
                actionsDiv.appendChild(downloadBtn);
                
                contentDiv.appendChild(headerDiv);
                contentDiv.appendChild(serviceDiv);
                
                if (file.description) {
                    const descDiv = document.createElement('div');
                    descDiv.style.cssText = 'color: #888; font-size: 12px; margin-bottom: 8px; font-style: italic;';
                    descDiv.textContent = file.description;
                    contentDiv.appendChild(descDiv);
                }
                
                contentDiv.appendChild(actionsDiv);
                
                flexContainer.appendChild(iconDiv);
                flexContainer.appendChild(contentDiv);
                fileCard.appendChild(flexContainer);
                container.appendChild(fileCard);
            });
            
            filesList.appendChild(container);
        } else {
            const emptyDiv = document.createElement('div');
            emptyDiv.style.cssText = 'text-align: center; padding: 50px 20px;';
            emptyDiv.innerHTML = '<div style="font-size: 56px; margin-bottom: 15px; opacity: 0.3;">📁</div><h3 style="color: #666; margin-bottom: 10px;">No hay archivos</h3><p style="color: #999;">Este cliente aún no ha enviado archivos</p>';
            filesList.appendChild(emptyDiv);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        const filesList = document.getElementById('modal-files-list');
        filesList.innerHTML = '';
        const errorDiv = document.createElement('div');
        errorDiv.style.cssText = 'text-align: center; padding: 50px 20px;';
        errorDiv.innerHTML = '<div style="font-size: 56px; margin-bottom: 15px;">❌</div><h3 style="color: #e74c3c; margin-bottom: 10px;">Error al cargar archivos</h3><p style="color: #999;">Por favor, intenta de nuevo más tarde</p>';
        filesList.appendChild(errorDiv);
    });
}

// Función para obtener el icono según el tipo de archivo
function getFileIcon(fileType) {
    const icons = {
        'document': '📄',
        'image': '🖼️',
        'audio': '🎵',
        'video': '🎬',
        'other': '📎'
    };
    return icons[fileType] || '📎';
}

// Función para descargar archivo
function downloadFile(fileId) {
    window.location.href = `/api/file/download/${fileId}/`;
}
