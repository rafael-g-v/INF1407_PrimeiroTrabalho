from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone

from .forms import RegistroForm, ProjetoForm, TarefaForm, ObservacaoForm, ConviteForm
from .models import MembroProjeto, Projeto, Tarefa, Observacao, Convite


# ---------- helpers de permissão ----------

def _is_lider(user, projeto):
    """
    Verifica se o usuário é líder do projeto.

    Args:
        user (User): Usuário a verificar.
        projeto (Projeto): Projeto alvo.

    Returns:
        bool: True se o usuário tiver papel 'L' no projeto.
    """
    return MembroProjeto.objects.filter(usuario=user, projeto=projeto, papel='L').exists()


def _is_membro(user, projeto):
    """
    Verifica se o usuário é membro (qualquer papel) do projeto.

    Args:
        user (User): Usuário a verificar.
        projeto (Projeto): Projeto alvo.

    Returns:
        bool: True se existir qualquer MembroProjeto para o par (user, projeto).
    """
    return MembroProjeto.objects.filter(usuario=user, projeto=projeto).exists()


# ---------- autenticação ----------

def home(request):
    """
    Página inicial / dashboard do usuário autenticado.

    Usuários não autenticados veem uma landing page genérica.
    Usuários autenticados veem seus projetos e convites pendentes.

    Args:
        request (HttpRequest): Requisição HTTP.

    Returns:
        HttpResponse: Landing page (home.html) ou dashboard (dashboard.html).
    """
    if request.user.is_authenticated:
        membros = MembroProjeto.objects.filter(usuario=request.user).select_related('projeto')
        projetos = [m.projeto for m in membros]
        convites = (
            Convite.objects
            .filter(convidado=request.user, status='P')
            .select_related('projeto', 'convidado_por__perfil')
        )
        return render(request, 'Core/dashboard.html', {
            'projetos': projetos,
            'convites': convites,
        })
    return render(request, 'Core/home.html')


def login_view(request):
    """
    Processa o formulário de login.

    Args:
        request (HttpRequest): Requisição HTTP.

    Returns:
        HttpResponse: Redireciona para home em caso de sucesso; reexibe
            o formulário com mensagem de erro em caso de falha.
    """
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('Core:home')
        return render(request, 'Core/login.html', {'error': 'E-mail ou matrícula incorretos.'})
    return render(request, 'Core/login.html')


def logout_view(request):
    """
    Encerra a sessão do usuário e redireciona para a home.

    Args:
        request (HttpRequest): Requisição HTTP.

    Returns:
        HttpResponseRedirect: Redireciona para 'Core:home'.
    """
    logout(request)
    return redirect('Core:home')


def register_view(request):
    """
    Exibe e processa o formulário de cadastro de novos usuários.

    Após o cadastro bem-sucedido, autentica e loga o usuário automaticamente,
    redirecionando para o dashboard.

    Args:
        request (HttpRequest): Requisição HTTP.

    Returns:
        HttpResponse: Formulário de registro (registrar.html) ou redirect para home.
    """
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            user = authenticate(request, username=user.email, password=form.cleaned_data['password1'])
            login(request, user)
            return redirect('Core:home')
        return render(request, 'Core/registrar.html', {'form': form})
    return render(request, 'Core/registrar.html', {'form': RegistroForm()})


# ---------- projetos ----------

@login_required
def projeto_criar(request):
    """
    Cria um novo projeto e adiciona o criador como líder automaticamente.

    Args:
        request (HttpRequest): Requisição HTTP.

    Returns:
        HttpResponse: Formulário de criação ou redirect para detalhe do projeto.
    """
    if request.method == 'POST':
        form = ProjetoForm(request.POST)
        if form.is_valid():
            projeto = form.save(commit=False)
            projeto.criado_por = request.user
            projeto.save()
            MembroProjeto.objects.create(usuario=request.user, projeto=projeto, papel='L')
            return redirect('Core:projeto_detalhe', pk=projeto.pk)
    else:
        form = ProjetoForm()
    return render(request, 'Core/projeto_form.html', {'form': form, 'acao': 'Criar'})


@login_required
def projeto_detalhe(request, pk):
    """
    Exibe os detalhes de um projeto: membros, tarefas e convites pendentes.

    Redireciona para home se o usuário não for membro do projeto.

    Args:
        request (HttpRequest): Requisição HTTP.
        pk (int): Chave primária do projeto.

    Returns:
        HttpResponse: Página de detalhe (projeto_detalhe.html) ou redirect.
    """
    projeto = get_object_or_404(Projeto, pk=pk)
    if not _is_membro(request.user, projeto):
        return redirect('Core:home')
    lider = _is_lider(request.user, projeto)
    membros = MembroProjeto.objects.filter(projeto=projeto).select_related('usuario__perfil')
    tarefas = Tarefa.objects.filter(projeto=projeto).select_related('responsavel__perfil')
    convites_pendentes = (
        Convite.objects
        .filter(projeto=projeto, status='P')
        .select_related('convidado__perfil')
    )
    return render(request, 'Core/projeto_detalhe.html', {
        'projeto': projeto,
        'lider': lider,
        'membros': membros,
        'tarefas': tarefas,
        'convites_pendentes': convites_pendentes,
    })


