from flask import Flask
from flask_wtf.csrf import CSRFProtect
from config import config
from models import db, init_db
from routes import register_blueprints
from flask_login import LoginManager
from flask_mail import Mail
from modulos.main.routes import roles_required

login_manager = LoginManager()
mail = Mail()
def create_app(config_name='development'):
    app = Flask(__name__, template_folder='templates')
    app.config.from_object(config[config_name])
    
        # Configuración de la base de datos
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:sergio@localhost:3306/CookieKing'
    
    # Initialize extensions
    db.init_app(app)
    csrf = CSRFProtect(app)
    login_manager.init_app(app)
    
    mail = Mail(app)

    login_manager.login_view = 'auth.iniciar_sesion'
    login_manager.login_message = 'Por favor, inicia sesión para acceder a esta página.'
    # Register all blueprints
    register_blueprints(app)
    
    # Create tables if they don't exist
    with app.app_context():
        init_db()   
        db.create_all()
                         
    return app

@login_manager.user_loader
def load_user(user_id):
    from modulos.auth.models import Usuario  
    return Usuario.query.get(int(user_id))

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)