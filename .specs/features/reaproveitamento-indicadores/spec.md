# Reaproveitamento e Indicadores (F6) — Specification

**Fontes:** `docs/requisitos.md` (RF11, RF10, RN09, RNF08; RF12, RF13, RF14, RN04, RN07, RNF07 e RNF09 reaplicados à sinalização e ao painel) · `docs/mapa-de-features.md` (F6) · `docs/design-spec.md` (§6 card e tabela, §7 estado vazio, §10 F6) · `docs/modelagem-uml.md` (§2.1 Reaproveitamento)
**Decisões vinculantes:** AD-001 (sessão do Django) · AD-002 (MVT sem Service Layer: a regra da RN09 fica no model) · AD-003 (PostgreSQL; unicidade por unidade e integridade referencial no banco) · AD-004 (perfil por enum; o perfil não restringe a sinalização) · AD-005 (o responsável aponta para `settings.AUTH_USER_MODEL`) · AD-006 (as rotas novas nascem protegidas) · AD-007 (o admin de `Reaproveitamento` herda `AcessoSomenteAdministradorMixin`) · AD-008 (a sinalização não grava `Inovacao`; `texto_busca` intacto) · AD-009 (a sinalização não altera a `Inovacao`: não herda `AlteracaoDeInovacaoMixin` e a rota nova entra na allowlist da varredura de autoria) · AD-010 (cards, gráficos e tabelas do painel são componentes da `kira.css`; pares de cor novos entram no DS-08) · AD-011 (a F6 só lê `Inovacao.status`, nunca o escreve)
**Reusa da F2:** `inovacoes.Inovacao`, `inovacoes.Unidade`, `inovacoes.Categoria` e `inovacoes.StatusInovacao` sem valores novos · padrão de erro de formulário com `aria-invalid` e mensagem associada (RF13)
**Reusa da F3:** detalhe `/inovacoes/<id>/` e o 404 "Inovação não encontrada." (CONS-15) · conjunto de demonstração e a medição de tempo do RNF08 (CONS-46)
**Reusa da F4/F5:** padrão de página própria com POST e link "Cancelar" (EDEX-30, STAT-06) · mensagens do framework no detalhe (RF12)
**Altera a F3/F4/F5:** o detalhe ganha a seção "Reaproveitamentos" (REAP-17, REAP-18) e o link de sinalização (REAP-01) · o menu principal ganha "Indicadores" (REAP-28) · `CONSULTAS_DO_DETALHE` em `inovacoes/tests/test_views_detalhe.py` muda de 7 para o valor medido depois da seção nova · a allowlist da varredura de autoria ganha `inovacoes:reaproveitar` — alterações de teste antigo autorizadas na aprovação desta spec
**Status:** Aprovada pelo usuário em 2026-10-18 (assumptions confirmadas na aprovação) · Design aprovado em 2026-10-18 (AD-012) · Tasks aprovadas em 2026-10-18 · **Execute pausado em 2026-10-18**: RF11 implementado (T1–T10, ACs em `Implementing`), painel RF10 (T11–T18) não iniciado, Verifier ainda não rodou
**Escopo (auto-sizing):** **Large** — modelo e migration novos, duas telas novas, componentes novos na `kira.css` e testes de desempenho. Roda Design e Tasks formais.
**Contexto da discussão:** `.specs/features/reaproveitamento-indicadores/context.md`

> **Nota de notação:** como na F1 a F5, os critérios de aceite estão em EARS em inglês (WHEN /
> WHILE / WHERE / IF-THEN / ubíquo + SHALL); o restante do documento está em português. Textos
> exibidos ao usuário aparecem entre aspas, em português, exatamente como devem ser renderizados.

## Problem Statement

Uma inovação chega a "Disponível para replicação", mas o repositório não sabe se alguma unidade de
fato a copiou. Sem esse registro, a proposta do TCC — reduzir retrabalho pelo reaproveitamento entre
unidades — não tem número que a sustente, e quem consulta não vê quais soluções já foram adotadas em
outro lugar. A F6 deixa qualquer colaborador registrar que uma unidade reaproveitou uma inovação
disponível (RN09, RF11) e reúne num painel o total de inovações, a distribuição por categoria e por
unidade e a contagem de reaproveitamentos (RF10).

## Goals

- [ ] Qualquer usuário autenticado registra, a partir do detalhe de uma inovação "Disponível para
      replicação", que outra unidade a reaproveitou; o registro guarda inovação, unidade, responsável
      e data/hora.
- [ ] Nenhum caminho (tela, POST forjado, corrida) registra reaproveitamento de inovação fora de
      "Disponível para replicação", pela própria unidade de origem ou duas vezes pela mesma unidade.
