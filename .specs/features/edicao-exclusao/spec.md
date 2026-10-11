# Edição e Exclusão de Inovações (F4) — Specification

**Fontes:** `docs/requisitos.md` (RF07, RF08, RF14, RN05, RN12, RNF07; RN04, RN08, RN10, RF12, RF13 e RNF09 reaplicados à edição) · `docs/mapa-de-features.md` (F4)
**Decisões vinculantes:** AD-001 (sessão do Django) · AD-002 (MVT sem Service Layer: a regra de autoria fica no model/view, sem camada própria) · AD-003 (PostgreSQL) · AD-004 (perfil por enum, consultado por `Usuario.is_administrador`) · AD-005 (`autor` aponta para `settings.AUTH_USER_MODEL`) · AD-006 (rotas novas nascem protegidas; nenhuma é pública) · AD-007 (`Inovacao` segue fora do Django admin; edição e exclusão só pelas telas da F4) · AD-008 (a edição grava por `Inovacao.save()`, que mantém `texto_busca`)
**Reusa da F1:** `contas.Usuario` e o perfil (`USUARIO` / `ADMINISTRADOR`) · página 500 sem vazamento (AUTH-26) · região de mensagens `role="status"` do `templates/base.html`
**Reusa da F2:** `inovacoes.Inovacao` sem campos novos · `InovacaoForm` com os rótulos, ajudas e mensagens da INOV-09 a INOV-17 e INOV-30 a INOV-35, INOV-41 · unicidade de título por unidade (INOV-22 a INOV-27) · tratamento da corrida na constraint (INOV-25)
**Reusa da F3:** detalhe `/inovacoes/<id>/` e a página "Inovação não encontrada." (CONS-15) · listagem `/inovacoes/` como destino após a exclusão
**Altera a F3:** o detalhe passa a exibir "Editar" e "Excluir" para quem pode alterar a inovação (a F3 dizia, em Out of Scope, que o detalhe não exibe esses botões) — ver EDEX-03 e EDEX-31
**Status:** Aprovada pelo usuário em 2026-10-11 (assumptions confirmadas na aprovação)
**Contexto da discussão:** `.specs/features/edicao-exclusao/context.md`

> **Nota de notação:** como na F1, F2 e F3, os critérios de aceite estão em EARS em inglês (WHEN /
> WHILE / WHERE / IF-THEN / ubíquo + SHALL); o restante do documento está em português. Textos
> exibidos ao usuário aparecem entre aspas, em português, exatamente como devem ser renderizados.

## Problem Statement

Depois de cadastrada, uma inovação não pode ser corrigida nem removida: um erro de digitação, um
contato que mudou ou um registro duplicado ficam para sempre no repositório, e a curadoria
institucional não tem como agir. A F4 entrega a edição e a exclusão, e é onde a política de autoria
da RN05 vira comportamento observável: o autor altera o que cadastrou, o administrador altera
qualquer registro, e um usuário comum nunca altera o registro de outra pessoa, nem pela tela nem
forjando a requisição. A exclusão é definitiva, então só acontece depois de uma confirmação
explícita (RN12).

## Goals

- [ ] O autor edita e exclui as inovações que cadastrou; o administrador edita e exclui as de
      qualquer autor; os dois perfis usam as mesmas telas.
- [ ] Um usuário comum que tenta editar ou excluir uma inovação de outra pessoa recebe HTTP 403 e
      nada muda no banco, tanto ao abrir a tela quanto ao enviar a requisição diretamente.
- [ ] Nenhuma inovação é excluída sem passar pela página de confirmação; abrir a confirmação e
      cancelar não apagam nada.
- [ ] A edição valida os dados com as mesmas regras e mensagens do cadastro, preserva o que foi
      digitado em caso de erro e oferece "Cancelar" sem gravar.
- [ ] Depois de editar, a busca da F3 encontra a inovação pelos textos novos e não pelos antigos.

## Out of Scope

Excluído explicitamente. Documentado para impedir scope creep.

