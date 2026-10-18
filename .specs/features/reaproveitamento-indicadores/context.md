# Reaproveitamento e Indicadores (F6) — Context

**Gathered:** 2026-10-18
**Spec:** `.specs/features/reaproveitamento-indicadores/spec.md`
**Status:** Spec e Design aprovados em 2026-10-18 · Tasks em revisão

---

## Feature Boundary

A F6 deixa qualquer colaborador autenticado registrar que uma unidade reaproveitou uma inovação
"Disponível para replicação" (RF11, RN09), mostra no detalhe quais unidades já a reaproveitaram e
entrega o painel `/indicadores/` com total de inovações, distribuição por categoria e por unidade e a
contagem de reaproveitamentos (RF10), em cards, gráficos e tabelas. O status da inovação só é lido,
nunca escrito (AD-011).

---

## Implementation Decisions

### De onde vem a unidade que reaproveitou

- A unidade é escolhida num select da tela de sinalização (lista controlada `Unidade`, RN07).
- O modelo `contas.Usuario` não ganha unidade; nenhuma conta existente muda.
- A conta que sinalizou fica gravada como responsável (`registrado_por`), além da unidade.

### Duplicidade

- Uma sinalização por par (inovação, unidade), garantida por restrição única no banco.
- A segunda tentativa é recusada com mensagem; a métrica conta unidades que reaproveitaram, não cliques.

### Quem sinaliza

- Qualquer usuário autenticado, autor ou não, `USUARIO` ou `ADMINISTRADOR`.
- A unidade de origem da inovação não pode ser escolhida (RN09: "por outra unidade").
- A sinalização não altera a `Inovacao`, então a view não herda `AlteracaoDeInovacaoMixin` (AD-009);
  a rota nova entra na allowlist da varredura de autoria como exceção consciente.

### Painel

- Cards de métrica, gráficos de barras e tabelas acessíveis (design-spec §10 F6).
- Gráficos em SVG gerado no servidor pelo template, sem JavaScript nem biblioteca nova; cada gráfico
  tem rótulos de dado e a tabela correspondente como alternativa.

### Abordagem de implementação (Design, 2026-10-18)

- A regra da RN09 mora em `Inovacao.registrar_reaproveitamento` (AD-012), não no formulário nem em trigger.
- O painel fica numa app nova `indicadores`, só de leitura e sem modelos; `Reaproveitamento` e a sinalização ficam em `inovacoes`.

### Agent's Discretion

- Textos exatos de títulos, mensagens e rótulos (fixados na spec; o usuário pode corrigir na aprovação).
- Ordenação das linhas das distribuições e inclusão de itens com zero.
- Correção de sinalização errada pelo Django admin (só `ADMINISTRADOR`, só ver e excluir).

### Declined / Undiscussed Gray Areas → Assumptions

Registradas na tabela de Assumptions da spec: exclusão da inovação apaga os reaproveitamentos;
unidade e conta responsável ficam protegidas; link de sinalização ausente (não desabilitado) fora de
"Disponível para replicação"; sem confirmação extra (o envio do formulário já é a ação explícita);
painel sem filtro de período; medição do RNF08 com o conjunto de demonstração mais reaproveitamentos
criados pelo teste.

---

## Specific References

- `docs/design-spec.md` §10 F6: "Dashboard com cards de métrica e gráficos. Gráficos trazem rótulos de
  dado e uma alternativa em tabela acessível (não dependem de cor). Ação 'sinalizar reaproveitamento'
  só aparece em inovação 'Disponível para replicação'."
- `docs/modelagem-uml.md` §2.1: `Inovacao 1 → 0..* Reaproveitamento`, `Reaproveitamento 0..* → 1
  Unidade`; operação `podeSerReaproveitada()` em `Inovacao`.
- `docs/mapa-de-features.md` F6: se o prazo apertar, RF11 + dashboard mínimo; RF10 completo vira
  incremento. A escolha por gráficos mantém o RF10 completo nesta feature.

---

## Deferred Ideas

- Ranking das inovações mais reaproveitadas no painel.
- Filtro do painel por período ou por unidade.
- Desfazer a própria sinalização sem passar pelo administrador.
- Comentário sobre como a unidade adaptou a solução ao reaproveitar.
- Unidade de lotação no modelo de usuário (pré-preencheria o select).
- Carga de demonstração com reaproveitamentos.
