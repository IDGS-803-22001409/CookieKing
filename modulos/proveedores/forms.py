# modulos/proveedores/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, HiddenField
from wtforms.validators import DataRequired, Optional, Email, Length
from utils.form_utils import TextField, TextAreaField as CustomTextAreaField, SelectField as CustomSelectField, HiddenField as CustomHiddenField

class ProveedorForm(FlaskForm):
    """Formulario para proveedores usando WTForms"""
    id = HiddenField('id')
    nombre_proveedor = StringField('Nombre del Proveedor', validators=[DataRequired(), Length(max=255)])
    telefono = StringField('Teléfono', validators=[Optional(), Length(max=20)])
    correo = StringField('Correo Electrónico', validators=[Optional(), Email(), Length(max=100)])
    direccion = TextAreaField('Dirección', validators=[Optional(), Length(max=255)])
    rfc = StringField('RFC', validators=[Optional(), Length(max=13)])
    estatus = SelectField('Estatus', 
                        choices=[('1', 'Activo'), ('0', 'Inactivo')], 
                        validators=[DataRequired()])

def create_proveedor_form(proveedor=None):
    """Crea un diccionario con los campos del formulario para usar con el sistema de formularios personalizado"""
    
    # Determinar el valor del estatus para inicializar el campo
    estatus_value = "1"
    if proveedor is not None and proveedor.estatus is not None:
        estatus_value = str(proveedor.estatus)
    
    fields = [
        CustomHiddenField('id', 'id', "" if proveedor is None else proveedor.idProveedor).get_dict(),
        TextField('nombre_proveedor', 'nombre_proveedor', 'Nombre del Proveedor', 
                 "" if proveedor is None else proveedor.nombre_proveedor, True).get_dict(),
        TextField('telefono', 'telefono', 'Teléfono', 
                 "" if proveedor is None else proveedor.telefono, False).get_dict(),
        TextField('correo', 'correo', 'Correo Electrónico', 
                 "" if proveedor is None else proveedor.correo, False).get_dict(),
        CustomTextAreaField('direccion', 'direccion', 'Dirección', 
                      "" if proveedor is None else proveedor.direccion, False, rows=3).get_dict(),
        TextField('rfc', 'rfc', 'RFC', 
                 "" if proveedor is None else proveedor.rfc, False).get_dict(),
        CustomSelectField('estatus', 'estatus', 'Estatus', 
                   [{'value': '1', 'label': 'Activo'}, {'value': '0', 'label': 'Inactivo'}],
                   estatus_value, True).get_dict()
    ]
    
    return fields