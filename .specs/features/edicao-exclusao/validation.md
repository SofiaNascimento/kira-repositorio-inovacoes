# Edição e Exclusão de Inovações (F4) Validation

**Date**: 2026-10-11
**Iteration**: 2
**Spec**: `.specs/features/edicao-exclusao/spec.md` (EDEX-01 … EDEX-45)
**Diff range**: feature `8ac62d4..6791933` em `main` (HEAD = `6791933`). Correções desta iteração: `ec93572..6791933`, 4 commits (T15 `e3feabe`, T16 `8ed816b`, T17 `602664e`, T18 `6791933`). Arquivos: `inovacoes/tests/conftest.py`, `test_controle_autoria.py`, `test_views_detalhe.py`, `test_views_edicao.py` e `tasks.md` (+184/−40). Nenhum arquivo de produção mudou desde a iteração 1: `git diff b749ff3..6791933 -- ':!inovacoes/tests'` só lista arquivos de `.specs/`.
**Verifier**: independent sub-agent (author ≠ verifier)

**Verdict**: PASS ✅

O gate passa com 492 testes (470 + 22). As quatro sobreviventes da iteração 1 morrem no HEAD: M22 e M22b nos testes de link do detalhe parametrizados por conta, M23b na varredura de rotas com o superusuário `USUARIO`, M24 na coleta, que agora lê os parâmetros capturados e recusa a rota `<int:id>`. As oito mutações novas no caminho de autorização e na busca também morrem, então o sensor fica em 12/12. As 45 ACs têm evidência `file:line` com o valor da spec afirmado. A EDEX-09 ganhou o campo só com espaços (INOV-10), e a EDEX-11 ganhou a busca depois de trocar o título e a solução. Os commits de correção só tocam testes e só reforçam: a fixture `terceiro` foi trocada por `nao_autor_usuario`, que ainda inclui o `terceiro` e acrescenta staff e superusuário, e o filtro `"<int:pk>" in str(padrao.pattern)` foi trocado por uma coleta que pega toda rota com o parâmetro `pk` e falha nas outras. Nenhuma asserção foi removida.

---

## Task Completion

| Task | Status | Notes |
| ---- | ------ | ----- |
| T1–T14 | ✅ Done | Inalteradas desde a iteração 1 (`tasks.md`, 14 de 14 completas) |
| T15 (Fix 1) | ✅ Done | `e3feabe`: fixture `nao_autor_usuario` (`conftest.py:59-76`) e `test_controle_autoria.py:102-121` com 3 contas × 2 rotas × 2 métodos. 478 passed (+8) confere |
| T16 (Fix 2) | ✅ Done | `8ed816b`: `test_views_detalhe.py:212`, `:249` com as 3 contas, e o rebaixado em `:258-277`. +5 confere |
| T17 (Fix 3) | ✅ Done | `602664e`: `test_views_edicao.py:365-375` (INOV-10) e `:482-510` (título e solução). +3 confere |
| T18 (Fix 4) | ✅ Done | `6791933`: coleta em `test_controle_autoria.py:18-40` e +6 testes da coleta (`:61-85`). 492 passed confere com o gate |

---

## Spec-Anchored Acceptance Criteria

Caminhos relativos a `inovacoes/tests/`, salvo indicação. Relidos no HEAD `6791933`. Os arquivos `test_views_exclusao.py`, `test_permissoes.py`, `test_views_acessibilidade_alteracao.py` e `test_views_erro_500.py` não mudaram desde a iteração 1, então as linhas deles valem como estão. Em `test_views_edicao.py`, as linhas até 362 não mudaram, e as seguintes foram atualizadas.

