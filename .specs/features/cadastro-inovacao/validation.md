# Cadastro de Inovação (F2) Validation

**Date**: 2026-10-02
**Iteration**: 3
**Spec**: `.specs/features/cadastro-inovacao/spec.md` (e AUTH-21/AUTH-22 de `.specs/features/autenticacao/spec.md`)
**Diff range**: `eb58569..8f329ea` em `main` (HEAD = `8f329ea`), 1 commit: a T24 (`fix(contas): abre o login do admin para o visitante anonimo`). Arquivos: `contas/admin.py`, `contas/tests/test_admin_perfil.py`, `tasks.md` e `STATE.md`. Desde a iteração 2 (`c37a565..eb58569`) só mudaram arquivos de `.specs/`; em `spec.md`, só o status, a cobertura e a tabela de rastreabilidade, nenhum texto de AC.
**Verifier**: independent sub-agent (author ≠ verifier)

**Verdict**: PASS ✅

O gate passa (206 passed). A T24 fecha o defeito achado no UAT: `GET /admin/login/` respondia 500 porque o login do admin monta a lista de apps com o `AnonymousUser` e o mixin chamava `request.user.is_administrador`, que o `AnonymousUser` não tem. O teste novo afirma o desfecho que a AUTH-21 promete (o redirecionamento leva a uma tela de login que abre) e mata o mutante que reverte a correção. Os ramos 403, 302 e liberado de USUARIO com staff, USUARIO sem staff e ADMINISTRADOR continuam iguais: os testes de admin existentes passam sem alteração e os mutantes que trocam o critério por `is_authenticated` ou `is_staff` morrem em 24 testes. Das 7 mutações da iteração 3, 4 morreram e 3 são equivalentes. Nenhum outro caminho consulta `is_administrador` sobre um usuário que pode ser anônimo. As 43 ACs da F2 continuam valendo: a única mudança de produção é `contas/admin.py`, e nenhum teste de `inovacoes/` mudou.

Fica um spec-precision gap, que não bloqueia: nenhuma AC fala do visitante anônimo no admin. A AUTH-21 só descreve o USUARIO autenticado.

---

## Task Completion

| Task | Status | Notes |
| ---- | ------ | ----- |
| T1–T21 | ✅ Done | Sem mudança desde a iteração 1: `git diff 49c82ee..c37a565` só toca `inovacoes/tests/test_views_cadastro.py` e arquivos de `.specs/`; nenhum arquivo de produção |
| T22 | ✅ Done | `999d080`: teste novo da INOV-04 com contas criadas antes e depois de quem envia (`tasks.md:742`, `:767`) |
| T23 | ✅ Done | `c37a565`: teste novo da INOV-11 com o erro na solução e o título afirmado pelo `value` (`tasks.md:771`, `:796`) |
| T24 | ✅ Done | `8f329ea`: `_is_administrador` exige `is_authenticated` antes do perfil (`contas/admin.py:19-22`) e os cinco `has_*_permission` passam por ele (`:24-37`); teste novo `test_anonimo_ve_o_login_do_admin` (`contas/tests/test_admin_perfil.py:125-134`). `tasks.md:808`, Done when todo marcado |

`tasks.md:13`: `Status: Em UAT — PASS na iteração 2; T24 corrige o primeiro achado do UAT`. Nenhuma task bloqueada ou parcial. As tabelas de conferência do `tasks.md` (Granularity, Diagram-Definition Cross-Check, Test Co-location) ainda param na T23; a T24 só aparece no Phase Execution Map (`tasks.md:849`, `:860`). `validate_tasks.py cadastro-inovacao`: 0 erros, 2 avisos (T2 sem teste, já aceito; T24 com código e teste no `Where`, que é a co-locação exigida).

---

## Spec-Anchored Acceptance Criteria

### T24: AUTH-21, INOV-20 e INOV-21

Caminhos relativos a `contas/tests/`, salvo indicação. Relidos no HEAD `8f329ea`.

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --------- | -------------------- | ----------------------- | ------ |
| AUTH-21, ramo do redirecionamento, visitante anônimo (achado do UAT) | `autenticacao/spec.md:196`: quem não abre a área de administração é redirecionado ao login. A AC não fala do anônimo; a leitura do teste é que o login para onde se redireciona precisa abrir | `test_admin_perfil.py:131` - `GET /admin/` com `follow=True`; `:132` - `redirect_chain == [("/admin/login/?next=/admin/", 302)]`; `:133` - `status_code == 200`; `:134` - `b'name="username"' in content` | ✅ PASS · ⚠️ Spec-precision gap (anônimo fora do texto da AC) |
| AUTH-21, ramo do redirecionamento, USUARIO sem staff | 302 para o login do admin | `test_admin_perfil.py:121` - `status_code == 302`; `:122` - `Location.startswith("/admin/login/")` | ✅ PASS (sem mudança) |
| AUTH-21, ramo 403, USUARIO com staff forjando a troca de perfil | 403 e o perfil persistido não muda | `test_admin_perfil.py:162` - `403`; `:164` - `perfil == USUARIO` (própria conta); `:173`, `:175` - o mesmo sobre a conta alheia | ✅ PASS (sem mudança) |
| AUTH-22 | só ADMINISTRADOR abre as telas de usuário; USUARIO com staff e todas as permissões de modelo é negado | `test_admin_perfil.py:73-74` - 404 no índice do app, 403 nas outras 5 telas; `:82-83` - exclusão forjada 403 e conta mantida; `:91` - ADMINISTRADOR promovido, 200 nas 6 telas; `:188-190` - o mesmo POST passa para o ADMINISTRADOR | ✅ PASS (sem mudança) |
| INOV-20 | não ADMINISTRADOR: 403 em lista, inclusão, alteração e exclusão de Unidade e Categoria | `inovacoes/tests/test_admin_listas.py:62` - `403` nas 4 telas × 2 modelos; `:76-77`, `:86-88`, `:97-98` - POSTs forjados, 403 e nada muda | ✅ PASS (arquivo sem mudança desde a iteração 2) |
| INOV-21 | ADMINISTRADOR lista, inclui e renomeia | `inovacoes/tests/test_admin_listas.py:108-109`, `:118-119`, `:129-131` | ✅ PASS (sem mudança) |

