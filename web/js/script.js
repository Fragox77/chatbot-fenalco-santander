// Configuración global
const CONFIG = {
    RASA_SERVER_URL: 'http://localhost:5005/webhooks/rest/webhook',
    TYPING_DELAY: 1000,
    MESSAGE_ANIMATION_DELAY: 300
};

// Estado global de la aplicación
let chatState = {
    isOpen: false,
    isTyping: false,
    messageHistory: [],
    userId: generateUserId()
};

// Generar ID único para el usuario
function generateUserId() {
    return 'user_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
}

// Inicialización cuando se carga la página
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    showWelcomeMessage();
});

// Inicializar la aplicación
function initializeApp() {
    // Configurar scroll suave para navegación
    setupSmoothScrolling();

    // Configurar animaciones de entrada
    setupScrollAnimations();

    // Verificar conexión con Rasa
    checkRasaConnection();
}

// Configurar event listeners
function setupEventListeners() {
    // Navegación móvil
    const menuToggle = document.getElementById('menuToggle');
    if (menuToggle) {
        menuToggle.addEventListener('click', toggleMobileMenu);
    }

    // Formulario de contacto
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', handleContactForm);
    }

    // Input del chat
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.addEventListener('keypress', handleKeyPress);
        chatInput.addEventListener('input', handleInputChange);
    }

    // Botón de envío del chat
    const sendButton = document.getElementById('sendButton');
    if (sendButton) {
        sendButton.addEventListener('click', sendMessage);
    }

    // Cerrar chat al hacer clic fuera
    document.addEventListener('click', handleOutsideClick);
}

// Navegación suave
function setupSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });

                // Actualizar navegación activa
                updateActiveNavLink(this);
            }
        });
    });
}

// Actualizar enlace de navegación activo
function updateActiveNavLink(clickedLink) {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    clickedLink.classList.add('active');
}

// Animaciones al hacer scroll
function setupScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observar elementos para animación
    document.querySelectorAll('.program-card, .feature, .contact-info').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
}

// Verificar conexión con Rasa
async function checkRasaConnection() {
    try {
        const response = await fetch(CONFIG.RASA_SERVER_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                sender: chatState.userId,
                message: '/greet'
            })
        });

        if (!response.ok) {
            console.warn('Rasa server not available. Using fallback responses.');
            showConnectionWarning();
        }
    } catch (error) {
        console.warn('Could not connect to Rasa server:', error);
        showConnectionWarning();
    }
}

// Mostrar advertencia de conexión
function showConnectionWarning() {
    const chatMessages = document.getElementById('chatMessages');
    if (chatMessages) {
        const warningMessage = createMessageElement(
            'El servidor de chat está temporalmente no disponible. Las respuestas pueden ser limitadas.',
            'bot',
            true
        );
        chatMessages.appendChild(warningMessage);
    }
}

// Mostrar mensaje de bienvenida
function showWelcomeMessage() {
    setTimeout(() => {
        const notification = document.getElementById('chatNotification');
        if (notification) {
            notification.style.display = 'flex';

            // Animar notificación
            setTimeout(() => {
                notification.style.animation = 'pulse 2s infinite';
            }, 1000);
        }
    }, 3000);
}

// Funciones del Chat
function toggleChat() {
    const chatWidget = document.getElementById('chatWidget');
    const chatButton = document.getElementById('chatButton');
    const notification = document.getElementById('chatNotification');

    if (chatState.isOpen) {
        closeChat();
    } else {
        openChat();
    }
}

function openChat() {
    const chatWidget = document.getElementById('chatWidget');
    const chatButton = document.getElementById('chatButton');
    const notification = document.getElementById('chatNotification');

    if (chatWidget) {
        chatWidget.classList.add('active');
        chatState.isOpen = true;

        // Ocultar notificación
        if (notification) {
            notification.style.display = 'none';
        }

        // Cambiar icono del botón
        if (chatButton) {
            chatButton.innerHTML = '<i class="fas fa-times"></i>';
        }

        // Enfocar input
        const chatInput = document.getElementById('chatInput');
        if (chatInput) {
            setTimeout(() => chatInput.focus(), 300);
        }

        // Scroll al último mensaje
        scrollToBottom();
    }
}

