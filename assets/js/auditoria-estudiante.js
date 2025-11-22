// Auditoría de Estudiante - JavaScript limpio

document.addEventListener('DOMContentLoaded', () => {
    initializeTabs();
    initializeProgressBars();
    initializeMaterials();
    initializeModal();
    initializeMessaging();
    setTimeout(() => {
        animateStats();
    }, 1000);
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
            setTimeout(() => { btn.style.transform = ''; }, 150);
        });
    });
}

function initializeProgressBars() {
    const progressBar = document.querySelector('.progress-bar');
    if (progressBar) {
        const targetProgress = parseInt(progressBar.getAttribute('data-progress'));
        setTimeout(() => { progressBar.style.width = targetProgress + '%'; }, 500);
    }
}

function initializeMaterials() {
    const materialItems = document.querySelectorAll('.material-item');
    materialItems.forEach((item, index) => {
        item.style.opacity = '0';
        item.style.transform = 'translateY(20px)';
        item.style.transition = 'all 0.5s ease';
        setTimeout(() => { item.style.opacity = '1'; item.style.transform = 'translateY(0)'; }, index * 100);
        item.addEventListener('click', () => { showMaterialDetails(item); });
    });
}

function showMaterialDetails(materialItem) {
    const title = materialItem.querySelector('h4').textContent;
    const description = materialItem.querySelector('p').textContent;
    const status = materialItem.getAttribute('data-status');
    const sessionId = materialItem.getAttribute('data-session-id'); // Obtener ID único
    
    let statusText = '';
    let statusColor = '';
    switch (status) {
        case 'completed': statusText = 'Completado ✅'; statusColor = '#a9d380'; break;
        case 'pending': statusText = 'Pendiente ⏳'; statusColor = '#f7bc7b'; break;
        case 'overdue': statusText = 'Atrasado ⚠️'; statusColor = '#dc7123'; break;
    }
    const modal = document.createElement('div');
    modal.style.cssText = 'position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); z-index:3000; display:flex; align-items:center; justify-content:center;';
    modal.innerHTML = `
        <div style="background:white; padding:40px; border-radius:20px; max-width:500px; width:90%;">
            <h3 style="margin:0 0 20px 0; color:#2c3e50;">${title}</h3>
            <div style="margin-bottom:15px;"><strong>Estado:</strong> <span style="color:${statusColor}; font-weight:600;">${statusText}</span></div>
            <div style="margin-bottom:20px; color:#555; line-height:1.5;">${description}</div>
            <div style="display:flex; gap:10px; justify-content:flex-end;">
                ${status !== 'completed' ? `<button onclick="markAsCompleted(this, '${sessionId}')" style="background:#a9d380; color:white; border:none; padding:10px 20px; border-radius:8px; cursor:pointer; font-weight:600;">Marcar Completado</button>` : ''}
                <button onclick="this.closest('div').parentElement.remove()" style="background:#95a5a6; color:white; border:none; padding:10px 20px; border-radius:8px; cursor:pointer; font-weight:600;">Cerrar</button>
            </div>
        </div>
    `;
    modal.addEventListener('click', (e) => { if (e.target === modal) modal.remove(); });
    document.body.appendChild(modal);
}

