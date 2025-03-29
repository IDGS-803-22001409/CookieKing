from models import db

class Receta(db.Model):
    """Modelo para las recetas"""
    __tablename__ = 'Recetas'
    idReceta = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombreReceta = db.Column(db.String(150), nullable=False)
    instruccionesReceta = db.Column(db.Text)
    galletasProducidas = db.Column(db.Integer)
    estatus = db.Column(db.Integer, nullable=False)
    idGalleta = db.Column(db.Integer, db.ForeignKey('Galletas.idGalleta'), nullable=False)
    
    # Relaciones
    ingredientes = db.relationship('RecetaIngrediente', backref='receta', lazy=True)
    producciones = db.relationship('Produccion', backref='receta', lazy=True)
    
    def to_dict(self):
        """Convierte el modelo a un diccionario para facilitar la serialización"""
        return {
            'idReceta': self.idReceta,
            'nombreReceta': self.nombreReceta,
            'instruccionesReceta': self.instruccionesReceta,
            'galletasProducidas': self.galletasProducidas,
            'idGalleta': self.idGalleta,
            'estatus': self.estatus
        } 