from datetime import datetime, timedelta
from flask_login import UserMixin
from extensions import db
from extensions import login_manager

# Usar db directamente
class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuario'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre_usuario = db.Column(db.String(50), unique=True, nullable=False)
    correo = db.Column(db.String(120), unique=True, nullable=False)
    hash_contrasena = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), nullable=False)  # Cambiado para coincidir
    ultimo_inicio_sesion = db.Column(db.DateTime)  # Nombre exacto
    intentos_inicio_sesion = db.Column(db.Integer, default=0)  # Nombre corregido
    esta_bloqueado = db.Column(db.Boolean, default=False)
    bloqueo_hasta = db.Column(db.DateTime)
    contrasena_cambiada_en = db.Column(db.DateTime, default=datetime.utcnow)  # Nombre exacto
    esta_activo = db.Column(db.Boolean, default=True)
    
    # Actualiza los métodos para usar los nombres correctos
    def incrementar_intentos_fallidos(self):
        self.intentos_inicio_sesion += 1  # Nombre corregido
        if self.intentos_inicio_sesion >= 3:
            self.esta_bloqueado = True
            self.bloqueo_hasta = datetime.utcnow() + timedelta(minutes=15)
        db.session.commit()
    
    def reiniciar_intentos_fallidos(self):
        self.intentos_inicio_sesion = 0  # Nombre corregido
        self.esta_bloqueado = False
        self.bloqueo_hasta = None
        db.session.commit()
    def incrementar_intentos_fallidos(self):
        self.intentos_fallidos += 1
        if self.intentos_fallidos >= 3:
            self.esta_bloqueado = True
            self.bloqueo_hasta = datetime.utcnow() + timedelta(minutes=15)
        db.session.commit()
    
    def reiniciar_intentos_fallidos(self):
        self.intentos_fallidos = 0
        self.esta_bloqueado = False
        self.bloqueo_hasta = None
        db.session.commit()
        
    def actualizar_ultimo_inicio_sesion(self):
        self.ultimo_inicio_sesion = datetime.utcnow()
        db.session.commit()
        
    def activar(self):
        self.esta_activo = True
        db.session.commit()
        
    def desactivar(self):
        self.esta_activo = False
        db.session.commit()

# Configuración para Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))