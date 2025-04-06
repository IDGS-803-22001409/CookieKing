# modulos / reportes / routes.py
import json
from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, request, jsonify, flash, send_file
from flask_login import login_required, current_user
from models import db
from modulos.reportes.models import HistorialReportes  
from modulos.reportes.forms import create_reportes_form
from modulos.reportes.reportes_generator import (
    generar_reporte_ventas, 
    generar_reporte_inventario, 
    generar_reporte_produccion,
    generar_reporte_financiero
)
from modulos.clientes.models import Cliente
from modulos.galletas.models import Galletas
from modulos.ventas.models import Venta, DetalleVenta
from modulos.ingredientes.models import Ingrediente
from sqlalchemy import func

# Crear blueprint para las rutas de reportes
reportes_bp = Blueprint('reportes', __name__, url_prefix='/reportes')

@reportes_bp.route('/')
@login_required
def index():
    """Vista principal para reportes"""
    return render_template('modulos/reportes/index.html')

@reportes_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal de reportes"""
    # Obtener fecha actual y fecha de hace 30 días
    fecha_actual = datetime.now().date()
    fecha_anterior = fecha_actual - timedelta(days=30)
    
    # Obtener estadísticas de ventas de los últimos 30 días
    ventas_stats = db.session.query(
        func.date(Venta.fechaVenta).label('fecha'),
        func.count(Venta.idVenta).label('total_ventas'),
        func.sum(Venta.total).label('ingresos')
    ).filter(
        func.date(Venta.fechaVenta) >= fecha_anterior,
        func.date(Venta.fechaVenta) <= fecha_actual
    ).group_by(
        func.date(Venta.fechaVenta)
    ).all()
    
    # Galletas más vendidas de los últimos 30 días
    galletas_top = db.session.query(
        Galletas.nombreGalleta,
        func.sum(DetalleVenta.cantidad).label('cantidad_vendida')
    ).join(DetalleVenta, DetalleVenta.galleta_id == Galletas.idGalleta)\
     .join(Venta, Venta.idVenta == DetalleVenta.venta_id)\
     .filter(
        func.date(Venta.fechaVenta) >= fecha_anterior,
        func.date(Venta.fechaVenta) <= fecha_actual
     ).group_by(Galletas.idGalleta)\
     .order_by(func.sum(DetalleVenta.cantidad).desc())\
     .limit(5).all()
    
    # Alertas de inventario bajo
    alertas_inventario = db.session.query(Ingrediente)\
        .filter(Ingrediente.stock <= Ingrediente.stock_minimo)\
        .order_by(
            (Ingrediente.stock / Ingrediente.stock_minimo).asc()
        ).limit(5).all()
    
    # Historial de reportes recientes
    reportes_recientes = HistorialReportes.query\
        .order_by(HistorialReportes.fechaGeneracion.desc())\
        .limit(5).all()
    
    # Ventas por cliente (top 5)
    ventas_por_cliente = db.session.query(
        Cliente.nombreCliente,
        func.sum(Venta.total).label('total_compras')
    ).join(Venta, Venta.IdCliente == Cliente.idCliente)\
     .filter(
        func.date(Venta.fechaVenta) >= fecha_anterior,
        func.date(Venta.fechaVenta) <= fecha_actual
     ).group_by(Cliente.idCliente)\
     .order_by(func.sum(Venta.total).desc())\
     .limit(5).all()
    
    return render_template(
        'modulos/reportes/dashboard.html',
        ventas_stats=ventas_stats,
        galletas_top=galletas_top,
        alertas_inventario=alertas_inventario,
        reportes_recientes=reportes_recientes,
        ventas_por_cliente=ventas_por_cliente,
        fecha_actual=fecha_actual.strftime('%d/%m/%Y'),
        fecha_anterior=fecha_anterior.strftime('%d/%m/%Y')
    )

@reportes_bp.route('/ventas', methods=['GET', 'POST'])
@login_required
def reporte_ventas():
    """Generar reportes de ventas"""
    # Obtener opciones para los select
    opciones = {
        'clientes': [(c.idCliente, c.nombreCliente) for c in Cliente.query.filter_by(estatus=1).all()],
        'productos': [(g.idGalleta, g.nombreGalleta) for g in Galletas.query.filter_by(estatus=1).all()]
    }
    
    form = create_reportes_form('ventas', choices=opciones)
    
    if request.method == 'POST' and form.validate_on_submit():
        # Recopilar datos del formulario
        datos_reporte = {
            'titulo': form.titulo.data,
            'fecha_inicio': form.fecha_inicio.data.strftime('%Y-%m-%d'),
            'fecha_fin': form.fecha_fin.data.strftime('%Y-%m-%d'),
            'tipo_reporte': form.tipo_reporte.data,
            'formato': 'pdf',  # Hardcoded to PDF
            'incluir_grafico': form.incluir_grafico.data,
            'clientes': form.clientes.data if hasattr(form, 'clientes') else [],
            'productos': form.productos.data if hasattr(form, 'productos') else []
        }
        
        try:
            # Generar el reporte
            ruta_archivo = generar_reporte_ventas(datos_reporte)
            
            # Registrar en historial
            historial = HistorialReportes(
                nombre=datos_reporte['titulo'],
                tipo=f"ventas_{datos_reporte['tipo_reporte']}",
                formato='PDF',  # Uppercase PDF
                usuario=current_user.nombre_usuario if current_user else None,
                rutaArchivo=ruta_archivo,
                exitoso=True
            )
            db.session.add(historial)
            db.session.commit()
            
            flash(f'Reporte generado correctamente', 'success')
            return redirect(url_for('reportes.descargar_reporte', historial_id=historial.idHistorial))
        
        except Exception as e:
            db.session.rollback()  # Rollback in case of error
            flash(f'Error al generar el reporte: {str(e)}', 'error')
    
    # Si es GET o si falló la validación, mostrar el formulario
    return render_template(
        'modulos/reportes/reporte_ventas.html',
        form=form,
        opciones=opciones
    )

# Similar updates for other routes - inventario, produccion, financiero
@reportes_bp.route('/inventario', methods=['GET', 'POST'])
@login_required
def reporte_inventario():
    """Generar reportes de inventario"""
    # Obtener categorías (en este caso, tipos de ingredientes)
    categorias = db.session.query(Ingrediente.unidad.distinct()).all()
    opciones = {
        'categorias': [(i, i) for i, in categorias]
    }
    
    form = create_reportes_form('inventario', choices=opciones)
    
    if request.method == 'POST' and form.validate_on_submit():
        # Recopilar datos del formulario
        datos_reporte = {
            'titulo': form.titulo.data,
            'tipo_reporte': form.tipo_reporte.data,
            'formato': 'pdf',  # Hardcoded to PDF
            'incluir_grafico': form.incluir_grafico.data,
            'categorias': form.categorias.data if hasattr(form, 'categorias') else [],
            'fecha_inicio': form.fecha_inicio.data.strftime('%Y-%m-%d') if form.fecha_inicio.data else None,
            'fecha_fin': form.fecha_fin.data.strftime('%Y-%m-%d') if form.fecha_fin.data else None
        }
        
        try:
            # Generar el reporte
            ruta_archivo = generar_reporte_inventario(datos_reporte)
            
            # Registrar en historial
            historial = HistorialReportes(
                nombre=datos_reporte['titulo'],
                tipo=f"inventario_{datos_reporte['tipo_reporte']}",
                formato='PDF',  # Uppercase PDF
                usuario=current_user.nombre_usuario if current_user else None,
                rutaArchivo=ruta_archivo,
                exitoso=True
            )
            db.session.add(historial)
            db.session.commit()
            
            flash(f'Reporte generado correctamente', 'success')
            return redirect(url_for('reportes.descargar_reporte', historial_id=historial.idHistorial))
        
        except Exception as e:
            db.session.rollback()  # Rollback in case of error
            flash(f'Error al generar el reporte: {str(e)}', 'error')
    
    # Si es GET o si falló la validación, mostrar el formulario
    return render_template(
        'modulos/reportes/reporte_inventario.html',
        form=form,
        opciones=opciones
    )

@reportes_bp.route('/produccion', methods=['GET', 'POST'])
@login_required
def reporte_produccion():
    """Generar reportes de producción"""
    # Obtener opciones para los select
    opciones = {
        'productos': [(g.idGalleta, g.nombreGalleta) for g in Galletas.query.filter_by(estatus=1).all()]
    }
    
    form = create_reportes_form('produccion', choices=opciones)
    
    if request.method == 'POST' and form.validate_on_submit():
        # Recopilar datos del formulario
        datos_reporte = {
            'titulo': form.titulo.data,
            'fecha_inicio': form.fecha_inicio.data.strftime('%Y-%m-%d'),
            'fecha_fin': form.fecha_fin.data.strftime('%Y-%m-%d'),
            'tipo_reporte': form.tipo_reporte.data,
            'formato': 'pdf',  # Hardcoded to PDF
            'incluir_grafico': form.incluir_grafico.data,
            'productos': form.productos.data if hasattr(form, 'productos') else []
        }
        
        try:
            # Generar el reporte
            ruta_archivo = generar_reporte_produccion(datos_reporte)
            
            # Registrar en historial
            historial = HistorialReportes(
                nombre=datos_reporte['titulo'],
                tipo=f"produccion_{datos_reporte['tipo_reporte']}",
                formato='PDF',  # Uppercase PDF
                usuario=current_user.nombre_usuario if current_user else None,
                rutaArchivo=ruta_archivo,
                exitoso=True
            )
            db.session.add(historial)
            db.session.commit()
            
            flash(f'Reporte generado correctamente', 'success')
            return redirect(url_for('reportes.descargar_reporte', historial_id=historial.idHistorial))
        
        except Exception as e:
            db.session.rollback()  # Rollback in case of error
            flash(f'Error al generar el reporte: {str(e)}', 'error')
    
    # Si es GET o si falló la validación, mostrar el formulario
    return render_template(
        'modulos/reportes/reporte_produccion.html',
        form=form,
        opciones=opciones
    )

@reportes_bp.route('/financiero', methods=['GET', 'POST'])
@login_required
def reporte_financiero():
    """Generar reportes financieros"""
    if request.method == 'POST':
        # Recopilar datos del formulario
        datos_reporte = {
            'titulo': request.form.get('titulo'),
            'fecha_inicio': request.form.get('fecha_inicio'),
            'fecha_fin': request.form.get('fecha_fin'),
            'tipo_reporte': request.form.get('tipo_reporte'),
            'formato': 'pdf',  # Hardcoded to PDF
            'incluir_grafico': 'incluir_grafico' in request.form
        }
        
        try:
            # Generar el reporte
            ruta_archivo = generar_reporte_financiero(datos_reporte)
            
            # Registrar en historial
            historial = HistorialReportes(
                nombre=datos_reporte['titulo'],
                tipo=f"financiero_{datos_reporte['tipo_reporte']}",
                formato='PDF',  # Uppercase PDF
                usuario=current_user.nombre_usuario if current_user else None,
                rutaArchivo=ruta_archivo,
                exitoso=True
            )
            db.session.add(historial)
            db.session.commit()
            
            flash(f'Reporte generado correctamente', 'success')
            return redirect(url_for('reportes.descargar_reporte', historial_id=historial.idHistorial))
        
        except Exception as e:
            db.session.rollback()  # Rollback in case of error
            flash(f'Error al generar el reporte: {str(e)}', 'error')
    
    # Si es GET o si falló la validación, mostrar el formulario
    return render_template('modulos/reportes/reporte_financiero.html')

@reportes_bp.route('/historial')
@login_required
def historial():
    """Ver historial de reportes generados"""
    historial_reportes = HistorialReportes.query\
        .order_by(HistorialReportes.fechaGeneracion.desc())\
        .all()
    
    return render_template(
        'modulos/reportes/historial.html',
        reportes=historial_reportes
    )

@reportes_bp.route('/descargar/<int:historial_id>')
@login_required
def descargar_reporte(historial_id):
    """Descargar un reporte generado"""
    reporte = HistorialReportes.query.get_or_404(historial_id)
    
    if not reporte.rutaArchivo:
        flash('El archivo del reporte no está disponible', 'error')
        return redirect(url_for('reportes.historial'))
    
    try:
        return send_file(
            reporte.rutaArchivo,
            as_attachment=True,
            download_name=f"{reporte.nombre}.{reporte.formato.lower()}"
        )
    except Exception as e:
        flash(f'Error al descargar el reporte: {str(e)}', 'error')
        return redirect(url_for('reportes.historial'))

@reportes_bp.route('/historial/<int:historial_id>/eliminar', methods=['POST'])
@login_required
def eliminar_historial(historial_id):
    """Eliminar un registro del historial"""
    historial = HistorialReportes.query.get_or_404(historial_id)
    db.session.delete(historial)
    db.session.commit()
    
    flash('Registro eliminado correctamente', 'success')
    return redirect(url_for('reportes.historial'))

# API endpoints para obtener datos para gráficos
@reportes_bp.route('/api/ventas_por_fecha')
@login_required
def api_ventas_por_fecha():
    """API para obtener datos de ventas por fecha"""
    dias = int(request.args.get('dias', 30))
    fecha_actual = datetime.now().date()
    fecha_anterior = fecha_actual - timedelta(days=dias)
    
    ventas = db.session.query(
        func.date(Venta.fechaVenta).label('fecha'),
        func.sum(Venta.total).label('total')
    ).filter(
        func.date(Venta.fechaVenta) >= fecha_anterior,
        func.date(Venta.fechaVenta) <= fecha_actual
    ).group_by(
        func.date(Venta.fechaVenta)
    ).all()
    
    data = [{"fecha": fecha.strftime('%Y-%m-%d'), "total": float(total)} for fecha, total in ventas]
    return jsonify(data)

@reportes_bp.route('/api/galletas_mas_vendidas')
@login_required
def api_galletas_mas_vendidas():
    """API para obtener datos de galletas más vendidas"""
    dias = int(request.args.get('dias', 30))
    limite = int(request.args.get('limite', 5))
    
    fecha_actual = datetime.now().date()
    fecha_anterior = fecha_actual - timedelta(days=dias)
    
    galletas = db.session.query(
        Galletas.nombreGalleta,
        func.sum(DetalleVenta.cantidad).label('cantidad')
    ).join(DetalleVenta, DetalleVenta.galleta_id == Galletas.idGalleta)\
     .join(Venta, Venta.idVenta == DetalleVenta.venta_id)\
     .filter(
        func.date(Venta.fechaVenta) >= fecha_anterior,
        func.date(Venta.fechaVenta) <= fecha_actual
     ).group_by(Galletas.nombreGalleta)\
     .order_by(func.sum(DetalleVenta.cantidad).desc())\
     .limit(limite).all()
    
    data = [{"nombre": nombre, "cantidad": int(cantidad)} for nombre, cantidad in galletas]
    return jsonify(data)