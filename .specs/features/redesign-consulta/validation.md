# Redesign da Consulta (R2) Validation

**Date**: 2026-11-19
**Iteration**: 1
**Spec**: `.specs/features/redesign-consulta/spec.md` (RCON-01 … RCON-50; edge cases; regras de teste da feature; testes antigos T-A a T-R)
**Diff range**: `98d79dd..459c85b` em `main` (T1 `5776a76` … T22 `459c85b`, com commits `docs(specs)` intercalados; spec em `79c51b3`, design em `295f5fd`)
**Verifier**: independent sub-agent (author ≠ verifier)

**Verdict**: FAIL ❌ (iteração 1)

As 50 ACs têm evidência `file:line` que afirma o valor da spec, o gate passa (1559 testes, +233) e nenhum teste antigo fora de T-A..T-R (mais T-P do design e o par do DS-08) mudou ou perdeu asserção. O FAIL vem de **1 mutante sobrevivente em 34** (M27): a lista pode renderizar o estado vazio ("Nenhuma inovação cadastrada ainda." e "Cadastrar a primeira inovação") junto com os resultados e a suíte inteira passa. É **lacuna de teste, não defeito de produção**: o template atual exclui o vazio quando há resultados (`inovacoes/templates/inovacoes/inovacao_list.html:44-74`). Dois spec-precision gaps (RCON-33, RCON-35) ficam sinalizados, sem reprovar.

---

## Task Completion

| Task | Status | Notes |
| ---- | ------ | ----- |
| T1–T22 | ✅ Done | `tasks.md` marca as 22 com ✅; cada uma tem commit próprio em `98d79dd..459c85b` |

---

## Testes antigos (integridade)

`git diff 98d79dd..HEAD --stat -- '*tests*'`: 15 arquivos. Os novos são `test_apresentacao.py`, `test_views_lista_cartoes.py`, `test_views_lista_filtros.py`, `test_views_lista_paginacao.py`, `test_views_lista_vazio.py` e `test_views_detalhe_v2.py`. Os antigos alterados, cada mudança conferida contra a tabela da spec (e o T-P do `design.md`, aprovado com o design):

| Arquivo | Mudança | Autorização | Perdeu asserção? |
| ------- | ------- | ----------- | ---------------- |
| `inovacoes/tests/test_views_lista.py` | `_linhas` lê os cartões exibidos (T-A); CONS-06 no `h2` (T-B); CONS-38 em `?exibicao=tabela` (T-B); CONS-34 com o texto novo e "sem lista nem tabela" (T-D); CONS-03 pontas como `span aria-disabled` (T-Q) | T-A, T-B, T-D, T-Q | Não. `_linhas` agora falha sem a lista (`:84`); CONS-03 troca "ausente" por "não é link" e ganha o `span` |
| `inovacoes/tests/test_views_busca.py` | `_titulos` falha sem a lista, salvo com o `div.vazio` exibido (T-A); textos da CONS-35 e "sem lista nem tabela" (T-D) | T-A, T-D | Não; ganhou `aria-label="Resultados" not in` e a sugestão |
| `inovacoes/tests/test_views_exclusao.py` | EDEX-37 lê os cartões (T-E) e o texto novo do vazio (T-R) | T-E, T-R | Não; passou de "não está na tabela" a "a lista é exatamente [Planilha de Compras]" |
| `inovacoes/tests/test_views_detalhe.py` | `ROTULOS`/`_pares` (T-F), `_links` pelo DOM exibido (T-G), ciclo/etapas (T-H), histórico (T-I), reaproveitamentos (T-J) | T-F a T-J | Não. CONS-12 continua conferindo os oito campos (ficha, narrativa, contato, selo); STAT-26 troca a frase de "sem mudanças" pelo item do cadastro (RCON-45) |
| `inovacoes/tests/test_views_acessibilidade_alteracao.py` | `SECOES_DO_CICLO`, Avançar no cabeçalho com `aria-describedby`, textos das etapas (T-K) | T-K | Não; STAT-34 passa a exigir também `links == []` no bloco e o link no cabeçalho |
| `inovacoes/tests/test_views_sistema_design.py` | DS-12 lista/detalhe (T-C), DS-13 (T-P), DS-16 e CONS-38 (T-B), `CADEIA_DO_COMPONENTE` e STAT-37 (T-L), `PECAS` (T-M), par `("on-brand","brand-navy")` no DS-08 | T-B, T-C, T-L, T-M, T-P, DS-08 | Não. DS-13 troca a forma do `::before` pelo SVG do selo, conferido contra o arquivo de cada status |
| `inovacoes/tests/test_folha_v2.py` | `ESCONDIDOS_PELA_SPEC` + ilustração no alto contraste e `clip` da `.visualmente-oculto` (T-N); testes novos da R2 no fim | T-N | Não |
| `nucleo/tests/test_casca.py` | `CABECALHO_DE_PAGINA` aceita selo antes do h1 e descrição/ações depois (T-O); pasta com os 4+10 ícones (T-O) | T-O | Não; o teste do ícone ganhou `"style" not in fonte` |
| `inovacoes/tests/test_consultas.py` | Só acréscimos (4 testes de RCON-13, 14, 16) | extensão prevista no `tasks.md` | Não |