| Feature | Reason |
| ------- | ------ |
| Alterar o status pela edição | F5 (RF09) define as transições do RN03. O formulário de edição não tem o campo Status. |
| Ações de editar/excluir na listagem | Decidido com o usuário: só no detalhe; a tabela da F3 continua só de leitura (H8). |
| Exclusão lógica, lixeira ou recuperação de inovação excluída | Decidido com o usuário: exclusão definitiva, como a RN12 descreve ("irreversível"). |
| Detecção de edição concorrente (versão, bloqueio) | Decidido com o usuário: a última gravação vence. |
| Exclusão em lote | Nenhum RF pede; a confirmação é por inovação. |
| Transferir a autoria ou editar autor e data de criação | RN08: autor e data são do sistema. |
| Histórico de alterações ou log de exclusões | Nenhum RF/RNF pede. Registrado em Deferred Ideas. |
| Aviso de alterações não salvas ao sair do formulário | Exigiria JavaScript; "Cancelar" já é explícito. |
| Editar ou excluir inovação pelo Django admin | AD-007: `Inovacao` segue fora do admin. |
| Auditoria WCAG completa, responsividade e teste SUS | RNF09, RNF03 e RNF01 têm validação transversal no fim. A F4 cobre o que é dela: formulário, confirmação e página de acesso negado. |

---

## Assumptions & Open Questions

Toda ambiguidade está resolvida ou registrada aqui — nada fica silenciosamente indefinido.

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --------------------- | -------------- | --------- | ---------- |
| Quem pode alterar | O autor da inovação, qualquer que seja o perfil, e toda conta com perfil `ADMINISTRADOR` | RN05 e RNF07 | y |
| Momento da checagem do perfil | A cada requisição, pelo perfil atual da conta (`is_administrador`); quem é rebaixado perde na hora o acesso às inovações de terceiros | Perfil é dado vivo (AD-004); nada fica guardado na sessão | y |
| Onde ficam as ações | Links "Editar" e "Excluir" só no detalhe, exibidos só para quem pode alterar a inovação | Decidido com o usuário | y |
| Rotas | `/inovacoes/<id>/editar/` e `/inovacoes/<id>/excluir/` | Mesmo padrão do detalhe da F3 | y |
| Acesso negado | HTTP 403 com página própria: "Você não tem permissão para alterar esta inovação.", "Só quem cadastrou a inovação ou um administrador pode editá-la ou excluí-la." e link "Voltar para a inovação" para o detalhe | Decidido com o usuário (403); como todos veem todas as inovações (CONS-08), esconder a existência não protege nada | y |
| Negação também no envio | Um POST de edição ou exclusão de quem não pode alterar responde 403 e não grava nem apaga nada | O RNF07 vale para a requisição, não só para a tela | y |
| Ordem das checagens | Id inexistente → 404 da CONS-15; inovação existente sem permissão → 403 | Saber se o id existe não vaza nada: o detalhe já é público para autenticados | y |
| Anônimo | Redireciona ao login com `next` (AD-006), em GET e em POST, sem alterar nada | Igual às demais rotas | y |
| Campos editáveis | Os sete do cadastro: título, unidade de origem, categoria, problema/dor, solução aplicada, resultado/impacto, contato responsável | Decidido com o usuário: status fica para a F5 | y |
| Valores iniciais do formulário | Os valores atuais da inovação, inclusive o contato salvo (não o pré-preenchimento da INOV-39) | Edição parte do que existe | y |
| Autor, data de criação e status na edição | Não mudam, nem quando o administrador edita a inovação de outra pessoa; valores forjados no POST são ignorados | RN08; status é da F5 | y |
| Validação | As mesmas regras e mensagens do cadastro (INOV-09 a INOV-17, INOV-22 a INOV-24, INOV-27), com o resumo da INOV-30 ("Não foi possível salvar a inovação. Corrija os campos indicados.") | Um formulário, uma regra (H4); o texto do resumo serve aos dois casos | y |
| Título igual ao próprio | Salvar sem mudar o título, ou mudando só a caixa, é aceito; a unicidade só compara com as outras inovações da unidade | Sem isso, nenhuma edição passaria | y |
| Título e página | "Editar inovação" (`<title>` e `h1`); botão "Salvar alterações"; link "Cancelar" para o detalhe | "Salvar alterações" diz que o registro já existe | y |
| Depois de salvar | Redirect 302 para o detalhe com "Inovação “<título salvo>” atualizada com sucesso." na região `role="status"`, uma vez só | Mesmo padrão da INOV-28/INOV-29 e da CONS-49 | y |
| Confirmação da exclusão | Página própria "Excluir inovação" que nomeia a inovação e avisa que não dá para desfazer, com o botão "Excluir definitivamente" (POST) e o link "Cancelar" para o detalhe | Decidido com o usuário: página com botão, sem JavaScript | y |
| Texto da confirmação | "Você vai excluir a inovação “<título>” (<unidade> · <categoria>). Esta ação não pode ser desfeita." | Unidade e categoria distinguem títulos iguais em unidades diferentes (INOV-24) | y |
| GET na rota de exclusão | Só mostra a confirmação; nunca apaga | RN12; um link seguido por engano ou por pré-carregamento do navegador não pode excluir | y |
| Tipo de exclusão | Definitiva: a linha sai do banco | Decidido com o usuário | y |
| Depois de excluir | Redirect 302 para `/inovacoes/` com "Inovação “<título>” excluída com sucesso." na região `role="status"`, uma vez só | O detalhe não existe mais; a lista é o lugar natural | y |
| Exclusão repetida | Um segundo POST para o mesmo id (Voltar, duplo clique) recebe o 404 da CONS-15, sem erro 500 | Idempotência: o efeito já aconteceu | y |
| Edição concorrente | A última gravação vence; a unicidade do título continua garantida pela constraint, e a corrida responde com a mensagem da INOV-22 em vez de 500 | Decidido com o usuário (última vence); a corrida de título repete a INOV-25 | y |
| Editar inovação excluída no meio do caminho | O envio do formulário de uma inovação que deixou de existir recebe o 404 da CONS-15 | Não recria o registro | y |
| CSRF | Edição e exclusão por POST com o token CSRF do Django; POST sem token válido responde 403 e não altera nada | Padrão do framework; protege a ação destrutiva de envio forjado | y |
| Banco indisponível | Página 500 do projeto, sem detalhes da conexão, sem gravação parcial | Mesmo padrão da INOV-42 e da CONS-53 | y |
| Dependências futuras da exclusão | Hoje nada referencia `Inovacao`. A F6 (Reaproveitamento) decide o `on_delete` da sua FK quando existir | Fora do escopo da F4 | y |
| Idioma dos critérios de aceite | EARS em inglês, restante em português | Mesmo padrão das features anteriores; `validate_spec.py` exige `SHALL` | y |

