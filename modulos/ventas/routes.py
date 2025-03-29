# modulos/ventas/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from models import db
from modulos.ventas.models import Venta, DetalleVenta
from modulos.ventas.controllers import VentaController
from modulos.clientes.controllers import ClienteController
from modulos.galletas.controllers import GalletaController
import json
from datetime import datetime, timedelta

# Crear blueprint para las rutas de ventas
ventas_bp = Blueprint('ventas', __name__, url_prefix='/ventas')

@ventas_bp.route('/')
@login_required
def index():
    """Vista principal para la administración de ventas"""
    ventas = VentaController.get_all_ventas()
    
    # Preparar datos para la plantilla
    items_data = []
    for venta in ventas:
        cliente_nombre = venta.cliente.nombreCliente if venta.cliente else "Cliente General"
        estatus_text = "Completada" if venta.estatus == 1 else "Pendiente" if venta.estatus == 0 else "Cancelada"
        estatus_class = "bg-green-100 text-green-800" if venta.estatus == 1 else "bg-yellow-100 text-yellow-800" if venta.estatus == 0 else "bg-red-100 text-red-800"
        
        # Calcular total
        total = 0
        for detalle in venta.detalles:
            if detalle.tipo_venta == 1:  # Individual
                precio = detalle.galleta.precio_unitario
            else:  # Paquete
                precio = detalle.galleta.precio_unitario * 0.9  # Ejemplo
            
            total += precio * detalle.cantidad
        
        items_data.append({
            'id': venta.idVenta,
            'fields': [
                venta.fechaVenta.strftime('%d/%m/%Y'),
                cliente_nombre,
                f"${total:.2f}",
                f'<span class="px-2 py-1 rounded-full text-xs {estatus_class}">{estatus_text}</span>'
            ]
        })
    
    return render_template('modulos/ventas/index.html', 
                          title="Administración de Ventas",
                          items=items_data)

@ventas_bp.route('/nueva', methods=['GET'])
@login_required
def nueva_venta():
    """Vista para crear una nueva venta"""
    # Obtener clientes activos para el formulario
    clientes = ClienteController.get_active_clientes()
    # Obtener galletas disponibles para el formulario
    galletas = GalletaController.get_active_galletas()
    
    return render_template('modulos/ventas/form.html',
                          title="Nueva Venta",
                          venta=None,
                          clientes=clientes,
                          galletas=galletas,
                          action=url_for('ventas.guardar'))

@ventas_bp.route('/editar/<int:venta_id>', methods=['GET'])
@login_required
def editar_venta(venta_id):
    """Vista para editar una venta existente"""
    venta = VentaController.get_venta_by_id(venta_id)
    
    if not venta:
        flash('Venta no encontrada', 'error')
        return redirect(url_for('ventas.index'))
    
    # Obtener los detalles de la venta
    detalles = VentaController.get_detalles_venta(venta_id)
    
    # Obtener clientes y galletas para el formulario
    clientes = ClienteController.get_active_clientes()
    galletas = GalletaController.get_active_galletas()
    
    return render_template('modulos/ventas/form.html',
                          title="Editar Venta",
                          venta=venta,
                          detalles=detalles,
                          clientes=clientes,
                          galletas=galletas,
                          action=url_for('ventas.guardar'))

@ventas_bp.route('/guardar', methods=['POST'])
@login_required
def guardar():
    """Guardar una venta (nueva o actualizada)"""
    try:
        # Obtener los datos del formulario
        venta_id = request.form.get('id', '')
        fecha = request.form.get('fecha')
        id_cliente = request.form.get('idCliente')
        estatus = request.form.get('estatus')
        
        # Obtener los detalles de la venta (enviados como JSON)
        detalles_json = request.form.get('detalles', '[]')
        detalles_data = json.loads(detalles_json)
        
        # Validar datos básicos
        if not fecha or not detalles_data:
            flash('La fecha y al menos un detalle son obligatorios', 'error')
            return redirect(url_for('ventas.index'))
        
        # Preparar datos de la venta
        data = {
            'fechaVenta': fecha,
            'IdCliente': int(id_cliente) if id_cliente else None,
            'estatus': int(estatus)
        }
        
        if venta_id and venta_id.isdigit():
            # Actualizar venta existente
            venta = VentaController.update_venta(int(venta_id), data, detalles_data)
            if venta:
                flash('Venta actualizada exitosamente', 'success')
            else:
                flash('Error al actualizar la venta', 'error')
        else:
            # Crear nueva venta
            venta = VentaController.create_venta(data, detalles_data)
            flash('Venta registrada exitosamente', 'success')
        
        return redirect(url_for('ventas.index'))
        
    except Exception as e:
        flash(f'Error al guardar la venta: {str(e)}', 'error')
        return redirect(url_for('ventas.index'))

