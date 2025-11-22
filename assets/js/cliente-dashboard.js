document.addEventListener('DOMContentLoaded', () => {
    initializeProgressBar();
    initializeCalendar();
    initializeFolders();
    initializeMessages();
});

function initializeProgressBar() {
    const progressBar = document.querySelector('.progress-bar');
    const progressPercentage = document.querySelector('.progress-percentage');
    
    if (progressBar) {
        const targetProgress = parseInt(progressBar.getAttribute('data-progress'));
        
        setTimeout(() => {
            progressBar.style.width = targetProgress + '%';
        }, 500);
        
        let currentProgress = 0;
        const increment = targetProgress / 100;
        
        const counter = setInterval(() => {
            currentProgress += increment;
            if (currentProgress >= targetProgress) {
                currentProgress = targetProgress;
                clearInterval(counter);
            }
            progressPercentage.textContent = Math.round(currentProgress) + '%';
        }, 20);
    }
}

function initializeCalendar() {
    const calendarDays = document.getElementById('calendarDays');
    const monthSelect = document.querySelector('.month-select');
    const yearSelect = document.querySelector('.year-select');
    const prevBtn = document.querySelector('[data-dir="prev"]');
    const nextBtn = document.querySelector('[data-dir="next"]');
    
    let currentDate = new Date();
    let currentMonth = currentDate.getMonth();
    let currentYear = currentDate.getFullYear();
    
    const sessions = {
        '2025-10-25': { type: 'asesoria', title: 'Revisión Capítulo 4' },
        '2025-10-30': { type: 'terapia', title: 'Sesión de Apoyo' },
        '2025-11-05': { type: 'asesoria', title: 'Presentación Marco Teórico' },
        '2025-11-12': { type: 'terapia', title: 'Manejo de Estrés' },
        '2025-11-20': { type: 'asesoria', title: 'Revisión Metodología' }
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
            const hasSession = sessions[dateStr];
            
            const dayEl = createDayElement(day, false, isToday, hasSession);
            calendarDays.appendChild(dayEl);
        }
        
        const totalCells = calendarDays.children.length;
        const remainingCells = 42 - totalCells;
        for (let i = 0; i < remainingCells; i++) {
            const dayEl = createDayElement('', true);
            calendarDays.appendChild(dayEl);
        }
    }
    
    function createDayElement(day, isOtherMonth = false, isToday = false, hasSession = null) {
        const dayEl = document.createElement('div');
        dayEl.className = 'calendar-day';
        dayEl.textContent = day;
        
        if (isOtherMonth) {
            dayEl.classList.add('other-month');
        }
        
        if (isToday) {
            dayEl.classList.add('today');
        }
        
        if (hasSession) {
            dayEl.classList.add('has-session');
            dayEl.title = hasSession.title;
            
            dayEl.addEventListener('click', () => {
                showSessionDetails(day, hasSession);
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
    
    function showSessionDetails(day, session) {
        const modal = createSessionModal(day, session);
        document.body.appendChild(modal);
        
        setTimeout(() => {
            modal.style.opacity = '1';
            modal.querySelector('.session-modal-content').style.transform = 'scale(1)';
        }, 10);
    }
    
    function createSessionModal(day, session) {
        const modal = document.createElement('div');
        modal.className = 'session-modal';
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
        
        modal.innerHTML = `
            <div class="session-modal-content" style="
                background: white;
                padding: 30px;
                border-radius: 15px;
                max-width: 400px;
                width: 90%;
                transform: scale(0.9);
                transition: transform 0.3s ease;
            ">
                <h3 style="margin: 0 0 15px 0; color: #2c3e50;">Sesión del ${day}</h3>
                <p style="margin: 0 0 10px 0; color: #34495e;"><strong>Tipo:</strong> ${session.type}</p>
                <p style="margin: 0 0 20px 0; color: #34495e;"><strong>Título:</strong> ${session.title}</p>
                <button onclick="this.closest('.session-modal').remove()" style="
                    background: #ff8c42;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 8px;
                    cursor: pointer;
                    font-weight: 600;
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
        }, index * 100);
    });
}

function initializeMessages() {
    const messageCards = document.querySelectorAll('.message-card');
    
    messageCards.forEach((card, index) => {
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 200);
        
        card.addEventListener('click', () => {
            if (card.classList.contains('urgent')) {
                showNotification('Recordatorio marcado como leído', 'success');
            }
        });
    });
    
    updateSessionCountdown();
    setInterval(updateSessionCountdown, 1000 * 60 * 60);
}

function updateSessionCountdown() {
    const urgentMessage = document.querySelector('.message-card.urgent h4');
    if (urgentMessage) {
        const nextSession = new Date('2025-11-15');
        const now = new Date();
        const diffTime = nextSession - now;
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        
        if (diffDays > 0) {
            urgentMessage.textContent = `TU PRÓXIMA SESIÓN ES EN ${diffDays} DÍAS`;
        } else if (diffDays === 0) {
            urgentMessage.textContent = 'TU PRÓXIMA SESIÓN ES HOY';
            urgentMessage.parentElement.parentElement.style.animation = 'pulse 1s infinite';
        } else {
            urgentMessage.textContent = 'TIENES SESIONES PENDIENTES';
        }
    }
}

function addProgressPoint() {
    const currentProgress = parseInt(document.querySelector('.progress-bar').getAttribute('data-progress'));
    const newProgress = Math.min(currentProgress + 5, 100);
    
    document.querySelector('.progress-bar').setAttribute('data-progress', newProgress);
    document.querySelector('.progress-bar').style.width = newProgress + '%';
    document.querySelector('.progress-percentage').textContent = newProgress + '%';
    
    if (newProgress % 20 === 0) {
        showAchievement(`¡${newProgress}% completado!`, '🎉');
    }
}

function showAchievement(title, icon) {
    const achievement = document.createElement('div');
    achievement.className = 'floating-achievement';
    achievement.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: linear-gradient(135deg, #f39c12, #e67e22);
        color: white;
        padding: 15px 20px;
        border-radius: 10px;
        box-shadow: 0 5px 20px rgba(243, 156, 18, 0.4);
        z-index: 2000;
        transform: translateX(100%);
        transition: transform 0.5s ease;
    `;
    
    achievement.innerHTML = `
        <div style="display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 20px;">${icon}</span>
            <span style="font-weight: 600;">${title}</span>
        </div>
    `;
    
    document.body.appendChild(achievement);
    
    setTimeout(() => {
        achievement.style.transform = 'translateX(0)';
    }, 100);
    
    setTimeout(() => {
        achievement.style.transform = 'translateX(100%)';
        setTimeout(() => {
            achievement.remove();
        }, 500);
    }, 3000);
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
    const folders = document.querySelectorAll('.folder-item');
    const messages = document.querySelectorAll('.message-card');
    
    folders.forEach(folder => {
        folder.style.opacity = '0';
        folder.style.transform = 'translateY(20px)';
        folder.style.transition = 'all 0.5s ease';
    });
    
    messages.forEach(message => {
        message.style.opacity = '0';
        message.style.transform = 'translateY(20px)';
        message.style.transition = 'all 0.5s ease';
    });
});