from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
from models import db, RecetaIngrediente
from modulos.recetas.models import Receta
from modulos.recetas.forms import create_receta_form, RecetaForm
from modulos.recetas.controllers import RecetaController
from modulos.galletas.models import Galleta
from modulos.galletas.controllers import GalletaController
from modulos.ingredientes.models import Ingrediente
from modulos.ingredientes.controllers import IngredienteController

# Crear blueprint para las rutas de recetas
recetas_bp = Blueprint('recetas', __name__, url_prefix='/recetas')

@recetas_bp.route('/')
def index():
    """Vista principal para la administración de recetas"""
    # Obtener todas las recetas con sus tipos de galleta relacionados
    recetas = RecetaController.get_all_recetas()
    
    # Convertir los elementos de la base de datos a diccionarios para la plantilla
    items_data = []
    for receta in recetas:
        items_data.append({
            'id': receta.idReceta,
            'fields': [
                receta.nombreReceta,
                receta.galleta.nombreGalleta,
                f"{receta.galletasProducidas} unidades",
                "Activo" if receta.estatus == 1 else "Inactivo"
            ]
        })
    
    # Definir los encabezados de la tabla
    headers = ['Nombre', 'Tipo de Galleta', 'Producción', 'Estatus']
    
    # Obtener todos los tipos de galleta para el dropdown del formulario
    galletas = GalletaController.get_active_galletas()
    
    # Crear campos del formulario para el modal
    form_fields = create_receta_form(galletas=galletas)
    
    return render_template('modulos/recetas/crud_layout.html', 
                          crud_title='Administración de Recetas',
                          modal_title='Receta',
                          table_headers=headers,
                          items=items_data,
                          form_fields=form_fields,
                          form_action=url_for('recetas.save'))

@recetas_bp.route('/save', methods=['POST'])
def save():
    """Guardar una receta nueva o actualizada"""
    # Crear una instancia del formulario y validar
    form = RecetaForm()
    
    # Obtener todos los tipos de galleta para validación del formulario
    galletas = GalletaController.get_active_galletas()
    form.idGalleta.choices = [(g.idGalleta, g.nombreGalleta) for g in galletas]
    
    # Forzar la validación para el campo estatus
    form.estatus.choices = [('1', 'Activo'), ('0', 'Inactivo')]
    
    if form.validate_on_submit():
        receta_id = request.form.get('id', '')
        
        # Recopilar datos del formulario
        data = {
            'nombreReceta': form.nombreReceta.data,
            'instruccionesReceta': form.instruccionesReceta.data,
            'galletasProducidas': form.galletasProducidas.data,
            'idGalleta': form.idGalleta.data,
            'estatus': 1 if form.estatus.data == '1' else 0
        }
        
        if receta_id and receta_id.isdigit():
            # Actualizar receta existente
            receta = RecetaController.update_receta(int(receta_id), data)
            if receta:
                flash('Receta actualizada exitosamente', 'success')
            else:
                flash('No se encontró la receta a actualizar', 'error')
        else:
            # Crear nueva receta
            receta = RecetaController.create_receta(data)
            flash('Receta creada exitosamente', 'success')
        
        return redirect(url_for('recetas.index'))
    
    # Si la validación del formulario falla
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"Error en {getattr(form, field).label.text}: {error}", 'error')
    
    return redirect(url_for('recetas.index'))

@recetas_bp.route('/get/<int:receta_id>')
def get_receta(receta_id):
    """Obtener datos de una receta para solicitudes AJAX"""
    receta = RecetaController.get_receta_by_id(receta_id)
    
    if not receta:
        return jsonify({"error": "Receta no encontrada"}), 404
    
    return jsonify(receta.to_dict())

@recetas_bp.route('/delete/<int:receta_id>', methods=['POST'])
def delete(receta_id):
    """Eliminar una receta"""
    if RecetaController.delete_receta(receta_id):
        flash('Receta eliminada exitosamente', 'success')
        
        # Para solicitudes AJAX, devolver respuesta JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True})
    else:
        flash('No se pudo eliminar la receta', 'error')
        
        # Para solicitudes AJAX, devolver respuesta JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'No se pudo eliminar la receta'})
    
    return redirect(url_for('recetas.index'))

