from django.db import models
from django.contrib.auth.models import User

class Projeto(models.Model):
    nome = models.CharField(max_length=200, verbose_name='Nome')
    descricao = models.TextField(verbose_name='Descrição')
    criado_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projetos_criados', verbose_name='Criado por')
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        verbose_name = 'Projeto'
        verbose_name_plural = 'Projetos'

    def __str__(self):
        return self.nome

class MembroProjeto(models.Model):
    PAPEL_CHOICES = [
        ('L', 'Líder'),
        ('M', 'Membro'),
    ]
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuário')
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE, verbose_name='Projeto')
    papel = models.CharField(max_length=1, choices=PAPEL_CHOICES, default='M', verbose_name='Papel')
    data_entrada = models.DateField(auto_now_add=True, verbose_name='Data de entrada')

    class Meta:
        verbose_name = 'Membro do projeto'
        verbose_name_plural = 'Membros dos projetos'
        unique_together = ('usuario', 'projeto')

    def __str__(self):
        return f'{self.usuario.username} - {self.projeto.nome} ({self.get_papel_display()})'

class Convite(models.Model):
    STATUS_CHOICES = [
        ('P', 'Pendente'),
        ('A', 'Aceito'),
        ('R', 'Recusado'),
    ]
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE, related_name='convites', verbose_name='Projeto')
    convidado_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='convites_enviados', verbose_name='Convidado por')
    convidado = models.ForeignKey(User, on_delete=models.CASCADE, related_name='convites_recebidos', verbose_name='Convidado')
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P', verbose_name='Status')
    data_envio = models.DateTimeField(auto_now_add=True, verbose_name='Data de envio')
    data_resposta = models.DateTimeField(null=True, blank=True, verbose_name='Data de resposta')

    class Meta:
        verbose_name = 'Convite'
        verbose_name_plural = 'Convites'
        unique_together = ('projeto', 'convidado')

    def __str__(self):
        return f'{self.convidado_por.username} convidou {self.convidado.username} para {self.projeto.nome}'

class Tarefa(models.Model):
    STATUS_CHOICES = [
        ('P', 'Pendente'),
        ('E', 'Em andamento'),
        ('C', 'Concluída'),
    ]
    titulo = models.CharField(max_length=200, verbose_name='Título')
    descricao = models.TextField(verbose_name='Descrição')
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE, related_name='tarefas', verbose_name='Projeto')
    responsavel = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tarefas', verbose_name='Responsável')
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P', verbose_name='Status')
    prazo = models.DateField(null=True, blank=True, verbose_name='Prazo')
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        verbose_name = 'Tarefa'
        verbose_name_plural = 'Tarefas'

    def __str__(self):
        return self.titulo

class Observacao(models.Model):
    texto = models.TextField(verbose_name='Texto')
    tarefa = models.ForeignKey(Tarefa, on_delete=models.CASCADE, related_name='observacoes', verbose_name='Tarefa')
    autor = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Autor')
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')

    class Meta:
        verbose_name = 'Observação'
        verbose_name_plural = 'Observações'

    def __str__(self):
        return f'Observação de {self.autor.username} em {self.criado_em.strftime("%d/%m/%Y %H:%M")}'

class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    nome = models.CharField(max_length=100, verbose_name='Nome')
    sobrenome = models.CharField(max_length=100, verbose_name='Sobrenome')
    matricula = models.CharField(max_length=20, unique=True, verbose_name='Matrícula')

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'

    def __str__(self):
        return f'{self.nome} {self.sobrenome}'