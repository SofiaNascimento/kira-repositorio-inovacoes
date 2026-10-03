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

### AD-007
- **Decision**: Todo `ModelAdmin` do projeto só abre para o perfil `ADMINISTRADOR`, herdando `contas.admin.AcessoSomenteAdministradorMixin`, que responde a todos os `has_*_permission` com `request.user.is_administrador`.
- **Reason**: Sem a regra, cada admin novo (as listas controladas da F2 agora, possivelmente outros depois) reabre a porta que a AUTH-22 fechou: basta `is_staff` e uma permissão de modelo para um `USUARIO` editar uma lista controlada. Um mixin único mantém a regra em um só lugar e a torna visível na declaração de cada admin.
- **Trade-off**: As permissões de modelo e os grupos do Django deixam de ter efeito no admin do projeto; o perfil é o único critério. Quem conhece só o admin padrão vai estranhar que conceder permissão a um grupo não mude nada.
- **Scope**: Todo `ModelAdmin` registrado em qualquer app — hoje `UsuarioAdmin` (F1), `UnidadeAdmin` e `CategoriaAdmin` (F2).
- **Date**: 2026-09-27
- **Status**: active

## Handoff

- **Feature**: cadastro-inovacao (F2) — `.specs/features/cadastro-inovacao/`. Pausa em 2026-10-02 no meio do **UAT interativo da F1+F2**, sem código a meio caminho.
- **Phase / Task**: Specify ✅ · Design ✅ · Tasks ✅ · Execute ✅ (T1–T24) · Verifier ✅ **PASS na iteração 3** (206 passed; sensor 4/4 não equivalentes mortos, 3 equivalentes; `validate_state.py` 0 erros) · UAT ⏳ preparação feita, **itens 1–21 pendentes**.
- **Completed**: T1–T23 (F2 original); **T24** (`8f329ea`) — primeiro achado do UAT: `GET /admin/login/` anônimo dava 500 porque `AcessoSomenteAdministradorMixin` lia `is_administrador` do `AnonymousUser`; agora `_is_administrador` exige `is_authenticated` (`contas/admin.py:19-22`), provado por `contas/tests/test_admin_perfil.py:125`. Validação da iteração 3 em `6277031`.
- **In-progress** (file:line): nenhum código. O roteiro do UAT (21 itens, esperado e AC de cada um) e o progresso estão em `.specs/features/cadastro-inovacao/validation.md`, seção *Interactive UAT Results*: é a fonte para retomar, não a conversa.
- **Next step**: (1) subir o servidor no terminal do usuário (`.venv/bin/python manage.py runserver`; o que rodava em segundo plano foi encerrado pelo limite de 2 h); (2) no admin, marcar **Membro da equipe** na `maria` (hoje `is_staff=False`; sem isso os itens 8 e 21 dão 302 em vez de 403); (3) seguir o roteiro do item 1 ao 21 e registrar cada resultado no `validation.md`. Itens 17–18 fecham o Success Criterion de teclado da `spec.md`; achados viram T25+ com nova rodada do Verifier.
- **Testes pendentes**: nenhum automatizado (206 passed, gate de build verde em 2026-10-02). Pendente só a verificação manual: os 21 itens do UAT, incluindo o percurso real por teclado (INOV-34/35) e o efeito visual do `:focus-visible`.
- **Blockers**: nenhum.
- **Ambiente**: PostgreSQL 16 na porta **5433** (`/opt/homebrew/opt/postgresql@16/bin/pg_ctl -D /opt/homebrew/var/postgresql@16 -o "-p 5433" -l /tmp/pg16.log start`); comandos pelo `.venv/`. No zsh interativo, não colar comandos com comentário `#` (vira argumento). DBeaver: `localhost:5433`, banco `kira`, usuário `ruan.santos`, senha vazia, **auto-commit ligado**.
- **Banco local**: migrations `inovacoes 0001–0004` aplicadas, 5 unidades e 5 categorias da carga. Contas: `admin` (ADMINISTRADOR, superusuário), `joao` (ADMINISTRADOR, sem nome, `is_staff` ligado), `maria` (USUARIO, "Maria Silva", `is_staff` **desligado**). Nenhuma inovação cadastrada ainda. Senhas fora do repositório.
- **Uncommitted files**: nenhum (este Handoff e o roteiro no `validation.md` entram no commit da pausa).
- **Branch**: `main`, **4 commits à frente** do `origin/main` (`8f329ea`, `6277031` e o da pausa, além do `eb58569` da pausa anterior), nenhum enviado. Push só com pedido explícito.

**Pendências abertas para decidir depois do UAT:**
- **Sugestão 1 do Verifier (spec-precision gap):** a AUTH-21 (`autenticacao/spec.md:196`) não diz que o login do admin abre para o visitante sem sessão. Proposta: AC nova na F1 apontando para `test_admin_perfil.py:125`. Aguarda o usuário.
- **Sugestão 2 (cosmética):** a T24 falta nas tabelas de Granularity, Diagram-Definition Cross-Check e Test Co-location do `tasks.md`.
- Depois do UAT: Specify da F3 (consulta-inovacoes).

**Decisões desta sessão (2026-10-02)**, feature-local, sem AD nova: a correção do anônimo fica dentro da AD-007 (o mixin continua sendo a regra única; anônimo nunca é administrador); o roteiro do UAT passa a viver no `validation.md`; o UAT vai até o fim antes de mexer na spec da F1.

**Lições candidatas**: L-007, L-008 (sessão anterior); **L-009** (hook de permissão que lê atributo próprio do `request.user` precisa de `is_authenticated` e de teste anônimo) e **L-010** (AC que promete redirecionar ao login precisa provar que o destino abre com 200), em `.specs/LESSONS.md`.

**Ideias adiadas em aberto**: F1 (`autenticacao/context.md`) — recuperação de senha, tela própria de gestão de usuários, `maxlength` 254 no campo de login. F2 (`cadastro-inovacao/context.md`) — comparação de título sem acentos, lista real de unidades.
