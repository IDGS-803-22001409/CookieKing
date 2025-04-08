# modulos/reportes/reportes_generator.py
import os
import tempfile
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_, desc, asc
from flask_login import current_user
from models import db
from modulos.ventas.models import Venta, DetalleVenta
from modulos.clientes.models import Cliente
from modulos.galletas.models import Galletas
from modulos.ingredientes.models import Ingrediente
from modulos.proveedores.models import Proveedor
from modulos.produccion.models import ProduccionDetalle

# Importar bibliotecas para PDF
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    from reportlab.graphics.charts.linecharts import HorizontalLineChart
    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.graphics.widgets.markers import makeMarker
except ImportError:
    print("La biblioteca reportlab no está instalada. Por favor, instálala con 'pip install reportlab'")

REPORTES_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', '..', 'static', 'reportes')
os.makedirs(REPORTES_DIR, exist_ok=True)

def generar_reporte_ventas(datos_reporte):
    """Genera reportes de ventas según los parámetros recibidos"""
    # Extraer parámetros
    titulo = datos_reporte.get('titulo', 'Reporte de Ventas')
    fecha_inicio = datetime.strptime(datos_reporte.get('fecha_inicio', ''), '%Y-%m-%d')
    fecha_fin = datetime.strptime(datos_reporte.get('fecha_fin', ''), '%Y-%m-%d')
    tipo_reporte = datos_reporte.get('tipo_reporte', 'ventas_diarias')
    formato = datos_reporte.get('formato', 'pdf')
    incluir_grafico = datos_reporte.get('incluir_grafico', True)
    clientes_ids = datos_reporte.get('clientes', [])
    productos_ids = datos_reporte.get('productos', [])
    
    # Crear filtros para la consulta
    filtros = [
        func.date(Venta.fechaVenta) >= fecha_inicio.date(),
        func.date(Venta.fechaVenta) <= fecha_fin.date(),
    ]
    
    if clientes_ids:
        filtros.append(Venta.IdCliente.in_(clientes_ids))
    
    # Realizar la consulta según el tipo de reporte
    if tipo_reporte == 'ventas_diarias':
        # Ventas agrupadas por día
        resultados = db.session.query(
            func.date(Venta.fechaVenta).label('fecha'),
            func.count(Venta.idVenta).label('cantidad'),
            func.sum(Venta.total).label('total')
        ).filter(*filtros).group_by(
            func.date(Venta.fechaVenta)
        ).order_by(
            func.date(Venta.fechaVenta)
        ).all()
        
        # Crear archivo según el formato solicitado
        if formato == 'pdf':
            return _generar_pdf_ventas_diarias(resultados, titulo, fecha_inicio, fecha_fin, incluir_grafico)
        
    elif tipo_reporte == 'ventas_por_cliente':
        # Ventas agrupadas por cliente
        resultados = db.session.query(
            Cliente.idCliente,
            Cliente.nombreCliente,
            func.count(Venta.idVenta).label('cantidad'),
            func.sum(Venta.total).label('total')
        ).join(
            Venta, Venta.IdCliente == Cliente.idCliente
        ).filter(*filtros).group_by(
            Cliente.idCliente
        ).order_by(
            func.sum(Venta.total).desc()
        ).all()
        
        # Crear archivo según el formato solicitado
        if formato == 'excel':
            return _generar_excel_ventas_por_cliente(resultados, titulo, fecha_inicio, fecha_fin, incluir_grafico)
        else:  # Por defecto, PDF
            return _generar_pdf_ventas_por_cliente(resultados, titulo, fecha_inicio, fecha_fin, incluir_grafico)
    
    elif tipo_reporte == 'ventas_por_producto':
        # Ventas por producto, teniendo en cuenta los filtros de producto si existen
        if productos_ids:
            filtros_prod = [DetalleVenta.galleta_id.in_(productos_ids)]
        else:
            filtros_prod = []
            
        resultados = db.session.query(
            Galletas.idGalleta,
            Galletas.nombreGalleta,
            func.sum(DetalleVenta.cantidad).label('cantidad'),
            func.sum(DetalleVenta.subtotal).label('total')
        ).join(
            DetalleVenta, DetalleVenta.galleta_id == Galletas.idGalleta
        ).join(
            Venta, Venta.idVenta == DetalleVenta.venta_id
        ).filter(
            *filtros, *filtros_prod
        ).group_by(
            Galletas.idGalleta
        ).order_by(
            func.sum(DetalleVenta.subtotal).desc()
        ).all()
        
        # Crear archivo según el formato solicitado
        if formato == 'excel':
            return _generar_pdf_ventas_por_producto(resultados, titulo, fecha_inicio, fecha_fin, incluir_grafico)
    
    elif tipo_reporte == 'ventas_por_tipo':
        # Ventas por tipo (individual o paquete)
        resultados = db.session.query(
            DetalleVenta.tipo_venta,
            func.count(DetalleVenta.id).label('cantidad_ventas'),
            func.sum(DetalleVenta.cantidad).label('cantidad_productos'),
            func.sum(DetalleVenta.subtotal).label('total')
        ).join(
            Venta, Venta.idVenta == DetalleVenta.venta_id
        ).filter(*filtros).group_by(
            DetalleVenta.tipo_venta
        ).all()
        
        # Mapear los tipos_venta a nombres legibles
        resultados = [(
            "Individual" if tipo == 1 else "Paquete", 
            cantidad_ventas, 
            cantidad_productos, 
            total
        ) for tipo, cantidad_ventas, cantidad_productos, total in resultados]
        
        # Crear archivo según el formato solicitado
        if formato == 'excel':
            return _generar_excel_ventas_por_tipo(resultados, titulo, fecha_inicio, fecha_fin, incluir_grafico)
        else:  # Por defecto, PDF
            return _generar_pdf_ventas_por_tipo(resultados, titulo, fecha_inicio, fecha_fin, incluir_grafico)
    
    # Ruta temporal para cualquier caso no manejado
    ruta_archivo = os.path.join(REPORTES_DIR, f"reporte_ventas_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt")
    with open(ruta_archivo, 'w') as f:
        f.write(f"Reporte generado: {titulo}\n")
        f.write(f"Tipo de reporte no implementado: {tipo_reporte}")
    
    return ruta_archivo

def generar_reporte_inventario(datos_reporte):
    """Genera reportes de inventario según los parámetros recibidos"""
    # Extraer parámetros
    titulo = datos_reporte.get('titulo', 'Reporte de Inventario')
    tipo_reporte = datos_reporte.get('tipo_reporte', 'stock_actual')
    formato = datos_reporte.get('formato', 'pdf')
    incluir_grafico = datos_reporte.get('incluir_grafico', True)
    categorias = datos_reporte.get('categorias', [])
    fecha_inicio = datos_reporte.get('fecha_inicio')
    fecha_fin = datos_reporte.get('fecha_fin')
    
    # Aplicar filtros de categoría si existen
    filtros = []
    if categorias:
        filtros.append(Ingrediente.unidad.in_(categorias))
    
    # Realizar la consulta según el tipo de reporte
    if tipo_reporte == 'stock_actual':
        # Inventario actual
        resultados = db.session.query(
            Ingrediente.idIngrediente,
            Ingrediente.nombreIngrediente,
            Ingrediente.stock,
            Ingrediente.unidad,
            Ingrediente.precio_unitario
        ).filter(*filtros).order_by(
            Ingrediente.nombreIngrediente
        ).all()
        
        # Formato de salida
        if formato == 'excel':
            return _generar_excel_inventario_actual(resultados, titulo, incluir_grafico)
        else:  # PDF por defecto
            return _generar_pdf_inventario_actual(resultados, titulo, incluir_grafico)        
    
    elif tipo_reporte == 'caducidad':
        # Reporte de fechas de caducidad
        hoy = datetime.now().date()
        
        resultados = db.session.query(
            Ingrediente.idIngrediente,
            Ingrediente.nombreIngrediente,
            Ingrediente.stock,
            Ingrediente.unidad,
            Ingrediente.fecha_expiracion
        ).filter(
            Ingrediente.fecha_expiracion.isnot(None),
            *filtros
        ).order_by(
            Ingrediente.fecha_expiracion
        ).all()
        
        # Formato de salida
        if formato == 'excel':
            return _generar_excel_caducidad(resultados, titulo, hoy, incluir_grafico)
        else:  # PDF por defecto
            return _generar_pdf_caducidad(resultados, titulo, hoy, incluir_grafico)
    
    # Si llegamos aquí, es un tipo no implementado
    ruta_archivo = os.path.join(REPORTES_DIR, f"reporte_inventario_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt")
    with open(ruta_archivo, 'w') as f:
        f.write(f"Reporte generado: {titulo}\n")
        f.write(f"Tipo de reporte no implementado: {tipo_reporte}")
    
    return ruta_archivo

def generar_reporte_produccion(datos_reporte):
    """Genera reportes de producción según los parámetros recibidos"""
    # Extraer parámetros
    titulo = datos_reporte.get('titulo', 'Reporte de Producción')
    tipo_reporte = datos_reporte.get('tipo_reporte', 'produccion_diaria')
    fecha_inicio = datetime.strptime(datos_reporte.get('fecha_inicio', ''), '%Y-%m-%d')
    fecha_fin = datetime.strptime(datos_reporte.get('fecha_fin', ''), '%Y-%m-%d')
    formato = datos_reporte.get('formato', 'pdf')
    incluir_grafico = datos_reporte.get('incluir_grafico', True)
    productos_ids = datos_reporte.get('productos', [])
    
    # Implementación básica para generar archivo según formato
    if formato == 'excel':
        return _generar_excel_produccion(datos_reporte, titulo, tipo_reporte, incluir_grafico)
    else:  # PDF por defecto
        return _generar_pdf_produccion(datos_reporte, titulo, tipo_reporte, incluir_grafico)

def generar_reporte_financiero(datos_reporte):
    """Genera reportes financieros según los parámetros recibidos"""
    # Extraer parámetros
    titulo = datos_reporte.get('titulo', 'Reporte Financiero')
    tipo_reporte = datos_reporte.get('tipo_reporte', 'ingresos_vs_gastos')
    fecha_inicio = datetime.strptime(datos_reporte.get('fecha_inicio', ''), '%Y-%m-%d')
    fecha_fin = datetime.strptime(datos_reporte.get('fecha_fin', ''), '%Y-%m-%d')
    formato = datos_reporte.get('formato', 'pdf')
    incluir_grafico = datos_reporte.get('incluir_grafico', True)
    
    # Implementación básica para generar archivo según formato
    if formato == 'excel':
        return _generar_excel_financiero(datos_reporte, titulo, tipo_reporte, incluir_grafico)
    else:  # PDF por defecto
        return _generar_pdf_financiero(datos_reporte, titulo, tipo_reporte, incluir_grafico)

# Funciones auxiliares para Excel
def _generar_excel_ventas_diarias(resultados, titulo, fecha_inicio, fecha_fin, incluir_grafico=True):
    """Genera un archivo Excel para el reporte de ventas diarias"""
    nombre_archivo = f"ventas_diarias_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
    ruta_archivo = os.path.join(REPORTES_DIR, nombre_archivo)
    
    # Crear un nuevo libro de Excel y una hoja
    workbook = xlsxwriter.Workbook(ruta_archivo)
    worksheet = workbook.add_worksheet("Ventas Diarias")
    
    # Añadir formatos
    titulo_formato = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'center',
        'valign': 'vcenter'
    })
    
    encabezado_formato = workbook.add_format({
        'bold': True,
        'bg_color': '#F3AD4E',  # Color cookie
        'border': 1,
        'align': 'center'
    })
    
    celda_formato = workbook.add_format({
        'border': 1
    })
    
    fecha_formato = workbook.add_format({
        'border': 1,
        'num_format': 'dd/mm/yyyy'
    })
    
    numero_formato = workbook.add_format({
        'border': 1,
        'num_format': '#,##0'
    })
    
    moneda_formato = workbook.add_format({
        'border': 1,
        'num_format': '$#,##0.00'
    })
    
    total_formato = workbook.add_format({
        'bold': True,
        'border': 1,
        'bg_color': '#F6C177',  # Color cookie claro
    })
    
    total_numero_formato = workbook.add_format({
        'bold': True,
        'border': 1,
        'bg_color': '#F6C177',
        'num_format': '#,##0'
    })
    
    total_moneda_formato = workbook.add_format({
        'bold': True,
        'border': 1,
        'bg_color': '#F6C177',
        'num_format': '$#,##0.00'
    })
    
    # Escribir el título y subtítulo
    worksheet.merge_range('A1:C1', titulo, titulo_formato)
    worksheet.merge_range('A2:C2', f"Período: {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}", titulo_formato)
    
    # Añadir un poco de espacio
    worksheet.write('A3', '')
    
    # Escribir encabezados de columna
    worksheet.write('A4', 'Fecha', encabezado_formato)
    worksheet.write('B4', 'Ventas', encabezado_formato)
    worksheet.write('C4', 'Total ($)', encabezado_formato)
    
    # Establecer anchos de columna
    worksheet.set_column('A:A', 15)
    worksheet.set_column('B:B', 12)
    worksheet.set_column('C:C', 15)
    
    # Escribir datos
    fila = 4
    for fecha, cantidad, total in resultados:
        worksheet.write_datetime(fila, 0, fecha, fecha_formato)
        worksheet.write_number(fila, 1, cantidad, numero_formato)
        worksheet.write_number(fila, 2, total, moneda_formato)
        fila += 1
    
    # Escribir totales
    total_ventas = sum(cantidad for _, cantidad, _ in resultados)
    total_ingresos = sum(total for _, _, total in resultados)
    
    worksheet.write(fila, 0, 'TOTAL', total_formato)
    worksheet.write_number(fila, 1, total_ventas, total_numero_formato)
    worksheet.write_number(fila, 2, total_ingresos, total_moneda_formato)
    
    # Añadir gráfico si se solicita
    if incluir_grafico:
        chart = workbook.add_chart({'type': 'line'})
        
        # Configurar datos del gráfico
        chart.add_series({
            'name': 'Ventas',
            'categories': ['Ventas Diarias', 4, 0, fila-1, 0],
            'values': ['Ventas Diarias', 4, 1, fila-1, 1],
            'line': {'color': '#F3AD4E', 'width': 2.25},
        })
        
        chart.add_series({
            'name': 'Total ($)',
            'categories': ['Ventas Diarias', 4, 0, fila-1, 0],
            'values': ['Ventas Diarias', 4, 2, fila-1, 2],
            'line': {'color': '#3CB371', 'width': 2.25},  # Verde medio
            'y2_axis': True,
        })
        
        # Añadir título y etiquetas
        chart.set_title({'name': 'Tendencia de Ventas'})
        chart.set_x_axis({'name': 'Fecha'})
        chart.set_y_axis({'name': 'Cantidad de Ventas'})
        chart.set_y2_axis({'name': 'Total ($)'})
        
        # Insertar el gráfico
        chart.set_size({'width': 720, 'height': 400})
        worksheet.insert_chart('A' + str(fila + 3), chart)
    
    # Cerrar el libro
    workbook.close()
    
    return ruta_archivo