### P1: Editar uma inovação que cadastrei

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| EDEX-01 | 200; `<title>`/`h1` "Editar inovação"; exatamente os 7 campos | `test_views_edicao.py:41` - `status_code == 200`; `:45-46` - title e `h1 == ["Editar inovação"]`; `:47` - `list(form.fields) == CAMPOS`; `:49-51`; `:70-72` - botão `["Salvar alterações"]` | ✅ PASS |
| EDEX-02 | todos os campos com o valor salvo, inclusive o contato salvo | `test_views_edicao.py:83-97` - os 7 valores salvos, contato salvo, sem pré-preenchimento da INOV-39, `option selected` | ✅ PASS |
| EDEX-03 | link "Editar" → `/inovacoes/<id>/editar/` para quem pode alterar | `test_views_detalhe.py:199` (autor), `:209` (administrador em inovação alheia) - `_links(html,"Editar") == ["/inovacoes/<pk>/editar/"]` | ✅ PASS |
| EDEX-04 | mesma inovação atualizada, textos aparados, nenhuma nova | `test_views_edicao.py:206-209`, `:217-220` - cada campo `== dados[campo].strip()`, `count() == 1` | ✅ PASS |
| EDEX-05 | 302 → `/inovacoes/<id>/` | `test_views_edicao.py:226` - `assertRedirects(…, f"/inovacoes/{pk}/")` | ✅ PASS |
| EDEX-06 | "Inovação “<título salvo>” atualizada com sucesso." no `role="status"` do detalhe | `test_views_edicao.py:233-235` - `redirect_chain` e texto exato com o título aparado na região de status | ✅ PASS (N4 morta) |
| EDEX-07 | mensagem não reaparece ao recarregar | `test_views_edicao.py:242`, `:244` | ✅ PASS |
| EDEX-08 | autor, status e data forjados ignorados | `test_views_edicao.py:251-263` - `autor_id`, `status == EM_TESTE`, `data_criacao == DATA_ORIGINAL` | ✅ PASS |
| EDEX-09 | mensagens da INOV-09, INOV-10, INOV-12, INOV-17; 200; valores enviados (INOV-11); resumo da INOV-30 em `role="alert"` | `test_views_edicao.py:347-361` (INOV-09, resumo, valores preservados); **`:365-375`** - `solucao="   "`, 200, `errors == {"solucao": ["Descreva a solução aplicada."]}` (texto da INOV-09 na spec da F2, linha 72), mensagem no campo, RESUMO no alerta, linha intacta (INOV-10); `:384` (INOV-17); `:394-396` (INOV-12) | ✅ PASS (Fix 3 resolvido) |
| EDEX-10 | qualquer recusa mantém todos os valores salvos | `test_views_edicao.py:362`, `:375`, `:385`, `:397`, `:420`, `:462` - `_linha(inovacao) == antes` | ✅ PASS |
| EDEX-11 | busca acha pelas palavras novas de título, problema ou solução, e não pelas substituídas | `test_views_edicao.py:475-479` (problema); **`:482-510`** parametrizado por título e solução: pré-condição `:503-504` (antiga acha, nova não), só o campo-alvo troca (`:505`), `:509` - `_titulos_da_busca(palavra_nova) == [titulo]`, `:510` - `_titulos_da_busca(palavra_antiga) == []` | ✅ PASS (Fix 3 resolvido; N7, N8 mortas) |
| EDEX-12 | mesmo título, com ou sem mudança de caixa, mesma unidade → aceito | `test_views_edicao.py:400-406` - parametrizado, `assertRedirects` e título gravado | ✅ PASS |
| EDEX-13 | título de outra inovação da unidade (ignorando caixa) → "Já existe uma inovação com este título nesta unidade. Escolha outro título." no campo | `test_views_edicao.py:415-420`; outra unidade aceita (`:423-432`), acento distinto (`:435-443`) | ✅ PASS |
| EDEX-14 | corrida → só uma persiste; a outra 200 com a mensagem da EDEX-13, nunca 500 | `test_views_edicao.py:457-464` - constraint real, 200, `errors == {"titulo": [MENSAGEM_DUPLICADO]}`, resumo, `count == 1` | ✅ PASS |
| EDEX-15 | duas edições em sequência → vale a última | `test_views_edicao.py:293-296` | ✅ PASS |
| EDEX-16 | "Cancelar" → `/inovacoes/<id>/`, sem alterar, sem confirmação | `test_views_edicao.py:105-110` | ✅ PASS |

