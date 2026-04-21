from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import Perfil, Projeto, Tarefa, Observacao


class RegistroForm(UserCreationForm):
    """
    Formulário de cadastro de novos usuários com criação automática de Perfil.

    Estende UserCreationForm para incluir e-mail, nome, sobrenome e matrícula.
    O campo ``username`` do Django é preenchido automaticamente com o e-mail.

    Validações extras:
        - E-mail deve ser único na tabela User.
        - Matrícula deve ser única na tabela Perfil.
    """

    email = forms.EmailField(required=True)
    nome = forms.CharField(max_length=100, required=True)
    sobrenome = forms.CharField(max_length=100, required=True)
    matricula = forms.CharField(max_length=20, required=True)

    class Meta:
        model = User
        fields = ('email', 'nome', 'sobrenome', 'matricula', 'password1', 'password2')

    def clean_email(self):
        """
        Garante que o e-mail ainda não está cadastrado.

        Returns:
            str: E-mail válido e disponível.

        Raises:
            ValidationError: Se já existir um User com esse e-mail.
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este e-mail já está cadastrado.')
        return email

    def clean_matricula(self):
        """
        Garante que a matrícula ainda não está cadastrada.

        Returns:
            str: Matrícula válida e disponível.

        Raises:
            ValidationError: Se já existir um Perfil com essa matrícula.
        """
        matricula = self.cleaned_data.get('matricula')
        if Perfil.objects.filter(matricula=matricula).exists():
            raise forms.ValidationError('Esta matrícula já está cadastrada.')
        return matricula

    def save(self, commit=True):
        """
        Salva o User e cria o Perfil vinculado em uma única operação.

        O ``username`` é definido como o e-mail para compatibilidade com
        ``ModelBackend``. O Perfil só é criado se ``commit=True``.

        Args:
            commit (bool): Se True, persiste no banco imediatamente.

        Returns:
            User: Instância do usuário criado.
        """
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
    """Formulário de criação e edição de projetos (nome e descrição)."""

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
    """
    Campo de seleção de usuário que exibe nome completo e matrícula.

    Substitui o label padrão (username) por algo mais legível:
    "Nome Sobrenome (matricula)".
    """

    def label_from_instance(self, obj):
        """
        Formata a opção exibida no <select>.

        Args:
            obj (User): Instância do usuário a ser exibida.

        Returns:
            str: Label no formato "Nome Sobrenome (matricula)", ou e-mail
                como fallback se o Perfil não existir.
        """
        try:
            return f'{obj.perfil.nome} {obj.perfil.sobrenome} ({obj.perfil.matricula})'
        except Exception:
            return obj.email


class TarefaForm(forms.ModelForm):
    """
    Formulário de criação e edição de tarefas.

    O queryset do campo ``responsavel`` começa vazio e deve ser limitado
    aos membros do projeto pela view, via ``_set_responsavel_queryset()``.
    """

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
    """Formulário simples para criação e edição de observações em tarefas."""

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
    """
    Formulário para convidar um usuário por e-mail ou matrícula.

    Após a validação, o atributo ``_usuario`` contém a instância do User
    encontrado, pronto para ser usado na view sem uma segunda consulta ao banco.
    """

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
        """
        Valida o identificador e armazena o usuário encontrado em ``self._usuario``.

        Tenta localizar o usuário primeiro por e-mail, depois por matrícula.

        Returns:
            str: Identificador original (e-mail ou matrícula).

        Raises:
            ValidationError: Se nenhum usuário for encontrado com o identificador.
        """
        identificador = self.cleaned_data.get('identificador')

        try:
            user = User.objects.get(email=identificador)
        except User.DoesNotExist:
            try:
                perfil = Perfil.objects.get(matricula=identificador)
                user = perfil.usuario
            except Perfil.DoesNotExist:
                raise forms.ValidationError(
                    'Nenhum usuário encontrado com esse e-mail ou matrícula.'
                )

        # Armazena o objeto para uso na view após a validação
        self._usuario = user
        return identificador