# modulos/produccion/controllers.py
from models import db
from modulos.produccion.models import Produccion, ProduccionDetalle
from modulos.recetas.models import Receta
from modulos.ingredientes.controllers import IngredienteController
from modulos.recetas.controllers import RecetaController
from datetime import datetime, timedelta

class ProduccionController:
    """Controlador para la lógica de negocio relacionada con producción"""
    
    @staticmethod
    def get_all_producciones():
        """Obtener todas las producciones"""
        return Produccion.query.order_by(Produccion.fecha_produccion.desc()).all()
    
    @staticmethod
    def get_produccion_by_id(produccion_id):
        """Obtener una producción por su ID"""
        return Produccion.query.get(produccion_id)
    
    @staticmethod
    def get_producciones_by_receta(receta_id):
        """Obtener producciones por receta"""
        return Produccion.query.filter_by(receta_id=receta_id).order_by(Produccion.fecha_produccion.desc()).all()
    
    @staticmethod
    def get_producciones_by_fecha(fecha_inicio, fecha_fin):
        """Obtener producciones en un rango de fechas"""
        return Produccion.query.filter(
            Produccion.fecha_produccion >= fecha_inicio,
            Produccion.fecha_produccion <= fecha_fin
        ).order_by(Produccion.fecha_produccion.desc()).all()
    
    @staticmethod
    def get_producciones_en_proceso():
        """Obtener producciones en proceso"""
        return Produccion.query.filter_by(estado_produccion=1).order_by(Produccion.fecha_produccion.desc()).all()
    
    @staticmethod
    def create_produccion(data):
        """Crear una nueva producción"""
        try:
            # Obtener la receta para calcular la fecha de caducidad
            receta = Receta.query.get(data.get('receta_id'))
            if not receta:
                raise ValueError("Receta no encontrada")
            
            # Convertir la fecha si viene como string
            if isinstance(data.get('fecha_produccion'), str):
                fecha_produccion = datetime.strptime(data.get('fecha_produccion'), '%Y-%m-%d').date()
            else:
                fecha_produccion = data.get('fecha_produccion', datetime.now().date())
            
            # Calcular fecha de caducidad (ejemplo: 7 días después de la producción)
            fecha_caducidad = fecha_produccion + timedelta(days=7)
            
            # Crear la producción
            produccion = Produccion(
                receta_id=data.get('receta_id'),
                estado_produccion=1,  # 1 = En Proceso
                fecha_produccion=fecha_produccion,
                fecha_caducidad=fecha_caducidad,
                cantidad_producida=0,  # Se actualiza al finalizar
                lote=data.get('lote', f"LOTE-{datetime.now().strftime('%Y%m%d%H%M%S')}")
            )
            
            db.session.add(produccion)
            db.session.flush()  # Para obtener el ID generado
            
            # Verificar ingredientes necesarios
            suficientes_ingredientes = True
            ingredientes_faltantes = []
            
            for ingrediente_receta in receta.ingredientes:
                ingrediente = ingrediente_receta.ingrediente
                cantidad_necesaria = ingrediente_receta.cantidad
                
                if ingrediente.stock < cantidad_necesaria:
                    suficientes_ingredientes = False
                    ingredientes_faltantes.append({
                        'nombre': ingrediente.nombreIngrediente,
                        'disponible': ingrediente.stock,
                        'necesario': cantidad_necesaria,
                        'faltante': cantidad_necesaria - ingrediente.stock
                    })
            
            if not suficientes_ingredientes:
                # Si no hay suficientes ingredientes, marcar como pendiente
                produccion.estado_produccion = 0  # 0 = Pendiente (esperando ingredientes)
                db.session.commit()
                return produccion, ingredientes_faltantes
            
            # Si hay suficientes ingredientes, crear detalles y consumir ingredientes
            for ingrediente_receta in receta.ingredientes:
                ingrediente = ingrediente_receta.ingrediente
                cantidad = ingrediente_receta.cantidad
                
                # Crear detalle de producción
                detalle = ProduccionDetalle(
                    produccion_id=produccion.idProduccion,
                    ingrediente_id=ingrediente.idIngrediente,
                    cantidad_requerida=cantidad,
                    cantidad_usada=cantidad,
                    estado=1  # 1 = Usado
                )
                db.session.add(detalle)
                
                # Consumir ingrediente del inventario
                IngredienteController.actualizar_stock(
                    ingrediente_id=ingrediente.idIngrediente,
                    cantidad=cantidad,
                    tipo_movimiento=1  # 1 = Consumo
                )
            
            db.session.commit()
            return produccion, None
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def finalizar_produccion(produccion_id, cantidad_producida):
        """Finalizar una producción"""
        try:
            produccion = Produccion.query.get(produccion_id)
            
            if not produccion:
                return False, "Producción no encontrada"
            
            if produccion.estado_produccion == 2:
                return False, "Esta producción ya ha sido finalizada"
            
            # Actualizar estado y cantidad producida
            produccion.estado_produccion = 2  # 2 = Terminado
            produccion.cantidad_producida = cantidad_producida
            
            # Actualizar inventario de galletas producidas
            # Esta lógica puede variar según tu implementación de inventario
            
            db.session.commit()
            return True, "Producción finalizada exitosamente"
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def cancelar_produccion(produccion_id):
        """Cancelar una producción y devolver ingredientes si ya fueron consumidos"""
        try:
            produccion = Produccion.query.get(produccion_id)
            
            if not produccion:
                return False, "Producción no encontrada"
            
            if produccion.estado_produccion == 2:
                return False, "No se puede cancelar una producción ya finalizada"
            
            # Si la producción está en proceso (ingredientes ya consumidos), devolverlos al inventario
            if produccion.estado_produccion == 1:
                for detalle in produccion.detalles:
                    if detalle.estado == 1:  # Ingrediente ya usado
                        # Devolver ingrediente al inventario
                        IngredienteController.actualizar_stock(
                            ingrediente_id=detalle.ingrediente_id,
                            cantidad=detalle.cantidad_usada,
                            tipo_movimiento=0  # 0 = Reabastecimiento
                        )
            
            # Marcar producción como cancelada
            produccion.estado_produccion = 3  # 3 = Cancelado
            
            db.session.commit()
            return True, "Producción cancelada exitosamente"
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def verificar_ingredientes_para_receta(receta_id):
        """Verificar si hay suficientes ingredientes para una receta"""
        receta = RecetaController.get_receta_by_id(receta_id)
        
        if not receta:
            return False, "Receta no encontrada", None
        
        suficientes_ingredientes = True
        ingredientes_faltantes = []
        
        for ingrediente_receta in receta.ingredientes:
            ingrediente = ingrediente_receta.ingrediente
            cantidad_necesaria = ingrediente_receta.cantidad
            
            if ingrediente.stock < cantidad_necesaria:
                suficientes_ingredientes = False
                ingredientes_faltantes.append({
                    'nombre': ingrediente.nombreIngrediente,
                    'disponible': ingrediente.stock,
                    'necesario': cantidad_necesaria,
                    'faltante': cantidad_necesaria - ingrediente.stock
                })
        
        return suficientes_ingredientes, None if suficientes_ingredientes else "Ingredientes insuficientes", ingredientes_faltantes