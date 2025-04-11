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
                f"{galleta.peso_por_unidad} kg",
                f"${galleta.precio_unitario:.2f}",
                "Activo" if galleta.estatus == 1 else "Inactivo"
            ]
        })
    
    # Definir los encabezados de la tabla
    headers = ['Nombre', 'Descripción', 'Estado', 'Peso', 'Precio', 'Estatus']
    
    # Crear campos del formulario para el modal
    form_fields = create_galleta_form()
    
    return render_template('modulos/galletas/index.html', 
                          crud_title='Administración de Galletas',                          
                          modal_title='Galleta',
                          table_headers=headers,
                          items=items_data,
                          form_fields=form_fields,
                          form_action=url_for('galletas.save'))

@galletas_bp.route('/save', methods=['POST'])
@login_required
@roles_required('admin', 'empleado')
def save():
    """Guardar una galleta nueva o actualizada"""
    try:
        print("Recibiendo datos del formulario:", request.form)
        print("Archivos recibidos:", request.files)
        
        # Obtener datos del formulario
        nombreGalleta = request.form.get('nombreGalleta')
        descripcion = request.form.get('descripcion')
        estado = request.form.get('estado')
        
        # Convertir a float con manejo de error
        try:
            peso_por_unidad = float(request.form.get('peso_por_unidad', 0))
        except ValueError:
            peso_por_unidad = 0
            
        try:
            precio_unitario = float(request.form.get('precio_unitario', 0))
        except ValueError:
            precio_unitario = 0
            
        estatus = int(request.form.get('estatus', 1))
        
        # Verificar datos obligatorios
        if not nombreGalleta or not estado:
            flash('Nombre y estado son campos obligatorios', 'error')
            return redirect(url_for('galletas.index'))

        # Crear la galleta
        galleta = Galletas(
            nombreGalleta=nombreGalleta,
            descripcion=descripcion,
            estado=estado,
            peso_por_unidad=peso_por_unidad,
            precio_unitario=precio_unitario,
            estatus=estatus
        )
        
        # Procesar la foto
        foto = request.files.get('foto')
        if foto and foto.filename:
            try:
                # Guarda los datos binarios directamente
                foto_data = foto.read()
                galleta.foto = foto_data  
            except Exception as e:
                flash(f'Error al procesar la imagen: {str(e)}', 'error')
                print(f"Error con la imagen: {str(e)}")
        
        # IMPORTANTE: Agregar la galleta a la sesión
        db.session.add(galleta)
        # Ahora hacemos el commit
        db.session.commit()
        flash('Galleta guardada exitosamente', 'success')
        
    except Exception as e:
        db.session.rollback()  # Importante: hacer rollback en caso de error
        flash(f'Error al guardar la galleta: {str(e)}', 'error')
        print(f"Error general: {str(e)}")
    
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
@roles_required('admin', 'empleado')
def details(galleta_id):
    """Ver detalles de una galleta"""
    galleta = GalletaController.get_galleta_by_id(galleta_id)
    # mostrar la foto de la galleta
    
    
    if not galleta:
        flash('Galleta no encontrada', 'error')
        return redirect(url_for('galletas.index'))
    
    return render_template('modulos/galletas/details.html', galleta=galleta)