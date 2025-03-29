# modulos/auth/controllers.py
from flask import session, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from models import db
from modulos.auth.models import Usuario

class AuthController:
    @staticmethod
    def login(username, password):
        usuario = Usuario.query.filter_by(username=username).first()
        if usuario and usuario.check_password(password) and usuario.activo:
            login_user(usuario)
            return True
        return False
    
    @staticmethod
    def logout():
        logout_user()
        return True
    
    @staticmethod
    def register(data):
        existing_user = Usuario.query.filter((Usuario.username == data['username']) | 
                                           (Usuario.email == data['email'])).first()
        if existing_user:
            return False, "El nombre de usuario o correo ya existe"
        
        usuario = Usuario(
            username=data['username'],
            email=data['email'],
            nombre=data.get('nombre', ''),
            apellido=data.get('apellido', ''),
            rol=data.get('rol', 'usuario')
        )
        usuario.set_password(data['password'])
        
        db.session.add(usuario)
        db.session.commit()
        return True, "Usuario registrado correctamente"
    
    @staticmethod
    def get_all_usuarios():
        return Usuario.query.all()
    
    @staticmethod
    def get_usuario_by_id(usuario_id):
        return Usuario.query.get(usuario_id)
    
    @staticmethod
    def update_usuario(usuario_id, data):
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return False, "Usuario no encontrado"
        
        # Verificar si cambia username o email
        if data.get('username') != usuario.username:
            existing = Usuario.query.filter_by(username=data['username']).first()
            if existing and existing.id != usuario_id:
                return False, "El nombre de usuario ya existe"
                
        if data.get('email') != usuario.email:
            existing = Usuario.query.filter_by(email=data['email']).first()
            if existing and existing.id != usuario_id:
                return False, "El correo ya existe"
        
        usuario.username = data.get('username', usuario.username)
        usuario.email = data.get('email', usuario.email)
        usuario.nombre = data.get('nombre', usuario.nombre)
        usuario.apellido = data.get('apellido', usuario.apellido)
        usuario.rol = data.get('rol', usuario.rol)
        usuario.activo = data.get('activo', usuario.activo)
        
        if 'password' in data and data['password']:
            usuario.set_password(data['password'])
        
        db.session.commit()
        return True, "Usuario actualizado correctamente"
    
    @staticmethod
    def delete_usuario(usuario_id):
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return False, "Usuario no encontrado"
        
        # En vez de eliminar físicamente, marcar como inactivo
        usuario.activo = False
        db.session.commit()
        return True, "Usuario eliminado correctamente"