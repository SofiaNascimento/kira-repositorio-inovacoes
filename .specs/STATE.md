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

### AD-009
- **Decision**: Toda view que altera uma `Inovacao` (editar, excluir e, na F5, trocar o status) herda `inovacoes.views.AlteracaoDeInovacaoMixin`, que busca a inovação e checa `Inovacao.pode_ser_alterada_por(request.user)` no `dispatch()`. A regra "autor ou `ADMINISTRADOR`" mora só nesse método do modelo. A recusa é HTTP 403 com a página própria `inovacoes/acesso_negado.html`, renderizada pela view, nunca o `403.html` global.
- **Reason**: A RN05 e o RNF07 exigem que um `USUARIO` nunca altere registro de terceiro, na tela e na requisição. Com a checagem espalhada por view, a próxima view de alteração (a troca de status da F5) pode esquecê-la e abrir a porta em silêncio. Um método no modelo dá uma regra única para views e templates, testável sem HTTP (AD-002), e o mixin a torna visível na declaração de cada view, como o mixin da AD-007. O `403.html` global fica de fora porque o Django admin o usa nas recusas da INOV-20 e da AUTH-22.
- **Trade-off**: As permissões de objeto do Django (`has_perm` com `obj`, `PermissionRequiredMixin`) não são usadas, e `is_superuser`/`is_staff` não dão acesso a inovações de terceiros: o perfil é o único critério. Quem conhece o mecanismo padrão do Django vai procurá-lo e não achar. Um teste de varredura exige 403 de um terceiro `USUARIO` em toda rota de `inovacoes` com `pk`, salvo uma allowlist (o detalhe).
- **Scope**: F4 (edicao-exclusao), F5 (ciclo-de-vida-status) e toda view futura que grave ou apague uma `Inovacao`. O detalhe usa o mesmo método para mostrar ou esconder as ações.
- **Date**: 2026-10-11
- **Status**: active

### AD-010
- **Decision**: O visual do sistema segue `docs/design-spec.md` por um template base único (`templates/base.html`) e uma folha de estilo central (`templates/kira.css`), embutida pelo base em `<style>{% include "kira.css" %}</style>`. Toda tela estende o base e usa só os componentes da folha (`botao`, `campo`, `alerta`, `cartao`, `tabela`, `selo`, `acoes`, `vazio`); nenhuma tela tem `<style>` ou `style=`. HTML que um teste fixa recebe estilo por seletor de papel ARIA ou por contêiner, nunca por atributo novo. A folha não tem `="` nem `<`, e os seletores de atributo vão sem aspas (`[role=alert]`).
- **Reason**: A §6 da spec de design pede que as telas estendam os componentes sem recriar estilo (H4). O projeto não serve estáticos: não há `STATIC_ROOT` nem servidor de arquivos com `DEBUG=False`, e um `<link>` para `/static/` sairia sem estilo fora do `runserver` de desenvolvimento. Embutir a folha mantém um arquivo só, sem dependência nova, e os testes de foco da F2–F4 (INOV-35, CONS-41, EDEX-42) continuam lendo o CSS real da página. Os testes procuram atributos no HTML por substring (`'role="alert"' not in html`, `aria-invalid`), e o CSS embutido os enganaria se repetisse esse texto.
- **Trade-off**: Cada página carrega ~14 KB de CSS sem cache do navegador. Quando o deploy servir estáticos (whitenoise ou servidor web), o caminho é mover `kira.css` para `static/` com um `<link>` e ajustar os testes de foco para ler o arquivo; isso exige supersedir esta decisão. Botões e links fixados pelos testes não ganham `aria-current` nem classes próprias, só estilo herdado do contêiner.
- **Scope**: Todas as telas: F1 a F4 hoje, F5 e F6 (o dashboard e o controle de status entram como componentes novos na mesma folha). Tokens e pares de contraste vigiados por `inovacoes/tests/test_views_sistema_design.py`; todo par novo de cor entra no teste DS-08.
- **Date**: 2026-10-11
- **Status**: active

