# Redesign da Consulta (R2) — Specification

**Status:** Aprovada pelo usuário em 2026-11-19 (assumptions confirmadas; testes antigos T-A a T-O autorizados). Escopo Large: segue para Design e Tasks.

Fonte do visual: `docs/design-spec.md` **v2 §10** (Lista de inovações; Detalhe da inovação), com os
componentes da §6 que a R1 já pôs na `kira.css` (cartão de inovação, indicador de etapas, linha
do tempo, cartão de contato, etiqueta de filtro ativo). A R2 refaz o miolo das duas telas da
consulta. Não muda regra de negócio, model nem migration.

## Testes antigos que mudam (autorização na aprovação)

A R2 muda o HTML que estes testes da F3 à F6, da sistema-de-design e da R1 fixam. Cada mudança
preserva a garantia da AC original (mesmos itens, mesma ordem, mesma ausência, mesma regra de
perfil); muda a forma de achar o elemento ou o texto, quando a §10 trocou o texto (decisão do
Discuss). Inventário feito por varredura em `contas/`, `inovacoes/`, `indicadores/`, `config/` e
`nucleo/` em 2026-11-19. Nenhum outro teste antigo pode mudar; se o Execute achar mais um, para e
pede.

| # | Teste | AC original | Muda o quê | Por quê |
| - | ----- | ----------- | ---------- | ------- |
| T-A | `test_views_lista.py:20` `_linhas` (14 testes: 7 em `test_views_lista.py`, 5 em `test_views_busca.py`, 2 em `test_desempenho.py`) e `test_views_busca.py:20` `_titulos` (4 testes) | CONS-01 a 05, 08, 19 a 21, 27, 28, 40, 47, 48 | Passam a ler os cartões do `ul aria-label="Resultados"` (título, categoria, unidade, status de cada `article`), pelo DOM parseado sobre `exibido()`. `_titulos` deixa de devolver `[]` quando não acha a lista e falha | Cartões viram a exibição padrão (RCON-10). Hoje `_titulos` devolveria `[]` e os asserts `== []` passariam sem testar nada |
| T-B | `test_views_lista.py:72` (CONS-06), `:136` (CONS-38) e `test_views_sistema_design.py:547` (DS-16) | CONS-06, CONS-38, DS-16 | CONS-06 acha o link no `h2` do cartão; CONS-38 e DS-16 abrem `/inovacoes/?exibicao=tabela` | A tabela só aparece na exibição em tabela (RCON-19) |
| T-C | `test_views_sistema_design.py:450` e `:464` | DS-12 | Lista: o selo do cartão (`span.selo.selo--x` com o rótulo depois do SVG `aria-hidden`). Detalhe: o selo acima do `h1`, não um `dd` | Selo com ícone (RCON-15) e fora da ficha (RCON-28) |
| T-D | `test_views_lista.py:121` (CONS-34) e `test_views_busca.py:332` (CONS-35), `:299` `LIMPAR` (2 testes) | CONS-32, CONS-34, CONS-35 | CONS-34 espera "Cadastrar a primeira inovação"; CONS-35 espera "Nenhuma inovação encontrada para esta busca." e a sugestão; `LIMPAR` aceita atributos de classe no link e `?exibicao=tabela` quando presente; o `"<table" not in` vira "sem lista de resultados nem tabela" | Textos da §10 (RCON-25, RCON-26) |
| T-E | `test_views_exclusao.py:167` | EDEX-37 | `html.index("<table>")` passa a procurar o `ul aria-label="Resultados"` ou a mensagem de vazio | Sem tabela por padrão |
| T-F | `test_views_detalhe.py:14` `ROTULOS`, `:32` `_pares` (4 testes: `:39`, `:60`, `:94`, `:101`) | CONS-12, CONS-14, CONS-16, CONS-42 | `_pares` lê a ficha nova (5 pares, RCON-33); Problema, Solução e Resultado passam a ser lidos pelos `h3` da narrativa; "Não informado" vira "Resultado ainda não informado."; o status é lido no selo | Ficha desmontada (RCON-29 a RCON-33) |
| T-G | `test_views_detalhe.py:193` `_links` (9 testes) | EDEX-03, EDEX-24, EDEX-25, EDEX-31, STAT-03, REAP-01 | Acha cada link pelo DOM parseado (`href` + texto exibido) em qualquer ordem de atributos, sem exigir só `aria-describedby`; STAT-03 e REAP-01 procuram no cabeçalho de página, não na seção do ciclo | Classes de botão nas ações e Avançar/Sinalizar no cabeçalho (RCON-37 a RCON-39) |
| T-H | `test_views_detalhe.py:295`–`:456` `_ciclo`, `_itens_do_ciclo`, `_explicacao`, `_botoes`, `ESCONDE` (cerca de 15 testes de STAT-01 a 05, 38 a 40) | STAT-01 a STAT-05, STAT-38 a STAT-40 | Leem o bloco "Ciclo de vida" do `aside` (`ol.etapas`); os itens passam a ser "{rótulo} · concluída" / "(status atual)" / "· próxima etapa"; `ESCONDE` ignora os marcadores `aria-hidden` decorativos (exigidos pela RCON-34) e continua exigindo que nenhum texto, link ou botão do bloco fique escondido | Indicador de etapas (RCON-34); a ação sai do bloco (RCON-37) |
| T-I | `test_views_detalhe.py:470` `_historico` (5 testes) e `:512` (STAT-26) | STAT-24 a STAT-27 | Cada item tem `time` + frase "De “X” para “Y”, por N"; o primeiro item é o cadastro; STAT-26 deixa de esperar "Nenhuma mudança de status registrada." e passa a esperar só o item do cadastro; `:556` conta mudanças + 1 | Linha do tempo com o cadastro (RCON-43 a RCON-45) |
| T-J | `test_views_detalhe.py:582` `_reaproveitamentos` (3 testes) | REAP-17, REAP-18, REAP-43 | Leem a tabela Unidade, Registrado por, Data e o título "Reaproveitamentos ({n})" em vez de `ol.reaproveitamentos` e "Reaproveitada por N unidades." | §10 (RCON-35) |
| T-K | `test_views_acessibilidade_alteracao.py:171` `SECOES_DO_CICLO`, `:241`, `:284`, `:315`, `:335` | STAT-34, STAT-37, STAT-41 | Classes `etapas` e `linha-do-tempo`; os itens com os textos novos; o link de Avançar descrito pela ajuda é procurado no cabeçalho de página, com o `aria-describedby` apontando para a explicação no bloco | RCON-34, RCON-37 |
| T-L | `test_views_sistema_design.py:576` `CADEIA_DO_COMPONENTE`, `:622`, `:673` | STAT-37 | Os seletores `.ciclo`, `.historico`, `.reaproveitamentos` viram `.etapas`, `.linha-do-tempo` e a tabela de reaproveitamentos; as regras antigas saem da folha | Componentes da R1 substituem os antigos (sem código morto) |
| T-M | `test_views_sistema_design.py:395` `PECAS` e `:412` (DS-01) | DS-01 | `PECAS` ganha as parciais da R2 (cartão, selo, paginação, etiquetas, ilustração e ícones novos); a contagem de telas segue 13 | Peças novas, sem estilo próprio |
| T-N | `test_folha_v2.py:943` `ESCONDIDOS_PELA_SPEC` e `:1011` | RED-16, RED-22, RED-32 | Acrescenta a ilustração do vazio no alto contraste (RCON-27) e o `caption` visualmente oculto da tabela de reaproveitamentos (RCON-35) | Ocultações novas que a spec manda |
| T-O | `nucleo/tests/test_casca.py:458` `CABECALHO_DE_PAGINA` (`:470`) e `:123` | RED-29, RED-31, RED-16, RED-23 | O cabeçalho do detalhe aceita o selo antes do `h1` e as ações depois, mantendo o `h1` único como primeiro título do `main`; a pasta de ícones deixa de ter exatamente 4 arquivos e passa a exigir os 4 da R1 mais os da R2 | RCON-28, RCON-39, RCON-15 |
| T-Q | `inovacoes/tests/test_views_lista.py:235` e `:246` | CONS-03 | Em vez de `"Anterior"/"Próxima" not in nav`, exigem que a ponta não seja link (texto com `aria-disabled="true"`, RCON-23); o resto do teste fica igual | Achado no Execute (T13), autorizado pelo usuário em 2026-11-19 |
| T-R | `inovacoes/tests/test_views_exclusao.py:172` | EDEX-37 | Espera o texto novo do vazio sem resultado ("Nenhuma inovação encontrada para esta busca.", RCON-26) | Achado no Execute (T14), autorizado pelo usuário em 2026-11-19 |

