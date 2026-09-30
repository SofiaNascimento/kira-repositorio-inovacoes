# Cadastro de Inovação (F2) Validation

**Date**: 2026-09-29
**Iteration**: 1
**Spec**: `.specs/features/cadastro-inovacao/spec.md`
**Diff range**: `b5dc1e8..HEAD` em `main` (HEAD = `49c82ee`), 21 commits (`0060f1e` … `49c82ee`). Código analisado: `inovacoes/` (models, forms, views, urls, admin, migrations 0001–0004, templates `inovacao_form.html` e `campo.html`), `contas/admin.py`, `config/settings.py`, `config/urls.py`, `templates/base.html`.
**Verifier**: independent sub-agent (author ≠ verifier)

**Verdict**: FAIL ❌

O gate passa (203 passed) e 41 de 43 ACs batem com o resultado da spec. Dois mutantes sobreviveram e mostram duas ACs sem evidência completa. **V2b**: gravar como autor a conta mais antiga do banco, e não quem enviou o formulário, passa em toda a suíte (INOV-04). Em todo teste de cadastro, quem envia é também a conta de menor `pk`. **T4**: descartar o título digitado quando o formulário volta com erro também passa (INOV-11). O único teste de preservação é justamente o que deixa o título vazio. Os 28 outros mutantes morreram. Os dois gaps pedem só testes mais fortes; nenhum código de produção está errado.

---

## Task Completion

| Task | Status | Notes |
| ---- | ------ | ----- |
| T1 | ✅ Done | Mixin extraído; `contas/tests/` inalterado e verde. Mutantes K1–K4 morrem nos testes da F1 e da F2 |
| T2–T8 | ✅ Done | App, listas, `Inovacao`, constraints, remapeamento do erro, carga inicial, admin das listas |
| T9–T12 | ✅ Done | Form: campos, rótulos, obrigatórios, limites, selects, ajuda |
| T13–T17 | ✅ Done | View, resposta a envio inválido, corrida, mensagem de sucesso, contato pré-preenchido |
| T18–T21 | ✅ Done | Acessibilidade, Cancelar, cabeçalho, banco indisponível |

As 21 tasks estão `✅ Complete` em `tasks.md`, sem bloqueio nem conclusão parcial. O cabeçalho diz `Status: Implementada (21/21) — aguardando o Verifier` (`tasks.md:13`).

---

## Spec-Anchored Acceptance Criteria