- [ ] O detalhe mostra quantas e quais unidades reaproveitaram a inovação.
- [ ] O painel `/indicadores/` mostra total de inovações, total de reaproveitamentos e as distribuições
      por categoria e por unidade, cada uma em gráfico com rótulos de dado e em tabela acessível.
- [ ] Com o conjunto de demonstração carregado, o painel responde em até 2 segundos (RNF08).

## Out of Scope

Excluído explicitamente. Documentado para impedir scope creep.

| Feature | Reason |
| ------- | ------ |
| Unidade de lotação no modelo de usuário | Decidido com o usuário: a unidade é escolhida no formulário; `contas.Usuario` não muda. |
| Restringir a sinalização ao administrador ou ao autor | Decidido com o usuário: qualquer usuário autenticado. |
| Mais de uma sinalização da mesma unidade para a mesma inovação | Decidido com o usuário: uma por par (inovação, unidade). |
| Desfazer ou editar a sinalização pela interface comum | Correção só pelo administrador no Django admin (REAP-26). Registrado em Deferred Ideas. |
| Comentário ou descrição da adaptação feita pela unidade | Nenhum RF pede. Registrado em Deferred Ideas. |
| Ranking das inovações mais reaproveitadas | Não pedido no RF10 nem na solicitação. Registrado em Deferred Ideas. |
| Filtro do painel por período, unidade ou categoria | Não pedido. Registrado em Deferred Ideas. |
| Distribuição por status no painel | Não pedida no RF10; o filtro por status da listagem já responde. |
| Exportar indicadores (CSV, PDF) | Nenhum RF pede. |
| Gráficos interativos (hover, zoom) ou biblioteca de gráficos em JavaScript | Decidido: SVG gerado no servidor, sem dependência nova (AD-010). |
| Reaproveitamentos na carga de demonstração | O teste de desempenho cria os seus; a carga não muda. Registrado em Deferred Ideas. |
| Mudança de status da inovação | F5 (AD-011). A F6 só lê o status. |
| Auditoria WCAG completa, responsividade e teste SUS | Validação transversal no fim (RNF09, RNF03, RNF01). A F6 cobre a sinalização e o painel. |

---

## Assumptions & Open Questions

Toda ambiguidade está resolvida ou registrada aqui — nada fica silenciosamente indefinido.

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --------------------- | -------------- | --------- | ---------- |
| Origem da unidade que reaproveitou | Select obrigatório "Unidade que reaproveitou" na tela de sinalização | Decidido com o usuário (2026-10-18) | y |
| Unicidade | Um `Reaproveitamento` por par (inovação, unidade), imposto por restrição única no banco | Decidido com o usuário (2026-10-18) | y |
| Quem sinaliza | Todo usuário autenticado, autor ou não, de qualquer perfil | Decidido com o usuário (2026-10-18); RN09 fala em unidade, não em autoria | y |
| Conteúdo do painel | Cards, gráficos de barras com rótulos de dado e tabelas acessíveis | Decidido com o usuário (2026-10-18); design-spec §10 F6 | y |
| Tecnologia dos gráficos | SVG inline gerado pelo template no servidor, sem JavaScript nem pacote novo | Decidido com o usuário (2026-10-18); AD-010 (sem dependência nova, sem estáticos) | y |
| Unidade de origem | Fica fora das opções do select; um POST forjado com ela é recusado | RN09: "por outra unidade" | y |
| Dados do registro | `Reaproveitamento` com inovação, unidade, `registrado_por` (conta logada) e data/hora automática | modelagem-uml §2.1 mais o responsável, pelo mesmo critério da RN08 e da F5 | y |
| Rota da sinalização | `/inovacoes/<id>/reaproveitar/`: GET mostra o formulário, POST registra | Mesmo padrão de `/editar/`, `/excluir/` e `/status/` | y |
| Confirmação extra | Não há: escolher a unidade e enviar o formulário já é a ação explícita; "Cancelar" volta ao detalhe | A sinalização não destrói nada e o administrador pode excluí-la (REAP-26); RN12 cobre ação destrutiva | y |
| Link fora de "Disponível para replicação" | Ausente, não desabilitado | design-spec §10 F6: "só aparece em inovação 'Disponível para replicação'" | y |
| Inovação fora de "Disponível" na rota | GET e POST redirecionam ao detalhe com aviso; nada é gravado | Explica por que nada aconteceu (H9), como o conflito da F5 | y |
| Sem unidade disponível | Se todas as outras unidades já sinalizaram (ou só existe a de origem), a página explica e não mostra formulário | Evita select vazio sem explicação (H1) | y |
| Exclusão da inovação | Apaga os reaproveitamentos dela; os totais do painel caem junto | A exclusão da F4 é definitiva; mesmo critério do histórico da F5 | y |
| Exclusão de unidade e de conta | Unidade e conta referenciadas por um reaproveitamento ficam protegidas | Mesmo critério de `Inovacao.unidade` (INOV-19) e `Inovacao.autor` | y |
| Correção de sinalização errada | Django admin, só `ADMINISTRADOR` (AD-007), só listar e excluir; sem incluir nem editar | Incluir pelo admin contornaria a RN09 e a unidade de origem | y |
| Seção no detalhe | "Reaproveitamentos" com a contagem e a lista de unidades, do registro mais antigo ao mais recente | Torna o reuso visível a quem consulta, sem ir ao painel | y |
| Acesso ao painel | Todo usuário autenticado, pelo link "Indicadores" do menu principal | RN04: consulta para qualquer autenticado | y |
| Totais do painel | "Inovações cadastradas" = todas as inovações, qualquer status; "Reaproveitamentos registrados" = todos os registros | RF10: "total" sem recorte | y |
| Distribuição por categoria | Uma linha por `Categoria` cadastrada, inclusive com zero; ordem: contagem decrescente, depois nome | Lista controlada: o zero também informa (onde não há inovação) | y |
| Distribuição por unidade | Uma linha por `Unidade`, inclusive com zero, com "Inovações de origem" e "Reaproveitamentos feitos"; ordem: inovações de origem decrescente, depois nome | Responde "quais unidades produzem" e "quais unidades reaproveitam" na mesma tabela | y |
| Gráficos | Três gráficos de barras horizontais: inovações por categoria, inovações de origem por unidade, reaproveitamentos feitos por unidade; mesma ordem das linhas da tabela | Um gráfico por série numérica das tabelas | y |
| Escala das barras | Comprimento proporcional ao valor sobre o maior valor do gráfico; o maior ocupa 100% da área; valor 0 não desenha barra, mas mantém nome e "0" | Regra determinística e testável; evita divisão por zero | y |
| Painel vazio | Sem nenhuma inovação, os cards mostram "0" e, no lugar de gráficos e tabelas, "Nenhuma inovação cadastrada ainda." com o link "Cadastrar inovação" | design-spec §7, estado vazio | y |
| Medição do RNF08 | Tempo de servidor do GET em `/indicadores/` com o conjunto de demonstração mais 200 reaproveitamentos criados pelo teste; número de consultas ao banco que não cresce com o volume | Mesmo método da CONS-46; o número fixo de consultas protege contra N+1 | y |
| Atualização dos números | Calculados a cada requisição, sem cache | Volume do MVP; o RNF08 é verificado por teste | y |

