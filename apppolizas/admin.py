from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Poliza

# 1. Configuración para el modelo USUARIO
class UsuarioAdmin(UserAdmin):
    # Campos que se muestran en la lista (tabla) de usuarios
    list_display = ('username', 'email', 'nombres_completos', 'rol', 'cedula', 'estado', 'is_staff')
    
    # Filtros laterales
    list_filter = ('rol', 'estado', 'is_staff', 'is_superuser')
    
    # Campos de búsqueda
    search_fields = ('username', 'email', 'cedula', 'first_name', 'last_name')

    # Organización del formulario de EDICIÓN
    # UserAdmin.fieldsets trae la config por defecto (user, pass, permisos). 
    # Agregamos nuestros campos personalizados al final.
    fieldsets = UserAdmin.fieldsets + (
        ('Información Extra', {'fields': ('rol', 'cedula', 'telefono', 'estado')}),
    )

    # Organización del formulario de CREACIÓN
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Extra', {'fields': ('email', 'first_name', 'last_name', 'rol', 'cedula', 'telefono', 'estado')}),
    )

    # Método auxiliar para mostrar nombres completos en la tabla
    def nombres_completos(self, obj):
        return f"{obj.first_name} {obj.last_name}"

# 2. Configuración para el modelo PÓLIZA
class PolizaAdmin(admin.ModelAdmin):
    # Columnas a mostrar
    list_display = ('numero_poliza', 'tipo_poliza', 'usuario_gestor', 'estado', 'vigencia_fin', 'monto_asegurado')
    
    # Filtros laterales
    list_filter = ('estado', 'tipo_poliza', 'renovable', 'fecha_registro')
    
    # Barra de búsqueda (puedes buscar por número o por el usuario que gestiona)
    search_fields = ('numero_poliza', 'usuario_gestor__username', 'usuario_gestor__first_name')
    
    # Paginación (útil si tienes muchas pólizas)
    list_per_page = 20

    # Opcional: Para que ciertos campos sean solo lectura (ej: fechas automáticas)
    readonly_fields = ('fecha_registro',)

# 3. Registrar los modelos
admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Poliza, PolizaAdmin)
