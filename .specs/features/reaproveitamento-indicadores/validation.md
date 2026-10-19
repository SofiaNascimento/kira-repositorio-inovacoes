# Reaproveitamento e Indicadores (F6) Validation

**Date**: 2026-10-19
**Iteration**: 1
**Spec**: `.specs/features/reaproveitamento-indicadores/spec.md` (REAP-01 … REAP-49)
**Diff range**: `eb957d2..e755a45` em `main` (HEAD = `e755a45`), 21 commits, 19 de código e teste (T1 `69f655d` … T18 `985bfa4`) e 2 de pausa (`0bd904a`, `50d41ce`) mais o `e755a45`, só artefatos. 41 arquivos, +4805/−16; sem `.specs` e `docs`, 35 arquivos, +2789/−16. Produção: `inovacoes/models.py`, `forms.py`, `views.py`, `admin.py`, `urls.py`, `migrations/0008_reaproveitamento.py`, os templates `inovacao_detail.html` e `inovacao_reaproveitar.html`, a app `indicadores/` (`graficos.py`, `views.py`, `urls.py`, `painel.html`, `grafico.html`), `templates/base.html`, `templates/kira.css` e `config/`.
**Verifier**: sub-agente independente (autor ≠ verifier)

**Verdict**: FAIL ❌. Das 49 ACs, 49 têm evidência `file:line` com o valor da spec afirmado, e o código de produção cumpre a spec em tudo o que conferi. O FAIL vem do sensor. Das 46 mutações válidas, 39 morrem e 7 sobrevivem. Três dos sobreviventes são equivalentes, sem comportamento observável (M06, M09, M17). Os outros quatro são lacunas de teste: o elemento continua no HTML, mas com `hidden`, e a suíte passa. M41 esconde o link "Sinalizar reaproveitamento" (REAP-01). M43 esconde a seção "Por unidade" do painel, com a tabela e dois gráficos (REAP-33, REAP-34). M44 esconde os dois cards (REAP-30, REAP-31, REAP-37). M45 esconde o texto da REAP-15. É a mesma classe de lacuna da F5: as asserções de "exibido" leem o HTML cru por regex, não o DOM exposto (L-028, L-030). Os quatro viram fix tasks só de teste. Nenhum código de produção precisa mudar.

---

## Task Completion

| Task | Status | Notes |
| ---- | ------ | ----- |
| T1–T18 | ✅ Done | `tasks.md`, 18 de 18 com `Status: ✅ Complete`; a contagem cresce de 710 (antes da T1) para 865, o mesmo número do gate |

---

## Spec-Anchored Acceptance Criteria

Lidos no HEAD `e755a45`. `inv/` = `inovacoes/tests/`, `ind/` = `indicadores/tests/`.

### P1: Sinalizar que uma unidade reaproveitou a inovação

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| REAP-01 | link "Sinalizar reaproveitamento" → `/inovacoes/<id>/reaproveitar/` para todo autenticado, em "Disponível" | `inv/test_views_detalhe.py:598` - `_links(html, SINALIZAR) == [f"/inovacoes/{pk}/reaproveitar/"]`, para autor, administrador e `nao_autor_usuario` (terceiro, staff, superuser) | ✅ PASS ⚠️ (M35 morta; **M41 sobrevive**: link com `hidden`) |
| REAP-02 | em "Em teste"/"Validada", nenhum href para `/reaproveitar/` nem o texto, para ninguém | `inv/test_views_detalhe.py:610-611` - `"/reaproveitar/" not in html`, `SINALIZAR not in html`; 2 status × 5 contas | ✅ PASS (M35 morta) |
| REAP-03 | 200; `<title>` começa com "Sinalizar reaproveitamento"; texto exato; select obrigatório rotulado; botão; "Cancelar" → detalhe | `inv/test_views_reaproveitar.py:68` 200; `:72` `titulo.startswith(...)`; `:74-77` texto exato com título e origem; `:80` `required`; `:82-84` label exato; `:90-91` um botão submit com o rótulo; `:93` `cancelar == [f"/inovacoes/{pk}/"]` | ✅ PASS |
| REAP-04 | todas as unidades menos a origem e as que já sinalizaram, em ordem alfabética, sem pré-seleção | `inv/test_forms_reaproveitamento.py:46-52` lista literal, com "Almoxarifado" criada por último; `:60` nenhuma opção com valor vem `selected`; `:103` a exclusão é por inovação; e2e `inv/test_views_reaproveitar.py:103` | ✅ PASS ⚠️ (M12, M13, M14 mortas; ver gap G1) |
| REAP-05 | um registro com inovação, unidade, `registrado_por` = conta logada, `data` = hora do servidor; 302 → `/inovacoes/<id>/` | `inv/test_views_reaproveitar.py:217-222` - 302, `Location`, `Reaproveitamento.objects.get()` com os três ids; hora em `inv/test_reaproveitamento.py:159` - `antes <= registro.data <= timezone.now()` | ✅ PASS (M10 morta) |
| REAP-06 | mensagem exata, uma vez | `inv/test_views_reaproveitar.py:232` - `_mensagens(...) == [("success", _sucesso("Sede"))]`; `:234-235` some no GET seguinte | ✅ PASS (M11 morta) |
| REAP-07 | nenhum campo da inovação muda | `inv/test_reaproveitamento.py:280` - `depois == antes` sobre `values()` inteiro | ✅ PASS |
| REAP-08 | GET nunca grava | `inv/test_views_reaproveitar.py:109-111` - 3 GETs, `count() == 0` | ✅ PASS |