**Open questions:** none - todas resolvidas com o usuário ou registradas como assumption acima (defaults do agente confirmados na aprovação da spec em 2026-10-11).

---

## Dimensions Sweep

Escopo Large ⇒ varredura completa: cada dimensão vira requisito ou recebe `N/A because…` explícito.

| Dimensão | Resolução |
| -------- | --------- |
| Input validation & bounds | EDEX-09 (regras e mensagens do cadastro), EDEX-12 (título próprio aceito), EDEX-13 (título de outra inovação recusado), EDEX-08 (campos do sistema ignorados), EDEX-27 e EDEX-28 (id inexistente) |
| Failure / partial-failure states | EDEX-44 (banco indisponível → 500, nada gravado nem apagado). Gravação parcial: **N/A because** cada edição e cada exclusão é uma única escrita numa linha. |
| Idempotency / retry / duplicate handling | EDEX-38 (segundo POST de exclusão → 404), EDEX-36 (GET nunca apaga). Reenviar a mesma edição grava os mesmos valores: **N/A** de requisito próprio, o resultado é igual. |
| Auth boundaries & rate limits | EDEX-17 a EDEX-26 (autor, administrador, terceiro negado em GET e POST, anônimo, perfil atual), EDEX-45 (CSRF). Rate limits: **N/A because** nenhum RN/RNF exige e toda ação exige sessão de conta criada por administrador. |
| Concurrency / ordering | EDEX-14 (corrida no título → mensagem da INOV-22, não 500), EDEX-15 (última gravação vence), EDEX-29 (edição de inovação já excluída → 404). |
| Data lifecycle / expiry | EDEX-37 (exclusão definitiva), EDEX-39 (detalhe da excluída → 404). Dependentes: **N/A because** nenhuma tabela referencia `Inovacao` hoje; a F6 decide. |
| Observability | **N/A because** nenhum RF/RNF pede log de edição ou exclusão. Registrado em Deferred Ideas. |
| External-dependency failure | EDEX-44 (PostgreSQL indisponível). **N/A** para outros serviços: a F4 não chama nenhum. |
| State-transition integrity | EDEX-08 (status não muda pela edição). Transições: **N/A because** são da F5. |

