from models import db
from datetime import datetime

class Produccion(db.Model):
    """Modelo para producción de galletas"""
    __tablename__ = 'Produccion'
    idProduccion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    receta_id = db.Column(db.Integer, db.ForeignKey('Recetas.idReceta'), nullable=False)
    estado_produccion = db.Column(db.Integer, nullable=False)  # 0=Pendiente, 1=En Proceso, 2=Terminado, 3=Cancelado
    fecha_produccion = db.Column(db.Date, nullable=False, default=datetime.now().date())
    fecha_caducidad = db.Column(db.Date)
    fecha_finalizacion = db.Column(db.DateTime)
    cantidad_producida = db.Column(db.Integer)
    lote = db.Column(db.String(20))
    
    # Relaciones
    detalles = db.relationship('ProduccionDetalle', backref='produccion', lazy=True, cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convierte el modelo a un diccionario para facilitar la serialización"""
        return {
            'idProduccion': self.idProduccion,
            'receta_id': self.receta_id,
            'nombre_receta': self.receta.nombreReceta if self.receta else None,
            'estado_produccion': self.estado_produccion,
            'fecha_produccion': self.fecha_produccion.strftime('%Y-%m-%d') if self.fecha_produccion else None,
            'fecha_caducidad': self.fecha_caducidad.strftime('%Y-%m-%d') if self.fecha_caducidad else None,
            'fecha_finalizacion': self.fecha_finalizacion.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_finalizacion else None,
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

class InventarioGalletas(db.Model):
    """Modelo para inventario de galletas producidas"""
    __tablename__ = 'InventarioGalletas'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    galleta_id = db.Column(db.Integer, db.ForeignKey('Galletas.idGalleta'), nullable=False)
    produccion_id = db.Column(db.Integer, db.ForeignKey('Produccion.idProduccion'))
    cantidad_inicial = db.Column(db.Integer, nullable=False)
    cantidad_actual = db.Column(db.Integer, nullable=False)
    fecha_produccion = db.Column(db.Date, nullable=False)
    fecha_caducidad = db.Column(db.Date, nullable=False)
    lote = db.Column(db.String(20))
    
    # Relaciones
    galleta = db.relationship('Galleta', backref='inventario', lazy=True)
    produccion = db.relationship('Produccion', backref='inventario_galletas', lazy=True)
    
    def to_dict(self):
        """Convierte el modelo a un diccionario para facilitar la serialización"""
        return {
            'id': self.id,
            'galleta_id': self.galleta_id,
            'nombre_galleta': self.galleta.nombreGalleta if self.galleta else None,
            'produccion_id': self.produccion_id,
            'cantidad_inicial': self.cantidad_inicial,
            'cantidad_actual': self.cantidad_actual,
            'fecha_produccion': self.fecha_produccion.strftime('%Y-%m-%d') if self.fecha_produccion else None,
            'fecha_caducidad': self.fecha_caducidad.strftime('%Y-%m-%d') if self.fecha_caducidad else None,
            'lote': self.lote
        }