def _generar_pdf_ventas_diarias(resultados, titulo, fecha_inicio, fecha_fin, incluir_grafico=True):
    """Genera un archivo PDF para el reporte de ventas diarias"""
    nombre_archivo = f"ventas_diarias_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    ruta_archivo = os.path.join(REPORTES_DIR, nombre_archivo)
    
    # Crear documento
    doc = SimpleDocTemplate(ruta_archivo, pagesize=letter)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Añadir título
    title_style = styles["Title"]
    title_style.alignment = 1  # 0=Izquierda, 1=Centro, 2=Derecha
    elements.append(Paragraph(titulo, title_style))
    
    # Añadir período
    subtitle_style = styles["Heading2"]
    subtitle_style.alignment = 1
    elements.append(Paragraph(f"Período: {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}", subtitle_style))
    
    # Añadir espacio
    elements.append(Spacer(1, 0.25*inch))
    
    # Preparar datos para la tabla
    data = [['Fecha', 'Ventas', 'Total ($)']]
    
    for fecha, cantidad, total in resultados:
        data.append([
            fecha.strftime('%d/%m/%Y'),
            str(cantidad),
            f"${total:.2f}"
        ])
    
    # Añadir totales
    total_ventas = sum(cantidad for _, cantidad, _ in resultados)
    total_ingresos = sum(total for _, _, total in resultados)
    
    data.append(['TOTAL', str(total_ventas), f"${total_ingresos:.2f}"])
    
    # Crear tabla
    table = Table(data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
    
    # Estilo de tabla
    style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F3AD4E')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 12),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#F6C177')),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ])
    
    table.setStyle(style)
    elements.append(table)
    
    # Añadir gráfico si se solicita
    if incluir_grafico and len(resultados) > 0:
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph("Gráfico de Ventas", styles["Heading3"]))
        elements.append(Spacer(1, 0.25*inch))
        
        # Crear un gráfico de líneas
        drawing = Drawing(500, 250)
        
        # Extraer datos para el gráfico
        fechas = [fecha.strftime('%d/%m') for fecha, _, _ in resultados]
        cantidades = [cantidad for _, cantidad, _ in resultados]
        
        # Crear el gráfico de líneas para cantidad de ventas
        lc = HorizontalLineChart()
        lc.x = 50
        lc.y = 50
        lc.height = 150
        lc.width = 400
        lc.data = [cantidades]
        
        # Configurar categorías en el eje X
        lc.categoryAxis.categoryNames = fechas
        lc.categoryAxis.labels.boxAnchor = 'n'
        lc.categoryAxis.labels.angle = 30
        lc.categoryAxis.labels.fontSize = 8
        
        # Configurar etiquetas en el eje Y
        lc.valueAxis.valueMin = 0
        lc.valueAxis.valueMax = max(cantidades) * 1.2 if cantidades else 10
        lc.valueAxis.valueStep = max(1, max(cantidades) // 5) if cantidades else 2
        
        # Estilo de línea
        lc.lines[0].strokeWidth = 3
        lc.lines[0].strokeColor = colors.HexColor('#F3AD4E')
        
        # Añadir leyendas
        lc.lines.symbol = makeMarker('FilledCircle')
        lc.lines[0].symbol.size = 6
        lc.lines[0].symbol.fillColor = colors.HexColor('#F3AD4E')
        
        # Añadir títulos
        lc.categoryAxis.labelAxisMode = 'low'
        lc.valueAxis.labelTextFormat = '%d'
        lc.categoryAxis.title = 'Fecha'
        lc.valueAxis.title = 'Cantidad de Ventas'
        
        # Añadir leyenda
        legend = Legend()
        legend.alignment = 'right'
        legend.x = 480
        legend.y = 150
        legend.colorNamePairs = [(colors.HexColor('#F3AD4E'), 'Ventas')]
        lc.legend = legend
        
        drawing.add(lc)
        elements.append(drawing)
        
        # Añadir un segundo gráfico para los ingresos
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph("Ingresos por Fecha", styles["Heading3"]))
        elements.append(Spacer(1, 0.25*inch))
        
        drawing2 = Drawing(500, 250)
        
        totales = [float(total) for _, _, total in resultados]
        
        # Crear gráfico para los ingresos
        lc2 = HorizontalLineChart()
        lc2.x = 50
        lc2.y = 50
        lc2.height = 150
        lc2.width = 400
        lc2.data = [totales]
        
        # Configurar categorías en el eje X
        lc2.categoryAxis.categoryNames = fechas
        lc2.categoryAxis.labels.boxAnchor = 'n'
        lc2.categoryAxis.labels.angle = 30
        lc2.categoryAxis.labels.fontSize = 8
        
        # Configurar etiquetas en el eje Y
        lc2.valueAxis.valueMin = 0
        lc2.valueAxis.valueMax = max(totales) * 1.2 if totales else 10
        lc2.valueAxis.valueStep = max(1, max(totales) // 5) if totales else 2
        
        # Estilo de línea
        lc2.lines[0].strokeWidth = 3
        lc2.lines[0].strokeColor = colors.green
        
        # Añadir leyendas
        lc2.lines.symbol = makeMarker('FilledCircle')
        lc2.lines[0].symbol.size = 6
        lc2.lines[0].symbol.fillColor = colors.green
        
        # Añadir títulos
        lc2.categoryAxis.labelAxisMode = 'low'
        lc2.valueAxis.labelTextFormat = '$%0.2f'
        lc2.categoryAxis.title = 'Fecha'
        lc2.valueAxis.title = 'Ingresos ($)'
        
        # Añadir leyenda
        legend2 = Legend()
        legend2.alignment = 'right'
        legend2.x = 480
        legend2.y = 150
        legend2.colorNamePairs = [(colors.green, 'Ingresos ($)')]
        lc2.legend = legend2
        
        drawing2.add(lc2)
        elements.append(drawing2)
    
    # Generar PDF
    doc.build(elements)
    
    return ruta_archivo

def _generar_excel_ventas_por_cliente(resultados, titulo, fecha_inicio, fecha_fin, incluir_grafico=True):
    """Genera un archivo Excel para el reporte de ventas por cliente"""
    nombre_archivo = f"ventas_por_cliente_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
    ruta_archivo = os.path.join(REPORTES_DIR, nombre_archivo)
    
    # Crear un nuevo libro de Excel y una hoja
    workbook = xlsxwriter.Workbook(ruta_archivo)
    worksheet = workbook.add_worksheet("Ventas por Cliente")
    
    # Añadir formatos
    titulo_formato = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'center',
        'valign': 'vcenter'
    })
    
    encabezado_formato = workbook.add_format({
        'bold': True,
        'bg_color': '#F3AD4E',  # Color cookie
        'border': 1,
        'align': 'center'
    })
    
    texto_formato = workbook.add_format({
        'border': 1
    })
    
    numero_formato = workbook.add_format({
        'border': 1,
        'num_format': '#,##0'
    })
    
    moneda_formato = workbook.add_format({
        'border': 1,
        'num_format': '$#,##0.00'
    })
    
    total_formato = workbook.add_format({
        'bold': True,
        'border': 1,
        'bg_color': '#F6C177',  # Color cookie claro
    })
    
    total_numero_formato = workbook.add_format({
        'bold': True,
        'border': 1,
        'bg_color': '#F6C177',
        'num_format': '#,##0'
    })
    
    total_moneda_formato = workbook.add_format({
        'bold': True,
        'border': 1,
        'bg_color': '#F6C177',
        'num_format': '$#,##0.00'
    })
    
    # Escribir el título y subtítulo
    worksheet.merge_range('A1:D1', titulo, titulo_formato)
    worksheet.merge_range('A2:D2', f"Período: {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}", titulo_formato)
    
    # Añadir un poco de espacio
    worksheet.write('A3', '')
    
    # Escribir encabezados de columna
    worksheet.write('A4', 'ID Cliente', encabezado_formato)
    worksheet.write('B4', 'Nombre Cliente', encabezado_formato)
    worksheet.write('C4', 'Cantidad de Ventas', encabezado_formato)
    worksheet.write('D4', 'Total ($)', encabezado_formato)
    
    # Establecer anchos de columna
    worksheet.set_column('A:A', 10)
    worksheet.set_column('B:B', 30)
    worksheet.set_column('C:C', 15)
    worksheet.set_column('D:D', 15)
    
    # Escribir datos
    fila = 4
    for id_cliente, nombre, cantidad, total in resultados:
        worksheet.write_number(fila, 0, id_cliente, texto_formato)
        worksheet.write_string(fila, 1, nombre, texto_formato)
        worksheet.write_number(fila, 2, cantidad, numero_formato)
        worksheet.write_number(fila, 3, total, moneda_formato)
        fila += 1
    
    # Escribir totales
    total_ventas = sum(cantidad for _, _, cantidad, _ in resultados)
    total_ingresos = sum(total for _, _, _, total in resultados)
    
    worksheet.write(fila, 0, '', total_formato)
    worksheet.write(fila, 1, 'TOTAL', total_formato)
    worksheet.write_number(fila, 2, total_ventas, total_numero_formato)
    worksheet.write_number(fila, 3, total_ingresos, total_moneda_formato)
    
    # Añadir gráfico si se solicita
    if incluir_grafico and len(resultados) > 0:
        # Gráfico de barras para la cantidad de ventas por cliente
        chart1 = workbook.add_chart({'type': 'column'})
        
        # Añadir serie de datos al gráfico
        chart1.add_series({
            'name': 'Cantidad de Ventas',
            'categories': ['Ventas por Cliente', 4, 1, fila-1, 1],  # Nombre de clientes
            'values': ['Ventas por Cliente', 4, 2, fila-1, 2],      # Cantidad de ventas
            'fill': {'color': '#F3AD4E'},
        })
        
        # Configurar el gráfico
        chart1.set_title({'name': 'Cantidad de Ventas por Cliente'})
        chart1.set_x_axis({'name': 'Cliente'})
        chart1.set_y_axis({'name': 'Cantidad'})
        chart1.set_style(11)  # Estilo de gráfico
        
        # Añadir el gráfico a la hoja
        worksheet.insert_chart('A' + str(fila + 3), chart1, {'x_scale': 1.5, 'y_scale': 1})
        
        # Gráfico de barras para el total de ventas por cliente
        chart2 = workbook.add_chart({'type': 'column'})
        
        # Añadir serie de datos al gráfico
        chart2.add_series({
            'name': 'Total de Ventas ($)',
            'categories': ['Ventas por Cliente', 4, 1, fila-1, 1],  # Nombre de clientes
            'values': ['Ventas por Cliente', 4, 3, fila-1, 3],      # Total de ventas
            'fill': {'color': '#3CB371'},  # Verde medio
        })
        
        # Configurar el gráfico
        chart2.set_title({'name': 'Total de Ventas por Cliente ($)'})
        chart2.set_x_axis({'name': 'Cliente'})
        chart2.set_y_axis({'name': 'Total ($)'})
        chart2.set_style(11)  # Estilo de gráfico
        
        # Añadir el gráfico a la hoja
        worksheet.insert_chart('A' + str(fila + 20), chart2, {'x_scale': 1.5, 'y_scale': 1})
    
    # Cerrar el libro
    workbook.close()
    
    return ruta_archivo

def _generar_pdf_ventas_por_cliente(resultados, titulo, fecha_inicio, fecha_fin, incluir_grafico=True):
    """Genera un archivo PDF para el reporte de ventas por cliente"""
    nombre_archivo = f"ventas_por_cliente_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    ruta_archivo = os.path.join(REPORTES_DIR, nombre_archivo)
    
    # Crear documento
    doc = SimpleDocTemplate(ruta_archivo, pagesize=letter)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Añadir título
    title_style = styles["Title"]
    title_style.alignment = 1  # 0=Izquierda, 1=Centro, 2=Derecha
    elements.append(Paragraph(titulo, title_style))
    
    # Añadir período
    subtitle_style = styles["Heading2"]
    subtitle_style.alignment = 1
    elements.append(Paragraph(f"Período: {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}", subtitle_style))
    
    # Añadir espacio
    elements.append(Spacer(1, 0.25*inch))
    
    # Preparar datos para la tabla
    data = [['ID', 'Cliente', 'Cantidad de Ventas', 'Total ($)']]
    
    for id_cliente, nombre, cantidad, total in resultados:
        data.append([
            str(id_cliente),
            nombre,
            str(cantidad),
            f"${total:.2f}"
        ])
    
    # Añadir totales
    total_ventas = sum(cantidad for _, _, cantidad, _ in resultados)
    total_ingresos = sum(total for _, _, _, total in resultados)
    
    data.append(['', 'TOTAL', str(total_ventas), f"${total_ingresos:.2f}"])
    
    # Crear tabla
    table = Table(data, colWidths=[0.5*inch, 2.5*inch, 1.5*inch, 1.5*inch])
    
    # Estilo de tabla
    style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F3AD4E')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 12),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#F6C177')),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('ALIGN', (2,1), (-1,-1), 'RIGHT'),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ])
    
    table.setStyle(style)
    elements.append(table)
    
    # Añadir gráfico si se solicita
    if incluir_grafico and len(resultados) > 0:
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph("Gráfico de Ventas por Cliente", styles["Heading3"]))
        elements.append(Spacer(1, 0.25*inch))
        
        # Crear gráfico de barras
        drawing = Drawing(500, 250)
        
        # Limitar a los 10 primeros clientes si hay más
        clientes_display = resultados[:10] if len(resultados) > 10 else resultados
        
        # Extraer datos para el gráfico
        nombres = [nombre[:15] + '...' if len(nombre) > 15 else nombre for _, nombre, _, _ in clientes_display]
        cantidades = [cantidad for _, _, cantidad, _ in clientes_display]
        
        # Crear el gráfico de barras
        bc = VerticalBarChart()
        bc.x = 50
        bc.y = 50
        bc.height = 150
        bc.width = 400
        bc.data = [cantidades]
        
        # Configurar categorías en el eje X
        bc.categoryAxis.categoryNames = nombres
        bc.categoryAxis.labels.boxAnchor = 'ne'
        bc.categoryAxis.labels.angle = 30
        bc.categoryAxis.labels.fontSize = 8
        
        # Configurar etiquetas en el eje Y
        bc.valueAxis.valueMin = 0
        bc.valueAxis.valueMax = max(cantidades) * 1.2 if cantidades else 10
        bc.valueAxis.valueStep = max(1, max(cantidades) // 5) if cantidades else 2
        
        # Estilo de barras
        bc.bars[0].fillColor = colors.HexColor('#F3AD4E')
        
        # Añadir títulos
        bc.categoryAxis.title = 'Clientes'
        bc.valueAxis.title = 'Cantidad de Ventas'
        
        drawing.add(bc)
        elements.append(drawing)
        
        # Gráfico para ingresos
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph("Ingresos por Cliente", styles["Heading3"]))
        elements.append(Spacer(1, 0.25*inch))
        
        drawing2 = Drawing(500, 250)
        
        totales = [total for _, _, _, total in clientes_display]
        
        # Crear el gráfico de barras
        bc2 = VerticalBarChart()
        bc2.x = 50
        bc2.y = 50
        bc2.height = 150
        bc2.width = 400
        bc2.data = [totales]
        
        # Configurar categorías en el eje X
        bc2.categoryAxis.categoryNames = nombres
        bc2.categoryAxis.labels.boxAnchor = 'ne'
        bc2.categoryAxis.labels.angle = 30
        bc2.categoryAxis.labels.fontSize = 8
        
        # Configurar etiquetas en el eje Y
        bc2.valueAxis.valueMin = 0
        bc2.valueAxis.valueMax = max(totales) * 1.2 if totales else 10
        bc2.valueAxis.valueStep = max(1, max(totales) // 5) if totales else 2
        
        # Estilo de barras
        bc2.bars[0].fillColor = colors.green
        
        # Añadir títulos
        bc2.categoryAxis.title = 'Clientes'
        bc2.valueAxis.title = 'Ingresos ($)'
        
        drawing2.add(bc2)
        elements.append(drawing2)
    
    # Generar PDF
    doc.build(elements)
    
    return ruta_archivo

def _generar_excel_ventas_por_producto(resultados, titulo, fecha_inicio, fecha_fin, incluir_grafico=True):
    """Genera un archivo Excel para el reporte de ventas por producto"""
    nombre_archivo = f"ventas_por_producto_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
    ruta_archivo = os.path.join(REPORTES_DIR, nombre_archivo)
    
    # Crear un nuevo libro de Excel y una hoja
    workbook = xlsxwriter.Workbook(ruta_archivo)
    worksheet = workbook.add_worksheet("Ventas por Producto")
    
    # Añadir formatos
    titulo_formato = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'center',
        'valign': 'vcenter'
    })
    
    encabezado_formato = workbook.add_format({
        'bold': True,
        'bg_color': '#F3AD4E',  # Color cookie
        'border': 1,
        'align': 'center'
    })
    
    texto_formato = workbook.add_format({
        'border': 1
    })
    
    numero_formato = workbook.add_format({
        'border': 1,
        'num_format': '#,##0'
    })
    
    moneda_formato = workbook.add_format({
        'border': 1,
        'num_format': '$#,##0.00'
    })
    
    total_formato = workbook.add_format({
        'bold': True,
        'border': 1,
        'bg_color': '#F6C177',  # Color cookie claro
    })
    
    total_numero_formato = workbook.add_format({
        'bold': True,
        'border': 1,
        'bg_color': '#F6C177',
        'num_format': '#,##0'
    })
    
    total_moneda_formato = workbook.add_format({
        'bold': True,
        'border': 1,
        'bg_color': '#F6C177',
        'num_format': '$#,##0.00'
    })
    
    # Escribir el título y subtítulo
    worksheet.merge_range('A1:D1', titulo, titulo_formato)
    worksheet.merge_range('A2:D2', f"Período: {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}", titulo_formato)
    
    # Añadir un poco de espacio
    worksheet.write('A3', '')
    
    # Escribir encabezados de columna
    worksheet.write('A4', 'ID Producto', encabezado_formato)
    worksheet.write('B4', 'Nombre Producto', encabezado_formato)
    worksheet.write('C4', 'Cantidad Vendida', encabezado_formato)
    worksheet.write('D4', 'Total ($)', encabezado_formato)
    
    # Establecer anchos de columna
    worksheet.set_column('A:A', 10)
    worksheet.set_column('B:B', 30)
    worksheet.set_column('C:C', 15)
    worksheet.set_column('D:D', 15)
    
    # Escribir datos
    fila = 4
    for id_producto, nombre, cantidad, total in resultados:
        worksheet.write_number(fila, 0, id_producto, texto_formato)
        worksheet.write_string(fila, 1, nombre, texto_formato)
        worksheet.write_number(fila, 2, cantidad, numero_formato)
        worksheet.write_number(fila, 3, total, moneda_formato)
        fila += 1
    
    # Escribir totales
    total_cantidad = sum(cantidad for _, _, cantidad, _ in resultados)
    total_ingresos = sum(total for _, _, _, total in resultados)
    
    worksheet.write(fila, 0, '', total_formato)
    worksheet.write(fila, 1, 'TOTAL', total_formato)
    worksheet.write_number(fila, 2, total_cantidad, total_numero_formato)
    worksheet.write_number(fila, 3, total_ingresos, total_moneda_formato)
    
    # Añadir gráfico si se solicita
    if incluir_grafico and len(resultados) > 0:
        # Gráfico de barras para la cantidad vendida por producto
        chart1 = workbook.add_chart({'type': 'column'})
        
        # Limitar a los 10 productos más vendidos
        max_display = min(10, len(resultados))
        
        # Añadir serie de datos al gráfico
        chart1.add_series({
            'name': 'Cantidad Vendida',
            'categories': ['Ventas por Producto', 4, 1, 4 + max_display - 1, 1],  # Nombre de productos
            'values': ['Ventas por Producto', 4, 2, 4 + max_display - 1, 2],      # Cantidad vendida
            'fill': {'color': '#F3AD4E'},
        })
        
        # Configurar el gráfico
        chart1.set_title({'name': 'Cantidad Vendida por Producto (Top 10)'})
        chart1.set_x_axis({'name': 'Producto'})
        chart1.set_y_axis({'name': 'Cantidad'})
        chart1.set_style(11)  # Estilo de gráfico
        
        # Añadir el gráfico a la hoja
        worksheet.insert_chart('A' + str(fila + 3), chart1, {'x_scale': 1.5, 'y_scale': 1})
        
        # Gráfico de pastel para el % de ventas por producto
        chart2 = workbook.add_chart({'type': 'pie'})
        
        # Añadir serie de datos al gráfico
        chart2.add_series({
            'name': 'Ventas por Producto',
            'categories': ['Ventas por Producto', 4, 1, 4 + max_display - 1, 1],  # Nombre de productos
            'values': ['Ventas por Producto', 4, 3, 4 + max_display - 1, 3],      # Total de ventas
            'data_labels': {'percentage': True, 'category': True, 'font': {'size': 9}},
        })
        
        # Configurar el gráfico
        chart2.set_title({'name': 'Distribución de Ventas por Producto (Top 10)'})
        chart2.set_style(10)  # Estilo de gráfico
        
        # Añadir el gráfico a la hoja
        worksheet.insert_chart('A' + str(fila + 20), chart2, {'x_scale': 1.5, 'y_scale': 1})
    
    # Cerrar el libro
    workbook.close()
    
    return ruta_archivo

