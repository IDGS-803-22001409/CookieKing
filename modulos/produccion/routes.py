# Actualización de routes.py
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from models import db
from flask_login import login_required
from modulos.main.routes import roles_required
from modulos.galletas.models import Galletas, MermaGalletas
from modulos.ingredientes.models import Ingrediente, MovimientoInsumo
from modulos.recetas.models import Receta, RecetaIngrediente
from modulos.produccion.models import Produccion, ProduccionDetalle
from datetime import datetime
import uuid

# Crear blueprint para las rutas de producción
produccion_bp = Blueprint('produccion', __name__, url_prefix='/produccion')


@produccion_bp.route('/solicitud/')
@login_required
def solicitud():
    """Vista principal para la administración de solicitudes"""
    galletas = Galletas.query.all()
    return render_template('modulos/produccion/solicitud.html')

@produccion_bp.route('/')
@login_required
@roles_required('admin', 'empleado')
def index():
    """Vista principal para la administración de producción"""
    galletas = Galletas.query.all()
    return render_template('modulos/produccion/index.html', galletas=galletas)

@produccion_bp.route('/inventarioGalletas', methods=['GET'])
@login_required
@roles_required('admin', 'empleado')
def inventario_galletas():
    """Vista para inventario de galletas"""
    galletas = Galletas.query.all()
    return render_template('modulos/produccion/inventarioGalletas.html', galletas=galletas)

@produccion_bp.route('/produccionGalletas/<int:galleta_id>', methods=['GET', 'POST'])
@login_required
def produccion_galletas(galleta_id):
    """Vista para producir galletas directamente"""
    # Obtener la galleta seleccionada
    galleta = Galletas.query.get_or_404(galleta_id)
    
    receta = Receta.query.filter_by(idGalleta=galleta_id, estatus=1).first()
    
    if not receta:
        flash('No existe una receta activa para esta galleta', 'error')
        return redirect(url_for('produccion.index'))
    
    ingredientes_receta = RecetaIngrediente.query.filter_by(receta_id=receta.idReceta).all()
    
    ingredientes_disponibles = True
    ingredientes_info = []
    max_lotes_posibles = float('inf')  
    
    for ingr_receta in ingredientes_receta:
        ingrediente = Ingrediente.query.get(ingr_receta.ingrediente_id)
        cantidad_requerida_por_lote = ingr_receta.cantidad
        
        if cantidad_requerida_por_lote > 0:
            lotes_posibles = int(ingrediente.stock / cantidad_requerida_por_lote)
            max_lotes_posibles = min(max_lotes_posibles, lotes_posibles)
        
        ingredientes_info.append({
            'ingrediente': ingrediente,
            'cantidad_requerida': cantidad_requerida_por_lote,
            'disponible': ingrediente.stock >= cantidad_requerida_por_lote,
            'faltante': max(0, cantidad_requerida_por_lote - ingrediente.stock),
            'lotes_posibles': int(ingrediente.stock / cantidad_requerida_por_lote) if cantidad_requerida_por_lote > 0 else 0
        })
        
        if ingrediente.stock < cantidad_requerida_por_lote:
            ingredientes_disponibles = False
    
    if request.method == 'POST':
        cantidad_solicitada = int(request.form.get('cantidad', 1))
        
        cantidad_a_producir = min(cantidad_solicitada, max_lotes_posibles)
        
        if cantidad_a_producir <= 0:
            flash('No hay suficientes ingredientes para producir galletas', 'error')
            return redirect(url_for('produccion.produccion_galletas', galleta_id=galleta_id))
        
        if cantidad_solicitada > cantidad_a_producir:
            flash(f'Solo se pueden producir {cantidad_a_producir} lotes con los ingredientes disponibles', 'warning')
        
        lote = f"LOTE-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}"
        nueva_produccion = Produccion(
            receta_id=receta.idReceta,
            estado_produccion=2,  
            fecha_produccion=datetime.now().date(),
            cantidad_producida=cantidad_a_producir * receta.galletasProducidas,
            lote=lote
        )
        
        db.session.add(nueva_produccion)
        db.session.flush()  # Para obtener el ID generado
        
        # Reducir el stock de ingredientes y registrar los movimientos
        for ingr_receta in ingredientes_receta:
            ingrediente = Ingrediente.query.get(ingr_receta.ingrediente_id)
            cantidad_usada = ingr_receta.cantidad * cantidad_a_producir
            
            # Crear detalle de producción
            detalle = ProduccionDetalle(
                produccion_id=nueva_produccion.idProduccion,
                ingrediente_id=ingr_receta.ingrediente_id,
                cantidad_requerida=cantidad_usada,
                cantidad_usada=cantidad_usada,
                estado=1  # Usado
            )
            db.session.add(detalle)
            
            # Registrar movimiento de consumo de ingrediente
            movimiento = MovimientoInsumo(
                ingrediente_id=ingrediente.idIngrediente,
                tipo_movimiento=1,  # Consumo
                cantidad=cantidad_usada,
                fecha_movimiento=datetime.now().date(),
                referencia=f"Producción #{nueva_produccion.idProduccion}"
            )
            db.session.add(movimiento)
            
            # Actualizar stock del ingrediente
            ingrediente.stock -= cantidad_usada
        
        # Actualizar existencias de la galleta
        galletas_producidas = cantidad_a_producir * receta.galletasProducidas
        galleta.existencias += galletas_producidas
        
        db.session.commit()
        
        flash(f'Se han producido {galletas_producidas} galletas ({cantidad_a_producir} lotes). Lote: {lote}', 'success')
        return redirect(url_for('produccion.index'))
    
    return render_template(
        'modulos/produccion/produccionGalletas.html', 
        galleta=galleta, 
        receta=receta, 
        ingredientes=ingredientes_info,
        ingredientes_disponibles=ingredientes_disponibles,
        max_lotes_posibles=max_lotes_posibles
    )

