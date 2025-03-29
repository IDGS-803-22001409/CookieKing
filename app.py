from flask import Flask
from flask_wtf.csrf import CSRFProtect
from config import config
from models import db, init_db
from routes import register_blueprints
from utils.init_db import init_test_data

def create_app(config_name='development'):
    app = Flask(__name__, template_folder='templates')
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    csrf = CSRFProtect(app)
    
    # Register all blueprints
    register_blueprints(app)
    
    # Create tables if they don't exist
    with app.app_context():
        init_db()
        # Inicializar datos de prueba
        init_test_data()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)