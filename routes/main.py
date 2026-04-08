"""
Main routes for the WhatsApp Orders System.

This module contains the primary routes for handling user messages via chatbot
and displaying orders. It manages user state and order creation.
"""

from flask import Blueprint, request, jsonify, render_template
import json
import os
import re
from datetime import datetime

main_bp = Blueprint('main', __name__)

def validate_cantidad(cantidad):
    """
    Validate quantity format for orders.

    Checks if the quantity string matches expected formats like '1kg', '2kg', '500g'.
    Uses regex to ensure it starts with digits, optionally with decimal, followed by 'kg' or 'g'.

    Args:
        cantidad (str): The quantity string to validate.

    Returns:
        bool: True if valid, False otherwise.
    """
    pattern = r'^\d+(?:\.\d+)?(kg|g)$'
    return bool(re.match(pattern, cantidad.lower()))


def parsear_pedido(mensaje):
    """
    Detecta un pedido completo en un solo mensaje.

    Soporta variantes como:
      - pollo 2kg
      - 2 kg pollo
      - pollo 2 kg
      - carne 500g
      - 500 g cerdo

    Args:
        mensaje (str): Mensaje del usuario.

    Returns:
        list[dict]|None: Lista de pedidos detectados, cada uno con 'producto' y 'cantidad'.
        Devuelve None si no se detecta ningún pedido válido.
    """
    texto = mensaje.lower().strip()
    # Normalizar separadores y palabras irrelevantes para agrupar bloques lógicos.
    # Preservar comas decimales como "2,5kg" y solo reemplazar comas que separan bloques.
    texto = re.sub(r'(?<=[^\d]),', ' ', texto)
    texto = re.sub(r"\b(de|y)\b", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()

    productos = {
        "pollo": ["pollo", "p", "chicken"],
        "carne": ["carne", "c", "beef", "vacuno"],
        "cerdo": ["cerdo", "ch", "pork"]
    }
    alias_a_producto = {alias: producto for producto, alias_list in productos.items() for alias in alias_list}

    cantidad_pat = r"\d+(?:[\.,]\d+)?\s*(?:kg|g)"
    producto_pat = r"pollo|carne|cerdo|p|c|ch|chicken|beef|vacuno|pork"
    bloque_pat = re.compile(
        rf"\b(?P<producto>{producto_pat})\b\s*(?:de\s*)?(?P<cantidad>{cantidad_pat})\b|"
        rf"\b(?P<cantidad2>{cantidad_pat})\s*(?:de\s*)?(?P<producto2>{producto_pat})\b"
    )

    pedidos = []
    seen = set()
    for match in bloque_pat.finditer(texto):
        producto_raw = match.group("producto") or match.group("producto2")
        cantidad_bruta = match.group("cantidad") or match.group("cantidad2")
        if not producto_raw or not cantidad_bruta:
            continue

        producto_normalizado = alias_a_producto.get(producto_raw)
        cantidad_normalizada = cantidad_bruta.replace(" ", "").replace(",", ".")
        if not producto_normalizado or not validate_cantidad(cantidad_normalizada):
            continue

        pedido_key = (producto_normalizado, cantidad_normalizada)
        if pedido_key in seen:
            continue
        seen.add(pedido_key)

        pedidos.append({
            "producto": producto_normalizado,
            "cantidad": cantidad_normalizada
        })

    if not pedidos:
        return None

    return pedidos


def unificar_carrito(carrito):
    """
    Unifica productos en el carrito sumando cantidades del mismo producto.
    
    Ejemplo:
        [{"producto": "pollo", "cantidad": "2kg"}, {"producto": "pollo", "cantidad": "2kg"}]
        →
        [{"producto": "pollo", "cantidad": "4kg"}]
    
    Args:
        carrito (list): Lista de items del carrito.
    
    Returns:
        list: Carrito unificado con cantidades sumadas.
    """
    if not carrito:
        return []
    
    # Agrupar por producto
    productos_agrupados = {}
    for item in carrito:
        producto = item["producto"]
        cantidad_str = item["cantidad"]
        
        # Extraer número y unidad
        match = re.match(r'(\d+(?:\.\d+)?)([kg|g]+)', cantidad_str)
        if not match:
            continue
        
        numero = float(match.group(1))
        unidad = match.group(2)
        
        if producto not in productos_agrupados:
            productos_agrupados[producto] = {"numero": 0, "unidad": unidad}
        
        productos_agrupados[producto]["numero"] += numero
    
    # Reconstruir carrito unificado
    carrito_unificado = []
    for producto, datos in productos_agrupados.items():
        numero = datos["numero"]
        unidad = datos["unidad"]
        
        # Formato: si es entero, mostrar sin decimal
        if numero == int(numero):
            cantidad_str = f"{int(numero)}{unidad}"
        else:
            cantidad_str = f"{numero}{unidad}"
        
        carrito_unificado.append({
            "producto": producto,
            "cantidad": cantidad_str
        })
    
    return carrito_unificado


def mostrar_carrito(carrito):
    """
    Genera la visualización del carrito completo.
    
    Args:
        carrito (list): Lista de items (puede estar unificada o no).
    
    Returns:
        str: Texto formateado del carrito.
    """
    if not carrito:
        return "🛒 Tu carrito está vacío."
    
    carrito_unificado = unificar_carrito(carrito)
    items_texto = "\n".join([f"• {item['producto']} {item['cantidad']}" for item in carrito_unificado])
    total = len(carrito_unificado)
    
    plural = "producto" if total == 1 else "productos"
    return f"🛒 Tu carrito:\n{items_texto}\n\nTotal: {total} {plural}"


def parsear_pedido_con_transparencia(mensaje):
    """
    Parsea un mensaje y retorna pedidos detectados + partes no interpretadas.
    
    Útil para mostrar transparencia al usuario sobre qué entendió el parser.
    
    Args:
        mensaje (str): Mensaje del usuario.
    
    Returns:
        tuple: (list[dict] pedidos_detectados, str partes_no_interpretadas)
               Si no hay partes no interpretadas, retorna string vacío.
    """
    texto_original = mensaje.lower().strip()
    texto_procesado = re.sub(r'(?<=[^\d]),', ' ', texto_original)
    texto_procesado = re.sub(r"\b(de|y)\b", " ", texto_procesado)
    texto_procesado = re.sub(r"\s+", " ", texto_procesado).strip()
    
    pedidos = parsear_pedido(mensaje)
    
    # Si no hay pedidos, toda la entrada no fue interpretada
    if not pedidos:
        return None, f"No entendí eso 🤔 ¿Podés escribirlo así? Ej: pollo 2kg"
    
    # Reconstruir qué fue interpretado
    texto_interpretado = ""
    for pedido in pedidos:
        producto = pedido["producto"]
        cantidad = pedido["cantidad"]
        # Buscar en el texto original
        for palabra in texto_original.split():
            if (producto in palabra or cantidad in palabra):
                texto_interpretado += palabra + " "
    
    # Encontrar partes no interpretadas
    palabras_procesadas = set(texto_interpretado.split())
    palabras_originales = set(texto_original.split())
    no_interpretadas = palabras_originales - palabras_procesadas
    
    no_interpretadas_str = ""
    if no_interpretadas:
        no_interpretadas_str = f"No interpreté: {', '.join(sorted(no_interpretadas))}"
    
    return pedidos, no_interpretadas_str


def variante_pregunta_sumar():
    """
    Retorna una variante aleatoria de la pregunta para sumar otro producto.
    
    Returns:
        str: Pregunta variante.
    """
    import random
    variantes = [
        "¿Querés sumar otro producto a tu pedido?",
        "¿Te gustaría agregar algo más?",
        "¿Necesitás algo más en tu pedido?",
        "¿Querés incluir otro producto?"
    ]
    return random.choice(variantes)

@main_bp.route('/')
def home():
    """
    Home route for the application.

    Returns a simple status message to indicate the system is running.

    Returns:
        str: Status message.
    """
    return "Sistema funcionando"


def manejar_comandos_globales(user, mensaje):
    """
    Procesa comandos globales que funcionan en cualquier estado.
    
    Comandos soportados:
    - 'ayuda': Muestra opciones disponibles
    - 'menu', 'cancelar': Vuelve al menú principal
    
    Args:
        user (dict): Diccionario del usuario
        mensaje (str): Mensaje en minúsculas y sin espacios extra
    
    Returns:
        tuple: (comando_procesado, respuesta) - comando_procesado es True si se ejecutó un comando global
    """
    if mensaje == "ayuda":
        respuesta = (
            "📚 **AYUDA - Comandos disponibles:**\n\n"
            "• 'menu' o 'cancelar' - Vuelve al menú principal\n"
            "• 'ayuda' - Muestra este mensaje\n\n"
            "¿Necesitás algo más?"
        )
        user["state"] = "inicio"
        user["producto"] = ""
        user["cantidad"] = ""
        user["carrito"] = []
        return True, respuesta
    
    if mensaje in ["menu", "cancelar"]:
        respuesta = (
            "🏠 Volvemos al inicio.\n\n"
            "Podés hacer tu pedido directamente, por ejemplo: pollo 2kg carne 1kg"
        )
        user["state"] = "inicio"
        user["producto"] = ""
        user["cantidad"] = ""
        user["carrito"] = []
        return True, respuesta
    
    return False, None


@main_bp.route('/mensaje', methods=['POST'])
def mensaje():
    """
    Maneja los mensajes del chatbot con UX conversacional mejorada.

    Procesa mensajes basados en el estado actual del usuario, valida entradas,
    y gestiona el flujo de pedidos con confirmación. Soporta comandos globales,
    reintentos en confirmación y mensajes más naturales.

    Estados: inicio, esperando_opcion, esperando_producto, esperando_cantidad, confirmando_pedido

    Comando global: 'ayuda', 'menu', 'cancelar'

    Espera JSON con 'mensaje' y 'usuario'.

    Returns:
        dict: JSON con 'respuesta' del bot.
    """
    try:
        data = request.get_json()
        if not data or not isinstance(data, dict):
            return jsonify({"respuesta": "❌ Error: Payload inválido. Envía JSON con 'mensaje' y 'usuario'.", "estado": "inicio"})
    except Exception:
        return jsonify({"respuesta": "❌ Error: No se pudo procesar el mensaje.", "estado": "inicio"})
    
    mensaje = data.get("mensaje", "").strip().lower()
    user_id = data.get("usuario")
    if not user_id:
        return jsonify({"respuesta": "❌ Error: Campo 'usuario' requerido en el JSON.", "estado": "inicio"})
    if not mensaje:
        return jsonify({"respuesta": "Escribe algo para continuar 😊", "estado": "inicio"})
    
    users_file = "data/usuarios.json"

    def load_users():
        """Carga los estados de usuarios desde JSON."""
        if os.path.exists(users_file):
            with open(users_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def save_users(users):
        """Guarda los estados de usuarios en JSON."""
        with open(users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=4)

    def get_user(users, uid):
        """Obtiene o crea entrada del usuario en el diccionario."""
        if uid not in users:
            users[uid] = {"state": "inicio", "producto": "", "cantidad": "", "carrito": []}
        # Agregar carrito si falta (para usuarios existentes)
        if "carrito" not in users[uid]:
            users[uid]["carrito"] = []
        return users[uid]

    users = load_users()
    user = get_user(users, user_id)

    # Verificar comandos globales primero (funcionan en cualquier estado)
    es_comando, respuesta_comando = manejar_comandos_globales(user, mensaje)
    if es_comando:
        save_users(users)
        return jsonify({"respuesta": respuesta_comando, "estado": user["state"]})

    # Detectar pedidos y agregar al carrito. Soporta múltiples productos en un mensaje.
    pedidos_parseados, no_interpretadas = parsear_pedido_con_transparencia(mensaje)
    if pedidos_parseados is not None:
        # Agregar todos los pedidos detectados al carrito
        for pedido in pedidos_parseados:
            user["carrito"].append(pedido)
        
        # Mostrar qué se agregó con transparencia
        items_agregados_texto = "\n".join([f"• {p['producto']} {p['cantidad']}" for p in pedidos_parseados])
        
        respuesta = (
            f"✅ Agregado al carrito.\n\n"
            f"Interpreté:\n{items_agregados_texto}"
        )
        
        # Si hay partes no interpretadas, mostrarlas
        if no_interpretadas:
            respuesta += f"\n\n{no_interpretadas}"
        
        respuesta += f"\n\n{mostrar_carrito(user['carrito'])}\n\n"
        respuesta += f"{variante_pregunta_sumar()}\n\nRespuestas: 'si' o 'no'"
        user["state"] = "esperando_sumar_otro"
        save_users(users)
        return jsonify({"respuesta": respuesta, "estado": user["state"]})

    respuesta = "No entendí eso 🤔 ¿Podés escribirlo así? Ej: pollo 2kg carne 1kg\n\nO escribí 'ayuda' para ver opciones"

    # Saludo inicial - Reinicia todo
    if mensaje in ["hola", "hi", "hey", "start"]:
        user["state"] = "inicio"
        user["producto"] = ""
        user["cantidad"] = ""
        user["carrito"] = []
        respuesta = (
            "¡Hola! 👋 Bienvenido a nuestro sistema de pedidos.\n\n"
            "Podés hacer tu pedido directamente, por ejemplo: pollo 2kg carne 1kg"
        )
        save_users(users)
        return jsonify({"respuesta": respuesta, "estado": user["state"]})
    
    # Cancelar con 0 - Volver al inicio
    if mensaje == "0":
        user["state"] = "inicio"
        user["producto"] = ""
        user["cantidad"] = ""
        respuesta = (
            "❌ Proceso cancelado.\n\n"
            "Podés hacer tu pedido directamente, por ejemplo: pollo 2kg carne 1kg"
        )
        save_users(users)
        return jsonify({"respuesta": respuesta, "estado": user["state"]})
    
    # ===== ESTADO: INICIO =====
    if user["state"] == "inicio":
        # Intentar parsear pedido directo
        pedidos_parseados, no_interpretadas = parsear_pedido_con_transparencia(mensaje)
        if pedidos_parseados is not None:
            # Agregar pedidos al carrito
            for pedido in pedidos_parseados:
                user["carrito"].append(pedido)
            
            # Mostrar carrito y preguntar si sumar otro
            respuesta = f"{mostrar_carrito(user['carrito'])}\n\n{variante_pregunta_sumar()}\n\nRespuestas: 'si' o 'no'"
            user["state"] = "esperando_sumar_otro"
            save_users(users)
            return jsonify({"respuesta": respuesta, "estado": user["state"]})
        
        # Si no es pedido, mostrar mensaje de ayuda
        respuesta = (
            "No entendí eso 🤔 ¿Podés escribirlo así? Ej: pollo 2kg carne 1kg\n\n"
            "O escribí 'ayuda' para ver opciones"
        )

    # ===== ESTADO: ESPERANDO_PRODUCTO =====
    elif user["state"] == "esperando_producto":
        # Intentar parsear pedido directo
        pedidos_parseados, no_interpretadas = parsear_pedido_con_transparencia(mensaje)
        if pedidos_parseados is not None:
            # Agregar pedidos al carrito
            for pedido in pedidos_parseados:
                user["carrito"].append(pedido)
            
            # Mostrar carrito y preguntar si sumar otro
            respuesta = f"{mostrar_carrito(user['carrito'])}\n\n{variante_pregunta_sumar()}\n\nRespuestas: 'si' o 'no'"
            user["state"] = "esperando_sumar_otro"
            save_users(users)
            return jsonify({"respuesta": respuesta, "estado": user["state"]})
        
        # Si no es pedido, validar producto
        mensaje_limpio = mensaje.lower().strip()
        productos_validos = {"pollo", "carne", "cerdo"}
        
        if mensaje_limpio in productos_validos:
            user["producto"] = mensaje_limpio
            user["state"] = "esperando_cantidad"
            respuesta = (
                f"Excelente, pedís {mensaje_limpio.upper()} 🛒\n\n"
                "¿Cuánto querés? (ej: 1kg, 2kg, 500g, 1.5kg)"
            )
        else:
            respuesta = (
                "Producto inválido.\n\n"
                "Opciones disponibles:\n"
                "• pollo\n"
                "• carne\n"
                "• cerdo\n\n"
                "O escribí el producto y cantidad juntos (ej: 2kg carne)"
            )

    # ===== ESTADO: ESPERANDO_CANTIDAD =====
    elif user["state"] == "esperando_cantidad":
        if not mensaje or mensaje == "":
            respuesta = "No se recibió cantidad. Escribi cuánto querés (ej: 1kg, 2kg, 500g)"
            save_users(users)
            return jsonify({"respuesta": respuesta, "estado": user["state"]})
        
        # Validar formato de cantidad
        if not validate_cantidad(mensaje):
            respuesta = (
                "Cantidad inválida.\n\n"
                "Ejemplos válidos:\n"
                "• 1kg\n"
                "• 2kg\n"
                "• 500g\n"
                "• 1.5kg\n\n"
                "¿Cuánto querés?"
            )
            save_users(users)
            return jsonify({"respuesta": respuesta, "estado": user["state"]})
        
        # Cantidad válida - Agregar al carrito y preguntar si sumar otro
        user["cantidad"] = mensaje
        user["carrito"].append({
            "producto": user["producto"],
            "cantidad": user["cantidad"]
        })
        respuesta = f"{mostrar_carrito(user['carrito'])}\n\n{variante_pregunta_sumar()}\n\nRespuestas: 'si' o 'no'"
        user["state"] = "esperando_sumar_otro"
        user["producto"] = ""
        user["cantidad"] = ""

    # ===== ESTADO: ESPERANDO_SUMAR_OTRO =====
    elif user["state"] == "esperando_sumar_otro":
        if mensaje == "si":
            user["state"] = "esperando_producto"
            respuesta = (
                "¿Qué producto querés agregar?\n\n"
                "Opciones: pollo, carne, cerdo\n\n"
                "O escribí el producto y cantidad juntos (ej: 2kg carne)"
            )
        elif mensaje == "no":
            # Confirmar pedido
            if not user["carrito"]:
                respuesta = "❌ No hay items en el carrito."
                save_users(users)
                return jsonify({"respuesta": respuesta, "estado": user["state"]})
            
            # Guardar pedidos
            carrito_unificado = unificar_carrito(user["carrito"])
            pedidos_file = "data/pedidos.json"
            if os.path.exists(pedidos_file):
                with open(pedidos_file, 'r', encoding='utf-8') as f:
                    pedido_list = json.load(f)
            else:
                pedido_list = []
            
            timestamp_pedido = datetime.now().isoformat()
            for item in carrito_unificado:
                order = {
                    "producto": item.get("producto", ""),
                    "cantidad": item.get("cantidad", ""),
                    "timestamp": timestamp_pedido
                }
                pedido_list.append(order)
            
            with open(pedidos_file, 'w', encoding='utf-8') as f:
                json.dump(pedido_list, f, indent=4)
            
            # Resetear usuario
            user["state"] = "inicio"
            user["carrito"] = []
            user["producto"] = ""
            user["cantidad"] = ""
            
            items_confirmados = "\n".join([f"• {item['producto']} {item['cantidad']}" for item in carrito_unificado])
            respuesta = (
                "✅ Pedido confirmado.\n\n"
                f"{items_confirmados}\n\n"
                "¡Gracias por tu pedido! En breve lo procesamos."
            )
        else:
            respuesta = (
                "No entendí eso 🤔 Responde con 'si' o 'no'\n\n"
                f"{mostrar_carrito(user['carrito'])}\n\n"
                f"{variante_pregunta_sumar()}\n\n"
                "Respuestas: 'si' o 'no'"
            )

    # ===== ESTADO: CARRITO_ABIERTO =====
    elif user["state"] == "carrito_abierto":
        if mensaje == "agregar":
            # Agregar otro producto
            user["state"] = "esperando_producto"
            respuesta = (
                "¿Cuál es el próximo producto que querés?\n\n"
                "Opciones:\n"
                "• pollo\n"
                "• carne\n"
                "• cerdo\n\n"
                "O escribí el producto y cantidad juntos (ej: 2kg carne)"
            )
        
        elif mensaje == "confirmar":
            # Confirmar todos los items del carrito (unificados)
            if not user["carrito"]:
                respuesta = "❌ No hay items en el carrito."
                save_users(users)
                return jsonify({"respuesta": respuesta, "estado": user["state"]})
            
            # Guardar todos los items unificados del carrito
            carrito_unificado = unificar_carrito(user["carrito"])
            pedidos_file = "data/pedidos.json"
            if os.path.exists(pedidos_file):
                with open(pedidos_file, 'r', encoding='utf-8') as f:
                    pedido_list = json.load(f)
            else:
                pedido_list = []
            
            # Agregar cada item del carrito como un pedido con timestamp unificado
            timestamp_pedido = datetime.now().isoformat()
            for item in carrito_unificado:
                order = {
                    "producto": item.get("producto", ""),
                    "cantidad": item.get("cantidad", ""),
                    "timestamp": timestamp_pedido
                }
                pedido_list.append(order)
            
            with open(pedidos_file, 'w', encoding='utf-8') as f:
                json.dump(pedido_list, f, indent=4)
            
            # Resetear usuario
            user["state"] = "inicio"
            user["carrito"] = []
            user["producto"] = ""
            user["cantidad"] = ""
            
            respuesta = (
                "✅ ¡Pedido confirmado!\n\n"
                "En breve lo procesamos.\n\n"
                "¿Querés hacer otro pedido?\n\n"
                "Podés hacer tu pedido directamente, por ejemplo: pollo 2kg carne 1kg"
            )
        
        elif mensaje == "cancelar":
            # Cancelar carrito completo
            user["state"] = "inicio"
            user["carrito"] = []
            user["producto"] = ""
            user["cantidad"] = ""
            respuesta = (
                "❌ Carrito cancelado.\n\n"
                "Podés hacer tu pedido directamente, por ejemplo: pollo 2kg carne 1kg"
            )
        
        else:
            # Si envía algo más, mostrar opciones disponibles
            respuesta = (
                f"{mostrar_carrito(user['carrito'])}\n\n"
                "¿Qué querés hacer?\n\n"
                "• 'agregar' para sumar otro producto\n"
                "• 'confirmar' para terminar\n"
                "• 'cancelar' para empezar de nuevo"
            )

    save_users(users)

    return jsonify({"respuesta": respuesta, "estado": user["state"]})

@main_bp.route('/pedidos')
def pedidos():
    """
    Display all orders in a web page.

    Loads orders from JSON file and renders them in an HTML table.

    Returns:
        str: Rendered HTML template with orders data.
    """
    file_path = "data/pedidos.json"
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            orders = json.load(f)
    else:
        orders = []
    return render_template('pedidos.html', orders=orders)

@main_bp.route('/chat')
def chat():
    """
    Render the chatbot interface.

    Displays the web-based chat interface for users to interact with the order system.

    Returns:
        str: Rendered HTML template for the chat interface.
    """
    return render_template('chat.html')