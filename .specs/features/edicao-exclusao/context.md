# Edição e Exclusão de Inovações (F4) Context

**Gathered:** 2026-10-11
**Spec:** `.specs/features/edicao-exclusao/spec.md`
**Status:** Feature implementada e verificada (2026-10-11, `validation.md`, iteração 2 PASS; conferência manual 20/20)

---

## Feature Boundary

Telas de edição e de exclusão de uma inovação, abertas ao autor e a qualquer administrador e negadas
com 403 a qualquer outro usuário comum, na tela e na requisição. A edição altera os sete campos do
cadastro; a exclusão é definitiva e só acontece pelo POST de uma página de confirmação. Status,
histórico, recuperação e ações na listagem ficam fora.

---

## Implementation Decisions

### Onde ficam as ações

- "Editar" e "Excluir" só no detalhe da inovação, visíveis só para o autor e para administradores.
- A listagem da F3 continua só de leitura, sem coluna de ações.

### Resposta ao acesso negado

- HTTP 403 com página própria: "Você não tem permissão para alterar esta inovação.", a explicação de
  quem pode, e o link "Voltar para a inovação".
- Não esconder a existência com 404: todo usuário autenticado já abre o detalhe de qualquer inovação
  (CONS-08).
- A negação vale em GET e em POST; o POST negado não altera nada.

### Confirmação da exclusão

- Página própria "Excluir inovação" que nomeia a inovação (título, unidade, categoria) e avisa que a
  ação não pode ser desfeita; botão "Excluir definitivamente" (POST) e link "Cancelar" para o
  detalhe. Sem JavaScript, sem digitar o título.
- Exclusão definitiva: a linha sai do banco. Sem lixeira nem recuperação.
- Depois de excluir, a lista com "Inovação “<título>” excluída com sucesso.".

### Escopo da edição

- Os sete campos do cadastro; o status não entra no formulário (fica para a F5, que define as
  transições do RN03).
- Edição concorrente: a última gravação vence. A unicidade do título continua garantida pela
  constraint da F2.

### Agent's Discretion

Nenhuma área foi deixada explicitamente a critério do agente. Os detalhes sem pergunta direta
(rotas, textos, destino após salvar, ordem 404/403, CSRF, perfil lido a cada requisição) estão na
spec como assumptions `n`, confirmadas na aprovação.

### Declined / Undiscussed Gray Areas → Assumptions

Nenhuma área foi recusada: as quatro propostas foram discutidas. Os pontos de baixo risco declarados
durante a discussão (negação também no POST, anônimo vai ao login, rotas `/editar/` e `/excluir/`,
GET da exclusão nunca apaga, exclusão repetida → 404, valores atuais no formulário, autor e data
preservados na edição do administrador, edição de inovação já excluída → 404) estão na tabela de
Assumptions da spec.

---

## Specific References

- Confirmação no padrão do `DeleteView` do Django: GET mostra a página, POST apaga.
- Mensagens de sucesso no mesmo formato da INOV-28: "Inovação “<título>” atualizada com sucesso." e
  "Inovação “<título>” excluída com sucesso.".
- Mesmo formulário e mesmas mensagens do cadastro (F2); "Salvar alterações" no lugar de "Salvar".

---

## Deferred Ideas

- Histórico de alterações e registro de quem excluiu o quê (útil para a curadoria do administrador;
  nenhum RF pede).
- Exclusão lógica com recuperação pelo administrador.
- Detecção de edição concorrente por versão do registro.
- Página própria, em português, para a recusa de CSRF (hoje é a padrão do Django, em inglês; ocorre
  quando a sessão expira com o formulário aberto). Achado no Design.