**Não mudam** (conferido): "Cadastrada por {autor} em {data}" como substring (CONS-13, EDEX-18,
ACER-11: a linha do cabeçalho começa assim, RCON-28); os h2 "Ciclo de vida" e "Histórico de status"
(STAT-05 em `test_views_status.py:330`); um só form GET com o botão "Buscar" e nenhum `on*` nem
`<script>` (CONS-31, CONS-37: etiquetas, alternador e paginação são links); o submit "Buscar" sem
classe dentro do `main` (DS-14); `id="id_q"` com `aria-invalid` e `id_q_error` (CONS-43, RED-14:
o campo continua renderizado pelo Django); o primeiro `role="status"` da página segue o do base
(EDEX); todo `a` tem `href` e nenhum controle ganha `role` (CONS-41: o atual do alternador continua
link com `href`; a página atual da paginação é texto sem `role`); `CONSULTAS_DO_DETALHE = 8`; CONS-46
a 48 em número de consultas; o link "Voltar para a lista de inovações" (CONS-18).

## Problem Statement

A lista mostra os resultados numa tabela de quatro colunas, sem resumo do problema nem a contagem
de reaproveitamentos, e os filtros aplicados só aparecem dentro dos selects. O detalhe empilha
todos os campos numa `dl` única, com o contato no meio da ficha e as ações sem hierarquia
(Editar e Excluir lado a lado; "Avançar" e "Sinalizar" perdidos no corpo da página). Quem procura
uma solução precisa ler cada linha para decidir se vale abrir, e quem abre não acha de cara o
problema, a solução e a quem perguntar. A R1 entregou a casca e os componentes; a R2 os usa nas
duas telas que mais se consultam.