### P1: Só inovação disponível, só outra unidade, uma vez por unidade

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| REAP-09 | GET e POST fora de "Disponível": nada gravado, 302 ao detalhe, aviso exato uma vez | GET `inv/test_views_reaproveitar.py:122-126` - `redirect_chain`, `[("warning", _aviso_de_status(rotulo))]`, some no GET seguinte, `count() == 0`; POST `:247-249` | ✅ PASS (M08 morta) |
| REAP-10 | o modelo recusa com erro de validação e não grava | `inv/test_reaproveitamento.py:171-176` - `code == "status_indisponivel"`, mensagem exata, `count() == 0`; pelo valor gravado `:189-191` | ✅ PASS (M01, M02 mortas) |
| REAP-11 | origem no POST → 200, erro de campo exato, nada gravado | `inv/test_views_reaproveitar.py:254-256` - `_erros_do_select(...) == [ORIGEM]`, `count() == 0`; modelo `inv/test_reaproveitamento.py:212-214` | ✅ PASS (M03 morta) |
| REAP-12 | unidade repetida → 200, erro exato com o nome, nada gravado | `inv/test_views_reaproveitar.py:262-264` - `[_repetida("Sede")]`, `count() == 1`; modelo `inv/test_reaproveitamento.py:227-231` | ✅ PASS (M05 morta) |
| REAP-13 | vazio, inexistente ou não numérico → 200, "Selecione a unidade que reaproveitou a inovação." | `inv/test_views_reaproveitar.py:267-272` - `["", "999999", "abc"]`, `[SELECIONE]`, `count() == 0`; form `inv/test_forms_reaproveitamento.py:91` | ✅ PASS |
| REAP-14 | UniqueConstraint no banco; corrida → um registro e o resultado da REAP-12, sem 500 | banco `inv/test_reaproveitamento.py:49` - `constraint_name == UNICA`; trava `:259-260` - primeira leitura termina em `FOR UPDATE`; corrida simulada `inv/test_views_reaproveitar.py:287-288`; outra violação sobe `inv/test_reaproveitamento.py:248` | ✅ PASS (M04b, M05, M07, M36 mortas). Sem teste com duas conexões reais; a trava é provada pelo SQL emitido |
| REAP-15 | sem unidade elegível: 200, texto exato, "Voltar para a inovação" → detalhe, sem select nem botão | `inv/test_views_reaproveitar.py:130-136` (`_afirma_sem_elegiveis`), nos dois cenários `:139` e `:147` | ✅ PASS ⚠️ (M15 morta; **M45 sobrevive**: texto com `hidden`) |
| REAP-16 | id inexistente → 404 com "Inovação não encontrada." | GET `inv/test_views_reaproveitar.py:158-160` - 404, template, `h1`; apagada durante o envio `:303-305` | ✅ PASS (M38 morta) |

