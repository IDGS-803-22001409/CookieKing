# modulos/clientes/controllers.py
from models import db
from modulos.clientes.models import Cliente
from datetime import datetime

class ClienteController:
    """Controlador para la lógica de negocio relacionada con clientes"""
    
    @staticmethod
    def get_all_clientes():
        """Obtener todos los clientes"""
        return Cliente.query.all()
    
    @staticmethod
    def get_active_clientes():
        """Obtener solo clientes activos"""
        return Cliente.query.filter_by(estatus=1).all()
    
    @staticmethod
    def get_cliente_by_id(cliente_id):
        """Obtener un cliente por su ID"""
        return Cliente.query.get(cliente_id)
    
    @staticmethod
    def create_cliente(data):
        """Crear un nuevo cliente con los datos proporcionados"""
        try:
            # Procesar la fecha de nacimiento si se proporciona
            fecha_nacimiento = None
            if data.get('fechaNacimiento'):
                fecha_nacimiento = datetime.strptime(data.get('fechaNacimiento'), '%Y-%m-%d').date()
            
            cliente = Cliente(
                nombreCliente=data.get('nombreCliente'),
                fechaNacimiento=fecha_nacimiento,
                telefono=data.get('telefono', ''),
                correo=data.get('correo', ''),
                estatus=int(data.get('estatus', 1))
            )
            
            db.session.add(cliente)
            db.session.commit()
            return cliente
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def update_cliente(cliente_id, data):
        """Actualizar un cliente existente"""
        cliente = Cliente.query.get(cliente_id)
        
        if not cliente:
            return None
        
        try:
            cliente.nombreCliente = data.get('nombreCliente', cliente.nombreCliente)
            
            # Procesar la fecha de nacimiento si se proporciona
            if 'fechaNacimiento' in data and data['fechaNacimiento']:
                cliente.fechaNacimiento = datetime.strptime(data['fechaNacimiento'], '%Y-%m-%d').date()
            
            cliente.telefono = data.get('telefono', cliente.telefono)
            cliente.correo = data.get('correo', cliente.correo)
            
            if 'estatus' in data:
                cliente.estatus = int(data['estatus'])
            
            db.session.commit()
            return cliente
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def delete_cliente(cliente_id):
        """Eliminar un cliente si no tiene dependencias"""
        cliente = Cliente.query.get(cliente_id)
        
        if not cliente:
            return False
        
        # Verificar si hay ventas asociadas
        if cliente.ventas and len(cliente.ventas) > 0:
            # En lugar de eliminar, marcar como inactivo
            cliente.estatus = 0
            db.session.commit()
            return True
        
        # Si no hay dependencias, eliminar físicamente
        db.session.delete(cliente)
        db.session.commit()
        return True
    
    @staticmethod
    def can_delete_cliente(cliente_id):
        """Verificar si un cliente puede ser eliminado (no tiene dependencias)"""
        cliente = Cliente.query.get(cliente_id)
        
        if not cliente:
            return False
        
        # Verificar si hay ventas asociadas
        if cliente.ventas and len(cliente.ventas) > 0:
            return False
        
        return True