Nenhum outro teste antigo mudou. Contagem 1326 → 1559 (+233).

**`_titulos` e o vazio por engano.** O `_titulos` (`inovacoes/tests/test_views_busca.py:21`) devolve `[]` só se a página não tem a lista e exibe o `div.vazio`; com a lista presente ele não confere a ausência do vazio. O mutante M27 (vazio renderizado junto com os resultados) testa exatamente esse buraco: ver o sensor.

---

## Spec-Anchored Acceptance Criteria

Caminhos abreviados: `filtros` = `inovacoes/tests/test_views_lista_filtros.py`, `cartoes` = `inovacoes/tests/test_views_lista_cartoes.py`, `paginacao` = `inovacoes/tests/test_views_lista_paginacao.py`, `vazio` = `inovacoes/tests/test_views_lista_vazio.py`, `detalhe_v2` = `inovacoes/tests/test_views_detalhe_v2.py`, `apresentacao` = `inovacoes/tests/test_apresentacao.py`, `folha` = `inovacoes/tests/test_folha_v2.py`. Toda leitura de tela abaixo passa por `exibido(html, rigoroso=True)` sobre a página inteira, salvo onde dito; a guarda da folha (L-044) aparece como `X not in CLASSES_OCULTAS`.

### P1: Busca em destaque e filtros ativos

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| RCON-01 | trilha "Inovações"; h1 "Inovações"; descrição exata; "Cadastrar inovação" → `/inovacoes/nova/` | `inovacoes/tests/test_views_lista_filtros.py:427` textos da trilha `== ["Inovações"]`; `:430-436` regex `<h1>Inovações</h1>\s*<p>{DESCRICAO}</p>\s*<a class="botao" href="/inovacoes/nova/">Cadastrar inovação</a>`; `:444` `"botao" not in CLASSES_OCULTAS` | ✅ |
| RCON-02 | `role="search"` com um form GET; primeiro controle `name="q"`/`id="id_q"`; lupa `aria-hidden` antes; ajuda e botão "Buscar" depois | `filtros:149-158` posições lupa < `id_q` < `id_q_helptext` < `<button type="submit">Buscar</button>` em ordem; `:161` primeiro controle tem `name="q"`; `:170-172` 1 SVG com `aria-hidden="true"`, ausente do exibido; `:403` `conteudo.count("<form") == 1` | ✅ |
| RCON-03 | selects Categoria/Unidade/Status depois do botão, com "Todas as categorias"/"Todas as unidades"/"Todos os status", rótulo e ajuda; sem `on*` nem script | `filtros:154-158` ordem; `:196-202` rótulo, opção vazia e ajuda exatas (parametrizado nos três); `:204`, `:210-211` sem `on*` nem `<script` na página | ✅ |
| RCON-04 | grupo "Filtros ativos:" dentro do search; ordem Busca, Categoria, Unidade, Status; textos "Busca: “{termo}”" etc. | `filtros:316-325` `role == "group"`, `na_busca`, rótulo `== "Filtros ativos:"`, textos na ordem exata com a query fora de ordem; `apresentacao:135` | ✅ |
| RCON-05 | nome acessível "Remover filtro {texto}"; `href` = query atual menos o parâmetro e o `page`, mantendo `exibicao` | `filtros:335-336` `aria-label == f"Remover filtro {texto}"` e `href` exato; `:360-363` com `page=2&exibicao=tabela`; `:132` `Etiqueta("Status: Em teste", "/inovacoes/")` | ✅ |
| RCON-06 | o grupo termina em "Limpar filtros" → `/inovacoes/` (com `exibicao=tabela` quando presente) | `filtros:338-339` último item `("link","Limpar filtros")`, `href == "/inovacoes/"`; `:364-365` `== "/inovacoes/?exibicao=tabela"` | ✅ |
| RCON-07 | sem filtro válido, nenhum grupo | `filtros:374-376` para `""`, `q` só com espaços, `exibicao=tabela`, `page=2` | ✅ |
| RCON-08 | alerta e erro do campo; sem etiqueta do inválido; "Limpar filtros" | `filtros:382-387` `role="alert"`, `id_status_error`, etiquetas `== ["Categoria: Financeiro"]`, último item Limpar; `:394-396` só o inválido: sem grupo, com Limpar | ✅ (SPEC_DEVIATION da T8 coerente com a AC: só o inválido perde a etiqueta) |