## Goals

- [ ] A lista mostra, sem abrir nenhuma inovação, o status, o resumo do problema, a unidade, a categoria e quantas unidades já reaproveitaram cada resultado.
- [ ] Os filtros aplicados aparecem como etiquetas, cada uma removível por um link, sem JavaScript.
- [ ] O detalhe lê como uma história (Problema → Solução → Resultado), com o contato em destaque e uma só ação primária.
- [ ] RNF08 preservado: a lista com 500 inovações responde em < 2 s, o número de consultas da lista não cresce com as linhas e o do detalhe segue `CONSULTAS_DO_DETALHE = 8`.
- [ ] Só os testes antigos listados acima mudam; suíte e build gate verdes.

## Code Reuse Analysis

| Item | Onde | Reuso |
| ---- | ---- | ----- |
| Componentes da v2 | `templates/kira.css`: `.cartao-inovacao`, `.etapas`/`.etapa--*`, `.linha-do-tempo`, `.cartao-contato`, `.filtros-ativos`/`.etiqueta-filtro`, `.selo--*`, `.botao--secundario`, `.botao--perigo`, `.vazio` (R1) | Consumidos como estão; a R2 só acrescenta o que a R1 não tem (alternador, paginação numerada, narrativa em passos, grade de duas colunas, busca em destaque, ilustração do vazio) |
| Cabeçalho de página | `templates/base.html` blocos `trilha`, `titulo`, `descricao`, `acao_principal` (R1, RED-29 a RED-31) | Lista preenche descrição e ação; detalhe preenche ações em hierarquia e o selo acima do h1 |
| Ícones | `templates/icones/*.svg` (Lucide, ISC) | Ganha os ícones de status, lupa, remoção, cartões/tabela, unidade, categoria, reaproveitamento e a ilustração do vazio |
| Busca e filtros | `BuscaForm`, `Inovacao.objects.para_listagem().buscar().filtrar()` (F3, AD-008) | Sem mudança de regra; `para_listagem` ganha a contagem de reaproveitamentos na mesma consulta |
| Regra de alteração | `Inovacao.pode_ser_alterada_por`, contexto `pode_alterar` (AD-009) | Decide Avançar, Editar e Excluir no cabeçalho |
| Transição | `Inovacao.proximo_status`, `pode_ser_reaproveitada` (AD-011, AD-012) | Decide a ação primária |
| Visibilidade nos testes | `inovacoes/tests/visibilidade.py` `exibido()` (L-028, L-030, L-044) | Toda AC de "exibido" |

## Out of Scope

| Feature | Reason |
| ------- | ------ |
| Formulários de cadastro e edição, login, painel | Telas das features seguintes do redesign |
| Esqueleto de carregamento dos cartões | A lista é renderizada no servidor; não há estado "carregando" sem JavaScript |
| Ordenação escolhida pelo usuário, destaque do termo buscado | Deferred Ideas da F3; não estão na §10 |
| Colunas novas na tabela (Cadastrada em, Reaproveitamentos) | Pedido do usuário: a alternativa mantém a tabela atual |
| Mudança de regra de busca, filtro, permissão, transição ou reaproveitamento | A R2 é visual; AD-008, AD-009, AD-011, AD-012 intactas |

---

## Assumptions & Open Questions

