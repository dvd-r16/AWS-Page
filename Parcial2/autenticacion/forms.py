from django import forms  
from captcha.fields import CaptchaField
from django.contrib.auth.models import User  
from django.contrib.auth.forms import UserCreationForm  
from django.core.exceptions import ValidationError  
from usuarios.models import usuarios, Profesor
from usuarios.models import BebeConsulta
from inventario.models import articulos


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(label='Nombre', max_length=150, help_text='Requerido. Introduzca su nombre.')
    last_name = forms.CharField(label='Apellido', max_length=150, help_text='Requerido. Introduzca su apellido.')
    cui = forms.IntegerField(label='DPI', help_text='Código Único de Identificación (DPI)')
    birth_date = forms.DateField(label='Fecha de nacimiento', widget=forms.TextInput(attrs={'type': 'date'}), help_text='Formato: YYYY-MM-DD')
    phone = forms.CharField(label='Teléfono', max_length=20, help_text='Número de teléfono de contacto.')
    email = forms.EmailField(label='Correo electrónico', help_text='Dirección de correo electrónico.')
    profile_image = forms.ImageField(label='Foto de perfil', required=False)
    captcha = CaptchaField()  # Add this line for CAPTCHA

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'cui', 'birth_date', 'phone', 'username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("El email ya está vinculado con otra cuenta, utiliza uno diferente.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("El nombre de usuario ya está en uso, elija uno diferente.")
        return username

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError("Las contraseñas no coinciden.")
        return password2
    
class ProfesorCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput)

    class Meta:
        model = Profesor
        fields = ['nombre', 'apellido', 'dpi']

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return password2

    def save(self, commit=True):
        profesor = super().save(commit=False)
        profesor.set_password(self.cleaned_data["password1"])  # Guarda la contraseña encriptada
        if commit:
            profesor.save()
        return profesor


class BebeConsultaForm(forms.ModelForm):
    producto = forms.ModelChoiceField(
        queryset=articulos.objects.all(), 
        widget=forms.HiddenInput(),  # Esto oculta el campo en el formulario
        required=False  # Para que no sea obligatorio en el formulario
    )
    
    class Meta:
        model = BebeConsulta
        fields = ['nombre', 'fecha_nacimiento', 'sexo', 'peso', 'tipo_sangre', 'foto', 'datos_adicionales']
        widgets = {
            'fecha_nacimiento': forms.TextInput(attrs={'type': 'date'}),
            'sexo': forms.Select(choices=[('Masculino', 'Masculino'), ('Femenino', 'Femenino')]),
            'tipo_sangre': forms.Select(choices=[
                ('A+', 'A+'), ('A-', 'A-'),
                ('B+', 'B+'), ('B-', 'B-'),
                ('AB+', 'AB+'), ('AB-', 'AB-'),
                ('O+', 'O+'), ('O-', 'O-')
            ]),
            'foto': forms.ClearableFileInput(attrs={'class': 'form-control'}),  # Widget personalizado para subir imagen
            'datos_adicionales': forms.Textarea(attrs={'rows': 4}),
        }