def _generar_pdf_ventas_por_producto(resultados, titulo, fecha_inicio, fecha_fin, incluir_grafico=True):
    """Genera un archivo PDF para el reporte de ventas por producto"""
    nombre_archivo = f"ventas_por_producto_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    ruta_archivo = os.path.join(REPORTES_DIR, nombre_archivo)
    
    # Crear documento
    doc = SimpleDocTemplate(ruta_archivo, pagesize=letter)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Añadir título
    title_style = styles["Title"]
    title_style.alignment = 1  # 0=Izquierda, 1=Centro, 2=Derecha
    elements.append(Paragraph(titulo, title_style))
    
    # Añadir período
    subtitle_style = styles["Heading2"]
    subtitle_style.alignment = 1
    elements.append(Paragraph(f"Período: {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}", subtitle_style))
    
    # Añadir espacio
    elements.append(Spacer(1, 0.25*inch))
    
    # Preparar datos para la tabla
    data = [['ID', 'Producto', 'Cantidad Vendida', 'Total ($)']]
    
    for id_producto, nombre, cantidad, total in resultados:
        data.append([
            str(id_producto),
            nombre,
            str(cantidad),
            f"${total:.2f}"
        ])
    
    # Añadir totales
    total_cantidad = sum(cantidad for _, _, cantidad, _ in resultados)
    total_ingresos = sum(total for _, _, _, total in resultados)
    
    data.append(['', 'TOTAL', str(total_cantidad), f"${total_ingresos:.2f}"])
    
    # Crear tabla
    table = Table(data, colWidths=[0.5*inch, 3*inch, 1.5*inch, 1*inch])
    
    # Estilo de tabla
    style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F3AD4E')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 12),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#F6C177')),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('ALIGN', (2,1), (-1,-1), 'RIGHT'),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ])
    
    table.setStyle(style)
    elements.append(table)
    
    # Añadir gráfico si se solicita
    if incluir_grafico and len(resultados) > 0:
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph("Productos más vendidos", styles["Heading3"]))
        elements.append(Spacer(1, 0.25*inch))
        
        # Limitar a los 10 primeros productos si hay más
        productos_display = resultados[:10] if len(resultados) > 10 else resultados
        
        # Crear gráfico de barras
        drawing = Drawing(500, 250)
        
        # Extraer datos para el gráfico
        nombres = [nombre[:15] + '...' if len(nombre) > 15 else nombre for _, nombre, _, _ in productos_display]
        cantidades = [cantidad for _, _, cantidad, _ in productos_display]
        
        # Crear el gráfico de barras
        bc = VerticalBarChart()
        bc.x = 50
        bc.y = 50
        bc.height = 150
        bc.width = 400
        bc.data = [cantidades]
        
        # Configurar categorías en el eje X
        bc.categoryAxis.categoryNames = nombres
        bc.categoryAxis.labels.boxAnchor = 'ne'
        bc.categoryAxis.labels.angle = 30
        bc.categoryAxis.labels.fontSize = 8
        
        # Configurar etiquetas en el eje Y
        bc.valueAxis.valueMin = 0
        bc.valueAxis.valueMax = max(cantidades) * 1.2 if cantidades else 10
        bc.valueAxis.valueStep = max(1, max(cantidades) // 5) if cantidades else 2
        
        # Estilo de barras
        bc.bars[0].fillColor = colors.HexColor('#F3AD4E')
        
        # Añadir títulos
        bc.categoryAxis.title = 'Productos'
        bc.valueAxis.title = 'Cantidad Vendida'
        
        drawing.add(bc)
        elements.append(drawing)
        
        # Gráfico de pastel para mostrar la distribución de ventas
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph("Distribución de Ventas por Producto", styles["Heading3"]))
        elements.append(Spacer(1, 0.25*inch))
        
        drawing2 = Drawing(500, 250)
        
        # Crear datos para el gráfico de pastel
        totales = [total for _, _, _, total in productos_display]
        
        # Crear el gráfico de pastel
        pie = Pie()
        pie.x = 150
        pie.y = 100
        pie.width = 200
        pie.height = 200
        pie.data = totales
        pie.labels = [f"{nombre[:10]}..." if len(nombre) > 10 else nombre for _, nombre, _, _ in productos_display]
        pie.slices.strokeWidth = 0.5
        
        # Añadir colores diferentes para cada sector
        colores = [colors.HexColor('#F3AD4E'), colors.HexColor('#3CB371'), 
                  colors.blue, colors.red, colors.purple, colors.orange,
                  colors.pink, colors.lightblue, colors.lightgreen, colors.yellow]
        
        for i, color in enumerate(colores[:len(productos_display)]):
            pie.slices[i].fillColor = color
        
        drawing2.add(pie)
        elements.append(drawing2)
    
    # Generar PDF
    doc.build(elements)
    
    return ruta_archivo

def _generar_excel_ventas_por_tipo(resultados, titulo, fecha_inicio, fecha_fin, incluir_grafico=True):
    """Genera un archivo Excel para el reporte de ventas por tipo"""
    nombre_archivo = f"ventas_por_tipo_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
    ruta_archivo = os.path.join(REPORTES_DIR, nombre_archivo)
    
    # Crear un nuevo libro de Excel y una hoja
    workbook = xlsxwriter.Workbook(ruta_archivo)
    worksheet = workbook.add_worksheet("Ventas por Tipo")
    
    # Añadir formatos
    titulo_formato = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'center',
        'valign': 'vcenter'
    })
    
    encabezado_formato = workbook.add_format({
        'bold': True,
        'bg_color': '#F3AD4E',  # Color cookie
        'border': 1,
        'align': 'center'
    })
    
    texto_formato = workbook.add_format({
        'border': 1
    })
    
    numero_formato = workbook.add_format({
        'border': 1,
        'num_format': '#,##0'
    })
    
    moneda_formato = workbook.add_format({
        'border': 1,
        'num_format': '$#,##0.00'
    })
    
    total_formato = workbook.add_format({
        'bold': True,
        'border': 1,
        'bg_color': '#F6C177',  # Color cookie claro
    })
    
    total_numero_formato = workbook.add_format({
        'bold': True,
        'border': 1,
        'bg_color': '#F6C177',
        'num_format': '#,##0'
    })
    
    total_moneda_formato = workbook.add_format({
        'bold': True,
        'border': 1,
        'bg_color': '#F6C177',
        'num_format': '$#,##0.00'
    })
    
    # Escribir el título y subtítulo
    worksheet.merge_range('A1:D1', titulo, titulo_formato)
    worksheet.merge_range('A2:D2', f"Período: {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}", titulo_formato)
    
    # Añadir un poco de espacio
    worksheet.write('A3', '')
    
    # Escribir encabezados de columna
    worksheet.write('A4', 'Tipo de Venta', encabezado_formato)
    worksheet.write('B4', 'Cantidad de Ventas', encabezado_formato)
    worksheet.write('C4', 'Cantidad de Productos', encabezado_formato)
    worksheet.write('D4', 'Total ($)', encabezado_formato)
    
    # Establecer anchos de columna
    worksheet.set_column('A:A', 15)
    worksheet.set_column('B:B', 18)
    worksheet.set_column('C:C', 20)
    worksheet.set_column('D:D', 15)
    
    # Escribir datos
    fila = 4
    for tipo, cantidad_ventas, cantidad_productos, total in resultados:
        worksheet.write_string(fila, 0, tipo, texto_formato)
        worksheet.write_number(fila, 1, cantidad_ventas, numero_formato)
        worksheet.write_number(fila, 2, cantidad_productos, numero_formato)
        worksheet.write_number(fila, 3, total, moneda_formato)
        fila += 1
    
    # Escribir totales
    total_cantidad_ventas = sum(cantidad_ventas for _, cantidad_ventas, _, _ in resultados)
    total_cantidad_productos = sum(cantidad_productos for _, _, cantidad_productos, _ in resultados)
    total_ingresos = sum(total for _, _, _, total in resultados)
    
    worksheet.write(fila, 0, 'TOTAL', total_formato)
    worksheet.write_number(fila, 1, total_cantidad_ventas, total_numero_formato)
    worksheet.write_number(fila, 2, total_cantidad_productos, total_numero_formato)
    worksheet.write_number(fila, 3, total_ingresos, total_moneda_formato)
    
    # Añadir gráfico si se solicita
    if incluir_grafico and len(resultados) > 0:
        # Gráfico de barras para comparar los tipos de venta
        chart1 = workbook.add_chart({'type': 'column'})
        
        # Añadir series de datos al gráfico
        chart1.add_series({
            'name': 'Cantidad de Ventas',
            'categories': ['Ventas por Tipo', 4, 0, fila-1, 0],
            'values': ['Ventas por Tipo', 4, 1, fila-1, 1],
            'fill': {'color': '#F3AD4E'},
        })
        
        chart1.add_series({
            'name': 'Cantidad de Productos',
            'categories': ['Ventas por Tipo', 4, 0, fila-1, 0],
            'values': ['Ventas por Tipo', 4, 2, fila-1, 2],
            'fill': {'color': '#3CB371'},
        })
        
        # Configurar el gráfico
        chart1.set_title({'name': 'Comparativa por Tipo de Venta'})
        chart1.set_x_axis({'name': 'Tipo de Venta'})
        chart1.set_y_axis({'name': 'Cantidad'})
        chart1.set_style(11)  # Estilo de gráfico
        
        # Añadir el gráfico a la hoja
        worksheet.insert_chart('A' + str(fila + 3), chart1, {'x_scale': 1.5, 'y_scale': 1})
        
        # Gráfico de pastel para el % de ingresos por tipo
        chart2 = workbook.add_chart({'type': 'pie'})
        
        # Añadir serie de datos al gráfico
        chart2.add_series({
            'name': 'Ingresos por Tipo',
            'categories': ['Ventas por Tipo', 4, 0, fila-1, 0],
            'values': ['Ventas por Tipo', 4, 3, fila-1, 3],
            'data_labels': {'percentage': True, 'category': True, 'font': {'size': 9}},
        })
        
        # Configurar el gráfico
        chart2.set_title({'name': 'Distribución de Ingresos por Tipo de Venta'})
        chart2.set_style(10)  # Estilo de gráfico
        
        # Añadir el gráfico a la hoja
        worksheet.insert_chart('A' + str(fila + 20), chart2, {'x_scale': 1.5, 'y_scale': 1})
    
    # Cerrar el libro
    workbook.close()
    
    return ruta_archivo

def _generar_pdf_ventas_por_tipo(resultados, titulo, fecha_inicio, fecha_fin, incluir_grafico=True):
    """Genera un archivo PDF para el reporte de ventas por tipo"""
    nombre_archivo = f"ventas_por_tipo_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    ruta_archivo = os.path.join(REPORTES_DIR, nombre_archivo)
    
    # Crear documento
    doc = SimpleDocTemplate(ruta_archivo, pagesize=letter)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Añadir título
    title_style = styles["Title"]
    title_style.alignment = 1  # 0=Izquierda, 1=Centro, 2=Derecha
    elements.append(Paragraph(titulo, title_style))
    
    # Añadir período
    subtitle_style = styles["Heading2"]
    subtitle_style.alignment = 1
    elements.append(Paragraph(f"Período: {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}", subtitle_style))
    
    # Añadir espacio
    elements.append(Spacer(1, 0.25*inch))
    
    # Preparar datos para la tabla
    data = [['Tipo de Venta', 'Cantidad de Ventas', 'Cantidad de Productos', 'Total ($)']]
    
    for tipo, cantidad_ventas, cantidad_productos, total in resultados:
        data.append([
            tipo,
            str(cantidad_ventas),
            str(cantidad_productos),
            f"${total:.2f}"
        ])
    
    # Añadir totales
    total_cantidad_ventas = sum(cantidad_ventas for _, cantidad_ventas, _, _ in resultados)
    total_cantidad_productos = sum(cantidad_productos for _, _, cantidad_productos, _ in resultados)
    total_ingresos = sum(total for _, _, _, total in resultados)
    
    data.append(['TOTAL', str(total_cantidad_ventas), str(total_cantidad_productos), f"${total_ingresos:.2f}"])
    
    # Crear tabla
    table = Table(data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    
    # Estilo de tabla
    style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F3AD4E')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 12),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#F6C177')),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ])
    
    table.setStyle(style)
    elements.append(table)
    
    # Añadir gráfico si se solicita
    if incluir_grafico and len(resultados) > 0:
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph("Comparativa por Tipo de Venta", styles["Heading3"]))
        elements.append(Spacer(1, 0.25*inch))
        
        # Crear gráfico de barras
        drawing = Drawing(500, 250)
        
        # Extraer datos para el gráfico
        tipos = [tipo for tipo, _, _, _ in resultados]
        cantidades_ventas = [cantidad_ventas for _, cantidad_ventas, _, _ in resultados]
        cantidades_productos = [cantidad_productos for _, _, cantidad_productos, _ in resultados]
        
        # Crear el gráfico de barras
        bc = VerticalBarChart()
        bc.x = 50
        bc.y = 50
        bc.height = 150
        bc.width = 400
        bc.data = [cantidades_ventas, cantidades_productos]
        
        # Configurar categorías en el eje X
        bc.categoryAxis.categoryNames = tipos
        bc.categoryAxis.labels.boxAnchor = 'ne'
        bc.categoryAxis.labels.angle = 30
        bc.categoryAxis.labels.fontSize = 8
        
        # Configurar etiquetas en el eje Y
        max_valor = max(max(cantidades_ventas), max(cantidades_productos)) if cantidades_ventas and cantidades_productos else 10
        bc.valueAxis.valueMin = 0
        bc.valueAxis.valueMax = max_valor * 1.2
        bc.valueAxis.valueStep = max(1, max_valor // 5)
        
        # Estilo de barras
        bc.bars[0].fillColor = colors.HexColor('#F3AD4E')
        bc.bars[1].fillColor = colors.HexColor('#3CB371')
        
        # Añadir títulos y leyendas
        bc.categoryAxis.title = 'Tipo de Venta'
        bc.valueAxis.title = 'Cantidad'
        
        # Añadir leyenda
        legend = Legend()
        legend.alignment = 'right'
        legend.x = 480
        legend.y = 150
        legend.colorNamePairs = [(colors.HexColor('#F3AD4E'), 'Cantidad de Ventas'),
                                 (colors.HexColor('#3CB371'), 'Cantidad de Productos')]
        bc.legend = legend
        
        drawing.add(bc)
        elements.append(drawing)
        
        # Gráfico de pastel para ingresos por tipo
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph("Distribución de Ingresos por Tipo", styles["Heading3"]))
        elements.append(Spacer(1, 0.25*inch))
        
        drawing2 = Drawing(500, 250)
        
        # Crear datos para el gráfico de pastel
        ingresos = [total for _, _, _, total in resultados]
        
        # Crear el gráfico de pastel
        pie = Pie()
        pie.x = 150
        pie.y = 100
        pie.width = 200
        pie.height = 200
        pie.data = ingresos
        pie.labels = [f"{tipo}" for tipo, _, _, _ in resultados]
        pie.slices.strokeWidth = 0.5
        
        # Añadir colores diferentes para cada sector
        colores = [colors.HexColor('#F3AD4E'), colors.HexColor('#3CB371')]
        
        for i, color in enumerate(colores[:len(resultados)]):
            pie.slices[i].fillColor = color
        
        drawing2.add(pie)
        elements.append(drawing2)
    
    # Generar PDF
    doc.build(elements)
    
    return ruta_archivo

