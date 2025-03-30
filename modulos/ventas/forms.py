from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, HiddenField, DateField, FloatField, IntegerField
from wtforms.validators import DataRequired, Optional, NumberRange
from datetime import datetime
from utils.form_utils import TextField, TextAreaField as CustomTextAreaField, DateField as CustomDateField
from utils.form_utils import NumberField, SelectField as CustomSelectField, HiddenField as CustomHiddenField

class VentaForm(FlaskForm):
    """Formulario para ventas usando WTForms"""
    id = HiddenField('id')
    IdCliente = SelectField('Cliente', validators=[Optional()], coerce=int)
    estatus = SelectField('Estatus', 
                        choices=[('1', 'Completada'), ('0', 'Pendiente'), ('2', 'Cancelada')],
                        validators=[DataRequired()])

def create_venta_form(venta=None, clientes=None):
    """Crea un diccionario con los campos del formulario para usar con el sistema de formularios personalizado"""
    if clientes is None:
        clientes = []
    
    # Crear opciones para el select de clientes
    clientes_choices = [{'value': '', 'label': 'Cliente General'}]
    clientes_choices.extend([{'value': str(c.idCliente), 'label': c.nombreCliente} for c in clientes])
    
    # Determinar el valor del estatus para inicializar el campo
    estatus_value = "1"  # Por defecto, completada
    if venta is not None and venta.estatus is not None:
        estatus_value = str(venta.estatus)
    
    # Determinar el valor del cliente para inicializar el campo
    cliente_value = ""
    if venta is not None and venta.IdCliente is not None:
        cliente_value = str(venta.IdCliente)
    
    fields = [
        CustomHiddenField('id', 'id', "" if venta is None else venta.idVenta).get_dict(),
        CustomSelectField('IdCliente', 'IdCliente', 'Cliente', 
                        clientes_choices,
                        cliente_value, False).get_dict(),
        CustomSelectField('estatus', 'estatus', 'Estatus', 
                        [
                            {'value': '1', 'label': 'Completada'}, 
                            {'value': '0', 'label': 'Pendiente'}, 
                            {'value': '2', 'label': 'Cancelada'}
                        ],
                        estatus_value, True).get_dict()
    ]
    
    return fields

class PagoProveedorForm(FlaskForm):
    """Formulario para pagos a proveedores usando WTForms"""
    id = HiddenField('id')
    idProveedor = SelectField('Proveedor', validators=[DataRequired()], coerce=int)
    fechaPago = DateField('Fecha de Pago', validators=[DataRequired()], format='%Y-%m-%d')
    monto = FloatField('Monto', validators=[DataRequired(), NumberRange(min=0.01)])
    referencia = StringField('Referencia', validators=[Optional()])
    idCompra = SelectField('Compra Relacionada', validators=[Optional()], coerce=int)
    estatus = SelectField('Estatus', 
                        choices=[('1', 'Pagado'), ('0', 'Pendiente'), ('2', 'Cancelado')],
                        validators=[DataRequired()])

