from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required

# Crear blueprint para las rutas de reportes
reportes_bp = Blueprint('reportes', __name__, url_prefix='/reportes')

@reportes_bp.route('/')
@login_required
def index():
    """Vista principal para reportes"""
    return render_template('modulos/reportes/index.html')