**Os três perfis continuam iguais.** O helper só acrescenta `is_authenticated and` antes de `is_administrador` (`contas/admin.py:22`). Para um usuário autenticado, `is_authenticated` é sempre `True`, então o valor devolvido é o mesmo de antes nos três casos: USUARIO com staff recebe `False` (403 nas telas, 404 no índice), USUARIO sem staff nem chega ao mixin (o `AdminSite.has_permission` exige `is_active and is_staff`, `django/contrib/admin/sites.py:207`, e redireciona), ADMINISTRADOR recebe `True`. Os 108 testes de `contas/tests/` e `test_admin_listas.py` que já existiam passam sem alteração (T24, Done when 3), e os mutantes S2 e S3 abaixo provam que eles distinguem o perfil.

**Outros caminhos com `is_administrador`.** `grep -rn is_administrador` em `*.py` e `*.html` fora do `.venv` acha só `contas/admin.py:19-37`, a propriedade em `contas/models.py:85` e o `save()` em `contas/models.py:80`, que consulta `self` (uma conta real, nunca o `request.user`). Nenhum template, view ou context processor consulta o perfil do `request.user`. Não há outro caminho exposto ao `AnonymousUser`.

**Por que o anônimo só chega ao mixin pelo login.** Toda view do admin passa pelo `admin_view`, que redireciona antes de chamar o `ModelAdmin` quando `has_permission` é falso (`sites.py:207`, `sites.py:234`). O `AnonymousUser` tem `is_staff = False`. O único caminho que chama o mixin com ele é o `each_context` do login (`sites.py:343`), que monta a lista de apps em `_build_app_dict` (`sites.py:488`).

### F2: INOV-01 a INOV-43

As 43 ACs ficam como na iteração 2. Evidência de que não foram tocadas: `git diff --stat c37a565..8f329ea` só lista `contas/admin.py`, `contas/tests/test_admin_perfil.py` e arquivos de `.specs/`; nenhum arquivo de `inovacoes/`, `templates/` ou `config/` mudou, então os números de linha abaixo continuam valendo. O texto das ACs em `spec.md` também não mudou (o diff só troca `Implementing` por `Verified` e as linhas de status e cobertura). A única produção alterada, `contas/admin.py`, sustenta a INOV-20 e a INOV-21, rechecadas acima.

