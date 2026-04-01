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

@main_bp.route('/')
def home():
    """
    Home route for the application.

    Returns a simple status message to indicate the system is running.

    Returns:
        str: Status message.
    """
    return "Sistema funcionando"


@main_bp.route('/mensaje', methods=['POST'])
def mensaje():
    """
    Handle incoming messages for the chatbot.

    Processes user messages based on their current state, validates inputs,
    and manages the order creation flow with confirmation step. Supports commands like 'hola' to reset
    and '0' to cancel. Persists user state in JSON files.

    States: inicio, esperando_opcion, esperando_producto, esperando_cantidad, confirmando_pedido

    Expects JSON payload with 'mensaje' and 'usuario' keys.

    Returns:
        dict: JSON response with 'respuesta' key containing the bot's reply.
    """
    try:
        data = request.get_json()
        if not data or not isinstance(data, dict):
            return jsonify({"respuesta": "Error: Payload inválido. Envía un JSON con 'mensaje' y 'usuario'."})
    except Exception:
        return jsonify({"respuesta": "Error: No se pudo procesar el mensaje."})
    
    mensaje = data.get("mensaje", "").strip().lower()
    user_id = data.get("usuario")
    if not user_id:
        return jsonify({"respuesta": "Error: Campo 'usuario' requerido en el JSON."})
    if not mensaje:
        return jsonify({"respuesta": "Mensaje vacío. Escribe algo."})
    
    users_file = "data/usuarios.json"

    def load_users():
        """
        Load user states from JSON file.

        Returns:
            dict: Dictionary of user states, or empty dict if file doesn't exist.
        """
        if os.path.exists(users_file):
            with open(users_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def save_users(users):
        """
        Save user states to JSON file.

        Args:
            users (dict): Dictionary of user states to save.
        """
        with open(users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=4)

    def get_user(users, uid):
        """
        Get or create a user entry in the users dictionary.

        Args:
            users (dict): The users dictionary.
            uid (str): User ID.

        Returns:
            dict: The user's state dictionary with keys: state, producto, cantidad.
        """
        if uid not in users:
            users[uid] = {"state": "inicio", "producto": "", "cantidad": ""}
        return users[uid]

    users = load_users()
    user = get_user(users, user_id)

    respuesta = "Opción no válida. Escribe hola para comenzar."

    if mensaje in ["hola", "menu", "inicio"]:
        user["state"] = "inicio"
        user["producto"] = ""
        user["cantidad"] = ""
        respuesta = "1. Ver productos / 2. Hacer pedido (0 para cancelar)"
        save_users(users)
        return jsonify({"respuesta": respuesta})
    if mensaje == "0":
        user["state"] = "inicio"
        user["producto"] = ""
        user["cantidad"] = ""
        respuesta = "Proceso cancelado. 1. Ver productos / 2. Hacer pedido"
        save_users(users)
        return jsonify({"respuesta": respuesta})
    
    if user["state"] == "inicio":
        if mensaje == "1":
            respuesta = "Lista de productos: pollo, carne, cerdo. Escribe 2 para hacer pedido o 0 para cancelar."
        elif mensaje == "2":
                user["state"] = "esperando_producto"
                respuesta = "Escribe el producto (0 para cancelar)"
        else:
                user["state"] = "esperando_opcion"
                respuesta = "1. Ver productos / 2. Hacer pedido (0 para cancelar)"

    elif user["state"] == "esperando_opcion":
        if mensaje == "1":
            respuesta = "Lista de productos: pollo, carne, cerdo. Escribe 2 para hacer pedido o 0 para cancelar."
        elif mensaje == "2":
            user["state"] = "esperando_producto"
            respuesta = "Escribe el producto (0 para cancelar)"
        else:
            respuesta = "Opción inválida. Escribe 1 o 2 (0 para cancelar)"

    elif user["state"] == "esperando_producto":
        if not mensaje:
            respuesta = "No se recibió producto. Escribe el producto (0 para cancelar)"
            save_users(users)
            return jsonify({"respuesta": respuesta})
        user["producto"] = mensaje
        user["state"] = "esperando_cantidad"
        respuesta = "Escribe la cantidad (0 para cancelar)"
    elif user["state"] == "esperando_cantidad":
        if not mensaje:
            respuesta = "No se recibió cantidad. Escribe la cantidad (0 para cancelar)"
            save_users(users)
            return jsonify({"respuesta": respuesta})
        
        if not validate_cantidad(mensaje):
            respuesta = "Cantidad inválida. Ej: 1kg, 2kg, 500g"
            save_users(users)
            return jsonify({"respuesta": respuesta})
        
        user["cantidad"] = mensaje
        user["state"] = "confirmando_pedido"
        respuesta = f"Producto: {user['producto']}\nCantidad: {user['cantidad']}\n\n¿Confirmar pedido? (si/no)"
    elif user["state"] == "confirmando_pedido":
        if mensaje == "si":
            order = {
                "producto": user.get("producto", ""),
                "cantidad": user.get("cantidad", ""),
                "timestamp": datetime.now().isoformat()
            }
            pedidos_file = "data/pedidos.json"
            if os.path.exists(pedidos_file):
                with open(pedidos_file, 'r', encoding='utf-8') as f:
                    pedido_list = json.load(f)
            else:
                pedido_list = []
            pedido_list.append(order)
            with open(pedidos_file, 'w', encoding='utf-8') as f:
                json.dump(pedido_list, f, indent=4)

            user["state"] = "inicio"
            user["producto"] = ""
            user["cantidad"] = ""
            respuesta = "Pedido registrado. ¿Querés hacer otro pedido? (1: ver productos / 2: pedir)"
        elif mensaje == "no":
            user["state"] = "inicio"
            user["producto"] = ""
            user["cantidad"] = ""
            respuesta = "Pedido cancelado. ¿Querés hacer otro pedido? (1: ver productos / 2: pedir)"
        
        else:
           respuesta = "Respuesta inválida. Escribí 'si' para confirmar o 'no' para cancelar."

    save_users(users)

    return jsonify({"respuesta": respuesta})

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