function closeChat() {
    const chatWidget = document.getElementById('chatWidget');
    const chatButton = document.getElementById('chatButton');

    if (chatWidget) {
        chatWidget.classList.remove('active');
        chatState.isOpen = false;

        // Restaurar icono del botón
        if (chatButton) {
            chatButton.innerHTML = '<i class="fas fa-comments"></i>';
        }
    }
}

// Manejar tecla Enter en el chat
function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// Manejar cambios en el input
function handleInputChange(event) {
    const sendButton = document.getElementById('sendButton');
    if (sendButton) {
        if (event.target.value.trim()) {
            sendButton.style.background = 'var(--primary-color)';
            sendButton.style.transform = 'scale(1.05)';
        } else {
            sendButton.style.background = '#ccc';
            sendButton.style.transform = 'scale(1)';
        }
    }
}

// Enviar mensaje
async function sendMessage() {
    const chatInput = document.getElementById('chatInput');
    const message = chatInput.value.trim();

    if (!message || chatState.isTyping) return;

    // Limpiar input
    chatInput.value = '';
    handleInputChange({ target: { value: '' } });

    // Mostrar mensaje del usuario
    displayMessage(message, 'user');

    // Mostrar indicador de escritura
    showTypingIndicator();

    try {
        // Enviar a Rasa
        const response = await sendToRasa(message);

        // Ocultar indicador de escritura
        hideTypingIndicator();

        // Mostrar respuesta(s) del bot
        if (response && response.length > 0) {
            for (let i = 0; i < response.length; i++) {
                setTimeout(() => {
                    displayMessage(response[i].text, 'bot');
                }, i * CONFIG.MESSAGE_ANIMATION_DELAY);
            }
        } else {
            // Respuesta de fallback
            setTimeout(() => {
                displayMessage(getFallbackResponse(message), 'bot');
            }, CONFIG.TYPING_DELAY);
        }

    } catch (error) {
        console.error('Error sending message:', error);
        hideTypingIndicator();

        setTimeout(() => {
            displayMessage(
                'Disculpa, hay un problema técnico. Por favor intenta de nuevo o contáctanos directamente.',
                'bot'
            );
        }, CONFIG.TYPING_DELAY);
    }
}

// Enviar mensaje a Rasa
async function sendToRasa(message) {
    const response = await fetch(CONFIG.RASA_SERVER_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            sender: chatState.userId,
            message: message
        })
    });

    if (!response.ok) {
        throw new Error('Network response was not ok');
    }

    return await response.json();
}

// Mostrar mensaje en el chat
function displayMessage(text, sender) {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;

    const messageElement = createMessageElement(text, sender);
    chatMessages.appendChild(messageElement);

    // Guardar en historial
    chatState.messageHistory.push({ text, sender, timestamp: new Date() });

    // Scroll al final
    scrollToBottom();
}

// Crear elemento de mensaje
function createMessageElement(text, sender, isWarning = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    if (isWarning) {
        contentDiv.style.background = '#fff3cd';
        contentDiv.style.color = '#856404';
        contentDiv.style.border = '1px solid #ffeaa7';
    }

    // Procesar texto con formato
    contentDiv.innerHTML = formatMessageText(text);

    const timeDiv = document.createElement('div');
    timeDiv.className = 'message-time';
    timeDiv.textContent = new Date().toLocaleTimeString('es-ES', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });

    messageDiv.appendChild(contentDiv);
    messageDiv.appendChild(timeDiv);

    return messageDiv;
}

// Formatear texto del mensaje
function formatMessageText(text) {
    return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // Negrita
        .replace(/\*(.*?)\*/g, '<em>$1</em>') // Cursiva
        .replace(/\n/g, '<br>') // Saltos de línea
        .replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>') // Enlaces
        .replace(/•/g, '•'); // Viñetas
}