Caminhos relativos a `inovacoes/tests/`, salvo indicação. Cada linha foi relida no HEAD `c37a565` (iteração 2). Os números de linha de `test_views_cadastro.py` mudaram desde a iteração 1 por causa dos dois testes novos.

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| INOV-01 | 200 e exatamente os 7 campos editáveis | `test_views_cadastro.py:39` - `status_code == 200`; `:40` - `list(form.fields) == CAMPOS`; `:43` - `name="{campo}"` presente; `:45` - `autor`/`status`/`data_criacao` ausentes; `test_forms.py:48` | ✅ PASS |
| INOV-02 | exatamente 1 registro com os valores enviados, sem espaços nas pontas | `test_views_cadastro.py:50` - envio com `"  v  "`; `:52` - `count() == 1`; `:55` - cada texto `== dados[campo]`; `:56-57` - `unidade_id`/`categoria_id`; `test_forms.py:83` | ✅ PASS (payload: os 7 campos afirmados por valor) |
| INOV-03 | 302 para a home interna | `test_views_cadastro.py:62` - `assertRedirects(post, "/", fetch_redirect_response=False)` (302 é o padrão) | ✅ PASS |
| INOV-04 | autor = conta de quem enviou | `test_views_cadastro.py:75-78` - `antiga`, `quem_envia` e `nova` criadas nessa ordem, login com a do meio; `:81` - `autor == quem_envia`; `:82` - `autor not in (antiga, nova)`; `:68` e `:118` - `autor == conta logada` | ✅ PASS (mata V2b e o "maior `pk`") |
| INOV-05 | status `Em teste` e data de criação = agora do servidor | `test_views_cadastro.py:91` - `status == StatusInovacao.EM_TESTE`; `:92` - `antes <= data_criacao <= depois`; `test_models.py:28`, `:38` | ✅ PASS |
| INOV-06 | autor/status/data forjados ignorados | `test_views_cadastro.py:99` - POST com `autor=outro.pk`, `status=VALIDADA`, `data_criacao=2020-01-01`; `:104` - `autor == autor`; `:105` - `status == EM_TESTE`; `:106` - `data_criacao >= antes`; `test_forms.py:103-106` | ✅ PASS |
| INOV-07 | anônimo GET/POST → login com `next=/inovacoes/nova/`, nada gravado | `test_views_cadastro.py:124-125` - GET → `"/entrar/?next=/inovacoes/nova/"`; `:133` - POST → mesmo destino; `:134` - `not Inovacao.objects.exists()`; `contas/tests/test_controle_acesso.py:71` - varredura de rotas | ✅ PASS |
| INOV-08 | `USUARIO` e `ADMINISTRADOR` cadastram igual | `test_views_cadastro.py:110` - parametrizado nos dois perfis; `:117` - redirect `/`; `:118` - `autor == conta` | ✅ PASS |
| INOV-09 | 200 e a mensagem exata de cada um dos 6 obrigatórios, junto do campo | `test_views_cadastro.py:157` - `200`; `:158-160` - `form.errors ==` as 6 mensagens; `:163-164` - mensagem dentro de `id_{campo}_error`; `test_forms.py:58` - um campo por vez | ✅ PASS |
| INOV-10 | só espaços conta como vazio | `test_forms.py:65` - `"   \t  "`; `:68-71` - `errors ==` as 4 mensagens de obrigatório | ✅ PASS |
| INOV-11 | todo campo re-renderizado com o valor enviado, incluindo unidade e categoria | `test_views_cadastro.py:203` - erro só na solução; `:205` - `errors == {"solucao": [...]}`; `:207` - `_valor_do_input(html, "titulo") == dados["titulo"]`; `:208` - contato; `:209-210` - `<option value="{pk}" selected>`; `:212` - problema e resultado no `textarea`. Complemento: `:184-190` - título vazio, solução preservada no `textarea` (`:190`) | ✅ PASS (os 7 campos afirmados por valor entre os dois testes; mata T4) |
| INOV-12 | "Use no máximo N caracteres (você digitou M)." com N e M reais | `test_forms.py:119-128` - parametrizado nos 5 campos, `errors == {campo: ["Use no máximo {limite} caracteres (você digitou {limite + 1})."]}`; `:136` - no limite passa | ✅ PASS (o template que põe o erro junto do campo é o mesmo da INOV-09) |
| INOV-13 | envio rejeitado não grava | `test_views_cadastro.py:165`, `:191`, `:213` - `not exists()`; `:223`, `:242` - `count() == 1` | ✅ PASS |
| INOV-14 | resultado vazio é aceito | `test_forms.py:91` - `is_valid()`; `:92` - `cleaned_data["resultado"] == ""`; `test_models.py:45` - `full_clean()` sem erro | ✅ PASS |
| INOV-15 | selects só com os registros, em ordem alfabética | `test_forms.py:153-154` - `choices == ["Selecione…", *OPCOES_INICIAIS]`; `test_models.py:20` - ordem da consulta padrão | ✅ PASS |
| INOV-16 | FK não nulas no banco | `test_constraints.py:38-39` - `IntegrityError` com `unidade`/`categoria` `None` | ✅ PASS |
| INOV-17 | "Selecione uma unidade da lista." / "Selecione uma categoria da lista." no campo | `test_forms.py:161-164` - `errors == {campo: [MENSAGEM_FORA_DA_LISTA[campo]]}`; `:170-173` - item apagado entre GET e POST | ✅ PASS |
| INOV-18 | banco vazio + migrations = as 5 categorias e as 5 unidades | `test_migracoes.py:24` - `_nomes(Categoria) == CATEGORIAS`; `:29` - `_nomes(Unidade) == UNIDADES`; `:36-37` - carga idempotente | ✅ PASS |
| INOV-19 | exclusão de item em uso recusada, item mantido | `test_models.py:53-55` - `ProtectedError` e `exists()`; `test_admin_listas.py:144-147` - admin: 200, `context["protected"]` com a inovação, item existe | ✅ PASS |
| INOV-20 | não `ADMINISTRADOR`: 403 em lista, inclusão, alteração e exclusão | `test_admin_listas.py:62` - `status_code == 403` nas 4 telas × 2 modelos, com `is_staff` e todas as permissões de modelo (`:34-40`); POST forjado: `:76-77`, `:86-88`, `:97-98` - 403 e nada muda | ✅ PASS |
| INOV-21 | `ADMINISTRADOR` lista, inclui e renomeia | `test_admin_listas.py:108-109` - 200 e item na lista; `:118-119` - 302 e item criado; `:129-131` - 302 e `nome == "Teste Renomeado"` | ✅ PASS |
| INOV-22 | mensagem exata no campo título, caixa ignorada | `test_views_cadastro.py:221` - `200`; `:222` - `errors == {"titulo": [MENSAGEM_DUPLICADO]}`; `test_models.py:76-77` - `message_dict` e `code == "titulo_duplicado"` | ✅ PASS |
| INOV-23 | espaços nas pontas não escapam | `test_views_cadastro.py:219` - `"  controle de caixa  "`; `:222` - mesma mensagem | ✅ PASS |
| INOV-24 | mesmo título em outra unidade é aceito | `test_views_cadastro.py:232-233` - redirect `/` e `count() == 2`; `test_constraints.py:72` | ✅ PASS |
| INOV-25 | corrida: 1 gravado, o outro 200 + mensagem, nunca 500 | `test_views_cadastro.py:252` - validação neutralizada, `save()` bate na constraint real do PostgreSQL; `:254` - `200`; `:255` - `errors == {"titulo": [MENSAGEM_DUPLICADO]}`; `:256` - resumo; `:257` - `count() == 1`; `:271-272` - outra violação vira 500 | ✅ PASS (corrida simulada; o ramo do `IntegrityError` é o real) |
| INOV-26 | unicidade por constraint no banco | `test_constraints.py:62-63` - `IntegrityError` com `"CONTROLE DE CAIXA"` gravado direto | ✅ PASS |
| INOV-27 | acentos contam | `test_constraints.py:78-80` - "Solução…" e "Solucao…" gravam, `count() == 2` | ✅ PASS |
| INOV-28 | "Inovação “<título>” cadastrada com sucesso." com o título salvo, no `role="status"` da página do redirect | `test_views_cadastro.py:284` - `redirect_chain == [("/", 302)]`; `:285-286` - texto exato dentro de `_regiao_de_status`, título enviado com espaços (`:282`) | ✅ PASS |
| INOV-29 | a mensagem não reaparece ao recarregar | `test_views_cadastro.py:292-293` - `"cadastrada com sucesso" not in html` no segundo GET | ✅ PASS |
| INOV-30 | resumo exato em `role="alert"` antes do primeiro campo | `test_views_cadastro.py:172` - `RESUMO in _trecho_do_alerta(html)`; `:173` - `index('role="alert"') < index('id="id_titulo"')`; `:178-179` - ausente sem erro | ✅ PASS |
| INOV-31 | todo campo com `<label>` visível por `for`/`id` | `test_views_acessibilidade.py:68` - 7 controles; `:70-71` - `id` e rótulo com texto em `rotulos[id]`; `:74` - label não escondido | ✅ PASS |
| INOV-32 | `required` e "(obrigatório)" no rótulo dos obrigatórios | `test_views_acessibilidade.py:82-83` - obrigatórios; `:85-86` - o opcional sem nenhum dos dois; `test_forms.py:112` | ✅ PASS |
| INOV-33 | `aria-invalid="true"` e `aria-describedby` com o id do erro | `test_forms.py:208` - `aria-invalid == "true"`; `:209` - `"id_titulo_error" in aria-describedby`; `:211` - mensagem no elemento de erro; `:224` - campo sem erro sem `aria-invalid` | ✅ PASS |
| INOV-34 | só controles nativos, sem `tabindex` positivo | `test_views_acessibilidade.py:92-97` - sem `role` de controle, `onclick`, `contenteditable`; `tabindex <= 0`; `:99` - `input/select/textarea/button` presentes | ✅ PASS |
| INOV-35 | foco visível em todo controle e no Cancelar | `test_views_acessibilidade.py:105-108` - regra universal `:focus-visible` com `outline: Npx solid`, nenhum `outline: none/0` | ✅ PASS (inspeção do CSS; o efeito visual fica para o UAT) |
| INOV-36 | link "Cancelar" para a home | `test_views_cadastro.py:323` - exatamente 1 link "Cancelar"; `:330` - `href="/"` | ✅ PASS |
| INOV-37 | segue o link: home, nada gravado, sem confirmação | `test_views_cadastro.py:336` - sem `onclick`; `:338-341` - GET do `href` → 200, `nucleo/home.html`, `not exists()` | ✅ PASS |
| INOV-38 | link "Cadastrar inovação" → `/inovacoes/nova/` no cabeçalho de toda página, autenticado | `test_views_cabecalho.py:20-24` - regex do link dentro do `<nav>` do `<header>` em `/` e `/inovacoes/nova/`; `:30-31` - ausente para anônimo | ✅ PASS (as duas únicas páginas internas; o link vive no `base.html`) |
| INOV-39 | "<nome completo> (<e-mail>)" ou "<username> (<e-mail>)" | `test_views_cadastro.py:304` - `== "Ana Souza (ana@x.com)"`; `:311` - `== "bruno (bruno@x.com)"` | ✅ PASS |
| INOV-40 | o contato digitado é o gravado | `test_views_cadastro.py:318` - `contato == "Equipe de Tesouraria (tesouraria@x.com)"` | ✅ PASS |
| INOV-41 | ajuda com exemplo abaixo de cada campo, no `aria-describedby` | `test_forms.py:188-197` - parametrizado nos 7: `"Ex.:"` no texto (`:195`); controle antes da ajuda (`:196`); `id_{campo}_helptext` no `aria-describedby` (`:197`) | ✅ PASS |
| INOV-42 | banco fora: página 500 do projeto, nada gravado, sem detalhes de conexão | `test_views_erro_500.py:44` - `DEBUG is False`; `:46` - `500`; `:47` - `assertTemplateUsed("500.html")`; `:48` - `not exists()`; `:55-64` - host, usuário, senha, `OperationalError`, `Traceback` ausentes | ✅ PASS (falha simulada em `Inovacao.save`) |
| INOV-43 | segundo envio idêntico recusado com a mensagem da INOV-22 | `test_views_cadastro.py:238` - 1º redirect; `:240-242` - 2º: 200, `errors == {"titulo": [MENSAGEM_DUPLICADO]}`, `count() == 1` | ✅ PASS |