### P1: Resultados em cartões

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| RCON-09 | `role="status"` "{n} inovação encontrada"/"{n} inovações encontradas", n de todas as páginas | `cartoes:276` `== "1 inovação encontrada"`; `:283` na página 2 `== "25 inovações encontradas"` | ✅ |
| RCON-10 | `ul aria-label="Resultados"` > `li` > `article`, ordem atual; sem tabela | `cartoes:73` regex `ul[aria-label=Resultados] > li > article`; `:170` `"<table" not in`; ordem via `_linhas` (`inovacoes/tests/test_views_lista.py:84`) nos testes da CONS-02 | ✅ |
| RCON-11 | selo + "Cadastrada em {dd/mm/aaaa}"; h2 só com o link; resumo; metadados unidade, categoria, reusos | `cartoes:77-86` textos do article na ordem exata; `:90` `Cadastrada em <time>09/09/2026</time>`; `:94-98` itens da lista de metadados | ✅ |
| RCON-12 | o link do título é o único do article | `cartoes:111` `len(re.findall(r"<a\b", artigo_bruto)) == 1` (HTML bruto) | ✅ |
| RCON-13 | ≤160: texto inteiro; >160: 159 + "…" | `cartoes:127-135` `"a"*160` → igual; `"b"*161` → `"b"*159 + "…"` | ✅ |
| RCON-14 | "Nenhum reaproveitamento" / "1 reaproveitamento" / "{n} reaproveitamentos" | `cartoes:159-163` valores exatos para 0, 1, 3; `inovacoes/tests/test_consultas.py:95` contagens `{0,1,3}` | ✅ |
| RCON-15 | selo com SVG `aria-hidden`: frasco/visto/caixa-seta + rótulo | `inovacoes/tests/test_views_sistema_design.py` DS-13 (`selo.html` renderizado, `svg == arquivo do status`); `detalhe_v2:94-98` selo do cabeçalho com o SVG do arquivo e o rótulo; DS-12 da lista (cartão) | ✅ (o oráculo é o próprio arquivo SVG; o desenho do Lucide não é verificável por teste, ver Observações) |
| RCON-16 | mesmo nº de consultas para 1 e 20 cartões de unidades, categorias e contagens diferentes | `cartoes:255-258` 20 artigos, 20 contagens distintas, `len(com_vinte) == len(com_um)`; `inovacoes/tests/test_consultas.py:101` 1 consulta | ✅ |

### P1: Tabela como alternativa

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| RCON-17 | grupo "Exibição" com "Cartões" e "Tabela", ícone decorativo, atual com `aria-current="true"` | `cartoes:351-361` grupo, rótulo `== "Exibição"`, textos, SVG `aria-hidden` antes do texto; `:407-409` `_atuais == [atual]`, `== "true"` | ✅ |
| RCON-18 | Tabela = query + `exibicao=tabela`; Cartões = query sem `exibicao`; ambos mantêm q, filtros e `page` | `cartoes:388-396` hrefs exatos com os cinco parâmetros, nas duas exibições; `filtros:129-130` | ✅ |
| RCON-19 | tabela com caption "Inovações cadastradas", Título/Categoria/Unidade/Status, mesmos itens e ordem; sem cartões | `cartoes:210-227` sem `aria-label="Resultados"` nem `<article`, caption, cabeçalhos e `_linhas_da_tabela == cartoes == [...]` | ✅ |
| RCON-20 | outro valor → cartões, "Cartões" atual, sem erro | `cartoes:412-421` para `x`, `TABELA`, `cartoes`, `""`: `_atuais == ["Cartões"]`, 1 artigo, sem `role="alert"` nem tabela; `apresentacao:119` | ✅ |

### P1: Paginação numerada

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| RCON-21 | `nav aria-label="Paginação"` com Anterior, números, Próxima e "Página {a} de {t}" abaixo; só com > 1 página | `paginacao:77` janela exata; `:128` `</ul>` antes de "Página 5 de 25"; `:165-166` sem nav com uma página | ✅ |
| RCON-22 | primeira, última, atual ± 2; "…" em texto por salto; atual `aria-current="page"` sem link | `paginacao:92-94` `"Anterior 1 … 3 4 5 6 7 … 25 Próxima"`, os "…" do tipo texto, atual `["5"]`; `:117-119`; `apresentacao:237` | ✅ |
| RCON-23 | ponta texto com `aria-disabled="true"`, sem link | `paginacao:78-86` `("desabilitado","Anterior")`; `:102` `("desabilitado","Próxima")`; `:118`; `inovacoes/tests/test_views_lista.py:247-248`, `:265-266` (T-Q) | ✅ |
| RCON-24 | todo link mantém q, categoria, unidade, status e exibicao | `paginacao:153-158` `parse_qs(...) == {cinco parâmetros, page}` para os quatro links | ✅ |

