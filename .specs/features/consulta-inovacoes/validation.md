# Consulta de Inovações (F3) Validation

**Date**: 2026-10-03
**Iteration**: 1
**Spec**: `.specs/features/consulta-inovacoes/spec.md` (CONS-01 … CONS-53)
**Diff range**: `1063bc8..41fd0b8` em `main` (HEAD = `41fd0b8`). 22 commits de código (T1 `1b4daf3` … T22 `41fd0b8`) e 4 commits `docs(specs)`. 42 arquivos, +2529/−265 (`git diff --stat 1063bc8..HEAD`).
**Verifier**: independent sub-agent (author ≠ verifier)

**Verdict**: PASS ✅

O build gate passa com 380 testes. As 53 ACs têm evidência `file:line` cujo valor afirmado é o que a spec define. O sensor injetou 20 mutações de comportamento num `git worktree` descartável (M1–M15 e as variantes M5b, M6b, M7b, M7c, M8b): 19 morreram e 1 sobreviveu, a M7, que é equivalente. Na M7 a view deixa de devolver `none()` com o form inválido, mas o template já esconde tabela, contagem e estado vazio quando há `form.errors`, então o HTML não muda. As variantes M7b (só o template) e M7c (template e view) morrem. Os testes reapontados da F1 e da F2 mantiveram ou aumentaram o rigor: as 11 asserções removidas foram trocadas por outras iguais ou mais fortes. Ficam 2 spec-precision gaps que não bloqueiam: `page` ≤ 0 na CONS-05, e se o limite de 100 caracteres da CONS-24 conta antes ou depois de aparar os espaços.

---

## Task Completion

| Task | Status | Notes |
| ---- | ------ | ----- |
| T1–T22 | ✅ Done | `tasks.md`: 22 de 22 com `**Status**: ✅ Complete` e todos os Done when marcados |
| T5 | ✅ Done · SPEC_DEVIATION | `inovacoes/views.py:101-102`: `page=0` vai para a página 1 (`max(int(page), 1)`, `:107`) em vez de para a última, que é o que o `get_page(0)` faria. A spec não define o zero (ver SPG-1) |
| T8 | ✅ Done · Done when ajustado | O Done when listava `contas/tests/test_controle_acesso.py:98` (AUTH-11) como inalterado, mas o teste dependia de `GET /` → 200, e a CONS-09 mudou isso. O teste foi reapontado para `GET /inovacoes/` com autorização do usuário (`tasks.md:367`, `:377`). Erro de planejamento: a tabela de reapontamentos do design (`design.md:332`) dava esse teste como válido |
| T17 | ✅ Done · SPEC_DEVIATION de forma | `inovacoes/forms.py:134-136`: `label_suffix=""` vai no `__init__` (`kwargs.setdefault`), porque o `Form.__init__` sobrescreve o atributo de classe. O resultado visível é o mesmo que o design pede (`test_forms_busca.py:169`, `">Buscar</label>"`) |

---

## Spec-Anchored Acceptance Criteria

Caminhos relativos a `inovacoes/tests/`, salvo indicação. Relidos no HEAD `41fd0b8`.

