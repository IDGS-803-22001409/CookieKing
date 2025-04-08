# modulos/clientes/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from models import db
from modulos.main.routes import roles_required
from modulos.clientes.models import Cliente
from modulos.clientes.forms import ClienteForm, create_cliente_form
from modulos.clientes.controllers import ClienteController

# Crear blueprint para las rutas de clientes
clientes_bp = Blueprint('clientes', __name__, url_prefix='/clientes')

@clientes_bp.route('/')
@roles_required('admin', 'empleado')
@login_required
def index():
    """Vista principal para la administración de clientes"""
    # Agregar log para depuración
    print("Accediendo a la vista index de clientes")
    
    # Obtener todos los clientes usando el controlador
    clientes = ClienteController.get_all_clientes()
    
    return render_template('modulos/clientes/index.html', clientes=clientes)

@clientes_bp.route('/admin')
@login_required
def admin():
    """Vista de administración con CRUD para clientes"""
    print("Accediendo a la vista admin de clientes")
    
    # Obtener todos los clientes usando el controlador
    clientes = ClienteController.get_all_clientes()
    
    # Convertir los elementos de la base de datos a diccionarios para la plantilla
    items_data = []
    for cliente in clientes:
        items_data.append({
            'id': cliente.idCliente,
            'fields': [
                cliente.nombreCliente,
                cliente.fechaNacimiento.strftime('%d/%m/%Y') if cliente.fechaNacimiento else "N/A",
                cliente.telefono or "N/A",
                cliente.correo or "N/A",
                "Activo" if cliente.estatus == 1 else "Inactivo"
            ]
        })
    
    # Definir los encabezados de la tabla
    headers = ['Nombre', 'Fecha de Nacimiento', 'Teléfono', 'Correo', 'Estatus']
    
    # Crear campos del formulario para el modal
    form_fields = create_cliente_form()
    
    return render_template('modulos/clientes/crud_layout.html', 
                          crud_title='Administración de Clientes',
                          modal_title='Cliente',
                          table_headers=headers,
                          items=items_data,
                          form_fields=form_fields,
                          form_action=url_for('clientes.save'))

@clientes_bp.route('/save', methods=['POST'])
@login_required
def save():
    """Guardar un cliente nuevo o actualizado"""
    # Crear una instancia del formulario y validar
    form = ClienteForm()
    
    if form.validate_on_submit():
        cliente_id = request.form.get('id', '')
        
        # Recopilar datos del formulario
        data = {
            'nombreCliente': form.nombreCliente.data,
            'fechaNacimiento': form.fechaNacimiento.data.strftime('%Y-%m-%d') if form.fechaNacimiento.data else None,
            'telefono': form.telefono.data,
            'correo': form.correo.data,
            'estatus': 1 if form.estatus.data == '1' else 0
        }
        
        if cliente_id and cliente_id.isdigit():
            # Actualizar cliente existente usando el controlador
            cliente = ClienteController.update_cliente(int(cliente_id), data)
            if cliente:
                flash('Cliente actualizado exitosamente', 'success')
            else:
                flash('No se encontró el cliente a actualizar', 'error')
        else:
            # Crear nuevo cliente usando el controlador
            cliente = ClienteController.create_cliente(data)
            flash('Cliente creado exitosamente', 'success')
        
        return redirect(url_for('clientes.index'))
    
    # Si la validación del formulario falla
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"Error en {getattr(form, field).label.text}: {error}", 'error')
    
    return redirect(url_for('clientes.index'))

@clientes_bp.route('/get/<int:cliente_id>')
@login_required
def get_cliente(cliente_id):
    """Obtener datos de un cliente para solicitudes AJAX"""
    cliente = ClienteController.get_cliente_by_id(cliente_id)
    
    if not cliente:
        return jsonify({"error": "Cliente no encontrado"}), 404
    
    return jsonify(cliente.to_dict())

@clientes_bp.route('/delete/<int:cliente_id>', methods=['POST'])
@login_required
def delete(cliente_id):
    """Eliminar un cliente"""
    # Verificar si el cliente puede ser eliminado
    if not ClienteController.can_delete_cliente(cliente_id):
        flash('No se puede eliminar este cliente porque tiene ventas asociadas. Se ha marcado como inactivo.', 'warning')
        
        # Marcar como inactivo en lugar de eliminar
        cliente = ClienteController.get_cliente_by_id(cliente_id)
        if cliente:
            cliente.estatus = 0
            db.session.commit()
        
        # Para solicitudes AJAX, devolver respuesta JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': 'Cliente marcado como inactivo'})
        
        return redirect(url_for('clientes.index'))
    
    # Eliminar el cliente
    if ClienteController.delete_cliente(cliente_id):
        flash('Cliente eliminado exitosamente', 'success')
        
        # Para solicitudes AJAX, devolver respuesta JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True})
    else:
        flash('No se pudo eliminar el cliente', 'error')
        
        # Para solicitudes AJAX, devolver respuesta JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'No se pudo eliminar el cliente'})
    
    return redirect(url_for('clientes.index'))

@clientes_bp.route('/details/<int:cliente_id>')
@login_required
def details(cliente_id):
    """Ver detalles de un cliente"""
    cliente = ClienteController.get_cliente_by_id(cliente_id)
    
    if not cliente:
        flash('Cliente no encontrado', 'error')
        return redirect(url_for('clientes.index'))
    
    return render_template('modulos/clientes/details.html', cliente=cliente)