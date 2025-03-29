import pyotp
from datetime import datetime, timedelta
import random

class AutenticacionDosFactores:
    @staticmethod
    def generar_codigo_totp(longitud=6):
        """
        Genera un código TOTP temporal para enviar por correo.
        
        Returns:
            dict: Diccionario con código TOTP, secret y tiempo de expiración
        """
        # Generar código numérico aleatorio
        codigo = str(random.randint(100000, 999999))
        
        return {
            'codigo': codigo,
            'expira_en': datetime.utcnow() + timedelta(minutes=10)
        }

    @staticmethod
    def verificar_codigo_totp(codigo_usuario, codigo_generado):
        """
        Verifica el código TOTP proporcionado por el usuario.
        
        Args:
            codigo_usuario (str): Código ingresado por el usuario
            codigo_generado (str): Código generado originalmente
        
        Returns:
            bool: True si el código es válido, False en caso contrario
        """
        return codigo_usuario == codigo_generado