# modulos/compras/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from models import db
from modulos.compras.models import CompraInsumo, CompraDetalle
from modulos.compras.controllers import CompraController
from modulos.proveedores.controllers import ProveedorController
from modulos.ingredientes.controllers import IngredienteController
import json
from datetime import datetime

# Crear blueprint para las rutas de compras
compras_bp = Blueprint('compras', __name__, url_prefix='/compras')

@compras_bp.route('/')
@login_required
def index():
    """Vista principal para la administración de compras"""
    compras = CompraController.get_all_compras()
    
    # Preparar datos para la plantilla
    items_data = []
    for compra in compras:
        estatus_text = "Pagado" if compra.estatus == 1 else "Pendiente" if compra.estatus == 0 else "Cancelado"
        estatus_class = "bg-green-100 text-green-800" if compra.estatus == 1 else "bg-yellow-100 text-yellow-800" if compra.estatus == 0 else "bg-red-100 text-red-800"
        
        items_data.append({
            'id': compra.idCompra,
            'fields': [
                compra.fecha.strftime('%d/%m/%Y'),
                compra.proveedor.nombre_proveedor if compra.proveedor else "Desconocido",
                f"${compra.total:.2f}",
                f'<span class="px-2 py-1 rounded-full text-xs {estatus_class}">{estatus_text}</span>',
                compra.numero_factura or "N/A"
            ]
        })
    
    return render_template('modulos/compras/index.html', 
                          title="Administración de Compras",
                          items=items_data)

@compras_bp.route('/nueva', methods=['GET'])
@login_required
def nueva_compra():
    """Vista para crear una nueva compra"""
    # Obtener proveedores activos para el formulario
    proveedores = ProveedorController.get_active_proveedores()
    # Obtener ingredientes activos para el formulario
    ingredientes = IngredienteController.get_all_ingredientes()
    
    return render_template('modulos/compras/form.html',
                          title="Nueva Compra",
                          compra=None,
                          proveedores=proveedores,
                          ingredientes=ingredientes,
                          action=url_for('compras.guardar'))

@compras_bp.route('/editar/<int:compra_id>', methods=['GET'])
@login_required
def editar_compra(compra_id):
    """Vista para editar una compra existente"""
    compra = CompraController.get_compra_by_id(compra_id)
    
    if not compra:
        flash('Compra no encontrada', 'error')
        return redirect(url_for('compras.index'))
    
    # Obtener los detalles de la compra
    detalles = CompraController.get_detalles_compra(compra_id)
    
    # Obtener proveedores e ingredientes para el formulario
    proveedores = ProveedorController.get_active_proveedores()
    ingredientes = IngredienteController.get_all_ingredientes()
    
    return render_template('modulos/compras/form.html',
                          title="Editar Compra",
                          compra=compra,
                          detalles=detalles,
                          proveedores=proveedores,
                          ingredientes=ingredientes,
                          action=url_for('compras.guardar'))

@compras_bp.route('/guardar', methods=['POST'])
@login_required
def guardar():
    """Guardar una compra (nueva o actualizada)"""
    try:
        # Obtener los datos del formulario
        compra_id = request.form.get('id', '')
        fecha = request.form.get('fecha')
        id_proveedor = request.form.get('idProveedor')
        estatus = request.form.get('estatus')
        numero_factura = request.form.get('numero_factura')
        
        # Obtener los detalles de la compra (enviados como JSON)
        detalles_json = request.form.get('detalles', '[]')
        detalles_data = json.loads(detalles_json)
        
        # Validar datos básicos
        if not fecha or not id_proveedor or not detalles_data:
            flash('Todos los campos son obligatorios y debe haber al menos un detalle', 'error')
            return redirect(url_for('compras.index'))
        
        # Preparar datos de la compra
        data = {
            'fecha': fecha,
            'idProveedor': int(id_proveedor),
            'estatus': int(estatus),
            'numero_factura': numero_factura
        }
        
        if compra_id and compra_id.isdigit():
            # Actualizar compra existente
            compra = CompraController.update_compra(int(compra_id), data, detalles_data)
            if compra:
                flash('Compra actualizada exitosamente', 'success')
            else:
                flash('Error al actualizar la compra', 'error')
        else:
            # Crear nueva compra
            compra = CompraController.create_compra(data, detalles_data)
            flash('Compra registrada exitosamente', 'success')
        
        return redirect(url_for('compras.index'))
        
    except Exception as e:
        flash(f'Error al guardar la compra: {str(e)}', 'error')
        return redirect(url_for('compras.index'))

@compras_bp.route('/detalle/<int:compra_id>')
@login_required
def detalle(compra_id):
    """Ver detalles de una compra"""
    compra = CompraController.get_compra_by_id(compra_id)
    
    if not compra:
        flash('Compra no encontrada', 'error')
        return redirect(url_for('compras.index'))
    
    # Obtener los detalles de la compra
    detalles = CompraController.get_detalles_compra(compra_id)
    
    return render_template('modulos/compras/detalle.html',
                          title="Detalle de Compra",
                          compra=compra,
                          detalles=detalles)

@compras_bp.route('/eliminar/<int:compra_id>', methods=['POST'])
@login_required
def eliminar(compra_id):
    """Eliminar una compra"""
    if CompraController.delete_compra(compra_id):
        flash('Compra eliminada exitosamente', 'success')
    else:
        flash('Error al eliminar la compra', 'error')
    
    return redirect(url_for('compras.index'))

@compras_bp.route('/get_ingrediente/<int:ingrediente_id>')
@login_required
def get_ingrediente(ingrediente_id):
    """Obtener información de un ingrediente para el formulario"""
    ingrediente = IngredienteController.get_ingrediente_by_id(ingrediente_id)
    
    if not ingrediente:
        return jsonify({'error': 'Ingrediente no encontrado'}), 404
    
    return jsonify(ingrediente.to_dict())