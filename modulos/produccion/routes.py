from flask import Blueprint, render_template, redirect, url_for
from models import db
from modulos.galletas.models import Galletas

# Crear blueprint para las rutas de producción
produccion_bp = Blueprint('produccion', __name__, url_prefix='/produccion')


@produccion_bp.route('/')
def index():
    """Vista principal para la administración de producción"""
    return render_template('modulos/produccion/index.html')

@produccion_bp.route('/inventarioGalletas', methods=['GET'])
def inventario_galletas():
    """Vista para inventario de galletas"""
    galletas = Galletas.query.all()
    return render_template('modulos/produccion/inventarioGalletas.html', galletas=galletas)

@produccion_bp.route('/solicitud')
def solicitud():
    """Vista para solicitar producción"""
    return render_template('modulos/produccion/solicitud.html')

@produccion_bp.route('/inventario')
def inventario():
    """Vista para inventario de galletas"""
    return render_template('modulos/produccion/inventario.html')