**Open questions:** none — todas resolvidas ou registradas acima; os defaults do agente foram confirmados na aprovação desta spec (2026-10-18).

---

## Dimensions Sweep

Escopo Large ⇒ varredura completa: cada dimensão vira requisito ou recebe `N/A because…` explícito.

| Dimensão | Resolução |
| -------- | --------- |
| Input validation & bounds | REAP-11 (unidade de origem), REAP-12 (unidade repetida), REAP-13 (unidade ausente, inexistente ou não numérica), REAP-16 (inovação inexistente → 404). Nenhum campo livre: **N/A** de limite de tamanho. |
| Failure / partial-failure states | REAP-49 (banco indisponível → 500, nada gravado). Um único INSERT por sinalização: **N/A** de gravação parcial. |
| Idempotency / retry / duplicate handling | REAP-12 e REAP-14 (segundo envio da mesma unidade não cria registro), REAP-08 (GET nunca grava). |
| Auth boundaries & rate limits | REAP-19 (qualquer autenticado sinaliza), REAP-20 e REAP-40 (anônimo vai ao login), REAP-21 (CSRF), REAP-22 (responsável é sempre a conta logada), REAP-26 e REAP-27 (admin só para `ADMINISTRADOR`, sem incluir nem editar). Rate limits: **N/A because** nenhum RN/RNF exige e a unicidade por unidade já limita o volume por inovação. |
| Concurrency / ordering | REAP-14 (duas sinalizações simultâneas da mesma unidade: uma grava, a outra recebe a mensagem da REAP-12, sem 500). A ordem da lista do detalhe é a da gravação (REAP-18). O status não regride (AD-011), então não há corrida de status a tratar. |
| Data lifecycle / expiry | REAP-23 (apagados com a inovação), REAP-24 (unidade protegida), REAP-25 (conta protegida), REAP-26 (exclusão pelo administrador). Expiração: **N/A because** o reaproveitamento é fato histórico sem prazo. |
| Observability | O próprio `Reaproveitamento` (com responsável e data) é o registro observável. Log técnico: **N/A because** nenhum RNF pede. |
| External-dependency failure | REAP-49 (PostgreSQL indisponível). **N/A** para outros serviços: a F6 não chama nenhum. |
| State-transition integrity | REAP-09 e REAP-10 (só inovação "Disponível para replicação"), REAP-07 (a sinalização não muda o status nem outro campo da inovação). |