### P1: Ver no detalhe quem reaproveitou

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| REAP-17 | h2 "Reaproveitamentos" com "Nenhum…", "Reaproveitada por 1 unidade." ou "…por N unidades." | `inv/test_views_detalhe.py:634` - `[t for t in textos if t in secao] == [texto]` para 0, 1 e 2; h2 no helper `_reaproveitamentos` | ✅ PASS (M40, M42 mortas) |
| REAP-18 | um item por registro, do mais antigo ao mais recente por `data` (id desempata), "<unidade> — dd/mm/aaaa" | `inv/test_views_detalhe.py:649` - `itens == ["Filial Norte — 02/10/2026", "Sede — 05/10/2026"]`, com outra inovação semeada; desempate `inv/test_reaproveitamento.py:129` | ✅ PASS (M33, M46 mortas) |

### P1: Quem pode sinalizar e integridade do registro

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| REAP-19 | todo autenticado faz GET e POST, nunca 403 por autoria | `inv/test_views_reaproveitar.py:169-176` (GET) e `:334-342` (POST, `registrado_por_id` da conta), para terceiro, staff, superuser e administrador | ✅ PASS |
| REAP-20 | anônimo → login com `next`, nada gravado | `inv/test_views_reaproveitar.py:356-357` - `assertRedirects(..., f"/entrar/?next={caminho}")`, GET e POST | ✅ PASS (M27 morta) |
| REAP-21 | sem CSRF → 403, nada gravado | `inv/test_views_reaproveitar.py:366-367` | ✅ PASS |
| REAP-22 | `registrado_por`, `data` e `inovacao` do corpo ignorados | `inv/test_views_reaproveitar.py:324-326` | ✅ PASS (M10 morta) |
| REAP-23 | excluir a inovação apaga os reaproveitamentos dela | `inv/test_reaproveitamento.py:83` - `== [da_outra]`; pela rota `inv/test_views_reaproveitar.py:382` | ✅ PASS |
| REAP-24 | unidade referenciada não é apagada | `inv/test_reaproveitamento.py:90-94` (`ProtectedError`); admin `inv/test_admin_reaproveitamento.py:177-180` | ✅ PASS |
| REAP-25 | conta referenciada não é apagada | `inv/test_reaproveitamento.py:101-105` | ✅ PASS |

### P2: Corrigir uma sinalização errada

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| REAP-26 | admin lista (inovação, unidade, responsável, data) e exclui só para ADMINISTRADOR; USUARIO com staff ou superuser negado | `inv/test_admin_reaproveitamento.py:76-80` - as quatro células; `:85-88` exclusão; `:97-98` 403 nas três telas para staff e superuser; `:107-108` POST de exclusão 403; `:117-120` superuser sem staff → 302 ao login do admin | ✅ PASS ⚠️ (M30 morta; ver G2, G3) |
| REAP-27 | ninguém inclui nem altera; URLs diretas não gravam | `inv/test_admin_reaproveitamento.py:126` sem link de inclusão; `:136-146` add GET/POST 403 e nada criado; `:153` sem `_save`; `:167-168` POST na alteração 403 e registro igual | ✅ PASS (M28, M29 mortas) |

