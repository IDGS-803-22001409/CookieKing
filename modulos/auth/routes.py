from flask import Blueprint, request, redirect, url_for, flash, session, render_template
from flask_login import login_required, current_user, login_user
from .controllers import AuthController
from functools import wraps
from modulos.main.routes import main_bp

auth_bp = Blueprint('auth', __name__)

# Decorador para restringir acceso solo a roles específicos
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.rol != 'admin':
            flash('Acceso denegado. Solo administradores pueden acceder a esta página.', 'error')
            return redirect(url_for('main.root_redirect'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/iniciar_sesion', methods=['GET', 'POST'])
def iniciar_sesion():
    
    if current_user.is_authenticated:
        return redirect(url_for('main.root_redirect'))
        
    if request.method == 'POST':
        nombre_usuario = request.form.get('nombre_usuario')
        contrasena = request.form.get('contrasena')

        success, message = AuthController.iniciar_sesion(nombre_usuario, contrasena)
        flash(message, 'success' if success else 'error')

        if success:
            return redirect(url_for('auth.verificar_totp'))

    return render_template('modulos/auth/iniciar_sesion.html')

# En la función verificar_totp, modificamos la redirección:
@auth_bp.route('/verificar_totp', methods=['GET', 'POST'])
def verificar_totp():
    if not session.get('totp_data'):
        return redirect(url_for('auth.iniciar_sesion'))

    if request.method == 'POST':
        codigo = request.form.get('codigo_totp')
        success, message = AuthController.verificar_totp(codigo)
        flash(message, 'success' if success else 'error')

        if success:
            if current_user.rol == 'admin':
                return redirect(url_for('main.index'))
            elif current_user.rol == 'empleado':
                return redirect(url_for('main.index'))
            else:  # cliente y otros roles
                return redirect(url_for('main.cliente_portal'))

    return render_template('modulos/auth/verificar_totp.html')

@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for('main.root_redirect'))
        
    # Determinar el rol predeterminado
    rol_predeterminado = 'admin'  
    
    if request.method == 'POST':
        data = {
            'nombre_usuario': request.form.get('nombre_usuario'),
            'correo': request.form.get('correo'),
            'contrasena': request.form.get('contrasena'),
            'rol': request.form.get('rol', rol_predeterminado)
        }
        
        # Verificar si el registro es desde la zona de administración
        desde_admin = request.args.get('admin', '0') == '1'
        if not desde_admin and 'rol' in data and data['rol'] != 'cliente':
            data['rol'] = 'cliente'  # Asegurar que los auto-registros sean siempre como cliente

        success, message = AuthController.registrar_usuario(data)
        flash(message, 'success' if success else 'error')

        if success:
            return redirect(url_for('auth.iniciar_sesion'))

    return render_template('modulos/auth/registro.html')

@auth_bp.route('/logout')
@login_required
def cerrar_sesion():
    AuthController.cerrar_sesion()
    flash('Sesión cerrada correctamente', 'success')
    return redirect(url_for('main.root_redirect'))

@auth_bp.route('/usuarios')
@login_required
@admin_required
def catalogo_usuarios():
    # Importa Usuario solo cuando sea necesario
    from modulos.auth.models import Usuario
    usuarios = Usuario.query.all()
    return render_template('modulos/auth/catalogo_usuarios.html', usuarios=usuarios)

@auth_bp.route('/usuarios/crear', methods=['GET', 'POST'])
@login_required
@admin_required
def crear_usuario():
    if request.method == 'POST':
        data = {
            'nombre_usuario': request.form.get('nombre_usuario'),
            'correo': request.form.get('correo'),
            'contrasena': request.form.get('contrasena'),
            'rol': request.form.get('rol')
        }

        success, message = AuthController.crear_usuario_admin(data)
        flash(message, 'success' if success else 'error')

        if success:
            return redirect(url_for('auth.catalogo_usuarios'))

    return render_template('modulos/auth/crear_usuario.html')

@auth_bp.route('/usuarios/editar/<int:usuario_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_usuario(usuario_id):
    if request.method == 'POST':
        data = {
            'nombre_usuario': request.form.get('nombre_usuario'),
            'correo': request.form.get('correo'),
            'contrasena': request.form.get('contrasena'),
            'rol': request.form.get('rol')
        }

        success, message = AuthController.actualizar_usuario(usuario_id, data)
        flash(message, 'success' if success else 'error')

        if success:
            return redirect(url_for('auth.catalogo_usuarios'))

    # Importa Usuario solo cuando sea necesario
    from modulos.auth.models import Usuario
    usuario = Usuario.query.get_or_404(usuario_id)
    return render_template('modulos/auth/editar_usuario.html', usuario=usuario)

@auth_bp.route('/usuarios/cambiar_estado/<int:usuario_id>')
@login_required
@admin_required
def cambiar_estado_usuario(usuario_id):
    success, message = AuthController.cambiar_estado_usuario(usuario_id)
    flash(message, 'success' if success else 'error')
    return redirect(url_for('auth.catalogo_usuarios'))