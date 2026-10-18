# Ciclo de Vida do Status (F5) — Specification

**Fontes:** `docs/requisitos.md` (RF09, RN03; RF12, RF14, RN05, RN12, RNF07 e RNF09 reaplicados à troca de status) · `docs/mapa-de-features.md` (F5) · `docs/design-spec.md` (§6 alerta e badge de status, §10 F5)
**Decisões vinculantes:** AD-001 (sessão do Django) · AD-002 (MVT sem Service Layer: a regra de transição fica no model, sem camada própria) · AD-003 (PostgreSQL; a validade das transições desce para o banco) · AD-004 (perfil por enum, `Usuario.is_administrador`) · AD-005 (o responsável pela mudança aponta para `settings.AUTH_USER_MODEL`) · AD-006 (a rota nova nasce protegida) · AD-007 (`Inovacao` e o histórico ficam fora do Django admin) · AD-008 (a troca de status grava por `Inovacao.save()`; status não entra em `texto_busca`) · AD-009 (a view herda `AlteracaoDeInovacaoMixin`; a regra é `Inovacao.pode_ser_alterada_por`; recusa em 403 com `inovacoes/acesso_negado.html`) · AD-010 (o controle do ciclo e o histórico são componentes da `kira.css`, sobre o `selo`; par de cor novo entra no DS-08)
**Reusa da F2:** `inovacoes.Inovacao` e `inovacoes.StatusInovacao` sem valores novos · status inicial "Em teste" (RN03, já implementado) · `CheckConstraint inovacao_status_valido`
**Reusa da F3:** detalhe `/inovacoes/<id>/` e o 404 "Inovação não encontrada." (CONS-15) · filtro por status da listagem (CONS-27), que passa a refletir o status avançado
**Reusa da F4:** `AlteracaoDeInovacaoMixin` e a página de acesso negado (EDEX-20, EDEX-21) · padrão de confirmação por página com POST (EDEX-30 a EDEX-36) · varredura de autoria de `inovacoes/tests/test_controle_autoria.py`, que passa a cobrir a rota nova sem mudança · EDEX-08 continua valendo: a edição não muda o status
**Altera a F3/F4:** o detalhe ganha a seção "Ciclo de vida" (estágios, ação de avançar e histórico) — ver STAT-01 a STAT-05 e STAT-24 a STAT-27
**Status:** Aprovada pelo usuário em 2026-10-18 (assumptions confirmadas na aprovação)
**Escopo (auto-sizing):** **Large** — o mapa previa Medium, mas o histórico de mudanças acrescenta modelo, migration e tela de confirmação. Roda Design e Tasks formais.
**Contexto da discussão:** `.specs/features/ciclo-de-vida-status/context.md`

> **Nota de notação:** como na F1 a F4, os critérios de aceite estão em EARS em inglês (WHEN /
> WHILE / WHERE / IF-THEN / ubíquo + SHALL); o restante do documento está em português. Textos
> exibidos ao usuário aparecem entre aspas, em português, exatamente como devem ser renderizados.

## Problem Statement

Toda inovação nasce "Em teste" e fica nesse status para sempre: não há como dizer ao repositório que
a solução foi validada nem que está pronta para outras unidades copiarem. Sem isso, quem consulta não
distingue um experimento de uma prática comprovada, e a F6 não tem como saber quais inovações podem
ser sinalizadas como reaproveitadas (RN09). A F5 deixa o autor e o administrador avançarem o status
pelo ciclo da RN03, um estágio por vez, e registra cada mudança: quem fez, quando, de qual status
para qual.

## Goals

- [ ] O autor ou um administrador avança uma inovação de "Em teste" para "Validada" e de "Validada"
      para "Disponível para replicação", cada passo pela página de confirmação.
- [ ] Nenhum caminho (tela, POST forjado, duplo envio, corrida) pula um estágio, volta um estágio ou
      sai de "Disponível para replicação"; o banco recusa uma transição inválida mesmo fora das telas.
- [ ] Cada avanço grava, na mesma transação, o novo status e um registro com status anterior, status
      novo, responsável e data/hora; o detalhe mostra esse histórico a qualquer usuário autenticado.
- [ ] Depois de cada tentativa, o usuário vê uma mensagem que diz o que aconteceu: o avanço feito, ou
      por que nada mudou.

## Out of Scope

Excluído explicitamente. Documentado para impedir scope creep.