// Mostrar indicador de escritura
function showTypingIndicator() {
    chatState.isTyping = true;

    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;

    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot-message typing-indicator';
    typingDiv.id = 'typingIndicator';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = `
        <div class="typing-dots">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;

    typingDiv.appendChild(contentDiv);
    chatMessages.appendChild(typingDiv);

    // Agregar estilos para los puntos de escritura
    const style = document.createElement('style');
    style.textContent = `
        .typing-dots {
            display: flex;
            gap: 4px;
            padding: 8px 0;
        }
        .typing-dots span {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.7);
            animation: typing 1.4s infinite ease-in-out;
        }
        .typing-dots span:nth-child(1) { animation-delay: -0.32s; }
        .typing-dots span:nth-child(2) { animation-delay: -0.16s; }
        @keyframes typing {
            0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
            40% { transform: scale(1); opacity: 1; }
        }
    `;
    document.head.appendChild(style);

    scrollToBottom();
}

// Ocultar indicador de escritura
function hideTypingIndicator() {
    chatState.isTyping = false;
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// Scroll al final del chat
function scrollToBottom() {
    const chatMessages = document.getElementById('chatMessages');
    if (chatMessages) {
        setTimeout(() => {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }, 100);
    }
}

// Respuestas de fallback
function getFallbackResponse(message) {
    const fallbackResponses = [
        "Te puedo ayudar con información sobre nuestros diplomados, talleres, seminarios, masterclass y bootcamps. ¿Qué te interesa saber?",
        "Puedo darte información sobre precios, horarios, modalidades e inscripciones. ¿Sobre qué tema específico quieres saber más?",
        "Estoy aquí para ayudarte con información sobre nuestros programas de formación empresarial. ¿En qué puedo asistirte?",
        "Para obtener información detallada, puedes contactarnos al (607) 697-5555 o escribir a formacion@fenalcosantander.com"
    ];

    // Respuestas específicas basadas en palabras clave
    const lowerMessage = message.toLowerCase();

    if (lowerMessage.includes('precio') || lowerMessage.includes('costo') || lowerMessage.includes('valor')) {
        return "💰 Nuestros precios varían según el programa:\n\n• Diplomados: $720.000 - $950.000\n• Talleres: $250.000 - $380.000\n• Bootcamps: $590.000 - $680.000\n• Masterclass: $450.000 - $520.000\n\nTenemos descuentos del 15% para empresas afiliadas y 10% para grupos de 3+ personas.";
    }

    if (lowerMessage.includes('horario') || lowerMessage.includes('hora')) {
        return "⏰ Ofrecemos múltiples horarios:\n\n• Jornada diurna: Lunes a viernes 8:00 AM - 12:00 PM\n• Jornada nocturna: Lunes a viernes 6:00 PM - 10:00 PM\n• Sábados: 8:00 AM - 5:00 PM\n• Modalidad virtual: Horarios flexibles";
    }

    if (lowerMessage.includes('contacto') || lowerMessage.includes('teléfono') || lowerMessage.includes('dirección')) {
        return "📞 Información de contacto:\n\n• Teléfono: (607) 697-5555\n• Email: formacion@fenalcosantander.com\n• Dirección: Calle 35 No. 10-43, Bucaramanga\n• Horarios: Lunes a viernes 8:00 AM - 6:00 PM";
    }

    return fallbackResponses[Math.floor(Math.random() * fallbackResponses.length)];
}

// Menú móvil
function toggleMobileMenu() {
    const navMenu = document.querySelector('.nav-menu');
    if (navMenu) {
        navMenu.classList.toggle('active');
    }
}

// Manejar clics fuera del chat
function handleOutsideClick(event) {
    const chatWidget = document.getElementById('chatWidget');
    const chatButton = document.getElementById('chatButton');

    if (chatState.isOpen && chatWidget && !chatWidget.contains(event.target) && !chatButton.contains(event.target)) {
        // No cerrar automáticamente para mejor UX
        // closeChat();
    }
}

// Formulario de contacto
function handleContactForm(event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData);

    // Simular envío
    const submitButton = event.target.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;

    submitButton.textContent = 'Enviando...';
    submitButton.disabled = true;

    setTimeout(() => {
        alert('¡Gracias por tu consulta! Te contactaremos pronto.');
        event.target.reset();
        submitButton.textContent = originalText;
        submitButton.disabled = false;
    }, 2000);
}

// Utilidades
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Exportar funciones globales para uso en HTML
window.openChat = openChat;
window.closeChat = closeChat;
window.toggleChat = toggleChat;
window.sendMessage = sendMessage;
window.handleKeyPress = handleKeyPress;

// Configuración adicional para PWA (opcional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        // Registrar service worker si está disponible
        // navigator.serviceWorker.register('/sw.js');
    });
}

console.log('🤖 Fenalco Santander Chat initialized successfully!');