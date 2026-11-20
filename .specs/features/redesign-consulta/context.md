# Redesign da Consulta (R2) Context

**Gathered:** 2026-11-19
**Spec:** `.specs/features/redesign-consulta/spec.md`
**Status:** Spec aprovada em 2026-11-19; pronta para o Design

---

## Feature Boundary

Refaz o miolo da lista de inovações (F3) e do detalhe (F3, F4, F5, F6) conforme a
`docs/design-spec.md` v2 §10, consumindo a casca e os componentes da R1. Sem regra de negócio,
model ou migration novos.

---

## Implementation Decisions

### Ações do detalhe

- "Avançar para “{próximo status}”" sai da seção do ciclo e vira a ação primária no cabeçalho de
  página (§10). Na lateral ficam as etapas, a explicação (alvo do `aria-describedby`), o botão
  desabilitado no último estágio e o aviso para quem não pode alterar.
- "Sinalizar reaproveitamento" é a primária em "Disponível para replicação".
- Editar secundária; Excluir por último, separado.

### Textos

- Os textos da §10 substituem os atuais onde diferem. Cada teste antigo afetado está listado na
  spec para autorização.

### Estado vazio

- Duas variantes da §10: acervo vazio com "Cadastrar a primeira inovação"; sem resultado com
  sugestão e "Limpar filtros", mantendo as etiquetas.

### Paginação

- Entra na R2: números de página, atual com `aria-current="page"`, pontas como texto desabilitado.

### Tabela alternativa

- A tabela atual, sem colunas novas (pedido do usuário, diverge da §10).

### Agent's Discretion

- Parâmetro `exibicao`, janela de páginas, corte do resumo, rótulos das etiquetas, ilustração em
  SVG embutido, ordem da lateral (Contato → Ciclo → Ficha), item de cadastro do histórico, link de
  volta e textos de ajuda dos selects. Todos registrados como assumptions `n` na spec, para
  confirmar na aprovação.

### Declined / Undiscussed Gray Areas → Assumptions

- Ordem da lateral: a §10 pede ordens diferentes em tela larga e estreita, o que contraria a
  restrição de ordem de leitura única; default Contato → Ciclo → Ficha (assumption na spec).

---

## Specific References

- `docs/design-spec.md` v2 §6 (cartão de inovação, indicador de etapas, linha do tempo, cartão de
  contato, etiqueta de filtro ativo), §7 (vazio) e §10 (lista e detalhe).

---

## Deferred Ideas

- Esqueleto de carregamento dos cartões (só faria sentido com carregamento assíncrono).
- Colunas "Cadastrada em" e "Reaproveitamentos" na tabela (§10), caso a tabela atual se mostre
  pobre na UAT.