def _generar_excel_inventario_actual(resultados, titulo, incluir_grafico=True):
    """Genera un archivo Excel para el reporte de inventario actual"""
    nombre_archivo = f"inventario_actual_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
    ruta_archivo = os.path.join(REPORTES_DIR, nombre_archivo)
    
    # Crear un nuevo libro de Excel y una hoja
    workbook = xlsxwriter.Workbook(ruta_archivo)
    worksheet = workbook.add_worksheet("Inventario Actual")
    
    # Añadir formatos
    titulo_formato = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'center',
        'valign': 'vcenter'
    })
    
    encabezado_formato = workbook.add_format({
        'bold': True,
        'bg_color': '#F3AD4E',  # Color cookie
        'border': 1,
        'align': 'center'
    })
    
    texto_formato = workbook.add_format({
        'border': 1
    })
    
    numero_formato = workbook.add_format({
        'border': 1,
        'num_format': '#,##0.00'
    })
    
    moneda_formato = workbook.add_format({
        'border': 1,
        'num_format': '$#,##0.00'
    })
    
    total_formato = workbook.add_format({
        'bold': True,
        'border': 1,
        'bg_color': '#F6C177',  # Color cookie claro
    })
    
    total_numero_formato = workbook.add_format({
        'bold': True,
        'border': 1,
        'bg_color': '#F6C177',
        'num_format': '#,##0.00'
    })
    
    total_moneda_formato = workbook.add_format({
        'bold': True,
        'border': 1,
        'bg_color': '#F6C177',
        'num_format': '$#,##0.00'
    })
    
    # Escribir el título y subtítulo
    worksheet.merge_range('A1:E1', titulo, titulo_formato)
    worksheet.merge_range('A2:E2', f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", titulo_formato)
    
    # Añadir un poco de espacio
    worksheet.write('A3', '')
    
    # Escribir encabezados de columna
    worksheet.write('A4', 'ID', encabezado_formato)
    worksheet.write('B4', 'Ingrediente', encabezado_formato)
    worksheet.write('C4', 'Stock', encabezado_formato)
    worksheet.write('D4', 'Unidad', encabezado_formato)
    worksheet.write('E4', 'Precio Unitario', encabezado_formato)
    
    # Establecer anchos de columna
    worksheet.set_column('A:A', 8)
    worksheet.set_column('B:B', 30)
    worksheet.set_column('C:C', 12)
    worksheet.set_column('D:D', 12)
    worksheet.set_column('E:E', 15)
    
    # Escribir datos
    fila = 4
    for id_ing, nombre, stock, unidad, precio in resultados:
        worksheet.write_number(fila, 0, id_ing, texto_formato)
        worksheet.write_string(fila, 1, nombre, texto_formato)
        worksheet.write_number(fila, 2, stock, numero_formato)
        worksheet.write_string(fila, 3, unidad, texto_formato)
        worksheet.write_number(fila, 4, precio, moneda_formato)
        fila += 1
    
    # Escribir totales
    total_stock = sum(stock for _, _, stock, _, _ in resultados)
    total_valor = sum(stock * precio for _, _, stock, _, precio in resultados)
    
    worksheet.write(fila, 0, '', total_formato)
    worksheet.write(fila, 1, 'TOTAL', total_formato)
    worksheet.write_number(fila, 2, total_stock, total_numero_formato)
    worksheet.write(fila, 3, '', total_formato)
    worksheet.write_number(fila, 4, total_valor, total_moneda_formato)
    
    # Añadir gráfico si se solicita
    if incluir_grafico and len(resultados) > 0:
        # Gráfico de barras para el stock por ingrediente
        chart1 = workbook.add_chart({'type': 'column'})
        
        # Limitar a los 10 ingredientes con mayor stock
        resultados_ordenados = sorted(resultados, key=lambda x: x[2], reverse=True)
        max_display = min(10, len(resultados_ordenados))
        
        # Añadir serie de datos al gráfico
        chart1.add_series({
            'name': 'Stock Actual',
            'categories': ['Inventario Actual', 4, 1, 4 + max_display - 1, 1],  # Nombres
            'values': ['Inventario Actual', 4, 2, 4 + max_display - 1, 2],      # Stock
            'fill': {'color': '#F3AD4E'},
        })
        
        # Configurar el gráfico
        chart1.set_title({'name': 'Ingredientes con Mayor Stock'})
        chart1.set_x_axis({'name': 'Ingrediente'})
        chart1.set_y_axis({'name': 'Cantidad'})
        chart1.set_style(11)  # Estilo de gráfico
        
        # Añadir el gráfico a la hoja
        worksheet.insert_chart('A' + str(fila + 3), chart1, {'x_scale': 1.5, 'y_scale': 1})
        
        # Gráfico de pastel para el valor del inventario
        chart2 = workbook.add_chart({'type': 'pie'})
        
        # Calcular valores de inventario para los ingredientes del top
        valores_display = [(nombre, stock * precio) for id_ing, nombre, stock, unidad, precio in resultados_ordenados[:max_display]]
        
        # Crear una tabla auxiliar para el gráfico de pastel
        worksheet.write('G4', 'Ingrediente', encabezado_formato)
        worksheet.write('H4', 'Valor ($)', encabezado_formato)
        
        for i, (nombre, valor) in enumerate(valores_display):
            worksheet.write_string(4 + i, 6, nombre, texto_formato)
            worksheet.write_number(4 + i, 7, valor, moneda_formato)
        
        # Añadir serie de datos al gráfico de pastel
        chart2.add_series({
            'name': 'Valor de Inventario',
            'categories': ['Inventario Actual', 4, 6, 4 + max_display - 1, 6],  # Nombres
            'values': ['Inventario Actual', 4, 7, 4 + max_display - 1, 7],      # Valores
            'data_labels': {'percentage': True, 'category': True, 'font': {'size': 9}},
        })
        
        # Configurar el gráfico
        chart2.set_title({'name': 'Distribución del Valor de Inventario'})
        chart2.set_style(10)  # Estilo de gráfico
        
        # Añadir el gráfico a la hoja
        worksheet.insert_chart('A' + str(fila + 20), chart2, {'x_scale': 1.5, 'y_scale': 1})
    
    # Cerrar el libro
    workbook.close()
    
    return ruta_archivo

def _generar_pdf_inventario_actual(resultados, titulo, incluir_grafico=True):
    """Genera un archivo PDF para el reporte de inventario actual"""
    nombre_archivo = f"inventario_actual_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    ruta_archivo = os.path.join(REPORTES_DIR, nombre_archivo)
    
    # Crear documento
    doc = SimpleDocTemplate(ruta_archivo, pagesize=letter)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Añadir título
    title_style = styles["Title"]
    title_style.alignment = 1  # 0=Izquierda, 1=Centro, 2=Derecha
    elements.append(Paragraph(titulo, title_style))
    
    # Añadir fecha
    subtitle_style = styles["Heading2"]
    subtitle_style.alignment = 1
    elements.append(Paragraph(f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", subtitle_style))
    
    # Añadir espacio
    elements.append(Spacer(1, 0.25*inch))
    
    # Preparar datos para la tabla
    data = [['ID', 'Ingrediente', 'Stock', 'Unidad', 'Precio Unitario']]
    
    for id_ing, nombre, stock, unidad, precio in resultados:
        data.append([
            str(id_ing),
            nombre,
            f"{stock:.2f}",
            unidad,
            f"${precio:.2f}"
        ])
    
    # Añadir totales
    total_stock = sum(stock for _, _, stock, _, _ in resultados)
    total_valor = sum(stock * precio for _, _, stock, _, precio in resultados)
    
    data.append(['', 'TOTAL', f"{total_stock:.2f}", '', f"${total_valor:.2f}"])
    
    # Crear tabla
    table = Table(data, colWidths=[0.5*inch, 3*inch, 1*inch, 1*inch, 1.5*inch])
    
    # Estilo de tabla
    style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F3AD4E')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 12),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#F6C177')),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('ALIGN', (2,1), (4,-1), 'RIGHT'),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ])
    
    table.setStyle(style)
    elements.append(table)
    
    # Añadir gráfico si se solicita
    if incluir_grafico and len(resultados) > 0:
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph("Inventario por Ingrediente (Top 10)", styles["Heading3"]))
        elements.append(Spacer(1, 0.25*inch))
        
        # Ordenar los resultados por stock (de mayor a menor)
        resultados_ordenados = sorted(resultados, key=lambda x: x[2], reverse=True)
        
        # Limitar a los 10 primeros ingredientes si hay más
        ingredientes_display = resultados_ordenados[:10] if len(resultados_ordenados) > 10 else resultados_ordenados
        
        # Crear gráfico de barras
        drawing = Drawing(500, 250)
        
        # Extraer datos para el gráfico
        nombres = [nombre[:15] + '...' if len(nombre) > 15 else nombre for _, nombre, _, _, _ in ingredientes_display]
        stocks = [stock for _, _, stock, _, _ in ingredientes_display]
        
        # Crear el gráfico de barras
        bc = VerticalBarChart()
        bc.x = 50
        bc.y = 50
        bc.height = 150
        bc.width = 400
        bc.data = [stocks]
        
        # Configurar categorías en el eje X
        bc.categoryAxis.categoryNames = nombres
        bc.categoryAxis.labels.boxAnchor = 'ne'
        bc.categoryAxis.labels.angle = 30
        bc.categoryAxis.labels.fontSize = 8
        
        # Configurar etiquetas en el eje Y
        bc.valueAxis.valueMin = 0
        bc.valueAxis.valueMax = max(stocks) * 1.2 if stocks else 10
        bc.valueAxis.valueStep = max(1, max(stocks) // 5) if stocks else 2
        
        # Estilo de barras
        bc.bars[0].fillColor = colors.HexColor('#F3AD4E')
        
        # Añadir títulos
        bc.categoryAxis.title = 'Ingredientes'
        bc.valueAxis.title = 'Stock'
        
        drawing.add(bc)
        elements.append(drawing)
        
        # Gráfico para el valor del inventario
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph("Valor del Inventario por Ingrediente (Top 10)", styles["Heading3"]))
        elements.append(Spacer(1, 0.25*inch))
        
        drawing2 = Drawing(500, 250)
        
        # Calcular el valor del inventario para cada ingrediente
        valores = [(nombre, stock * precio) for _, nombre, stock, _, precio in ingredientes_display]
        nombres_valor = [nombre for nombre, _ in valores]
        valores_stock = [valor for _, valor in valores]
        
        # Crear el gráfico de barras
        bc2 = VerticalBarChart()
        bc2.x = 50
        bc2.y = 50
        bc2.height = 150
        bc2.width = 400
        bc2.data = [valores_stock]
        
        # Configurar categorías en el eje X
        bc2.categoryAxis.categoryNames = nombres_valor
        bc2.categoryAxis.labels.boxAnchor = 'ne'
        bc2.categoryAxis.labels.angle = 30
        bc2.categoryAxis.labels.fontSize = 8
        
        # Configurar etiquetas en el eje Y
        bc2.valueAxis.valueMin = 0
        bc2.valueAxis.valueMax = max(valores_stock) * 1.2 if valores_stock else 10
        bc2.valueAxis.valueStep = max(1, max(valores_stock) // 5) if valores_stock else 2
        
        # Estilo de barras
        bc2.bars[0].fillColor = colors.green
        
        # Añadir títulos
        bc2.categoryAxis.title = 'Ingredientes'
        bc2.valueAxis.title = 'Valor ($)'
        
        drawing2.add(bc2)
        elements.append(drawing2)
    
    # Generar PDF
    doc.build(elements)
    
    return ruta_archivo


def _generar_excel_caducidad(resultados, titulo, hoy, incluir_grafico=True):
    """Genera un archivo Excel para el reporte de fechas de caducidad"""
    nombre_archivo = f"caducidad_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
    ruta_archivo = os.path.join(REPORTES_DIR, nombre_archivo)
    
    # Crear un nuevo libro de Excel y una hoja
    workbook = xlsxwriter.Workbook(ruta_archivo)
    worksheet = workbook.add_worksheet("Fechas de Caducidad")
    
    # Añadir formatos
    titulo_formato = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'center',
        'valign': 'vcenter'
    })
    
    encabezado_formato = workbook.add_format({
        'bold': True,
        'bg_color': '#F3AD4E',  # Color cookie
        'border': 1,
        'align': 'center'
    })
    
    texto_formato = workbook.add_format({
        'border': 1
    })
    
    numero_formato = workbook.add_format({
        'border': 1,
        'num_format': '#,##0.00'
    })
    
    fecha_formato = workbook.add_format({
        'border': 1,
        'num_format': 'dd/mm/yyyy'
    })
    
    # Formatos para alertas de caducidad
    caducado_formato = workbook.add_format({
        'border': 1,
        'bg_color': '#FF9999',  # Rojo claro
        'num_format': 'dd/mm/yyyy'
    })
    
    proximo_formato = workbook.add_format({
        'border': 1,
        'bg_color': '#FFFF99',  # Amarillo claro
        'num_format': 'dd/mm/yyyy'
    })
    
    # Escribir el título y subtítulo
    worksheet.merge_range('A1:E1', titulo, titulo_formato)
    worksheet.merge_range('A2:E2', f"Fecha del reporte: {hoy.strftime('%d/%m/%Y')}", titulo_formato)
    
    # Añadir un poco de espacio
    worksheet.write('A3', '')
    
    # Escribir encabezados de columna
    worksheet.write('A4', 'ID', encabezado_formato)
    worksheet.write('B4', 'Ingrediente', encabezado_formato)
    worksheet.write('C4', 'Stock', encabezado_formato)
    worksheet.write('D4', 'Unidad', encabezado_formato)
    worksheet.write('E4', 'Fecha de Expiración', encabezado_formato)
    worksheet.write('F4', 'Días Restantes', encabezado_formato)
    
    # Establecer anchos de columna
    worksheet.set_column('A:A', 8)
    worksheet.set_column('B:B', 30)
    worksheet.set_column('C:C', 12)
    worksheet.set_column('D:D', 12)
    worksheet.set_column('E:E', 18)
    worksheet.set_column('F:F', 15)
    
    # Escribir datos
    fila = 4
    for id_ing, nombre, stock, unidad, fecha_exp in resultados:
        worksheet.write_number(fila, 0, id_ing, texto_formato)
        worksheet.write_string(fila, 1, nombre, texto_formato)
        worksheet.write_number(fila, 2, stock, numero_formato)
        worksheet.write_string(fila, 3, unidad, texto_formato)
        
        # Calcular días restantes y aplicar formato según proximidad
        dias_restantes = (fecha_exp - hoy).days if fecha_exp else 0
        
        if dias_restantes < 0:
            # Caducado
            worksheet.write_datetime(fila, 4, fecha_exp, caducado_formato)
            worksheet.write_number(fila, 5, dias_restantes, caducado_formato)
        elif dias_restantes < 30:
            # Próximo a caducar (menos de 30 días)
            worksheet.write_datetime(fila, 4, fecha_exp, proximo_formato)
            worksheet.write_number(fila, 5, dias_restantes, proximo_formato)
        else:
            # Normal
            worksheet.write_datetime(fila, 4, fecha_exp, fecha_formato)
            worksheet.write_number(fila, 5, dias_restantes, texto_formato)
        
        fila += 1
    
    # Añadir gráfico si se solicita
    if incluir_grafico and len(resultados) > 0:
        # Ordenar resultados por fecha de expiración
        datos_grafico = [(nombre, (fecha_exp - hoy).days) for id_ing, nombre, stock, unidad, fecha_exp in resultados if fecha_exp]
        datos_grafico.sort(key=lambda x: x[1])  # Ordenar por días restantes
        
        # Limitar a los 15 ingredientes más próximos a caducar
        datos_grafico = datos_grafico[:15]
        
        # Crear una tabla auxiliar para el gráfico
        worksheet.write('H4', 'Ingrediente', encabezado_formato)
        worksheet.write('I4', 'Días hasta caducidad', encabezado_formato)
        
        for i, (nombre, dias) in enumerate(datos_grafico):
            worksheet.write_string(4 + i, 7, nombre, texto_formato)
            worksheet.write_number(4 + i, 8, dias, numero_formato)
        
        # Gráfico de barras horizontales para mostrar los días restantes
        chart = workbook.add_chart({'type': 'bar'})
        
        # Añadir serie de datos al gráfico
        chart.add_series({
            'name': 'Días hasta caducidad',
            'categories': ['Fechas de Caducidad', 4, 7, 4 + len(datos_grafico) - 1, 7],  # Nombres
            'values': ['Fechas de Caducidad', 4, 8, 4 + len(datos_grafico) - 1, 8],     # Días
            'fill': {'color': '#F3AD4E'},
        })
        
        # Configurar el gráfico
        chart.set_title({'name': 'Ingredientes por Fecha de Caducidad'})
        chart.set_x_axis({'name': 'Días restantes'})
        chart.set_y_axis({'name': 'Ingrediente'})
        chart.set_style(11)  # Estilo de gráfico
        
        # Añadir el gráfico a la hoja
        worksheet.insert_chart('A' + str(fila + 2), chart, {'x_scale': 1.5, 'y_scale': 1.5})
    
    # Cerrar el libro
    workbook.close()
    
    return ruta_archivo

