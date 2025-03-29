from models import db
from modulos.recetas.models import Receta
from modulos.galletas.models import Galleta

class RecetaController:
    """Controlador para la lógica de negocio relacionada con recetas"""
    
    @staticmethod
    def get_all_recetas():
        """Obtener todas las recetas"""
        return Receta.query.all()
    
    @staticmethod
    def get_active_recetas():
        """Obtener solo recetas activas"""
        return Receta.query.filter_by(estatus=1).all()
    
    @staticmethod
    def get_receta_by_id(receta_id):
        """Obtener una receta por su ID"""
        return Receta.query.get(receta_id)
    
    @staticmethod
    def get_recetas_by_galleta(galleta_id):
        """Obtener todas las recetas para una galleta específica"""
        return Receta.query.filter_by(idGalleta=galleta_id).all()
    
    @staticmethod
    def create_receta(data):
        """Crear una nueva receta con los datos proporcionados"""
        receta = Receta(
            nombreReceta=data.get('nombreReceta'),
            instruccionesReceta=data.get('instruccionesReceta', ''),
            galletasProducidas=int(data.get('galletasProducidas', 0)),
            idGalleta=int(data.get('idGalleta')),
            estatus=int(data.get('estatus', 1))
        )
        
        db.session.add(receta)
        db.session.commit()
        return receta
    
    @staticmethod
    def update_receta(receta_id, data):
        """Actualizar una receta existente"""
        receta = Receta.query.get(receta_id)
        
        if not receta:
            return None
        
        receta.nombreReceta = data.get('nombreReceta', receta.nombreReceta)
        receta.instruccionesReceta = data.get('instruccionesReceta', receta.instruccionesReceta)
        
        if 'galletasProducidas' in data:
            receta.galletasProducidas = int(data.get('galletasProducidas'))
        
        if 'idGalleta' in data:
            receta.idGalleta = int(data.get('idGalleta'))
        
        if 'estatus' in data:
            receta.estatus = int(data.get('estatus'))
        
        db.session.commit()
        return receta
    
    @staticmethod
    def delete_receta(receta_id):
        """Eliminar una receta si no tiene dependencias"""
        receta = Receta.query.get(receta_id)
        
        if not receta:
            return False
        
        # Eliminar relaciones en RecetaIngrediente
        for ingrediente in receta.ingredientes:
            db.session.delete(ingrediente)
        
        db.session.delete(receta)
        db.session.commit()
        return True
    
    @staticmethod
    def get_galletas_for_form():
        """Obtener galletas activas para usar en el formulario"""
        return Galleta.query.filter_by(estatus=1).all() 