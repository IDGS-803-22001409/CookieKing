from flask import Blueprint, render_template, redirect, url_for

# Crear blueprint para las rutas de ingredientes
ingredientes_bp = Blueprint('ingredientes', __name__, url_prefix='/ingredientes')

@ingredientes_bp.route('/')
def index():
    """Vista principal para la administración de ingredientes"""
    return render_template('modulos/ingredientes/index.html')