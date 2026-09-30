# Cadastro de Inovação (F2) — Specification

**Fontes:** `docs/requisitos.md` (RF02, RF12, RF13, RF14, RF15, RN01, RN02, RN03, RN06, RN07, RN08, RN10, RNF01, RNF05, RNF09; seção 5, Estrutura de Dados) · `docs/mapa-de-features.md` (F2) · `docs/modelagem-uml.md` (classes Inovacao, Unidade, Categoria, StatusInovacao)
**Decisões vinculantes:** AD-002 (MVT sem Service Layer) · AD-003 (PostgreSQL, integridade no banco) · AD-005 (autor via `settings.AUTH_USER_MODEL`) · AD-006 (acesso negado por padrão)
**Reusa da F1:** `contas.Usuario` como autor · `is_administrador` como ponto único de consulta do perfil (AUTH-19) · página 500 sem vazamento (AUTH-26) · região de mensagens `role="status"` do `templates/base.html`
**Status:** Aprovada pelo usuário em 2026-09-27 (assumptions confirmadas na aprovação) · implementada e verificada em 2026-09-29 (`validation.md`, iteração 2)
**Contexto da discussão:** `.specs/features/cadastro-inovacao/context.md`

> **Nota de notação:** como na F1, os critérios de aceite estão em EARS em inglês (WHEN / WHILE /
> WHERE / IF-THEN / ubíquo + SHALL); o restante do documento está em português. Textos exibidos ao
> usuário aparecem entre aspas, em português, exatamente como devem ser renderizados.

## Problem Statement

As unidades da organização resolvem problemas de back office parecidos sem saber que outra unidade já
resolveu. Não há hoje onde registrar uma solução de forma estruturada: sem registro não há o que
consultar (F3), editar (F4), evoluir no ciclo de vida (F5) nem reaproveitar (F6). A F2 cria a entidade
central do domínio e o único caminho para ela nascer — um formulário que valida os dados, ajuda a
corrigir erros sem perder o que foi digitado e deixa autor, data e status a cargo do sistema.

## Goals

- [x] Um usuário autenticado, de qualquer perfil, registra uma inovação completa pelo formulário em uma
      única submissão válida, e o registro fica persistido no PostgreSQL com autor, data de criação e
      status `Em teste` definidos pelo sistema.
- [x] Nenhuma submissão inválida grava registro, e toda submissão inválida devolve o formulário com a
      mensagem de erro no campo afetado e todos os valores já digitados preservados.
- [x] Nenhum par de inovações na mesma unidade tem títulos iguais sem distinção de maiúsculas e
      minúsculas — garantido pelo banco, não só pelo formulário.
- [x] Unidade e categoria de toda inovação vêm de listas controladas mantidas somente pelo perfil
      `ADMINISTRADOR`.

## Out of Scope

Excluído explicitamente. Documentado para impedir scope creep.

| Feature | Reason |
| ------- | ------ |
| Listagem, busca, filtros e página de detalhe de inovações | F3 (RF03–RF06). Enquanto a F3 não existir, o destino após o cadastro é a home interna. |
| Edição e exclusão de inovações; autorização por autoria (RN05) | F4 (RF07, RF08). |
| Alteração de status após o cadastro | F5 (RF09). A F2 só fixa o status inicial. |
| Cadastro, edição ou exclusão de inovações pelo Django admin | Contornaria a autoria (RN08) e, mais tarde, a RN05 da F4. A `Inovacao` não é registrada no admin. |
| Rascunho / salvamento parcial / autosave | Nenhum RF pede. RF13 é atendido preservando os dados na resposta de erro. |
| Anexos, imagens, tags ou campos além da seção 5 do documento de requisitos | Não constam na estrutura de dados do MVP. |
| Confirmação ao cancelar com formulário preenchido | O RF14 exige confirmação só em ação destrutiva ou irreversível (RN12); cancelar um cadastro não grava nada. Mantém o formulário sem JavaScript. |
| Comparação de título que ignora acentos | Decidido com o usuário: exigiria a extensão `unaccent` no deploy (RNF06). |
| Avaliação heurística completa e teste SUS (RNF01) | Transversais, validados no fim do projeto (`docs/mapa-de-features.md`). A F2 contribui com RF12, RF13, RF14 e RF15. |
| Auditoria WCAG completa (contraste, responsividade) | RNF09 e RNF03 têm auditoria final dedicada. A F2 cobre o que é do formulário: rótulos, teclado, foco visível, erros acessíveis. |

