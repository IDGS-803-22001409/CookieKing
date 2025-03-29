from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

def init_db():
    # Importar todos los modelos para asegurarse de que SQLAlchemy los conozca
    # Las importaciones están aquí para evitar dependencias circulares
    import modulos.galletas.models
    import modulos.recetas.models
    import modulos.ingredientes.models
    
    # Crear todas las tablas
    db.create_all()

class Proveedor(db.Model):
    __tablename__ = 'Proveedores'
    idProveedor = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_proveedor = db.Column(db.String(255), nullable=False)
    telefono = db.Column(db.String(255))
    
    # Relaciones
    compras = db.relationship('CompraInsumo', backref='proveedor', lazy=True)

class CompraInsumo(db.Model):
    __tablename__ = 'ComprasInsumos'
    idCompra = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha = db.Column(db.Date, nullable=False)
    idProveedor = db.Column(db.Integer, db.ForeignKey('Proveedores.idProveedor'))
    
    # Relaciones
    detalles = db.relationship('CompraDetalle', backref='compra', lazy=True)

class CompraDetalle(db.Model):
    __tablename__ = 'ComprasDetalles'
    idCompraDetalle = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idCompra = db.Column(db.Integer, db.ForeignKey('ComprasInsumos.idCompra'))
    idIngrediente = db.Column(db.Integer, db.ForeignKey('Ingredientes.idIngrediente'))
    cantidad = db.Column(db.Integer, nullable=False)

class RecetaIngrediente(db.Model):
    __tablename__ = 'RecetaIngredientes'
    receta_id = db.Column(db.Integer, db.ForeignKey('Recetas.idReceta'), primary_key=True)
    ingrediente_id = db.Column(db.Integer, db.ForeignKey('Ingredientes.idIngrediente'), primary_key=True)
    cantidad = db.Column(db.Float, nullable=False)

class Produccion(db.Model):
    __tablename__ = 'Produccion'
    idProduccion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    receta_id = db.Column(db.Integer, db.ForeignKey('Recetas.idReceta'))
    estado_produccion = db.Column(db.Integer, nullable=False)  # 1 = En Proceso, 0 = Terminado
    fecha_produccion = db.Column(db.Date)

class Venta(db.Model):
    __tablename__ = 'Ventas'
    idVenta = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fechaVenta = db.Column(db.Date, nullable=False)
    cliente = db.Column(db.String(150))
    estatus = db.Column(db.Integer, nullable=False)
    
    # Relaciones
    detalles = db.relationship('DetalleVenta', backref='venta', lazy=True)

class DetalleVenta(db.Model):
    __tablename__ = 'DetallesVenta'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    venta_id = db.Column(db.Integer, db.ForeignKey('Ventas.idVenta'))
    galleta_id = db.Column(db.Integer, db.ForeignKey('Galletas.idGalleta'))
    cantidad = db.Column(db.Integer, nullable=False)
    tipo_venta = db.Column(db.Integer, nullable=False)  # 1 = Individual, 0 = Paquete

class MovimientoInsumo(db.Model):
    __tablename__ = 'MovimientosInsumos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ingrediente_id = db.Column(db.Integer, db.ForeignKey('Ingredientes.idIngrediente'))
    tipo_movimiento = db.Column(db.Integer, nullable=False)  # 1 = Consumo, 0 = Reabastecimiento
    cantidad = db.Column(db.Float, nullable=False)
    fecha_movimiento = db.Column(db.Date, nullable=False)