### P1: Curadoria pelo administrador

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| EDEX-17 | ADMINISTRADOR em inovação alheia → 200 e o form da EDEX-01 | `test_views_edicao.py:118`; `test_permissoes.py:31` | ✅ PASS |
| EDEX-18 | aplica EDEX-04 a 06 e mantém autor e data originais | `test_views_edicao.py:271-280` | ✅ PASS (N4 morta) |
| EDEX-19 | autor USUARIO e autor ADMINISTRADOR editam e excluem do mesmo jeito | `test_permissoes.py:15`, `:21`; `test_views_edicao.py:124`, `:286-288`; `test_views_exclusao.py:70`, `:197-199` | ✅ PASS |

### P1: Negar a alteração de inovações de terceiros

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| EDEX-20 | GET de USUARIO não autor nas duas rotas → 403 com os dois textos exatos | `test_views_edicao.py:56-60` e `test_views_exclusao.py:113-117` - 403, template, os dois textos exatos; **`test_controle_autoria.py:102-121`** - `[terceiro|staff|superusuario]` × rota × GET: `status_code == 403` (`:119`), `values() == antes` (`:120`). A fixture confere `perfil == USUARIO` e as bandeiras (`conftest.py:70-75`) | ✅ PASS (Fix 1 resolvido; M23b, N1 mortas) |
| EDEX-21 | link "Voltar para a inovação" → `/inovacoes/<id>/` | `test_views_edicao.py:61-62`; `test_views_exclusao.py:118-120` | ✅ PASS |
| EDEX-22 | POST de edição do terceiro → 403, todos os valores intactos | `test_views_edicao.py:302-305`; `test_controle_autoria.py:115-121` - POST com dados válidos e diferentes, as 3 contas | ✅ PASS (M23b, N1, N6 mortas) |
| EDEX-23 | POST de exclusão do terceiro → 403, inovação continua | `test_views_exclusao.py:224-228`; `test_controle_autoria.py:115-121` (as 3 contas, `count() == 1`) | ✅ PASS (N3 morta) |
| EDEX-24 | sem "Editar"/"Excluir" no detalhe para quem não é autor nem ADMINISTRADOR | `test_views_detalhe.py:212-218`, `:249-255` - `[terceiro|staff|superusuario]`: `_links == []` e o caminho ausente do HTML; `:258-277` - administrador rebaixado por `update()`, que mantém `is_staff` (`:271`), deixa de ver os dois links (`:274-277`) | ✅ PASS (Fix 2 resolvido; M22, M22b, N2 mortas) |
| EDEX-25 | perfil lido a cada requisição; rebaixado → 403 na seguinte | `test_permissoes.py:52-54`; `test_views_edicao.py:141-143`; `test_views_exclusao.py:237-242`; `test_views_detalhe.py:274-277` (tela) | ✅ PASS (N2 morta) |
| EDEX-26 | anônimo em GET e POST nas duas rotas → login com `next`, nada muda | `test_views_edicao.py:160`, `:313-314`; `test_views_exclusao.py:250-253` | ✅ PASS |
| EDEX-27 | `editar` com id inexistente em GET e POST → 404 da CONS-15 | `test_views_edicao.py:149-151`; `:524-526` (POST, nada criado) | ✅ PASS |
| EDEX-28 | `excluir` com id inexistente em GET → CONS-15 | `test_views_exclusao.py:128-130` | ✅ PASS |
| EDEX-29 | edição de inovação excluída no meio → CONS-15, nada criado | `test_views_edicao.py:534-537` (sequencial); `:553-557` (mesma requisição, `count == 0`) | ✅ PASS |

