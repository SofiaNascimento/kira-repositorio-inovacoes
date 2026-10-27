# Acervo Realista — Specification

Substitui o conteúdo do comando `carregar_demonstracao` (RNF08): as 500 inovações deixam de ser
"Demonstração 001…500" com frases sorteadas e passam a parecer um acervo real de back office,
para o ambiente publicado (deploy-producao). **Supersede CONS-44 e CONS-45** da
`consulta-inovacoes`; CONS-46 a CONS-48 continuam valendo sobre o conteúdo novo.

## Problem Statement

O sistema publicado vai ser mostrado a avaliadores e usuários. Com a carga atual, a lista mostra
"Demonstração 042", o detalhe diz "Cadastrada por demo", todas as datas são o minuto da carga, não
há histórico de status nem reaproveitamento, e o painel de indicadores fica zerado. Parece teste,
não um repositório em uso.

## Goals

- [ ] 500 inovações com títulos, problemas, soluções, resultados e contatos plausíveis de back office, sem marca de teste em nenhum texto visível.
- [ ] Autoria, datas, histórico de status e reaproveitamentos coerentes entre si, para que detalhe, lista e painel pareçam de um sistema em uso há meses.
- [ ] A carga continua reproduzível e idempotente, e serve aos testes de desempenho do RNF08.

## Code Reuse Analysis

| Item | Onde | Situação | Reuso |
| ---- | ---- | -------- | ----- |
| Comando | `inovacoes/management/commands/carregar_demonstracao.py` | 500 títulos "Demonstração NNN", textos de um vocabulário sorteado, conta `demo` | Mesmo nome e mesma mensagem final; conteúdo, autoria e datas trocados |
| Testes do comando | `inovacoes/tests/test_carregar_demonstracao.py` | Fixam títulos "Demonstração NNN", conta `demo` e `VOCABULARIO` | Reescritos para as ACs desta spec (autorizado: o usuário escolheu substituir) |
| Testes de desempenho | `inovacoes/tests/test_desempenho.py` (CONS-46 a 48), `indicadores/tests/test_desempenho_painel.py` (REAP-41/42) | Usam `VOCABULARIO`, "Demonstração NNN" e `autor__username="demo"` | Ajustados para escolher termos e inovações do conteúdo novo, sem mudar limite nem o que medem |
| Mudança de status | `Inovacao.avancar_status(por=, status_visto=)` (AD-011) | Único caminho para mudar status depois do cadastro | Usado para gerar o histórico |
| Reaproveitamento | `Inovacao.registrar_reaproveitamento(unidade=, por=)` (AD-012) | Único caminho para criar reuso | Usado para gerar os reusos |
| Datas | `data_criacao`, `MudancaDeStatus.data`, `Reaproveitamento.data` | `auto_now_add` | Retroagidas por `QuerySet.update()` depois de criar, campos fora da busca (AD-008 não se aplica) |
| Listas | `inovacoes 0004_listas_iniciais` | 5 unidades (Filial Leste/Norte/Oeste/Sul, Sede) e 5 categorias | Lidas do banco, como hoje |

## Out of Scope

| Feature | Reason |
| ------- | ------ |
| Apagar a carga antiga "Demonstração NNN" de bancos que já a têm | O banco publicado está vazio. O banco local tem 499 delas; limpar é decisão separada. |
| Mais de 500 inovações ou volume configurável | O RNF08 fixa o conjunto em 500. |
| Imagens, anexos ou campos novos | O modelo não tem; a carga só preenche o que existe. |
| Renomear as unidades provisórias | INOV-18: o administrador as renomeia quando a lista real existir. |
| Contas de administrador fictícias | Os autores são colaboradores (perfil USUARIO). |

