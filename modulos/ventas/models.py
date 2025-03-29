from models import db
from datetime import datetime

class Venta(db.Model):
    """Model for sales"""
    __tablename__ = 'Ventas'
    idVenta = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fechaVenta = db.Column(db.Date, nullable=False, default=datetime.now().date())
    IdCliente = db.Column(db.Integer, db.ForeignKey('Cliente.idCliente'))
    estatus = db.Column(db.Integer, nullable=False, default=1)  # 1: Completada, 0: Pendiente, 2: Cancelada
    
    # Relaciones
    detalles = db.relationship('DetalleVenta', backref='venta', lazy=True, cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert model to dictionary for serialization"""
        return {
            'idVenta': self.idVenta,
            'fechaVenta': self.fechaVenta.strftime('%Y-%m-%d') if self.fechaVenta else None,
            'IdCliente': self.IdCliente,
            'nombre_cliente': self.cliente.nombreCliente if self.cliente else "Cliente General",
            'estatus': self.estatus
        }

class DetalleVenta(db.Model):
    """Model for sale details"""
    __tablename__ = 'DetallesVenta'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    venta_id = db.Column(db.Integer, db.ForeignKey('Ventas.idVenta'), nullable=False)
    galleta_id = db.Column(db.Integer, db.ForeignKey('Galletas.idGalleta'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    tipo_venta = db.Column(db.Integer, nullable=False)  # 1 = Individual, 0 = Paquete
    
    # Relationship
    galleta = db.relationship('Galleta', backref='detalles_venta', lazy=True)
    
    def to_dict(self):
        """Convert model to dictionary for serialization"""
        return {
            'id': self.id,
            'venta_id': self.venta_id,
            'galleta_id': self.galleta_id,
            'nombre_galleta': self.galleta.nombreGalleta if self.galleta else None,
            'cantidad': self.cantidad,
            'tipo_venta': self.tipo_venta
        }