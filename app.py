from flask import Flask
from extensions import db, mail, login_manager
from modulos.main.routes import main_bp
from flask_wtf.csrf import CSRFProtect

def create_app():
    app = Flask(__name__)
    app.register_blueprint(main_bp)

    # Configuración de la aplicación
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@localhost:3306/CookieKing'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'
    
    # Configuración de correo
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'cortezgonzalezjuandiego3@gmail.com'
    app.config['MAIL_PASSWORD'] = 'lqog yyak mslx shtt'
    app.config['MAIL_DEFAULT_SENDER'] = 'cortezgonzalezjuandiego3@gmail.com'  # !

    csrf = CSRFProtect(app)

    # Inicializar extensiones con la app
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'autenticacion.iniciar_sesion'
    
    with app.app_context():
        # Registrar blueprints
        from modulos.login.controlador_autenticacion import autenticacion_bp
        app.register_blueprint(autenticacion_bp)
        
        # Crear tablas en la base de datos
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("Registered blueprints:", app.blueprints)
    app.run(debug=True)