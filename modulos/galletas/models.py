from models import db
from datetime import datetime
import base64

class Galletas(db.Model):
    """Modelo para las galletas"""
    __tablename__ = 'Galletas'
    idGalleta = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombreGalleta = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text)
    estado = db.Column(db.String(90), nullable=True)
    existencias = db.Column(db.Integer, nullable=True, default=0)
    peso_por_unidad = db.Column(db.Float)
    precio_unitario = db.Column(db.Float)
    foto = db.Column(db.LargeBinary(length=16777215))
    estatus = db.Column(db.Integer, nullable=False)
    
    # Relaciones
    recetas = db.relationship('Receta', backref='galletas', lazy=True)
    
    def to_dict(self):
        """Convierte el modelo a un diccionario para facilitar la serialización"""
        return {
            'idGalleta': self.idGalleta,
            'nombreGalleta': self.nombreGalleta,
            'descripcion': self.descripcion,
            'estado': self.estado,
            'peso_por_unidad': self.peso_por_unidad,
            'precio_unitario': self.precio_unitario,
            'estatus': self.estatus
        } 
    
    def get_galleta_foto(self):
        if self.foto:
            return f"data:image/jpeg;base64,{base64.b64encode(self.foto).decode('utf-8')}"
        else:
            return None
    
class MermaGalletas(db.Model):
    """Modelo para registrar las mermas de galletas"""
    __tablename__ = 'MermaGalletas'
    idMerma = db.Column(db.Integer, primary_key=True, autoincrement=True)
    galleta_id = db.Column(db.Integer, db.ForeignKey('Galletas.idGalleta'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.now)
    
    # Relación con Galletas
    galleta = db.relationship('Galletas', backref='mermas', lazy=True)