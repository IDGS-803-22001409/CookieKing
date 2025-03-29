# modulos/auth/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user
from modulos.auth.controllers import AuthController
from modulos.auth.forms import LoginForm, RegisterForm, UserForm

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        if AuthController.login(form.username.data, form.password.data):
            next_page = request.args.get('next', url_for('main.index'))
            return redirect(next_page)
        else:
            flash('Credenciales inválidas', 'error')
    
    return render_template('modulos/auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    AuthController.logout()
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated and current_user.rol != 'admin':
        return redirect(url_for('main.index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        success, message = AuthController.register({
            'username': form.username.data,
            'email': form.email.data,
            'password': form.password.data,
            'nombre': form.nombre.data,
            'apellido': form.apellido.data,
            'rol': form.rol.data
        })
        
        if success:
            flash(message, 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(message, 'error')
    
    return render_template('modulos/auth/register.html', form=form)

@auth_bp.route('/usuarios')
@login_required
def usuarios():
    if current_user.rol != 'admin':
        flash('No tienes permisos para acceder a esta sección', 'error')
        return redirect(url_for('main.index'))
    
    usuarios = AuthController.get_all_usuarios()
    return render_template('modulos/auth/usuarios.html', usuarios=usuarios)

@auth_bp.route('/usuarios/nuevo', methods=['GET', 'POST'])
@login_required
def new_usuario():
    if current_user.rol != 'admin':
        flash('No tienes permisos para acceder a esta sección', 'error')
        return redirect(url_for('main.index'))
    
    form = UserForm()
    if form.validate_on_submit():
        success, message = AuthController.register({
            'username': form.username.data,
            'email': form.email.data,
            'password': form.password.data,
            'nombre': form.nombre.data,
            'apellido': form.apellido.data,
            'rol': form.rol.data
        })
        
        if success:
            flash(message, 'success')
            return redirect(url_for('auth.usuarios'))
        else:
            flash(message, 'error')
    
    return render_template('modulos/auth/usuario_form.html', form=form, title="Nuevo Usuario")

@auth_bp.route('/usuarios/editar/<int:usuario_id>', methods=['GET', 'POST'])
@login_required
def edit_usuario(usuario_id):
    if current_user.rol != 'admin' and current_user.id != usuario_id:
        flash('No tienes permisos para acceder a esta sección', 'error')
        return redirect(url_for('main.index'))
    
    usuario = AuthController.get_usuario_by_id(usuario_id)
    if not usuario:
        flash('Usuario no encontrado', 'error')
        return redirect(url_for('auth.usuarios'))
    
    form = UserForm(obj=usuario)
    if form.validate_on_submit():
        success, message = AuthController.update_usuario(usuario_id, {
            'username': form.username.data,
            'email': form.email.data,
            'password': form.password.data if form.password.data else None,
            'nombre': form.nombre.data,
            'apellido': form.apellido.data,
            'rol': form.rol.data,
            'activo': form.activo.data
        })
        
        if success:
            flash(message, 'success')
            return redirect(url_for('auth.usuarios'))
        else:
            flash(message, 'error')
    
    return render_template('modulos/auth/usuario_form.html', form=form, title="Editar Usuario")

@auth_bp.route('/usuarios/eliminar/<int:usuario_id>', methods=['POST'])
@login_required
def delete_usuario(usuario_id):
    if current_user.rol != 'admin':
        flash('No tienes permisos para acceder a esta sección', 'error')
        return redirect(url_for('main.index'))
    
    success, message = AuthController.delete_usuario(usuario_id)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('auth.usuarios'))