### P2: Excluir uma inovação com confirmação

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| EDEX-30 | autor/ADMINISTRADOR GET → 200, "Excluir inovação", texto exato com título, unidade e categoria | `test_views_exclusao.py:38-44`, `:56`, `:64` | ✅ PASS |
| EDEX-31 | link "Excluir" → `/inovacoes/<id>/excluir/` para quem pode alterar | `test_views_detalhe.py:236`, `:246`, `:266` | ✅ PASS |
| EDEX-32 | botão "Excluir definitivamente" com POST à própria rota | `test_views_exclusao.py:78-84` | ✅ PASS |
| EDEX-33 | link "Cancelar" → `/inovacoes/<id>/` | `test_views_exclusao.py:91-92` | ✅ PASS |
| EDEX-34 | seguir "Cancelar" → detalhe e a inovação continua | `test_views_exclusao.py:93-96` | ✅ PASS |
| EDEX-35 | POST de autor/ADMINISTRADOR → apaga e 302 a `/inovacoes/` | `test_views_exclusao.py:152-153`, `:190-191` | ✅ PASS |
| EDEX-36 | GET nunca apaga | `test_views_exclusao.py:104-106` | ✅ PASS |
| EDEX-37 | linha sai do banco; some da lista, da busca e da contagem da CONS-33 | `test_views_exclusao.py:153`, `:161-173` | ✅ PASS |
| EDEX-38 | segundo POST → CONS-15, nunca 500 | `test_views_exclusao.py:206-207` | ✅ PASS |
| EDEX-39 | detalhe da excluída → CONS-15 | `test_views_exclusao.py:214-215` | ✅ PASS |
| EDEX-40 | "Inovação “<título>” excluída com sucesso." no `role="status"` da lista, uma vez só | `test_views_exclusao.py:181-183` | ✅ PASS |

### P1: Edição, confirmação e acesso negado acessíveis

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| EDEX-41 | rótulos, marcadores, ajudas e erros iguais ao cadastro | `test_views_acessibilidade_alteracao.py:69-72`, `:79-84`, `:91-92`, `:113-115` | ✅ PASS |
| EDEX-42 | só controles nativos, sem `tabindex` positivo, foco visível, nas 3 páginas | `test_views_acessibilidade_alteracao.py:126-136`, `:142-146` | ✅ PASS |
| EDEX-43 | um `h1` e `<title>` "Editar inovação", "Excluir inovação", "Acesso negado" | `test_views_acessibilidade_alteracao.py:153-155` | ✅ PASS |

### Edge Cases da spec

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| EDEX-44 | banco fora → 500 do projeto, nada muda, sem detalhes da conexão | `test_views_erro_500.py:110-133` | ✅ PASS |
| EDEX-45 | POST sem CSRF nas duas rotas → 403, nada muda | `test_controle_autoria.py:124-135` - o próprio autor, `enforce_csrf_checks=True`; 403, não é a página de acesso negado, `values() == antes` | ✅ PASS |

**Status**: ✅ 45/45 ACs com o valor da spec afirmado. Nenhum spec-precision gap.

### RNF07 — "usuário comum tenta alterar registro de terceiro"

| Exigência | Evidência | Result |
| --------- | --------- | ------ |
| GET e POST nas duas rotas, 403 | `test_controle_autoria.py:102-121` (contas × rotas × métodos); `test_views_edicao.py:127-132`, `:299-305`; `test_views_exclusao.py:109-122`, `:218-228` | ✅ |
| Banco intacto campo a campo | `values().get(pk=…) == antes` em `test_controle_autoria.py:120`, `test_views_edicao.py:304`, `test_views_exclusao.py:228` | ✅ |
| Links escondidos | `test_views_detalhe.py:212-218`, `:249-255` (3 contas), `:258-277` (rebaixado) | ✅ |
| Administrador rebaixado | `test_views_edicao.py:135-143`, `test_views_exclusao.py:231-242`, `test_views_detalhe.py:258-277` | ✅ |
| `is_staff`/`is_superuser` sem perfil | modelo `test_permissoes.py:39-45`; rota `test_controle_autoria.py:102-121`; tela `test_views_detalhe.py:212`, `:249` | ✅ |
| Varredura AD-009 dinâmica | `test_controle_autoria.py:18-44`: lê `pattern.converters` e `regex.groupindex`, recolhe toda rota de `inovacoes` com exatamente o parâmetro `pk` em 1 grupo e derruba a coleta nas outras (`:33-39`). Sanidade em `:47-50`; os 5 formatos recusados (`:61-75`) e os aceitos (`:78-85`) têm teste próprio | ✅ (M24, N5 mortas) |