---

## User Stories

### P1: Sinalizar que uma unidade reaproveitou a inovação ⭐ MVP

**User Story**: Como colaborador de uma unidade, quero registrar que minha unidade reaproveitou uma
inovação disponível, para que o repositório mostre que a solução foi adotada em outro lugar.

**Why P1**: RF11 e RN09; é o dado que alimenta a métrica de reuso e o painel.

**Acceptance Criteria**:

1. **REAP-01** — WHILE the Inovacao's status is "Disponível para replicação" the system SHALL display on its detail page, to every authenticated user, a link labeled "Sinalizar reaproveitamento" pointing to `/inovacoes/<id>/reaproveitar/`.
2. **REAP-02** — WHILE the Inovacao's status is "Em teste" or "Validada" the system SHALL NOT display on its detail page any link or button pointing to `/inovacoes/<id>/reaproveitar/` nor the text "Sinalizar reaproveitamento", for any user.
3. **REAP-03** — WHEN an authenticated user requests `/inovacoes/<id>/reaproveitar/` for an Inovacao in "Disponível para replicação" with at least one eligible Unidade THEN the system SHALL respond with HTTP 200 and a page whose `<title>` starts with "Sinalizar reaproveitamento", showing the text "Registre a unidade que reaproveitou a inovação “<título>”, criada na unidade “<unidade de origem>”.", a required select labeled "Unidade que reaproveitou", a submit button "Sinalizar reaproveitamento" and a link "Cancelar" pointing to `/inovacoes/<id>/`.
4. **REAP-04** — The system SHALL offer in the "Unidade que reaproveitou" select every Unidade in alphabetical order except the Inovacao's unidade de origem and except every Unidade that already has a Reaproveitamento for this Inovacao, with no option preselected.
5. **REAP-05** — WHEN an authenticated user submits the form with an eligible Unidade THEN the system SHALL store exactly one Reaproveitamento with that Inovacao, that Unidade, `registrado_por` equal to the logged-in user and `data` equal to the server's current date and time, and SHALL respond with HTTP 302 to `/inovacoes/<id>/`.
6. **REAP-06** — WHEN a Reaproveitamento is stored THEN the system SHALL display on the next page, exactly once, the success message "Reaproveitamento da inovação “<título>” pela unidade “<unidade>” registrado."
7. **REAP-07** — WHEN a Reaproveitamento is stored THEN the system SHALL keep every field of the Inovacao unchanged, including `status`, `autor`, `data_criacao` and `texto_busca`.
8. **REAP-08** — WHEN an authenticated user sends GET to `/inovacoes/<id>/reaproveitar/` THEN the system SHALL NOT store any Reaproveitamento.

**Independent Test**: como `maria`, abrir uma inovação do `joao` em "Disponível para replicação",
clicar "Sinalizar reaproveitamento", escolher uma unidade diferente da origem, enviar e ver a mensagem
de sucesso no detalhe.

---

### P1: Só inovação disponível, só outra unidade, uma vez por unidade ⭐ MVP

**User Story**: Como gestor que lê a métrica de reuso, quero que cada reaproveitamento contado seja
de uma inovação pronta para replicação, feito por outra unidade e contado uma vez, para que o número
signifique adoção real.

**Why P1**: RN09; sem essas guardas a métrica do RF10 perde o sentido.

**Acceptance Criteria**:

1. **REAP-09** — IF an authenticated user sends GET or POST to `/inovacoes/<id>/reaproveitar/` for an Inovacao whose status is "Em teste" or "Validada" THEN the system SHALL store no Reaproveitamento, SHALL respond with HTTP 302 to `/inovacoes/<id>/` and SHALL display, exactly once, the warning message "Só uma inovação “Disponível para replicação” pode ser sinalizada como reaproveitada. Status atual: “<status atual>”."
2. **REAP-10** — IF application code asks the model layer to register a Reaproveitamento for an Inovacao whose status is not "Disponível para replicação" THEN the system SHALL raise a validation error and SHALL store no Reaproveitamento.
3. **REAP-11** — IF a POST to `/inovacoes/<id>/reaproveitar/` carries the Inovacao's unidade de origem THEN the system SHALL store no Reaproveitamento and SHALL re-render the form with HTTP 200 and the field error "A unidade de origem não pode reaproveitar a própria inovação."
4. **REAP-12** — IF a POST to `/inovacoes/<id>/reaproveitar/` carries a Unidade that already has a Reaproveitamento for this Inovacao THEN the system SHALL store no Reaproveitamento and SHALL re-render the form with HTTP 200 and the field error "A unidade “<unidade>” já sinalizou o reaproveitamento desta inovação."
5. **REAP-13** — IF a POST to `/inovacoes/<id>/reaproveitar/` carries no Unidade, an id of a nonexistent Unidade or a non-numeric value THEN the system SHALL store no Reaproveitamento and SHALL re-render the form with HTTP 200 and the field error "Selecione a unidade que reaproveitou a inovação."
6. **REAP-14** — The system SHALL keep at most one Reaproveitamento per (Inovacao, Unidade) pair through a database unique constraint, and IF two concurrent submissions for the same pair reach the database THEN the system SHALL store exactly one and SHALL answer the other with the outcome of REAP-12 instead of HTTP 500.
7. **REAP-15** — WHILE the Inovacao is in "Disponível para replicação" and no eligible Unidade remains (every Unidade other than the origin already has a Reaproveitamento for it, or no other Unidade exists) the system SHALL answer GET to `/inovacoes/<id>/reaproveitar/` with HTTP 200, the text "Todas as outras unidades já sinalizaram o reaproveitamento desta inovação.", a link "Voltar para a inovação" to `/inovacoes/<id>/`, and no select nor submit button.
8. **REAP-16** — IF `/inovacoes/<id>/reaproveitar/` is requested with the id of a nonexistent Inovacao THEN the system SHALL respond with HTTP 404 and the message "Inovação não encontrada." (CONS-15).

