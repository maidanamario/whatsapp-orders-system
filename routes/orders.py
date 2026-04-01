"""
Order-related routes for the WhatsApp Orders System.

This module provides additional routes for order management,
currently with basic placeholder implementations.
"""

from flask import Blueprint

orders_bp = Blueprint('orders', __name__, url_prefix='/orders')

@orders_bp.route('/', methods=['GET'])
def list_orders():
    """
    List all orders.

    Currently returns a placeholder message. Intended for future expansion.

    Returns:
        str: Placeholder response.
    """
    return "Sistema funcionando"

@orders_bp.route('/create', methods=['POST'])
def create_order():
    """
    Create a new order.

    Currently returns a placeholder response. Intended for future expansion.

    Returns:
        dict: Placeholder JSON response.
    """
    return {"message": "Order created"}