---

## Discrimination Sensor

Executado num `git worktree add --detach` temporário a partir de `6791933` (scratchpad da sessão), com o `.env` copiado e o mesmo PostgreSQL de teste (porta 5433). Linha de base no worktree: 492 passed. Uma mutação por vez, por substituição exata de texto (cada trecho conferido como único), `pytest -q` da suíte inteira e `git checkout -- .` no worktree depois de cada uma, em sequência. No fim: `git worktree remove --force` + `git worktree prune`. `git status --porcelain` da árvore real: vazio antes e vazio depois. HEAD inalterado (`6791933`).

### Sobreviventes da iteração 1, rodadas de novo como descritas

| # | File:line | Mutação | Killed? (testes que falharam) |
| - | --------- | ------- | ----------------------------- |
| M22 | `inovacoes/views.py:128` | `pode_alterar` também para `is_staff` | ✅ 3 falhas: `test_views_detalhe.py::test_terceiro_nao_ve_o_link_editar[staff]`, `…_excluir[staff]`, `test_administrador_rebaixado_deixa_de_ver_os_links_na_requisicao_seguinte` |
| M22b | `inovacoes/views.py:128` | `pode_alterar` também para `is_superuser` | ✅ 2 falhas: `…_editar[superusuario]`, `…_excluir[superusuario]` |
| M23b | `inovacoes/views.py:41` | mixin aceita `is_superuser` (sem tocar o modelo) | ✅ 4 falhas: `test_controle_autoria.py::test_terceiro_recebe_403_e_nada_muda[superusuario-{editar,excluir}-{get,post}]` |
| M24 | `inovacoes/urls.py:18` | rota nova `<int:id>/status/` sem guarda | ✅ erro de coleta em `test_controle_autoria.py:34`: "captura ['id'] … só sabe montar rotas nomeadas com exatamente o parâmetro pk"; pytest sai com 2 |

### Mutações novas (iteração 2)

| # | File:line | Mutação | Killed? (testes que falharam) |
| - | --------- | ------- | ----------------------------- |
| N1 | `inovacoes/views.py:41` | `dispatch` do mixin aceita `is_staff` | ✅ 6 falhas: `[staff-…]` nas 4 combinações e os dois rebaixados (edição e exclusão) |
| N2 | `inovacoes/views.py:128` | `pode_alterar` guardado num cache de módulo por (usuário, inovação): ignora o rebaixamento | ✅ `test_views_detalhe.py::test_administrador_rebaixado_deixa_de_ver_os_links_na_requisicao_seguinte` |
| N3 | `inovacoes/views.py:170` | `InovacaoDeleteView` sem o `AlteracaoDeInovacaoMixin` (`model = Inovacao`) | ✅ 11 falhas, entre elas `[terceiro|staff|superusuario-inovacoes:excluir-{get,post}]` |
| N4 | `inovacoes/views.py:78`, `:150` | mensagem da edição com o título antigo (lido antes de gravar) | ✅ `test_edicao_bem_sucedida_confirma_com_o_titulo_salvo`, `test_administrador_edita_a_inovacao_de_outro_autor_e_mantem_autor_e_data` |
| N5 | `inovacoes/urls.py:18` | `re_path(r"^(?P<inovacao>[0-9]+)/status/$")` sem guarda | ✅ erro de coleta: "captura ['inovacao']" |
| N6 | `inovacoes/views.py:41` | mixin só nega o GET; o POST de qualquer autenticado passa | ✅ 9 falhas: `[terceiro|staff|superusuario-{editar,excluir}-post]` e outras |
| N7 | `inovacoes/views.py:150` | depois de gravar, a edição refaz o `texto_busca` com a solução antiga | ✅ `test_busca_acompanha_a_troca_do_titulo_e_da_solucao[solucao-…]` |
| N8 | `inovacoes/views.py:150` | idem com o título antigo | ✅ `test_busca_acompanha_a_troca_do_titulo_e_da_solucao[titulo-…]` |

