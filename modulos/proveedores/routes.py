# modulos/proveedores/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from modulos.main.routes import roles_required
from models import db
from modulos.proveedores.models import Proveedor
from modulos.proveedores.forms import ProveedorForm, create_proveedor_form
from modulos.proveedores.controllers import ProveedorController

# Crear blueprint para las rutas de proveedores
proveedores_bp = Blueprint('proveedores', __name__, url_prefix='/proveedores')

@proveedores_bp.route('/')
@login_required
@roles_required("admin","empleado")
def index():
    """Vista principal para la administración de proveedores"""
    proveedores = ProveedorController.get_all_proveedores()
    
    items_data = []
    for proveedor in proveedores:
        items_data.append({
            'id': proveedor.idProveedor,
            'fields': [
                proveedor.nombre_proveedor,
                proveedor.telefono or "-",
                proveedor.correo or "-",
                proveedor.direccion or "-",
                proveedor.rfc or "-",
                "Activo" if proveedor.estatus == 1 else "Inactivo"
            ]
        })
    
    headers = ['Nombre', 'Teléfono', 'Correo', 'Dirección', 'RFC', 'Estatus']
    
    # Crear campos del formulario para el modal
    form_fields = create_proveedor_form()
    
    return render_template('modulos/proveedores/crud_layout.html', 
                          crud_title='Administración de Proveedores',
                          modal_title='Proveedor',
                          table_headers=headers,
                          items=items_data,
                          form_fields=form_fields,
                          form_action=url_for('proveedores.save'))

@proveedores_bp.route('/save', methods=['POST'])
def save():
    """Guardar un proveedor nuevo o actualizado"""    
    form = ProveedorForm()
    
    if form.validate_on_submit():
        proveedor_id = request.form.get('id', '')
                
        data = {
            'nombre_proveedor': form.nombre_proveedor.data,
            'telefono': form.telefono.data,
            'correo': form.correo.data,
            'direccion': form.direccion.data,
            'rfc': form.rfc.data,
            'estatus': 1 if form.estatus.data == '1' else 0
        }
        
        if proveedor_id and proveedor_id.isdigit():
            # Actualizar proveedor existente usando el controlador
            proveedor = ProveedorController.update_proveedor(int(proveedor_id), data)
            if proveedor:
                flash('Proveedor actualizado exitosamente', 'success')
            else:
                flash('No se encontró el proveedor a actualizar', 'error')
        else:
            # Crear nuevo proveedor usando el controlador
            proveedor = ProveedorController.create_proveedor(data)
            flash('Proveedor creado exitosamente', 'success')
        
        return redirect(url_for('proveedores.index'))
    
    # Si la validación del formulario falla
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"Error en {getattr(form, field).label.text}: {error}", 'error')
    
    return redirect(url_for('proveedores.index'))

@proveedores_bp.route('/get/<int:proveedor_id>')
def get_proveedor(proveedor_id):
    """Obtener datos de un proveedor para solicitudes AJAX"""
    proveedor = ProveedorController.get_proveedor_by_id(proveedor_id)
    
    if not proveedor:
        return jsonify({"error": "Proveedor no encontrado"}), 404
    
    return jsonify(proveedor.to_dict())

@proveedores_bp.route('/delete/<int:proveedor_id>', methods=['POST'])
def delete(proveedor_id):
    """Eliminar un proveedor"""
    # Verificar si el proveedor puede ser eliminado
    if not ProveedorController.can_delete_proveedor(proveedor_id):
        flash('No se puede eliminar este proveedor porque tiene compras asociadas. Se ha marcado como inactivo.', 'warning')
        
        # Marcar como inactivo en lugar de eliminar
        proveedor = ProveedorController.get_proveedor_by_id(proveedor_id)
        if proveedor:
            proveedor.estatus = 0
            db.session.commit()
    else:
        # Eliminar el proveedor
        if ProveedorController.delete_proveedor(proveedor_id):
            flash('Proveedor eliminado exitosamente', 'success')
        else:
            flash('No se pudo eliminar el proveedor', 'error')
    
    # Para solicitudes AJAX, devolver respuesta JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True})
        
    return redirect(url_for('proveedores.index'))

@proveedores_bp.route('/details/<int:proveedor_id>')
@login_required
def details(proveedor_id):
    """Ver detalles de un proveedor"""
    proveedor = ProveedorController.get_proveedor_by_id(proveedor_id)
    
    if not proveedor:
        flash('Proveedor no encontrado', 'error')
        return redirect(url_for('proveedores.index'))
    
    return render_template('modulos/proveedores/details.html', proveedor=proveedor)