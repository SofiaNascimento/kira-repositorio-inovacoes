# Ciclo de Vida do Status (F5) Context

**Gathered:** 2026-10-18
**Spec:** `.specs/features/ciclo-de-vida-status/spec.md`
**Status:** Spec aprovada pelo usuário em 2026-10-18; Design a seguir

---

## Feature Boundary

Avanço do status de uma inovação pelo ciclo da RN03 (Em teste → Validada → Disponível para
replicação), um estágio por vez, por uma ação separada a partir do detalhe, aberta ao autor e a
qualquer administrador. Cada avanço grava um registro de histórico exibido no detalhe. Retroceder,
escolher status livre, alterar o histórico e notificar ficam fora.

---

## Implementation Decisions

### Onde trocar o status

- Ação separada no detalhe, rota `/inovacoes/<id>/status/`; o formulário de edição continua sem o
  campo Status (EDEX-08 intacta).

### Transições

- Só avançar, um passo: "Em teste" → "Validada" → "Disponível para replicação". Sem pular, sem
  voltar; "Disponível para replicação" é final.

### Registro da mudança

- Histórico de mudanças: inovação, status anterior, status novo, responsável e data/hora, gravado na
  mesma transação do novo status e exibido no detalhe a todo usuário autenticado.

### Quem pode avançar

- Autor ou `ADMINISTRADOR`, pela regra única da AD-009 (`Inovacao.pode_ser_alterada_por`).

### Agent's Discretion

Nenhuma área foi deixada explicitamente a critério do agente. Os detalhes sem pergunta direta
(página de confirmação, proteção contra duplo envio e corrida, textos, estágio final explicado no
lugar da ação, ordem do histórico, `on_delete` do histórico, constraint de transição no banco) estão
na spec como assumptions, confirmadas na aprovação de 2026-10-18.

### Declined / Undiscussed Gray Areas → Assumptions

Nenhuma área foi recusada: as quatro propostas foram discutidas e decididas pelo usuário.

---

## Specific References

- Confirmação no padrão da exclusão da F4: GET mostra a página, só o POST grava.
- design-spec §10 F5: controle que mostra o ciclo com o estado atual evidente; transição inválida
  desabilitada com explicação, não escondida sem motivo.
- Mensagem de sucesso no formato da EDEX-06, na região `role="status"`.

---

## Deferred Ideas

- Comentário ou justificativa opcional ao avançar.
- Retroceder um estágio com justificativa, restrito ao administrador.
- Notificar o autor quando outra pessoa avançar a inovação.
- Teste de contraste do ciclo e do histórico que leia toda regra cujo seletor **contenha** `.ciclo`/`.historico` (não só as que começam pela classe) e exija cada uma na `CADEIA_DO_COMPONENTE` — fecha o risco residual A6/A7 da STAT-37 aceito no fechamento da F5 (`validation.md`, Decisão do usuário).
- Emendar STAT-06/STAT-34 para "o `<title>` começa por 'Avançar status'" na próxima revisão da spec.
- Helper de testes que analise a página inteira como DOM (ignora comentários, `<template>` e `<details>` fechado; herda `hidden`/`inert`/`aria-hidden` de qualquer ancestral sem depender de caixa ou aspas; decodifica entidades) e substitua as checagens por regex de exibição do ciclo — fecha o risco residual F1–F18 do passe de design aceito em 2026-10-18 (`validation.md`).
