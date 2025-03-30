from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db
from modulos.ventas.models import Venta, DetalleVenta, PagoProveedor, PedidoCliente, DetallePedido
from modulos.ventas.forms import (
    VentaForm, create_venta_form,
    PagoProveedorForm, create_pago_proveedor_form,
    PedidoClienteForm, create_pedido_cliente_form
)
from modulos.ventas.controllers import VentaController, PagoProveedorController, PedidoClienteController
from modulos.clientes.controllers import ClienteController
from modulos.galletas.controllers import GalletaController
from modulos.proveedores.controllers import ProveedorController
from modulos.compras.controllers import CompraController
import json
from datetime import datetime, timedelta

# Crear blueprint para las rutas de ventas
ventas_bp = Blueprint('ventas', __name__, url_prefix='/ventas')

# ------------------------ RUTAS PARA VENTAS ------------------------ #

@ventas_bp.route('/')
def index():
    """Vista principal para la administración de ventas"""
    # Obtener todas las ventas
    ventas = VentaController.get_all_ventas()
    
    # Preparar datos para la plantilla
    items_data = []
    for venta in ventas:
        cliente_nombre = venta.cliente.nombreCliente if venta.cliente else "Cliente General"
        estatus_text = "Completada" if venta.estatus == 1 else "Pendiente" if venta.estatus == 0 else "Cancelada"
        estatus_class = "bg-green-100 text-green-800" if venta.estatus == 1 else "bg-yellow-100 text-yellow-800" if venta.estatus == 0 else "bg-red-100 text-red-800"
        
        items_data.append({
            'id': venta.idVenta,
            'fields': [
                venta.fechaVenta.strftime('%d/%m/%Y %H:%M'),
                cliente_nombre,
                f"${venta.total:.2f}",
                f'<span class="px-2 py-1 rounded-full text-xs {estatus_class}">{estatus_text}</span>'
            ]
        })
    
    # Definir los encabezados de la tabla
    headers = ['Fecha', 'Cliente', 'Total', 'Estatus']
    
    return render_template('modulos/ventas/index.html', 
                          title="Administración de Ventas",
                          items=items_data,
                          headers=headers)

@ventas_bp.route('/nueva', methods=['GET'])
def nueva_venta():
    """Vista para crear una nueva venta"""
    # Obtener clientes activos para el formulario
    clientes = ClienteController.get_active_clientes()
    # Obtener galletas disponibles para el formulario
    galletas = GalletaController.get_active_galletas()
    
    return render_template('modulos/ventas/form.html',
                          title="Nueva Venta",
                          venta=None,
                          form_fields=create_venta_form(clientes=clientes),
                          clientes=clientes,
                          galletas=galletas,
                          action=url_for('ventas.guardar'))

@ventas_bp.route('/editar/<int:venta_id>', methods=['GET'])
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
                          form_fields=create_venta_form(venta=venta, clientes=clientes),
                          detalles=detalles,
                          clientes=clientes,
                          galletas=galletas,
                          action=url_for('ventas.guardar'))

