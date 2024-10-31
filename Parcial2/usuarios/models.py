from email.policy import default
from statistics import mode
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
User = get_user_model()

# Create your models here.

class usuarios(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    username = models.CharField(max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField()
    cui = models.BigIntegerField()  # Cambia a BigIntegerField
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    login_attempts = models.BigIntegerField(default=0)
    birth_date = models.DateField(null=True, blank=True)  # Agrega este campo
    phone = models.CharField(max_length=20, null=True, blank=True)  # Agrega este campo

    def __str__(self):
        return self.user.username

    class Meta:
        db_table = 'usuarios_info'
        verbose_name='Cliente'
        verbose_name_plural = 'Clientes'
        ordering=['id']

class Profesor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    dpi = models.CharField(max_length=13, unique=True)  # DPI único para identificación
    telefono = models.CharField(max_length=15)  # Campo de teléfono
    password = models.CharField(max_length=128)  # Contraseña encriptada
    password_confirmation = models.CharField(max_length=128)  # Confirmación de contraseña
    especialidad = models.CharField(max_length=100, null=True, blank=True)  # Nueva especialidad
    foto_perfil = models.ImageField(upload_to='profesores/', null=True, blank=True)  # Nueva foto de perfil

    def __str__(self):
        return f'{self.nombre} {self.apellido}'

    class Meta:
        db_table = 'profesores_info'
        verbose_name = 'Doctor'
        verbose_name_plural = 'Doctores'
        ordering = ['apellido', 'nombre']

class BebeConsulta(models.Model):
    nombre = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    sexo = models.CharField(max_length=10, choices=[('Masculino', 'Masculino'), ('Femenino', 'Femenino')])
    peso = models.DecimalField(max_digits=5, decimal_places=2)
    tipo_sangre = models.CharField(max_length=3, choices=[
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-')
    ])
    foto = models.ImageField(upload_to='fotos_bebes/', blank=True, null=True)
    datos_adicionales = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre
    