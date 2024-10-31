from django.contrib import admin
from .models import usuarios, Profesor
from inventario.models import articulos
from inventario.models import  Reserva
from .models import BebeConsulta
# Register your models here.

# @admin.register(usuarios)
# class UsuariosAdmin(admin.ModelAdmin):
#     list_display=['cui', 'username']
#     list_display_links=['username']



    # readonly_fields=('login_attempts', 'active_account')

# admin.site.register(Usuarios, UsuariosAdmin)


class UsuariosAdmin(admin.ModelAdmin):
    # Definir los campos que se mostrarán
    list_display = ('user', 'cui', 'phone', 'birth_date', 'profile_image')  # Campos a mostrar
    search_fields = ('user__username', 'cui', 'phone')  # Agregar búsqueda por campos
    list_filter = ('birth_date',)  # Agregar filtro por fecha de nacimiento
    fieldsets = (
        (None, {
            'fields': ('user', 'cui', 'phone', 'birth_date', 'profile_image')  # Agregar estos campos en la página de edición
        }),
    )

admin.site.register(usuarios, UsuariosAdmin)

class ProfesorAdmin(admin.ModelAdmin):
    # Mostrar los campos relevantes en la lista de profesores
    list_display = ('get_username', 'nombre', 'apellido', 'dpi', 'especialidad', 'telefono')  # Mostrar la especialidad y teléfono
    search_fields = ('user__username', 'nombre', 'apellido', 'dpi', 'especialidad', 'telefono')  # Añadir búsqueda por especialidad y teléfono
    list_filter = ('apellido', 'especialidad')  # Agregar filtro por apellido y especialidad
    fieldsets = (
        (None, {
            'fields': ('user', 'nombre', 'apellido', 'dpi', 'especialidad', 'telefono', 'foto_perfil')  # Añadir campos de especialidad, teléfono y foto de perfil
        }),
    )

    # Mostrar el nombre de usuario del campo user
    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Username'

    # Controla que solo el administrador pueda crear catedráticos
    def has_add_permission(self, request):
        return request.user.is_superuser

# Registrar el modelo en el admin
admin.site.register(Profesor, ProfesorAdmin)

# Admin para BebeConsulta
class BebeConsultaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha_nacimiento', 'sexo', 'peso', 'tipo_sangre', 'datos_adicionales', 'foto')
    search_fields = ('nombre', 'sexo', 'tipo_sangre')
    list_filter = ('sexo', 'tipo_sangre')
    fieldsets = (
        (None, {
            'fields': ('nombre', 'fecha_nacimiento', 'sexo', 'peso', 'tipo_sangre', 'foto', 'datos_adicionales')
        }),
    )

# Admin para Reserva
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('nombre_bebe', 'profesor', 'fecha_reserva', 'hora_reserva', 'producto', 'usuario')
    search_fields = ('nombre_bebe__nombre', 'profesor__nombre', 'fecha_reserva')
    list_filter = ('fecha_reserva', 'profesor')
    fieldsets = (
        (None, {
            'fields': ('nombre_bebe', 'profesor', 'fecha_reserva', 'hora_reserva', 'producto', 'usuario')
        }),
    )

# Registrar ambos modelos en el admin
admin.site.register(BebeConsulta, BebeConsultaAdmin)
admin.site.register(Reserva, ReservaAdmin)



"""
    list_display = ['last_name', 'fisrt_name', 'username', 'email', 'cui'] #Propiedades visibles del campo
    ordering = ['last_name']    #Ordena registros por
    search_fields = ['last_name', 'username', 'cui'] #Permite buscar por
    # list_display_links = [''] #brindar link a campo
    # list_filter=['']  #Añadir buscar por filtro
    list_per_page=15    #Cantidad de items por pagina
    readonly_fields=('cui', 'username') #Evitar la modificacion en la edicion de registro
    # exclude=['']      #Excluir campos en la edicion de registro
"""