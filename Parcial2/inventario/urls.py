from xml.dom.minidom import Document
from django.urls import path
from inventario import views
from django.conf import settings
from django.conf.urls.static import static
from .views import catalogo, single_product, curso_page
from .views import exportar_notas_excel
from .views import descargar_certificado
from . import views

urlpatterns = [
    path('', views.catalogo, name="Catalogo"),
    path('producto/<int:id>', views.single_product, name="Producto"),
    path('curso/<int:id>/', curso_page, name='curso_page'),
    path('curso/<int:id>/exportar-notas/', exportar_notas_excel, name='exportar_notas_excel'),
    path('curso/<int:id>/descargar-certificado/', descargar_certificado, name='descargar_certificado'),
    path('desasignar-curso/<int:id>/', views.desasignar_curso, name='desasignar_curso'),
    path('bebe_consulta/', views.bebe_consulta, name='bebe_consulta'),
    path('reserva/completar/<int:reserva_id>/', views.marcar_completada, name='marcar_completada'),
    
]

urlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)