| Feature | Reason |
| ------- | ------ |
| Voltar um estágio ou escolher qualquer status | Decidido com o usuário: só avançar, um passo por vez. |
| Trocar o status pelo formulário de edição | Decidido com o usuário: ação separada. EDEX-08 continua valendo. |
| Restringir o avanço ao administrador (curadoria) | Decidido com o usuário: autor ou administrador, a regra da AD-009. |
| Editar ou apagar registros do histórico | O histórico é trilha; nenhuma tela, rota ou admin o altera. |
| Histórico de outras alterações (edição de campos, exclusão) | Só a mudança de status é pedida. A ideia adiada da F4 continua adiada. |
| Registro retroativo das inovações existentes | O histórico começa na F5; inovações cadastradas antes mostram o histórico vazio. |
| Comentário ou justificativa na mudança | Nenhum RF pede. Registrado em Deferred Ideas. |
| Notificar o autor quando um administrador avança a inovação | Nenhum RF pede e o projeto não envia e-mail. |
| Avançar pela listagem ou em lote | Mesmo padrão da F4: ações só no detalhe. |
| Sinalização de reuso e métricas por status | F6 (RF10, RF11, RN09). |
| Auditoria WCAG completa, responsividade e teste SUS | Validação transversal no fim (RNF09, RNF03, RNF01). A F5 cobre o controle do ciclo, a confirmação e o histórico. |

---

## Assumptions & Open Questions

Toda ambiguidade está resolvida ou registrada aqui — nada fica silenciosamente indefinido.

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --------------------- | -------------- | --------- | ---------- |
| Onde trocar o status | Ação separada a partir do detalhe; o formulário de edição continua sem o campo Status | Decidido com o usuário (2026-10-18) | y |
| Transições permitidas | Exatamente duas: "Em teste" → "Validada" e "Validada" → "Disponível para replicação". "Disponível para replicação" é estágio final | Decidido com o usuário (2026-10-18): só avançar, um passo | y |
| Quem pode avançar | O autor da inovação e toda conta `ADMINISTRADOR`, pelo perfil atual a cada requisição | Decidido com o usuário (2026-10-18); AD-009 | y |
| Significado de "registrada" | Cada avanço cria um registro de histórico com inovação, status anterior, status novo, responsável e data/hora, exibido no detalhe | Decidido com o usuário (2026-10-18) | y |
| Confirmação antes de avançar | Página própria "Avançar status", como a exclusão da F4; só o POST dela grava | Avançar não tem volta, e a RN12 cobre "toda ação destrutiva ou irreversível"; a confirmação também impede que um link seguido por engano ou pré-carregado mude o status (H3, H5) | y |
| Rota | `/inovacoes/<id>/status/`: GET mostra a confirmação, POST avança | Mesmo padrão de `/editar/` e `/excluir/`; parâmetro `pk`, que a varredura da AD-009 já cobre | y |
| Texto da confirmação | "Você vai avançar a inovação “<título>” de “<status atual>” para “<próximo status>”. Depois de avançar, não é possível voltar ao status anterior.", botão "Avançar para “<próximo status>”" e link "Cancelar" para o detalhe | Diz o estado atual, o efeito e que não tem volta | y |
| Inovação já no estágio final | O detalhe mostra "Último estágio do ciclo." no lugar da ação; GET em `/status/` responde 200 com "Esta inovação já está em “Disponível para replicação”, o último estágio do ciclo.", sem botão, e o link "Voltar para a inovação" | design-spec §10 F5: transição inválida é desabilitada com explicação, não escondida sem motivo | y |
| Usuário sem permissão | Vê os estágios e o histórico, não vê a ação de avançar; GET e POST em `/status/` respondem 403 com a página da EDEX-20 | EDEX-24 e design-spec §10 F4: quem não pode não vê a ação | y |
| Texto do acesso negado | O mesmo da EDEX-20 ("Você não tem permissão para alterar esta inovação." / "Só quem cadastrou a inovação ou um administrador pode editá-la ou excluí-la.") | AD-009 fixa uma página só; reescrever a segunda frase mexeria nos testes da F4. A frase não cita o status, mas continua verdadeira | y |
| Proteção contra duplo envio e corrida | O formulário de confirmação envia o status que a pessoa viu; o POST trava a linha e só avança se o status gravado for igual ao enviado | Sem isso, dois cliques ou duas pessoas ao mesmo tempo levariam "Em teste" direto a "Disponível para replicação", pulando um estágio | y |
| Mensagem de conflito | Nada muda; redirect ao detalhe com "O status desta inovação já foi alterado para “<status gravado>”. Confira o status atual antes de avançar." (nível aviso) | Explica por que nada aconteceu e o que fazer (H9) | y |
| Mensagem de sucesso | Redirect 302 ao detalhe com "Status da inovação “<título>” alterado de “<anterior>” para “<novo>”." (nível sucesso), uma vez só | RF12; mesmo padrão da EDEX-06 | y |
| Ordem e formato do histórico | Seção "Histórico de status" no detalhe, do mais antigo ao mais recente; cada item: "<dd/mm/aaaa HH:MM> — de “<anterior>” para “<novo>”, por <nome completo ou username>"; vazio: "Nenhuma mudança de status registrada." | Ordem cronológica lê como o ciclo; responsável pelo mesmo critério da CONS-13 | y |
| Estágio atual no controle | Lista ordenada dos três estágios; o atual marcado por texto "(status atual)", não só por cor | WCAG 1.4.1; design-spec §6 badge de status | y |
| Exclusão da inovação | Apagar a inovação apaga o histórico dela | A exclusão da F4 é definitiva; histórico sem inovação não tem onde ser exibido | y |
| Exclusão da conta responsável | A conta que fez uma mudança não pode ser apagada enquanto houver registro dela (proteção, como em `Inovacao.autor`) | Mesmo critério da F2: excluir uma conta não apaga o conhecimento registrado | y |
| Validade das transições no banco | O banco recusa um registro de histórico cujo par (anterior, novo) não seja uma das duas transições | Mesmo critério da `inovacao_status_valido`: a regra não depende só da view | y |
| Banco indisponível | Página 500 do projeto, sem detalhes; nem status nem histórico gravados pela metade | Mesmo padrão da EDEX-44 | y |
| Idioma dos critérios de aceite | EARS em inglês, restante em português | Mesmo padrão das features anteriores; `validate_spec.py` exige `SHALL` | y |

