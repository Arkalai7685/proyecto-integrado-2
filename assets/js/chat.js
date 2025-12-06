// Sistema de Chat Interno
class ChatSystem {
    constructor() {
        this.currentAssignmentId = null;
        this.messagePollingInterval = null;
        this.conversations = [];
        this.init();
    }

    init() {
        this.loadConversations();
        this.setupEventListeners();
        this.startUnreadCountPolling();
    }

    setupEventListeners() {
        // Enter para enviar mensaje
        const chatInput = document.getElementById('chatInput');
        if (chatInput) {
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }

        // Botón enviar
        const sendBtn = document.getElementById('sendMessageBtn');
        if (sendBtn) {
            sendBtn.addEventListener('click', () => this.sendMessage());
        }
    }

    async loadConversations() {
        try {
            const response = await fetch('/api/chat/conversations/');
            const data = await response.json();

            if (data.success) {
                this.conversations = data.conversations;
                this.renderConversations();
            }
        } catch (error) {
            console.error('Error loading conversations:', error);
        }
    }

    renderConversations() {
        const container = document.getElementById('chatConversationsList');
        if (!container) return;

        if (this.conversations.length === 0) {
            container.innerHTML = `
                <div style="padding: 20px; text-align: center; color: #a0aec0;">
                    <p>No hay conversaciones disponibles</p>
                </div>
            `;
            return;
        }

        container.innerHTML = this.conversations.map(conv => {
            const displayName = conv.client_name || conv.employee_name;
            const isActive = conv.assignment_id === this.currentAssignmentId;
            
            return `
                <div class="conversation-item ${isActive ? 'active' : ''}" 
                     onclick="chatSystem.openConversation(${conv.assignment_id})">
                    <div class="conversation-header">
                        <span class="conversation-name">${displayName}</span>
                        <span class="conversation-service">${conv.service_name}</span>
                    </div>
                    <div class="conversation-preview">${conv.last_message || 'Sin mensajes'}</div>
                    <div class="conversation-footer">
                        <span>${conv.last_message_time}</span>
                        ${conv.unread_count > 0 ? `<span class="unread-badge">${conv.unread_count}</span>` : ''}
                    </div>
                </div>
            `;
        }).join('');
    }

    async openConversation(assignmentId) {
        this.currentAssignmentId = assignmentId;
        
        // Actualizar UI
        this.renderConversations();
        
        // Cargar mensajes
        await this.loadMessages(assignmentId);
        
        // Iniciar polling de mensajes
        this.startMessagePolling();
        
        // Mostrar área de chat
        document.getElementById('chatMainArea').style.display = 'flex';
    }

    async loadMessages(assignmentId) {
        try {
            const response = await fetch(`/api/chat/${assignmentId}/messages/`);
            const data = await response.json();

            if (data.success) {
                this.renderMessages(data.messages);
                this.updateChatHeader(data.other_user, data.service_name);
            }
        } catch (error) {
            console.error('Error loading messages:', error);
        }
    }

    updateChatHeader(otherUser, serviceName) {
        const headerInfo = document.querySelector('.chat-header-info');
        if (headerInfo) {
            headerInfo.innerHTML = `
                <h3>${otherUser.name}</h3>
                <p>${serviceName}</p>
            `;
        }
    }

    renderMessages(messages) {
        const container = document.getElementById('chatMessagesContainer');
        if (!container) return;

        if (messages.length === 0) {
            container.innerHTML = `
                <div class="chat-empty-state">
                    <p>No hay mensajes aún. Inicia la conversación.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = messages.map(msg => `
            <div class="chat-message ${msg.is_mine ? 'mine' : ''}">
                <div class="message-bubble">
                    <p class="message-text">${this.escapeHtml(msg.message)}</p>
                    <span class="message-time">${msg.created_at}</span>
                </div>
            </div>
        `).join('');

        // Scroll al final
        container.scrollTop = container.scrollHeight;
    }

    async sendMessage() {
        if (!this.currentAssignmentId) return;

        const input = document.getElementById('chatInput');
        const message = input.value.trim();

        if (!message) return;

        try {
            const response = await fetch(`/api/chat/${this.currentAssignmentId}/send/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({ message })
            });

            const data = await response.json();