**Independent Test**: com uma inovação em "Validada", abrir `/inovacoes/<id>/reaproveitar/` pela
barra de endereço e ver o aviso no detalhe; numa inovação disponível, forjar POST com a unidade de
origem e com uma unidade que já sinalizou e ver os erros de campo, sem registro novo.

---

### P1: Ver no detalhe quem reaproveitou ⭐ MVP

**User Story**: Como colaborador que consulta uma inovação, quero ver quais unidades já a
reaproveitaram, para saber a quem perguntar como foi a adoção.

**Why P1**: torna o RF11 visível sem ir ao painel; é onde a sinalização dá retorno (H1).

**Acceptance Criteria**:

1. **REAP-17** — WHEN an authenticated user requests `/inovacoes/<id>/` THEN the system SHALL display a section with the heading "Reaproveitamentos" containing "Nenhum reaproveitamento registrado." when the Inovacao has none, "Reaproveitada por 1 unidade." when it has one, and "Reaproveitada por <N> unidades." when it has N ≥ 2.
2. **REAP-18** — WHILE the Inovacao has at least one Reaproveitamento the system SHALL list in the "Reaproveitamentos" section one item per Reaproveitamento, from the oldest to the newest by `data` (id breaks ties), each with the text "<unidade> — <dd/mm/aaaa>".

**Independent Test**: depois de duas sinalizações de unidades diferentes, o detalhe mostra
"Reaproveitada por 2 unidades." e as duas unidades na ordem em que foram registradas.

---

### P1: Quem pode sinalizar e integridade do registro ⭐ MVP

**User Story**: Como colaborador de qualquer unidade, quero sinalizar o reaproveitamento sem precisar
ser o autor, e como administrador quero que o registro seja confiável e corrigível.

**Why P1**: RN04, RNF07 e as decisões de acesso desta feature; o registro precisa de responsável fiel.

**Acceptance Criteria**:

1. **REAP-19** — The system SHALL allow every authenticated user — `USUARIO` or `ADMINISTRADOR`, author of the Inovacao or not — to GET and POST `/inovacoes/<id>/reaproveitar/` with the outcomes of REAP-03 to REAP-15, never HTTP 403 for lack of authorship.
2. **REAP-20** — IF an anonymous visitor sends GET or POST to `/inovacoes/<id>/reaproveitar/` THEN the system SHALL redirect to the login page with the `next` parameter and SHALL store no Reaproveitamento.
3. **REAP-21** — IF a POST to `/inovacoes/<id>/reaproveitar/` lacks a valid CSRF token THEN the system SHALL respond with HTTP 403 and SHALL store no Reaproveitamento.
4. **REAP-22** — The system SHALL set `registrado_por` to the logged-in user and `data` to the server time, ignoring any value for `registrado_por`, `data` or `inovacao` sent in the POST body.
5. **REAP-23** — WHEN an Inovacao is deleted THEN the system SHALL delete every Reaproveitamento of that Inovacao.
6. **REAP-24** — IF an administrator tries to delete a Unidade referenced by a Reaproveitamento THEN the system SHALL refuse the deletion and keep the Unidade and the Reaproveitamento.
7. **REAP-25** — IF anyone tries to delete a user account referenced as `registrado_por` of a Reaproveitamento THEN the system SHALL refuse the deletion and keep the account and the Reaproveitamento.

**Independent Test**: como `maria` (`USUARIO`), sinalizar em inovação do `joao` e ver o registro com
`maria` como responsável; sair e abrir a rota anônimo, sendo levado ao login.

---

### P2: Corrigir uma sinalização errada

