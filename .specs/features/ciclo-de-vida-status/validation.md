# Ciclo de Vida do Status (F5) Validation

**Date**: 2026-10-18
**Iteration**: 3, a última antes de escalar (a iteração 1 fica abaixo, intacta; as iterações 2 e 3 estão em [Iteração 2](#iteração-2) e [Iteração 3](#iteração-3), no fim)
**Spec**: `.specs/features/ciclo-de-vida-status/spec.md` (STAT-01 … STAT-37)
**Diff range (iteração 3)**: feature `6616da1..5e0fd25` em `main` (HEAD = `5e0fd25`). Correção: `5e0fd25` (T14), só em `inovacoes/tests/test_views_sistema_design.py` e no `tasks.md`. `git diff f48bb1a..5e0fd25 -- . ':!inovacoes/tests' ':!.specs'` vazio: nenhum código de produção mudou desde a iteração 1.
**Diff range (iteração 2)**: feature `6616da1..ef25406` em `main` (HEAD = `ef25406`). Correções: `f1d3de1` (T12) e `ef25406` (T13), só em `inovacoes/tests/`. `git diff f48bb1a..ef25406 -- ':!inovacoes/tests' ':!.specs'` vazio: nenhum código de produção mudou desde a iteração 1.
**Diff range (iteração 1)**: `6616da1..f48bb1a` em `main` (HEAD = `f48bb1a`), 11 commits (T1 `fd1ee9c`, T2 `0f09ede`, T3 `0a6307d`, T4 `8ad7dad`, T5 `10603fd`, T6 `73eccf5`, T7 `9f417d1`, T8 `4a48733`, T9 `0b4f8f4`, T10 `36fa95a`, T11 `f48bb1a`). 17 arquivos, +1604/−115. Produção: `inovacoes/models.py`, `views.py`, `urls.py`, `migrations/0007_mudancadestatus.py`, `templates/inovacoes/inovacao_detail.html`, `inovacao_status.html` e `templates/kira.css`.
**Verifier**: independent sub-agent (author ≠ verifier)

**Verdict**: FAIL ❌ na iteração 6 (passe de design, HEAD `e71c6b5`), **com risco residual de teste aceito pelo usuário em 2026-10-18** — ver [Decisão do usuário — passe de design](#decisão-do-usuário--passe-de-design-2026-10-18). O veredito do Verifier não foi reescrito; o passe foi fechado por decisão, não por PASS. FAIL ❌ na iteração 6 (passe de design, HEAD `e71c6b5`, última rodada autorizada) — ver [Iteração 6](#iteração-6--passe-de-design-2026-10-18). As seis re-injeções da iteração 5 (E2b, E9, E10, E11, E16, E17) morrem, e T21–T22 não enfraquecem nada. Mas sobrevivem nove mutantes novos cobertos por AC, todos por lacuna de teste. A causa é uma só: as asserções de "exibido" leem o HTML cru por regex, não o DOM exposto. Os mutantes: um `<div hidden>` em volta da seção inteira (F1); textos e controles dentro de um comentário HTML, de `<template>` ou de `<details>` fechado (F2, F3, F4, F5, F16, F18); `HIDDEN` em maiúsculas (F14); e "Avan&ccedil;ar" com entidade fora da seção, para staff (F17). As ACs afetadas são STAT-01, 03, 04, 05, 38, 39, 40 e 41. O template de produção não tem nenhum desses defeitos. O risco residual A6/A7 da STAT-37 continua aceito e não conta. Antes: FAIL ❌ na iteração 5 (passe de design, HEAD `6020a4f`) — ver [Iteração 5](#iteração-5--passe-de-design-2026-10-18). R1, R2 e D12 morrem, e T18–T20 não enfraquecem nada. Mas sobrevivem cinco mutantes novos cobertos por AC, todos por lacuna de teste: E2b (STAT-05, botão fora da seção para staff com próximo estágio), E9 (STAT-03), E10/E11 (STAT-38) e E16 (STAT-40), estes quatro com `hidden` num ancestral ou no próprio elemento. O risco residual A6/A7 da STAT-37 continua aceito e não conta. Antes: FAIL ❌ na iteração 4 (passe de design, HEAD `b246c63`) — ver [Iteração 4](#iteração-4--passe-de-design-2026-10-18). O template cumpre a spec, mas sobrevivem dois mutantes cobertos por AC, os dois por lacuna de teste da T16: R1 (STAT-05) e R2 (STAT-03). O risco residual A6/A7 da STAT-37 continua aceito pelo usuário e não conta como falha nova. Antes: FAIL ❌ na iteração 3 (HEAD `5e0fd25`), **com risco residual aceito pelo usuário em 2026-10-18** — ver [Decisão do usuário](#decisão-do-usuário-2026-10-18). Aquele veredito não foi reescrito: a feature foi fechada por decisão, não por PASS.

**Iteração 3 em resumo:** o gate passa com 685 testes, e o código de produção continua igual ao da iteração 1. A T14 mata a N14, a M27 e a M11 continuam mortas, e a `CADEIA_DO_COMPONENTE` confere com o DOM e o layout reais. Mas a T14 **enfraqueceu uma checagem anterior**. Antes, todo `background*` (inclusive `background-image`) de `.ciclo`/`.historico` tinha de ser `var(--token)` de um fundo do DS-08. Agora (`test_views_sistema_design.py:597-599`), a regra só é conferida se declarar `color`, `background` ou `background-color`. Com isso, **A1** (`.historico li { background-image: linear-gradient(var(--brand-blue), var(--brand-blue)) }`) e **A2** (`background-image: var(--brand-gradient)`) em `templates/kira.css:521` passam a suíte inteira. As duas morriam no teste do `ef25406`, o que prova a regressão. Sobreviveram também **A6** (`ol.historico li { background: var(--brand-blue) }`) e **A7** (`section .ciclo li { color: var(--surface) }`): o teste só lê regras cujo seletor *começa* pela classe (`:536-543`). Essa lacuna já existia antes da T14. A STAT-37 cobre os quatro casos ("every color the cycle control and the history add to `kira.css`"). Resultado: 36/37 ACs, sensor 17/22. Fix 4 abaixo, só de teste. Como esta é a terceira iteração, o próximo passo é decisão do usuário.

**Iteração 2 em resumo:** o gate passa com 685 testes. T12 mata a M11 e T13 mata a M27, e as duas correções afirmam o valor da spec sem enfraquecer nenhuma checagem anterior. Das 15 mutações novas, 14 morrem. A **N14** sobrevive: `.historico li { background: var(--brand-blue) }` (`templates/kira.css:521`) põe o texto do histórico a 2,48:1 e a data a 1,0:1, e a suíte inteira passa. O teste da STAT-37 só confere o par das regras que declaram `color`. Uma regra que só declara fundo não tem o texto herdado conferido, e o `FUNDO_HERDADO` é fixo, não derivado do fundo do ancestral. A STAT-37 cobre o caso ("every color the cycle control and the history add"), então a lacuna é de teste: 36/37 ACs, Fix 3 abaixo. Nenhum código de produção precisa mudar.

**Iteração 1 (registro original):** O gate passa com 684 testes, e 35 das 37 ACs têm evidência `file:line` com o valor da spec afirmado. O código de produção cumpre a spec em tudo o que conferi, inclusive nos dois pontos com lacuna. O FAIL vem do sensor: 2 dos 29 mutantes sobreviveram. **M11**: o detalhe mostra o histórico de *todas* as inovações em vez do histórico só daquela, e a suíte inteira passa (STAT-24, "every history record **of that Inovacao**"). Todo teste do histórico usa uma inovação só, então nenhum distingue "desta inovação" de "de todas". **M27**: `.ciclo li` passa a usar texto branco sobre fundo branco (`color: var(--surface)` sobre `background: var(--surface)`), e o teste da STAT-37 continua verde. O teste confere cada cor isoladamente contra o conjunto de textos e o conjunto de fundos do DS-08, nunca o par que a regra forma, e `surface` está nos dois conjuntos. Os dois viram fix tasks só de teste. Nenhum código de produção precisa mudar.

---

## Task Completion

| Task | Status | Notes |
| ---- | ------ | ----- |
| T1–T11 | ✅ Done | `tasks.md`, 11 de 11 marcadas completas; contagens por task (588 → 684) conferem com o gate |

---

## Spec-Anchored Acceptance Criteria

Caminhos relativos a `inovacoes/tests/`, salvo indicação. Lidos no HEAD `f48bb1a`.

### P1: Ver em que estágio do ciclo a inovação está

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| STAT-01 | h2 "Ciclo de vida"; `ol` com "Em teste", "Validada", "Disponível para replicação" nessa ordem | `test_views_detalhe.py:309` - `findall(h2) == ["Ciclo de vida"]`; `:311` - itens sem o sufixo `== ETAPAS`; `test_views_acessibilidade_alteracao.py:238-251` - `listas == [("ol", "ciclo")]` | ✅ PASS (M15 morta) |
| STAT-02 | "(status atual)" só no estágio gravado | `test_views_detalhe.py:322` - `html.count("(status atual)") == 1`; `:325` - lista inteira igual à esperada, nos 3 status | ✅ PASS (M15 morta) |
| STAT-03 | autor/administrador, status "Em teste" ou "Validada" → link "Avançar para “<próximo>”" → `/inovacoes/<id>/status/` | `test_views_detalhe.py:340` - `_links(secao, f"Avançar para “{proximo}”") == [f"/inovacoes/{pk}/status/"]`, 2 contas × 2 status | ✅ PASS (M3, M14 mortas) |
| STAT-04 | "Último estágio do ciclo." e nenhum link "Avançar", para qualquer conta | `test_views_detalhe.py:350` - `"<p>Último estágio do ciclo.</p>" in secao`; `:351-352` - `"Avançar" not in html`, caminho ausente; autor, administrador e terceiro | ✅ PASS (M4, M14 mortas) |
| STAT-05 | quem não pode alterar não vê o link | `test_views_detalhe.py:362-363` (terceiro, 2 status); `test_views_status.py:335-336` - `nao_autor_usuario` (terceiro, staff, superusuário) | ✅ PASS (M8 morta) |

### P1: Avançar o status um estágio

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| STAT-06 | 200; página "Avançar status"; texto exato; botão "Avançar para “Validada”"; "Cancelar" → `/inovacoes/<id>/` | `test_views_status.py:46` - 200; `:51` - `h1 == ["Avançar status"]`; `:52-55` - texto exato; `:60-61` - um botão submit com o rótulo exato; `:62-65` - `status_visto` oculto com o status gravado; `:66-67` - `cancelar == [f"/inovacoes/{pk}/"]`. Autor (`:70`), segundo passo (`:77`), administrador (`:84`). `<title>` por prefixo (`:50`), ver *Spec-Precision Gaps* | ✅ PASS ⚠️ (M16, M22 mortas) |
| STAT-07 | "Em teste" → "Validada"; 302 a `/inovacoes/<id>/` | `test_views_status.py:175` - `assertRedirects(…, f"/inovacoes/{pk}/", fetch_redirect_response=False)`; `:176` - `_status_no_banco == VALIDADA` | ✅ PASS |
| STAT-08 | "Validada" → "Disponível para replicação"; 302 ao detalhe | `test_views_status.py:204` - `redirect_chain == [(f"/inovacoes/{pk}/", 302)]`; `:205` - `== DISPONIVEL`; `:207` | ✅ PASS |
| STAT-09 | só o próximo estágio; nunca pula nem volta | `test_ciclo_de_vida.py:131-133` - `proximo_status` para os 3 status (último `None`); `:138-151` - avança um estágio; `:69-73` - os 7 pares inválidos recusados pelo banco | ✅ PASS (M3, M4, M4b mortas) |
| STAT-10 | GET: 200, texto exato, sem botão, "Voltar para a inovação" → detalhe. POST: status igual, sem registro, redirect com o mesmo texto como aviso | GET `test_views_status.py:98-105` - 200, `ULTIMO_ESTAGIO in conteudo`, sem `<form`/`<button`, `voltar == [f"/inovacoes/{pk}/"]`, autor e administrador. POST `:231-234` - redirect, `== DISPONIVEL`, `count() == 0`, `_mensagens == [("warning", ULTIMO_ESTAGIO)]` | ✅ PASS (M4, M4b, M17 mortas) |
| STAT-11 | GET nunca muda status nem cria registro | `test_views_status.py:113-116` - 3 GETs × 3 status, status igual e `count() == 0` | ✅ PASS (M24 morta) |
| STAT-12 | status enviado ausente ou diferente → nada muda; redirect com o aviso exato citando o status gravado | `test_views_status.py:244-247` - `[None, VALIDADA, "APROVADA"]`: redirect, `== EM_TESTE`, `count() == 0`, `[("warning", _conflito("Em teste"))]`; modelo `test_ciclo_de_vida.py:171-175` | ✅ PASS (M2, M25 mortas) |
| STAT-13 | duas confirmações simultâneas → exatamente um estágio e um registro | `test_views_status.py:255-259` (reenvio: `== VALIDADA`, `count() == 1`, aviso com "Validada"); `:262-278` (outra pessoa avança entre o `dispatch()` e a trava: nada gravado, aviso com o status gravado); `test_ciclo_de_vida.py:209-211` - primeira leitura termina em `FOR UPDATE`; `:191-200` - recusa pelo valor gravado, não pelo da instância | ✅ PASS (M1, M2b, M12b mortas). Sem teste com duas conexões reais; a trava é provada pelo SQL emitido |

### P1: Registrar cada mudança e dar feedback claro

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| STAT-14 | um registro com inovação, anterior, novo, responsável = usuário logado, data/hora | Payload completo: `test_ciclo_de_vida.py:145-151` - `MudancaDeStatus.objects.get()` (exatamente um), `inovacao_id == pk`, `(anterior, novo)`, `responsavel == autor`, `antes <= data <= now()`. Pela rota: `test_views_status.py:177-183` | ✅ PASS (M6 morta) |
| STAT-15 | status e registro na mesma transação | `test_ciclo_de_vida.py:215-225` - `create` falha → status `EM_TESTE`, `count() == 0`; `test_views_erro_500.py:147-170` (falha no `save` e no `create`) | ✅ PASS (M5, M5b mortas) |
| STAT-16 | mensagem de sucesso exata em `role="status"`; não reaparece ao recarregar | `test_views_status.py:185`, `:194`, `:208-210`, `:224` - `_mensagens(...) == [("success", _sucesso(...))]` (a função lê a região `role="status"`, `:153-157`); `:196-197` - recarregado `== []` | ✅ PASS (M12, M13 mortas) |
| STAT-24 | h2 "Histórico de status" com **todo registro daquela inovação**, do mais antigo ao mais recente | `test_views_detalhe.py:372` - h2; `:398-401` - ordem pela data, contra a ordem de criação; `test_ciclo_de_vida.py:101-117` - `ordering` com desempate pelo id. **Nenhum teste tem registros de outra inovação**: trocar a consulta por `MudancaDeStatus.objects` (todas as inovações) passa a suíte inteira (M11) | ❌ GAP (M11 sobreviveu) |
| STAT-25 | "<dd/mm/aaaa HH:MM> — de “X” para “Y”, por <nome completo ou username>", no fuso do projeto | `test_views_detalhe.py:398-401` - nome completo ("Ana Souza") e username ("carla"); `:409` - 02:30 UTC → "14/09/2026 23:30"; `:437-439` - sem N+1 com 3 responsáveis | ✅ PASS (M10 morta) |
| STAT-26 | sem registros → "Nenhuma mudança de status registrada." | `test_views_detalhe.py:416-417` - parágrafo exato e nenhum `<li`, com a inovação já em "Validada" (caso pré-F5) | ✅ PASS |
| STAT-27 | histórico visível para quem não pode alterar | `test_views_detalhe.py:426` - terceiro vê a linha exata | ✅ PASS |

### P1: Só o autor ou um administrador avança

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| STAT-17 | autor `USUARIO` avança como em STAT-07/08 | `test_views_status.py:170-185`, `:200-210` (fixture `autor` é `USUARIO`) | ✅ PASS |
| STAT-18 | ADMINISTRADOR avança a de outro autor; autor igual; administrador é o responsável | `test_views_status.py:220-224` - `== VALIDADA`, `gravada.autor == autor`, `responsavel == administrador`, mensagem; `test_ciclo_de_vida.py:233-234` | ✅ PASS (M6 morta) |
| STAT-19 | USUARIO não autor, GET e POST → 403 com a página da EDEX-20/21; nada muda | `test_views_status.py:323-327` - 403, `acesso_negado.html`, texto da EDEX-20, `== EM_TESTE`, `count() == 0`, GET e POST com `status_visto` correto; `test_controle_autoria.py:104-121` (varredura AD-009 inclui `inovacoes:status`, `:50`) | ✅ PASS (M7 morta) |
| STAT-20 | idem com `is_staff`/`is_superuser` | `test_views_status.py:309-327` com `nao_autor_usuario` = terceiro, staff, superusuário (`conftest.py:60-76` confere perfil e bandeiras) | ✅ PASS (M7 morta) |
| STAT-21 | perfil lido por requisição; rebaixado → 403 na próxima | `test_views_status.py:345-356` - 200 antes; rebaixado por `update()` (mantém `is_staff`, `:350`); POST → 403, nada gravado | ✅ PASS (M7, M24 mortas) |
| STAT-22 | id inexistente, GET e POST → 404 "Inovação não encontrada."; nenhum registro | `test_views_status.py:133-136` (GET, h1 exato); `:300-303` (POST); `:281-295` (apagada entre o `dispatch()` e a trava) | ✅ PASS (M18 morta) |
| STAT-23 | anônimo, GET e POST → login com `next`; nada muda | `test_views_status.py:369-371` - `assertRedirects(…, f"/entrar/?next={caminho}")`, status e contagem | ✅ PASS |

### P1: Histórico íntegro

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| STAT-28 | apagar a inovação apaga o histórico dela | `test_ciclo_de_vida.py:85-87` - `list(MudancaDeStatus.objects.all()) == [da_outra]` | ✅ PASS (M20 morta) |
| STAT-29 | apagar a conta responsável é recusado; registro fica | `test_ciclo_de_vida.py:94-97` - `ProtectedError`, mesmo registro, mesmo `responsavel_id` | ✅ PASS (M19 morta) |
| STAT-30 | nenhuma rota, tela ou admin edita/apaga o histórico | `test_ciclo_de_vida.py:311` - fora do `admin.site._registry`; `:318-320` - 404 em lista/alteração/exclusão para superusuário ADMINISTRADOR, registro intacto; `:331-336` - as 6 rotas exatas, nenhuma view com `MudancaDeStatus` | ✅ PASS |
| STAT-31 | banco recusa par fora das duas transições | `test_ciclo_de_vida.py:69-73` - 7 pares, `IntegrityError` nomeando `mudanca_de_status_transicao_valida`; `:49` - sanidade (7) | ✅ PASS |
| STAT-32 | cadastro → "Em teste", sem registro | `test_ciclo_de_vida.py:284-288` - com `status=DISPONIVEL` forjado: `== EM_TESTE`, `count() == 0` | ✅ PASS |
| STAT-33 | edição com status forjado → status igual, sem registro | `test_ciclo_de_vida.py:298-305` - título gravado, `== EM_TESTE`, `count() == 0`, 2 valores forjados | ✅ PASS |

### P1: Ciclo, confirmação e histórico acessíveis

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| STAT-34 | só nativos (`ol`/`ul`, links, `form` + `button`); sem `tabindex` positivo; foco visível; um `h1` e `<title>` "Avançar status" | `test_views_acessibilidade_alteracao.py:220-235` - um `button type=submit` dentro do `form`, um link; `:203-216` - nenhum papel de controle, `tabindex <= 0`; `:238-256` - seções `section aria-labelledby` + h2, uma `ol`; `:259-265` - `:focus-visible` com `outline` sólido nas 3 páginas; `:276-278` - `h1 == ["Avançar status"]`, `<title>` por prefixo | ✅ PASS ⚠️ (título por prefixo) |
| STAT-37 | estágio atual por texto; toda cor do ciclo e do histórico nos pares do DS-08 | Texto: `test_views_acessibilidade_alteracao.py:293` - sem CSS, `["Em teste", "Validada (status atual)", "Disponível para replicação"]`. Cor: `test_views_sistema_design.py:548-564` - cada `color` ∈ textos de `PARES_DE_TEXTO` e cada `background` ∈ fundos, **separadamente**; `:568-572` - `brand-navy` no estágio atual. O par formado não é conferido: texto `surface` sobre fundo `surface` passa (M27) | ❌ GAP (M27 sobreviveu). O CSS atual cumpre o DS-08 (conferido à mão abaixo) |

### Edge Cases da spec

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| STAT-35 | banco fora → 500 do projeto, nada gravado, sem detalhes | `test_views_erro_500.py:163` - 500; `:164` - `500.html`; `:166-168` - host, usuário, senha e traceback ausentes; `:169-170` - `== EM_TESTE`, `count() == 0`; falha no `save` e no `create` | ✅ PASS (M5, M5b mortas) |
| STAT-36 | POST sem CSRF → 403, status igual | `test_views_erro_500.py:179-183` - o próprio autor, `enforce_csrf_checks=True`: 403, não é o acesso negado, `== EM_TESTE`, `count() == 0` | ✅ PASS (M26 morta) |

**Status**: ❌ 35/37 ACs com o valor da spec afirmado e discriminante. STAT-24 e STAT-37 têm asserção, mas o sensor mostra que ela não distingue a violação. 1 spec-precision gap de redação (STAT-06/STAT-34), que não bloqueia.

### Conferência manual do DS-08 (STAT-37, código atual)

O CSS de produção está correto. A lacuna é só do teste. Pares que as regras novas formam (`templates/kira.css:493-523`): `.ciclo li` `text`/`surface`; `.ciclo li + li::before` `text-muted` sobre o `surface` do item; `[aria-current=step]` `brand-navy`/`surface` e borda `brand-blue`/`surface` (3:1, `test_views_sistema_design.py:286-289`); `.historico time` `text-muted` sobre `bg` ou `surface`. Os pares de texto estão em `PARES_DE_TEXTO` (`test_views_sistema_design.py:255-269`), com contraste ≥ 4,5 provado em `:279-282`.

---

## Discrimination Sensor

Executado num `git worktree add --detach` temporário a partir de `f48bb1a`, no scratchpad da sessão, com o `.env` copiado e o mesmo PostgreSQL de teste (porta 5433). O `import inovacoes` no worktree resolve para o próprio worktree. Linha de base no worktree: 684 passed. Uma mutação por vez, por substituição exata de texto (cada trecho conferido como único), `pytest -q` da suíte inteira e `git checkout -- .` depois de cada uma. M27 rodou num segundo worktree, criado e removido do mesmo jeito. No fim: `git worktree remove --force` + `git worktree prune`. `git status --porcelain` da árvore real: vazio antes e vazio depois. HEAD inalterado (`f48bb1a`).

| # | File:line | Mutação | Killed? (testes que falharam) |
| - | --------- | ------- | ----------------------------- |
| M1 | `inovacoes/models.py:223` | `select_for_update()` → `all()` | ✅ `test_ciclo_de_vida.py::test_avancar_trava_a_linha_ao_ler_o_status` |
| M2 | `inovacoes/models.py:227` | sem a checagem `status_visto != gravado` | ✅ 10 falhas: `test_status_visto_diferente_do_gravado…[3]`, `test_segundo_avanco…`, `test_recusa_pelo_status_gravado…`, `test_views_status.py::test_status_visto_ausente_ou_diferente…[3]`, `test_reenvio…`, `test_status_mudado_durante_o_envio…` |
| M2b | `inovacoes/models.py:227` | compara com `self.status` (instância velha) em vez do gravado | ✅ `test_recusa_pelo_status_gravado_e_nao_pelo_da_instancia`, `test_status_mudado_durante_o_envio_avisa_e_nao_grava` |
| M3 | `inovacoes/models.py:28` | `PROXIMO_STATUS` pula: "Em teste" → "Disponível" | ✅ 19 falhas, entre elas `test_proximo_status_segue_o_ciclo[EM_TESTE-VALIDADA]`, `test_avancar_status_avanca_um_estagio_e_registra[…]`, `test_quem_pode_alterar_ve_o_link_de_avancar[…]` |
| M4 | `inovacoes/models.py:29` | estágio final avança para "Em teste" | ✅ 9 falhas: `test_proximo_status_segue_o_ciclo[DISPONIVEL…]`, `test_avancar_no_ultimo_estagio…`, `test_ultimo_estagio_explica_e_ninguem_ve_o_link[3]`, `test_ultimo_estagio_explica_e_nao_oferece_botao[2]`, `test_envio_no_ultimo_estagio…`, acessibilidade `[ultimo_estagio]` |
| M4b | `inovacoes/models.py:229` | `PROXIMO_STATUS.get(gravado, gravado)` (repete o estágio final) | ✅ `test_avancar_no_ultimo_estagio_e_recusado_sem_gravar`, `test_envio_no_ultimo_estagio_avisa_e_nao_grava` |
| M5 | `inovacoes/models.py:234-237` | registro criado fora da transação, depois do status | ✅ `test_falha_ao_registrar_desfaz_o_novo_status`, `test_banco_indisponivel_na_troca_de_status…[criacao-do-registro]` |
| M5b | `inovacoes/models.py:233-237` | registro criado antes, dentro da transação; status gravado fora dela | ✅ `test_banco_indisponivel_na_troca_de_status…[gravacao-do-status]` |
| M6 | `inovacoes/models.py:236` | `responsavel=self.autor` em vez de `por` | ✅ `test_responsavel_e_quem_avanca_e_o_autor_nao_muda`, `test_administrador_avanca_a_inovacao_de_outro_autor` |
| M7 | `inovacoes/views.py:199` | `InovacaoStatusView` sem o `AlteracaoDeInovacaoMixin` (`model = Inovacao`) | ✅ 46+ falhas, entre elas `test_nao_autor_usuario_recebe_403…[terceiro|staff|superusuario-get|post]`, `test_administrador_rebaixado…`, `test_controle_autoria.py::test_terceiro_recebe_403…[…status…]` |
| M8 | `inovacao_detail.html:58` | link "Avançar" sem checar `pode_alterar` (`{% else %}`) | ✅ 5 falhas: `test_terceiro_nao_ve_o_link_de_avancar[2]`, `test_nao_autor_usuario_nao_ve_o_link_de_avancar[3]` |
| M9 | `inovacoes/views.py:132` | `.order_by("-data", "-id")` na consulta do detalhe | ✅ `test_historico_lista_as_mudancas_do_mais_antigo_ao_mais_recente` |
| M9b | `inovacoes/models.py:291` | `ordering = ["-data", "-id"]` | ✅ `test_historico_sai_do_mais_antigo…`, `test_historico_com_a_mesma_data…`, `test_historico_lista_as_mudancas…` |
| M10 | `inovacoes/views.py:132` | sem `select_related("responsavel")` | ✅ `test_historico_nao_cresce_em_consultas_com_os_registros[3]` |
| **M11** | `inovacoes/views.py:132` | `mudancas = MudancaDeStatus.objects.select_related("responsavel")` (histórico de **todas** as inovações) | ❌ **Survived**: 684 passed. Uma sonda descartável no scratch (outra inovação com registro; o detalhe da primeira deveria mostrar "Nenhuma mudança…") falha com a mutação, então a mutação é efetiva |
| M12 | `inovacoes/views.py:240` | mensagem de sucesso "mudado de" | ✅ 4 falhas: `test_autor_avanca_de_em_teste…`, `test_mensagem_de_sucesso_nao_reaparece…`, `test_autor_avanca_de_validada…`, `test_administrador_avanca…` |
| M12b | `inovacoes/views.py:224` | aviso de conflito com o status da instância em vez do gravado | ✅ `test_status_mudado_durante_o_envio_avisa_e_nao_grava` |
| M13 | `inovacoes/views.py:241` | mensagem de sucesso com o status novo no lugar do anterior | ✅ 4 falhas (as mesmas da M12) |
| M14 | `inovacao_detail.html:56` | condição do estágio final invertida | ✅ 11 falhas: `test_quem_pode_alterar_ve_o_link…[4]`, `test_ultimo_estagio_explica_e_ninguem_ve_o_link[3]`, `test_terceiro_nao_ve_o_link…[2]`, acessibilidade `[ciclo]` |
| M15 | `inovacao_detail.html:48` | "(status atual)" nos estágios que não são o atual | ✅ `test_ciclo_marca_so_o_estagio_atual_com_texto[3]`, `test_estagio_atual_e_identificavel_sem_css` |
| M16 | `inovacao_status.html:17` | `status_visto` oculto com o próximo status | ✅ `test_autor_ve_a_confirmacao…[2]`, `test_administrador_ve_a_confirmacao…` |
| M17 | `inovacoes/views.py:232` | aviso do estágio final como `info` | ✅ `test_envio_no_ultimo_estagio_avisa_e_nao_grava` |
| M18 | `inovacoes/views.py:233` | `except Inovacao.DoesNotExist` → `except LookupError` | ✅ `test_inovacao_excluida_durante_o_envio_responde_404` |
| M19 | `inovacoes/models.py:281` | `responsavel` com `CASCADE` | ✅ `test_excluir_a_conta_responsavel_e_recusado` |
| M20 | `inovacoes/models.py:270` | `inovacao` com `PROTECT` | ✅ `test_excluir_a_inovacao_apaga_so_o_historico_dela` |
| M21 | `inovacoes/models.py:234` | `self.save()` sem `update_fields` | ✅ `test_avancar_grava_so_o_status` |
| M22 | `inovacao_status.html:19` | "Cancelar" aponta para a lista | ✅ `test_autor_ve_a_confirmacao…[2]`, `test_administrador_ve_a_confirmacao…`, acessibilidade `[avancar]` |
| M24 | `inovacoes/views.py:208` | o GET avança o status ao montar o contexto | ✅ 6 falhas, entre elas `test_get_nunca_muda_o_status_nem_registra[EM_TESTE|VALIDADA]` |
| M25 | `inovacoes/views.py:220` | `status_visto` ausente tratado como o status da instância | ✅ `test_status_visto_ausente_ou_diferente_avisa_e_nao_grava[None]` |
| M26 | `inovacoes/views.py:199` | `csrf_exempt` na view | ✅ `test_views_erro_500.py::test_troca_de_status_sem_token_csrf_e_recusada` |
| **M27** | `templates/kira.css:510` | `.ciclo li { color: var(--surface) }` (branco sobre o `background: var(--surface)`) | ❌ **Survived**: 684 passed |

**Sensor depth**: expandido (integridade de transição de estado e autorização): 29 mutações de comportamento, cobrindo trava, checagem do status visto, sequência, estágio final, transação, responsável, mixin, CSRF, GET sem efeito, link condicional, ordem, N+1, filtro por inovação, mensagens, `on_delete` e contraste.
**Result**: 27/29 mortas, 2 sobreviventes (M11, M27) - FAIL ❌

---

## Code Quality

| Principle | Status |
| --------- | ------ |
| Minimum code | ✅ A regra fica em `Inovacao.avancar_status` (AD-011), sem camada nova; a view só traduz exceções em mensagens |
| Surgical changes | ✅ Testes existentes só ganharam acréscimos previstos (`CONSULTAS_DO_DETALHE` 6 → 7, telas 8 → 9, sanidade da varredura com `inovacoes:status`) |
| No scope creep | ✅ |
| Matches patterns | ✅ Confirmação por página com POST (F4), mixin da AD-009, 404 da CONS-15, mensagens em `role="status"` |
| Spec-anchored outcome check | ❌ 35/37 (STAT-24 e STAT-37 sem discriminação) |
| Per-layer Coverage Expectation met | ⚠️ Modelo 1:1 com as ACs; rota com caminho feliz, borda e erro. Falta, na tela, o caso de registros de outra inovação (STAT-24) |
| Every test maps to a spec requirement | ✅ Toda docstring nova cita STAT-NN, AD-008/009/011 ou L-003 |
| Documented guidelines followed | ✅ `.specs/LESSONS.md` (L-003 aplicada na rota e na tela; L-005 aplicada: o histórico e o link são conferidos no detalhe, não só no modelo) |

---

## Edge Cases

- [x] Inovação pré-F5 já em "Validada": controle no estágio gravado e histórico vazio (`test_views_detalhe.py:412-417`, `:317-325`).
- [x] Inovação excluída entre abrir a confirmação e enviar: 404, sem registro (`test_views_status.py:281-295`).
- [x] Duplo clique: o segundo POST cai no aviso de conflito (`test_views_status.py:250-259`).
- [ ] Administrador avança a própria inovação: sem teste próprio; a regra é a mesma do autor (`pode_ser_alterada_por`). Não bloqueia.
- [ ] Filtro "Validada" da listagem logo depois do avanço: sem teste na F5; o filtro da CONS-27 lê a coluna `status`, que o avanço grava (`test_ciclo_de_vida.py:145`). Não bloqueia.
- [ ] Id não numérico em `/inovacoes/abc/status/`: sem teste próprio; a rota usa `<int:pk>` (`inovacoes/urls.py:20`), como na F4. Não bloqueia.

---

## Gate Check

- **Gate command**: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q` (árvore real, HEAD `f48bb1a`)
- **Result**: exit 0. `ruff check`: All checks passed · `ruff format --check`: 109 files already formatted · `makemigrations --check`: No changes detected · `pytest -q`: 684 passed, 0 failed, 0 skipped (15.9 s)
- **Test count before feature**: 574 (`tasks.md`, linha de base)
- **Test count after feature**: 684
- **Delta**: +110. Nenhum teste removido; as três alterações em testes existentes são acréscimos previstos nas tasks
- **Skipped tests**: nenhum
- **Failures**: nenhuma

---

## Spec-Precision Gaps

1. **STAT-06 / STAT-34, `<title>`**: a AC pede o `<title>` "reading 'Avançar status'", mas o `base.html` acrescenta " · Repositório de Inovações" a toda página. Os testes conferem o prefixo (`test_views_status.py:50`, `test_views_acessibilidade_alteracao.py:278`), como na EDEX-43. Julgamento: a página cumpre a intenção da AC (o nome da página abre o título), e o texto da AC é que está impreciso. **Não bloqueia.** Sugestão: na próxima revisão da spec, escrever "um `<title>` que começa por 'Avançar status'".
2. **STAT-37, "contrast pairs of DS-08"**: a AC exige pares, mas o teste trata texto e fundo como conjuntos independentes. Não é ambiguidade da spec: o teste não chega ao que a spec diz, e isso está registrado como GAP (M27), não aqui.

---

## Fix Plans

### Fix 1: STAT-24 não distingue "desta inovação" de "de todas" (M11) — Major

- **Root cause**: todo teste do histórico no detalhe cria registros de uma única inovação, então a consulta `self.object.mudancas_de_status` nunca é confrontada com registros alheios.
- **Fix task**: em `inovacoes/tests/test_views_detalhe.py`, acrescentar um teste com duas inovações. A outra tem um registro, e a do detalhe tem zero ou um. Afirmar que `_historico(html)` lista só os itens da inovação aberta e que, com zero, aparece "Nenhuma mudança de status registrada.".
- **Verify**: com a mutação M11 (`mudancas=MudancaDeStatus.objects.select_related("responsavel")`) num scratch, o teste novo falha; no HEAD passa.
- **Done when**: M11 morta; gate de build verde; nenhum código de produção alterado.
- **Priority**: Major (STAT-24, AC MVP)

### Fix 2: STAT-37 confere cores soltas, não pares (M27) — Minor

- **Root cause**: `test_ciclo_e_historico_so_usam_cores_de_pares_conferidos` (`test_views_sistema_design.py:548-564`) testa `color ∈ textos` e `background ∈ fundos` separadamente; `surface` está nos dois conjuntos.
- **Fix task**: afirmar o par efetivo de cada regra de `.ciclo`/`.historico` contra `PARES_DE_TEXTO`: `(color, background)` quando a regra declara os dois; quando só declara `color`, usar o fundo herdado explícito no teste (`.ciclo li` e o `::before` sobre `surface`; `.historico time` sobre `bg` e `surface`).
- **Verify**: com M27 (`.ciclo li { color: var(--surface) }`) num scratch, o teste falha; no HEAD passa.
- **Done when**: M27 morta; gate verde; nenhum código de produção alterado.
- **Priority**: Minor (o CSS atual cumpre o DS-08; o risco é regressão futura não detectada)

---

## Requirement Traceability Update

Não aplicada (FAIL). Proposta para depois da iteração 2:

| Requirement | Previous Status | New Status |
| ----------- | --------------- | ---------- |
| STAT-01 … STAT-23, STAT-25 … STAT-36 | Implementing | ✅ Verified (evidência acima) |
| STAT-24 | Implementing | ❌ Needs Fix (Fix 1) |
| STAT-37 | Implementing | ❌ Needs Fix (Fix 2) |

---

## Histórico

- **Iteração 1** (HEAD `f48bb1a`): FAIL ❌. 35/37 ACs; 27/29 mutantes mortos. Sobreviveram M11 (histórico de todas as inovações no detalhe) e M27 (texto branco sobre branco no ciclo). Viram Fix 1 e Fix 2, só em teste.

---

## Summary

**Overall**: ❌ Not Ready (evidência das lacunas: `inovacoes/views.py:132` sob M11 com 684 passed; `inovacoes/tests/test_views_sistema_design.py:548-564` sob M27 com 684 passed)

**Spec-anchored check**: 35/37 ACs com o valor da spec afirmado e discriminante; 1 spec-precision gap de redação (título, não bloqueia)
**Sensor**: 27/29 mortas (sobreviventes: M11, M27)
**Gate**: 684 passed, 0 failed
**validate_state.py**: `python3 .claude/skills/tlc-spec-driven/scripts/validate_state.py ciclo-de-vida-status` → exit 1, "validation.md verdict is FAIL - route the ranked gaps to fix tasks, then re-verify (feature is not done)". É o resultado esperado para um FAIL.

**What works**: a transição é atômica e serializada. `select_for_update` lê o valor gravado, o `status_visto` recusa reenvio e corrida, e o registro é criado na mesma transação (`inovacoes/models.py:211-237`). O banco recusa os 7 pares inválidos. A autorização reaproveita o mixin da AD-009 e é provada com terceiro, staff, superusuário e administrador rebaixado. O GET nunca grava, e o CSRF e o banco fora do ar não deixam nada pela metade. As mensagens são exatas e têm o nível certo.

**Issues found**: Fix 1 (STAT-24, M11) e Fix 2 (STAT-37, M27), ambos de teste.

**Lessons recorded**: L-019 (M11, filtro por pai), L-020 (M27, contraste por par) e L-021 (título com sufixo do layout), todas `candidate` em `.specs/lessons.json`.

**Next steps**: o orquestrador encaminha Fix 1 e Fix 2 a um implementador, que só mexe em teste, e depois despacha a iteração 2 do Verifier.

---

## Iteração 2

**Date**: 2026-10-18
**HEAD**: `ef25406` (feature `6616da1..ef25406`; correções `f1d3de1` T12 e `ef25406` T13)
**Verifier**: novo sub-agente independente (não escreveu código, testes nem correções); cobertura re-derivada da spec
**Produção inalterada**: `git diff --stat f48bb1a..ef25406 -- ':!inovacoes/tests' ':!.specs'` vazio. Os dois commits de correção só tocam `inovacoes/tests/test_views_detalhe.py` (+27) e `inovacoes/tests/test_views_sistema_design.py` (+30/−11), e o `tasks.md`

### Task Completion

| Task | Status | Notes |
| ---- | ------ | ----- |
| T1–T11 | ✅ Done | Inalteradas desde a iteração 1 |
| T12 (Fix 1) | ✅ Done | `f1d3de1`: `test_views_detalhe.py:429-453`. 685 passed (+1), confere com o gate |
| T13 (Fix 2) | ✅ Done | `ef25406`: `test_views_sistema_design.py:546-585`, reescrito no lugar (+0 testes) |

### Reconferência das correções

**T12 (STAT-24, STAT-26)**: `test_historico_lista_so_as_mudancas_da_inovacao_aberta` (`test_views_detalhe.py:429-453`) cria três inovações. A primeira tem um registro, a segunda dois e a terceira nenhum. `:441` afirma `_historico(html) == ["01/10/2026 09:05 — de “Em teste” para “Validada”, por Ana Souza"]` no detalhe da primeira, e `:444-447` afirma a lista exata de dois itens, em ordem, no da segunda. Isso prova "every history record **of that Inovacao**, from the oldest to the most recent", e o texto é o da STAT-25. `:452-453` afirma `'<p class="vazio">Nenhuma mudança de status registrada.</p>' in secao` e `"<li" not in secao` na terceira, enquanto as outras têm histórico (STAT-26 com dados alheios presentes). Com a M11, só esse teste falha. O resultado bate com a spec. ✅

**T13 (STAT-37)**: comparei com `git show ef25406^:inovacoes/tests/test_views_sistema_design.py`. As checagens antigas eram quatro: nenhuma cor literal, todo `var(--x)` existente no `:root`, `color` ser `var()` de um token que aparece como texto em algum par, e `background*` ser `var()` de um token que aparece como fundo em algum par. As quatro continuam, em `:569`, `:573` e `:574-576` (o `_token_de` de `:557-560` exige `var(--x)` em todo `background*` e no `color`). A checagem de texto ficou mais estrita: `(texto, fundo) in PARES_DE_TEXTO` (`:585`) implica a pertinência antiga. Regra com `color` sem fundo próprio nem entrada em `FUNDO_HERDADO` faz o teste falhar (`:583`). Dois mais `background*` na mesma regra quebram o desempacotamento `(fundo,) = fundos` (`:581`), o que é conservador. Só existe uma diferença de forma: `dict(re.findall(...))` guarda a última declaração de cada propriedade. Para `color`, a última é a que o navegador aplica, então isso não enfraquece nada. `FUNDO_HERDADO` (`:549-553`) confere com o CSS e o HTML atuais: `.ciclo li` tem `background: var(--surface)` (`kira.css:509`), e a seção do histórico fica fora do `.cartao` (`inovacao_detail.html:20-41` contra `:63-75`), sobre o `body` com `--bg` (`kira.css:71`). Nenhuma checagem foi enfraquecida. ✅ A M27 morre. **Lacuna residual**: só as regras que declaram `color` têm o par conferido. Uma regra que só declara fundo deixa o texto herdado sem conferência, e `FUNDO_HERDADO` não acompanha o fundo real do ancestral. A N14, abaixo, explora isso.

### Spec-Anchored Acceptance Criteria (re-derivado no HEAD `ef25406`)

Caminhos relativos a `inovacoes/tests/`. "Reli" quer dizer que esta iteração leu a linha no HEAD e conferiu que a asserção afirma o valor da spec. "Herdado" quer dizer que a iteração 1 já tinha a evidência, o arquivo não mudou e a célula não foi relida aqui.

| AC | `file:line` + assertion (HEAD) | Conferência | Result |
| -- | ------------------------------ | ----------- | ------ |
| STAT-01 | `test_views_detalhe.py:309` h2 `== ["Ciclo de vida"]`; `:311` itens `== ETAPAS` | Reli; N5 morta | ✅ |
| STAT-02 | `test_views_detalhe.py:322` `count("(status atual)") == 1`; `:325` lista exata, 3 status | Reli; N5 morta | ✅ |
| STAT-03 | `test_views_detalhe.py:340` `_links(secao, f"Avançar para “{proximo}”") == [f"/inovacoes/{pk}/status/"]` | Reli; N4 morta | ✅ |
| STAT-04 | `test_views_detalhe.py:350-352` "<p>Último estágio do ciclo.</p>", sem "Avançar", 3 contas | Reli | ✅ |
| STAT-05 | `test_views_detalhe.py:362-363`; `test_views_status.py:335-336` (terceiro, staff, superusuário) | Reli | ✅ |
| STAT-06 | `test_views_status.py:46` 200; `:51` h1; `:52-55` texto exato; `:60-61` botão; `:66-67` "Cancelar" → detalhe; `<title>` por prefixo `:50` | Reli; N10, N11 mortas | ✅ ⚠️ (título, ver *Spec-precision*) |
| STAT-07 | `test_views_status.py:175` `assertRedirects(…, f"/inovacoes/{pk}/")`; `:176` `== VALIDADA` | Reli; N7, N9 mortas | ✅ |
| STAT-08 | `test_views_status.py:204` (`redirect_chain == [(…, 302)]` em `:166`); `:205` `== DISPONIVEL`; `:207` | Reli; N7, N9 mortas | ✅ |
| STAT-09 | `test_ciclo_de_vida.py:131-133` `proximo_status`; `:138-151`; `:69-73` | Reli | ✅ |
| STAT-10 | GET `test_views_status.py:98-105`; POST `:231-234` `[("warning", ULTIMO_ESTAGIO)]` | Reli | ✅ |
| STAT-11 | `test_views_status.py:113-116` 3 GETs, status igual, `count() == 0` | Reli | ✅ |
| STAT-12 | `test_views_status.py:244-247` `[None, VALIDADA, "APROVADA"]` → `[("warning", _conflito("Em teste"))]`; `test_ciclo_de_vida.py:171-175` | Reli; N6, N8 mortas | ✅ |
| STAT-13 | `test_views_status.py:255-259`, `:262-278`; `test_ciclo_de_vida.py:191-200`, `:209-211` (`FOR UPDATE`) | Reli | ✅ |
| STAT-14 | `test_ciclo_de_vida.py:145-151` payload completo; `test_views_status.py:177-183` | Reli; N9 morta | ✅ |
| STAT-15 | `test_ciclo_de_vida.py:215-225`; `test_views_erro_500.py:147-170` | Reli | ✅ |
| STAT-16 | `test_views_status.py:185`, `:194`, `:208-210`, `:224` (região `role="status"`, `:153-157`); `:196-197` recarregado `== []` | Reli; N7 morta | ✅ |
| STAT-17 | `test_views_status.py:170-185`, `:200-210` (`conftest.py:8-11`: `autor` criado por `create_user`, perfil padrão) | Reli | ✅ |
| STAT-18 | `test_views_status.py:220-224`; `test_ciclo_de_vida.py:233-234` | Reli | ✅ |
| STAT-19 | `test_views_status.py:323-327` 403, `acesso_negado.html`, texto da EDEX-20, nada gravado | Reli | ✅ |
| STAT-20 | `test_views_status.py:309-327` com `nao_autor_usuario` (terceiro, staff, superusuário) | Reli | ✅ |
| STAT-21 | `test_views_status.py:345-356` | Reli | ✅ |
| STAT-22 | `test_views_status.py:133-136`, `:300-303`, `:281-295` | Reli | ✅ |
| STAT-23 | `test_views_status.py:369-371` `assertRedirects(…, f"/entrar/?next={caminho}")` | Reli | ✅ |
| STAT-24 | `test_views_detalhe.py:372` h2; `:398-401` ordem pela data; **`:441`, `:444-447` só os registros da inovação aberta** | Re-derivado (T12); M11 morta | ✅ |
| STAT-25 | `test_views_detalhe.py:398-401` nome/username; `:409` fuso; `:441`, `:444-447` | Reli; N1, N2, N3 mortas | ✅ |
| STAT-26 | `test_views_detalhe.py:416-417`; **`:452-453` com outras inovações tendo histórico** | Re-derivado (T12); N15 morta | ✅ |
| STAT-27 | `test_views_detalhe.py:420-426` terceiro vê a linha exata | Reli | ✅ |
| STAT-28 | `test_ciclo_de_vida.py:85-87` `== [da_outra]` | Reli | ✅ |
| STAT-29 | `test_ciclo_de_vida.py:94-97` `ProtectedError` | Reli | ✅ |
| STAT-30 | `test_ciclo_de_vida.py:311-320`, `:331-336` | Reli | ✅ |
| STAT-31 | `test_ciclo_de_vida.py:69-73` 7 pares, `IntegrityError` com o nome da constraint | Reli | ✅ |
| STAT-32 | `test_ciclo_de_vida.py:284-288` | Reli | ✅ |
| STAT-33 | `test_ciclo_de_vida.py:298-305` | Reli | ✅ |
| STAT-34 | `test_views_acessibilidade_alteracao.py:220-234`, `:205-216`, `:246-255`, `:259-265`, `:276-278` (`<title>` por prefixo) | Reli; N11 morta | ✅ ⚠️ (título) |
| STAT-35 | `test_views_erro_500.py:163-170` | Reli | ✅ |
| STAT-36 | `test_views_erro_500.py:179-183` | Reli | ✅ |
| STAT-37 | Texto: `test_views_acessibilidade_alteracao.py:293`. Cor: `test_views_sistema_design.py:585` `(texto, fundo) in PARES_DE_TEXTO` só para regras com `color`. **Regra com fundo e sem `color` não tem o texto herdado conferido**: `.historico li { background: var(--brand-blue) }` passa a suíte (N14), com o texto a 2,48:1 e a data a 1,0:1 | Re-derivado (T13); M27, N12, N13 mortas; **N14 sobreviveu** | ❌ GAP |

**Status**: ❌ 36/37 ACs com o valor da spec afirmado e discriminante. A STAT-37 tem asserção, mas ela não distingue um fundo novo sem `color` (N14). Há 1 spec-precision gap de redação (título, STAT-06/STAT-34), que não bloqueia.

### Discrimination Sensor (iteração 2)

Rodado num `git worktree add --detach` em `scratchpad/wt`, a partir de `ef25406`, com o `.env` copiado e o PostgreSQL de teste (porta 5433). O `inovacoes.__file__` resolve para a worktree, e a linha de base nela é 685 passed. Cada mutação foi feita por substituição exata, com o trecho conferido como único (`count == 1`). Para cada uma rodei a suíte inteira (`.venv/bin/pytest -q -p no:cacheprovider`) e depois `git checkout -- .` e `git diff --quiet`. No fim, `git worktree remove --force` e `git worktree prune`. O `git status --porcelain` da árvore real ficou vazio antes e depois, o HEAD continua `ef25406` e `git worktree list` só mostra a árvore principal.

#### Sobreviventes da iteração 1, re-injetadas como descritas

| # | File:line | Mutação | Killed? |
| - | --------- | ------- | ------- |
| M11 | `inovacoes/views.py:132` | `mudancas=MudancaDeStatus.objects.select_related("responsavel")`, com `MudancaDeStatus` acrescentado ao import da linha 9 | ✅ `test_views_detalhe.py::test_historico_lista_so_as_mudancas_da_inovacao_aberta` (único) |
| M27 | `templates/kira.css:510` | `.ciclo li { … color: var(--surface) }` | ✅ `test_views_sistema_design.py::test_ciclo_e_historico_so_usam_cores_de_pares_conferidos[.ciclo]` (único) |

#### Mutações novas (iteração 2)

| # | File:line | Mutação | Killed? (testes que falharam) |
| - | --------- | ------- | ----------------------------- |
| N1 | `inovacao_detail.html:69` | responsável só pelo username (sem nome completo) | ✅ 4: `test_historico_lista_as_mudancas_do_mais_antigo…`, `…_no_fuso_de_sao_paulo`, `test_terceiro_ve_o_historico`, `…_so_as_mudancas_da_inovacao_aberta` |
| N2 | `inovacao_detail.html:69` | data `"m/d/Y H:i"` | ✅ os mesmos 4 |
| N3 | `inovacao_detail.html:69` | anterior e novo trocados no item do histórico | ✅ os mesmos 4 |
| N4 | `inovacao_detail.html:59` | link "Avançar para “<status atual>”" em vez do próximo | ✅ 4: `test_quem_pode_alterar_ve_o_link_de_avancar[em_teste|validada × autor|administrador]` |
| N5 | `inovacoes/views.py:130` | `etapas=StatusInovacao.choices[::-1]` (ordem invertida) | ✅ 5: `test_ciclo_de_vida_lista_os_tres_estagios_em_ordem`, `test_ciclo_marca_so_o_estagio_atual…[3]`, `test_estagio_atual_e_identificavel_sem_css` |
| N6 | `inovacoes/views.py:224` | aviso de conflito com o valor cru (`VALIDADA`) em vez do rótulo | ✅ 5: `test_status_visto_ausente_ou_diferente…[3]`, `test_reenvio…`, `test_status_mudado_durante_o_envio…` |
| N7 | `inovacoes/views.py:244` | toda resposta do POST redireciona para a lista | ✅ 10: sucesso, estágio final, conflito e reenvio em `test_views_status.py` |
| N8 | `inovacoes/models.py:227` | `status_visto` ausente aceito (`is not None and …`) | ✅ 2: `test_status_visto_diferente_do_gravado…[None]`, `test_status_visto_ausente_ou_diferente…[None]` |
| N9 | `inovacoes/models.py:234` | sem `self.save(update_fields=["status"])`: o registro é criado e o status não muda | ✅ 9+: `test_avancar_status_avanca_um_estagio_e_registra[2]`, `test_avancar_grava_so_o_status`, `test_autor_avanca…[2]`, `test_administrador_avanca…`, `test_views_erro_500…[gravacao-do-status]` |
| N10 | `inovacao_status.html:11` | sem "Depois de avançar, não é possível voltar ao status anterior." | ✅ 3: `test_autor_ve_a_confirmacao…[2]`, `test_administrador_ve_a_confirmacao…` |
| N11 | `inovacao_status.html:3` | `<title>` com o título da inovação em vez de "Avançar status" | ✅ 5: as 3 de STAT-06 e `test_avancar_status_tem_um_unico_h1_e_title[avancar|ultimo_estagio]` |
| N12 | `templates/kira.css:523` | `.historico time { color: var(--bg) }` (texto da cor do fundo) | ✅ `test_ciclo_e_historico_so_usam_cores_de_pares_conferidos[.historico]` |
| N13 | `templates/kira.css:518` | `.ciclo [aria-current=step]` ganha `background: var(--brand-blue)` (navy sobre azul) | ✅ `test_ciclo_e_historico_so_usam_cores_de_pares_conferidos[.ciclo]` |
| **N14** | `templates/kira.css:521` | `.historico li` ganha `background: var(--brand-blue)`: texto `--text` herdado a 2,48:1 e `.historico time` (`--text-muted`) a 1,0:1 | ❌ **Survived**: 685 passed |
| N15 | `inovacao_detail.html:66` | `{% if mudancas|length > 1 %}` (off-by-one: um registro só mostra "Nenhuma mudança…") | ✅ 4: `…_no_fuso_de_sao_paulo`, `test_terceiro_ve_o_historico`, `…_so_as_mudancas_da_inovacao_aberta`, `test_secoes_do_detalhe…[historico]` |

**Sensor depth**: expandido (integridade de transição de estado, autorização e acessibilidade): 2 re-injeções e 15 mutações novas, cobrindo o texto e a ordem do histórico, o rótulo do link, a ordem dos estágios, as mensagens, o redirect, o status visto ausente, a gravação do status, o texto e o título da confirmação, o off-by-one do histórico vazio e o contraste.
**Result**: 16/17 mortas, 1 sobrevivente (N14) - FAIL ❌

### Gate Check (iteração 2)

- **Gate command**: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q` (árvore real, HEAD `ef25406`)
- **Result**: exit 0. `ruff check`: All checks passed · `ruff format --check`: 110 files already formatted · `makemigrations --check`: No changes detected · `pytest -q`: 685 passed, 0 failed, 0 skipped (16.0 s)
- **Test count**: 574 antes da feature → 684 na iteração 1 → 685 agora (+1, T12; a T13 reescreveu um teste parametrizado existente). Nenhum teste removido; nenhuma asserção enfraquecida (ver *Reconferência das correções*)

### Spec-Precision Gaps (iteração 2): julgamento do `<title>`

**STAT-06 / STAT-34, `<title>` "reading 'Avançar status'"**: a página renderiza `Avançar status · Repositório de Inovações`, porque `templates/base.html:6` acrescenta o sufixo do site a toda página, e os testes conferem o prefixo (`test_views_status.py:50`, `test_views_acessibilidade_alteracao.py:278`). **Julgamento: spec-precision gap de redação, não GAP de implementação. Não bloqueia.** O sufixo é convenção global do layout, anterior à F5 e vigente na F1–F4. A AC da F4 equivalente (EDEX-43, "a `<title>` that name the page") aceitou o mesmo formato. O que a AC protege (WCAG 2.4.2: o título identifica a página, e o `h1` é único) está afirmado: o `h1` exato em `:51`/`:276` e o nome da página no começo do `<title>`. A N11, que troca o nome da página, morre. Limite conhecido: um sufixo inesperado depois de "Avançar status" passaria pelo prefixo. Sugestão para a próxima revisão da spec, sem editar as ACs agora: "a `<title>` that begins with 'Avançar status'", ou afirmar nos testes o título renderizado completo. Lição L-021 (candidate) mantida.

### Fix Plans (iteração 2)

#### Fix 3: STAT-37 não confere o texto herdado sob uma regra que só declara fundo (N14) — Minor

- **Root cause**: `test_ciclo_e_historico_so_usam_cores_de_pares_conferidos` (`test_views_sistema_design.py:564-585`) só monta o par `(texto, fundo)` quando a regra declara `color` (`:577-578`, `continue`). Uma regra de `.ciclo`/`.historico` que declara `background` sem `color` passa só porque o fundo é um fundo de algum par (`:576`). O texto herdado (`--text` do `body`) e os descendentes com `color` (`.historico time`, `.ciclo li + li::before`, `.ciclo [aria-current=step]`) continuam conferidos contra o fundo fixo de `FUNDO_HERDADO`, não contra o novo.
- **Fix task**: no mesmo teste, toda regra de `.ciclo`/`.historico` que declara `background*` precisa ter o par do texto que fica sobre ela em `PARES_DE_TEXTO`. Usar o `color` da própria regra ou, sem ele, o texto herdado `text` (o `color` do `body`, `kira.css:72`). Além disso, o fundo de cada entrada de `FUNDO_HERDADO` deve ser conferido contra o `background` real da regra ancestral (`.ciclo li` para o `::before` e o estágio atual; `.historico li`, se declarar fundo, e senão `bg` para o `.historico time`). Uma alternativa mais simples e aceitável: exigir que toda regra com `background*` declare também `color`, e derivar `FUNDO_HERDADO` do ancestral em vez de fixá-lo.
- **Verify**: num scratch, com N14 (`.historico li { …; background: var(--brand-blue); }`) o teste falha; com N14 trocado por `background: var(--surface)` (par do DS-08) ele passa; no HEAD passa; M27, N12 e N13 continuam mortas.
- **Done when**: N14 morta; gate de build verde; nenhum código de produção alterado.
- **Priority**: Minor (o CSS atual cumpre o DS-08; o risco é regressão futura não detectada na mesma classe da M27)

### Requirement Traceability Update (iteração 2)

Não aplicada (FAIL). Proposta para a iteração 3:

| Requirement | Previous Status | New Status |
| ----------- | --------------- | ---------- |
| STAT-01 … STAT-36 | Implementing | ✅ Verified (evidência acima; STAT-24 fechada pela T12) |
| STAT-37 | Implementing | ❌ Needs Fix (Fix 3) |

### Histórico (continuação)

- **Iteração 2** (HEAD `ef25406`): FAIL ❌. 36/37 ACs; 16/17 mutantes mortos. M11 e M27 agora morrem. Sobreviveu N14 (fundo sem `color` no histórico, mesma classe da M27), que vira Fix 3, só em teste. Restam 1 iteração de correção e re-verificação antes de escalar ao usuário (limite de 3).

### Summary (iteração 2)

**Overall**: ❌ Not Ready (evidência da lacuna: `templates/kira.css:521` sob N14 com 685 passed; `inovacoes/tests/test_views_sistema_design.py:577-578` pula regras sem `color`)

**Spec-anchored check**: 36/37 ACs com o valor da spec afirmado e discriminante; 1 spec-precision gap de redação (título, não bloqueia)
**Sensor**: 16/17 mortas (sobrevivente: N14)
**Gate**: 685 passed, 0 failed
**validate_state.py**: `python3 .claude/skills/tlc-spec-driven/scripts/validate_state.py ciclo-de-vida-status` → exit 1, "validation.md verdict is FAIL - route the ranked gaps to fix tasks, then re-verify (feature is not done)". É o resultado esperado para um FAIL.

**What works**: tudo o que a iteração 1 já provava continua provado, e as correções fecham a STAT-24 (histórico só da inovação aberta, com o vazio ao lado de inovações com histórico) e o caso "texto com `color` sobre fundo da mesma regra" da STAT-37.

**Issues found**: Fix 3 (STAT-37, N14), só de teste.

**Lessons**: L-020 (candidate) recorreu nesta feature com a N14, e o `lessons.py add` acrescentou a evidência; L-019 não recorreu (M11 morta); L-021 continua (o título segue como spec-precision gap), e o `lessons.py add` acrescentou a evidência. Nenhuma lição nova; nenhuma promovida, porque a recorrência é na mesma feature.

**Next steps**: o orquestrador encaminha o Fix 3 a um implementador, que só mexe em teste, e depois despacha a iteração 3 do Verifier (a última antes de escalar).

---

## Iteração 3

**Date**: 2026-10-18
**HEAD**: `5e0fd25` (feature `6616da1..5e0fd25`; correção `5e0fd25`, T14)
**Verifier**: novo sub-agente independente. Não escreveu código, testes nem correções, e re-derivou a cobertura da spec.
**Produção inalterada**: `git diff --stat f48bb1a..5e0fd25 -- . ':!inovacoes/tests' ':!.specs'` vazio. A T14 só toca `inovacoes/tests/test_views_sistema_design.py` (+35/−25 no teste) e o `tasks.md`.

### Task Completion

| Task | Status | Notes |
| ---- | ------ | ----- |
| T1–T13 | ✅ Done | Inalteradas desde a iteração 2 |
| T14 (Fix 3) | ⚠️ Done com regressão | `5e0fd25`: `test_views_sistema_design.py:546-603`. Mata a N14, mas deixa de conferir `background-image` (ver abaixo). 685 passed (+0) |

### Reconferência da T14 (STAT-37)

Comparei com `git show 5e0fd25^:inovacoes/tests/test_views_sistema_design.py`.

**O que melhorou.** O par efetivo `(color, background)` agora é calculado a partir do CSS real. `_cor_desenhada` (`:572-578`) percorre o seletor, a cadeia de `CADEIA_DO_COMPONENTE` e o `body`, e em cada passo vale a última declaração. Isso acontece em toda regra que declara `color`, `background` ou `background-color` (`:597-603`). Um seletor de uma lista que não está na cadeia faz o teste falhar (`:601`). A N14 morre.

**`CADEIA_DO_COMPONENTE` contra o DOM e o layout reais.** A cadeia (`:550-559`) confere:

- **Estágio atual.** `.ciclo [aria-current=step]` é o próprio `li` (`inovacao_detail.html:49`), então a cadeia `.ciclo li` → `.ciclo` está certa. O `<strong>` interno não tem regra na `kira.css`.
- **Separador.** O `::before` é filho do `li`.
- **Data do histórico.** `.historico time` fica dentro do `li` de `ol.historico` (`:67-69`).
- **Ancestrais sem fundo.** As duas `section` ficam fora do `.cartao` (`:20-41` contra `:43-75`). `main` não tem fundo (`kira.css:165-171`). Nenhuma regra genérica de `section`, `ol`, `li`, `time` ou `strong` define cor.
- **Fundo efetivo.** Com isso, o fundo efetivo é o do `body` (`--bg`, `kira.css:71`), e a cor do texto também vem do `body` (`--text`, `:72`).

**O que foi enfraquecido (regressão).**

- **Antes da T14:** `fundos = [_token_de(v) for p, v in propriedades.items() if p.startswith("background")]` (linha 574 do `ef25406`) exigia que **todo** `background*`, inclusive `background-image`, fosse `var(--token)` de um fundo de par do DS-08.
- **Depois da T14:**
  - **Regra pulada.** Uma regra que só declara `background-image` é pulada (`:597-599`). Restam apenas as checagens de cor literal e de token existente.
  - **Ancestral ignorado.** `_cor_desenhada` também ignora `background-image` de um ancestral (`:576`).
- **Prova da regressão:** A1 e A2, abaixo, morrem com o arquivo de teste do `ef25406` (`1 failed, 79 passed` em `test_views_sistema_design.py`) e sobrevivem no HEAD.

As demais checagens anteriores continuam:

- nenhuma cor literal (`:592`);
- todo `var()` existe no `:root` (`:594-596`);
- `color`, `background` e `background-color` só por `var(--token)`, garantido pelo `fullmatch` de `_token_de` (`:562-565`);
- pertinência do par (`:603`), que implica a pertinência antiga do texto e do fundo.

**Lacuna anterior, não criada pela T14.** `_regras_do_componente` (`:536-543`) só lê regras com algum seletor que *começa* por `.ciclo`/`.historico`, e `_corpos` só casa o seletor exato (`:54-61`). Uma regra como `ol.historico li` ou `section .ciclo li` fica invisível. A6 e A7 sobrevivem também com o teste do `ef25406`.

### Spec-Anchored Acceptance Criteria (re-derivado no HEAD `5e0fd25`)

Os arquivos de teste das ACs STAT-01 a STAT-36 não mudaram desde `ef25406`, e a T14 só tocou `test_views_sistema_design.py`. Reli independentemente 14 linhas da tabela da iteração 2 e conferi o valor da spec em cada uma:

| AC | `file:line` + assertion (relido no HEAD) | Result |
| -- | ---------------------------------------- | ------ |
| STAT-03 | `test_views_detalhe.py:340` `_links(secao, f"Avançar para “{proximo}”") == [f"/inovacoes/{pk}/status/"]` | ✅ |
| STAT-06 | `test_views_status.py:46-67` 200, `h1 == ["Avançar status"]`, texto exato, um botão `type="submit"` com o rótulo exato, `method="post"`, `status_visto` oculto com o valor gravado, `cancelar == [f"/inovacoes/{pk}/"]`; `<title>` por prefixo (`:50`) | ✅ ⚠️ (título) |
| STAT-07 | `test_views_status.py:175-176` `assertRedirects(…, f"/inovacoes/{pk}/")`, `== VALIDADA` | ✅ (B5 morta) |
| STAT-10 | GET `test_views_status.py:98-105`; POST `:231-234` `[("warning", ULTIMO_ESTAGIO)]`, `count() == 0` | ✅ |
| STAT-12 | `test_views_status.py:244-247` `[("warning", _conflito("Em teste"))]`, `== EM_TESTE`, `count() == 0` | ✅ (B4 morta) |
| STAT-14 | `test_views_status.py:177-183` registro exato (`inovacao_id`, anterior, novo), `responsavel == autor` | ✅ |
| STAT-16 | `test_views_status.py:194-197` `[("success", _sucesso(...))]` na região `role="status"` (`:153-157`); recarregado `== []` | ✅ (B2 morta) |
| STAT-19 | `test_views_status.py:323-327` 403, `acesso_negado.html`, `NEGADO`, status e contagem | ✅ |
| STAT-23 | `test_views_status.py:369-371` `assertRedirects(…, f"/entrar/?next={caminho}")`, nada gravado | ✅ |
| STAT-25 | `test_views_detalhe.py:398-401` lista exata com nome completo e username; `:409` fuso | ✅ |
| STAT-28 | `test_ciclo_de_vida.py:85-87` `== [da_outra]` | ✅ |
| STAT-29 | `test_ciclo_de_vida.py:94-97` `ProtectedError`, registro e `responsavel_id` | ✅ |
| STAT-31 | `test_ciclo_de_vida.py:69-73` `IntegrityError` com `mudanca_de_status_transicao_valida`, 7 pares | ✅ (B1 morta) |
| STAT-36 | `test_views_erro_500.py:179-183` 403 que não é o acesso negado, `== EM_TESTE`, `count() == 0` | ✅ |

As demais (STAT-01, 02, 04, 05, 08, 09, 11, 13, 15, 17, 18, 20–22, 24, 26, 27, 30, 32–35) foram herdadas da iteração 2. Os arquivos não mudaram, e as mutações B3, B6, M11 e as das iterações anteriores continuam valendo como discriminação. Não as reli linha a linha.

**STAT-37 (re-derivada por inteiro).** A AC tem duas cláusulas:

- **"by text (STAT-02)".** `test_views_acessibilidade_alteracao.py:286-294`: sem o `<style>` e sem `style=`, os itens leem `["Em teste", "Validada (status atual)", "Disponível para replicação"]`. ✅
- **"every color the cycle control and the history add to `kira.css`" nos pares do DS-08.** Pertinência do par: `test_views_sistema_design.py:603` `par in PARES_DE_TEXTO`. Contraste dos pares ≥ 4,5: `:278-282`. Borda do estágio atual (3:1): `:286-289` e `:606-611`. O CSS atual cumpre a cláusula; conferi à mão:
  - `.ciclo li`: `text` sobre `surface`;
  - `::before`: `text-muted` sobre `surface`;
  - estágio atual: `brand-navy` sobre `surface`, com borda `brand-blue`;
  - `.historico li`: `text` sobre `bg`;
  - `.historico time`: `text-muted` sobre `bg`.

  **O teste, porém, não discrimina:**
  - **`background-image`.** Um fundo novo por `background-image` passa (A1: o texto `--text` fica a 2,48:1 sobre `--brand-blue`, e a data a 1,0:1; A2: `--brand-gradient`, com o texto a 1,42:1 sobre a ponta navy).
  - **Seletor que não começa pela classe.** Passa também uma regra do componente escrita assim (A6, a mesma cor da N14; A7, texto branco sobre o branco do `li`, 1,0:1). ❌ GAP

**Status**: ❌ 36/37 ACs com o valor da spec afirmado e discriminante. A STAT-37 tem asserção, mas ela não distingue A1, A2, A6 e A7. Há 1 spec-precision gap de redação (título), que não bloqueia.

### Discrimination Sensor (iteração 3)

Rodei o sensor num `git worktree add --detach` em `scratchpad/wt3`, a partir de `5e0fd25`:

- **Preparação.** Copiei o `.env` e usei o PostgreSQL de teste (porta 5433). `inovacoes.__file__` resolve para a worktree, e a linha de base nela é 685 passed.
- **Execução.** Cada mutação foi feita por substituição exata de texto, com o trecho conferido como único (`count == 1`). Para cada uma rodei a suíte inteira com `.venv/bin/pytest -q -p no:cacheprovider` e depois `git checkout -- .` e `git diff --quiet`. A1, A2, A6 e A7 rodaram também contra o teste do `ef25406` (`git checkout ef25406 -- inovacoes/tests/test_views_sistema_design.py` na worktree, depois restaurado).
- **Limpeza e isolamento.** No fim, `git worktree remove --force` e `git worktree prune`. O `git status --porcelain` da árvore real ficou vazio antes e depois (idêntico à linha de base gravada), o HEAD continua `5e0fd25` e `git worktree list` só mostra a árvore principal.

#### Sobreviventes anteriores, re-injetadas como descritas

| # | File:line | Mutação | Killed? |
| - | --------- | ------- | ------- |
| N14 | `templates/kira.css:521` | `.historico li { …; background: var(--brand-blue); }` | ✅ `test_ciclo_e_historico_so_usam_cores_de_pares_conferidos[.historico]` (único) |
| M11 | `inovacoes/views.py:132` | `mudancas = MudancaDeStatus.objects.select_related("responsavel")` (todas as inovações) | ✅ `test_views_detalhe.py::test_historico_lista_so_as_mudancas_da_inovacao_aberta` (único) |
| M27 | `templates/kira.css:510` | `.ciclo li { …; color: var(--surface) }` | ✅ `test_ciclo_e_historico_so_usam_cores_de_pares_conferidos[.ciclo]` (único) |

#### Mutações novas contra a lógica da T14

| # | File:line | Mutação | Killed? | AC |
| - | --------- | ------- | ------- | -- |
| **A1** | `templates/kira.css:521` | `.historico li` ganha `background-image: linear-gradient(var(--brand-blue), var(--brand-blue))` | ❌ **Survived** (685 passed). Morta com o teste do `ef25406` → **regressão da T14** | STAT-37 |
| **A2** | `templates/kira.css:521` | `.historico li` ganha `background-image: var(--brand-gradient)` | ❌ **Survived** (685 passed). Morta com o teste do `ef25406` → **regressão da T14** | STAT-37 |
| A3 | `templates/kira.css:521` | `.historico li` ganha `background: linear-gradient(var(--brand-blue), var(--brand-blue))` (gradiente no atalho) | ✅ `[.historico]` (`_token_de` exige `var()` puro) | STAT-37 |
| A4 | `templates/kira.css:521` (regra nova) | lista de seletores `.vazio, .historico li { background: var(--brand-blue); }` | ✅ `[.historico]` (`.vazio` sem cadeia) | STAT-37 |
| A5 | `templates/kira.css:520` | `color: var(--surface)` no ancestral `.historico` | ✅ `[.historico]` (herdado por `.historico li`) | STAT-37 |
| **A6** | `templates/kira.css:521` (regra nova) | `ol.historico li { background: var(--brand-blue); }` | ❌ **Survived** (685 passed; também com o teste do `ef25406`) | STAT-37 |
| **A7** | `templates/kira.css:521` (regra nova) | `section .ciclo li { color: var(--surface); }` (branco sobre o branco do `li`) | ❌ **Survived** (685 passed; também com o teste do `ef25406`) | STAT-37 |
| A8 | `templates/kira.css:521` (regra nova) | `.ciclo [aria-current=step] strong { color: var(--surface); }` | ✅ `[.ciclo]` (seletor sem cadeia) | STAT-37 |
| A9 | `templates/kira.css:509` | `.ciclo li` com `background-color: var(--brand-navy)` no lugar do `background: var(--surface)` | ✅ `[.ciclo]` | STAT-37 |
| A10 | `templates/kira.css:521` | `.historico li` ganha `opacity: 0.3` | ⚪ Survived, **fora da spec** (opacidade não é cor; a STAT-37 fala de "every color … add") | nota |

#### Mutações novas de comportamento

| # | File:line | Mutação | Killed? (testes que falharam) |
| - | --------- | ------- | ----------------------------- |
| B1 | `inovacoes/migrations/0007_mudancadestatus.py` (CheckConstraint) | a constraint do banco passa a aceitar também ("Disponível para replicação", "Em teste") | ✅ `test_transicao_invalida_e_recusada_pelo_banco[DISPONIVEL_PARA_REPLICACAO-EM_TESTE]` |
| B2 | `inovacoes/views.py:238` | mensagem de sucesso com nível `info` em vez de `success` | ✅ 4: `test_autor_avanca_de_em_teste…`, `…_de_validada…`, `test_mensagem_de_sucesso_nao_reaparece…`, `test_administrador_avanca…` |
| B3 | `inovacao_status.html:14` | `<form method="get">` na confirmação | ✅ 3: `test_autor_ve_a_confirmacao…[2]`, `test_administrador_ve_a_confirmacao…` |
| B4 | `inovacoes/views.py:220` | `status_visto` lido de `request.GET` | ✅ 8+: sucesso, reenvio, estágio final e `test_views_erro_500…[2]` |
| B5 | `inovacoes/views.py:244` | redirect 301 (`HttpResponsePermanentRedirect`) em vez de 302 | ✅ 11: todo POST de `test_views_status.py` que volta ao detalhe |
| B6 | `inovacao_detail.html:46,54` | `<ol class="ciclo">` → `<ul>` | ✅ 8: `test_ciclo_de_vida_lista_os_tres_estagios_em_ordem`, `test_ciclo_marca_so_o_estagio_atual…[3]`, `test_secoes_do_detalhe…[ciclo]`, `test_terceiro_nao_ve_o_link…[2]` |
| B7 | `inovacoes/models.py:291` | `ordering = ["data"]` (sem o desempate pelo id) | ⚪ Survived, **fora da spec**. A STAT-24 não define ordem para datas iguais. `test_ciclo_de_vida.py:108-115` existe, mas o PostgreSQL devolve as linhas na ordem física, então o mutante é equivalente na prática (`auto_now_add` com microssegundos torna o empate irrealista) |

**Sensor depth**: expandido (integridade de transição de estado, autorização e acessibilidade): 3 re-injeções e 17 mutações novas (10 contra a T14, 7 de comportamento).
**Result**: 14/20 mortas. 6 sobreviveram: A1, A2, A6 e A7, cobertas pela STAT-37; A10 e B7, fora da spec e registradas só como nota. FAIL ❌

### Gate Check (iteração 3)

- **Gate command**: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q` (árvore real, HEAD `5e0fd25`)
- **Result**: exit 0. `ruff check`: All checks passed · `ruff format --check`: 110 files already formatted · `makemigrations --check`: No changes detected · `pytest -q`: 685 passed, 0 failed, 0 skipped (15.8 s)
- **Test count**: 574 antes da feature → 684 (iteração 1) → 685 (iteração 2) → 685 agora (a T14 reescreveu o teste no lugar). Nenhum teste removido. **Uma checagem foi enfraquecida**: `background-image` deixou de ser conferido (ver *Reconferência da T14*)

### Spec-Precision Gaps (iteração 3): novo julgamento do `<title>`

**STAT-06 / STAT-34, `<title>` "reading 'Avançar status'"**: mantenho o julgamento da iteração 2. É um **spec-precision gap de redação e não bloqueia**.

- **O que a página renderiza.** `Avançar status · Repositório de Inovações` (`templates/base.html:6`, convenção global anterior à F5).
- **O que os testes afirmam.** O prefixo (`test_views_status.py:50`, `test_views_acessibilidade_alteracao.py:278`) e o `h1` exato (`:51`, `:276`). A N11 (iteração 2), que trocava o nome da página no título, morre.
- **Precedente.** A EDEX-43 da F4 aceitou o mesmo formato.
- **Sem edição de AC.** Não editei a AC. Sugestão para a próxima revisão da spec: "a `<title>` that begins with 'Avançar status'".

### Fix Plans (iteração 3)

#### Fix 4: STAT-37 não confere `background-image` nem regras cujo seletor não começa pela classe (A1, A2, A6, A7) — Minor, só teste

- **Root cause**:
  - **Regressão da T14.** `test_views_sistema_design.py:597-599` só confere regras com `color`/`background`/`background-color`, e `_cor_desenhada` (`:576`) ignora as outras propriedades `background-*`. A checagem antiga `p.startswith("background")` sumiu.
  - **Lacuna antiga.** `_regras_do_componente` (`:536-543`) e `_corpos` (`:54-61`) só enxergam seletores que começam pela classe ou que são iguais a ela.
- **Fix task** (em `inovacoes/tests/test_views_sistema_design.py`):
  1. Tratar **toda** propriedade que começa por `background` como fundo. Ela entra na condição de `:598`, e `_cor_desenhada` a lê, para que `background-image` ou um gradiente falhe no `_token_de` ou no par. Alternativa aceitável: restaurar a checagem antiga, com todo `background*` = `var(--token)` de um fundo de par do DS-08, ao lado da nova.
  2. Selecionar as regras do componente por qualquer seletor que **contenha** `.ciclo`/`.historico` (por exemplo `re.search(r"\.ciclo\b", s)`). Exigir que cada um desses seletores esteja em `CADEIA_DO_COMPONENTE`, para que `ol.historico li` e `section .ciclo li` falhem com "declare a cadeia".
- **Verify**: num scratch, A1, A2, A6 e A7 fazem o teste falhar; N14, M27, A3, A4, A5, A8 e A9 continuam mortas; no HEAD o teste passa.
- **Done when**: os 4 mutantes estão mortos, o gate de build está verde e nenhum código de produção foi alterado.
- **Priority**: Minor. O CSS atual cumpre o DS-08; o risco é uma regressão futura de contraste não detectada.

### Requirement Traceability Update (iteração 3)

Não aplicada (FAIL). Proposta:

| Requirement | Previous Status | New Status |
| ----------- | --------------- | ---------- |
| STAT-01 … STAT-36 | Implementing | ✅ Verified (evidência nas tabelas acima) |
| STAT-37 | Implementing | ❌ Needs Fix (Fix 4) |

### Histórico (continuação)

- **Iteração 3** (HEAD `5e0fd25`): FAIL ❌. 36/37 ACs; 14/20 mutantes mortos. A N14, a M11 e a M27 morrem. A T14 deixou de conferir `background-image` (A1 e A2, regressão provada contra o teste do `ef25406`). Além disso, seletores que não começam pela classe ficam fora do teste (A6 e A7, lacuna anterior). As quatro sobreviventes estão na mesma AC (STAT-37) e o código de produção cumpre a AC. **Limite de 3 iterações atingido: escalar ao usuário.**

### Summary (iteração 3)

**Overall**: ❌ Not Ready. Evidência: `templates/kira.css:521` sob A1/A2/A6 e uma regra `section .ciclo li` (A7), com 685 passed; `inovacoes/tests/test_views_sistema_design.py:597-599` pula regras com só `background-image`; `:536-543` só lê seletores que começam pela classe.

**Spec-anchored check**: 36/37 ACs com o valor da spec afirmado e discriminante; 1 spec-precision gap de redação (título, não bloqueia)
**Sensor**: 14/20 mortas. Sobreviventes cobertas pela STAT-37: A1, A2, A6, A7. Fora da spec: A10, B7
**Gate**: 685 passed, 0 failed
**validate_state.py**: `python3 .claude/skills/tlc-spec-driven/scripts/validate_state.py ciclo-de-vida-status` → exit 1, "validation.md verdict is FAIL - route the ranked gaps to fix tasks, then re-verify (feature is not done)". É o resultado esperado para um FAIL.

**What works**: tudo o que as iterações 1 e 2 provaram continua provado. A T14 fecha o caso da N14, porque o fundo herdado agora vem do CSS real e não de um valor fixo no teste. As 7 mutações novas de comportamento (constraint do banco, nível da mensagem, método do formulário, origem do `status_visto`, código do redirect, `ol` do ciclo) morrem.

**Issues found**: Fix 4 (STAT-37: A1, A2, A6, A7), só de teste.

**Lessons**:
- **L-020 (candidate).** O caso dela (par não conferido: M27, N14) agora morre. Os sobreviventes novos são de outro tipo e viraram duas lições novas, ambas `candidate`: **L-022** (A1/A2: toda propriedade `background-*` conta como fundo numa checagem estática de cor) e **L-023** (A6/A7: selecionar as regras do componente por qualquer seletor que contenha a classe). Nenhuma foi promovida, porque tudo aconteceu numa feature só.
- **L-021.** Continua: o título segue como spec-precision gap.
- **L-019.** Não recorreu.

**Next steps**: escalar ao usuário. Opções:
1. Autorizar uma 4ª rodada: Fix 4, só de teste, e nova verificação.
2. Aceitar o risco residual da STAT-37, já que o CSS de produção cumpre o DS-08, e registrar a decisão no `STATE.md`.

---

## Decisão do usuário (2026-10-18)

Registrada pelo orquestrador depois da escalada (limite de 3 iterações atingido). Não é uma
iteração do Verifier.

- **Decisão**: aceitar o risco residual da STAT-37 e fechar a F5, corrigindo só a regressão que a
  T14 introduziu. Sem iteração 4.
- **Base**: o código de produção não mudou desde a iteração 1 e cumpre a spec; o Verifier conferiu
  à mão que todo par de cor do `.ciclo` e do `.historico` está no DS-08. As 36 outras ACs têm
  evidência e passaram no sensor das três iterações. M11, M27 e N14 continuam mortos.
- **Corrigido depois da iteração 3**: T15 (`1a57e9c`) — toda propriedade `background*` volta a ser
  conferida no teste de pares. A1 e A2 conferidos mortos numa worktree temporária pelo
  orquestrador (autor da correção, não verificação independente); N14 e M27 continuam mortos.
  Gate de build verde, 685 testes.
- **Risco residual aceito (STAT-37)**: o teste de pares só lê regras cujo seletor **começa** por
  `.ciclo`/`.historico`. Uma regra como `ol.historico li { background: var(--brand-blue) }` (A6) ou
  `section .ciclo li { color: var(--surface) }` (A7) quebraria o contraste sem derrubar a suíte.
  Mitigação: a auditoria de acessibilidade final do RNF09 confere o contraste na página renderizada;
  a ideia de correção fica em `context.md` (Deferred Ideas).
- **Fora do escopo, só registrado**: A10 (`opacity`) e B7 (desempate por `id` na ordenação) não são
  cobertos por nenhuma AC.
- **Lacuna de precisão aberta**: STAT-06/STAT-34 (`<title>` conferido pelo prefixo). Não bloqueia;
  emenda sugerida: "o `<title>` começa por 'Avançar status'".
- **`validate_state.py`**: sai com código 1, porque o veredito registrado é FAIL. É o resultado
  esperado: a feature foi fechada por decisão do usuário, e o gate determinístico continua dizendo
  a verdade sobre o veredito.

---

## Interactive UAT Results (2026-10-18)

Conferência manual no navegador pelo usuário, no banco local `kira` com a migration 0007 aplicada,
seguindo o roteiro de 12 passos: ciclo e histórico no detalhe; confirmação e "Cancelar"; dois
avanços com mensagem de sucesso que some ao recarregar; estágio final no detalhe e em `/status/`;
reenvio da confirmação → aviso de conflito sem pular estágio; terceiro sem o link e com 403 em
`/status/`; administrador avançando inovação de outra autora e registrado como responsável; filtro
"Validada" na listagem; percurso só com teclado e foco visível. **Resultado: aprovado pelo usuário.**
A conferência não altera o veredito do Verifier nem o risco residual da STAT-37, que é de teste e
não de comportamento.


---

## Iteração 4 — passe de design (2026-10-18)

**Date**: 2026-10-18
**HEAD**: `b246c63`. Passe de design `e7d8709..b246c63`: `aa2b039` (emenda da spec, do design e das tasks), `9298190` (T16, template e testes), `b246c63` (T17, testes de acessibilidade). Feature inteira: `6616da1..b246c63`.
**Escopo**: design-spec §10 F5, "transições inválidas desabilitadas, não escondidas sem explicação". STAT-04 e STAT-05 foram emendadas, e STAT-38 a STAT-41 são novas.
**Verifier**: novo sub-agente independente. Não escreveu código, testes nem correções. Re-derivou a cobertura a partir da spec.
**Produção tocada**: só `inovacoes/templates/inovacoes/inovacao_detail.html` (+10/−3). `git diff --stat e7d8709..HEAD -- templates/kira.css` vazio: **nenhum CSS novo**. O botão usa `button[aria-disabled=true]` (`templates/kira.css:250-251`), e a ajuda usa `.helptext` (`:300`). A view não mudou.
**Risco já aceito**: a lacuna A6/A7 da STAT-37 (o teste de contraste só lê seletores que *começam* por `.ciclo`/`.historico`) continua aceita pelo usuário ([Decisão do usuário](#decisão-do-usuário-2026-10-18)). O passe não toca CSS, então não reabri essa lacuna, e ela não conta como falha nova.

### Task Completion

| Task | Status | Notes |
| ---- | ------ | ----- |
| T1–T15 | ✅ Done | Inalteradas; veredito e risco aceito nas seções acima |
| T16 | ⚠️ Done com regressão de teste | `9298190`. O template cumpre os quatro estados do design. Porém `test_ultimo_estagio_explica_e_ninguem_ve_o_link[terceiro]` perdeu a asserção de página inteira `"Avançar" not in html` (ver R1). A nota da task diz "sem perder nenhuma outra asserção", e isso não confere |
| T17 | ✅ Done | `b246c63`. 704 passed (+4) |

### Gate Check (iteração 4)

- **Gate command**: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q`, rodado na árvore real com HEAD `b246c63`.
- **Result**: exit 0 em cada etapa.
  - `ruff check`: All checks passed.
  - `ruff format --check`: 110 files already formatted.
  - `makemigrations --check`: No changes detected.
  - `pytest -q`: **704 passed**, 0 failed, 0 skipped (15,9 s).
- **Test count**: 574 antes da feature → 685 (iteração 3 e T15) → 700 (T16) → 704 (T17). Nenhum teste removido. Dois testes foram alterados com autorização do usuário: um deles perdeu uma asserção (R1). O helper `_links` foi alargado (R2). Os dois casos estão em *Testes e helper alterados*.

### Tabela "Controle de transição" do design contra o HTML renderizado

Renderizei o detalhe pela suíte, numa worktree temporária, com o autor e com o terceiro. Recortei o trecho entre `</ol>` e `</section>` da seção do ciclo:

| Estado | HTML renderizado | Confere com `design.md:157-162`? |
| ------ | ---------------- | -------------------------------- |
| Pode alterar, "Em teste" | `<p class="acoes"><a href="/inovacoes/1/status/" aria-describedby="ciclo-explicacao">Avançar para “Validada”</a></p>` + `<p id="ciclo-explicacao" class="helptext">O status avança um estágio por vez e não volta ao anterior.</p>` | ✅ |
| Pode alterar, estágio final | `<p class="acoes"><button type="button" aria-disabled="true" aria-describedby="ciclo-explicacao">Avançar status</button></p>` + `<p id="ciclo-explicacao">Último estágio do ciclo.</p>`, sem `form` | ✅ |
| Não pode alterar, "Validada" | só `<p id="ciclo-explicacao">Só quem cadastrou a inovação ou um administrador pode avançar o status.</p>` | ✅ |
| Não pode alterar, estágio final | só `<p id="ciclo-explicacao">Último estágio do ciclo.</p>` | ✅ |

Os textos renderizados são idênticos, caractere por caractere, aos da spec (STAT-04, STAT-38, STAT-39, STAT-40). As constantes dos testes também conferem: `AJUDA_DO_AVANCO` e `QUEM_PODE_AVANCAR` (`test_views_detalhe.py:348-349`), e `"Último estágio do ciclo."`. O id `ciclo-explicacao` é único em cada estado.

### Spec-Anchored Acceptance Criteria (re-derivado no HEAD `b246c63`)

Caminhos relativos a `inovacoes/tests/`.

#### ACs do passe de design (re-derivadas por inteiro)

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| STAT-03 | quem pode alterar, em "Em teste"/"Validada": link "Avançar para “<próximo>”" → `/inovacoes/<id>/status/`, na seção do ciclo | `test_views_detalhe.py:344` `_links(secao, f"Avançar para “{proximo}”") == [f"/inovacoes/{pk}/status/"]` (autor e administrador × 2 status); `test_views_acessibilidade_alteracao.py:255` `links == [f"/inovacoes/{pk}/status/"]` | ❌ **GAP**: o rótulo e o destino são exatos, mas o helper alargado (`:197`) aceita qualquer atributo depois do `href`. Um link com `hidden` passa: **R2 sobrevive** |
| STAT-04 (emendada) | estágio final: "Último estágio do ciclo." na seção; nenhum link para `/status/`, para qualquer conta | `test_views_detalhe.py:371` `_explicacao(secao) == "Último estágio do ciclo."`; `:372` `"<a " not in secao`; `:373` caminho fora da página; `:374` `"Avançar para" not in html` (autor, administrador e terceiro); `:399` para `nao_autor_usuario` (terceiro, staff, superusuário) | ✅ PASS (D9 morta) |
| STAT-05 (emendada) | quem não pode alterar não vê **nenhum** link ou botão "Avançar" **na página de detalhe** | Página inteira, só com próximo estágio: `test_views_detalhe.py:410-411` (terceiro: `"Avançar" not in html`, `_botoes == []`) e `test_views_status.py:336` (`nao_autor_usuario`: `"Avançar para" not in html`). Só a seção: `test_views_detalhe.py:397-398` (estágio final) e `:424-425` (com próximo) | ❌ **GAP**: no estágio final, nenhum teste olha a página inteira à procura de um botão "Avançar". **R1 sobrevive.** Antes do passe, `"Avançar" not in html` (terceiro) o matava |
| STAT-38 | pode alterar + estágio final: botão "Avançar status" com `aria-disabled="true"` na seção | `test_views_detalhe.py:387` `[texto.strip() for _, texto in botoes] == ["Avançar status"]`; `:388` `'aria-disabled="true"' in botoes[0][0]` (autor e administrador); `test_views_acessibilidade_alteracao.py:325` `atributos.get("aria-disabled") == "true"` | ✅ PASS (D2, D14 mortas) |
| STAT-39 | não pode alterar + "Em teste"/"Validada": o texto exato na seção | `test_views_detalhe.py:423` `_explicacao(secao) == QUEM_PODE_AVANCAR`, 3 contas × 2 status. O texto não aparece ao autor (`:439`) nem no estágio final (`:376`) | ✅ PASS (D5, D6 mortas) |
| STAT-40 | pode alterar + "Em teste"/"Validada": ajuda exata na seção | `test_views_detalhe.py:437` `_explicacao(secao) == AJUDA_DO_AVANCO` (autor e administrador × 2 status); ausente para quem não pode alterar (`:426`) e no estágio final (`:375`) | ✅ PASS (D10, D13 mortas). D11 é só nota |
| STAT-41 | botão focável (sem `disabled`, sem `tabindex` positivo); `aria-describedby` → "Último estágio do ciclo."; link → ajuda da STAT-40 por `aria-describedby`; botão `type="button"` fora de `form` | `test_views_acessibilidade_alteracao.py:323` (exatamente um botão); `:324` `type == "button"`; `:326` `"disabled" not in atributos`; `:327` `tabindex <= 0`; `:328` `no_form is False`; `:329` `_texto_do_id(trecho, atributos["aria-describedby"]) == "Último estágio do ciclo."`; `:338-340` o `aria-describedby` do link resolve para a ajuda exata, nos 2 status | ✅ PASS ⚠️ (D2b, D3, D4, D7, D8 mortas). D12 (`tabindex="-1"`) sobrevive: lacuna de precisão, ver abaixo |
| STAT-34 | só elementos nativos, sem `tabindex` positivo, foco visível em cada link e botão; `h1`/`<title>` "Avançar status" | Novo: `test_views_acessibilidade_alteracao.py:320` `_afirma_so_nativos` na seção do estágio final; `:167` `detalhe_final` entra em `test_paginas_do_ciclo_tem_foco_visivel_com_contorno` (`:261-267`, CSS real da página com o botão). Anterior, relido: `:222-236` (confirmação: um `submit` dentro do `form`; estágio final: só o link de volta); `:240-257` (seções do detalhe); `:271-280` (`h1` exato, `<title>` por prefixo) | ✅ PASS ⚠️ (título: lacuna de redação herdada, sem bloqueio) |

#### Amostragem das demais ACs no HEAD (12, relidas linha a linha)

| AC | `file:line` + assertion | Result |
| -- | ----------------------- | ------ |
| STAT-01 | `test_views_detalhe.py:310-314` `findall(h2) == ["Ciclo de vida"]`; itens sem o sufixo `== ETAPAS` | ✅ |
| STAT-02 | `test_views_detalhe.py:323-327` `html.count("(status atual)") == 1`; lista inteira igual à esperada, nos 3 status | ✅ |
| STAT-06 | `test_views_status.py:44-67` 200, `h1 == ["Avançar status"]`, texto exato, botão `submit` com o rótulo exato, `method="post"`, `status_visto` oculto, `cancelar == [f"/inovacoes/{pk}/"]` | ✅ ⚠️ (título) |
| STAT-07 | `test_views_status.py:175-176` `assertRedirects(…, f"/inovacoes/{pk}/")`, `== VALIDADA` | ✅ |
| STAT-10 | `test_views_status.py:228-234` POST: redirect, `== DISPONIVEL`, `count() == 0`, `[("warning", ULTIMO_ESTAGIO)]` | ✅ |
| STAT-12 | `test_views_status.py:237-247` `[None, VALIDADA, "APROVADA"]`: `== EM_TESTE`, `count() == 0`, `[("warning", _conflito("Em teste"))]` | ✅ |
| STAT-14 | `test_views_status.py:177-183` `(inovacao_id, anterior, novo) == (pk, EM_TESTE, VALIDADA)`, `responsavel == autor` | ✅ |
| STAT-19 | `test_views_status.py:323-327` 403, `acesso_negado.html`, `NEGADO`, status e contagem | ✅ |
| STAT-24/25 | `test_views_detalhe.py:464-476` lista exata, do mais antigo ao mais recente, contra a ordem de criação; `:479-484` fuso de São Paulo | ✅ |
| STAT-26 | `test_views_detalhe.py:487-492` `<p class="vazio">Nenhuma mudança de status registrada.</p>`, sem `<li` | ✅ |
| STAT-31 | `test_ciclo_de_vida.py:67-73` `IntegrityError` com `mudanca_de_status_transicao_valida`, 7 pares | ✅ |
| STAT-36 | `test_views_erro_500.py:174-184` 403 que não é o acesso negado, `== EM_TESTE`, `count() == 0` | ✅ |

As outras ACs (STAT-08, 09, 11, 13, 15–18, 20–23, 27–30, 32, 33, 35) foram herdadas das iterações 1 a 3. O passe de design não tocou os arquivos de teste delas (`test_views_status.py`, `test_ciclo_de_vida.py` e `test_views_erro_500.py` estão fora do diff `e7d8709..HEAD`), nem a produção que elas exercitam. A STAT-37 segue com o risco residual A6/A7 aceito.

**Status**: ❌ 39/41 ACs com o valor da spec afirmado e discriminante. STAT-03 e STAT-05 têm asserção, mas cada uma deixa sobreviver um mutante que a AC cobre (R2 e R1). A STAT-37 conta à parte, pelo risco aceito. Há 2 lacunas de precisão que não bloqueiam: o título (herdada) e o "focusable" da STAT-41 (nova).

### Testes e helper alterados: houve enfraquecimento?

1. **`test_ultimo_estagio_explica_e_ninguem_ve_o_link`** (`test_views_detalhe.py:363-376`): **sim, enfraquecido para o terceiro.**
   - **Mudança.** O teste trocou `"Avançar" not in html` por `"<a " not in secao` + `"Avançar para" not in html`. Para autor e administrador, a troca é necessária, porque a STAT-38 agora põe "Avançar status" na página. Para o parâmetro `terceiro`, porém, a STAT-05 emendada **continua** proibindo qualquer botão "Avançar" na página. A asserção antiga continuava válida e foi perdida.
   - **Compensação parcial.** `test_ultimo_estagio_nao_mostra_botao_a_quem_nao_pode_alterar` (`:391-399`) olha só a seção (`"Avançar" not in secao`, `_botoes(secao) == []`).
   - **Prova.** Numa worktree, a linha removida, isolada num teste (`"Avançar" not in html` para o terceiro em "Disponível para replicação"), passa no HEAD e **falha sob R1**. A suíte do HEAD passa inteira sob R1 (704 passed).
2. **`test_terceiro_nao_ve_o_link_de_avancar`** (`:402-413`): **não foi enfraquecido.** Mantém `"Avançar" not in html`, o caminho fora da página, os 3 itens e "Último estágio do ciclo." ausente. Ganhou `_botoes(secao) == []`.
3. **Helper `_links`** (`:191-197`): **enfraquecido, de forma menor.**
   - **Mudança.** O regex passou de `<a href="…">` exato para `<a href="…"[^>]*>`. Ele continua sem atravessar `>`, e o rótulo e o `href` continuam exatos. As asserções negativas (`_links(...) == []` do Editar/Excluir) ficaram mais fortes.
   - **Enfraquecimento.** As positivas (STAT-03; EDEX-03 e EDEX-24 com Editar/Excluir) passam a aceitar links com atributos que escondem o controle, como `hidden` ou `aria-hidden="true"`. O regex antigo os recusava. **R2** prova isso para a STAT-03.
   - **Correção.** Aceitar só o atributo esperado (`(?: aria-describedby="[^"]*")?`) restaura a força sem perder o propósito.

### Discrimination Sensor (iteração 4)

**Preparação.**
- Worktree: `git worktree add --detach scratchpad/wt4 HEAD`, com o `.env` copiado.
- Banco: PostgreSQL de teste na porta 5433.
- Código em uso: `inovacoes.__file__` resolve para a worktree.
- Linha de base: **704 passed**.

**Execução.** Cada mutação foi feita por substituição exata e única (`count == 1`) em `inovacoes/templates/inovacoes/inovacao_detail.html`. Para cada uma, rodei a suíte inteira com `.venv/bin/pytest -q -p no:cacheprovider`, depois `git checkout -- .` e `git diff --quiet`.

**Limpeza.** No fim, `git worktree remove --force` e `git worktree prune`. O `git status --porcelain` da árvore real está vazio e é idêntico à linha de base gravada antes do sensor. O HEAD continua `b246c63`, e `git worktree list` só mostra a árvore principal.

#### Mutações do passe de design

| # | File:line | Mutação | Killed? (testes que falharam) | AC |
| - | --------- | ------- | ----------------------------- | -- |
| D1 | `inovacao_detail.html:58-60` | botão desabilitado para quem não pode alterar (sem o `{% if pode_alterar %}`) | ✅ `test_ultimo_estagio_nao_mostra_botao_a_quem_nao_pode_alterar[terceiro, staff, superusuario]` | STAT-05 |
| D2 | `:59` | `disabled` no lugar de `aria-disabled="true"` | ✅ `test_ultimo_estagio_mostra_avancar_desabilitado…[autor, administrador]`, `test_botao_desabilitado_continua_focavel…` | STAT-38, STAT-41 |
| D2b | `:59` | `disabled` **somado** a `aria-disabled="true"` | ✅ `test_botao_desabilitado_continua_focavel…` | STAT-41 |
| D3 | `:59` | botão sem `aria-describedby` | ✅ `test_botao_desabilitado_continua_focavel…` | STAT-41 |
| D4 | `:63` | `aria-describedby` do link → `ciclo-titulo` (id errado e existente) | ✅ `test_link_de_avancar_e_descrito_pela_ajuda[EM_TESTE, VALIDADA]` | STAT-41 |
| D5 | `:64`, `:66` | textos da ajuda (STAT-40) e da permissão (STAT-39) trocados | ✅ 10: `test_quem_pode_alterar_le_a_ajuda…`, `test_quem_nao_pode_alterar_le_quem_pode_avancar…` (3 contas × 2 status), `test_link_de_avancar…` | STAT-39, STAT-40 |
| D6 | `:64` | texto da STAT-39 mostrado também ao autor e ao administrador | ✅ `test_quem_pode_alterar_le_a_ajuda_de_um_estagio_por_vez` (4) | STAT-39/40 |
| D7 | `:59` | botão dentro de `<form method="post">` | ✅ `test_botao_desabilitado_continua_focavel…` | STAT-41 |
| D8 | `:59` | `type="submit"` | ✅ `test_botao_desabilitado_continua_focavel…` | STAT-41 |
| D9 | `:59` | link `<a href="…/status/">Avançar status</a>` ao lado do botão, no estágio final | ✅ `test_ultimo_estagio_explica_e_ninguem_ve_o_link[autor, administrador]` | STAT-04 |
| D10 | `:64` | ajuda da STAT-40 removida | ✅ `test_quem_pode_alterar_le_a_ajuda…` (4), `test_link_de_avancar…` (2) | STAT-40, STAT-41 |
| D11 | `:64` | ajuda sem `class="helptext"` | ⚪ Survived, **fora da spec**: a STAT-40 fixa o texto, não a classe (a classe é detalhe do design) | nota |
| D12 | `:59` | `tabindex="-1"` no botão | ⚪ Survived (`:327` aceita `<= 0`). **Lacuna de precisão da STAT-41**: o parêntese da AC define "focusable" como "no `disabled`, no positive `tabindex`", e `-1` cumpre essa letra. O `design.md:164` promete que o botão "continua no Tab", e `-1` o tira do Tab | ⚠️ SPG |
| D13 | `:62` | botão desabilitado também quando há próximo estágio | ✅ `test_quem_pode_alterar_le_a_ajuda…` (4) | STAT-38, STAT-40 |
| D14 | `:58` | condição invertida (`{% if not pode_alterar %}`) | ✅ 7: STAT-38 (2), STAT-05 no estágio final (3), STAT-41 | STAT-05, STAT-38 |

#### Regressões sobre o que os testes alterados guardavam

| # | File:line | Mutação | Killed? | AC |
| - | --------- | ------- | ------- | -- |
| **R1** | `inovacao_detail.html:68` (depois da seção do ciclo) | `{% if not pode_alterar and not inovacao.proximo_status %}<p><button type="button" aria-disabled="true">Avançar status</button></p>{% endif %}`: quem não pode alterar vê o botão no estágio final, fora da seção | ❌ **Survived** (704 passed). A asserção removida de `test_ultimo_estagio_explica_e_ninguem_ve_o_link[terceiro]`, isolada, passa no HEAD e **falha** com R1. Regressão do teste alterado | **STAT-05** ("SHALL NOT display any 'Avançar' link or button on its detail page") |
| **R2** | `inovacao_detail.html:63` | `<a href="…/status/" hidden aria-describedby="ciclo-explicacao">`: o link de avançar fica oculto para todos | ❌ **Survived** (704 passed). O `_links` alargado (`test_views_detalhe.py:197`) aceita `hidden`; o regex anterior, exato, o recusaria. As checagens de atributo da T17 (`:333-340`) não procuram `hidden` | **STAT-03** ("SHALL display … a link") |

**Sensor depth**: expandido (autorização na tela e acessibilidade): 15 mutações do passe e 2 regressões.
**Result**: 13/17 mortas. Das 4 sobreviventes:
- **R1 e R2** são cobertas por AC (STAT-05 e STAT-03) → FAIL ❌.
- **D12** é uma lacuna de precisão da spec (não bloqueia).
- **D11** está fora da spec (só nota).

Nenhuma sobrevivente é da classe A6/A7 já aceita.

### Spec-Precision Gaps (iteração 4)

- **STAT-41, "focusable" (novo).** A AC define focável pela ausência de `disabled` e de `tabindex` positivo. Com essa definição, `tabindex="-1"` (D12) passa, mas tira o botão da ordem de Tab que o design e o Independent Test da história prometem ("Tab … até o botão"). Sugestão de emenda: "SHALL keep the disabled 'Avançar status' button in the sequential Tab order (no `disabled`, no `tabindex` attribute other than `0`)". O teste então afirmaria `tabindex` ausente ou igual a `0`. **Não bloqueia.**
- **STAT-06/STAT-34, `<title>` (herdado).** Igual às iterações 2 e 3, sem bloqueio.

### Fix Plans (iteração 4)

#### Fix 5: STAT-05 no estágio final só é conferida dentro da seção (R1) — Major, só teste

- **Root cause**: a T16 trocou `"Avançar" not in html` por asserções que valem também para quem pode alterar. Com isso, perdeu a checagem de página inteira para quem não pode alterar no estágio final (`test_views_detalhe.py:363-376`, parâmetro `terceiro`). O teste `:391-399` só olha a `secao`.
- **Fix task**: em `test_ultimo_estagio_nao_mostra_botao_a_quem_nao_pode_alterar`, afirmar sobre a página inteira: `"Avançar" not in html` e nenhum `<button` com "Avançar" no `html`. Isso cobre terceiro, staff e superusuário. Opcional: restaurar `"Avançar" not in html` quando `conta == "terceiro"` em `:365`.
- **Verify**: numa worktree, R1 faz o teste falhar; D1 e D14 continuam mortas; no HEAD o teste passa.
- **Done when**: R1 está morta, o gate de build está verde e nenhum código de produção mudou.

#### Fix 6: `_links` aceita atributos que escondem o link (R2) — Minor, só teste

- **Root cause**: `test_views_detalhe.py:197` `<a href="([^"]*)"[^>]*>` aceita qualquer atributo depois do `href`, inclusive `hidden` e `aria-hidden`.
- **Fix task**: restringir o regex ao atributo esperado, `rf'<a href="([^"]*)"(?: aria-describedby="[^"]*")?>\s*{rotulo}\s*</a>'`. Alternativa: manter o regex e afirmar, em `test_link_de_avancar_e_descrito_pela_ajuda`, que o link não tem `hidden` nem `aria-hidden`.
- **Verify**: R2 morre, e os testes de Editar/Excluir (EDEX-03, EDEX-24) e da STAT-03 continuam passando no HEAD.
- **Done when**: R2 está morta e o gate de build está verde.

### Requirement Traceability Update (iteração 4)

Não aplicada (FAIL). A `spec.md` e o `tasks.md` não foram alterados. Proposta para quando os Fix 5 e 6 passarem no Verifier:

| Requirement | Status atual | Proposto |
| ----------- | ------------ | -------- |
| STAT-04, STAT-38, STAT-39, STAT-40, STAT-41 | Implementing | ✅ Verified |
| STAT-03 | Verified | ❌ Needs Fix (Fix 6; regressão do teste, não da produção) |
| STAT-05 | Implementing (emendada) | ❌ Needs Fix (Fix 5) |
| STAT-37 | Implementing (risco residual aceito) | sem mudança |

### Summary (iteração 4)

**Overall**: ❌ Not Ready.
- **O que não é o problema.** O template do passe de design cumpre a spec e a tabela do design nos quatro estados, sem CSS novo.
- **Por que FAIL.** Dois mutantes cobertos por AC sobrevivem:
  - **R1** (STAT-05): botão "Avançar status" para quem não pode alterar, fora da seção, no estágio final.
  - **R2** (STAT-03): link de avançar com `hidden`.
- **Origem.** Os dois vêm da T16: um teste perdeu uma asserção e um helper foi alargado.

**Spec-anchored check**: 39/41 ACs com o valor da spec afirmado e discriminante. STAT-03 e STAT-05 têm lacuna de discriminação, e a STAT-37 fica fora da conta pelo risco aceito. 2 lacunas de precisão que não bloqueiam (STAT-41 "focusable" e o título).
**Sensor**: 13/17 mortas. Sobreviventes cobertas por AC: R1 (STAT-05) e R2 (STAT-03). Lacuna de precisão: D12. Fora da spec: D11.
**Gate**: 704 passed, 0 failed; ruff, format e makemigrations limpos.
**validate_state.py**: `python3 .claude/skills/tlc-spec-driven/scripts/validate_state.py ciclo-de-vida-status` → exit 1, "validation.md verdict is FAIL - route the ranked gaps to fix tasks, then re-verify (feature is not done)". É o resultado esperado para um FAIL.

**Lessons**: três lições `candidate` novas, todas desta feature, então nenhuma foi promovida:

| Lição | Sinal | Regra |
| ----- | ----- | ----- |
| **L-024** | R1 | Ao relaxar uma asserção negativa de página para alguns papéis, mantê-la para os papéis cuja regra não mudou |
| **L-025** | R2 | Helper de HTML alargado aceita só os atributos esperados |
| **L-026** | D12, lacuna de precisão | AC de controle alcançável por teclado exige a ordem de Tab, não só "focável" |

As demais sobreviventes não geraram lição:

- **D11** está fora da spec.
- **L-020, L-022 e L-023** (CSS) não recorreram, porque o passe não tocou CSS.
- **L-003** (confirmada) foi aplicada: `nao_autor_usuario` cobre staff e superusuário na STAT-39 e no estágio final. Por isso não houve penalidade.

**What works**:
- **Controle de transição.** Botão desabilitado com `aria-disabled`, focável, `type="button"`, fora de `form` e descrito pela explicação. Explicação de permissão para quem não pode alterar. Ajuda ligada ao link.
- **Sensor.** Todas as 13 mutações de comportamento do controle que a spec cobre morrem.
- **Testes alterados.** Os testes dos estados com próximo estágio não perderam força.

**Next steps**: Fix 5 e Fix 6 (só testes) e nova verificação. A iteração 4 foi aberta pelo passe de design, fora do ciclo de 3 iterações já encerrado. Cabe ao usuário decidir se as correções entram ou se aceita R1 e R2 como risco.

---

## Iteração 5 — passe de design (2026-10-18)

**Date**: 2026-10-18
**HEAD**: `6020a4f`. Correções da iteração 4 `16fe215..6020a4f`: `380b575` (emenda da STAT-41 e plano da Fase 9), `64b97f2` (T18, R1), `44ea0f7` (T19, R2) e `6020a4f` (T20, D12). Passe de design inteiro: `e7d8709..6020a4f`.
**Produção tocada desde a iteração 4**: nenhuma. `git diff b246c63..HEAD -- . ':!inovacoes/tests' ':!.specs'` sai vazio. Só mudaram `inovacoes/tests/test_views_detalhe.py` (+15/−5 líquido), `inovacoes/tests/test_views_acessibilidade_alteracao.py` (+2/−1) e os artefatos de `.specs/`.
**Verifier**: novo sub-agente independente. Não escreveu código, testes nem correções. Re-derivou a cobertura a partir da `spec.md` (STAT-41 lida na redação emendada).
**Risco já aceito**: a lacuna A6/A7 da STAT-37 continua aceita ([Decisão do usuário](#decisão-do-usuário-2026-10-18)). Nenhuma sobrevivente desta iteração pertence a essa classe.

### Task Completion

| Task | Status | Notes |
| ---- | ------ | ----- |
| T1–T17 | ✅ Done | Inalteradas desde a iteração 4 |
| T18 | ✅ Done | `64b97f2`. R1 morta (4 falhas) |
| T19 | ✅ Done | `44ea0f7`. R2 morta (4 falhas) |
| T20 | ✅ Done | `6020a4f`. D12 morta (1 falha) |

### Gate Check (iteração 5)

- **Gate command**: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q`, rodado na árvore real com HEAD `6020a4f`.
- **Result**: exit 0 em cada etapa.
  - `ruff check`: All checks passed.
  - `ruff format --check`: 110 files already formatted.
  - `makemigrations --check`: No changes detected.
  - `pytest -q`: **704 passed**, 0 failed, 0 skipped (16,9 s).
- **Test count**: 704 (igual à iteração 4; a Fase 9 não acrescentou nem removeu testes).

### T18–T20: houve enfraquecimento?

**Não.** Cada diff foi comparado com o commit pai.

1. **T18** (`64b97f2`, `test_views_detalhe.py`):
   - `test_ultimo_estagio_explica_e_ninguem_ve_o_link` ganha `:378-379`, `if conta == "terceiro": assert "Avançar" not in html`. Recupera a asserção que a T16 tirou, sem mexer nas outras seis.
   - `test_ultimo_estagio_nao_mostra_botao_a_quem_nao_pode_alterar` troca `"Avançar" not in secao` por `"Avançar" not in html` (`:403`). Como a seção é um trecho da página, a asserção nova implica a antiga. `_botoes(secao) == []` e a explicação exata ficam.
2. **T19** (`44ea0f7`, `_links` em `:191-197`):
   - O regex passa de `<a href="…"[^>]*>` para `<a href="…"(?: aria-describedby="[^"]*")?>`. As asserções positivas (STAT-03 `:344`; EDEX-03/EDEX-31 `:204`, `:214`, `:241`, `:251`, `:270-271`) ficam mais fortes.
   - As negativas (`_links(...) == []` em `:222`, `:259`, `:279-280`) ficam mais fracas que no `b246c63`, porque um link com outro atributo deixaria de casar. Mas todas estão acompanhadas de `f"/inovacoes/{pk}/editar|excluir/" not in html` (`:223`, `:260`, `:281-282`), que não depende do helper. Em relação ao regex original da F4 (`<a href="…">` exato), nenhuma asserção perdeu força. **Não há enfraquecimento líquido.**
3. **T20** (`6020a4f`, `test_views_acessibilidade_alteracao.py:328`): `int(tabindex) <= 0` vira `atributos.get("tabindex", "0") == "0"`, que é estritamente mais forte e segue a STAT-41 emendada. As demais checagens (`:320-330`) ficam.

### Spec-Anchored Acceptance Criteria (re-derivado no HEAD `6020a4f`)

Caminhos relativos a `inovacoes/tests/`. O template está em `inovacoes/templates/inovacoes/inovacao_detail.html:55-68`.

#### ACs re-derivadas por inteiro

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| STAT-03 | quem pode alterar, em "Em teste"/"Validada": **exibe** na seção do ciclo o link "Avançar para “<próximo>”" → `/inovacoes/<id>/status/` | `test_views_detalhe.py:344` `_links(secao, f"Avançar para “{proximo}”") == [f"/inovacoes/{pk}/status/"]` (autor e administrador × 2 status), com o regex restrito de `:197`; `test_views_acessibilidade_alteracao.py:255` `links == [f"/inovacoes/{pk}/status/"]` | ❌ **GAP**: R2 (`hidden` no `<a>`) e E1 (`aria-hidden`) morrem. Mas **E9** (`hidden` no `<p class="acoes">` que envolve o link) sobrevive: nenhum teste olha os ancestrais do link |
| STAT-04 (emendada) | estágio final: "Último estágio do ciclo." na seção; nenhum link para `/status/`, para qualquer conta | `test_views_detalhe.py:371` `_explicacao(secao) == "Último estágio do ciclo."`; `:372` `"<a " not in secao`; `:373` caminho fora da página; `:374` `"Avançar para" not in html` (autor, administrador, terceiro); `:404` para `nao_autor_usuario` | ✅ PASS (E13 morta) |
| STAT-05 (emendada) | quem não pode alterar não vê **nenhum** link ou botão "Avançar" na página de detalhe | Estágio final, página inteira: `test_views_detalhe.py:403` (`nao_autor_usuario`: terceiro, staff, superusuário) e `:379` (terceiro). Com próximo estágio, página inteira: `:415` `"Avançar" not in html` **só para `terceiro`**. Para `nao_autor_usuario` só há `test_views_status.py:336` `"Avançar para" not in html` (página) e `test_views_detalhe.py:429-430` `"Avançar" not in secao`, `_botoes(secao) == []` (seção) | ❌ **GAP**: R1 e E2 morrem. Mas **E2b** sobrevive: um botão "Avançar status" fora da seção, só para conta `USUARIO` com `is_staff` em "Em teste"/"Validada". A checagem de página inteira por "Avançar" não roda para staff/superusuário com próximo estágio |
| STAT-38 | pode alterar + estágio final: **exibe** na seção o botão "Avançar status" com `aria-disabled="true"` | `test_views_detalhe.py:390` `[texto.strip() …] == ["Avançar status"]`; `:391` `'aria-disabled="true"' in botoes[0][0]` (autor, administrador); `test_views_acessibilidade_alteracao.py:325` `aria-disabled == "true"` | ❌ **GAP**: E4, E8 e E12 morrem. Mas **E10** (`hidden` no `<p>` do botão) e **E11** (`hidden` no próprio `<button>`) sobrevivem. Nenhum teste recusa `hidden` no botão ou num ancestral |
| STAT-39 | não pode alterar + "Em teste"/"Validada": o texto exato na seção | `test_views_detalhe.py:428` `_explicacao(secao) == QUEM_PODE_AVANCAR` (3 contas × 2 status); ausente no estágio final (`:376`) e para quem pode alterar (`:444`) | ✅ PASS (E3 morta) |
| STAT-40 | pode alterar + "Em teste"/"Validada": **exibe** na seção a ajuda exata | `test_views_detalhe.py:442` `_explicacao(secao) == AJUDA_DO_AVANCO` (2 contas × 2 status); `test_views_acessibilidade_alteracao.py:339-341`; ausente no estágio final (`:375`) e para quem não pode alterar (`:431`) | ❌ **GAP**: E5 morta. Mas **E16** (`hidden` no `<p id="ciclo-explicacao" class="helptext">`) sobrevive. `_explicacao` lê o texto e ignora atributos |
| STAT-41 (emendada) | botão na ordem do Tab (sem `disabled`; `tabindex` ausente ou `0`); `aria-describedby` → "Último estágio do ciclo."; link → ajuda da STAT-40; botão `type="button"` fora de `form` | `test_views_acessibilidade_alteracao.py:322` um botão; `:324` `type == "button"`; `:325` `aria-disabled == "true"`; `:326` sem `disabled`; `:328` `tabindex` ausente ou `"0"`; `:329` fora de `form`; `:330` `_texto_do_id(…) == "Último estágio do ciclo."`; `:338-341` o link resolve para a ajuda exata, nos 2 status | ✅ PASS (D12, E3, E7, E8 mortas) |
| STAT-34 | só nativos, sem `tabindex` positivo, foco visível em cada link e botão; um `h1` e `<title>` "Avançar status" | `test_views_acessibilidade_alteracao.py:207-218` `_afirma_so_nativos` (sem papel de controle, `tabindex <= 0`), aplicado em `:224`, `:250`, `:320`; `:233-236` confirmação com um `submit` no `form` e um link; `:248-257` seções rotuladas pelo `h2`, uma `ol`; `:261-267` `:focus-visible` com `outline` sólido nas 4 páginas do ciclo, inclusive `detalhe_final`; `:278-280` `h1` exato e `<title>` por prefixo | ✅ PASS ⚠️ (E7, E14 mortas; título por prefixo, lacuna herdada sem bloqueio) |

#### Amostragem das demais ACs no HEAD (10, relidas linha a linha)

`test_views_status.py`, `test_ciclo_de_vida.py` e `test_views_erro_500.py` estão fora do diff `b246c63..HEAD`.

| AC | `file:line` + assertion | Result |
| -- | ----------------------- | ------ |
| STAT-01 | `test_views_detalhe.py:313` `findall(h2) == ["Ciclo de vida"]`; `:315` itens sem o sufixo `== ETAPAS` | ✅ |
| STAT-02 | `test_views_detalhe.py:326` `html.count("(status atual)") == 1`; `:329` lista inteira igual à esperada, 3 status | ✅ |
| STAT-06 | `test_views_status.py:46-67` 200, template, `h1 == ["Avançar status"]`, texto exato, `method="post"`, um `submit` "Avançar para “<próximo>”", `status_visto` oculto com o status gravado, `cancelar == [f"/inovacoes/{pk}/"]` | ✅ ⚠️ (título) |
| STAT-07 | `test_views_status.py:175-176` `assertRedirects(…, f"/inovacoes/{pk}/")`, `== VALIDADA` | ✅ |
| STAT-10 | `test_views_status.py:230-234` POST: redirect, `== DISPONIVEL`, `count() == 0`, `[("warning", ULTIMO_ESTAGIO)]` | ✅ |
| STAT-12 | `test_views_status.py:237-247` `[None, VALIDADA, "APROVADA"]`: `== EM_TESTE`, `count() == 0`, `[("warning", _conflito("Em teste"))]` | ✅ |
| STAT-14 | `test_views_status.py:177-183` `(inovacao_id, anterior, novo) == (pk, EM_TESTE, VALIDADA)`, `responsavel == autor` | ✅ |
| STAT-19/20 | `test_views_status.py:310-327` terceiro, staff e superusuário, GET e POST: 403, `acesso_negado.html`, `NEGADO`, status e contagem | ✅ |
| STAT-31 | `test_ciclo_de_vida.py:67-73` `IntegrityError` com `mudanca_de_status_transicao_valida`, 7 pares | ✅ |
| STAT-36 | `test_views_erro_500.py:173-183` 403 que não é o acesso negado, `== EM_TESTE`, `count() == 0` | ✅ |

As demais ACs (STAT-08, 09, 11, 13, 15–18, 21–30, 32, 33, 35) foram herdadas das iterações 1 a 4, sem mudança nos testes nem na produção que as exercita. A STAT-37 segue com o risco residual A6/A7 aceito.

**Status**: ❌ 36/41 ACs com o valor da spec afirmado e discriminante. STAT-03, STAT-05, STAT-38 e STAT-40 têm asserção, mas cada uma deixa sobreviver um mutante que a AC cobre (E9, E2b, E10/E11, E16). A STAT-37 conta à parte, pelo risco aceito.

### Discrimination Sensor (iteração 5)

**Preparação.**
- Worktree: `git worktree add --detach scratchpad/wt5 HEAD`, com o `.env` copiado.
- Banco: PostgreSQL de teste na porta 5433.
- Código em uso: `inovacoes.__file__` resolve para a worktree.
- Linha de base: **704 passed**.

**Execução.** Cada mutação foi feita por substituição exata e única (`count == 1`) em `inovacoes/templates/inovacoes/inovacao_detail.html`. Para cada uma, rodei a suíte inteira com `.venv/bin/pytest -q -p no:cacheprovider`, depois `git checkout -- .` e `git diff --quiet`.

**Sondas.** Para provar que as sobreviventes são efetivas, usei um arquivo de sonda descartável, não rastreado, só na worktree. Cada sonda passa no HEAD (9 passed) e falha com o seu mutante. Depois apaguei o arquivo.

**Limpeza.** No fim, `git worktree remove --force` e `git worktree prune`. `git worktree list` só mostra a árvore principal. O `git status --porcelain` da árvore real está vazio e é idêntico à linha de base gravada antes do sensor. O HEAD continua `6020a4f`.

#### Re-injeções da iteração 4

| # | File:line | Mutação | Killed? (testes que falharam) | AC |
| - | --------- | ------- | ----------------------------- | -- |
| R1 | `inovacao_detail.html:68` (depois da seção) | `{% if not pode_alterar and not inovacao.proximo_status %}<p><button type="button" aria-disabled="true">Avançar status</button></p>{% endif %}` | ✅ 4: `test_ultimo_estagio_explica_e_ninguem_ve_o_link[terceiro]`, `test_ultimo_estagio_nao_mostra_botao_a_quem_nao_pode_alterar[terceiro, staff, superusuario]` | STAT-05 |
| R2 | `:63` | `hidden` no `<a>` de avançar | ✅ 4: `test_quem_pode_alterar_ve_o_link_de_avancar[2 contas × 2 status]` | STAT-03 |
| D12 | `:59` | `tabindex="-1"` no botão | ✅ `test_botao_desabilitado_continua_focavel_e_le_a_explicacao` | STAT-41 |

#### Mutações novas

| # | File:line | Mutação | Killed? (testes que falharam) | AC |
| - | --------- | ------- | ----------------------------- | -- |
| E1 | `:63` | `aria-hidden="true"` no `<a>` | ✅ 4: `test_quem_pode_alterar_ve_o_link_de_avancar[…]` | STAT-03 |
| E2 | `:68` | link visível `<a href="/inovacoes/">Avançar</a>` fora da seção, para quem não pode alterar, com próximo estágio | ✅ 2: `test_terceiro_nao_ve_o_link_de_avancar[EM_TESTE, VALIDADA]` | STAT-05 |
| **E2b** | `:68` | `{% if not pode_alterar and inovacao.proximo_status and user.is_staff %}<p><button type="button" aria-disabled="true">Avançar status</button></p>{% endif %}` (botão fora da seção para `USUARIO` com `is_staff`) | ❌ **Survived** (704 passed). Sonda `"Avançar" not in html` com `nao_autor_usuario` falha em `[staff-EM_TESTE]` e `[staff-VALIDADA]` | **STAT-05** |
| E3 | `:59` | `aria-describedby` do botão → um `<p id="ciclo-permissao">` novo com o texto da STAT-39 | ✅ 3: `test_botao_desabilitado_continua_focavel…`, `test_ultimo_estagio_explica_e_ninguem_ve_o_link[autor, administrador]` | STAT-41, STAT-39 |
| E4 | `:59` | `aria-disabled="false"` | ✅ 3: `test_ultimo_estagio_mostra_avancar_desabilitado…[2]`, `test_botao_desabilitado_continua_focavel…` | STAT-38 |
| E5 | `:61` | ajuda da STAT-40 (`.helptext`) mostrada também no estágio final | ✅ 3: `test_ultimo_estagio_explica_e_ninguem_ve_o_link[3 contas]` | STAT-40, design |
| E6 | `:61` | "Último estágio do ciclo." duplicado (dois `#ciclo-explicacao`) | ⚪ Survived, **fora da letra da spec**: nenhuma AC proíbe repetir o texto. O `id` duplicado é HTML inválido, e o `aria-describedby` resolve para o primeiro. Sonda com `count('id="ciclo-explicacao"') == 1` falha | nota |
| E7 | `:59` | `tabindex="1"` no botão | ✅ `test_botao_desabilitado_continua_focavel…` | STAT-34, STAT-41 |
| E8 | `:59` → `:71` | botão movido para dentro da seção "Histórico de status" | ✅ 3: `test_ultimo_estagio_mostra_avancar_desabilitado…[2]`, `test_botao_desabilitado_continua_focavel…` | STAT-38 |
| **E9** | `:63` | `<p class="acoes" hidden>` em volta do link de avançar | ❌ **Survived** (704 passed). Sonda falha | **STAT-03** ("SHALL display … a link") |
| **E10** | `:59` | `<p class="acoes" hidden>` em volta do botão desabilitado | ❌ **Survived** (704 passed). Sonda falha | **STAT-38** ("SHALL display … a button") |
| **E11** | `:59` | `<button hidden type="button" …>` | ❌ **Survived** (704 passed). Sonda falha | **STAT-38** |
| E12 | `:59` | rótulo "Avançar" em vez de "Avançar status" | ✅ 2: `test_ultimo_estagio_mostra_avancar_desabilitado…[2]` | STAT-38 |
| E13 | `:61` → depois de `:68` | "Último estágio do ciclo." movido para fora da seção | ✅ 7: `test_ultimo_estagio_explica…[3]`, `test_ultimo_estagio_nao_mostra_botao…[3]`, `test_botao_desabilitado…` | STAT-04 |
| E14 | `:63` | `role="button"` no link | ✅ 6: STAT-03 (4), `test_secoes_do_detalhe_sao_nativas…[ciclo]`, `test_views_acessibilidade_consulta.py::test_pagina_so_tem_controles_nativos[detalhe]` | STAT-03, STAT-34 |
| E15 | `:59` | `style="display:none"` no botão | ✅ 2: `test_views_sistema_design.py::test_pecas_e_base_nao_tem_estilo_inline…`, `test_toda_tela_estende_o_base_sem_estilo_proprio` | STAT-38 (via DS) |
| **E16** | `:64` | `hidden` no `<p id="ciclo-explicacao" class="helptext">` | ❌ **Survived** (704 passed). Sonda falha | **STAT-40** ("SHALL display … the help text") |
| E17 | `:63` | `<p class="acoes" inert>` em volta do link | ⚪ Survived (704 passed). Sonda falha. O link continua **exibido**, então a letra da STAT-03 é cumprida. `inert` o tira do Tab e da árvore de acessibilidade, e a STAT-34 pede foco visível "on each link", o que pressupõe um link focável. Nenhuma AC exige, com todas as letras, que o link de avançar esteja na ordem do Tab (a STAT-41 só exige isso do botão) | ⚠️ SPG |

**Sensor depth**: expandido (autorização na tela e acessibilidade): 3 re-injeções e 18 mutações novas.
**Result**: 14/21 mortas. Das 7 sobreviventes:
- **E2b** (STAT-05), **E9** (STAT-03), **E10 e E11** (STAT-38) e **E16** (STAT-40) são cobertas por AC → FAIL ❌. As quatro de `hidden` são da mesma classe da R2, que a iteração 4 contou como falha.
- **E17** é uma lacuna de precisão da spec (não bloqueia).
- **E6** está fora da spec (só nota).

Nenhuma sobrevivente é da classe A6/A7 já aceita: o passe de design não toca CSS.

### Spec-Precision Gaps (iteração 5)

- **STAT-03, link operável (novo, E17).** A STAT-41 emendada exige a ordem do Tab só para o botão desabilitado. O link "Avançar para" pode ficar `inert` (visível, mas fora do Tab e da árvore de acessibilidade) sem violar a letra de nenhuma AC. Sugestão de emenda: "the link SHALL be reachable in the sequential Tab order and exposed to assistive technology (no `hidden`, `inert` or `aria-hidden` on it or an ancestor)". **Não bloqueia.**
- **STAT-06/STAT-34, `<title>` (herdado).** Igual às iterações anteriores, sem bloqueio.

### Fix Plans (iteração 5)

#### Fix 7: STAT-05 com próximo estágio só é conferida na página inteira para o terceiro sem bandeiras (E2b) — Major, só teste

- **Root cause**: `test_terceiro_nao_ve_o_link_de_avancar` (`test_views_detalhe.py:407-418`) tem `"Avançar" not in html`, mas usa só a fixture `terceiro`. Os testes com `nao_autor_usuario` olham a página por `"Avançar para"` (`test_views_status.py:336`) ou a seção por `"Avançar"` (`test_views_detalhe.py:429`). Um controle "Avançar status" fora da seção, condicionado a `is_staff`, passa. É a lacuna da R1, no outro ramo do `{% if %}`.
- **Fix task**: em `test_quem_nao_pode_alterar_le_quem_pode_avancar` (`:421-431`), carregar a página inteira e afirmar `"Avançar" not in html`, como a T18 fez no estágio final. Alternativa: trocar `"Avançar para"` por `"Avançar"` em `test_views_status.py:336`.
- **Verify**: E2b morre na worktree; R1, E2, D1 e D14 continuam mortas.
- **Done when**: E2b está morta, o gate de build está verde e nenhum código de produção mudou.

#### Fix 8: controles e textos "exibidos" não recusam `hidden` num ancestral ou no próprio elemento (E9, E10, E11, E16) — Major, só teste

- **Root cause**: as asserções positivas da STAT-03, STAT-38 e STAT-40 leem rótulo, destino e atributos ARIA do elemento por regex ou parser, mas nada recusa um `hidden` (ou `inert`, ou `aria-hidden`) no elemento ou num ancestral dentro da seção. A T19 fechou só o caso do atributo no próprio `<a>`.
- **Fix task**: em `test_views_acessibilidade_alteracao.py` (ou `test_views_detalhe.py`), criar um helper que, sobre a seção do ciclo analisada por `_analisar`, afirme que **nenhum** elemento tem `hidden`, `inert` ou `aria-hidden="true"`. Aplicá-lo nos quatro estados da tabela "Controle de transição" (pode/não pode alterar × com próximo/estágio final). A recusa de `style=` inline já vem do DS (E15 morta).
- **Verify**: E9, E10, E11, E16 e E17 morrem na worktree; R2 e E1 continuam mortas.
- **Done when**: as cinco estão mortas, o gate de build está verde e nenhum código de produção mudou.

### Requirement Traceability Update (iteração 5)

Não aplicada (FAIL). A `spec.md` e o `tasks.md` não foram alterados. Proposta para quando os Fix 7 e 8 passarem no Verifier:

| Requirement | Status atual | Proposto |
| ----------- | ------------ | -------- |
| STAT-04, STAT-39, STAT-41 | Implementing / Implementing (emendada) | ✅ Verified (evidência acima) |
| STAT-03 | Verified | ❌ Needs Fix (Fix 8, E9) |
| STAT-05 | Implementing (emendada) | ❌ Needs Fix (Fix 7, E2b) |
| STAT-38 | Implementing | ❌ Needs Fix (Fix 8, E10/E11) |
| STAT-40 | Implementing | ❌ Needs Fix (Fix 8, E16) |
| STAT-37 | Implementing (risco residual aceito) | sem mudança |

### Summary (iteração 5)

**Overall**: ❌ Not Ready.
- **O que foi corrigido.** As três correções da iteração 4 funcionam: R1, R2 e D12 morrem, e T18–T20 não enfraquecem nada. O template continua cumprindo a spec nos quatro estados.
- **Por que FAIL.** Cinco mutantes novos, cobertos por AC, sobrevivem, todos por lacuna de teste:
  - **E2b** (STAT-05): botão "Avançar status" fora da seção para `USUARIO` com `is_staff`, com próximo estágio.
  - **E9** (STAT-03): `hidden` no `<p>` que envolve o link.
  - **E10 e E11** (STAT-38): `hidden` no `<p>` do botão ou no próprio botão.
  - **E16** (STAT-40): `hidden` na ajuda.

**Spec-anchored check**: 36/41 ACs com o valor da spec afirmado e discriminante. STAT-03, STAT-05, STAT-38 e STAT-40 têm lacuna de discriminação, e a STAT-37 fica fora da conta pelo risco aceito. 2 lacunas de precisão que não bloqueiam (link operável da STAT-03/E17 e o título).
**Sensor**: 14/21 mortas. Sobreviventes cobertas por AC: E2b, E9, E10, E11 e E16. Lacuna de precisão: E17. Fora da spec: E6.
**Gate**: 704 passed, 0 failed; ruff, format e makemigrations limpos.
**validate_state.py**: `python3 .claude/skills/tlc-spec-driven/scripts/validate_state.py ciclo-de-vida-status` → exit 1, "validation.md verdict is FAIL - route the ranked gaps to fix tasks, then re-verify (feature is not done)". É o resultado esperado para um FAIL.

**Lessons** (estado das candidatas da iteração 4):

| Lição | Situação |
| ----- | -------- |
| **L-024** | Aplicada para o caso que a originou: R1 morre. **Recorre no ramo vizinho** (E2b). A asserção de página inteira voltou no estágio final, mas, com próximo estágio, nunca existiu para staff/superusuário |
| **L-025** | Aplicada: R2 e E1 morrem. A mesma família reaparece um nível acima (E9, E10, E11, E16): o helper agora recusa atributos no `<a>`, mas nenhum teste olha `hidden` num ancestral, no botão ou no texto |
| **L-026** | Atendida: STAT-41 emendada, e D12 e E7 morrem. O caso vizinho (E17, link `inert`) fica como lacuna de precisão |

Lições novas, `candidate`:

| Lição | Sinal | Regra |
| ----- | ----- | ----- |
| **L-027** | E2b | Asserção negativa de página roda para toda variante de conta do papel negado |
| **L-028** | E9/E10/E11/E16 | Asserção de "exibido" recusa `hidden`, `inert` e `aria-hidden` no elemento e nos ancestrais |
| **L-029** | E17, lacuna de precisão | AC de link de ação também exige ordem do Tab e exposição à tecnologia assistiva |

**L-003** (confirmada) não foi penalizada. A letra dela, a recusa da tela e da rota a contas com `is_staff`/`is_superuser`, é cumprida (`test_views_status.py:310-327`). A falha da E2b é de asserção negativa na página, não de acesso.

**Next steps**: Fix 7 e Fix 8 (só testes) e nova verificação, se o usuário aceitar a rodada. A outra opção é aceitar E2b, E9, E10, E11 e E16 como risco residual: o template atual não tem nenhum desses defeitos.

---

## Iteração 6 — passe de design (2026-10-18)

**Date**: 2026-10-18
**HEAD**: `e71c6b5`. Correções da iteração 5 `90a3a28..e71c6b5`: `db5f389` (T21, E2b) e `e71c6b5` (T22, E9/E10/E11/E16/E17). Passe de design inteiro: `e7d8709..e71c6b5`. Última rodada autorizada pelo usuário para o passe.
**Produção tocada desde a iteração 5**: nenhuma. `git diff 90a3a28..HEAD -- . ':!inovacoes/tests' ':!.specs'` e `git diff b246c63..HEAD -- . ':!inovacoes/tests' ':!.specs'` saem vazios. Só mudaram `inovacoes/tests/test_views_detalhe.py` (+20/−2) e o `tasks.md`.
**Verifier**: novo sub-agente independente. Não escreveu código, testes nem correções. Re-derivou a cobertura a partir da `spec.md`, do `design.md` ("Controle de transição") e do design-spec §6, §8 e §10 F5.
**Risco já aceito**: a lacuna A6/A7 da STAT-37 continua aceita ([Decisão do usuário](#decisão-do-usuário-2026-10-18)). Nenhuma sobrevivente desta iteração pertence a essa classe, porque nenhuma mutação toca CSS.

### Task Completion

| Task | Status | Notes |
| ---- | ------ | ----- |
| T1–T20 | ✅ Done | Inalteradas desde a iteração 5 |
| T21 | ✅ Done | `db5f389`. E2b morta (2 falhas: `[staff-EM_TESTE]`, `[staff-VALIDADA]`) |
| T22 | ✅ Done | `e71c6b5`. E9, E10, E11, E16 e E17 mortas. O teste cobre só as tags **dentro** da seção, por regex sensível a maiúsculas, sobre o HTML cru (ver sensor) |

### Gate Check (iteração 6)

- **Gate command**: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q`, rodado na árvore real com HEAD `e71c6b5`.
- **Result**: exit 0 em cada etapa.
  - `ruff check`: All checks passed.
  - `ruff format --check`: 110 files already formatted.
  - `makemigrations --check`: No changes detected.
  - `pytest -q`: **710 passed**, 0 failed, 0 skipped (15,9 s).
- **Test count**: 704 (iteração 5) → 710 (+6 da T22). Nenhum teste removido.

### T21–T22: houve enfraquecimento?

**Não.** Cada diff foi comparado com o commit pai.

1. **T21** (`db5f389`, `test_quem_nao_pode_alterar_le_quem_pode_avancar`, `test_views_detalhe.py:421-434`):
   - `_ciclo(...)` foi trocado pela mesma sequência inline (`force_login`, `get`, `_secao`), para guardar o `html`.
   - `"Avançar" not in secao` virou `"Avançar" not in html` (`:432`). Como a seção é um trecho da página, a asserção nova implica a antiga.
   - `_explicacao == QUEM_PODE_AVANCAR` (`:430`), `_botoes(secao) == []` (`:433`) e `AJUDA_DO_AVANCO not in secao` (`:434`) ficam.
   - Roda para terceiro, staff e superusuário × "Em teste"/"Validada".
2. **T22** (`e71c6b5`): teste novo, `test_nada_na_secao_do_ciclo_fica_escondido` (`:437-449`). Puramente aditivo, sem nenhuma asserção ou helper existente alterado.
   - `ESCONDE` (`:438`): `\s(?:hidden|inert)(?=[\s=/>])|\saria-hidden="true"`.
   - É aplicado a toda tag `<[a-z][^>]*>` do trecho `_secao` (`:447-449`), para autor/terceiro × 3 status.

### Spec-Anchored Acceptance Criteria (re-derivado no HEAD `e71c6b5`)

Caminhos relativos a `inovacoes/tests/`. O template está em `inovacoes/templates/inovacoes/inovacao_detail.html:43-68`. Renderizado nos quatro estados, ele confere caractere por caractere com a tabela "Controle de transição" (`design.md:157-162`) e com os textos da spec.

#### ACs re-derivadas por inteiro

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| STAT-03 | quem pode alterar, em "Em teste"/"Validada": **exibe** na seção do ciclo o link "Avançar para “<próximo>”" → `/inovacoes/<id>/status/` | `test_views_detalhe.py:344` `_links(secao, f"Avançar para “{proximo}”") == [f"/inovacoes/{pk}/status/"]` (regex restrito de `:197`); `:449` nenhuma tag da seção com `hidden`/`inert`/`aria-hidden="true"`; `test_views_acessibilidade_alteracao.py:255` `links == [f"/inovacoes/{pk}/status/"]` | ❌ **GAP**: R2, E1, E9, E17, F10, F11 e F13 morrem. Mas **F1** (`<div hidden>` em volta da `<section>`), **F5** (link dentro de `<template>`), **F14** (`<p class="acoes" HIDDEN>`) e **F16** (link dentro de `<details>` fechado) sobrevivem |
| STAT-04 (emendada) | estágio final: **exibe** "Último estágio do ciclo." na seção; nenhum link para `/status/`, para qualquer conta | `test_views_detalhe.py:371` `_explicacao(secao) == "Último estágio do ciclo."`; `:372` `"<a " not in secao`; `:373` caminho fora da página; `:374` `"Avançar para" not in html`; `:404` para `nao_autor_usuario` | ❌ **GAP**: a parte negativa é discriminante (D9 e E13 mortas). Mas **F3** (o `<p>` do texto dentro de `<!-- -->`) e **F1** sobrevivem: `_explicacao` lê o texto por regex no HTML cru, inclusive dentro de comentário |
| STAT-05 (emendada) | quem não pode alterar não vê **nenhum** link ou botão "Avançar" na página de detalhe | Página inteira: `test_views_detalhe.py:379` (terceiro, estágio final), `:403` (`nao_autor_usuario`, estágio final), `:415` (terceiro, com próximo), `:432` (`nao_autor_usuario`, com próximo; T21). Seção: `:402`, `:416`, `:433` `_botoes(secao) == []` | ❌ **GAP**: R1, E2, E2b e D1 morrem. Mas **F17** sobrevive: botão `Avan&ccedil;ar status` fora da seção, para `USUARIO` com `is_staff`, que o navegador mostra como "Avançar status". `"Avançar" not in html` compara a string crua, sem decodificar entidades |
| STAT-38 | pode alterar + estágio final: **exibe** na seção o botão "Avançar status" com `aria-disabled="true"` | `test_views_detalhe.py:390` `[texto.strip() …] == ["Avançar status"]`; `:391` `'aria-disabled="true"' in botoes[0][0]`; `:449`; `test_views_acessibilidade_alteracao.py:322-325` | ❌ **GAP**: E4, E8, E10, E11, E12, F9 e F12 morrem. Mas **F1** e **F18** (botão dentro de `<details>` fechado) sobrevivem. F15 (`aria-hidden=true` sem aspas) é lacuna de precisão |
| STAT-39 | não pode alterar + "Em teste"/"Validada": **exibe** o texto exato na seção | `test_views_detalhe.py:430` `_explicacao(secao) == QUEM_PODE_AVANCAR` (3 contas × 2 status); ausente no estágio final (`:376`) e para quem pode alterar (`:462`) | ❌ **GAP**: D5, E3 e F7 morrem. Mas **F4** (texto dentro de `<!-- -->`) e **F1** sobrevivem |
| STAT-40 | pode alterar + "Em teste"/"Validada": **exibe** na seção a ajuda exata | `test_views_detalhe.py:460` `_explicacao(secao) == AJUDA_DO_AVANCO` (2 contas × 2 status); `test_views_acessibilidade_alteracao.py:339-341`; ausente no estágio final (`:375`) e para quem não pode alterar (`:434`) | ❌ **GAP**: D10, E5, E16 e F6 morrem. Mas **F2** (ajuda dentro de `<!-- -->`) e **F1** sobrevivem. F19 (`aria-hidden='true'`) é lacuna de precisão |
| STAT-41 (emendada) | botão na ordem do Tab (sem `disabled`; `tabindex` ausente ou `0`); `aria-describedby` do botão → "Último estágio do ciclo."; `aria-describedby` do link → ajuda da STAT-40; botão `type="button"` fora de `form` | `test_views_acessibilidade_alteracao.py:322` um botão; `:324` `type == "button"`; `:325` `aria-disabled == "true"`; `:326` sem `disabled`; `:328` `tabindex` ausente ou `"0"`; `:329` fora de `form`; `:330` `_texto_do_id(...) == "Último estágio do ciclo."`; `:337-341` o link resolve para a ajuda exata | ❌ **GAP**: D2, D2b, D3, D4, D7, D8, D12, E7 e F8 morrem. Mas **F3** e **F2** sobrevivem: `_texto_do_id` (`:301-304`) acha o `id` por regex dentro de um comentário HTML, e no DOM o `aria-describedby` aponta para um elemento que não existe |
| STAT-34 | só nativos, sem `tabindex` positivo, foco visível em cada link e botão; um `h1` e `<title>` "Avançar status" | `test_views_acessibilidade_alteracao.py:207-218` `_afirma_so_nativos`, aplicado em `:224`, `:250`, `:320`; `:233-236` confirmação: um `submit` no `form` e um link; `:248-257` seções rotuladas pelo `h2`, uma `ol`; `:261-267` `:focus-visible` com `outline` sólido nas 4 páginas do ciclo; `:278-280` `h1` exato e `<title>` por prefixo; `test_views_detalhe.py:449` recusa `inert` | ✅ PASS ⚠️ (E7, E14 e E17 mortas; o título por prefixo é lacuna herdada, sem bloqueio) |

#### Amostragem das demais ACs no HEAD (11, relidas linha a linha)

`test_views_status.py`, `test_ciclo_de_vida.py` e `test_views_erro_500.py` estão fora do diff `90a3a28..HEAD`.

| AC | `file:line` + assertion | Result |
| -- | ----------------------- | ------ |
| STAT-01 | `test_views_detalhe.py:313` `findall(h2) == ["Ciclo de vida"]`; `:315` itens sem o sufixo `== ETAPAS` | ✅ ordem e rótulos. ❌ "display" não discrimina F1 (seção inteira com ancestral `hidden`) |
| STAT-02 | `test_views_detalhe.py:326` `html.count("(status atual)") == 1`; `:329` lista exata, 3 status | ✅ |
| STAT-06 | `test_views_status.py:46-67` 200, template, `h1 == ["Avançar status"]`, texto exato, `method="post"`, um `submit` com o rótulo exato, `status_visto` oculto com o status gravado (`:65`), `cancelar == [f"/inovacoes/{pk}/"]` (`:67`) | ✅ ⚠️ (título) |
| STAT-07 | `test_views_status.py:175-176` `assertRedirects(…, f"/inovacoes/{pk}/")`, `== VALIDADA` | ✅ |
| STAT-10 | `test_views_status.py:98-105` GET 200, texto, sem `<form>`/`<button>`, `voltar == [detalhe]`; `:232-234` POST: `== DISPONIVEL`, `count() == 0`, `[("warning", ULTIMO_ESTAGIO)]` | ✅ |
| STAT-12 | `test_views_status.py:245-247` `== EM_TESTE`, `count() == 0`, `[("warning", _conflito("Em teste"))]` | ✅ |
| STAT-14 | `test_views_status.py:178-183` `(inovacao_id, anterior, novo) == (pk, EM_TESTE, VALIDADA)`, `responsavel == autor` | ✅ |
| STAT-18 | `test_views_status.py:221-223` `status == VALIDADA`, `autor == autor`, `responsavel == administrador` | ✅ |
| STAT-19/20 | `test_views_status.py:323-326` (terceiro, staff, superusuário; GET e POST) 403, `acesso_negado.html`, `NEGADO`, status inalterado | ✅ |
| STAT-31 | `test_ciclo_de_vida.py:72` `pytest.raises(IntegrityError, match="mudanca_de_status_transicao_valida")` | ✅ |
| STAT-36 | `test_views_erro_500.py:179-183` 403 que não é o acesso negado, `== EM_TESTE`, `count() == 0` | ✅ |

As demais ACs (STAT-08, 09, 11, 13, 15–17, 21–30, 32, 33, 35) foram herdadas das iterações 1 a 5, sem mudança nos testes nem na produção que as exercita. A STAT-37 segue com o risco residual A6/A7 aceito.

**Status**: ❌ 32/41 ACs com o valor da spec afirmado e discriminante. STAT-01, 03, 04, 05, 38, 39, 40 e 41 têm asserção, mas cada uma deixa sobreviver ao menos um mutante que a AC cobre. A STAT-37 conta à parte, pelo risco aceito. Lacunas de precisão que não bloqueiam: `aria-hidden` em conteúdo visível (F15, F19) e o título (herdada).

### Discrimination Sensor (iteração 6)

**Preparação.**
- Worktree: `git worktree add --detach scratchpad/wt6 HEAD`, com o `.env` copiado.
- Banco: PostgreSQL de teste na porta 5433.
- Código em uso: `inovacoes.__file__` resolve para a worktree.
- Linha de base: **710 passed**. `git status --porcelain` da árvore real gravado antes, vazio.

**Execução.** Um script de sensor no scratchpad, fora da worktree, aplica cada mutação por substituição exata e única (`count == 1`) em `inovacoes/templates/inovacoes/inovacao_detail.html`. Para cada uma, roda a suíte inteira (`.venv/bin/pytest -q -p no:cacheprovider -rf`) e restaura o arquivo original. No fim, confere que o arquivo é idêntico ao original.

**Sondas.** Para provar que cada sobrevivente é efetiva, usei um arquivo de sonda descartável, não rastreado, só na worktree. A sonda lê o DOM com `HTMLParser`, que ignora comentários e decodifica entidades. Ela descarta `template`, `details` fechado e todo ancestral com `hidden`/`inert`/`aria-hidden=true` em qualquer caixa, e afirma os textos e controles de cada estado. Passa no HEAD (15 passed) e falha com cada uma das 11 sobreviventes. Depois apaguei o arquivo.

**Limpeza.** No fim, `git worktree remove --force` e `git worktree prune`. `git worktree list` só mostra a árvore principal. O `git status --porcelain` da árvore real está vazio e é idêntico à linha de base. O HEAD continua `e71c6b5`.

**DS-01 conferido antes de contar sobreviventes.** `test_views_sistema_design.py:398` e `:407` proíbem `style=` e `<style` nas telas. A `kira.css` não tem classe de ocultação (só `.pular`, o link de pular, deslocado até receber foco). Nenhuma das sobreviventes usa CSS: todas são HTML puro, que o DS não proíbe.

#### Re-injeções da iteração 5

| # | File:line | Mutação | Killed? (testes que falharam) | AC |
| - | --------- | ------- | ----------------------------- | -- |
| E2b | `inovacao_detail.html:68` (depois da seção) | `{% if not pode_alterar and inovacao.proximo_status and user.is_staff %}<p><button type="button" aria-disabled="true">Avançar status</button></p>{% endif %}` | ✅ 2: `test_quem_nao_pode_alterar_le_quem_pode_avancar[staff-EM_TESTE, staff-VALIDADA]` | STAT-05 |
| E9 | `:63` | `<p class="acoes" hidden>` em volta do link | ✅ 2: `test_nada_na_secao_do_ciclo_fica_escondido[EM_TESTE-autor, VALIDADA-autor]` | STAT-03 |
| E10 | `:59` | `<p class="acoes" hidden>` em volta do botão | ✅ 1: `test_nada_na_secao…[DISPONIVEL_PARA_REPLICACAO-autor]` | STAT-38 |
| E11 | `:59` | `<button hidden type="button" …>` | ✅ 1: `test_nada_na_secao…[DISPONIVEL_PARA_REPLICACAO-autor]` | STAT-38 |
| E16 | `:64` | `hidden` no `<p id="ciclo-explicacao" class="helptext">` | ✅ 2: `test_nada_na_secao…[EM_TESTE-autor, VALIDADA-autor]` | STAT-40 |
| E17 | `:63` | `<p class="acoes" inert>` em volta do link | ✅ 2: `test_nada_na_secao…[EM_TESTE-autor, VALIDADA-autor]` | STAT-03, STAT-34 |

#### Mutações novas (não tentadas nas iterações 4 e 5)

| # | File:line | Mutação | Killed? (testes que falharam) | AC |
| - | --------- | ------- | ----------------------------- | -- |
| **F1** | `:43`, `:68` | `<div hidden>` em volta da `<section aria-labelledby="ciclo-titulo">` inteira (ancestral **fora** da seção) | ❌ **Survived** (710 passed). Sonda: 6 falhas | **STAT-01, 03, 04, 38, 39, 40** ("SHALL display") |
| **F2** | `:64` | ajuda da STAT-40 dentro de `<!-- … -->` | ❌ **Survived** (710 passed). Sonda: 2 falhas | **STAT-40**, **STAT-41** (o `aria-describedby` do link aponta para um `id` que não existe no DOM) |
| **F3** | `:61` | "Último estágio do ciclo." dentro de `<!-- … -->` | ❌ **Survived** (710 passed). Sonda: 2 falhas | **STAT-04**, **STAT-41** (idem, para o botão) |
| **F4** | `:66` | texto da STAT-39 dentro de `<!-- … -->` | ❌ **Survived** (710 passed). Sonda: 2 falhas | **STAT-39** |
| **F5** | `:63` | `<template>` em volta do `<p class="acoes">` do link (o navegador não renderiza) | ❌ **Survived** (710 passed). Sonda: 2 falhas | **STAT-03** |
| F6 | `:64` → depois de `:68` | ajuda da STAT-40 movida para fora da seção | ✅ 6: `test_quem_pode_alterar_le_a_ajuda…[4]`, `test_link_de_avancar_e_descrito_pela_ajuda[2]` | STAT-40 |
| F7 | `:66` → depois de `:68` | texto da STAT-39 movido para fora da seção | ✅ 6: `test_quem_nao_pode_alterar_le_quem_pode_avancar[3 contas × 2]` | STAT-39 |
| F8 | `:63`, `:46` | `aria-describedby` tirado do link e posto na `<ol class="ciclo">` (ajuda ligada ao controle errado) | ✅ 8: `test_link_de_avancar…[2]`, STAT-01/02 (4), `test_terceiro_nao_ve_o_link…[2]` | STAT-41 |
| F9 | `:59` | segundo `<button aria-disabled="true">Avançar status</button>` na seção | ✅ 3: `test_ultimo_estagio_mostra_avancar_desabilitado…[2]`, `test_botao_desabilitado_continua_focavel…` | STAT-38, STAT-41 |
| F10 | `:63` | `aria-disabled="true"` no link "Avançar para" | ✅ 4: `test_quem_pode_alterar_ve_o_link_de_avancar[…]` | STAT-03 |
| F11 | `:63` | link com o mesmo rótulo para `inovacoes:editar` | ✅ 5: `test_quem_pode_alterar_ve_o_link…[4]`, `test_secoes_do_detalhe_sao_nativas…[ciclo]` | STAT-03 |
| F12 | `:59` | rótulo "Avançar Status" | ✅ 2: `test_ultimo_estagio_mostra_avancar_desabilitado…[2]` | STAT-38 |
| F13 | `:63` | aspas retas no rótulo do link (`"Validada"`) | ✅ 4: `test_quem_pode_alterar_ve_o_link…[…]` | STAT-03 |
| **F14** | `:63` | `<p class="acoes" HIDDEN>` (atributo HTML não diferencia caixa) | ❌ **Survived** (710 passed). `ESCONDE` (`test_views_detalhe.py:438`) e `<[a-z][^>]*>` (`:447`) diferenciam caixa. Sonda: 2 falhas | **STAT-03** (mesmo comportamento da E9) |
| F15 | `:59` | `<p class="acoes" aria-hidden=true>` sem aspas, em volta do botão | ⚪ Survived (710 passed). `ESCONDE` exige `="true"`. Sonda: 1 falha. O botão continua **visível** e focável, então a letra da STAT-38 é cumprida | ⚠️ SPG |
| **F16** | `:63` | link dentro de `<details><summary>Ações</summary>…</details>` fechado | ❌ **Survived** (710 passed). Sonda: 2 falhas | **STAT-03** (o link só aparece depois de expandir) |
| **F17** | `:68` (depois da seção) | `{% if not pode_alterar and user.is_staff %}<p><button type="button" aria-disabled="true">Avan&ccedil;ar status</button></p>{% endif %}` | ❌ **Survived** (710 passed). `"Avançar" not in html` não decodifica entidades. Sonda com `html.unescape`: 3 falhas (staff × 3 status) | **STAT-05** |
| **F18** | `:59` | botão desabilitado dentro de `<details>` fechado | ❌ **Survived** (710 passed). Sonda: 1 falha | **STAT-38** |
| F19 | `:64` | `aria-hidden='true'` (aspas simples) na ajuda | ⚪ Survived (710 passed). Sonda: 2 falhas. A ajuda continua **visível**; o `aria-describedby` ainda resolve para ela | ⚠️ SPG |

**Sensor depth**: expandido (autorização na tela e acessibilidade): 6 re-injeções e 19 mutações novas.
**Result**: 14/25 mortas. Das 11 sobreviventes:
- **F1, F2, F3, F4, F5, F14, F16, F17 e F18** são cobertas por AC (STAT-01, 03, 04, 05, 38, 39, 40, 41) → FAIL ❌.
- **F15 e F19** são lacunas de precisão: conteúdo visível, mas escondido da tecnologia assistiva.

Nenhuma sobrevivente é da classe A6/A7 já aceita.

**Causa comum.** Toda asserção de "exibido" (`_links`, `_explicacao`, `_botoes`, `_texto_do_id`, `ESCONDE`) e a negativa da STAT-05 (`"Avançar" not in html`) operam por regex sobre o HTML cru. Por isso deixam passar quatro coisas:
- **Ancestral fora do trecho.** O `_secao` começa na própria `<section>`, e nada olha acima dela (F1).
- **Marcação que o navegador não renderiza.** Comentário, `<template>` e `<details>` fechado (F2, F3, F4, F5, F16, F18).
- **Atributo em maiúsculas.** HTML não diferencia caixa, e o regex diferencia (F14).
- **Entidade HTML.** O regex compara a string sem decodificar (F17).

### Spec-Precision Gaps (iteração 6)

- **STAT-38/STAT-40, exibido mas escondido da tecnologia assistiva (novo, F15, F19).** "SHALL display" é cumprido visualmente com `aria-hidden="true"`. A L-029 já pediu essa precisão para o link (STAT-03). Sugestão de emenda: "displayed and exposed to assistive technology (no `hidden`, `inert` or `aria-hidden` on it or an ancestor)" para STAT-03, 38, 39 e 40. **Não bloqueia.**
- **STAT-06/STAT-34, `<title>` (herdado).** Igual às iterações anteriores, sem bloqueio.

### Fix Plans (iteração 6)

#### Fix 9: "exibido" afirmado sobre o DOM exposto, não sobre o HTML cru (F1–F5, F14, F16, F18) — Major, só teste

- **Root cause**: veja "Causa comum" acima. A T22 aplicou a L-028 só às tags dentro da seção, com regex sensível a maiúsculas e às aspas.
- **Fix task**: um helper baseado em `HTMLParser` sobre a **página inteira**, desde a raiz. Ele mantém a pilha de ancestrais e devolve os elementos e o texto expostos:
  - comentários são ignorados naturalmente;
  - descarta o conteúdo de `<template>` e de `<details>` sem `open` (exceto o `<summary>`);
  - descarta todo elemento com `hidden`, `inert` ou `aria-hidden` igual a `true` (nome e valor sem diferenciar caixa, qualquer aspa) nele ou em qualquer ancestral.

  Use-o nas asserções positivas da STAT-01, STAT-03, STAT-04, STAT-38, STAT-39 e STAT-40. Use-o também para resolver o `aria-describedby` da STAT-41: o `id` tem de existir no DOM, não num comentário. A sonda descrita no sensor serve de referência.
- **Verify**: na worktree, F1, F2, F3, F4, F5, F14, F16 e F18 morrem. E9, E10, E11, E16, E17, R2 e E1 continuam mortas.
- **Done when**: as oito estão mortas, o gate de build está verde e nenhum código de produção mudou.

#### Fix 10: negativa da STAT-05 sem decodificar entidades (F17) — Minor, só teste

- **Root cause**: `test_views_detalhe.py:379`, `:403`, `:415` e `:432` usam `"Avançar" not in html` sobre a string crua.
- **Fix task**: afirmar sobre `html.unescape(html)`, ou sobre o texto do parser do Fix 9, que decodifica entidades.
- **Verify**: F17 morre, e R1, E2 e E2b continuam mortas.
- **Done when**: F17 está morta e o gate de build está verde.

### Requirement Traceability Update (iteração 6)

Não aplicada (FAIL). A `spec.md` e o `tasks.md` não foram alterados. Proposta para quando os Fix 9 e 10 passarem no Verifier:

| Requirement | Status atual | Proposto |
| ----------- | ------------ | -------- |
| STAT-01, STAT-03 | Verified | ❌ Needs Fix (Fix 9; lacuna de teste, não de produção) |
| STAT-04, STAT-05 | Implementing (emendada) | ❌ Needs Fix (Fix 9; Fix 10) |
| STAT-38, STAT-39, STAT-40 | Implementing | ❌ Needs Fix (Fix 9) |
| STAT-41 | Implementing (emendada) | ❌ Needs Fix (Fix 9: `aria-describedby` resolvido no DOM) |
| STAT-34 | Verified | sem mudança |
| STAT-37 | Implementing (risco residual aceito) | sem mudança |

### Summary (iteração 6)

**Overall**: ❌ Not Ready.
- **O que foi corrigido.** As correções da iteração 5 funcionam: E2b, E9, E10, E11, E16 e E17 morrem, e T21–T22 não enfraquecem nada. O template de produção continua cumprindo a spec e o design nos quatro estados, sem CSS novo.
- **Por que FAIL.** Nove mutantes novos, cobertos por AC, sobrevivem, todos por lacuna de teste e com uma causa comum: as asserções de "exibido" leem o HTML cru por regex, não o DOM que o navegador expõe. O caso mais direto é o **F1**: um `<div hidden>` em volta da seção inteira some com tudo o que as STAT-01, 03, 04, 38, 39 e 40 mandam exibir, e a suíte passa.

**Spec-anchored check**: 32/41 ACs com o valor da spec afirmado e discriminante. STAT-01, 03, 04, 05, 38, 39, 40 e 41 têm lacuna de discriminação, e a STAT-37 fica fora da conta pelo risco aceito. 2 lacunas de precisão que não bloqueiam: `aria-hidden` em conteúdo visível (F15/F19) e o título.
**Sensor**: 14/25 mortas. Sobreviventes cobertas por AC: F1, F2, F3, F4, F5, F14, F16, F17 e F18. Lacunas de precisão: F15 e F19.
**Gate**: 710 passed, 0 failed; ruff, format e makemigrations limpos.
**validate_state.py**: `python3 .claude/skills/tlc-spec-driven/scripts/validate_state.py ciclo-de-vida-status` → exit 1, "validation.md verdict is FAIL - route the ranked gaps to fix tasks, then re-verify (feature is not done)". É o resultado esperado para um FAIL.

**Lessons** (estado das candidatas da iteração 5):

| Lição | Situação |
| ----- | -------- |
| **L-027** | Aplicada: a T21 roda a negativa de página para as três contas, e E2b morre. **Recorre** por outra via (F17): a negativa compara a string crua, e uma entidade HTML a contorna |
| **L-028** | **Recorre.** A T22 recusa `hidden`/`inert`/`aria-hidden` só nas tags **dentro** da seção, não nos ancestrais acima dela (F1), e por regex sensível a maiúsculas e às aspas (F14, F15, F19). Comentário, `<template>` e `<details>` fechado também escondem sem atributo (F2–F5, F16, F18) |
| **L-029** | Atendida no teste (E17 morre pela T22), mas a spec não foi emendada. A mesma lacuna aparece no botão e na ajuda (F15, F19) |

Lições novas, `candidate`, registradas pelo `lessons.py`. Nenhuma lição confirmada foi carregada para este passe; a L-003 continua cumprida, sem penalidade.

| Lição | Sinal | Regra |
| ----- | ----- | ----- |
| **L-030** | F1–F5, F14, F16, F18 | Afirmar "exibido" sobre o DOM analisado da página inteira, não por regex no HTML cru |
| **L-031** | F17 | Decodificar entidades HTML antes de uma asserção negativa de texto na página |
| **L-032** | F15/F19, lacuna de precisão | "Exibido" numa AC precisa dizer se também vale para a tecnologia assistiva |

**Next steps**: esta era a última rodada autorizada para o passe de design, então o próximo passo é escalar ao usuário. Opções:
1. Autorizar mais uma rodada: Fix 9 e Fix 10, só de teste, e nova verificação.
2. Aceitar F1–F5, F14, F16, F17 e F18 como risco residual, como foi feito com a STAT-37. O template de produção não tem nenhum desses defeitos, e a auditoria final de acessibilidade do RNF09 confere a página renderizada.

---

## Decisão do usuário — passe de design (2026-10-18)

Registrada pelo orquestrador depois da escalada (rodadas autorizadas para o passe esgotadas). Não é
uma iteração do Verifier.

- **Decisão**: aceitar o risco residual de teste do passe de design e fechar a F5. Sem iteração 7.
- **Base**: o template de produção não muda desde a T16 (`9298190`) e cumpre STAT-01 a STAT-41 nos
  quatro estados do controle de transição; o Verifier da iteração 6 confirmou com uma sonda de DOM
  que o HEAD passa e cada sobrevivente seria um defeito real. Todos os mutantes das iterações 4 e 5
  (R1, R2, D12, E2b, E9, E10, E11, E16, E17) estão mortos.
- **Risco residual aceito**: as checagens de "está exibido" e a negativa de página inteira da
  STAT-05 usam expressão regular sobre o HTML cru. Não pegam: ancestral escondido fora da seção
  (F1), texto ou controle dentro de comentário (F2, F3, F4), `<template>` (F5) ou `<details>` fechado
  (F16, F18), `HIDDEN` em maiúsculas (F14) e entidade HTML em "Avançar" (F17). ACs afetadas:
  STAT-01, STAT-03, STAT-04, STAT-05, STAT-38, STAT-39, STAT-40, STAT-41, que ficam
  `Implementing (risco residual aceito)` na rastreabilidade, ao lado da STAT-37.
- **Correção conhecida, não feita**: um helper que analise a página inteira como DOM (ignorando
  comentários, `<template>` e `<details>` fechado; herdando `hidden`/`inert`/`aria-hidden` de
  qualquer ancestral, sem depender de caixa ou aspas; com entidades decodificadas) usado por todas as
  checagens de exibição do ciclo. Registrada em `context.md` (Deferred Ideas).
- **Lacunas de precisão abertas**: `aria-hidden` sobre conteúdo visível (F15, F19, L-032) e o
  `<title>` da STAT-06/STAT-34.
- **`validate_state.py`**: sai com código 1, porque o veredito registrado é FAIL; é o esperado.
