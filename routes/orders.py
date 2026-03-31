from flask import Blueprint

orders_bp = Blueprint('orders', __name__, url_prefix='/orders')

@orders_bp.route('/', methods=['GET'])
def list_orders():
    return "Sistema funcionando"

@orders_bp.route('/create', methods=['POST'])
def create_order():
    return {"message": "Order created"}
