from modulos.main.routes import main_bp
from modulos.recetas.routes import recetas_bp
from modulos.galletas.routes import galletas_bp
from modulos.clientes.routes import clientes_bp
from modulos.ventas.routes import ventas_bp
from modulos.produccion.routes import produccion_bp
from modulos.auth.routes import auth_bp
from modulos.ingredientes.routes import ingredientes_bp
from modulos.proveedores.routes import proveedores_bp
from modulos.reportes.routes import reportes_bp

from modulos.temp.routes import (
    usuarios_bp,    
    compras_bp,           
)

def register_blueprints(app):
    """Registra todos los blueprints con la aplicación"""
    # Registrar blueprint principal primero
    app.register_blueprint(auth_bp, url_prefix='/auth') 
    app.register_blueprint(main_bp)
    
    # Módulos ya implementados
    app.register_blueprint(recetas_bp)
    app.register_blueprint(galletas_bp)
    app.register_blueprint(clientes_bp)
    app.register_blueprint(ventas_bp)
    app.register_blueprint(ingredientes_bp)
    app.register_blueprint(proveedores_bp)    
    app.register_blueprint(reportes_bp)
    
    # Blueprints temporales para módulos en desarrollo
    app.register_blueprint(usuarios_bp)    
    app.register_blueprint(compras_bp)
    app.register_blueprint(produccion_bp)    
    