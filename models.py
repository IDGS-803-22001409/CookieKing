from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

def init_db():
    """
    Inicializa la base de datos importando todos los modelos para que SQLAlchemy los conozca.
    Las importaciones están aquí para evitar dependencias circulares.
    """
    # Importar todos los modelos
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

# Importar modelos desde sus módulos para mantener compatibilidad
from modulos.recetas.models import RecetaIngrediente
from modulos.ingredientes.models import Ingrediente, MovimientoInsumo
from modulos.proveedores.models import Proveedor
from modulos.compras.models import CompraInsumo, CompraDetalle
from modulos.produccion.models import Produccion
from modulos.ventas.models import Venta, DetalleVenta
from modulos.clientes.models import Cliente

# El resto del archivo podría quedarse vacío ya que los modelos se importan de sus respectivos módulos