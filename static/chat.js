/* ========================================
   VARIABLES Y ESTADO GLOBAL
   ======================================== */

// Generar un usuario único tipo web_user_XXXXX
// Se usa para identificar cada sesión de chat
const usuarioId = 'web_user_' + Math.floor(Math.random() * 100000);

// Variable para controlar si estamos enviando un mensaje
// Evita que se envíen múltiples mensajes al mismo tiempo
let enviando = false;

// Estado actual del chatbot (será actualizado dinámicamente)
let estadoActual = "inicio";

// Diccionario de productos disponibles
const productos = {
    "1": { nombre: "pollo", emoji: "🍗", alias: ["pollo", "p", "chicken"] },
    "2": { nombre: "carne", emoji: "🥩", alias: ["carne", "c", "beef", "vacuno"] },
    "3": { nombre: "cerdo", emoji: "🐷", alias: ["cerdo", "ch", "pork"] }
};

// Configuración de sugerencias según estado
const sugerenciasConfig = {
    "inicio": {
        tipo: "botones",
        opciones: [
            { texto: "Ver productos", valor: "1", emoji: "📦" },
            { texto: "Hacer pedido", valor: "2", emoji: "🛒" },
            { texto: "Ayuda", valor: "ayuda", emoji: "❓" }
        ]
    },
    "esperando_opcion": {
        tipo: "botones",
        opciones: [
            { texto: "Ver productos", valor: "1", emoji: "📦" },
            { texto: "Hacer pedido", valor: "2", emoji: "🛒" }
        ]
    },
    "esperando_producto": {
        tipo: "autocompletado",
        opciones: Object.values(productos).map((p, i) => ({
            texto: `${p.emoji} ${p.nombre.charAt(0).toUpperCase() + p.nombre.slice(1)}`,
            valor: String(i + 1),
            keywords: p.alias
        })),
        placeholder: "Ej: pollo, carne, cerdo"
    },
    "esperando_cantidad": {
        tipo: "ejemplos",
        opciones: [
            { texto: "1kg", valor: "1kg", emoji: "⚖️" },
            { texto: "2kg", valor: "2kg", emoji: "⚖️" },
            { texto: "500g", valor: "500g", emoji: "⚖️" },
            { texto: "1.5kg", valor: "1.5kg", emoji: "⚖️" }
        ],
        placeholder: "Ej: 1kg, 2kg, 500g"
    },
    "confirmando_pedido": {
        tipo: "botones",
        opciones: [
            { texto: "Sí, confirmar", valor: "si", emoji: "✅" },
            { texto: "No, cancelar", valor: "no", emoji: "❌" },
            { texto: "Cambiar producto", valor: "producto", emoji: "🔄" },
            { texto: "Cambiar cantidad", valor: "cantidad", emoji: "⚖️" }
        ]
    }
};

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
    
    // Escuchar cambios en el input para sugerencias inteligentes
    inputMensaje.addEventListener('input', function(evento) {
        actualizarSugerencias(evento.target.value);
    });
    
    // Mostrar sugerencias iniciales
    mostrarSugerenciasIniciales();
    
    // Mostrar mensaje de bienvenida del bot
    mostrarMensajeBot('¡Hola! 👋 Bienvenido al sistema de órdenes. Escribe "hola" para comenzar.');
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
        
        // Actualizar estado si el servidor lo proporciona
        if (datos.estado) {
            estadoActual = datos.estado;
        }
        
        // Actualizar sugerencias y acciones rápidas
        mostrarSugerenciasIniciales();
        actualizarAccionesRapidas();
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

/* ========================================
   INPUT INTELIGENTE - SUGERENCIAS
   ======================================== */

/**
 * Muestra las sugerencias iniciales según el estado
 * Se llama al iniciar y después de cada respuesta del bot
 */
function mostrarSugerenciasIniciales() {
    const config = sugerenciasConfig[estadoActual];
    if (!config) return;
    
    const caja = document.getElementById('suggestionsBox');
    caja.innerHTML = '';
    
    if (config.tipo === "botones") {
        config.opciones.forEach(opcion => {
            const boton = document.createElement('button');
            boton.className = 'suggestion-button quick-action';
            boton.innerHTML = `${opcion.emoji} ${opcion.texto}`;
            boton.onclick = () => seleccionarSugerencia(opcion.valor);
            caja.appendChild(boton);
        });
    } else if (config.tipo === "ejemplos") {
        config.opciones.forEach(opcion => {
            const boton = document.createElement('button');
            boton.className = 'suggestion-button example-button';
            boton.textContent = opcion.texto;
            boton.onclick = () => seleccionarSugerencia(opcion.valor);
            caja.appendChild(boton);
        });
    }
}

/**
 * Actualiza las sugerencias según lo que escribe el usuario
 * Implementa:
 * - Autocompletado de productos
 * - Validación en tiempo real
 * - Sugerencias contextuales
 */
function actualizarSugerencias(texto) {
    const config = sugerenciasConfig[estadoActual];
    if (!config || config.tipo !== "autocompletado") {
        mostrarSugerenciasIniciales();
        return;
    }
    
    const caja = document.getElementById('suggestionsBox');
    const input = texto.toLowerCase().trim();
    
    // Si está vacío, mostrar todas las opciones
    if (!input) {
        mostrarSugerenciasIniciales();
        return;
    }
    
    // Filtrar opciones que coincidan
    const coincidencias = config.opciones.filter(opcion => 
        opcion.keywords.some(k => k.startsWith(input))
    );
    
    caja.innerHTML = '';
    
    if (coincidencias.length === 0) {
        caja.innerHTML = '<div class="no-suggestions">No encontramos coincidencias</div>';
        return;
    }
    
    coincidencias.forEach(opcion => {
        const boton = document.createElement('button');
        boton.className = 'suggestion-button autocomplete-button';
        boton.innerHTML = `${opcion.texto}`;
        boton.onclick = () => seleccionarSugerencia(opcion.valor);
        caja.appendChild(boton);
    });
    
    // Validar si lo escrito es una cantidad válida
    if (estadoActual === "esperando_cantidad") {
        const esValido = /^\d+(?:\.\d+)?(kg|g)$/.test(input);
        const validador = document.getElementById('validationIndicator');
        
        if (input.length > 0) {
            if (esValido) {
                validador.className = 'validation-indicator valid';
                validador.textContent = '✅';
            } else {
                validador.className = 'validation-indicator invalid';
                validador.textContent = '❌';
            }
        } else {
            validador.className = 'validation-indicator';
            validador.textContent = '';
        }
    }
}

/**
 * Selecciona una sugerencia (usuario click en botón o sugerencia)
 */
function seleccionarSugerencia(valor) {
    document.getElementById('messageInput').value = valor;
    enviarMensaje();
}

/**
 * Actualiza las acciones rápidas según el estado actual
 * Se llama después de recibir respuesta del bot
 */
function actualizarAccionesRapidas() {
    const config = sugerenciasConfig[estadoActual];
    const caja = document.getElementById('quickActions');
    
    if (!config || config.tipo !== "botones") {
        caja.innerHTML = '';
        return;
    }
    
    caja.innerHTML = '';
    config.opciones.forEach(opcion => {
        const boton = document.createElement('button');
        boton.className = 'quick-action-button';
        boton.innerHTML = `${opcion.emoji} ${opcion.texto}`;
        boton.onclick = () => seleccionarSugerencia(opcion.valor);
        caja.appendChild(boton);
    });
}
