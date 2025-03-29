from models import db
from datetime import datetime

class Ingrediente(db.Model):
    """Modelo para los ingredientes"""
    __tablename__ = 'Ingredientes'
    idIngrediente = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombreIngrediente = db.Column(db.String(255), nullable=False)
    stock = db.Column(db.Float, nullable=False, default=0)
    unidad = db.Column(db.String(50))
    stock_minimo = db.Column(db.Float, nullable=False, default=0)
    precio_unitario = db.Column(db.Float, nullable=False, default=0)
    fecha_expiracion = db.Column(db.Date)
    
    # Relaciones
    movimientos = db.relationship('MovimientoInsumo', backref='ingrediente', lazy=True)
    
    def to_dict(self):
        """Convierte el modelo a un diccionario para facilitar la serialización"""
        return {
            'idIngrediente': self.idIngrediente,
            'nombreIngrediente': self.nombreIngrediente,
            'stock': self.stock,
            'unidad': self.unidad,
            'stock_minimo': self.stock_minimo,
            'precio_unitario': self.precio_unitario,
            'fecha_expiracion': self.fecha_expiracion.strftime('%Y-%m-%d') if self.fecha_expiracion else None
        }

class MovimientoInsumo(db.Model):
    """Modelo para registrar movimientos de ingredientes"""
    __tablename__ = 'MovimientosInsumos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ingrediente_id = db.Column(db.Integer, db.ForeignKey('Ingredientes.idIngrediente'), nullable=False)
    tipo_movimiento = db.Column(db.Integer, nullable=False)  # 1 = Consumo, 0 = Reabastecimiento
    cantidad = db.Column(db.Float, nullable=False)
    fecha_movimiento = db.Column(db.Date, nullable=False, default=datetime.now().date())
    referencia = db.Column(db.String(100))  # Referencia opcional (ej. ID de orden de compra o producción)
    
    def to_dict(self):
        """Convierte el modelo a un diccionario para facilitar la serialización"""
        return {
            'id': self.id,
            'ingrediente_id': self.ingrediente_id,
            'nombre_ingrediente': self.ingrediente.nombreIngrediente if self.ingrediente else None,
            'tipo_movimiento': self.tipo_movimiento,
            'cantidad': self.cantidad,
            'fecha_movimiento': self.fecha_movimiento.strftime('%Y-%m-%d') if self.fecha_movimiento else None,
            'referencia': self.referencia
        }