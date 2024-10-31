from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from autenticacion import views as autenticacion_views
from .import views

from .views import VRegistro, cerrar_sesion, iniciar_sesion, perfil, perfil_pdf
urlpatterns = [
    path('', VRegistro.as_view(), name="Autenticacion"),
    path('cerrar_sesion', cerrar_sesion, name="cerrar_sesion"),
    path('iniciar_sesion', iniciar_sesion, name="iniciar_sesion"),
    path('perfil', perfil, name="perfil"),
    path('perfil_pdf', perfil_pdf.as_view(), name="perfil_pdf"),
    path('bebe_consulta/', autenticacion_views.bebe_consulta_view, name='bebe_consulta'),



    path('reset_password/', auth_views.PasswordResetView.as_view(template_name="reset_password/password_reset.html"), name="reset_password"),

    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name="reset_password/password_reset_sent.html"), name="password_reset_done"),
    
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="reset_password/password_reset_form.html"), name="password_reset_confirm"),

    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name="reset_password/password_reset_complete.html"), name="password_reset_complete"),

    path('facial-login/', views.facial_login, name='facial_login'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)