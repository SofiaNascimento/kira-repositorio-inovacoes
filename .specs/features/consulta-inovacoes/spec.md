# Consulta de Inovações (F3) — Specification

**Fontes:** `docs/requisitos.md` (RF03, RF04, RF05, RF06, RF15, RN04, RN06, RN07, RNF01, RNF08, RNF09) · `docs/mapa-de-features.md` (F3)
**Decisões vinculantes:** AD-001 (sessão do Django) · AD-002 (MVT sem Service Layer: consulta pelo ORM nas views/forms) · AD-003 (PostgreSQL) · AD-006 (acesso negado por padrão: nenhuma view da F3 é pública) · AD-007 (nenhuma consulta pelo Django admin; `Inovacao` segue fora do admin)
**Reusa da F2:** modelo `inovacoes.Inovacao` sem campos novos de domínio · `Unidade`, `Categoria` e `StatusInovacao` como fonte das opções dos filtros (RN07) · mensagens da INOV-12 e INOV-17 · padrões de acessibilidade INOV-31 a INOV-35 e INOV-41
**Reusa da F1:** página 500 sem vazamento (AUTH-26) · região de mensagens `role="status"` do `templates/base.html`
**Altera a F2:** INOV-03 (destino após cadastro) e INOV-36/INOV-37 (destino do "Cancelar") — ver CONS-49 a CONS-51
**Status:** Aprovada pelo usuário em 2026-10-03 (assumptions confirmadas na aprovação)
**Contexto da discussão:** `.specs/features/consulta-inovacoes/context.md`

> **Nota de notação:** como na F1 e na F2, os critérios de aceite estão em EARS em inglês (WHEN /
> WHILE / WHERE / IF-THEN / ubíquo + SHALL); o restante do documento está em português. Textos
> exibidos ao usuário aparecem entre aspas, em português, exatamente como devem ser renderizados.

## Problem Statement

A F2 permite registrar inovações, mas ninguém consegue encontrá-las: não há lista, nem página de
detalhe, nem busca. Sem isso, a unidade que enfrenta um problema continua resolvendo do zero o que
outra unidade já resolveu — exatamente a dor que o sistema existe para eliminar. A F3 entrega o lado
de leitura do repositório: ver o que existe, achar por palavra ou por categoria, unidade e status, e
chegar ao contato de quem responde pela solução.

## Goals

- [ ] Qualquer usuário autenticado, dos dois perfis, vê todas as inovações cadastradas numa lista
      resumida com título, categoria, unidade e status, e abre o detalhe de qualquer uma com todos os
      campos e o contato responsável.
- [ ] Uma busca por palavras encontra toda inovação que contém essas palavras em título, problema ou
      solução, sem distinguir maiúsculas, minúsculas nem acentos, e nenhuma que não as contenha.
- [ ] Os filtros de categoria, unidade e status funcionam isolados, combinados entre si e combinados
      com a busca.
- [ ] Com 500 inovações carregadas, a listagem e a busca combinada respondem em até 2 segundos.
- [ ] Toda consulta sem resultado e o repositório vazio exibem uma mensagem que diz o que aconteceu e
      o que fazer a seguir.

## Out of Scope

Excluído explicitamente. Documentado para impedir scope creep.

| Feature | Reason |
| ------- | ------ |
| Editar, excluir ou trocar o status a partir da lista ou do detalhe | F4 (RF07, RF08) e F5 (RF09). O detalhe da F3 não exibe esses botões. |
| Botão "Reaproveitei esta inovação" e indicadores | F6 (RF10, RF11). |
| Ordenação escolhida pelo usuário ou por relevância | Nenhum RF pede; ordem fixa por data de criação. Registrado em Deferred Ideas. |
| Destaque do termo buscado nos resultados | Nenhum RF pede. Registrado em Deferred Ideas. |
| Busca em resultado/impacto, contato, autor, categoria ou unidade | O RF05 limita a busca a título, problema e solução; categoria e unidade já têm filtro. |
| Filtros por autor ou por data | O RF06 limita os filtros a categoria, unidade e status. |
| Busca com operadores (aspas, `-palavra`, OU) | Fora do RF05; a semântica é "todas as palavras". |
| Rolagem infinita, atualização sem recarregar a página, autocomplete | Exigiriam JavaScript; o formulário GET atende RF05/RF06 e WCAG 3.2.2. |
| Ignorar acentos na unicidade de título (RN10) | Decisão da F2 mantida; a F3 ignora acentos só na busca. |
| Exportar resultados | Nenhum RF pede. |
| Auditoria WCAG completa, responsividade e teste SUS | RNF09, RNF03 e RNF01 têm validação transversal no fim. A F3 cobre o que é dela: rótulos, teclado, foco, semântica da tabela e dos filtros. |

