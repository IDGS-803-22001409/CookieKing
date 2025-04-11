from models import db
from modulos.ingredientes.models import Ingrediente, MovimientoInsumo
from datetime import datetime

class IngredienteController:
    """Controlador para la lógica de negocio relacionada con ingredientes"""
    
    @staticmethod
    def get_all_ingredientes():
        """Obtener todos los ingredientes"""
        return Ingrediente.query.all()
    
    @staticmethod
    def get_ingrediente_by_id(ingrediente_id):
        """Obtener un ingrediente por su ID"""
        return Ingrediente.query.get(ingrediente_id)
    
    @staticmethod
    def get_ingredientes_by_stock_minimo():
        """Obtener ingredientes por debajo del stock mínimo"""
        return Ingrediente.query.filter(Ingrediente.stock < Ingrediente.stock_minimo).all()
    
    @staticmethod
    def create_ingrediente(data):
        """Crear un nuevo ingrediente con los datos proporcionados"""
        try:
            # Procesar la fecha de expiración si se proporciona
            fecha_expiracion = None
            if data.get('fecha_expiracion'):
                fecha_expiracion = datetime.strptime(data.get('fecha_expiracion'), '%Y-%m-%d').date()
            
            ingrediente = Ingrediente(
                nombreIngrediente=data.get('nombreIngrediente'),
                stock=float(data.get('stock', 0)),  # Esto ya acepta 0
                unidad=data.get('unidad', ''),
                stock_minimo=float(data.get('stock_minimo', 0)),
                precio_unitario=float(data.get('precio_unitario', 0)),
                fecha_expiracion=fecha_expiracion
            )
            
            db.session.add(ingrediente)
            db.session.commit()
            return ingrediente
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def update_ingrediente(ingrediente_id, data):
        """Actualizar un ingrediente existente"""
        ingrediente = Ingrediente.query.get(ingrediente_id)
        
        if not ingrediente:
            return None
        
        try:
            ingrediente.nombreIngrediente = data.get('nombreIngrediente', ingrediente.nombreIngrediente)
            
            if 'stock' in data:
                ingrediente.stock = float(data['stock'])
            
            if 'unidad' in data:
                ingrediente.unidad = data['unidad']
            
            if 'stock_minimo' in data:
                ingrediente.stock_minimo = float(data['stock_minimo'])
                
            if 'precio_unitario' in data:
                ingrediente.precio_unitario = float(data['precio_unitario'])
            
            if 'fecha_expiracion' in data and data['fecha_expiracion']:
                ingrediente.fecha_expiracion = datetime.strptime(data['fecha_expiracion'], '%Y-%m-%d').date()
            
            db.session.commit()
            return ingrediente
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def delete_ingrediente(ingrediente_id):
        """Eliminar un ingrediente si no tiene dependencias"""
        ingrediente = Ingrediente.query.get(ingrediente_id)
        
        if not ingrediente:
            return False
        
        # Verificar si hay relaciones que impidan eliminarlo
        if len(ingrediente.movimientos) > 0:
            return False
        
        try:
            db.session.delete(ingrediente)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False
    
    @staticmethod
    def actualizar_stock(ingrediente_id, cantidad, tipo_movimiento, referencia=None, fecha_expiracion=None):
        """
        Actualizar el stock de un ingrediente
        
        Args:
            ingrediente_id: ID del ingrediente
            cantidad: Cantidad a agregar/restar
            tipo_movimiento: 0 = Reabastecimiento (sumar), 1 = Consumo (restar)
            referencia: Información adicional sobre el movimiento (opcional)
            fecha_expiracion: Fecha de expiración del ingrediente (opcional, solo para reabastecimiento)
        """
        ingrediente = Ingrediente.query.get(ingrediente_id)
        
        if not ingrediente:
            return False
        
        try:
            if tipo_movimiento == 1:  # Consumo
                if ingrediente.stock < cantidad:
                    return False  # No hay suficiente stock
                ingrediente.stock -= cantidad
            else:  # Reabastecimiento
                ingrediente.stock += cantidad
                # Actualizar fecha de expiración si se proporciona
                if fecha_expiracion:
                    ingrediente.fecha_expiracion = fecha_expiracion
            
            # Registrar el movimiento
            movimiento = MovimientoInsumo(
                ingrediente_id=ingrediente_id,
                tipo_movimiento=tipo_movimiento,
                cantidad=cantidad,
                fecha_movimiento=datetime.now().date(),
                referencia=referencia
            )
            
            db.session.add(movimiento)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False
    @staticmethod
    def get_movimientos_by_ingrediente(ingrediente_id):
        """Obtener todos los movimientos de un ingrediente específico"""
        return MovimientoInsumo.query.filter_by(ingrediente_id=ingrediente_id).order_by(
            MovimientoInsumo.fecha_movimiento.desc()).all()
    

    @staticmethod
    def registrar_merma(ingrediente_id, cantidad, motivo, unidad_ingresada=None):
        """
        Registrar una merma de ingrediente con posible conversión de unidades
        
        Args:
            ingrediente_id: ID del ingrediente
            cantidad: Cantidad perdida
            motivo: Motivo de la merma (caducidad, accidente, etc.)
            unidad_ingresada: Unidad en la que se ingresó la cantidad (opcional)
        """
        ingrediente = Ingrediente.query.get(ingrediente_id)
        
        if not ingrediente:
            return False
        
        try:
            # Convertir la cantidad si es necesario
            cantidad_convertida = cantidad
            
            if unidad_ingresada and unidad_ingresada != ingrediente.unidad:
                # Conversiones de kg a g y viceversa
                if ingrediente.unidad == 'kg' and unidad_ingresada == 'g':
                    cantidad_convertida = cantidad / 1000
                elif ingrediente.unidad == 'g' and unidad_ingresada == 'kg':
                    cantidad_convertida = cantidad * 1000
                # Conversiones de l a ml y viceversa
                elif ingrediente.unidad == 'l' and unidad_ingresada == 'ml':
                    cantidad_convertida = cantidad / 1000
                elif ingrediente.unidad == 'ml' and unidad_ingresada == 'l':
                    cantidad_convertida = cantidad * 1000
            
            # Verificar que haya suficiente stock
            if ingrediente.stock < cantidad_convertida:
                return False
            
            # Reducir el stock
            ingrediente.stock -= cantidad_convertida
            
            # Incluir la información de la unidad en la referencia si es diferente
            referencia_detallada = motivo
            if unidad_ingresada and unidad_ingresada != ingrediente.unidad:
                referencia_detallada = f"Merma: {cantidad} {unidad_ingresada} ({cantidad_convertida} {ingrediente.unidad}) - {motivo}"
            else:
                referencia_detallada = f"Merma: {motivo}"
            
            # Registrar el movimiento como un tipo especial (2 = Merma)
            movimiento = MovimientoInsumo(
                ingrediente_id=ingrediente_id,
                tipo_movimiento=2,  # 2 para merma
                cantidad=cantidad_convertida,
                fecha_movimiento=datetime.now().date(),
                referencia=referencia_detallada
            )
            
            db.session.add(movimiento)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False