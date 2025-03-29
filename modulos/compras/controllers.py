# modulos/compras/controllers.py
from models import db
from modulos.compras.models import CompraInsumo, CompraDetalle
from modulos.ingredientes.controllers import IngredienteController
from datetime import datetime

class CompraController:
    """Controlador para la lógica de negocio relacionada con compras de insumos"""
    
    @staticmethod
    def get_all_compras():
        """Obtener todas las compras"""
        return CompraInsumo.query.order_by(CompraInsumo.fecha.desc()).all()
    
    @staticmethod
    def get_compras_by_proveedor(proveedor_id):
        """Obtener compras por proveedor"""
        return CompraInsumo.query.filter_by(idProveedor=proveedor_id).order_by(CompraInsumo.fecha.desc()).all()
    
    @staticmethod
    def get_compra_by_id(compra_id):
        """Obtener una compra por su ID"""
        return CompraInsumo.query.get(compra_id)
    
    # modulos/compras/controllers.py (continuación)
    @staticmethod
    def create_compra(data, detalles_data):
        """
        Crear una nueva compra con sus detalles
        
        Args:
            data: Diccionario con datos de la compra
            detalles_data: Lista de diccionarios con detalles de la compra
        """
        try:
            # Convertir la fecha si viene como string
            if isinstance(data.get('fecha'), str):
                fecha = datetime.strptime(data.get('fecha'), '%Y-%m-%d').date()
            else:
                fecha = data.get('fecha', datetime.now().date())
                
            # Crear la compra
            compra = CompraInsumo(
                fecha=fecha,
                idProveedor=data.get('idProveedor'),
                total=data.get('total', 0.0),
                estatus=int(data.get('estatus', 1)),
                numero_factura=data.get('numero_factura', '')
            )
            
            db.session.add(compra)
            db.session.flush()  # Para obtener el ID generado para la compra
            
            # Crear los detalles
            total_compra = 0.0
            for detalle_data in detalles_data:
                cantidad = float(detalle_data.get('cantidad', 0))
                precio_unitario = float(detalle_data.get('precio_unitario', 0))
                subtotal = cantidad * precio_unitario
                total_compra += subtotal
                
                detalle = CompraDetalle(
                    idCompra=compra.idCompra,
                    idIngrediente=detalle_data.get('idIngrediente'),
                    cantidad=cantidad,
                    precio_unitario=precio_unitario,
                    subtotal=subtotal
                )
                
                db.session.add(detalle)
                
                # Actualizar el stock del ingrediente
                IngredienteController.actualizar_stock(
                    ingrediente_id=detalle_data.get('idIngrediente'),
                    cantidad=cantidad,
                    tipo_movimiento=0  # 0 = Reabastecimiento
                )
            
            # Actualizar el total de la compra
            compra.total = total_compra
            
            db.session.commit()
            return compra
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def update_compra(compra_id, data, detalles_data=None):
        """
        Actualizar una compra existente y opcionalmente sus detalles
        
        Args:
            compra_id: ID de la compra a actualizar
            data: Diccionario con datos de la compra
            detalles_data: Lista de diccionarios con detalles de la compra (opcional)
        """
        try:
            compra = CompraInsumo.query.get(compra_id)
            
            if not compra:
                return None
            
            # Actualizar datos de la compra
            if 'fecha' in data:
                if isinstance(data['fecha'], str):
                    compra.fecha = datetime.strptime(data['fecha'], '%Y-%m-%d').date()
                else:
                    compra.fecha = data['fecha']
            
            if 'idProveedor' in data:
                compra.idProveedor = data['idProveedor']
            
            if 'estatus' in data:
                compra.estatus = int(data['estatus'])
            
            if 'numero_factura' in data:
                compra.numero_factura = data['numero_factura']
            
            # Si se proporcionan detalles nuevos, recrear los detalles
            if detalles_data is not None:
                # Primero, revertir los movimientos de stock de los detalles antiguos
                for detalle in compra.detalles:
                    IngredienteController.actualizar_stock(
                        ingrediente_id=detalle.idIngrediente,
                        cantidad=detalle.cantidad,
                        tipo_movimiento=1  # 1 = Consumo (para revertir el ingreso)
                    )
                
                # Eliminar los detalles antiguos
                for detalle in compra.detalles:
                    db.session.delete(detalle)
                
                # Crear los nuevos detalles
                total_compra = 0.0
                for detalle_data in detalles_data:
                    cantidad = float(detalle_data.get('cantidad', 0))
                    precio_unitario = float(detalle_data.get('precio_unitario', 0))
                    subtotal = cantidad * precio_unitario
                    total_compra += subtotal
                    
                    detalle = CompraDetalle(
                        idCompra=compra.idCompra,
                        idIngrediente=detalle_data.get('idIngrediente'),
                        cantidad=cantidad,
                        precio_unitario=precio_unitario,
                        subtotal=subtotal
                    )
                    
                    db.session.add(detalle)
                    
                    # Actualizar el stock del ingrediente
                    IngredienteController.actualizar_stock(
                        ingrediente_id=detalle_data.get('idIngrediente'),
                        cantidad=cantidad,
                        tipo_movimiento=0  # 0 = Reabastecimiento
                    )
                
                # Actualizar el total de la compra
                compra.total = total_compra
            
            db.session.commit()
            return compra
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def delete_compra(compra_id):
        """Eliminar una compra y sus detalles"""
        try:
            compra = CompraInsumo.query.get(compra_id)
            
            if not compra:
                return False
            
            # Revertir los movimientos de stock
            for detalle in compra.detalles:
                IngredienteController.actualizar_stock(
                    ingrediente_id=detalle.idIngrediente,
                    cantidad=detalle.cantidad,
                    tipo_movimiento=1  # 1 = Consumo (para revertir el ingreso)
                )
            
            # Eliminar la compra (los detalles se eliminarán automáticamente por el cascade)
            db.session.delete(compra)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False
    
    @staticmethod
    def get_detalles_compra(compra_id):
        """Obtener los detalles de una compra"""
        return CompraDetalle.query.filter_by(idCompra=compra_id).all()