# Autenticação (F1) — Tasks

## Execution Protocol (MANDATORY -- do not skip)

Implement these tasks with the `tlc-spec-driven` skill: **activate it by name and follow its Execute flow and Critical Rules.** Do not search for skill files by filesystem path. The skill is the source of truth for the full flow (per-task cycle, sub-agent delegation, adequacy review, Verifier, discrimination sensor).

**If the skill cannot be activated, STOP and tell the user - do not proceed without it.**

---

**Spec**: `.specs/features/autenticacao/spec.md`
**Design**: `.specs/features/autenticacao/design.md`
**Status**: In Progress

**Stack fixado**: Django 5.2 LTS · PostgreSQL 16 (AD-003) · pytest + pytest-django · Ruff

---

## Test Coverage Matrix

> Gerada a partir do código, das diretrizes do projeto e da spec — confirmar antes do Execute.
> **Guidelines encontradas: nenhuma.** Não existe `AGENTS.md`, `CONTRIBUTING.md`, config de runner
> nem workflow de CI neste repositório — só `docs/` (requisitos, features, UML) e `.specs/`. Sem
> guideline aplicável, valem os **strong defaults**: toda AC da spec e todo edge case listado têm
> teste; lógica de domínio mapeia 1:1 para as ACs; rotas cobrem happy + edge + erro. O stack de
> testes foi definido pelo usuário (não havia teste algum para amostrar).

| Code Layer | Required Test Type | Coverage Expectation | Location Pattern | Run Command |
| ---------- | ------------------ | -------------------- | ---------------- | ----------- |
| Modelo de domínio (`contas/models.py`) | unit | Todos os ramos; 1:1 com as ACs de perfil (AUTH-16, 17, 19, 20); nenhum acesso a banco | `contas/tests/test_models.py` | `pytest -q -m unit` |
| Constraints de banco (`Meta.constraints`) | integration | Cada constraint com um caso que a viola e um que a respeita (AUTH-18, AUTH-25) | `contas/tests/test_constraints.py` | `pytest -q` |
| Authentication backend (`contas/backends.py`) | integration | Happy por username, happy por e-mail, caixa alternada, inexistente, senha errada, conta inativa (AUTH-01, 02, 23) | `contas/tests/test_backends.py` | `pytest -q` |
| Formulário (`contas/forms.py`) | unit | Mensagem única, campos obrigatórios, repopulação do identificador (AUTH-03, AUTH-04) | `contas/tests/test_forms.py` | `pytest -q -m unit` |
| Views e rotas (`contas/views.py`, `nucleo/views.py`) | e2e | Toda rota que a task adiciona: happy + todo edge case listado + caminho de erro | `contas/tests/test_views_*.py` | `pytest -q` |
| Controle de acesso (middleware + settings) | e2e | Varredura de todas as rotas registradas + `next` + já autenticado + sessão expirada (AUTH-09 a AUTH-12, AUTH-15) | `contas/tests/test_controle_acesso.py` | `pytest -q` |
| Admin (`contas/admin.py`) | e2e | Cada perfil × cada operação sobre `perfil` (AUTH-21, AUTH-22) | `contas/tests/test_admin.py` | `pytest -q` |
| Sinais (`contas/signals.py`) | unit | Emissão do log com identificador e ausência da senha (AUTH-08, AUTH-27) | `contas/tests/test_signals.py` | `pytest -q -m unit` |
| Configuração, templates, migrations | none | — (apenas gate de build) | — | build gate only |

## Gate Check Commands

> Gerados a partir do stack escolhido — confirmar antes do Execute. O marcador `unit` é registrado
> no `pyproject.toml` pela T3; testes sem ele tocam o banco e só rodam no gate full.

| Gate Level | When to Use | Command |
| ---------- | ----------- | ------- |
| Quick | Depois de tasks só com teste unitário | `pytest -q -m unit` |
| Full | Depois de tasks com teste de integração ou e2e | `pytest -q` |
| Build | Ao fechar uma fase, e em tasks de config/migration/template | `ruff check . && ruff format --check . && python manage.py makemigrations --check --dry-run && pytest -q` |

---

## Execution Plan

As fases são ordenadas e rodam em sequência — cada fase termina antes de a próxima começar, e as tasks dentro de uma fase executam em ordem.

### Phase 1: Fundação do projeto

Esqueleto, dependências e ferramentas. Nada de modelo ainda.

```
T1 → T2 → T3 → T4
```

### Phase 2: Modelo de usuário

Precisa vir antes de qualquer migration de qualquer app (AD-005).

```
T5 → T6 → T7 → T8 → T9 → T10 → T11
```

### Phase 3: Autenticação

Backend de credencial, formulário, telas de entrada e saída.

```
T12 → T13 → T14 → T15 → T16 → T17 → T18
```

### Phase 4: Controle de acesso

Negação por padrão (AD-006) e ciclo de vida da sessão.

```
T19 → T20 → T21 → T22
```

### Phase 5: Perfil e curadoria no admin

A RN11 virando comportamento observável.

