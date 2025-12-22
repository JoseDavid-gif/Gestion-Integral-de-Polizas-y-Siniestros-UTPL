import jwt
import datetime
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from .repositories import UsuarioRepository
from .models import Usuario

class AuthService:
    """Servicio de Autenticación y Reglas de Negocio"""

    @staticmethod
    def login_analista(username, password):
        # 1. Validar que los campos no estén vacíos
        if not username or not password:
            raise ValidationError("Usuario y contraseña son obligatorios")

        # 2. Buscar usuario (usando Repository)
        user = UsuarioRepository.get_by_username(username)
        
        if not user:
            raise ValidationError("Credenciales inválidas")

        # 3. Validar contraseña (usando método nativo de AbstractUser)
        if not user.check_password(password):
            raise ValidationError("Credenciales inválidas")

        # 4. REGLA DE NEGOCIO: Verificar que sea Analista
        if user.rol != Usuario.ANALISTA:
            raise ValidationError("Acceso denegado. Este usuario no es Analista.")

        # 5. Generar JWT
        payload = {
            'id': user.id,
            'username': user.username,
            'rol': user.rol,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2), # Expira en 2 horas
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        
        return token