### P1: Ver a lista de inovações

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| CONS-01 | 200; tabela com uma linha por inovação: título, nome da categoria, nome da unidade, rótulo do status | `test_views_lista.py:47` - `status_code == 200`; `:49-57` - `sorted(linhas) == [["Conciliação","Teste Outra Categoria","Teste Outra Unidade","Disponível para replicação"], ["Controle de Caixa","Teste Categoria","Teste Unidade","Em teste"]]`; `:133` - `h1` "Inovações" | ✅ PASS |
| CONS-02 | data de criação decrescente; empate por id decrescente | `test_consultas.py:30` - `ids == [recente, meio, antiga]` com datas forçadas fora da ordem de id (`:24-26`); `:44-45` - `segunda.pk > primeira.pk` e `ids == [segunda, primeira, outra]`; `test_views_lista.py:69` - mesma ordem na tela | ✅ PASS (M5 e M5b mortas) |
| CONS-03 | ≤ 20 por página; "Página X de Y"; "Anterior" ausente na 1ª, "Próxima" ausente na última | `test_views_lista.py:161` - 20 títulos `I24…I05`; `:163-165` - "Página 1 de 2", link `?page=2` "Próxima", `"Anterior" not in nav`; `:172-176` - 5 títulos, "Página 2 de 2", "Anterior" → `?page=1`, `"Próxima" not in nav`; `:184-186` - 20 linhas sem `nav` | ✅ PASS |
| CONS-04 | "Anterior"/"Próxima" mantêm busca e filtros | `test_views_busca.py:219-222` - `parse_qs(proxima) == {q, categoria, unidade, status, page:["2"]}`; `:224` - a página 2 tem as 5 restantes; `:227-230` - `parse_qs(anterior) == {…, page:["1"]}` | ✅ PASS (payload: os 4 parâmetros afirmados por valor) |
| CONS-05 | `page` não inteiro → página 1; acima da última → última; ambos 200 | `test_views_lista.py:193-194` - `?page=abc` → 200 e "Página 1 de 2"; `:200-203` - `?page=99` → 200, "Página 2 de 2", 5 linhas | ✅ PASS · ⚠️ SPG-1 (`page` ≤ 0) |
| CONS-06 | título de cada linha é link para o detalhe | `test_views_lista.py:77` - `<td><a href="/inovacoes/<pk>/">Controle de Caixa</a>`; `:78` - `get_absolute_url() == f"/inovacoes/{pk}/"` | ✅ PASS |
| CONS-07 | anônimo → login com `next` = caminho pedido, com a query string | `test_views_lista.py:101-103` - 302 e `Location == "/entrar/?next=/inovacoes/%3Fq%3Dcaixa"`; `test_views_detalhe.py:152` - `assertRedirects(…, "/entrar/?next=/inovacoes/<pk>/")`; `contas/tests/test_controle_acesso.py:65-71` - varredura de todas as rotas | ✅ PASS |
| CONS-08 | `USUARIO` e `ADMINISTRADOR` veem inovações de todo autor e toda unidade | `test_views_lista.py:81-95` - parametrizado nos 2 perfis; `titulos == {"Da Ana", "Do Bruno"}` (outro autor, outra unidade) | ✅ PASS |
| CONS-09 | autenticado em `/` → 302 para `/inovacoes/` | `contas/tests/test_views_home.py:32` - `assertRedirects(client.get("/"), "/inovacoes/")` (302 é o padrão do `assertRedirects`); `:25` - `redirect_chain == [("/inovacoes/", 302)]` | ✅ PASS |
| CONS-10 | link "Inovações" → `/inovacoes/` no cabeçalho de toda página autenticada | `test_views_cabecalho.py:38-47` - lista, cadastro e detalhe: `<a href="/inovacoes/">Inovações</a>` no `nav` principal, antes de "Cadastrar inovação"; `:54-55` - ausente para o anônimo | ✅ PASS |
| CONS-11 | login sem `next`, seguindo os redirects, termina em `/inovacoes/` | `contas/tests/test_views_home.py:37-41` - POST `/entrar/` sem `next`; `redirect_chain[-1] == ("/inovacoes/", 302)`; `status_code == 200` | ✅ PASS |

### P1: Ver o detalhe de uma inovação

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| CONS-12 | 200; título como `h1`; os 8 campos, cada um com o rótulo antes | `test_views_detalhe.py:42` - 200; `:44` - `<h1>Controle de Caixa</h1>`; `:45-54` - `_pares(html) ==` os 8 pares (rótulo, valor) na ordem; `:63` - status pelo rótulo "Disponível para replicação" | ✅ PASS (payload: os 8 valores afirmados) |
| CONS-13 | "Cadastrada por <nome completo ou username> em <dd/mm/aaaa>" no fuso `America/Sao_Paulo` | `test_views_detalhe.py:71` - `"Cadastrada por Ana Souza em {dd/mm/aaaa}"`; `:79` - `"Cadastrada por bruno em "` (sem nome); `:89-90` - 02:30 UTC de 15/09 → `"… em 14/09/2026"` e `"15/09/2026" not in html` | ✅ PASS |
| CONS-14 | resultado vazio → "Não informado" | `test_views_detalhe.py:97` - `("Resultado ou impacto", "Não informado") in _pares(html)` | ✅ PASS |
| CONS-15 | id sem inovação → 404 com "Inovação não encontrada." e link "Voltar para a lista de inovações" → `/inovacoes/` | `test_views_detalhe.py:156-160` - 404, template próprio, `<h1>Inovação não encontrada.</h1>`, `<a href="/inovacoes/">Voltar para a lista de inovações</a>`; `:168-173` - igual com `DEBUG=True` | ✅ PASS (M9 morta) |
| CONS-16 | quebras de linha de problema, solução e resultado viram quebras | `test_views_detalhe.py:104-106` - `"a<br>b"`, `"c<br>d"`, `"e<br>f"` | ✅ PASS |
| CONS-17 | HTML de qualquer campo sai como texto literal | `test_views_detalhe.py:113-118` - `&lt;b&gt;x&lt;/b&gt;` (solução), `&lt;i&gt;…` (título), `&lt;u&gt;…` (contato) presentes; as formas cruas ausentes | ✅ PASS |
| CONS-18 | link "Voltar para a lista de inovações" → `/inovacoes/` | `test_views_detalhe.py:125` - `<a href="/inovacoes/">Voltar para a lista de inovações</a>` | ✅ PASS |

