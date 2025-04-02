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
                stock=float(data.get('stock', 0)),
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
        # (Asumimos que necesitarás verificar otras relaciones en el futuro)
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
    def actualizar_stock(ingrediente_id, cantidad, tipo_movimiento, referencia=None):
        """
        Actualizar el stock de un ingrediente
        tipo_movimiento: 1 = Consumo (restar), 0 = Reabastecimiento (sumar)
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