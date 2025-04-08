from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, DateField
from wtforms.validators import DataRequired, NumberRange, Optional
from datetime import datetime

class IngredienteForm(FlaskForm):
    """Formulario para la creación y edición de ingredientes"""
    nombreIngrediente = StringField('Nombre del Ingrediente', validators=[DataRequired(message='El nombre es obligatorio')])
    
    stock = FloatField('Cantidad en Stock', 
                      validators=[DataRequired(message='El stock es obligatorio'), 
                                 NumberRange(min=0, message='El stock no puede ser negativo')])
    
    unidad = SelectField('Unidad de Medida', 
                        choices=[
                            ('kg', 'Kilogramo (kg)'),
                            ('g', 'Gramo (g)'),
                            ('l', 'Litro (l)'),
                            ('ml', 'Mililitro (ml)'),
                            ('unidad', 'Unidad'),
                            ('caja', 'Caja'),
                            ('paquete', 'Paquete')
                        ])
    
    stock_minimo = FloatField('Stock Mínimo', 
                            validators=[DataRequired(message='El stock mínimo es obligatorio'),
                                       NumberRange(min=0, message='El stock mínimo no puede ser negativo')])
    
    precio_unitario = FloatField('Precio Unitario', 
                               validators=[DataRequired(message='El precio es obligatorio'),
                                         NumberRange(min=0, message='El precio no puede ser negativo')])
    
    fecha_expiracion = DateField('Fecha de Expiración', validators=[Optional()],
                               format='%Y-%m-%d')

class MovimientoStockForm(FlaskForm):
    """Formulario para registrar movimientos de stock"""
    cantidad = FloatField('Cantidad', 
                        validators=[DataRequired(message='La cantidad es obligatoria'),
                                   NumberRange(min=0.01, message='La cantidad debe ser mayor a cero')])
    
    tipo_movimiento = SelectField('Tipo de Movimiento', 
                                choices=[
                                    (0, 'Entrada (Aumentar Stock)'),
                                    (1, 'Salida (Reducir Stock)')
                                ], coerce=int)
    
    referencia = StringField('Referencia (Opcional)', validators=[Optional()])
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, DateField
from wtforms.validators import DataRequired, NumberRange, Optional
from datetime import datetime

class IngredienteForm(FlaskForm):
    """Formulario para la creación y edición de ingredientes"""
    nombreIngrediente = StringField('Nombre del Ingrediente', validators=[DataRequired(message='El nombre es obligatorio')])
    
    stock = FloatField('Cantidad en Stock',
                  validators=[Optional(),
                             NumberRange(min=0, message='El stock no puede ser negativo')])
    
    unidad = SelectField('Unidad de Medida', 
                        choices=[
                            ('kg', 'Kilogramo (kg)'),
                            ('g', 'Gramo (g)'),
                            ('l', 'Litro (l)'),
                            ('ml', 'Mililitro (ml)'),
                            ('unidad', 'Unidad'),
                            ('caja', 'Caja'),
                            ('paquete', 'Paquete')
                        ])
    
    stock_minimo = FloatField('Stock Mínimo', 
                            validators=[DataRequired(message='El stock mínimo es obligatorio'),
                                       NumberRange(min=0, message='El stock mínimo no puede ser negativo')])
    
    precio_unitario = FloatField('Precio Unitario', 
                               validators=[DataRequired(message='El precio es obligatorio'),
                                         NumberRange(min=0, message='El precio no puede ser negativo')])
    
    fecha_expiracion = DateField('Fecha de Expiración', validators=[Optional()],
                               format='%Y-%m-%d')

class MovimientoStockForm(FlaskForm):
    """Formulario para registrar movimientos de stock"""
    cantidad = FloatField('Cantidad', 
                        validators=[DataRequired(message='La cantidad es obligatoria'),
                                   NumberRange(min=0.01, message='La cantidad debe ser mayor a cero')])
    
    tipo_movimiento = SelectField('Tipo de Movimiento', 
                                choices=[
                                    (0, 'Entrada (Aumentar Stock)'),
                                    (1, 'Salida (Reducir Stock)')
                                ], coerce=int)
    
    referencia = StringField('Referencia (Opcional)', validators=[Optional()])