---

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --------------------- | -------------- | --------- | ---------- |
| Onde fica a carga | Substitui o conteúdo de `carregar_demonstracao` | Decisão do usuário. CONS-44/45 são supersedidas por esta spec | y |
| Variação dos registros | ~100 casos base escritos à mão (~20 por categoria), cada um em 1 a 5 unidades com detalhes e números próprios | Decisão do usuário. O mesmo nome de solução em unidades diferentes é o que um acervo de replicação tem | y |
| Contato | "Setor, Unidade — ramal NNNN" | Decisão do usuário. Sem e-mail que possa ser de alguém real | y |
| Autores | 15 contas de colaboradores com nome e sobrenome, perfil USUARIO, sem senha utilizável, e-mail `nome.sobrenome@acervo.invalid` | Decisão do usuário (autores variados). O TLD `.invalid` é reservado e o e-mail não aparece nas telas | y |
| Conta `demo` | A carga nova não a cria nem a usa | Ela é o que fazia o detalhe mostrar "Cadastrada por demo" | y |
| Quem muda o status | O próprio autor da inovação | `avancar_status` não decide autorização; o autor é quem pode alterar (AD-009) | y |
| Quem registra o reaproveitamento | Um autor do acervo diferente do autor da inovação | Plausível: alguém de outra unidade sinaliza o reuso | y |
| Janela de datas | Cadastros nos 540 dias (≈18 meses) antes da execução | Decisão do usuário (datas espalhadas). Relativa à execução, para continuar plausível em qualquer data | y |
| Reprodutibilidade das datas | Os deslocamentos (dias e horas antes da execução) saem de um Random semeado pelo caso; as datas absolutas dependem do dia da execução | Rodar de novo no mesmo banco não mexe no que existe (idempotência); só os ausentes nascem com datas relativas ao novo dia | y |
| Distribuição | Cada unidade, categoria e status em pelo menos 20 inovações | Mantém a garantia da antiga CONS-44, de que os testes de filtro do RNF08 dependem | y |
| Mensagem final | "N inovações de demonstração criadas (500 no total)." | Saída do terminal, não da tela; mantida | y |
| Idempotência | A chave de cada inovação é (título, unidade); ausentes são recriados iguais, com histórico e reusos; nada duplica | Mesmo contrato da antiga CONS-45, estendido ao histórico e aos reusos | y |
| Palavras vetadas nos textos visíveis | "demonstração", "lorem", "fictício", "teste de carga", "exemplo" (sem acento e sem caixa) | São as marcas de dado de teste; "teste" sozinho fica liberado ("período de teste" é plausível) | y |
| Idioma dos critérios | EARS em inglês, restante em português | Padrão das features anteriores | y |

**Open questions:** none (nenhuma).

---

## User Stories

### P1: Inovações que parecem reais ⭐ MVP

**User Story**: Como quem avalia o KIRA publicado, quero ver inovações com títulos, problemas,
soluções e resultados plausíveis de back office, para julgar o sistema como seria em uso.

**Why P1**: É o pedido; sem isso a lista e o detalhe parecem teste.

**Acceptance Criteria**:

1. ACER-01: WHEN `carregar_demonstracao` runs on a migrated database THEN the system SHALL create exactly 500 Inovacoes, each (título, unidade) pair unique.
2. ACER-02: The system SHALL give the 500 Inovacoes at least 90 distinct titles, and each title SHALL appear in at most 5 Inovacoes.
3. ACER-03: The system SHALL give the 500 Inovacoes 500 distinct `problema` texts and 500 distinct `solucao` texts.
4. ACER-04: The system SHALL NOT include, in `titulo`, `problema`, `solucao`, `resultado` or `contato` of any Inovacao, any of the terms "demonstracao", "lorem", "ficticio", "teste de carga" or "exemplo", compared without accents and case.
5. ACER-05: The system SHALL fill `resultado` with a non-empty text on every Inovacao whose status is "Validada" or "Disponível para replicação".
6. ACER-06: The system SHALL set every `contato` to the pattern "<setor>, <unidade> — ramal <4 dígitos>", where <unidade> is the name of that Inovacao's Unidade.
7. ACER-07: The system SHALL place every Unidade, every Categoria and every status in at least 20 of the 500 Inovacoes.
8. ACER-08: WHEN a search for "conciliacao" (without accent) runs on the loaded data THEN the system SHALL return the same non-empty set as a search for "conciliação".