### P1: Painel de indicadores

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| REAP-28 | link "Indicadores" → `/indicadores/` no `nav` "Principal" de toda página autenticada | `inv/test_views_cabecalho.py:75-76` - `LINK_INDICADORES.search(navegacao)`, em 4 páginas; anônimo sem link `:80-84` | ✅ PASS |
| REAP-29 | 200, `<title>` começa com "Painel de indicadores", h1 | `ind/test_views_painel.py:59`, `:87-88`, USUARIO e administrador | ✅ PASS |
| REAP-30 | card "Inovações cadastradas" = todas, qualquer status | `ind/test_views_painel.py:94-96` - os três status presentes, `_card(...) == "4"`; demonstração `ind/test_desempenho_painel.py:70` | ✅ PASS ⚠️ (M34 morta; **M44 sobrevive**: cards com `hidden`) |
| REAP-31 | card "Reaproveitamentos registrados" = todos | `ind/test_views_painel.py:97` - `== "2"` | ✅ PASS ⚠️ (**M44 sobrevive**) |
| REAP-32 | caption, cabeçalhos, uma linha por categoria com 0, total desc e nome asc | `ind/test_views_painel.py:107-116` - cabeçalhos e lista literal; agregação `inv/test_agregacoes.py:58-65`, três status `:74` | ✅ PASS (M18, M19 mortas) |
| REAP-33 | caption, 3 cabeçalhos, uma linha por unidade com 0 e 0, contagens certas, origem desc e nome asc | `ind/test_views_painel.py:131-140`; sem fan-out `inv/test_agregacoes.py:89-90` - `(2, 3)`; ordem `:109-116` | ✅ PASS ⚠️ (M16, M20, M21 mortas; **M43 sobrevive**: seção com `hidden`) |
| REAP-34 | três gráficos com os títulos, uma barra por linha, na ordem da tabela | `ind/test_views_painel.py:247` - `list(graficos) == TITULOS`; `:274` pares (nome, valor) iguais aos da tabela | ✅ PASS ⚠️ (M25 morta; **M43 sobrevive**) |
| REAP-35 | comprimento = valor / maior × área; maior = 100%; 0 sem barra; tudo 0 sem barras | unit `ind/test_graficos.py:18`, `:25-26`, `:33`, `:42`; e2e `ind/test_views_painel.py:290-291` (480 e 160), `:303`, `:314` | ✅ PASS ⚠️ (M22, M23, M24 mortas; ver G4) |
| REAP-36 | nome e valor visíveis junto de cada barra, inclusive "0" | `ind/test_views_painel.py:274`, `:302` - `valor == "0"`; `:446-448` | ✅ PASS ⚠️ (M25 morta; ver G5) |
| REAP-37 | sem inovação: cards "0", texto, link "Cadastrar inovação" → `/inovacoes/nova/`, sem tabela nem gráfico | `ind/test_views_painel.py:147-153`; o contrário `:161-162` | ✅ PASS ⚠️ (M39 morta; **M44 sobrevive** para os cards) |
| REAP-38 | números do estado do banco a cada requisição | `ind/test_views_painel.py:170-187` - criar, reaproveitar e apagar mudam a resposta seguinte | ✅ PASS |
| REAP-39 | o painel não altera nada | `ind/test_views_painel.py:200` - `retrato() == antes` sobre as quatro tabelas | ✅ PASS |
| REAP-40 | anônimo → login com `next` | `ind/test_views_painel.py:207` | ✅ PASS (M26 morta) |

### P2: Desempenho do painel e do detalhe (RNF08)

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| REAP-41 | demonstração + 200 reaproveitamentos, GET em até 2 s | `ind/test_desempenho_painel.py:62-63` carga conferida; `:72` - `segundos < LIMITE_EM_SEGUNDOS` (2.0, `inv/test_desempenho.py:22`) | ✅ PASS |
| REAP-42 | consultas do painel não crescem com o volume das quatro tabelas | `ind/test_desempenho_painel.py:108` - `len(grande) == len(pequeno)`, com +500 inovações, +200 reaproveitamentos, +1 categoria e +1 unidade | ✅ PASS (M32 morta) |
| REAP-43 | consultas do detalhe não crescem com os reaproveitamentos | `inv/test_views_detalhe.py:660` - `django_assert_num_queries(8)` com 1 e 4 | ✅ PASS (M31 morta) |

### P1: Sinalização e painel acessíveis

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| REAP-44 | label ligado ao select por `for`/`id` | `inv/test_views_acessibilidade_alteracao.py:370`; `inv/test_views_reaproveitar.py:82-84` | ✅ PASS |
| REAP-45 | com erro: `aria-invalid="true"` e `aria-describedby` → a mensagem | `inv/test_views_acessibilidade_alteracao.py:393-395`, nos três erros; sem erro, sem `aria-invalid` (`:402`) | ✅ PASS |
| REAP-46 | `caption`, `th scope="col"`, primeira célula `th scope="row"` | `ind/test_views_painel.py:401-416` sobre a árvore do HTML | ✅ PASS |
| REAP-47 | `role="img"`, nome acessível = título, tabela na mesma página | `ind/test_views_painel.py:256-257` - `aria-labelledby` → id do `figcaption` com o título; `:446-450` a tabela da mesma seção traz os mesmos pares | ✅ PASS |
| REAP-48 | só componentes da `kira.css`; texto ≥ 4.5:1; barra ≥ 3:1; pares no DS-08 | `inv/test_views_sistema_design.py:653` - `_contraste(...) >= minimo` para nome, valor e barra; `:631` pares do DS-08 para `.reaproveitamentos`, `.metrica` e `.grafico`; `:405` telas estendem o base sem `<style` | ✅ PASS (M37 morta) |