---

## Assumptions & Open Questions

Toda ambiguidade está resolvida ou registrada aqui — nada fica silenciosamente indefinido.

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --------------------- | -------------- | --------- | ---------- |
| Representação de Unidade e Categoria | Tabelas próprias (modelos), não enum nem texto livre | Decidido com o usuário; segue a UML e a RN07 | y |
| Quem mantém as listas | Somente `ADMINISTRADOR`, pelo Django admin; demais perfis recebem 403 nessas telas | Decidido com o usuário; mesmo padrão da AUTH-22 | y |
| Valores iniciais das listas | Criados por data migration. Categorias: Atendimento interno, Compras, Financeiro, RH, TI interno. Unidades (provisórias): Filial Leste, Filial Norte, Filial Oeste, Filial Sul, Sede | Decidido com o usuário; categorias da seção 5 dos requisitos; unidades provisórias renomeáveis pelo admin | y |
| Critério de "título idêntico" (RN10) | Mesma unidade + mesmo título ignorando maiúsculas/minúsculas, após remover espaços nas pontas; acentos contam | Decidido com o usuário; mesmo critério do e-mail na F1; garantido por constraint no banco | y |
| Contato responsável | Texto livre obrigatório, pré-preenchido com "Nome Completo (e-mail)" do autor — ou "username (e-mail)" quando a conta não tem nome — e editável | Decidido com o usuário; cobre o caso comum sem prender o contato ao autor | y |
| Ajuda contextual (RF15) | Entra na F2 como P3: texto de apoio com exemplo em cada campo, associado ao campo | Decidido com o usuário; o mapa aloca RF15 aos formulários da F2 | y |
| Item de lista em uso | Não pode ser excluído (o admin informa o motivo); renomear é permitido | Integridade referencial (RNF05, AD-003); renomear não quebra vínculo | y |
| Ordem das opções nas listas | Alfabética pelo nome | Reconhecimento em vez de memorização (Nielsen H6) | y |
| Limites de tamanho | Título ≤ 150 caracteres; contato ≤ 150; problema, solução e resultado ≤ 5.000 cada | Nenhum requisito fixa valor; título curto por definição ("nome curto e descritivo"); teto nos textos longos evita abuso | y |
| Espaços em branco | Campo obrigatório preenchido só com espaços conta como vazio; espaços nas pontas são removidos antes de salvar | RN02 exige conteúdo, não caracteres | y |
| Ponto de entrada | Link "Cadastrar inovação" no cabeçalho de toda página para usuário autenticado; rota `/inovacoes/nova/` | Visível de qualquer tela (Nielsen H1/H6); a rota concreta torna os critérios testáveis | y |
| Destino após cadastro bem-sucedido | Redireciona (302) à home interna, com a mensagem de sucesso. Quando a F3 existir, ela redefine o destino | A página de detalhe é da F3; redirecionar após POST evita reenvio ao recarregar | y |
| Texto da mensagem de sucesso (RF12) | "Inovação “<título>” cadastrada com sucesso." | Diz o que aconteceu e com qual registro (Nielsen H1) | y |
| Feedback de falha (RF12) | Resumo no topo do formulário: "Não foi possível salvar a inovação. Corrija os campos indicados.", além das mensagens por campo | RF12 pede feedback de sucesso e de falha; o resumo orienta leitor de tela e teclado | y |
| Mensagens de campo obrigatório (RF13) | Título: "Informe o título da inovação." · Unidade: "Selecione a unidade de origem." · Categoria: "Selecione a categoria." · Problema: "Descreva o problema ou dor." · Solução: "Descreva a solução aplicada." · Contato: "Informe o contato responsável." | RF13 pede indicar o campo e como corrigir; texto fixo torna o teste determinístico | y |
| Mensagem de título duplicado | "Já existe uma inovação com este título nesta unidade. Escolha outro título." | Diz o problema e a correção (Nielsen H9) | y |
| Mensagem de valor fora da lista | "Selecione uma unidade da lista." / "Selecione uma categoria da lista." | RF13; só ocorre com POST adulterado ou item removido entre GET e POST | y |
| Mensagem de tamanho excedido | "Use no máximo N caracteres (você digitou M)." com os valores reais | RF13: indica o limite e quanto passou | y |
| Cancelar (RF14) | Link "Cancelar" que leva à home interna sem gravar nada e sem pedir confirmação | Não é ação destrutiva (RN12 não se aplica); funciona sem JavaScript | y |
| Duplo envio | Nenhum mecanismo próprio: o segundo POST idêntico é recusado pela RN10 com a mensagem de título duplicado | A RN10 já é a chave de deduplicação; evita token extra | y |
| Idioma dos critérios de aceite | EARS em inglês, restante em português | Mesmo padrão da F1; `validate_spec.py` exige `SHALL` | y |

