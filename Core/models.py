from django.db import models
from django.contrib.auth.models import User


class Projeto(models.Model):
    """
    Representa um projeto acadêmico em equipe.

    Cada projeto tem um criador (que se torna líder automaticamente)
    e pode ter múltiplos membros, tarefas e convites associados.

    Attributes:
        nome (str): Nome do projeto. Máx. 200 caracteres.
        descricao (str): Descrição livre do projeto.
        criado_por (User): Usuário que criou o projeto; vira líder automático.
        criado_em (datetime): Timestamp de criação, preenchido automaticamente.
        atualizado_em (datetime): Timestamp da última atualização, atualizado automaticamente.
    """

    nome = models.CharField(max_length=200, verbose_name='Nome')
    descricao = models.TextField(verbose_name='Descrição')
    criado_por = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='projetos_criados',
        verbose_name='Criado por',
    )
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        verbose_name = 'Projeto'
        verbose_name_plural = 'Projetos'

    def __str__(self):
        return self.nome


class MembroProjeto(models.Model):
    """
    Associação entre um usuário e um projeto.

    Um usuário pode ser Líder ('L') ou Membro ('M') de um projeto.
    A combinação (usuario, projeto) é única — ninguém pode aparecer duas vezes
    no mesmo projeto.

    Attributes:
        usuario (User): Usuário participante.
        projeto (Projeto): Projeto ao qual o usuário pertence.
        papel (str): 'L' para Líder, 'M' para Membro.
        data_entrada (date): Data de entrada no projeto, preenchida automaticamente.
    """

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
    """
    Convite enviado por um líder para um usuário entrar em um projeto.

    Um convite pode ser aceito, recusado ou estar pendente. Caso um convite
    recusado seja reenviado, o registro existente é reutilizado (status volta
    para 'P'), evitando repetir na tabela.

    Attributes:
        projeto (Projeto): Projeto para o qual o convite foi enviado.
        convidado_por (User): Líder que enviou o convite.
        convidado (User): Usuário que recebeu o convite.
        status (str): 'P' Pendente | 'A' Aceito | 'R' Recusado.
        data_envio (datetime): Timestamp de envio, preenchido automaticamente.
        data_resposta (datetime): Timestamp da resposta; nulo enquanto pendente.
    """

    STATUS_CHOICES = [
        ('P', 'Pendente'),
        ('A', 'Aceito'),
        ('R', 'Recusado'),
    ]

    projeto = models.ForeignKey(
        Projeto, on_delete=models.CASCADE, related_name='convites', verbose_name='Projeto'
    )
    convidado_por = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='convites_enviados', verbose_name='Convidado por'
    )
    convidado = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='convites_recebidos', verbose_name='Convidado'
    )
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
    """
    Tarefa dentro de um projeto, podendo ter um responsável e um prazo.

    O responsável pode atualizar o status sem precisar ser líder.
    Quando o responsável é removido do projeto, o campo vira NULL
    (on_delete = SET_NULL) para não perder o histórico da tarefa.

    Attributes:
        titulo (str): Título curto da tarefa.
        descricao (str): Detalhamento da tarefa.
        projeto (Projeto): Projeto ao qual a tarefa pertence.
        responsavel (User | None): Membro responsável; pode ser nulo.
        status (str): 'P' Pendente | 'E' Em andamento | 'C' Concluída.
        prazo (date | None): Data limite de conclusão; opcional.
        criado_em (datetime): Timestamp de criação.
        atualizado_em (datetime): Timestamp da última edição.
    """

    STATUS_CHOICES = [
        ('P', 'Pendente'),
        ('E', 'Em andamento'),
        ('C', 'Concluída'),
    ]

    titulo = models.CharField(max_length=200, verbose_name='Título')
    descricao = models.TextField(verbose_name='Descrição')
    projeto = models.ForeignKey(
        Projeto, on_delete=models.CASCADE, related_name='tarefas', verbose_name='Projeto'
    )
    responsavel = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tarefas',
        verbose_name='Responsável',
    )
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
    """
    Comentário de um membro sobre uma tarefa específica.

    Qualquer membro do projeto pode criar observações. Cada um pode editar
    e excluir as próprias e o líder pode excluir qualquer uma.

    Attributes:
        texto (str): Conteúdo da observação.
        tarefa (Tarefa): Tarefa à qual a observação pertence.
        autor (User): Usuário que escreveu a observação.
        criado_em (datetime): Timestamp de criação.
    """

    texto = models.TextField(verbose_name='Texto')
    tarefa = models.ForeignKey(
        Tarefa, on_delete=models.CASCADE, related_name='observacoes', verbose_name='Tarefa'
    )
    autor = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Autor')
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')

    class Meta:
        verbose_name = 'Observação'
        verbose_name_plural = 'Observações'

    def __str__(self):
        return f'Observação de {self.autor.username} em {self.criado_em.strftime("%d/%m/%Y %H:%M")}'


class Perfil(models.Model):
    """
    Extensão do modelo User padrão do Django com dados acadêmicos.

    A relação 1 pra 1 garante que cada usuário tem exatamente um perfil.

    Attributes:
        usuario (User): Usuário Django associado (1-para-1).
        nome (str): Primeiro nome do usuário.
        sobrenome (str): Sobrenome do usuário.
        matricula (str): Número de matrícula acadêmica; único no sistema.
    """

    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    nome = models.CharField(max_length=100, verbose_name='Nome')
    sobrenome = models.CharField(max_length=100, verbose_name='Sobrenome')
    matricula = models.CharField(max_length=20, unique=True, verbose_name='Matrícula')

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'

    def __str__(self):
        return f'{self.nome} {self.sobrenome}'