**Independent Test**: rodar o comando num banco migrado e conferir contagens, unicidades, padrões
e o vocabulário vetado sobre o banco.

---

### P1: Autores variados ⭐ MVP

**User Story**: Como quem lê o detalhe, quero ver quem cadastrou cada inovação com nome de
pessoa, não "demo".

**Why P1**: "Cadastrada por demo" em toda página é a marca de teste mais visível.

**Acceptance Criteria**:

1. ACER-09: WHEN the command runs THEN the system SHALL author the 500 Inovacoes with exactly 15 accounts, each with non-empty first and last names, profile `USUARIO`, no usable password and an e-mail ending in `@acervo.invalid`, and every one of the 15 SHALL author at least one Inovacao.
2. ACER-10: The system SHALL NOT create nor use an account named `demo`.
3. ACER-11: WHEN the detail page of a loaded Inovacao is rendered THEN the system SHALL show "Cadastrada por <nome completo do autor>".

**Independent Test**: conferir as 15 contas no banco e abrir o detalhe de uma inovação.

---

### P1: Datas, histórico e reaproveitamentos coerentes ⭐ MVP

**User Story**: Como quem navega pelo sistema publicado, quero datas espalhadas, histórico de
status e reusos registrados, para que detalhe e painel pareçam de um sistema em uso há meses.

**Why P1**: Pedido do usuário; sem isso o painel fica zerado e toda data é o minuto da carga.

**Acceptance Criteria**:

1. ACER-12: The system SHALL set every `data_criacao` within the 540 days before the command ran and not after it, spread over at least 12 distinct calendar months.
2. ACER-13: The system SHALL give every Inovacao with status "Validada" exactly one MudancaDeStatus (Em teste → Validada) and every Inovacao with status "Disponível para replicação" exactly two (Em teste → Validada, Validada → Disponível para replicação), and SHALL give Inovacoes with status "Em teste" none.
3. ACER-14: The system SHALL create every MudancaDeStatus through `Inovacao.avancar_status`, with the Inovacao's author as `responsavel`, and dated after the Inovacao's `data_criacao`, after the previous change of the same Inovacao, and not after the command ran.
4. ACER-15: The system SHALL create at least 60 Reaproveitamentos through `Inovacao.registrar_reaproveitamento`, all on Inovacoes "Disponível para replicação", each in a Unidade other than the Inovacao's origin, and at least 30 distinct Inovacoes SHALL have one or more.
5. ACER-16: The system SHALL date every Reaproveitamento after the date of its Inovacao's change to "Disponível para replicação" and not after the command ran.

**Independent Test**: conferir datas, histórico e reusos no banco; abrir o painel de indicadores
e ver números diferentes de zero.

---

### P1: Carga reproduzível e idempotente ⭐ MVP

**User Story**: Como quem publica, quero poder rodar a carga de novo sem duplicar nada, e recriar
o que foi apagado igual ao original.

**Why P1**: A carga roda à mão no Supabase; uma segunda execução por engano não pode estragar o
acervo.

**Acceptance Criteria**:

1. ACER-17: WHEN the command runs a second time THEN the system SHALL print "0 inovações de demonstração criadas (500 no total)." and end with exactly 500 Inovacoes, 15 author accounts, and the same number of MudancaDeStatus and Reaproveitamentos as before.
2. ACER-18: WHEN two loaded Inovacoes are deleted and the command runs again THEN the system SHALL print "2 inovações de demonstração criadas (500 no total)." and recreate both with the same titulo, unidade, categoria, status, problema, solucao, resultado, contato and author, with their MudancaDeStatus and Reaproveitamentos.
3. ACER-19: WHEN the command finishes THEN the system SHALL print "N inovações de demonstração criadas (500 no total).", where N is the number created in that run.
4. ACER-20: IF there are fewer than 5 Unidades or fewer than 5 Categorias THEN the command SHALL fail with CommandError and SHALL NOT create any Inovacao nor account.