### P1: Estados vazios

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| RCON-25 | ilustração `aria-hidden`; "Nenhuma inovação cadastrada ainda."; botão "Cadastrar a primeira inovação" → `/inovacoes/nova/`; sem contador, cartões, tabela, paginação | `vazio:50-60` regex da ilustração (`aria-hidden="true" focusable="false"`), textos exibidos exatos, link em `.acoes--primaria`, `_sem_resultados`; `vazio:65` fundo `--brand-blue` | ✅ |
| RCON-26 | ilustração, "Nenhuma inovação encontrada para esta busca.", "Tente outras palavras ou remova algum filtro.", "Limpar filtros" → `/inovacoes/`, etiquetas mantidas, sem resultados | `vazio:73-83` textos exibidos exatos na ordem, `href="/inovacoes/"`, etiqueta "Busca: “xyzxyz”" exibida, `_sem_resultados` | ✅ |
| RCON-27 | o tema alto esconde a ilustração | `vazio:105-107` `display: none` sob `[data-contraste=alto]`, e a classe fora de `CLASSES_OCULTAS`; `folha` `ESCONDIDOS_PELA_SPEC` (T-N) | ✅ |

### P1: Detalhe em narrativa com lateral

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| RCON-28 | trilha "Inovações › {título}", selo, h1, "Cadastrada por {autor} em {dd/mm/aaaa} · {unidade} · {categoria}" | `detalhe_v2:61-73` trilha, regex selo → h1 → linha, trilha antes; `:113-115` linha exata no fuso; `:124` com username; `:139-146` as outras telas sem nada antes do h1 | ✅ |
| RCON-29 | "Como a inovação funciona"; `ol` de três `h3` na ordem; texto completo com quebras, escapado | `detalhe_v2:167-177` h2 único e pares `(h3, texto)` exatos com `<br>`; `:243-246` escape | ✅ |
| RCON-30 | "Resultado ainda não informado." | `detalhe_v2:183-187` | ✅ |
| RCON-31 | `aside aria-label="Resumo da inovação"` depois da narrativa, antes dos reaproveitamentos; contato → ciclo → ficha | `detalhe_v2:197` `narrativa < aside < reaproveitamentos`; `:395` `contato < ciclo < ficha`; `:202` um só aside | ✅ |
| RCON-32 | "Contato responsável"; texto como digitado com quebras; nota exata | `detalhe_v2:210-215` h2, `<p class="cartao-contato__texto">{contato}</p>` com `\n`, nota exata, `white-space: pre-line` na folha | ✅ |
| RCON-33 | `dl`: Unidade de origem, Categoria, Cadastrada por, Cadastrada em ({dd/mm/aaaa}), Reaproveitamentos ({n}) | `detalhe_v2:229-236` pares exatos, `("Cadastrada em","14/09/2026")`, `("Reaproveitamentos","2")`, 5 `dt` | ⚠️ Spec-precision gap: "({dd/mm/aaaa})" e "({n})" foram lidos como "rótulo + valor no `dd`". A leitura é razoável, mas a spec não fixa a forma |
| RCON-34 | `h2` "Ciclo de vida"; `ol` das três etapas; "· concluída" / "(status atual)" com `aria-current="step"` / "· próxima etapa"; marcadores `aria-hidden` | `detalhe_v2:370-374` textos exatos nos três status, e só a atual com `aria-current="step"`; `:382-384` marcador `aria-hidden="true"` em cada etapa | ✅ |
| RCON-35 | "Reaproveitamentos ({n})"; tabela com caption oculta; Unidade, Registrado por, Data; mais antigo primeiro; n=0 → frase e sem tabela | `detalhe_v2:690-700` h2 `"Reaproveitamentos (3)"`, colunas, linhas em ordem de data; `:709-711` n=0; `:718-732` caption `.visualmente-oculto` (`clip` + 1px, sem `display:none`) | ⚠️ Spec-precision gap: a spec não dá o texto da legenda; o teste fixa "Unidades que reaproveitaram a inovação", escolha do Execute |
| RCON-36 | `CONSULTAS_DO_DETALHE = 8` | `detalhe_v2:650` e `:744` `django_assert_num_queries(CONSULTAS_DO_DETALHE)` com 0 e 3 mudanças/reaproveitamentos de pessoas diferentes | ✅ |

### P1: Ações em hierarquia

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| RCON-37 | Em teste/Validada + pode alterar: "Avançar para “{próximo}”" → status, `aria-describedby` → "O status avança um estágio por vez e não volta ao anterior." no bloco do ciclo | `detalhe_v2:477-483` + `:494` (`_esperado`, 3 status × 4 perfis); `:525-533` `aria-describedby` aponta para o `p` do bloco com o texto exato, id único | ✅ |
| RCON-38 | Disponível: "Sinalizar reaproveitamento" → reaproveitar, para todo usuário | `detalhe_v2:473-475` + `:494` nos perfis autor, administrador, terceiro e staff | ✅ |
| RCON-39 | depois da primária, "Editar" secundário; "Excluir" por último num grupo separado | `detalhe_v2:480-483` + `:494` `([..., editar], [excluir])` (o segundo é o conteúdo do `div.acoes-pagina__perigo`); `:539-542` ações depois da linha de autoria; `:548-551` divisor e 32px | ✅ |
| RCON-40 | no máximo uma primária | `detalhe_v2:498` `len([... if classe == "botao"]) <= 1` | ✅ |
| RCON-41 | quem não pode alterar: nem Avançar, nem Editar, nem Excluir; texto "Só quem cadastrou…" fora do último estágio | `detalhe_v2:512-514` (terceiro e staff, 3 status); `:415-419` texto exato por status e perfil | ✅ |
| RCON-42 | Disponível: "Último estágio do ciclo. O status avança um estágio por vez e não volta." para todos; botão "Avançar status" `aria-disabled="true"` descrito por ele, só para quem pode | `detalhe_v2:411-419`; `:430-437` botão, `aria-disabled`, sem `disabled`, `aria-describedby="ciclo-explicacao"`; ausente para os outros perfis e status | ✅ |

