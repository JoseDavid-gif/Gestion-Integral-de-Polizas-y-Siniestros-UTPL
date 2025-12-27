import jwt
import datetime
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from .repositories import UsuarioRepository
from .models import Usuario, Poliza 
from .repositories import UsuarioRepository, PolizaRepository # Importar el nuevo repo

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
        
        # Retornamos el token y el valor crudo del rol ('admin'/'analista')
        return user, user.rol
        return token
    

class PolizaService:
    """Servicio para gestión de Pólizas"""

    @staticmethod
    def listar_polizas():
        return PolizaRepository.get_all()

    @staticmethod
    def crear_poliza(data):
        # Aquí podrías agregar validaciones de negocio, ej:
        if data.get('prima_total') < data.get('prima_base'):
            raise ValidationError("La prima total no puede ser menor a la base")
        
        return PolizaRepository.create(data)

    @staticmethod
    def obtener_poliza(poliza_id):
        poliza = PolizaRepository.get_by_id(poliza_id)
        if not poliza:
            raise ValidationError("La póliza no existe")
        return poliza

    @staticmethod
    def actualizar_poliza(poliza_id, data):
        poliza = PolizaRepository.get_by_id(poliza_id)
        if not poliza:
            raise ValidationError("La póliza no existe")
        return PolizaRepository.update(poliza, data)

    @staticmethod
    def eliminar_poliza(poliza_id):
        poliza = PolizaRepository.get_by_id(poliza_id)
        if not poliza:
            raise ValidationError("La póliza no existe")
        PolizaRepository.delete(poliza)
