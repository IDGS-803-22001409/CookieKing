from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

def init_db():
    """
    Inicializa la base de datos importando todos los modelos para que SQLAlchemy los conozca.
    Las importaciones están aquí para evitar dependencias circulares.
    """    
    import modulos.galletas.models
    import modulos.recetas.models
    import modulos.ingredientes.models
    import modulos.proveedores.models
    import modulos.compras.models
    import modulos.produccion.models
    import modulos.ventas.models
    import modulos.clientes.models
    
    # Crear todas las tablas
    db.create_all()