**Open questions:** none - as quatro decisões de produto foram tomadas com o usuário em 2026-10-18; os defaults do agente foram confirmados na aprovação da spec em 2026-10-18.

---

## Dimensions Sweep

Escopo Large ⇒ varredura completa: cada dimensão vira requisito ou recebe `N/A because…` explícito.

| Dimensão | Resolução |
| -------- | --------- |
| Input validation & bounds | STAT-12 (status enviado diferente do gravado, ausente ou inválido → nada muda), STAT-22 (id inexistente → 404). Nenhum campo livre: **N/A** de limite de tamanho. |
| Failure / partial-failure states | STAT-15 (status e histórico na mesma transação), STAT-35 (banco indisponível → 500, nada gravado). |
| Idempotency / retry / duplicate handling | STAT-12 (segundo envio da mesma confirmação não avança de novo), STAT-11 (GET nunca grava). |
| Auth boundaries & rate limits | STAT-16 a STAT-23 (autor, administrador, terceiro negado em GET e POST, staff/superuser `USUARIO` negado, perfil atual, anônimo), STAT-36 (CSRF). Rate limits: **N/A because** nenhum RN/RNF exige e toda conta é criada por administrador. |
| Concurrency / ordering | STAT-12 e STAT-13 (corrida entre duas pessoas: só a primeira avança, a segunda recebe o aviso de conflito). |
| Data lifecycle / expiry | STAT-28 (histórico apagado com a inovação), STAT-29 (conta responsável protegida), STAT-30 (histórico imutável). |
| Observability | STAT-14 (o histórico é o registro observável da mudança). Log técnico: **N/A because** nenhum RNF pede. |
| External-dependency failure | STAT-35 (PostgreSQL indisponível). **N/A** para outros serviços: a F5 não chama nenhum. |
| State-transition integrity | STAT-06 a STAT-10 (só as duas transições, estágio final, sem pular nem voltar), STAT-31 (o banco recusa par inválido no histórico), STAT-32 (status inicial "Em teste" continua), STAT-33 (edição não muda status). |

---

## User Stories

### P1: Ver em que estágio do ciclo a inovação está ⭐ MVP

**User Story**: Como colaborador que consulta o repositório, quero ver em que estágio do ciclo a
inovação está e o que falta, para saber se é um experimento ou uma prática pronta para copiar.

**Why P1**: RN03 e H1 (visibilidade do status); sem o controle, o avanço não tem onde aparecer.