---

## User Stories

### P1: Editar uma inovação que cadastrei ⭐ MVP

**User Story**: Como autor de uma inovação, quero corrigir e atualizar os dados que cadastrei, para
que o repositório mostre a versão certa da solução e o contato atual.

**Why P1**: RF07 é Essencial; sem ele, todo erro de cadastro fica permanente.

**Acceptance Criteria**:

1. **EDEX-01** — WHEN the autor of an Inovacao requests `/inovacoes/<id>/editar/` THEN the system SHALL respond with HTTP 200 and a form titled "Editar inovação" with exactly these editable fields: título, unidade de origem, categoria, problema/dor, solução aplicada, resultado/impacto and contato responsável.
2. **EDEX-02** — WHEN the edit form is displayed THEN the system SHALL pre-fill every field with the Inovacao's current saved value, including the saved contato responsável.
3. **EDEX-03** — WHILE the logged-in user may change an Inovacao the system SHALL display on that Inovacao's detail page a link labeled "Editar" pointing to `/inovacoes/<id>/editar/`.
4. **EDEX-04** — WHEN the user submits the edit form with every required field valid THEN the system SHALL update that same Inovacao with the submitted values, with leading and trailing spaces removed from every text field, and SHALL NOT create any other Inovacao.
5. **EDEX-05** — WHEN an edit succeeds THEN the system SHALL respond with HTTP 302 to `/inovacoes/<id>/`.
6. **EDEX-06** — WHEN an edit succeeds THEN the system SHALL display on the detail page, inside the `role="status"` region, the message "Inovação “<título>” atualizada com sucesso." with the saved título.
7. **EDEX-07** — WHEN the page that displayed the edit success message is loaded again THEN the system SHALL NOT display that message again.
8. **EDEX-08** — IF the edit request carries values for autor, status or data de criação THEN the system SHALL ignore them and keep the Inovacao's autor, status and data de criação unchanged.
9. **EDEX-09** — IF the edit form is submitted with invalid data THEN the system SHALL reject it with the same field messages as the registration form (INOV-09, INOV-10, INOV-12, INOV-17), re-render the form with HTTP 200 and the submitted values (INOV-11), and show the INOV-30 summary inside `role="alert"`.
10. **EDEX-10** — IF an edit is rejected for any validation error THEN the system SHALL keep every stored value of the Inovacao unchanged.
11. **EDEX-11** — WHEN an edit changes the título, problema/dor or solução aplicada THEN the system SHALL make the listing search (CONS-19, CONS-20) find the Inovacao by the new words and SHALL NOT find it by words present only in the replaced text.
12. **EDEX-12** — WHEN the submitted título equals the Inovacao's own current título, with or without a change in letter case, and the unidade de origem is unchanged THEN the system SHALL accept the edit.
13. **EDEX-13** — IF the submitted título and unidade de origem match, ignoring letter case, another Inovacao of that unidade THEN the system SHALL reject the edit and show next to the título field "Já existe uma inovação com este título nesta unidade. Escolha outro título."
14. **EDEX-14** — IF two concurrent edits or an edit and a registration result in the same título for the same unidade THEN the system SHALL persist only one of them and SHALL answer the other with HTTP 200 and the EDEX-13 message, never with HTTP 500.
15. **EDEX-15** — WHEN two edits of the same Inovacao are processed one after the other THEN the system SHALL keep the values of the last one processed.
16. **EDEX-16** — WHEN the user follows the edit form's "Cancelar" link THEN the system SHALL navigate to `/inovacoes/<id>/` without changing the Inovacao and without asking for confirmation.