**User Story**: Como administrador, quero excluir uma sinalização registrada por engano, para manter
a métrica fiel.

**Why P2**: sem desfazer na tela comum, um erro ficaria permanente; o MVP funciona sem, mas a curadoria
é do administrador (RN05, por analogia).

**Acceptance Criteria**:

1. **REAP-26** — WHERE the Django admin is used, the system SHALL list Reaproveitamento records (inovação, unidade, responsável, data) and allow deleting them only to `ADMINISTRADOR` accounts, and SHALL deny the Reaproveitamento admin pages to `USUARIO` accounts even with `is_staff` or `is_superuser` (AD-007).
2. **REAP-27** — WHERE the Django admin is used, the system SHALL NOT offer adding or changing a Reaproveitamento to any account, and a direct request to the admin add or change URL SHALL NOT store or alter a record.

**Independent Test**: como `admin`, excluir no Django admin uma sinalização; como `maria` com
`is_staff`, abrir a URL do admin de reaproveitamentos e ser recusada.

---

### P1: Painel de indicadores ⭐ MVP

**User Story**: Como gestor do repositório, quero um painel com o total de inovações, a distribuição
por categoria e por unidade e a contagem de reaproveitamentos, para medir a adoção da proposta.

**Why P1**: RF10 e o eixo 3 do ENADE (BI/dashboards); é o objetivo "apoiar a gestão do conhecimento".

**Acceptance Criteria**:

1. **REAP-28** — The system SHALL display in the main navigation (`nav` "Principal") of every page that extends the base template, for authenticated users, a link labeled "Indicadores" pointing to `/indicadores/`.
2. **REAP-29** — WHEN an authenticated user requests `/indicadores/` THEN the system SHALL respond with HTTP 200, a `<title>` starting with "Painel de indicadores" and an `h1` "Painel de indicadores".
3. **REAP-30** — The system SHALL display on `/indicadores/` a metric card labeled "Inovações cadastradas" whose value is the count of all Inovacao records, of any status.
4. **REAP-31** — The system SHALL display on `/indicadores/` a metric card labeled "Reaproveitamentos registrados" whose value is the count of all Reaproveitamento records.
5. **REAP-32** — WHILE at least one Inovacao exists the system SHALL display on `/indicadores/` a table with caption "Inovações por categoria", column headers "Categoria" and "Inovações", and one row per Categoria (including those with 0), ordered by count descending and then by name ascending.
6. **REAP-33** — WHILE at least one Inovacao exists the system SHALL display on `/indicadores/` a table with caption "Inovações por unidade", column headers "Unidade", "Inovações de origem" and "Reaproveitamentos feitos", and one row per Unidade (including those with 0 in both columns), where "Inovações de origem" counts Inovacao records with that unidade and "Reaproveitamentos feitos" counts Reaproveitamento records with that unidade, ordered by "Inovações de origem" descending and then by name ascending.
7. **REAP-34** — WHILE at least one Inovacao exists the system SHALL display on `/indicadores/` three horizontal bar charts titled "Inovações por categoria", "Inovações de origem por unidade" and "Reaproveitamentos feitos por unidade", each with one bar per row of the corresponding table column, in the same order as the table.
8. **REAP-35** — The system SHALL draw each bar with length proportional to its value divided by the largest value of its chart, the largest value filling 100% of the plot width, and SHALL draw no bar for a value of 0; WHILE every value of a chart is 0 the system SHALL draw no bars in it.
9. **REAP-36** — The system SHALL show next to every bar, as visible text, the item name and its numeric value (including "0"), so that no value depends on bar length or color alone.
10. **REAP-37** — WHILE no Inovacao exists the system SHALL display on `/indicadores/` both metric cards with the value "0", the text "Nenhuma inovação cadastrada ainda." and a link "Cadastrar inovação" pointing to `/inovacoes/nova/`, and SHALL NOT display the tables nor the charts.
11. **REAP-38** — WHEN `/indicadores/` is requested THEN the system SHALL compute every number from the database state at that request, so that a Reaproveitamento stored or an Inovacao created or deleted just before appears in the next response.
12. **REAP-39** — The system SHALL compute the indicators without changing any Inovacao, Reaproveitamento, Categoria or Unidade.
13. **REAP-40** — IF an anonymous visitor requests `/indicadores/` THEN the system SHALL redirect to the login page with the `next` parameter.

**Independent Test**: com o banco local, abrir "Indicadores" no menu e conferir que o card "Inovações
cadastradas" bate com o total da listagem; sinalizar um reaproveitamento e ver o card
"Reaproveitamentos registrados" e a linha da unidade subirem em 1.

---

### P2: Desempenho do painel e do detalhe (RNF08)

**User Story**: Como usuário, quero que o painel e o detalhe abram sem espera perceptível, mesmo com o
conjunto de demonstração carregado.