**Acceptance Criteria**:

1. **STAT-01** — WHEN an authenticated user requests `/inovacoes/<id>/` THEN the system SHALL display a section with the heading "Ciclo de vida" containing an ordered list of the three stages in this order: "Em teste", "Validada", "Disponível para replicação".
2. **STAT-02** — The system SHALL mark the Inovacao's current stage in that list with the visible text "(status atual)" and SHALL NOT mark any other stage with it.
3. **STAT-03** — WHILE the logged-in user can alter the Inovacao (`Inovacao.pode_ser_alterada_por`) and its status is "Em teste" or "Validada" the system SHALL display in the "Ciclo de vida" section a link labeled "Avançar para “<próximo status>”" pointing to `/inovacoes/<id>/status/`.
4. **STAT-04** — WHILE the Inovacao's status is "Disponível para replicação" the system SHALL display in the "Ciclo de vida" section the text "Último estágio do ciclo." and SHALL NOT display an "Avançar" link, for any user.
5. **STAT-05** — WHILE the logged-in user can not alter the Inovacao the system SHALL NOT display the "Avançar" link on its detail page.

**Independent Test**: como `maria`, abrir uma inovação própria em "Em teste" e ver os três estágios,
"Em teste (status atual)" e o link "Avançar para “Validada”"; abrir uma do `joao` e ver os estágios
sem o link.

---

### P1: Avançar o status um estágio ⭐ MVP

**User Story**: Como autor de uma inovação, quero avançá-la para o próximo estágio quando ela for
validada ou estiver pronta para replicação, para que outras unidades saibam que podem adotá-la.

**Why P1**: RF09 e RN03; é a operação da feature.

**Acceptance Criteria**:

1. **STAT-06** — WHEN a user who can alter an Inovacao with status "Em teste" requests `/inovacoes/<id>/status/` with GET THEN the system SHALL respond with HTTP 200 and a page titled "Avançar status" showing "Você vai avançar a inovação “<título>” de “Em teste” para “Validada”. Depois de avançar, não é possível voltar ao status anterior.", a submit button labeled "Avançar para “Validada”" and a link labeled "Cancelar" pointing to `/inovacoes/<id>/`.
2. **STAT-07** — WHEN that user submits the confirmation of an Inovacao with status "Em teste" THEN the system SHALL set its status to "Validada" and redirect with HTTP 302 to `/inovacoes/<id>/`.
3. **STAT-08** — WHEN that user submits the confirmation of an Inovacao with status "Validada" THEN the system SHALL set its status to "Disponível para replicação" and redirect with HTTP 302 to `/inovacoes/<id>/`.
4. **STAT-09** — The system SHALL change an Inovacao's status only to the next stage of the sequence "Em teste" → "Validada" → "Disponível para replicação", never skipping a stage and never returning to a previous one.
5. **STAT-10** — IF a user who can alter the Inovacao requests `/inovacoes/<id>/status/` for an Inovacao with status "Disponível para replicação" THEN the system SHALL respond to GET with HTTP 200, the text "Esta inovação já está em “Disponível para replicação”, o último estágio do ciclo.", no submit button and a link labeled "Voltar para a inovação" to `/inovacoes/<id>/`, and SHALL respond to POST by keeping the status unchanged, creating no history record and redirecting to `/inovacoes/<id>/` with that same text as a warning message.
6. **STAT-11** — The system SHALL NOT change the status nor create a history record on a GET request to `/inovacoes/<id>/status/`.
7. **STAT-12** — IF the status submitted with the confirmation is missing or differs from the Inovacao's stored status THEN the system SHALL keep the status unchanged, SHALL create no history record and SHALL redirect to `/inovacoes/<id>/` with the warning "O status desta inovação já foi alterado para “<status gravado>”. Confira o status atual antes de avançar."
8. **STAT-13** — WHEN two confirmations for the same Inovacao and the same current status are submitted concurrently THEN the system SHALL advance the status exactly one stage and create exactly one history record.

**Independent Test**: como `maria`, avançar uma inovação própria de "Em teste" para "Validada" e
depois para "Disponível para replicação", cada vez pela confirmação; voltar o navegador e reenviar a
primeira confirmação e ver o aviso de conflito, com o status ainda em "Disponível para replicação".

---

### P1: Registrar cada mudança e dar feedback claro ⭐ MVP

