# Gerência de Projetos Acadêmicos

Sistema web para organizar trabalhos em grupo, desenvolvido em Python/Django para a disciplina INF1407 — Programação para Web (2026/1).

**Aluno:** Rafael Gama Vergilio  
**Matrícula:** 2320469

---

## Escopo

Times acadêmicos precisam de um lugar para saber o que precisa ser feito, quem está fazendo, e quando. O sistema permite criar projetos, convidar colegas, criar tarefas com prazo e responsável, e deixar observações em cada tarefa.

Cada usuário vê só o que é seu: os projetos dos quais faz parte, os convites pendentes, e as tarefas dentro de cada projeto. O líder tem controles que um membro comum não tem — editar o projeto, criar e excluir tarefas, remover membros.

### Funcionalidades

- Cadastro e login por e-mail
- Criação de projetos (o criador vira líder automaticamente)
- Convite de membros por e-mail ou matrícula
- Aceitar ou recusar convites direto no dashboard
- CRUD completo de projetos, tarefas e observações
- Controle de acesso por papel: Líder e Membro
- Responsável da tarefa pode atualizar o status sem ser líder
- Qualquer membro do projeto pode adicionar observações nas tarefas

---

## Manual do usuário

### Cadastro e login

Na página inicial, clique em **Começar agora** para criar uma conta. Preencha nome, sobrenome, matrícula (7 dígitos), e-mail e senha. Para entrar, use o e-mail e a senha cadastrados.

### Criando um projeto

No dashboard, clique em **Criar projeto** e preencha o nome e a descrição. Você entra automaticamente como líder.

### Convidando membros

Dentro da página do projeto, clique em **Convidar** na seção da equipe. Digite o e-mail ou a matrícula do colega. O convite aparece no dashboard dele na próxima vez que ele entrar.

### Aceitando convites

Convites pendentes aparecem no topo do dashboard. Clique em **Aceitar** para entrar no projeto ou **Recusar** para ignorar.

### Criando tarefas

Líderes veem o botão **+ Nova tarefa** dentro do projeto. É possível definir título, descrição, responsável (qualquer membro), status e prazo.

### Atualizando o status de uma tarefa

O líder ou o responsável pela tarefa podem alterar o status (Pendente / Em andamento / Concluída) dentro da página da tarefa.

### Observações

Qualquer membro do projeto pode adicionar observações em qualquer tarefa. Cada um pode editar e excluir as próprias; o líder pode excluir qualquer uma.

### Removendo membros

Líderes podem remover membros pela página do projeto clicando em **Remover** ao lado do nome. O próprio líder não pode ser removido.

---

## O que funcionou

- Cadastro e login por e-mail (backend customizado)
- CRUD completo de projetos, tarefas e observações
- Fluxo de convites: envio, aceitação e recusa
- Separação de permissões entre Líder e Membro
- Responsável consegue atualizar status sem ter controle total de líder
- Reenvio de convite para usuário que havia recusado anteriormente

## O que não funcionou / não foi implementado

- "Esqueci a senha": não implementado. A única forma viável de funcionar em produção seria via SMTP com credenciais reais de e-mail, o que exigiria guardar uma senha de app no `.env` do servidor. Optei por não implementar a funcionalidade em vez de deixar algo quebrado ou mal documentado.
- Upload de arquivos anexos nas tarefas
- Histórico de alterações de status
- Transferência de liderança para outro membro

---

## Como rodar localmente

```bash
git clone <url-do-repositório>
cd INF1407_PrimeiroTrabalho
pip install -r requirements.txt
```

Crie um arquivo `.env` na raiz do projeto com:

```
SECRET_KEY=qualquer_string_longa_e_aleatoria
```

Depois:

```bash
python manage.py migrate
python manage.py runserver
```

Acesse `http://127.0.0.1:8000`.

---

## Tecnologias

- Python 3.12 / Django 5.x
- Bootstrap 5.3
- SQLite (desenvolvimento)
- Claude (auxílio no backend)
- DeepSeek (auxílio no front-end)

**Publicado em:** (link do PythonAnywhere)  
**Repositório:** https://github.com/rafael-g-v/INF1407_PrimeiroTrabalho