Caminhos relativos a `inovacoes/tests/`, salvo indicação. Cada linha foi relida no HEAD `49c82ee`.

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| INOV-01 | 200 e exatamente os 7 campos editáveis | `test_views_cadastro.py:39` - `status_code == 200`; `:40` - `list(form.fields) == CAMPOS`; `:43` - `name="{campo}"` presente; `:45` - `autor`/`status`/`data_criacao` ausentes; `test_forms.py:48` | ✅ PASS |
| INOV-02 | exatamente 1 registro com os valores enviados, sem espaços nas pontas | `test_views_cadastro.py:52` - `count() == 1`; `:55` - cada texto `== dados[campo]` (enviado com `"  v  "`, `:50`); `:56-57` - `unidade_id`/`categoria_id`; `test_forms.py:83` | ✅ PASS (payload: os 7 campos afirmados por valor) |
| INOV-03 | 302 para a home interna | `test_views_cadastro.py:62` - `assertRedirects(post, "/", fetch_redirect_response=False)` (status 302 é o padrão do `assertRedirects`) | ✅ PASS |
| INOV-04 | autor = conta de quem enviou | `test_views_cadastro.py:68` - `Inovacao.objects.get().autor == autor`; `:104` - `autor == conta` | ❌ GAP. Mutante V2b sobrevive: nos três testes, quem envia é a conta de menor `pk`, então "autor = conta mais antiga" passa |
| INOV-05 | status `Em teste` e data de criação = agora do servidor | `test_views_cadastro.py:77` - `status == StatusInovacao.EM_TESTE`; `:78` - `antes <= data_criacao <= depois`; `test_models.py:28`, `:38` | ✅ PASS |
| INOV-06 | autor/status/data forjados ignorados | `test_views_cadastro.py:85` - POST com `autor=outro.pk`, `status=VALIDADA`, `data_criacao=2020-01-01`; `:90` - `autor == autor`; `:91` - `status == EM_TESTE`; `:92` - `data_criacao >= antes`; `test_forms.py:103-106` | ✅ PASS (mata V2c, "conta mais nova", porque `outro` é criado depois) |
| INOV-07 | anônimo GET/POST → login com `next=/inovacoes/nova/`, nada gravado | `test_views_cadastro.py:110-111` - GET → `"/entrar/?next=/inovacoes/nova/"`; `:119` - POST → mesmo destino; `:120` - `not Inovacao.objects.exists()`; `contas/tests/test_controle_acesso.py:71` - varredura inclui a rota | ✅ PASS |
| INOV-08 | `USUARIO` e `ADMINISTRADOR` cadastram igual | `test_views_cadastro.py:96` - parametrizado nos dois perfis; `:103` - redirect `/`; `:104` - `autor == conta` | ✅ PASS |
| INOV-09 | 200 e a mensagem exata de cada um dos 6 obrigatórios, junto do campo | `test_views_cadastro.py:143` - `200`; `:144-146` - `form.errors == {campo: [mensagem]}` para os 6; `:149-150` - mensagem dentro de `id_{campo}_error`; `test_forms.py:58` - um campo por vez | ✅ PASS |
| INOV-10 | só espaços conta como vazio | `test_forms.py:65` - `"   \t  "`; `:68-71` - `errors ==` as 4 mensagens de obrigatório | ✅ PASS |
| INOV-11 | todo campo re-renderizado com o valor enviado, incluindo unidade e categoria | `test_views_cadastro.py:172-173` - `<option value="{pk}" selected>`; `:174` - `value="{contato}"`; `:176` - os 3 `textarea`. O título é o campo esvaziado (`:170`), então nunca é afirmado | ❌ GAP. Mutante T4 (título descartado no re-render) sobrevive; nenhum teste afirma o título preservado depois de um erro |
| INOV-12 | "Use no máximo N caracteres (você digitou M)." com N e M reais | `test_forms.py:119-128` - parametrizado nos 5 campos, `errors == {campo: ["Use no máximo {limite} caracteres (você digitou {limite + 1})."]}`; `:136` - no limite passa | ✅ PASS (nível do form; o template de campo que põe o erro junto do campo é o mesmo da INOV-09) |
| INOV-13 | envio rejeitado não grava | `test_views_cadastro.py:151`, `:177`, `:187`, `:206` - `not exists()` / `count() == 1` | ✅ PASS |
| INOV-14 | resultado vazio é aceito | `test_forms.py:91` - `is_valid()`; `:92` - `cleaned_data["resultado"] == ""`; `test_models.py:45` - `full_clean()` sem erro | ✅ PASS (nível form/modelo) |
| INOV-15 | selects só com os registros, em ordem alfabética | `test_forms.py:153-154` - `choices == ["Selecione…", *OPCOES_INICIAIS]`; `test_models.py:20` - ordem da consulta padrão | ✅ PASS |
| INOV-16 | FK não nulas no banco | `test_constraints.py:38-39` - `IntegrityError` ao gravar com `unidade`/`categoria` `None` | ✅ PASS |
| INOV-17 | "Selecione uma unidade da lista." / "Selecione uma categoria da lista." no campo | `test_forms.py:161-164` - `errors == {campo: [MENSAGEM_FORA_DA_LISTA[campo]]}`; `:170-173` - item apagado entre GET e POST | ✅ PASS |
| INOV-18 | banco vazio + migrations = as 5 categorias e as 5 unidades | `test_migracoes.py:24` - `_nomes(Categoria) == CATEGORIAS`; `:29` - `_nomes(Unidade) == UNIDADES`; `:36-37` - carga idempotente | ✅ PASS |
| INOV-19 | exclusão de item em uso recusada, item mantido | `test_models.py:53-55` - `ProtectedError` e `exists()`; `test_admin_listas.py:144-147` - admin: 200, `context["protected"]` com a inovação, item existe | ✅ PASS |
| INOV-20 | não `ADMINISTRADOR`: 403 em lista, inclusão, alteração e exclusão | `test_admin_listas.py:62` - `status_code == 403` nas 4 telas × 2 modelos, com `is_staff` e todas as permissões de modelo (`:34-40`); POST forjado: `:76-77`, `:86-88`, `:97-98` - 403 e nada muda | ✅ PASS |
| INOV-21 | `ADMINISTRADOR` lista, inclui e renomeia | `test_admin_listas.py:108-109` - 200 e item na lista; `:118-119` - 302 e item criado; `:129-131` - 302 e `nome == "Teste Renomeado"` | ✅ PASS |
| INOV-22 | mensagem exata no campo título, caixa ignorada | `test_views_cadastro.py:185` - `200`; `:186` - `errors == {"titulo": [MENSAGEM_DUPLICADO]}`; `test_models.py:76` - `message_dict == {"titulo": [...]}` | ✅ PASS |
| INOV-23 | espaços nas pontas não escapam | `test_views_cadastro.py:183` - `"  controle de caixa  "`; `:186` - mesma mensagem | ✅ PASS |
| INOV-24 | mesmo título em outra unidade é aceito | `test_views_cadastro.py:196-197` - redirect `/` e `count() == 2`; `test_constraints.py:72` | ✅ PASS |
| INOV-25 | corrida: 1 gravado, o outro 200 + mensagem, nunca 500 | `test_views_cadastro.py:216` - validação neutralizada, `save()` bate na constraint real do PostgreSQL; `:218` - `200`; `:219` - `errors == {"titulo": [MENSAGEM_DUPLICADO]}`; `:221` - `count() == 1`; `:235` - outra violação vira 500 | ✅ PASS (corrida simulada; o ramo do `IntegrityError` é o real) |
| INOV-26 | unicidade por constraint no banco | `test_constraints.py:62-63` - `IntegrityError` com `"CONTROLE DE CAIXA"` gravado direto | ✅ PASS |
| INOV-27 | acentos contam | `test_constraints.py:78-80` - "Solução…" e "Solucao…" gravam, `count() == 2` | ✅ PASS |
| INOV-28 | "Inovação “<título>” cadastrada com sucesso." com o título salvo, no `role="status"` da página do redirect | `test_views_cadastro.py:248` - `redirect_chain == [("/", 302)]`; `:249-250` - texto exato dentro de `_regiao_de_status`, com o título enviado com espaços (`:246`) | ✅ PASS |
| INOV-29 | a mensagem não reaparece ao recarregar | `test_views_cadastro.py:256-257` - `"cadastrada com sucesso" not in html` no segundo GET | ✅ PASS |
| INOV-30 | resumo exato em `role="alert"` antes do primeiro campo | `test_views_cadastro.py:158` - `RESUMO in _trecho_do_alerta(html)`; `:159` - `index('role="alert"') < index('id="id_titulo"')`; `:164-165` - ausente sem erro | ✅ PASS |
| INOV-31 | todo campo com `<label>` visível por `for`/`id` | `test_views_acessibilidade.py:68` - 7 controles; `:70-71` - `id` e rótulo com texto em `rotulos[id]` (chaveado pelo `for`); `:74` - label não escondido | ✅ PASS |
| INOV-32 | `required` e "(obrigatório)" no rótulo dos obrigatórios | `test_views_acessibilidade.py:82-83` - obrigatórios; `:85-86` - o opcional sem nenhum dos dois; `test_forms.py:112` | ✅ PASS |
| INOV-33 | `aria-invalid="true"` e `aria-describedby` com o id do erro | `test_forms.py:208` - `aria-invalid == "true"`; `:209` - `"id_titulo_error" in aria-describedby`; `:224` - campo sem erro sem `aria-invalid` | ✅ PASS |
| INOV-34 | só controles nativos, sem `tabindex` positivo | `test_views_acessibilidade.py:92-97` - sem `role` de controle, `onclick`, `contenteditable`; `tabindex <= 0`; `:99` - `input/select/textarea/button` presentes | ✅ PASS |
| INOV-35 | foco visível em todo controle e no Cancelar | `test_views_acessibilidade.py:105-108` - regra universal `:focus-visible` com `outline: Npx solid`, nenhum `outline: none/0` | ✅ PASS (inspeção do CSS; o efeito visual fica para o UAT) |
| INOV-36 | link "Cancelar" para a home | `test_views_cadastro.py:287` - exatamente 1 link "Cancelar"; `:294` - `href="/"` | ✅ PASS |
| INOV-37 | segue o link: home, nada gravado, sem confirmação | `test_views_cadastro.py:300` - sem `onclick`; `:303-305` - GET do `href` → 200, `nucleo/home.html`, `not exists()` | ✅ PASS |
| INOV-38 | link "Cadastrar inovação" → `/inovacoes/nova/` no cabeçalho de toda página, autenticado | `test_views_cabecalho.py:20-24` - regex do link dentro de `<nav>` do `<header>` em `/` e `/inovacoes/nova/`; `:30-31` - ausente para anônimo | ✅ PASS (as duas únicas páginas internas; o link vive no `base.html`) |
| INOV-39 | "<nome completo> (<e-mail>)" ou "<username> (<e-mail>)" | `test_views_cadastro.py:268` - `== "Ana Souza (ana@x.com)"`; `:275` - `== "bruno (bruno@x.com)"` | ✅ PASS |
| INOV-40 | o contato digitado é o gravado | `test_views_cadastro.py:282` - `contato == "Equipe de Tesouraria (tesouraria@x.com)"` | ✅ PASS |
| INOV-41 | ajuda com exemplo abaixo de cada campo, no `aria-describedby` | `test_forms.py:188-197` - parametrizado nos 7: `"Ex.:"` no texto; controle antes da ajuda; `id_{campo}_helptext` no `aria-describedby` | ✅ PASS |
| INOV-42 | banco fora: página 500 do projeto, nada gravado, sem detalhes de conexão | `test_views_erro_500.py:44` - `DEBUG is False`; `:46` - `500`; `:47` - `assertTemplateUsed("500.html")`; `:48` - `not exists()`; `:55-64` - host, usuário, senha, `OperationalError`, `Traceback` ausentes | ✅ PASS (falha simulada em `Inovacao.save`) |
| INOV-43 | segundo envio idêntico recusado com a mensagem da INOV-22 | `test_views_cadastro.py:202` - 1º redirect; `:204-206` - 2º: 200, `errors == {"titulo": [MENSAGEM_DUPLICADO]}`, `count() == 1` | ✅ PASS |

