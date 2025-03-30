from models import db
from modulos.recetas.models import Receta, RecetaIngrediente
from modulos.galletas.models import Galletas
from modulos.ingredientes.models import Ingrediente

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
        RecetaIngrediente.query.filter_by(receta_id=receta_id).delete()
        
        db.session.delete(receta)
        db.session.commit()
        return True
    
    @staticmethod
    def get_galletas_for_form():
        """Obtener galletas activas para usar en el formulario"""
        return Galletas.query.filter_by(estatus=1).all()
    
    @staticmethod
    def get_ingredientes_by_receta(receta_id):
        """Obtener todos los ingredientes asociados a una receta"""
        ingredientes_data = []
        ingredientes_receta = RecetaIngrediente.query.filter_by(receta_id=receta_id).all()
        
        for ingrediente_receta in ingredientes_receta:
            ingrediente = Ingrediente.query.get(ingrediente_receta.ingrediente_id)
            if ingrediente:
                ingredientes_data.append({
                    'id': ingrediente.idIngrediente,
                    'nombre': ingrediente.nombreIngrediente,
                    'cantidad': ingrediente_receta.cantidad,
                    'unidad': ingrediente.unidad or ''
                })
        
        return ingredientes_data
    
    @staticmethod
    def get_available_ingredientes(receta_id):
        """Obtener ingredientes disponibles que no están en la receta"""
        # Obtener IDs de ingredientes ya en la receta
        ingredientes_existentes = RecetaIngrediente.query.filter_by(receta_id=receta_id).all()
        ingredientes_ids = [ir.ingrediente_id for ir in ingredientes_existentes]
        
        # Obtener ingredientes que no están en la receta
        ingredientes_disponibles = Ingrediente.query.filter(~Ingrediente.idIngrediente.in_(ingredientes_ids)).all()
        
        return ingredientes_disponibles
    
    @staticmethod
    def add_ingrediente_to_receta(receta_id, ingrediente_id, cantidad):
        """Añadir un ingrediente a una receta"""
        try:
            # Verificar si ya existe esta relación
            existente = RecetaIngrediente.query.filter_by(
                receta_id=receta_id,
                ingrediente_id=ingrediente_id
            ).first()
            
            if existente:
                return False, "Este ingrediente ya está en la receta"
                
            # Crear la nueva relación
            receta_ingrediente = RecetaIngrediente(
                receta_id=receta_id,
                ingrediente_id=ingrediente_id,
                cantidad=float(cantidad)
            )
            
            db.session.add(receta_ingrediente)
            db.session.commit()
            return True, "Ingrediente añadido correctamente"
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def remove_ingrediente_from_receta(receta_id, ingrediente_id):
        """Eliminar un ingrediente de una receta"""
        try:
            relacion = RecetaIngrediente.query.filter_by(
                receta_id=receta_id,
                ingrediente_id=ingrediente_id
            ).first()
            
            if not relacion:
                return False, "No se encontró el ingrediente en la receta"
                
            db.session.delete(relacion)
            db.session.commit()
            return True, "Ingrediente eliminado correctamente"
        except Exception as e:
            db.session.rollback()
            return False, str(e)