### Edge Cases

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| REAP-49 | banco indisponível: 500 do projeto, nada gravado, sem detalhes da conexão | sinalização `inv/test_views_reaproveitar.py:403-410`; painel `ind/test_views_painel.py:495-507`, nas duas agregações | ✅ PASS |

**Status**: ✅ 49/49 ACs com evidência que afirma o valor da spec · ❌ 4 mutantes sobreviventes cobertos por AC (REAP-01, REAP-15, REAP-30/31/37, REAP-33/34) · ⚠️ 6 spec-precision gaps

---

## Spec-Precision Gaps

| # | AC / Task | O que a spec não define | Como o código e o teste resolvem |
| - | --------- | ----------------------- | -------------------------------- |
| G1 | REAP-04 | "no option preselected": não diz se a opção vazia "Selecione a unidade" conta. O Django a renderiza com `selected` no form não vinculado | O teste (`inv/test_forms_reaproveitamento.py:60`) afirma que nenhuma opção **com valor** vem `selected`. Leitura razoável; a spec deveria dizer "nenhuma unidade pré-selecionada" |
| G2 | REAP-26 | "deny" não define a resposta. O `USUARIO` com `is_staff` recebe 403. O superuser sem `is_staff` nem entra no admin e recebe 302 ao login do admin | `inv/test_admin_reaproveitamento.py:117-120` afirma o 302 e que nada é apagado |
| G3 | REAP-26/27 | o destino depois da exclusão no admin não é definido (o admin volta ao índice) | só `status_code == 302` (`:87`); fora das ACs |
| G4 | REAP-35 | "100% of the plot width" sem largura numérica nem formato. A barra sai `width="480.0"` (float) dentro do `viewBox` 600 | os testes afirmam o número (`float == 480`, `in {"160.0", "160"}`) e a ausência de vírgula, não o literal |
| G5 | REAP-36 | "the item name" não prevê nome longo. O SVG trunca em 70 caracteres (`truncatechars`), e a tradução pt-BR põe um espaço antes do texto truncado | `ind/test_views_painel.py:320-334` afirma o truncamento no SVG e o nome inteiro na tabela, que é a alternativa da REAP-47. Desvio aceitável, mas a spec deveria registrar a regra |
| G6 | T18 (`What`) | "ordem de leitura" não aparece em nenhuma AC nem no `Done when` | não há teste de ordem além da ordem dos gráficos (REAP-34) |

Também conferidos e **não** contados como gap: o savepoint da T2 e o `.order_by()` vazio da Q4. Os dois são mutantes equivalentes (M06, M17), e a seção do sensor explica por quê.

---

## Discrimination Sensor

Feito num worktree temporário (`git worktree add <scratchpad>/verifier-wt HEAD`, com o `.env` copiado). Cada mutação rodou a suíte inteira (`pytest -q -x`, com o `.venv` da raiz) e o arquivo foi restaurado com `git checkout` no worktree. No fim, `git worktree remove --force` e `git worktree prune`. O `git status --porcelain` da árvore real ficou vazio antes e depois, igual à linha de base. Profundidade: **P0 expandida** (integridade de dados e acesso), 46 mutações válidas.