@login_required
def projeto_editar(request, pk):
    """
    Permite ao líder editar nome e descrição de um projeto.

    Membros comuns são redirecionados para o detalhe do projeto.

    Args:
        request (HttpRequest): Requisição HTTP.
        pk (int): Chave primária do projeto.

    Returns:
        HttpResponse: Formulário de edição ou redirect.
    """
    projeto = get_object_or_404(Projeto, pk=pk)
    if not _is_lider(request.user, projeto):
        return redirect('Core:projeto_detalhe', pk=pk)
    if request.method == 'POST':
        form = ProjetoForm(request.POST, instance=projeto)
        if form.is_valid():
            form.save()
            return redirect('Core:projeto_detalhe', pk=pk)
    else:
        form = ProjetoForm(instance=projeto)
    return render(request, 'Core/projeto_form.html', {
        'form': form,
        'acao': 'Editar',
        'projeto': projeto,
    })


@login_required
def projeto_deletar(request, pk):
    """
    Permite ao líder excluir um projeto após confirmação.

    GET exibe a tela de confirmação; POST executa a exclusão.

    Args:
        request (HttpRequest): Requisição HTTP.
        pk (int): Chave primária do projeto.

    Returns:
        HttpResponse: Tela de confirmação ou redirect para home após exclusão.
    """
    projeto = get_object_or_404(Projeto, pk=pk)
    if not _is_lider(request.user, projeto):
        return redirect('Core:projeto_detalhe', pk=pk)
    if request.method == 'POST':
        projeto.delete()
        return redirect('Core:home')
    return render(request, 'Core/projeto_confirmar_delete.html', {'projeto': projeto})


# ---------- membros e convites ----------

@login_required
def convite_enviar(request, pk):
    """
    Envia um convite para um usuário entrar no projeto.

    Apenas líderes podem convidar. Se o usuário já for membro, exibe erro.
    Se houver convite recusado anteriormente, reusa o registro e redefine
    o status para Pendente, em vez de criar um novo registro.

    Args:
        request (HttpRequest): Requisição HTTP.
        pk (int): Chave primária do projeto.

    Returns:
        HttpResponse: Formulário de convite ou redirect para detalhe do projeto.
    """
    projeto = get_object_or_404(Projeto, pk=pk)
    if not _is_lider(request.user, projeto):
        return redirect('Core:projeto_detalhe', pk=pk)
    if request.method == 'POST':
        form = ConviteForm(request.POST)
        if form.is_valid():
            usuario = form._usuario
            if _is_membro(usuario, projeto):
                form.add_error('identificador', 'Este usuário já é membro do projeto.')
            else:
                existente = Convite.objects.filter(projeto=projeto, convidado=usuario).first()
                if existente:
                    if existente.status == 'P':
                        form.add_error('identificador', 'Este usuário já tem um convite pendente.')
                    else:
                        # Reenvio: reutiliza o registro existente
                        existente.status = 'P'
                        existente.convidado_por = request.user
                        existente.data_resposta = None
                        existente.save()
                        return redirect('Core:projeto_detalhe', pk=pk)
                else:
                    Convite.objects.create(
                        projeto=projeto,
                        convidado_por=request.user,
                        convidado=usuario,
                    )
                    return redirect('Core:projeto_detalhe', pk=pk)
    else:
        form = ConviteForm()
    return render(request, 'Core/convite_enviar.html', {'form': form, 'projeto': projeto})


@login_required
def convite_responder(request, pk):
    """
    Processa a resposta do usuário a um convite (aceitar ou recusar).

    Ao aceitar, cria o MembroProjeto com papel 'M'.
    Ao recusar, apenas atualiza o status do convite.
    Em ambos os casos, registra o timestamp da resposta.

    Args:
        request (HttpRequest): Requisição HTTP.
        pk (int): Chave primária do Convite.

    Returns:
        HttpResponseRedirect: Redireciona sempre para o dashboard (home).
    """
    convite = get_object_or_404(Convite, pk=pk, convidado=request.user, status='P')
    if request.method == 'POST':
        resposta = request.POST.get('resposta')
        if resposta == 'aceitar':
            convite.status = 'A'
            convite.data_resposta = timezone.now()
            convite.save()
            MembroProjeto.objects.get_or_create(
                usuario=request.user,
                projeto=convite.projeto,
                defaults={'papel': 'M'},
            )
        elif resposta == 'recusar':
            convite.status = 'R'
            convite.data_resposta = timezone.now()
            convite.save()
    return redirect('Core:home')


