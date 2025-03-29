from flask_wtf import FlaskForm
# Renombrar las importaciones de WTForms para evitar conflictos
from wtforms import StringField as WTFStringField
from wtforms import TextAreaField as WTFTextAreaField
from wtforms import IntegerField as WTFIntegerField
from wtforms import SelectField as WTFSelectField
from wtforms import FloatField as WTFFloatField
from wtforms import HiddenField as WTFHiddenField
from wtforms.validators import DataRequired, Optional, NumberRange

class FormField:
    """Base class for form fields"""
    
    def __init__(self, id, name, label, value="", required=False, **kwargs):
        self.id = id
        self.name = name
        self.label = label
        self.value = value
        self.required = required
        self.attrs = kwargs
        self.template = "components/input_text.html"
    
    def get_dict(self):
        """Return a dictionary representation of this field"""
        return {
            'id': self.id,
            'name': self.name,
            'label': self.label,
            'value': self.value,
            'required': self.required,
            'template': self.template,
            'attrs': self.attrs
        }

class TextField(FormField):
    """Text input field"""
    
    def __init__(self, id, name, label, value="", required=False, **kwargs):
        super().__init__(id, name, label, value, required, **kwargs)
        self.template = "components/input_text.html"

class TextAreaField(FormField):
    """Textarea input field"""
    
    def __init__(self, id, name, label, value="", required=False, rows=4, **kwargs):
        super().__init__(id, name, label, value, required, **kwargs)
        self.rows = rows
        self.template = "components/input_textarea.html"

class NumberField(FormField):
    """Number input field"""
    
    def __init__(self, id, name, label, value="", min=None, max=None, required=False, **kwargs):
        super().__init__(id, name, label, value, required, **kwargs)
        self.min = min
        self.max = max
        self.template = "components/input_number.html"

class SelectField(FormField):
    """Select dropdown field"""
    
    def __init__(self, id, name, label, options=None, value="", required=False, **kwargs):
        super().__init__(id, name, label, value, required, **kwargs)
        self.options = options or []
        self.template = "components/input_select.html"
    
    def get_dict(self):
        """Return a dictionary representation of this field"""
        dict_data = super().get_dict()
        dict_data['options'] = self.options  # Asegúrate de que las opciones estén en el diccionario
        return dict_data

class HiddenField(FormField):
    """Hidden input field"""
    
    def __init__(self, id, name, value="", **kwargs):
        super().__init__(id, name, "", value, False, **kwargs)
        self.template = "components/input_hidden.html"

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