| Mutação | File | Descrição | Resultado |
| ------- | ---- | --------- | --------- |
| M01 | `inovacoes/models.py` | guarda de status da RN09 removida | ✅ Morta (`test_registrar_fora_de_disponivel_e_recusado`) |
| M02 | `inovacoes/models.py` | status lido da instância, não do valor gravado | ✅ Morta (`test_registrar_recusa_pelo_status_gravado…`) |
| M03 | `inovacoes/models.py` | guarda da unidade de origem removida | ✅ Morta |
| M04 | — | âncora ambígua (o `select_for_update` aparece também no `avancar_status`); refeita como M04b | inválida, não conta |
| M04b | `inovacoes/models.py` | `select_for_update()` removido do `registrar_reaproveitamento` | ✅ Morta (`test_registrar_trava_a_linha_ao_ler_o_status`) |
| M05 | `inovacoes/models.py` | a `IntegrityError` da unicidade é relançada (500) | ✅ Morta |
| M06 | `inovacoes/models.py` | savepoint interno removido | ⚪ Sobrevive, **equivalente**: a `ValidationError` sai do `atomic` externo do próprio método, que reverte. Confirmado com um teste `transaction=True` descartável no worktree: sem o savepoint, a segunda chamada recusa, a contagem fica 1 e a transação de quem chama segue usável |
| M07 | `inovacoes/models.py` | toda `IntegrityError` vira "repetida" | ✅ Morta |
| M08 | `inovacoes/views.py` | `dispatch` não recusa inovação fora de "Disponível" | ✅ Morta |
| M09 | `inovacoes/views.py` | o ramo `status_indisponivel` do `form_valid` vira erro de campo | ⚪ Sobrevive, **equivalente na prática**: o ramo só roda se o status sair de "Disponível" entre o `dispatch` e a trava. A AD-011 e a própria spec (Dimensions Sweep, "o status não regride… não há corrida de status a tratar") excluem isso. É código defensivo inalcançável |
| M10 | `inovacoes/views.py` | `registrado_por` = autor da inovação | ✅ Morta |
| M11 | `inovacoes/views.py` | mensagem de sucesso cita a unidade de origem | ✅ Morta |
| M12 | `inovacoes/forms.py` | select oferece a unidade que já sinalizou | ✅ Morta |
| M13 | `inovacoes/forms.py` | select oferece a origem | ✅ Morta |
| M14 | `inovacoes/forms.py` | ordem do select invertida | ✅ Morta |
| M15 | `inovacoes/views.py` | `sem_elegiveis` sempre falso | ✅ Morta |
| M16 | `inovacoes/models.py` | Q4 com duas `Count()` e dois JOINs (fan-out) | ✅ Morta (`test_tabela_por_unidade…`; `inv/test_agregacoes.py:89`) |
| M17 | `inovacoes/models.py` | `.order_by()` vazio da subconsulta removido | ⚪ Sobrevive, **equivalente**: o Django 5.2.17 ignora o `Meta.ordering` em consultas com `GROUP BY` desde o 3.1. O teste das duas datas (`inv/test_agregacoes.py:130`) afirma o resultado |
| M18 | `inovacoes/models.py` | categorias ordenadas só por nome | ✅ Morta |
| M19 | `inovacoes/models.py` | categorias contam só "Disponível" | ✅ Morta |
| M20 | `inovacoes/models.py` | unidades ordenadas pela coluna errada | ✅ Morta |
| M21 | `inovacoes/models.py` | "reaproveitamentos feitos" conta inovações | ✅ Morta |
| M22 | `indicadores/graficos.py` | proporção sobre a soma, não sobre o maior | ✅ Morta |
| M23 | `indicadores/graficos.py` | sem guarda de divisão por zero | ✅ Morta (500 no painel todo zero) |
| M24 | `indicadores/templates/indicadores/grafico.html` | barra desenhada para o valor 0 | ✅ Morta |
| M25 | `indicadores/templates/indicadores/grafico.html` | rótulo "0" omitido | ✅ Morta |
| M26 | `indicadores/urls.py` | painel com `login_not_required` | ✅ Morta (varredura de `contas/tests/test_controle_acesso.py`) |
| M27 | `inovacoes/urls.py` | sinalização com `login_not_required` | ✅ Morta |
| M28 | `inovacoes/admin.py` | `has_add_permission` → True | ✅ Morta |
| M29 | `inovacoes/admin.py` | `has_change_permission` → True | ✅ Morta |
| M30 | `inovacoes/admin.py` | admin sem `AcessoSomenteAdministradorMixin` | ✅ Morta |
| M31 | `inovacoes/views.py` | detalhe sem `select_related("unidade")` (N+1) | ✅ Morta (REAP-43) |
| M32 | `indicadores/templates/indicadores/painel.html` | `reaproveitamentos.count` por linha (N+1, mesmos valores) | ✅ Morta (REAP-42) |
| M33 | `inovacoes/views.py` | lista do detalhe do mais recente ao mais antigo | ✅ Morta |
| M34 | `indicadores/views.py` | card conta só "Disponível" | ✅ Morta |
| M35 | `inovacoes/templates/inovacoes/inovacao_detail.html` | link de sinalizar em todo status | ✅ Morta |
| M36 | `inovacoes/migrations/0008_reaproveitamento.py` | constraint com outro nome | ✅ Morta |
| M37 | `templates/kira.css` | barra com `var(--border)` (contraste baixo) | ✅ Morta |
| M38 | `inovacoes/views.py` | inovação apagada durante o envio vira 500 | ✅ Morta |
| M39 | `indicadores/templates/indicadores/painel.html` | estado vazio decidido pelos reaproveitamentos | ✅ Morta |
| M40 | `inovacoes/templates/inovacoes/inovacao_detail.html` | sem singular ("1 unidades") | ✅ Morta |
| **M41** | `inovacoes/templates/inovacoes/inovacao_detail.html` | `<p class="acoes" hidden>` em volta do link "Sinalizar reaproveitamento" | ❌ **Sobrevive** → Fix 1 (REAP-01) |
| M42 | `inovacoes/templates/inovacoes/inovacao_detail.html` | seção "Reaproveitamentos" com `hidden` | ✅ Morta, mas só porque o helper `_secao` casa a tag literal, não porque confere visibilidade |
| **M43** | `indicadores/templates/indicadores/painel.html` | `<section aria-labelledby="por-unidade" hidden>` | ❌ **Sobrevive** → Fix 1 (REAP-33, REAP-34) |
| **M44** | `indicadores/templates/indicadores/painel.html` | `<dl class="metricas" hidden>` | ❌ **Sobrevive** → Fix 1 (REAP-30, REAP-31, REAP-37) |
| **M45** | `inovacoes/templates/inovacoes/inovacao_reaproveitar.html` | `<p hidden>Todas as outras unidades…` | ❌ **Sobrevive** → Fix 1 (REAP-15) |
| M46 | `inovacoes/templates/inovacoes/inovacao_detail.html` | `<ol class="reaproveitamentos" hidden>` | ✅ Morta, também por casamento literal da tag |