```
T23 → T24 → T25
```

---

## Task Breakdown

### T1: Fixar as dependências do projeto ✅

**What**: Declarar as dependências com versões fixadas, incluindo Django 5.2 LTS.
**Where**: `requirements.txt`
**Depends on**: None
**Reuses**: Nada — primeiro arquivo do projeto.
**Requirement**: AD-003, AD-005 (pré-requisito de infraestrutura)

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `Django>=5.2,<5.3` fixado (LTS; `LoginRequiredMiddleware` exige ≥ 5.1)
- [x] `psycopg[binary]`, `python-dotenv` presentes
- [x] `pytest`, `pytest-django`, `ruff` presentes
- [x] `pip install -r requirements.txt` completa sem conflito

**Tests**: none
**Gate**: build

**Commit**: `chore(setup): fixa dependencias do projeto com Django 5.2 LTS`

**Status**: ✅ Complete (pendente)

---

### T2: Gerar o esqueleto do projeto Django ✅

**What**: Criar o projeto Django `config` com `manage.py` na raiz do repositório.
**Where**: `config/`
**Depends on**: T1
**Reuses**: `django-admin startproject`
**Requirement**: AD-002 (estrutura MVT)

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `python manage.py check` termina sem erro
- [x] `.gitignore` já existente cobre `__pycache__`, `.env` e `*.sqlite3`
- [x] Nenhuma migration foi aplicada ainda (`AUTH_USER_MODEL` ainda não existe — AD-005)

**Tests**: none
**Gate**: build

**Commit**: `chore(setup): gera esqueleto do projeto Django`

**Status**: ✅ Complete (pendente)

---

### T3: Configurar pytest, pytest-django e Ruff ✅

**What**: Registrar o módulo de settings para o pytest, o marcador `unit` e as regras do Ruff.
**Where**: `pyproject.toml`
**Depends on**: T2
**Reuses**: Defaults do Ruff (`E`, `F`, `I`) e do pytest-django.
**Requirement**: RNF04

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `DJANGO_SETTINGS_MODULE = "config.settings"` e `python_files = ["test_*.py"]` configurados
- [x] Marcador `unit` registrado (sem ele, `-m unit` emite warning)
- [x] `ruff check .` e `ruff format --check .` passam limpo
- [x] `pytest -q` roda e reporta "no tests ran" sem erro de configuração

**Tests**: none
**Gate**: build

**Commit**: `chore(setup): configura pytest-django e ruff`

**Status**: ✅ Complete (pendente)

---

### T4: Configurar o PostgreSQL 16 e as variáveis de ambiente ✅

**What**: Apontar `DATABASES` para PostgreSQL lendo credenciais do ambiente, com `DEBUG` também vindo do ambiente.
**Where**: `config/settings.py`
**Depends on**: T3
**Reuses**: `django.db.backends.postgresql`, `python-dotenv`
**Requirement**: AD-003, AUTH-26

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `DATABASES["default"]` usa o backend `postgresql` com host/porta/credenciais do ambiente
- [x] `DEBUG` lê do ambiente e tem default `False`
- [x] `SECRET_KEY` vem do ambiente e não está versionada
- [x] `.env.example` documenta cada variável esperada
- [x] `python manage.py check --database default` conecta ao PostgreSQL 16 local

**Tests**: none
**Gate**: build

**Commit**: `chore(setup): configura PostgreSQL 16 e variaveis de ambiente`

**Status**: ✅ Complete (pendente)

---

### T5: Criar a app `contas` ✅

**What**: Criar a app Django `contas` e registrá-la em `INSTALLED_APPS`.
**Where**: `contas/`
**Depends on**: T4
**Reuses**: `python manage.py startapp`
**Requirement**: AD-005

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] App criada e presente em `INSTALLED_APPS`
- [x] Diretório `contas/tests/` criado com `__init__.py`
- [x] `python manage.py check` passa
- [x] Continua sem nenhuma migration aplicada

**Tests**: none
**Gate**: build

**Commit**: `chore(contas): cria a app de contas`

**Status**: ✅ Complete (pendente)

---

### T6: Modelo `Usuario` com perfil, e-mail único e `is_administrador` ✅

**What**: Definir `Usuario(AbstractUser)` com o `TextChoices` `Perfil`, `email` único e a property `is_administrador`.
**Where**: `contas/models.py`
**Depends on**: T5
**Reuses**: `django.contrib.auth.models.AbstractUser` (username, password hasheada, `is_active`, `is_staff`)
**Requirement**: AUTH-16, AUTH-17, AUTH-19

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `Usuario.Perfil` expõe exatamente `USUARIO` e `ADMINISTRADOR` (AUTH-16)
- [x] `perfil` tem `default=Perfil.USUARIO` (AUTH-17)
- [x] `is_administrador` é o único ponto de consulta do perfil (AUTH-19)
- [x] Nenhum campo `senha_hash` próprio foi criado — a senha é a do `AbstractUser`
- [x] Testes unitários sem banco: `is_administrador` para cada valor do enum, default do perfil em instância não salva, e `Perfil.values` com exatamente dois elementos
- [x] Gate check passa: `pytest -q -m unit`
- [x] Test count: 4 testes passam (sem deleções silenciosas)