@ventas_bp.route('/guardar', methods=['POST'])
def guardar():
    """Guardar una venta (nueva o actualizada)"""
    try:
        # Obtener los datos del formulario
        venta_id = request.form.get('id', '')
        id_cliente = request.form.get('IdCliente')
        estatus = request.form.get('estatus')
        
        # Obtener los detalles de la venta (enviados como JSON)
        detalles_json = request.form.get('detalles', '[]')
        detalles_data = json.loads(detalles_json)
        
        # Validar datos básicos
        if not detalles_data:
            flash('Debe agregar al menos un detalle a la venta', 'error')
            return redirect(url_for('ventas.index'))
        
        # Preparar datos de la venta
        data = {
            'IdCliente': int(id_cliente) if id_cliente and id_cliente != '' else None,
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
def detalle(venta_id):
    """Ver detalles de una venta"""
    venta = VentaController.get_venta_by_id(venta_id)
    
    if not venta:
        flash('Venta no encontrada', 'error')
        return redirect(url_for('ventas.index'))
    
    # Obtener los detalles de la venta
    detalles = VentaController.get_detalles_venta(venta_id)
    
    return render_template('modulos/ventas/detalle.html',
                          title="Detalle de Venta",
                          venta=venta,
                          detalles=detalles)

@ventas_bp.route('/ticket/<int:venta_id>')
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
def eliminar(venta_id):
    """Eliminar una venta"""
    if VentaController.delete_venta(venta_id):
        flash('Venta eliminada exitosamente', 'success')
    else:
        flash('Error al eliminar la venta', 'error')
    
    return redirect(url_for('ventas.index'))

@ventas_bp.route('/diarias')
def ventas_diarias():
    """Ver ventas del día actual o una fecha específica"""
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
def productos_mas_vendidos():
    """Ver productos más vendidos"""
    # Obtener fechas del request, si no hay, usar el mes actual
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    
    if not fecha_inicio:
        fecha_inicio = datetime.now().replace(day=1).strftime('%Y-%m-%d')  # Primer día del mes
    
    if not fecha_fin:
        fecha_fin = datetime.now().strftime('%Y-%m-%d')  # Hoy
    
    resumen = PagoProveedorController.get_resumen_pagos(fecha_inicio, fecha_fin)
    
    return render_template('modulos/ventas/productos_mas_vendidos.html',
                          title="Resumen de Pagos a Proveedores",
                          resumen=resumen,
                          fecha_inicio=fecha_inicio,
                          fecha_fin=fecha_fin)

# ------------------------ RUTAS PARA PEDIDOS DE CLIENTES ------------------------ #

@ventas_bp.route('/pedidos')
def pedidos_index():
    """Vista principal para la administración de pedidos de clientes"""
    # Obtener todos los pedidos
    pedidos = PedidoClienteController.get_all_pedidos()
    
    # Preparar datos para la plantilla
    items_data = []
    for pedido in pedidos:
        cliente_nombre = pedido.cliente.nombreCliente if pedido.cliente else "Desconocido"
        estatus_map = {0: "Pendiente", 1: "En Proceso", 2: "Completado", 3: "Cancelado"}
        estatus_class_map = {
            0: "bg-yellow-100 text-yellow-800",
            1: "bg-blue-100 text-blue-800",
            2: "bg-green-100 text-green-800",
            3: "bg-red-100 text-red-800"
        }
        estatus_text = estatus_map.get(pedido.estatus, "Desconocido")
        estatus_class = estatus_class_map.get(pedido.estatus, "bg-gray-100 text-gray-800")
        
        items_data.append({
            'id': pedido.idPedido,
            'fields': [
                pedido.fechaPedido.strftime('%d/%m/%Y %H:%M'),
                cliente_nombre,
                pedido.fechaEntrega.strftime('%d/%m/%Y') if pedido.fechaEntrega else "-",
                f"${pedido.total:.2f}",
                f'<span class="px-2 py-1 rounded-full text-xs {estatus_class}">{estatus_text}</span>'
            ]
        })
    
    # Definir los encabezados de la tabla
    headers = ['Fecha Pedido', 'Cliente', 'Fecha Entrega', 'Total', 'Estatus']
    
    return render_template('modulos/ventas/pedidos_index.html', 
                          title="Administración de Pedidos",
                          items=items_data,
                          headers=headers)

@ventas_bp.route('/pedidos/nuevo', methods=['GET'])
def nuevo_pedido():
    """Vista para crear un nuevo pedido de cliente"""
    # Obtener clientes activos para el formulario
    clientes = ClienteController.get_active_clientes()
    # Obtener galletas disponibles para el formulario
    galletas = GalletaController.get_active_galletas()
    
    return render_template('modulos/ventas/pedido_form.html',
                          title="Nuevo Pedido",
                          pedido=None,
                          form_fields=create_pedido_cliente_form(clientes=clientes),
                          clientes=clientes,
                          galletas=galletas,
                          action=url_for('ventas.guardar_pedido'))

@ventas_bp.route('/pedidos/editar/<int:pedido_id>', methods=['GET'])
def editar_pedido(pedido_id):
    """Vista para editar un pedido existente"""
    pedido = PedidoClienteController.get_pedido_by_id(pedido_id)
    
    if not pedido:
        flash('Pedido no encontrado', 'error')
        return redirect(url_for('ventas.pedidos_index'))
    
    # Obtener los detalles del pedido
    detalles = PedidoClienteController.get_detalles_pedido(pedido_id)
    
    # Obtener clientes y galletas para el formulario
    clientes = ClienteController.get_active_clientes()
    galletas = GalletaController.get_active_galletas()
    
    return render_template('modulos/ventas/pedido_form.html',
                          title="Editar Pedido",
                          pedido=pedido,
                          form_fields=create_pedido_cliente_form(pedido=pedido, clientes=clientes),
                          detalles=detalles,
                          clientes=clientes,
                          galletas=galletas,
                          action=url_for('ventas.guardar_pedido'))

@ventas_bp.route('/pedidos/guardar', methods=['POST'])
def guardar_pedido():
    """Guardar un pedido de cliente (nuevo o actualizado)"""
    try:
        # Obtener los datos del formulario
        pedido_id = request.form.get('id', '')
        id_cliente = request.form.get('idCliente')
        fecha_entrega = request.form.get('fechaEntrega')
        instrucciones = request.form.get('instrucciones', '')
        estatus = request.form.get('estatus')
        
        # Obtener los detalles del pedido (enviados como JSON)
        detalles_json = request.form.get('detalles', '[]')
        detalles_data = json.loads(detalles_json)
        
        # Validar datos básicos
        if not id_cliente or not detalles_data:
            flash('Debe seleccionar un cliente y agregar al menos un producto', 'error')
            return redirect(url_for('ventas.pedidos_index'))
        
        # Preparar datos del pedido
        data = {
            'idCliente': int(id_cliente),
            'fechaEntrega': fecha_entrega if fecha_entrega else None,
            'instrucciones': instrucciones,
            'estatus': int(estatus)
        }
        
        if pedido_id and pedido_id.isdigit():
            # Actualizar pedido existente
            pedido = PedidoClienteController.update_pedido(int(pedido_id), data, detalles_data)
            if pedido:
                flash('Pedido actualizado exitosamente', 'success')
            else:
                flash('Error al actualizar el pedido', 'error')
        else:
            # Crear nuevo pedido
            pedido = PedidoClienteController.create_pedido(data, detalles_data)
            flash('Pedido registrado exitosamente', 'success')
        
        return redirect(url_for('ventas.pedidos_index'))
        
    except Exception as e:
        flash(f'Error al guardar el pedido: {str(e)}', 'error')
        return redirect(url_for('ventas.pedidos_index'))

@ventas_bp.route('/pedidos/detalle/<int:pedido_id>')
def detalle_pedido(pedido_id):
    """Ver detalles de un pedido"""
    pedido = PedidoClienteController.get_pedido_by_id(pedido_id)
    
    if not pedido:
        flash('Pedido no encontrado', 'error')
        return redirect(url_for('ventas.pedidos_index'))
    
    # Obtener los detalles del pedido
    detalles = PedidoClienteController.get_detalles_pedido(pedido_id)
    
    return render_template('modulos/ventas/pedido_detalle.html',
                          title="Detalle de Pedido",
                          pedido=pedido,
                          detalles=detalles)

@ventas_bp.route('/pedidos/eliminar/<int:pedido_id>', methods=['POST'])
def eliminar_pedido(pedido_id):
    """Eliminar un pedido"""
    if PedidoClienteController.delete_pedido(pedido_id):
        flash('Pedido eliminado exitosamente', 'success')
    else:
        flash('Error al eliminar el pedido', 'error')
    
    return redirect(url_for('ventas.pedidos_index'))

@ventas_bp.route('/pedidos/cambiar-estatus/<int:pedido_id>', methods=['POST'])
def cambiar_estatus_pedido(pedido_id):
    """Cambiar el estatus de un pedido"""
    nuevo_estatus = request.form.get('estatus')
    
    if not nuevo_estatus or not nuevo_estatus.isdigit():
        flash('Estatus inválido', 'error')
        return redirect(url_for('ventas.pedidos_index'))
    
    success, message = PedidoClienteController.cambiar_estatus_pedido(pedido_id, int(nuevo_estatus))
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('ventas.detalle_pedido', pedido_id=pedido_id))