### AD-011
- **Decision**: Depois do cadastro, o status de uma `Inovacao` só muda por `Inovacao.avancar_status(por=, status_visto=)`, que trava a linha (`select_for_update`), confere o status visto, avança um estágio por `PROXIMO_STATUS` e cria o `MudancaDeStatus` na mesma transação. O banco recusa um `MudancaDeStatus` fora das duas transições (CHECK `mudanca_de_status_transicao_valida`).
- **Reason**: A F5 promete que o histórico conta como cada inovação chegou ao estágio atual (RN03, STAT-14, STAT-15). Uma escrita direta em `status` (view nova, script, F6) mudaria o estado sem deixar registro, e o histórico deixaria de ser prova. Um método no modelo dá uma regra única, testável sem HTTP (AD-002), como o `pode_ser_alterada_por` da AD-009.
- **Trade-off**: A regra é de convenção na aplicação: o banco valida o histórico, não a coluna `Inovacao.status`, e `QuerySet.update(status=…)` ou um `save()` com status trocado continuam possíveis. Uma trigger fecharia isso, mas seria a primeira lógica procedural no banco, invisível ao Django. A carga de demonstração cria inovações já com status: isso é cadastro, não mudança, e fica fora da regra.
- **Scope**: F5 (ciclo-de-vida-status), F6 (que lê o status e o histórico) e qualquer view, comando ou script que altere o status de uma inovação existente.
- **Date**: 2026-10-18
- **Status**: active

### AD-012
- **Decision**: Todo `Reaproveitamento` nasce por `Inovacao.registrar_reaproveitamento(unidade=, por=)`, que trava a linha da inovação (`select_for_update`), confere o status gravado ("Disponível para replicação") e a unidade de origem e cria o registro. A unicidade (inovação, unidade) fica com o banco (`UniqueConstraint reaproveitamento_unico_por_unidade`), e a violação vira `ValidationError(code="unidade_ja_reaproveitou")`. Recusas levantam `ValidationError` com os códigos `status_indisponivel`, `unidade_de_origem` e `unidade_ja_reaproveitou`.
- **Reason**: A RN09 é o que dá sentido à métrica de reuso do RF10. Duas das três guardas (status e unidade ≠ origem) dependem de outra tabela, e uma CHECK do PostgreSQL não as expressa. Um método no modelo dá uma regra única, testável sem HTTP (AD-002), e corresponde à operação `podeSerReaproveitada()` do diagrama de classes, no mesmo desenho do `avancar_status` da AD-011. A view, o admin e qualquer script passam pelo mesmo caminho.
- **Trade-off**: A regra é de convenção na aplicação: `Reaproveitamento.objects.create()` direto (shell, script, fixture de teste) grava um reuso inválido e infla o painel. Uma trigger fecharia isso, mas seria a primeira lógica procedural no banco, invisível ao Django (recusada na AD-011). O admin de `Reaproveitamento` não permite incluir nem editar, só listar e excluir.
- **Scope**: F6 (reaproveitamento-indicadores) e qualquer view, comando, carga de demonstração ou teste que crie reaproveitamentos. A rota de sinalização não altera a `Inovacao` e por isso fica fora da AD-009, num conjunto `ROTAS_SEM_AUTORIA` da varredura de autoria.
- **Date**: 2026-10-18
- **Status**: active

## Handoff