### P1: Buscar por palavra-chave

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| CONS-19 | só as inovações em que toda palavra aparece como trecho de título, problema ou solução, cada uma podendo estar num campo diferente | `test_consultas.py:77` - `_achadas("conciliacao planilha") == {as_duas}` (título + problema; as que têm só uma das palavras ficam de fora); `:80-86` - cada um dos 3 campos; `:94` - trecho `"caix"`; `test_views_busca.py:66` - na tela, só "Conciliação bancária" | ✅ PASS (M1 E→OU morta) |
| CONS-20 | caixa e acento ignorados no termo e nos campos | `test_consultas.py:97-106` - `"SOLUÇÃO"` acha "solucao" e `"solucao"` acha "Solução"; `test_busca.py:11`, `:18-28`, `:34` (casefold, forma NFD); `test_models.py:122-124` - coluna gravada normalizada | ✅ PASS (M2 e M3 mortas) |
| CONS-21 | termo vazio ou só de espaços não filtra | `test_consultas.py:109-114` - `None`, `""` e `"   "` → as 3 inovações; `test_views_busca.py:312-314` - `q="   "` lista tudo, sem "Limpar filtros"; `test_forms_busca.py:43` | ✅ PASS |
| CONS-22 | palavra só em resultado, contato, categoria ou unidade → não lista | `test_consultas.py:117-129` - os 4 lugares; `_achadas("zeladoria") == set()`, com controle positivo pelo título (`:128`); `test_models.py:185-187` | ✅ PASS |
| CONS-23 | `%`, `_` e `\` casam literalmente | `test_consultas.py:132-145` - `"100%"` não acha "1000", `"a_b"` não acha "axb", `"c:\\temp"` não acha "c:temp"; cada um acha o literal | ✅ PASS |
| CONS-24 | > 100 caracteres → "Use no máximo 100 caracteres (você digitou M)." junto do campo e nenhuma linha | `test_forms_busca.py:66` - `errors == {"q": ["Use no máximo 100 caracteres (você digitou 101)."]}`; `:73` - 100 passa; `test_views_busca.py:236-238`, `:263-267` - mensagem dentro de `id_q_error`, 200, sem `<table>` (com uma inovação que casaria com os 100 primeiros caracteres) | ✅ PASS · ⚠️ SPG-2 (espaços nas pontas) |
| CONS-25 | o termo enviado volta no campo | `test_views_busca.py:74-75` - `<input name="q" … value="CONCILIACAO planilha">` | ✅ PASS |

### P1: Filtrar por categoria, unidade e status

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| CONS-26 | Categoria e Unidade em ordem alfabética depois de "Todas as categorias"/"Todas as unidades"; status "Em teste", "Validada", "Disponível para replicação" depois de "Todos os status" | `test_forms_busca.py:88-105` - listas completas e ordenadas, com um registro criado por último que é o primeiro na ordem alfabética; `:111` - `["Todos os status","Em teste","Validada","Disponível para replicação"]` | ✅ PASS |
| CONS-27 | um filtro → só as inovações com aquele valor | `test_views_busca.py:78-91` - categoria → Primeira e Segunda; unidade → Primeira e Terceira; status → Primeira e Terceira; `test_consultas.py:187-202` | ✅ PASS (M13 morta) |
| CONS-28 | dois ou mais critérios (com ou sem busca) → só as que satisfazem todos | `test_views_busca.py:97-104` - 2 filtros, 3 filtros, 3 filtros + busca (achou e não achou), unidade + busca; `test_consultas.py:205-239` | ✅ PASS |
| CONS-29 | o valor do filtro continua selecionado | `test_views_busca.py:119-121` - `option selected` = pk de RH, pk de Filial Norte e `EM_TESTE` | ✅ PASS |
| CONS-30 | valor inexistente → mensagem no controle, resumo exato em `role="alert"`, nenhuma linha | `test_views_busca.py:240-242` + `:263-267` - "Selecione uma categoria da lista." / "… unidade …" / "Selecione um status da lista." em `id_<campo>_error`; `<div role="alert"><p>Não foi possível buscar. Corrija os campos indicados.</p></div>`; sem `<table>`; `:275-276` - sem contagem nem mensagem de vazio; `test_forms_busca.py:116-131` (pk inexistente e não numérico) | ✅ PASS (M7 equivalente; M7b e M7c mortas) |
| CONS-31 | um único form GET com busca e filtros, botão "Buscar"; nada aplicado ao trocar um select | `test_views_busca.py:173-183` - 1 form `method=get`, `action="/inovacoes/"`, submit "Buscar", nenhum atributo `on*`, nenhum `<script>`; `:195-197` - os 4 controles no mesmo form | ✅ PASS |
| CONS-32 | com busca ou filtro ativo, link "Limpar filtros" → `/inovacoes/` sem parâmetros | `test_views_busca.py:317-329` - cada um dos 4 parâmetros: `<a href="/inovacoes/">Limpar filtros</a>`; `:305` - ausente sem parâmetros; `:313` - ausente com `q` só de espaços | ✅ PASS (M8 e M8b mortas) |

### P1: Contagem e estados vazios

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| CONS-33 | "1 inovação encontrada" / "N inovações encontradas", N = total de todas as páginas | `test_views_lista.py:109` - singular; `:117-118` - "2 inovações encontradas" e sem o singular; `:206-210` - "25 inovações encontradas" nas páginas 1 e 2 | ✅ PASS (M15 morta) |
| CONS-34 | repositório vazio sem filtro → "Nenhuma inovação cadastrada ainda." + link "Cadastrar inovação" → `/inovacoes/nova/`, sem tabela | `test_views_lista.py:125-128` - mensagem, `<a href="/inovacoes/nova/">Cadastrar inovação</a>`, `"<table" not in html`; `test_views_busca.py:359-361` | ✅ PASS |
| CONS-35 | filtro ativo sem resultado → "Nenhuma inovação encontrada para a busca e os filtros informados." + "Limpar filtros", sem tabela | `test_views_busca.py:335-338` - sem `<table>`, sem a mensagem do repositório, mensagem seguida do link; `:344-345` (filtro combinado); `:351-353` (banco vazio com busca) | ✅ PASS (M14 morta) |

### P1: Consulta acessível

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| CONS-36 | busca e 3 selects com `<label>` visível, `for` = `id` do controle | `test_forms_busca.py:134-146` - para os 4 campos: `<label for=X>` com o rótulo exato e um único `<input|select id=X>`. Evidência no HTML do `as_field_group`, que é o que a listagem renderiza (`inovacao_list.html:18-20`) | ✅ PASS |
| CONS-37 | form dentro de `role="search"` | `test_views_busca.py:186-189` - o form GET tem ancestral `role="search"` | ✅ PASS |
| CONS-38 | `<caption>` e `<th scope="col">` Título, Categoria, Unidade, Status | `test_views_lista.py:140-142` - `<caption>Inovações cadastradas</caption>`; cabeçalhos `== ["Título","Categoria","Unidade","Status"]` | ✅ PASS |
| CONS-39 | paginação num `<nav aria-label="Paginação">` | `test_views_lista.py:216-217` - exatamente 1 `nav` rotulado, com os links dentro (`:162-165`) | ✅ PASS |
| CONS-40 | status sempre pelo texto | `test_views_lista.py:53-56` - "Disponível para replicação" e "Em teste" na célula; `test_desempenho.py:91-93` - "Validada" na célula. O template não aplica classe nem cor por status (`inovacao_list.html:53`) | ✅ PASS |
| CONS-41 | só controles nativos, sem `tabindex` positivo, com foco visível | `test_views_acessibilidade_consulta.py:37-68` - lista paginada, lista com busca e detalhe: `tabindex ≤ 0`, nenhum `role` de controle nem `onclick`, todo `<a>` com `href`, regra `:focus-visible` com `outline: Npx solid` e nenhum `outline: none/0` | ✅ PASS |
| CONS-42 | detalhe em lista de descrição, `<dt>` seguido de `<dd>` | `test_views_detalhe.py:45-56` - pares `dt`/`dd` na ordem, `"<dl" in html` | ✅ PASS |
| CONS-43 | controle com erro: `aria-invalid="true"` e o id do erro no `aria-describedby` | `test_views_busca.py:279-286` - os 4 controles inválidos; `:289-294` - sem erro, nem alerta nem `aria-invalid` | ✅ PASS |

### P2: Desempenho com o conjunto de demonstração

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| CONS-44 | 500 inovações "Demonstração 001" a "500", autor `demo` com perfil `USUARIO` e sem senha utilizável; toda unidade, toda categoria e todo status em ≥ 20 | `test_carregar_demonstracao.py:33` - `sorted(títulos) == TITULOS` (001 a 500); `:36-38` - `perfil == "USUARIO"`, `has_usable_password() is False`, nenhuma de outro autor; `:51-56` - os conjuntos de unidades, categorias e status são todos os existentes, e `min(...) >= 20` | ✅ PASS |
| CONS-45 | rodar de novo → exatamente 500 "Demonstração NNN" e exatamente uma conta `demo` | `test_carregar_demonstracao.py:78-80` - "0 … criadas", `count() == 500`, 1 conta `demo`; `:89-92` - recria só as 2 apagadas, com o mesmo conteúdo | ✅ PASS |
| CONS-46 | com a carga, `GET /inovacoes/` em < 2 s de servidor | `test_desempenho.py:46-48` - 200, "500 inovações encontradas", `segundos < 2.0` | ✅ PASS |
| CONS-47 | com a carga, busca de 2 palavras + categoria + unidade + status em < 2 s | `test_desempenho.py:87-94` - 200, `< 2.0`, títulos == esperados calculados sem `buscar()`/`filtrar()`, todas as linhas com o trio | ✅ PASS |
| CONS-48 | nº de consultas não cresce com as linhas da página | `test_desempenho.py:115-118` - `len(com_vinte) == len(com_uma)` (20 linhas de unidades e categorias diferentes); `test_consultas.py:53-56` - 1 consulta | ✅ PASS (M11 morta) |

### P2: Cadastro e cancelamento levam à consulta

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| CONS-49 | cadastro bem-sucedido → 302 para o detalhe da nova inovação | `test_views_cadastro.py:62-65` - `assertRedirects(resposta, f"/inovacoes/{pk}/")` (302); também `:120-123`, `:238-239`, `:246-248` | ✅ PASS (M10 morta) |
| CONS-50 | mensagem da INOV-28 no `role="status"` do detalhe | `test_views_cadastro.py:294` - `redirect_chain == [("/inovacoes/<pk>/", 302)]`; `:296` - "Inovação “Conciliação bancária automática” cadastrada com sucesso." dentro da região `role="status"` | ✅ PASS |
| CONS-51 | "Cancelar" → `/inovacoes/` | `test_views_cadastro.py:342` - `href="/inovacoes/"`; `:351-354` - segue o link: 200, template da listagem, nada gravado | ✅ PASS |

### P3 e edge case

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| CONS-52 | sob cada um dos 4 controles, o texto de ajuda das Assumptions, no `aria-describedby` | `test_forms_busca.py:15-20` - os 4 textos literais da spec; `:149-161` - `<div class="helptext" id="id_<campo>_helptext">texto</div>` depois do controle e no `aria-describedby` | ✅ PASS |
| CONS-53 | banco fora → página 500 do projeto, sem detalhes da conexão | `test_views_erro_500.py:66-94` - listagem e detalhe: 500, template `500.html`, sem host, usuário, senha, `Traceback` nem a mensagem de conexão | ✅ PASS |

**Status**: ✅ 53/53 ACs com evidência que casa com a spec · ⚠️ 2 spec-precision gaps (não bloqueiam)

### Testes reapontados da F1 e da F2 (integridade)

`git diff 1063bc8..HEAD -- inovacoes/tests contas/tests` remove 11 linhas de asserção, e todas foram substituídas:

| Teste | Antes (`1063bc8`) | Agora | Rigor |
| ----- | ----------------- | ----- | ----- |
| `contas/tests/test_views_home.py:20` (AUTH-01) | `GET /` → 200 | `redirect_chain == [("/inovacoes/", 302)]` e 200 (`:25-26`) | ↑ (afirma também o destino) |
| `contas/tests/test_views_home.py:44` (AUTH-01, AUTH-13) | `"ana"` e o form de logout em `/` | os mesmos, na página para onde `/` leva (`:49-50`) | = |
| `contas/tests/test_sessao.py:49` (AUTH-15) | renova com `GET /` | renova com `GET /inovacoes/`; a janela de 8 h segue afirmada | = |
| `contas/tests/test_controle_acesso.py:98` (AUTH-11) | `GET /` 200 nos 2 perfis | `GET /inovacoes/` 200 nos 2 perfis | = (ver T8) |
| `test_views_cabecalho.py:20` (INOV-38) | parâmetro `/` | parâmetro `/inovacoes/` | = |
| `test_views_cadastro.py:60`, `:110`, `:232`, `:243` (INOV-03/08/24/43) | redirect para `/` | redirect para `/inovacoes/<pk da nova>/` | ↑ (pk exato) |
| `test_views_cadastro.py:290` (INOV-28) | `redirect_chain == [("/", 302)]` | `[("/inovacoes/<pk>/", 302)]` + mensagem em `role="status"` | = |
| `test_views_cadastro.py:299` (INOV-29) | recarrega `/` | confirma a mensagem na 1ª renderização (`:302`) e a ausência ao recarregar o detalhe (`:305`) | ↑ |
| `test_views_cadastro.py:339`, `:345` (INOV-36/37) | `href="/"`, template `nucleo/home.html` | `href="/inovacoes/"`, `href == "/inovacoes/"`, template da listagem | = / ↑ |

Nenhum teste removido; contagem 206 → 380.

---

## Discrimination Sensor

Executado num `git worktree add --detach` temporário a partir de `41fd0b8` (scratchpad da sessão), com o `.env` copiado e o mesmo PostgreSQL de teste, uma mutação por vez. Depois de cada mutação, `git checkout` do arquivo no worktree. No fim: `git worktree remove --force` + `git worktree prune`. `git status --porcelain` da árvore real: vazio antes e vazio depois (idêntico ao baseline). HEAD inalterado.

| # | File:line | Mutação | Testes rodados | Killed? |
| - | --------- | ------- | -------------- | ------- |
| M1 | `inovacoes/models.py:77-80` | `buscar`: E → OU (um `Q(...) \| Q(...)`) | `test_consultas`, `test_views_busca` | ✅ Killed (2: `test_consultas.py:69`, `test_views_busca.py:58`) |
| M2 | `inovacoes/busca.py:13` | `normalizar` sem remover os combinantes (acento fica) | `test_busca`, `test_consultas`, `test_views_busca`, `test_models` | ✅ Killed (21) |
| M3 | `inovacoes/busca.py:14` | `normalizar` sem `casefold()` | idem | ✅ Killed (25) |
| M4 | `inovacoes/models.py:162` | `save()` não acrescenta `texto_busca` ao `update_fields` | `test_models` | ✅ Killed (5) |
| M5 | `inovacoes/models.py:68` | `order_by("-id")` (ignora a data) | `test_consultas`, `test_views_lista` | ✅ Killed (2) |
| M5b | `inovacoes/models.py:68` | desempate por `id` crescente | idem | ✅ Killed (2) |
| M6 | `inovacoes/views.py:103` | sem o `paginate_queryset` tolerante (volta o 404 do `ListView`) | `test_views_lista` | ✅ Killed (3) |
| M6b | `inovacoes/views.py:107-109` | `page` não numérico → última página | `test_views_lista` | ✅ Killed (2) |
| M7 | `inovacoes/views.py:83` | form inválido → `consulta` (lista tudo) em vez de `none()` | `test_views_busca` | ⚪ Survived, **equivalente**: o ramo `{% if form.errors %}` (`inovacao_list.html:27-28`) esconde tabela, contagem e estado vazio, e o HTML é idêntico |
| M7b | `inovacao_list.html:27` | sem o ramo `form.errors` (a view mantém o `none()`) | `test_views_busca` | ✅ Killed (4: `test_views_busca.py:270-276`) |
| M7c | `views.py:83` + `inovacao_list.html:27` | as duas proteções removidas | `test_views_busca` | ✅ Killed (8: `:258-267`, `:270-276`) |
| M8 | `inovacoes/views.py:94` | `filtros_ativos` sem `.strip()` na busca | `test_views_busca`, `test_views_lista` | ✅ Killed (`test_views_busca.py:308`) |
| M8b | `inovacoes/views.py:97` | `filtros_ativos` ignora `status` | `test_views_busca` | ✅ Killed (`test_views_busca.py:317[status]`) |
| M9 | `inovacoes/views.py:65` | sem o 404 próprio (cai no 404 padrão) | `test_views_detalhe` | ✅ Killed (2) |
| M10 | `inovacoes/views.py:48` | redirect pós-cadastro volta para `/` | `test_views_cadastro` | ✅ Killed (6) |
| M11 | `inovacoes/models.py:66-67` | sem `select_related` na listagem (N+1) | `test_desempenho`, `test_consultas` | ✅ Killed (`test_desempenho.py:97`, `test_consultas.py:48`) |
| M12 | `carregar_demonstracao.py:68-77` | `bulk_create` no lugar de `save()` um a um | `test_carregar_demonstracao` | ✅ Killed (2: `:59`, `:67`) |
| M13 | `inovacoes/models.py:89-90` | `filtrar` ignora `status` | `test_consultas`, `test_views_busca` | ✅ Killed (3) |
| M14 | `inovacao_list.html:71` | consulta sem resultado cai na mensagem de repositório vazio | `test_views_busca` | ✅ Killed (3) |
| M15 | `inovacao_list.html:32` | contagem só da página atual | `test_views_lista`, `test_views_busca` | ✅ Killed (3) |

**Sensor depth**: expandido (P1 de busca e a regra de dado derivado da AD-008): 18 mutações principais (M1–M15 com as variantes b) mais as 2 de diagnóstico da M7.
**Result**: 19/20 mortas; 1 sobrevivente equivalente (M7), nenhum sobrevivente relevante → PASS ✅

Sobre a M7: o `none()` da view (`views.py:81-83`) é defesa redundante. Nenhum teste HTTP consegue distingui-lo, porque o template já decide pelo `form.errors`. Ele ainda evita a consulta de contagem e o acesso a um `cleaned_data` incompleto (o ramo válido lê `dados["q"]`, `views.py:84-87`). Não é defeito.

---

## Code Quality

| Principle | Status |
| --------- | ------ |
| Minimum code | ✅ Duas views de prateleira, um `QuerySet` com 3 métodos, um módulo puro de 3 funções, um `Form`, um comando |
| Surgical changes | ✅ O diff de produção se limita ao que o design lista. `nucleo/views.py` e `nucleo/home.html` foram removidos, como o design previa |
| No scope creep | ✅ Nada de ordenação escolhida, destaque, operadores nem JavaScript (`test_views_busca.py:182-183`) |
| Matches patterns | ✅ `campo.html`, `MENSAGEM_TAMANHO` e as `error_messages` seguem o `InovacaoForm`; os testes seguem as amostras da F2 |
| Spec-anchored outcome check | ✅ 53/53; 2 spec-precision gaps sinalizados |
| Per-layer Coverage Expectation met | ✅ unit (`busca.py`), integration (model/QuerySet 1:1 com CONS-02, 19–23, 27, 28; migration 0006; form; comando), e2e com happy, edge e erro em `/inovacoes/`, `/inovacoes/<id>/`, `/` e `/inovacoes/nova/` |
| Every test maps to a spec requirement | ✅ Toda docstring cita CONS-NN, AD-008 ou a AC reapontada; `test_views_detalhe.py:176` declara estar fora da CONS-15 (id não numérico) |
| Documented guidelines followed | ✅ nenhuma diretriz no projeto; strong defaults da Test Coverage Matrix (`tasks.md:35-54`) |

---

## Edge Cases

- [x] CONS-53 banco indisponível na listagem e no detalhe (`test_views_erro_500.py:66-94`).
- [x] Busca vazia (CONS-21), curingas (CONS-23), busca longa (CONS-24), filtro inexistente (CONS-30), página inválida (CONS-05), id inexistente (CONS-15), repositório vazio (CONS-34), consulta sem resultado (CONS-35): ver as tabelas acima.
- [x] Invariante da AD-008 em `create`, `save` e `save(update_fields=…)` (lista, tupla, frozenset; campo fora da busca): `test_models.py:115-187`. Migração 0006 com a regra atual: `test_migracoes.py:79-104`.
- [x] Id não numérico cai no 404 padrão, sem a mensagem de inovação (`test_views_detalhe.py:176-180`).
- [x] Carga sem 5 unidades ou 5 categorias: `CommandError`, nada gravado (`test_carregar_demonstracao.py:95-103`).

---

## Gate Check

- **Gate command**: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q` (árvore real, HEAD `41fd0b8`)
- **Result**: exit 0. `ruff check`: All checks passed · `ruff format --check`: 87 files already formatted · `makemigrations --check`: No changes detected · `pytest -q`: 380 passed, 0 failed, 0 skipped (13.75 s)
- **Test count before feature**: 206 (`tasks.md:66`)
- **Test count after feature**: 380
- **Delta**: +174. Nenhum teste removido; as 11 asserções trocadas estão na tabela de reapontamentos acima
- **Skipped tests**: nenhum
- **Failures**: nenhuma

