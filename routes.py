# Archivo: blueprints.py
# Corrige la duplicación de blueprints
from modulos.main.routes import main_bp
from modulos.recetas.routes import recetas_bp
from modulos.galletas.routes import galletas_bp
from modulos.clientes.routes import clientes_bp
from modulos.ventas.routes import ventas_bp
from modulos.ingredientes.routes import ingredientes_bp
from modulos.proveedores.routes import proveedores_bp
# Importar blueprints temporales (excluimos los que ya tenemos implementados)
from modulos.temp.routes import (
    usuarios_bp,
    # proveedores_bp,  # Comentar esta línea para evitar la duplicación
    compras_bp,
    produccion_bp,
    reportes_bp
)

def register_blueprints(app):
    """Registra todos los blueprints con la aplicación"""
    # Registrar blueprint principal primero
    app.register_blueprint(main_bp)
   
    # Módulos ya implementados
    app.register_blueprint(recetas_bp)
    app.register_blueprint(galletas_bp)
    app.register_blueprint(clientes_bp)
    app.register_blueprint(ventas_bp)
    app.register_blueprint(ingredientes_bp)
    app.register_blueprint(proveedores_bp)  # Módulo proveedores implementado
   
    # Blueprints temporales para módulos en desarrollo
    app.register_blueprint(usuarios_bp)
    # app.register_blueprint(proveedores_bp)  # Comentar esta línea para evitar la duplicación
    app.register_blueprint(compras_bp)
    app.register_blueprint(produccion_bp)
    app.register_blueprint(reportes_bp)