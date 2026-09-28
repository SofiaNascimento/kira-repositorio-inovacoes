# STATE

## Decisions

### AD-001
- **Decision**: Autenticação por sessão nativa do Django (`django.contrib.auth` + cookie de sessão), não JWT.
- **Reason**: O sistema é uma aplicação web MVT renderizada no servidor, com um único cliente; a sessão do framework já entrega login, logout, hash de senha e proteção de rotas sem código adicional (RF01, RNF02).
- **Trade-off**: Abre mão de autenticação stateless e de reuso imediato por clientes externos (SPA/mobile); se um dia existir API pública, será preciso acrescentar um esquema de token à parte.
- **Scope**: F1 (autenticacao) e todas as views que exigem usuário autenticado ou autorização por perfil (F2, F3, F4, F5, F6).
- **Date**: 2026-09-21
- **Status**: active

### AD-002
- **Decision**: Arquitetura MVT do Django sem Service Layer; o ORM cumpre o papel de repositório.
- **Reason**: O domínio do MVP é CRUD com regras simples de autoria e status; uma camada de serviço/repositório sobre o ORM seria over-engineering e adicionaria indireção sem ganho de testabilidade real dentro do prazo do TCC. A modularidade exigida pelo RNF04 já decorre da separação models/views/templates.
- **Trade-off**: Regras de negócio ficam distribuídas entre models, forms e views em vez de concentradas em uma camada única; uma futura troca de ORM ou reuso da lógica fora do Django exigiria refatoração.
- **Scope**: Todas as features — nenhum design pode introduzir camada de serviço ou repositório próprio sem supersedir esta decisão.
- **Date**: 2026-09-21
- **Status**: active

### AD-003
- **Decision**: PostgreSQL 16 como banco de dados relacional, com integridade referencial garantida por chaves estrangeiras.
- **Reason**: O RNF05 exige persistência relacional com integridade referencial; as relações Inovacao→Unidade, Inovacao→Categoria, Inovacao→autor e Reaproveitamento→Inovacao são centrais e precisam ser impostas pelo banco, não apenas pela aplicação. O PostgreSQL é o backend de primeira classe do Django e está disponível na camada gratuita das plataformas previstas no RNF06.
- **Trade-off**: Exige serviço de banco em execução no ambiente local e no deploy (SQLite seria zero-configuração), e acopla o projeto a um dialeto específico onde se usarem recursos próprios do PostgreSQL.
- **Scope**: Toda a persistência do projeto; configuração de ambiente, migrações e deploy.
- **Date**: 2026-09-21
- **Status**: active

### AD-004
- **Decision**: Perfil de usuário representado por um campo enum (`USUARIO` / `ADMINISTRADOR`) em um único modelo de usuário do Django, em vez de duas classes distintas.
- **Reason**: Os dois perfis compartilham todos os atributos e diferem apenas em poderes de edição/exclusão (RN05, RN11, RNF07); um campo de perfil mantém uma única tabela de usuários, simplifica autoria (`Inovacao.autor` aponta sempre para o mesmo modelo) e permite promover ou rebaixar alguém sem migrar registros.
- **Trade-off**: A distinção de perfil deixa de ser expressa pelo sistema de tipos e passa a depender de verificações explícitas nas views e nos testes de autorização; papéis futuros com atributos próprios exigiriam repensar o modelo.
- **Scope**: F1 (autenticacao), F4 (edicao-exclusao) e toda regra de autorização por perfil.
- **Date**: 2026-09-21
- **Status**: active

### AD-005
- **Decision**: O projeto usa um modelo de usuário customizado (`contas.Usuario`, subclasse de `AbstractUser`) declarado em `AUTH_USER_MODEL` desde a primeira migration; nenhuma app referencia `auth.User` diretamente.
- **Reason**: O AD-004 exige o campo `perfil` no próprio modelo de usuário, o que já pede um modelo customizado. Além disso, trocar `AUTH_USER_MODEL` depois que migrations existem é uma das operações mais dolorosas do Django — na prática exige apagar migrations e recriar o banco. Declarar desde o início custa uma classe; declarar depois custa o histórico de migrations.
- **Trade-off**: Toda FK para usuário precisa usar `settings.AUTH_USER_MODEL` em vez de importar o modelo, e o `UserAdmin` precisa ser re-registrado. Em troca, o projeto nunca paga o custo da migração tardia.
- **Scope**: Todas as apps. A F2 depende disto para `Inovacao.autor`; F4 e F6 para autoria e métricas.
- **Date**: 2026-09-21
- **Status**: active