**Independent Test**: rodar duas vezes; apagar duas inovações e rodar de novo.

---

### P2: Desempenho do RNF08 com o conteúdo novo

**User Story**: Como avaliador, quero que as medições do RNF08 continuem valendo sobre o acervo
publicado.

**Why P2**: Os limites não mudam; só os testes precisam escolher termos e inovações do conteúdo
novo.

**Acceptance Criteria**:

1. ACER-21: WHILE the 500 loaded Inovacoes exist, the system SHALL keep satisfying CONS-46, CONS-47 and CONS-48 (listing, two-word search with three filters, query count independent of rows), with the search terms taken from the loaded content.
2. ACER-22: WHILE the 500 loaded Inovacoes and 200 additional Reaproveitamentos exist, the system SHALL keep satisfying REAP-41 and REAP-42 (dashboard under 2 s and constant query count).

**Independent Test**: a suíte de desempenho existente, com os fixtures ajustados.

---

## Edge Cases

- IF a loaded Inovacao is deleted together with its history and reuses THEN the system SHALL recreate them on the next run (ACER-18).
- IF the database already has Inovacoes from other authors (for example the old "Demonstração NNN") THEN the command SHALL leave them untouched and still create its 500 (they are not part of the (título, unidade) set unless the pair coincides).
- WHEN the command runs on any calendar date THEN the system SHALL keep every date within the 540 days before that run (ACER-12, ACER-14, ACER-16).

---

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
| -------------- | ----- | ----- | ------ |
| ACER-01 | P1: Inovações reais | Execute | Implementing |
| ACER-02 | P1: Inovações reais | Execute | Implementing |
| ACER-03 | P1: Inovações reais | Execute | Implementing |
| ACER-04 | P1: Inovações reais | Execute | Implementing |
| ACER-05 | P1: Inovações reais | Execute | Implementing |
| ACER-06 | P1: Inovações reais | Execute | Implementing |
| ACER-07 | P1: Inovações reais | Execute | Implementing |
| ACER-08 | P1: Inovações reais | Execute | Implementing |
| ACER-09 | P1: Autores variados | Execute | Implementing |
| ACER-10 | P1: Autores variados | Execute | Implementing |
| ACER-11 | P1: Autores variados | Execute | Implementing |
| ACER-12 | P1: Datas, histórico e reusos | - | Pending |
| ACER-13 | P1: Datas, histórico e reusos | - | Pending |
| ACER-14 | P1: Datas, histórico e reusos | - | Pending |
| ACER-15 | P1: Datas, histórico e reusos | - | Pending |
| ACER-16 | P1: Datas, histórico e reusos | - | Pending |
| ACER-17 | P1: Reproduzível e idempotente | - | Pending |
| ACER-18 | P1: Reproduzível e idempotente | - | Pending |
| ACER-19 | P1: Reproduzível e idempotente | Execute | Implementing |
| ACER-20 | P1: Reproduzível e idempotente | Execute | Implementing |
| ACER-21 | P2: Desempenho RNF08 | Execute | Implementing |
| ACER-22 | P2: Desempenho RNF08 | Execute | Implementing |

**Coverage:** 22 total, 0 mapped to tasks, 22 unmapped ⚠️

---

## Success Criteria

- [ ] Um avaliador abre a lista, um detalhe e o painel no sistema publicado e não encontra nenhum texto que pareça dado de teste.
- [ ] A suíte inteira, incluindo o RNF08, continua verde.
