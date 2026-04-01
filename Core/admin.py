from django.contrib import admin
from .models import Projeto, MembroProjeto, Convite, Tarefa, Observacao

admin.site.register(Projeto)
admin.site.register(MembroProjeto)
admin.site.register(Convite)
admin.site.register(Tarefa)
admin.site.register(Observacao)