**Tests**: unit
**Gate**: quick

**Commit**: `feat(contas): adiciona modelo Usuario com perfil enum`

**Status**: ✅ Complete (pendente)

---

### T7: Declarar `AUTH_USER_MODEL` e gerar a migration inicial ✅

**What**: Apontar `AUTH_USER_MODEL` para `contas.Usuario` e gerar/aplicar a primeira migration do projeto.
**Where**: `config/settings.py`
**Depends on**: T6
**Reuses**: `makemigrations` / `migrate`
**Requirement**: AD-005, AUTH-16

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `AUTH_USER_MODEL = "contas.Usuario"` declarado
- [x] `contas/migrations/0001_initial.py` gerado e aplicado
- [x] Esta é a **primeira** migration aplicada no projeto (AD-005)
- [x] Teste de integração: a tabela `contas_usuario` existe e tem as colunas `perfil` e `email`
- [x] Gate check passa: `pytest -q`
- [x] Test count: 1 teste passa (sem deleções silenciosas)

**Tests**: integration
**Gate**: full

**Commit**: `feat(contas): declara AUTH_USER_MODEL e migration inicial`

**Status**: ✅ Complete (pendente)

---

### T8: Constraint de perfil válido no banco ✅

**What**: Acrescentar `CheckConstraint(condition=Q(perfil__in=Perfil.values))` ao `Meta` de `Usuario`.
**Where**: `contas/models.py`
**Depends on**: T7
**Reuses**: `django.db.models.CheckConstraint` (parâmetro `condition`, Django ≥ 5.1)
**Requirement**: AUTH-18

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] Constraint `usuario_perfil_valido` criada e migrada
- [x] Teste de integração: `Usuario.objects.create(perfil="CHEFE", ...)` levanta `IntegrityError`
- [x] Teste de integração: `update()` em massa para um perfil inválido também é rejeitado
- [x] Teste de integração: ambos os valores válidos gravam sem erro
- [x] Gate check passa: `pytest -q`
- [x] Test count: 3 testes passam (sem deleções silenciosas)

**Tests**: integration
**Gate**: full

**Commit**: `feat(contas): adiciona check constraint de perfil valido`

**Status**: ✅ Complete (pendente)

---

### T9: Constraint de e-mail único case-insensitive ✅

**What**: Acrescentar `UniqueConstraint(Lower("email"), name="usuario_email_unico_ci")` ao `Meta` de `Usuario`.
**Where**: `contas/models.py`
**Depends on**: T8
**Reuses**: `django.db.models.functions.Lower`
**Requirement**: AUTH-25, AUTH-02

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] Constraint `usuario_email_unico_ci` criada e migrada
- [x] Teste de integração: criar `ana@x.com` e depois `Ana@X.com` levanta `IntegrityError`
- [x] Teste de integração: dois e-mails realmente distintos convivem
- [x] `violation_error_message` traz "Já existe uma conta com este e-mail."
- [x] Gate check passa: `pytest -q`
- [x] Test count: 2 testes passam (sem deleções silenciosas)

**Tests**: integration
**Gate**: full

**Commit**: `feat(contas): adiciona unicidade case-insensitive de e-mail`

**Status**: ✅ Complete (pendente)

---

### T10: `UsuarioManager` forçando perfil no `createsuperuser` ✅

**What**: Estender `UserManager` para que `create_superuser` grave `perfil=ADMINISTRADOR`.
**Where**: `contas/models.py`
**Depends on**: T9
**Reuses**: `django.contrib.auth.models.UserManager`
**Requirement**: AUTH-20, AUTH-17

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `create_superuser` grava `perfil=ADMINISTRADOR` sem receber o argumento (AUTH-20)
- [x] `create_user` continua produzindo `perfil=USUARIO` (AUTH-17)
- [x] Teste de integração cobre os dois caminhos, verificando o valor persistido
- [x] Gate check passa: `pytest -q`
- [x] Test count: 2 testes passam (sem deleções silenciosas)

**Tests**: integration
**Gate**: full

**Commit**: `feat(contas): forca perfil ADMINISTRADOR em createsuperuser`

**Status**: ✅ Complete (pendente)

---

### T11: Sincronizar `is_staff` com o perfil ✅

**What**: Sobrescrever `Usuario.save()` para manter `is_staff` verdadeiro enquanto o perfil for `ADMINISTRADOR`.
**Where**: `contas/models.py`
**Depends on**: T10
**Reuses**: `models.Model.save`
**Requirement**: AUTH-22 (pré-requisito — sem `is_staff` o admin é inalcançável)

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] Promover uma conta a `ADMINISTRADOR` e salvar resulta em `is_staff=True`
- [x] Uma conta `USUARIO` criada normalmente permanece `is_staff=False`
- [x] `is_staff=True` concedido manualmente a um `USUARIO` não é revogado pelo `save()`
- [x] Teste de integração cobre os três casos
- [x] Gate check passa: `pytest -q`
- [x] Test count: 3 testes passam (sem deleções silenciosas)