---

## Spec-Precision Gaps (não bloqueiam)

1. **SPG-1 · CONS-05: `page` inteiro ≤ 0.** A AC fala de "não inteiro" e de "maior que a última", e `0` e `-1` são inteiros que não cabem em nenhum dos dois casos. O `Paginator.get_page` mandaria o zero para a última página. A T5 escolheu a primeira (`views.py:101-107`, SPEC_DEVIATION) e o teste afirma isso para `0` (`test_views_lista.py:189-194`). Os negativos caem no mesmo `max(…, 1)`, mas nenhum teste os cobre. Sugestão: acrescentar à CONS-05 "IF it is less than 1 THEN page 1".
2. **SPG-2 · CONS-24: contagem antes ou depois de aparar as pontas.** "exceeds 100 characters" não diz se os espaços nas pontas contam. O `CharField(strip=True)` apara antes do `MaxLengthValidator`, então `" " + "x"*100` é aceito e "você digitou M" reporta o comprimento já aparado. Nenhum teste fixa esse comportamento. Sugestão: definir na spec ("contados depois de remover os espaços nas pontas") e acrescentar um caso de teste.

---

## Fix Plans

Nenhum obrigatório. Sugestões que não bloqueiam o PASS:

### Sugestão 1: fechar os dois spec-precision gaps
- **Fix task**: atualizar o texto da CONS-05 (`page` < 1 → página 1) e da CONS-24 (contagem depois de aparar), e acrescentar `"-1"` ao parametrize de `test_views_lista.py:189` e um caso `" " + "x"*100` aceito em `test_forms_busca.py`.
- **Priority**: Minor