Decisões do Discuss de 2026-11-19 (ver `context.md`) e defaults do agente.

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --------------------- | -------------- | --------- | ---------- |
| Lugar do "Avançar" | No cabeçalho de página, como ação primária; a explicação continua ligada ao link por `aria-describedby` e fica na lateral, sob as etapas | §10; uma primária por tela (H8) | y |
| Textos | Os da §10 substituem os atuais onde diferem; cada teste que muda está na tabela acima | A R2 é o redesign destas telas | y |
| Estado vazio | Duas variantes da §10: acervo vazio com o botão "Cadastrar a primeira inovação"; sem resultado com sugestão e "Limpar filtros" | Decisão do usuário | y |
| Paginação | Entra na R2: números de página, "Anterior"/"Próxima" como texto desabilitado nas pontas | Decisão do usuário | y |
| Tabela alternativa | A tabela atual, sem coluna nova (legenda "Inovações cadastradas"; Título, Categoria, Unidade, Status); o selo ganha o ícone como em toda a tela | Pedido do usuário ("mantendo a tabela atual") diverge das seis colunas da §10 | y |
| Parâmetro `exibicao` | Só o valor `tabela` muda a exibição; ausente ou qualquer outro valor mostra cartões, sem erro; fica fora do `BuscaForm` e não conta como filtro ativo | Um valor inválido de apresentação não deve esconder resultados (CONS-30 vale para filtros) | y |
| Janela de páginas | Primeira, última e a atual ± 2; cada salto vira um "…" em texto | Com 500 inovações são 25 páginas; todas numa linha não cabem a 320px | y |
| Resumo do cartão | Até 160 caracteres contando o "…" (159 + "…" quando passa de 160) | §6 ("~160 caracteres com …"). Emendado no Execute: o `truncatechars` em pt-BR põe um espaço antes do "…" e entrega 158 | y |
| Rótulos das etiquetas | "Busca: “{termo}”", "Categoria: {nome}", "Unidade: {nome}", "Status: {rótulo}"; só para valores válidos; o link de remoção tira aquele parâmetro e o `page` e mantém os outros, inclusive `exibicao` | §6 dá o formato "Categoria: Financeiro"; o termo vai entre aspas para não se confundir com o rótulo | y |
| Ilustração do vazio | SVG embutido com `aria-hidden="true"` e `focusable="false"`, não um `<img alt="">` | Efeito igual para o leitor de tela; segue o padrão dos ícones da R1 e some no alto contraste pela folha (§7) | y |
| Ordem da lateral | No código e na tela: Contato responsável → Ciclo de vida → Ficha, nas duas larguras; sem a propriedade CSS `order` | A §10 pede o ciclo primeiro na tela larga e o contato primeiro na estreita; as duas não convivem com uma ordem única de leitura (restrição eMAG do pedido). O contato primeiro segue a RN06 | y |
| Lugar da lateral no código | Narrativa → `aside` → Reaproveitamentos → Histórico; na tela larga a grade põe o `aside` na coluna da direita, ao lado da narrativa | Na estreita a lateral vem depois da narrativa (§10) sem reordenar por CSS | y |
| Item de cadastro do histórico | "Cadastrada como “{status}”, por {autor}", com a data e hora de cadastro; `{status}` é o `status_anterior` da primeira mudança ou, sem mudanças, o status atual | O acervo de demonstração cria inovações já com status (AD-011); escrever sempre "Em teste" seria falso para elas | y |
| Link "Voltar para a lista de inovações" | Continua no fim do detalhe | A §10 não o tira; a trilha já leva à lista, mas o link não atrapalha | y |
| Ajuda dos selects | Os textos de ajuda atuais continuam abaixo de cada controle (CONS-52) | A §10 não os tira | y |
| Idioma dos critérios | EARS em inglês, restante em português | Padrão das features anteriores | y |

**Open questions:** none — as do Discuss estão resolvidas; os defaults do agente foram confirmados na aprovação de 2026-11-19.

---

## User Stories

### P1: Busca em destaque e filtros ativos ⭐ MVP

**User Story**: Como quem procura uma solução, quero buscar e filtrar num só lugar e ver quais
filtros estão aplicados, para tirar um sem refazer a busca.

**Why P1**: Busca e filtros são o caminho principal da consulta (RF05, RF06).

**Acceptance Criteria**:

1. RCON-01: The list page SHALL render the page header with the trail "Inovações", the h1 "Inovações", the description "Encontre soluções que outras unidades já testaram antes de começar do zero." and the primary action link "Cadastrar inovação" → `/inovacoes/nova/`.
2. RCON-02: The list page SHALL render a search landmark (`role="search"`) containing one GET form to `/inovacoes/` whose first control is the field "Buscar" (`name="q"`, `id="id_q"`), preceded by a decorative magnifier icon (`aria-hidden="true"`), with its current help text and the submit button "Buscar" after it in source order.
3. RCON-03: The search form SHALL render, after the "Buscar" button in source order, the selects Categoria ("Todas as categorias"), Unidade ("Todas as unidades") and Status ("Todos os status"), each with its label and current help text; changing a select SHALL submit nothing (no `onchange`, no script).
4. RCON-04: WHEN the request has at least one valid filter (non-blank `q`, `categoria`, `unidade` or `status`) THEN the system SHALL render, inside the search landmark, a group labeled "Filtros ativos:" with one tag per valid filter, in the order Busca, Categoria, Unidade, Status, reading "Busca: “{termo}”", "Categoria: {nome}", "Unidade: {nome}" and "Status: {rótulo}".
5. RCON-05: Each active-filter tag SHALL contain a link whose accessible name is "Remover filtro {texto da etiqueta}" and whose `href` is `/inovacoes/` with the same query string minus that parameter and minus `page`, keeping `exibicao` when present.
6. RCON-06: WHILE at least one tag is rendered the group SHALL end with the link "Limpar filtros" → `/inovacoes/` (keeping `exibicao=tabela` when present).
7. RCON-07: IF no valid filter is present THEN the system SHALL render no "Filtros ativos:" group.
8. RCON-08: IF a filter parameter is invalid (CONS-30) THEN the system SHALL render the current error alert and field errors, no tag for the invalid parameter, and the link "Limpar filtros".

