import json
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView, TemplateView, View
from .forms import LoginForm, PolizaForm
from .repositories import UsuarioRepository
from .services import AuthService, PolizaService




@method_decorator(csrf_exempt, name='dispatch')
def logout_view(request):
    logout(request)
    return JsonResponse({'success': True})

class LoginView(FormView):
    template_name = 'login.html'
    form_class = LoginForm

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            try:
                user, rol = AuthService.login_universal(
                    form.cleaned_data['username'], 
                    form.cleaned_data['password']
                )
                
                login(request, user)
                
                if rol == 'admin':
                    redirect_url = '/administrador/dashboard/'
                else:
                    redirect_url = '/dashboard-analista/'
                
                return JsonResponse({
                    'success': True,
                    'redirect_url': redirect_url
                }, status=200)

            except ValidationError as e:
                return JsonResponse({'success': False, 'error': str(e)}, status=400)
            except Exception as e:
                return JsonResponse({'success': False, 'error': "Error interno"}, status=500)
        return JsonResponse({'success': False, 'error': "Datos inválidos"}, status=400)


class DashboardAdminView(LoginRequiredMixin, TemplateView):
    template_name = 'administrador/dashboard_admin.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if request.user.rol != 'admin':
            return redirect('dashboard_analista')
            
        return super().dispatch(request, *args, **kwargs)

class AdminUsuariosView(LoginRequiredMixin, TemplateView):
    template_name = 'administrador/usuarios.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
            
        if request.user.rol != 'admin':
            return redirect('dashboard_analista')
            
        return super().dispatch(request, *args, **kwargs)  


class DashboardAnalistaView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'       



@method_decorator(csrf_exempt, name='dispatch')
class UsuarioCRUDView(LoginRequiredMixin, View):
    """
    Vista centralizada para gestionar el CRUD de usuarios mediante JSON.
    """

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        # Si no está autenticado, responder 401 (Unauthorized)
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'No autenticado'}, status=401)
        
        # Si no es admin, responder 403 (Forbidden)
        if request.user.rol != 'admin':
            return JsonResponse({'error': 'No tienes permisos de administrador'}, status=403)
            
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, usuario_id=None):
        """LISTAR: Retorna todos los usuarios o uno específico."""
        if usuario_id:
            usuario = UsuarioRepository.get_by_id(usuario_id) 
            if not usuario:
                return JsonResponse({'error': 'Usuario no encontrado'}, status=404)
            data = {
                'id': usuario.id, 'username': usuario.username, 'email': usuario.email,
                'rol': usuario.rol, 'cedula': usuario.cedula, 'estado': usuario.estado
            }
        else:
            usuarios = UsuarioRepository.get_all_usuarios()
            data = list(usuarios.values('id', 'username', 'email', 'rol', 'cedula', 'estado'))
        
        return JsonResponse(data, safe=False)

    def post(self, request):
        """CREAR: Recibe JSON para crear un nuevo usuario."""
        try:
            data = json.loads(request.body)
            user = UsuarioRepository.create_usuario(data)
            return JsonResponse({
                'success': True,
                'message': 'Usuario creado exitosamente',
                'id': user.id
            }, status=201)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    def put(self, request, usuario_id):
        """ACTUALIZAR: Modifica un usuario existente."""
        try:
            data = json.loads(request.body)
            usuario = UsuarioRepository.update_usuario(usuario_id, data)
            return JsonResponse({
                'success': True,
                'message': f'Usuario {usuario.username} actualizado'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    def delete(self, request, usuario_id):
        """ELIMINAR: Borra un usuario del sistema."""
        try:
            UsuarioRepository.delete_usuario(usuario_id)
            return JsonResponse({
                'success': True, 
                'message': 'Usuario eliminado correctamente'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)    
        """
        Sobrescribimos el POST para responder con JSON para el manejo de JWT
        """
        form = self.get_form()
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            try:
                # Llamada al Servicio
                token = AuthService.login_analista(username, password)
                
                # Respuesta Exitosa con Token
                return JsonResponse({
                    'success': True,
                    'token': token,
                    'message': 'Inicio de sesión exitoso'
                }, status=200)

            except ValidationError as e:
                return JsonResponse({'success': False, 'error': str(e)}, status=403)
        
        return JsonResponse({'success': False, 'error': 'Datos de formulario inválidos'}, status=400)



class DashboardAnalistaView(TemplateView):
    template_name = 'dashboard.html'        

class PolizaListView(View):
    template_name = 'polizas.html'

    def get(self, request, *args, **kwargs):
        polizas = PolizaService.listar_polizas()
        form = PolizaForm() # Formulario vacío para el modal de crear
        return render(request, self.template_name, {'polizas': polizas, 'form': form})

    def post(self, request, *args, **kwargs):
        # Opción para CREAR desde la misma página (modal)
        form = PolizaForm(request.POST)
        if form.is_valid():
            try:
                PolizaService.crear_poliza(form.cleaned_data)
                messages.success(request, 'Póliza creada exitosamente')
                return redirect('polizas_list')
            except Exception as e:
                messages.error(request, f'Error al crear: {str(e)}')
        
        polizas = PolizaService.listar_polizas()
        return render(request, self.template_name, {'polizas': polizas, 'form': form})

class PolizaUpdateView(View):
    template_name = 'poliza_edit.html'
    
    def post(self, request, pk, *args, **kwargs):
        template_name = 'poliza_edit.html' # Usaremos un template específico para editar

    def get(self, request, pk, *args, **kwargs):
        try:
            poliza = PolizaService.obtener_poliza(pk)
            form = PolizaForm(instance=poliza) # Carga los datos existentes en el form
            return render(request, self.template_name, {'form': form, 'poliza': poliza})
        except Exception as e:
            messages.error(request, 'Error al cargar la póliza')
            return redirect('polizas_list')

    def post(self, request, pk, *args, **kwargs):
        try:
            poliza = PolizaService.obtener_poliza(pk)
            form = PolizaForm(request.POST, instance=poliza)
            
            if form.is_valid():
                # Pasamos los datos limpios al servicio para que actualice
                PolizaService.actualizar_poliza(pk, form.cleaned_data)
                messages.success(request, 'Póliza actualizada exitosamente')
                return redirect('polizas_list')
            else:
                messages.error(request, 'Por favor corrige los errores del formulario')
        
        except Exception as e:
            messages.error(request, f'Error al actualizar: {str(e)}')
            
        return render(request, self.template_name, {'form': form, 'poliza': poliza})

class PolizaDeleteView(View):
    def post(self, request, pk, *args, **kwargs):
        try:
            PolizaService.eliminar_poliza(pk)
            messages.success(request, 'Póliza eliminada')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
        return redirect('polizas_list')