**Tests**: integration
**Gate**: full

**Commit**: `feat(contas): sincroniza is_staff com o perfil administrador`

**Status**: ✅ Complete (pendente)

---

### T12: `UsernameOrEmailBackend` ✅

**What**: Backend de autenticação que resolve o identificador como username **ou** e-mail, preservando o dummy hash do `ModelBackend`.
**Where**: `contas/backends.py`
**Depends on**: T11
**Reuses**: `ModelBackend` — herda `user_can_authenticate()` (conta inativa) e o dummy hash anti-enumeração
**Requirement**: AUTH-01, AUTH-02, AUTH-23

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] Busca única com `Q(username__iexact=ident) | Q(email__iexact=ident)`
- [x] Mais de uma linha retornada ⇒ recusa (não confia na constraint)
- [x] Caminho "não encontrado" executa `set_password` descartável antes de retornar `None`
- [x] Testes de integração chamando o backend diretamente: username correto, e-mail correto, e-mail em caixa alternada, identificador inexistente, senha errada, conta inativa
- [x] Gate check passa: `pytest -q`
- [x] Test count: 7 testes passam (sem deleções silenciosas) — os 6 previstos mais 1 para o critério "mais de uma linha ⇒ recusa", que sem teste ficaria sem evidência

**Tests**: integration
**Gate**: full

**Commit**: `feat(contas): adiciona backend de login por usuario ou e-mail`

**Status**: ✅ Complete (pendente)

---

### T13: Registrar a cadeia de authentication backends ✅

**What**: Declarar `AUTHENTICATION_BACKENDS` com o backend customizado antes do `ModelBackend`.
**Where**: `config/settings.py`
**Depends on**: T12
**Reuses**: `django.contrib.auth.backends.ModelBackend` como fallback
**Requirement**: AUTH-01, AUTH-02

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `UsernameOrEmailBackend` precede `ModelBackend` na lista
- [x] Teste de integração via `django.contrib.auth.authenticate()` (não mais chamando o backend direto): autentica por username e por e-mail
- [x] Teste de integração: credencial inválida retorna `None`
- [x] Gate check passa: `pytest -q`
- [x] Test count: 3 testes passam (sem deleções silenciosas)

**Tests**: integration
**Gate**: full

**Commit**: `feat(contas): registra cadeia de authentication backends`

**Status**: ✅ Complete (pendente)

---

### T14: `LoginForm` com mensagem de erro única ✅

**What**: Subclassar `AuthenticationForm` para rotular o campo como "Usuário ou e-mail" e unificar a mensagem de credencial inválida.
**Where**: `contas/forms.py`
**Depends on**: T13
**Reuses**: `AuthenticationForm` — campos obrigatórios e repopulação do identificador já vêm prontos
**Requirement**: AUTH-03, AUTH-04, RF13

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `error_messages["invalid_login"]` é "Usuário ou senha inválidos.", sem interpolar o rótulo do campo
- [x] Rótulo do campo é "Usuário ou e-mail", com `autofocus` e `autocomplete="username"` (RNF09)
- [x] Testes unitários: form vazio acusa os dois campos; só identificador acusa a senha; identificador digitado é repopulado após erro
- [x] Gate check passa: `pytest -q -m unit`
- [x] Test count: 5 testes passam (sem deleções silenciosas) — os 4 previstos mais 1 para o rótulo e os atributos `autofocus`/`autocomplete`, critério que sem teste ficaria sem evidência

**Tests**: unit
**Gate**: quick

**Commit**: `feat(contas): adiciona formulario de login com mensagem unica`

**Status**: ✅ Complete (pendente)

---

### T15: Template base do projeto ✅

**What**: Criar o template base com HTML semântico, região de mensagens e `lang="pt-br"`, do qual as telas herdam.
**Where**: `templates/base.html`
**Depends on**: T14
**Reuses**: `django.contrib.messages` no contexto
**Requirement**: RNF09 (semântica e foco visível), RF12 (região de mensagens)

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `<html lang="pt-br">`, landmarks `header`/`main`/`footer`, `<title>` por bloco
- [x] Região de mensagens com `role="status"` iterando `messages`
- [x] Estilo de foco visível declarado (`:focus-visible`)
- [x] `DIRS` das settings inclui `templates/`
- [x] Gate check passa: `ruff check . && ruff format --check . && python manage.py makemigrations --check --dry-run && pytest -q`

**Tests**: none
**Gate**: build

**Commit**: `feat(ui): adiciona template base com landmarks e mensagens`

**Status**: ✅ Complete (pendente)

---

### T16: Tela de login (`LoginUsuarioView`, rota e template) ✅