@ventas_bp.route('/pedidos/convertir-a-venta/<int:pedido_id>', methods=['POST'])
def convertir_pedido_a_venta(pedido_id):
    """Convertir un pedido en una venta"""
    success, message, venta = PedidoClienteController.convertir_pedido_a_venta(pedido_id)
    
    if success:
        flash(message, 'success')
        return redirect(url_for('ventas.detalle', venta_id=venta.idVenta))
    else:
        flash(message, 'error')
        return redirect(url_for('ventas.detalle_pedido', pedido_id=pedido_id))

@ventas_bp.route('/pedidos/pendientes')
def pedidos_pendientes():
    """Ver pedidos pendientes"""
    pedidos = PedidoClienteController.get_pedidos_pendientes()
    
    # Preparar datos para la plantilla
    items_data = []
    for pedido in pedidos:
        cliente_nombre = pedido.cliente.nombreCliente if pedido.cliente else "Desconocido"
        estatus_map = {0: "Pendiente", 1: "En Proceso"}
        estatus_class_map = {
            0: "bg-yellow-100 text-yellow-800",
            1: "bg-blue-100 text-blue-800"
        }
        estatus_text = estatus_map.get(pedido.estatus, "Desconocido")
        estatus_class = estatus_class_map.get(pedido.estatus, "bg-gray-100 text-gray-800")
        
        items_data.append({
            'id': pedido.idPedido,
            'cliente': cliente_nombre,
            'fecha_pedido': pedido.fechaPedido.strftime('%d/%m/%Y %H:%M'),
            'fecha_entrega': pedido.fechaEntrega.strftime('%d/%m/%Y') if pedido.fechaEntrega else "-",
            'total': f"${pedido.total:.2f}",
            'estatus': estatus_text,
            'estatus_class': estatus_class
        })
    
    return render_template('modulos/ventas/pedidos_pendientes.html',
                          title="Pedidos Pendientes",
                          pedidos=items_data)
    
    if not fecha_fin:
        fecha_fin = datetime.now().strftime('%Y-%m-%d')  # Hoy
    
    productos = VentaController.get_productos_mas_vendidos(fecha_inicio, fecha_fin)
    
    return render_template('modulos/ventas/productos_mas_vendidos.html',
                          title="Productos Más Vendidos",
                          productos=productos,
                          fecha_inicio=fecha_inicio,
                          fecha_fin=fecha_fin)

