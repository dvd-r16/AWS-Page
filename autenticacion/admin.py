from django.contrib import admin
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from axes.admin import AccessLogAdmin as DefaultAccessLogAdmin
from axes.models import AccessLog
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from datetime import datetime
from inventario.models import Reserva
import random

# La función exportar_pdf está bien definida aquí

def exportar_pdf(modeladmin, request, queryset):
    # Crear un objeto HttpResponse con el tipo de contenido PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="access_logs.pdf"'

    # Crear un objeto canvas para generar el PDF y definir el tamaño de la página
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4  # Tamaño de página A4 (Ancho y Alto)

    # Establecer el título del documento
    p.setFont("Helvetica-Bold", 12)  # Reducir un poco el tamaño de la fuente
    p.drawString(50, height - 40, "Reporte de Accesos")

    # Posiciones iniciales para la tabla
    y_position = height - 80  # Ajuste la posición vertical inicial
    x_offsets = [50, 140, 230, 320, 410, 500]  # Ajustar posiciones de columnas
    column_widths = [90, 90, 90, 90, 90, 90]  # Ancho de cada columna
    max_width = width - 60  # Espacio máximo permitido horizontalmente

    # Agregar encabezados de la tabla
    headers = ['Attempt Time', 'Logout Time', 'IP Address', 'Username', 'User Agent', 'Path Info']
    p.setFont("Helvetica-Bold", 10)  # Fuente y tamaño más pequeños para encabezados
    for index, header in enumerate(headers):
        p.drawString(x_offsets[index], y_position, header)

    # Reducir la posición Y para las filas
    y_position -= 20

    # Ajustar el tamaño de la fuente para el contenido
    p.setFont("Helvetica", 8)  # Reducir más el tamaño para el contenido

    # Iterar sobre los registros seleccionados y agregarlos al PDF
    for log in queryset:
        fields = [
            str(log.attempt_time),
            str(log.logout_time) if log.logout_time else '-',
            log.ip_address,
            log.username,
            log.user_agent,
            log.path_info
        ]

        # Asegurarse de no superponer textos
        for index, field in enumerate(fields):
            # Ajustar texto al ancho de columna si es necesario
            max_text_width = column_widths[index]
            text_width = stringWidth(field, "Helvetica", 8)
            if text_width > max_text_width:
                # Dividir en múltiples líneas si el texto es demasiado ancho
                max_chars = int(max_text_width / 5)  # Estimación de caracteres por línea
                lines = [field[i:i+max_chars] for i in range(0, len(field), max_chars)]
                for line in lines:
                    if y_position < 40:  # Añadir nueva página si se llega al final
                        p.showPage()
                        y_position = height - 40
                        p.setFont("Helvetica", 8)  # Ajustar fuente en nueva página
                    p.drawString(x_offsets[index], y_position, line)
                    y_position -= 10  # Espacio entre líneas divididas
            else:
                p.drawString(x_offsets[index], y_position, field)

        # Reducir la posición Y para la siguiente fila
        y_position -= 20
        if y_position < 40:  # Añadir nueva página si se llega al final
            p.showPage()
            y_position = height - 40
            p.setFont("Helvetica", 8)

    # Finalizar el PDF
    p.showPage()
    p.save()
    return response

# Asegúrate de que estás extendiendo la clase AccessLogAdmin correctamente
DefaultAccessLogAdmin.actions = tuple(DefaultAccessLogAdmin.actions) + (exportar_pdf,)

# Función para generar la factura en PDF
# Función para generar la factura en PDF
def exportar_facturas_pdf(modeladmin, request, queryset):
    response = HttpResponse(content_type='application/pdf')
    
    # Generar número de factura único
    numero_factura = random.randint(1000, 9999)  # Genera un número aleatorio, puedes personalizarlo
    fecha_actual = datetime.now().strftime('%Y%m%d')  # Fecha en formato año-mes-día
    nombre_archivo = f"factura_{fecha_actual}_{numero_factura}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
    
    p = canvas.Canvas(response, pagesize=A4)

    total_con_impuesto = 450.00  # Precio total con el impuesto ya incluido
    impuesto_porcentaje = 0.08
    precio_base = total_con_impuesto / (1 + impuesto_porcentaje)  # Precio antes del impuesto
    impuesto = total_con_impuesto - precio_base  # Impuesto incluido en el total

    for reserva in queryset:
        # Encabezado de la clínica y número de factura
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, 770, "Clínica Pedíatrica: Sonrisas de la Vida")
        p.setFont("Helvetica", 10)
        p.drawString(50, 755, f"NIT Emisor: 108710444 | Fecha de Emisión: {datetime.now().strftime('%d-%m-%Y')}")
        p.drawString(50, 740, "Dirección: 3 Calle 9-80, Centro Comercial Plaza Médica, Local 19, Ciudad San Cristobal, Zona 8 de Mixco")
        p.drawString(50, 725, f"Número de Factura: {numero_factura}")

        # Información del receptor (usuario)
        p.setFont("Helvetica-Bold", 10)
        nit = getattr(reserva.usuario, 'nit', 'N/A') if hasattr(reserva.usuario, 'nit') else 'N/A'
        nombre_completo = f"{reserva.usuario.first_name} {reserva.usuario.last_name}" if reserva.usuario.first_name and reserva.usuario.last_name else reserva.usuario.username
        p.drawString(50, 710, f"NIT Receptor: {nit}")
        p.drawString(50, 695, f"Nombre Receptor: {nombre_completo}")
        p.drawString(50, 680, f"Fecha y hora de emisión: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")

        # Información del producto / servicio
        p.setFont("Helvetica-Bold", 10)
        p.drawString(50, 650, "Descripción del Servicio")
        p.setFont("Helvetica", 10)
        p.drawString(50, 635, f"Producto: {reserva.producto.nombre}")
        p.drawString(50, 620, f"Fecha de Reserva: {reserva.fecha_reserva.strftime('%d/%m/%Y')}")
        p.drawString(50, 605, f"Hora de Reserva: {reserva.hora_reserva.strftime('%H:%M')}")

        # Tabla de precios
        y_position = 570
        p.setFont("Helvetica-Bold", 10)
        p.drawString(50, y_position, "Cantidad")
        p.drawString(150, y_position, "Descripción")
        p.drawString(300, y_position, "P. Base (Q)")
        p.drawString(400, y_position, "Impuesto (Q)")
        p.drawString(500, y_position, "Total (Q)")

        # Valores de la tabla
        p.setFont("Helvetica", 10)
        y_position -= 20
        p.drawString(50, y_position, "1")
        p.drawString(150, y_position, "Consulta médica")
        p.drawString(300, y_position, f"{precio_base:.2f}")
        p.drawString(400, y_position, f"{impuesto:.2f}")
        p.drawString(500, y_position, f"{total_con_impuesto:.2f}")

        # Totales
        y_position -= 30
        p.setFont("Helvetica-Bold", 10)
        p.drawString(400, y_position, "TOTAL:")
        p.drawString(500, y_position, f"{total_con_impuesto:.2f}")

        # Pie de página
        y_position -= 40
        p.setFont("Helvetica", 8)
        p.drawString(50, y_position, "Superintendencia de Administración Tributaria - Contribuyendo por el país que todos queremos")

        # Añadir una nueva página para la próxima factura, si hay más
        p.showPage()

    # Guardar el PDF
    p.save()
    return response


# Registrar la acción en el admin para el modelo Reserva
@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('nombre_bebe', 'profesor', 'fecha_reserva', 'hora_reserva', 'producto', 'usuario')
    actions = [exportar_facturas_pdf]  # Agregar la acción para exportar facturas en PDF