@login_required
def membro_remover(request, pk, usuario_pk):
    """
    Remove um membro do projeto (somente líderes podem remover).

    O próprio líder não pode ser removido — a view ignora silenciosamente
    qualquer tentativa de remover um membro com papel 'L'.

    Args:
        request (HttpRequest): Requisição HTTP.
        pk (int): Chave primária do projeto.
        usuario_pk (int): Chave primária do usuário a ser removido.

    Returns:
        HttpResponse: Tela de confirmação ou redirect.
    """
    projeto = get_object_or_404(Projeto, pk=pk)
    if not _is_lider(request.user, projeto):
        return redirect('Core:projeto_detalhe', pk=pk)
    membro = get_object_or_404(MembroProjeto, projeto=projeto, usuario__pk=usuario_pk)
    if membro.papel == 'L':
        return redirect('Core:projeto_detalhe', pk=pk)
    if request.method == 'POST':
        membro.delete()
        return redirect('Core:projeto_detalhe', pk=pk)
    return render(request, 'Core/membro_confirmar_remover.html', {
        'projeto': projeto,
        'membro': membro,
    })


# ---------- tarefas ----------

def _set_responsavel_queryset(form, projeto):
    """
    Restringe o campo ``responsavel`` do TarefaForm aos membros do projeto.

    Deve ser chamada sempre que TarefaForm for instanciado em uma view,
    pois o queryset padrão começa vazio por segurança.

    Args:
        form (TarefaForm): Instância do formulário a ser ajustada.
        projeto (Projeto): Projeto cujos membros serão listados no campo.
    """
    ids = MembroProjeto.objects.filter(projeto=projeto).values_list('usuario_id', flat=True)
    form.fields['responsavel'].queryset = User.objects.filter(id__in=ids)


@login_required
def tarefa_criar(request, projeto_pk):
    """
    Cria uma nova tarefa dentro de um projeto (somente líderes).

    Args:
        request (HttpRequest): Requisição HTTP.
        projeto_pk (int): Chave primária do projeto.

    Returns:
        HttpResponse: Formulário de criação ou redirect para detalhe do projeto.
    """
    projeto = get_object_or_404(Projeto, pk=projeto_pk)
    if not _is_lider(request.user, projeto):
        return redirect('Core:projeto_detalhe', pk=projeto_pk)
    form = TarefaForm(request.POST or None)
    _set_responsavel_queryset(form, projeto)
    if request.method == 'POST' and form.is_valid():
        tarefa = form.save(commit=False)
        tarefa.projeto = projeto
        tarefa.save()
        return redirect('Core:projeto_detalhe', pk=projeto_pk)
    return render(request, 'Core/tarefa_form.html', {
        'form': form,
        'projeto': projeto,
        'acao': 'Criar',
    })


@login_required
def tarefa_detalhe(request, pk):
    """
    Exibe os detalhes de uma tarefa, incluindo suas observações.

    Redireciona para home se o usuário não for membro do projeto.
    Passa flags ``lider`` e ``eh_responsavel`` para controlar o que o template exibe.

    Args:
        request (HttpRequest): Requisição HTTP.
        pk (int): Chave primária da tarefa.

    Returns:
        HttpResponse: Página de detalhe da tarefa (tarefa_detalhe.html).
    """
    tarefa = get_object_or_404(Tarefa, pk=pk)
    if not _is_membro(request.user, tarefa.projeto):
        return redirect('Core:home')
    observacoes = Observacao.objects.filter(tarefa=tarefa).select_related('autor__perfil')
    return render(request, 'Core/tarefa_detalhe.html', {
        'tarefa': tarefa,
        'lider': _is_lider(request.user, tarefa.projeto),
        'eh_responsavel': tarefa.responsavel == request.user,
        'observacoes': observacoes,
        'form_obs': ObservacaoForm(),
        'status_choices': Tarefa.STATUS_CHOICES,
    })


@login_required
def tarefa_editar(request, pk):
    """
    Permite ao líder editar os dados de uma tarefa existente.

    Args:
        request (HttpRequest): Requisição HTTP.
        pk (int): Chave primária da tarefa.

    Returns:
        HttpResponse: Formulário de edição ou redirect para detalhe da tarefa.
    """
    tarefa = get_object_or_404(Tarefa, pk=pk)
    if not _is_lider(request.user, tarefa.projeto):
        return redirect('Core:tarefa_detalhe', pk=pk)
    form = TarefaForm(request.POST or None, instance=tarefa)
    _set_responsavel_queryset(form, tarefa.projeto)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('Core:tarefa_detalhe', pk=pk)
    return render(request, 'Core/tarefa_form.html', {
        'form': form,
        'projeto': tarefa.projeto,
        'tarefa': tarefa,
        'acao': 'Editar',
    })