@ventas_bp.route('/tipos-venta')
def tipos_venta():
    """Ver ventas por tipo (Individual vs Paquete)"""
    # Obtener fechas del request, si no hay, usar el mes actual
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    
    if not fecha_inicio:
        fecha_inicio = datetime.now().replace(day=1).strftime('%Y-%m-%d')  # Primer día del mes
    
    if not fecha_fin:
        fecha_fin = datetime.now().strftime('%Y-%m-%d')  # Hoy
    
    ventas_por_tipo = VentaController.get_ventas_por_tipo(fecha_inicio, fecha_fin)
    
    return render_template('modulos/ventas/tipos_venta.html',
                          title="Ventas por Tipo",
                          ventas_por_tipo=ventas_por_tipo,
                          fecha_inicio=fecha_inicio,
                          fecha_fin=fecha_fin)

# ------------------------ RUTAS PARA PAGOS A PROVEEDORES ------------------------ #

@ventas_bp.route('/pagos')
def pagos_index():
    """Vista principal para la administración de pagos a proveedores"""
    # Obtener todos los pagos
    pagos = PagoProveedorController.get_all_pagos()
    
    # Preparar datos para la plantilla
    items_data = []
    for pago in pagos:
        proveedor_nombre = pago.proveedor.nombre_proveedor if pago.proveedor else "Desconocido"
        estatus_text = "Pagado" if pago.estatus == 1 else "Pendiente" if pago.estatus == 0 else "Cancelado"
        estatus_class = "bg-green-100 text-green-800" if pago.estatus == 1 else "bg-yellow-100 text-yellow-800" if pago.estatus == 0 else "bg-red-100 text-red-800"
        
        items_data.append({
            'id': pago.idPago,
            'fields': [
                pago.fechaPago.strftime('%d/%m/%Y'),
                proveedor_nombre,
                f"${pago.monto:.2f}",
                pago.referencia or "-",
                f'<span class="px-2 py-1 rounded-full text-xs font-medium {estatus_class}">{estatus_text}</span>'
            ]
        })
    
    # Definir los encabezados de la tabla
    headers = ['Fecha', 'Proveedor', 'Monto', 'Referencia', 'Estatus']
    
    return render_template('modulos/ventas/pagos_index.html', 
                          title="Administración de Pagos a Proveedores",
                          items=items_data,
                          headers=headers)