### P1: Histórico como linha do tempo

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| RCON-43 | 1º item: `time` {dd/mm/aaaa HH:MM} + "Cadastrada como “{status inicial}”, por {autor}"; inicial = `status_anterior` da 1ª mudança ou o atual | `detalhe_v2:599-600` nos casos sem mudança, nascida Validada e nascida Em teste: `itens[0] == ("14/09/2026 23:30", cadastro)`; `:609`; `apresentacao:282`, `:292` | ✅ |
| RCON-44 | cada mudança, mais antiga primeiro, `time` + "De “X” para “Y”, por {responsável}" | `detalhe_v2:620-624` lista exata, com a criada primeiro e a data mais recente | ✅ |
| RCON-45 | sem mudança, só o cadastro | `detalhe_v2:600` (`sem_mudancas`, `len == 1`); `inovacoes/tests/test_views_detalhe.py` STAT-26 (T-I) | ✅ |
| RCON-46 | pontos `aria-hidden="true"` | `detalhe_v2:634-637` atributos exatos dos dois pontos | ✅ |

### P1: Ordem de leitura, acessibilidade e folha

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| RCON-47 | sem `order`, sem áreas/posicionamento que antecipe um irmão posterior | `inovacoes/tests/test_folha_v2.py:1133-1146` sem `order:`, sem `grid-area(s)`, sem `-reverse`; o conjunto de `grid-row/column` da folha é exatamente o do `.detalhe` (aside na coluna 2, linhas 1–3, ao lado da narrativa) | ✅ |
| RCON-48 | sem `<style>`/`style=`; só classes da folha; todo par novo no DS-08, normal e alto | `folha:1181-1188` (lista, detalhe e parciais); `folha:1214-1218` (`CORES_R2`), `paginacao:183-185`, `folha` `test_cores_dos_componentes_da_lista_r2_estao_no_ds08_nos_dois_temas` (`.alternador`) | ✅ |
| RCON-49 | RED-11 (movimento reduzido); RED-12 (sem `fixed`, sem largura > 320px fora de `max-width`, refluxo a 200%) | `folha:1229-1241` transições só com `var(--transicao)` e o bloco `reduce`; `folha:1260-1271` sem `position: fixed`, sem largura > 320px fora de `min()`/`max-width` | ✅ (o refluxo a 200% é conferido por proxy estático, como na R1; a conferência real fica para o UAT) |
| RCON-50 | < 720px: detalhe e cartões em uma coluna | `folha:1282-1284` `.cartoes` com `minmax(0, 1fr)` e `.detalhe` sem colunas fora da `@media (min-width: 45rem)`; `detalhe_v2:263-278` | ✅ |

**Status**: 50/50 ACs com evidência `file:line` que afirma o valor da spec. Dois spec-precision gaps sinalizados (RCON-33, RCON-35), ambos interpretações razoáveis do Execute e conferidas na tela.

---

## Edge Cases

- [x] `page` além do fim: `paginacao:106-111` marca a 25 como atual e "Página 25 de 25". `page` inválido (`abc`, `0`): `inovacoes/tests/test_views_lista.py:276-280` só confere "Página 1 de 2". O `aria-current` vem do mesmo `page_obj.number`, mas não é afirmado nesse caso (cobertura parcial, menor).
- [x] Filtro válido sem resultado mantém a etiqueta: `vazio:86-93`.
- [~] Título de 150 caracteres sem rolagem horizontal: só o proxy estático da RCON-49 (`folha:1260-1271`); nenhum teste renderiza um título de 150 caracteres, e a folha não tem `overflow-wrap` no título do cartão (uma palavra longa sem espaço transbordaria). Fica para o UAT.
- [x] `contato`/`problema` com HTML saem escapados: `cartoes:138-143`, `detalhe_v2:239-246`, `filtros:410-414`.
- [x] `q` só com espaços não gera etiqueta: `filtros:368-376`, `apresentacao:191`.

---

## Discrimination Sensor

Worktree isolada em `459c85b` no scratchpad (`git worktree add --detach`, `.env` por symlink, ignorado pelo git), rodando o `.venv/bin/pytest` do projeto. Baseline na worktree: 1559 passed. Cada mutante rodou a suíte inteira com `-x`, e a worktree voltou ao `HEAD` (`git checkout -- .`) em seguida; `git status --porcelain` da worktree vazio no fim. Worktree removida com `git worktree remove --force` e `git worktree prune`. A árvore real ficou igual ao baseline (` M .specs/LESSONS.md`, ` M .specs/lessons.json`, `?? .specs/features/gestao-por-unidade/`, `?? .specs/features/link-administracao/`), mais este `validation.md`.