**Open questions:** none - todas resolvidas com o usuário ou registradas como assumption acima.

---

## Dimensions Sweep

Escopo Large ⇒ varredura completa: cada dimensão vira requisito ou recebe `N/A because…` explícito.

| Dimensão | Resolução |
| -------- | --------- |
| Input validation & bounds | INOV-09 (obrigatórios), INOV-10 (só espaços), INOV-12 (tamanho), INOV-17 (valor fora da lista), INOV-22/INOV-23 (título duplicado) |
| Failure / partial-failure states | INOV-13 (submissão inválida não grava nada), INOV-42 (banco indisponível → página 500, nada gravado) |
| Idempotency / retry / duplicate handling | INOV-43 (segundo envio idêntico recusado pela RN10), INOV-03 (redirect após POST: recarregar não reenvia) |
| Auth boundaries & rate limits | Boundaries: INOV-07 (anônimo), INOV-08 (qualquer perfil cadastra), INOV-20 (listas só por `ADMINISTRADOR`), INOV-06 (campos do sistema não aceitos do cliente). Rate limits: **N/A because** nenhum RN/RNF exige e o cadastro exige sessão autenticada de conta criada por administrador. |
| Concurrency / ordering | INOV-25 (dois cadastros simultâneos com o mesmo título na mesma unidade: o banco aceita um e o outro recebe erro de campo, não 500) |
| Data lifecycle / expiry | INOV-19 (item de lista em uso não pode ser excluído). Exclusão de inovação: **N/A because** é da F4. Sem expiração: registros não têm TTL. |
| Observability | **N/A because** o próprio registro guarda autor e data de criação (RN08), que é a trilha exigida; nenhum requisito pede log ou métrica do cadastro. |
| External-dependency failure | INOV-42 (PostgreSQL indisponível). **N/A** para outros serviços: a F2 não chama nenhum. |
| State-transition integrity | INOV-05 (todo registro nasce `Em teste`), INOV-06 (status não é aceito do formulário). Transições: **N/A because** são da F5. |

---

## User Stories

### P1: Cadastrar uma inovação com autor, data e status automáticos ⭐ MVP

**User Story**: Como colaborador autenticado, quero registrar uma solução que minha unidade aplicou,
para que outras unidades possam encontrá-la e reaproveitá-la.

**Why P1**: É o RF02 e a razão de existir do sistema; sem registro, F3 a F6 não têm dado.

**Acceptance Criteria**:

1. **INOV-01** — WHEN an authenticated user requests `/inovacoes/nova/` THEN the system SHALL respond with HTTP 200 and a form with exactly these editable fields: título, unidade de origem, categoria, problema/dor, solução aplicada, resultado/impacto and contato responsável.
2. **INOV-02** — WHEN an authenticated user submits the form with every required field valid THEN the system SHALL persist exactly one new Inovacao holding the submitted values, with leading and trailing spaces removed from every text field.
3. **INOV-03** — WHEN a registration succeeds THEN the system SHALL respond with HTTP 302 to the internal home page.
4. **INOV-04** — WHEN a registration succeeds THEN the system SHALL set the new Inovacao's autor to the account of the user who submitted the form.
5. **INOV-05** — WHEN a registration succeeds THEN the system SHALL set the new Inovacao's status to `Em teste` and its data de criação to the server's current date and time.
6. **INOV-06** — IF the submitted request carries values for autor, status or data de criação THEN the system SHALL ignore them and apply the values defined by INOV-04 and INOV-05.
7. **INOV-07** — IF an anonymous visitor requests `/inovacoes/nova/` with GET or POST THEN the system SHALL redirect to the login page with `next=/inovacoes/nova/` and SHALL NOT persist any Inovacao.
8. **INOV-08** — WHEN a user with profile `USUARIO` or `ADMINISTRADOR` submits a valid form THEN the system SHALL accept the registration in the same way for both profiles.