def _generar_pdf_caducidad(resultados, titulo, hoy, incluir_grafico=True):
    """Genera un archivo PDF para el reporte de fechas de caducidad"""
    nombre_archivo = f"caducidad_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    ruta_archivo = os.path.join(REPORTES_DIR, nombre_archivo)
    
    # Crear documento
    doc = SimpleDocTemplate(ruta_archivo, pagesize=letter)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Añadir título
    title_style = styles["Title"]
    title_style.alignment = 1  # 0=Izquierda, 1=Centro, 2=Derecha
    elements.append(Paragraph(titulo, title_style))
    
    # Añadir fecha
    subtitle_style = styles["Heading2"]
    subtitle_style.alignment = 1
    elements.append(Paragraph(f"Fecha del reporte: {hoy.strftime('%d/%m/%Y')}", subtitle_style))
    
    # Añadir espacio
    elements.append(Spacer(1, 0.25*inch))
    
    # Preparar datos para la tabla
    data = [['ID', 'Ingrediente', 'Stock', 'Unidad', 'Fecha Expiración', 'Días']]
    
    # Lista para almacenar datos para el gráfico
    datos_grafico = []
    
    for id_ing, nombre, stock, unidad, fecha_exp in resultados:
        # Calcular días restantes
        dias_restantes = (fecha_exp - hoy).days if fecha_exp else 0
        
        data.append([
            str(id_ing),
            nombre,
            f"{stock:.2f}",
            unidad,
            fecha_exp.strftime('%d/%m/%Y') if fecha_exp else '',
            str(dias_restantes)
        ])
        
        # Guardar para el gráfico
        datos_grafico.append((nombre, dias_restantes))
    
    # Crear tabla
    table = Table(data, colWidths=[0.5*inch, 2*inch, 0.75*inch, 0.75*inch, 1.25*inch, 0.75*inch])
    
    # Estilo de tabla
    style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F3AD4E')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 12),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('ALIGN', (2,1), (5,-1), 'RIGHT'),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ])
    
    # Añadir colores para alertas
    for i, (_, _, _, _, fecha_exp) in enumerate(resultados, 1):
        if fecha_exp:
            dias_restantes = (fecha_exp - hoy).days
            if dias_restantes < 0:
                # Caducado
                style.add('BACKGROUND', (4,i), (5,i), colors.HexColor('#FF9999'))
            elif dias_restantes < 30:
                # Próximo a caducar
                style.add('BACKGROUND', (4,i), (5,i), colors.HexColor('#FFFF99'))
    
    table.setStyle(style)
    elements.append(table)
    
    # Añadir gráfico si se solicita
    if incluir_grafico and len(resultados) > 0:
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph("Ingredientes por Fecha de Caducidad", styles["Heading3"]))
        elements.append(Spacer(1, 0.25*inch))
        
        # Ordenar y limitar a los 15 ingredientes más próximos a caducar
        datos_grafico.sort(key=lambda x: x[1])
        datos_grafico = datos_grafico[:15]
        
        # Crear gráfico de barras horizontales
        drawing = Drawing(500, 250)
        
        # Extraer datos para el gráfico
        nombres = [nombre[:15] + '...' if len(nombre) > 15 else nombre for nombre, _ in datos_grafico]
        dias = [dias for _, dias in datos_grafico]
        
        # Crear el gráfico de barras horizontales
        bc = HorizontalBarChart()
        bc.x = 50
        bc.y = 50
        bc.height = 150
        bc.width = 400
        bc.data = [dias]
        
        # Configurar categorías en el eje Y
        bc.categoryAxis.categoryNames = nombres
        bc.categoryAxis.labels.boxAnchor = 'e'
        bc.categoryAxis.labels.fontSize = 8
        
        # Configurar etiquetas en el eje X
        min_dias = min(dias) if dias else 0
        max_dias = max(dias) if dias else 60
        
        bc.valueAxis.valueMin = min(0, min_dias)  # Puede ser negativo si hay productos caducados
        bc.valueAxis.valueMax = max_dias + 10
        bc.valueAxis.valueStep = 10
        
        # Estilo de barras y colores según días restantes
        for i, (_, dias_restantes) in enumerate(datos_grafico):
            # Asignar colores según los días de caducidad
            if dias_restantes < 0:
                bc.bars[0].fillColor = colors.red
            elif dias_restantes < 30:
                bc.bars[0].fillColor = colors.yellow
            else:
                bc.bars[0].fillColor = colors.green
        
        # Añadir títulos
        bc.categoryAxis.title = 'Ingredientes'
        bc.valueAxis.title = 'Días hasta caducidad'
        
        drawing.add(bc)
        elements.append(drawing)
        
        # Añadir leyenda de colores
        elements.append(Spacer(1, 0.25*inch))
        legend_style = styles["Normal"]
        
        elements.append(Paragraph("<font color='red'>■</font> Caducado (Días negativos)", legend_style))
        elements.append(Paragraph("<font color='yellow'>■</font> Próximo a caducar (Menos de 30 días)", legend_style))
        elements.append(Paragraph("<font color='green'>■</font> OK (Más de 30 días)", legend_style))
    
    # Generar PDF
    doc.build(elements)
    
    return ruta_archivo

def _generar_excel_produccion(datos_reporte, titulo, tipo_reporte, incluir_grafico=True):
    """Genera un archivo Excel para reportes de producción"""
    nombre_archivo = f"produccion_{tipo_reporte}_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
    ruta_archivo = os.path.join(REPORTES_DIR, nombre_archivo)
    
    # Extraer parámetros
    fecha_inicio = datetime.strptime(datos_reporte.get('fecha_inicio', ''), '%Y-%m-%d')
    fecha_fin = datetime.strptime(datos_reporte.get('fecha_fin', ''), '%Y-%m-%d')
    productos_ids = datos_reporte.get('productos', [])
    
    # Crear un nuevo libro de Excel
    workbook = xlsxwriter.Workbook(ruta_archivo)
    worksheet = workbook.add_worksheet(f"Producción - {tipo_reporte}")
    
    # Formatos
    titulo_formato = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'center',
        'valign': 'vcenter'
    })
    
    encabezado_formato = workbook.add_format({
        'bold': True,
        'bg_color': '#F3AD4E',
        'border': 1,
        'align': 'center'
    })
    
    # Escribir encabezado
    worksheet.merge_range('A1:D1', titulo, titulo_formato)
    worksheet.merge_range('A2:D2', f"Período: {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}", titulo_formato)
    
    # Ejemplo de datos (simular datos de producción)
    # En una implementación real, aquí se consultaría la base de datos
    
    if tipo_reporte == 'produccion_diaria':
        # Simular datos de producción diaria
        worksheet.write('A4', 'Fecha', encabezado_formato)
        worksheet.write('B4', 'Cantidad Producida', encabezado_formato)
        worksheet.write('C4', 'Costo ($)', encabezado_formato)
        worksheet.write('D4', 'Eficiencia (%)', encabezado_formato)
        
        # Establecer anchos de columna
        worksheet.set_column('A:A', 15)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 15)
        worksheet.set_column('D:D', 15)
        
        # Datos de ejemplo
        # En una implementación real, estos datos vendrían de una consulta a la base de datos
        delta = fecha_fin - fecha_inicio
        
        fecha_formato = workbook.add_format({
            'border': 1,
            'num_format': 'dd/mm/yyyy'
        })
        
        numero_formato = workbook.add_format({
            'border': 1,
            'num_format': '#,##0'
        })
        
        moneda_formato = workbook.add_format({
            'border': 1,
            'num_format': '$#,##0.00'
        })
        
        porcentaje_formato = workbook.add_format({
            'border': 1,
            'num_format': '0.00%'
        })
        
        # Generar datos para cada día
        fechas = []
        cantidades = []
        costos = []
        eficiencias = []
        
        for i in range(delta.days + 1):
            fecha = fecha_inicio + timedelta(days=i)
            fechas.append(fecha)
            
            # Datos aleatorios para ejemplo
            cantidad = 100 + i * 5
            costo = cantidad * 2.5
            eficiencia = 0.75 + (i % 10) / 100
            
            cantidades.append(cantidad)
            costos.append(costo)
            eficiencias.append(eficiencia)
            
            # Escribir los datos
            worksheet.write_datetime(4 + i, 0, fecha, fecha_formato)
            worksheet.write_number(4 + i, 1, cantidad, numero_formato)
            worksheet.write_number(4 + i, 2, costo, moneda_formato)
            worksheet.write_number(4 + i, 3, eficiencia, porcentaje_formato)
        
        # Añadir gráfico si se solicita
        if incluir_grafico:
            chart = workbook.add_chart({'type': 'line'})
            
            # Configurar datos del gráfico
            chart.add_series({
                'name': 'Cantidad Producida',
                'categories': [f'Producción - {tipo_reporte}', 4, 0, 4 + delta.days, 0],
                'values': [f'Producción - {tipo_reporte}', 4, 1, 4 + delta.days, 1],
                'line': {'color': '#F3AD4E', 'width': 2.25},
            })
            
            chart.add_series({
                'name': 'Eficiencia (%)',
                'categories': [f'Producción - {tipo_reporte}', 4, 0, 4 + delta.days, 0],
                'values': [f'Producción - {tipo_reporte}', 4, 3, 4 + delta.days, 3],
                'line': {'color': '#3CB371', 'width': 2.25},
                'y2_axis': True,
            })
            
            # Añadir título y etiquetas
            chart.set_title({'name': 'Producción Diaria y Eficiencia'})
            chart.set_x_axis({'name': 'Fecha'})
            chart.set_y_axis({'name': 'Cantidad'})
            chart.set_y2_axis({'name': 'Eficiencia'})
            
            # Insertar el gráfico
            chart.set_size({'width': 720, 'height': 400})
            worksheet.insert_chart('F4', chart)
    
    elif tipo_reporte == 'produccion_por_producto':
        # Simular datos de producción por producto
        worksheet.write('A4', 'Producto', encabezado_formato)
        worksheet.write('B4', 'Cantidad Producida', encabezado_formato)
        worksheet.write('C4', 'Costo Total ($)', encabezado_formato)
        worksheet.write('D4', 'Costo Unitario ($)', encabezado_formato)
        
        # Establecer anchos de columna
        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 15)
        worksheet.set_column('D:D', 15)
        
        texto_formato = workbook.add_format({
            'border': 1
        })
        
        numero_formato = workbook.add_format({
            'border': 1,
            'num_format': '#,##0'
        })
        
        moneda_formato = workbook.add_format({
            'border': 1,
            'num_format': '$#,##0.00'
        })
        
        # Datos de ejemplo para productos
        # En una implementación real, estos datos vendrían de una consulta a la base de datos
        productos = [
            "Galleta de Chocolate",
            "Galleta de Vainilla",
            "Galleta de Fresa",
            "Galleta de Limón",
            "Galleta de Coco",
            "Galleta de Nuez",
            "Galleta Integral",
            "Galleta sin Gluten",
            "Galleta de Mantequilla",
            "Galleta de Canela"
        ]
        
        cantidades = []
        costos_totales = []
        costos_unitarios = []
        
        for i, producto in enumerate(productos):
            # Datos aleatorios para ejemplo
            cantidad = 500 + i * 100
            costo_total = cantidad * (2.0 + i * 0.25)
            costo_unitario = costo_total / cantidad
            
            cantidades.append(cantidad)
            costos_totales.append(costo_total)
            costos_unitarios.append(costo_unitario)
            
            # Escribir los datos
            worksheet.write_string(4 + i, 0, producto, texto_formato)
            worksheet.write_number(4 + i, 1, cantidad, numero_formato)
            worksheet.write_number(4 + i, 2, costo_total, moneda_formato)
            worksheet.write_number(4 + i, 3, costo_unitario, moneda_formato)
        
        # Añadir gráfico si se solicita
        if incluir_grafico:
            # Gráfico de barras para cantidad producida
            chart1 = workbook.add_chart({'type': 'column'})
            
            chart1.add_series({
                'name': 'Cantidad Producida',
                'categories': [f'Producción - {tipo_reporte}', 4, 0, 4 + len(productos) - 1, 0],
                'values': [f'Producción - {tipo_reporte}', 4, 1, 4 + len(productos) - 1, 1],
                'fill': {'color': '#F3AD4E'},
            })
            
            chart1.set_title({'name': 'Cantidad Producida por Producto'})
            chart1.set_x_axis({'name': 'Producto'})
            chart1.set_y_axis({'name': 'Cantidad'})
            
            chart1.set_size({'width': 720, 'height': 400})
            worksheet.insert_chart('F4', chart1)
            
            # Gráfico de barras para costo unitario
            chart2 = workbook.add_chart({'type': 'column'})
            
            chart2.add_series({
                'name': 'Costo Unitario',
                'categories': [f'Producción - {tipo_reporte}', 4, 0, 4 + len(productos) - 1, 0],
                'values': [f'Producción - {tipo_reporte}', 4, 3, 4 + len(productos) - 1, 3],
                'fill': {'color': '#3CB371'},
            })
            
            chart2.set_title({'name': 'Costo Unitario por Producto'})
            chart2.set_x_axis({'name': 'Producto'})
            chart2.set_y_axis({'name': 'Costo ($)'})
            
            chart2.set_size({'width': 720, 'height': 400})
            worksheet.insert_chart('F24', chart2)
    
    # Cerrar el libro
    workbook.close()
    
    return ruta_archivo

