from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from modulos.main.routes import roles_required
from modulos.ingredientes.controllers import IngredienteController
from modulos.ingredientes.forms import IngredienteForm, MovimientoStockForm, MermaForm
from datetime import datetime

# Crear blueprint para las rutas de ingredientes
ingredientes_bp = Blueprint('ingredientes', __name__, url_prefix='/ingredientes')

@ingredientes_bp.route('/')
@login_required
@roles_required("admin","empleado")
def index():
    """Vista principal para la administración de ingredientes"""
    ingredientes = IngredienteController.get_all_ingredientes()
    alertas = IngredienteController.get_ingredientes_by_stock_minimo()
    return render_template('modulos/ingredientes/index.html', 
                          ingredientes=ingredientes,
                          alertas=alertas)

@ingredientes_bp.route('/nuevo', methods=['GET', 'POST'])
def nuevo_ingrediente():
    """Vista para crear un nuevo ingrediente"""
    form = IngredienteForm()
    
    if form.validate_on_submit():
        data = {
            'nombreIngrediente': form.nombreIngrediente.data,
            'stock': form.stock.data,
            'unidad': form.unidad.data,
            'stock_minimo': form.stock_minimo.data,
            'precio_unitario': form.precio_unitario.data,
            'fecha_expiracion': form.fecha_expiracion.data.strftime('%Y-%m-%d') if form.fecha_expiracion.data else None
        }
        
        try:
            IngredienteController.create_ingrediente(data)
            flash('Ingrediente creado con éxito', 'success')
            return redirect(url_for('ingredientes.index'))
        except Exception as e:
            flash(f'Error al crear ingrediente: {str(e)}', 'error')
    
    return render_template('modulos/ingredientes/nuevo.html', form=form)

@ingredientes_bp.route('/editar/<int:ingrediente_id>', methods=['GET', 'POST'])
def editar_ingrediente(ingrediente_id):
    """Vista para editar un ingrediente existente"""
    ingrediente = IngredienteController.get_ingrediente_by_id(ingrediente_id)
    
    if not ingrediente:
        flash('Ingrediente no encontrado', 'error')
        return redirect(url_for('ingredientes.index'))
    
    form = IngredienteForm(obj=ingrediente)
    
    if form.validate_on_submit():
        data = {
            'nombreIngrediente': form.nombreIngrediente.data,
            'stock': form.stock.data,
            'unidad': form.unidad.data,
            'stock_minimo': form.stock_minimo.data,
            'precio_unitario': form.precio_unitario.data,
            'fecha_expiracion': form.fecha_expiracion.data.strftime('%Y-%m-%d') if form.fecha_expiracion.data else None
        }
        
        try:
            IngredienteController.update_ingrediente(ingrediente_id, data)
            flash('Ingrediente actualizado con éxito', 'success')
            return redirect(url_for('ingredientes.index'))
        except Exception as e:
            flash(f'Error al actualizar ingrediente: {str(e)}', 'error')
    
    return render_template('modulos/ingredientes/editar.html', form=form, ingrediente=ingrediente)

@ingredientes_bp.route('/eliminar/<int:ingrediente_id>', methods=['POST'])
def eliminar_ingrediente(ingrediente_id):
    """Eliminar un ingrediente"""
    try:
        resultado = IngredienteController.delete_ingrediente(ingrediente_id)
        
        if resultado:
            flash('Ingrediente eliminado con éxito', 'success')
        else:
            flash('No se puede eliminar el ingrediente porque tiene movimientos asociados', 'error')
    except Exception as e:
        flash(f'Error al eliminar ingrediente: {str(e)}', 'error')
    
    return redirect(url_for('ingredientes.index'))

@ingredientes_bp.route('/movimiento/<int:ingrediente_id>', methods=['GET', 'POST'])
def registrar_movimiento(ingrediente_id):
    """Vista para registrar un movimiento de stock"""
    ingrediente = IngredienteController.get_ingrediente_by_id(ingrediente_id)
    
    if not ingrediente:
        flash('Ingrediente no encontrado', 'error')
        return redirect(url_for('ingredientes.index'))
    
    form = MovimientoStockForm()
    
    if form.validate_on_submit():
        try:
            resultado = IngredienteController.actualizar_stock(
                ingrediente_id=ingrediente_id,
                cantidad=form.cantidad.data,
                tipo_movimiento=form.tipo_movimiento.data,
                referencia=form.referencia.data
            )
            
            if resultado:
                flash('Movimiento registrado con éxito', 'success')
                return redirect(url_for('ingredientes.historial', ingrediente_id=ingrediente_id))
            else:
                flash('Error al registrar el movimiento. Verifique que haya stock suficiente para consumo.', 'error')
        except Exception as e:
            flash(f'Error al registrar movimiento: {str(e)}', 'error')
    
    return render_template('modulos/ingredientes/movimiento.html', 
                          form=form, 
                          ingrediente=ingrediente)

@ingredientes_bp.route('/historial/<int:ingrediente_id>')
def historial(ingrediente_id):
    """Ver historial de movimientos de un ingrediente"""
    ingrediente = IngredienteController.get_ingrediente_by_id(ingrediente_id)
    
    if not ingrediente:
        flash('Ingrediente no encontrado', 'error')
        return redirect(url_for('ingredientes.index'))
    
    movimientos = IngredienteController.get_movimientos_by_ingrediente(ingrediente_id)
    
    return render_template('modulos/ingredientes/historial.html',
                          ingrediente=ingrediente,
                          movimientos=movimientos)

@ingredientes_bp.route('/api/listar', methods=['GET'])
def api_listar():
    """API para obtener lista de ingredientes en formato JSON"""
    ingredientes = IngredienteController.get_all_ingredientes()
    return jsonify([ing.to_dict() for ing in ingredientes])



@ingredientes_bp.route('/merma/<int:ingrediente_id>', methods=['GET', 'POST'])
@login_required
@roles_required("admin","empleado")
def registrar_merma(ingrediente_id):
    """Registra una merma de ingrediente"""
    ingrediente = IngredienteController.get_ingrediente_by_id(ingrediente_id)
    
    if not ingrediente:
        flash('Ingrediente no encontrado', 'error')
        return redirect(url_for('ingredientes.index'))
    
    form = MermaForm()
    form.set_unidades_choices(ingrediente.unidad)
    
    if form.validate_on_submit():
        try:
            resultado = IngredienteController.registrar_merma(
                ingrediente_id=ingrediente_id,
                cantidad=form.cantidad.data,
                motivo=form.motivo.data,
                unidad_ingresada=form.unidad.data
            )
            
            if resultado:
                flash('Merma registrada con éxito', 'success')
                return redirect(url_for('ingredientes.historial', ingrediente_id=ingrediente_id))
            else:
                flash('Error al registrar la merma. Verifique que haya stock suficiente.', 'error')
        except Exception as e:
            flash(f'Error al registrar merma: {str(e)}', 'error')
    
    return render_template('modulos/ingredientes/merma.html', form=form, ingrediente=ingrediente)