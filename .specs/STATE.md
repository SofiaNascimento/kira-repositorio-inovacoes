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

- **Feature**: autenticacao — `.specs/features/autenticacao/` — **concluída e verificada**. Retomada em 2026-09-27 só para conferir a base e testar no navegador; nenhum código mudou.
- **Phase / Task**: Execute encerrado. Fases 1–6 completas (T1–T31). Verifier independente: PASS na iteração 3 de 3 (`validation.md`); `validate_state.py autenticacao` → exit 0.
- **Completed**: T1–T31. 27 de 27 requisitos em `Verified` (AUTH-19 com ressalva: a cláusula de uso por outras features é regra de processo, auditada por grep).
- **In-progress** (file:line): nenhum. Último commit de código: `8b2eca9` (`contas/tests/test_admin_perfil.py`, T31); último commit da feature: `bccd08e` (fechamento dos artefatos).
- **Next step**: iniciar a F2 (`cadastro-inovacao`) do `docs/mapa-de-features.md` pelo Specify, com discuss das áreas cinzentas (ex.: RN10 título único por unidade, RN07 listas controladas fixas ou editáveis). A F2 herda AD-005 (FK de autoria via `settings.AUTH_USER_MODEL`, `on_delete=PROTECT` sugerido no design da F1) e AD-006 (o teste de varredura em `contas/tests/test_controle_acesso.py` cobre rotas novas automaticamente).
- **Blockers**: nenhum. Ambiente: PostgreSQL 16 na porta **5433** (`/opt/homebrew/opt/postgresql@16/bin/pg_ctl -D /opt/homebrew/var/postgresql@16 -o "-p 5433" -l /tmp/pg16.log start`); comandos pelo `.venv/` (`.venv/bin/pytest`, `.venv/bin/python manage.py`). Subir o banco é passo de ambiente, não escopo de feature. Teste no navegador exige `DJANGO_DEBUG=True` (fora de DEBUG os cookies são `Secure` e o login falha em HTTP).
- **Banco local de desenvolvimento**: tem o superusuário `admin` (`admin@kira.local`, perfil `ADMINISTRADOR`), criado em 2026-09-27 para o teste manual. Senha fora do repositório; se perdida, `.venv/bin/python manage.py changepassword admin`.
- **Uncommitted files**: nenhum (este Handoff entra no próprio commit).
- **Branch**: `main`. O commit da pausa anterior (`4a45499`) já está no `origin/main`; o Handoff antigo dizia que ficaria só local.

**Decisões da sessão de 2026-09-26:** README fica vazio; `.DS_Store` fora do versionamento; execução inline; AUTH-22 cumprida como escrita (telas de usuário do admin só para `ADMINISTRADOR`, T26).

**Ideias adiadas em aberto (`context.md`)**: recuperação de senha, tela própria de gestão de usuários, `maxlength` 254 no campo de login.

**Estado verificado na retomada de 2026-09-27**: `.venv/bin/pytest -q` → **84 passed**; `makemigrations --check --dry-run` → "No changes detected"; `ruff check` e `ruff format --check` → limpos; `validate_state.py autenticacao` → exit 0.

**UAT no navegador**: iniciado em 2026-09-27, resultado ainda não informado. `GET /` sem sessão → 302 para `/entrar/?next=/` (AUTH-09/10) e `createsuperuser` → `ADMINISTRADOR` com senha em hash `pbkdf2_sha256` (AUTH-16, AUTH-06) confirmados. Quando o roteiro terminar, registrar em `validation.md` › Interactive UAT Results.