@recetas_bp.route('/details/<int:receta_id>')
def details(receta_id):
    """Ver detalles de una receta incluyendo ingredientes"""
    receta = RecetaController.get_receta_by_id(receta_id)
    
    if not receta:
        flash('Receta no encontrada', 'error')
        return redirect(url_for('recetas.index'))
    
    # Obtener todos los ingredientes para esta receta
    receta_ingredientes = RecetaIngrediente.query.filter_by(receta_id=receta_id).join(Ingrediente).all()
    
    ingredientes = []
    for ri in receta_ingredientes:
        ingredientes.append({
            'nombre': ri.ingrediente.nombreIngrediente,
            'cantidad': ri.cantidad,
            'unidad': ri.ingrediente.unidad or ''
        })
    
    return render_template('modulos/recetas/details.html',
                          receta=receta,
                          ingredientes=ingredientes)

# Rutas para administrar los ingredientes de las recetas
@recetas_bp.route('/ingredientes/<int:receta_id>')
def ingredientes(receta_id):
    """Administrar ingredientes para una receta específica"""
    receta = RecetaController.get_receta_by_id(receta_id)
    
    if not receta:
        flash('Receta no encontrada', 'error')
        return redirect(url_for('recetas.index'))
    
    # Obtener ingredientes actuales en la receta
    receta_ingredientes = RecetaIngrediente.query.filter_by(receta_id=receta_id).join(Ingrediente).all()
    
    # Formatear los ingredientes actuales para la plantilla
    current_ingredientes = []
    for ri in receta_ingredientes:
        current_ingredientes.append({
            'id': ri.ingrediente.idIngrediente,
            'nombre': ri.ingrediente.nombreIngrediente,
            'cantidad': ri.cantidad,
            'unidad': ri.ingrediente.unidad or ''
        })
    
    # Obtener todos los ingredientes disponibles que no están ya en la receta
    todos_ingredientes = IngredienteController.get_all_ingredientes()
    
    # Filtrar ingredientes ya utilizados
    ingredientes_utilizados = [ri.ingrediente_id for ri in receta_ingredientes]
    available_ingredientes = []
    
    for ing in todos_ingredientes:
        if ing.idIngrediente not in ingredientes_utilizados:
            available_ingredientes.append({
                'id': ing.idIngrediente,
                'nombre': ing.nombreIngrediente
            })
    
    return render_template('modulos/recetas/ingredientes.html',
                          receta=receta,
                          current_ingredientes=current_ingredientes,
                          available_ingredientes=available_ingredientes)

@recetas_bp.route('/add_ingrediente', methods=['POST'])
def add_ingrediente():
    """Añadir un ingrediente a una receta"""
    receta_id = request.form.get('receta_id')
    ingrediente_id = request.form.get('ingrediente_id')
    cantidad = request.form.get('cantidad')
    
    if not receta_id or not ingrediente_id or not cantidad:
        flash('Todos los campos son requeridos', 'error')
        return redirect(url_for('recetas.ingredientes', receta_id=receta_id))
    
    try:
        # Verificar si ya existe esta relación
        existing = RecetaIngrediente.query.filter_by(
            receta_id=receta_id, 
            ingrediente_id=ingrediente_id
        ).first()
        
        if existing:
            flash('Este ingrediente ya está en la receta', 'error')
        else:
            # Crear nueva relación entre receta e ingrediente
            nueva_relacion = RecetaIngrediente(
                receta_id=receta_id,
                ingrediente_id=ingrediente_id,
                cantidad=cantidad
            )
            db.session.add(nueva_relacion)
            db.session.commit()
            flash('Ingrediente añadido correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al añadir ingrediente: {str(e)}', 'error')
    
    return redirect(url_for('recetas.ingredientes', receta_id=receta_id))

@recetas_bp.route('/delete_ingrediente', methods=['POST'])
def delete_ingrediente():
    """Eliminar un ingrediente de una receta"""
    receta_id = request.form.get('receta_id')
    ingrediente_id = request.form.get('ingrediente_id')
    
    if not receta_id or not ingrediente_id:
        flash('Información incompleta', 'error')
        return redirect(url_for('recetas.ingredientes', receta_id=receta_id))
    
    try:
        # Buscar y eliminar la relación
        relacion = RecetaIngrediente.query.filter_by(
            receta_id=receta_id, 
            ingrediente_id=ingrediente_id
        ).first()
        
        if relacion:
            db.session.delete(relacion)
            db.session.commit()
            flash('Ingrediente eliminado correctamente', 'success')
        else:
            flash('No se encontró el ingrediente en la receta', 'error')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar ingrediente: {str(e)}', 'error')
    
    return redirect(url_for('recetas.ingredientes', receta_id=receta_id))