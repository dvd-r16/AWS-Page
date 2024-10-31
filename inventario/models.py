from tabnanny import verbose
from django.utils import timezone
from django.db import models
from usuarios.models import Profesor
from django.contrib.auth.models import User  # Para relacionar con catedráticos
from usuarios.models import BebeConsulta

class articulos(models.Model):
    nombre = models.CharField(max_length=30, null=False)
    categoria = models.CharField(max_length=30, null=False)
    precio = models.FloatField(null=False)
    descuento = models.FloatField(null=False)
    descripcion = models.CharField(max_length=150)
    imagen = models.ImageField(upload_to='servicios')
    cantidad = models.IntegerField(null=False, default= 0)
    catedratico = models.ForeignKey(Profesor, on_delete=models.CASCADE)
    disponibilidad = models.BooleanField()
    creacion = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name= 'articulo'

    def __str__(self):
        return self.nombre
    
class Curso(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    profesor = models.ForeignKey(Profesor, on_delete=models.CASCADE)  # Relación con el profesor
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()

    def __str__(self):
        return self.nombre
    

class Estudiante(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return self.nombre


class Nota(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)  # Relación con Curso
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)  # Relación con Estudiante
    valor = models.DecimalField(max_digits=5, decimal_places=2)  # Ejemplo de valor de nota, hasta 100.00

    def __str__(self):
        return f'{self.estudiante} - {self.curso} - {self.valor}'

# class clientes(models.Model):
#     nombre = models.CharField(max_length=50)
#     apellido = models.CharField(max_length=50)
#     dpi = models.IntegerField()
#     telefono = models.IntegerField()
#     direccion = models.CharField(max_length=150)

class Reserva(models.Model):
    bebe_consulta = models.OneToOneField(BebeConsulta, on_delete=models.CASCADE, null=True, blank=True)
    # Otros campos de Reserva...
    nombre_bebe = models.CharField(max_length=255)
    fecha_nacimiento = models.DateField()
    profesor = models.ForeignKey(Profesor, on_delete=models.CASCADE)
    fecha_reserva = models.DateField()
    hora_reserva = models.TimeField()
    datos_adicionales = models.TextField(blank=True, null=True)
    foto = models.ImageField(upload_to='fotos_bebe/', blank=True, null=True)
    producto = models.ForeignKey(articulos, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    notas_profesor = models.TextField(blank=True, null=True)
    archivo = models.FileField(upload_to='archivos_reservas/', blank=True, null=True)
    completada = models.BooleanField(default=False)  # Nuevo campo para indicar si la consulta fue hecha
    
    class Meta:
        db_table = 'reserva_consultas'
    
    def __str__(self):
        return f'Reserva de {self.nombre_bebe} por {self.usuario} para el {self.fecha_reserva} a las {self.hora_reserva}'