**Independent Test**: buscar "planilha" com Categoria Financeiro; ver as duas etiquetas; clicar no
"×" da categoria e cair na lista só com a busca.

---

### P1: Resultados em cartões ⭐ MVP

**User Story**: Como quem procura uma solução, quero ver em cada resultado o status, o problema
e se outras unidades já a reaproveitaram, para decidir o que abrir.

**Why P1**: É a mudança central da lista (§10).

**Acceptance Criteria**:

1. RCON-09: WHEN the list has results THEN the system SHALL render a results bar with a `role="status"` counter "{n} inovação encontrada" / "{n} inovações encontradas", where `{n}` counts every page (CONS-33).
2. RCON-10: WHILE `exibicao` is not `tabela` the system SHALL render the results of the current page as a `ul aria-label="Resultados"` with one `li` > `article` per inovação, in the current order (most recent first, CONS-02), and SHALL NOT render the results table.
3. RCON-11: Each card SHALL render, in source order: the status badge and the text "Cadastrada em {dd/mm/aaaa}"; an `h2` whose only content is a link to the detail with the title; the summary; and a metadata list with the unit name, the category name and the reuse count.
4. RCON-12: The card's title link SHALL be the only link inside the `article`.
5. RCON-13: The card summary SHALL be the full `problema` text when it has at most 160 characters; otherwise its first 159 characters followed by "…".
6. RCON-14: The card reuse count SHALL read "Nenhum reaproveitamento" for 0, "1 reaproveitamento" for 1 and "{n} reaproveitamentos" for n ≥ 2.
7. RCON-15: The status badge (cards, table and detail) SHALL contain a decorative SVG icon (`aria-hidden="true"`) — flask for "Em teste", check for "Validada", box-with-arrow for "Disponível para replicação" — and the status label as text.
8. RCON-16: The list SHALL use the same number of database queries for a page of 1 card as for a page of 20 cards from different units and categories, each with a different reuse count (CONS-48 extended to the summary and the reuse count).

**Independent Test**: abrir `/inovacoes/` com o acervo de demonstração e ler um cartão: selo,
data, título, resumo, unidade, categoria, "3 reaproveitamentos".

---

### P1: Tabela como alternativa ⭐ MVP

**User Story**: Como quem compara muitos resultados, quero alternar para a tabela atual sem
perder a busca, os filtros nem a página.

**Why P1**: Pedido explícito; a tabela é mais densa para comparar.

**Acceptance Criteria**:

1. RCON-17: WHEN the list has results THEN the results bar SHALL render a group labeled "Exibição" with the links "Cartões" and "Tabela", each with a decorative icon, the current one marked `aria-current="true"`.
2. RCON-18: The "Tabela" link SHALL point to the current query string with `exibicao=tabela`; the "Cartões" link SHALL point to the current query string without `exibicao`; both SHALL keep `q`, `categoria`, `unidade`, `status` and `page`.
3. RCON-19: WHEN `exibicao=tabela` THEN the system SHALL render the current table (caption "Inovações cadastradas"; columns Título, Categoria, Unidade, Status; same items and order as the cards) and SHALL NOT render the card list.
4. RCON-20: IF `exibicao` has any value other than `tabela` THEN the system SHALL render the cards, mark "Cartões" as current and show no error.

**Independent Test**: filtrar por Status, ir à página 2, clicar "Tabela" e ver a mesma página 2
filtrada em tabela; "Próxima" continua em tabela.

---

### P1: Paginação numerada ⭐ MVP

**User Story**: Como quem percorre muitos resultados, quero saltar direto para uma página.

**Why P1**: Decisão do usuário no Discuss (§10).

**Acceptance Criteria**:

