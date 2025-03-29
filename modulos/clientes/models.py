from models import db

class Cliente(db.Model):
    """Modelo de clientes"""
    __tablename__ = 'Cliente'
    idCliente = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombreCliente = db.Column(db.String(250), nullable=False)
    fechaNacimiento = db.Column(db.DateTime)
    telefono = db.Column(db.String(25), nullable=False)
    correo = db.Column(db.String(150))
    estatus = db.Column(db.Integer, nullable=False)
    
    # Relationships
    ventas = db.relationship('Venta', backref='cliente', lazy=True)
    
    def to_dict(self):        
        return {
            'idCliente': self.idCliente,
            'nombreCliente': self.nombreCliente,
            'fechaNacimiento': self.fechaNacimiento.strftime('%Y-%m-%d') if self.fechaNacimiento else None,
            'telefono': self.telefono,
            'correo': self.correo,
            'estatus': self.estatus
        }