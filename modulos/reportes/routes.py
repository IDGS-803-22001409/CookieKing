from flask import Blueprint, render_template, redirect, url_for

# Crear blueprint para las rutas de reportes
reportes_bp = Blueprint('reportes', __name__, url_prefix='/reportes')

@reportes_bp.route('/')
def index():
    """Vista principal para reportes"""
    return render_template('modulos/reportes/index.html')