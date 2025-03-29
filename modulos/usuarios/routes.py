from flask import Blueprint, render_template, redirect, url_for

# Crear blueprint para las rutas de usuarios
usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')

@usuarios_bp.route('/')
def index():
    """Vista principal para la administración de usuarios"""
    return render_template('modulos/usuarios/index.html')