def _generar_pdf_produccion(datos_reporte, titulo, tipo_reporte, incluir_grafico=True):
    """Genera un archivo PDF para reportes de producción"""
    nombre_archivo = f"produccion_{tipo_reporte}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    ruta_archivo = os.path.join(REPORTES_DIR, nombre_archivo)
    
    # Extraer parámetros
    fecha_inicio = datetime.strptime(datos_reporte.get('fecha_inicio', ''), '%Y-%m-%d')
    fecha_fin = datetime.strptime(datos_reporte.get('fecha_fin', ''), '%Y-%m-%d')
    productos_ids = datos_reporte.get('productos', [])
    
    # Crear documento
    doc = SimpleDocTemplate(ruta_archivo, pagesize=letter)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Añadir título
    title_style = styles["Title"]
    title_style.alignment = 1  # 0=Izquierda, 1=Centro, 2=Derecha
    elements.append(Paragraph(titulo, title_style))
    
    # Añadir período
    subtitle_style = styles["Heading2"]
    subtitle_style.alignment = 1
    elements.append(Paragraph(f"Período: {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}", subtitle_style))
    
    # Añadir espacio
    elements.append(Spacer(1, 0.25*inch))
    
    # Implementar según el tipo de reporte
    if tipo_reporte == 'produccion_diaria':
        # Simular datos de producción diaria
        delta = fecha_fin - fecha_inicio
        
        # Datos de ejemplo
        fechas = []
        cantidades = []
        costos = []
        eficiencias = []
        
        for i in range(delta.days + 1):
            fecha = fecha_inicio + timedelta(days=i)
            fechas.append(fecha)
            
            # Datos aleatorios para ejemplo
            cantidad = 100 + i * 5
            costo = cantidad * 2.5
            eficiencia = 0.75 + (i % 10) / 100
            
            cantidades.append(cantidad)
            costos.append(costo)
            eficiencias.append(eficiencia)
        
        # Crear tabla
        data = [['Fecha', 'Cantidad', 'Costo ($)', 'Eficiencia (%)']]
        
        for i in range(len(fechas)):
            data.append([
                fechas[i].strftime('%d/%m/%Y'),
                str(cantidades[i]),
                f"${costos[i]:.2f}",
                f"{eficiencias[i]*100:.2f}%"
            ])
        
        table = Table(data, colWidths=[1.25*inch, 1.75*inch, 1.5*inch, 1.5*inch])
        
        # Estilo de tabla
        style = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F3AD4E')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 12),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
        ])
        
        table.setStyle(style)
        elements.append(table)
        
        # Añadir gráfico si se solicita
        if incluir_grafico and len(fechas) > 0:
            elements.append(Spacer(1, 0.5*inch))
            elements.append(Paragraph("Producción Diaria", styles["Heading3"]))
            elements.append(Spacer(1, 0.25*inch))
            
            # Crear gráfico de líneas
            drawing = Drawing(500, 250)
            
            # Datos para el gráfico
            fechas_str = [fecha.strftime('%d/%m') for fecha in fechas]
            
            # Gráfico de producción
            lc = HorizontalLineChart()
            lc.x = 50
            lc.y = 50
            lc.height = 150
            lc.width = 400
            lc.data = [cantidades]
            
            # Configurar categorías
            lc.categoryAxis.categoryNames = fechas_str
            lc.categoryAxis.labels.boxAnchor = 'n'
            lc.categoryAxis.labels.angle = 30
            lc.categoryAxis.labels.fontSize = 8
            
            # Configurar ejes
            lc.valueAxis.valueMin = 0
            lc.valueAxis.valueMax = max(cantidades) * 1.2
            lc.valueAxis.valueStep = max(cantidades) // 5
            
            # Estilo de línea
            lc.lines[0].strokeWidth = 3
            lc.lines[0].strokeColor = colors.HexColor('#F3AD4E')
            
            # Añadir títulos
            lc.categoryAxis.title = 'Fecha'
            lc.valueAxis.title = 'Cantidad'
            
            drawing.add(lc)
            elements.append(drawing)
            
            # Gráfico de eficiencia
            elements.append(Spacer(1, 0.5*inch))
            elements.append(Paragraph("Eficiencia de Producción", styles["Heading3"]))
            elements.append(Spacer(1, 0.25*inch))
            
            drawing2 = Drawing(500, 250)
            
            # Convertir eficiencias a porcentajes para mejor visualización
            eficiencias_pct = [ef * 100 for ef in eficiencias]
            
            lc2 = HorizontalLineChart()
            lc2.x = 50
            lc2.y = 50
            lc2.height = 150
            lc2.width = 400
            lc2.data = [eficiencias_pct]
            
            # Configurar categorías
            lc2.categoryAxis.categoryNames = fechas_str
            lc2.categoryAxis.labels.boxAnchor = 'n'
            lc2.categoryAxis.labels.angle = 30
            lc2.categoryAxis.labels.fontSize = 8
            
            # Configurar ejes
            lc2.valueAxis.valueMin = min(eficiencias_pct) * 0.9
            lc2.valueAxis.valueMax = 100
            lc2.valueAxis.valueStep = 5
            
            # Estilo de línea
            lc2.lines[0].strokeWidth = 3
            lc2.lines[0].strokeColor = colors.green
            
            # Añadir títulos
            lc2.categoryAxis.title = 'Fecha'
            lc2.valueAxis.title = 'Eficiencia (%)'
            
            drawing2.add(lc2)
            elements.append(drawing2)
    
    elif tipo_reporte == 'produccion_por_producto':
        # Simular datos de producción por producto
        productos = [
            "Galleta de Chocolate",
            "Galleta de Vainilla",
            "Galleta de Fresa",
            "Galleta de Limón",
            "Galleta de Coco",
            "Galleta de Nuez",
            "Galleta Integral",
            "Galleta sin Gluten",
            "Galleta de Mantequilla",
            "Galleta de Canela"
        ]
        
        cantidades = []
        costos_totales = []
        costos_unitarios = []
        
        for i, producto in enumerate(productos):
            # Datos aleatorios para ejemplo
            cantidad = 500 + i * 100
            costo_total = cantidad * (2.0 + i * 0.25)
            costo_unitario = costo_total / cantidad
            
            cantidades.append(cantidad)
            costos_totales.append(costo_total)
            costos_unitarios.append(costo_unitario)
        
        # Crear tabla
        data = [['Producto', 'Cantidad', 'Costo Total ($)', 'Costo Unitario ($)']]
        
        for i in range(len(productos)):
            data.append([
                productos[i],
                str(cantidades[i]),
                f"${costos_totales[i]:.2f}",
                f"${costos_unitarios[i]:.2f}"
            ])
        
        table = Table(data, colWidths=[2.5*inch, 1.25*inch, 1.5*inch, 1.5*inch])
        
        # Estilo de tabla
        style = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F3AD4E')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 12),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
        ])
        
        table.setStyle(style)
        elements.append(table)
        
        # Añadir gráfico si se solicita
        if incluir_grafico and len(productos) > 0:
            elements.append(Spacer(1, 0.5*inch))
            elements.append(Paragraph("Producción por Producto", styles["Heading3"]))
            elements.append(Spacer(1, 0.25*inch))
            
            # Crear gráfico de barras
            drawing = Drawing(500, 250)
            
            # Mostrar solo los primeros 10 productos si hay más
            productos_display = productos[:10]
            cantidades_display = cantidades[:10]
            
            bc = VerticalBarChart()
            bc.x = 50
            bc.y = 50
            bc.height = 150
            bc.width = 400
            bc.data = [cantidades_display]
            
            # Configurar categorías
            bc.categoryAxis.categoryNames = [p[:15] + '...' if len(p) > 15 else p for p in productos_display]
            bc.categoryAxis.labels.boxAnchor = 'ne'
            bc.categoryAxis.labels.angle = 30
            bc.categoryAxis.labels.fontSize = 8
            
            # Configurar ejes
            bc.valueAxis.valueMin = 0
            bc.valueAxis.valueMax = max(cantidades_display) * 1.2
            bc.valueAxis.valueStep = max(cantidades_display) // 5
            
            # Estilo de barras
            bc.bars[0].fillColor = colors.HexColor('#F3AD4E')
            
            # Añadir títulos
            bc.categoryAxis.title = 'Producto'
            bc.valueAxis.title = 'Cantidad'
            
            drawing.add(bc)
            elements.append(drawing)
            
            # Gráfico de costo unitario
            elements.append(Spacer(1, 0.5*inch))
            elements.append(Paragraph("Costo Unitario por Producto", styles["Heading3"]))
            elements.append(Spacer(1, 0.25*inch))
            
            drawing2 = Drawing(500, 250)
            
            costos_unitarios_display = costos_unitarios[:10]
            
            bc2 = VerticalBarChart()
            bc2.x = 50
            bc2.y = 50
            bc2.height = 150
            bc2.width = 400
            bc2.data = [costos_unitarios_display]
            
            # Configurar categorías
            bc2.categoryAxis.categoryNames = [p[:15] + '...' if len(p) > 15 else p for p in productos_display]
            bc2.categoryAxis.labels.boxAnchor = 'ne'
            bc2.categoryAxis.labels.angle = 30
            bc2.categoryAxis.labels.fontSize = 8
            
            # Configurar ejes
            bc2.valueAxis.valueMin = 0
            bc2.valueAxis.valueMax = max(costos_unitarios_display) * 1.2
            bc2.valueAxis.valueStep = max(1, max(costos_unitarios_display) // 5) if costos_unitarios_display else 1
            
            # Estilo de barras
            bc2.bars[0].fillColor = colors.green
            
            # Añadir títulos
            bc2.categoryAxis.title = 'Producto'
            bc2.valueAxis.title = 'Costo Unitario ($)'
            
            drawing2.add(bc2)
            elements.append(drawing2)
    
    elif tipo_reporte == 'eficiencia':
        # Simular datos de eficiencia de producción por día
        delta = fecha_fin - fecha_inicio
        
        # Datos de ejemplo
        fechas = []
        eficiencias = []
        tiempos_produccion = []
        desperdicios = []
        
        for i in range(delta.days + 1):
            fecha = fecha_inicio + timedelta(days=i)
            fechas.append(fecha)
            
            # Datos aleatorios para ejemplo
            eficiencia = 0.75 + (i % 10) / 100
            tiempo_produccion = 8.0 - (i % 5) / 10  # horas
            desperdicio = 5.0 - (i % 8) / 10  # porcentaje
            
            eficiencias.append(eficiencia)
            tiempos_produccion.append(tiempo_produccion)
            desperdicios.append(desperdicio)
        
        # Crear tabla
        data = [['Fecha', 'Eficiencia (%)', 'Tiempo (h)', 'Desperdicio (%)']]
        
        for i in range(len(fechas)):
            data.append([
                fechas[i].strftime('%d/%m/%Y'),
                f"{eficiencias[i]*100:.2f}%",
                f"{tiempos_produccion[i]:.1f}",
                f"{desperdicios[i]:.1f}%"
            ])
        
        table = Table(data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        
        # Estilo de tabla
        style = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F3AD4E')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 12),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
        ])
        
        table.setStyle(style)
        elements.append(table)
        
        # Añadir gráfico si se solicita
        if incluir_grafico and len(fechas) > 0:
            elements.append(Spacer(1, 0.5*inch))
            elements.append(Paragraph("Eficiencia de Producción", styles["Heading3"]))
            elements.append(Spacer(1, 0.25*inch))
            
            # Crear gráfico de líneas
            drawing = Drawing(500, 250)
            
            # Datos para el gráfico
            fechas_str = [fecha.strftime('%d/%m') for fecha in fechas]
            
            # Convertir valores a porcentajes
            eficiencias_pct = [ef * 100 for ef in eficiencias]
            
            lc = HorizontalLineChart()
            lc.x = 50
            lc.y = 50
            lc.height = 150
            lc.width = 400
            lc.data = [eficiencias_pct, desperdicios]
            
            # Configurar categorías
            lc.categoryAxis.categoryNames = fechas_str
            lc.categoryAxis.labels.boxAnchor = 'n'
            lc.categoryAxis.labels.angle = 30
            lc.categoryAxis.labels.fontSize = 8
            
            # Configurar ejes
            lc.valueAxis.valueMin = 0
            lc.valueAxis.valueMax = 100
            lc.valueAxis.valueStep = 10
            
            # Estilo de línea
            lc.lines[0].strokeWidth = 3
            lc.lines[0].strokeColor = colors.green
            lc.lines[1].strokeWidth = 3
            lc.lines[1].strokeColor = colors.red
            
            # Añadir títulos
            lc.categoryAxis.title = 'Fecha'
            lc.valueAxis.title = 'Porcentaje (%)'
            
            # Añadir leyenda
            legend = Legend()
            legend.alignment = 'right'
            legend.x = 480
            legend.y = 150
            legend.colorNamePairs = [(colors.green, 'Eficiencia'), (colors.red, 'Desperdicio')]
            lc.legend = legend
            
            drawing.add(lc)
            elements.append(drawing)
    
    elif tipo_reporte == 'costos':
        # Simular datos de costos de producción
        delta = fecha_fin - fecha_inicio
        
        # Datos de ejemplo
        fechas = []
        costos_ingredientes = []
        costos_mano_obra = []
        costos_indirectos = []
        costos_totales = []
        
        for i in range(delta.days + 1):
            fecha = fecha_inicio + timedelta(days=i)
            fechas.append(fecha)
            
            # Datos aleatorios para ejemplo
            costo_ingredientes = 1000 + i * 50
            costo_mano_obra = 800 + i * 20
            costo_indirecto = 500 + i * 10
            costo_total = costo_ingredientes + costo_mano_obra + costo_indirecto
            
            costos_ingredientes.append(costo_ingredientes)
            costos_mano_obra.append(costo_mano_obra)
            costos_indirectos.append(costo_indirecto)
            costos_totales.append(costo_total)
        
        # Crear tabla
        data = [['Fecha', 'Ingredientes ($)', 'Mano de Obra ($)', 'Indirectos ($)', 'Total ($)']]
        
        for i in range(len(fechas)):
            data.append([
                fechas[i].strftime('%d/%m/%Y'),
                f"${costos_ingredientes[i]:.2f}",
                f"${costos_mano_obra[i]:.2f}",
                f"${costos_indirectos[i]:.2f}",
                f"${costos_totales[i]:.2f}"
            ])
        
        table = Table(data, colWidths=[1.2*inch, 1.3*inch, 1.3*inch, 1.3*inch, 1.3*inch])
        
        # Estilo de tabla
        style = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F3AD4E')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 12),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
        ])
        
        table.setStyle(style)
        elements.append(table)
        
        # Añadir gráfico si se solicita
        if incluir_grafico and len(fechas) > 0:
            elements.append(Spacer(1, 0.5*inch))
            elements.append(Paragraph("Costos de Producción", styles["Heading3"]))
            elements.append(Spacer(1, 0.25*inch))
            
            # Crear gráfico de barras apiladas
            drawing = Drawing(500, 250)
            
            # Datos para el gráfico
            fechas_str = [fecha.strftime('%d/%m') for fecha in fechas]
            
            # Limitar a los últimos 7 días si hay más datos
            if len(fechas_str) > 7:
                fechas_str = fechas_str[-7:]
                costos_ingredientes = costos_ingredientes[-7:]
                costos_mano_obra = costos_mano_obra[-7:]
                costos_indirectos = costos_indirectos[-7:]
            
            bc = VerticalBarChart()
            bc.x = 50
            bc.y = 50
            bc.height = 150
            bc.width = 400
            bc.data = [costos_ingredientes, costos_mano_obra, costos_indirectos]
            
            # Configurar categorías
            bc.categoryAxis.categoryNames = fechas_str
            bc.categoryAxis.labels.boxAnchor = 'n'
            bc.categoryAxis.labels.angle = 30
            bc.categoryAxis.labels.fontSize = 8
            
            # Configurar ejes
            max_total = max([a + b + c for a, b, c in zip(costos_ingredientes, costos_mano_obra, costos_indirectos)])
            bc.valueAxis.valueMin = 0
            bc.valueAxis.valueMax = max_total * 1.1
            bc.valueAxis.valueStep = max_total // 5 if max_total > 5 else 1
            
            # Configurar colores y estilo
            bc.bars[0].fillColor = colors.HexColor('#F3AD4E')
            bc.bars[1].fillColor = colors.HexColor('#3CB371')
            bc.bars[2].fillColor = colors.HexColor('#6495ED')
            
            # Añadir títulos
            bc.categoryAxis.title = 'Fecha'
            bc.valueAxis.title = 'Costo ($)'
            
            # Añadir leyenda
            legend = Legend()
            legend.alignment = 'right'
            legend.x = 480
            legend.y = 150
            legend.colorNamePairs = [
                (colors.HexColor('#F3AD4E'), 'Ingredientes'),
                (colors.HexColor('#3CB371'), 'Mano de Obra'),
                (colors.HexColor('#6495ED'), 'Indirectos')
            ]
            bc.legend = legend
            
            drawing.add(bc)
            elements.append(drawing)
            
            # Gráfico de pastel con distribución de costos
            elements.append(Spacer(1, 0.5*inch))
            elements.append(Paragraph("Distribución de Costos (Promedio)", styles["Heading3"]))
            elements.append(Spacer(1, 0.25*inch))
            
            drawing2 = Drawing(500, 250)
            
            # Calcular promedios de costos
            prom_ingredientes = sum(costos_ingredientes) / len(costos_ingredientes)
            prom_mano_obra = sum(costos_mano_obra) / len(costos_mano_obra)
            prom_indirectos = sum(costos_indirectos) / len(costos_indirectos)
            
            pie = Pie()
            pie.x = 150
            pie.y = 50
            pie.width = 200
            pie.height = 200
            pie.data = [prom_ingredientes, prom_mano_obra, prom_indirectos]
            pie.labels = ['Ingredientes', 'Mano de Obra', 'Indirectos']
            
            # Configurar colores
            pie.slices[0].fillColor = colors.HexColor('#F3AD4E')
            pie.slices[1].fillColor = colors.HexColor('#3CB371')
            pie.slices[2].fillColor = colors.HexColor('#6495ED')
            
            drawing2.add(pie)
            elements.append(drawing2)
    
    # Generar PDF
    doc.build(elements)
    
    return ruta_archivo

