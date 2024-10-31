from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseNotFound
from inventario.models import articulos
from inventario.models import Reserva
from pedidos.models import Pedido, LineaPedido
from django.http import HttpRequest
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
import openpyxl
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.conf import settings
from django.http import HttpResponse
from django.http import JsonResponse
# Create your views here.

def catalogo(request):
    arts = articulos.objects.all()
    return render(request, "inventario/catalogo.html", {"arts":arts})

def single_product(request, id):
    # arts = articulos.objects.all()
    product = articulos.objects.get(pk=id)
    # product_name = product.cantidad
    # print(product_name)
    return render(request, "inventario/single-product.html", {"product":product})



@login_required
def curso_page(request, id):
    # Intentar obtener la reserva usando el ID
    try:
        reserva = Reserva.objects.get(pk=id)
    except Reserva.DoesNotExist:
        return HttpResponseNotFound(f"No se encontró la reserva con el ID {id}.")
    
    # Verificar si el usuario es el profesor asignado a la reserva
    es_profesor = request.user == reserva.profesor.user

    # Mensaje de depuración
    if es_profesor:
        print(f"El usuario {request.user} es el profesor de la consulta.")
    else:
        print(f"El usuario {request.user} NO es el profesor de la consulta.")

    # Verificar si el usuario es el padre/madre que hizo la reserva
    es_cliente = request.user == reserva.usuario

    # Si el profesor envía información adicional a través del formulario
    if es_profesor and request.method == "POST":
        # Guardar comentarios o notas adicionales del profesor
        reserva.notas_profesor = request.POST.get("notas_profesor", reserva.notas_profesor)
        
        # Guardar archivo adjunto, si lo hay
        if 'archivo' in request.FILES:
            reserva.archivo = request.FILES['archivo']
        
        reserva.save()

    # Obtener los datos de la reserva y la consulta relacionada
    detalles_reserva = {
        "nombre_bebe": reserva.nombre_bebe,
        "fecha_nacimiento": reserva.fecha_nacimiento,
        "fecha_reserva": reserva.fecha_reserva,
        "hora_reserva": reserva.hora_reserva,
        "datos_adicionales": reserva.datos_adicionales,
        "producto": reserva.producto,  # Consulta o servicio que se está brindando
    }

    # Si es profesor o el cliente (padre/madre), mostrar la página de la reserva
    if es_profesor or es_cliente:
        return render(request, "inventario/curso_page.html", {
            "reserva": reserva,
            "es_profesor": es_profesor,  # Indicar si es el profesor
            "es_cliente": es_cliente,  # Indicar si es el cliente (padre/madre)
            "detalles_reserva": detalles_reserva,  # Enviar los detalles de la reserva
        })
    else:
        return HttpResponseForbidden("No tienes acceso a esta consulta.")


    
@login_required
def exportar_notas_excel(request, id):
    # Obtener el curso específico
    curso = get_object_or_404(articulos, pk=id)

    # Verificar si el usuario es el catedrático del curso
    if request.user != curso.catedratico.user:
        return HttpResponseForbidden("No tienes permiso para descargar las notas de este curso.")

    # Crear un nuevo archivo Excel en memoria
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Notas de {curso.nombre}"

    # Agregar encabezados
    ws.append(['Estudiante', 'Zona (75pts)', 'Final (25pts)', 'Total'])

    # Obtener los estudiantes inscritos en el curso y sus notas
    lineas_pedido = LineaPedido.objects.filter(producto=curso)

    for linea in lineas_pedido:
        # Si los valores de zona o final están en None, los mostramos como 'N/A'
        zona = linea.zona if linea.zona is not None else 'N/A'
        final = linea.final if linea.final is not None else 'N/A'
        total = zona + final if isinstance(zona, int) and isinstance(final, int) else 'N/A'
        
        ws.append([linea.user.username, zona, final, total])

    # Configurar la respuesta HTTP
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="Notas_{curso.nombre}.xlsx"'

    # Guardar el archivo en la respuesta
    wb.save(response)

    return response

@login_required
def desasignar_curso(request, id):
    # Obtener el curso específico
    curso = get_object_or_404(articulos, pk=id)

    # Verificar si el usuario está inscrito en el curso
    linea_pedido = get_object_or_404(LineaPedido, user=request.user, producto=curso)

    # Solo permitir que el estudiante se desasigne
    if request.user != linea_pedido.user:
        return HttpResponseForbidden("No tienes permiso para desasignarte de este curso.")

    # Eliminar la asignación
    linea_pedido.delete()

    # Aumentar la cantidad del artículo (curso) en 1, devolviendo el cupo
    curso.cantidad += 1
    curso.save()

    return redirect('perfil')

@login_required
def descargar_certificado(request, id):
    # Obtener el curso específico y la imagen de fondo del certificado
    curso = get_object_or_404(articulos, pk=id)
    estudiante = request.user

    # Verificar que el estudiante está inscrito y que ha pasado el curso
    es_estudiante = LineaPedido.objects.filter(user=estudiante, producto_id=curso.id, zona__gte=61).exists()

    if not es_estudiante:
        return HttpResponseForbidden("No tienes acceso a este certificado.")

    # Crear un nuevo PDF en memoria
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Certificado_{curso.nombre}_{estudiante.username}.pdf"'

    # Configurar el tamaño de la página
    pdf = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # Agregar la imagen de fondo si existe
    if curso.imagen_certificado:
        pdf.drawImage(
            curso.imagen_certificado.path,
            0, 0,
            width=width,
            height=height
        )

    # Configuración del texto para que esté centrado
    pdf.setFont("Helvetica-Bold", 24)
    pdf.setFillColorRGB(0, 0, 0)  # Color negro

    # Texto de felicitación
    texto_felicitacion = "Se le otorga el siguiente diploma a:"
    pdf.drawCentredString(width / 2, height / 2 + 50, texto_felicitacion)

     # Agregar el nombre del estudiante y DPI
    nombre_estudiante = f"{estudiante.first_name} {estudiante.last_name} con DPI: {estudiante.profile.cui}"
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawCentredString(width / 2, height / 2, nombre_estudiante)

    # Agregar la nota final del estudiante
    nota_final = LineaPedido.objects.get(user=estudiante, producto_id=curso.id).zona + LineaPedido.objects.get(user=estudiante, producto_id=curso.id).final
    texto_nota = f"Por haber completado satisfactoriamente el curso con una nota de: {nota_final}"
    pdf.setFont("Helvetica", 16)
    pdf.drawCentredString(width / 2, height / 2 - 30, texto_nota)

    pdf.showPage()
    pdf.save()

    return response

@login_required
def bebe_consulta(request):
    if request.method == 'POST':
        # Aquí manejarás la lógica del formulario cuando sea enviado
        # Por ejemplo, podrías procesar los datos que recibas y guardarlos.
        # formulario = BebeConsultaForm(request.POST)
        # if formulario.is_valid():
        #     formulario.save()
        #     # Redirige a otra vista después de guardar los datos, si es necesario.
        #     return redirect('nombre_de_otra_vista')

        pass  # Sustituye esto con la lógica de manejo de formulario.

    # Si no es una solicitud POST, simplemente renderiza la plantilla del formulario.
    return render(request, 'stock/bebe_consulta.html')

def marcar_completada(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    
    if request.method == 'POST':
        reserva.completada = not reserva.completada  # Alternar entre True y False
        reserva.save()
        return redirect('perfil')  # Redirige al perfil después de marcar como completada o no completada