**Status**: ✅ 43/43 ACs da F2 batem com o resultado da spec · 0 gaps · 0 spec-precision gaps na F2. ⚠️ 1 spec-precision gap na T24: a AUTH-21 não fala do visitante anônimo no admin.

**Payload/conjunção (INOV-02, 04, 05, 06)**: INOV-02 afirma os 7 campos por valor e a contagem exata. INOV-04 afirma o valor (`autor == quem_envia`) num cenário com uma conta mais antiga e uma mais nova, e afirma que não é nenhuma delas. INOV-05 afirma o valor do status e a janela da data. INOV-06 afirma os três campos do sistema por valor depois de forjá-los.

---

## Discrimination Sensor

### Iteração 3 (T24)

Worktree temporário `<scratchpad>/verifier-wt3` (`git worktree add --detach … HEAD`, HEAD `8f329ea`), com `.env` copiado. O pytest do `.venv` da raiz rodou com cwd no scratch; `contas` resolveu para `<scratchpad>/verifier-wt3/contas/__init__.py`. Baseline no scratch: 206 passed. Um script aplicava cada mutação em `contas/admin.py` por substituição de texto (mutação sem efeito seria marcada inválida; nenhuma foi), rodava `contas/tests` e `inovacoes/tests/test_admin_listas.py` (109 testes) e restaurava o arquivo num `finally`. `git status --porcelain` do scratch vazio no fim.

