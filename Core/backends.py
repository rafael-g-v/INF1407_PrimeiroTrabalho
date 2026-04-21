from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

from .models import Perfil

User = get_user_model()


class EmailOrMatriculaBackend(ModelBackend):
    """
    Backend de autenticação que aceita e-mail ou matrícula no lugar do username.

    O Django chama ``authenticate()`` com o campo "username" do formulário de login.
    Este backend tenta primeiro localizar o usuário pelo e-mail; se não encontrar,
    tenta pela matrícula via tabela Perfil. Caso nenhum dos dois funcione, retorna
    None e o Django passa para o próximo backend configurado em AUTHENTICATION_BACKENDS.

    Registre este backend em settings.py ANTES do ModelBackend padrão para que ele
    seja tentado primeiro:

        AUTHENTICATION_BACKENDS = [
            'Core.backends.EmailOrMatriculaBackend',
            'django.contrib.auth.backends.ModelBackend',
        ]
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Args:
            request (HttpRequest): Requisição HTTP atual.
            username (str | None): Valor digitado no campo de login
                (pode ser e-mail ou matrícula).
            password (str | None): Senha em texto claro para verificação.
            **kwargs: Argumentos adicionais ignorados por este backend.

        Returns:
            User: Instância do usuário autenticado, se credenciais forem válidas.
            None: Se o usuário não for encontrado ou a senha estiver errada.
        """
        if username is None or password is None:
            return None

        # Tenta localizar por e-mail primeiro
        try:
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            # Se não achar por e-mail, tenta pela matrícula
            try:
                perfil = Perfil.objects.get(matricula=username)
                user = perfil.usuario
            except Perfil.DoesNotExist:
                return None

        if user.check_password(password):
            return user
        return None