**What**: A tela de entrada completa: view, rota `/entrar/` e template que estende a base.
**Where**: `contas/views.py`
**Depends on**: T15
**Reuses**: `django.contrib.auth.views.LoginView` — tratamento de `next` com validação de host e `redirect_authenticated_user`
**Requirement**: AUTH-01, AUTH-02, AUTH-03, AUTH-04, AUTH-05, AUTH-12, AUTH-24

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `LoginUsuarioView` usa `LoginForm` e `redirect_authenticated_user = True` (AUTH-12)
- [x] Rota `/entrar/` registrada em `contas/urls.py` e incluída no `config/urls.py`
- [x] Template `contas/templates/contas/login.html` com `{% csrf_token %}` e `<label>` associado a cada campo
- [x] Testes e2e: login por username redireciona ao destino padrão; login por e-mail idem; credencial inválida devolve 200 com a mensagem única; POST sem token CSRF devolve 403 (AUTH-24); chave de sessão muda após o login (AUTH-05); usuário autenticado pedindo `/entrar/` é redirecionado (AUTH-12)
- [x] `LOGIN_URL = "/entrar/"` e `LOGIN_REDIRECT_URL = "/"` definidos aqui, antecipados da T20: sem eles o destino padrão do login seria `/accounts/profile/` e o teste não poderia afirmar o valor da spec
- [x] Gate check passa: `pytest -q`
- [x] Test count: 6 testes passam (sem deleções silenciosas)

**Tests**: e2e
**Gate**: full

**Commit**: `feat(contas): adiciona tela de login`

**Status**: ✅ Complete (pendente)

---

### T17: Tela de saída (`LogoutUsuarioView` e rota) ✅

**What**: Encerrar a sessão por POST, com mensagem de confirmação e retorno ao login.
**Where**: `contas/views.py`
**Depends on**: T16
**Reuses**: `django.contrib.auth.views.LogoutView` (aceita apenas POST desde a 4.1), `django.contrib.messages`
**Requirement**: AUTH-13, AUTH-14

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] Rota `/sair/` registrada; o template base expõe um `<form method="post">`, não um link
- [x] Mensagem "Sessão encerrada." adicionada antes do redirecionamento (AUTH-13)
- [x] Testes e2e: POST em `/sair/` limpa a sessão e redireciona ao login com a mensagem; GET em `/sair/` não encerra a sessão; reenviar o cookie antigo depois do logout resulta em requisição anônima (AUTH-14)
- [x] Gate check passa: `pytest -q`
- [x] Test count: 4 testes passam (sem deleções silenciosas) — os 3 previstos mais 1 que renderiza o `base.html` autenticado e prova o `<form method="post">`, critério que ainda não tem página autenticada onde aparecer (a home chega na T19)

**Tests**: e2e
**Gate**: full

**Commit**: `feat(contas): adiciona encerramento de sessao`

**Status**: ✅ Complete (pendente)

---

### T18: Log de tentativa de login malsucedida ✅

**What**: Receiver do sinal `user_login_failed` gravando timestamp e identificador submetido.
**Where**: `contas/signals.py`
**Depends on**: T17
**Reuses**: `django.contrib.auth.signals.user_login_failed` — o Django já remove a senha do dict de credenciais antes de emitir
**Requirement**: AUTH-27, AUTH-08

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] Receiver conectado em `ContasConfig.ready()`, com logger nomeado (`contas.autenticacao`)
- [x] Horário em ISO 8601 na própria mensagem: o projeto não configura `LOGGING`, e sem formatter o registro sairia sem timestamp
- [x] Testes unitários com `caplog`: um login recusado emite um `warning` contendo o identificador
- [x] Teste unitário: a senha submetida **não** aparece em nenhum registro de log emitido
- [x] Gate check passa: `pytest -q -m unit`
- [x] Test count: 2 testes passam (sem deleções silenciosas)

**Tests**: unit
**Gate**: quick

**Commit**: `feat(contas): registra tentativas de login malsucedidas`

**Status**: ✅ Complete (pendente)

---

### T19: App `nucleo` com a home interna ✅

**What**: App `nucleo` com `HomeInternaView` na rota `/`, primeira tela protegida do sistema.
**Where**: `nucleo/`
**Depends on**: T18
**Reuses**: `django.views.generic.TemplateView`, `templates/base.html`
**Requirement**: AUTH-01 (destino do login), AUTH-11

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] App criada, registrada e com rota `/` respondendo
- [x] Template estende `base.html` e traz o formulário de logout (herdado do cabeçalho da base, T17)
- [x] Comentário no topo da view marcando-a como provisória, substituída pela listagem da F3
- [x] Testes e2e: usuário autenticado recebe 200; o conteúdo renderizado identifica a conta autenticada
- [x] Gate check passa: `pytest -q`
- [x] Test count: 2 testes passam (sem deleções silenciosas)

**Tests**: e2e
**Gate**: full

**Commit**: `feat(nucleo): adiciona home interna provisoria`

**Status**: ✅ Complete (pendente)

---

### T20: Negar acesso por padrão via `LoginRequiredMiddleware` ✅