**Why P2**: RNF08 é Desejável, mas o critério de 2 s já é medido na F3 e vale para as telas novas.

**Acceptance Criteria**:

1. **REAP-41** — WHILE the demonstration set and 200 Reaproveitamento records created by the test are loaded the system SHALL answer an authenticated GET of `/indicadores/` within 2 seconds of server time.
2. **REAP-42** — The system SHALL answer an authenticated GET of `/indicadores/` with a number of database queries that does not change when the number of Inovacao, Categoria, Unidade or Reaproveitamento records grows.
3. **REAP-43** — The system SHALL answer an authenticated GET of `/inovacoes/<id>/` with a number of database queries that does not change when the number of Reaproveitamento records of that Inovacao grows.

**Independent Test**: `pytest` com o conjunto de demonstração; medir o painel com 1 e com 50
reaproveitamentos e ver o mesmo número de consultas.

---

### P1: Sinalização e painel acessíveis ⭐ MVP

**User Story**: Como colaborador que usa teclado ou leitor de tela, quero sinalizar e ler os
indicadores sem depender de cor ou de mouse.

**Why P1**: RNF09 é Essencial; design-spec §10 F6 pede alternativa em tabela e gráfico sem dependência de cor.

**Acceptance Criteria**:

1. **REAP-44** — The system SHALL associate the "Unidade que reaproveitou" select with its visible label through `for`/`id`.
2. **REAP-45** — IF the sinalização form is re-rendered with a field error THEN the system SHALL mark the select with `aria-invalid="true"` and `aria-describedby` pointing to the element that contains the error message.
3. **REAP-46** — The system SHALL render each indicator table with a `caption`, column headers as `th scope="col"` and the first cell of each row as `th scope="row"`.
4. **REAP-47** — The system SHALL give each chart `role="img"` and an accessible name equal to its title, and SHALL keep the corresponding table on the same page as its text alternative.
5. **REAP-48** — The system SHALL style the metric cards and the bar charts only through `kira.css` components (AD-010), with text contrast of at least 4.5:1 and bar-to-background contrast of at least 3:1, every new color pair registered in the DS-08 contrast test.

**Independent Test**: navegar só com Tab do menu até "Indicadores" e da inovação até o botão
"Sinalizar reaproveitamento"; ler o painel com o CSS desligado e entender todos os números.

---

## Edge Cases

- **REAP-49** — IF the database is unreachable while a Reaproveitamento is being registered or the indicators are being computed THEN the system SHALL respond with the project's HTTP 500 page, SHALL store no Reaproveitamento and SHALL NOT expose connection details.
- Inovação cadastrada já "Disponível para replicação" pela carga de demonstração (sem histórico de status): pode ser sinalizada normalmente; a RN09 olha o status gravado (REAP-01, REAP-09).
- Inovação excluída entre abrir o formulário e enviá-lo: 404 da CONS-15, sem registro (REAP-16).
- Duplo clique no botão: o segundo POST chega com a mesma unidade e cai no erro da REAP-12 (REAP-14).
- Só existe a unidade de origem no cadastro: a página mostra a mensagem da REAP-15.
- Unidade renomeada no admin: a lista do detalhe e o painel mostram o nome atual (leitura pela FK).
- Categoria ou unidade sem nenhuma inovação: aparece na tabela com 0 e no gráfico com nome e "0", sem barra (REAP-32, REAP-33, REAP-35).
- Autor da inovação sinaliza a própria inovação por outra unidade: permitido; só a unidade de origem é recusada (REAP-11, REAP-19).
- Id não numérico em `/inovacoes/abc/reaproveitar/`: a rota não casa e cai no 404 padrão, como na F4 e na F5.