**Sensor depth**: P0 expandida (46 mutações válidas; ≥ 5 exigidas)
**Result**: 39 mortas, 7 sobreviventes. 3 equivalentes (M06, M09, M17), e 4 são lacunas de teste (M41, M43, M44, M45). FAIL ❌

As regras centrais morrem todas: as guardas da RN09 (status pelo valor gravado, origem, unicidade e trava), o fan-out da Q4, a geometria das barras (zero, proporção e divisão por zero), a proteção de acesso do painel e da sinalização, o admin só listar e excluir e o número de consultas do painel e do detalhe. O que sobrevive é uma classe só: o elemento exigido continua no HTML, mas fora da tela e do leitor de tela.

---

## Code Quality

| Principle | Status |
| --------- | ------ |
| Minimum code | ✅. Exceção menor: o ramo `status_indisponivel` de `InovacaoReaproveitarView.form_valid` (`inovacoes/views.py`) é inalcançável sob a AD-011 (M09) |
| Surgical changes | ✅. Os testes antigos alterados (`ROTAS_SEM_AUTORIA`, STAT-30, DS-01 9→11, `CONSULTAS_DO_DETALHE` 7→8, `PECAS`, `RAIZES`, cores) estão autorizados na spec e no `tasks.md` |
| No scope creep | ✅ |
| Matches patterns | ✅. Mesmo desenho do `avancar_status` (AD-011/AD-012), `LoginRequiredMiddleware` (AD-006) e o mixin de admin (AD-007) |
| SPEC_DEVIATION | 1, `InovacaoReaproveitarView.get_form_kwargs` (só `data` e `inovacao`). Desvio do design, não da spec; sem efeito em AC |
| Spec-anchored outcome check | ✅, com 6 gaps (G1–G6) |
| Per-layer coverage | ✅. Modelo 1:1 (RN09), rotas com caminho feliz, borda e erro |
| Every test maps to a requirement | ✅. `test_unidade_elegivel_e_valida`, `test_lista_vazia_nao_tem_barras`, `test_le_o_atributo_pedido` e `test_altura_do_grafico…` cobrem Done-when de T3/T12 |
| Documented guidelines | `.specs/STATE.md` (AD-001 … AD-012), confirmed lessons L-003 (aplicada: staff e superuser no admin) e L-005 |

---

## Edge Cases