**Independent Test**: como `maria` (USUARIO), abrir o detalhe de uma inovação dela, clicar em
"Editar", conferir os valores atuais, trocar o título e o problema, salvar e ver o detalhe com a
mensagem; buscar uma palavra do problema novo (acha) e uma só do antigo (não acha); abrir de novo,
apagar o título e conferir a mensagem e os demais campos preservados; clicar em "Cancelar" e ver o
registro intacto.

---

### P1: Curadoria pelo administrador ⭐ MVP

**User Story**: Como administrador, quero editar a inovação de qualquer autor, para manter a
qualidade e a integridade do conteúdo institucional.

**Why P1**: RF07 e RN05 dão ao administrador o poder de curadoria; é o mesmo fluxo da edição com
outra regra de acesso.

**Acceptance Criteria**:

1. **EDEX-17** — WHEN a user with profile `ADMINISTRADOR` requests `/inovacoes/<id>/editar/` for an Inovacao authored by another account THEN the system SHALL respond with HTTP 200 and the edit form of EDEX-01.
2. **EDEX-18** — WHEN a user with profile `ADMINISTRADOR` submits a valid edit of an Inovacao authored by another account THEN the system SHALL apply EDEX-04 to EDEX-06 and SHALL keep the original autor and data de criação.
3. **EDEX-19** — WHEN the autor of an Inovacao has profile `USUARIO` or `ADMINISTRADOR` THEN the system SHALL allow that autor to edit and delete it in the same way for both profiles.

**Independent Test**: como `joao` (ADMINISTRADOR), editar uma inovação da `maria`; conferir no
detalhe que continua "Cadastrada por Maria Silva em <data original>" e que os valores mudaram.

---

### P1: Negar a alteração de inovações de terceiros ⭐ MVP

**User Story**: Como colaborador que cadastrou uma inovação, quero que só eu e os administradores
possamos alterá-la, para que o registro da minha unidade não seja modificado por outras pessoas.

**Why P1**: RNF07 é Essencial e o mapa da F4 pede atenção especial a estes casos.

**Acceptance Criteria**:

1. **EDEX-20** — IF a user with profile `USUARIO` who is not the autor requests `/inovacoes/<id>/editar/` or `/inovacoes/<id>/excluir/` with GET THEN the system SHALL respond with HTTP 403 and a page showing "Você não tem permissão para alterar esta inovação." and "Só quem cadastrou a inovação ou um administrador pode editá-la ou excluí-la."
2. **EDEX-21** — The system SHALL display on the access-denied page a link labeled "Voltar para a inovação" pointing to `/inovacoes/<id>/`.
3. **EDEX-22** — IF a user with profile `USUARIO` who is not the autor submits a POST to `/inovacoes/<id>/editar/` THEN the system SHALL respond with HTTP 403 and SHALL keep every stored value of the Inovacao unchanged.
4. **EDEX-23** — IF a user with profile `USUARIO` who is not the autor submits a POST to `/inovacoes/<id>/excluir/` THEN the system SHALL respond with HTTP 403 and SHALL keep the Inovacao stored.
5. **EDEX-24** — WHILE the logged-in user is neither the autor of an Inovacao nor has profile `ADMINISTRADOR` the system SHALL NOT display the "Editar" and "Excluir" links on that Inovacao's detail page.
6. **EDEX-25** — The system SHALL decide each edit and delete request from the account's profile at the time of that request, so that an account changed from `ADMINISTRADOR` to `USUARIO` receives HTTP 403 on its next request for another account's Inovacao.
7. **EDEX-26** — IF an anonymous visitor requests `/inovacoes/<id>/editar/` or `/inovacoes/<id>/excluir/` with GET or POST THEN the system SHALL redirect to the login page with `next` set to the requested path and SHALL NOT change or delete any Inovacao.
8. **EDEX-27** — IF `/inovacoes/<id>/editar/` is requested with GET or POST for an id with no Inovacao THEN the system SHALL respond as defined in CONS-15 (HTTP 404, "Inovação não encontrada.").
9. **EDEX-28** — IF `/inovacoes/<id>/excluir/` is requested with GET for an id with no Inovacao THEN the system SHALL respond as defined in CONS-15.
10. **EDEX-29** — IF an edit form is submitted for an Inovacao deleted after the form was opened THEN the system SHALL respond as defined in CONS-15 and SHALL NOT create any Inovacao.

