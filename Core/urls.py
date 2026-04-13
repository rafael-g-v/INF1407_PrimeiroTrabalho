from django.urls import path
from Core import views

app_name = 'Core'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registrar/', views.register_view, name='registrar'),

    # Projetos
    path('projetos/criar/', views.projeto_criar, name='projeto_criar'),
    path('projetos/<int:pk>/', views.projeto_detalhe, name='projeto_detalhe'),
    path('projetos/<int:pk>/editar/', views.projeto_editar, name='projeto_editar'),
    path('projetos/<int:pk>/deletar/', views.projeto_deletar, name='projeto_deletar'),

    # Membros e convites
    path('projetos/<int:pk>/convidar/', views.convite_enviar, name='convite_enviar'),
    path('projetos/<int:pk>/membros/<int:usuario_pk>/remover/', views.membro_remover, name='membro_remover'),
    path('convites/<int:pk>/responder/', views.convite_responder, name='convite_responder'),

    # Tarefas
    path('projetos/<int:projeto_pk>/tarefas/criar/', views.tarefa_criar, name='tarefa_criar'),
    path('tarefas/<int:pk>/', views.tarefa_detalhe, name='tarefa_detalhe'),
    path('tarefas/<int:pk>/editar/', views.tarefa_editar, name='tarefa_editar'),
    path('tarefas/<int:pk>/deletar/', views.tarefa_deletar, name='tarefa_deletar'),
    path('tarefas/<int:pk>/status/', views.tarefa_status, name='tarefa_status'),

    # Observações
    path('tarefas/<int:tarefa_pk>/observacoes/criar/', views.observacao_criar, name='observacao_criar'),
    path('observacoes/<int:pk>/editar/', views.observacao_editar, name='observacao_editar'),
    path('observacoes/<int:pk>/deletar/', views.observacao_deletar, name='observacao_deletar'),
]