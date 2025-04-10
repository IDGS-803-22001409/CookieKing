from flask import Blueprint, redirect, render_template, url_for, flash, request
from flask_login import current_user, login_required
from modulos.ventas.models import Venta, DetalleVenta, PedidoCliente
from modulos.clientes.models import Cliente
from modulos.galletas.models import Galletas
from datetime import datetime, timedelta
from models import db
from sqlalchemy import func, case
from functools import wraps
from modulos.ventas.controllers import PedidoClienteController

main_bp = Blueprint('main', __name__)


# Decorador para restringir acceso solo a roles específicos
def roles_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.iniciar_sesion'))
            if current_user.rol not in roles:
                flash('No tienes permiso para acceder a esta página', 'error')
                if current_user.rol == 'cliente':
                    return redirect(url_for('main.cliente_portal'))
                return redirect(url_for('main.index'))
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

@main_bp.route('/')
def root_redirect():
    """Página principal pública"""
    return render_template('home.html')

@main_bp.route('/index')
@login_required
@roles_required('admin', 'empleado')
def index():    
    """Dashboard de ventas diarias (solo admin/empleado)"""
    hoy = datetime.now().date()
    inicio_mes = datetime.now().replace(day=1).date()
    
    # Inicializar variables
    ventasClientes = []
    ventas_cliente_general = 0
    total_ventas = 0
    total_unidades = 0
    galletas_mas_vendidas = []
    presentaciones = []
    ventas_periodo = 0
    galletas_con_costos = []
    galleta_recomendada = None
    
    try:        
        # Consulta para ventas por cliente
        ventasClientes = db.session.query(
            Cliente.nombreCliente,
            func.sum(DetalleVenta.cantidad * Galletas.precio_unitario).label('total_cliente')
        ).select_from(Venta)\
         .join(Cliente, Venta.IdCliente == Cliente.idCliente)\
         .join(DetalleVenta, DetalleVenta.venta_id == Venta.idVenta)\
         .join(Galletas, DetalleVenta.galleta_id == Galletas.idGalleta)\
         .filter(func.date(Venta.fechaVenta) == hoy)\
         .group_by(Cliente.nombreCliente)\
         .order_by(func.sum(DetalleVenta.cantidad * Galletas.precio_unitario).desc())\
         .all()

        # Consulta para obtener ventas sin cliente específico (clientes generales)
        ventas_sin_cliente = db.session.query(
            func.sum(DetalleVenta.cantidad * Galletas.precio_unitario).label('total_general')
        ).select_from(Venta)\
         .outerjoin(Cliente, Venta.IdCliente == Cliente.idCliente)\
         .join(DetalleVenta, DetalleVenta.venta_id == Venta.idVenta)\
         .join(Galletas, DetalleVenta.galleta_id == Galletas.idGalleta)\
         .filter(func.date(Venta.fechaVenta) == hoy)\
         .filter(Cliente.idCliente.is_(None))\
         .first()
        
        # Si hay ventas sin cliente, agregar "Cliente General" a la lista
        if ventas_sin_cliente and ventas_sin_cliente.total_general:
            ventas_cliente_general = float(ventas_sin_cliente.total_general or 0)
            # Crear objeto similar a los resultados de ventasClientes
            cliente_general = type('obj', (object,), {
                'nombreCliente': 'Cliente General', 
                'total_cliente': ventas_cliente_general
            })
            # Agregar al inicio de la lista
            ventasClientes = [cliente_general] + list(ventasClientes)

        # Resto del código como estaba
        totales = db.session.query(
            func.sum(DetalleVenta.cantidad * Galletas.precio_unitario).label('total_ventas'),
            func.sum(DetalleVenta.cantidad).label('total_unidades')
        ).join(Venta, DetalleVenta.venta_id == Venta.idVenta)\
         .join(Galletas, DetalleVenta.galleta_id == Galletas.idGalleta)\
         .filter(func.date(Venta.fechaVenta) == hoy).first()
        
        if totales:
            total_ventas = float(totales.total_ventas or 0)
            total_unidades = int(totales.total_unidades or 0)
        
        galletas = db.session.query(
            Galletas.nombreGalleta,
            func.sum(DetalleVenta.cantidad).label('ventas')  
        ).join(DetalleVenta, DetalleVenta.galleta_id == Galletas.idGalleta)\
         .join(Venta, DetalleVenta.venta_id == Venta.idVenta)\
         .group_by(Galletas.nombreGalleta)\
         .order_by(func.sum(DetalleVenta.cantidad).desc())\
         .limit(5)\
         .all()
        
        galletas_mas_vendidas = galletas
        
        presentaciones = db.session.query(
            case(
                (DetalleVenta.tipo_venta == 1, 'Individual'),
                (DetalleVenta.tipo_venta == 0, 'Paquete'),
                else_='Otro'
            ).label('presentacion'),
            func.sum(DetalleVenta.cantidad).label('total_ventas'),
            func.count().label('total_unidades')
            ).group_by(DetalleVenta.tipo_venta
            ).order_by(func.sum(DetalleVenta.cantidad).desc()
        ).all()

        # 1. Ventas totales con período específico (último mes)
        ventas_periodo_result = db.session.query(
            func.sum(DetalleVenta.cantidad * Galletas.precio_unitario).label('total_ventas')
        ).join(Venta, DetalleVenta.venta_id == Venta.idVenta)\
         .join(Galletas, DetalleVenta.galleta_id == Galletas.idGalleta)\
         .filter(func.date(Venta.fechaVenta) >= inicio_mes).first()
        
        ventas_periodo = float(ventas_periodo_result.total_ventas or 0) if ventas_periodo_result else 0
        
        # 2. Cálculo de costos usando un enfoque alternativo
        galletas_result = Galletas.query.filter_by(estatus=1).all()
        
        for galleta in galletas_result:
            try:
                # Usar un costo estimado basado en el precio
                precio = float(galleta.precio_unitario or 0)                
                costo_unitario = precio * 0.40
                margen = precio - costo_unitario
                margen_porcentaje = (margen / costo_unitario * 100) if costo_unitario > 0 else 0
                
                galleta_info = {
                    'nombreGalleta': galleta.nombreGalleta,
                    'precio': precio,
                    'costo': costo_unitario,
                    'margen': margen,
                    'margen_porcentaje': margen_porcentaje
                }
                
                galletas_con_costos.append(galleta_info)
                
                # Actualizar la galleta recomendada si tiene mejor margen
                if not galleta_recomendada or margen_porcentaje > galleta_recomendada['margen_porcentaje']:
                    galleta_recomendada = galleta_info
                    
            except Exception as e:
                print(f"Error calculando costo para galleta {galleta.nombreGalleta}: {str(e)}")
                # Continuar con la siguiente galleta

        return render_template('index.html',
            ventasClientes=ventasClientes,
            total_ventas=total_ventas,
            total_unidades=total_unidades,
            fecha_actual=hoy.strftime('%d/%m/%Y'),
            galletas_mas_vendidas=galletas_mas_vendidas,
            presentaciones=presentaciones,
            # Nuevos datos para los criterios faltantes
            ventas_periodo=ventas_periodo,
            periodo_inicio=inicio_mes.strftime('%d/%m/%Y'),
            periodo_fin=hoy.strftime('%d/%m/%Y'),
            galletas_con_costos=galletas_con_costos,
            galleta_recomendada=galleta_recomendada)
    
    except Exception as e:
        import traceback
        print(f"Error en consulta principal: {str(e)}")
        print(traceback.format_exc())
        return render_template('index.html',
            ventasClientes=[],
            total_ventas=0,
            total_unidades=0,
            fecha_actual=hoy.strftime('%d/%m/%Y'),
            ventas_periodo=0,
            periodo_inicio=inicio_mes.strftime('%d/%m/%Y'),
            periodo_fin=hoy.strftime('%d/%m/%Y'),
            galletas_con_costos=[],
            galleta_recomendada=None)

