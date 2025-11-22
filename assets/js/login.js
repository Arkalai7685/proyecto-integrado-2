document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    
    // El formulario ahora se envía directamente a Django
    // Django se encargará de la autenticación y redirección automática

    if (document.getElementById('forgotPassword')) {
        document.getElementById('forgotPassword').addEventListener('click', (e) => {
            e.preventDefault();
            showMessage('Se ha enviado un enlace de recuperación a tu email (función en desarrollo).', 'info');
        });
    }

    if (document.getElementById('resetPassword')) {
        document.getElementById('resetPassword').addEventListener('click', (e) => {
            e.preventDefault();
            showMessage('Redirigiendo a la página de restablecimiento (función en desarrollo).', 'info');
        });
    }

    const inputs = document.querySelectorAll('.input-container input');
    inputs.forEach(input => {
        input.addEventListener('focus', () => {
            input.parentElement.style.transform = 'scale(1.02)';
        });
        
        input.addEventListener('blur', () => {
            input.parentElement.style.transform = '';
        });
    });
});

function showMessage(text, type = 'info') {
    const existingMessage = document.querySelector('.notification-message');
    if (existingMessage) {
        existingMessage.remove();
    }
    
    const message = document.createElement('div');
    message.className = `notification-message ${type}`;
    message.textContent = text;
    
    Object.assign(message.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '15px 20px',
        borderRadius: '8px',
        color: 'white',
        fontSize: '14px',
        fontWeight: '500',
        zIndex: '3000',
        maxWidth: '300px',
        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.15)',
        transform: 'translateX(100%)',
        transition: 'transform 0.3s ease'
    });
    
    switch (type) {
        case 'success':
            message.style.background = 'linear-gradient(135deg, #27ae60, #2ecc71)';
            break;
        case 'error':
            message.style.background = 'linear-gradient(135deg, #e74c3c, #c0392b)';
            break;
        case 'info':
        default:
            message.style.background = 'linear-gradient(135deg, #3498db, #2980b9)';
            break;
    }
    
    document.body.appendChild(message);
    
    setTimeout(() => {
        message.style.transform = 'translateX(0)';
    }, 100);
    
    setTimeout(() => {
        message.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (message.parentNode) {
                message.parentNode.removeChild(message);
            }
        }, 300);
    }, 4000);
}

document.addEventListener('DOMContentLoaded', () => {
    const loginContainer = document.querySelector('.login-container');
    if (loginContainer) {
        let mouseX = 0;
        let mouseY = 0;
        
        document.addEventListener('mousemove', (e) => {
            mouseX = (e.clientX / window.innerWidth - 0.5) * 10;
            mouseY = (e.clientY / window.innerHeight - 0.5) * 10;
            
            loginContainer.style.transform = `translate(${mouseX}px, ${mouseY}px)`;
        });
    }
    
    const buttons = document.querySelectorAll('.user-type-btn, .login-btn');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple');
            
            if (!document.querySelector('#ripple-styles')) {
                const style = document.createElement('style');
                style.id = 'ripple-styles';
                style.textContent = `
                    .ripple {
                        position: absolute;
                        border-radius: 50%;
                        background: rgba(255, 255, 255, 0.3);
                        transform: scale(0);
                        animation: ripple-animation 0.6s linear;
                        pointer-events: none;
                    }
                    @keyframes ripple-animation {
                        to {
                            transform: scale(2);
                            opacity: 0;
                        }
                    }
                `;
                document.head.appendChild(style);
            }
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
});