**User Story**: Como colaborador ou curador, quero ver quem mudou o status, quando e de qual para
qual, e saber na hora se a minha mudança deu certo, para confiar no estágio mostrado.

**Why P1**: pedido explícito da feature (registro + feedback); RF12 é Essencial.

**Acceptance Criteria**:

1. **STAT-14** — WHEN the status of an Inovacao is advanced THEN the system SHALL create one history record with the Inovacao, the previous status, the new status, the logged-in user as responsible and the date and time of the change.
2. **STAT-15** — The system SHALL store the new status and its history record in a single transaction, so that neither exists without the other.
3. **STAT-16** — WHEN the status is advanced THEN the system SHALL display on the detail page, inside the `role="status"` region, the success message "Status da inovação “<título>” alterado de “<anterior>” para “<novo>”." and SHALL NOT display it again when the detail page is reloaded.
4. **STAT-24** — WHEN an authenticated user requests `/inovacoes/<id>/` THEN the system SHALL display a section with the heading "Histórico de status" listing every history record of that Inovacao, from the oldest to the most recent.
5. **STAT-25** — The system SHALL render each history item as "<dd/mm/aaaa HH:MM> — de “<anterior>” para “<novo>”, por <responsável>", with the date in the project's time zone and the responsável by full name or, without one, by username (as in CONS-13).
6. **STAT-26** — WHILE an Inovacao has no history record the system SHALL display in the "Histórico de status" section the text "Nenhuma mudança de status registrada."
7. **STAT-27** — The system SHALL display the history to every authenticated user, including users who can not alter the Inovacao.

**Independent Test**: como `joao` (ADMINISTRADOR), avançar uma inovação da `maria` e ver a mensagem
de sucesso; recarregar e ver que ela some; como `maria`, abrir o detalhe e ver no histórico a linha
"… — de “Em teste” para “Validada”, por <nome do joao>".

---

### P1: Só o autor ou um administrador avança ⭐ MVP

**User Story**: Como autor de uma inovação, quero que só eu e os administradores possamos mudar o
estágio dela, para que ninguém declare validada uma solução da minha unidade.

**Why P1**: RN05 e RNF07 valem para toda alteração de `Inovacao` (AD-009).

**Acceptance Criteria**:

1. **STAT-17** — WHEN the autor of an Inovacao, with profile `USUARIO`, submits the confirmation THEN the system SHALL advance the status as defined in STAT-07 and STAT-08.
2. **STAT-18** — WHEN a user with profile `ADMINISTRADOR` submits the confirmation for an Inovacao of another autor THEN the system SHALL advance the status, SHALL keep the Inovacao's autor unchanged and SHALL record the administrator as responsible in the history.
3. **STAT-19** — IF a user with profile `USUARIO` who is not the autor requests `/inovacoes/<id>/status/` with GET or POST THEN the system SHALL respond with HTTP 403 and the access-denied page defined in EDEX-20 and EDEX-21, SHALL keep the status unchanged and SHALL create no history record.
4. **STAT-20** — IF a user with profile `USUARIO` who is not the autor but has `is_staff` or `is_superuser` set requests `/inovacoes/<id>/status/` with GET or POST THEN the system SHALL respond with HTTP 403 as defined in STAT-19.
5. **STAT-21** — The system SHALL decide each request to `/inovacoes/<id>/status/` from the account's profile at the time of that request, so that an account changed from `ADMINISTRADOR` to `USUARIO` receives HTTP 403 on its next request for another account's Inovacao.
6. **STAT-22** — IF `/inovacoes/<id>/status/` is requested with GET or POST for an id with no Inovacao THEN the system SHALL respond as defined in CONS-15 (HTTP 404, "Inovação não encontrada.") and SHALL create no history record.
7. **STAT-23** — IF an anonymous visitor requests `/inovacoes/<id>/status/` with GET or POST THEN the system SHALL redirect to the login page with `next` set to the requested path and SHALL NOT change any status.

**Independent Test**: como `maria`, abrir `/inovacoes/<id>/status/` de uma inovação do `joao` pela
barra de endereço e receber 403; num teste automatizado, enviar POST com o status correto e conferir
que o status e o histórico continuam iguais. A varredura de `test_controle_autoria.py` cobre a rota
sem alteração.

---

### P1: Histórico íntegro ⭐ MVP

**User Story**: Como curador do repositório, quero que o histórico não possa ser corrigido nem
contrariar o ciclo, para que ele sirva de prova de como a inovação chegou ao estágio atual.

