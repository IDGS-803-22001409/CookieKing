from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import db
from flask_login import login_required
from modulos.main.routes import roles_required
from modulos.galletas.models import Galletas
from modulos.galletas.forms import GalletaForm, create_galleta_form
from modulos.galletas.controllers import GalletaController

# Crear blueprint para las rutas de galletas
galletas_bp = Blueprint('galletas', __name__, url_prefix='/galletas')

@galletas_bp.route('/')
@login_required
@roles_required('admin', 'empleado')
def index():
    """Vista principal para la administración de galletas"""
    # Obtener todas las galletas usando el controlador
    galletas = GalletaController.get_all_galletas()
    
    # Convertir los elementos de la base de datos a diccionarios para la plantilla
    items_data = []
    for galleta in galletas:
        items_data.append({
            'id': galleta.idGalleta,
            'fields': [
                galleta.nombreGalleta,
                galleta.descripcion[:50] + '...' if galleta.descripcion and len(galleta.descripcion) > 50 else galleta.descripcion,
                galleta.estado,
                f"{galleta.peso_por_unidad} g",
                f"${galleta.precio_unitario:.2f}",
                "Activo" if galleta.estatus == 1 else "Inactivo"
            ]
        })
    
    # Definir los encabezados de la tabla
    headers = ['Nombre', 'Descripción', 'Estado', 'Peso', 'Precio', 'Estatus']
    
    # Crear campos del formulario para el modal
    form_fields = create_galleta_form()
    
    return render_template('modulos/galletas/crud_layout.html', 
                          crud_title='Administración de Galletas',                          
                          modal_title='Galleta',
                          table_headers=headers,
                          items=items_data,
                          form_fields=form_fields,
                          form_action=url_for('galletas.save'))

@galletas_bp.route('/save', methods=['POST'])
@login_required
def save():
    """Guardar una galleta nueva o actualizada"""
    # Crear una instancia del formulario y validar
    form = GalletaForm()
    
    if form.validate_on_submit():
        galleta_id = request.form.get('id', '')
        
        # Recopilar datos del formulario
        data = {
            'nombreGalleta': form.nombreGalleta.data,
            'descripcion': form.descripcion.data,
            'estado': form.estado.data,
            'peso_por_unidad': form.peso_por_unidad.data,
            'precio_unitario': form.precio_unitario.data,
            'estatus': 1 if form.estatus.data == '1' else 0
        }
        
        if galleta_id and galleta_id.isdigit():
            # Actualizar galleta existente usando el controlador
            galleta = GalletaController.update_galleta(int(galleta_id), data)
            if galleta:
                flash('Galleta actualizada exitosamente', 'success')
            else:
                flash('No se encontró la galleta a actualizar', 'error')
        else:
            # Crear nueva galleta usando el controlador
            galleta = GalletaController.create_galleta(data)
            flash('Galleta creada exitosamente', 'success')
        
        return redirect(url_for('galletas.index'))
    
    # Si la validación del formulario falla
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"Error en {getattr(form, field).label.text}: {error}", 'error')
    
    return redirect(url_for('galletas.index'))

@galletas_bp.route('/get/<int:galleta_id>')
@login_required
def get_galleta(galleta_id):
    """Obtener datos de una galleta para solicitudes AJAX"""
    galleta = GalletaController.get_galleta_by_id(galleta_id)
    
    if not galleta:
        return jsonify({"error": "Galleta no encontrada"}), 404
    
    return jsonify(galleta.to_dict())

@galletas_bp.route('/delete/<int:galleta_id>', methods=['POST'])
def delete(galleta_id):
    """Eliminar una galleta"""
    # Verificar si la galleta puede ser eliminada
    if not GalletaController.can_delete_galleta(galleta_id):
        flash('No se puede eliminar esta galleta porque tiene recetas asociadas', 'error')
        
        # Para solicitudes AJAX, devolver respuesta JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'No se puede eliminar esta galleta porque tiene recetas asociadas'})
        
        return redirect(url_for('galletas.index'))
    
    # Eliminar la galleta
    if GalletaController.delete_galleta(galleta_id):
        flash('Galleta eliminada exitosamente', 'success')
        
        # Para solicitudes AJAX, devolver respuesta JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True})
    else:
        flash('No se pudo eliminar la galleta', 'error')
        
        # Para solicitudes AJAX, devolver respuesta JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'No se pudo eliminar la galleta'})
    
    return redirect(url_for('galletas.index'))

@galletas_bp.route('/details/<int:galleta_id>')
@login_required
def details(galleta_id):
    """Ver detalles de una galleta"""
    galleta = GalletaController.get_galleta_by_id(galleta_id)
    
    if not galleta:
        flash('Galleta no encontrada', 'error')
        return redirect(url_for('galletas.index'))
    
    return render_template('modulos/galletas/details.html', galleta=galleta) 