**Sensor depth**: expandido (caminho de segurança RNF07/AD-009): 4 sobreviventes da iteração 1 + 8 mutações novas. As 27 mortas da iteração 1 não foram repetidas: nenhum arquivo de produção mudou, e nenhuma asserção que as matava foi removida.
**Result**: 12/12 mortas (4/4 ex-sobreviventes, 8/8 novas) - PASS ✅

---

## Interactive UAT Results

O Verifier roda sem usuário; a conferência no navegador é conduzida pelo orquestrador. **Status (2026-10-11): concluída. 20/20 aprovados; nenhum achado no código.** Contas `maria` (USUARIO, com `is_staff`, que é o caso real do Fix 2) e `joao` (ADMINISTRADOR) em sessões separadas; `admin` só no passo 16. Ids do banco local: 1 "Processo RH" (maria, Filial Leste), 2 "PROCESSO RH" (maria, Filial Norte), 3 "Checklist de compras" (joao, Sede), 4 "Procésso RH" (maria, Filial Leste), 5 "Teste" (maria, Sede · Compras), 6 "Demonstração 001" (demo, Filial Norte · Atendimento interno).

| # | Test | Esperado | Result |
| - | ---- | -------- | ------ |
| 1 | `maria` no detalhe da 1 | "Editar" e "Excluir" abaixo de "Cadastrada por…" (EDEX-03, EDEX-31) | ✅ Pass |
| 2 | Abre a edição | "Editar inovação", sete campos com os valores salvos (contato `maria.teste@kira`), sem Status, botão "Salvar alterações" (EDEX-01, EDEX-02) | ✅ Pass. O usuário pediu que o status também seja editável; decidido manter fora da F4 e tratar na F5 (RF09), como no Discuss |
| 3 | Troca o problema e salva | Detalhe com "Inovação “Processo RH” atualizada com sucesso."; some ao recarregar (EDEX-04 a EDEX-07) | ✅ Pass |
| 4 | Busca `reembolso` e `tetestetstet` | 1 e 0 resultados (EDEX-11) | ✅ Pass |
| 5 | Título vazio; depois "Cancelar" | Resumo + "Informe o título da inovação.", demais campos preservados; cancelar volta ao detalhe intacto (EDEX-09, EDEX-10, EDEX-16) | ✅ Pass |
| 6 | Na 4, título `PROCESSO RH`; depois `PROCÉSSO RH` | Recusado com a mensagem da INOV-22; o próprio título em maiúsculas é aceito (EDEX-12, EDEX-13) | ✅ Pass |
| 7 | `maria` no detalhe da 3 (do joao) | Sem "Editar" e "Excluir" (EDEX-24) | ✅ Pass |
| 8 | `/inovacoes/3/editar/` | "Acesso negado", os dois textos e "Voltar para a inovação" → `/inovacoes/3/` (EDEX-20, EDEX-21) | ✅ Pass |
| 9 | `/inovacoes/3/excluir/` | Acesso negado (EDEX-20) | ✅ Pass |
| 10 | `/inovacoes/999999/editar/` e `/excluir/` | "Inovação não encontrada." (EDEX-27, EDEX-28) | ✅ Pass |
| 11 | Excluir na 5; "Cancelar" | Confirmação com "(Sede · Compras)", botão e cancelar; cancelar mantém a inovação (EDEX-30, EDEX-32 a EDEX-34, EDEX-36) | ✅ Pass |
| 12 | "Excluir definitivamente" | Lista com "Inovação “Teste” excluída com sucesso.", total 504; some ao recarregar (EDEX-35, EDEX-37, EDEX-40) | ✅ Pass |
| 13 | Voltar + reenviar; abrir `/inovacoes/5/` | "Inovação não encontrada." nos dois (EDEX-38, EDEX-39) | ✅ Pass |
| 14 | `joao` edita o contato da 2 | Links visíveis; contato novo; "Cadastrada por Maria Silva em 03/10/2026" mantido (EDEX-17, EDEX-18) | ✅ Pass |
| 15 | `joao` exclui a 6 | Confirmação "(Filial Norte · Atendimento interno)"; total 503 (EDEX-35) | ✅ Pass |
| 16 | `admin` rebaixa o joao; joao recarrega; restaura | Links somem e a edição dá acesso negado; reaparecem ao restaurar (EDEX-25) | ✅ Pass. Senha do `admin` redefinida pelo usuário com `changepassword` |
| 17 | Anônimo em `/inovacoes/1/editar/`; login | Login com `next`; depois cai no formulário (EDEX-26) | ✅ Pass |
| 18 | Cadastro de inovação nova | "Cadastrar inovação", botão "Salvar", detalhe com a mensagem da INOV-28 e os links (regressão da T2/T3) | ✅ Pass |
| 19 | Só teclado: Editar, formulário, erro, salvar; Excluir, confirmação, Cancelar | Ordem visual e foco visível em todos os passos (EDEX-42; Success Criterion de teclado) | ✅ Pass. Fecha o Success Criterion de teclado |
| 20 | DevTools nas três páginas | `label[for]`, `required` e "(obrigatório)", `aria-invalid` e `aria-describedby` com erro, sem `tabindex` positivo (EDEX-41, EDEX-42) | ✅ Pass |