| # | Arquivo | Mutação | Resultado (primeiro teste que falhou) |
| - | ------- | ------- | ------------------------------------- |
| M01 | `inovacoes/apresentacao.py:40` | `url_da_lista`: `None` deixa `x=` sobrando em vez de tirar o parâmetro | ✅ morto, `test_views_busca.py::test_qualquer_busca_ou_filtro_ativo_mostra_limpar_filtros_para_a_lista_sem_query[q]` |
| M02 | `inovacoes/apresentacao.py:45` | `url_da_lista`: sempre põe `?`, mesmo sem parâmetro | ✅ morto, idem |
| M03 | `inovacoes/apresentacao.py:71` | etiqueta mantém o `page` | ✅ morto, `test_views_lista_filtros.py::test_contexto_na_pagina_2` |
| M04 | `inovacoes/apresentacao.py:71` | etiqueta perde `exibicao` | ✅ morto, `test_views_lista_filtros.py::test_contexto_com_exibicao_tabela` |
| M05 | `inovacoes/apresentacao.py:70` | etiquetas: Status antes de Busca | ✅ morto, `test_views_lista_filtros.py::test_contexto_com_filtros_validos` |
| M06 | `inovacoes/apresentacao.py:50` | `exibicao` aceita `TABELA` (ignora caixa) | ✅ morto, `test_views_lista_cartoes.py::test_exibicao_desconhecida_mostra_cartoes_como_atual_sem_erro[TABELA]` |
| M07 | `inovacoes/apresentacao.py:50` | qualquer valor não vazio de `exibicao` vira tabela | ✅ morto, idem `[x]` |
| M08 | `inovacoes/apresentacao.py:83` | janela de páginas ±1 em vez de ±2 | ✅ morto, `test_views_lista_paginacao.py::test_janela_na_primeira_pagina` |
| M09 | `inovacoes/apresentacao.py:86` | salto de uma página sem "…" (comportamento do `get_elided_page_range`) | ✅ morto, `test_views_lista_paginacao.py::test_janela_na_pagina_5` |
| M10 | `inovacoes/apresentacao.py:103` | status inicial do histórico é sempre o atual | ✅ morto, `test_views_detalhe.py::test_historico_lista_as_mudancas_do_mais_antigo_ao_mais_recente` |
| M11 | `inovacoes/apresentacao.py:103` | status inicial é o `status_novo` da primeira mudança | ✅ morto, idem |
| M12 | `inovacoes/models.py:128` | anotação conta `id` (sempre 1) | ✅ morto, `test_consultas.py::test_listagem_conta_os_reaproveitamentos_de_cada_inovacao` |
| M13 | `inovacoes/models.py:128` + `parciais/cartao.html:14` | sem anotação; o cartão chama `.count` (N+1) | ✅ morto, idem |
| M14 | `parciais/cartao.html:10` | corta já com 160 caracteres (`>=`) | ✅ morto, `test_views_lista_cartoes.py::test_resumo_e_o_problema_cortado_em_160_caracteres[a*160]` |
| M15 | `parciais/cartao.html:10` | 160 caracteres + "…" | ✅ morto, idem `[b*161]` |
| M16 | `inovacao_detail.html:19,21` | "Avançar para" para quem não pode alterar (AD-009) | ✅ morto, `test_views_detalhe.py::test_terceiro_nao_ve_o_link_de_avancar[EM_TESTE]` |
| M17 | `inovacao_detail.html:23` | Sinalizar some para quem pode alterar em "Disponível" | ✅ morto, `test_views_detalhe.py::test_disponivel_mostra_o_link_de_sinalizar_a_todo_perfil` |
| M18 | `inovacao_detail.html:28-30` | Excluir fora do grupo separado | ✅ morto, `test_views_detalhe_v2.py::test_acoes_do_cabecalho_por_status_e_perfil[EM_TESTE-autor]` |
| M19 | `inovacao_detail.html:27` | Editar com a classe da primária (duas primárias) | ✅ morto, idem |
| M20 | `inovacao_list.html:56` | "Tabela" nunca recebe `aria-current` | ✅ morto, `test_views_lista_cartoes.py::test_so_a_exibicao_atual_tem_aria_current[?exibicao=tabela-Tabela]` |
| M21 | `inovacao_detail.html:79` | `aria-current="step"` também nas etapas concluídas | ✅ morto, `test_views_detalhe_v2.py::test_etapas_dizem_a_situacao_em_texto_e_so_a_atual_tem_aria_current[VALIDADA]` |
| M22 | `templates/kira.css` (`.paginacao [aria-disabled=true]`) | `display: none` nas pontas desabilitadas | ✅ morto, `test_folha_v2.py::test_folha_so_esconde_o_que_a_spec_manda` |
| M23 | `templates/kira.css` | regra nova `.cartao-inovacao__resumo { visibility: hidden }` | ✅ morto, `test_folha_v2.py::test_cartao_de_inovacao_em_hover_ganha_borda_azul` (primeiro com `-x`) |
| M24 | `templates/kira.css` | `.detalhe > aside { order: -1 }` | ✅ morto, `test_folha_v2.py::test_folha_nao_reordena_nada_por_css` |
| M25 | `templates/kira.css` (`@media (min-width: 45rem)`) | histórico posto na linha 1 da grade (antes da narrativa) | ✅ morto, idem |
| M26 | `inovacoes/views.py:160` | reaproveitamentos sem `select_related("registrado_por")` (consulta extra) | ✅ morto, `test_views_detalhe.py::test_reaproveitamentos_nao_crescem_em_consultas[1]` |
| M27 | `inovacao_list.html:70` | estado vazio renderizado junto com os resultados | ❌ **sobreviveu** (1559 passed) |
| M28 | `parciais/paginacao.html:9` | links de página só com `?page=` (perdem filtros e exibição) | ✅ morto, `test_views_lista_paginacao.py::test_links_mantem_busca_filtros_e_exibicao` |
| M29 | `inovacao_list.html:49` | contador conta só a página | ✅ morto, `test_desempenho.py::test_listagem_com_500_inovacoes_responde_em_menos_de_2_segundos` |
| M30 | `inovacoes/views.py:382` | form inválido zera as etiquetas válidas | ✅ morto, `test_views_lista_filtros.py::test_contexto_com_form_invalido_mantem_so_as_etiquetas_validas` |
| M31 | `parciais/cartao.html:12` | unidade vira link (dois links no `article`) | ✅ morto, `test_views_lista_cartoes.py::test_titulo_e_h2_com_so_o_link_para_o_detalhe` |
| M32 | `inovacao_detail.html:88` | botão "Avançar status" para quem não pode alterar | ✅ morto, `test_views_detalhe.py::test_ultimo_estagio_explica_e_ninguem_ve_o_link[terceiro]` |
| M33 | `parciais/selo.html:2` | "Validada" com o ícone do frasco | ✅ morto, `test_views_detalhe_v2.py::test_selo_do_cabecalho_tem_o_icone_do_status_e_o_rotulo[VALIDADA]` |
| M34 | `inovacoes/views.py:384` | "Limpar filtros" perde `exibicao=tabela` | ✅ morto, `test_views_lista_filtros.py::test_contexto_com_exibicao_tabela` |

