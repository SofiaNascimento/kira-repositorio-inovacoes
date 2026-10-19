# Reaproveitamento e Indicadores (F6) Validation

**Date**: 2026-10-19
**Iteration**: 3 de 3, a última (as iterações 1 e 2 ficam abaixo, intactas; a iteração 3 está em [Iteração 3](#iteração-3), no fim)
**Spec**: `.specs/features/reaproveitamento-indicadores/spec.md` (REAP-01 … REAP-49)
**Diff range (iteração 3)**: feature `eb957d2..4b3dae2` em `main` (HEAD = `4b3dae2`), 25 commits, 45 arquivos, +5836/−39. Correção: `4b3dae2` (T20, Fix 2), só em 7 arquivos de teste e no `tasks.md`. `git diff ebbc35e..4b3dae2 -- . ':!.specs'` só toca `inovacoes/tests/` e `indicadores/tests/`: nenhum código de produção mudou desde a iteração 1.
**Diff range (iteração 2)**: feature `eb957d2..865fe7a` em `main` (HEAD = `865fe7a`), 23 commits, 45 arquivos, +5450/−39. Correção: `865fe7a` (T19, Fix 1), só em `inovacoes/tests/` (`visibilidade.py` novo, `test_views_detalhe.py`, `test_views_reaproveitar.py`), `indicadores/tests/test_views_painel.py` e o `tasks.md`. `git diff e755a45..865fe7a -- . ':!inovacoes/tests' ':!indicadores/tests' ':!.specs'` vazio: nenhum código de produção mudou desde a iteração 1.
**Diff range (iteração 1)**: `eb957d2..e755a45` em `main` (HEAD = `e755a45`), 21 commits, 19 de código e teste (T1 `69f655d` … T18 `985bfa4`) e 2 de pausa (`0bd904a`, `50d41ce`) mais o `e755a45`, só artefatos. 41 arquivos, +4805/−16; sem `.specs` e `docs`, 35 arquivos, +2789/−16. Produção: `inovacoes/models.py`, `forms.py`, `views.py`, `admin.py`, `urls.py`, `migrations/0008_reaproveitamento.py`, os templates `inovacao_detail.html` e `inovacao_reaproveitar.html`, a app `indicadores/` (`graficos.py`, `views.py`, `urls.py`, `painel.html`, `grafico.html`), `templates/base.html`, `templates/kira.css` e `config/`.
**Verifier**: sub-agente independente (autor ≠ verifier)

**Verdict**: FAIL ❌ na iteração 3 (HEAD `4b3dae2`), a última do loop: **escalar ao usuário**. A T20 fecha a classe das iterações 1 e 2. X01, Y01 e Y02 morrem, M41–M46 continuam mortas e, com o `exibido()` neutralizado, X01/Y01/Y02 voltam a sobreviver, então a morte vem das asserções novas. A minha varredura independente não achou nenhuma asserção de "exibido" da F6 que ainda leia só o HTML cru. As regras centrais seguem mortas (RN09 com trava, fan-out, geometria, acesso, admin, consultas). O FAIL vem de **4 vetores de ocultação novos**, que ficam fora do modelo do `exibido()` (só atributos HTML): **L1** atributos de apresentação SVG no texto do gráfico (N01 `display="none"`, N12 `fill-opacity="0"`; REAP-36), **L2** controle desabilitado (N04 `<button disabled>`, N13 `<fieldset disabled>`; REAP-03), **L3** ocultação por CSS na `kira.css` (N02 `.metricas`, N10 `.grafico__valor`; REAP-30/31/36), **L4** `role="presentation"` na tabela (N05; REAP-46). O código de produção está correto. As quatro são lacunas de teste. A decisão de rodar um Fix 3 ou fechar com risco registrado é do usuário.

**Verdict anterior (iteração 2)**: FAIL ❌ (HEAD `865fe7a`). A T19 mata os quatro sobreviventes da iteração 1 (M41, M43, M44, M45), e M42/M46 agora morrem também pela visibilidade. O helper `exibido()` esconde o que deve esconder e as asserções dependem dele: neutralizado, M41, M43, M44 e M45 voltam a sobreviver. Nenhuma regra central afrouxou. Mas sobrevivem dois mutantes novos da mesma classe, em código e ACs da F6 que a T19 não alcançou: **X01**, o link "Indicadores" do `nav` "Principal" dentro de um `<span hidden>` (REAP-28, `templates/base.html:23`), e **Y01**, o `h1` "Painel de indicadores" dentro de um `<div hidden>` (REAP-29, `indicadores/templates/indicadores/painel.html:6`). Os testes das duas ACs ainda leem o HTML cru (`inovacoes/tests/test_views_cabecalho.py:75`, `indicadores/tests/test_views_painel.py:108`). Um terceiro sobrevivente, **Y02** (`<ul class="mensagens" hidden>`, REAP-06/REAP-09), fica em código anterior à F6 e entra como lacuna de menor prioridade. Fix 2 abaixo, só de teste. A próxima é a iteração 3, a última antes de escalar. Antes: FAIL ❌ na iteração 1 (HEAD `e755a45`), com 4 sobreviventes de ocultação (M41, M43, M44, M45).

**Iteração 3 em resumo:** o gate passa com 865 testes. A checagem ancorada na spec dá 49/49, e REAP-28/REAP-29 voltam a ✅. O sensor rodou 40 mutações válidas: 33 mortas e 7 sobreviventes, todas lacunas e nenhuma equivalente, agrupadas em L1–L4. G1–G6 e os equivalentes M06, M09, M17 e C07 se mantêm.

**Iteração 2 em resumo:** o gate passa com 865 testes e o código de produção é o mesmo da iteração 1. A checagem ancorada na spec segue 49/49, com as linhas reconferidas no HEAD. O sensor rodou 47 mutações válidas (mais 13 combinações de auditoria do helper): 44 mortas, 3 sobreviventes de lacuna (X01, Y01, Y02) e 1 equivalente nova (C07). G1–G6 e os equivalentes M06, M09 e M17 se mantêm.

---

## Iteração 1 (registro original)

**Verdict (iteração 1)**: FAIL ❌. Das 49 ACs, 49 têm evidência `file:line` com o valor da spec afirmado, e o código de produção cumpre a spec em tudo o que conferi. O FAIL vem do sensor. Das 46 mutações válidas, 39 morrem e 7 sobrevivem. Três dos sobreviventes são equivalentes, sem comportamento observável (M06, M09, M17). Os outros quatro são lacunas de teste: o elemento continua no HTML, mas com `hidden`, e a suíte passa. M41 esconde o link "Sinalizar reaproveitamento" (REAP-01). M43 esconde a seção "Por unidade" do painel, com a tabela e dois gráficos (REAP-33, REAP-34). M44 esconde os dois cards (REAP-30, REAP-31, REAP-37). M45 esconde o texto da REAP-15. É a mesma classe de lacuna da F5: as asserções de "exibido" leem o HTML cru por regex, não o DOM exposto (L-028, L-030). Os quatro viram fix tasks só de teste. Nenhum código de produção precisa mudar.

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

---

## Iteração 2

**Date**: 2026-10-19 · **HEAD**: `865fe7a` · **Diff range**: `eb957d2..865fe7a` (correção `6b71bcd..865fe7a`, T19, só teste)

### Task Completion

| Task | Status | Notes |
| ---- | ------ | ----- |
| T1–T18 | ✅ Done | Inalteradas desde a iteração 1 |
| T19 (Fix 1) | ✅ Done | `865fe7a`. Helper `inovacoes/tests/visibilidade.py` (`exibido(html)`) e o padrão "extraído de `exibido(html)` == extraído do cru" em `_card`, `_tabela`, `_graficos`, no `div.vazio`, em `_reaproveitamentos`, no link de sinalizar, no `<main>` do formulário e em `_afirma_sem_elegiveis`. A contagem continua 865: a T19 reforça asserções existentes, não cria testes |

### Auditoria do helper `exibido()`

Leitura (`inovacoes/tests/visibilidade.py:16-84`): `HTMLParser` com uma pilha de elementos abertos; cada item guarda se ele ou um ancestral está escondido. `escondido()` (`:16-20`) cobre `<template>`, `hidden` e `inert` pela presença do atributo (o parser já põe o nome em minúsculas e dá `None` ao atributo sem valor) e `aria-hidden` por `strip().lower() == "true"`. A subárvore some porque `_abrir` (`:38-43`) herda o `oculto` do topo da pilha e `_texto` (`:67-69`) descarta o texto escondido. Comentários caem por omissão (sem `handle_comment`), e o conteúdo de `<details>` fechado fora do `<summary>` também sai. Elementos vazios (`VAZIOS`) não entram na pilha, e o `<rect .../>` vai por `handle_startendtag`.

Checagem direta no scratch (15 entradas): some a subárvore com `hidden`, `hidden=""`, `hidden=''`, `HIDDEN`, `hidden=hidden`, `inert`, `INERT=""`, `aria-hidden="true"`, `aria-hidden='TRUE'`, `ARIA-HIDDEN=True` sem aspas, `aria-hidden=" true "`, `aria-hidden` no `<main>` com o alvo quatro níveis abaixo, `<td hidden>`, `<rect hidden/>` e um vazio dentro de `<div hidden>`. Ficam intactos `aria-hidden="false"`, `class="hidden"` e `data-hidden`. O desvio possível é esconder **demais**: tag não fechada que o navegador fecharia sozinha (`<p hidden>…<div>`) e `hidden` em elemento SVG (o `[hidden]` do navegador só vale no namespace HTML) somem do `exibido`. Nas duas situações a comparação com o cru falha, então o teste quebra alto. Não há caminho de vacuidade.

Mutação do helper no scratch, combinada com um mutante de ocultação (a combinação tem de **sobreviver** para provar que a morte vem do helper):

| Combinação | Resultado | Leitura |
| ---------- | --------- | ------- |
| H00: `exibido` devolve o HTML cru, sozinho | 865 passam | baseline idêntico: nenhuma asserção depende de o helper mudar o HTML sem mutante |
| cru + M41, M43, M44, M45, V09 | todas sobrevivem | as cinco mortes da tabela abaixo vêm do `exibido` |
| cru + M42, M46 | morrem | também por casamento literal da tag (`_secao`, regex do `<ol>`), como na iteração 1 |
| sem `inert` + V03 (`<p class="acoes" inert>`) | sobrevive | o ramo `inert` é o que mata V03 |
| sem propagação ao descendente + M41, M43 | sobrevivem | a herança da pilha é o que mata `hidden` em ancestral |
| sem `aria-hidden` + V01 | sobrevive | o ramo `aria-hidden` é o que mata V01 |
| sem `.lower()` + V02 (`aria-hidden="TRUE"` no `<main>`) | o teste do painel passa; a morte vem de um teste da F5 com o próprio `ESCONDE` | a caixa do `exibido` é o que mata V02 no painel (`indicadores/tests/test_views_painel.py:116`) |

Conclusão: o helper remove de fato a subárvore de `hidden`, `inert` e `aria-hidden="true"` em qualquer caixa e com qualquer aspas, e as asserções que o usam falham quando ele é neutralizado. O padrão "exibido == cru" não passa por trivialidade: com o HTML de produção os dois são iguais porque nada está escondido, e qualquer ocultação no recorte os separa.

### Spec-Anchored Acceptance Criteria (re-derivado no HEAD `865fe7a`)

`inv/` = `inovacoes/tests/`, `ind/` = `indicadores/tests/`. Os arquivos que a T19 não tocou (`inv/test_reaproveitamento.py`, `inv/test_forms_reaproveitamento.py`, `inv/test_admin_reaproveitamento.py`, `inv/test_agregacoes.py`, `inv/test_views_cabecalho.py`, `inv/test_views_acessibilidade_alteracao.py`, `inv/test_views_sistema_design.py`, `ind/test_graficos.py`, `ind/test_desempenho_painel.py`) mantêm as linhas da iteração 1. As linhas abaixo foram relidas nos três arquivos alterados.

| AC | Spec-defined outcome | `file:line` + assertion (HEAD `865fe7a`) | Result |
| -- | -------------------- | ---------------------------------------- | ------ |
| REAP-01 | link "Sinalizar reaproveitamento" → `/inovacoes/<id>/reaproveitar/`, exibido, a todo autenticado | `inv/test_views_detalhe.py:601` cru e `:603` - `_links(exibido(html), SINALIZAR) == [f"/inovacoes/{pk}/reaproveitar/"]` | ✅ PASS (M41, V03, W01, W02 mortas) |
| REAP-02 | nenhum href nem texto fora de "Disponível" | `inv/test_views_detalhe.py:617-618` | ✅ PASS |
| REAP-03 | 200, `<title>`, texto, select rotulado obrigatório, botão, "Cancelar" | `inv/test_views_reaproveitar.py:69`, `:73`, `:76` - `_conteudo(exibido(html)) == conteudo`, `:83` `required`, `:96` `cancelar == [...]` | ✅ PASS (V09, V10 mortas) |
| REAP-04 | elegíveis em ordem alfabética, sem pré-seleção | `inv/test_forms_reaproveitamento.py:46-52`, `:60`; e2e `inv/test_views_reaproveitar.py:106` | ✅ PASS ⚠️ G1 |
| REAP-05 | um registro, conta logada, hora do servidor, 302 | `inv/test_views_reaproveitar.py:222-227`; `inv/test_reaproveitamento.py:159` | ✅ PASS (C09 morta) |
| REAP-06 | mensagem exata, uma vez | `inv/test_views_reaproveitar.py:237`, `:240` | ✅ PASS ⚠️ (Y02 sobrevive, componente anterior à F6) |
| REAP-07 | nenhum campo muda | `inv/test_reaproveitamento.py:280` | ✅ PASS |
| REAP-08 | GET nunca grava | `inv/test_views_reaproveitar.py:112-114` | ✅ PASS |
| REAP-09 | fora de "Disponível": nada gravado, 302, aviso uma vez | GET `inv/test_views_reaproveitar.py:127-129`; POST `:253-254` | ✅ PASS (C08 morta) ⚠️ Y02 |
| REAP-10 | o modelo recusa e não grava | `inv/test_reaproveitamento.py:171-176`, `:189-191` | ✅ PASS (C01 morta) |
| REAP-11 | origem → 200, erro exato, nada gravado | `inv/test_views_reaproveitar.py:260-261` (`_afirma_formulario_com_erro`, `:211`) | ✅ PASS (C02 morta) |
| REAP-12 | repetida → 200, erro com o nome | `inv/test_views_reaproveitar.py:268-269`; `inv/test_reaproveitamento.py:227-231` | ✅ PASS (C04 morta) |
| REAP-13 | vazio, inexistente, não numérico → mensagem exata | `inv/test_views_reaproveitar.py:276-277` | ✅ PASS |
| REAP-14 | constraint no banco; corrida → REAP-12, sem 500 | `inv/test_reaproveitamento.py:49`, `:259-260`; `inv/test_views_reaproveitar.py:292-293` | ✅ PASS (C03b morta) |
| REAP-15 | texto exato, "Voltar para a inovação", sem select nem botão, exibidos | `inv/test_views_reaproveitar.py:136` - `_conteudo(exibido(...)) == conteudo`, `:137`, `:139`; cenários `:149`, `:157` | ✅ PASS (M45, W04 mortas) |
| REAP-16 | 404 com "Inovação não encontrada." | `inv/test_views_reaproveitar.py:163-165`, `:308-310` | ✅ PASS |
| REAP-17 | h2 "Reaproveitamentos" e o texto de 0, 1 e N, exibidos | `inv/test_views_detalhe.py:586` - `_secao(exibido(html), ...) == secao`; `:641` | ✅ PASS (M42, V11 mortas) |
| REAP-18 | itens do mais antigo ao mais recente, "<unidade> — dd/mm/aaaa" | `inv/test_views_detalhe.py:656`, com `:586` | ✅ PASS (M46, V12 mortas) |
| REAP-19 | todo autenticado, nunca 403 | `inv/test_views_reaproveitar.py:174-181`, `:339-347` | ✅ PASS |
| REAP-20 | anônimo → login com `next` | `inv/test_views_reaproveitar.py:361-362` | ✅ PASS |
| REAP-21 | sem CSRF → 403 | `inv/test_views_reaproveitar.py:371-372` | ✅ PASS |
| REAP-22 | campos do corpo ignorados | `inv/test_views_reaproveitar.py:329` | ✅ PASS |
| REAP-23 | excluir a inovação leva os registros dela | `inv/test_reaproveitamento.py:83`; `inv/test_views_reaproveitar.py:387` | ✅ PASS |
| REAP-24, REAP-25 | unidade e conta referenciadas protegidas | `inv/test_reaproveitamento.py:90-94`, `:101-105` | ✅ PASS |
| REAP-26 | admin lista e exclui só para ADMINISTRADOR | `inv/test_admin_reaproveitamento.py:76-80`, `:85-88`, `:97-98`, `:117-120` | ✅ PASS ⚠️ G2, G3 (C12 morta) |
| REAP-27 | ninguém inclui nem altera | `inv/test_admin_reaproveitamento.py:126`, `:136-146`, `:167-168` | ✅ PASS (C11 morta) |
| REAP-28 | link "Indicadores" → `/indicadores/` **exibido** no `nav` "Principal" | `inv/test_views_cabecalho.py:75-76` - `LINK_INDICADORES.search(navegacao)` sobre o HTML cru | ❌ GAP (**X01 sobrevive**: link num `<span hidden>`) |
| REAP-29 | 200, `<title>`, `h1` "Painel de indicadores" | `ind/test_views_painel.py:60`, `:107` e `:108` - `re.search(r"<h1>Painel de indicadores</h1>", html)` sobre o cru | ❌ GAP (**Y01 sobrevive**: `h1` num `<div hidden>`) |
| REAP-30, REAP-31 | cards com todas as inovações e todos os reaproveitamentos, exibidos | `ind/test_views_painel.py:116-117`, via `_card` (`:64-69`, exibido em `:68`) | ✅ PASS (M44, V08, W03 mortas) |
| REAP-32 | tabela por categoria, ordem e zeros, exibida | `ind/test_views_painel.py:127-135`, via `_tabela` (`:82`) | ✅ PASS (V01, C14 mortas) |
| REAP-33 | tabela por unidade, contagens sem fan-out, ordem, exibida | `ind/test_views_painel.py:151-160` | ✅ PASS (M43, V04, C05, C15 mortas) |
| REAP-34 | três gráficos, uma barra por linha, ordem da tabela, exibidos | `ind/test_views_painel.py:277`, `:305`, via `_graficos` (`:247`) | ✅ PASS (V05, V06 mortas) |
| REAP-35 | proporção ao maior, 0 sem barra, tudo 0 sem barras | `ind/test_graficos.py:18`, `:25-26`, `:33`, `:42`; `ind/test_views_painel.py:320-321`, `:333`, `:346` | ✅ PASS ⚠️ G4 (C06 morta; C07 equivalente) |
| REAP-36 | nome e valor visíveis, inclusive "0" | `ind/test_views_painel.py:305`, `:332` | ✅ PASS ⚠️ G5 (V06 morta) |
| REAP-37 | sem inovação: cards "0", texto e link exibidos, sem tabela nem gráfico | `ind/test_views_painel.py:167-168`, `:172-175` | ✅ PASS (V07, V13 mortas) |
| REAP-38 | números do banco a cada requisição | `ind/test_views_painel.py:193-209` | ✅ PASS |
| REAP-39 | o painel não altera nada | `ind/test_views_painel.py:223` | ✅ PASS |
| REAP-40 | anônimo → login | `ind/test_views_painel.py:230` | ✅ PASS (C13 morta) |
| REAP-41 | demonstração + 200 em até 2 s | `ind/test_desempenho_painel.py:62-63`, `:72` | ✅ PASS |
| REAP-42 | consultas do painel fixas | `ind/test_desempenho_painel.py:108` | ✅ PASS |
| REAP-43 | consultas do detalhe fixas | `inv/test_views_detalhe.py:667` - `django_assert_num_queries(CONSULTAS_DO_DETALHE)` | ✅ PASS (C10 morta) |
| REAP-44, REAP-45 | label/`for`, `aria-invalid` e `aria-describedby` | `inv/test_views_acessibilidade_alteracao.py:370`, `:393-395`, `:402` | ✅ PASS |
| REAP-46 | caption e `scope` | `ind/test_views_painel.py:428-447` | ✅ PASS |
| REAP-47 | `role="img"`, nome = título, tabela na seção | `ind/test_views_painel.py:286-287`, `:470-480` | ✅ PASS |
| REAP-48 | componentes da `kira.css`, contrastes | `inv/test_views_sistema_design.py:653`, `:631`, `:405` | ✅ PASS |
| REAP-49 | 500 do projeto, nada gravado, sem detalhes | `inv/test_views_reaproveitar.py:408-415`; `ind/test_views_painel.py:525-536` | ✅ PASS |

**Status**: 47/49 ACs com evidência que afirma o valor da spec e resiste ao sensor · ❌ 2 ACs com sobrevivente de ocultação (REAP-28, REAP-29) · ⚠️ REAP-06/REAP-09 com Y02 em componente anterior à F6 · ⚠️ 6 spec-precision gaps (mantidos)

### Spec-Precision Gaps e equivalentes (reavaliados)

| # | Decisão | Justificativa |
| - | ------- | ------------- |
| G1 (REAP-04, opção vazia `selected`) | Mantido | a spec não mudou; o teste segue em `inv/test_forms_reaproveitamento.py:60` |
| G2 (REAP-26, "deny" sem resposta definida) | Mantido | idem; `inv/test_admin_reaproveitamento.py:117-120` |
| G3 (destino após excluir no admin) | Mantido | fora das ACs; só `status_code == 302` |
| G4 (REAP-35, largura sem formato) | Mantido | `ind/test_views_painel.py:320-321` afirma o número, não o literal |
| G5 (REAP-36, truncamento em 70) | Mantido | `ind/test_views_painel.py:350-365`; a regra não está na spec |
| G6 (T18, "ordem de leitura") | Mantido | nem AC nem Done-when citam; nenhum teste novo |
| M06 (savepoint) | Equivalente, mantido | `inovacoes/models.py:326` sem mudança desde a iteração 1; a prova com `transaction=True` continua válida |
| M09 (ramo `status_indisponivel` do `form_valid`) | Equivalente, mantido | `inovacoes/views.py` sem mudança; inalcançável sob a AD-011 |
| M17 (`.order_by()` vazio da subconsulta) | Equivalente, mantido | `inovacoes/models.py:72` sem mudança; o Django 5.2.17 ignora o `Meta.ordering` com `GROUP BY` |
| C07 (`if valor and maior` → `if valor`) | Equivalente, novo | `indicadores/graficos.py:46`: contagens são ≥ 0, então `maior == 0` implica `valor == 0`; as duas condições coincidem em todo valor alcançável |

### Discrimination Sensor (iteração 2)

Worktree temporário (`git worktree add --detach <scratchpad>/vwt2 HEAD`, `.env` copiado). Cada mutação rodou a suíte inteira com `pytest -q -x -p no:cacheprovider` pelo `.venv` da raiz e foi desfeita com `git checkout` no worktree, conferindo `git status --porcelain` vazio do worktree depois de cada uma. No fim, `git worktree remove --force` e `git worktree prune`. O `git status --porcelain` da árvore real ficou vazio antes e depois, igual à linha de base. Profundidade: **P0 expandida**, 47 mutações válidas (uma âncora ambígua, C03, refeita como C03b), mais as 13 combinações da auditoria do helper acima.

| Mutação | File | Descrição | Resultado |
| ------- | ---- | --------- | --------- |
| M41 | `inovacoes/templates/inovacoes/inovacao_detail.html:86` | `<p class="acoes" hidden>` no link de sinalizar | ✅ Morta (`test_disponivel_mostra_o_link_de_sinalizar_a_todo_perfil`) |
| M42 | `inovacao_detail.html:89` | seção "Reaproveitamentos" com `hidden` | ✅ Morta |
| M43 | `indicadores/templates/indicadores/painel.html:41` | `<section aria-labelledby="por-unidade" hidden>` | ✅ Morta (`test_tabela_por_unidade…`) |
| M44 | `painel.html:9` | `<dl class="metricas" hidden>` | ✅ Morta (`test_cards_contam…`) |
| M45 | `inovacoes/templates/inovacoes/inovacao_reaproveitar.html:11` | `<p hidden>Todas as outras…` | ✅ Morta (`test_todas_as_outras_unidades_ja_sinalizaram`) |
| M46 | `inovacao_detail.html:98` | `<ol class="reaproveitamentos" hidden>` | ✅ Morta |
| V01 | `painel.html:16` | seção "Por categoria" com `aria-hidden="true"` | ✅ Morta |
| V02 | `templates/base.html:38` | `<main id="conteudo" aria-hidden="TRUE">` (ancestral mais alto, caixa alta) | ✅ Morta |
| V03 | `inovacao_detail.html:86` | `<p class="acoes" inert>` no link de sinalizar | ✅ Morta |
| V04 | `painel.html:60` | `<td hidden>` em "Reaproveitamentos feitos" | ✅ Morta |
| V05 | `indicadores/templates/indicadores/grafico.html:11` | `<rect hidden class="grafico__barra">` | ✅ Morta |
| V06 | `grafico.html:12` | `aria-hidden="true"` no texto do valor | ✅ Morta |
| V07 | `painel.html:71` | `hidden=""` no parágrafo do link "Cadastrar inovação" | ✅ Morta |
| V08 | `painel.html:11` | `HIDDEN` só no card "Reaproveitamentos registrados" | ✅ Morta |
| V09 | `inovacao_reaproveitar.html:18` | `<form … hidden>` (REAP-03) | ✅ Morta |
| V10 | `inovacao_reaproveitar.html:8` | `<div class="cartao" aria-hidden='true'>` (aspas simples) | ✅ Morta |
| V11 | `inovacao_detail.html:96` | `<p hidden>Reaproveitada por…` | ✅ Morta |
| V12 | `inovacao_detail.html:100` | `<li hidden="">` nos itens | ✅ Morta |
| V13 | `painel.html:69` | `<div class="vazio" inert>` | ✅ Morta |
| W01 | `inovacao_detail.html:86` | link de sinalizar dentro de comentário HTML | ✅ Morta |
| W02 | `inovacao_detail.html:86` | link de sinalizar dentro de `<template>` | ✅ Morta |
| W03 | `painel.html:9` | cards dentro de `<details>` fechado | ✅ Morta |
| W04 | `inovacao_reaproveitar.html:11` | `ARIA-HIDDEN=true` sem aspas no texto da REAP-15 | ✅ Morta |
| **X01** | `templates/base.html:23` | link "Indicadores" do `nav` dentro de `<span hidden>` | ❌ **Sobrevive** → Fix 2 (REAP-28) |
| **Y01** | `indicadores/templates/indicadores/painel.html:6` | `<div hidden><h1>Painel de indicadores</h1></div>` | ❌ **Sobrevive** → Fix 2 (REAP-29) |
| **Y02** | `templates/base.html:41` | `<ul class="mensagens" hidden>` | ❌ Sobrevive → Fix 2, opcional (REAP-06, REAP-09; bloco anterior à F6) |
| X02 | `templates/base.html:39` | `<div role="status" hidden>` | ✅ Morta (incidental: o `<main>` do formulário da REAP-03 muda) |
| C01 | `inovacoes/models.py:317` | guarda de status da RN09 removida | ✅ Morta |
| C02 | `inovacoes/models.py:322` | guarda da unidade de origem removida | ✅ Morta |
| C03 | — | âncora ambígua (o `select_for_update` aparece também no `avancar_status`) | inválida, refeita como C03b |
| C03b | `inovacoes/models.py:313` | `select_for_update()` removido do `registrar_reaproveitamento` | ✅ Morta (`test_registrar_trava_a_linha_ao_ler_o_status`) |
| C04 | `inovacoes/models.py:333` | teste do nome da constraint invertido | ✅ Morta |
| C05 | `inovacoes/models.py:80-81` | Q4 com duas `Count()` (fan-out) | ✅ Morta |
| C06 | `indicadores/graficos.py:46` | proporção sobre a soma | ✅ Morta |
| C07 | `indicadores/graficos.py:46` | `if valor and maior` → `if valor` | ⚪ Sobrevive, **equivalente** (ver tabela acima) |
| C08 | `inovacoes/views.py:281` | `dispatch` não recusa fora de "Disponível" | ✅ Morta |
| C09 | `inovacoes/views.py:300` | `por=` o autor da inovação | ✅ Morta |
| C10 | `inovacoes/views.py:148` | detalhe sem `select_related("unidade")` | ✅ Morta (REAP-43) |
| C11 | `inovacoes/admin.py:43-44` | `has_add_permission` → True | ✅ Morta |
| C12 | `inovacoes/admin.py:31` | admin sem `AcessoSomenteAdministradorMixin` | ✅ Morta |
| C13 | `indicadores/urls.py:8` | painel com `login_not_required` | ✅ Morta |
| C14 | `inovacoes/models.py:91` | categorias só por nome | ✅ Morta |
| C15 | `inovacoes/models.py:83` | unidades pela coluna errada | ✅ Morta |

**Sensor depth**: P0 expandida (47 mutações válidas; ≥ 5 exigidas)
**Result**: 43 mortas, 4 sobreviventes. 1 equivalente (C07) e 3 lacunas de teste (X01, Y01, Y02). FAIL ❌

M41–M46 morrem todas, e a amostra das regras centrais (RN09 com trava, fan-out da Q4, geometria, acesso, admin e consultas) continua morta: a T19 não afrouxou nada. Os sobreviventes são a mesma classe da iteração 1, em duas ACs da F6 que o Fix 1 não listou (REAP-28 e REAP-29) e num bloco compartilhado do `base.html`.

### Gate Check (iteração 2)

- **Gate command**: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q`
- **Result**: ruff "All checks passed!"; format "131 files already formatted"; makemigrations "No changes detected"; pytest **865 passed**, 0 failed, 0 skipped (17.70 s); exit 0
- **Test count**: 865, igual à iteração 1 (a T19 só endurece asserções). Antes da feature: 710; delta +155
- **Asserções enfraquecidas**: nenhuma. Toda checagem antiga continua sobre o HTML cru, e a T19 só soma a comparação com o `exibido`

### Fix Plans (iteração 2)

#### Fix 2: REAP-28, REAP-29 (e REAP-06/REAP-09) ainda afirmam "exibido" sobre o HTML cru

- **Root cause**: `inv/test_views_cabecalho.py:75` procura o link no `nav` do HTML cru; `ind/test_views_painel.py:108` procura o `h1` no cru; `_mensagens` (`inv/test_views_reaproveitar.py:45-48`) lê a região `role="status"` do cru.
- **Fix task** (só teste): aplicar o mesmo padrão da T19 com `exibido()` de `inovacoes/tests/visibilidade.py`. No teste da REAP-28, exigir `LINK_INDICADORES.search(_navegacao_principal(exibido(html)))`. No da REAP-29, exigir o `h1` em `exibido(html)`. Opcional, menor: em `_mensagens`, comparar a região do `exibido` com a do cru (REAP-06, REAP-09).
- **Done when**: X01 e Y01 morrem (Y02 também, se a parte opcional entrar); M41–M46 e V01–V13 continuam mortas; gate verde.
- **Priority**: Major para X01/Y01 (lacuna de teste em AC da F6; produção correta); Minor para Y02 (componente anterior à F6).

### Requirement Traceability Update (iteração 2)

| Requirement | Previous Status | New Status |
| ----------- | --------------- | ---------- |
| REAP-01, REAP-15, REAP-30, REAP-31, REAP-33, REAP-34, REAP-37 | ❌ Needs Fix | ✅ Verified (T19) |
| REAP-28, REAP-29 | ✅ Verified | ❌ Needs Fix (Fix 2, só teste) |
| Demais | ✅ Verified | ✅ Verified (REAP-06/REAP-09 com Y02 registrado) |

### Histórico

- **Iteração 1** (HEAD `e755a45`): FAIL ❌. 49/49 ACs com evidência; sensor 39/46, com M41, M43, M44 e M45 sobrevivendo (ocultação) e M06, M09, M17 equivalentes. Fix 1 → T19.
- **Iteração 2** (HEAD `865fe7a`): FAIL ❌. T19 mata M41–M46 e o helper passa na auditoria. Sobrevivem X01 (REAP-28) e Y01 (REAP-29), mais Y02 em bloco anterior à F6; C07 equivalente. Fix 2.

### Summary (iteração 2)

**Overall**: ❌ Not Ready (só testes a reforçar; produção correta)

**Spec-anchored check**: 47/49 ACs resistem ao sensor · 2 ACs com sobrevivente (REAP-28, REAP-29) · 6 spec-precision gaps mantidos
**Sensor**: 43/47 mortas. 1 equivalente (C07) e 3 lacunas de teste (X01, Y01, Y02)
**Gate**: 865 passed

**Next steps**: rodar o Fix 2 como task de teste e reexecutar o Verifier na iteração 3, a última antes de escalar. Se sobrar só risco de teste nessa rodada, a decisão de fechar com risco registrado é do usuário, como na F5.

---

## Iteração 3

**Date**: 2026-10-19 · **HEAD**: `4b3dae2` · **Diff range**: `eb957d2..4b3dae2` (correção `ebbc35e..4b3dae2`, T20, só teste)

### Task Completion

| Task | Status | Notes |
| ---- | ------ | ----- |
| T1–T19 | ✅ Done | Inalteradas desde a iteração 2 |
| T20 (Fix 2) | ✅ Done | `4b3dae2`. Tocou 7 arquivos de teste e somou 18 asserções sobre o `exibido(html)`, sem remover nenhuma antiga. Helpers da F1–F5 e produção ficaram intactos (conferido no diff). A contagem continua 865 |

### Varredura da T20, refeita de forma independente

Li toda asserção dos 16 arquivos de `git diff --name-only eb957d2..HEAD -- '*tests*'` que afirma que algo aparece. **Conclusão: a classe "asserção de exibido que só lê o HTML cru" está fechada na F6.** Toda asserção de presença sobre elemento da F6 passa pelo `exibido()`, direto ou por um helper que compara o recorte do exibido com o do cru: `_card` e `_tabela` (`ind/test_views_painel.py:68`, `:82`), `_graficos` (`:250`), `.vazio` (`:173`), tabelas (`:437`), seções (`:466`), cards `dl` (`:507`), `h1` (`:110`); `_reaproveitamentos` e o link de sinalizar (`inv/test_views_detalhe.py:586`, `:603`); `_mensagens` (`inv/test_views_reaproveitar.py:50`), o `<main>` da REAP-03 (`:86`), das opções (`:119`), da REAP-15 (`:149`), do 404 (`:181`), do formulário aberto (`:190`) e com erro (`:232`); o `nav` (`inv/test_views_cabecalho.py:80`); as opções do widget (`inv/test_forms_reaproveitamento.py:28`); o select, o rótulo e a mensagem (`inv/test_views_acessibilidade_alteracao.py:374-376`, `:403-405`) e a ordem de foco (`:445`); as células do admin (`inv/test_admin_reaproveitamento.py:83-85`); os cards da REAP-41 (`ind/test_desempenho_painel.py:74-76`).

Exclusões da T20, julgadas uma a uma:

| Exclusão | Se sustenta? | Por quê |
| -------- | ------------ | ------- |
| `<title>` | Sim | Fica no `<head>`. `hidden` não muda o título do documento nem o que o leitor de tela anuncia |
| Ausências (REAP-02, REAP-27, REAP-37, REAP-49, anônimo da REAP-28) | Sim | Ausência no cru implica ausência no exibido. Afirmar sobre o cru é **mais** forte |
| Atributos ARIA lidos da tag (REAP-45 sem erro, REAP-47 `role`/`aria-labelledby`) | Sim | O `svg` vem de `_graficos`, que já exige exibido == cru. `aria-invalid` ausente é uma ausência |
| Status HTTP, redirecionamentos, banco | Sim | Não há conteúdo exibido a conferir |
| Módulos sem HTML, rotas de `test_ciclo_de_vida.py`/`test_controle_autoria.py`, `test_views_sistema_design.py` | Sim | Não afirmam presença de conteúdo da F6 na tela |
| Não listado pela T20: `ind/test_desempenho_painel.py:97-98`, `:111-112` (cards crus no teste da REAP-42) | Sim | São sanidade do teste de número de consultas. A visibilidade dos cards está em `:74-76` e em `ind/test_views_painel.py:68` |

Controle: com o `exibido()` trocado por `return html` no scratch, X01, Y01 e Y02 voltam a sobreviver (865 passam). A morte vem das asserções novas, não de efeito colateral.

**Limite do modelo, que é o que sobrevive abaixo:** o `exibido()` só reconhece ocultação por atributo HTML (`hidden`, `inert`, `aria-hidden`, `<template>`, `<details>` fechado). Atributos de apresentação SVG, CSS, `disabled` e um `role` que anula a semântica nativa ficam fora dele. A varredura da T20 fechou o que prometia. Os sobreviventes são vetores novos que escolhi nesta iteração.

### Spec-Anchored Acceptance Criteria (re-derivado no HEAD `4b3dae2`)

`inv/` = `inovacoes/tests/`, `ind/` = `indicadores/tests/`. Os arquivos que a T20 não tocou (`inv/test_reaproveitamento.py`, `inv/test_agregacoes.py`, `inv/test_views_detalhe.py`, `inv/test_views_sistema_design.py`, `ind/test_graficos.py`) mantêm as linhas da iteração 2. As linhas abaixo foram relidas nos arquivos alterados.

| AC | Spec-defined outcome | `file:line` + assertion (HEAD `4b3dae2`) | Result |
| -- | -------------------- | ---------------------------------------- | ------ |
| REAP-01 | link exibido a todo autenticado em "Disponível" | `inv/test_views_detalhe.py:601`, `:603` | ✅ PASS (M41, N03, N03b mortas) |
| REAP-02 | nenhum href nem texto fora de "Disponível" | `inv/test_views_detalhe.py:617-618` | ✅ PASS |
| REAP-03 | 200, `<title>`, texto, select obrigatório rotulado, botão submit, "Cancelar" | `inv/test_views_reaproveitar.py:79`, `:83`, `:86` `_conteudo(exibido(html)) == conteudo`, `:93`, `:95`, `:103-104`, `:106` | ✅ PASS ⚠️ **L2**: N04 (`<button disabled>`) e N13 (`<fieldset disabled>`) sobrevivem |
| REAP-04 | elegíveis em ordem alfabética, sem pré-seleção, exibidas | `inv/test_forms_reaproveitamento.py:28`, `:55`, `:68-69`, `:112`; `inv/test_views_reaproveitar.py:117`, `:119` | ✅ PASS ⚠️ G1 |
| REAP-05 | um registro, conta logada, hora do servidor, 302 | `inv/test_views_reaproveitar.py:243-249`; `inv/test_reaproveitamento.py:159` | ✅ PASS (C09 morta) |
| REAP-06 | mensagem exata uma vez, exibida | `inv/test_views_reaproveitar.py:258`, `:260-261`, via `_mensagens` (`:50`) | ✅ PASS (Y02, N06 mortas) |
| REAP-07 | nenhum campo da inovação muda | `inv/test_reaproveitamento.py:280` | ✅ PASS |
| REAP-08 | GET nunca grava | `inv/test_views_reaproveitar.py:126-127` | ✅ PASS |
| REAP-09 | fora de "Disponível": nada gravado, 302, aviso uma vez | GET `inv/test_views_reaproveitar.py:138-142`; POST `:273-275` | ✅ PASS (C08, Y02 mortas) |
| REAP-10 | o modelo recusa e não grava | `inv/test_reaproveitamento.py:171-176`, `:189-191` | ✅ PASS (C01 morta) |
| REAP-11 | origem → 200, erro exato, nada gravado | `inv/test_views_reaproveitar.py:278-282`, via `_afirma_formulario_com_erro` (`:230`, `:232`) | ✅ PASS (C02 morta) |
| REAP-12 | repetida → 200, erro com o nome | `inv/test_views_reaproveitar.py:285-290`; `inv/test_reaproveitamento.py:227-231` | ✅ PASS (C04 morta) |
| REAP-13 | vazio, inexistente, não numérico → mensagem exata | `inv/test_views_reaproveitar.py:294-298`; `inv/test_forms_reaproveitamento.py:99-100` | ✅ PASS |
| REAP-14 | constraint no banco; corrida → REAP-12, sem 500 | `inv/test_reaproveitamento.py:49`, `:259-260`; `inv/test_views_reaproveitar.py:301-314` | ✅ PASS (C03b, C04 mortas) |
| REAP-15 | texto, "Voltar para a inovação", sem select nem botão, exibidos | `inv/test_views_reaproveitar.py:146-154` (`:149` exibido), cenários `:157`, `:165` | ✅ PASS (M45, N11 mortas) |
| REAP-16 | 404 com "Inovação não encontrada." | `inv/test_views_reaproveitar.py:176-181`, `:329-331` | ✅ PASS |
| REAP-17 | h2 e texto de 0, 1 e N, exibidos | `inv/test_views_detalhe.py:586`, `:641` | ✅ PASS (M42 morta) |
| REAP-18 | itens do mais antigo ao mais recente, "<unidade> — dd/mm/aaaa" | `inv/test_views_detalhe.py:656` | ✅ PASS (M46, N09 mortas) |
| REAP-19 | todo autenticado, nunca 403 | `inv/test_views_reaproveitar.py:185-190`, `:193-199`, `:355-368` | ✅ PASS |
| REAP-20 | anônimo → login com `next` | `inv/test_views_reaproveitar.py:382-383` | ✅ PASS |
| REAP-21 | sem CSRF → 403 | `inv/test_views_reaproveitar.py:392-393` | ✅ PASS |
| REAP-22 | campos do corpo ignorados | `inv/test_views_reaproveitar.py:348-352` | ✅ PASS |
| REAP-23 | excluir a inovação leva os registros dela | `inv/test_reaproveitamento.py:83`; `inv/test_views_reaproveitar.py:406-408` | ✅ PASS |
| REAP-24, REAP-25 | unidade e conta referenciadas protegidas | `inv/test_reaproveitamento.py:90-94`, `:101-105`; `inv/test_admin_reaproveitamento.py:182-185` | ✅ PASS |
| REAP-26 | admin lista e exclui só para ADMINISTRADOR | `inv/test_admin_reaproveitamento.py:77-85`, `:90-93`, `:102-103`, `:112-113`, `:122-125` | ✅ PASS ⚠️ G2, G3 (C12 morta) |
| REAP-27 | ninguém inclui nem altera | `inv/test_admin_reaproveitamento.py:131`, `:141-151`, `:158`, `:172-173` | ✅ PASS (C11 morta) |
| REAP-28 | link "Indicadores" exibido no `nav` "Principal" | `inv/test_views_cabecalho.py:77-78`, `:80` `_navegacao_principal(exibido(...)) == navegacao`; anônimo `:87-88` | ✅ PASS (X01, N07 mortas) |
| REAP-29 | 200, `<title>`, `h1` exibido | `ind/test_views_painel.py:60`, `:107`, `:110` | ✅ PASS (Y01 morta) |
| REAP-30, REAP-31 | cards com todas as inovações e todos os reaproveitamentos, exibidos | `ind/test_views_painel.py:118-119` via `_card` (`:68`), `:505`, `:507`; `ind/test_desempenho_painel.py:74-76` | ✅ PASS (M44 morta) ⚠️ **L3**: N02 (`.metricas { display: none; }` na `kira.css`) sobrevive |
| REAP-32 | tabela por categoria, ordem e zeros, exibida | `ind/test_views_painel.py:129-131` via `_tabela` (`:82`) | ✅ PASS (C14 morta) |
| REAP-33 | tabela por unidade, sem fan-out, ordem, exibida | `ind/test_views_painel.py:153-155`; `inv/test_agregacoes.py:89-90` | ✅ PASS (M43, C05, C16 mortas) |
| REAP-34 | três gráficos com título, uma barra por linha, ordem da tabela | `ind/test_views_painel.py:250`, `:281`, `:308` | ✅ PASS (N08 morta) |
| REAP-35 | proporção ao maior, 0 sem barra, tudo 0 sem barras | `ind/test_graficos.py:18`, `:25-26`, `:33`, `:42`; `ind/test_views_painel.py:324-325`, `:337`, `:348` | ✅ PASS ⚠️ G4 (C06, C07 mortas) |
| REAP-36 | nome e valor **visíveis** junto de cada barra, inclusive "0" | `ind/test_views_painel.py:308`, `:336`, `:350`, via `_graficos` (`:250`) | ✅ PASS ⚠️ G5 · **L1**: N01 (`display="none"` no `<text>` do valor) e N12 (`fill-opacity="0"` no nome) sobrevivem · **L3**: N10 (`.grafico__valor { display: none; }`) sobrevive |
| REAP-37 | vazio: cards "0", texto e link exibidos, sem tabela nem gráfico | `ind/test_views_painel.py:169-178`, `:186-189` | ✅ PASS |
| REAP-38 | números do banco a cada requisição | `ind/test_views_painel.py:197-214` | ✅ PASS |
| REAP-39 | o painel não altera nada | `ind/test_views_painel.py:227` | ✅ PASS |
| REAP-40 | anônimo → login | `ind/test_views_painel.py:234` | ✅ PASS (C13 morta) |
| REAP-41 | demonstração + 200 em até 2 s | `ind/test_desempenho_painel.py:63-64`, `:77` | ✅ PASS |
| REAP-42 | consultas do painel fixas | `ind/test_desempenho_painel.py:113` | ✅ PASS (C15 morta) |
| REAP-43 | consultas do detalhe fixas | `inv/test_views_detalhe.py:667` | ✅ PASS (C10 morta) |
| REAP-44 | label ligado por `for`/`id`, exibido | `inv/test_views_acessibilidade_alteracao.py:368-376` | ✅ PASS |
| REAP-45 | `aria-invalid="true"` e `aria-describedby` → mensagem | `inv/test_views_acessibilidade_alteracao.py:399-405`, sem erro `:408` | ✅ PASS |
| REAP-46 | `caption`, `th scope="col"`, primeira célula `th scope="row"` | `ind/test_views_painel.py:437-454` | ✅ PASS ⚠️ **L4**: N05 (`<table role="presentation">`) sobrevive |
| REAP-47 | `role="img"`, nome = título, tabela na seção | `ind/test_views_painel.py:290-291`, `:466-492` | ✅ PASS |
| REAP-48 | componentes da `kira.css`, contrastes | `inv/test_views_sistema_design.py:653`, `:631`, `:405-409` | ✅ PASS |
| REAP-49 | 500 do projeto, nada gravado, sem detalhes | `inv/test_views_reaproveitar.py:429-436`; `ind/test_views_painel.py:549-561` | ✅ PASS |

**Status**: 49/49 ACs com evidência que afirma o valor da spec · ❌ 4 ACs com sobrevivente de um vetor de ocultação novo (REAP-03 L2, REAP-30/31 L3, REAP-36 L1+L3, REAP-46 L4) · ⚠️ 6 spec-precision gaps (mantidos)

### Spec-Precision Gaps e equivalentes (reavaliados)

| # | Decisão | Justificativa |
| - | ------- | ------------- |
| G1 (REAP-04) | Mantido | spec igual; `inv/test_forms_reaproveitamento.py:69` |
| G2 (REAP-26) | Mantido | `inv/test_admin_reaproveitamento.py:122-125` |
| G3 (destino após excluir no admin) | Mantido | só `status_code == 302` (`inv/test_admin_reaproveitamento.py:92`) |
| G4 (REAP-35) | Mantido | `ind/test_views_painel.py:324-325` |
| G5 (REAP-36, truncamento em 70) | Mantido | `ind/test_views_painel.py:354-368` |
| G6 (T18, "ordem de leitura") | Mantido | nenhuma AC nem Done-when cita |
| M06, M09, M17, C07 | Equivalentes, mantidos | `inovacoes/models.py`, `inovacoes/views.py` e `indicadores/graficos.py` sem mudança desde a iteração 1 |
| L2 e L4 diante da letra da spec | Lacuna de teste, não gap da spec | Um botão `disabled` continua "a submit button" e uma tabela com `role="presentation"` continua tendo `caption` e `scope`, mas a REAP-03 existe para o usuário enviar o formulário e a REAP-46 para o leitor de tela ler a tabela (RNF09). As duas mutações quebram o propósito declarado da AC |

### Discrimination Sensor (iteração 3)

Worktree temporário (`git worktree add --detach <scratchpad>/vwt3 HEAD`, `.env` copiado). Cada mutação rodou a suíte inteira (`pytest -q -x -p no:cacheprovider`) pelo `.venv` da raiz em caminho absoluto, foi desfeita com `git checkout` no worktree e teve o `git status --porcelain` do worktree conferido limpo. No fim, `git worktree remove --force` e `git worktree prune`. `git worktree list` mostra só a árvore principal, e o `git status --porcelain` da árvore real ficou vazio antes e depois, igual à linha de base. Profundidade: **P0 expandida**, 40 mutações válidas (uma âncora ambígua, C03, refeita como C03b), mais 3 rodadas de controle com o helper neutralizado.

| Mutação | File | Descrição | Resultado |
| ------- | ---- | --------- | --------- |
| X01 | `templates/base.html:23` | link "Indicadores" num `<span hidden>` | ✅ Morta (`inv/test_views_cabecalho.py:80`) |
| Y01 | `indicadores/templates/indicadores/painel.html:6` | `<div hidden><h1>…</h1></div>` | ✅ Morta (`ind/test_views_painel.py:110`) |
| Y02 | `templates/base.html:41` | `<ul class="mensagens" hidden>` | ✅ Morta (`inv/test_views_reaproveitar.py:50`) |
| M41 | `inovacao_detail.html:86` | `<p class="acoes" hidden>` no link de sinalizar | ✅ Morta (`:603`) |
| M42 | `inovacao_detail.html:89` | seção "Reaproveitamentos" com `hidden` | ✅ Morta |
| M43 | `painel.html:41` | seção "Por unidade" com `hidden` | ✅ Morta (`ind/test_views_painel.py:82`) |
| M44 | `painel.html:9` | `<dl class="metricas" hidden>` | ✅ Morta |
| M45 | `inovacao_reaproveitar.html:11` | `<p hidden>Todas as outras…` | ✅ Morta (`:149`) |
| M46 | `inovacao_detail.html:98` | `<ol class="reaproveitamentos" hidden>` | ✅ Morta (`:586`) |
| N03 | `inovacao_detail.html:86` | `tabindex="-1"` antes do `href` do link de sinalizar | ✅ Morta, pelo regex estrito de `_links` (`inv/test_views_detalhe.py:199`) |
| N03b | `inovacao_detail.html:86` | `tabindex="-1"` depois do `href` | ✅ Morta, idem (o regex só aceita `aria-describedby` depois do `href`) |
| N06 | `templates/base.html:41` | `<ul class="mensagens" aria-hidden="true">` | ✅ Morta |
| N07 | `templates/base.html:19` | `<nav aria-label="Principal" inert>` | ✅ Morta (incidental: o `index` cru de `_navegacao_principal`, teste da F1) |
| N08 | `grafico.html:5` | `<figcaption hidden>` (título do gráfico) | ✅ Morta |
| N09 | `inovacao_detail.html:100` | `<time hidden>` nos itens | ✅ Morta |
| N11 | `inovacao_reaproveitar.html:12` | `inert` no "Voltar para a inovação" | ✅ Morta |
| N15 | `inovacao_reaproveitar.html:24` | `tabindex="-1"` no "Cancelar" | ✅ Morta (`inv/test_views_acessibilidade_alteracao.py:443`) |
| **N01** | `indicadores/templates/indicadores/grafico.html:12` | `<text display="none" class="grafico__valor">` | ❌ **Sobrevive** → L1 (REAP-36) |
| **N12** | `grafico.html:10` | `<text fill-opacity="0" class="grafico__nome">` | ❌ **Sobrevive** → L1 (REAP-36) |
| **N04** | `inovacao_reaproveitar.html:22` | `<button type="submit" disabled>` | ❌ **Sobrevive** → L2 (REAP-03) |
| **N13** | `inovacao_reaproveitar.html:20` | `<fieldset disabled>` em volta do select e do botão | ❌ **Sobrevive** → L2 (REAP-03, REAP-44) |
| **N02** | `templates/kira.css:542` | `.metricas { display: none; }` | ❌ **Sobrevive** → L3 (REAP-30, REAP-31) |
| **N10** | `templates/kira.css:563` | `.grafico__valor { …; display: none; }` | ❌ **Sobrevive** → L3 (REAP-36) |
| **N05** | `painel.html:20` | `<table role="presentation">` na tabela por categoria | ❌ **Sobrevive** → L4 (REAP-46) |
| C01 | `inovacoes/models.py:317` | guarda de status da RN09 removida | ✅ Morta |
| C02 | `inovacoes/models.py:322` | guarda da unidade de origem removida | ✅ Morta |
| C03 | — | âncora ambígua (`avancar_status` também tem `select_for_update`) | inválida, refeita como C03b |
| C03b | `inovacoes/models.py:313` | `select_for_update()` removido do `registrar_reaproveitamento` | ✅ Morta (`inv/test_reaproveitamento.py:260`) |
| C04 | `inovacoes/models.py:333` | teste do nome da constraint invertido | ✅ Morta |
| C05 | `inovacoes/models.py:81-82` | Q4 com duas `Count()` (fan-out) | ✅ Morta (`ind/test_views_painel.py:154`) |
| C06 | `indicadores/graficos.py:46` | proporção sobre a soma | ✅ Morta (`:324`) |
| C07 | `grafico.html:11` | barra desenhada para o valor 0 | ✅ Morta (`:337`) |
| C08 | `inovacoes/views.py:281` | `dispatch` não recusa fora de "Disponível" | ✅ Morta |
| C09 | `inovacoes/views.py:300` | `por=` o autor da inovação | ✅ Morta (`inv/test_views_reaproveitar.py:248`) |
| C10 | `inovacoes/views.py:148` | detalhe sem `select_related("unidade")` | ✅ Morta (REAP-43) |
| C11 | `inovacoes/admin.py:43-44` | `has_add_permission` → True | ✅ Morta |
| C12 | `inovacoes/admin.py:31` | admin sem `AcessoSomenteAdministradorMixin` | ✅ Morta |
| C13 | `indicadores/urls.py:8` | painel com `login_not_required` | ✅ Morta (`contas/tests/test_controle_acesso.py`) |
| C14 | `inovacoes/models.py:91` | categorias só por nome | ✅ Morta |
| C15 | `painel.html:60` | `unidade.reaproveitamentos.count` por linha (N+1) | ✅ Morta (REAP-42, `ind/test_desempenho_painel.py:113`) |
| C16 | `inovacoes/models.py:83` | unidades ordenadas por reaproveitamentos feitos | ✅ Morta |

Controle do helper: `exibido()` trocado por `return html` + X01, + Y01, + Y02 → as três **sobrevivem** (865 passam). A morte delas vem do `exibido`.

**Sensor depth**: P0 expandida (40 mutações válidas; ≥ 5 exigidas)
**Result**: 33 mortas, 7 sobreviventes, nenhuma equivalente. As 7 são lacunas de teste em 4 vetores (L1–L4). FAIL ❌

### Gate Check (iteração 3)

- **Gate command**: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q`
- **Result**: ruff "All checks passed!"; format "131 files already formatted"; makemigrations "No changes detected"; pytest **865 passed**, 0 failed, 0 skipped (17.73 s); exit 0
- **Test count**: 865, igual às iterações 1 e 2 (a T20 só endurece asserções). Antes da feature: 710; delta +155
- **Asserções enfraquecidas**: nenhuma. O diff da T20 só soma linhas de asserção; as que mudaram de forma (`_mensagens`, `_opcoes`, `_pares_dos_cards`) mantêm a checagem crua e somam a exibida

### Lacunas ranqueadas (para o usuário decidir: Fix 3 ou risco registrado)

| # | Lacuna | AC | `file:line` | Correção (só teste) | Severidade |
| - | ------ | -- | ----------- | ------------------- | ---------- |
| L2 | Botão ou `fieldset` `disabled` passa: o formulário aparece mas não envia, e os POSTs dos testes são forjados pelo `client` | REAP-03 (REAP-44) | produção `inovacoes/templates/inovacoes/inovacao_reaproveitar.html:18-22`; teste `inv/test_views_reaproveitar.py:86`, `:103-104`; `inv/test_views_acessibilidade_alteracao.py:445` | No teste da REAP-03 e na ordem de foco, exigir que o `<select>` e o `<button type="submit">` não tenham `disabled` e não fiquem dentro de um `<fieldset disabled>` | Major (o caminho de tela do RF11 quebra com a suíte verde) |
| L1 | Atributo de apresentação SVG (`display="none"`, `visibility="hidden"`, `opacity`/`fill-opacity="0"`) esconde o nome ou o valor da barra | REAP-36 | produção `indicadores/templates/indicadores/grafico.html:10-12`; teste `ind/test_views_painel.py:250` (`_graficos`) | Em `_graficos`, aceitar só os atributos esperados: `<text>` com `class`, `x`, `y`; `<rect>` com `class`, `x`, `y`, `width`, `height` (L-025) | Major (a AC existe para nenhum valor depender só da barra) |
| L3 | Ocultação por CSS na `kira.css` (`display: none` em `.metricas`, `.grafico__valor`) | REAP-30, REAP-31, REAP-36 | produção `templates/kira.css:536-565`; teste `inv/test_views_sistema_design.py` (sem checagem de ocultação) | Na suíte de DS, recusar `display: none`, `visibility: hidden`, `opacity: 0` e `clip` nas regras que selecionam `.metrica*`, `.metricas`, `.grafico*`, `.reaproveitamentos` e `.tabela` | Minor (exige editar a folha central de propósito) |
| L4 | `role="presentation"` (ou `none`) na `<table>` anula a semântica para o leitor de tela | REAP-46 | produção `indicadores/templates/indicadores/painel.html:20`, `:46`; teste `ind/test_views_painel.py:437-454` | Exigir `role` ausente (ou `"table"`) em cada `<table>` e nos `th`/`td` | Minor |

### L-040 nesta iteração

A T20 aplicou a L-040 e varreu toda a feature. A minha varredura independente confirma que a classe "asserção crua" fechou: nenhum sobrevivente desta iteração vem de uma asserção que esqueceu o `exibido()`. Pelas regras do `lessons.md`, isso **não** é registrado no `lessons.py`: um acerto não é sinal de falha, e a promoção exige outra feature, não outra iteração da mesma. A L-040 fica `candidate` (x1) até reaparecer numa feature diferente.

### Requirement Traceability Update (iteração 3)

| Requirement | Previous Status | New Status |
| ----------- | --------------- | ---------- |
| REAP-28, REAP-29 | ❌ Needs Fix | ✅ Verified (T20) |
| REAP-03, REAP-30, REAP-31, REAP-36, REAP-46 | ✅ Verified | ⚠️ Verified com lacuna de teste aberta (L1–L4), decisão do usuário |
| Demais | ✅ Verified | ✅ Verified |

### Histórico

- **Iteração 1** (HEAD `e755a45`): FAIL ❌. Sensor 39/46; M41, M43, M44 e M45 sobrevivem (ocultação). Fix 1 → T19.
- **Iteração 2** (HEAD `865fe7a`): FAIL ❌. A T19 mata M41–M46. X01, Y01 e Y02 sobrevivem (asserções cruas fora do Fix 1). Fix 2 → T20.
- **Iteração 3** (HEAD `4b3dae2`): FAIL ❌. A T20 fecha a classe crua (X01, Y01, Y02 mortas; o controle prova a origem). Sobrevivem 7 mutantes em 4 vetores novos fora do modelo do `exibido()` (L1–L4). O loop terminou: escalar ao usuário.

### Summary (iteração 3)

**Overall**: ❌ Not Ready pelo critério do sensor. Produção correta, e as lacunas são só de teste.

**Spec-anchored check**: 49/49 ACs com evidência · 4 ACs com lacuna de vetor novo (REAP-03, REAP-30/31, REAP-36, REAP-46) · 6 spec-precision gaps mantidos
**Sensor**: 33/40 mortas, 7 sobreviventes (L1–L4), nenhuma equivalente
**Gate**: 865 passed

**Next steps**: o loop de 3 iterações terminou, e a decisão é do usuário. (a) Rodar um Fix 3 só de teste com L1–L4 (L2 e L1 primeiro) e uma re-verificação fora do loop. (b) Fechar a F6 com L1–L4 registradas como risco residual, como na F5. O `validate_state.py` só passa com um veredito PASS neste arquivo.