def _generar_excel_financiero(datos_reporte, titulo, tipo_reporte, incluir_grafico=True):
    """Genera un archivo Excel para reportes financieros"""
    nombre_archivo = f"financiero_{tipo_reporte}_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
    ruta_archivo = os.path.join(REPORTES_DIR, nombre_archivo)
    
    # Extraer parámetros
    fecha_inicio = datetime.strptime(datos_reporte.get('fecha_inicio', ''), '%Y-%m-%d')
    fecha_fin = datetime.strptime(datos_reporte.get('fecha_fin', ''), '%Y-%m-%d')
    
    # Crear un nuevo libro de Excel
    workbook = xlsxwriter.Workbook(ruta_archivo)
    worksheet = workbook.add_worksheet(f"Financiero - {tipo_reporte}")
    
    # Formatos
    titulo_formato = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'center',
        'valign': 'vcenter'
    })
    
    encabezado_formato = workbook.add_format({
        'bold': True,
        'bg_color': '#F3AD4E',
        'border': 1,
        'align': 'center'
    })
    
    fecha_formato = workbook.add_format({
        'border': 1,
        'num_format': 'dd/mm/yyyy'
    })
    
    numero_formato = workbook.add_format({
        'border': 1,
        'num_format': '#,##0'
    })
    
    moneda_formato = workbook.add_format({
        'border': 1,
        'num_format': '$#,##0.00'
    })
    
    porcentaje_formato = workbook.add_format({
        'border': 1,
        'num_format': '0.00%'
    })
    
    total_formato = workbook.add_format({
        'bold': True,
        'border': 1,
        'bg_color': '#F6C177',  # Color cookie claro
    })
    
    total_moneda_formato = workbook.add_format({
        'bold': True,
        'border': 1,
        'bg_color': '#F6C177',
        'num_format': '$#,##0.00'
    })
    
    positivo_formato = workbook.add_format({
        'border': 1,
        'num_format': '$#,##0.00',
        'bg_color': '#D8F8D8'  # Verde claro
    })
    
    negativo_formato = workbook.add_format({
        'border': 1,
        'num_format': '$#,##0.00',
        'bg_color': '#F8D8D8'  # Rojo claro
    })
    
    # Escribir encabezado
    worksheet.merge_range('A1:D1', titulo, titulo_formato)
    worksheet.merge_range('A2:D2', f"Período: {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}", titulo_formato)
    
    # Implementar según el tipo de reporte
    if tipo_reporte == 'ingresos_vs_gastos':
        # Simular datos de ingresos y gastos
        delta = fecha_fin - fecha_inicio
        
        # Datos de ejemplo
        fechas = []
        ingresos = []
        gastos = []
        balances = []
        
        for i in range(delta.days + 1):
            fecha = fecha_inicio + timedelta(days=i)
            fechas.append(fecha)
            
            # Datos aleatorios para ejemplo
            ingreso = 5000 + i * 100 + (i % 5) * 200
            gasto = 4500 + i * 90 + (i % 3) * 150
            balance = ingreso - gasto
            
            ingresos.append(ingreso)
            gastos.append(gasto)
            balances.append(balance)
        
        # Escribir encabezados de columna
        worksheet.write('A4', 'Fecha', encabezado_formato)
        worksheet.write('B4', 'Ingresos ($)', encabezado_formato)
        worksheet.write('C4', 'Gastos ($)', encabezado_formato)
        worksheet.write('D4', 'Balance ($)', encabezado_formato)
        
        # Establecer anchos de columna
        worksheet.set_column('A:A', 15)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 15)
        worksheet.set_column('D:D', 15)
        
        # Escribir datos
        for i, fecha in enumerate(fechas):
            worksheet.write_datetime(4 + i, 0, fecha, fecha_formato)
            worksheet.write_number(4 + i, 1, ingresos[i], moneda_formato)
            worksheet.write_number(4 + i, 2, gastos[i], moneda_formato)
            
            # Formato condicional para balance
            if balances[i] >= 0:
                worksheet.write_number(4 + i, 3, balances[i], positivo_formato)
            else:
                worksheet.write_number(4 + i, 3, balances[i], negativo_formato)
        
        # Escribir totales
        fila = 4 + len(fechas)
        total_ingresos = sum(ingresos)
        total_gastos = sum(gastos)
        total_balance = total_ingresos - total_gastos
        
        worksheet.write(fila, 0, 'TOTAL', total_formato)
        worksheet.write_number(fila, 1, total_ingresos, total_moneda_formato)
        worksheet.write_number(fila, 2, total_gastos, total_moneda_formato)
        
        # Formato condicional para balance total
        if total_balance >= 0:
            worksheet.write_number(fila, 3, total_balance, total_moneda_formato)
        else:
            worksheet.write_number(fila, 3, total_balance, negativo_formato)
        
        # Añadir gráfico si se solicita
        if incluir_grafico:
            # Gráfico de líneas para ingresos y gastos
            chart = workbook.add_chart({'type': 'line'})
            
            # Limitar a los últimos 30 días si hay más
            if len(fechas) > 30:
                start_row = 4 + len(fechas) - 30
                end_row = 4 + len(fechas) - 1
            else:
                start_row = 4
                end_row = 4 + len(fechas) - 1
            
            # Añadir series de datos
            chart.add_series({
                'name': 'Ingresos',
                'categories': [f'Financiero - {tipo_reporte}', start_row, 0, end_row, 0],
                'values': [f'Financiero - {tipo_reporte}', start_row, 1, end_row, 1],
                'line': {'color': '#3CB371', 'width': 2.25},  # Verde
            })
            
            chart.add_series({
                'name': 'Gastos',
                'categories': [f'Financiero - {tipo_reporte}', start_row, 0, end_row, 0],
                'values': [f'Financiero - {tipo_reporte}', start_row, 2, end_row, 2],
                'line': {'color': '#FF6347', 'width': 2.25},  # Rojo
            })
            
            # Configurar el gráfico
            chart.set_title({'name': 'Ingresos vs. Gastos'})
            chart.set_x_axis({'name': 'Fecha'})
            chart.set_y_axis({'name': 'Monto ($)'})
            
            # Insertar gráfico
            chart.set_size({'width': 720, 'height': 400})
            worksheet.insert_chart('F4', chart)
            
            # Gráfico de barras para el balance
            chart2 = workbook.add_chart({'type': 'column'})
            
            chart2.add_series({
                'name': 'Balance',
                'categories': [f'Financiero - {tipo_reporte}', start_row, 0, end_row, 0],
                'values': [f'Financiero - {tipo_reporte}', start_row, 3, end_row, 3],
                'data_labels': {'value': True},
                'fill': {'type': 'gradient', 'gradient': {'colors': ['#3CB371', '#FF6347']}},
            })
            
            # Configurar el gráfico
            chart2.set_title({'name': 'Balance Diario'})
            chart2.set_x_axis({'name': 'Fecha'})
            chart2.set_y_axis({'name': 'Balance ($)'})
            
            # Insertar gráfico
            chart2.set_size({'width': 720, 'height': 400})
            worksheet.insert_chart('F24', chart2)

    elif tipo_reporte == 'margen_beneficio':
        # Simular datos de margen de beneficio por producto
        productos = [
            "Galleta de Chocolate",
            "Galleta de Vainilla",
            "Galleta de Fresa",
            "Galleta de Limón",
            "Galleta de Coco",
            "Galleta de Nuez",
            "Galleta Integral",
            "Galleta sin Gluten",
            "Galleta de Mantequilla",
            "Galleta de Canela"
        ]
        
        # Datos de ejemplo
        precios_venta = []
        costos_produccion = []
        margenes_brutos = []
        porcentajes_margen = []
        
        for i, producto in enumerate(productos):
            # Datos aleatorios para ejemplo
            precio_venta = 10.0 + i * 0.5
            costo_produccion = 6.0 + i * 0.2
            margen_bruto = precio_venta - costo_produccion
            porcentaje_margen = margen_bruto / precio_venta
            
            precios_venta.append(precio_venta)
            costos_produccion.append(costo_produccion)
            margenes_brutos.append(margen_bruto)
            porcentajes_margen.append(porcentaje_margen)
        
        # Escribir encabezados de columna
        worksheet.write('A4', 'Producto', encabezado_formato)
        worksheet.write('B4', 'Precio de Venta ($)', encabezado_formato)
        worksheet.write('C4', 'Costo de Producción ($)', encabezado_formato)
        worksheet.write('D4', 'Margen Bruto ($)', encabezado_formato)
        worksheet.write('E4', 'Margen (%)', encabezado_formato)
        
        # Establecer anchos de columna
        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:B', 18)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 15)
        worksheet.set_column('E:E', 12)
        
        # Escribir datos
        for i, producto in enumerate(productos):
            worksheet.write_string(4 + i, 0, producto)
            worksheet.write_number(4 + i, 1, precios_venta[i], moneda_formato)
            worksheet.write_number(4 + i, 2, costos_produccion[i], moneda_formato)
            worksheet.write_number(4 + i, 3, margenes_brutos[i], moneda_formato)
            worksheet.write_number(4 + i, 4, porcentajes_margen[i], porcentaje_formato)
        
        # Escribir promedios
        fila = 4 + len(productos)
        promedio_precio = sum(precios_venta) / len(precios_venta)
        promedio_costo = sum(costos_produccion) / len(costos_produccion)
        promedio_margen = sum(margenes_brutos) / len(margenes_brutos)
        promedio_porcentaje = sum(porcentajes_margen) / len(porcentajes_margen)
        
        worksheet.write(fila, 0, 'PROMEDIO', total_formato)
        worksheet.write_number(fila, 1, promedio_precio, total_moneda_formato)
        worksheet.write_number(fila, 2, promedio_costo, total_moneda_formato)
        worksheet.write_number(fila, 3, promedio_margen, total_moneda_formato)
        worksheet.write_number(fila, 4, promedio_porcentaje, porcentaje_formato)
        
        # Añadir gráfico si se solicita
        if incluir_grafico:
            # Gráfico de barras para el margen bruto por producto
            chart = workbook.add_chart({'type': 'column'})
            
            chart.add_series({
                'name': 'Precio de Venta',
                'categories': [f'Financiero - {tipo_reporte}', 4, 0, 4 + len(productos) - 1, 0],
                'values': [f'Financiero - {tipo_reporte}', 4, 1, 4 + len(productos) - 1, 1],
                'fill': {'color': '#3CB371'},
            })
            
            chart.add_series({
                'name': 'Costo de Producción',
                'categories': [f'Financiero - {tipo_reporte}', 4, 0, 4 + len(productos) - 1, 0],
                'values': [f'Financiero - {tipo_reporte}', 4, 2, 4 + len(productos) - 1, 2],
                'fill': {'color': '#FF6347'},
            })
            
            # Configurar el gráfico
            chart.set_title({'name': 'Precio vs. Costo por Producto'})
            chart.set_x_axis({'name': 'Producto'})
            chart.set_y_axis({'name': 'Monto ($)'})
            
            # Insertar gráfico
            chart.set_size({'width': 720, 'height': 400})
            worksheet.insert_chart('G4', chart)
            
            # Gráfico de porcentaje de margen
            chart2 = workbook.add_chart({'type': 'column'})
            
            chart2.add_series({
                'name': 'Margen (%)',
                'categories': [f'Financiero - {tipo_reporte}', 4, 0, 4 + len(productos) - 1, 0],
                'values': [f'Financiero - {tipo_reporte}', 4, 4, 4 + len(productos) - 1, 4],
                'data_labels': {'value': True, 'num_format': '0.0%'},
                'fill': {'color': '#F3AD4E'},
            })
            
            # Configurar el gráfico
            chart2.set_title({'name': 'Porcentaje de Margen por Producto'})
            chart2.set_x_axis({'name': 'Producto'})
            chart2.set_y_axis({'name': 'Margen (%)', 'num_format': '0%', 'min': 0, 'max': 0.5})
            
            # Insertar gráfico
            chart2.set_size({'width': 720, 'height': 400})
            worksheet.insert_chart('G24', chart2)

    elif tipo_reporte == 'flujo_efectivo':
        # Simular datos de flujo de efectivo
        delta = fecha_fin - fecha_inicio
        
        # Generar fechas por semana
        fechas = []
        ingresos_operativos = []
        ingresos_financieros = []
        egresos_operativos = []
        egresos_financieros = []
        flujos_netos = []
        
        # Generar datos semanales
        num_semanas = delta.days // 7 + 1
        for i in range(num_semanas):
            fecha = fecha_inicio + timedelta(days=i*7)
            fechas.append(fecha)
            
            # Datos aleatorios para ejemplo
            ingreso_operativo = 25000 + i * 500 + (i % 3) * 1000
            ingreso_financiero = 2000 + i * 100 + (i % 2) * 500
            egreso_operativo = 20000 + i * 400 + (i % 4) * 800
            egreso_financiero = 3000 + i * 200 + (i % 3) * 300
            
            flujo_neto = (ingreso_operativo + ingreso_financiero) - (egreso_operativo + egreso_financiero)
            
            ingresos_operativos.append(ingreso_operativo)
            ingresos_financieros.append(ingreso_financiero)
            egresos_operativos.append(egreso_operativo)
            egresos_financieros.append(egreso_financiero)
            flujos_netos.append(flujo_neto)
        
        # Escribir encabezados de columna
        worksheet.write('A4', 'Semana', encabezado_formato)
        worksheet.write('B4', 'Ingresos Operativos', encabezado_formato)
        worksheet.write('C4', 'Ingresos Financieros', encabezado_formato)
        worksheet.write('D4', 'Egresos Operativos', encabezado_formato)
        worksheet.write('E4', 'Egresos Financieros', encabezado_formato)
        worksheet.write('F4', 'Flujo Neto', encabezado_formato)
        
        # Establecer anchos de columna
        worksheet.set_column('A:A', 15)
        worksheet.set_column('B:B', 18)
        worksheet.set_column('C:C', 18)
        worksheet.set_column('D:D', 18)
        worksheet.set_column('E:E', 18)
        worksheet.set_column('F:F', 15)
        
        # Escribir datos
        for i, fecha in enumerate(fechas):
            worksheet.write_datetime(4 + i, 0, fecha, fecha_formato)
            worksheet.write_number(4 + i, 1, ingresos_operativos[i], moneda_formato)
            worksheet.write_number(4 + i, 2, ingresos_financieros[i], moneda_formato)
            worksheet.write_number(4 + i, 3, egresos_operativos[i], moneda_formato)
            worksheet.write_number(4 + i, 4, egresos_financieros[i], moneda_formato)
            
            # Formato condicional para flujo neto
            if flujos_netos[i] >= 0:
                worksheet.write_number(4 + i, 5, flujos_netos[i], positivo_formato)
            else:
                worksheet.write_number(4 + i, 5, flujos_netos[i], negativo_formato)
        
        # Escribir totales
        fila = 4 + len(fechas)
        total_ing_operativos = sum(ingresos_operativos)
        total_ing_financieros = sum(ingresos_financieros)
        total_egr_operativos = sum(egresos_operativos)
        total_egr_financieros = sum(egresos_financieros)
        total_flujo_neto = total_ing_operativos + total_ing_financieros - total_egr_operativos - total_egr_financieros
        
        worksheet.write(fila, 0, 'TOTAL', total_formato)
        worksheet.write_number(fila, 1, total_ing_operativos, total_moneda_formato)
        worksheet.write_number(fila, 2, total_ing_financieros, total_moneda_formato)
        worksheet.write_number(fila, 3, total_egr_operativos, total_moneda_formato)
        worksheet.write_number(fila, 4, total_egr_financieros, total_moneda_formato)
        
        # Formato condicional para flujo neto total
        if total_flujo_neto >= 0:
            worksheet.write_number(fila, 5, total_flujo_neto, total_moneda_formato)
        else:
            worksheet.write_number(fila, 5, total_flujo_neto, negativo_formato)
        
        # Añadir gráfico si se solicita
        if incluir_grafico:
            # Gráfico de columnas apiladas para ingresos y egresos
            chart = workbook.add_chart({'type': 'column', 'subtype': 'stacked'})
            
            # Añadir series de datos
            chart.add_series({
                'name': 'Ingresos Operativos',
                'categories': [f'Financiero - {tipo_reporte}', 4, 0, 4 + len(fechas) - 1, 0],
                'values': [f'Financiero - {tipo_reporte}', 4, 1, 4 + len(fechas) - 1, 1],
                'fill': {'color': '#3CB371'},
            })
            
            chart.add_series({
                'name': 'Ingresos Financieros',
                'categories': [f'Financiero - {tipo_reporte}', 4, 0, 4 + len(fechas) - 1, 0],
                'values': [f'Financiero - {tipo_reporte}', 4, 2, 4 + len(fechas) - 1, 2],
                'fill': {'color': '#32CD32'},
            })
            
            # Configurar el gráfico
            chart.set_title({'name': 'Ingresos por Semana'})
            chart.set_x_axis({'name': 'Semana'})
            chart.set_y_axis({'name': 'Monto ($)'})
            
            # Insertar gráfico
            chart.set_size({'width': 720, 'height': 300})
            worksheet.insert_chart('H4', chart)
            
            # Gráfico de columnas apiladas para egresos
            chart2 = workbook.add_chart({'type': 'column', 'subtype': 'stacked'})
            
            chart2.add_series({
                'name': 'Egresos Operativos',
                'categories': [f'Financiero - {tipo_reporte}', 4, 0, 4 + len(fechas) - 1, 0],
                'values': [f'Financiero - {tipo_reporte}', 4, 3, 4 + len(fechas) - 1, 3],
                'fill': {'color': '#FF6347'},
            })
            
            chart2.add_series({
                'name': 'Egresos Financieros',
                'categories': [f'Financiero - {tipo_reporte}', 4, 0, 4 + len(fechas) - 1, 0],
                'values': [f'Financiero - {tipo_reporte}', 4, 4, 4 + len(fechas) - 1, 4],
                'fill': {'color': '#FF4500'},
            })
            
            # Configurar el gráfico
            chart2.set_title({'name': 'Egresos por Semana'})
            chart2.set_x_axis({'name': 'Semana'})
            chart2.set_y_axis({'name': 'Monto ($)'})
            
            # Insertar gráfico
            chart2.set_size({'width': 720, 'height': 300})
            worksheet.insert_chart('H20', chart2)
            
            # Gráfico de línea para flujo neto
            chart3 = workbook.add_chart({'type': 'line'})
            
            chart3.add_series({
                'name': 'Flujo Neto',
                'categories': [f'Financiero - {tipo_reporte}', 4, 0, 4 + len(fechas) - 1, 0],
                'values': [f'Financiero - {tipo_reporte}', 4, 5, 4 + len(fechas) - 1, 5],
                'line': {'color': '#F3AD4E', 'width': 2.5},
                'marker': {'type': 'circle', 'size': 7},
                'data_labels': {'value': True, 'num_format': '$#,##0'},
            })
            
            # Configurar el gráfico
            chart3.set_title({'name': 'Flujo Neto por Semana'})
            chart3.set_x_axis({'name': 'Semana'})
            chart3.set_y_axis({'name': 'Monto ($)'})
            
            # Insertar gráfico
            chart3.set_size({'width': 720, 'height': 300})
            worksheet.insert_chart('H36', chart3)

    elif tipo_reporte == 'costo_producto':
        # ... (código anterior) ...
        
        worksheet.write(fila, 0, 'PROMEDIO', total_formato)
        worksheet.write_number(fila, 1, prom_c_ingredientes, total_moneda_formato)
        worksheet.write_number(fila, 2, prom_c_mano_obra, total_moneda_formato)
        worksheet.write_number(fila, 3, prom_c_indirecto, total_moneda_formato)
        worksheet.write_number(fila, 4, prom_c_total, total_moneda_formato)
        worksheet.write_number(fila, 5, prom_p_venta, total_moneda_formato)
        worksheet.write_number(fila, 6, prom_margen, total_moneda_formato)
        
        # Añadir gráfico si se solicita
        if incluir_grafico:
            # Gráfico de barras apiladas para los componentes del costo
            chart = workbook.add_chart({'type': 'column', 'subtype': 'stacked'})
            
            chart.add_series({
                'name': 'Costo Ingredientes',
                'categories': [f'Financiero - {tipo_reporte}', 4, 0, 4 + len(productos) - 1, 0],
                'values': [f'Financiero - {tipo_reporte}', 4, 1, 4 + len(productos) - 1, 1],
                'fill': {'color': '#F3AD4E'},
            })
            
            chart.add_series({
                'name': 'Costo Mano Obra',
                'categories': [f'Financiero - {tipo_reporte}', 4, 0, 4 + len(productos) - 1, 0],
                'values': [f'Financiero - {tipo_reporte}', 4, 2, 4 + len(productos) - 1, 2],
                'fill': {'color': '#3CB371'},
            })
            
            chart.add_series({
                'name': 'Costo Indirecto',
                'categories': [f'Financiero - {tipo_reporte}', 4, 0, 4 + len(productos) - 1, 0],
                'values': [f'Financiero - {tipo_reporte}', 4, 3, 4 + len(productos) - 1, 3],
                'fill': {'color': '#6495ED'},
            })
            
            # Configurar el gráfico
            chart.set_title({'name': 'Componentes del Costo por Producto'})
            chart.set_x_axis({'name': 'Producto'})
            chart.set_y_axis({'name': 'Costo ($)'})
            
            # Insertar gráfico
            chart.set_size({'width': 720, 'height': 400})
            worksheet.insert_chart('I4', chart)
            
            # Gráfico de barras para precio de venta y costo total
            chart2 = workbook.add_chart({'type': 'column'})
            
            chart2.add_series({
                'name': 'Precio Venta',
                'categories': [f'Financiero - {tipo_reporte}', 4, 0, 4 + len(productos) - 1, 0],
                'values': [f'Financiero - {tipo_reporte}', 4, 5, 4 + len(productos) - 1, 5],
                'fill': {'color': '#32CD32'},
            })
            
            chart2.add_series({
                'name': 'Costo Total',
                'categories': [f'Financiero - {tipo_reporte}', 4, 0, 4 + len(productos) - 1, 0],
                'values': [f'Financiero - {tipo_reporte}', 4, 4, 4 + len(productos) - 1, 4],
                'fill': {'color': '#FF6347'},
            })
            
            chart2.add_series({
                'name': 'Margen',
                'categories': [f'Financiero - {tipo_reporte}', 4, 0, 4 + len(productos) - 1, 0],
                'values': [f'Financiero - {tipo_reporte}', 4, 6, 4 + len(productos) - 1, 6],
                'fill': {'color': '#F3AD4E'},
            })
            
            # Configurar el gráfico
            chart2.set_title({'name': 'Precio, Costo y Margen por Producto'})
            chart2.set_x_axis({'name': 'Producto'})
            chart2.set_y_axis({'name': 'Monto ($)'})
            
            # Insertar gráfico
            chart2.set_size({'width': 720, 'height': 400})
            worksheet.insert_chart('I24', chart2)
    
    # Cerrar el libro
    workbook.close()
    
    return ruta_archivo

