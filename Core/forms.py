from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Perfil

class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)
    nome = forms.CharField(max_length=100, required=True)
    sobrenome = forms.CharField(max_length=100, required=True)
    matricula = forms.CharField(max_length=20, required=True)

    class Meta:
        model = User
        fields = ('email', 'nome', 'sobrenome', 'matricula', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este e-mail já está cadastrado.')
        return email

    def clean_matricula(self):
        matricula = self.cleaned_data.get('matricula')
        if Perfil.objects.filter(matricula=matricula).exists():
            raise forms.ValidationError('Esta matrícula já está cadastrada.')
        return matricula

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            Perfil.objects.create(
                usuario=user,
                nome=self.cleaned_data['nome'],
                sobrenome=self.cleaned_data['sobrenome'],
                matricula=self.cleaned_data['matricula']
            )
        return user