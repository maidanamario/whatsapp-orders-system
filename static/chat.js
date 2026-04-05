/* ========================================
   VARIABLES Y ESTADO GLOBAL
   ======================================== */

// Generar un usuario único tipo web_user_XXXXX
// Se usa para identificar cada sesión de chat
const usuarioId = 'web_user_' + Math.floor(Math.random() * 100000);

// Variable para controlar si estamos enviando un mensaje
// Evita que se envíen múltiples mensajes al mismo tiempo
let enviando = false;

/* ========================================
   INICIALIZACIÓN
   ======================================== */

// Se ejecuta cuando el DOM está completamente cargado
document.addEventListener('DOMContentLoaded', function() {
    // Obtener referencias a elementos del DOM
    const inputMensaje = document.getElementById('messageInput');
    const botonEnviar = document.getElementById('sendButton');
    
    // Permitir enviar mensaje con la tecla Enter
    inputMensaje.addEventListener('keypress', function(evento) {
        // Si se presiona Enter y no es Shift+Enter
        if (evento.key === 'Enter' && !evento.shiftKey) {
            evento.preventDefault();
            // Llamar función para enviar mensaje
            enviarMensaje();
        }
    });
    
    // Enviar mensaje al hacer click en botón
    botonEnviar.addEventListener('click', enviarMensaje);
    
    // Mostrar mensaje de bienvenida del bot
    mostrarMensajeBot('¡Hola! Bienvenido al sistema de órdenes. Escribe "hola" para comenzar.');
});

/* ========================================
   FUNCIÓN PRINCIPAL: ENVIAR MENSAJE
   ======================================== */

/**
 * Envía el mensaje del usuario al servidor
 * - Obtiene el texto del input
 * - Valida que no esté vacío
 * - Muestra el mensaje en pantalla
 * - Hace fetch al endpoint /mensaje
 * - Muestra la respuesta del bot
 * - Limpia el input
 */
function enviarMensaje() {
    // Obtener elemento input
    const inputMensaje = document.getElementById('messageInput');
    // Obtener el texto y eliminar espacios en blanco
    const mensaje = inputMensaje.value.trim();
    
    // Validar que el mensaje no esté vacío
    if (!mensaje) {
        console.warn('Mensaje vacío, no se envía');
        return;
    }
    
    // Evitar múltiples envíos simultáneos
    if (enviando) {
        console.warn('Ya se está enviando un mensaje');
        return;
    }
    
    // Marcar que estamos enviando
    enviando = true;
    
    // Mostrar mensaje del usuario en pantalla
    mostrarMensajeUsuario(mensaje);
    
    // Limpiar el input inmediatamente
    inputMensaje.value = '';
    
    // Preparar datos para enviar al servidor
    const datos = {
        usuario: usuarioId,      // ID único del usuario
        mensaje: mensaje          // El mensaje escrito
    };
    
    // Hacer petición POST al servidor
    fetch('/mensaje', {
        method: 'POST',                          // Método HTTP
        headers: {
            'Content-Type': 'application/json'   // Tipo de contenido
        },
        body: JSON.stringify(datos)              // Convertir objeto a JSON
    })
    // Procesar respuesta del servidor
    .then(respuesta => {
        // Verificar si la respuesta es exitosa (código 200-299)
        if (!respuesta.ok) {
            throw new Error(`Error HTTP: ${respuesta.status}`);
        }
        // Convertir respuesta a JSON
        return respuesta.json();
    })
    // Mostrar respuesta del bot
    .then(datos => {
        // Extraer el mensaje de respuesta
        const respuestaBot = datos.respuesta;
        // Mostrar respuesta en pantalla
        mostrarMensajeBot(respuestaBot);
    })
    // Manejar errores
    .catch(error => {
        console.error('Error al enviar mensaje:', error);
        // Mostrar mensaje de error al usuario
        mostrarMensajeBot('Error: No se pudo conectar con el servidor. Intenta de nuevo.');
    })
    // Finalmente, permitir nuevo envío
    .finally(() => {
        // Desmarcar el estado de envío
        enviando = false;
        // Enfocar el input nuevamente
        document.getElementById('messageInput').focus();
    });
}

/* ========================================
   FUNCIÓN: MOSTRAR MENSAJE DEL USUARIO
   ======================================== */

/**
 * Muestra un mensaje del usuario en el chat
 * - Crea un elemento con la clase 'message' y 'user'
 * - Añade el texto del mensaje
 * - Lo inserta en el contenedor de mensajes
 * - Realiza scroll automático al final
 */
function mostrarMensajeUsuario(texto) {
    // Crear elemento div para el mensaje
    const elementoMensaje = document.createElement('div');
    // Asignar clases para estilos (usuario derecha)
    elementoMensaje.className = 'message user';
    
    // Crear la burbuja del mensaje
    const burbuja = document.createElement('div');
    burbuja.className = 'bubble';
    // Establecer el texto del mensaje
    burbuja.textContent = texto;
    
    // Insertar burbuja dentro del mensaje
    elementoMensaje.appendChild(burbuja);
    
    // Obtener contenedor de mensajes
    const contenedorMensajes = document.getElementById('chatMessages');
    // Añadir mensaje al contenedor
    contenedorMensajes.appendChild(elementoMensaje);
    
    // Realizar scroll automático al último mensaje
    hacerScrollAlFinal();
}

/* ========================================
   FUNCIÓN: MOSTRAR MENSAJE DEL BOT
   ======================================== */

/**
 * Muestra un mensaje del bot en el chat
 * - Crea un elemento con la clase 'message' y 'bot'
 * - Añade el texto del mensaje
 * - Lo inserta en el contenedor de mensajes
 * - Realiza scroll automático al final
 */
function mostrarMensajeBot(texto) {
    // Crear elemento div para el mensaje
    const elementoMensaje = document.createElement('div');
    // Asignar clases para estilos (bot izquierda)
    elementoMensaje.className = 'message bot';
    
    // Crear la burbuja del mensaje
    const burbuja = document.createElement('div');
    burbuja.className = 'bubble';
    // Establecer el texto del mensaje
    burbuja.textContent = texto;
    
    // Insertar burbuja dentro del mensaje
    elementoMensaje.appendChild(burbuja);
    
    // Obtener contenedor de mensajes
    const contenedorMensajes = document.getElementById('chatMessages');
    // Añadir mensaje al contenedor
    contenedorMensajes.appendChild(elementoMensaje);
    
    // Realizar scroll automático al último mensaje
    hacerScrollAlFinal();
}

/* ========================================
   FUNCIÓN: SCROLL AUTOMÁTICO
   ======================================== */

/**
 * Realiza scroll automático al final del contenedor de mensajes
 * Se usa cada vez que se agrega un nuevo mensaje
 * para que el usuario siempre vea el mensaje más reciente
 */
function hacerScrollAlFinal() {
    // Obtener contenedor de mensajes
    const contenedorMensajes = document.getElementById('chatMessages');
    
    // Realizar scroll al final del contenedor
    // scrollHeight es la altura total del contenido
    contenedorMensajes.scrollTop = contenedorMensajes.scrollHeight;
}