def _generar_pdf_financiero(datos_reporte, titulo, tipo_reporte, incluir_grafico=True):
    """Genera un archivo PDF para reportes financieros"""
    nombre_archivo = f"financiero_{tipo_reporte}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    ruta_archivo = os.path.join(REPORTES_DIR, nombre_archivo)
    
    # Extraer parámetros
    fecha_inicio = datetime.strptime(datos_reporte.get('fecha_inicio', ''), '%Y-%m-%d')
    fecha_fin = datetime.strptime(datos_reporte.get('fecha_fin', ''), '%Y-%m-%d')
    
    # Crear documento
    doc = SimpleDocTemplate(ruta_archivo, pagesize=letter)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Añadir título
    title_style = styles["Title"]
    title_style.alignment = 1  # 0=Izquierda, 1=Centro, 2=Derecha
    elements.append(Paragraph(titulo, title_style))
    
    # Añadir período
    subtitle_style = styles["Heading2"]
    subtitle_style.alignment = 1
    elements.append(Paragraph(f"Período: {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}", subtitle_style))
    
    # Añadir espacio
    elements.append(Spacer(1, 0.25*inch))
    
    # Implementar según el tipo de reporte
    if tipo_reporte == 'ingresos_vs_gastos':
        # Simular datos de ingresos y gastos
        delta = fecha_fin - fecha_inicio
        
        # Datos de ejemplo
        fechas = []
        ingresos = []
        gastos = []
        balances = []
        
        for i in range(delta.days + 1):
            fecha = fecha_inicio + timedelta(days=i)
            fechas.append(fecha)
            
            # Datos aleatorios para ejemplo
            ingreso = 5000 + i * 100 + (i % 5) * 200
            gasto = 4500 + i * 90 + (i % 3) * 150
            balance = ingreso - gasto
            
            ingresos.append(ingreso)
            gastos.append(gasto)
            balances.append(balance)
        
        # Crear tabla
        data = [['Fecha', 'Ingresos ($)', 'Gastos ($)', 'Balance ($)']]
        
        for i in range(len(fechas)):
            data.append([
                fechas[i].strftime('%d/%m/%Y'),
                f"${ingresos[i]:.2f}",
                f"${gastos[i]:.2f}",
                f"${balances[i]:.2f}"
            ])
        
        # Totales
        total_ingresos = sum(ingresos)
        total_gastos = sum(gastos)
        total_balance = total_ingresos - total_gastos
        
        data.append([
            'TOTAL',
            f"${total_ingresos:.2f}",
            f"${total_gastos:.2f}",
            f"${total_balance:.2f}"
        ])
        
        # Crear tabla
        table = Table(data, colWidths=[1.25*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        
        # Estilo de tabla
        style = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F3AD4E')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 12),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#F6C177')),
            ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
            ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
        ])
        
        # Añadir formato condicional para balance
        for i in range(1, len(fechas) + 1):
            balance = balances[i-1]
            if balance >= 0:
                style.add('BACKGROUND', (3,i), (3,i), colors.lightgreen)
            else:
                style.add('BACKGROUND', (3,i), (3,i), colors.lightpink)
        
        table.setStyle(style)
        elements.append(table)
        
        # Añadir gráfico si se solicita
        if incluir_grafico and len(fechas) > 0:
            # Limitar a los últimos 15 días para el gráfico si hay más
            max_dias_grafico = 15
            if len(fechas) > max_dias_grafico:
                fechas_display = fechas[-max_dias_grafico:]
                ingresos_display = ingresos[-max_dias_grafico:]
                gastos_display = gastos[-max_dias_grafico:]
            else:
                fechas_display = fechas
                ingresos_display = ingresos
                gastos_display = gastos
            
            elements.append(Spacer(1, 0.5*inch))
            elements.append(Paragraph("Ingresos vs. Gastos", styles["Heading3"]))
            elements.append(Spacer(1, 0.25*inch))
            
            # Crear gráfico de líneas
            drawing = Drawing(500, 250)
            
            # Datos para el gráfico
            fechas_str = [fecha.strftime('%d/%m') for fecha in fechas_display]
            
            # Gráfico de líneas
            lc = HorizontalLineChart()
            lc.x = 50
            lc.y = 50
            lc.height = 150
            lc.width = 400
            lc.data = [ingresos_display, gastos_display]
            
            # Configurar categorías
            lc.categoryAxis.categoryNames = fechas_str
            lc.categoryAxis.labels.boxAnchor = 'n'
            lc.categoryAxis.labels.angle = 30
            lc.categoryAxis.labels.fontSize = 8
            
            # Configurar ejes
            max_valor = max(max(ingresos_display), max(gastos_display))
            lc.valueAxis.valueMin = 0
            lc.valueAxis.valueMax = max_valor * 1.2
            lc.valueAxis.valueStep = max_valor // 5 if max_valor > 5 else 1
            
            # Estilo de línea
            lc.lines[0].strokeWidth = 3
            lc.lines[0].strokeColor = colors.green
            lc.lines[1].strokeWidth = 3
            lc.lines[1].strokeColor = colors.red
            
            # Añadir leyenda
            legend = Legend()
            legend.alignment = 'right'
            legend.x = 480
            legend.y = 150
            legend.colorNamePairs = [(colors.green, 'Ingresos'), (colors.red, 'Gastos')]
            lc.legend = legend
            
            # Añadir títulos
            lc.categoryAxis.title = 'Fecha'
            lc.valueAxis.title = 'Monto ($)'
            
            drawing.add(lc)
            elements.append(drawing)
            
            # Gráfico de barras para el balance
            elements.append(Spacer(1, 0.5*inch))
            elements.append(Paragraph("Balance Diario", styles["Heading3"]))
            elements.append(Spacer(1, 0.25*inch))
            
            drawing2 = Drawing(500, 250)
            
            # Balance para gráfico
            balances_display = [ingresos_display[i] - gastos_display[i] for i in range(len(ingresos_display))]
            
            bc = VerticalBarChart()
            bc.x = 50
            bc.y = 50
            bc.height = 150
            bc.width = 400
            bc.data = [balances_display]
            
            # Configurar categorías
            bc.categoryAxis.categoryNames = fechas_str
            bc.categoryAxis.labels.boxAnchor = 'n'
            bc.categoryAxis.labels.angle = 30
            bc.categoryAxis.labels.fontSize = 8
            
            # Configurar ejes
            max_bal = max(balances_display)
            min_bal = min(balances_display)
            
            if min_bal < 0:
                bc.valueAxis.valueMin = min_bal * 1.2
            else:
                bc.valueAxis.valueMin = 0
                
            bc.valueAxis.valueMax = max_bal * 1.2
            bc.valueAxis.valueStep = max(abs(max_bal), abs(min_bal)) // 5 if max(abs(max_bal), abs(min_bal)) > 5 else 1
            
            # Personalizar colores de barras según el valor
            for i in range(len(balances_display)):
                if balances_display[i] >= 0:
                    bc.bars[0][i].fillColor = colors.green
                else:
                    bc.bars[0][i].fillColor = colors.red
            
            # Añadir títulos
            bc.categoryAxis.title = 'Fecha'
            bc.valueAxis.title = 'Balance ($)'
            
            drawing2.add(bc)
            elements.append(drawing2)
    
    elif tipo_reporte == 'margen_beneficio':
        # Simular datos de margen de beneficio por producto
        productos = [
            "Galleta de Chocolate",
            "Galleta de Vainilla",
            "Galleta de Fresa",
            "Galleta de Limón",
            "Galleta de Coco",
            "Galleta de Nuez",
            "Galleta Integral",
            "Galleta sin Gluten",
            "Galleta de Mantequilla",
            "Galleta de Canela"
        ]
        
        # Datos de ejemplo
        precios_venta = []
        costos_produccion = []
        margenes_brutos = []
        porcentajes_margen = []
        
        for i, producto in enumerate(productos):
            # Datos aleatorios para ejemplo
            precio_venta = 10.0 + i * 0.5
            costo_produccion = 6.0 + i * 0.2
            margen_bruto = precio_venta - costo_produccion
            porcentaje_margen = margen_bruto / precio_venta
            
            precios_venta.append(precio_venta)
            costos_produccion.append(costo_produccion)
            margenes_brutos.append(margen_bruto)
            porcentajes_margen.append(porcentaje_margen)
        
        # Crear tabla
        data = [['Producto', 'Precio Venta ($)', 'Costo Prod. ($)', 'Margen ($)', 'Margen (%)']]
        
        for i, producto in enumerate(productos):
            data.append([
                producto,
                f"${precios_venta[i]:.2f}",
                f"${costos_produccion[i]:.2f}",
                f"${margenes_brutos[i]:.2f}",
                f"{porcentajes_margen[i]*100:.2f}%"
            ])
        
        # Promedios
        promedio_precio = sum(precios_venta) / len(precios_venta)
        promedio_costo = sum(costos_produccion) / len(costos_produccion)
        promedio_margen = sum(margenes_brutos) / len(margenes_brutos)
        promedio_porcentaje = sum(porcentajes_margen) / len(porcentajes_margen)
        
        data.append([
            'PROMEDIO',
            f"${promedio_precio:.2f}",
            f"${promedio_costo:.2f}",
            f"${promedio_margen:.2f}",
            f"{promedio_porcentaje*100:.2f}%"
        ])
        
        # Crear tabla
        table = Table(data, colWidths=[2*inch, 1.2*inch, 1.2*inch, 1*inch, 1*inch])
        
        # Estilo de tabla
        style = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F3AD4E')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 12),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#F6C177')),
            ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
            ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
        ])
        
        table.setStyle(style)
        elements.append(table)
        
        # Añadir gráfico si se solicita
        if incluir_grafico and len(productos) > 0:
            elements.append(Spacer(1, 0.5*inch))
            elements.append(Paragraph("Precio vs. Costo por Producto", styles["Heading3"]))
            elements.append(Spacer(1, 0.25*inch))
            
            # Crear gráfico de barras
            drawing = Drawing(500, 250)
            
            # Datos para el gráfico
            productos_display = [p[:15] + '...' if len(p) > 15 else p for p in productos]
            
            # Gráfico de barras agrupadas
            bc = VerticalBarChart()
            bc.x = 50
            bc.y = 50
            bc.height = 150
            bc.width = 400
            bc.data = [precios_venta, costos_produccion]
            
            # Configurar categorías
            bc.categoryAxis.categoryNames = productos_display
            bc.categoryAxis.labels.boxAnchor = 'ne'
            bc.categoryAxis.labels.angle = 30
            bc.categoryAxis.labels.fontSize = 8
            
            # Configurar ejes
            max_valor = max(max(precios_venta), max(costos_produccion))
            bc.valueAxis.valueMin = 0
            bc.valueAxis.valueMax = max_valor * 1.2
            bc.valueAxis.valueStep = max_valor // 5 if max_valor > 5 else 1
            
            # Estilo de barras
            bc.bars[0].fillColor = colors.green
            bc.bars[1].fillColor = colors.red
            
            # Añadir leyenda
            legend = Legend()
            legend.alignment = 'right'
            legend.x = 480
            legend.y = 150
            legend.colorNamePairs = [(colors.green, 'Precio Venta'), (colors.red, 'Costo Producción')]
            bc.legend = legend
            
            # Añadir títulos
            bc.categoryAxis.title = 'Producto'
            bc.valueAxis.title = 'Monto ($)'
            
            drawing.add(bc)
            elements.append(drawing)
            
            # Gráfico de porcentaje de margen
            elements.append(Spacer(1, 0.5*inch))
            elements.append(Paragraph("Margen de Beneficio (%)", styles["Heading3"]))
            elements.append(Spacer(1, 0.25*inch))
            
            drawing2 = Drawing(500, 250)
            
            # Convertir porcentajes a valores más legibles
            porcentajes_display = [p * 100 for p in porcentajes_margen]
            
            bc2 = VerticalBarChart()
            bc2.x = 50
            bc2.y = 50
            bc2.height = 150
            bc2.width = 400
            bc2.data = [porcentajes_display]
            
            # Configurar categorías
            bc2.categoryAxis.categoryNames = productos_display
            bc2.categoryAxis.labels.boxAnchor = 'ne'
            bc2.categoryAxis.labels.angle = 30
            bc2.categoryAxis.labels.fontSize = 8
            
            # Configurar ejes
            max_pct = max(porcentajes_display)
            bc2.valueAxis.valueMin = 0
            bc2.valueAxis.valueMax = max_pct * 1.2
            bc2.valueAxis.valueStep = max_pct // 5 if max_pct > 5 else 5
            
            # Estilo de barras
            bc2.bars[0].fillColor = colors.HexColor('#F3AD4E')
            
            # Añadir títulos
            bc2.categoryAxis.title = 'Producto'
            bc2.valueAxis.title = 'Margen (%)'
            
            drawing2.add(bc2)
            elements.append(drawing2)
    
    # Generar PDF
    doc.build(elements)
    
    return ruta_archivo