| # | File:line | Description | Killed? |
| - | --------- | ----------- | ------- |
| S1 | `contas/admin.py:24-37` | volta ao check sem guarda: os cinco `has_*` devolvem `request.user.is_administrador` | ✅ Killed (`test_anonimo_ve_o_login_do_admin`) |
| S2 | `contas/admin.py:22` | `_is_administrador` devolve só `is_authenticated` | ✅ Killed (24 testes: AUTH-21, AUTH-22 e INOV-20) |
| S3 | `contas/admin.py:22` | `_is_administrador` devolve `is_staff` | ✅ Killed (os mesmos 24) |
| S4 | `contas/admin.py:22` | anônimo vira administrador: `not is_authenticated or is_administrador` | ⚪ Survived, **equivalente** |
| S5 | `contas/admin.py:27-37` | guarda só em `has_module_permission`; as outras quatro sem guarda | ⚪ Survived, **equivalente** |
| S6 | `contas/admin.py:24-25` | `has_module_permission` → `return True` (o A3 da iteração 2) | ⚪ Survived, **equivalente** |
| S7 | `contas/admin.py:24-25` | guarda só nas quatro; `has_module_permission` sem guarda | ✅ Killed (`test_anonimo_ve_o_login_do_admin`) |

**Por que S4, S5 e S6 são equivalentes.** O anônimo só chega ao mixin em `_build_app_dict` (`sites.py:488`), chamado pelo login. Ali, `has_module_permission` vem primeiro e um `False` pula o modelo antes de `get_model_perms` (`sites.py:489-490`), então S5 nunca chama as quatro sem guarda; em S6, `get_model_perms` chama as quatro com guarda, que devolvem `False`, e o modelo é pulado em `sites.py:494-497`. Em S4, a lista de apps do contexto do login passa a ter `contas` e `inovacoes`, mas o `login.html` esvazia o bloco que a mostraria (`django/contrib/admin/templates/admin/login.html:15`). Conferi no scratch: com S4, `/admin/login/` responde 200 sem nenhum link `/admin/contas/` ou `/admin/inovacoes/`, e `/admin/`, `/admin/contas/usuario/` e `/admin/inovacoes/unidade/add/` continuam 302 para o login, porque o `admin_view` barra o anônimo antes do `ModelAdmin` (`sites.py:207`). Nenhuma resposta muda; não é teste fraco. Um `assert resposta.context["available_apps"] == []` mataria S4, mas afirmaria um detalhe interno que a spec não define, então não vira fix task.

**Sensor depth**: P0 (autorização). 7 mutações manuais cobrindo a guarda do anônimo, o critério de perfil e a ordem em que o Django consulta os `has_*`.
**Result**: 4/4 mutantes não equivalentes mortos; 3 equivalentes (S4, S5, S6). PASS ✅

**Isolamento**: `git status --porcelain` do worktree real antes = vazio; depois de `git worktree remove --force` e `git worktree prune` = vazio. **Idêntico**. `git worktree list` mostra só o worktree principal (`8f329ea [main]`). `git stash list` vazio; nenhum `git stash` usado.

### Iteração 2 (F2)

Worktree temporário `<scratchpad>/verifier-wt` (`git worktree add --detach … HEAD`, HEAD `c37a565`), com `.env` copiado. O pytest do `.venv` da raiz rodou com cwd no scratch; `inovacoes` e `contas` resolveram para `<scratchpad>/verifier-wt/…/__init__.py`. Baseline no scratch: 205 passed. Um script aplicava cada mutação por substituição exata de texto (contagem 1 conferida, senão a mutação era marcada inválida e não rodava), rodava a suíte inteira e restaurava o arquivo original num `finally`. `git status --porcelain` do scratch vazio no fim.

Além de repetir V2b e T4, o conjunto é novo: nenhuma das outras 19 mutações repete a lista da iteração 1.

