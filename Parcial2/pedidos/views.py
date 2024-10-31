from email import message
from django.shortcuts import redirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from carro.carro import Carro
from pedidos.models import LineaPedido, Pedido
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
from usuarios.models import usuarios
from inventario.models import articulos
from autenticacion.forms import BebeConsultaForm
from inventario.models import Reserva


from .models import Reserva

@login_required(login_url="/autenticacion/iniciar_sesion")
def procesar_pedido(request):
    pedido = Pedido.objects.create(user=request.user)
    carro = Carro(request)
    lineas_pedido = list()

    # Iterar sobre los productos en el carrito
    for key, value in carro.carro.items():
        lineas_pedido.append(LineaPedido(
            producto_id=key,
            cantidad=value["cantidad"],
            user=request.user,
            pedido=pedido
        ))

    # Lógica para verificar la validez del pedido
    pedido_valido = True
    for linea in lineas_pedido:
        en_stock = articulos.objects.get(pk=linea.producto_id)
        nueva_cantidad = en_stock.cantidad - linea.cantidad

        if nueva_cantidad < 0:
            pedido_valido = False
            break

    if pedido_valido:
        # Almacenar el pedido
        for linea in lineas_pedido:
            en_stock = articulos.objects.get(pk=linea.producto_id)
            en_stock.cantidad -= linea.cantidad
            en_stock.save()

        LineaPedido.objects.bulk_create(lineas_pedido)

        # Obtener la reserva asociada al usuario o al pedido
        try:
            reserva = Reserva.objects.filter(usuario=request.user).order_by('fecha_reserva').last()  # Obtiene la última reserva
        except Reserva.DoesNotExist:
            reserva = None  # Si no hay reserva, asignar None

        # Llamar a la función para enviar el correo con la reserva
        enviar_mail(
            pedido=pedido,
            lineas_pedido=lineas_pedido,
            nombreusuario=request.user.username,
            emailusuario=request.user.email,
            reserva=reserva  # Pasar la reserva al correo
        )

        return redirect("/autenticacion/perfil")
    else:
        # Manejo de errores si el pedido no es válido
        info_usuario = usuarios.objects.all()
        return render(request, "stock/checkout.html", {"info_usuario": info_usuario, "pedido_valido": pedido_valido})


def enviar_mail(pedido, lineas_pedido, nombreusuario, emailusuario, **kwargs):
    # Obtener la reserva si está en los argumentos
    reserva = kwargs.get('reserva', None)

    # Asunto del correo
    asunto = "Comprobante de pedido"

    # Renderizamos el HTML del correo con el contexto, incluyendo la reserva si está disponible
    mensaje = render_to_string("emails/pedido.html", {
        "pedido": pedido,
        "lineas_pedido": lineas_pedido,
        "nombreusuario": nombreusuario,
        "reserva": reserva  # Añadimos la reserva al contexto si está presente
    })

    # Generar el mensaje en texto plano a partir del HTML
    mensaje_texto = strip_tags(mensaje)

    # Correo desde el que se envía
    from_email = "andrericardo763@gmail.com"
    # Correo al que se envía
    to = emailusuario

    # Enviar el correo con HTML y mensaje en texto plano
    send_mail(asunto, mensaje_texto, from_email, [to], html_message=mensaje)


# def enviar_mail(**kwargs):

#     asunto="Comprobante de pedido"
#     mensaje = render_to_string("emails/pedido.html",{

#         "pedido": kwargs.get("pedido"),
#         "lineas_pedido": kwargs.get("lineas_pedido"),
#         "nombreusuario": kwargs.get("nombreusuario")

#     })


#     mensaje_texto=strip_tags(mensaje)
#     from_email="kaorigtshop@gmail.com"         ########Correo desde el que se envia        aajekdjonxyejtih 
#     to=kwargs.get("emailusuario")               ########Correo desde al que se envia
#     # to = "francoabimael07@gmail.com"

#     send_mail(asunto, mensaje_texto, from_email, [to], html_message=mensaje)