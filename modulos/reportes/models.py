# modulos / reportes / models.py
from datetime import datetime
from models import db

class HistorialReportes(db.Model):
    """Modelo para historial de reportes generados"""
    __tablename__ = 'historial_reportes'
    
    idHistorial = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    formato = db.Column(db.String(20), nullable=False)
    fechaGeneracion = db.Column(db.DateTime, nullable=False, default=datetime.now)
    usuario = db.Column(db.String(100), nullable=True)
    rutaArchivo = db.Column(db.String(255), nullable=True)
    exitoso = db.Column(db.Boolean, nullable=False, default=True)
    error = db.Column(db.Text, nullable=True)
    
    def to_dict(self):
        return {
            'idHistorial': self.idHistorial,
            'nombre': self.nombre,
            'tipo': self.tipo,
            'formato': self.formato,
            'fechaGeneracion': self.fechaGeneracion,
            'usuario': self.usuario,
            'rutaArchivo': self.rutaArchivo,
            'exitoso': self.exitoso,
            'error': self.error
        }