### Sugestão 2: CONS-36 e CONS-52 também na página
- **Root cause**: a evidência está no `as_field_group` do form. A página usa o mesmo render (`inovacao_list.html:18-20`), então nada falha hoje. Mas, se o template trocar o loop por campos escritos à mão, nenhum teste acusa.
- **Fix task**: na varredura de `test_views_acessibilidade_consulta.py`, afirmar `label[for]` e o `aria-describedby` com `_helptext` no HTML da `/inovacoes/`.
- **Priority**: Cosmetic

---

## Requirement Traceability Update

Proposta. O Verifier **não** edita `spec.md`.

| Requirement | Previous Status | New Status |
| ----------- | --------------- | ---------- |
| CONS-01 … CONS-53 | Implementing | ✅ Verified (CONS-05 e CONS-24 com ⚠️ spec-precision gap) |

---

## Summary

**Overall**: ✅ Ready (evidência: `inovacoes/tests/test_consultas.py:77`, `inovacoes/tests/test_views_busca.py:263-267`, `inovacoes/tests/test_desempenho.py:118`)

**Spec-anchored check**: 53/53 ACs matched spec outcome · 2 spec-precision gaps (CONS-05, CONS-24)
**Sensor**: 20 mutações; 19 mortas, 1 equivalente (M7); nenhum sobrevivente relevante
**Gate**: 380 passed, 0 failed

**What works**: lista ordenada e paginada com tolerância a `page` inválido; detalhe com os 8 campos, autor, data no fuso e 404 próprio; busca E por trecho sem caixa e sem acento, só em título, problema e solução, com curingas literais; filtros isolados e combinados; parâmetros inválidos recusados com mensagem e alerta; estados vazios; acessibilidade da consulta; carga de demonstração idempotente pelo `save()`; desempenho medido; cadastro e cancelamento ligados à consulta.

**Issues found**: nenhum bloqueante. SPG-1 e SPG-2 (Sugestão 1); evidência de CONS-36/52 só no nível do form (Sugestão 2).

**Next steps**: UAT interativo da F3 (feature com interface), se o orquestrador o conduzir; aplicar as Sugestões 1 e 2 se o usuário quiser.
