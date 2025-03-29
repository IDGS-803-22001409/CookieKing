from models import db
from datetime import datetime

class Ingrediente(db.Model):
    """Modelo para los ingredientes"""
    __tablename__ = 'Ingredientes'
    idIngrediente = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombreIngrediente = db.Column(db.String(255), nullable=False)
    stock = db.Column(db.Float, nullable=False)
    unidad = db.Column(db.String(50))
    stock_minimo = db.Column(db.Float, nullable=False)
    fecha_expiracion = db.Column(db.Date)
    
    # Relaciones
    recetas_relacion = db.relationship('RecetaIngrediente', backref='ingrediente', lazy=True)
    movimientos = db.relationship('MovimientoInsumo', backref='ingrediente', lazy=True)
    
    def to_dict(self):
        """Convierte el modelo a un diccionario para facilitar la serialización"""
        return {
            'idIngrediente': self.idIngrediente,
            'nombreIngrediente': self.nombreIngrediente,
            'stock': self.stock,
            'unidad': self.unidad,
            'stock_minimo': self.stock_minimo,
            'fecha_expiracion': self.fecha_expiracion.strftime('%Y-%m-%d') if self.fecha_expiracion else None
        } 