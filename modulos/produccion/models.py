from models import db
from datetime import datetime

class Produccion(db.Model):
    """Modelo para producción de galletas"""
    __tablename__ = 'Produccion'
    idProduccion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    receta_id = db.Column(db.Integer, db.ForeignKey('Recetas.idReceta'), nullable=False)
    estado_produccion = db.Column(db.Integer, nullable=False)  # 0=Pendiente, 1=En Proceso, 2=Terminado, 3=Cancelado
    fecha_produccion = db.Column(db.Date, nullable=False, default=datetime.now().date())
    cantidad_producida = db.Column(db.Integer)
    lote = db.Column(db.String(20))
    
    # Relaciones
    detalles = db.relationship('ProduccionDetalle', backref='produccion', lazy=True, cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convierte el modelo a un diccionario para facilitar la serialización"""
        return {
            'idProduccion': self.idProduccion,
            'receta_id': self.receta_id,
            'estado_produccion': self.estado_produccion,
            'fecha_produccion': self.fecha_produccion.strftime('%Y-%m-%d') if self.fecha_produccion else None,
            'cantidad_producida': self.cantidad_producida,
            'lote': self.lote
        }

class ProduccionDetalle(db.Model):
    """Modelo para detalles de producción (ingredientes utilizados)"""
    __tablename__ = 'ProduccionDetalles'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    produccion_id = db.Column(db.Integer, db.ForeignKey('Produccion.idProduccion'), nullable=False)
    ingrediente_id = db.Column(db.Integer, db.ForeignKey('Ingredientes.idIngrediente'), nullable=False)
    cantidad_requerida = db.Column(db.Float, nullable=False)
    cantidad_usada = db.Column(db.Float, nullable=False)
    estado = db.Column(db.Integer, nullable=False)  # 0=Pendiente, 1=Usado
    
    # Relaciones
    ingrediente = db.relationship('Ingrediente', backref='produccion_detalles', lazy=True)
    
    def to_dict(self):
        """Convierte el modelo a un diccionario para facilitar la serialización"""
        return {
            'id': self.id,
            'produccion_id': self.produccion_id,
            'ingrediente_id': self.ingrediente_id,
            'nombre_ingrediente': self.ingrediente.nombreIngrediente if self.ingrediente else None,
            'cantidad_requerida': self.cantidad_requerida,
            'cantidad_usada': self.cantidad_usada,
            'estado': self.estado
        }