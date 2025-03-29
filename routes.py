from modulos.main.routes import main_bp
from modulos.recetas.routes import recetas_bp
from modulos.galletas.routes import galletas_bp

# Importar blueprints temporales
from modulos.temp.routes import (
    usuarios_bp,
    clientes_bp,
    proveedores_bp,
    compras_bp, 
    ingredientes_bp,
    produccion_bp,
    ventas_bp,
    reportes_bp
)

def register_blueprints(app):
    """Registra todos los blueprints con la aplicación"""
    # Registrar blueprint principal primero
    app.register_blueprint(main_bp)
    
    # Módulos ya implementados
    app.register_blueprint(recetas_bp)
    app.register_blueprint(galletas_bp)
    
    # Blueprints temporales para módulos en desarrollo
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(clientes_bp)
    app.register_blueprint(proveedores_bp)
    app.register_blueprint(compras_bp)
    app.register_blueprint(ingredientes_bp)
    app.register_blueprint(produccion_bp)
    app.register_blueprint(ventas_bp)
    app.register_blueprint(reportes_bp)