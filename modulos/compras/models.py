from models import db
from datetime import datetime

class CompraInsumo(db.Model):
    """Modelo para compras de insumos"""
    __tablename__ = 'ComprasInsumos'
    idCompra = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha = db.Column(db.Date, nullable=False, default=datetime.now().date)
    fecha_registro = db.Column(db.DateTime, default=datetime.now)
    idProveedor = db.Column(db.Integer, db.ForeignKey('Proveedores.idProveedor'), nullable=False)
    total = db.Column(db.Float, nullable=False, default=0.0)
    estatus = db.Column(db.Integer, nullable=False, default=1)  # 1: Pagado, 0: Pendiente, 2: Cancelado
    numero_factura = db.Column(db.String(50))
    
    # Relaciones
    detalles = db.relationship('CompraDetalle', backref='compra', lazy=True, cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convierte el modelo a un diccionario para facilitar la serialización"""
        return {
            'idCompra': self.idCompra,
            'fecha': self.fecha.strftime('%Y-%m-%d') if self.fecha else None,
            'fecha_registro': self.fecha_registro.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_registro else None,
            'idProveedor': self.idProveedor,
            'nombre_proveedor': self.proveedor.nombre_proveedor if self.proveedor else None,
            'total': self.total,
            'estatus': self.estatus,
            'numero_factura': self.numero_factura
        }

class CompraDetalle(db.Model):
    """Modelo para detalles de compra"""
    __tablename__ = 'ComprasDetalles'
    idCompraDetalle = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idCompra = db.Column(db.Integer, db.ForeignKey('ComprasInsumos.idCompra'), nullable=False)
    idIngrediente = db.Column(db.Integer, db.ForeignKey('Ingredientes.idIngrediente'), nullable=False)
    cantidad = db.Column(db.Float, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    
    # Relaciones
    ingrediente = db.relationship('Ingrediente', backref='compras_detalle', lazy=True)
    
    def to_dict(self):
        """Convierte el modelo a un diccionario para facilitar la serialización"""
        return {
            'idCompraDetalle': self.idCompraDetalle,
            'idCompra': self.idCompra,
            'idIngrediente': self.idIngrediente,
            'nombre_ingrediente': self.ingrediente.nombreIngrediente if self.ingrediente else None,
            'cantidad': self.cantidad,
            'precio_unitario': self.precio_unitario,
            'subtotal': self.subtotal
        }