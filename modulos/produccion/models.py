from models import db

class Produccion(db.Model):
    """Model for production"""
    __tablename__ = 'Produccion'
    idProduccion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    receta_id = db.Column(db.Integer, db.ForeignKey('Recetas.idReceta'))
    estado_produccion = db.Column(db.Integer, nullable=False)  # 1 = En Proceso, 0 = Terminado
    fecha_produccion = db.Column(db.Date)
    fecha_caducidad = db.Column(db.Date)
    
    def to_dict(self):
        """Convert model to dictionary for serialization"""
        return {
            'idProduccion': self.idProduccion,
            'receta_id': self.receta_id,
            'estado_produccion': self.estado_produccion,
            'fecha_produccion': self.fecha_produccion.strftime('%Y-%m-%d') if self.fecha_produccion else None,
            'fecha_caducidad': self.fecha_caducidad.strftime('%Y-%m-%d') if self.fecha_caducidad else None
        }