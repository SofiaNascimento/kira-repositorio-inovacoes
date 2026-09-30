# Cadastro de Inovação (F2) Context

**Gathered:** 2026-09-27
**Spec:** `.specs/features/cadastro-inovacao/spec.md`
**Status:** Feature concluída e verificada (2026-09-29)

---

## Feature Boundary

Um formulário, acessível a qualquer usuário autenticado dos dois perfis, que grava a entidade
`Inovacao`: título, unidade de origem, categoria, problema/dor, solução aplicada, resultado/impacto e
contato responsável. Autor, data de criação e status inicial `Em teste` são definidos pelo sistema.
Inclui a validação com recuperação de erro (RF13), a mensagem de resultado (RF12), o cancelamento sem
salvar (RF14), a ajuda contextual nos campos (RF15) e as listas controladas de Unidade e Categoria, que
só o perfil `ADMINISTRADOR` mantém. Listagem, detalhe, edição, exclusão e troca de status ficam fora
(F3, F4 e F5).

---

## Implementation Decisions

### Listas controladas (RN07, RN01)

- Unidade e Categoria são tabelas próprias, como as classes da UML, não enum nem texto livre.
- Só o perfil `ADMINISTRADOR` inclui e renomeia itens, pelo Django admin. Os demais perfis recebem
  403 nessas telas, no mesmo padrão da AUTH-22.
- Os valores iniciais nascem de uma data migration. As categorias são as cinco da seção 5 dos
  requisitos: Atendimento interno, Compras, Financeiro, RH, TI interno.
- As unidades iniciais são provisórias (Sede, Filial Norte, Filial Sul, Filial Leste, Filial Oeste) e
  serão renomeadas pelo administrador quando a lista real existir.

### Título único por unidade (RN10)

- Dois títulos colidem quando pertencem à mesma unidade e são iguais sem distinção de maiúsculas e
  minúsculas, depois de remover os espaços nas pontas.
- Acentos contam: "Solução" e "Solucao" são títulos diferentes. Ignorar acentos exigiria a extensão
  `unaccent` do PostgreSQL no deploy.
- A regra é garantida por constraint no banco, como a unicidade de e-mail da F1.

### Campos e ajuda (RN06, RF15)

- Contato responsável é texto livre obrigatório, pré-preenchido com o nome e o e-mail do autor e
  editável.
- A ajuda contextual entra na F2 como P3: um texto de apoio com exemplo em cada campo, associado ao
  campo para leitores de tela.

### Agent's Discretion

Nenhuma área foi marcada como "você decide".

### Declined / Undiscussed Gray Areas → Assumptions

**Pós-cadastro e cancelar** não foi escolhida para discussão. Os defaults estão na tabela de
Assumptions da spec, confirmados pelo usuário na aprovação da spec:

- depois de salvar, redirecionamento à home interna com "Inovação “<título>” cadastrada com
  sucesso.";
- "Cancelar" é um link para a home, sem confirmação;
- "Cadastrar inovação" fica no cabeçalho de toda página autenticada, na rota `/inovacoes/nova/`.

Também registrados como assumption, sem discussão: limites de tamanho, textos exatos das mensagens de
erro, ordem alfabética das listas, bloqueio de exclusão de item de lista em uso e tratamento do duplo
envio pela própria RN10.

---

## Specific References

- Mesmo padrão de restrição por perfil da F1: `has_*_permission` baseado em `is_administrador`
  (`contas/admin.py`).
- Mesmo critério de unicidade case-insensitive do e-mail da F1 (`UniqueConstraint(Lower(...))` em
  `contas/models.py`).
- As mensagens de sucesso usam a região `role="status"` que já existe em `templates/base.html`.

---

## Deferred Ideas

- Comparação de título que ignora acentos, se duplicatas por acentuação aparecerem no uso real.
- Lista real de unidades (sede e filiais), a ser informada e cadastrada pelo administrador.