**Independent Test**: entrar como `USUARIO`, abrir `/inovacoes/nova/`, preencher todos os campos e
salvar; confirmar no banco um registro com autor = essa conta, status `Em teste` e data de criação do
momento; repetir enviando `status=VALIDADA` e `autor=<outro id>` no POST e confirmar que foram
ignorados.

---

### P1: Validar e recuperar de erros sem perder o que foi digitado ⭐ MVP

**User Story**: Como colaborador que esqueceu um campo, quero ver exatamente o que falta e como
corrigir, sem precisar digitar tudo de novo.

**Why P1**: É o RF13 (Essencial) e a RN02; o mapa exige que seja construído junto do cadastro.

**Acceptance Criteria**:

1. **INOV-09** — IF the form is submitted with any of título, unidade de origem, categoria, problema/dor, solução aplicada or contato responsável empty THEN the system SHALL re-render the form with HTTP 200 and show, next to each empty field, that field's required-field message defined in Assumptions.
2. **INOV-10** — IF a required text field is submitted containing only whitespace THEN the system SHALL treat it as empty and apply INOV-09.
3. **INOV-11** — IF a submission is rejected for any validation error THEN the system SHALL re-render every field with the value the user submitted, including the selected unidade and categoria.
4. **INOV-12** — IF the título or contato responsável exceeds 150 characters, or the problema/dor, solução aplicada or resultado/impacto exceeds 5,000 characters, THEN the system SHALL reject the submission and show next to that field "Use no máximo N caracteres (você digitou M)." with the actual limit and length.
5. **INOV-13** — IF a submission is rejected for any validation error THEN the system SHALL NOT persist any Inovacao.
6. **INOV-14** — The system SHALL accept a submission whose resultado/impacto is empty.

**Independent Test**: enviar o formulário com título e solução vazios e o problema preenchido;
confirmar HTTP 200, as duas mensagens nos campos certos, o problema ainda preenchido e nenhum
registro novo no banco.

---

### P1: Unidade e categoria só de listas controladas ⭐ MVP

**User Story**: Como colaborador que vai buscar soluções depois, quero que unidade e categoria usem
sempre os mesmos nomes, para que filtros e buscas encontrem tudo.

**Why P1**: RN01 e RN07 são Essenciais e sustentam os filtros da F3.

**Acceptance Criteria**:

1. **INOV-15** — The system SHALL present unidade de origem and categoria as selection controls listing only the registered Unidade and Categoria records, in alphabetical order by name.
2. **INOV-16** — The system SHALL require every Inovacao to reference exactly one Unidade and exactly one Categoria, enforced by non-null foreign keys in the database.
3. **INOV-17** — IF the submitted unidade or categoria does not match a registered record THEN the system SHALL reject the submission and show "Selecione uma unidade da lista." or "Selecione uma categoria da lista." next to the offending field.
4. **INOV-18** — WHEN the database migrations are applied to an empty database THEN the system SHALL create the Categoria records Atendimento interno, Compras, Financeiro, RH and TI interno, and the Unidade records Filial Leste, Filial Norte, Filial Oeste, Filial Sul and Sede.
5. **INOV-19** — IF a user tries to delete a Unidade or Categoria referenced by at least one Inovacao THEN the system SHALL refuse the deletion and keep the record.
6. **INOV-20** — WHILE the logged-in user's profile is not `ADMINISTRADOR` the system SHALL respond with HTTP 403 to every Django admin screen that lists, adds, changes or deletes Unidade or Categoria records.
7. **INOV-21** — WHILE the logged-in user's profile is `ADMINISTRADOR` the system SHALL allow listing, adding and renaming Unidade and Categoria records in the Django admin.

**Independent Test**: aplicar as migrations num banco vazio e contar os 10 itens; abrir o formulário
e conferir as opções em ordem alfabética; enviar um POST com o id de uma unidade inexistente e ver a
mensagem; como `USUARIO` com `is_staff`, receber 403 no admin de Unidade; como `ADMINISTRADOR`, tentar
excluir uma categoria usada e ver a recusa.

---

### P1: Título único dentro da mesma unidade

**User Story**: Como colaborador, quero ser avisado se minha unidade já registrou uma solução com o
mesmo nome, para não criar uma duplicata.

**Why P1**: RN10 é Importante na priorização, mas o critério foi pedido explicitamente para esta
feature e define a constraint do modelo — adiá-la exigiria migração de dados depois.

**Acceptance Criteria**:

1. **INOV-22** — IF the submitted título equals, ignoring letter case, the título of an existing Inovacao of the same unidade de origem THEN the system SHALL reject the submission and show next to the título field "Já existe uma inovação com este título nesta unidade. Escolha outro título."
2. **INOV-23** — IF the submitted título equals an existing título of the same unidade after removing leading and trailing spaces THEN the system SHALL treat it as a duplicate and apply INOV-22.
3. **INOV-24** — WHEN the submitted título equals the título of an existing Inovacao of a different unidade de origem THEN the system SHALL accept the registration.
4. **INOV-25** — IF two submissions with the same título and unidade are processed concurrently THEN the system SHALL persist exactly one of them and SHALL answer the other with HTTP 200 and the INOV-22 message, never with HTTP 500.
5. **INOV-26** — The system SHALL enforce título uniqueness per unidade, ignoring letter case, through a database constraint.
6. **INOV-27** — The system SHALL treat títulos that differ only in accented characters as distinct.

**Independent Test**: cadastrar "Controle de Caixa" na Sede; tentar " controle de caixa " na Sede e
ver a mensagem; cadastrar "Controle de Caixa" na Filial Sul com sucesso; inserir direto no banco um
duplicado em caixa diferente e confirmar a violação da constraint.

---

### P1: Feedback claro sobre o resultado ⭐ MVP

**User Story**: Como colaborador, quero saber na hora se minha inovação foi salva ou não, para não
ficar em dúvida nem cadastrar de novo.

**Why P1**: RF12 é Essencial e, pelo mapa, precisa nascer junto do cadastro.

**Acceptance Criteria**:

1. **INOV-28** — WHEN a registration succeeds THEN the system SHALL display, on the page reached by the redirect, the message "Inovação “<título>” cadastrada com sucesso." with the saved título, inside the page's `role="status"` region.
2. **INOV-29** — WHEN the page that displayed the success message is loaded again THEN the system SHALL NOT display that message again.
3. **INOV-30** — IF a submission is rejected for any validation error THEN the system SHALL display at the top of the form, before the first field, the message "Não foi possível salvar a inovação. Corrija os campos indicados." inside an element with `role="alert"`.

**Independent Test**: cadastrar uma inovação e ler a mensagem com o título na home; recarregar e
ver que ela sumiu; enviar um formulário inválido e ler o resumo no topo.

---

### P1: Formulário acessível por teclado e leitor de tela ⭐ MVP

**User Story**: Como colaborador que usa teclado ou leitor de tela, quero preencher e corrigir o
formulário sem depender do mouse nem da cor.

**Why P1**: RNF09 é Essencial; o mapa lista rótulos, teclado e foco visível no escopo da F2.

**Acceptance Criteria**:

1. **INOV-31** — The system SHALL associate every form field with a visible `<label>` element through matching `for` and `id` attributes.
2. **INOV-32** — The system SHALL mark every required field with the `required` attribute and with the text "(obrigatório)" inside its label, so the requirement is not conveyed by color alone.
3. **INOV-33** — IF a field has a validation error THEN the system SHALL render that field with `aria-invalid="true"` and reference the error message element in the field's `aria-describedby`.
4. **INOV-34** — The system SHALL build the form only from native HTML controls (`input`, `select`, `textarea`, `button`, `a`) without any positive `tabindex`, so keyboard order follows document order.
5. **INOV-35** — The system SHALL show a visible focus indicator on every form control and on the cancel link.

**Independent Test**: percorrer o formulário só com Tab e Enter até salvar; inspecionar o HTML e
conferir `label[for]`, `required`, "(obrigatório)", `aria-invalid` e `aria-describedby` depois de um
envio inválido.

---

### P2: Cancelar sem salvar

**User Story**: Como colaborador que abriu o formulário por engano ou desistiu, quero sair sem
gravar nada.

**Why P2**: RF14 é Importante; o MVP funciona sem ele, mas o custo é um link.

**Acceptance Criteria**:

1. **INOV-36** — The system SHALL display in the form a link labeled "Cancelar" pointing to the internal home page.
2. **INOV-37** — WHEN the user follows the "Cancelar" link THEN the system SHALL navigate to the internal home page without persisting any Inovacao and without asking for confirmation.

