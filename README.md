Sistema web para organizar trabalhos em grupo, desenvolvido em Python/Django como primeiro trabalho da disciplina INF1407 — Programação para Web (2026/1).

**Aluno:** Rafael Gama Vergilio 
**Matrícula:** 2320469

---
A ideia é simples: times acadêmicos precisam de um lugar para organizar o que precisa ser feito, quem está fazendo, e quando. O sistema permite criar projetos, convidar colegas, criar tarefas com prazo e responsável, e deixar observações em cada tarefa.

Cada usuário vê só o que é seu: os projetos dos quais faz parte, os convites que recebeu, e as tarefas do projeto. Um líder de projeto tem controles que um membro comum não tem — editar o projeto, criar e excluir tarefas, remover membros.

### Funcionalidades implementadas
- Cadastro e login por e-mail ou matrícula
- Criação de projetos (quem cria vira líder automaticamente)
- Convite de membros por e-mail ou matrícula
- Aceitar ou recusar convites direto no dashboard
- CRUD completo de projetos, tarefas e observações
- Controle de acesso por papel: Líder e Membro
- Responsável da tarefa pode atualizar o status sem precisar ser líder
- Qualquer membro do projeto pode adicionar observações nas tarefas

---

## Como usar

### Cadastro e login

Acesse a página inicial e clique em **Começar agora** para **criar** uma conta. Preencha nome, sobrenome, matrícula única (7 dígitos), e-mail e senha. Para entrar, use o e-mail ou a matrícula junto com a senha.

### Criando um projeto

No dashboard, clique em **Criar projeto**, preencha o nome e a descrição. Você vira líder do projeto automaticamente.

### Convidando membros

Dentro do projeto, clique em **Convidar** na seção da equipe. Digite o e-mail ou a matrícula do colega. Ele vai receber o convite no dashboard na próxima vez que entrar, já que não há JS pra notificar dinamicamente.

### Aceitando convites

Convites pendentes aparecem no topo do dashboard. Clique em **Aceitar** para entrar no projeto ou **Recusar** para ignorar.

### Criando tarefas

Líderes veem o botão **+ Nova tarefa** dentro do projeto. Dá para definir título, descrição, responsável (qualquer membro), status e prazo.

### Atualizando o status de uma tarefa

Qualquer líder ou o responsável pela tarefa pode alterar o status (Pendente / Em andamento / Concluída) dentro da página da tarefa.

### Observações

Qualquer membro do projeto pode adicionar observações em qualquer tarefa. Cada um pode editar e excluir as próprias observações; o líder pode excluir qualquer uma.

### Removendo membros

Líderes podem remover membros pela página do projeto, clicando em **Remover** ao lado do nome. O líder em si não pode ser removido.

---

## O que funcionou
- Cadastro e login por e-mail e matrícula (backend customizado)
- Todas as operações de CRUD para projetos, tarefas e observações
- Fluxo de convites: envio, aceitação e recusa
- Separação de permissões entre Líder e Membro
- Responsável consegue atualizar status sem ter controle total
- Navegação por breadcrumbs em todas as páginas internas
- Reenvio de convite para usuário que tinha recusado anteriormente

## O que não funcionou / não foi implementado
- Upload de arquivos anexos nas tarefas
- Histórico de alterações de status
- Transferência de liderança do projeto para outro membro

---

## Como rodar localmente

```bash
git clone <url-do-repositório>
cd INF1407_PrimeiroTrabalho
pip install -r requirements.txt

# crie um arquivo .env com:
# SECRET_KEY=sua_chave_secreta (importante, mas eu errei na hora de subir então dá pra ver a minha no histórico de commits 😅)

python manage.py migrate
python manage.py runserver
```

Acesse `http://127.0.0.1:8000` no navegador.

---

## Tecnologias
- Python 3.12 / Django 5.x
- Bootstrap 5.3
- SQLite (desenvolvimento)
- Claude (auxílio no backend)
- Deepseek (auxílio no front-end)
- Publicado em:
- Repositório:
