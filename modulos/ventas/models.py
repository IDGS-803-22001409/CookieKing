from models import db
from datetime import datetime

class Venta(db.Model):
    """Modelo para ventas"""
    __tablename__ = 'Ventas'
    idVenta = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fechaVenta = db.Column(db.DateTime, nullable=False, default=datetime.now)
    IdCliente = db.Column(db.Integer, db.ForeignKey('Cliente.idCliente'))
    estatus = db.Column(db.Integer, nullable=False, default=1)  # 1: Completada, 0: Pendiente, 2: Cancelada
    total = db.Column(db.Float, nullable=False, default=0.0)
    
    # Relaciones
    detalles = db.relationship('DetalleVenta', backref='venta', lazy=True, cascade="all, delete-orphan")
    # Importante: No definimos la relación con Cliente aquí porque ya existe en el modelo Cliente
    
    def to_dict(self):
        """Convierte el modelo a un diccionario para serialización"""
        cliente_nombre = None
        try:
            from modulos.clientes.models import Cliente
            cliente = Cliente.query.get(self.IdCliente)
            if cliente:
                cliente_nombre = cliente.nombreCliente
        except:
            pass
            
        return {
            'idVenta': self.idVenta,
            'fechaVenta': self.fechaVenta.strftime('%Y-%m-%d %H:%M:%S') if self.fechaVenta else None,
            'IdCliente': self.IdCliente,
            'nombre_cliente': cliente_nombre or "Cliente General",
            'estatus': self.estatus,
            'total': self.total
        }

# Alias para compatibilidad con el código existente
Ventas = Venta

class DetalleVenta(db.Model):
    """Modelo para detalles de venta"""
    __tablename__ = 'DetallesVenta'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    venta_id = db.Column(db.Integer, db.ForeignKey('Ventas.idVenta'), nullable=False)
    galleta_id = db.Column(db.Integer, db.ForeignKey('Galletas.idGalleta'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    tipo_venta = db.Column(db.Integer, nullable=False)  # 1 = Individual, 0 = Paquete
    
    # Relationship
    galleta = db.relationship('Galletas', backref='detalles_venta', lazy=True)
    
    def to_dict(self):
        """Convierte el modelo a un diccionario para serialización"""
        galleta_nombre = None
        try:
            from modulos.galletas.models import Galletas
            galleta = Galletas.query.get(self.galleta_id)
            if galleta:
                galleta_nombre = galleta.nombreGalleta
        except:
            pass
            
        return {
            'id': self.id,
            'venta_id': self.venta_id,
            'galleta_id': self.galleta_id,
            'nombre_galleta': galleta_nombre,
            'cantidad': self.cantidad,
            'precio_unitario': self.precio_unitario,
            'subtotal': self.subtotal,
            'tipo_venta': self.tipo_venta
        }

# Alias para compatibilidad con el código existente
DetallesVenta = DetalleVenta

class PagoProveedor(db.Model):
    """Modelo para pagos a proveedores"""
    __tablename__ = 'PagosProveedores'
    idPago = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idProveedor = db.Column(db.Integer, db.ForeignKey('Proveedores.idProveedor'), nullable=False)
    fechaPago = db.Column(db.Date, nullable=False, default=datetime.now().date)
    monto = db.Column(db.Float, nullable=False)
    referencia = db.Column(db.String(100))
    idCompra = db.Column(db.Integer, db.ForeignKey('ComprasInsumos.idCompra'))
    estatus = db.Column(db.Integer, nullable=False, default=1)  # 1: Pagado, 0: Pendiente, 2: Cancelado
    
    # Relaciones - las manejamos con cuidado para evitar conflictos
    def get_proveedor(self):
        try:
            from modulos.proveedores.models import Proveedor
            return Proveedor.query.get(self.idProveedor)
        except:
            return None
            
    def get_compra(self):
        try:
            from modulos.compras.models import CompraInsumo
            return CompraInsumo.query.get(self.idCompra)
        except:
            return None
    
    @property
    def proveedor(self):
        return self.get_proveedor()
    
    def to_dict(self):
        """Convierte el modelo a un diccionario para serialización"""
        proveedor = self.get_proveedor()
        
        return {
            'idPago': self.idPago,
            'idProveedor': self.idProveedor,
            'nombre_proveedor': proveedor.nombre_proveedor if proveedor else None,
            'fechaPago': self.fechaPago.strftime('%Y-%m-%d') if self.fechaPago else None,
            'monto': self.monto,
            'referencia': self.referencia,
            'idCompra': self.idCompra,
            'estatus': self.estatus
        }

class PedidoCliente(db.Model):
    """Modelo para pedidos de clientes"""
    __tablename__ = 'PedidosClientes'
    idPedido = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idCliente = db.Column(db.Integer, db.ForeignKey('Cliente.idCliente'), nullable=False)
    fechaPedido = db.Column(db.DateTime, nullable=False, default=datetime.now)
    fechaEntrega = db.Column(db.Date, nullable=True)
    instrucciones = db.Column(db.Text)
    estatus = db.Column(db.Integer, nullable=False, default=0)  # 0: Pendiente, 1: En Proceso, 2: Completado, 3: Cancelado
    total = db.Column(db.Float, nullable=False, default=0.0)
    
    # Relaciones - manejamos con cuidado
    detalles = db.relationship('DetallePedido', backref='pedido', lazy=True, cascade="all, delete-orphan")
    
    def get_cliente(self):
        try:
            from modulos.clientes.models import Cliente
            return Cliente.query.get(self.idCliente)
        except:
            return None
    
    @property
    def cliente(self):
        return self.get_cliente()
    
    def to_dict(self):
        """Convierte el modelo a un diccionario para serialización"""
        cliente = self.get_cliente()
        
        return {
            'idPedido': self.idPedido,
            'idCliente': self.idCliente,
            'nombre_cliente': cliente.nombreCliente if cliente else None,
            'fechaPedido': self.fechaPedido.strftime('%Y-%m-%d %H:%M:%S') if self.fechaPedido else None,
            'fechaEntrega': self.fechaEntrega.strftime('%Y-%m-%d') if self.fechaEntrega else None,
            'instrucciones': self.instrucciones,
            'estatus': self.estatus,
            'total': self.total
        }

class DetallePedido(db.Model):
    """Modelo para detalles de pedidos"""
    __tablename__ = 'DetallesPedido'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('PedidosClientes.idPedido'), nullable=False)
    galleta_id = db.Column(db.Integer, db.ForeignKey('Galletas.idGalleta'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    tipo_venta = db.Column(db.Integer, nullable=False)  # 1 = Individual, 0 = Paquete
    
    # Relationship
    galleta = db.relationship('Galletas', backref='detalles_pedido', lazy=True)
    
    def to_dict(self):
        """Convierte el modelo a un diccionario para serialización"""
        galleta_nombre = None
        try:
            from modulos.galletas.models import Galletas
            galleta = Galletas.query.get(self.galleta_id)
            if galleta:
                galleta_nombre = galleta.nombreGalleta
        except:
            pass
            
        return {
            'id': self.id,
            'pedido_id': self.pedido_id,
            'galleta_id': self.galleta_id,
            'nombre_galleta': galleta_nombre,
            'cantidad': self.cantidad,
            'precio_unitario': self.precio_unitario,
            'subtotal': self.subtotal,
            'tipo_venta': self.tipo_venta
        }