**Independent Test**: preencher parte do formulário, clicar em "Cancelar", chegar à home e confirmar
que nenhum registro foi criado.

---

### P2: Ponto de entrada e contato pré-preenchido

**User Story**: Como colaborador, quero chegar ao cadastro de qualquer tela e não precisar digitar
meu próprio contato quando sou eu o responsável.

**Why P2**: Reduz esforço (Nielsen H7) sem ser condição para o cadastro funcionar.

**Acceptance Criteria**:

1. **INOV-38** — WHILE a user is authenticated the system SHALL display in the header of every page a link labeled "Cadastrar inovação" pointing to `/inovacoes/nova/`.
2. **INOV-39** — WHEN an authenticated user opens an empty registration form THEN the system SHALL pre-fill contato responsável with "<nome completo> (<e-mail>)" of that user, or "<username> (<e-mail>)" when the account has no first or last name.
3. **INOV-40** — WHEN the user replaces the pre-filled contato responsável before submitting THEN the system SHALL persist the value the user typed.

**Independent Test**: logar com uma conta com nome e outra sem; abrir o formulário pelo link do
cabeçalho e conferir o contato pré-preenchido em cada caso; trocar o contato e salvar.

---

### P3: Ajuda contextual nos campos

**User Story**: Como colaborador que cadastra pela primeira vez, quero exemplos do que escrever em
cada campo.

**Why P3**: RF15 é Desejável; entra por decisão do usuário por ser barato.

**Acceptance Criteria**:

1. **INOV-41** — The system SHALL display below every form field a help text containing a filling example, referenced by that field's `aria-describedby`.

**Independent Test**: abrir o formulário e conferir um texto de apoio com exemplo em cada um dos
sete campos, ligado ao campo pelo `aria-describedby`.

---

## Edge Cases

- **INOV-42** — IF the database is unreachable while a registration is being processed THEN the system SHALL respond with the project's HTTP 500 page, SHALL NOT persist any Inovacao and SHALL NOT expose connection details.
- **INOV-43** — IF the same valid form is submitted twice in sequence THEN the system SHALL persist only the first submission and SHALL answer the second with the INOV-22 message.

---

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
| -------------- | ----- | ----- | ------ |
| INOV-01 | P1: Cadastrar uma inovação com autor, data e status automáticos | Execute | Verified |
| INOV-02 | P1: Cadastrar uma inovação com autor, data e status automáticos | Execute | Verified |
| INOV-03 | P1: Cadastrar uma inovação com autor, data e status automáticos | Execute | Verified |
| INOV-04 | P1: Cadastrar uma inovação com autor, data e status automáticos | Execute | Verified |
| INOV-05 | P1: Cadastrar uma inovação com autor, data e status automáticos | Execute | Verified |
| INOV-06 | P1: Cadastrar uma inovação com autor, data e status automáticos | Execute | Verified |
| INOV-07 | P1: Cadastrar uma inovação com autor, data e status automáticos | Execute | Verified |
| INOV-08 | P1: Cadastrar uma inovação com autor, data e status automáticos | Execute | Verified |
| INOV-09 | P1: Validar e recuperar de erros sem perder o que foi digitado | Execute | Verified |
| INOV-10 | P1: Validar e recuperar de erros sem perder o que foi digitado | Execute | Verified |
| INOV-11 | P1: Validar e recuperar de erros sem perder o que foi digitado | Execute | Verified |
| INOV-12 | P1: Validar e recuperar de erros sem perder o que foi digitado | Execute | Verified |
| INOV-13 | P1: Validar e recuperar de erros sem perder o que foi digitado | Execute | Verified |
| INOV-14 | P1: Validar e recuperar de erros sem perder o que foi digitado | Execute | Verified |
| INOV-15 | P1: Unidade e categoria só de listas controladas | Execute | Verified |
| INOV-16 | P1: Unidade e categoria só de listas controladas | Execute | Verified |
| INOV-17 | P1: Unidade e categoria só de listas controladas | Execute | Verified |
| INOV-18 | P1: Unidade e categoria só de listas controladas | Execute | Verified |
| INOV-19 | P1: Unidade e categoria só de listas controladas | Execute | Verified |
| INOV-20 | P1: Unidade e categoria só de listas controladas | Execute | Verified |
| INOV-21 | P1: Unidade e categoria só de listas controladas | Execute | Verified |
| INOV-22 | P1: Título único dentro da mesma unidade | Execute | Verified |
| INOV-23 | P1: Título único dentro da mesma unidade | Execute | Verified |
| INOV-24 | P1: Título único dentro da mesma unidade | Execute | Verified |
| INOV-25 | P1: Título único dentro da mesma unidade | Execute | Verified |
| INOV-26 | P1: Título único dentro da mesma unidade | Execute | Verified |
| INOV-27 | P1: Título único dentro da mesma unidade | Execute | Verified |
| INOV-28 | P1: Feedback claro sobre o resultado | Execute | Verified |
| INOV-29 | P1: Feedback claro sobre o resultado | Execute | Verified |
| INOV-30 | P1: Feedback claro sobre o resultado | Execute | Verified |
| INOV-31 | P1: Formulário acessível por teclado e leitor de tela | Execute | Verified |
| INOV-32 | P1: Formulário acessível por teclado e leitor de tela | Execute | Verified |
| INOV-33 | P1: Formulário acessível por teclado e leitor de tela | Execute | Verified |
| INOV-34 | P1: Formulário acessível por teclado e leitor de tela | Execute | Verified |
| INOV-35 | P1: Formulário acessível por teclado e leitor de tela | Execute | Verified |
| INOV-36 | P2: Cancelar sem salvar | Execute | Verified |
| INOV-37 | P2: Cancelar sem salvar | Execute | Verified |
| INOV-38 | P2: Ponto de entrada e contato pré-preenchido | Execute | Verified |
| INOV-39 | P2: Ponto de entrada e contato pré-preenchido | Execute | Verified |
| INOV-40 | P2: Ponto de entrada e contato pré-preenchido | Execute | Verified |
| INOV-41 | P3: Ajuda contextual nos campos | Execute | Verified |
| INOV-42 | Edge case: banco indisponível | Execute | Verified |
| INOV-43 | Edge case: duplo envio | Execute | Verified |