- **Feature (2026-10-27)**: deploy-producao (RNF06) — `.specs/features/deploy-producao/`. **Concluída** em 2026-10-27: Verifier PASS na iteração 2 (17/17 ACs, 21/21 mutantes mortos; `validate_state.py` sai com 0). Vercel (runtime Python, 3.13 por `.python-version`) + Supabase pelo transaction pooler. Decisões do usuário no Specify: `kira.css` segue embutido (AD-010 não supersedida), `DATABASE_URL` via `dj-database-url` com fallback às `POSTGRES_*`, sem WhiteNoise (a Vercel serve `/static/` pela CDN com `STATIC_ROOT`). Design e Tasks dispensados (plano inline de 5 passos): `f014e94` (CSRF_TRUSTED_ORIGINS), `f272ad2` (banco), `8046e7b` (STATIC_ROOT), `c701f35` (`.python-version`, `vercel.json`), `088d7d7` (`.env.example`, README); validação it. 1 FAIL `c0e6457` (M13: DEPL-17 não ligava os comandos à `DATABASE_URL`), correção `56e934c`. **904 testes** passando, build gate verde. Nenhum teste antigo alterado. Lição candidata nova L-046. **README**: estava vazio desde `2095b21` ("Arquivos skill" apagou as 238 linhas do `7bd7907`); hoje só tem o título e a seção de deploy. Perguntar ao usuário se restaura o texto antigo. **Próximo passo**: roteiro de UAT manual da spec (9 passos), que depende de nuvem e de go-ahead explícito do usuário para cada operação remota (deploy, `migrate`/`createsuperuser` no Supabase). O agente não cria contas nem acessa Vercel/Supabase. Ressalvas não bloqueantes: o glob do `excludeFiles` é emulado no teste (só o build da Vercel confirma); o teste da DEPL-17 exige a `DATABASE_URL` inline com aspas simples na linha do comando. Postgres local da 5433 foi ligado nesta sessão. Branch `main`, tudo commitado só local; push pelo usuário.

- **Feature (2026-10-19)**: reaproveitamento-indicadores (F6) — `.specs/features/reaproveitamento-indicadores/`. **Concluída com ressalva** em 2026-10-19. Retomada da pausa da linha de corte por decisão do usuário (opção a: fazer o painel). Lotes 3 (T11–T16, `64ca2cc`…`0511e61`) e 4 (T17–T18, `eeb50cb`, `985bfa4`) por sub-agentes; correções só de teste T19 (`865fe7a`, helper `inovacoes/tests/visibilidade.py` com `exibido()`) e T20 (`4b3dae2`, varredura de toda asserção de exibido da F6). **865 testes** passando, build gate verde. Verifier FAIL nas 3 iterações só por lacunas de teste (produção inalterada desde a iteração 1 e conforme às 49 ACs): it. 1 M41/M43/M44/M45, it. 2 X01/Y01/Y02, it. 3 vetores novos L1–L4 (SVG `display`/`fill-opacity`, `disabled`, CSS `display:none`, `role="presentation"`). **O usuário aceitou o risco residual L1–L4** e pediu o fechamento (`validation.md`, Decisão do usuário). Spec: 43 ACs `Verified`; REAP-03, 30, 31, 36, 44 e 46 `Implementing (risco residual aceito)`. `validate_state.py` sai com 1 de propósito (veredito registrado FAIL). Equivalentes aceitos: M06, M09, M17, C07. Spec-precision gaps abertos G1–G6 (REAP-04 opção vazia `selected`; REAP-26 superuser sem staff 302; REAP-26/27 destino após excluir; REAP-35 `width="480.0"`; REAP-36 truncagem com espaço inicial; ordem de leitura da T18). Correção de L1–L4 em Deferred Ideas do `context.md`. Lições: L-028 e L-030 promovidas a confirmed; candidatas novas L-033 a L-045 (L-040 = aplicar a correção a todo teste da feature que afirma o mesmo tipo de resultado). Testes antigos alterados, todos autorizados no `tasks.md`. Migration nova `inovacoes 0008` (não aplicada no banco local `kira` por este agente). **Próximo passo**: conferência manual no navegador (sinalização, detalhe, admin, painel e menu "Indicadores"), depois de `.venv/bin/python manage.py migrate`; responder a pendência da F5 (emenda STAT-06/STAT-34). Branch `main`, tudo commitado só local; push pelo usuário.

