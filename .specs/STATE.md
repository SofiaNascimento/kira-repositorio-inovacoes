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

- **Feature**: autenticacao — `.specs/features/autenticacao/`
- **Phase / Task**: Fase 3 (Autenticação) / T12 — `UsernameOrEmailBackend`. Não iniciada.
- **Completed**: T1, T2, T3, T4 (Fase 1) · T5, T6, T7, T8, T9, T10, T11 (Fase 2). 11 de 25.
- **In-progress** (file:line): nenhum. A Fase 2 fechou no commit `b246945`; não há edição a meio caminho. O último arquivo tocado foi `contas/models.py:47` (`Usuario.save`, sincronização de `is_staff`), já commitado e com gate verde.
- **Next step**: implementar T12 — criar `contas/backends.py` com `UsernameOrEmailBackend` herdando de `ModelBackend`, buscando por `Q(username__iexact=ident) | Q(email__iexact=ident)`, preservando o dummy hash no caminho "não encontrado", e escrever os 6 testes de integração previstos na task.
- **Blockers**: nenhum bloqueio de código. Duas condições de ambiente para retomar:
  1. O PostgreSQL 16 precisa estar no ar na porta **5433** (a 14 ocupa a 5432). Subir com `/opt/homebrew/opt/postgresql@16/bin/pg_ctl -D /opt/homebrew/var/postgresql@16 -o "-p 5433" -l /tmp/pg16.log start`. Banco: `kira`. Credenciais no `.env` (não versionado; modelo em `.env.example`).
  2. Os comandos rodam pelo virtualenv `.venv/` (`.venv/bin/pytest`, `.venv/bin/python manage.py`). O `.venv` não é versionado: recriar com `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`.
- **Uncommitted files**: nenhum arquivo da feature. O que resta na árvore **é anterior a esta sessão e não foi tocado por ela**:
  - `README.md` — modificado: 238 linhas removidas, arquivo vazio no disco contra 238 no `HEAD`. Não foi alteração deste trabalho; já estava assim no início da sessão. **Não commitado de propósito** — precisa da decisão do autor (restaurar com `git restore README.md` ou commitar a remoção).
  - `.DS_Store` — lixo do macOS, não rastreado e ausente do `.gitignore`.
  - `.agents/`, `.claude/`, `docs/` — não rastreados desde antes da sessão. `.claude/skills/tlc-spec-driven/` é a própria metodologia; `docs/` traz requisitos, mapa de features e modelagem UML, que as specs referenciam.
- **Branch**: `main`

**Estado verificável na retomada**: 11 commits a partir de `66cb910` até `b246945`; `.venv/bin/pytest -q` deve reportar **17 passed**; `.venv/bin/python manage.py makemigrations --check --dry-run` deve dizer "No changes detected". Se algum desses três não bater, reconcilie pelo git antes de escrever código.
