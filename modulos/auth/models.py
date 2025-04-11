from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta
from passlib.context import CryptContext
import re
from models import db  

class Usuario(db.Model, UserMixin):  
    __tablename__ = 'usuario'

    id = db.Column(db.Integer, primary_key=True)
    nombre_usuario = db.Column(db.String(50), unique=True, nullable=False)
    correo = db.Column(db.String(120), unique=True, nullable=False)
    hash_contrasena = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), nullable=False)
    ultimo_inicio_sesion = db.Column(db.DateTime, nullable=True)
    intentos_inicio_sesion = db.Column(db.Integer, default=0)
    esta_bloqueado = db.Column(db.Boolean, default=False)
    bloqueo_hasta = db.Column(db.DateTime, nullable=True)
    contrasena_cambiada_en = db.Column(db.DateTime, default=datetime.utcnow)
    esta_activo = db.Column(db.Boolean, default=True)
    token_recuperacion = db.Column(db.String(100), nullable=True)
    token_expiracion = db.Column(db.DateTime, nullable=True)
    
    def get_id(self):
        return str(self.id)
    
    def _repr_(self):
        return f'<Usuario {self.nombre_usuario}>'

    def is_active(self):
        return self.esta_activo and not self.esta_bloqueado

    def necesita_cambiar_contrasena(self):
        dias_desde_cambio = (datetime.utcnow() - self.contrasena_cambiada_en).days
        return dias_desde_cambio > 90

    def incrementar_intentos_fallidos(self):
        self.intentos_inicio_sesion += 1
        if self.intentos_inicio_sesion >= 3:
            self.esta_bloqueado = True
            self.bloqueo_hasta = datetime.utcnow() + timedelta(minutes=15)
        db.session.commit()

    def reiniciar_intentos_fallidos(self):
        self.intentos_inicio_sesion = 0
        self.esta_bloqueado = False
        self.bloqueo_hasta = None
        db.session.commit()

    def actualizar_ultimo_inicio_sesion(self):
        self.ultimo_inicio_sesion = datetime.utcnow()
        db.session.commit()

    def desactivar(self):
        self.esta_activo = False
        db.session.commit()

    def activar(self):
        self.esta_activo = True
        db.session.commit()

    def generar_token_recuperacion(self):
        import secrets
        self.token_recuperacion = secrets.token_urlsafe(32)
        self.token_expiracion = datetime.utcnow() + timedelta(hours=1)
        db.session.commit()
        return self.token_recuperacion

    def verificar_token_recuperacion(self, token):
        if token != self.token_recuperacion:
            return False
        if datetime.utcnow() > self.token_expiracion:
            return False
        return True

    def limpiar_token_recuperacion(self):
        self.token_recuperacion = None
        self.token_expiracion = None
        db.session.commit()

class ValidadorContrasena:
    CONTRASENAS_DEBILES = [
        'contrasena', '123456', 'qwerty', 'admin', 'dejame_entrar', 
        'bienvenido', 'monkey', 'abc123', 'password', '12345678'
    ]

    def __init__(self):
        self.pwd_context = CryptContext(
            schemes=["bcrypt", "django_pbkdf2_sha256"],
            deprecated="auto",
            bcrypt__default_rounds=12
        )

    def validar_contrasena(self, contrasena):
        if len(contrasena) < 8:
            return False, "La contraseña debe tener al menos 8 caracteres"
        if contrasena.lower() in self.CONTRASENAS_DEBILES:
            return False, "Contraseña muy común o insegura"
        if not re.search(r'[A-Z]', contrasena):
            return False, "Debe contener al menos una letra mayúscula"
        if not re.search(r'[a-z]', contrasena):
            return False, "Debe contener al menos una letra minúscula"
        if not re.search(r'\d', contrasena):
            return False, "Debe contener al menos un número"
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', contrasena):
            return False, "Debe contener al menos un carácter especial"
        return True, "Contraseña válida"

    def hash_contrasena(self, contrasena):
        return self.pwd_context.hash(contrasena)

    def verificar_contrasena(self, contrasena_plana, contrasena_hash):
        return self.pwd_context.verify(contrasena_plana, contrasena_hash)


class AutenticacionDosFactores:
    @staticmethod
    def generar_codigo_totp():
        import random
        return {
            'codigo': str(random.randint(100000, 999999)),
            'expira_en': datetime.utcnow() + timedelta(minutes=10)
        }

    @staticmethod
    def verificar_codigo_totp(codigo_usuario, codigo_generado):
        return codigo_usuario == codigo_generado