@main_bp.route('/cliente')
def cliente_portal():
    """Portal de clientes"""
    galletas = Galletas.query.filter_by(estatus=1).all()
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    pedidos_cliente = []
    
    if current_user.is_authenticated and current_user.rol == 'cliente':
        try:
            # Asegurarse de que el usuario actual se identifique correctamente
            from modulos.auth.models import Usuario
            from modulos.clientes.models import Cliente
            
            # Buscar el cliente asociado al usuario actual
            cliente = Cliente.query.filter_by(correo=current_user.correo).first()
            
            if cliente:
                # Si encontramos el cliente por su correo, usamos su ID
                pedidos_cliente = PedidoCliente.query.filter_by(idCliente=cliente.idCliente)\
                                .order_by(PedidoCliente.fechaPedido.desc()).all()
            else:
                # Si no encontramos al cliente por correo, usamos el ID del usuario
                pedidos_cliente = PedidoCliente.query.filter_by(idCliente=current_user.id)\
                                .order_by(PedidoCliente.fechaPedido.desc()).all()
        except Exception as e:
            print(f"Error obteniendo pedidos: {e}")

    return render_template('cliente/portal.html', 
                         galletas=galletas,
                         tomorrow=tomorrow,
                         pedidos_cliente=pedidos_cliente)

