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
    '🍪 Código de Seguridad - Dulce Verificación',
    recipients=[usuario.correo],
    html=f'''
    <html>
        <head>
            <style>
                body {{ font-family: 'Arial', sans-serif; line-height: 1.6; color: #5a3e2b; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #fff5e6; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ padding: 20px; background-color: #fff9f0; }}
                .code {{ font-size: 28px; font-weight: bold; color: #d35400; text-align: center; margin: 25px 0; 
                        background: #fff; padding: 15px; border-radius: 8px; border: 2px dashed #e67e22; }}
                .footer {{ margin-top: 30px; font-size: 12px; color: #8b6b4a; text-align: center; 
                          background-color: #fff5e6; padding: 15px; border-radius: 0 0 10px 10px; }}
                .logo {{ color: #e67e22; font-weight: bold; font-size: 24px; }}
                .cookie-icon {{ font-size: 20px; vertical-align: middle; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2><span class="cookie-icon">🍪</span> <span class="logo">CooKieKing</span></h2>
                </div>
                <div class="content">
                    <p>¡Hola {usuario.nombre_usuario}!</p>
                    <p>Alguien está intentando acceder a tu cuenta en <strong>CooKieKing</strong>. Para asegurarnos de que eres tú, por favor utiliza este dulce código de verificación:</p>
                    
                    <div class="code">{datos_totp["codigo"]}</div>
                    
                    <p>Este código es tan fresco como nuestras galletas recién horneadas, pero solo dura 5 minutos. Si no has solicitado iniciar sesión, por favor ignora este mensaje o contáctanos en <a href="mailto:galletascookieking@gmail.com" style="color: #e67e22;">galletascookieking@gmail.com</a>.</p>
                    
                    <p style="text-align: center; margin-top: 25px;">
                        <span style="font-size: 18px;">🍪 🍪 🍪</span>
                    </p>
                </div>
                <div class="footer">
                    <p>© {datetime.now().year} CooKieKing. Todos los derechos reservados.</p>
                    <p>Este es un mensaje automático - Por la seguridad de tu cuenta, no lo reenvíes.</p>
                </div>
            </div>
        </body>
    </html>
    '''
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
                        
            if usuario.rol == 'admin':
                msg = "¡Bienvenido Administrador! Has iniciado sesión correctamente."
            elif usuario.rol == 'empleado':
                msg = "¡Bienvenido! Has iniciado sesión como empleado."
            else:
                msg = "¡Bienvenido! Has iniciado sesión correctamente."
                
            return True, msg
        
        return False, "Código TOTP inválido"

    @staticmethod
    def registrar_usuario(data, usuario_actual=None):
        es_valida, mensaje = AuthController.validador.validar_contrasena(data['contrasena'])
        if not es_valida:
            return False, mensaje
        
        usuario_existente = Usuario.query.filter(
            (Usuario.nombre_usuario == data['nombre_usuario']) | 
            (Usuario.correo == data['correo'])
        ).first()
        
        if usuario_existente:
            return False, "Nombre de usuario o correo ya registrados"
        
        # Lógica mejorada para asignación de roles
        rol = data.get('rol', 'cliente')
        
        # Solo permitir asignación de roles admin/empleado si el usuario actual es admin
        if rol in ['admin', 'empleado']:
            if not (usuario_actual and usuario_actual.is_authenticated and usuario_actual.rol == 'admin'):
                return False, "No tienes permisos para asignar este rol"
        
        nuevo_usuario = Usuario(
            nombre_usuario=data['nombre_usuario'],
            correo=data['correo'],
            hash_contrasena=AuthController.validador.hash_contrasena(data['contrasena']),
            rol=rol,
            esta_activo=True
        )
        
        try:
            db.session.add(nuevo_usuario)
            db.session.commit()
            return True, "Registro exitoso"
        except Exception as e:
            db.session.rollback()
            return False, f"Error al registrar: {str(e)}"

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
            