1. RCON-21: WHILE the results span more than one page the system SHALL render a `nav aria-label="Paginação"` with "Anterior", the page numbers, "Próxima", and below it "Página {atual} de {total}".
2. RCON-22: The page numbers SHALL be the first page, the last page and the pages within 2 of the current one, in ascending order, with a text "…" (not a link) for each gap; the current page SHALL be text with `aria-current="page"`, not a link.
3. RCON-23: IF the current page is the first THEN "Anterior" SHALL be text with `aria-disabled="true"`, not a link; IF it is the last THEN "Próxima" SHALL be the same.
4. RCON-24: Every pagination link SHALL keep `q`, `categoria`, `unidade`, `status` and `exibicao` from the current request.

**Independent Test**: na página 5 de 25, ver 1 … 3 4 5 6 7 … 25.

---

### P1: Estados vazios ⭐ MVP

**User Story**: Como quem não achou nada, quero saber o que aconteceu e o que fazer em seguida.

**Why P1**: §7 e H1/H10.

**Acceptance Criteria**:

1. RCON-25: WHEN no inovação exists and no filter is active THEN the system SHALL render a decorative SVG illustration (`aria-hidden="true"`), the text "Nenhuma inovação cadastrada ainda." and the button-styled link "Cadastrar a primeira inovação" → `/inovacoes/nova/`, and no counter, card list, table or pagination.
2. RCON-26: WHEN filters are active and nothing matches THEN the system SHALL render the illustration, the text "Nenhuma inovação encontrada para esta busca.", the suggestion "Tente outras palavras ou remova algum filtro." and the link "Limpar filtros" → `/inovacoes/`, keep the active-filter tags, and render no counter, card list, table or pagination.
3. RCON-27: WHILE the high-contrast theme is active the stylesheet SHALL hide the empty-state illustration (§7).

**Independent Test**: buscar "xyzxyz" e ver a ilustração, a sugestão e as etiquetas.

---

### P1: Detalhe em narrativa com lateral ⭐ MVP

**User Story**: Como quem pensa em replicar uma solução, quero ler o problema, a solução e o
resultado em sequência e achar logo a quem perguntar.

**Why P1**: É a mudança central do detalhe (§10, RN06).

**Acceptance Criteria**:

1. RCON-28: The detail page header SHALL render, in source order, the trail "Inovações › {título}", the status badge, the h1 with the title, and the line "Cadastrada por {autor} em {dd/mm/aaaa} · {unidade} · {categoria}" (autor as in CONS-13).
2. RCON-29: The detail SHALL render a section titled "Como a inovação funciona" with an ordered list of three steps whose `h3` are, in order, "Problema ou dor", "Solução aplicada" and "Resultado ou impacto", each followed by the full text with line breaks preserved (escaped, CONS-17).
3. RCON-30: IF `resultado` is empty THEN the third step SHALL read "Resultado ainda não informado.".
4. RCON-31: The detail SHALL render an `aside aria-label="Resumo da inovação"` after the narrative and before the reuse section in source order, containing, in order, the contact card, the life-cycle block and the fact sheet.
5. RCON-32: The contact card SHALL have the title "Contato responsável", the `contato` text as typed with line breaks preserved, and the line "Procure esta pessoa para tirar dúvidas antes de replicar.".
6. RCON-33: The fact sheet SHALL be a `dl` with, in order, Unidade de origem, Categoria, Cadastrada por, Cadastrada em ({dd/mm/aaaa}) and Reaproveitamentos ({n}).
7. RCON-34: The life-cycle block SHALL keep the `h2` "Ciclo de vida" and render an `ol` with the three stages in cycle order, where stages before the current one read "{rótulo} · concluída", the current one "{rótulo} (status atual)" with `aria-current="step"`, and later ones "{rótulo} · próxima etapa"; the stage markers SHALL be `aria-hidden="true"`.
8. RCON-35: The detail SHALL render the section "Reaproveitamentos ({n})" with a table (visually hidden caption) of columns Unidade, Registrado por, Data, oldest first (REAP-18); IF n = 0 THEN it SHALL read "Nenhum reaproveitamento registrado." and render no table.
9. RCON-36: The detail SHALL keep `CONSULTAS_DO_DETALHE = 8` queries.

**Independent Test**: abrir uma inovação do acervo e ler, de cima a baixo: narrativa, contato,
ciclo, ficha, reaproveitamentos, histórico.

---

### P1: Ações em hierarquia ⭐ MVP

**User Story**: Como autor ou administrador, quero saber qual é o próximo passo da inovação e
não excluir por engano.

**Why P1**: Pedido explícito; H5 e H8.

**Acceptance Criteria**:

