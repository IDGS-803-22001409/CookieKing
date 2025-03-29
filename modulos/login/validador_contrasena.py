import re
from passlib.context import CryptContext

class ValidadorContrasena:
    CONTRASENAS_DEBILES = [
        'contrasena', '123456', 'qwerty', 'admin', 'dejame_entrar', 
        'bienvenido', 'monkey', 'abc123', 'password', '12345678'
    ]

    # Configurar contexto de hashing con múltiples esquemas para compatibilidad
    pwd_context = CryptContext(
        schemes=["bcrypt", "django_pbkdf2_sha256", "plaintext"],
        deprecated="auto",
        bcrypt__default_rounds=12,
        django_pbkdf2_sha256__default_rounds=29000
    )

    @staticmethod
    def validar_contrasena(contrasena):
        # Validaciones de política de contraseñas
        if len(contrasena) < 8:
            return False, "La contraseña debe tener al menos 8 caracteres"
        
        # Agregar más contraseñas comunes
        if contrasena.lower() in ValidadorContrasena.CONTRASENAS_DEBILES:
            return False, "Contraseña muy común o insegura"
        
        if not re.search(r'[A-Z]', contrasena):
            return False, "Debe contener al menos una letra mayúscula"
        
        if not re.search(r'[a-z]', contrasena):
            return False, "Debe contener al menos una letra minúscula"
        
        if not re.search(r'\d', contrasena):
            return False, "Debe contener al menos un número"
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', contrasena):
            return False, "Debe contener al menos un carácter especial"
        
        return True, "Contraseña válida"

    @staticmethod
    def hash_contrasena(contrasena):
        # Usar bcrypt como método de hashing predeterminado
        return ValidadorContrasena.pwd_context.hash(contrasena)

    @staticmethod
    def verificar_contrasena(contrasena_plana, contrasena_hash):
        try:
            # Intentar verificar usando múltiples esquemas
            return ValidadorContrasena.pwd_context.verify(contrasena_plana, contrasena_hash)
        except Exception as e:
            # Registro de error para depuración
            print(f"Error al verificar contraseña: {e}")
            return False