Estado do banco local ao fim: 503 inovações (a "Teste" e a "Demonstração 001" foram excluídas de verdade; `carregar_demonstracao` recriaria a 001); `joao` de volta a ADMINISTRADOR.

---

## Code Quality

| Principle | Status |
| --------- | ------ |
| Minimum code | ✅ Produção inalterada; as correções são uma fixture parametrizada, uma coleta mais estrita e 5 testes novos |
| Surgical changes | ✅ Os commits T15–T18 só tocam `inovacoes/tests/` e `tasks.md` |
| No scope creep | ✅ |
| Matches patterns | ✅ A fixture `nao_autor_usuario` (`conftest.py:59-76`) é reaproveitada na rota e na tela, e confere perfil e bandeiras no setup |
| Spec-anchored outcome check | ✅ 45/45 |
| Per-layer Coverage Expectation met | ✅ A regra da AD-009 sobre `is_staff`/`is_superuser` agora é provada nas três camadas que a aplicam: modelo, mixin (rota) e detalhe (tela) |
| Every test maps to a spec requirement | ✅ Os testes novos citam EDEX-09/10/11/20/22/23/24/25 ou AD-009 na docstring |
| Documented guidelines followed | ✅ nenhuma diretriz no projeto; strong defaults da Test Coverage Matrix |
| Testes só reforçados | ✅ `git diff ec93572..6791933 -- inovacoes/tests`: as 40 linhas removidas são docstrings, o import, o parâmetro `terceiro` (trocado pela fixture que ainda o inclui) e o filtro `"<int:pk>" in str(padrao.pattern)` (trocado por uma coleta que inclui toda rota com `pk` e recusa as demais). Nenhum `assert` removido |

---

## Edge Cases

- [x] Título que existe em outra unidade é aceito (`test_views_edicao.py:423-432`).
- [x] Títulos que diferem só no acento continuam distintos (`test_views_edicao.py:435-443`).
- [x] Unidade inexistente no POST → INOV-17 (`test_views_edicao.py:378-385`). Categoria inexistente coberta pelo formulário da F2.
- [x] Campo obrigatório só com espaços na edição → INOV-09 (`test_views_edicao.py:365-375`).
- [ ] Id não numérico em `/inovacoes/abc/editar/`: sem teste próprio na F4; equivale ao de `/inovacoes/abc/` (`test_views_detalhe.py:176-180`). Não bloqueia.
- Observação (fora da spec, mantida da iteração 1): dois POSTs de exclusão que passam juntos pelo `dispatch()` recebem os dois a mensagem de sucesso. A EDEX-38 só fala do reenvio depois da exclusão (coberto). Não bloqueia.

---

## Gate Check