| # | File:line | Description | Killed? |
| - | --------- | ----------- | ------- |
| V2b | `inovacoes/views.py:35` | autor = conta de **menor** `pk` do banco (`get_user_model().objects.order_by("pk").first()`) | ✅ Killed (`test_autor_e_quem_enviou_e_nao_outra_conta_do_banco`) |
| T4 | `inovacoes/views.py:33` | `form_invalid` que apaga `titulo` dos dados antes de renderizar (erros e demais atributos iguais) | ✅ Killed (`test_erro_em_outro_campo_preserva_o_titulo_e_os_demais`) |
| V7 | `inovacoes/views.py:31` | contato pré-preenchido como `nome <email>` | ✅ Killed (os 2 testes da INOV-39) |
| V8 | `inovacoes/views.py:44` | condição invertida: `!=` → `==` (duplicado sobe como 500, outra violação vira erro de título) | ✅ Killed (corrida e outra violação) |
| V9 | `inovacoes/views.py:47` | ramo da corrida redireciona à home em vez de re-renderizar | ✅ Killed (`test_corrida_…_nao_500`) |
| V10 | `inovacoes/views.py:49` | `messages.success` removido | ✅ Killed (INOV-28) |
| M1 | `inovacoes/models.py:125-126` | outros erros de constraint descartados no remapeamento | ✅ Killed (`test_outro_erro_de_constraint_continua_geral`) |
| M2 | `inovacoes/models.py:92` | `"unidade"` tirado da `UniqueConstraint` (título único global) | ✅ Killed (INOV-24 na view) |
| M3 | `inovacoes/models.py:70` | `blank=True` tirado de `resultado` | ✅ Killed (7 testes, incluindo INOV-14 e INOV-32) |
| M4 | `inovacoes/models.py:82` | `auto_now_add` → default fixo `2020-01-01` | ✅ Killed (4 testes da INOV-05/06) |
| F6 | `inovacoes/forms.py:86` | `resultado` sem o limite de 5000 no form | ✅ Killed (INOV-12 `[resultado]`) |
| F7 | `inovacoes/forms.py:10` | N e M trocados na mensagem de tamanho | ✅ Killed (INOV-12 nos 5 campos) |
| A2 | `inovacoes/admin.py:11` | `UnidadeAdmin` sem o `AcessoSomenteAdministradorMixin` | ✅ Killed (12 testes da INOV-20 para Unidade) |
| A3 | `contas/admin.py:19-20` (hoje `:24-25`) | `has_module_permission` → `return True` | ⚪ Survived, **equivalente** (veja abaixo; repetido como S6 na iteração 3) |
| A4 | `contas/admin.py:22-23` (hoje `:27-28`) | `has_view_permission` → `is_administrador or obj is not None` (tela de alteração em modo leitura) | ✅ Killed (INOV-20 `alteracao` × 2 e AUTH da F1) |
| T5 | `inovacoes/templates/inovacoes/inovacao_form.html:9-13` | resumo `role="alert"` movido para depois dos campos | ✅ Killed (`test_envio_invalido_mostra_o_resumo_antes_do_primeiro_campo`) |
| T6 | `inovacoes/templates/inovacoes/inovacao_form.html:25` | "Cancelar" aponta para `inovacoes:nova` | ✅ Killed (INOV-36 e INOV-37) |
| T7 | `inovacoes/templates/inovacoes/campo.html:13-15` | ajuda renderizada antes do controle | ✅ Killed (INOV-41 nos 7 campos e INOV-33). Primeira tentativa marcada inválida pelo script (padrão de texto meu errado); corrigida e rodada |
| T8 | `templates/base.html:35` | `role="status"` → `role="log"` | ✅ Killed (INOV-28) |
| T9 | `templates/base.html:11` | `:focus-visible` → `a:focus-visible` (só links) | ✅ Killed (INOV-35) |
| G1 | `inovacoes/migrations/0004_listas_iniciais.py:5` | "RH" tirado da carga inicial | ✅ Killed (INOV-18 e INOV-15) |

**Por que A3 é equivalente**: `has_module_permission` só é lido em `AdminSite._build_app_dict` (`django/contrib/admin/sites.py:488`). Logo depois, `sites.py:492-497` pula o modelo quando `get_model_perms(request)` não tem nenhum `True`, e para quem não é `ADMINISTRADOR` as quatro `has_*` do mixin devolvem `False`. Para o `ADMINISTRADOR`, o original já devolve `True`. Nenhuma tela, índice ou resposta muda, então nenhum teste pode matar esse mutante. Não é teste fraco.

**Sensor depth**: P0-full (autorização e integridade de dados). Sem ferramenta de mutação instalada; 21 mutações manuais válidas cobrindo view (autor, contato, ramo do `IntegrityError`, re-render, mensagem), modelo (remapeamento, escopo da constraint, `blank`, data), form (limite, mensagem), admin (mixin nas listas, `has_view_permission`, `has_module_permission`), templates (resumo, Cancelar, ordem da ajuda, `role="status"`, foco) e a carga inicial.
**Result**: 20/20 mutantes não equivalentes mortos; 1 equivalente (A3). PASS ✅

**Isolamento**: `git status --porcelain` do worktree real antes = vazio; depois de `git worktree remove --force` e `git worktree prune` = vazio. **Idêntico**. `git worktree list` mostra só o worktree principal. `git stash list` vazio; nenhum `git stash` usado.

---

## Interactive UAT Results

