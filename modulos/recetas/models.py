from models import db

class Receta(db.Model):
    """Modelo para las recetas"""
    __tablename__ = 'Recetas'
    idReceta = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombreReceta = db.Column(db.String(150), nullable=False)
    instruccionesReceta = db.Column(db.Text)
    galletasProducidas = db.Column(db.Integer, nullable=True)
    estatus = db.Column(db.Integer, nullable=False)
    idGalleta = db.Column(db.Integer, db.ForeignKey('Galletas.idGalleta'), nullable=False)
    
    # Relaciones

    ingredientes = db.relationship('RecetaIngrediente', backref='receta', lazy=True)
    
    
    def to_dict(self):
        """Convierte el modelo a un diccionario para facilitar la serialización"""
        return {
            'id': self.idReceta,  # Incluir como 'id' para compatibilidad con JavaScript
            'idReceta': self.idReceta,
            'nombreReceta': self.nombreReceta,
            'instruccionesReceta': self.instruccionesReceta,
            'galletasProducidas': self.galletasProducidas,
            'idGalleta': self.idGalleta,
            'estatus': self.estatus
        }

class RecetaIngrediente(db.Model):
    """Modelo para la relación entre recetas e ingredientes"""
    __tablename__ = 'RecetaIngredientes'
    receta_id = db.Column(db.Integer, db.ForeignKey('Recetas.idReceta'), primary_key=True)
    ingrediente_id = db.Column(db.Integer, db.ForeignKey('Ingredientes.idIngrediente'), primary_key=True)
    cantidad = db.Column(db.Float, nullable=False)
    
    # Relación con Ingrediente
    ingrediente = db.relationship('Ingrediente', backref='recetas_relacion', lazy=True)
    
    def to_dict(self):
        """Convierte el modelo a un diccionario para facilitar la serialización"""
        return {
            'receta_id': self.receta_id,
            'ingrediente_id': self.ingrediente_id,
            'cantidad': self.cantidad
        }
