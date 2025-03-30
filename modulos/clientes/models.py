from models import db
from datetime import datetime

class Cliente(db.Model):
    """Modelo de clientes"""
    __tablename__ = 'Cliente'
    idCliente = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombreCliente = db.Column(db.String(250), nullable=False)
    fechaNacimiento = db.Column(db.DateTime)
    telefono = db.Column(db.String(25), nullable=False)
    correo = db.Column(db.String(150))
    estatus = db.Column(db.Integer, nullable=False, default=1)
    
    # Relationships (si se implementan)
    # Modify this line to use the string name of the model instead of directly referencing it
    ventas = db.relationship('Venta', backref='cliente', lazy=True)
    
    def to_dict(self):
        """Convertir objeto a diccionario para serialización JSON"""
        try:
            return {
                'idCliente': self.idCliente,
                'nombreCliente': self.nombreCliente,
                'fechaNacimiento': self.fechaNacimiento.strftime('%Y-%m-%d') if self.fechaNacimiento else None,
                'telefono': self.telefono,
                'correo': self.correo,
                'estatus': self.estatus
            }
        except Exception as e:
            print(f"Error en to_dict: {str(e)}")
            # Versión simplificada en caso de error
            return {
                'idCliente': self.idCliente,
                'nombreCliente': self.nombreCliente,
                'telefono': self.telefono,
                'correo': self.correo,
                'estatus': self.estatus
            }