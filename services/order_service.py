import json
from pathlib import Path

DATA_FILE = Path(__file__).parent.parent / 'data' / 'orders.json'

class OrderService:
    """Business logic for order management"""
    
    @staticmethod
    def get_all_orders():
        """Retrieve all orders from JSON"""
        if DATA_FILE.exists():
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        return []
    
    @staticmethod
    def create_order(order_data):
        """Create a new order"""
        orders = OrderService.get_all_orders()
        orders.append(order_data)
        OrderService._save_orders(orders)
        return order_data
    
    @staticmethod
    def _save_orders(orders):
        """Save orders to JSON file"""
        DATA_FILE.parent.mkdir(exist_ok=True)
        with open(DATA_FILE, 'w') as f:
            json.dump(orders, f, indent=2)