**ID format:** `INOV-NN`
**Status values:** Pending → In Design → In Tasks → Implementing → Verified
**Coverage:** 43 total, 43 mapeados para tasks, 43 verificados (`validation.md`, iteração 2).

---

## Rastreabilidade com o Documento de Requisitos

| Origem | Requirement IDs |
| ------ | --------------- |
| RF02 | INOV-01, INOV-02, INOV-03 |
| RF12 | INOV-28, INOV-29, INOV-30 |
| RF13 | INOV-09 … INOV-13, INOV-17, INOV-22, INOV-33 |
| RF14 | INOV-36, INOV-37 |
| RF15 | INOV-41 |
| RN01 | INOV-16 |
| RN02 | INOV-09, INOV-10, INOV-14 |
| RN03 | INOV-05, INOV-06 |
| RN04 | INOV-07, INOV-08 |
| RN06 | INOV-01, INOV-09, INOV-39, INOV-40 |
| RN07 | INOV-15, INOV-17, INOV-18, INOV-19, INOV-20, INOV-21 |
| RN08 | INOV-04, INOV-05, INOV-06 |
| RN10 | INOV-22 … INOV-26, INOV-27, INOV-43 |
| RNF01 | INOV-28 … INOV-30 (H1, H9), INOV-36, INOV-37 (H3), INOV-38 … INOV-40 (H7), INOV-15 (H6), INOV-41 (H10) |
| RNF05 | INOV-16, INOV-19, INOV-26, INOV-42 |
| RNF09 | INOV-31 … INOV-35 |
| AD-005 | INOV-04 |
| AD-006 | INOV-07 |

---

## Success Criteria

- [x] Um `USUARIO` e um `ADMINISTRADOR` cadastram cada um uma inovação pelo formulário, e o banco mostra
      autor correto, status `Em teste` e data de criação preenchida em ambas.
- [x] Um envio com todos os campos obrigatórios vazios mostra as seis mensagens de campo e o resumo, e
      nenhum registro novo existe no banco.
- [x] Uma tentativa de gravar dois títulos iguais em caixa diferente na mesma unidade falha tanto
      pelo formulário quanto por inserção direta no banco.
- [ ] O formulário é preenchido e enviado só com teclado, e todo campo tem rótulo associado.
      Rótulos, `required`, ordem de foco e `:focus-visible` estão provados no HTML
      (`inovacoes/tests/test_views_acessibilidade.py`); o percurso real com teclado fica para o UAT.