@login_required
def tarefa_deletar(request, pk):
    """
    Permite ao líder excluir uma tarefa após confirmação.

    GET exibe tela de confirmação; POST executa a exclusão e redireciona
    para o detalhe do projeto.

    Args:
        request (HttpRequest): Requisição HTTP.
        pk (int): Chave primária da tarefa.

    Returns:
        HttpResponse: Tela de confirmação ou redirect para detalhe do projeto.
    """
    tarefa = get_object_or_404(Tarefa, pk=pk)
    if not _is_lider(request.user, tarefa.projeto):
        return redirect('Core:tarefa_detalhe', pk=pk)
    projeto_pk = tarefa.projeto.pk
    if request.method == 'POST':
        tarefa.delete()
        return redirect('Core:projeto_detalhe', pk=projeto_pk)
    return render(request, 'Core/tarefa_confirmar_delete.html', {'tarefa': tarefa})


@login_required
def tarefa_status(request, pk):
    """
    Atualiza somente o status de uma tarefa.

    Acessível ao responsável pela tarefa e ao líder do projeto.
    Membros sem nenhum desses papéis são ignorados silenciosamente.

    Args:
        request (HttpRequest): Requisição HTTP.
        pk (int): Chave primária da tarefa.

    Returns:
        HttpResponseRedirect: Redireciona sempre para o detalhe da tarefa.
    """
    tarefa = get_object_or_404(Tarefa, pk=pk)
    if not _is_membro(request.user, tarefa.projeto):
        return redirect('Core:home')
    pode_alterar = _is_lider(request.user, tarefa.projeto) or tarefa.responsavel == request.user
    if request.method == 'POST' and pode_alterar:
        novo = request.POST.get('status')
        if novo in [s[0] for s in Tarefa.STATUS_CHOICES]:
            tarefa.status = novo
            tarefa.save()
    return redirect('Core:tarefa_detalhe', pk=pk)


# ---------- observações ----------

@login_required
def observacao_criar(request, tarefa_pk):
    """
    Adiciona uma observação a uma tarefa.

    Qualquer membro do projeto pode criar observações. O autor é definido
    automaticamente como o usuário logado.

    Args:
        request (HttpRequest): Requisição HTTP.
        tarefa_pk (int): Chave primária da tarefa.

    Returns:
        HttpResponseRedirect: Redireciona para o detalhe da tarefa.
    """
    tarefa = get_object_or_404(Tarefa, pk=tarefa_pk)
    if not _is_membro(request.user, tarefa.projeto):
        return redirect('Core:home')
    if request.method == 'POST':
        form = ObservacaoForm(request.POST)
        if form.is_valid():
            obs = form.save(commit=False)
            obs.tarefa = tarefa
            obs.autor = request.user
            obs.save()
    return redirect('Core:tarefa_detalhe', pk=tarefa_pk)


@login_required
def observacao_editar(request, pk):
    """
    Edita uma observação existente.

    Permitido ao autor da observação ou ao líder do projeto.

    Args:
        request (HttpRequest): Requisição HTTP.
        pk (int): Chave primária da observação.

    Returns:
        HttpResponse: Formulário de edição ou redirect.
    """
    obs = get_object_or_404(Observacao, pk=pk)
    if obs.autor != request.user and not _is_lider(request.user, obs.tarefa.projeto):
        return redirect('Core:tarefa_detalhe', pk=obs.tarefa.pk)
    if request.method == 'POST':
        form = ObservacaoForm(request.POST, instance=obs)
        if form.is_valid():
            form.save()
            return redirect('Core:tarefa_detalhe', pk=obs.tarefa.pk)
    else:
        form = ObservacaoForm(instance=obs)
    return render(request, 'Core/observacao_form.html', {'form': form, 'obs': obs})


@login_required
def observacao_deletar(request, pk):
    """
    Exclui uma observação após confirmação.

    Permitido ao autor ou ao líder. GET exibe confirmação; POST executa a exclusão.

    Args:
        request (HttpRequest): Requisição HTTP.
        pk (int): Chave primária da observação.

    Returns:
        HttpResponse: Tela de confirmação ou redirect para detalhe da tarefa.
    """
    obs = get_object_or_404(Observacao, pk=pk)
    tarefa_pk = obs.tarefa.pk
    if obs.autor != request.user and not _is_lider(request.user, obs.tarefa.projeto):
        return redirect('Core:tarefa_detalhe', pk=tarefa_pk)
    if request.method == 'POST':
        obs.delete()
        return redirect('Core:tarefa_detalhe', pk=tarefa_pk)
    return render(request, 'Core/observacao_confirmar_delete.html', {'obs': obs})