@produccion_bp.route('/inventario')
@login_required
def inventario():
    """Vista para inventario de galletas"""
    return render_template('modulos/produccion/inventario.html')


from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from models import db
from flask_login import login_required
from modulos.main.routes import roles_required
from modulos.galletas.models import Galletas, MermaGalletas
from modulos.ingredientes.models import Ingrediente, MovimientoInsumo
from modulos.recetas.models import Receta, RecetaIngrediente
from modulos.produccion.models import Produccion, ProduccionDetalle
from datetime import datetime
import uuid

# Crear blueprint para las rutas de producción
produccion_bp = Blueprint('produccion', __name__, url_prefix='/produccion')


@produccion_bp.route('/solicitud/')
@login_required
def solicitud():
    """Vista principal para la administración de solicitudes"""
    galletas = Galletas.query.all()
    return render_template('modulos/produccion/solicitud.html')

@produccion_bp.route('/')
@login_required
@roles_required('admin', 'empleado')
def index():
    """Vista principal para la administración de producción"""
    galletas = Galletas.query.all()
    return render_template('modulos/produccion/index.html', galletas=galletas)

@produccion_bp.route('/inventarioGalletas', methods=['GET'])
@login_required
@roles_required('admin', 'empleado')
def inventario_galletas():
    """Vista para inventario de galletas"""
    galletas = Galletas.query.all()
    return render_template('modulos/produccion/inventarioGalletas.html', galletas=galletas)

@produccion_bp.route('/produccionGalletas/<int:galleta_id>', methods=['GET', 'POST'])
@login_required
def produccion_galletas(galleta_id):
    """Vista para producir galletas directamente"""
    # Obtener la galleta seleccionada
    galleta = Galletas.query.get_or_404(galleta_id)
    
    receta = Receta.query.filter_by(idGalleta=galleta_id, estatus=1).first()
    
    if not receta:
        flash('No existe una receta activa para esta galleta', 'error')
        return redirect(url_for('produccion.index'))
    
    ingredientes_receta = RecetaIngrediente.query.filter_by(receta_id=receta.idReceta).all()
    
    ingredientes_disponibles = True
    ingredientes_info = []
    max_lotes_posibles = float('inf')  
    
    for ingr_receta in ingredientes_receta:
        ingrediente = Ingrediente.query.get(ingr_receta.ingrediente_id)
        cantidad_requerida_por_lote = ingr_receta.cantidad
        
        if cantidad_requerida_por_lote > 0:
            lotes_posibles = int(ingrediente.stock / cantidad_requerida_por_lote)
            max_lotes_posibles = min(max_lotes_posibles, lotes_posibles)
        
        ingredientes_info.append({
            'ingrediente': ingrediente,
            'cantidad_requerida': cantidad_requerida_por_lote,
            'disponible': ingrediente.stock >= cantidad_requerida_por_lote,
            'faltante': max(0, cantidad_requerida_por_lote - ingrediente.stock),
            'lotes_posibles': int(ingrediente.stock / cantidad_requerida_por_lote) if cantidad_requerida_por_lote > 0 else 0
        })
        
        if ingrediente.stock < cantidad_requerida_por_lote:
            ingredientes_disponibles = False
    
    if request.method == 'POST':
        cantidad_solicitada = int(request.form.get('cantidad', 1))
        
        cantidad_a_producir = min(cantidad_solicitada, max_lotes_posibles)
        
        if cantidad_a_producir <= 0:
            flash('No hay suficientes ingredientes para producir galletas', 'error')
            return redirect(url_for('produccion.produccion_galletas', galleta_id=galleta_id))
        
        if cantidad_solicitada > cantidad_a_producir:
            flash(f'Solo se pueden producir {cantidad_a_producir} lotes con los ingredientes disponibles', 'warning')
        
        lote = f"LOTE-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}"
        nueva_produccion = Produccion(
            receta_id=receta.idReceta,
            estado_produccion=2,  
            fecha_produccion=datetime.now().date(),
            cantidad_producida=cantidad_a_producir * receta.galletasProducidas,
            lote=lote
        )
        
        db.session.add(nueva_produccion)
        db.session.flush()  # Para obtener el ID generado
        
        # Reducir el stock de ingredientes y registrar los movimientos
        for ingr_receta in ingredientes_receta:
            ingrediente = Ingrediente.query.get(ingr_receta.ingrediente_id)
            cantidad_usada = ingr_receta.cantidad * cantidad_a_producir
            
            # Crear detalle de producción
            detalle = ProduccionDetalle(
                produccion_id=nueva_produccion.idProduccion,
                ingrediente_id=ingr_receta.ingrediente_id,
                cantidad_requerida=cantidad_usada,
                cantidad_usada=cantidad_usada,
                estado=1  # Usado
            )
            db.session.add(detalle)
            
            # Registrar movimiento de consumo de ingrediente
            movimiento = MovimientoInsumo(
                ingrediente_id=ingrediente.idIngrediente,
                tipo_movimiento=1,  # Consumo
                cantidad=cantidad_usada,
                fecha_movimiento=datetime.now().date(),
                referencia=f"Producción #{nueva_produccion.idProduccion}"
            )
            db.session.add(movimiento)
            
            # Actualizar stock del ingrediente
            ingrediente.stock -= cantidad_usada
        
        # Actualizar existencias de la galleta
        galletas_producidas = cantidad_a_producir * receta.galletasProducidas
        galleta.existencias += galletas_producidas
        
        db.session.commit()
        
        flash(f'Se han producido {galletas_producidas} galletas ({cantidad_a_producir} lotes). Lote: {lote}', 'success')
        return redirect(url_for('produccion.index'))
    
    return render_template(
        'modulos/produccion/produccionGalletas.html', 
        galleta=galleta, 
        receta=receta, 
        ingredientes=ingredientes_info,
        ingredientes_disponibles=ingredientes_disponibles,
        max_lotes_posibles=max_lotes_posibles
    )