- **Gate command**: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q` (árvore real, HEAD `6791933`)
- **Result**: exit 0. `ruff check`: All checks passed · `ruff format --check`: 98 files already formatted · `makemigrations --check`: No changes detected · `pytest -q`: 492 passed, 0 failed, 0 skipped (14.58 s)
- **Test count before feature**: 380 (`tasks.md`, linha de base)
- **Test count after iteration 1**: 470
- **Test count after feature**: 492
- **Delta**: +112 na feature (+22 nesta iteração: T15 +8, T16 +5, T17 +3, T18 +6). Nenhum teste removido
- **Skipped tests**: nenhum
- **Failures**: nenhuma

---

## Spec-Precision Gaps

Nenhum.

---

## Fix Plans

Nenhum aberto. Situação dos planos da iteração 1:

| Fix | Resolvido? | Evidência |
| --- | ---------- | --------- |
| Fix 1 (M23b, staff/superuser na rota) | ✅ | `conftest.py:59-76`; `test_controle_autoria.py:102-121`. M23b e N1 morrem |
| Fix 2 (M22, M22b, links do detalhe) | ✅ | `test_views_detalhe.py:212-218`, `:249-255`, `:258-277`. M22, M22b e N2 morrem |
| Fix 3 (EDEX-09 INOV-10, EDEX-11 título e solução) | ✅ | `test_views_edicao.py:365-375`, `:482-510`. N7 e N8 morrem |
| Fix 4 (M24, varredura presa a `<int:pk>`) | ✅ | `test_controle_autoria.py:18-44`, `:61-85`. M24 e N5 morrem |

---

## Requirement Traceability Update

Proposta (o `spec.md` não foi editado pelo Verifier):

| Requirement | Previous Status | New Status |
| ----------- | --------------- | ---------- |
| EDEX-01 … EDEX-45 | Implementing | ✅ Verified |

---

## Histórico

- **Iteração 1** (HEAD `b749ff3`): FAIL ❌. 43/45 ACs (EDEX-09 e EDEX-11 parciais), 27/31 mutantes mortos. Sobreviveram M22 e M22b (links do detalhe para staff/superusuário `USUARIO`), M23b (mixin aceita superusuário) e M24 (varredura presa ao texto `<int:pk>`). Viraram T15 (`e3feabe`), T16 (`8ed816b`), T17 (`602664e`) e T18 (`6791933`), só em teste.
- **Iteração 2** (HEAD `6791933`): PASS ✅. 45/45 ACs, os 4 ex-sobreviventes mortos, 8/8 mutantes novos mortos.

---

## Summary

**Overall**: ✅ Ready (evidência: `inovacoes/tests/test_controle_autoria.py:102-121`, `inovacoes/tests/test_views_detalhe.py:258-277`, `inovacoes/tests/test_views_edicao.py:482-510`)

**Spec-anchored check**: 45/45 ACs com o valor da spec afirmado; 0 spec-precision gaps
**Sensor**: 12/12 mortas (M22, M22b, M23b, M24 e N1–N8)
**Gate**: 492 passed, 0 failed

**What works**: a regra de autoria fica num único método (`inovacoes/models.py:169-178`), aplicada no `dispatch()` antes de qualquer método HTTP (`inovacoes/views.py:35-46`) e no detalhe (`inovacoes/views.py:128`). As três camadas agora são testadas com as contas que a AD-009 exclui: terceiro sem bandeiras, `USUARIO` com `is_staff`, `USUARIO` com `is_superuser` e administrador rebaixado. A varredura da AD-009 não deixa passar em silêncio uma rota de `inovacoes` com parâmetro diferente de `pk` (`test_controle_autoria.py:33-39`). A edição refaz a busca para os três campos (`test_views_edicao.py:475-479`, `:509-510`).

**Issues found**: nenhum.

**Next steps**: ~~o orquestrador atualiza a rastreabilidade do `spec.md` e o `STATE.md`~~ feito em `3fe7d10`. Conferência manual concluída em 2026-10-11, 20/20 (ver *Interactive UAT Results*).
