from models import db
from modulos.ventas.models import Venta, DetalleVenta, PagoProveedor, PedidoCliente, DetallePedido
from modulos.galletas.models import Galletas
from modulos.clientes.models import Cliente
from modulos.proveedores.models import Proveedor
from datetime import datetime, timedelta
import json

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
        return Venta.query.filter(
            Venta.fechaVenta >= fecha_inicio,
            Venta.fechaVenta <= fecha_fin
        ).order_by(Venta.fechaVenta.desc()).all()
    
    @staticmethod
    def verificar_stock(detalles_data):
        """
        Verificar si hay suficiente stock para todos los productos de una venta,
        considerando el stock combinado (paquetes + unidades individuales)
        """
        # Crear un diccionario para sumar unidades por galleta
        unidades_por_galleta = {}
        
        # Primera pasada: sumar todas las unidades necesarias por galleta
        for detalle_data in detalles_data:
            galleta_id = detalle_data.get('galleta_id')
            cantidad = int(detalle_data.get('cantidad', 0))
            tipo_venta = int(detalle_data.get('tipo_venta', 1))  # 1 = Individual, 0 = Paquete
            
            # Calcular unidades reales según tipo de venta
            unidades_reales = cantidad
            if tipo_venta == 0:  # Paquete (5 unidades)
                unidades_reales = cantidad * 5
            
            # Sumar al total de esta galleta
            if galleta_id not in unidades_por_galleta:
                unidades_por_galleta[galleta_id] = 0
            unidades_por_galleta[galleta_id] += unidades_reales
        
        # Segunda pasada: verificar stock disponible para cada galleta
        for galleta_id, unidades_necesarias in unidades_por_galleta.items():
            galleta = Galletas.query.get(galleta_id)
            if not galleta:
                return False, f"Producto con ID {galleta_id} no encontrado"
            
            if galleta.existencias < unidades_necesarias:
                return False, f"Stock insuficiente para {galleta.nombreGalleta}. Disponible: {galleta.existencias}, Solicitado: {unidades_necesarias}"
        
        return True, "Stock suficiente para la venta"
    
    @staticmethod
    def actualizar_stock(detalles_data, aumentar=False, accion='venta'):
        """
        Actualizar el stock de galletas con validaciones avanzadas.

        Args:
            detalles_data: Lista de diccionarios con detalles de venta.
            aumentar: Si es True, aumenta el stock.
            accion: Tipo de acción ('venta', 'cancelacion').

        Returns:
            tuple: (bool, str) - Estado de la operación y mensaje.
        """
        try:
            # Validación de stock antes de cualquier cambio.
            if not aumentar:
                for detalle_data in detalles_data:
                    galleta_id = detalle_data.get('galleta_id')
                    cantidad = int(detalle_data.get('cantidad', 0))
                    tipo_venta = int(detalle_data.get('tipo_venta', 1))

                    # Calcular unidades reales.
                    unidades_reales = cantidad * 5 if tipo_venta == 0 else cantidad

                    galleta = Galletas.query.get(galleta_id)

                    if not galleta:
                        return False, f"Producto con ID {galleta_id} no encontrado"

                    if galleta.existencias < unidades_reales:
                        return False, (
                            f"Stock insuficiente para {galleta.nombreGalleta}. "
                            f"Disponible: {galleta.existencias}, Solicitado: {unidades_reales}"
                        )

            # Actualización de stock.
            for detalle_data in detalles_data:
                galleta_id = detalle_data.get('galleta_id')
                cantidad = int(detalle_data.get('cantidad', 0))
                tipo_venta = int(detalle_data.get('tipo_venta', 1))

                # Calcular unidades reales.
                unidades_reales = cantidad * 5 if tipo_venta == 0 else cantidad

                galleta = Galletas.query.get(galleta_id)

                if galleta:
                    if aumentar:
                        # Aumentar stock (devolución o cancelación).
                        galleta.existencias += unidades_reales
                    else:
                        # Reducir stock (venta).
                        galleta.existencias = max(0, galleta.existencias - unidades_reales)

                    # Log o notificación de stock bajo.
                    if galleta.existencias <= 5:
                        print(
                            f"ALERTA: Stock bajo para {galleta.nombreGalleta}. "
                            f"Quedan {galleta.existencias} unidades."
                        )

            return True, f"Stock {'aumentado' if aumentar else 'reducido'} correctamente"

        except Exception as e:
            print(f"Error al actualizar stock: {str(e)}")
            return False, f"Error al actualizar stock: {str(e)}"
                                                                     
    
    @staticmethod
    def create_venta(data, detalles_data):
        """Crear una nueva venta con validación de stock"""
        try:
            # Verificar stock disponible antes de crear la venta
            stock_suficiente, mensaje = VentaController.verificar_stock(detalles_data)
            if not stock_suficiente:
                raise ValueError(mensaje)            
            
            # Crear la venta
            venta = Venta(
                fechaVenta=datetime.now(),
                IdCliente=data.get('IdCliente'),
                estatus=int(data.get('estatus', 1))
            )
            
            db.session.add(venta)
            db.session.flush()
            
            # Calcular total y crear detalles
            total_venta = 0.0
            for detalle_data in detalles_data:
                galleta = Galletas.query.get(detalle_data.get('galleta_id'))
                if not galleta:
                    continue
                
                cantidad = int(detalle_data.get('cantidad', 0))
                tipo_venta = int(detalle_data.get('tipo_venta', 1))
                
                precio_unitario = galleta.precio_unitario
                if tipo_venta == 0:  # Paquete
                    precio_unitario *= 0.9 * 5
                
                subtotal = cantidad * precio_unitario
                total_venta += subtotal
                
                detalle = DetalleVenta(
                    venta_id=venta.idVenta,
                    galleta_id=detalle_data.get('galleta_id'),
                    cantidad=cantidad,
                    precio_unitario=precio_unitario,
                    subtotal=subtotal,
                    tipo_venta=tipo_venta
                )
                
                db.session.add(detalle)
            
            venta.total = total_venta
            
            # CORRECCIÓN: Actualizar el inventario reduciendo el stock
            if venta.estatus == 1:  # Si la venta está completada
                VentaController.actualizar_stock(detalles_data, aumentar=False)
            
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
            
            # Guardar estatus anterior para verificar cambios
            estatus_anterior = venta.estatus
            
            # Actualizar datos de la venta
            if 'IdCliente' in data:
                venta.IdCliente = data['IdCliente']
            
            if 'estatus' in data:
                venta.estatus = int(data['estatus'])
            
            # Si se proporcionan detalles nuevos, recrear los detalles
            if detalles_data is not None:
                # Obtener detalles actuales para devolver el stock
                detalles_actuales = DetalleVenta.query.filter_by(venta_id=venta_id).all()
                detalles_actuales_data = []
                
                for detalle in detalles_actuales:
                    detalles_actuales_data.append({
                        'galleta_id': detalle.galleta_id,
                        'cantidad': detalle.cantidad,
                        'tipo_venta': detalle.tipo_venta
                    })
                
                # Devolver el stock de los productos anteriores si la venta estaba completada
                if estatus_anterior == 1:
                    VentaController.actualizar_stock(detalles_actuales_data, aumentar=True)
                
                # Verificar stock disponible para los nuevos productos
                stock_suficiente, mensaje = VentaController.verificar_stock(detalles_data)
                if not stock_suficiente:
                    # Si no hay stock suficiente, volver a reducir el stock de los productos anteriores
                    # para mantener la consistencia (solo si la venta estaba completada)
                    if estatus_anterior == 1:
                        VentaController.actualizar_stock(detalles_actuales_data, aumentar=False)
                    raise ValueError(mensaje)
                
                # Eliminar los detalles antiguos
                for detalle in detalles_actuales:
                    db.session.delete(detalle)
                
                # Crear los nuevos detalles y recalcular el total
                total_venta = 0.0
                for detalle_data in detalles_data:
                    galleta = Galletas.query.get(detalle_data.get('galleta_id'))
                    if not galleta:
                        continue
                    
                    cantidad = int(detalle_data.get('cantidad', 0))
                    tipo_venta = int(detalle_data.get('tipo_venta', 1))  # 1 = Individual, 0 = Paquete
                    
                    # Calcular precio unitario (puede variar según tipo de venta)
                    precio_unitario = galleta.precio_unitario
                    if tipo_venta == 0:  # Paquete
                        precio_unitario = precio_unitario * 0.9 * 5  # 10% de descuento
                    
                    subtotal = cantidad * precio_unitario
                    total_venta += subtotal
                    
                    detalle = DetalleVenta(
                        venta_id=venta.idVenta,
                        galleta_id=detalle_data.get('galleta_id'),
                        cantidad=cantidad,
                        precio_unitario=precio_unitario,
                        subtotal=subtotal,
                        tipo_venta=tipo_venta
                    )
                    
                    db.session.add(detalle)
                
                # Reducir el stock de los nuevos productos si la venta está completada
                if venta.estatus == 1:
                    VentaController.actualizar_stock(detalles_data, aumentar=False)
                
                # Actualizar el total de la venta
                venta.total = total_venta
            else:
                # Si no hay nuevos detalles pero cambió el estatus, actualizar el stock
                if estatus_anterior != venta.estatus:
                    detalles = DetalleVenta.query.filter_by(venta_id=venta_id).all()
                    detalles_data = []
                    
                    for detalle in detalles:
                        detalles_data.append({
                            'galleta_id': detalle.galleta_id,
                            'cantidad': detalle.cantidad,
                            'tipo_venta': detalle.tipo_venta
                        })
                    
                    # Si cambia de completada a cancelada, devolver el stock
                    if estatus_anterior == 1 and venta.estatus == 2:
                        VentaController.actualizar_stock(detalles_data, aumentar=True)
                    
                    # Si cambia de cancelada a completada, reducir el stock
                    elif estatus_anterior == 2 and venta.estatus == 1:
                        # Verificar stock disponible
                        stock_suficiente, mensaje = VentaController.verificar_stock(detalles_data)
                        if not stock_suficiente:
                            # Revertir el cambio de estatus
                            venta.estatus = estatus_anterior
                            raise ValueError(mensaje)
                        
                        # Reducir inventario
                        VentaController.actualizar_stock(detalles_data, aumentar=False)
            
            db.session.commit()
            return venta
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def delete_venta(venta_id):
        """Eliminar una venta y devolver productos al inventario"""
        try:
            venta = Venta.query.get(venta_id)
            
            if not venta:
                return False
            
            # Obtener detalles para devolver el stock
            detalles = DetalleVenta.query.filter_by(venta_id=venta_id).all()
            detalles_data = []
            
            for detalle in detalles:
                detalles_data.append({
                    'galleta_id': detalle.galleta_id,
                    'cantidad': detalle.cantidad,
                    'tipo_venta': detalle.tipo_venta
                })
            
            # Devolver el stock de galletas al inventario solo si la venta estaba completada
            if venta.estatus == 1:
                VentaController.actualizar_stock(detalles_data, aumentar=True)
            
            # Eliminar la venta (los detalles se eliminarán automáticamente por el cascade)
            db.session.delete(venta)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False
    
    @staticmethod
    def cambiar_estatus_venta(venta_id, nuevo_estatus):
        """Cambiar el estatus de una venta y gestionar el stock e ingresos"""
        try:
            venta = Venta.query.get(venta_id)
            
            if not venta:
                return False, "Venta no encontrada"
            
            estatus_actual = venta.estatus
            
            # Si no hay cambio, no hacer nada
            if estatus_actual == nuevo_estatus:
                return True, "El estatus no ha cambiado"
            
            # Obtener detalles para manejar el inventario
            detalles = DetalleVenta.query.filter_by(venta_id=venta_id).all()
            detalles_data = []
            
            for detalle in detalles:
                detalles_data.append({
                    'galleta_id': detalle.galleta_id,
                    'cantidad': detalle.cantidad,
                    'tipo_venta': detalle.tipo_venta
                })
            
            # CORRECCIÓN: Si estamos cancelando una venta completada (devolver stock)
            if estatus_actual == 1 and nuevo_estatus == 2:
                # Devolver producto al inventario
                VentaController.actualizar_stock(detalles_data, aumentar=True)
            
            # Si estamos completando una venta cancelada (reducir stock)
            elif estatus_actual == 2 and nuevo_estatus == 1:
                # Verificar stock disponible
                stock_suficiente, mensaje = VentaController.verificar_stock(detalles_data)
                if not stock_suficiente:
                    return False, f"No se puede completar: {mensaje}"
                
                # Reducir inventario
                VentaController.actualizar_stock(detalles_data, aumentar=False)
            
            # Si estamos completando una venta pendiente (reducir stock)
            elif estatus_actual == 0 and nuevo_estatus == 1:
                # Verificar stock disponible
                stock_suficiente, mensaje = VentaController.verificar_stock(detalles_data)
                if not stock_suficiente:
                    return False, f"No se puede completar: {mensaje}"
                
                # Reducir inventario
                VentaController.actualizar_stock(detalles_data, aumentar=False)
            
            # Actualizar estatus
            venta.estatus = nuevo_estatus
            
            db.session.commit()
            
            estatus_texto = {
                0: "Pendiente",
                1: "Completada",
                2: "Cancelada"
            }
            
            return True, f"Venta actualizada a '{estatus_texto[nuevo_estatus]}'"
        except Exception as e:
            db.session.rollback()
            return False, str(e)
        
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
        
        # Preparar datos del ticket
        ticket_data = {
            'venta_id': venta.idVenta,
            'fecha': venta.fechaVenta.strftime('%d/%m/%Y'),
            'hora': venta.fechaVenta.strftime('%H:%M:%S'),
            'cliente': venta.cliente.nombreCliente if venta.cliente else "Cliente General",
            'detalles': [],
            'total': venta.total
        }
        
        for detalle in detalles:
            ticket_data['detalles'].append({
                'galleta': detalle.galleta.nombreGalleta,
                'cantidad': detalle.cantidad,
                'tipo': "Individual" if detalle.tipo_venta == 1 else "Paquete",
                'precio_unitario': detalle.precio_unitario,
                'subtotal': detalle.subtotal
            })
        
        return ticket_data
    
    @staticmethod
    def get_ventas_diarias(fecha=None):
        """Obtener ventas de un día específico o del día actual"""
        if fecha is None:
            fecha = datetime.now().date()
        elif isinstance(fecha, str):
            fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
        
        # Establecer hora de inicio y fin del día
        fecha_inicio = datetime.combine(fecha, datetime.min.time())
        fecha_fin = datetime.combine(fecha, datetime.max.time())
        
        ventas = Venta.query.filter(
            Venta.fechaVenta >= fecha_inicio,
            Venta.fechaVenta <= fecha_fin
        ).all()
        
        # Calcular totales
        total_ventas = sum(venta.total for venta in ventas)
        
        # Agrupar por cliente
        ventas_por_cliente = {}
        for venta in ventas:
            cliente_nombre = venta.cliente.nombreCliente if venta.cliente else "Cliente General"
            if cliente_nombre not in ventas_por_cliente:
                ventas_por_cliente[cliente_nombre] = {
                    'total': 0,
                    'ventas': []
                }
            ventas_por_cliente[cliente_nombre]['total'] += venta.total
            ventas_por_cliente[cliente_nombre]['ventas'].append(venta)
        
        return {
            'fecha': fecha.strftime('%d/%m/%Y'),
            'num_ventas': len(ventas),
            'total_ventas': total_ventas,
            'ventas': ventas,
            'ventas_por_cliente': ventas_por_cliente
        }
    
    @staticmethod
    def get_productos_mas_vendidos(fecha_inicio=None, fecha_fin=None, limit=10):
        """Obtener los productos más vendidos en un rango de fechas"""
        if fecha_inicio is None:
            fecha_inicio = datetime.now().replace(day=1)  # Primer día del mes actual
        elif isinstance(fecha_inicio, str):
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            
        if fecha_fin is None:
            fecha_fin = datetime.now()
        elif isinstance(fecha_fin, str):
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
            # Establecer la hora al final del día
            fecha_fin = datetime.combine(fecha_fin.date(), datetime.max.time())
        
        # Consulta para obtener los productos más vendidos
        resultados = db.session.query(
            DetalleVenta.galleta_id,
            db.func.sum(DetalleVenta.cantidad).label('total_cantidad'),
            db.func.sum(DetalleVenta.subtotal).label('total_ventas')
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
        for galleta_id, total_cantidad, total_ventas in resultados:
            galleta = Galletas.query.get(galleta_id)
            if galleta:
                productos.append({
                    'id': galleta.idGalleta,
                    'nombre': galleta.nombreGalleta,
                    'cantidad_vendida': int(total_cantidad),
                    'valor_total': float(total_ventas)
                })
        
        return productos
    
    @staticmethod
    def get_ventas_por_tipo(fecha_inicio=None, fecha_fin=None):
        """Obtener ventas agrupadas por tipo (Individual vs Paquete)"""
        if fecha_inicio is None:
            fecha_inicio = datetime.now().replace(day=1)  # Primer día del mes actual
        elif isinstance(fecha_inicio, str):
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            
        if fecha_fin is None:
            fecha_fin = datetime.now()
        elif isinstance(fecha_fin, str):
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
            # Establecer la hora al final del día
            fecha_fin = datetime.combine(fecha_fin.date(), datetime.max.time())
        
        # Consulta para obtener ventas por tipo
        resultados = db.session.query(
            DetalleVenta.tipo_venta,
            db.func.sum(DetalleVenta.cantidad).label('total_cantidad'),
            db.func.sum(DetalleVenta.subtotal).label('total_ventas'),
            db.func.count(DetalleVenta.id).label('num_ventas')
        ).join(Venta).filter(
            Venta.fechaVenta >= fecha_inicio,
            Venta.fechaVenta <= fecha_fin,
            Venta.estatus == 1  # Solo ventas completadas
        ).group_by(
            DetalleVenta.tipo_venta
        ).all()
        
        # Procesar resultados
        ventas_por_tipo = []
        for tipo_venta, total_cantidad, total_ventas, num_ventas in resultados:
            tipo_nombre = "Individual" if tipo_venta == 1 else "Paquete"
            ventas_por_tipo.append({
                'tipo': tipo_nombre,
                'total_cantidad': int(total_cantidad),
                'total_ventas': float(total_ventas),
                'num_ventas': int(num_ventas)
            })
        
        return ventas_por_tipo

class PagoProveedorController:
    """Controlador para la lógica de negocio relacionada con pagos a proveedores"""
    
    @staticmethod
    def get_all_pagos():
        """Obtener todos los pagos"""
        return PagoProveedor.query.order_by(PagoProveedor.fechaPago.desc()).all()
    
    @staticmethod
    def get_pagos_by_proveedor(proveedor_id):
        """Obtener pagos por proveedor"""
        return PagoProveedor.query.filter_by(idProveedor=proveedor_id).order_by(PagoProveedor.fechaPago.desc()).all()
    
    @staticmethod
    def get_pago_by_id(pago_id):
        """Obtener un pago por su ID"""
        return PagoProveedor.query.get(pago_id)
    
    @staticmethod
    def get_pagos_by_fecha(fecha_inicio, fecha_fin):
        """Obtener pagos en un rango de fechas"""
        return PagoProveedor.query.filter(
            PagoProveedor.fechaPago >= fecha_inicio,
            PagoProveedor.fechaPago <= fecha_fin
        ).order_by(PagoProveedor.fechaPago.desc()).all()
    
    @staticmethod
    def create_pago(data):
        """Crear un nuevo pago a proveedor"""
        try:
            # Convertir la fecha si viene como string
            if isinstance(data.get('fechaPago'), str):
                fecha_pago = datetime.strptime(data.get('fechaPago'), '%Y-%m-%d').date()
            else:
                fecha_pago = data.get('fechaPago', datetime.now().date())
            
            pago = PagoProveedor(
                idProveedor=data.get('idProveedor'),
                fechaPago=fecha_pago,
                monto=float(data.get('monto')),
                referencia=data.get('referencia', ''),
                idCompra=data.get('idCompra'),
                estatus=int(data.get('estatus', 1))
            )
            
            db.session.add(pago)
            db.session.commit()
            return pago
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def update_pago(pago_id, data):
        """Actualizar un pago existente"""
        try:
            pago = PagoProveedor.query.get(pago_id)
            
            if not pago:
                return None
            
            # Actualizar datos del pago
            if 'idProveedor' in data:
                pago.idProveedor = data['idProveedor']
            
            if 'fechaPago' in data:
                if isinstance(data['fechaPago'], str):
                    pago.fechaPago = datetime.strptime(data['fechaPago'], '%Y-%m-%d').date()
                else:
                    pago.fechaPago = data['fechaPago']
            
            if 'monto' in data:
                pago.monto = float(data['monto'])
            
            if 'referencia' in data:
                pago.referencia = data['referencia']
            
            if 'idCompra' in data:
                pago.idCompra = data['idCompra']
            
            if 'estatus' in data:
                pago.estatus = int(data['estatus'])
            
            db.session.commit()
            return pago
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def delete_pago(pago_id):
        """Eliminar un pago"""
        try:
            pago = PagoProveedor.query.get(pago_id)
            
            if not pago:
                return False
            
            db.session.delete(pago)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False
    
    @staticmethod
    def get_resumen_pagos(fecha_inicio=None, fecha_fin=None):
        """Obtener resumen de pagos en un rango de fechas"""
        if fecha_inicio is None:
            fecha_inicio = datetime.now().replace(day=1).date()  # Primer día del mes actual
        elif isinstance(fecha_inicio, str):
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            
        if fecha_fin is None:
            fecha_fin = datetime.now().date()
        elif isinstance(fecha_fin, str):
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        
        # Obtener pagos en el rango de fechas
        pagos = PagoProveedor.query.filter(
            PagoProveedor.fechaPago >= fecha_inicio,
            PagoProveedor.fechaPago <= fecha_fin
        ).all()
        
        # Calcular total de pagos
        total_pagos = sum(pago.monto for pago in pagos if pago.estatus == 1)
        
        # Agrupar por proveedor
        pagos_por_proveedor = {}
        for pago in pagos:
            proveedor_nombre = pago.proveedor.nombre_proveedor if pago.proveedor else "Desconocido"
            if proveedor_nombre not in pagos_por_proveedor:
                pagos_por_proveedor[proveedor_nombre] = {
                    'total': 0,
                    'pagos': []
                }
            if pago.estatus == 1:  # Solo pagos completados
                pagos_por_proveedor[proveedor_nombre]['total'] += pago.monto
            pagos_por_proveedor[proveedor_nombre]['pagos'].append(pago)
        
        return {
            'fecha_inicio': fecha_inicio.strftime('%d/%m/%Y'),
            'fecha_fin': fecha_fin.strftime('%d/%m/%Y'),
            'num_pagos': len(pagos),
            'total_pagos': total_pagos,
            'pagos': pagos,
            'pagos_por_proveedor': pagos_por_proveedor
        }
    
class PedidoClienteController:
    """Controlador para la lógica de negocio relacionada con pedidos de clientes"""
    
    @staticmethod
    def get_all_pedidos():
        """Obtener todos los pedidos"""
        return PedidoCliente.query.order_by(PedidoCliente.fechaPedido.desc()).all()
    
    @staticmethod
    def get_pedidos_by_cliente(cliente_id):
        """Obtener pedidos por cliente"""
        return PedidoCliente.query.filter_by(idCliente=cliente_id).order_by(PedidoCliente.fechaPedido.desc()).all()
    
    @staticmethod
    def get_pedido_by_id(pedido_id):
        """Obtener un pedido por su ID"""
        return PedidoCliente.query.get(pedido_id)
    
    @staticmethod
    def get_pedidos_pendientes():
        """Obtener pedidos pendientes"""
        return PedidoCliente.query.filter(PedidoCliente.estatus.in_([0, 1])).order_by(PedidoCliente.fechaPedido.asc()).all()
    
    @staticmethod
    def verificar_stock_pedido(detalles_data):
        """
        Verificar si hay suficiente stock para todos los productos de un pedido
        
        Args:
            detalles_data: Lista de diccionarios con detalles de productos
            
        Returns:
            tuple: (bool, str) - Estado de verificación y mensaje
        """
        # Crear un diccionario para sumar unidades por galleta
        unidades_por_galleta = {}
        
        # Primera pasada: sumar todas las unidades necesarias por galleta
        for detalle_data in detalles_data:
            galleta_id = detalle_data.get('galleta_id')
            cantidad = int(detalle_data.get('cantidad', 0))
            tipo_venta = int(detalle_data.get('tipo_venta', 1))  # 1 = Individual, 0 = Paquete
            
            # Calcular unidades reales según tipo de venta
            unidades_reales = cantidad
            if tipo_venta == 0:  # Paquete (5 unidades)
                unidades_reales = cantidad * 5
            
            # Sumar al total de esta galleta
            if galleta_id not in unidades_por_galleta:
                unidades_por_galleta[galleta_id] = 0
            unidades_por_galleta[galleta_id] += unidades_reales
        
        # Segunda pasada: verificar stock disponible para cada galleta
        for galleta_id, unidades_necesarias in unidades_por_galleta.items():
            galleta = Galletas.query.get(galleta_id)
            if not galleta:
                return False, f"Producto con ID {galleta_id} no encontrado"
            
            if galleta.existencias < unidades_necesarias:
                return False, f"Stock insuficiente para {galleta.nombreGalleta}. Disponible: {galleta.existencias}, Solicitado: {unidades_necesarias}"
        
        return True, "Stock suficiente para el pedido"
    
    @staticmethod
    def create_pedido(data, detalles_data):
        """
        Crear un nuevo pedido con sus detalles
        
        Args:
            data: Diccionario con datos del pedido
            detalles_data: Lista de diccionarios con detalles del pedido
        """
        try:
            # Verificar stock si se necesita (opcional para pedidos, ya que no afecta inventario hasta convertirse en venta)
            stock_suficiente, mensaje = PedidoClienteController.verificar_stock_pedido(detalles_data)
            if not stock_suficiente:
                # Se puede optar por mostrar la advertencia pero permitir el pedido,
                # o impedir el pedido si no hay stock suficiente
                # En este caso, permitimos que se cree el pedido aunque no haya suficiente stock
                print(f"Advertencia: {mensaje}")
            
            # Convertir la fecha si viene como string
            fecha_entrega = None
            if data.get('fechaEntrega'):
                if isinstance(data.get('fechaEntrega'), str):
                    fecha_entrega = datetime.strptime(data.get('fechaEntrega'), '%Y-%m-%d').date()
                else:
                    fecha_entrega = data.get('fechaEntrega')
            
            # Crear el pedido
            pedido = PedidoCliente(
                idCliente=data.get('idCliente'),
                fechaPedido=datetime.now(),
                fechaEntrega=fecha_entrega,
                instrucciones=data.get('instrucciones', ''),
                estatus=int(data.get('estatus', 0))  # 0: Pendiente por defecto
            )
            
            db.session.add(pedido)
            db.session.flush()  # Para obtener el ID generado para el pedido
            
            # Crear los detalles y calcular el total
            total_pedido = 0.0
            for detalle_data in detalles_data:
                galleta = Galletas.query.get(detalle_data.get('galleta_id'))
                if not galleta:
                    continue
                
                cantidad = int(detalle_data.get('cantidad', 0))
                tipo_venta = int(detalle_data.get('tipo_venta', 1))  # 1 = Individual, 0 = Paquete
                
                # Calcular precio unitario según tipo de venta
                if tipo_venta == 0:  # Paquete (5 unidades con 10% de descuento)
                    precio_unitario = galleta.precio_unitario * 0.9 * 5  # Precio por paquete
                else:
                    precio_unitario = galleta.precio_unitario  # Precio individual
                
                subtotal = cantidad * precio_unitario
                total_pedido += subtotal
                
                detalle = DetallePedido(
                    pedido_id=pedido.idPedido,
                    galleta_id=detalle_data.get('galleta_id'),
                    cantidad=cantidad,
                    precio_unitario=precio_unitario,
                    subtotal=subtotal,
                    tipo_venta=tipo_venta
                )
                
                db.session.add(detalle)
            
            # Actualizar el total del pedido
            pedido.total = total_pedido
            
            # Los pedidos no afectan el inventario hasta que se convierten en ventas
            
            db.session.commit()
            return pedido
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def update_pedido(pedido_id, data, detalles_data=None):
        """
        Actualizar un pedido existente y opcionalmente sus detalles
        
        Args:
            pedido_id: ID del pedido a actualizar
            data: Diccionario con datos del pedido
            detalles_data: Lista de diccionarios con detalles del pedido (opcional)
        """
        try:
            pedido = PedidoCliente.query.get(pedido_id)
            
            if not pedido:
                return None
            
            # Guardar estatus anterior para comprobar si hay cambios
            estatus_anterior = pedido.estatus
            
            # Actualizar datos del pedido
            if 'idCliente' in data:
                pedido.idCliente = data['idCliente']
            
            if 'fechaEntrega' in data and data['fechaEntrega']:
                if isinstance(data['fechaEntrega'], str):
                    pedido.fechaEntrega = datetime.strptime(data['fechaEntrega'], '%Y-%m-%d').date()
                else:
                    pedido.fechaEntrega = data['fechaEntrega']
            
            if 'instrucciones' in data:
                pedido.instrucciones = data['instrucciones']
            
            if 'estatus' in data:
                pedido.estatus = int(data['estatus'])
            
            # Si se proporcionan detalles nuevos, recrear los detalles
            if detalles_data is not None:
                # Verificar stock si necesario (opcional para pedidos)
                stock_suficiente, mensaje = PedidoClienteController.verificar_stock_pedido(detalles_data)
                if not stock_suficiente:
                    # Advertencia pero permitimos actualizar
                    print(f"Advertencia: {mensaje}")
                
                # Eliminar los detalles antiguos
                for detalle in pedido.detalles:
                    db.session.delete(detalle)
                
                # Crear los nuevos detalles y recalcular el total
                total_pedido = 0.0
                for detalle_data in detalles_data:
                    galleta = Galletas.query.get(detalle_data.get('galleta_id'))
                    if not galleta:
                        continue
                    
                    cantidad = int(detalle_data.get('cantidad', 0))
                    tipo_venta = int(detalle_data.get('tipo_venta', 1))  # 1 = Individual, 0 = Paquete
                    
                    # Calcular precio unitario según tipo de venta
                    precio_unitario = galleta.precio_unitario
                    if tipo_venta == 0:  # Paquete (5 unidades con 10% de descuento)
                        precio_unitario = precio_unitario * 0.9 * 5  # Precio por paquete
                    
                    subtotal = cantidad * precio_unitario
                    total_pedido += subtotal
                    
                    detalle = DetallePedido(
                        pedido_id=pedido.idPedido,
                        galleta_id=detalle_data.get('galleta_id'),
                        cantidad=cantidad,
                        precio_unitario=precio_unitario,
                        subtotal=subtotal,
                        tipo_venta=tipo_venta
                    )
                    
                    db.session.add(detalle)
                
                # Actualizar el total del pedido
                pedido.total = total_pedido
            
            # Los pedidos no afectan el inventario
            # Si cambia de estado a completado o cancelado, solo actualizamos el estado
            
            db.session.commit()
            return pedido
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def delete_pedido(pedido_id):
        """Eliminar un pedido"""
        try:
            pedido = PedidoCliente.query.get(pedido_id)
            
            if not pedido:
                return False
            
            # Los pedidos no afectan el inventario, solo los eliminamos
            db.session.delete(pedido)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False
            
    @staticmethod
    def get_detalles_pedido(pedido_id):
        """Obtener los detalles de un pedido"""
        return DetallePedido.query.filter_by(pedido_id=pedido_id).all()
    
    @staticmethod
    def cambiar_estatus_pedido(pedido_id, nuevo_estatus):
        """Cambiar el estatus de un pedido"""
        try:
            pedido = PedidoCliente.query.get(pedido_id)
            
            if not pedido:
                return False, "Pedido no encontrado"
            
            if nuevo_estatus not in [0, 1, 2, 3]:  # Validar estatus
                return False, "Estatus no válido"
            
            # Guardar estatus anterior
            estatus_anterior = pedido.estatus
            
            # Si no hay cambio, no hacer nada
            if estatus_anterior == nuevo_estatus:
                return True, "El estatus no ha cambiado"
                
            # Cambio a completado (2) debe realizarse a través de convertir_pedido_a_venta
            if nuevo_estatus == 2 and estatus_anterior != 2:
                return False, "Para completar un pedido, debe convertirlo a venta"
            
            pedido.estatus = nuevo_estatus
            db.session.commit()
            
            estatus_texto = {
                0: "Pendiente",
                1: "En Proceso",
                2: "Completado",
                3: "Cancelado"
            }
            
            return True, f"Pedido actualizado a '{estatus_texto[nuevo_estatus]}'"
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def convertir_pedido_a_venta(pedido_id):
        """Convertir un pedido en una venta con validación de inventario"""
        try:
            pedido = PedidoCliente.query.get(pedido_id)
            
            if not pedido:
                return False, "Pedido no encontrado", None
            
            if pedido.estatus == 3:  # Cancelado
                return False, "No se puede convertir un pedido cancelado en venta", None
                    
            if pedido.estatus == 2:  # Ya completado
                return False, "Este pedido ya ha sido completado", None
            
            # Crear datos para la venta
            venta_data = {
                'IdCliente': pedido.idCliente,
                'estatus': 1  # Completada
            }
            
            # Obtener detalles del pedido para crear detalles de venta
            detalles_pedido = DetallePedido.query.filter_by(pedido_id=pedido_id).all()
            detalles_venta = []
            
            # Verificar disponibilidad de stock para todos los productos
            for detalle in detalles_pedido:
                galleta = Galletas.query.get(detalle.galleta_id)
                
                if not galleta:
                    return False, f"Galleta con ID {detalle.galleta_id} no encontrada", None
                
                # Calcular unidades reales según tipo de venta
                unidades_reales = detalle.cantidad
                if detalle.tipo_venta == 0:  # Paquete (5 unidades)
                    unidades_reales = detalle.cantidad * 5
                
                if galleta.existencias < unidades_reales:
                    return False, f"Stock insuficiente para {galleta.nombreGalleta}. Disponible: {galleta.existencias}, Requerido: {unidades_reales}", None
                
                detalles_venta.append({
                    'galleta_id': detalle.galleta_id,
                    'cantidad': detalle.cantidad,
                    'tipo_venta': detalle.tipo_venta
                })
            
            # Crear la venta 
            venta = Venta(
                fechaVenta=datetime.now(),
                IdCliente=pedido.idCliente,
                estatus=1  # Completada
            )
            
            db.session.add(venta)
            db.session.flush()
            
            # Crear los detalles de la venta y reducir inventario
            total_venta = 0.0
            for detalle in detalles_pedido:
                galleta = Galletas.query.get(detalle.galleta_id)
                
                # Reducir inventario
                unidades_reales = detalle.cantidad
                if detalle.tipo_venta == 0:  # Paquete (5 unidades)
                    unidades_reales = detalle.cantidad * 5
                
                galleta.existencias -= unidades_reales
                
                # Crear detalle de venta
                precio_unitario = detalle.precio_unitario
                subtotal = detalle.cantidad * precio_unitario
                total_venta += subtotal
                
                detalle_venta = DetalleVenta(
                    venta_id=venta.idVenta,
                    galleta_id=detalle.galleta_id,
                    cantidad=detalle.cantidad,
                    precio_unitario=precio_unitario,
                    subtotal=subtotal,
                    tipo_venta=detalle.tipo_venta
                )
                
                db.session.add(detalle_venta)
            
            # Actualizar el total de la venta
            venta.total = total_venta
            
            # Actualizar el estatus del pedido a Completado
            pedido.estatus = 2  # Completado
            
            db.session.commit()
            
            return True, "Pedido convertido a venta exitosamente", venta
        except Exception as e:
            db.session.rollback()
            return False, str(e), None