**Status**: ❌ 41/43 ACs batem com o resultado da spec · 2 gaps (INOV-04, INOV-11), ambos revelados por mutante sobrevivente · 0 spec-precision gaps (a spec fixa textos, códigos e atributos de todas as 43).

**Payload/conjunção (INOV-02, 04, 05, 06)**: INOV-02 afirma os 7 campos por valor e a contagem exata. INOV-05 afirma o valor do status e a janela da data. INOV-06 afirma os três campos do sistema por valor depois de forjá-los. INOV-04 afirma o valor (`autor == autor`), mas num cenário que não separa "quem enviou" de "a conta mais antiga". Esse é o gap 1.

---

## Discrimination Sensor

Worktree temporário `<scratchpad>/verifier-wt` (`git worktree add --detach … HEAD`, HEAD `49c82ee`), com `.env` copiado. O pytest do `.venv` da raiz rodou com cwd no scratch; `import inovacoes` resolveu para `<scratchpad>/verifier-wt/inovacoes/__init__.py`. Baseline no scratch: 203 passed. Cada mutante foi aplicado por substituição exata de texto (contagem 1 conferida), a suíte inteira rodou, e o arquivo original voltou do backup em memória. `git status --porcelain` do scratch vazio no fim.

| # | File:line | Description | Killed? |
| - | --------- | ----------- | ------- |
| K1 | `contas/admin.py:23` | mixin `has_view_permission` → `return True` | ✅ Killed (telas de lista/alteração de F1 e F2) |
| K2 | `contas/admin.py:32` | mixin `has_delete_permission` → `return True` | ✅ Killed (exclusão das listas e de usuário, POST forjado) |
| K3 | `contas/admin.py:29` | mixin `has_change_permission` → `request.user.is_staff` | ✅ Killed (11 testes, incluindo promoção forjada da F1) |
| K4 | `contas/admin.py:26` | mixin `has_add_permission` → `return True` | ✅ Killed (`novo` e inclusão forjada das listas) |
| R1 | `inovacoes/models.py:124` | duplicado remapeado para `NON_FIELD_ERRORS` em vez de `titulo` | ✅ Killed (modelo, INOV-22, INOV-43) |
| R2 | `inovacoes/models.py:123` | `if duplicados:` → `if False:` (erro de duplicado descartado) | ✅ Killed (`test_titulo_duplicado_acusa_o_erro_no_campo_titulo`). Na view, o ramo do `IntegrityError` mascara o mutante; só o teste de modelo o pega |
| R3 | `inovacoes/models.py:91` | `Lower("titulo")` → `"titulo"` (validação sensível à caixa) | ✅ Killed (teste de modelo; a constraint da migration continua `Lower`) |
| V1 | `inovacoes/views.py:44` | captura qualquer `IntegrityError` como título duplicado | ✅ Killed (`test_outra_violacao_de_integridade_nao_vira_titulo_duplicado`) |
| V2 | `inovacoes/views.py:35` | autor = `type(request.user).objects…first()` | ⚪ Inválido: `type()` de `SimpleLazyObject` levanta `AttributeError`, e o mutante morre pelo motivo errado. Substituído por V2b/V2c |
| V2b | `inovacoes/views.py:35` | autor = conta de **menor** `pk` do banco | ❌ **Survived** (203 passed) → Fix 1 |
| V2c | `inovacoes/views.py:35` | autor = conta de **maior** `pk` do banco | ✅ Killed (`test_autor_status_e_data_forjados_no_post_sao_ignorados`) |
| V3 | `inovacoes/views.py:30` | sem fallback para o username | ✅ Killed (`test_contato_usa_o_username_quando_a_conta_nao_tem_nome`) |
| V4 | `inovacoes/views.py:49` | mensagem com o título cru do POST, não o salvo | ✅ Killed (`test_cadastro_bem_sucedido_confirma_com_o_titulo_salvo`) |
| V5 | `inovacoes/views.py:25` | `success_url` → `inovacoes:nova` | ✅ Killed (6 testes) |
| V6 | `inovacoes/views.py:37` | `transaction.atomic()` removido | ✅ Killed (corrida e outra violação: a transação do teste quebra) |
| O1 | `inovacoes/models.py:32` | `ordering = ["-nome"]` | ✅ Killed (8 testes: select, migração, modelo) |
| O2 | `inovacoes/models.py:66` | `unidade` `PROTECT` → `CASCADE` | ✅ Killed (modelo e admin, INOV-19) |
| O3 | `inovacoes/models.py:73` | status default → `VALIDADA` | ✅ Killed (5 testes) |
| T1 | `inovacao_form.html:9` | resumo só com `form.non_field_errors` | ✅ Killed (INOV-30, corrida) |
| T2 | `templates/base.html:19-23` | `<nav>` fora do `{% if user.is_authenticated %}` | ✅ Killed (`test_cabecalho_anonimo_nao_mostra_o_link`) |
| T3 | `campo.html:14` | `{{ field.errors }}` removido | ✅ Killed (INOV-09 e INOV-33) |
| T4 | `campo.html:13` | título renderizado sem valor sempre que o form tem erro (demais atributos iguais) | ❌ **Survived** (203 passed) → Fix 2 |
| F1 | `inovacoes/forms.py:85` | `strip = False` em todo campo | ✅ Killed (5 testes: INOV-02, 10, 23, 28) |
| F2 | `inovacoes/forms.py:82` | `empty_label` → `"---------"` | ✅ Killed (select da INOV-15) |
| F3 | `inovacoes/forms.py:9` | `LIMITE_TEXTO_LONGO = 5001` | ✅ Killed (INOV-12 nos 3 textos longos) |
| F4 | `inovacoes/forms.py:24` | `"status"` em `Meta.fields` | ✅ Killed (43 testes) |
| F5 | `inovacoes/forms.py:56` | `invalid_choice` da unidade com outro texto | ✅ Killed (INOV-17) |
| A1 | `inovacoes/forms.py:20` | `use_required_attribute = False` | ✅ Killed (INOV-32) |
| L1 | `inovacoes/urls.py:8` | rota envolvida em `login_not_required` | ✅ Killed (varredura da F1 e os dois testes da INOV-07) |