@ventas_bp.route('/detalle/<int:venta_id>')
@login_required
def detalle(venta_id):
    """Ver detalles de una venta"""
    venta = VentaController.get_venta_by_id(venta_id)
    
    if not venta:
        flash('Venta no encontrada', 'error')
        return redirect(url_for('ventas.index'))
    
    # Obtener los detalles de la venta
    detalles = VentaController.get_detalles_venta(venta_id)
    
    # Calcular total
    total = 0
    detalles_con_subtotal = []
    
    for detalle in detalles:
        if detalle.tipo_venta == 1:  # Individual
            tipo = "Individual"
            precio = detalle.galleta.precio_unitario
        else:  # Paquete
            tipo = "Paquete"
            precio = detalle.galleta.precio_unitario * 0.9  # Ejemplo
        
        subtotal = precio * detalle.cantidad
        total += subtotal
        
        detalles_con_subtotal.append({
            'detalle': detalle,
            'tipo': tipo,
            'precio': precio,
            'subtotal': subtotal
        })
    
    return render_template('modulos/ventas/detalle.html',
                          title="Detalle de Venta",
                          venta=venta,
                          detalles=detalles_con_subtotal,
                          total=total)

@ventas_bp.route('/ticket/<int:venta_id>')
@login_required
def ticket(venta_id):
    """Generar un ticket para una venta"""
    ticket_data = VentaController.generar_ticket(venta_id)
    
    if not ticket_data:
        flash('No se pudo generar el ticket', 'error')
        return redirect(url_for('ventas.detalle', venta_id=venta_id))
    
    return render_template('modulos/ventas/ticket.html',
                          title="Ticket de Venta",
                          ticket=ticket_data)

@ventas_bp.route('/eliminar/<int:venta_id>', methods=['POST'])
@login_required
def eliminar(venta_id):
    """Eliminar una venta"""
    if VentaController.delete_venta(venta_id):
        flash('Venta eliminada exitosamente', 'success')
    else:
        flash('Error al eliminar la venta', 'error')
    
    return redirect(url_for('ventas.index'))

@ventas_bp.route('/diarias')
@login_required
def ventas_diarias():
    """Ver ventas del día actual"""
    fecha = request.args.get('fecha')
    
    if fecha:
        try:
            fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
        except ValueError:
            fecha = datetime.now().date()
    else:
        fecha = datetime.now().date()
    
    datos_ventas = VentaController.get_ventas_diarias(fecha)
    
    return render_template('modulos/ventas/ventas_diarias.html',
                          title="Ventas Diarias",
                          datos_ventas=datos_ventas,
                          fecha_actual=fecha.strftime('%Y-%m-%d'))

@ventas_bp.route('/productos-mas-vendidos')
@login_required
def productos_mas_vendidos():
    """Ver productos más vendidos"""
    # Obtener fechas del request, si no hay, usar el mes actual
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    
    if not fecha_inicio:
        fecha_inicio = datetime.now().replace(day=1).strftime('%Y-%m-%d')  # Primer día del mes
    
    if not fecha_fin:
        fecha_fin = datetime.now().strftime('%Y-%m-%d')  # Hoy
    
    productos = VentaController.get_productos_mas_vendidos(fecha_inicio, fecha_fin)
    
    return render_template('modulos/ventas/productos_mas_vendidos.html',
                          title="Productos Más Vendidos",
                          productos=productos,
                          fecha_inicio=fecha_inicio,
                          fecha_fin=fecha_fin)