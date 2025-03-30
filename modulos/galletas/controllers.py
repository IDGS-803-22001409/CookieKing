from models import db
from modulos.galletas.models import Galletas

class GalletaController:
    """Controlador para la lógica de negocio relacionada con galletas"""
    
    @staticmethod
    def get_all_galletas():
        """Obtener todas las galletas"""
        return Galletas.query.all()
    
    @staticmethod
    def get_active_galletas():
        """Obtener solo galletas activas"""
        return Galletas.query.filter_by(estatus=1).all()
    
    @staticmethod
    def get_galleta_by_id(galleta_id):
        """Obtener una galleta por su ID"""
        return Galletas.query.get(galleta_id)
    
    @staticmethod
    def create_galleta(data):
        """Crear una nueva galleta con los datos proporcionados"""
        galleta = Galletas(
            nombreGalleta=data.get('nombreGalleta'),
            descripcion=data.get('descripcion', ''),
            estado=data.get('estado'),
            peso_por_unidad=float(data.get('peso_por_unidad', 0)),
            precio_unitario=float(data.get('precio_unitario', 0)),
            estatus=int(data.get('estatus', 1))
        )
        
        db.session.add(galleta)
        db.session.commit()
        return galleta
    
    @staticmethod
    def update_galleta(galleta_id, data):
        """Actualizar una galleta existente"""
        galleta = Galletas.query.get(galleta_id)
        
        if not galleta:
            return None
        
        galleta.nombreGalleta = data.get('nombreGalleta', galleta.nombreGalleta)
        galleta.descripcion = data.get('descripcion', galleta.descripcion)
        galleta.estado = data.get('estado', galleta.estado)
        
        if 'peso_por_unidad' in data:
            galleta.peso_por_unidad = float(data['peso_por_unidad'])
        
        if 'precio_unitario' in data:
            galleta.precio_unitario = float(data['precio_unitario'])
        
        if 'estatus' in data:
            galleta.estatus = int(data['estatus'])
        
        db.session.commit()
        return galleta
    
    @staticmethod
    def delete_galleta(galleta_id):
        """Eliminar una galleta si no tiene dependencias"""
        galleta = Galletas.query.get(galleta_id)
        
        if not galleta:
            return False
        
        # Verificar si hay recetas asociadas
        if galleta.recetas and len(galleta.recetas) > 0:
            return False
        
        db.session.delete(galleta)
        db.session.commit()
        return True
    
    @staticmethod
    def can_delete_galleta(galleta_id):
        """Verificar si una galleta puede ser eliminada (no tiene dependencias)"""
        galleta = Galletas.query.get(galleta_id)
        
        if not galleta:
            return False
        
        # Verificar si hay recetas asociadas
        if galleta.recetas and len(galleta.recetas) > 0:
            return False
        
        return True 