O Verifier roda sem usuário; o UAT é conduzido pelo orquestrador. **Status (2026-10-02): em andamento, pausado depois da preparação; itens 1–21 pendentes.**

**Preparação**

| # | Test | Result | Details |
| - | ---- | ------ | ------- |
| P1 | `migrate` no banco local | ✅ Pass | `inovacoes 0001–0004` aplicadas; 5 unidades e 5 categorias da carga presentes |
| P2 | Abrir `/admin/` sem sessão para criar as contas | ❌ Issue → corrigido na T24 | `GET /admin/login/` respondia HTTP 500 (`AttributeError` em `AnonymousUser.is_administrador`) - Severity: Blocker. Corrigido em `8f329ea`; prova em `contas/tests/test_admin_perfil.py:132-134` |
| P3 | Contas de teste pelo admin | ⚠️ Parcial | `maria` (USUARIO, "Maria Silva") e `joao` (ADMINISTRADOR, sem nome, `is_staff` ligado sozinho) criadas. Falta marcar **Membro da equipe** na `maria`: sem `is_staff`, os itens 8 e 21 dão 302 para o login em vez de 403 |

**Roteiro** (contas `maria` e `joao`; esperado conforme as ACs citadas)

| # | Test | Esperado | Result |
| - | ---- | -------- | ------ |
| 1 | Anônimo abre `/inovacoes/nova/` | Login com `?next=/inovacoes/nova/` (INOV-07) | ⏳ |
| 2 | Entra como `maria` nesse login | Cai em `/inovacoes/nova/` (AUTH-10) | ⏳ |
| 3 | Sai e entra com `MARIA@kira.local` | Home "Olá, maria" (AUTH-02) | ⏳ |
| 4 | Senha errada | Só "Usuário ou senha inválidos." (AUTH-03) | ⏳ |
| 5 | Senha vazia | Erro no campo; identificador preservado (AUTH-04) | ⏳ |
| 6 | Logado, abre `/entrar/` | Vai para a home (AUTH-12) | ⏳ |
| 7 | Sair; Voltar e recarregar | "Sessão encerrada."; página interna manda ao login (AUTH-13, AUTH-14) | ⏳ |
| 8 | `maria` em `/admin/contas/usuario/` | 403 (AUTH-22) | ⏳ |
| 9 | Cabeçalho logado | Link "Cadastrar inovação" (INOV-38) | ⏳ |
| 10 | Abre o formulário | 7 campos; selects com "Selecione…" e listas em ordem alfabética; ajuda em cada campo (INOV-01, 15, 41) | ⏳ |
| 11 | Contato | "Maria Silva (maria@kira.local)", editável (INOV-39) | ⏳ |
| 12 | Apaga o contato e envia vazio | Resumo no topo + as seis mensagens de campo; nada gravado (INOV-09, 13, 30) | ⏳ |
| 13 | Título, unidade e categoria preenchidos; Problema só com espaços | Erro em Problema; os demais preservados (INOV-10, 11) | ⏳ |
| 14 | Salva "Triagem de chamados" na Sede, Resultado vazio | Home com "Inovação “Triagem de chamados” cadastrada com sucesso."; some no F5; banco com autor `maria`, `EM_TESTE`, data (INOV-03–05, 14, 28, 29) | ⏳ |
| 15 | "TRIAGEM DE CHAMADOS" na Sede | Recusado com a mensagem da INOV-22 | ⏳ |
| 16 | Mesmo título na Filial Norte; "Triagem de chamádos" na Sede | Ambos aceitos (INOV-24, 27) | ⏳ |
| 17 | Só teclado: Tab do topo, setas nos selects, Enter | Ordem de foco = ordem visual; foco visível; envio funciona (INOV-34, 35; Success Criterion de teclado) | ⏳ |
| 18 | Só teclado: erro visível; Tab até "Cancelar" + Enter | Erro junto ao campo; volta à home sem salvar (INOV-33, 37; Success Criterion de teclado) | ⏳ |
| 19 | `joao` cadastra uma inovação | Igual à `maria`; contato "joao (joao@kira.local)" (INOV-08, 39) | ⏳ |
| 20 | `joao` no admin de Unidades e Categorias | Lista, inclui, renomeia; excluir "Sede" em uso é recusado (INOV-19, 21) | ⏳ |
| 21 | `maria` em `/admin/inovacoes/unidade/` | 403 (INOV-20) | ⏳ |

Fora do roteiro por desenho, cobertos por teste automatizado: limites de 150/5000 caracteres (o `maxlength` do HTML impede digitar além), banco indisponível (INOV-42) e envios concorrentes (INOV-25, 43).

---

## Code Quality

| Principle | Status |
| --------- | ------ |
| Minimum code | ✅ T24: um helper de uma linha (`contas/admin.py:19-22`) chamado pelos cinco `has_*`; nada além |
| Surgical changes | ✅ `8f329ea` só toca `contas/admin.py`, `contas/tests/test_admin_perfil.py`, `tasks.md` e `STATE.md` |
| No scope creep | ✅ Nada novo além da fix task |
| Matches patterns | ✅ O teste novo segue os vizinhos do mesmo arquivo (cliente do Django, `redirect_chain` e `status_code` afirmados por valor) |
| Spec-anchored outcome check (asserted values match spec) | ✅ 43/43 da F2; T24 com ⚠️ spec-precision gap (anônimo fora da AUTH-21) |
| Per-layer Coverage Expectation met | ✅ `/inovacoes/nova/`: happy, edge e erro; modelo e form com 1:1 nas ACs; admin: os três perfis e agora o anônimo |
| Every test maps to a spec requirement - no unclaimed tests | ✅ O teste novo cita AUTH-21 e o achado do UAT na docstring (`test_admin_perfil.py:126-130`) |
| Documented guidelines followed: `tasks.md` (Test Coverage Matrix) | ✅ |