def create_pago_proveedor_form(pago=None, proveedores=None, compras=None):
    """Crea un diccionario con los campos del formulario para usar con el sistema de formularios personalizado"""
    if proveedores is None:
        proveedores = []
    
    if compras is None:
        compras = []
    
    # Crear opciones para el select de proveedores
    proveedores_choices = [{'value': str(p.idProveedor), 'label': p.nombre_proveedor} for p in proveedores]
    
    # Crear opciones para el select de compras
    compras_choices = [{'value': '', 'label': 'Ninguna'}]
    compras_choices.extend([{'value': str(c.idCompra), 'label': f'Compra #{c.idCompra} - ${c.total:.2f}'} for c in compras])
    
    # Determinar valores iniciales
    proveedor_value = ""
    fecha_pago_value = datetime.now().strftime('%Y-%m-%d')
    monto_value = ""
    referencia_value = ""
    compra_value = ""
    estatus_value = "1"  # Por defecto, pagado
    
    if pago is not None:
        proveedor_value = str(pago.idProveedor) if pago.idProveedor else ""
        fecha_pago_value = pago.fechaPago.strftime('%Y-%m-%d') if pago.fechaPago else datetime.now().strftime('%Y-%m-%d')
        monto_value = pago.monto
        referencia_value = pago.referencia or ""
        compra_value = str(pago.idCompra) if pago.idCompra else ""
        estatus_value = str(pago.estatus) if pago.estatus is not None else "1"
    
    fields = [
        CustomHiddenField('id', 'id', "" if pago is None else pago.idPago).get_dict(),
        CustomSelectField('idProveedor', 'idProveedor', 'Proveedor', 
                        proveedores_choices,
                        proveedor_value, True).get_dict(),
        CustomDateField('fechaPago', 'fechaPago', 'Fecha de Pago', 
                      fecha_pago_value, True).get_dict(),
        NumberField('monto', 'monto', 'Monto', 
                   monto_value, 0.01, None, True).get_dict(),
        TextField('referencia', 'referencia', 'Referencia', 
                 referencia_value, False).get_dict(),
        CustomSelectField('idCompra', 'idCompra', 'Compra Relacionada', 
                        compras_choices,
                        compra_value, False).get_dict(),
        CustomSelectField('estatus', 'estatus', 'Estatus', 
                        [
                            {'value': '1', 'label': 'Pagado'}, 
                            {'value': '0', 'label': 'Pendiente'}, 
                            {'value': '2', 'label': 'Cancelado'}
                        ],
                        estatus_value, True).get_dict()
    ]
    
    return fields

class PedidoClienteForm(FlaskForm):
    """Formulario para pedidos de clientes usando WTForms"""
    id = HiddenField('id')
    idCliente = SelectField('Cliente', validators=[DataRequired()], coerce=int)
    fechaEntrega = DateField('Fecha de Entrega', validators=[Optional()], format='%Y-%m-%d')
    instrucciones = TextAreaField('Instrucciones', validators=[Optional()])
    estatus = SelectField('Estatus', 
                        choices=[
                            ('0', 'Pendiente'), 
                            ('1', 'En Proceso'), 
                            ('2', 'Completado'), 
                            ('3', 'Cancelado')
                        ],
                        validators=[DataRequired()])

def create_pedido_cliente_form(pedido=None, clientes=None):
    """Crea un diccionario con los campos del formulario para usar con el sistema de formularios personalizado"""
    if clientes is None:
        clientes = []
    
    # Crear opciones para el select de clientes
    clientes_choices = [{'value': str(c.idCliente), 'label': c.nombreCliente} for c in clientes]
    
    # Determinar valores iniciales
    cliente_value = ""
    fecha_entrega_value = ""
    instrucciones_value = ""
    estatus_value = "0"  # Por defecto, pendiente
    
    if pedido is not None:
        cliente_value = str(pedido.idCliente) if pedido.idCliente else ""
        fecha_entrega_value = pedido.fechaEntrega.strftime('%Y-%m-%d') if pedido.fechaEntrega else ""
        instrucciones_value = pedido.instrucciones or ""
        estatus_value = str(pedido.estatus) if pedido.estatus is not None else "0"
    
    fields = [
        CustomHiddenField('id', 'id', "" if pedido is None else pedido.idPedido).get_dict(),
        CustomSelectField('idCliente', 'idCliente', 'Cliente', 
                        clientes_choices,
                        cliente_value, True).get_dict(),
        CustomDateField('fechaEntrega', 'fechaEntrega', 'Fecha de Entrega', 
                      fecha_entrega_value, False).get_dict(),
        CustomTextAreaField('instrucciones', 'instrucciones', 'Instrucciones', 
                          instrucciones_value, False, rows=3).get_dict(),
        CustomSelectField('estatus', 'estatus', 'Estatus', 
                        [
                            {'value': '0', 'label': 'Pendiente'}, 
                            {'value': '1', 'label': 'En Proceso'}, 
                            {'value': '2', 'label': 'Completado'}, 
                            {'value': '3', 'label': 'Cancelado'}
                        ],
                        estatus_value, True).get_dict()
    ]
    
    return fields