**Independent Test**: como `maria` (USUARIO), abrir o detalhe de uma inovação do `joao` e não ver
"Editar" nem "Excluir"; abrir `/inovacoes/<id>/editar/` e `/inovacoes/<id>/excluir/` pela barra de
endereço e receber 403 com a mensagem e o link; num teste automatizado, enviar POST às duas rotas e
conferir que o registro continua igual.

---

### P2: Excluir uma inovação com confirmação

**User Story**: Como autor de uma inovação (ou administrador), quero removê-la do repositório quando
ela não faz mais sentido, sem risco de apagá-la por engano.

**Why P2**: RF08, RN12 e RF14 são Importantes no MoSCoW; o repositório funciona sem exclusão, mas a
curadoria fica incompleta.

**Acceptance Criteria**:

1. **EDEX-30** — WHEN the autor of an Inovacao or a user with profile `ADMINISTRADOR` requests `/inovacoes/<id>/excluir/` with GET THEN the system SHALL respond with HTTP 200 and a confirmation page titled "Excluir inovação" showing "Você vai excluir a inovação “<título>” (<unidade> · <categoria>). Esta ação não pode ser desfeita."
2. **EDEX-31** — WHILE the logged-in user may change an Inovacao the system SHALL display on that Inovacao's detail page a link labeled "Excluir" pointing to `/inovacoes/<id>/excluir/`.
3. **EDEX-32** — The system SHALL display on the confirmation page a button labeled "Excluir definitivamente" that submits a POST to `/inovacoes/<id>/excluir/`.
4. **EDEX-33** — The system SHALL display on the confirmation page a link labeled "Cancelar" pointing to `/inovacoes/<id>/`.
5. **EDEX-34** — WHEN the user follows the confirmation page's "Cancelar" link THEN the system SHALL navigate to `/inovacoes/<id>/` and SHALL keep the Inovacao stored.
6. **EDEX-35** — WHEN the autor or a user with profile `ADMINISTRADOR` submits the confirmation THEN the system SHALL delete the Inovacao and respond with HTTP 302 to `/inovacoes/`.
7. **EDEX-36** — IF `/inovacoes/<id>/excluir/` is requested with GET THEN the system SHALL NOT delete the Inovacao.
8. **EDEX-37** — WHEN a deletion succeeds THEN the system SHALL remove the Inovacao's row from the database, so that it no longer appears in the listing, in the search or in the count of CONS-33.
9. **EDEX-38** — IF the confirmation is submitted again for an Inovacao that was already deleted THEN the system SHALL respond as defined in CONS-15, never with HTTP 500.
10. **EDEX-39** — WHEN the detail page of a deleted Inovacao is requested THEN the system SHALL respond as defined in CONS-15.
11. **EDEX-40** — WHEN a deletion succeeds THEN the system SHALL display on the listing, inside the `role="status"` region, the message "Inovação “<título>” excluída com sucesso." with the deleted Inovacao's título, and SHALL NOT display it again when the listing is reloaded.

**Independent Test**: como `maria`, abrir o detalhe de uma inovação dela, clicar em "Excluir", ler a
confirmação, clicar em "Cancelar" e ver o registro intacto; repetir e clicar em "Excluir
definitivamente"; ver a lista com a mensagem e sem a inovação; abrir o detalhe antigo e receber
"Inovação não encontrada."; como `joao`, excluir uma inovação da `maria` do mesmo jeito.

---

### P1: Edição, confirmação e acesso negado acessíveis ⭐ MVP

**User Story**: Como colaborador que usa teclado ou leitor de tela, quero editar, confirmar uma
exclusão e entender uma recusa sem depender de mouse ou de cor.

**Why P1**: RNF09 é Essencial; as telas novas da F4 precisam do mesmo nível do cadastro.

**Acceptance Criteria**:

1. **EDEX-41** — The system SHALL render the edit form with the same labels, required-field markers, help texts and error associations as the registration form (INOV-31, INOV-32, INOV-33, INOV-41).
2. **EDEX-42** — The system SHALL build the edit form, the confirmation page and the access-denied page only from native HTML controls and links, without any positive `tabindex`, and SHALL show a visible focus indicator on each of them.
3. **EDEX-43** — The system SHALL give the edit form, the confirmation page and the access-denied page a single `h1` and a `<title>` that name the page: "Editar inovação", "Excluir inovação" and "Acesso negado".

**Independent Test**: só com teclado, a partir do detalhe: Tab até "Editar", Enter, percorrer o
formulário, provocar um erro, corrigir e salvar; Tab até "Excluir", Enter, Tab até "Cancelar" e
depois até "Excluir definitivamente"; foco visível em cada passo. No DevTools, conferir `label[for]`,
`aria-invalid`, `aria-describedby` e a ausência de `tabindex` positivo.

---

## Edge Cases

- **EDEX-44** — IF the database is unreachable while an edit or a deletion is being processed THEN the system SHALL respond with the project's HTTP 500 page, SHALL NOT change or delete the Inovacao and SHALL NOT expose connection details.
- **EDEX-45** — IF a POST to `/inovacoes/<id>/editar/` or `/inovacoes/<id>/excluir/` lacks a valid CSRF token THEN the system SHALL respond with HTTP 403 and SHALL NOT change or delete the Inovacao.
- Título alterado para um que existe em **outra** unidade: aceito (INOV-24 vale na edição, por EDEX-13).
- Títulos que diferem só por acento continuam distintos na edição (INOV-27, por EDEX-13).
- Unidade ou categoria inexistente no POST de edição: mensagem da INOV-17 (EDEX-09).
- Id não numérico em `/inovacoes/abc/editar/`: a rota não casa e cai no 404 padrão, como em `/inovacoes/abc/` (fora da CONS-15).

---

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
| -------------- | ----- | ----- | ------ |
| EDEX-01 | P1: Editar uma inovação que cadastrei | Execute | Implementing |
| EDEX-02 | P1: Editar uma inovação que cadastrei | Execute | Implementing |
| EDEX-03 | P1: Editar uma inovação que cadastrei | Specify | Pending |
| EDEX-04 | P1: Editar uma inovação que cadastrei | Execute | Implementing |
| EDEX-05 | P1: Editar uma inovação que cadastrei | Execute | Implementing |
| EDEX-06 | P1: Editar uma inovação que cadastrei | Execute | Implementing |
| EDEX-07 | P1: Editar uma inovação que cadastrei | Execute | Implementing |
| EDEX-08 | P1: Editar uma inovação que cadastrei | Execute | Implementing |
| EDEX-09 | P1: Editar uma inovação que cadastrei | Execute | Implementing |
| EDEX-10 | P1: Editar uma inovação que cadastrei | Execute | Implementing |
| EDEX-11 | P1: Editar uma inovação que cadastrei | Execute | Implementing |
| EDEX-12 | P1: Editar uma inovação que cadastrei | Execute | Implementing |
| EDEX-13 | P1: Editar uma inovação que cadastrei | Execute | Implementing |
| EDEX-14 | P1: Editar uma inovação que cadastrei | Execute | Implementing |
| EDEX-15 | P1: Editar uma inovação que cadastrei | Execute | Implementing |
| EDEX-16 | P1: Editar uma inovação que cadastrei | Execute | Implementing |
| EDEX-17 | P1: Curadoria pelo administrador | Execute | Implementing |
| EDEX-18 | P1: Curadoria pelo administrador | Execute | Implementing |
| EDEX-19 | P1: Curadoria pelo administrador | Execute | Implementing |
| EDEX-20 | P1: Negar a alteração de inovações de terceiros | Execute | Implementing |
| EDEX-21 | P1: Negar a alteração de inovações de terceiros | Execute | Implementing |
| EDEX-22 | P1: Negar a alteração de inovações de terceiros | Execute | Implementing |
| EDEX-23 | P1: Negar a alteração de inovações de terceiros | Specify | Pending |
| EDEX-24 | P1: Negar a alteração de inovações de terceiros | Specify | Pending |
| EDEX-25 | P1: Negar a alteração de inovações de terceiros | Execute | Implementing |
| EDEX-26 | P1: Negar a alteração de inovações de terceiros | Execute | Implementing |
| EDEX-27 | P1: Negar a alteração de inovações de terceiros | Execute | Implementing |
| EDEX-28 | P1: Negar a alteração de inovações de terceiros | Specify | Pending |
| EDEX-29 | P1: Negar a alteração de inovações de terceiros | Specify | Pending |
| EDEX-30 | P2: Excluir uma inovação com confirmação | Specify | Pending |
| EDEX-31 | P2: Excluir uma inovação com confirmação | Specify | Pending |
| EDEX-32 | P2: Excluir uma inovação com confirmação | Specify | Pending |
| EDEX-33 | P2: Excluir uma inovação com confirmação | Specify | Pending |
| EDEX-34 | P2: Excluir uma inovação com confirmação | Specify | Pending |
| EDEX-35 | P2: Excluir uma inovação com confirmação | Specify | Pending |
| EDEX-36 | P2: Excluir uma inovação com confirmação | Specify | Pending |
| EDEX-37 | P2: Excluir uma inovação com confirmação | Specify | Pending |
| EDEX-38 | P2: Excluir uma inovação com confirmação | Specify | Pending |
| EDEX-39 | P2: Excluir uma inovação com confirmação | Specify | Pending |
| EDEX-40 | P2: Excluir uma inovação com confirmação | Specify | Pending |
| EDEX-41 | P1: Edição, confirmação e acesso negado acessíveis | Specify | Pending |
| EDEX-42 | P1: Edição, confirmação e acesso negado acessíveis | Specify | Pending |
| EDEX-43 | P1: Edição, confirmação e acesso negado acessíveis | Specify | Pending |
| EDEX-44 | Edge Cases | Specify | Pending |
| EDEX-45 | Edge Cases | Specify | Pending |