---

## Edge Cases

- [x] INOV-42 banco indisponível: 500, `500.html`, nada gravado, sem detalhes da conexão (`test_views_erro_500.py:46-48`, `:63-64`).
- [x] INOV-43 duplo envio: o segundo recusado com a mensagem da INOV-22, 1 registro (`test_views_cadastro.py:240-242`).
- [x] Item de lista apagado entre GET e POST (`test_forms.py:170-173`).
- [x] Outra violação de integridade não vira erro de título (`test_views_cadastro.py:271-272`).
- [x] Visitante anônimo no admin: redirecionado a `/admin/login/?next=/admin/`, que abre com 200 e o campo `username` (`contas/tests/test_admin_perfil.py:132-134`).

---

## Gate Check

- **Gate command**: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q` (worktree real)
- **Result**: exit 0. `ruff check`: All checks passed · `ruff format --check`: 71 files already formatted · `makemigrations --check`: No changes detected · `pytest -q`: 206 passed, 0 failed, 0 skipped (10.88 s)
- **Test count before feature**: 84 (fim da F1)
- **Test count after feature**: 206 (203 na iteração 1, 205 na iteração 2, +1 da T24)
- **Delta**: +122. Nenhum teste removido nem enfraquecido; o diff da T24 em `test_admin_perfil.py` só adiciona linhas
- **Skipped tests**: nenhum
- **Failures**: nenhuma

---

## Fix Plans

Nenhum obrigatório. Duas sugestões, sem bloquear o PASS:

### Sugestão 1: AC para o visitante anônimo no admin

- **Root cause**: a AUTH-21 (`autenticacao/spec.md:196`) descreve só o USUARIO autenticado. Nada na spec dizia que o login do admin precisa abrir para quem chega sem sessão, e foi por aí que o 500 passou pela F1 e pelas duas iterações da F2.
- **Fix task**: acrescentar à F1 uma AC do tipo "WHEN a visitor without a session opens any Django admin URL THEN the system SHALL redirect to `/admin/login/?next=<url>` and that page SHALL respond 200 with the login form", e apontar `test_admin_perfil.py:125` para ela.
- **Priority**: Minor (o comportamento já está provado; falta o texto)

### Sugestão 2: tabelas de conferência do `tasks.md`

- **Root cause**: a T24 entrou no Phase Execution Map, mas não nas tabelas de Granularity, Diagram-Definition Cross-Check e Test Co-location.
- **Fix task**: acrescentar a linha da T24 nas três tabelas.
- **Priority**: Cosmetic

---

## Requirement Traceability Update

Proposta. O Verifier **não** edita `spec.md`.

| Requirement | Previous Status | New Status |
| ----------- | --------------- | ---------- |
| INOV-01 … INOV-43 | Verified | ✅ Verified (mantido) |
| AUTH-21 (F1) | Verified | ✅ Verified (o ramo de redirecionamento agora tem o login aberto provado; ⚠️ texto sem o anônimo) |

---

## Histórico

- **Iteração 1** (HEAD `49c82ee`): FAIL ❌. 41/43 ACs, 27/29 mutantes mortos. Sobreviveram V2b (INOV-04, autor = conta mais antiga) e T4 (INOV-11, título perdido no re-render). Viraram T22 e T23, só em teste.
- **Iteração 2** (HEAD `c37a565`): PASS ✅. 43/43 ACs, V2b e T4 mortos, 20/20 mutantes não equivalentes mortos.
- **Iteração 3** (HEAD `8f329ea`): PASS ✅. UAT achou o 500 no `GET /admin/login/` para o anônimo; T24 corrigiu. 4/4 mutantes não equivalentes mortos, 3 equivalentes; 1 spec-precision gap na AUTH-21 (anônimo).

---

## Summary

**Overall**: ✅ Ready (evidência: `contas/tests/test_admin_perfil.py:132`, `contas/admin.py:22`, `inovacoes/tests/test_admin_listas.py:62`)

**Spec-anchored check**: 43/43 ACs da F2 matched spec outcome · AUTH-21/AUTH-22/INOV-20/INOV-21 inalteradas · 1 spec-precision gap (anônimo fora da AUTH-21)
**Sensor**: 7 mutações na iteração 3; 4 mortas, 3 equivalentes (S4, S5, S6)
**Gate**: 206 passed, 0 failed

**What works**: o login do admin abre para quem chega sem sessão; USUARIO com staff continua com 403 (404 no índice), USUARIO sem staff continua redirecionado, ADMINISTRADOR continua liberado; todo o cadastro da F2 como na iteração 2.

**Issues found**: nenhum bloqueante. Spec-precision gap na AUTH-21 (Sugestão 1) e tabelas do `tasks.md` sem a T24 (Sugestão 2).

**Next steps**: o orquestrador segue com o UAT interativo e decide se abre a Sugestão 1 como ajuste de spec da F1.