- [x] Inovação "Disponível" da carga de demonstração, sem histórico: sinalizável (`ind/test_desempenho_painel.py:35`, pelo método)
- [x] Inovação excluída entre abrir e enviar: 404 (`inv/test_views_reaproveitar.py:303`)
- [x] Duplo clique: o segundo POST cai na REAP-12 (`inv/test_views_reaproveitar.py:262`, `:287`)
- [x] Só existe a unidade de origem: mensagem da REAP-15 (`inv/test_views_reaproveitar.py:147`)
- [x] Unidade renomeada: leitura pela FK (`{{ r.unidade.nome }}`, `{{ unidade.nome }}`). Sem teste próprio; é consequência direta da leitura pela FK
- [x] Categoria ou unidade sem inovação: 0 na tabela e no gráfico, sem barra (`ind/test_views_painel.py:302-303`)
- [x] Autor sinaliza por outra unidade: permitido (`inv/test_reaproveitamento.py:146`, `conta="autor"`; `inv/test_views_reaproveitar.py:214`)
- [x] Id não numérico na rota: o conversor `<int:pk>` não casa e devolve o 404 padrão

---

## Gate Check

- **Gate command**: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q`
- **Result**: ruff "All checks passed!"; format "129 files already formatted"; makemigrations "No changes detected"; pytest **865 passed**, 0 failed, 0 skipped (17.95 s); exit 0
- **Test count before feature**: 710 (T1: 717, +7)
- **Test count after feature**: 865
- **Delta**: +155
- **Skipped tests**: nenhum
- **Failures**: nenhuma

---

## Fix Plans

### Fix 1: as asserções de "exibido" da F6 não rejeitam `hidden`, `inert` nem `aria-hidden`

- **Root cause**: `_links` (`inv/test_views_detalhe.py:192`), `_afirma_sem_elegiveis` (`inv/test_views_reaproveitar.py:129`), `_card` (`ind/test_views_painel.py:63`), `_tabela` (`:67`) e `_graficos` (`:219`) leem o HTML cru por regex. Um atributo `hidden` no próprio elemento ou num ancestral não muda o texto casado.
- **Fix task** (só teste, sem mudar produção): nos testes das REAP-01, REAP-15, REAP-30, REAP-31, REAP-33, REAP-34 e REAP-37, conferir sobre a árvore do HTML que o elemento exigido e cada ancestral não têm `hidden`, `inert` nem `aria-hidden="true"`, em qualquer caixa (L-028, L-030). A árvore `Arvore` de `ind/test_views_painel.py:342` serve de base, e o `ESCONDE` de `inv/test_views_detalhe.py:439` dá os atributos. Aplicar a mesma checagem aos itens da REAP-17/REAP-18 e ao formulário da REAP-03, que hoje só morrem por casamento literal (M42, M46).
- **Done when**: M41, M43, M44 e M45 morrem, e também `hidden` no `<section>` "Reaproveitamentos", no `<ol class="reaproveitamentos">`, no `<form>` da sinalização e em `<section aria-labelledby="por-categoria">`. Gate verde.
- **Priority**: Major (lacuna de teste; o código de produção está correto)

---

## Requirement Traceability Update

| Requirement | Previous Status | New Status |
| ----------- | --------------- | ---------- |
| REAP-02 … REAP-14, REAP-16 … REAP-29, REAP-32, REAP-35, REAP-36, REAP-38 … REAP-49 | Implementing | ✅ Verified (gaps G1–G6 registrados) |
| REAP-01, REAP-15, REAP-30, REAP-31, REAP-33, REAP-34, REAP-37 | Implementing | ❌ Needs Fix (Fix 1, só teste) |

---

## Summary

**Overall**: ❌ Not Ready (só testes a reforçar)

**Spec-anchored check**: 49/49 ACs com evidência e o valor da spec afirmado · 6 spec-precision gaps
**Sensor**: 39/46 mortas. 3 sobreviventes equivalentes e 4 lacunas de teste
**Gate**: 865 passed

**What works**: a RN09 inteira (status pelo valor gravado com trava, origem, unicidade no banco com a recusa certa e as outras violações subindo); o select elegível; as mensagens exatas; o acesso (anônimo, CSRF e qualquer autenticado sem 403); o admin só listar e excluir para o ADMINISTRADOR; as agregações sem fan-out e com zeros; a geometria das barras; o número fixo de consultas; o RNF08; a acessibilidade de tabela, gráfico e formulário; o 500 sem vazamento.

**Issues found**: 4 mutantes de ocultação sobrevivem (Fix 1). É a mesma lacuna de teste da F5.

**Next steps**: rodar o Fix 1 como task de teste e reexecutar o Verifier (iteração 2 de 3). Na F5 o usuário aceitou esta mesma classe como risco residual depois de esgotado o loop. Essa decisão é dele, não do Verifier.