**Why P1**: o histórico só tem valor se for confiável; RN03 vale também para dados gravados fora da tela.

**Acceptance Criteria**:

1. **STAT-28** — WHEN an Inovacao is deleted THEN the system SHALL delete its history records.
2. **STAT-29** — IF an account that is responsible for a history record is deleted THEN the system SHALL refuse the deletion and keep the history record.
3. **STAT-30** — The system SHALL NOT offer any route, screen or Django admin page that edits or deletes a history record.
4. **STAT-31** — IF a history record is stored whose (previous status, new status) pair is neither ("Em teste", "Validada") nor ("Validada", "Disponível para replicação") THEN the database SHALL reject it.
5. **STAT-32** — WHEN an Inovacao is registered THEN the system SHALL set its status to "Em teste" and create no history record.
6. **STAT-33** — IF an edit request carries a value for status THEN the system SHALL keep the status unchanged and create no history record (EDEX-08 extended to the history).

**Independent Test**: num teste automatizado, tentar gravar um registro "Em teste" → "Disponível para
replicação" direto pelo ORM e receber erro de integridade; excluir a inovação pela F4 e conferir que
os registros dela sumiram.

---

### P1: Ciclo, confirmação e histórico acessíveis ⭐ MVP

**User Story**: Como colaborador que usa teclado ou leitor de tela, quero saber o estágio atual e
avançá-lo sem depender de mouse ou de cor.

**Why P1**: RNF09 é Essencial; o controle do ciclo é a tela nova da F5.

**Acceptance Criteria**:

1. **STAT-34** — The system SHALL build the "Ciclo de vida" section, the "Histórico de status" section and the "Avançar status" page only from native HTML elements (`ol`/`ul`, links, a `form` with a `button`), without any positive `tabindex`, with a visible focus indicator on each link and button, and SHALL give the "Avançar status" page a single `h1` and a `<title>` both reading "Avançar status".
2. **STAT-37** — The system SHALL convey the current stage by text (STAT-02) and SHALL meet the contrast pairs of DS-08 for every color the cycle control and the history add to `kira.css`.

**Independent Test**: só com teclado, a partir do detalhe: Tab até "Avançar para “Validada”", Enter,
Tab até "Cancelar" e até o botão, Enter; foco visível em cada passo. Com as cores desligadas
(DevTools, emular acromatopsia), o estágio atual continua identificável pelo texto.

---

## Edge Cases

- **STAT-35** — IF the database is unreachable while a status change is being processed THEN the system SHALL respond with the project's HTTP 500 page, SHALL store neither the new status nor a history record and SHALL NOT expose connection details.
- **STAT-36** — IF a POST to `/inovacoes/<id>/status/` lacks a valid CSRF token THEN the system SHALL respond with HTTP 403 and SHALL keep the status unchanged.
- Inovação cadastrada antes da F5 já em "Validada" ou "Disponível para replicação" (carga de demonstração): o controle mostra o estágio gravado e o histórico mostra "Nenhuma mudança de status registrada." (STAT-02, STAT-26).
- Inovação excluída entre abrir a confirmação e enviá-la: 404 da CONS-15, sem histórico (STAT-22).
- Duplo clique no botão: o segundo POST chega com o status antigo e cai no aviso de conflito (STAT-12).
- Administrador avança a própria inovação: autor e responsável são a mesma conta; nada muda na regra.
- Filtro "Validada" da listagem: a inovação aparece logo depois do avanço (CONS-27, sem mudança).
- Id não numérico em `/inovacoes/abc/status/`: a rota não casa e cai no 404 padrão, como na F4.

