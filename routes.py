from modulos.main.routes import main_bp
from modulos.recetas.routes import recetas_bp
from modulos.galletas.routes import galletas_bp
# from modulos.ingredientes.routes import ingredientes_bp  # Se descomentará cuando esté completamente implementado

# Importar otros blueprints a medida que agregues más módulos
# from modulos.proveedores.routes import proveedores_bp
# from modulos.ventas.routes import ventas_bp
# from modulos.produccion.routes import produccion_bp

def register_blueprints(app):
    """Registra todos los blueprints con la aplicación"""
    # Registrar blueprint principal primero
    app.register_blueprint(main_bp)
    
    # Registrar otros blueprints
    app.register_blueprint(recetas_bp)
    app.register_blueprint(galletas_bp)
    
    # Descomentar a medida que se implementen estos módulos
    # app.register_blueprint(ingredientes_bp)
    # app.register_blueprint(proveedores_bp)
    # app.register_blueprint(ventas_bp)
    # app.register_blueprint(produccion_bp)