- **Feature atual (2026-10-18)**: ciclo-de-vida-status (F5) — `.specs/features/ciclo-de-vida-status/`. **Concluída com ressalva** em 2026-10-18. Specify, Design (AD-011) e Tasks aprovados; Execute T1–T15 em dois lotes de sub-agentes mais as correções T12–T15; 685 testes passando e build gate verde. Verifier FAIL nas 3 iterações só por lacunas de teste (produção inalterada desde a iteração 1 e conforme): M11 e M27 (it. 1), N14 (it. 2), A1/A2 e A6/A7 (it. 3). Limite atingido; **o usuário aceitou o risco residual da STAT-37** e pediu o fechamento: a T15 (`1a57e9c`) corrigiu a regressão A1/A2 da T14 sem nova verificação, e fica aberta a lacuna A6/A7 (teste de contraste só lê seletores que começam por `.ciclo`/`.historico`). Spec: 36 ACs `Verified`, STAT-37 `Implementing (risco residual aceito)`. `validate_state.py` sai com 1 de propósito: o veredito registrado continua FAIL (`validation.md`, Decisão do usuário). Testes antigos alterados com autorização: `CONSULTAS_DO_DETALHE` 6→7 e contagem de telas do DS-01 8→9; sanidade da varredura AD-009 ganhou `inovacoes:status`. **Em aberto**: emendar STAT-06/STAT-34 para "o `<title>` começa por 'Avançar status'" (pergunta ao usuário sem resposta); correção A6/A7 em Deferred Ideas do `context.md`; lições candidatas novas L-019 a L-023. **Passe de design (design-spec §10 F5) feito em 2026-10-18**: controle de transição com botão "Avançar status" desabilitado (`aria-disabled`) e explicação no estágio final, explicação de permissão para quem não pode alterar, ajuda de um estágio por vez (STAT-04/05/41 emendadas, STAT-38 a STAT-41 novas; T16–T22; 710 testes). Verifier FAIL nas iterações 4–6 só por lacunas de teste; o usuário aceitou o risco residual (checagens de exibição por regex) e fechou. Ideia de correção em `context.md`. **Conferência manual no navegador aprovada pelo usuário em 2026-10-18** (antes do passe de design; o controle novo ainda não foi conferido no navegador) (12 passos; `validation.md`, Interactive UAT Results). Banco local `kira`: migration `inovacoes 0007` aplicada; inovações 1, 2 e 4 (e possivelmente outras) tiveram o status avançado na conferência, com histórico. **Próximo passo**: iniciar a F6 (reaproveitamento-indicadores) pelo Specify, conformando com a AD-011. Tudo commitado só local; push pelo usuário.