**Coverage:** 45 total, 0 mapped to tasks, 45 unmapped ⚠️ (esperado antes de Design/Tasks)

---

## Rastreabilidade com o Documento de Requisitos

| Requisito | Critérios |
| --------- | --------- |
| RF07 | EDEX-01 … EDEX-19 |
| RF08 | EDEX-30 … EDEX-40 |
| RF14 | EDEX-16 (cancelar a edição), EDEX-30, EDEX-33, EDEX-34, EDEX-36 (confirmação e cancelar a exclusão) |
| RN05 | EDEX-17 … EDEX-25, EDEX-35 |
| RN12 | EDEX-30, EDEX-32, EDEX-35, EDEX-36 |
| RNF07 | EDEX-20 … EDEX-26, EDEX-45 |
| RN04 | EDEX-26 |
| RN08 | EDEX-08, EDEX-18 |
| RN10 | EDEX-12 … EDEX-14 |
| RF12 | EDEX-06, EDEX-07, EDEX-40 |
| RF13 | EDEX-09, EDEX-10 |
| RNF09 | EDEX-41 … EDEX-43 |
| RNF01 (Nielsen) | H1: EDEX-06, EDEX-40 · H3: EDEX-16, EDEX-34 · H5: EDEX-30, EDEX-36 · H9: EDEX-09, EDEX-20 |

---

## Success Criteria

- [ ] Um `USUARIO` edita e exclui uma inovação própria; um `ADMINISTRADOR` edita e exclui uma
      inovação de outro autor; em ambos os casos o autor e a data de criação originais continuam no
      detalhe.
- [ ] Um `USUARIO` não vê "Editar" nem "Excluir" numa inovação de outra pessoa, e GET e POST nas duas
      rotas respondem 403 sem alterar o banco (provado por teste automatizado para cada combinação
      de rota, método e perfil).
- [ ] Nenhum caminho apaga uma inovação sem o POST da página de confirmação.
- [ ] Depois de editar o problema, a busca acha a inovação pela palavra nova e não pela antiga.
- [ ] Edição, confirmação e acesso negado são operados só com teclado, com rótulos associados e foco
      visível.
