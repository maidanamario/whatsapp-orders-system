"""
Order Service Module.

Provides business logic for managing orders, including retrieval and creation.
Orders are stored in a JSON file for simplicity.
"""

import json
from pathlib import Path

DATA_FILE = Path(__file__).parent.parent / 'data' / 'orders.json'

class OrderService:
    """
    Business logic for order management.

    Handles CRUD operations for orders using JSON file storage.
    Designed for simplicity without a database.
    """
    
    @staticmethod
    def get_all_orders():
        """
        Retrieve all orders from the JSON file.

        Returns:
            list: List of order dictionaries, or empty list if file doesn't exist.
        """
        if DATA_FILE.exists():
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        return []
    
    @staticmethod
    def create_order(order_data):
        """
        Create a new order and save it to the JSON file.

        Args:
            order_data (dict): Dictionary containing order details (producto, cantidad, timestamp).

        Returns:
            dict: The created order data.
        """
        orders = OrderService.get_all_orders()
        orders.append(order_data)
        OrderService._save_orders(orders)
        return order_data
    
    @staticmethod
    def _save_orders(orders):
        """
        Save the list of orders to the JSON file.

        Creates the data directory if it doesn't exist.

        Args:
            orders (list): List of order dictionaries to save.
        """
        DATA_FILE.parent.mkdir(exist_ok=True)
        with open(DATA_FILE, 'w') as f:
            json.dump(orders, f, indent=2)
