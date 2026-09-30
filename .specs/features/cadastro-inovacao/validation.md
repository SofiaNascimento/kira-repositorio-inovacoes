# Cadastro de Inovação (F2) Validation

**Date**: 2026-09-29
**Iteration**: 2
**Spec**: `.specs/features/cadastro-inovacao/spec.md`
**Diff range**: `b5dc1e8..HEAD` em `main` (HEAD = `c37a565`), 24 commits (`0060f1e` … `c37a565`). As correções da iteração 1 são `999d080` (T22) e `c37a565` (T23), só em teste (`inovacoes/tests/test_views_cadastro.py`, mais `tasks.md` e `STATE.md`). Código analisado: `inovacoes/` (models, forms, views, urls, admin, migrations 0001–0004, templates `inovacao_form.html` e `campo.html`), `contas/admin.py`, `config/settings.py`, `config/urls.py`, `templates/base.html`.
**Verifier**: independent sub-agent (author ≠ verifier)

**Verdict**: PASS ✅

O gate passa (205 passed). As 43 ACs batem com o resultado da spec. Os dois gaps da iteração 1 fecharam: o mutante V2b (autor = conta de menor `pk`) agora morre em `test_autor_e_quem_enviou_e_nao_outra_conta_do_banco`, e o T4 (título re-renderizado vazio depois de um erro) morre em `test_erro_em_outro_campo_preserva_o_titulo_e_os_demais`. Das 21 mutações válidas, 20 morreram. A que sobreviveu (A3) é equivalente: não muda nenhum comportamento observável (veja o sensor). O código de produção não mudou desde a iteração 1.

---

## Task Completion

| Task | Status | Notes |
| ---- | ------ | ----- |
| T1–T21 | ✅ Done | Sem mudança desde a iteração 1: `git diff 49c82ee..c37a565` só toca `inovacoes/tests/test_views_cadastro.py` e arquivos de `.specs/`; nenhum arquivo de produção |
| T22 | ✅ Done | `999d080`: teste novo da INOV-04 com contas criadas antes e depois de quem envia (`tasks.md:742`, `:767`) |
| T23 | ✅ Done | `c37a565`: teste novo da INOV-11 com o erro na solução e o título afirmado pelo `value` (`tasks.md:771`, `:796`) |

`tasks.md:13`: `Status: Implementada (23/23)`. Nenhuma task bloqueada ou parcial.

---

## Spec-Anchored Acceptance Criteria

Caminhos relativos a `inovacoes/tests/`, salvo indicação. Cada linha foi relida no HEAD `c37a565`. Os números de linha de `test_views_cadastro.py` mudaram desde a iteração 1 por causa dos dois testes novos.

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

**Status**: ✅ 43/43 ACs batem com o resultado da spec · 0 gaps · 0 spec-precision gaps (a spec fixa textos, códigos e atributos de todas as 43).

**Payload/conjunção (INOV-02, 04, 05, 06)**: INOV-02 afirma os 7 campos por valor e a contagem exata. INOV-04 afirma o valor (`autor == quem_envia`) num cenário com uma conta mais antiga e uma mais nova, e afirma que não é nenhuma delas. INOV-05 afirma o valor do status e a janela da data. INOV-06 afirma os três campos do sistema por valor depois de forjá-los.

---

## Discrimination Sensor

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
| A3 | `contas/admin.py:19-20` | `has_module_permission` → `return True` | ⚪ Survived, **equivalente** (veja abaixo) |
| A4 | `contas/admin.py:22-23` | `has_view_permission` → `is_administrador or obj is not None` (tela de alteração em modo leitura) | ✅ Killed (INOV-20 `alteracao` × 2 e AUTH da F1) |
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

Não realizado. O Verifier roda sem usuário. A F2 é voltada ao usuário (formulário, teclado, foco visível), e o UAT fica a cargo do orquestrador.

---

## Code Quality

| Principle | Status |
| --------- | ------ |
| Minimum code | ✅ Sem mudança de produção desde a iteração 1; os fixes são dois testes e um helper `_valor_do_input` |
| Surgical changes | ✅ `999d080` e `c37a565` só tocam `test_views_cadastro.py`, `tasks.md` e `STATE.md` |
| No scope creep | ✅ Nada novo além das duas fix tasks |
| Matches patterns | ✅ `_valor_do_input` segue o `_valor_do_contato` já existente (`test_views_cadastro.py:296-299`) |
| Spec-anchored outcome check (asserted values match spec) | ✅ 43/43 |
| Per-layer Coverage Expectation met | ✅ `/inovacoes/nova/`: happy, edge e erro; modelo e form com 1:1 nas ACs |
| Every test maps to a spec requirement - no unclaimed tests | ✅ Os dois testes novos citam INOV-04 e INOV-11 na docstring |
| Documented guidelines followed: `tasks.md` (Test Coverage Matrix) | ✅ |

---

## Edge Cases

- [x] INOV-42 banco indisponível: 500, `500.html`, nada gravado, sem detalhes da conexão (`test_views_erro_500.py:46-48`, `:63-64`).
- [x] INOV-43 duplo envio: o segundo recusado com a mensagem da INOV-22, 1 registro (`test_views_cadastro.py:240-242`).
- [x] Item de lista apagado entre GET e POST (`test_forms.py:170-173`).
- [x] Outra violação de integridade não vira erro de título (`test_views_cadastro.py:271-272`).

---

## Gate Check

- **Gate command**: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q` (worktree real)
- **Result**: `ruff check`: All checks passed · `ruff format --check`: 71 files already formatted · `makemigrations --check`: No changes detected · `pytest -q`: 205 passed, 0 failed, 0 skipped (10.94 s)
- **Test count before feature**: 84 (fim da F1)
- **Test count after feature**: 205 (203 na iteração 1, +2 dos fixes)
- **Delta**: +121. Nenhum teste removido nem enfraquecido; os fixes só adicionam
- **Skipped tests**: nenhum
- **Failures**: nenhuma

---

## Fix Plans

Nenhum.

---

## Requirement Traceability Update

Proposta. O Verifier **não** edita `spec.md`.

| Requirement | Previous Status | New Status |
| ----------- | --------------- | ---------- |
| INOV-01 … INOV-43 | Implementing | ✅ Verified |

---

## Histórico

- **Iteração 1** (HEAD `49c82ee`): FAIL ❌. 41/43 ACs, 27/29 mutantes mortos. Sobreviveram V2b (INOV-04, autor = conta mais antiga) e T4 (INOV-11, título perdido no re-render). Viraram T22 e T23, só em teste.
- **Iteração 2** (HEAD `c37a565`): PASS ✅. 43/43 ACs, V2b e T4 mortos, 20/20 mutantes não equivalentes mortos.

---

## Summary

**Overall**: ✅ Ready (evidência: `inovacoes/tests/test_views_cadastro.py:81`, `inovacoes/tests/test_views_cadastro.py:207`)

**Spec-anchored check**: 43/43 ACs matched spec outcome · 0 spec-precision gaps
**Sensor**: 21 mutações válidas; 20 mortas, 1 equivalente (A3)
**Gate**: 205 passed, 0 failed

**What works**: tudo o que a iteração 1 já mostrava, mais o autor distinguido de outras contas do banco e o título preservado quando o erro está em outro campo.

**Issues found**: nenhum.

**Next steps**: o orquestrador marca INOV-01…43 como Verified em `spec.md` e conduz o UAT interativo (teclado, foco visível, leitor de tela).