**What**: Ativar o middleware, abrir exceção só para o login e provar a negação com varredura de rotas.
**Where**: `config/settings.py`
**Depends on**: T19
**Reuses**: `django.contrib.auth.middleware.LoginRequiredMiddleware`, `login_not_required`
**Requirement**: AUTH-09, AUTH-10, AUTH-11, AD-006

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] Middleware presente depois de `AuthenticationMiddleware` (`LOGIN_URL` e `LOGIN_REDIRECT_URL` já foram definidos na T16)
- [x] `LoginUsuarioView` marcada com `@login_not_required` — única exceção
- [x] **Teste de varredura**: percorre as rotas de `urlpatterns`, requisita cada uma anonimamente e exige 302 para `LOGIN_URL`, com allowlist explícita (`/entrar/`, estáticos, admin). É este teste que sustenta a AUTH-09 nas features seguintes
- [x] Teste e2e: anônimo pedindo `/` é redirecionado com `next=/` (AUTH-09)
- [x] Teste e2e: autenticar com `next` preenchido leva ao destino original (AUTH-10)
- [x] Teste e2e: conta `USUARIO` acessa a home igual a um `ADMINISTRADOR` (AUTH-11)
- [x] Gate check passa: `pytest -q`
- [x] Test count: 4 testes, 5 casos passam (sem deleções silenciosas) — o de AUTH-11 é parametrizado pelos dois perfis. A varredura preenche conversores de rota (`<int:pk>` etc.) e falha diante de `re_path`, para que nenhuma rota nova escape dela

**Tests**: e2e
**Gate**: full

**Commit**: `feat(config): nega acesso por padrao com LoginRequiredMiddleware`

**Status**: ✅ Complete (pendente)

---

### T21: Ciclo de vida e expiração da sessão ✅

**What**: Configurar expiração por inatividade de 8 horas e o endurecimento dos cookies.
**Where**: `config/settings.py`
**Depends on**: T20
**Reuses**: Framework de sessões do Django
**Requirement**: AUTH-15, RNF02

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `SESSION_COOKIE_AGE = 28800` e `SESSION_SAVE_EVERY_REQUEST = True` — sem o segundo, a contagem é a partir do login, não da última requisição
- [x] `SESSION_COOKIE_HTTPONLY`, `SESSION_COOKIE_SECURE` e `CSRF_COOKIE_SECURE` verdadeiros fora de `DEBUG`
- [x] Teste de integração: sessão com `expiry` vencido resulta em requisição anônima e redirecionamento ao login
- [x] Teste de integração: uma requisição dentro da janela renova a expiração
- [x] Gate check passa: `pytest -q`
- [x] Test count: 3 testes passam (sem deleções silenciosas) — os 2 previstos mais 1 unitário que carrega o `settings.py` isolado com `DJANGO_DEBUG` ligado e desligado, para provar os flags de cookie (o `.env` local usa `DEBUG=True`)

**Tests**: integration
**Gate**: full

**Commit**: `feat(config): define expiracao de sessao e cookies seguros`

**Status**: ✅ Complete (pendente)

---

### T22: Página de erro 500 sem vazamento de detalhes

**What**: Template 500 próprio, garantindo que falha de banco não exponha string de conexão nem traceback.
**Where**: `templates/500.html`
**Depends on**: T21
**Reuses**: Handler `server_error` padrão do Django
**Requirement**: AUTH-26

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [ ] `templates/500.html` estende a base e traz orientação ao usuário
- [ ] Teste e2e com `DEBUG=False`: simular `OperationalError` no login devolve 500, sem sessão aberta
- [ ] Teste e2e: a resposta não contém host, usuário ou senha do banco, nem traceback
- [ ] Gate check passa: `pytest -q`
- [ ] Test count: 2 testes passam (sem deleções silenciosas)

**Tests**: e2e
**Gate**: full

**Commit**: `feat(config): adiciona pagina 500 sem vazamento de detalhes`

---

### T23: Registrar `UsuarioAdmin`

**What**: Registrar `Usuario` no admin estendendo `UserAdmin`, com `perfil` nos fieldsets e na listagem.
**Where**: `contas/admin.py`
**Depends on**: T22
**Reuses**: `django.contrib.auth.admin.UserAdmin` — trata a senha com `ReadOnlyPasswordHashField`
**Requirement**: AUTH-22, AUTH-08, RN11

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [ ] `Usuario` registrado; `perfil` aparece em `list_display`, `list_filter` e nos fieldsets
- [ ] Nenhuma tela do admin exibe ou aceita senha em texto puro (AUTH-08)
- [ ] Teste e2e: `ADMINISTRADOR` abre a listagem de usuários (200) e cria uma conta
- [ ] Teste e2e: a conta criada pelo admin nasce com perfil `USUARIO`
- [ ] Gate check passa: `pytest -q`
- [ ] Test count: 2 testes passam (sem deleções silenciosas)

**Tests**: e2e
**Gate**: full

**Commit**: `feat(contas): registra Usuario no admin`

---

### T24: Esconder o campo de perfil de não administradores