            if (data.success) {
                input.value = '';
                this.appendMessage(data.message);
                this.loadConversations(); // Actualizar lista
            } else {
                alert(data.error || 'Error al enviar mensaje');
            }
        } catch (error) {
            console.error('Error sending message:', error);
            alert('Error de conexión al enviar mensaje');
        }
    }

    appendMessage(message) {
        const container = document.getElementById('chatMessagesContainer');
        if (!container) return;

        // Remover estado vacío si existe
        const emptyState = container.querySelector('.chat-empty-state');
        if (emptyState) {
            emptyState.remove();
        }

        const messageEl = document.createElement('div');
        messageEl.className = `chat-message ${message.is_mine ? 'mine' : ''}`;
        messageEl.innerHTML = `
            <div class="message-bubble">
                <p class="message-text">${this.escapeHtml(message.message)}</p>
                <span class="message-time">${message.created_at}</span>
            </div>
        `;
        container.appendChild(messageEl);
        container.scrollTop = container.scrollHeight;
    }

    startMessagePolling() {
        // Limpiar polling anterior
        if (this.messagePollingInterval) {
            clearInterval(this.messagePollingInterval);
        }

        // Polling cada 3 segundos
        this.messagePollingInterval = setInterval(() => {
            if (this.currentAssignmentId) {
                this.loadMessages(this.currentAssignmentId);
            }
        }, 3000);
    }

    startUnreadCountPolling() {
        setInterval(async () => {
            try {
                const response = await fetch('/api/chat/unread-count/');
                const data = await response.json();

                if (data.success) {
                    this.updateUnreadBadge(data.unread_count);
                }
            } catch (error) {
                console.error('Error fetching unread count:', error);
            }
        }, 10000); // Cada 10 segundos
    }

    updateUnreadBadge(count) {
        const badge = document.getElementById('chatUnreadBadge');
        if (badge) {
            if (count > 0) {
                badge.textContent = count;
                badge.style.display = 'inline-block';
            } else {
                badge.style.display = 'none';
            }
        }
    }

    getCsrfToken() {
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

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Sistema de subida de archivos para empleados
class FileUploadSystem {
    constructor() {
        this.currentAssignmentId = null;
    }

    showUploadModal(assignmentId) {
        this.currentAssignmentId = assignmentId;
        
        const modal = document.createElement('div');
        modal.className = 'file-upload-modal';
        modal.id = 'fileUploadModal';
        modal.innerHTML = `
            <div class="file-upload-content">
                <h3>Compartir Archivo con Cliente</h3>
                <form class="file-upload-form" id="fileUploadForm">
                    <div>
                        <label>Seleccionar archivo (máx. 10MB)</label>
                        <input type="file" id="fileToUpload" required 
                               accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png,.gif,.mp3,.mp4,.zip">
                    </div>
                    <div>
                        <label>Descripción (opcional)</label>
                        <textarea id="fileDescription" placeholder="Agrega una descripción del archivo..."></textarea>
                    </div>
                    <div class="file-upload-actions">
                        <button type="button" class="btn-cancel-upload" onclick="fileUploadSystem.closeModal()">
                            Cancelar
                        </button>
                        <button type="submit" class="btn-upload-file">
                            Subir Archivo
                        </button>
                    </div>
                </form>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Event listener para el formulario
        document.getElementById('fileUploadForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.uploadFile();
        });
        
        // Cerrar al hacer clic fuera
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.closeModal();
            }
        });
    }

    async uploadFile() {
        const fileInput = document.getElementById('fileToUpload');
        const description = document.getElementById('fileDescription').value;
        const file = fileInput.files[0];

        if (!file) {
            alert('Por favor selecciona un archivo');
            return;
        }

        // Validar tamaño
        if (file.size > 10 * 1024 * 1024) {
            alert('El archivo es demasiado grande. Tamaño máximo: 10MB');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);
        formData.append('assignment_id', this.currentAssignmentId);
        formData.append('description', description);

        try {
            const response = await fetch('/api/chat/upload-file/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                alert('Archivo compartido exitosamente');
                this.closeModal();
                
                // Recargar archivos si estamos en esa vista
                if (typeof verArchivosCliente === 'function' && chatSystem.currentAssignmentId) {
                    // Obtener el client_id de la asignación actual
                    const conv = chatSystem.conversations.find(c => c.assignment_id === this.currentAssignmentId);
                    if (conv && conv.client_id) {
                        verArchivosCliente(conv.client_id);
                    }
                }
            } else {
                alert(data.error || 'Error al subir archivo');
            }
        } catch (error) {
            console.error('Error uploading file:', error);
            alert('Error de conexión al subir archivo');
        }
    }

    closeModal() {
        const modal = document.getElementById('fileUploadModal');
        if (modal) {
            modal.remove();
        }
    }

    getCsrfToken() {
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
}

// Inicializar sistemas
let chatSystem, fileUploadSystem;

document.addEventListener('DOMContentLoaded', function() {
    chatSystem = new ChatSystem();
    fileUploadSystem = new FileUploadSystem();
});
