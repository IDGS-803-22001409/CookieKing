from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user, login_required
from modulos.ventas.models import Venta, DetalleVenta
from modulos.clientes.models import Cliente
from modulos.galletas.models import Galletas
from datetime import datetime
from models import db
from sqlalchemy import func, case
from flask_login import login_required


# Crear blueprint para las rutas principales
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def root_redirect():
    """Redirige automáticamente a la página de inicio de sesión"""
    return redirect(url_for('auth.iniciar_sesion'))  

@main_bp.route('/index')
@login_required
def index():    
    """Dashboard de ventas diarias con detalles"""
    hoy = datetime.now().date()
    
    try:
        # Consulta de ventas diarias
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
                

        # Consulta para totales con el mismo filtro
        totales = db.session.query(
            func.sum(DetalleVenta.cantidad * Galletas.precio_unitario).label('total_ventas'),
            func.sum(DetalleVenta.cantidad).label('total_unidades')
        ).join(Venta, DetalleVenta.venta_id == Venta.idVenta)\
         .join(Galletas, DetalleVenta.galleta_id == Galletas.idGalleta)\
         .filter(func.date(Venta.fechaVenta) == hoy).first()
        
        # consulta de galletas mas vendidas
        galletas = db.session.query(
            Galletas.nombreGalleta,
            func.sum(DetalleVenta.cantidad).label('ventas')  
        ).join(DetalleVenta, DetalleVenta.galleta_id == Galletas.idGalleta)\
         .join(Venta, DetalleVenta.venta_id == Venta.idVenta)\
         .group_by(Galletas.nombreGalleta)\
         .order_by(func.sum(DetalleVenta.cantidad).desc())\
         .limit(5)\
         .all()
        
        # consulta de presentaciones mas vendidas 1 individual 0 paquete
        presentaciones = db.session.query(
            case(
                (DetalleVenta.tipo_venta == 1, 'Individual'),
                (DetalleVenta.tipo_venta == 0, 'Paquete'),
                else_='Otro'
            ).label('presentacion'),
            func.sum(DetalleVenta.cantidad).label('total_ventas'),
            func.count().label('total_unidades')
            ).group_by(
                DetalleVenta.tipo_venta
            ).order_by(
                func.sum(DetalleVenta.cantidad).desc()
        ).all()

        return render_template('index.html',
            ventasClientes=ventasClientes,
            total_ventas=totales.total_ventas if totales and totales.total_ventas else 0,
            total_unidades=totales.total_unidades if totales and totales.total_unidades else 0,
            fecha_actual=hoy.strftime('%d/%m/%Y'),
            galletas_mas_vendidas=galletas,
            presentaciones=presentaciones)
    
    except Exception as e:
        print(f"Error en la consulta: {str(e)}")
        return render_template('index.html',
            ventasClientes=[],
            total_ventas=0,
            total_unidades=0,
            fecha_actual=hoy.strftime('%d/%m/%Y'))
    
    
# Manejadores de errores
@main_bp.app_errorhandler(404)
def page_not_found(e):
    """Página no encontrada"""
    return render_template('errors/404.html'), 404

@main_bp.app_errorhandler(500)
def internal_server_error(e):
    """Error interno del servidor"""
    return render_template('errors/500.html'), 500

@main_bp.route('/principal')
@login_required
def principal():
    """Redirige al dashboard según el rol del usuario"""
    if current_user.rol == 'admin':
        return redirect(url_for('auth.catalogo_usuarios'))
    elif current_user.rol == 'empleado':
        return redirect(url_for('index.html'))
    else:
        # Para otros roles o como fallback
        return render_template('#')