**What**: `get_fieldsets`, `get_readonly_fields` e `has_change_permission` removendo `perfil` e `is_superuser` de quem não é administrador.
**Where**: `contas/admin.py`
**Depends on**: T23
**Reuses**: Ganchos de permissão do `ModelAdmin`
**Requirement**: AUTH-22, RN11

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [ ] Para `request.user.is_administrador` falso, `perfil` e `is_superuser` saem do formulário e entram em readonly
- [ ] `has_change_permission` é falso para não administrador sobre conta de terceiro
- [ ] Teste e2e: um `USUARIO` com `is_staff` concedido manualmente abre o próprio registro e **não** vê o campo `perfil`
- [ ] Teste e2e: um `ADMINISTRADOR` vê e edita o campo
- [ ] Teste e2e: um `USUARIO` sem `is_staff` é redirecionado ao login do admin (AUTH-21, ramo de redirecionamento)
- [ ] Gate check passa: `pytest -q`
- [ ] Test count: 3 testes passam (sem deleções silenciosas)

**Tests**: e2e
**Gate**: full

**Commit**: `feat(contas): esconde campo de perfil de nao administradores`

---

### T25: Recusar com 403 a alteração de perfil por não administrador

**What**: `save_model` levantando `PermissionDenied` quando um POST altera `perfil` sem o requisitante ser administrador.
**Where**: `contas/admin.py`
**Depends on**: T24
**Reuses**: `django.core.exceptions.PermissionDenied` → handler 403 do Django
**Requirement**: AUTH-21, RN11

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [ ] `save_model` compara o `perfil` submetido com o persistido e levanta `PermissionDenied` se divergirem sem autorização
- [ ] A defesa vale mesmo com o campo removido do formulário pela T24 (POST forjado)
- [ ] Teste e2e: POST forjado de um `USUARIO` com `is_staff` tentando promover a si mesmo devolve 403 e o perfil persistido não muda (AUTH-21, ramo 403)
- [ ] Teste e2e: POST forjado tentando promover terceiro devolve 403
- [ ] Teste e2e: o mesmo POST feito por `ADMINISTRADOR` é aceito e persiste a mudança
- [ ] Gate check passa: `pytest -q`
- [ ] Test count: 3 testes passam (sem deleções silenciosas)

**Tests**: e2e
**Gate**: full

**Commit**: `feat(contas): recusa com 403 alteracao de perfil por nao administrador`

---

## Phase Execution Map

```
Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5

Phase 1:  T1 → T2 → T3 → T4
Phase 2:  T5 → T6 → T7 → T8 → T9 → T10 → T11
Phase 3:  T12 → T13 → T14 → T15 → T16 → T17 → T18
Phase 4:  T19 → T20 → T21 → T22
Phase 5:  T23 → T24 → T25
```

Arcos de fronteira entre fases (a primeira task de cada fase depende da última da anterior):

```
T4  → T5
T11 → T12
T18 → T19
T22 → T23
```

A execução é estritamente sequencial — não há paralelismo dentro de uma fase.

**Empacotamento previsto no Execute:** 25 tasks ⇒ com orçamento de ~7 por lote e corte apenas em
fronteira de fase: **lote 1** = Fases 1+2 (11 tasks), **lote 2** = Fase 3 (7), **lote 3** = Fases 4+5
(7). Mais de um lote ⇒ o Execute deve **oferecer** sub-agentes antes de começar.

---

## Task Granularity Check

| Task | Scope | Status |
| ---- | ----- | ------ |
| T1–T5 | 1 arquivo de config / 1 scaffold cada | ✅ Granular |
| T6, T8, T9, T10, T11 | 1 conceito cada dentro de `contas/models.py` | ✅ Granular (coeso, mesmo arquivo) |
| T7, T13, T20, T21 | 1 bloco de configuração cada | ✅ Granular |
| T12, T14, T18 | 1 classe / 1 receiver | ✅ Granular |
| T15, T22 | 1 template | ✅ Granular |
| T16, T17 | 1 tela = view + rota + template | ⚠️ 3 arquivos, coeso — ver nota |
| T19 | 1 app com 1 view | ⚠️ scaffold + view, coeso — ver nota |
| T23, T24, T25 | 1 comportamento cada em `contas/admin.py` | ✅ Granular |

**Nota sobre T16, T17 e T19:** uma view Django não é testável sem sua rota, e a rota não entrega
nada sem o template. Separá-las produziria tasks que deixam código não verificado — exatamente o que
a regra de co-locação de testes proíbe. O `Where` nomeia o arquivo principal; rota e template estão
declarados no `Done when` e cobertos pelos mesmos testes e2e. É merge backward deliberado, não
falta de granularidade.

---

## Diagram-Definition Cross-Check