---

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
| -------------- | ----- | ----- | ------ |
| REAP-01 | P1: Sinalizar | Tasks | Implementing |
| REAP-02 | P1: Sinalizar | Tasks | Implementing |
| REAP-03 | P1: Sinalizar | Tasks | Implementing |
| REAP-04 | P1: Sinalizar | Tasks | Implementing |
| REAP-05 | P1: Sinalizar | Tasks | Implementing |
| REAP-06 | P1: Sinalizar | Tasks | Implementing |
| REAP-07 | P1: Sinalizar | Tasks | Implementing |
| REAP-08 | P1: Sinalizar | Tasks | Implementing |
| REAP-09 | P1: Guardas da RN09 | Tasks | Implementing |
| REAP-10 | P1: Guardas da RN09 | Tasks | Implementing |
| REAP-11 | P1: Guardas da RN09 | Tasks | Implementing |
| REAP-12 | P1: Guardas da RN09 | Tasks | Implementing |
| REAP-13 | P1: Guardas da RN09 | Tasks | Implementing |
| REAP-14 | P1: Guardas da RN09 | Tasks | Implementing |
| REAP-15 | P1: Guardas da RN09 | Tasks | Implementing |
| REAP-16 | P1: Guardas da RN09 | Tasks | Implementing |
| REAP-17 | P1: Detalhe | Tasks | Implementing |
| REAP-18 | P1: Detalhe | Tasks | Implementing |
| REAP-19 | P1: Acesso e integridade | Tasks | Implementing |
| REAP-20 | P1: Acesso e integridade | Tasks | Implementing |
| REAP-21 | P1: Acesso e integridade | Tasks | Implementing |
| REAP-22 | P1: Acesso e integridade | Tasks | Implementing |
| REAP-23 | P1: Acesso e integridade | Tasks | Implementing |
| REAP-24 | P1: Acesso e integridade | Tasks | Implementing |
| REAP-25 | P1: Acesso e integridade | Tasks | Implementing |
| REAP-26 | P2: Correção pelo administrador | Tasks | Implementing |
| REAP-27 | P2: Correção pelo administrador | Tasks | Implementing |
| REAP-28 | P1: Painel | Tasks | In Tasks |
| REAP-29 | P1: Painel | Tasks | In Tasks |
| REAP-30 | P1: Painel | Tasks | In Tasks |
| REAP-31 | P1: Painel | Tasks | In Tasks |
| REAP-32 | P1: Painel | Tasks | Implementing |
| REAP-33 | P1: Painel | Tasks | Implementing |
| REAP-34 | P1: Painel | Tasks | In Tasks |
| REAP-35 | P1: Painel | Tasks | In Tasks |
| REAP-36 | P1: Painel | Tasks | In Tasks |
| REAP-37 | P1: Painel | Tasks | In Tasks |
| REAP-38 | P1: Painel | Tasks | In Tasks |
| REAP-39 | P1: Painel | Tasks | In Tasks |
| REAP-40 | P1: Painel | Tasks | In Tasks |
| REAP-41 | P2: Desempenho | Tasks | In Tasks |
| REAP-42 | P2: Desempenho | Tasks | In Tasks |
| REAP-43 | P2: Desempenho | Tasks | Implementing |
| REAP-44 | P1: Acessibilidade | Tasks | Implementing |
| REAP-45 | P1: Acessibilidade | Tasks | Implementing |
| REAP-46 | P1: Acessibilidade | Tasks | In Tasks |
| REAP-47 | P1: Acessibilidade | Tasks | In Tasks |
| REAP-48 | P1: Acessibilidade | Tasks | Implementing |
| REAP-49 | Edge Cases | Tasks | Implementing |

**Coverage:** 49 total, 49 mapped to tasks (T1–T18, ver `tasks.md` → Requirement Coverage), 0 unmapped

---

## Rastreabilidade com o Documento de Requisitos

| Requisito | Critérios |
| --------- | --------- |
| RF11 | REAP-01, REAP-03 … REAP-08, REAP-17, REAP-18 |
| RN09 | REAP-02, REAP-04, REAP-09 … REAP-15 |
| RF10 | REAP-28 … REAP-40 |
| RNF08 | REAP-41, REAP-42, REAP-43 |
| RF12 | REAP-06, REAP-09 |
| RF13 | REAP-11, REAP-12, REAP-13, REAP-45 |
| RF14 | REAP-03 (Cancelar), REAP-15 (Voltar) |
| RN04 / RNF07 | REAP-19, REAP-20, REAP-21, REAP-26, REAP-27, REAP-40 |
| RN07 | REAP-04 (select da lista controlada) |
| RN08 (por analogia) | REAP-05, REAP-22 |
| RNF05 | REAP-14, REAP-23, REAP-24, REAP-25 |
| RNF09 | REAP-36, REAP-44 … REAP-48 |
| RNF01 (Nielsen) | H1: REAP-06, REAP-17, REAP-15 · H3: REAP-03 · H5: REAP-04, REAP-11, REAP-12 · H8: REAP-30, REAP-31 · H9: REAP-09, REAP-11 … REAP-13 |

---

## Success Criteria

- [ ] Uma inovação "Disponível para replicação" recebe sinalizações de duas unidades diferentes da
      origem, e o detalhe e o painel mostram as duas.
- [ ] Nenhum caminho (tela, POST forjado, duplo envio) registra reaproveitamento de inovação fora de
      "Disponível para replicação", pela unidade de origem ou repetido pela mesma unidade — provado
      por teste automatizado para cada caso.
- [ ] Os números do painel batem com contagens feitas direto no banco, inclusive com categorias e
      unidades zeradas.
- [ ] Com o conjunto de demonstração e 200 reaproveitamentos, o painel responde em até 2 segundos e
      com número fixo de consultas.
- [ ] Todo número do painel é legível sem cor e sem os gráficos, pela tabela correspondente.
