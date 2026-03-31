from flask import Blueprint, request, jsonify, render_template
import json
import os
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return "Sistema funcionando"


@main_bp.route('/mensaje', methods=['POST'])
def mensaje():
    data = request.get_json()
    mensaje = data.get("mensaje", "")

    if mensaje == "1":
        respuesta = "Lista de productos: pollo, carne, cerdo"
    elif mensaje == "2":
        respuesta = "Por favor escribe tu pedido"
    else:
        # Try to parse as product quantity
        parts = mensaje.split()
        if len(parts) == 2:
            producto = parts[0]
            cantidad = parts[1]
            # Create order object
            order = {
                "producto": producto,
                "cantidad": cantidad,
                "timestamp": datetime.now().isoformat()
            }
            # Save to JSON file
            file_path = "data/pedidos.json"
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    orders = json.load(f)
            else:
                orders = []
            orders.append(order)
            with open(file_path, 'w') as f:
                json.dump(orders, f, indent=4)
            respuesta = "Pedido registrado"
        else:
            respuesta = "Opción no válida. Escribe 1 o 2"

    return jsonify({"respuesta": respuesta})

@main_bp.route('/pedidos')
def pedidos():
    file_path = "data/pedidos.json"
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            orders = json.load(f)
    else:
        orders = []
    return render_template('pedidos.html', orders=orders)