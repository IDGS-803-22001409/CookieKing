from models import db
from datetime import datetime

class Proveedor(db.Model):
    """Modelo para los proveedores"""
    __tablename__ = 'Proveedores'
    idProveedor = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_proveedor = db.Column(db.String(255), nullable=False)
    telefono = db.Column(db.String(20))
    correo = db.Column(db.String(100))
    direccion = db.Column(db.String(255))
    rfc = db.Column(db.String(13))
    estatus = db.Column(db.Integer, nullable=False, default=1)  # 1: Activo, 0: Inactivo
    fecha_registro = db.Column(db.DateTime, default=datetime.now)
    
    # Relaciones
    compras = db.relationship('CompraInsumo', backref='proveedor', lazy=True)
    
    def to_dict(self):
        """Convierte el modelo a un diccionario para facilitar la serialización"""
        return {
            'idProveedor': self.idProveedor,
            'nombre_proveedor': self.nombre_proveedor,
            'telefono': self.telefono,
            'correo': self.correo,
            'direccion': self.direccion,
            'rfc': self.rfc,
            'estatus': self.estatus,
            'fecha_registro': self.fecha_registro.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_registro else None
        }