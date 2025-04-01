from flask import Blueprint, render_template

# Crear blueprints para los módulos en desarrollo
usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')
clientes_bp = Blueprint('clientes', __name__, url_prefix='/clientes')
proveedores_bp = Blueprint('proveedores', __name__, url_prefix='/proveedores')
compras_bp = Blueprint('compras', __name__, url_prefix='/compras')
ingredientes_bp = Blueprint('ingredientes', __name__, url_prefix='/ingredientes')
produccion_bp = Blueprint('produccion', __name__, url_prefix='/produccion')
ventas_bp = Blueprint('ventas', __name__, url_prefix='/ventas')
reportes_bp = Blueprint('reportes', __name__, url_prefix='/reportes')

# Rutas para usuarios
@usuarios_bp.route('/')
def index():
    return render_template('modulos/usuarios/index.html')

# Rutas para clientes
@clientes_bp.route('/')
def index():
    return render_template('modulos/clientes/index.html')

# Rutas para proveedores
@proveedores_bp.route('/')
def index():
    return render_template('modulos/proveedores/index.html')

# Rutas para compras
@compras_bp.route('/')
def index():
    return render_template('modulos/compras/index.html')

@compras_bp.route('/nueva')
def nueva():
    return render_template('modulos/compras/index.html')

# Rutas para ingredientes
@ingredientes_bp.route('/')
def index():
    return render_template('modulos/ingredientes/index.html')

# Rutas para producción
@produccion_bp.route('/')
def index():
    return render_template('modulos/produccion/index.html')

@produccion_bp.route('/inventarioGalletas')
def inventario_galletas():
    return render_template('modulos/produccion/inventarioGalletas.html')

@produccion_bp.route('/solicitud')
def solicitud():
    return render_template('modulos/produccion/solicitud.html')

@produccion_bp.route('/inventario')
def inventario():
    return render_template('modulos/produccion/inventario.html')

# Rutas para ventas
@ventas_bp.route('/')
def index():
    return render_template('modulos/ventas/index.html')

@ventas_bp.route('/nueva')
def nueva():
    return render_template('modulos/ventas/index.html')

@ventas_bp.route('/diarias')
def diarias():
    return render_template('modulos/ventas/index.html')

@ventas_bp.route('/productos-mas-vendidos')
def productos_mas_vendidos():
    return render_template('modulos/ventas/index.html')

# Rutas para reportes
@reportes_bp.route('/')
def index():
    return render_template('modulos/reportes/index.html')