| Task | Depends On (task body) | Diagram Shows | Status |
| ---- | ---------------------- | ------------- | ------ |
| T1 | None | (início da Fase 1) | ✅ Match |
| T2 | T1 | T1 → T2 | ✅ Match |
| T3 | T2 | T2 → T3 | ✅ Match |
| T4 | T3 | T3 → T4 | ✅ Match |
| T5 | T4 | T4 → T5 (arco de fronteira) | ✅ Match |
| T6 | T5 | T5 → T6 | ✅ Match |
| T7 | T6 | T6 → T7 | ✅ Match |
| T8 | T7 | T7 → T8 | ✅ Match |
| T9 | T8 | T8 → T9 | ✅ Match |
| T10 | T9 | T9 → T10 | ✅ Match |
| T11 | T10 | T10 → T11 | ✅ Match |
| T12 | T11 | T11 → T12 (arco de fronteira) | ✅ Match |
| T13 | T12 | T12 → T13 | ✅ Match |
| T14 | T13 | T13 → T14 | ✅ Match |
| T15 | T14 | T14 → T15 | ✅ Match |
| T16 | T15 | T15 → T16 | ✅ Match |
| T17 | T16 | T16 → T17 | ✅ Match |
| T18 | T17 | T17 → T18 | ✅ Match |
| T19 | T18 | T18 → T19 (arco de fronteira) | ✅ Match |
| T20 | T19 | T19 → T20 | ✅ Match |
| T21 | T20 | T20 → T21 | ✅ Match |
| T22 | T21 | T21 → T22 | ✅ Match |
| T23 | T22 | T22 → T23 (arco de fronteira) | ✅ Match |
| T24 | T23 | T23 → T24 | ✅ Match |
| T25 | T24 | T24 → T25 | ✅ Match |

Nenhuma dependência aponta para fase posterior.

---

## Test Co-location Validation

| Task | Code Layer Created/Modified | Matrix Requires | Task Says | Status |
| ---- | --------------------------- | --------------- | --------- | ------ |
| T1 | Configuração | none | none | ✅ OK |
| T2 | Configuração (scaffold) | none | none | ✅ OK |
| T3 | Configuração | none | none | ✅ OK |
| T4 | Configuração | none | none | ✅ OK |
| T5 | Configuração (scaffold) | none | none | ✅ OK |
| T6 | Modelo de domínio | unit | unit | ✅ OK |
| T7 | Configuração + migration | none → elevado | integration | ✅ OK (a task prova que a tabela existe) |
| T8 | Constraints de banco | integration | integration | ✅ OK |
| T9 | Constraints de banco | integration | integration | ✅ OK |
| T10 | Modelo de domínio (manager, toca banco) | integration | integration | ✅ OK |
| T11 | Modelo de domínio (`save`, toca banco) | integration | integration | ✅ OK |
| T12 | Authentication backend | integration | integration | ✅ OK |
| T13 | Configuração + backend | integration | integration | ✅ OK |
| T14 | Formulário | unit | unit | ✅ OK |
| T15 | Template | none | none | ✅ OK |
| T16 | Views e rotas | e2e | e2e | ✅ OK |
| T17 | Views e rotas | e2e | e2e | ✅ OK |
| T18 | Sinais | unit | unit | ✅ OK |
| T19 | Views e rotas | e2e | e2e | ✅ OK |
| T20 | Controle de acesso | e2e | e2e | ✅ OK |
| T21 | Controle de acesso (sessão) | e2e → integration | integration | ✅ OK (sem navegação de tela; manipula a sessão direto) |
| T22 | Template + views | e2e | e2e | ✅ OK |
| T23 | Admin | e2e | e2e | ✅ OK |
| T24 | Admin | e2e | e2e | ✅ OK |
| T25 | Admin | e2e | e2e | ✅ OK |

Nenhuma violação. Nenhum `Tests: none` em task que produz lógica — os quatro casos (T1–T5, T15) são
configuração, scaffold e template, que a matriz marca como cobertos pelo gate de build e exercitados
indiretamente pelos testes e2e das views que os consomem.

---

## Cobertura de requisitos por task

| Requirement | Task(s) |
| ----------- | ------- |
| AUTH-01 | T12, T13, T16, T19 |
| AUTH-02 | T9, T12, T13, T16 |
| AUTH-03 | T14, T16 |
| AUTH-04 | T14, T16 |
| AUTH-05 | T16 |
| AUTH-06 / AUTH-07 | T6 (herdado do `AbstractUser`), verificado em T23 |
| AUTH-08 | T18, T23 |
| AUTH-09 | T20 |
| AUTH-10 | T20 |
| AUTH-11 | T20 |
| AUTH-12 | T16 |
| AUTH-13 | T17 |
| AUTH-14 | T17 |
| AUTH-15 | T21 |
| AUTH-16 | T6, T7 |
| AUTH-17 | T6, T10 |
| AUTH-18 | T8 |
| AUTH-19 | T6 |
| AUTH-20 | T10 |
| AUTH-21 | T24, T25 |
| AUTH-22 | T11, T23, T24 |
| AUTH-23 | T12 |
| AUTH-24 | T16 |
| AUTH-25 | T9 |
| AUTH-26 | T4, T22 |
| AUTH-27 | T18 |

27 requisitos, 27 mapeados, 0 órfãos.