---

## Assumptions & Open Questions

Toda ambiguidade está resolvida ou registrada aqui — nada fica silenciosamente indefinido.

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --------------------- | -------------- | --------- | ---------- |
| Caixa e acentos na busca | Ignora os dois, no termo e nos campos: "solucao" encontra "Solução" | Decidido com o usuário | y |
| Mecanismo para ignorar acentos | Decidido no Design e registrado como AD; opções: extensão `unaccent` ou texto normalizado gravado pela aplicação, sem extensão | Na F2 o usuário recusou depender do `unaccent` no deploy (RNF06); o trade-off é técnico, não de produto | y |
| Várias palavras | Separa por espaço; todas precisam aparecer, cada uma por trecho, em título, problema ou solução, podendo estar em campos diferentes | Decidido com o usuário | y |
| Caracteres especiais na busca | `%`, `_` e `\` valem como texto literal | Evita que o termo vire curinga do `LIKE` | y |
| Tamanho máximo da busca | 100 caracteres; acima disso, mensagem no campo no formato da INOV-12 e nenhuma inovação listada | Nenhum requisito fixa valor; 100 cobre qualquer busca real e limita o custo da consulta | y |
| Rota e tela inicial | Listagem em `/inovacoes/`; `/` redireciona (302) para ela; a `HomeInternaView` provisória sai; login sem `next` cai na listagem via `/` | Decidido com o usuário | y |
| Link no cabeçalho | "Inovações" → `/inovacoes/`, antes de "Cadastrar inovação" | Reconhecimento em vez de memorização (H6) | y |
| Ordem da listagem | Data de criação decrescente; empate pelo id decrescente | Decidido com o usuário; o desempate torna a ordem determinística | y |
| Paginação | 20 por página; "Anterior", "Próxima" e "Página X de Y"; busca e filtros preservados nos links | Decidido com o usuário | y |
| Parâmetro `page` inválido | Não numérico → página 1; acima da última → última página; sem erro | Comportamento padrão do `Paginator.get_page` do Django; URL adulterada não quebra a tela | y |
| Forma da listagem | Tabela com `<caption>` e cabeçalhos `<th scope="col">` Título, Categoria, Unidade, Status; título como link para o detalhe | Dado tabular com quatro atributos por linha; leitor de tela anuncia o cabeçalho de cada célula (RNF09) | y |
| Rota do detalhe | `/inovacoes/<id>/` | Padrão de URL do Django; o id já existe | y |
| Inovação inexistente | HTTP 404 com "Inovação não encontrada." e link "Voltar para a lista de inovações" | Sem `404.html` no projeto hoje; a F4 vai gerar ids apagados | y |
| Campos do detalhe | Os oito da seção 5 + "Cadastrada por <nome completo, ou username sem nome> em <dd/mm/aaaa>" | Decidido com o usuário | y |
| Resultado vazio no detalhe | "Não informado" | Campo opcional (INOV-14); campo em branco parece erro de tela | y |
| Quebras de linha e HTML no detalhe | Quebras de linha preservadas; marcação HTML exibida como texto | Textos longos são digitados em parágrafos; escapar evita XSS | y |
| Destino após cadastro | Detalhe da inovação criada, com a mensagem da INOV-28 | Decidido com o usuário; substitui a INOV-03 | y |
| Destino do "Cancelar" do cadastro | `/inovacoes/` | A home provisória deixa de existir; substitui o alvo da INOV-36/INOV-37 | y |
| Forma dos filtros | Um formulário GET dentro de `role="search"`: busca (`type="search"`), Categoria, Unidade, Status, botão "Buscar"; nada é aplicado ao mudar um select | Decidido com o usuário (WCAG 3.2.2) | y |
| Opções dos filtros | Categoria e Unidade em ordem alfabética, precedidas de "Todas as categorias" / "Todas as unidades"; Status na ordem do ciclo (Em teste, Validada, Disponível para replicação), precedido de "Todos os status" | Mesma ordem da INOV-15; o ciclo de vida é a ordem natural do status | y |
| "Limpar filtros" | Link para `/inovacoes/` sem parâmetros, exibido só quando há busca ou filtro ativo | Nada a limpar é ruído (H8) | y |
| Filtro com valor inexistente | Mensagem no campo ("Selecione uma categoria da lista.", "Selecione uma unidade da lista.", "Selecione um status da lista."), resumo "Não foi possível buscar. Corrija os campos indicados." em `role="alert"` e nenhuma inovação listada | Só ocorre por URL adulterada ou item renomeado/excluído; listar tudo ignoraria o pedido em silêncio | y |
| Contagem | "1 inovação encontrada" / "N inovações encontradas", com o total de todas as páginas | Visibilidade do estado do sistema (H1) | y |
| Estado vazio sem filtros | "Nenhuma inovação cadastrada ainda." + link "Cadastrar inovação" | Diz o que houve e o próximo passo | y |
| Estado vazio com busca ou filtros | "Nenhuma inovação encontrada para a busca e os filtros informados." + link "Limpar filtros"; sem tabela vazia | Diz o que houve e como sair (H9) | y |
| Ajuda contextual (RF15) | Texto com exemplo sob cada um dos quatro controles, ligado por `aria-describedby`. Busca: "Procura em título, problema e solução. Ex.: planilha conciliação". Categoria: "Área de back office. Ex.: Financeiro". Unidade: "Sede ou filial que criou a solução. Ex.: Filial Norte". Status: "Estágio da solução. Ex.: Disponível para replicação" | O mapa aloca RF15 aos filtros da F3; mesmo padrão da INOV-41 | y |
| Conjunto de demonstração | Management command `carregar_demonstracao` cria 500 inovações com títulos "Demonstração 001" a "Demonstração 500", textos variados, autor uma conta `demo` (perfil `USUARIO`, sem senha utilizável); cada unidade, categoria e status aparece em pelo menos 20 registros | Decidido com o usuário (500 via comando); conta própria separa os dados de demo dos reais | y |
| Repetir a carga de demonstração | Rodar de novo não duplica: ao fim, existem exatamente 500 inovações "Demonstração NNN" | Idempotência; a RN10 já recusaria duplicatas | y |
| Medição do RNF08 | Tempo de resposta do servidor medido por teste automatizado com o conjunto de demonstração carregado, no ambiente local de desenvolvimento | "Tempo adequado à interação" com referência de 2 s; rede e navegador ficam fora da medição | y |
| Idioma dos critérios de aceite | EARS em inglês, restante em português | Mesmo padrão da F1 e da F2; `validate_spec.py` exige `SHALL` | y |

**Open questions:** none - todas resolvidas com o usuário ou registradas como assumption acima (defaults do agente confirmados na aprovação da spec em 2026-10-03).

---

## Dimensions Sweep

Escopo Large ⇒ varredura completa: cada dimensão vira requisito ou recebe `N/A because…` explícito.

| Dimensão | Resolução |
| -------- | --------- |
| Input validation & bounds | CONS-21 (busca vazia), CONS-23 (curingas literais), CONS-24 (tamanho da busca), CONS-30 (filtro inexistente), CONS-05 (página inválida), CONS-15 (id inexistente) |
| Failure / partial-failure states | CONS-53 (banco indisponível → página 500 sem detalhes). Escrita parcial: **N/A because** a F3 só lê. |
| Idempotency / retry / duplicate handling | CONS-45 (carga de demonstração repetida não duplica). Consultas: **N/A because** são GET sem efeito colateral; repetir dá o mesmo resultado. |
| Auth boundaries & rate limits | CONS-07 (anônimo redirecionado ao login), CONS-08 (os dois perfis veem tudo, RN04). Rate limits: **N/A because** nenhum RN/RNF exige e toda consulta exige sessão de conta criada por administrador. |
| Concurrency / ordering | CONS-02 (ordem determinística com desempate). Registro novo entre duas páginas deslocando itens: **N/A because** é aceitável numa lista ordenada por data e nenhum requisito pede paginação estável. |
| Data lifecycle / expiry | **N/A because** a F3 não cria, altera nem apaga dados de domínio; inovação apagada depois (F4) cai no 404 da CONS-15. |
| Observability | **N/A because** nenhum requisito pede log ou métrica de consulta; o RNF08 é verificado por teste (CONS-46, CONS-47). |
| External-dependency failure | CONS-53 (PostgreSQL indisponível). **N/A** para outros serviços: a F3 não chama nenhum. |
| State-transition integrity | **N/A because** a F3 exibe o status sem alterá-lo; transições são da F5. |

---

## User Stories

### P1: Ver a lista de inovações ⭐ MVP

**User Story**: Como colaborador autenticado, quero ver de relance o que já foi registrado no
repositório, para descobrir soluções antes de começar a minha.

**Why P1**: RF03 é Essencial; é a porta de entrada de toda a consulta e passa a ser a tela inicial.

**Acceptance Criteria**:

1. **CONS-01** — WHEN an authenticated user requests `/inovacoes/` THEN the system SHALL respond with HTTP 200 and a table with one row per Inovacao showing its título, categoria name, unidade de origem name and status label.
2. **CONS-02** — The system SHALL order the listing by data de criação descending and, for equal dates, by id descending.
3. **CONS-03** — The system SHALL show at most 20 Inovacoes per page and, when there is more than one page, display "Página X de Y" and the links "Anterior" (absent on the first page) and "Próxima" (absent on the last page).
4. **CONS-04** — WHILE a search term or filter is active the system SHALL keep the same search term and filter values in the "Anterior" and "Próxima" links.
5. **CONS-05** — IF the `page` parameter is not an integer THEN the system SHALL show page 1, and IF it is greater than the last page THEN the system SHALL show the last page, both with HTTP 200.
6. **CONS-06** — The system SHALL render the título in each row as a link to that Inovacao's detail page.
7. **CONS-07** — IF an anonymous visitor requests `/inovacoes/` or `/inovacoes/<id>/` THEN the system SHALL redirect to the login page with `next` set to the requested path, including its query string.
8. **CONS-08** — WHEN a user with profile `USUARIO` or `ADMINISTRADOR` requests the listing THEN the system SHALL include the Inovacoes of every author and every unidade de origem.
9. **CONS-09** — WHEN an authenticated user requests `/` THEN the system SHALL respond with HTTP 302 to `/inovacoes/`.
10. **CONS-10** — WHILE a user is authenticated the system SHALL display in the header of every page a link labeled "Inovações" pointing to `/inovacoes/`.
11. **CONS-11** — WHEN a user logs in from a login page without `next` THEN the system SHALL bring the user, following redirects, to `/inovacoes/`.

**Independent Test**: cadastrar 25 inovações de autores e unidades diferentes; entrar como `USUARIO`;
conferir a tabela com as 20 mais recentes, "Página 1 de 2", só "Próxima"; abrir `?page=abc` e
`?page=99`; sair e abrir `/inovacoes/?q=caixa` como anônimo.

---

### P1: Ver o detalhe de uma inovação e falar com o responsável ⭐ MVP

**User Story**: Como colaborador que achou uma solução promissora, quero ler como ela funciona e saber
com quem falar, para replicá-la na minha unidade.

**Why P1**: RF04 e RN06 são Essenciais; o contato responsável é o que torna o reaproveitamento
possível.

**Acceptance Criteria**:

1. **CONS-12** — WHEN an authenticated user requests `/inovacoes/<id>/` for an existing Inovacao THEN the system SHALL respond with HTTP 200, show its título as the page's `h1`, and show título, unidade de origem, categoria, problema/dor, solução aplicada, resultado/impacto, status and contato responsável, each preceded by its label.
2. **CONS-13** — WHEN the detail page is shown THEN the system SHALL display "Cadastrada por <autor> em <dd/mm/aaaa>", where <autor> is the author's full name, or the username when the account has no first or last name, and the date is the data de criação in the `America/Sao_Paulo` time zone.
3. **CONS-14** — IF the Inovacao's resultado/impacto is empty THEN the system SHALL display "Não informado" in its place.
4. **CONS-15** — IF `/inovacoes/<id>/` is requested for an id with no Inovacao THEN the system SHALL respond with HTTP 404 and a page showing "Inovação não encontrada." and a link "Voltar para a lista de inovações" to `/inovacoes/`.
5. **CONS-16** — The system SHALL display the line breaks typed in problema/dor, solução aplicada and resultado/impacto as line breaks on the detail page.
6. **CONS-17** — IF any field of the Inovacao contains HTML markup THEN the system SHALL display it as literal text and SHALL NOT render it as markup.
7. **CONS-18** — The system SHALL display on the detail page a link labeled "Voltar para a lista de inovações" pointing to `/inovacoes/`.

**Independent Test**: cadastrar uma inovação sem resultado, com problema em dois parágrafos e
`<b>x</b>` na solução; abrir o detalhe e conferir os oito rótulos, "Não informado", as quebras de
linha, o texto literal `<b>x</b>`, a linha "Cadastrada por" e o link de volta; abrir
`/inovacoes/999999/` e ver o 404.

---

### P1: Buscar por palavra-chave ⭐ MVP

**User Story**: Como colaborador com um problema concreto, quero digitar algumas palavras e achar
soluções que tratam disso, sem me preocupar com acentos nem maiúsculas.

**Why P1**: RF05 é Essencial; é o caminho mais rápido entre o problema e uma solução existente.

**Acceptance Criteria**:

1. **CONS-19** — WHEN the listing is requested with a non-blank search term `q` THEN the system SHALL list only the Inovacoes in which every whitespace-separated word of `q` appears as a substring of the título, the problema/dor or the solução aplicada, each word possibly in a different one of these fields.
2. **CONS-20** — The system SHALL match search words ignoring letter case and accents in both the term and the fields, so that "solucao" matches "Solução" and "SOLUÇÃO" matches "solucao".
3. **CONS-21** — IF the search term is empty or contains only whitespace THEN the system SHALL apply no text filter.
4. **CONS-22** — IF a search word appears only in resultado/impacto, contato responsável, categoria or unidade de origem of an Inovacao THEN the system SHALL NOT list that Inovacao for that word.
5. **CONS-23** — IF the search term contains `%`, `_` or `\` THEN the system SHALL match those characters literally.
6. **CONS-24** — IF the search term exceeds 100 characters THEN the system SHALL show next to the search field "Use no máximo 100 caracteres (você digitou M)." with the actual length and SHALL list no Inovacao.
7. **CONS-25** — WHEN results are shown for a search THEN the system SHALL display the submitted term in the search field.

**Independent Test**: cadastrar "Conciliação bancária" (problema: "planilha manual") e outra com
"planilha" só no resultado; buscar "CONCILIACAO planilha" e ver só a primeira; buscar "planilha" e
ver só a primeira; buscar "%" e ver só inovações com "%" no texto; buscar 101 caracteres e ver a
mensagem.

---

### P1: Filtrar por categoria, unidade e status ⭐ MVP

**User Story**: Como colaborador de uma área, quero restringir a lista às soluções da minha área,
de uma unidade ou já prontas para replicar, isoladamente ou tudo junto.

**Why P1**: RF06 e RN07 são Essenciais; os filtros são a razão de unidade e categoria serem listas
controladas.

**Acceptance Criteria**:

1. **CONS-26** — The system SHALL offer selection controls for categoria, unidade de origem and status, with Categoria and Unidade records in alphabetical order preceded by "Todas as categorias" and "Todas as unidades", and the status options "Em teste", "Validada" and "Disponível para replicação", in that order, preceded by "Todos os status".
2. **CONS-27** — WHEN exactly one of categoria, unidade or status is selected THEN the system SHALL list only the Inovacoes with that value.
3. **CONS-28** — WHEN two or more of categoria, unidade, status and a non-blank search term are given THEN the system SHALL list only the Inovacoes that satisfy all of them at once.
4. **CONS-29** — WHEN results are shown for a filter THEN the system SHALL keep that value selected in its control.
5. **CONS-30** — IF the categoria, unidade or status parameter does not match a registered record or status THEN the system SHALL show next to that control "Selecione uma categoria da lista.", "Selecione uma unidade da lista." or "Selecione um status da lista.", show "Não foi possível buscar. Corrija os campos indicados." inside an element with `role="alert"`, and list no Inovacao.
6. **CONS-31** — The system SHALL submit the search term and the filters together through a single form using the GET method and a button labeled "Buscar", and SHALL NOT apply any filter when a selection control changes without that submission.
7. **CONS-32** — WHILE a search term or filter is active the system SHALL display a link labeled "Limpar filtros" pointing to `/inovacoes/` without parameters.

**Independent Test**: com inovações em Financeiro/Sede/Validada, Financeiro/Filial Norte/Em teste e
RH/Sede/Validada, filtrar só Financeiro (2), Financeiro + Sede (1), Sede + Validada + busca por uma
palavra da terceira (1); abrir `?categoria=999999` e ver a mensagem; clicar "Limpar filtros".

---

### P1: Contagem e estados vazios claros ⭐ MVP

**User Story**: Como colaborador, quero saber quantas inovações minha consulta achou e, quando não
achar nada, entender por quê e o que fazer.

**Why P1**: Pedido explícito da feature; atende H1 e H9 do RNF01 (Essencial).

**Acceptance Criteria**:

1. **CONS-33** — WHEN the listing has at least one result THEN the system SHALL display above the table "1 inovação encontrada" or "N inovações encontradas", where N is the total across all pages.
2. **CONS-34** — WHILE no Inovacao exists and no search term or filter is active the system SHALL display "Nenhuma inovação cadastrada ainda." with a link "Cadastrar inovação" to `/inovacoes/nova/`, and SHALL NOT render the table.
3. **CONS-35** — IF a search term or filter is active and no Inovacao matches THEN the system SHALL display "Nenhuma inovação encontrada para a busca e os filtros informados." with the "Limpar filtros" link, and SHALL NOT render the table.

**Independent Test**: num banco sem inovações, abrir a lista e ver a primeira mensagem; cadastrar
uma, buscar "inexistente" e ver a segunda; limpar e ver "1 inovação encontrada".

---

### P1: Consulta acessível por teclado e leitor de tela ⭐ MVP

**User Story**: Como colaborador que usa teclado ou leitor de tela, quero buscar, filtrar, navegar
entre páginas e ler o detalhe sem depender do mouse nem da cor.

**Why P1**: RNF09 é Essencial.

**Acceptance Criteria**:

1. **CONS-36** — The system SHALL associate the search field and each of the three selection controls with a visible `<label>` through matching `for` and `id` attributes.
2. **CONS-37** — The system SHALL place the search and filter form inside an element with `role="search"`.
3. **CONS-38** — The system SHALL render the listing table with a `<caption>` and with `<th scope="col">` headers "Título", "Categoria", "Unidade" and "Status".
4. **CONS-39** — The system SHALL place the pagination links inside a `<nav>` element with `aria-label="Paginação"`.
5. **CONS-40** — The system SHALL convey every status as its text label, never by color alone.
6. **CONS-41** — The system SHALL build the listing and detail pages only from native HTML controls and links, without any positive `tabindex`, and SHALL show a visible focus indicator on each of them.
7. **CONS-42** — The system SHALL present the fields of the detail page as a description list, with each label in a `<dt>` followed by its value in a `<dd>`.
8. **CONS-43** — IF a search or filter control has a validation error THEN the system SHALL render it with `aria-invalid="true"` and reference the error message element in its `aria-describedby`.

**Independent Test**: percorrer busca, filtros, "Buscar", resultados e paginação só com Tab e Enter;
inspecionar o HTML e conferir `label[for]`, `role="search"`, `caption`, `th[scope=col]`,
`nav[aria-label]`, `dl/dt/dd`, `aria-invalid` após `?status=X`.

---

### P2: Desempenho com o conjunto de demonstração

**User Story**: Como avaliador do TCC, quero provar que listagem e busca continuam ágeis com um volume
realista, carregado de forma reproduzível.

**Why P2**: RNF08 é Desejável, mas o critério de 2 s foi pedido explicitamente para esta feature.

**Acceptance Criteria**:

1. **CONS-44** — WHEN the command `carregar_demonstracao` runs on a migrated database THEN the system SHALL create 500 Inovacoes titled "Demonstração 001" to "Demonstração 500", authored by the account `demo` with profile `USUARIO` and no usable password, with every Unidade, every Categoria and every status present in at least 20 of them.
2. **CONS-45** — IF `carregar_demonstracao` runs again THEN the system SHALL end with exactly 500 Inovacoes titled "Demonstração NNN" and exactly one account `demo`.
3. **CONS-46** — WHILE the demonstration set is loaded the system SHALL answer an authenticated GET of `/inovacoes/` within 2 seconds of server time.
4. **CONS-47** — WHILE the demonstration set is loaded the system SHALL answer within 2 seconds of server time an authenticated GET of `/inovacoes/` combining a two-word search term with categoria, unidade and status filters.
5. **CONS-48** — The system SHALL render a listing page with a number of database queries that does not grow with the number of Inovacoes on the page.

**Independent Test**: rodar o comando duas vezes e contar 500 registros e uma conta `demo`; medir as
duas requisições no teste automatizado; comparar o número de consultas com 1 e com 20 inovações na
página.

---

### P2: Cadastro e cancelamento levam à consulta

**User Story**: Como colaborador que acabou de cadastrar, quero ver a inovação como os outros vão
vê-la; e, se desistir, voltar para a lista.

**Why P2**: Fecha a costura com a F2, que deixou a home provisória como destino até a F3 existir.

**Acceptance Criteria**:

1. **CONS-49** — WHEN a registration succeeds THEN the system SHALL respond with HTTP 302 to the detail page of the new Inovacao.
2. **CONS-50** — WHEN the detail page is reached by the redirect after a registration THEN the system SHALL display the INOV-28 success message inside the page's `role="status"` region.
3. **CONS-51** — The system SHALL point the registration form's "Cancelar" link to `/inovacoes/`.

**Independent Test**: cadastrar uma inovação e cair no detalhe dela com a mensagem; abrir o formulário
de novo, clicar "Cancelar" e cair na listagem.

---

### P3: Ajuda contextual nos filtros

**User Story**: Como colaborador que busca pela primeira vez, quero saber onde a busca procura e o que
cada filtro significa.

**Why P3**: RF15 é Desejável; o mapa o aloca aos filtros da F3.

**Acceptance Criteria**:

1. **CONS-52** — The system SHALL display below the search field and each of the three selection controls the help text defined in Assumptions, referenced by that control's `aria-describedby`.

**Independent Test**: abrir a lista e conferir os quatro textos de apoio, cada um ligado ao seu
controle pelo `aria-describedby`.

---

## Edge Cases

- **CONS-53** — IF the database is unreachable while the listing or a detail page is being processed THEN the system SHALL respond with the project's HTTP 500 page and SHALL NOT expose connection details.

Os demais limites estão nos critérios das histórias: busca vazia (CONS-21), curingas (CONS-23), busca
longa (CONS-24), filtro inexistente (CONS-30), página inválida (CONS-05), id inexistente (CONS-15),
repositório vazio (CONS-34) e consulta sem resultado (CONS-35).

---

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
| -------------- | ----- | ----- | ------ |
| CONS-01 | P1: Ver a lista de inovações | Execute | Implementing |
| CONS-02 | P1: Ver a lista de inovações | Execute | Implementing |
| CONS-03 | P1: Ver a lista de inovações | Execute | Implementing |
| CONS-04 | P1: Ver a lista de inovações | - | Pending |
| CONS-05 | P1: Ver a lista de inovações | Execute | Implementing |
| CONS-06 | P1: Ver a lista de inovações | Execute | Implementing |
| CONS-07 | P1: Ver a lista de inovações | Execute | Implementing |
| CONS-08 | P1: Ver a lista de inovações | Execute | Implementing |
| CONS-09 | P1: Ver a lista de inovações | Execute | Implementing |
| CONS-10 | P1: Ver a lista de inovações | Execute | Implementing |
| CONS-11 | P1: Ver a lista de inovações | Execute | Implementing |
| CONS-12 | P1: Ver o detalhe de uma inovação e falar com o responsável | Execute | Implementing |
| CONS-13 | P1: Ver o detalhe de uma inovação e falar com o responsável | Execute | Implementing |
| CONS-14 | P1: Ver o detalhe de uma inovação e falar com o responsável | Execute | Implementing |
| CONS-15 | P1: Ver o detalhe de uma inovação e falar com o responsável | Execute | Implementing |
| CONS-16 | P1: Ver o detalhe de uma inovação e falar com o responsável | Execute | Implementing |
| CONS-17 | P1: Ver o detalhe de uma inovação e falar com o responsável | Execute | Implementing |
| CONS-18 | P1: Ver o detalhe de uma inovação e falar com o responsável | Execute | Implementing |
| CONS-19 | P1: Buscar por palavra-chave | - | Pending |
| CONS-20 | P1: Buscar por palavra-chave | - | Pending |
| CONS-21 | P1: Buscar por palavra-chave | - | Pending |
| CONS-22 | P1: Buscar por palavra-chave | - | Pending |
| CONS-23 | P1: Buscar por palavra-chave | - | Pending |
| CONS-24 | P1: Buscar por palavra-chave | - | Pending |
| CONS-25 | P1: Buscar por palavra-chave | - | Pending |
| CONS-26 | P1: Filtrar por categoria, unidade e status | - | Pending |
| CONS-27 | P1: Filtrar por categoria, unidade e status | - | Pending |
| CONS-28 | P1: Filtrar por categoria, unidade e status | - | Pending |
| CONS-29 | P1: Filtrar por categoria, unidade e status | - | Pending |
| CONS-30 | P1: Filtrar por categoria, unidade e status | - | Pending |
| CONS-31 | P1: Filtrar por categoria, unidade e status | - | Pending |
| CONS-32 | P1: Filtrar por categoria, unidade e status | - | Pending |
| CONS-33 | P1: Contagem e estados vazios claros | Execute | Implementing |
| CONS-34 | P1: Contagem e estados vazios claros | Execute | Implementing |
| CONS-35 | P1: Contagem e estados vazios claros | - | Pending |
| CONS-36 | P1: Consulta acessível por teclado e leitor de tela | - | Pending |
| CONS-37 | P1: Consulta acessível por teclado e leitor de tela | - | Pending |
| CONS-38 | P1: Consulta acessível por teclado e leitor de tela | Execute | Implementing |
| CONS-39 | P1: Consulta acessível por teclado e leitor de tela | Execute | Implementing |
| CONS-40 | P1: Consulta acessível por teclado e leitor de tela | Execute | Implementing |
| CONS-41 | P1: Consulta acessível por teclado e leitor de tela | Execute | Implementing |
| CONS-42 | P1: Consulta acessível por teclado e leitor de tela | Execute | Implementing |
| CONS-43 | P1: Consulta acessível por teclado e leitor de tela | - | Pending |
| CONS-44 | P2: Desempenho com o conjunto de demonstração | - | Pending |
| CONS-45 | P2: Desempenho com o conjunto de demonstração | - | Pending |
| CONS-46 | P2: Desempenho com o conjunto de demonstração | - | Pending |
| CONS-47 | P2: Desempenho com o conjunto de demonstração | - | Pending |
| CONS-48 | P2: Desempenho com o conjunto de demonstração | Execute | Implementing |
| CONS-49 | P2: Cadastro e cancelamento levam à consulta | Execute | Implementing |
| CONS-50 | P2: Cadastro e cancelamento levam à consulta | Execute | Implementing |
| CONS-51 | P2: Cadastro e cancelamento levam à consulta | Execute | Implementing |
| CONS-52 | P3: Ajuda contextual nos filtros | - | Pending |
| CONS-53 | Edge case: banco indisponível | Execute | Implementing |

**ID format:** `CONS-NN`
**Status values:** Pending → In Design → In Tasks → Implementing → Verified
**Coverage:** 53 total, 29 implementando (Execute), 24 pendentes.

---

## Rastreabilidade com o Documento de Requisitos

| Origem | Requirement IDs |
| ------ | --------------- |
| RF03 | CONS-01 … CONS-06, CONS-09 … CONS-11 |
| RF04 | CONS-12 … CONS-18 |
| RF05 | CONS-19 … CONS-25 |
| RF06 | CONS-26 … CONS-32 |
| RF15 | CONS-52 |
| RN04 | CONS-07, CONS-08 |
| RN06 | CONS-12 |
| RN07 | CONS-26, CONS-30 |
| RNF01 | CONS-33 … CONS-35 (H1, H9), CONS-31, CONS-32 (H3), CONS-19, CONS-28 (H7), CONS-26 (H6), CONS-03 (H8), CONS-52 (H10) |
| RNF08 | CONS-44 … CONS-48 |
| RNF09 | CONS-36 … CONS-43 |
| AD-006 | CONS-07 |
| AUTH-26 | CONS-53 |
| INOV-03 (substituída) | CONS-49 |
| INOV-28 | CONS-50 |
| INOV-36, INOV-37 (alvo alterado) | CONS-51 |

---

## Success Criteria

- [ ] Um `USUARIO` e um `ADMINISTRADOR` veem a mesma listagem, com inovações de todos os autores, e
      abrem o detalhe de qualquer uma com o contato responsável.
- [ ] A busca "conciliacao planilha" encontra a inovação "Conciliação bancária" cujo problema cita
      "planilha" e não encontra uma que cita "planilha" só no resultado.
- [ ] Com o conjunto de demonstração carregado, filtrar por categoria + unidade + status + busca
      devolve exatamente os registros que satisfazem os quatro critérios, em até 2 s de servidor.
- [ ] Repositório vazio e consulta sem resultado mostram cada um sua mensagem, com o próximo passo.
- [ ] Busca, filtros, paginação e detalhe são operados só com teclado, com rótulos associados e foco
      visível.