**Sensor depth**: expandido (34 mutações de comportamento cobrindo `url_da_lista`/`etiquetas`, `exibicao`, janela de páginas, `itens_do_historico`, anotação de contagem, resumo 159/160, ação primária por status e perfil, Excluir separado, `aria-current` do alternador e das etapas, ocultação por CSS, ordem de leitura, consultas do detalhe).
**Result**: 33/34 mortos. **FAIL ❌** (M27).

**Por que M27 sobrevive.** Nenhum teste com resultados afirma a ausência do estado vazio. `_titulos` (`inovacoes/tests/test_views_busca.py:21`) só olha o vazio quando a lista falta; `_linhas` (`inovacoes/tests/test_views_lista.py:84`) só exige a lista; `_sem_resultados` (`inovacoes/tests/test_views_lista_vazio.py:36`) é a direção oposta (vazio sem resultados). A página com resultados mostraria "Nenhuma inovação cadastrada ainda." e "Cadastrar a primeira inovação" abaixo dos cartões e nada falha. As RCON-25 e RCON-26 são cláusulas "WHEN nada existe/casa"; a exclusão mútua (com resultados, sem o vazio) é a contraparte que o mutante explora.

---

## Gate Check

- **Gate command**: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q` (PostgreSQL 16 na porta 5433)
- **Result**: `All checks passed!`; `175 files already formatted`; `No changes detected`; **1559 passed**, 0 failed, 0 skipped (37,3 s). Exit 0.
- **Test count before feature**: 1326
- **Test count after feature**: 1559
- **Delta**: +233
- **Skipped tests**: nenhum
- **Failures**: nenhuma

---

## Code Quality

| Principle | Status |
| --------- | ------ |
| Minimum code | ✅ `apresentacao.py` com quatro funções puras; o template só itera |
| Surgical changes | ✅ regras `.ficha`, `.ciclo`, `.historico`, `.reaproveitamentos`, `.meta` e `.selo::before` saíram junto com o HTML que as usava |
| No scope creep | ✅ sem mudança de regra de negócio, model de dados ou migration (`makemigrations --check` limpo); `para_listagem` só ganhou `problema` e a anotação |
| Matches patterns | ✅ mesmo padrão do `busca.py` (AD-008) |
| Spec-anchored outcome check | ✅ (2 spec-precision gaps sinalizados) |
| Per-layer Coverage Expectation met | ✅ unit (apresentação, folha), integration (queryset), e2e (lista e detalhe, quatro perfis nas ações) |
| Every test maps to a spec requirement | ✅ cada teste novo cita RCON, edge case ou o T-x que altera |
| Documented guidelines followed | ✅ regras de teste da feature (L-003, L-005, L-028, L-030, L-044) |

**Desvios registrados (`SPEC_DEVIATION`)**, todos conferidos:

1. `inovacoes/apresentacao.py:76`: janela de páginas calculada em Python, não com `get_elided_page_range`. O método do Django dá `1 2 3 4 5 6 7 … 25` na página 5; a RCON-22 pede `1 … 3 4 5 6 7 … 25`. O desvio é do design, não da spec: a saída cumpre a AC (`paginacao:92`).
2. `inovacoes/views.py:373`: etiquetas montadas também com o form inválido. A RCON-08 só proíbe a etiqueta do parâmetro inválido; o comportamento bate com a AC (`filtros:84-92`, `:379-387`).
3. Ilustração com acento `--info-tint`, não `--brand-blue-light` (design, Lote 2). Escolha de cor do design, fora de AC.

**Observações (não reprovam):**

- Os 10 ícones Lucide foram desenhados de memória. Os testes conferem que cada SVG é decorativo, sem `style`, `id` ou `title` (`nucleo/tests/test_casca.py`), e que o selo usa o arquivo certo, mas não podem conferir que o desenho é o do Lucide. Fica para o UAT.
- `.vazio__acento { fill: var(--info-tint) }` não entra em nenhuma conferência de par de cor (é preenchimento decorativo, não texto nem limite).
- Risco residual herdado da R1 (RED-16, RED-22) está fora do escopo desta feature.

---

## Requirement Traceability Update

O status das ACs fica em `Implementing` até o fix de M27 e a reverificação. Depois do PASS, RCON-01 … RCON-50 passam a `Verified`. Nenhuma AC tem defeito de produção.

---

## Summary

**Overall**: ❌ Not Ready (iteração 1): uma lacuna de teste, nenhum defeito de produção.

**Spec-anchored check**: 50/50 ACs com evidência e valor da spec | 2 spec-precision gaps (RCON-33, RCON-35)
**Sensor**: 33/34 mutações mortas; M27 sobreviveu
**Gate**: 1559 passed, 0 failed, 0 skipped; ruff, format e makemigrations limpos

**What works**: etiquetas e URLs da lista (todas as mutações de `url_da_lista`, `etiquetas`, `exibicao` morrem); janela de páginas; cartões (resumo 159/160, contagem, link único, N+1); alternador e `aria-current`; ações por status e perfil, com `USUARIO` `is_staff` (L-003); etapas, linha do tempo e tabela de reaproveitamentos; guardas da folha (ocultação, `order`, posicionamento na grade); consultas do detalhe.

**Ranked gaps**:

1. **M27, exclusão mútua lista × vazio sem teste** (RCON-10, RCON-25, RCON-26): `inovacoes/templates/inovacoes/inovacao_list.html:70`, nenhum teste. Severidade: Minor (lacuna de teste).
   - **Fix task**: em `inovacoes/tests/test_views_lista_cartoes.py` (ou no `_linhas` compartilhado), afirmar que, com resultados, a tela exibida não tem `div.vazio`, "Nenhuma inovação cadastrada ainda.", "Nenhuma inovação encontrada para esta busca." nem a ilustração, nas duas exibições (cartões e tabela). Done when: M27 reinjetado morre.
2. **Spec-precision RCON-33**: "Cadastrada em ({dd/mm/aaaa})" e "Reaproveitamentos ({n})" lidos como rótulo + valor no `dd`. Fix: emendar a spec para dizer isso. Sem mudança de código.
3. **Spec-precision RCON-35**: texto da legenda oculta não definido; o teste fixa "Unidades que reaproveitaram a inovação". Fix: emendar a spec com o texto.
4. **Edge cases parciais** (menores): `page` inválido não afirma o `aria-current` da página mostrada; o título de 150 caracteres só tem o proxy estático da folha (sem `overflow-wrap` no título do cartão). Ficam para o UAT ou um teste a mais.

**`validate_state.py redesign-consulta`**: exit 1, como esperado para um FAIL:

```
  ERROR redesign-consulta: validation.md verdict is FAIL - route the ranked gaps to fix tasks, then re-verify (feature is not done)

validate_state: 1 error(s) across [redesign-consulta]
```

**Lições registradas** (`lessons.py add`, todas candidatas): L-058 (M27, exclusão mútua de estados), L-059 (RCON-33), L-060 (RCON-35), L-061 (SPEC_DEVIATION da janela de páginas), L-062 (SPEC_DEVIATION das etiquetas com form inválido), L-063 (edge case do título longo). `.specs/LESSONS.md` e `.specs/lessons.json` ficam sem commit, junto com as mudanças locais do usuário.

**Next steps**: rodar o fix de M27 (uma task de teste) e reverificar (iteração 2 de no máximo 3).