### AD-006
- **Decision**: O acesso é negado por padrão: `LoginRequiredMiddleware` está no `MIDDLEWARE` e toda view exige sessão autenticada; uma view pública é exceção explícita, marcada com `@login_not_required`.
- **Reason**: A RN04 exige que nenhuma tela interna seja alcançável sem autenticação. Com `@login_required`/`LoginRequiredMixin` por view, o default é aberto e a regra passa a depender de alguém lembrar do decorator em cada view nova de F2 a F6 — um esquecimento vaza conteúdo silenciosamente. Com o middleware, o esquecimento fecha a porta em vez de abrir.
- **Trade-off**: Um controle global e implícito: quem lê uma view isolada não vê que ela é protegida. Mitigado por um teste que varre as rotas registradas e exige redirecionamento ao login para todas, salvo uma allowlist explícita. Exige Django ≥ 5.1.
- **Scope**: Todas as features com interface web (F1 a F6). Toda view nova nasce protegida; tornar uma view pública é uma decisão consciente e visível no código.
- **Date**: 2026-09-21
- **Status**: active

## Handoff

- **Feature**: cadastro-inovacao (F2) — `.specs/features/cadastro-inovacao/`. Pausa em 2026-09-27 entre o Design e o Tasks, sem trabalho a meio caminho.
- **Phase / Task**: Specify ✅ (spec aprovada) · Design ✅ (aprovado em 2026-09-27, abordagem A: uma app `inovacoes`) · Tasks ⏳ não iniciado · Execute ⏳. Nenhum código da F2 escrito.
- **Completed**: `spec.md` (43 requisitos INOV-01 … INOV-43, fase `Tasks`/`Pending`; `validate_spec.py` → 0 erros), `context.md` e `design.md`.
- **In-progress** (file:line): nenhum.
- **Pendência do Design**: registrar a **AD-007** em `## Decisions` (todo `ModelAdmin` do projeto só abre para `ADMINISTRADOR`, herdando `contas.admin.AcessoSomenteAdministradorMixin`; trade-off: grupos e permissões de modelo deixam de valer no admin). Aprovada com o design; o texto completo está em `design.md` › Tech Decisions. Ficou fora do log porque a pausa pediu para não tocar em `## Decisions`. Fazer isso antes do Tasks.
- **Next step**: (1) anexar a AD-007; (2) rodar o Tasks da F2 a partir do `design.md`. Primeira task prevista: extrair o mixin de `contas/admin.py:34-50` sem mudar comportamento, com `contas/tests/test_admin_perfil.py` e `test_admin.py` verdes como gate.
- **Blockers**: nenhum. Ambiente: PostgreSQL 16 na porta **5433** (`/opt/homebrew/opt/postgresql@16/bin/pg_ctl -D /opt/homebrew/var/postgresql@16 -o "-p 5433" -l /tmp/pg16.log start`), hoje em execução; comandos pelo `.venv/` (`.venv/bin/pytest`, `.venv/bin/python manage.py`). Teste no navegador exige `DJANGO_DEBUG=True`.
- **Banco local de desenvolvimento**: só o superusuário `admin` (`admin@kira.local`, `ADMINISTRADOR`); senha fora do repositório (`changepassword admin` se perdida).
- **Uncommitted files**: nenhum (`design.md`, os ajustes de status em `spec.md` e este Handoff entram no commit da pausa).
- **Branch**: `main`. O `origin/main` estava igual à `main` antes deste commit (push feito pelo autor); só o commit da pausa fica local.

**Decisões da discussão da F2 (2026-09-27):** listas mantidas só pelo `ADMINISTRADOR` no admin, com unidades provisórias; título único ignora maiúsculas/minúsculas e conta acentos; contato responsável pré-preenchido e editável; RF15 entra como P3; arquitetura A (uma app `inovacoes`).

**Decisões da sessão de 2026-09-26:** README fica vazio; `.DS_Store` fora do versionamento; execução inline; AUTH-22 cumprida como escrita (telas de usuário do admin só para `ADMINISTRADOR`, T26).

**Ideias adiadas em aberto**: F1 (`autenticacao/context.md`) — recuperação de senha, tela própria de gestão de usuários, `maxlength` 254 no campo de login. F2 (`cadastro-inovacao/context.md`) — comparação de título sem acentos, lista real de unidades.

**Estado verificado em 2026-09-27**: `.venv/bin/pytest -q` → **84 passed**; `makemigrations --check --dry-run` → "No changes detected"; ruff limpo. F1: UAT 24/24 PASS (`autenticacao/validation.md`).
