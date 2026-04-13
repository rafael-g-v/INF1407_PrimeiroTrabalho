from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Perfil, Projeto, Tarefa, Observacao


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
                matricula=self.cleaned_data['matricula'],
            )
        return user


class ProjetoForm(forms.ModelForm):
    class Meta:
        model = Projeto
        fields = ['nome', 'descricao']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
        labels = {
            'nome': 'Nome do Projeto',
            'descricao': 'Descrição',
        }


class MembroChoiceField(forms.ModelChoiceField):
    """Exibe nome completo e matrícula no seletor de responsável."""
    def label_from_instance(self, obj):
        try:
            return f'{obj.perfil.nome} {obj.perfil.sobrenome} ({obj.perfil.matricula})'
        except Exception:
            return obj.email


class TarefaForm(forms.ModelForm):
    responsavel = MembroChoiceField(
        queryset=User.objects.none(),
        required=False,
        label='Responsável',
        empty_label='— Sem responsável —',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    class Meta:
        model = Tarefa
        fields = ['titulo', 'descricao', 'responsavel', 'status', 'prazo']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'prazo': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class ObservacaoForm(forms.ModelForm):
    class Meta:
        model = Observacao
        fields = ['texto']
        labels = {'texto': ''}
        widgets = {
            'texto': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Escreva uma observação...',
            }),
        }


class ConviteForm(forms.Form):
    identificador = forms.CharField(
        max_length=100,
        label='E-mail ou Matrícula',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'autocomplete': 'off',
            'placeholder': 'Digite o e-mail ou matrícula do usuário',
        }),
    )

    def clean_identificador(self):
        identificador = self.cleaned_data.get('identificador')
        try:
            user = User.objects.get(email=identificador)
        except User.DoesNotExist:
            try:
                perfil = Perfil.objects.get(matricula=identificador)
                user = perfil.usuario
            except Perfil.DoesNotExist:
                raise forms.ValidationError('Nenhum usuário encontrado com esse e-mail ou matrícula.')
        # Armazena o objeto para uso na view após a validação
        self._usuario = user
        return identificador