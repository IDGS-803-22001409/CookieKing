from flask import Blueprint, current_app, request, render_template, redirect, session, url_for, flash
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Mail, Message
from extensions import db, mail
from modulos.login.usuario import Usuario
from modulos.login.validador_contrasena import ValidadorContrasena
from modulos.login.autenticacion_dos_factores import AutenticacionDosFactores
from datetime import datetime, timedelta


# Crear un Blueprint para las rutas de autenticación
autenticacion_bp = Blueprint('autenticacion', __name__,template_folder='templates')

class ControladorAutenticacion:
    @staticmethod
    @autenticacion_bp.route('/iniciar_sesion', methods=['GET', 'POST'])
    def iniciar_sesion():
        """
        Método para gestionar el inicio de sesión de usuarios
        """
        if request.method == 'POST':
            nombre_usuario = request.form['nombre_usuario']
            contrasena = request.form['contrasena']
            
            # Buscar usuario por nombre de usuario
            usuario = Usuario.query.filter_by(nombre_usuario=nombre_usuario).first()
            
            if not usuario:
                flash('Usuario no encontrado', 'error')
                return render_template('modulos/login/iniciar_sesion.html')
            
            # Verificar si la cuenta está bloqueada
            if usuario.esta_bloqueado and usuario.bloqueo_hasta and usuario.bloqueo_hasta > datetime.utcnow():
                tiempo_restante = int((usuario.bloqueo_hasta - datetime.utcnow()).total_seconds() / 60)
                flash(f'Cuenta bloqueada. Intente nuevamente en {tiempo_restante} minutos', 'error')
                return render_template('modulos/login/iniciar_sesion.html')
            
            # Verificar si el usuario está activo
            if not usuario.esta_activo:
                flash('Su cuenta está desactivada. Contacte al administrador.', 'error')
                return render_template('modulos/login/iniciar_sesion.html')
            
            # Verificar contraseña
            if ValidadorContrasena.verificar_contrasena(contrasena, usuario.hash_contrasena):
                # Reiniciar intentos fallidos
                usuario.reiniciar_intentos_fallidos()
                
                # Generar código de dos pasos
                datos_totp = AutenticacionDosFactores.generar_codigo_totp()
                
                # Enviar código por correo
                mail = Mail(current_app)
                msg = Message('Código de Verificación', 
                              recipients=[usuario.correo])
                msg.body = f'Tu código de verificación es: {datos_totp["codigo"]}'
                mail.send(msg)
                
                # Almacenar información temporal de autenticación
                session['totp_codigo'] = datos_totp['codigo']
                session['usuario_id'] = usuario.id
                session['totp_expira_en'] = datos_totp['expira_en'].isoformat()
                
                return redirect(url_for('autenticacion.verificar_totp'))
            else:
                # Incrementar intentos fallidos
                usuario.incrementar_intentos_fallidos()
                flash('Credenciales inválidas', 'error')
        
        return render_template('modulos/login/iniciar_sesion.html')

    @staticmethod
    @autenticacion_bp.route('/verificar_totp', methods=['GET', 'POST'])
    def verificar_totp():
        """
        Método para verificar el código de autenticación de dos pasos
        """
        if request.method == 'POST':
            codigo_usuario = request.form['codigo_totp']
            usuario_id = session.get('usuario_id')
            totp_codigo_generado = session.get('totp_codigo')
            totp_expira_en = session.get('totp_expira_en')
            
            if not usuario_id or not totp_codigo_generado:
                flash('Sesión de autenticación inválida', 'error')
                return redirect(url_for('autenticacion.iniciar_sesion'))
            
            # Verificar expiración del código
            if datetime.fromisoformat(totp_expira_en) < datetime.utcnow():
                flash('Código expirado. Intente iniciar sesión nuevamente', 'error')
                return redirect(url_for('autenticacion.iniciar_sesion'))
            
            usuario = Usuario.query.get(usuario_id)
            
            if AutenticacionDosFactores.verificar_codigo_totp(codigo_usuario, totp_codigo_generado):
                # Iniciar sesión
                login_user(usuario, duration=timedelta(minutes=10))
                
                # Actualizar último inicio de sesión
                usuario.actualizar_ultimo_inicio_sesion()
                
                # Limpiar sesión temporal
                session.pop('totp_codigo', None)
                session.pop('usuario_id', None)
                session.pop('totp_expira_en', None)
                
                # Redirigir según el rol
                if usuario.rol == 'admin':
                    flash('Inicio de sesión exitoso', 'success')
                    return redirect(url_for('autenticacion.catalogo_usuarios'))
                else:
                    flash('Inicio de sesión exitoso', 'success')
                    return redirect(url_for('principal'))
            else:
                flash('Código TOTP inválido', 'error')
        
        return render_template('modulos/login/verificar_totp.html')

    @staticmethod
    @autenticacion_bp.route('/registro', methods=['GET', 'POST'])
    def registro():
        """
        Método para registrar nuevos usuarios
        """
        if request.method == 'POST':
            if not request.form.get('csrf_token'):
                flash('Token de seguridad inválido', 'error')
                return render_template('modulos/login/registro.html')
            nombre_usuario = request.form['nombre_usuario']
            correo = request.form['correo']
            contrasena = request.form['contrasena']
            rol = request.form.get('rol', 'admin')  # Valor por defecto
            
            # Validar contraseña
            es_valida, mensaje = ValidadorContrasena.validar_contrasena(contrasena)
            if not es_valida:
                flash(mensaje, 'error')
                return render_template('modulos/login/registro.html')
            
            # Verificar si el usuario ya existe
            usuario_existente = Usuario.query.filter(
                (Usuario.nombre_usuario == nombre_usuario) | (Usuario.correo == correo)
            ).first()
            
            if usuario_existente:
                flash('Nombre de usuario o correo ya registrados', 'error')
                return render_template('modulos/login/registro.html')
            
            # Hash de contraseña
            hash_contrasena = ValidadorContrasena.hash_contrasena(contrasena)
            
            # Crear nuevo usuario
            nuevo_usuario = Usuario(
                nombre_usuario=nombre_usuario,
                correo=correo,
                hash_contrasena=hash_contrasena,
                rol=rol,
                esta_activo=True
            )
            
            try:
                db.session.add(nuevo_usuario)  # Usa db en lugar de base_datos
                db.session.commit()
                flash('Registro exitoso. Inicie sesión.', 'success')
                return redirect(url_for('autenticacion.iniciar_sesion'))
            except Exception as e:
                db.session.rollback()  # Usa db en lugar de base_datos
                flash('Error al registrar usuario', 'error')
                print(f"Error de registro: {e}")
        
        return render_template('modulos/login/registro.html')

    @staticmethod
    @autenticacion_bp.route('/logout')
    @login_required
    def cerrar_sesion():
        """
        Método para cerrar sesión
        """
        logout_user()
        flash('Sesión cerrada correctamente', 'success')
        return redirect(url_for('autenticacion.iniciar_sesion'))

    
    @staticmethod
    @autenticacion_bp.route('/usuarios/crear', methods=['GET', 'POST'])
    @login_required
    def crear_usuario():
        """
        Método para crear nuevos usuarios (solo para administradores)
        """
        if current_user.rol != 'admin':
            flash('Acceso denegado', 'error')
            return redirect(url_for('principal'))
        
        if request.method == 'POST':
            nombre_usuario = request.form['nombre_usuario']
            correo = request.form['correo']
            contrasena = request.form['contrasena']
            rol = request.form['rol']
            
            # Validar existencia de usuario
            usuario_existente = Usuario.query.filter(
                (Usuario.nombre_usuario == nombre_usuario) | (Usuario.correo == correo)
            ).first()
            
            if usuario_existente:
                flash('Nombre de usuario o correo ya registrados', 'error')
                return render_template('crear_usuario.html')
            
            # Validar contraseña
            es_valida, mensaje = ValidadorContrasena.validar_contrasena(contrasena)
            if not es_valida:
                flash(mensaje, 'error')
                return render_template('crear_usuario.html')
            
            # Hash de contraseña
            hash_contrasena = ValidadorContrasena.hash_contrasena(contrasena)
            
            # Crear nuevo usuario
            nuevo_usuario = Usuario(
                nombre_usuario=nombre_usuario,
                correo=correo,
                hash_contrasena=hash_contrasena,
                rol=rol,
                esta_activo=True
            )
            
            try:
                db.session.add(nuevo_usuario)
                db.session.commit()
                flash('Usuario creado exitosamente', 'success')
                return redirect(url_for('autenticacion.catalogo_usuarios'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error al crear usuario: {str(e)}', 'error')
                print(f"Error de creación: {e}")
        
        return render_template('modulos/login/crear_usuario.html')


    @staticmethod
    @autenticacion_bp.route('/usuarios/editar/<int:usuario_id>', methods=['GET', 'POST'])
    @login_required
    def editar_usuario(usuario_id):
        """
        Método para editar usuarios (solo para administradores)
        """
        if current_user.rol != 'admin':
            flash('Acceso denegado', 'error')
            return redirect(url_for('principal'))
        
        usuario = Usuario.query.get_or_404(usuario_id)
        
        if request.method == 'POST':
            # Obtener datos del formulario
            nuevo_nombre_usuario = request.form['nombre_usuario']
            nuevo_correo = request.form['correo']
            nuevo_rol = request.form['rol']
            
            # Validar que el nuevo nombre de usuario o correo no existan ya
            usuario_existente = Usuario.query.filter(
                ((Usuario.nombre_usuario == nuevo_nombre_usuario) | (Usuario.correo == nuevo_correo)) 
                & (Usuario.id != usuario_id)
            ).first()
            
            if usuario_existente:
                flash('Nombre de usuario o correo ya registrados por otro usuario', 'error')
                return render_template('editar_usuario.html', usuario=usuario)
            
            # Actualizar datos
            usuario.nombre_usuario = nuevo_nombre_usuario
            usuario.correo = nuevo_correo
            usuario.rol = nuevo_rol
            
            try:
                db.session.commit()
                flash('Usuario actualizado exitosamente', 'success')
                return redirect(url_for('autenticacion.catalogo_usuarios'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error al actualizar usuario: {str(e)}', 'error')
                print(f"Error de actualización: {e}")
        
        # Para GET, renderizar formulario con datos existentes
        return render_template('modulos/login/editar_usuario.html', usuario=usuario)

    @staticmethod
    @autenticacion_bp.route('/usuarios/cambiar_estado/<int:usuario_id>')
    @login_required
    def cambiar_estado_usuario(usuario_id):
        """
        Método para cambiar el estado de un usuario (solo para administradores)
        """
        if current_user.rol != 'admin':
            flash('Acceso denegado', 'error')
            return redirect(url_for('principal'))
        
        usuario = Usuario.query.get_or_404(usuario_id)
        
        # Alternar estado del usuario
        if usuario.esta_activo:
            usuario.desactivar()
            flash('Usuario desactivado', 'warning')
        else:
            usuario.activar()
            flash('Usuario activado', 'success')
        
        return redirect(url_for('autenticacion.catalogo_usuarios'))
    @staticmethod
    @autenticacion_bp.route('/usuarios', methods=['GET'])
    @login_required
    def catalogo_usuarios():
        """
        Método para mostrar el catálogo de usuarios (solo para administradores)
        """
        if current_user.rol != 'admin':
            flash('Acceso denegado', 'error')
            return redirect(url_for('principal'))
        
        usuarios = Usuario.query.all()
        return render_template('modulos/login/catalogo_usuarios.html', usuarios=usuarios)
    