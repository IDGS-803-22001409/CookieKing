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
        try:
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
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Error al crear receta: {str(e)}")
    
    @staticmethod
    def update_receta(receta_id, data):
        """Actualizar una receta existente"""
        try:
            receta = Receta.query.get(receta_id)
            if not receta:
                return None
            
            if 'nombreReceta' in data:
                receta.nombreReceta = data['nombreReceta']
            if 'instruccionesReceta' in data:
                receta.instruccionesReceta = data['instruccionesReceta']
            if 'galletasProducidas' in data:
                receta.galletasProducidas = int(data['galletasProducidas'])
            if 'idGalleta' in data:
                receta.idGalleta = int(data['idGalleta'])
            if 'estatus' in data:
                receta.estatus = int(data['estatus'])
            
            db.session.commit()
            return receta
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Error al actualizar receta: {str(e)}")
    
    @staticmethod
    def delete_receta(receta_id):
        """Eliminar una receta si no tiene dependencias"""
        try:
            receta = Receta.query.get(receta_id)
            if not receta:
                return False
            
            # Eliminar relaciones en RecetaIngrediente
            RecetaIngrediente.query.filter_by(receta_id=receta_id).delete()
            db.session.delete(receta)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Error al eliminar receta: {str(e)}")
    
    @staticmethod
    def get_galletas_for_form():
        """Obtener galletas activas para usar en el formulario"""
        return Galletas.query.filter_by(estatus=1).all()
    
    @staticmethod
    def get_ingredientes_by_receta(receta_id):
        """Obtener todos los ingredientes asociados a una receta"""
        try:
            ingredientes_data = []
            ingredientes_receta = RecetaIngrediente.query.filter_by(receta_id=receta_id).all()
            
            for ingrediente_receta in ingredientes_receta:
                ingrediente = Ingrediente.query.get(ingrediente_receta.ingrediente_id)
                if ingrediente:
                    ingredientes_data.append({
                        'id': ingrediente.idIngrediente,
                        'nombre': ingrediente.nombreIngrediente,
                        'cantidad': ingrediente_receta.cantidad,
                        'unidad': ingrediente.unidad or '',
                        'precio_unitario': ingrediente.precio_unitario or 0
                    })
            
            return ingredientes_data
        except Exception as e:
            raise ValueError(f"Error al obtener ingredientes: {str(e)}")
    
    @staticmethod
    def get_available_ingredientes(receta_id):
        """Obtener ingredientes disponibles que no están en la receta"""
        try:
            # Obtener IDs de ingredientes ya en la receta
            ingredientes_existentes = RecetaIngrediente.query.filter_by(receta_id=receta_id).all()
            ingredientes_ids = [ir.ingrediente_id for ir in ingredientes_existentes]
            
            # Obtener ingredientes que no están en la receta
            return Ingrediente.query.filter(
                ~Ingrediente.idIngrediente.in_(ingredientes_ids)
            ).all()
        except Exception as e:
            raise ValueError(f"Error al obtener ingredientes disponibles: {str(e)}")
    
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
            
            # Actualizar cálculos
            success, message = RecetaController.calcular_galletas_producidas(receta_id)
            if not success:
                db.session.rollback()
                return False, message
                
            success, message = RecetaController.actualizar_precio_peso_galleta(receta_id)
            if not success:
                db.session.rollback()
                return False, message
            
            db.session.commit()
            return True, "Ingrediente añadido correctamente"
        except Exception as e:
            db.session.rollback()
            return False, f"Error al añadir ingrediente: {str(e)}"

    @staticmethod
    def actualizar_galletas_por_ingrediente(ingrediente_id):
        """
        Actualiza todas las galletas que usan este ingrediente
        cuando se modifica su precio
        """
        try:
            # Obtener todas las recetas que usan este ingrediente
            recetas = db.session.query(RecetaIngrediente.receta_id).filter_by(
                ingrediente_id=ingrediente_id
            ).distinct().all()
            
            for receta_id in recetas:
                receta_id = receta_id[0]  # Extraer el ID de la tupla
                
                # Recalcular producción y precios
                success, msg = RecetaController.calcular_galletas_producidas(receta_id)
                if not success:
                    print(f"Error actualizando producción para receta {receta_id}: {msg}")
                    continue
                    
                success, msg = RecetaController.actualizar_precio_peso_galleta(receta_id)
                if not success:
                    print(f"Error actualizando precio/peso para receta {receta_id}: {msg}")
            
            db.session.commit()
            return True, "Galletas actualizadas correctamente"
        except Exception as e:
            db.session.rollback()
            return False, f"Error al actualizar galletas: {str(e)}"

    @staticmethod
    def actualizar_precio_peso_galleta(receta_id):
        """Calcular el precio unitario y el peso por unidad de una receta"""
        try:
            receta = Receta.query.get(receta_id)
            if not receta or not receta.idGalleta:
                return False, "No se encontró la receta o la galleta asociada"
            
            # Obtener todos los ingredientes con sus precios y unidades
            ingredientes = db.session.query(
                RecetaIngrediente.cantidad,
                Ingrediente.precio_unitario,
                Ingrediente.unidad,
                Ingrediente.nombreIngrediente
            ).join(
                Ingrediente,
                RecetaIngrediente.ingrediente_id == Ingrediente.idIngrediente
            ).filter(
                RecetaIngrediente.receta_id == receta_id
            ).all()

            if not ingredientes:
                # Resetear valores si no hay ingredientes
                Galletas.query.filter_by(idGalleta=receta.idGalleta).update({
                    'peso_por_unidad': 0,
                    'precio_unitario': 0
                })
                db.session.commit()
                return True, "Receta sin ingredientes - valores reseteados"
            
            peso_total = 0.0
            costo_total = 0.0

            for cantidad, precio, unidad, nombre in ingredientes:
                if precio is None:
                    return False, f"El ingrediente {nombre} no tiene precio unitario"
                
                # Convertir todo a kg para cálculo consistente
                if unidad and unidad.lower() in ['g', 'gr', 'gramos']:
                    cantidad_kg = cantidad / 1000
                elif unidad and unidad.lower() in ['unidad', 'unidades', 'u']:
                    # Manejo especial para huevos (50g por unidad)
                    if 'huevo' in nombre.lower():
                        cantidad_kg = cantidad * 0.05
                    else:
                        cantidad_kg = cantidad
                elif unidad and unidad.lower() in ['litro', 'litros', 'l']:
                    # Asumir 1 kg por litro para líquidos
                    cantidad_kg = cantidad * 1.0
                else:  # asumimos kg por defecto
                    cantidad_kg = cantidad

                peso_total += cantidad_kg
                costo_total += cantidad_kg * precio

            if receta.galletasProducidas <= 0:
                return False, "La producción debe ser mayor a cero"

            peso_por_galleta = peso_total / receta.galletasProducidas
            precio_por_galleta = (costo_total * 1.3) / receta.galletasProducidas  # 30% margen

            # Actualizar la galleta
            Galletas.query.filter_by(idGalleta=receta.idGalleta).update({
                'peso_por_unidad': round(peso_por_galleta, 4),
                'precio_unitario': round(precio_por_galleta, 2)
            })
            db.session.commit()
            
            return True, "Precio y peso actualizados correctamente"
        except Exception as e:
            db.session.rollback()
            return False, f"Error al actualizar precio/peso: {str(e)}"

    @staticmethod
    def calcular_galletas_producidas(receta_id):
        """Calcula cuántas galletas se pueden producir con los ingredientes actuales"""
        try:
            receta = Receta.query.get(receta_id)
            if not receta:
                return False, "Receta no encontrada"
            
            # Obtener ingredientes con sus stocks y unidades
            ingredientes = db.session.query(
                RecetaIngrediente.cantidad,
                Ingrediente.unidad,
                Ingrediente.stock,
                Ingrediente.nombreIngrediente
            ).join(
                Ingrediente,
                RecetaIngrediente.ingrediente_id == Ingrediente.idIngrediente
            ).filter(
                RecetaIngrediente.receta_id == receta_id
            ).all()

            if not ingredientes:
                return False, "No hay ingredientes en esta receta"
            
            max_galletas = float('inf')
            ingrediente_limitante = None

            for cantidad_receta, unidad, stock, nombre in ingredientes:
                if stock is None:
                    return False, f"El ingrediente {nombre} no tiene existencias registradas"
                
                if stock <= 0:
                    return False, f"El ingrediente {nombre} no tiene existencias disponibles"
                
                # Conversión a kg para cálculo consistente
                if unidad and unidad.lower() in ['g', 'gr', 'gramos']:
                    cantidad_kg = cantidad_receta / 1000
                    existencias_kg = stock / 1000
                elif unidad and unidad.lower() in ['unidad', 'unidades', 'u']:
                    # Manejo especial para huevos (50g por unidad)
                    if 'huevo' in nombre.lower():
                        cantidad_kg = cantidad_receta * 0.05
                        existencias_kg = stock * 0.05
                    else:
                        cantidad_kg = cantidad_receta
                        existencias_kg = stock
                elif unidad and unidad.lower() in ['litro', 'litros', 'l']:
                    # Asumir 1 kg por litro para líquidos
                    cantidad_kg = cantidad_receta * 1.0
                    existencias_kg = stock * 1.0
                else:  # asumimos kg por defecto
                    cantidad_kg = cantidad_receta
                    existencias_kg = stock

                if cantidad_kg <= 0:
                    return False, f"Cantidad inválida para {nombre}"

                galletas_posibles = existencias_kg / cantidad_kg
                
                if galletas_posibles < max_galletas:
                    max_galletas = galletas_posibles
                    ingrediente_limitante = nombre

            if max_galletas == float('inf'):
                return False, "No se pudo calcular la producción"

            galletas_producibles = int(max_galletas)
            
            # Actualizar la receta
            receta.galletasProducidas = galletas_producibles
            db.session.commit()
            
            msg = f"Producción actualizada a {galletas_producibles} unidades"
            if ingrediente_limitante:
                msg += f" (limitado por {ingrediente_limitante})"
            
            return True, msg
        except ZeroDivisionError:
            db.session.rollback()
            return False, "Error: Cantidades en la receta no pueden ser cero"
        except Exception as e:
            db.session.rollback()
            return False, f"Error al calcular producción: {str(e)}"

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
            
            # Verificar si quedan ingredientes
            remaining = RecetaIngrediente.query.filter_by(receta_id=receta_id).count()
            
            if remaining > 0:
                # Recalcular si aún hay ingredientes
                success, message = RecetaController.calcular_galletas_producidas(receta_id)
                if not success:
                    db.session.rollback()
                    return False, message
                
                success, message = RecetaController.actualizar_precio_peso_galleta(receta_id)
                if not success:
                    db.session.rollback()
                    return False, message
            else:
                # Resetear valores si no quedan ingredientes
                Receta.query.filter_by(idReceta=receta_id).update({
                    'galletasProducidas': 0
                })
                Galletas.query.filter_by(idGalleta=Receta.query.get(receta_id).idGalleta).update({
                    'peso_por_unidad': 0,
                    'precio_unitario': 0
                })
            
            db.session.commit()
            return True, "Ingrediente eliminado correctamente"
        except Exception as e:
            db.session.rollback()
            return False, f"Error al eliminar ingrediente: {str(e)}"