@main_bp.route('/cliente/pedido', methods=['POST'])
@login_required
@roles_required('cliente')
def guardar_pedido():
    """Procesar pedido de cliente"""
    try:
        detalles_json = request.form.get('detalles', '[]')
        instrucciones = request.form.get('instrucciones', '')
        fecha_entrega = request.form.get('fechaEntrega')
        
        import json
        detalles_data = json.loads(detalles_json)
        
        if not detalles_data:
            flash('Debes agregar al menos un producto', 'error')
            return redirect(url_for('main.cliente_portal'))
        
        # Buscar el cliente asociado al usuario actual
        from modulos.clientes.models import Cliente
        cliente = Cliente.query.filter_by(correo=current_user.correo).first()
        
        if cliente:
            # Si encontramos el cliente por su correo
            cliente_id = cliente.idCliente
        else:
            # Si no encontramos al cliente por correo, usamos el ID del usuario
            cliente_id = current_user.id
            
            # Intentamos crear un cliente asociado al usuario actual si no existe
            try:
                nuevo_cliente = Cliente(
                    nombreCliente=current_user.nombre_usuario,
                    correo=current_user.correo,
                    telefono="Sin especificar",
                    estatus=1
                )
                db.session.add(nuevo_cliente)
                db.session.commit()
                cliente_id = nuevo_cliente.idCliente
            except Exception as e:
                print(f"Error al crear cliente: {e}")
        
        # Preparamos los datos del pedido
        data = {
            'idCliente': cliente_id,
            'instrucciones': instrucciones,
            'fechaEntrega': fecha_entrega,
            'estatus': 0  # Pendiente
        }
        
        # Verificamos stock antes de crear el pedido
        for detalle in detalles_data:
            galleta_id = detalle.get('galleta_id')
            cantidad = int(detalle.get('cantidad', 0))
            
            galleta = Galletas.query.get(galleta_id)
            if not galleta:
                flash(f'Producto no encontrado', 'error')
                return redirect(url_for('main.cliente_portal'))
            
            # Verificar stock (opcional para pedidos)
            if galleta.existencias < cantidad:
                flash(f'Stock insuficiente para {galleta.nombreGalleta}. Disponible: {galleta.existencias}, Solicitado: {cantidad}', 'warning')
                # No es necesario retornar aquí, ya que es sólo un pedido sin reducción inmediata de stock
        
        # Crear el pedido
        PedidoClienteController.create_pedido(data, detalles_data)
        flash('Pedido registrado exitosamente', 'success')
        return redirect(url_for('main.cliente_portal'))
        
    except Exception as e:
        flash(f'Error al procesar pedido: {str(e)}', 'error')
        return redirect(url_for('main.cliente_portal'))

@main_bp.route('/principal')
@login_required
def principal():
    """Redirección por rol de usuario"""
    if current_user.rol == 'admin':
        return redirect(url_for('main.index'))
    elif current_user.rol == 'empleado':
        return redirect(url_for('main.index'))
    elif current_user.rol == 'cliente':
        return redirect(url_for('main.cliente_portal'))
    return redirect(url_for('main.root_redirect'))

# Manejadores de errores
@main_bp.app_errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@main_bp.app_errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500