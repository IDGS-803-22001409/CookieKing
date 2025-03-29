from flask_wtf import FlaskForm
from wtforms import StringField as WTFStringField
from wtforms import TextAreaField as WTFTextAreaField
from wtforms import IntegerField as WTFIntegerField
from wtforms import SelectField as WTFSelectField
from wtforms import FloatField as WTFFloatField
from wtforms import HiddenField as WTFHiddenField
from wtforms.validators import DataRequired, Optional, NumberRange
from utils.form_utils import FormField, TextField, TextAreaField, NumberField, SelectField, HiddenField

class RecetaForm(FlaskForm):
    """WTForms form for recipe validation"""
    id = WTFHiddenField('id')
    nombreReceta = WTFStringField('Nombre de la Receta', validators=[DataRequired()])
    instruccionesReceta = WTFTextAreaField('Instrucciones', validators=[DataRequired()])
    galletasProducidas = WTFIntegerField('Galletas Producidas', validators=[NumberRange(min=1)])
    idGalleta = WTFSelectField('Tipo de Galleta', validators=[DataRequired()], coerce=int)
    
    # Cambiar a string para la validación y hacer la conversión manualmente
    estatus = WTFSelectField('Estatus', 
                           choices=[('1', 'Activo'), ('0', 'Inactivo')], 
                           validators=[DataRequired()])

def create_receta_form(receta=None, galletas=None):
    """Create a form for recipe CRUD operations"""
    if galletas is None:
        galletas = []
    
    galletas_choices = [(g.idGalleta, g.nombreGalleta) for g in galletas]
    print(f"Choices generadas para galletas: {galletas_choices}")
    
    # Determinar el valor del estatus para inicializar el campo
    estatus_value = "1"
    if receta is not None and receta.estatus is not None:
        estatus_value = str(receta.estatus)
    
    fields = [
        HiddenField('id', 'id', "" if receta is None else receta.idReceta).get_dict(),
        TextField('nombreReceta', 'nombreReceta', 'Nombre de la Receta', 
                 "" if receta is None else receta.nombreReceta, True).get_dict(),
        TextAreaField('instruccionesReceta', 'instruccionesReceta', 'Instrucciones', 
                      "" if receta is None else receta.instruccionesReceta, True, rows=6).get_dict(),
        NumberField('galletasProducidas', 'galletasProducidas', 'Galletas Producidas', 
                    "" if receta is None else receta.galletasProducidas, 1, None, True).get_dict(),
        SelectField('idGalleta', 'idGalleta', 'Tipo de Galleta', 
                   [{'value': str(g[0]), 'label': g[1]} for g in galletas_choices],
                   "" if receta is None else str(receta.idGalleta), True).get_dict(),
        SelectField('estatus', 'estatus', 'Estatus', 
                   [{'value': '1', 'label': 'Activo'}, {'value': '0', 'label': 'Inactivo'}],
                   estatus_value, True).get_dict()
    ]
    
    return fields