---

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
| -------------- | ----- | ----- | ------ |
| STAT-01 | P1: Ver o estágio | Execute | Implementing |
| STAT-02 | P1: Ver o estágio | Execute | Implementing |
| STAT-03 | P1: Ver o estágio | Execute | Implementing |
| STAT-04 | P1: Ver o estágio | Execute | Implementing |
| STAT-05 | P1: Ver o estágio | Tasks | In Tasks |
| STAT-06 | P1: Avançar o status | Execute | Implementing |
| STAT-07 | P1: Avançar o status | Execute | Implementing |
| STAT-08 | P1: Avançar o status | Execute | Implementing |
| STAT-09 | P1: Avançar o status | Execute | Implementing |
| STAT-10 | P1: Avançar o status | Execute | Implementing |
| STAT-11 | P1: Avançar o status | Execute | Implementing |
| STAT-12 | P1: Avançar o status | Execute | Implementing |
| STAT-13 | P1: Avançar o status | Execute | Implementing |
| STAT-14 | P1: Registrar e dar feedback | Execute | Implementing |
| STAT-15 | P1: Registrar e dar feedback | Execute | Implementing |
| STAT-16 | P1: Registrar e dar feedback | Execute | Implementing |
| STAT-17 | P1: Só autor ou administrador | Execute | Implementing |
| STAT-18 | P1: Só autor ou administrador | Execute | Implementing |
| STAT-19 | P1: Só autor ou administrador | Tasks | In Tasks |
| STAT-20 | P1: Só autor ou administrador | Tasks | In Tasks |
| STAT-21 | P1: Só autor ou administrador | Tasks | In Tasks |
| STAT-22 | P1: Só autor ou administrador | Execute | Implementing |
| STAT-23 | P1: Só autor ou administrador | Tasks | In Tasks |
| STAT-24 | P1: Registrar e dar feedback | Execute | Implementing |
| STAT-25 | P1: Registrar e dar feedback | Execute | Implementing |
| STAT-26 | P1: Registrar e dar feedback | Execute | Implementing |
| STAT-27 | P1: Registrar e dar feedback | Execute | Implementing |
| STAT-28 | P1: Histórico íntegro | Execute | Implementing |
| STAT-29 | P1: Histórico íntegro | Execute | Implementing |
| STAT-30 | P1: Histórico íntegro | Tasks | In Tasks |
| STAT-31 | P1: Histórico íntegro | Execute | Implementing |
| STAT-32 | P1: Histórico íntegro | Tasks | In Tasks |
| STAT-33 | P1: Histórico íntegro | Tasks | In Tasks |
| STAT-34 | P1: Acessível | Tasks | In Tasks |
| STAT-35 | Edge Cases | Tasks | In Tasks |
| STAT-36 | Edge Cases | Tasks | In Tasks |
| STAT-37 | P1: Acessível | Tasks | In Tasks |

**ID format:** `STAT-NN`. A numeração segue a ordem de escrita, não a das seções (STAT-17 a STAT-23 ficam na história de autorização).

**Coverage:** 37 total, 37 mapeados para tasks (`tasks.md`, T1 a T11), 0 sem mapeamento.

---

## Rastreabilidade com o Documento de Requisitos

| Requisito | Critérios |
| --------- | --------- |
| RF09 | STAT-03, STAT-06 … STAT-13 |
| RN03 | STAT-01, STAT-02, STAT-04, STAT-09, STAT-10, STAT-31, STAT-32 |
| RF12 | STAT-10, STAT-12, STAT-16 |
| RF14 / RN12 | STAT-06, STAT-11 (confirmação, cancelar, GET não grava) |
| RN05 / RNF07 | STAT-05, STAT-17 … STAT-23, STAT-36 |
| RN08 | STAT-18 (autor não muda) |
| RNF05 | STAT-15, STAT-28, STAT-29, STAT-31 |
| RNF09 | STAT-02, STAT-34, STAT-37 |
| RNF01 (Nielsen) | H1: STAT-01, STAT-02, STAT-16, STAT-24 · H3: STAT-06 · H5: STAT-06, STAT-12 · H9: STAT-10, STAT-12 |

---

## Success Criteria

- [ ] Uma inovação vai de "Em teste" a "Disponível para replicação" em exatamente dois avanços
      confirmados, e o detalhe mostra os dois registros com responsável e data/hora.
- [ ] Nenhum caminho pula, repete ou desfaz um estágio: reenvio, corrida e POST forjado deixam o
      status e o histórico iguais (provado por teste automatizado para cada caso).
- [ ] Um `USUARIO` que não é o autor não vê a ação, e GET e POST em `/status/` respondem 403 sem
      alterar nada, inclusive com `is_staff`.
- [ ] Toda tentativa termina numa mensagem que diz o que aconteceu: sucesso, conflito ou estágio final.
- [ ] O ciclo e a confirmação são operados só com teclado, e o estágio atual é identificável sem cor.

---

## Deferred Ideas

- Comentário ou justificativa opcional ao avançar ("validada no piloto de março").
- Retroceder um estágio com justificativa, restrito ao administrador.
- Notificar o autor quando outra pessoa avançar a inovação.
