from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, SelectField, HiddenField
from wtforms.validators import DataRequired, Optional, NumberRange

class GalletaForm(FlaskForm):
    """Formulario para galletas usando WTForms"""
    id = HiddenField('id')
    nombreGalleta = StringField('Nombre de la Galleta', validators=[DataRequired()])
    descripcion = TextAreaField('Descripción', validators=[Optional()])
    estado = StringField('Estado', validators=[DataRequired()])
    peso_por_unidad = FloatField('Peso por Unidad (g)', validators=[NumberRange(min=0.1)])
    precio_unitario = FloatField('Precio Unitario ($)', validators=[NumberRange(min=0.1)])
    estatus = SelectField('Estatus', 
                        choices=[('1', 'Activo'), ('0', 'Inactivo')], 
                        validators=[DataRequired()])

def create_galleta_form(galleta=None):
    """Crea un diccionario con los campos del formulario para usar con el sistema de formularios personalizado"""
    from forms import TextField, TextAreaField, NumberField, SelectField, HiddenField
    
    # Determinar el valor del estatus para inicializar el campo
    estatus_value = "1"
    if galleta is not None and galleta.estatus is not None:
        estatus_value = str(galleta.estatus)
    
    fields = [
        HiddenField('id', 'id', "" if galleta is None else galleta.idGalleta).get_dict(),
        TextField('nombreGalleta', 'nombreGalleta', 'Nombre de la Galleta', 
                 "" if galleta is None else galleta.nombreGalleta, True).get_dict(),
        TextAreaField('descripcion', 'descripcion', 'Descripción', 
                      "" if galleta is None else galleta.descripcion, False, rows=4).get_dict(),
        TextField('estado', 'estado', 'Estado', 
                 "" if galleta is None else galleta.estado, True).get_dict(),
        NumberField('peso_por_unidad', 'peso_por_unidad', 'Peso por Unidad (g)', 
                    "" if galleta is None else galleta.peso_por_unidad, 0.1, None, True).get_dict(),
        NumberField('precio_unitario', 'precio_unitario', 'Precio Unitario ($)', 
                    "" if galleta is None else galleta.precio_unitario, 0.1, None, True).get_dict(),
        SelectField('estatus', 'estatus', 'Estatus', 
                   [{'value': '1', 'label': 'Activo'}, {'value': '0', 'label': 'Inactivo'}],
                   estatus_value, True).get_dict()
    ]
    
    return fields 