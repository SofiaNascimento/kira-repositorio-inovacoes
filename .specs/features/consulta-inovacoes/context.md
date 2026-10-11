# Consulta de Inovações (F3) Context

**Gathered:** 2026-10-03
**Spec:** `.specs/features/consulta-inovacoes/spec.md`
**Status:** Feature implementada e verificada (2026-10-03, `validation.md`, PASS)

---

## Feature Boundary

O lado de leitura do repositório, aberto a qualquer usuário autenticado dos dois perfis: a listagem
resumida (título, categoria, unidade, status), a página de detalhe com todos os campos e o contato
responsável, a busca por palavra-chave em título, problema e solução, e os filtros por categoria,
unidade e status, isolados ou combinados com a busca. Inclui estados vazios claros, a ajuda contextual
nos filtros (RF15), o conjunto de demonstração que mede o RNF08 e a troca dos destinos provisórios da
F2 (home interna) pela listagem e pelo detalhe. Edição, exclusão, troca de status e reaproveitamento
ficam fora (F4, F5, F6).

---

## Implementation Decisions

### Semântica da busca (RF05)

- A busca ignora maiúsculas/minúsculas **e acentos**, nos dois sentidos: "solucao" encontra "solução"
  e "SOLUÇÃO" encontra "solucao".
- O termo é quebrado em palavras por espaço. **Todas as palavras** precisam aparecer, cada uma em
  título, problema ou solução — podem estar em campos diferentes. Cada palavra casa por trecho
  ("caix" encontra "caixa").
- O mecanismo para ignorar acentos (extensão `unaccent` do PostgreSQL ou texto normalizado sem
  extensão) é decisão do Design e vira AD. Na F2 o usuário recusou depender do `unaccent` no deploy;
  o Design precisa pesar isso contra o RNF06.
- A RN10 da F2 não muda: títulos que diferem só por acento continuam distintos no cadastro.

### Lugar e forma da listagem (RF03)

- A listagem fica em `/inovacoes/` e vira a tela inicial: `/` redireciona para ela e a
  `HomeInternaView` provisória sai. O login sem `next` cai na listagem.
- Link "Inovações" no cabeçalho de toda página autenticada.
- Ordem: mais recentes primeiro (data de criação decrescente). 20 por página, com "Anterior",
  "Próxima" e "Página X de Y"; busca e filtros se mantêm ao paginar.

### Detalhe e pós-cadastro (RF04, RN06)

- O detalhe mostra os oito campos da seção 5 e, além deles, "Cadastrada por <nome> em <dd/mm/aaaa>".
  Resultado vazio aparece como "Não informado".
- O cadastro bem-sucedido passa a redirecionar ao detalhe da inovação criada, onde aparece a mensagem
  de sucesso da INOV-28.

### Filtros e conjunto de demonstração (RF06, RF15, RNF08)

- Um único formulário GET: campo de busca, três selects com opção "Todas/Todos", botão "Buscar" e
  link "Limpar filtros". Nada é aplicado sem ação explícita (WCAG 3.2.2); a URL reproduz a consulta.
- Ajuda contextual com exemplo sob cada controle e contagem de resultados acima da lista.
- O conjunto de demonstração tem 500 inovações, gerado por um management command, distribuído pelas
  cinco unidades, cinco categorias e três status. Um teste automatizado mede listagem e busca combinada
  sobre ele.

### Agent's Discretion

Nenhuma área foi marcada como "você decide".

### Declined / Undiscussed Gray Areas → Assumptions

Todas as quatro áreas foram discutidas. Ficaram como assumption, sem discussão, por serem de baixo
risco: textos exatos dos estados vazios e da contagem, limite de 100 caracteres na busca, tratamento de
parâmetros inválidos na URL (página, filtro inexistente), página 404 própria para inovação
inexistente, formato da data, autoria dos registros de demonstração e a tabela semântica da listagem.
Todas estão na tabela de Assumptions da spec.

---

## Specific References

- Mesmos padrões de acessibilidade da F2: `label[for]`, ajuda ligada por `aria-describedby`,
  `aria-invalid` no erro, `:focus-visible` do `templates/base.html`.
- Mensagem de valor fora da lista reaproveitada da INOV-17 ("Selecione uma unidade da lista." /
  "Selecione uma categoria da lista.").
- Mensagem de tamanho excedido no formato da INOV-12.
- Página 500 sem vazamento da AUTH-26.

---

## Deferred Ideas

- Ordenação escolhida pelo usuário (por título, por status) e ordenação por relevância.
- Destaque do termo buscado nos resultados.
- Voltar do detalhe para a listagem preservando busca e filtros.
- Avisar o limite de 100 caracteres no texto de ajuda da busca. O `maxlength="100"` corta em silêncio o que passa disso (digitado ou colado), e a mensagem da CONS-24 só aparece por URL montada à mão. Achado na conferência da parte B (passo 8, 2026-10-11); o usuário manteve o comportamento, igual aos limites da F2.
- `InovacaoForm.label_suffix = ""` (F2) não tem efeito: o `Form.__init__` o sobrescreve com ":", então os rótulos do cadastro saem com dois-pontos. Achado na T17; a F3 não altera o formulário da F2.
