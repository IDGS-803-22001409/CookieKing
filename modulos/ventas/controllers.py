# modulos/ventas/controllers.py
from models import db
from modulos.ventas.models import Venta, DetalleVenta
from modulos.galletas.controllers import GalletaController
from datetime import datetime

class VentaController:
    """Controlador para la lógica de negocio relacionada con ventas"""
    
    @staticmethod
    def get_all_ventas():
        """Obtener todas las ventas"""
        return Venta.query.order_by(Venta.fechaVenta.desc()).all()
    
    @staticmethod
    def get_ventas_by_cliente(cliente_id):
        """Obtener ventas por cliente"""
        return Venta.query.filter_by(IdCliente=cliente_id).order_by(Venta.fechaVenta.desc()).all()
    
    @staticmethod
    def get_venta_by_id(venta_id):
        """Obtener una venta por su ID"""
        return Venta.query.get(venta_id)
    
    @staticmethod
    def get_ventas_by_fecha(fecha_inicio, fecha_fin):
        """Obtener ventas en un rango de fechas"""
        return Venta.query.filter(Venta.fechaVenta >= fecha_inicio, Venta.fechaVenta <= fecha_fin).order_by(Venta.fechaVenta.desc()).all()
    
    @staticmethod
    def create_venta(data, detalles_data):
        """
        Crear una nueva venta con sus detalles
        
        Args:
            data: Diccionario con datos de la venta
            detalles_data: Lista de diccionarios con detalles de la venta
        """
        try:
            # Convertir la fecha si viene como string
            if isinstance(data.get('fechaVenta'), str):
                fecha_venta = datetime.strptime(data.get('fechaVenta'), '%Y-%m-%d').date()
            else:
                fecha_venta = data.get('fechaVenta', datetime.now().date())
                
            # Crear la venta
            venta = Venta(
                fechaVenta=fecha_venta,
                IdCliente=data.get('IdCliente'),
                estatus=int(data.get('estatus', 1))
            )
            
            db.session.add(venta)
            db.session.flush()  # Para obtener el ID generado para la venta
            
            # Crear los detalles
            for detalle_data in detalles_data:
                detalle = DetalleVenta(
                    venta_id=venta.idVenta,
                    galleta_id=detalle_data.get('galleta_id'),
                    cantidad=int(detalle_data.get('cantidad', 0)),
                    tipo_venta=int(detalle_data.get('tipo_venta', 1))  # 1 = Individual, 0 = Paquete
                )
                
                db.session.add(detalle)
            
            db.session.commit()
            return venta
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def update_venta(venta_id, data, detalles_data=None):
        """
        Actualizar una venta existente y opcionalmente sus detalles
        
        Args:
            venta_id: ID de la venta a actualizar
            data: Diccionario con datos de la venta
            detalles_data: Lista de diccionarios con detalles de la venta (opcional)
        """
        try:
            venta = Venta.query.get(venta_id)
            
            if not venta:
                return None
            
            # Actualizar datos de la venta
            if 'fechaVenta' in data:
                if isinstance(data['fechaVenta'], str):
                    venta.fechaVenta = datetime.strptime(data['fechaVenta'], '%Y-%m-%d').date()
                else:
                    venta.fechaVenta = data['fechaVenta']
            
            if 'IdCliente' in data:
                venta.IdCliente = data['IdCliente']
            
            if 'estatus' in data:
                venta.estatus = int(data['estatus'])
            
            # Si se proporcionan detalles nuevos, recrear los detalles
            if detalles_data is not None:
                # Eliminar los detalles antiguos
                for detalle in venta.detalles:
                    db.session.delete(detalle)
                
                # Crear los nuevos detalles
                for detalle_data in detalles_data:
                    detalle = DetalleVenta(
                        venta_id=venta.idVenta,
                        galleta_id=detalle_data.get('galleta_id'),
                        cantidad=int(detalle_data.get('cantidad', 0)),
                        tipo_venta=int(detalle_data.get('tipo_venta', 1))  # 1 = Individual, 0 = Paquete
                    )
                    
                    db.session.add(detalle)
            
            db.session.commit()
            return venta
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def delete_venta(venta_id):
        """Eliminar una venta y sus detalles"""
        try:
            venta = Venta.query.get(venta_id)
            
            if not venta:
                return False
            
            # Eliminar la venta (los detalles se eliminarán automáticamente por el cascade)
            db.session.delete(venta)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False
    
    @staticmethod
    def get_detalles_venta(venta_id):
        """Obtener los detalles de una venta"""
        return DetalleVenta.query.filter_by(venta_id=venta_id).all()
    
    @staticmethod
    def generar_ticket(venta_id):
        """Generar un ticket para una venta"""
        venta = Venta.query.get(venta_id)
        
        if not venta:
            return None
        
        detalles = DetalleVenta.query.filter_by(venta_id=venta_id).all()
        
        # Calcular total
        total = 0
        for detalle in detalles:
            if detalle.tipo_venta == 1:  # Individual
                precio = detalle.galleta.precio_unitario
            else:  # Paquete (asumiendo que el precio de paquete es diferente)
                precio = detalle.galleta.precio_unitario * 0.9  # 10% de descuento por paquete, ejemplo
            
            total += precio * detalle.cantidad
        
        # modulos/ventas/controllers.py (continuación)
        # Preparar datos del ticket
        ticket_data = {
            'venta_id': venta.idVenta,
            'fecha': venta.fechaVenta.strftime('%d/%m/%Y'),
            'hora': datetime.now().strftime('%H:%M:%S'),
            'cliente': venta.cliente.nombreCliente if venta.cliente else "Cliente General",
            'detalles': [],
            'total': total
        }
        
        for detalle in detalles:
            if detalle.tipo_venta == 1:  # Individual
                tipo = "Individual"
                precio = detalle.galleta.precio_unitario
            else:  # Paquete
                tipo = "Paquete"
                precio = detalle.galleta.precio_unitario * 0.9  # 10% de descuento por paquete, ejemplo
                
            subtotal = precio * detalle.cantidad
            
            ticket_data['detalles'].append({
                'galleta': detalle.galleta.nombreGalleta,
                'cantidad': detalle.cantidad,
                'tipo': tipo,
                'precio_unitario': precio,
                'subtotal': subtotal
            })
        
        return ticket_data
    
    @staticmethod
    def get_ventas_diarias(fecha=None):
        """Obtener ventas de un día específico o del día actual"""
        if fecha is None:
            fecha = datetime.now().date()
        elif isinstance(fecha, str):
            fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
        
        ventas = Venta.query.filter(Venta.fechaVenta == fecha).all()
        
        # Calcular total de ventas
        total_ventas = 0
        num_ventas = len(ventas)
        
        for venta in ventas:
            for detalle in venta.detalles:
                if detalle.tipo_venta == 1:  # Individual
                    precio = detalle.galleta.precio_unitario
                else:  # Paquete
                    precio = detalle.galleta.precio_unitario * 0.9  # Ejemplo
                
                total_ventas += precio * detalle.cantidad
        
        return {
            'fecha': fecha.strftime('%d/%m/%Y'),
            'num_ventas': num_ventas,
            'total_ventas': total_ventas,
            'ventas': ventas
        }
    
    @staticmethod
    def get_productos_mas_vendidos(fecha_inicio=None, fecha_fin=None, limit=10):
        """Obtener los productos más vendidos en un rango de fechas"""
        if fecha_inicio is None:
            fecha_inicio = datetime.now().replace(day=1).date()  # Primer día del mes actual
        elif isinstance(fecha_inicio, str):
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            
        if fecha_fin is None:
            fecha_fin = datetime.now().date()
        elif isinstance(fecha_fin, str):
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        
        # Consulta para obtener los productos más vendidos
        resultados = db.session.query(
            DetalleVenta.galleta_id,
            db.func.sum(DetalleVenta.cantidad).label('total_cantidad')
        ).join(Venta).filter(
            Venta.fechaVenta >= fecha_inicio,
            Venta.fechaVenta <= fecha_fin,
            Venta.estatus == 1  # Solo ventas completadas
        ).group_by(
            DetalleVenta.galleta_id
        ).order_by(
            db.desc('total_cantidad')
        ).limit(limit).all()
        
        # Obtener información de cada galleta
        productos = []
        for galleta_id, total_cantidad in resultados:
            galleta = GalletaController.get_galleta_by_id(galleta_id)
            if galleta:
                productos.append({
                    'id': galleta.idGalleta,
                    'nombre': galleta.nombreGalleta,
                    'cantidad_vendida': total_cantidad,
                    'precio_unitario': galleta.precio_unitario,
                    'valor_total': total_cantidad * galleta.precio_unitario
                })
        
        return productos