1. RCON-37: WHILE the status is "Em teste" or "Validada" and the user can alter the inovação (AD-009) the page header SHALL render the primary action link "Avançar para “{próximo status}”" → the status page, with `aria-describedby` pointing to the cycle explanation "O status avança um estágio por vez e não volta ao anterior." rendered in the life-cycle block.
2. RCON-38: WHILE the status is "Disponível para replicação" the page header SHALL render, for any authenticated user, the primary action link "Sinalizar reaproveitamento" → the reuse page.
3. RCON-39: WHILE the user can alter the inovação the page header SHALL render, after the primary action, the secondary link "Editar" and, last and inside a separate group, the danger link "Excluir" → the delete confirmation.
4. RCON-40: The page header SHALL render at most one primary action.
5. RCON-41: IF the user cannot alter the inovação THEN the system SHALL render neither "Avançar para …", "Editar" nor "Excluir", and the life-cycle block SHALL read "Só quem cadastrou a inovação ou um administrador pode avançar o status." unless the status is the last stage.
6. RCON-42: WHILE the status is "Disponível para replicação" the life-cycle block SHALL read "Último estágio do ciclo. O status avança um estágio por vez e não volta." for every user and, for a user who can alter, render the button "Avançar status" with `aria-disabled="true"` described by that text.

**Independent Test**: como autor de uma inovação Em teste, ver "Avançar para “Validada”" como
botão primário, Editar ao lado e Excluir afastado; como outro usuário, não ver nenhum dos três.

---

### P1: Histórico como linha do tempo ⭐ MVP

**User Story**: Como quem avalia a maturidade de uma solução, quero ver quando e por quem cada
estágio foi alcançado, desde o cadastro.

**Why P1**: Pedido explícito; §6 linha do tempo (STAT-24).

**Acceptance Criteria**:

1. RCON-43: The detail SHALL render the section with the `h2` "Histórico de status" as an `ol` whose first item is the registration — a `time` with the creation date and time ({dd/mm/aaaa HH:MM}) and the text "Cadastrada como “{status inicial}”, por {autor}", where the initial status is the `status_anterior` of the first change or, without changes, the current status.
2. RCON-44: Each status change SHALL follow as an item, oldest first, with its `time` ({dd/mm/aaaa HH:MM}) and the text "De “{anterior}” para “{novo}”, por {responsável}" (responsável as in CONS-13).
3. RCON-45: IF the inovação has no status change THEN the list SHALL contain only the registration item.
4. RCON-46: The timeline dots SHALL be `aria-hidden="true"`.

**Independent Test**: avançar uma inovação duas vezes e ver três itens: cadastro e as duas mudanças.

---

### P1: Ordem de leitura, acessibilidade e folha ⭐ MVP

**User Story**: Como usuário de leitor de tela, teclado ou zoom, quero as duas telas na mesma
ordem em que aparecem e sem perder nada.

**Why P1**: Restrições do pedido (eMAG, WCAG 2.1 AA, AD-010).

**Acceptance Criteria**:

1. RCON-47: The stylesheet SHALL NOT use the `order` property nor `grid-template-areas`/explicit placement that puts an element before a preceding sibling in source order, in the rules added by this feature.
2. RCON-48: The list and detail templates SHALL keep AD-010: no `<style>`, no `style=` and only `kira.css` components; every new color pair SHALL be in the DS-08 contrast test, including the high-contrast theme.
3. RCON-49: The new components (alternador, paginação, narrativa, grade do detalhe, busca em destaque, ilustração) SHALL respect RED-11 (reduced motion) and RED-12 (no `position: fixed`, no width above 320px outside `max-width`, reflow at 200%).
4. RCON-50: WHILE the viewport is narrower than 720px the detail SHALL render a single column, and the list cards SHALL fill one column.

**Independent Test**: zoom de 200% nas duas telas sem rolagem horizontal; Tab percorre na ordem visual.

---

## Edge Cases

- IF `page` is beyond the last page or invalid THEN the system SHALL keep the current behavior (CONS-05) and the pagination SHALL mark the page actually shown.
- IF a filter value is valid but matches nothing THEN its tag SHALL still render (RCON-26).
- WHEN the title has 150 characters THEN the card SHALL wrap it without horizontal scroll (RCON-49).
- IF `contato` or `problema` contain HTML THEN the system SHALL render it escaped (CONS-17).
- WHEN `q` contains only spaces THEN no "Busca" tag SHALL render (CONS-21).

## Implicit-requirement dimensions

| Dimension | Coverage |
| --------- | -------- |
| Input validation & bounds | `exibicao` (RCON-20), `page` (edge case, CONS-05), filtros inválidos (RCON-08) |
| Failure / partial-failure states | Form inválido (RCON-08); estados vazios (RCON-25, RCON-26) |
| Idempotency / retry / duplicate handling | N/A because the feature only renders GET pages; the POSTs it links to are unchanged |
| Auth boundaries & rate limits | Ações por perfil (RCON-37 a RCON-42, AD-009); rate limit N/A because nothing new is callable |
| Concurrency / ordering | N/A because no write is added; ordering of results and history is RCON-10, RCON-44 |
| Data lifecycle / expiry | N/A because nothing is stored |
| Observability | N/A because no new server path beyond rendering |
| External-dependency failure | N/A because no external call is added |
| State-transition integrity | Exibição do ciclo e da ação primária por status (RCON-34, RCON-37, RCON-38, RCON-42); a transição segue em AD-011 |

