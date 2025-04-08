from flask import Blueprint, render_template, redirect, url_for
from modulos.main.routes import roles_required

usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')

@usuarios_bp.route('/')
@roles_required('admin', 'empleado')
def index():
    """Vista principal para la administración de usuarios"""
    return render_template('modulos/usuarios/index.html')