from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

# Esta es la única instancia de SQLAlchemy en toda la aplicación
db = SQLAlchemy()

def init_db(app):
    # Importar todos los modelos para asegurarse de que SQLAlchemy los conozca
    # Las importaciones están aquí para evitar dependencias circulares
    import modulos.galletas.models
    import modulos.recetas.models
    import modulos.ingredientes.models
    
    # Crear todas las tablas dentro del contexto de la aplicación
    with app.app_context():
        db.create_all()

class Proveedor(db.Model):
    __tablename__ = 'Proveedores'
    idProveedor = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_proveedor = db.Column(db.String(255), nullable=False)
    telefono = db.Column(db.String(255))
    
    # Relaciones
    compras = db.relationship('CompraInsumo', backref='proveedor', lazy=True)

class CompraInsumo(db.Model):
    __tablename__ = 'ComprasInsumos'
    idCompra = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha = db.Column(db.Date, nullable=False)
    idProveedor = db.Column(db.Integer, db.ForeignKey('Proveedores.idProveedor'))
    
    # Relaciones
    detalles = db.relationship('CompraDetalle', backref='compra', lazy=True)

class CompraDetalle(db.Model):
    __tablename__ = 'ComprasDetalles'
    idCompraDetalle = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idCompra = db.Column(db.Integer, db.ForeignKey('ComprasInsumos.idCompra'))
    idIngrediente = db.Column(db.Integer, db.ForeignKey('Ingredientes.idIngrediente'))
    cantidad = db.Column(db.Integer, nullable=False)

class RecetaIngrediente(db.Model):
    __tablename__ = 'RecetaIngredientes'
    receta_id = db.Column(db.Integer, db.ForeignKey('Recetas.idReceta'), primary_key=True)
    ingrediente_id = db.Column(db.Integer, db.ForeignKey('Ingredientes.idIngrediente'), primary_key=True)
    cantidad = db.Column(db.Float, nullable=False)

class Produccion(db.Model):
    __tablename__ = 'Produccion'
    idProduccion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    receta_id = db.Column(db.Integer, db.ForeignKey('Recetas.idReceta'))
    estado_produccion = db.Column(db.Integer, nullable=False)  # 1 = En Proceso, 0 = Terminado
    fecha_produccion = db.Column(db.Date)

class Venta(db.Model):
    __tablename__ = 'Ventas'
    idVenta = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fechaVenta = db.Column(db.Date, nullable=False)
    cliente = db.Column(db.String(150))
    estatus = db.Column(db.Integer, nullable=False)
    
    # Relaciones
    detalles = db.relationship('DetalleVenta', backref='venta', lazy=True)

class DetalleVenta(db.Model):
    __tablename__ = 'DetallesVenta'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    venta_id = db.Column(db.Integer, db.ForeignKey('Ventas.idVenta'))
    galleta_id = db.Column(db.Integer, db.ForeignKey('Galletas.idGalleta'))
    cantidad = db.Column(db.Integer, nullable=False)
    tipo_venta = db.Column(db.Integer, nullable=False)  # 1 = Individual, 0 = Paquete

class MovimientoInsumo(db.Model):
    __tablename__ = 'MovimientosInsumos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ingrediente_id = db.Column(db.Integer, db.ForeignKey('Ingredientes.idIngrediente'))
    tipo_movimiento = db.Column(db.Integer, nullable=False)  # 1 = Consumo, 0 = Reabastecimiento
    cantidad = db.Column(db.Float, nullable=False)
    fecha_movimiento = db.Column(db.Date, nullable=False)
    
class Usuario(db.Model):
    __tablename__ = 'usuario'

    id = db.Column(db.Integer, primary_key=True)
    nombre_usuario = db.Column(db.String(50), unique=True, nullable=False)
    correo = db.Column(db.String(120), unique=True, nullable=False)
    hash_contrasena = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), nullable=False)
    
    # Campos de seguridad
    ultimo_inicio_sesion = db.Column(db.DateTime, nullable=True)
    intentos_inicio_sesion = db.Column(db.Integer, default=0)
    esta_bloqueado = db.Column(db.Boolean, default=False)
    bloqueo_hasta = db.Column(db.DateTime, nullable=True)
    contrasena_cambiada_en = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Nuevo campo de estado
    esta_activo = db.Column(db.Boolean, default=True)

    def is_active(self):
        """
        Verifica si el usuario está activo y no bloqueado
        """
        return self.esta_activo and not self.esta_bloqueado

    def necesita_cambiar_contrasena(self):
        """
        Verifica si el usuario necesita cambiar su contraseña.
        Por defecto, cada 90 días.
        """
        dias_desde_cambio = (datetime.utcnow() - self.contrasena_cambiada_en).days
        return dias_desde_cambio > 90

    def incrementar_intentos_fallidos(self):
        """
        Incrementa los intentos fallidos y bloquea la cuenta si es necesario.
        """
        self.intentos_inicio_sesion += 1
        if self.intentos_inicio_sesion >= 3:
            self.esta_bloqueado = True
            self.bloqueo_hasta = datetime.utcnow() + timedelta(minutes=15)
        db.session.commit()

    def reiniciar_intentos_fallidos(self):
        """
        Reinicia los intentos fallidos y desbloquea la cuenta.
        """
        self.intentos_inicio_sesion = 0
        self.esta_bloqueado = False
        self.bloqueo_hasta = None
        db.session.commit()

    def actualizar_ultimo_inicio_sesion(self):
        """
        Actualiza la marca de tiempo del último inicio de sesión.
        """
        self.ultimo_inicio_sesion = datetime.utcnow()
        db.session.commit()

    def desactivar(self):
        """
        Desactiva la cuenta de usuario
        """
        self.esta_activo = False
        db.session.commit()

    def activar(self):
        """
        Activa la cuenta de usuario
        """
        self.esta_activo = True
        db.session.commit()