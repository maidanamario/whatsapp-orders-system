"""
WhatsApp Orders System - Main Flask Application

This module initializes and runs the Flask application for the WhatsApp orders system.
It registers blueprints for handling main routes and order-related routes.
"""

from flask import Flask
from routes.main import main_bp
from routes.orders import orders_bp

app = Flask(__name__)

# Register blueprints for modular routing
app.register_blueprint(main_bp)
app.register_blueprint(orders_bp)

if __name__ == "__main__":
    app.run(debug=True)