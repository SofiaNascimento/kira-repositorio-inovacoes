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

### AD-008
- **Decision**: A busca textual ignora caixa e acentos por meio da coluna `Inovacao.texto_busca`, derivada de título, problema e solução por `inovacoes.busca.normalizar` e mantida por `Inovacao.save()`; nenhuma extensão do PostgreSQL é usada.
- **Reason**: A CONS-20 exige busca sem acento, e a F2 recusou depender da extensão `unaccent` no deploy (RNF06). Normalizar o termo e o texto pela mesma função Python dá uma regra única, testável sem banco e independente da collation.
- **Trade-off**: Dado derivado no banco e uma regra de escrita: toda gravação de título, problema ou solução precisa passar por `Inovacao.save()`; `QuerySet.update()`, `bulk_create` e `bulk_update` nesses campos deixam a busca errada. O `LIKE '%…%'` não usa índice; para volumes muito maiores que o do MVP, o caminho é `pg_trgm`, que exigiria supersedir esta decisão.
- **Scope**: F3 (busca), F4 (edição grava por `save()`), F6 (se reaproveitar `buscar()`) e qualquer carga ou script que grave inovações.
- **Date**: 2026-10-03
- **Status**: active

## Handoff

- **Feature**: consulta-inovacoes (F3) — `.specs/features/consulta-inovacoes/`. F2 concluída em 2026-10-03 (UAT 21/21).
- **Phase / Task**: Specify ✅ aprovado em 2026-10-03 (`spec.md` com CONS-01 a CONS-53, `context.md` da discussão) · Design ✅ aprovado em 2026-10-03 (`design.md`, abordagem A: coluna normalizada; AD-008 registrada) · Tasks ✅ aprovado em 2026-10-03 (`tasks.md`, T1–T22 em 5 fases; parte A = T1–T11, parte B = T12–T22, numa única feature) · Execute 🔄 parte A concluída (lotes 1 e 2, T1–T11) em 2026-10-03; parte B (T12–T22) pendente, aguardando a conferência manual da parte A pelo usuário.
- **Completed**: T1–T11. Lote 1: `1b4daf3`, `060decd`, `46e285c`, `023464a`, `11c2ee5`. Lote 2: `d585e72`, `d9088b7`, `5c98282`, `238e7fa`, `5848a80`, `c2c94ec`. Build gate verde com 259 testes. Desvios: T5 `?page=0` → página 1 (SPEC_DEVIATION em `inovacoes/views.py`); teste de fuso da T2 com 02:30 UTC; T8 reapontou também `contas/tests/test_controle_acesso.py:98` (AUTH-11 → `GET /inovacoes/`), autorizado pelo usuário depois de bloqueio.
- **In-progress** (file:line): nenhum.
- **Next step**: conferência manual da parte A pelo usuário; depois lote 3 (Fase 3, T12–T16, Opus) e lote 4 (Fases 4+5, T17–T22). No fechamento: anotar "alterado pela F3" nas linhas do `design.md` da F2 que citam a home (`:78`, `:182`, `:197`, `:427`, `:428`); o `validation.md` da F2 fica como registro histórico.
- **Testes pendentes**: nenhum. 259 passed em 2026-10-03.
- **Blockers**: nenhum.
- **Ambiente**: PostgreSQL 16 na porta **5433** (`/opt/homebrew/opt/postgresql@16/bin/pg_ctl -D /opt/homebrew/var/postgresql@16 -o "-p 5433" -l /tmp/pg16.log start`); comandos pelo `.venv/`. No zsh interativo, não colar comandos com comentário `#` (vira argumento). DBeaver: `localhost:5433`, banco `kira`, usuário `ruan.santos`, senha vazia, **auto-commit ligado**.
- **Banco local**: migrations `inovacoes 0001–0004`; 5 unidades e 5 categorias da carga. Contas: `admin` (ADMINISTRADOR, superusuário), `joao` (ADMINISTRADOR, sem nome, staff), `maria` (USUARIO, "Maria Silva", staff ligado no UAT). 4 inovações do UAT: `Processo RH` e `Procésso RH` (Filial Leste, maria), `PROCESSO RH` (Filial Norte, maria), `Checklist de compras` (Sede, joao). Senhas fora do repositório.
- **Uncommitted files**: nenhum.
- **Branch**: `main`. O `origin/main` está em `9e7823d` (push de 2026-10-03); os commits do registro do UAT e da AUTH-28 ficam só locais. Push só com pedido explícito.

**Decisões desta sessão (2026-10-03)**, feature-local, sem AD nova: o UAT aceitou dados adaptados pelo usuário (títulos e unidades diferentes do roteiro) quando o critério do item era o mesmo; a conferência no banco substituiu os dados do roteiro como evidência.

**Lições candidatas**: L-007, L-008, L-009, L-010 em `.specs/LESSONS.md` (sem mudança nesta sessão).

**Ideias adiadas em aberto**: F1 (`autenticacao/context.md`) — recuperação de senha, tela própria de gestão de usuários, `maxlength` 254 no campo de login. F2 (`cadastro-inovacao/context.md`) — comparação de título sem acentos, lista real de unidades.
