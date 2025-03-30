from models import db

class Galletas(db.Model):
    """Modelo para las galletas"""
    __tablename__ = 'Galletas'
    idGalleta = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombreGalleta = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text)
    estado = db.Column(db.String(90), nullable=False)
    peso_por_unidad = db.Column(db.Float)
    precio_unitario = db.Column(db.Float)
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