**Sensor depth**: P0-full (autorização e integridade de dados). Sem ferramenta de mutação instalada; 30 mutações manuais (1 inválida, 29 válidas) cobrindo o mixin do admin (as 4 `has_*`), o remapeamento de `validate_constraints`, o ramo do `IntegrityError`, a atribuição do autor, o fallback do contato, a mensagem de sucesso, o destino, a transação, a ordenação, o `PROTECT`, o default de status, os templates (resumo, erros, valor, cabeçalho), `strip`, `empty_label`, limite de 5000, `Meta.fields`, mensagens, `required` e o default-deny.
**Result**: 27/29 killed, 2 sobreviventes reais (V2b, T4). FAIL ❌

**Isolamento**: `git status --porcelain` do worktree real antes = vazio; depois de `git worktree remove --force` e `git worktree prune` = vazio. **Idêntico**. `git worktree list` mostra só o worktree principal; o diretório do scratch não existe mais. `git stash list` vazio; nenhum `git stash` usado.

---

## Interactive UAT Results

Não realizado. O Verifier roda sem usuário. A F2 é voltada ao usuário (formulário, teclado, foco visível), e o UAT fica a cargo do orquestrador depois dos fixes.

---

## Code Quality

| Principle | Status |
| --------- | ------ |
| Minimum code | ✅ View de 50 linhas sobre `CreateView`; form declarativo; um template de campo copiado do Django só para mudar a ordem (INOV-41) |
| Surgical changes | ✅ Fora de `inovacoes/`: mixin extraído sem mudar comportamento (`contas/admin.py`), 1 linha em settings, 1 em urls, 4 no `base.html` |
| No scope creep | ✅ Unicidade de nome nas listas (`ItemDeLista`) não é AC, mas está no design (`design.md:114`, `tasks.md:184`); `Inovacao` fora do admin como pede o Out of Scope (`test_admin_listas.py:152`) |
| Matches patterns | ✅ Mesmo padrão da F1: mensagens em constraint, `role="status"`, varredura de acesso, AD-007 aplicada nos dois `ModelAdmin` |
| Spec-anchored outcome check (asserted values match spec) | ❌ 2 gaps (INOV-04, INOV-11) |
| Per-layer Coverage Expectation met | ⚠️ Views: happy, edge e erro cobertos para `/inovacoes/nova/`, menos a preservação do título e um autor que não seja a conta mais antiga |
| Every test maps to a spec requirement - no unclaimed tests | ✅ Os poucos testes sem ID (`test_formulario_sem_erro_nao_mostra_o_resumo`, `test_texto_exatamente_no_limite_e_aceito`, `test_campo_sem_erro_nao_fica_invalido`, constraints de nome e de status) são o lado negativo ou a borda de uma AC, ou uma decisão do design |
| Documented guidelines followed: `tasks.md` (Test Coverage Matrix, `tasks.md:36-41`) | ✅ |

