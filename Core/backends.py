from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from .models import Perfil

User = get_user_model()

class EmailOrMatriculaBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
        try:
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            try:
                perfil = Perfil.objects.get(matricula=username)
                user = perfil.usuario
            except Perfil.DoesNotExist:
                return None
        if user.check_password(password):
            return user
        return None