from datetime import datetime, timedelta
from models import db
from modulos.galletas.models import Galleta
from modulos.ingredientes.models import Ingrediente

def init_test_data():
    """Inicializar la base de datos con datos de prueba"""
    
    # Añadir galletas de prueba si la tabla está vacía
    if Galleta.query.count() == 0:
        print("Añadiendo galletas de prueba...")
        
        # Crear algunos tipos de galletas de ejemplo
        galletas = [
            Galleta(
                nombreGalleta="Chocolate Chip",
                descripcion="Galleta tradicional con chispas de chocolate. Suave por dentro y crujiente por fuera.",
                estado="Disponible",
                peso_por_unidad=30.0,
                precio_unitario=10.0,
                estatus=1
            ),
            Galleta(
                nombreGalleta="Vainilla",
                descripcion="Galleta clásica de vainilla, perfecta para acompañar con té o café.",
                estado="Disponible",
                peso_por_unidad=25.0,
                precio_unitario=8.0,
                estatus=1
            ),
            Galleta(
                nombreGalleta="Avena y Pasas",
                descripcion="Galleta nutritiva con avena y pasas, ideal para el desayuno.",
                estado="Disponible",
                peso_por_unidad=35.0,
                precio_unitario=12.0,
                estatus=1
            ),
            Galleta(
                nombreGalleta="Mantequilla",
                descripcion="Galleta tradicional de mantequilla, con un sabor suave y delicado.",
                estado="Disponible",
                peso_por_unidad=20.0,
                precio_unitario=7.5,
                estatus=1
            ),
            Galleta(
                nombreGalleta="Doble Chocolate",
                descripcion="Galleta para amantes del chocolate, con masa de chocolate y chispas de chocolate.",
                estado="En desarrollo",
                peso_por_unidad=32.0,
                precio_unitario=15.0,
                estatus=0
            )
        ]
        
        # Agregar las galletas a la base de datos
        for galleta in galletas:
            db.session.add(galleta)
        
        # Guardar los cambios
        db.session.commit()
        print("Datos de prueba de galletas creados exitosamente")
    
    # Añadir ingredientes de prueba si la tabla está vacía
    if Ingrediente.query.count() == 0:
        print("Añadiendo ingredientes de prueba...")
        
        # Establecer fechas de expiración relativas a la fecha actual
        hoy = datetime.now().date()
        un_mes = hoy + timedelta(days=30)
        dos_meses = hoy + timedelta(days=60)
        tres_meses = hoy + timedelta(days=90)
        seis_meses = hoy + timedelta(days=180)
        
        # Crear algunos ingredientes de ejemplo
        ingredientes = [
            Ingrediente(
                nombreIngrediente="Harina de trigo",
                stock=25.0,
                unidad="kg",
                stock_minimo=5.0,
                fecha_expiracion=seis_meses
            ),
            Ingrediente(
                nombreIngrediente="Azúcar",
                stock=15.0,
                unidad="kg",
                stock_minimo=3.0,
                fecha_expiracion=seis_meses
            ),
            Ingrediente(
                nombreIngrediente="Mantequilla",
                stock=10.0,
                unidad="kg",
                stock_minimo=2.0,
                fecha_expiracion=un_mes
            ),
            Ingrediente(
                nombreIngrediente="Huevos",
                stock=120.0,
                unidad="unidades",
                stock_minimo=24.0,
                fecha_expiracion=hoy + timedelta(days=15)
            ),
            Ingrediente(
                nombreIngrediente="Chispas de chocolate",
                stock=8.0,
                unidad="kg",
                stock_minimo=1.5,
                fecha_expiracion=tres_meses
            ),
            Ingrediente(
                nombreIngrediente="Esencia de vainilla",
                stock=2.0,
                unidad="litros",
                stock_minimo=0.5,
                fecha_expiracion=seis_meses
            ),
            Ingrediente(
                nombreIngrediente="Avena",
                stock=12.0,
                unidad="kg",
                stock_minimo=2.0,
                fecha_expiracion=dos_meses
            ),
            Ingrediente(
                nombreIngrediente="Pasas",
                stock=5.0,
                unidad="kg",
                stock_minimo=1.0,
                fecha_expiracion=tres_meses
            )
        ]
        
        # Agregar los ingredientes a la base de datos
        for ingrediente in ingredientes:
            db.session.add(ingrediente)
        
        # Guardar los cambios
        db.session.commit()
        print("Datos de prueba de ingredientes creados exitosamente")
    
    # Aquí se pueden añadir más datos de prueba para otras tablas 