from flask import Blueprint, render_template, flash, current_app
from flask_wtf.csrf import generate_csrf

# Crear blueprint para las rutas principales
main_bp = Blueprint('main', __name__, template_folder='templates')

@main_bp.route('/')
def index():
    """Vista principal de la aplicación"""
    return render_template('modulos/login/iniciar_sesion.html', title='Cookie King - Sistema de Administración')

# Filtros personalizados para plantillas
@main_bp.app_template_filter('date_format')
def date_format(value, format='%d/%m/%Y'):
    """Formatear fechas para mostrar en plantillas"""
    if value:
        return value.strftime(format)
    return ""

# Manejadores de errores
@main_bp.app_errorhandler(404)
def page_not_found(e):
    """Página no encontrada"""
    return render_template('errors/404.html'), 404

@main_bp.app_errorhandler(500)
def internal_server_error(e):
    """Error interno del servidor"""
    return render_template('errors/500.html'), 500 