@produccion_bp.route('/inventario')
@login_required
def inventario():
    """Vista para inventario de galletas"""
    return render_template('modulos/produccion/inventario.html')


@produccion_bp.route('/mermaGalletas', methods=['GET'])
@login_required
@roles_required('admin', 'empleado')
def merma_galletas():
    """Vista para gestionar mermas de galletas"""
    galletas = Galletas.query.all()
    mermas = MermaGalletas.query.order_by(MermaGalletas.fecha_registro.desc()).all()
    
    return render_template('modulos/produccion/mermaGalletas.html', galletas=galletas, mermas=mermas)


@produccion_bp.route('/registrarMerma', methods=['POST'])
@login_required
@roles_required('admin', 'empleado')
def registrar_merma():
    """Endpoint para registrar una nueva merma"""
    if request.method == 'POST':
        try:
            galleta_id = request.form.get('galleta_id')
            cantidad = int(request.form.get('cantidad', 0))
            descripcion = request.form.get('descripcion', '')
            
            # Validar datos
            if not galleta_id or cantidad <= 0 or not descripcion:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'message': 'Datos incompletos o inválidos'}), 400
                flash('Datos incompletos o inválidos', 'error')
                return redirect(url_for('produccion.merma_galletas'))
            
            # Obtener la galleta
            galleta = Galletas.query.get(galleta_id)
            if not galleta:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'message': 'Galleta no encontrada'}), 404
                flash('Galleta no encontrada', 'error')
                return redirect(url_for('produccion.merma_galletas'))
            
            # Verificar que haya suficientes existencias
            if galleta.existencias < cantidad:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'message': f'No hay suficientes existencias. Disponibles: {galleta.existencias}'}), 400
                flash(f'No hay suficientes existencias. Disponibles: {galleta.existencias}', 'error')
                return redirect(url_for('produccion.merma_galletas'))
            
            # Registrar la merma
            nueva_merma = MermaGalletas(
                galleta_id=galleta_id,
                cantidad=cantidad,
                descripcion=descripcion,
                fecha_registro=datetime.now()
            )
            db.session.add(nueva_merma)
            
            # Actualizar existencias
            galleta.existencias -= cantidad
            
            db.session.commit()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': True, 
                    'message': f'Merma de {cantidad} galletas "{galleta.nombreGalleta}" registrada correctamente'
                })
            
            flash(f'Merma de {cantidad} galletas "{galleta.nombreGalleta}" registrada correctamente', 'success')
            return redirect(url_for('produccion.merma_galletas'))
            
        except Exception as e:
            db.session.rollback()
            print(f"Error al registrar merma: {str(e)}")
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': f'Error al registrar la merma: {str(e)}'}), 500
            
            flash(f'Error al registrar la merma: {str(e)}', 'error')
            return redirect(url_for('produccion.merma_galletas'))
            
    # Si no es POST
    return redirect(url_for('produccion.merma_galletas'))