from flask import Flask
from routes.main import main_bp
from routes.orders import orders_bp

app = Flask(__name__)

# Register blueprints
app.register_blueprint(main_bp)
app.register_blueprint(orders_bp)

if __name__ == "__main__":
    app.run(debug=True)