- **Feature**: sistema-de-design — `.specs/features/sistema-de-design/`. **Concluído** em 2026-10-11: Verifier PASS na iteração 2 (`validation.md`). Passe de design sobre a F1–F4, guiado por `docs/design-spec.md`; decisão AD-010. A F4 (edicao-exclusao) segue concluída (Verifier PASS, conferência manual 20/20).
- **Phase / Task**: Specify ✅ (spec breve com Code Reuse Analysis, DS-01 a DS-16) · Design e Tasks dispensados (plano inline de 4 passos) · Execute ✅ · Verifier ✅ PASS (iteração 2: 16/16 ACs, 33/34 mutantes mortos; o sobrevivente `outline: thin solid` está fora da spec).
- **Completed**: `7f90d0d` (spec), `3bbc99b` (base + kira.css), `a7b9d9a` (telas), `50b8818` (AD-010), `7918c00` (validação iteração 1: FAIL, comentário do CSS satisfazia o `"ana" in html` da AUTH-01 e DS-07 fraco), `4db5be8` (correção), fechamento (commit desta atualização). Nenhum teste da F1–F4 alterado.
- **In-progress** (file:line): nenhum.
- **Next step**: conferir o visual no navegador (`DJANGO_DEBUG=True .venv/bin/python manage.py runserver`) e confirmar a premissa da paleta: o pedido falava em "teal", a `design-spec.md` define navy/azul, e o passe seguiu a spec. Depois, iniciar a **F5 (ciclo-de-vida-status, RF09)** pelo Specify. **Pedido do usuário na conferência da F4 (passo 2): o status deve ser editável** — decidido tratar na F5. No Specify da F5, decidir com o usuário se a troca de status entra no formulário de edição ou numa ação separada, e se as transições do RN03 são livres ou ordenadas. A F5 conforma com a AD-009 e a AD-010 (controle de status como componente da `kira.css`, sobre o `selo`) e carrega as lições confirmadas L-003 e L-005.
- **Notas não bloqueantes do Verifier**: sem teste próprio da F4 para id não numérico em `/editar/` (cai no 404 padrão, como no detalhe); duas exclusões simultâneas mostram sucesso às duas (aceito no design). O teste de consultas do detalhe (T8) afirma exatamente 6 consultas, medidas antes da mudança: mudança futura em sessão/middleware o quebra de propósito.
- **Testes pendentes**: nenhum. 569 passed (`.venv/bin/pytest -q`: 492 da F1–F4 + 77 do sistema de design) e build gate verde em 2026-10-11.
- **Blockers**: nenhum.
- **Ambiente**: PostgreSQL 16 na porta **5433** (`/opt/homebrew/opt/postgresql@16/bin/pg_ctl -D /opt/homebrew/var/postgresql@16 -o "-p 5433" -l /tmp/pg16.log start`); comandos pelo `.venv/`. No zsh interativo, não colar comandos com comentário `#`. DBeaver: `localhost:5433`, banco `kira`, usuário `ruan.santos`, senha vazia, **auto-commit ligado**. Servidor: `DJANGO_DEBUG=True .venv/bin/python manage.py runserver`. Em roteiros, URL de teste vai na **barra de endereço**, não no campo de busca.
- **Banco local (`kira`, 2026-10-11)**: migrations `inovacoes 0001–0006` (a F4 não cria migration). **503 inovações**: 499 da conta `demo` (a "Demonstração 001" foi excluída na conferência; `carregar_demonstracao` a recriaria) + 4 dos UATs (a "Teste" foi excluída; a 1 teve o problema trocado para "Planilha de reembolso manual", a 4 virou "PROCÉSSO RH", a 2 tem contato "RH Filial Norte"). Contas: `admin` (ADMINISTRADOR, superusuário; senha redefinida pelo usuário em 2026-10-11), `joao` (ADMINISTRADOR, restaurado após o teste de rebaixamento), `maria` (USUARIO, staff), `demo`.
- **Uncommitted files**: nenhum (após o commit desta atualização).
- **Branch**: `main`. O usuário disse em 2026-10-11 que faria o push por conta própria; conferir `git status`/`origin/main` na retomada. Push pelo agente só com pedido explícito.

**Lições**: confirmadas **L-003** (negar a tela a outros papéis com acesso do framework) e **L-005** (afirmar cada cláusula na camada que a AC descreve), promovidas pela recorrência na F4 — carregar no Specify/Design da F5. Candidata nova L-016 (varredura de autorização por parâmetro capturado, não por texto). Demais candidatas L-001, L-002, L-004, L-006 a L-015.

**Spec-precision gaps abertos da F3 (não bloqueiam)**: SPG-1 `page` ≤ 0 (CONS-05); SPG-2 limite de 100 caracteres depois de aparar (CONS-24).

**Ideias adiadas em aberto**: F1 — recuperação de senha, gestão de usuários própria, `maxlength` 254 no login. F2 — título sem acentos, lista real de unidades. F3 — ordenação pelo usuário, destaque do termo, voltar ao detalhe com filtros, `label_suffix` do `InovacaoForm`, aviso do limite de 100 caracteres. F4 (`edicao-exclusao/context.md`) — histórico/log de exclusões, exclusão lógica com recuperação, detecção de edição concorrente, página de CSRF em português.
