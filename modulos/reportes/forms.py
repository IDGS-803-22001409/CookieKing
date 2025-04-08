from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, DateField, BooleanField
from wtforms.validators import DataRequired, Optional, Email

class ReporteVentasForm(FlaskForm):
    """Formulario para generar reportes de ventas"""
    titulo = StringField('Título del Reporte', validators=[DataRequired()])
    fecha_inicio = DateField('Fecha Inicio', validators=[DataRequired()])
    fecha_fin = DateField('Fecha Fin', validators=[DataRequired()])
    tipo_reporte = SelectField('Tipo de Reporte', choices=[
        ('ventas_diarias', 'Ventas Diarias'),
        ('ventas_por_cliente', 'Ventas por Cliente'),        
        ('ventas_por_tipo', 'Ventas por Tipo')
    ], validators=[DataRequired()])
    formato = StringField('Formato', default='pdf', render_kw={'readonly': True})
    incluir_grafico = BooleanField('Incluir Gráfico', default=False)
    clientes = SelectMultipleField('Clientes (Opcional)', coerce=int)
    productos = SelectMultipleField('Productos (Opcional)', coerce=int)
    
class ReporteInventarioForm(FlaskForm):
    """Formulario para generar reportes de inventario"""
    titulo = StringField('Título del Reporte', validators=[DataRequired()])
    tipo_reporte = SelectField('Tipo de Reporte', choices=[
        ('stock_actual', 'Stock Actual'),                
        ('caducidad', 'Fechas de Caducidad')
    ], validators=[DataRequired()])
    formato = StringField('Formato', default='pdf', render_kw={'readonly': True})
    incluir_grafico = BooleanField('Incluir Gráfico', default=False)
    fecha_inicio = DateField('Fecha Inicio (para Movimientos)', validators=[Optional()])
    fecha_fin = DateField('Fecha Fin (para Movimientos)', validators=[Optional()])
    categorias = SelectMultipleField('Categorías (Opcional)', coerce=int)

class ReporteProduccionForm(FlaskForm):
    """Formulario para generar reportes de producción"""
    titulo = StringField('Título del Reporte', validators=[DataRequired()])
    fecha_inicio = DateField('Fecha Inicio', validators=[DataRequired()])
    fecha_fin = DateField('Fecha Fin', validators=[DataRequired()])
    tipo_reporte = SelectField('Tipo de Reporte', choices=[
        ('produccion_diaria', 'Producción Diaria'),
        ('produccion_por_producto', 'Producción por Producto'),
        ('eficiencia', 'Eficiencia de Producción'),
        ('costos', 'Costos de Producción')
    ], validators=[DataRequired()])
    formato = StringField('Formato', default='pdf', render_kw={'readonly': True})
    incluir_grafico = BooleanField('Incluir Gráfico', default=False)
    productos = SelectMultipleField('Productos (Opcional)', coerce=int)

def create_reportes_form(form_type, form_data=None, choices=None):
    """
    Crea el formulario correspondiente según el tipo solicitado
    """
    # Inicializar el diccionario de opciones si es None
    if choices is None:
        choices = {}
    
    if form_type == 'ventas':
        form = ReporteVentasForm()
        if 'clientes' in choices:
            form.clientes.choices = choices['clientes']
        if 'productos' in choices:
            form.productos.choices = choices['productos']
    elif form_type == 'inventario':
        form = ReporteInventarioForm()
        if 'categorias' in choices:
            form.categorias.choices = choices['categorias']
    elif form_type == 'produccion':
        form = ReporteProduccionForm()
        if 'productos' in choices:
            form.productos.choices = choices['productos']
        
    # Cargar datos del formulario si se proporcionan
    if form_data:
        for field_name, value in form_data.items():
            if hasattr(form, field_name):
                getattr(form, field_name).data = value
                
    return form