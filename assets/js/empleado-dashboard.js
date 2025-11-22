document.addEventListener('DOMContentLoaded', () => {
    initializeTabs();
    initializeStudentProgressBars();
    initializeEmployeeCalendar();
    initializeFolders();
    initializeSolicitudes();
    initializeStudentCards();
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

function initializeEmployeeCalendar() {
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
            { time: '10:00', student: 'María García', type: 'asesoría' },
            { time: '14:30', student: 'Carlos López', type: 'revisión' }
        ],
        '2025-10-25': [
            { time: '11:00', student: 'Ana Martínez', type: 'terapia' }
        ],
        '2025-10-28': [
            { time: '09:00', student: 'Pedro Rodríguez', type: 'asesoría' },
            { time: '15:00', student: 'Laura Silva', type: 'consulta' }
        ],
        '2025-11-02': [
            { time: '10:30', student: 'Miguel Torres', type: 'revisión' }
        ],
        '2025-11-05': [
            { time: '13:00', student: 'Sofia Mendez', type: 'asesoría' }
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
                border-left: 4px solid #3498db;
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
                    background: #ff8c42;
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
    const acceptBtns = document.querySelectorAll('.accept-btn');
    const declineBtns = document.querySelectorAll('.decline-btn');
    
    acceptBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const solicitudItem = btn.closest('.solicitud-item');
            const studentName = solicitudItem.querySelector('h4').textContent;
            
            solicitudItem.style.transform = 'translateX(-100%)';
            solicitudItem.style.opacity = '0';
            
            setTimeout(() => {
                solicitudItem.remove();
                updateSolicitudesCount();
                showNotification(`Solicitud de ${studentName} aceptada`, 'success');
            }, 300);
        });
    });
    
    declineBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const solicitudItem = btn.closest('.solicitud-item');
            const studentName = solicitudItem.querySelector('h4').textContent;
            
            solicitudItem.style.transform = 'translateX(100%)';
            solicitudItem.style.opacity = '0';
            
            setTimeout(() => {
                solicitudItem.remove();
                updateSolicitudesCount();
                showNotification(`Solicitud de ${studentName} rechazada`, 'error');
            }, 300);
        });
    });
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
            const studentName = studentCard.querySelector('.avatar-img').alt;
            
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
                background: #ff8c42;
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
            notification.style.background = 'linear-gradient(135deg, #3498db, #2980b9)';
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

document.addEventListener('DOMContentLoaded', () => {
    const studentCards = document.querySelectorAll('.student-card');
    const folders = document.querySelectorAll('.folder-item');
    
    studentCards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'all 0.6s ease';
    });
    
    folders.forEach(folder => {
        folder.style.opacity = '0';
        folder.style.transform = 'translateY(20px)';
        folder.style.transition = 'all 0.5s ease';
    });
    
    setTimeout(() => {
        animateStats();
    }, 1000);
});

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