@ventas_bp.route('/pagos/nuevo', methods=['GET'])
def nuevo_pago():
    """Vista para crear un nuevo pago a proveedor"""
    # Obtener proveedores activos para el formulario
    proveedores = ProveedorController.get_active_proveedores()
    # Obtener compras pendientes para el formulario
    compras = CompraController.get_all_compras()
    
    return render_template('modulos/ventas/pago_form.html',
                          title="Nuevo Pago a Proveedor",
                          pago=None,
                          form_fields=create_pago_proveedor_form(proveedores=proveedores, compras=compras),
                          action=url_for('ventas.guardar_pago'))

@ventas_bp.route('/pagos/editar/<int:pago_id>', methods=['GET'])
def editar_pago(pago_id):
    """Vista para editar un pago existente"""
    pago = PagoProveedorController.get_pago_by_id(pago_id)
    
    if not pago:
        flash('Pago no encontrado', 'error')
        return redirect(url_for('ventas.pagos_index'))
    
    # Obtener proveedores y compras para el formulario
    proveedores = ProveedorController.get_active_proveedores()
    compras = CompraController.get_all_compras()
    
    return render_template('modulos/ventas/pago_form.html',
                          title="Editar Pago a Proveedor",
                          pago=pago,
                          form_fields=create_pago_proveedor_form(pago=pago, proveedores=proveedores, compras=compras),
                          action=url_for('ventas.guardar_pago'))

@ventas_bp.route('/pagos/guardar', methods=['POST'])
def guardar_pago():
    """Guardar un pago a proveedor (nuevo o actualizado)"""
    try:
        # Obtener los datos del formulario
        pago_id = request.form.get('id', '')
        id_proveedor = request.form.get('idProveedor')
        fecha_pago = request.form.get('fechaPago')
        monto = request.form.get('monto')
        referencia = request.form.get('referencia', '')
        id_compra = request.form.get('idCompra')
        estatus = request.form.get('estatus')
        
        # Validar datos básicos
        if not id_proveedor or not fecha_pago or not monto:
            flash('Los campos Proveedor, Fecha de Pago y Monto son obligatorios', 'error')
            return redirect(url_for('ventas.pagos_index'))
        
        # Preparar datos del pago
        data = {
            'idProveedor': int(id_proveedor),
            'fechaPago': fecha_pago,
            'monto': float(monto),
            'referencia': referencia,
            'idCompra': int(id_compra) if id_compra and id_compra != '' else None,
            'estatus': int(estatus)
        }
        
        if pago_id and pago_id.isdigit():
            # Actualizar pago existente
            pago = PagoProveedorController.update_pago(int(pago_id), data)
            if pago:
                flash('Pago actualizado exitosamente', 'success')
            else:
                flash('Error al actualizar el pago', 'error')
        else:
            # Crear nuevo pago
            pago = PagoProveedorController.create_pago(data)
            flash('Pago registrado exitosamente', 'success')
        
        return redirect(url_for('ventas.pagos_index'))
        
    except Exception as e:
        flash(f'Error al guardar el pago: {str(e)}', 'error')
        return redirect(url_for('ventas.pagos_index'))

@ventas_bp.route('/pagos/eliminar/<int:pago_id>', methods=['POST'])
def eliminar_pago(pago_id):
    """Eliminar un pago a proveedor"""
    if PagoProveedorController.delete_pago(pago_id):
        flash('Pago eliminado exitosamente', 'success')
    else:
        flash('Error al eliminar el pago', 'error')
    
    return redirect(url_for('ventas.pagos_index'))

@ventas_bp.route('/pagos/resumen')
def resumen_pagos():
    """Ver resumen de pagos a proveedores en un período"""
    # Obtener fechas del request, si no hay, usar el mes actual
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    
    if not fecha_inicio:
        fecha_inicio = datetime.now