---

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
| -------------- | ----- | ----- | ------ |
| RCON-01 | P1: Busca e filtros | Design | Pending |
| RCON-02 | P1: Busca e filtros | Design | Implementing |
| RCON-03 | P1: Busca e filtros | Design | Implementing |
| RCON-04 | P1: Busca e filtros | Design | Implementing |
| RCON-05 | P1: Busca e filtros | Design | Implementing |
| RCON-06 | P1: Busca e filtros | Design | Implementing |
| RCON-07 | P1: Busca e filtros | Design | Implementing |
| RCON-08 | P1: Busca e filtros | Design | Implementing |
| RCON-09 | P1: Cartões | Design | Implementing |
| RCON-10 | P1: Cartões | Design | Implementing |
| RCON-11 | P1: Cartões | Design | Implementing |
| RCON-12 | P1: Cartões | Design | Implementing |
| RCON-13 | P1: Cartões | Design | Implementing |
| RCON-14 | P1: Cartões | Design | Implementing |
| RCON-15 | P1: Cartões | Design | Implementing |
| RCON-16 | P1: Cartões | Design | Implementing |
| RCON-17 | P1: Tabela | Design | Implementing |
| RCON-18 | P1: Tabela | Design | Implementing |
| RCON-19 | P1: Tabela | Design | Implementing |
| RCON-20 | P1: Tabela | Design | Implementing |
| RCON-21 | P1: Paginação | Design | Implementing |
| RCON-22 | P1: Paginação | Design | Implementing |
| RCON-23 | P1: Paginação | Design | Implementing |
| RCON-24 | P1: Paginação | Design | Implementing |
| RCON-25 | P1: Vazios | Design | Pending |
| RCON-26 | P1: Vazios | Design | Pending |
| RCON-27 | P1: Vazios | Design | Pending |
| RCON-28 | P1: Detalhe | Design | Pending |
| RCON-29 | P1: Detalhe | Design | Pending |
| RCON-30 | P1: Detalhe | Design | Pending |
| RCON-31 | P1: Detalhe | Design | Pending |
| RCON-32 | P1: Detalhe | Design | Pending |
| RCON-33 | P1: Detalhe | Design | Pending |
| RCON-34 | P1: Detalhe | Design | Pending |
| RCON-35 | P1: Detalhe | Design | Pending |
| RCON-36 | P1: Detalhe | Design | Pending |
| RCON-37 | P1: Ações | Design | Pending |
| RCON-38 | P1: Ações | Design | Pending |
| RCON-39 | P1: Ações | Design | Pending |
| RCON-40 | P1: Ações | Design | Pending |
| RCON-41 | P1: Ações | Design | Pending |
| RCON-42 | P1: Ações | Design | Pending |
| RCON-43 | P1: Histórico | Design | Implementing |
| RCON-44 | P1: Histórico | Design | Implementing |
| RCON-45 | P1: Histórico | Design | Implementing |
| RCON-46 | P1: Histórico | Design | Pending |
| RCON-47 | P1: Ordem e folha | Design | Pending |
| RCON-48 | P1: Ordem e folha | Design | Pending |
| RCON-49 | P1: Ordem e folha | Design | Pending |
| RCON-50 | P1: Ordem e folha | Design | Pending |

**Status values:** Pending → In Design → In Tasks → Implementing → Verified

**Coverage:** 50 total, 0 mapped to tasks, 50 unmapped (Tasks ainda não feitas).

**Regras de teste para a feature toda:** toda AC de "está exibido" ou "não está exibido" usa
`exibido(html, rigoroso=True)` de `inovacoes/tests/visibilidade.py` sobre o DOM da página inteira
(L-028, L-030) e confere que a `kira.css` não esconde o seletor (L-044). Toda AC de ação por perfil
testa também o `USUARIO` com `is_staff` (L-003). Cada cláusula de AC composta é afirmada na tela
(L-005).

---

## Success Criteria

- [ ] Com o acervo de demonstração, a lista mostra 20 cartões completos e responde em < 2 s (RNF08).
- [ ] Remover uma etiqueta ou trocar Cartões/Tabela nunca perde os outros filtros nem a página.
- [ ] O detalhe tem uma só ação primária e o Excluir separado, para todo status e perfil.
- [ ] Conferência no navegador (UAT) aprovada pelo usuário, inclusive zoom de 200% e alto contraste.
