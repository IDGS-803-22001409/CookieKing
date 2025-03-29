# modulos/clientes/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, TextAreaField, SelectField, HiddenField
from wtforms.validators import DataRequired, Optional, Email, Length
from utils.form_utils import TextField, TextAreaField as CustomTextAreaField, SelectField as CustomSelectField, HiddenField as CustomHiddenField

class ClienteForm(FlaskForm):
    """Formulario para clientes usando WTForms"""
    id = HiddenField('id')
    nombreCliente = StringField('Nombre del Cliente', validators=[DataRequired(), Length(max=250)])
    fechaNacimiento = DateField('Fecha de Nacimiento', validators=[Optional()], format='%Y-%m-%d')
    telefono = StringField('Teléfono', validators=[DataRequired(), Length(max=25)])
    correo = StringField('Correo Electrónico', validators=[Optional(), Email(), Length(max=150)])
    estatus = SelectField('Estatus', 
                        choices=[('1', 'Activo'), ('0', 'Inactivo')], 
                        validators=[DataRequired()])

def create_cliente_form(cliente=None):
    """Crea un diccionario con los campos del formulario para usar con el sistema de formularios personalizado"""
    
    # Determinar el valor del estatus para inicializar el campo
    estatus_value = "1"
    if cliente is not None and cliente.estatus is not None:
        estatus_value = str(cliente.estatus)
    
    fields = [
        CustomHiddenField('id', 'id', "" if cliente is None else cliente.idCliente).get_dict(),
        TextField('nombreCliente', 'nombreCliente', 'Nombre del Cliente', 
                 "" if cliente is None else cliente.nombreCliente, True).get_dict(),
        TextField('fechaNacimiento', 'fechaNacimiento', 'Fecha de Nacimiento', 
                 "" if cliente is None or not cliente.fechaNacimiento else cliente.fechaNacimiento.strftime('%Y-%m-%d'), False, type="date").get_dict(),
        TextField('telefono', 'telefono', 'Teléfono', 
                 "" if cliente is None else cliente.telefono, True).get_dict(),
        TextField('correo', 'correo', 'Correo Electrónico', 
                 "" if cliente is None else cliente.correo, False).get_dict(),
        CustomSelectField('estatus', 'estatus', 'Estatus', 
                   [{'value': '1', 'label': 'Activo'}, {'value': '0', 'label': 'Inactivo'}],
                   estatus_value, True).get_dict()
    ]
    
    return fields