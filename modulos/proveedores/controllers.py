# modulos/proveedores/controllers.py
from models import db
from modulos.proveedores.models import Proveedor

class ProveedorController:
    """Controlador para la lógica de negocio relacionada con proveedores"""
    
    @staticmethod
    def get_all_proveedores():
        """Obtener todos los proveedores"""
        return Proveedor.query.all()
    
    @staticmethod
    def get_active_proveedores():
        """Obtener solo proveedores activos"""
        return Proveedor.query.filter_by(estatus=1).all()
    
    @staticmethod
    def get_proveedor_by_id(proveedor_id):
        """Obtener un proveedor por su ID"""
        return Proveedor.query.get(proveedor_id)
    
    @staticmethod
    def create_proveedor(data):
        """Crear un nuevo proveedor con los datos proporcionados"""
        proveedor = Proveedor(
            nombre_proveedor=data.get('nombre_proveedor'),
            telefono=data.get('telefono', ''),
            correo=data.get('correo', ''),
            direccion=data.get('direccion', ''),
            rfc=data.get('rfc', ''),
            estatus=int(data.get('estatus', 1))
        )
        
        db.session.add(proveedor)
        db.session.commit()
        return proveedor
    
    @staticmethod
    def update_proveedor(proveedor_id, data):
        """Actualizar un proveedor existente"""
        proveedor = Proveedor.query.get(proveedor_id)
        
        if not proveedor:
            return None
        
        proveedor.nombre_proveedor = data.get('nombre_proveedor', proveedor.nombre_proveedor)
        proveedor.telefono = data.get('telefono', proveedor.telefono)
        proveedor.correo = data.get('correo', proveedor.correo)
        proveedor.direccion = data.get('direccion', proveedor.direccion)
        proveedor.rfc = data.get('rfc', proveedor.rfc)
        
        if 'estatus' in data:
            proveedor.estatus = int(data['estatus'])
        
        db.session.commit()
        return proveedor
    
    @staticmethod
    def delete_proveedor(proveedor_id):
        """Eliminar un proveedor si no tiene dependencias"""
        proveedor = Proveedor.query.get(proveedor_id)
        
        if not proveedor:
            return False
        
        # Verificar si hay compras asociadas
        if proveedor.compras and len(proveedor.compras) > 0:
            # En lugar de eliminar, marcar como inactivo
            proveedor.estatus = 0
            db.session.commit()
            return True
        
        # Si no hay dependencias, eliminar físicamente
        db.session.delete(proveedor)
        db.session.commit()
        return True
    
    @staticmethod
    def can_delete_proveedor(proveedor_id):
        """Verificar si un proveedor puede ser eliminado (no tiene dependencias)"""
        proveedor = Proveedor.query.get(proveedor_id)
        
        if not proveedor:
            return False
        
        # Verificar si hay compras asociadas
        if proveedor.compras and len(proveedor.compras) > 0:
            return False
        
        return True