function markAsCompleted(btn, sessionId) {
    // Guardar en la base de datos
    fetch(`/api/session/${sessionId}/update-status/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: 'completed' })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Actualizar visualmente el elemento
            const materialItems = document.querySelectorAll('.material-item');
            let completedTitle = '';
            
            materialItems.forEach(item => {
                if (item.getAttribute('data-session-id') === sessionId) {
                    completedTitle = item.querySelector('h4').textContent;
                    item.setAttribute('data-status', 'completed');
                    item.className = 'material-item completed';
                    item.querySelector('p').textContent = `Completado el ${new Date().toLocaleDateString('es-ES')}`;
                    item.querySelector('.status-indicator').className = 'status-indicator completed-status';
                    item.querySelector('.status-indicator').textContent = '✓';
                    item.querySelector('.material-icon').textContent = '📁';
                }
            });
            
            updateStats();
            btn.closest('div').parentElement.remove();
            showNotification(`Sesión "${completedTitle}" marcada como completada`, 'success');
            
            // Marcar que se actualizó un cliente para que el dashboard se refresque
            const urlParams = new URLSearchParams(window.location.search);
            const clientId = urlParams.get('client');
            if (clientId) {
                localStorage.setItem('clientUpdated', clientId);
            }
            
            // Recargar después de 1 segundo para actualizar las estadísticas
            setTimeout(() => location.reload(), 1000);
        } else {
            showNotification('Error al actualizar la sesión: ' + data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error de conexión al actualizar la sesión', 'error');
    });
}

function updateStats() {
    const materials = document.querySelectorAll('.material-item');
    const completed = document.querySelectorAll('.material-item[data-status="completed"]').length;
    const pending = document.querySelectorAll('.material-item[data-status="pending"]').length;
    const overdue = document.querySelectorAll('.material-item[data-status="overdue"]').length;
    const statCards = document.querySelectorAll('.stat-card');
    if (statCards.length >= 3) {
        statCards[0].querySelector('.stat-number').textContent = completed;
        statCards[1].querySelector('.stat-number').textContent = pending;
        statCards[2].querySelector('.stat-number').textContent = overdue;
    }
    const totalMaterials = materials.length || 1;
    const progressPercent = Math.round((completed / totalMaterials) * 100);
    const progressBar = document.querySelector('.progress-bar');
    const progressPercentEl = document.querySelector('.progress-percent');
    if (progressBar && progressPercentEl) {
        progressBar.style.width = progressPercent + '%';
        progressBar.style.background = 'linear-gradient(135deg, #a9d380, #a9d380)';
        progressPercentEl.textContent = progressPercent + '%';
        progressPercentEl.style.color = '#a9d380';
    }
}

function initializeModal() {
    const addMaterialBtn = document.querySelector('.add-material-btn');
    const modal = document.getElementById('addMaterialModal');
    const closeModal = document.querySelector('.close-modal');
    const cancelBtn = document.querySelector('.cancel-btn');
    const addMaterialForm = document.getElementById('addMaterialForm');
    if (!addMaterialBtn || !modal || !closeModal || !cancelBtn || !addMaterialForm) return;
    addMaterialBtn.addEventListener('click', () => { modal.classList.add('active'); document.body.style.overflow = 'hidden'; });
    function closeModalFunc() { modal.classList.remove('active'); document.body.style.overflow = ''; addMaterialForm.reset(); }
    closeModal.addEventListener('click', closeModalFunc);
    cancelBtn.addEventListener('click', closeModalFunc);
    modal.addEventListener('click', (e) => { if (e.target === modal) closeModalFunc(); });
    addMaterialForm.addEventListener('submit', (e) => { e.preventDefault(); const formData = new FormData(addMaterialForm); const materialData = { title: formData.get('materialTitle'), type: formData.get('materialType'), deadline: formData.get('materialDeadline'), description: formData.get('materialDescription') }; addNewMaterial(materialData); closeModalFunc(); });
}

function addNewMaterial(data) {
    const materialsGrid = document.querySelector('.materials-grid');
    if (!materialsGrid) return;
    const currentDate = new Date();
    const deadlineDate = new Date(data.deadline);
    const isOverdue = deadlineDate < currentDate;
    const status = isOverdue ? 'overdue' : 'pending';
    const statusClass = isOverdue ? 'overdue' : 'pending';
    const statusIcon = isOverdue ? '⚠️' : '⏳';
    const materialIcon = '📂';
    const statusText = isOverdue ? `Vencido desde: ${deadlineDate.toLocaleDateString('es-ES')}` : `Fecha límite: ${deadlineDate.toLocaleDateString('es-ES')}`;
    const newMaterial = document.createElement('div');
    newMaterial.className = `material-item ${statusClass}`;
    newMaterial.setAttribute('data-status', status);
    newMaterial.style.opacity = '0';
    newMaterial.style.transform = 'translateY(20px)';
    newMaterial.innerHTML = `<div class="material-icon">${materialIcon}</div><div class="material-info"><h4>${data.title}</h4><p>${statusText}</p></div><div class="status-indicator ${status}-status">${statusIcon}</div>`;
    newMaterial.addEventListener('click', () => { showMaterialDetails(newMaterial); });
    materialsGrid.appendChild(newMaterial);
    setTimeout(() => { newMaterial.style.transition = 'all 0.5s ease'; newMaterial.style.opacity = '1'; newMaterial.style.transform = 'translateY(0)'; }, 100);
    updateStats();
    showNotification(`Material "${data.title}" añadido exitosamente`, 'success');
}

function initializeMessaging() {
    const nuevoMensajeBtn = document.querySelector('.nuevo-mensaje-btn');
    const enviarMensajeBtn = document.querySelector('.enviar-mensaje-btn');
    const mensajeInput = document.querySelector('.mensaje-input');
    const mensajesContainer = document.querySelector('.mensajes-container');
    if (!nuevoMensajeBtn || !enviarMensajeBtn || !mensajeInput || !mensajesContainer) return;
    nuevoMensajeBtn.addEventListener('click', () => { mensajeInput.focus(); mensajeInput.scrollIntoView({ behavior: 'smooth', block: 'center' }); });
    function sendMessage() { const messageText = mensajeInput.value.trim(); if (!messageText) return; const newMessage = document.createElement('div'); newMessage.className = 'mensaje empleado-mensaje'; newMessage.innerHTML = `<div class="mensaje-avatar"><div class="avatar-empleado">E</div></div><div class="mensaje-content"><div class="mensaje-header"><span class="mensaje-autor">Dr. Francisco Herrera</span><span class="mensaje-fecha">Ahora</span></div><div class="mensaje-texto">${messageText}</div></div>`; newMessage.style.opacity = '0'; newMessage.style.transform = 'translateY(20px)'; mensajesContainer.appendChild(newMessage); setTimeout(() => { newMessage.style.transition = 'all 0.5s ease'; newMessage.style.opacity = '1'; newMessage.style.transform = 'translateY(0)'; }, 100); mensajeInput.value = ''; mensajesContainer.scrollTop = mensajesContainer.scrollHeight; showNotification('Mensaje enviado', 'success'); }
    enviarMensajeBtn.addEventListener('click', sendMessage);
    mensajeInput.addEventListener('keydown', (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } });
}

function animateStats() {
    const statNumbers = document.querySelectorAll('.stat-number');
    statNumbers.forEach(stat => {
        const target = parseInt(stat.textContent) || 0;
        let current = 0;
        const increment = target / 30;
        const counter = setInterval(() => { current += increment; if (current >= target) { current = target; clearInterval(counter); } stat.textContent = Math.round(current); }, 50);
    });
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.style.cssText = 'position: fixed; bottom: 20px; right: 20px; padding: 15px 25px; border-radius: 10px; color: white; font-weight: 600; z-index: 4000; max-width: 350px; transform: translateX(400px); transition: transform 0.3s ease; box-shadow: 0 6px 25px rgba(0,0,0,0.2);';
    switch (type) { case 'success': notification.style.background = 'linear-gradient(135deg, #a9d380, #a9d380)'; break; case 'error': notification.style.background = 'linear-gradient(135deg, #dc7123, #dc7123)'; break; default: notification.style.background = 'linear-gradient(135deg, #73cbf4, #73cbf4)'; }
    notification.textContent = message;
    document.body.appendChild(notification);
    setTimeout(() => { notification.style.transform = 'translateX(0)'; }, 100);
    setTimeout(() => { notification.style.transform = 'translateX(400px)'; setTimeout(() => { notification.remove(); }, 300); }, 3000);
}

document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        const statCards = document.querySelectorAll('.stat-card');
        statCards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(30px)';
            card.style.transition = 'all 0.6s ease';
            setTimeout(() => { card.style.opacity = '1'; card.style.transform = 'translateY(0)'; }, 800 + (index * 200));
        });
    }, 500);
});

window.markAsCompleted = markAsCompleted;