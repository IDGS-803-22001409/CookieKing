from mailbox import Message
from flask import current_app, session
from flask_login import login_user, logout_user
from datetime import datetime
from .models import Usuario, db, ValidadorContrasena, AutenticacionDosFactores
from flask_mail import Message

class AuthController:
    validador = ValidadorContrasena()
    auth_2fa = AutenticacionDosFactores()

    @staticmethod
    def iniciar_sesion(nombre_usuario, contrasena):
        usuario = Usuario.query.filter_by(nombre_usuario=nombre_usuario).first()
        
        if not usuario:
            return False, "Usuario no encontrado"
        
        if usuario.esta_bloqueado and usuario.bloqueo_hasta > datetime.utcnow():
            tiempo_restante = int((usuario.bloqueo_hasta - datetime.utcnow()).total_seconds() / 60)
            return False, f"Cuenta bloqueada. Intente nuevamente en {tiempo_restante} minutos"
        
        if not usuario.esta_activo:
            return False, "Su cuenta está desactivada. Contacte al administrador."
        
        if AuthController.validador.verificar_contrasena(contrasena, usuario.hash_contrasena):
            usuario.reiniciar_intentos_fallidos()
            
            datos_totp = AuthController.auth_2fa.generar_codigo_totp()
            
            mail = current_app.extensions.get('mail')
            msg = Message(
    'Código de Verificación',
    recipients=[usuario.correo],
    body=f'Tu código de verificación es: {datos_totp["codigo"]}'
)
            mail.send(msg)
            
            session['totp_data'] = {
                'codigo': datos_totp['codigo'],
                'usuario_id': usuario.id,
                'expira_en': datos_totp['expira_en'].isoformat()
            }
            
            return True, "Código de verificación enviado"
        else:
            usuario.incrementar_intentos_fallidos()
            return False, "Credenciales inválidas"

    @staticmethod
    def verificar_totp(codigo_usuario):
        totp_data = session.get('totp_data')
        if not totp_data:
            return False, "Sesión de autenticación inválida"
        
        if datetime.fromisoformat(totp_data['expira_en']) < datetime.utcnow():
            return False, "Código expirado. Intente iniciar sesión nuevamente"
        
        if codigo_usuario == totp_data['codigo']:
            usuario = Usuario.query.get(totp_data['usuario_id'])
            login_user(usuario)
            usuario.actualizar_ultimo_inicio_sesion()
            session.pop('totp_data', None)
            return True, "Inicio de sesión exitoso"
        return False, "Código TOTP inválido"

    @staticmethod
    def registrar_usuario(data):
        es_valida, mensaje = AuthController.validador.validar_contrasena(data['contrasena'])
        if not es_valida:
            return False, mensaje
        
        usuario_existente = Usuario.query.filter(
            (Usuario.nombre_usuario == data['nombre_usuario']) | 
            (Usuario.correo == data['correo'])
        ).first()
        
        if usuario_existente:
            return False, "Nombre de usuario o correo ya registrados"
        
        nuevo_usuario = Usuario(
            nombre_usuario=data['nombre_usuario'],
            correo=data['correo'],
            hash_contrasena=AuthController.validador.hash_contrasena(data['contrasena']),
            rol=data.get('rol', 'usuario'),
            esta_activo=True
        )
        
        try:
            db.session.add(nuevo_usuario)
            db.session.commit()
            return True, "Registro exitoso. Inicie sesión."
        except Exception as e:
            db.session.rollback()
            return False, f"Error al registrar usuario: {str(e)}"

    @staticmethod
    def cerrar_sesion():
        logout_user()
        return True, "Sesión cerrada correctamente"

    @staticmethod
    def obtener_usuarios():
        return Usuario.query.all()

    @staticmethod
    def crear_usuario_admin(data):
        return AuthController.registrar_usuario(data)

    @staticmethod
    def actualizar_usuario(usuario_id, data):
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return False, "Usuario no encontrado"
        
        usuario_existente = Usuario.query.filter(
            ((Usuario.nombre_usuario == data['nombre_usuario']) | 
             (Usuario.correo == data['correo'])) & 
            (Usuario.id != usuario_id)
        ).first()
        
        if usuario_existente:
            return False, "Nombre de usuario o correo ya registrados por otro usuario"
        
        usuario.nombre_usuario = data['nombre_usuario']
        usuario.correo = data['correo']
        usuario.rol = data['rol']
        
        if 'contrasena' in data and data['contrasena']:
            es_valida, mensaje = AuthController.validador.validar_contrasena(data['contrasena'])
            if not es_valida:
                return False, mensaje
            usuario.hash_contrasena = AuthController.validador.hash_contrasena(data['contrasena'])
        
        try:
            db.session.commit()
            return True, "Usuario actualizado exitosamente"
        except Exception as e:
            db.session.rollback()
            return False, f"Error al actualizar usuario: {str(e)}"

    @staticmethod
    def cambiar_estado_usuario(usuario_id):
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return False, "Usuario no encontrado"
        
        if usuario.esta_activo:
            usuario.desactivar()
            mensaje = "Usuario desactivado"
        else:
            usuario.activar()
            mensaje = "Usuario activado"
        
        try:
            db.session.commit()
            return True, mensaje
        except Exception as e:
            db.session.rollback()
            return False, f"Error al cambiar estado: {str(e)}"