---

## Edge Cases

- [x] INOV-42 banco indisponível: 500, `500.html`, nada gravado, sem detalhes da conexão (`test_views_erro_500.py:46-48`, `:63-64`).
- [x] INOV-43 duplo envio: o segundo recusado com a mensagem da INOV-22, 1 registro (`test_views_cadastro.py:204-206`).
- [x] Item de lista apagado entre GET e POST (`test_forms.py:170-173`).
- [x] Outra violação de integridade não vira erro de título (`test_views_cadastro.py:235-236`).

---

## Gate Check

- **Gate command**: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q` (worktree real)
- **Result**: `ruff check`: All checks passed · `ruff format --check`: 70 files already formatted · `makemigrations --check`: No changes detected · `pytest -q`: 203 passed, 0 failed, 0 skipped (11.13 s)
- **Test count before feature**: 84 (fim da F1)
- **Test count after feature**: 203
- **Delta**: +119. `contas/tests/` sem teste removido nem enfraquecido (T1 só moveu código)
- **Skipped tests**: nenhum
- **Failures**: nenhuma

---

## Fix Plans

### Fix 1: autor não discriminado da conta mais antiga (V2b, INOV-04)

- **Root cause**: em `test_views_cadastro.py:65-68`, `:81-92` e `:96-104`, quem envia o formulário é sempre a conta criada primeiro. Um `form_valid` que gravasse como autor a conta de menor `pk` (ou uma conta fixa criada cedo, como um admin inicial) passaria.
- **Fix task**: no teste da INOV-04, criar outra conta **antes** do autor e logar com a segunda (por exemplo, criar `bruno` antes de `force_login(autor)`, ou logar como a conta nova); afirmar `Inovacao.objects.get().autor == <conta logada>` e `!= <conta anterior>`.
- **Done when**: V2b morre; gate verde.
- **Priority**: Major (autoria é a trilha da RN08 e a base da autorização da F4).

### Fix 2: título digitado não afirmado depois de um erro (T4, INOV-11)

- **Root cause**: `test_views_cadastro.py:168-177` esvazia justamente o título (`:170`) e afirma os outros 6 campos. Nenhum teste afirma o `value` do título num formulário rejeitado.
- **Fix task**: no teste da INOV-11, provocar o erro em outro campo (ex.: `solucao = ""`) e afirmar `value="{dados["titulo"]}"` no `input` do título, além dos demais campos preenchidos.
- **Done when**: T4 morre; gate verde.
- **Priority**: Major (RF13 é Essencial: não perder o que foi digitado).

---

## Requirement Traceability Update

Proposta. O Verifier **não** edita `spec.md`.

| Requirement | Previous Status | New Status |
| ----------- | --------------- | ---------- |
| INOV-01, 02, 03 | Implementing | ✅ Verified |
| INOV-04 | Implementing | ❌ Needs Fix (Fix 1) |
| INOV-05 … 10 | Implementing | ✅ Verified |
| INOV-11 | Implementing | ❌ Needs Fix (Fix 2) |
| INOV-12 … 43 | Implementing | ✅ Verified |

---

## Summary

**Overall**: ❌ Not Ready - FAIL (evidência: `inovacoes/tests/test_views_cadastro.py:68`, `inovacoes/tests/test_views_cadastro.py:170`)

**Spec-anchored check**: 41/43 ACs matched spec outcome · 0 spec-precision gaps · 2 gaps (INOV-04, INOV-11)
**Sensor**: 27/29 mutations killed (2 sobreviventes reais: V2b, T4; 1 mutação inválida descartada: V2)
**Gate**: 203 passed, 0 failed

**What works**: cadastro com os 7 campos, `strip`, status e data do sistema, campos forjados ignorados, default-deny com `next`, as seis mensagens de obrigatório, os limites com N e M reais, listas controladas em ordem alfabética com carga inicial exata, `PROTECT`, admin das listas fechado para quem não é `ADMINISTRADOR` (mixin discriminado nas 4 `has_*`), unicidade de título por unidade no banco e no campo, corrida e duplo envio sem 500, mensagens de sucesso e de resumo, acessibilidade do formulário, Cancelar, link no cabeçalho, contato pré-preenchido, página 500 sem vazamento.

**Issues found**: 2 testes fracos (Fix 1, Fix 2). Nenhum defeito no código de produção.

**Next steps**: o orquestrador cria as fix tasks T22 (Fix 1) e T23 (Fix 2), executa e redespacha o Verifier (iteração 2 de no máximo 3).
