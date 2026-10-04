# Consulta de Inovações (F3) — Tasks

## Execution Protocol (MANDATORY -- do not skip)

Implement these tasks with the `tlc-spec-driven` skill: **activate it by name and follow its Execute flow and Critical Rules.** Do not search for skill files by filesystem path. The skill is the source of truth for the full flow (per-task cycle, sub-agent delegation, adequacy review, Verifier, discrimination sensor).

**If the skill cannot be activated, STOP and tell the user - do not proceed without it.**

---

**Spec**: `.specs/features/consulta-inovacoes/spec.md`
**Design**: `.specs/features/consulta-inovacoes/design.md`
**Status**: Approved (2026-10-03) — recorte A/B aprovado dentro de uma única feature; Test Coverage Matrix e Gate Check Commands confirmados

**Stack fixado**: Django 5.2.17 · PostgreSQL 16 (AD-003) · pytest + pytest-django · Ruff — o mesmo da F1 e da F2.

**Desvio do design, já decidido aqui:** o design previa uma migration `0005` com `AddField` +
`RunPython`. Como o campo e o preenchimento nascem em tasks separadas, cada uma gera a sua:
`0005_inovacao_texto_busca` (esquema, T13) e `0006_preenche_texto_busca` (dados, T14). O esquema
final é o mesmo; nenhuma das duas foi publicada.

**Recorte em duas partes (proposta de divisão da feature):** as fases seguem a costura
`listagem-detalhe` × `busca-filtros` sugerida em `docs/mapa-de-features.md`.

| Parte | Fases | Tasks | Requisitos | Entrega demonstrável ao fim |
| ----- | ----- | ----- | ---------- | --------------------------- |
| **A — listagem-detalhe** | 1, 2 | T1–T11 | RF03, RF04, RN06 · CONS-01 … CONS-18, CONS-33, CONS-34, CONS-38 … CONS-42, CONS-49 … CONS-51, CONS-53 | Lista paginada como tela inicial, detalhe com contato, cadastro terminando no detalhe |
| **B — busca-filtros** | 3, 4, 5 | T12–T22 | RF05, RF06, RF15, RN07, RNF08 · CONS-04, CONS-19 … CONS-32, CONS-35 … CONS-37, CONS-43 … CONS-48, CONS-52 | Busca sem acento, filtros combinados, estados vazios com filtro, carga de 500 e medição de 2 s |

A parte A não depende de nada da parte B. A parte B só depende da view e do template da listagem
(T4, T5).

---

## Test Coverage Matrix

> Gerada a partir do código, das diretrizes do projeto e da spec — confirmar antes do Execute.
> **Guidelines encontradas: nenhuma.** Não existe `AGENTS.md`, `CONTRIBUTING.md` nem workflow de CI;
> o `pyproject.toml` só configura o pytest (marcador `unit`, `--strict-markers`) e o Ruff, sem limite
> de cobertura. Valem os **strong defaults**: toda AC e todo edge case da spec têm teste; rotas cobrem
> happy + edge + erro. Estilo, local e fixtures seguem as amostras de `inovacoes/tests/`
> (`conftest.py`, `test_models.py`, `test_forms.py`, `test_views_cadastro.py`,
> `test_views_acessibilidade.py`, `test_views_erro_500.py`, `test_migracoes.py`) e
> `contas/tests/test_controle_acesso.py`, que são o piso de profundidade.

| Code Layer | Required Test Type | Coverage Expectation | Location Pattern | Run Command |
| ---------- | ------------------ | -------------------- | ---------------- | ----------- |
| Normalização pura (`inovacoes/busca.py`) | unit | Todo ramo; acentos, caixa, `ß`/`casefold`, espaços múltiplos, termo vazio, separador entre campos (CONS-19, CONS-20, CONS-21) | `inovacoes/tests/test_busca.py` (`@pytest.mark.unit`) | `.venv/bin/pytest -q -m unit` |
| Model e QuerySet (`inovacoes/models.py`: `save()`, `texto_busca`, `get_absolute_url`, `InovacaoQuerySet`) | integration | 1:1 com as ACs de consulta (CONS-02, CONS-19 … CONS-23, CONS-27, CONS-28); a invariante da AD-008 em `create`, `save` e `save(update_fields=…)` | `inovacoes/tests/test_models.py`, `inovacoes/tests/test_consultas.py` | `.venv/bin/pytest -q` |
| Data migration (`0006_preenche_texto_busca`) | integration | Linha criada antes da migration sai com `texto_busca` igual ao da função atual | `inovacoes/tests/test_migracoes.py` | `.venv/bin/pytest -q` |
| Formulário (`inovacoes/forms.py`: `BuscaForm`) | integration | Todo campo × toda mensagem da spec (tamanho, fora da lista); opções e ordem; textos de ajuda. Integration porque os `ModelChoiceField` consultam o banco | `inovacoes/tests/test_forms_busca.py` | `.venv/bin/pytest -q` |
| Views, rotas e templates de página (`inovacoes/views.py`, `nucleo/urls.py`, `inovacoes/templates/inovacoes/*.html`, `templates/base.html`) | e2e | Toda rota que a task adiciona ou altera: happy + todo edge case listado + caminho de erro, pelo `client` | `inovacoes/tests/test_views_*.py`, `contas/tests/test_views_*.py` | `.venv/bin/pytest -q` |
| Management command (`carregar_demonstracao`) | integration | Contagens e distribuição da CONS-44; idempotência da CONS-45; `CommandError` sem listas | `inovacoes/tests/test_carregar_demonstracao.py` | `.venv/bin/pytest -q` |
| Migrations de esquema | none | — (apenas gate de build: `makemigrations --check`) | — | build gate only |

## Gate Check Commands

> Gerados a partir do projeto — confirmar antes do Execute. Todos pelo `.venv/`, com o PostgreSQL 16
> na porta 5433 em execução.

| Gate Level | When to Use | Command |
| ---------- | ----------- | ------- |
| Quick | Depois de tasks só com teste unitário (T12) | `.venv/bin/pytest -q -m unit` |
| Full | Depois de tasks com teste de integração ou e2e | `.venv/bin/pytest -q` |
| Build | Ao fechar uma fase, e em tasks de migration/template | `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q` |

**Linha de base:** 206 testes passando antes da T1 (`.venv/bin/pytest -q`, 2026-10-03).

**Testes da F1 e da F2 que mudam por mudança de spec** (design, *Risks & Concerns*): são
**reapontados** para o comportamento novo dentro da task que muda o comportamento, nunca apagados nem
afrouxados. A contagem total nunca cai.

| Teste | Task | De → para |
| ----- | ---- | --------- |
| `inovacoes/tests/test_views_cadastro.py:62,117,232,238` | T6 | redirect `"/"` → detalhe da inovação criada |
| `inovacoes/tests/test_views_cadastro.py:284,292` | T6 | cadeia `[("/", 302)]` → `[("/inovacoes/<id>/", 302)]`; recarregar o detalhe, e não `/` |
| `inovacoes/tests/test_views_cadastro.py:330` (+ teste da INOV-37) | T7 | `href="/"` → `href="/inovacoes/"` |
| `contas/tests/test_views_home.py:21,28` | T8 | `GET /` 200 → `GET /` segue até `/inovacoes/` (200), com usuário e logout lá |
| `contas/tests/test_sessao.py:49` | T8 | renova a sessão com `GET /inovacoes/` |
| `inovacoes/tests/test_views_cabecalho.py:20` | T8 | parâmetro `"/"` → `"/inovacoes/"` |
| `contas/tests/test_controle_acesso.py:98` | T8 | GET "/" 200 → GET "/inovacoes/" 200 (AUTH-11) |

---

## Execution Plan

As fases são ordenadas e rodam em sequência — cada fase termina antes de a próxima começar, e as
tasks dentro de uma fase executam em ordem.

### Phase 1: Listagem e detalhe (parte A)

QuerySet base, detalhe, 404 próprio, tabela e paginação.

```
T1 → T2 → T3 → T4 → T5
```

### Phase 2: Navegação, costura com a F2 e qualidade da parte A (parte A)

O cadastro passa a terminar no detalhe, `/` vira a listagem, o cabeçalho ganha o link e a parte A
recebe as evidências de acessibilidade e de falha de banco.

```
T6 → T7 → T8 → T9 → T10 → T11
```

### Phase 3: Busca no domínio (parte B)

Normalização, coluna derivada, preenchimento das linhas existentes e os dois métodos de consulta.
Nada de tela.

```
T12 → T13 → T14 → T15 → T16
```

### Phase 4: Busca e filtros na tela (parte B)

O formulário GET, a ligação com a listagem, os parâmetros inválidos e o estado vazio com filtro.

```
T17 → T18 → T19 → T20
```

### Phase 5: Desempenho com o conjunto de demonstração (parte B)

```
T21 → T22
```

---

## Task Breakdown

### T1: `InovacaoQuerySet.para_listagem()` e `Inovacao.get_absolute_url()` ✅

**What**: O manager `objects = InovacaoQuerySet.as_manager()` com `para_listagem()` (ordem, `select_related`, `only`) e a URL canônica do detalhe.
**Where**: `inovacoes/models.py`
**Depends on**: None
**Reuses**: model `Inovacao` da F2; fixture `criar_inovacao` de `inovacoes/tests/conftest.py`
**Requirement**: CONS-02, CONS-06 (URL), CONS-48 (base)

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `InovacaoQuerySet(models.QuerySet)` com `para_listagem()` = `select_related("unidade", "categoria").only("id", "titulo", "status", "data_criacao", "unidade__nome", "categoria__nome").order_by("-data_criacao", "-id")`
- [x] `Inovacao.objects = InovacaoQuerySet.as_manager()`; nenhum `Meta.ordering` novo no model
- [x] `get_absolute_url()` → `reverse("inovacoes:detalhe", args=[self.pk])`. A rota nasce na T2, então o teste da URL entra lá (merge forward); esta task prova a ordem e o carregamento
- [x] Testes de integração em `inovacoes/tests/test_consultas.py`: três inovações com `data_criacao` forçada (`update()` direto) saem em ordem decrescente; duas com a mesma `data_criacao` saem por id decrescente (CONS-02); ler `unidade.nome` e `categoria.nome` de todas as linhas de `para_listagem()` executa 1 consulta (`django_assert_num_queries(1)`)
- [x] Gate check passa: `.venv/bin/pytest -q`
- [x] Test count: 209 testes passam (+3)

**Tests**: integration
**Gate**: full

**Commit**: `feat(inovacoes): adiciona o queryset de listagem de inovacoes`

**Status**: ✅ Complete — 209 passed (+3); get_absolute_url() implementado aqui, mas o teste da URL entra na T2 (a rota nasce lá), como previsto

---

### T2: Página de detalhe (`InovacaoDetailView`, rota e template) ✅

**What**: A rota `/inovacoes/<id>/` mostrando os oito campos numa `<dl>`, a linha "Cadastrada por" e o link de volta.
**Where**: `inovacoes/views.py`
**Depends on**: T1
**Reuses**: `DetailView`; `LoginRequiredMiddleware` + varredura de `contas/tests/test_controle_acesso.py` (AD-006); filtros `linebreaksbr` e `date`
**Requirement**: CONS-06 (URL), CONS-07 (detalhe), CONS-08 (detalhe), CONS-12, CONS-13, CONS-14, CONS-16, CONS-17, CONS-18, CONS-42

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `InovacaoDetailView` com `queryset = Inovacao.objects.select_related("unidade", "categoria", "autor")`, `context_object_name = "inovacao"`; sem decorator
- [x] `inovacoes/urls.py`: `path("<int:pk>/", …, name="detalhe")`
- [x] `inovacoes/templates/inovacoes/inovacao_detail.html`: `h1` = título; "Cadastrada por <nome ou username> em dd/mm/aaaa"; `<dl>` com `<dt>`/`<dd>` para Título, Unidade de origem, Categoria, Problema ou dor, Solução aplicada, Resultado ou impacto, Status, Contato responsável; `linebreaksbr` nos três textos longos; `default:"Não informado"` no resultado; link "Voltar para a lista de inovações" → `/inovacoes/` (literal até a T4 criar `inovacoes:lista`; a T4 troca por `{% url %}`)
- [x] Testes e2e em `inovacoes/tests/test_views_detalhe.py`: 200 com `h1` e os oito pares `dt`/`dd` na ordem (CONS-12, CONS-42); "Cadastrada por Ana Souza em <data>" e, para conta sem nome, "Cadastrada por bruno em …" (CONS-13); `data_criacao` em 03:30 UTC aparece com a data do dia anterior em `America/Sao_Paulo` (CONS-13, fuso); resultado vazio → "Não informado" (CONS-14); problema com `\n` → `<br>` (CONS-16); `<b>x</b>` na solução sai como `&lt;b&gt;x&lt;/b&gt;` (CONS-17); link de volta (CONS-18); `get_absolute_url()` == `/inovacoes/<id>/`; `USUARIO` abre a inovação de outro autor (CONS-08); anônimo → `/entrar/?next=/inovacoes/<id>/` (CONS-07)
- [x] A varredura de `contas/tests/test_controle_acesso.py` passa sem alteração e já inclui `/inovacoes/1/`
- [x] Gate check passa: `.venv/bin/pytest -q`
- [x] Test count: 221 testes passam (+12)

**Tests**: e2e
**Gate**: full

**Commit**: `feat(inovacoes): adiciona a pagina de detalhe da inovacao`

**Status**: ✅ Complete — 222 passed (+13); 13 testes no lugar dos 12 estimados (perfil parametrizado em dois); o teste de fuso usa 02:30 UTC (23:30 do dia anterior em America/Sao_Paulo, UTC-3), pois 03:30 UTC ainda e o mesmo dia; get_absolute_url() (T1) provado aqui

---

### T3: "Inovação não encontrada" com 404 próprio ✅

**What**: Id sem inovação responde 404 com a página própria da inovação, igual com e sem `DEBUG`.
**Where**: `inovacoes/views.py`
**Depends on**: T2
**Reuses**: `InovacaoDetailView` da T2
**Requirement**: CONS-15

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `InovacaoDetailView.get()` captura `Http404` e devolve `render(request, "inovacoes/inovacao_nao_encontrada.html", status=404)`
- [x] `inovacoes/templates/inovacoes/inovacao_nao_encontrada.html`: `h1` "Inovação não encontrada." e link "Voltar para a lista de inovações" → `/inovacoes/`
- [x] Testes e2e: `/inovacoes/999999/` autenticado → 404, template usado, texto e link (CONS-15); o mesmo com `settings.DEBUG = True` (sem página técnica); `/inovacoes/abc/` → 404 sem a mensagem de inovação (rota não casa, fora da CONS-15)
- [x] Gate check passa: `.venv/bin/pytest -q`
- [x] Test count: 224 testes passam (+3)

**Tests**: e2e
**Gate**: full

**Commit**: `feat(inovacoes): responde 404 proprio para inovacao inexistente`

**Status**: ✅ Complete — 225 passed (+3); 404 renderizado pela view, igual com DEBUG ligado

---

### T4: Listagem (`InovacaoListView`, rota, tabela, contagem e repositório vazio) ✅

**What**: A rota `/inovacoes/` com a tabela resumida, a contagem e a mensagem de repositório vazio, ainda sem busca nem filtros.
**Where**: `inovacoes/views.py`
**Depends on**: T3
**Reuses**: `ListView`; `para_listagem()` da T1; `get_absolute_url()`
**Requirement**: CONS-01, CONS-02, CONS-06, CONS-07, CONS-08, CONS-33, CONS-34, CONS-38, CONS-40

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `InovacaoListView` com `template_name = "inovacoes/inovacao_list.html"`, `context_object_name = "inovacoes"`, `get_queryset()` = `Inovacao.objects.para_listagem()`; sem decorator
- [x] `inovacoes/urls.py`: `path("", …, name="lista")`; os links "Voltar para a lista de inovações" da T2 e da T3 passam a `{% url 'inovacoes:lista' %}`
- [x] `inovacao_list.html`: `h1` "Inovações"; com resultado: "1 inovação encontrada" / "N inovações encontradas" (`paginator.count` quando paginado, senão `inovacoes|length`) e `<table>` com `<caption>Inovações cadastradas</caption>`, `<th scope="col">` Título / Categoria / Unidade / Status, título como link para o detalhe, status por `get_status_display`; sem resultado e sem filtro: "Nenhuma inovação cadastrada ainda." + link "Cadastrar inovação" → `/inovacoes/nova/`, sem `<table>`
- [x] Testes e2e em `inovacoes/tests/test_views_lista.py`: 200 e uma linha por inovação com título, categoria, unidade e rótulo do status (CONS-01, CONS-40); ordem decrescente com desempate por id (CONS-02); link do título == `get_absolute_url()` (CONS-06); `USUARIO` e `ADMINISTRADOR` veem inovações de autores e unidades diferentes (CONS-08, parametrizado); anônimo em `/inovacoes/?q=caixa` → `/entrar/?next=/inovacoes/%3Fq%3Dcaixa` com a query string preservada (CONS-07; o `next` exato segue o `redirect_to_login` do Django); singular e plural da contagem (CONS-33); banco sem inovação → mensagem, link e nenhuma `<table>` (CONS-34); `caption` e os quatro `th[scope=col]` (CONS-38)
- [x] Gate check passa: `.venv/bin/pytest -q`
- [x] Test count: 236 testes passam (+12)

**Tests**: e2e
**Gate**: full

**Commit**: `feat(inovacoes): adiciona a listagem de inovacoes`

**Status**: ✅ Complete — 236 passed (+11); 11 testes no lugar dos 12 estimados (parametrizado conta como um por perfil); o next do anonimo e /entrar/?next=/inovacoes/%3Fq%3Dcaixa, afirmado pelo Location literal

---

### T5: Paginação tolerante ✅

**What**: 20 por página com "Anterior", "Próxima" e "Página X de Y", e página inválida levando à 1 ou à última.
**Where**: `inovacoes/views.py`
**Depends on**: T4
**Reuses**: `Paginator.get_page`; `{% querystring %}` (Django 5.1+)
**Requirement**: CONS-03, CONS-05, CONS-33 (total entre páginas), CONS-39

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `paginate_by = 20`; `paginate_queryset()` sobrescrito para `paginator.get_page(self.request.GET.get("page"))`, devolvendo `(paginator, page, page.object_list, page.has_other_pages())`
- [x] `inovacao_list.html`: com `is_paginated`, `<nav aria-label="Paginação">` com "Anterior" só se `has_previous`, "Página X de Y" e "Próxima" só se `has_next`, ambos via `{% querystring page=… %}`; a contagem usa `paginator.count`
- [x] Testes e2e: 25 inovações → página 1 com 20 linhas, "Página 1 de 2", só "Próxima"; página 2 com 5, só "Anterior"; 20 inovações → sem `<nav>` de paginação (CONS-03); `?page=abc` e `?page=0` → 200 na página 1; `?page=99` → 200 na última (CONS-05); contagem "25 inovações encontradas" nas duas páginas (CONS-33); `nav[aria-label="Paginação"]` (CONS-39)
- [x] Gate check passa: `.venv/bin/pytest -q`
- [x] Test count: 243 testes passam (+7)

**Tests**: e2e
**Gate**: full

**Commit**: `feat(inovacoes): pagina a listagem de inovacoes`

**Status**: ✅ Complete — 245 passed (+9); testes parametrizados (abc/0 e páginas 1/2) somam mais casos que os 7 estimados. Ajuste do Done when: paginate_queryset não chama get_page() com o valor cru, porque get_page(0) devolve a última página; usa max(int(page), 1) para que page=0 caia na primeira, como a T5 pede (registrado no design.md com SPEC_DEVIATION no código). Build gate (ruff, format, makemigrations, pytest) verde no fim da Phase 1; o bloco de código do design.md foi reformatado para o ruff format --check passar

---

### T6: Cadastro termina no detalhe ✅

**What**: O `InovacaoCreateView` redireciona ao detalhe da inovação criada, onde aparece a mensagem de sucesso.
**Where**: `inovacoes/views.py`
**Depends on**: T5
**Reuses**: `get_absolute_url()` da T1 (padrão do `CreateView` sem `success_url`); `messages.success` e região `role="status"` existentes
**Requirement**: CONS-49, CONS-50

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `success_url` e o comentário "PROVISORIO" saem de `InovacaoCreateView`; nada mais muda na view
- [x] `inovacoes/tests/test_views_cadastro.py:62,117,232,238` passam a afirmar o redirect para `/inovacoes/<id da nova>/` (CONS-49); `:284` afirma a cadeia `[("/inovacoes/<id>/", 302)]` e a mensagem no `role="status"` do detalhe (CONS-50); `:292` recarrega o detalhe e afirma que a mensagem sumiu (INOV-29 mantida)
- [x] `.specs/features/cadastro-inovacao/spec.md`: INOV-03 ganha a nota "alterado pela F3 (CONS-49): o destino passa a ser o detalhe da inovação criada"; mesma nota na linha da INOV-03 em *Cobertura dos requisitos* do `design.md` da F2
- [x] Gate check passa: `.venv/bin/pytest -q`
- [x] Test count: 243 testes passam (+0: seis testes reapontados, nenhum removido)

**Tests**: e2e
**Gate**: full

**Commit**: `feat(inovacoes): leva o cadastro ao detalhe da inovacao criada`

**Status**: ✅ Complete — 245 passed (+0); seis testes reapontados (INOV-03 x5 casos, INOV-28, INOV-29) sem remoção; o teste da INOV-29 agora recarrega o detalhe e confirma antes que a mensagem estava lá. Estimativa de 243 do Done when estava defasada: a base já era 245

---

### T7: "Cancelar" do cadastro leva à listagem ✅

**What**: O link "Cancelar" do formulário de cadastro aponta para `/inovacoes/`.
**Where**: `inovacoes/templates/inovacoes/inovacao_form.html`
**Depends on**: T6
**Reuses**: rota `inovacoes:lista` da T4
**Requirement**: CONS-51

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `href="{% url 'inovacoes:lista' %}"` no "Cancelar"
- [x] `inovacoes/tests/test_views_cadastro.py:330` e o teste da INOV-37 passam a afirmar `href="/inovacoes/"` e que seguir o link leva à listagem (200) sem gravar nada (CONS-51)
- [x] `.specs/features/cadastro-inovacao/spec.md`: INOV-36 e INOV-37 ganham a nota "alvo alterado pela F3 (CONS-51): `/inovacoes/`"
- [x] Gate check passa: `.venv/bin/pytest -q`
- [x] Test count: 243 testes passam (+0: dois testes reapontados)

**Tests**: e2e
**Gate**: full

**Commit**: `feat(inovacoes): leva o cancelar do cadastro a listagem`

**Status**: ✅ Complete — 245 passed (+0); dois testes reapontados (INOV-36 e INOV-37), o da INOV-37 também afirma o template da listagem; estimativa de 243 do Done when defasada (base 245)

---

### T8: `/` vira a listagem e a home provisória sai ✅

**What**: A rota `""` (`nucleo:home`) passa a ser um `RedirectView` para `inovacoes:lista`; `HomeInternaView` e `nucleo/home.html` são removidos.
**Where**: `nucleo/urls.py`
**Depends on**: T7
**Reuses**: `RedirectView`; `LOGIN_REDIRECT_URL = "/"` sem mudança
**Requirement**: CONS-09, CONS-11

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `path("", RedirectView.as_view(pattern_name="inovacoes:lista", permanent=False), name="home")`
- [x] `nucleo/views.py` fica sem `HomeInternaView` (arquivo mantido vazio de views, ou removido se nada mais o importa); `nucleo/templates/nucleo/home.html` removido
- [x] Testes e2e: autenticado em `/` → 302 para `/inovacoes/` (CONS-09); POST de login válido sem `next`, com `follow=True`, termina em `/inovacoes/` com 200 (CONS-11)
- [x] Reapontados: `contas/tests/test_views_home.py:21,28` seguem o redirect e afirmam 200, o username e o formulário de logout na listagem (AUTH-01, AUTH-13); `contas/tests/test_sessao.py:49` renova com `GET /inovacoes/`; `inovacoes/tests/test_views_cabecalho.py:20` troca `"/"` por `"/inovacoes/"`
- [x] Reapontado (AUTH-11): `contas/tests/test_controle_acesso.py:98` usa `GET /inovacoes/` (200, os dois perfis)
- [x] Sem alteração e verdes: `contas/tests/test_controle_acesso.py` (a varredura e as linhas 68/77; a varredura ainda enxerga `/`), `contas/tests/test_views_login.py` (o login ainda redireciona para `/`), `contas/tests/test_sessao.py:39`
- [x] Gate check passa: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q`
- [x] Test count: 245 testes passam (+2)

**Tests**: e2e
**Gate**: build

**Commit**: `feat(nucleo): redireciona a raiz para a listagem de inovacoes`

**Status**: ✅ Complete — 247 passed (+2); testes novos da CONS-09 e da CONS-11 em contas/tests/test_views_home.py; HomeInternaView, nucleo/views.py e nucleo/home.html removidos. Ajuste do Done when: contas/tests/test_controle_acesso.py:98 (AUTH-11) também foi reapontado para GET /inovacoes/, autorizado pelo usuário depois do bloqueio (o item o listava como inalterado). Build gate verde

---

### T9: Link "Inovações" no cabeçalho ✅

**What**: O `<nav aria-label="Principal">` ganha "Inovações" → `/inovacoes/`, antes de "Cadastrar inovação".
**Where**: `templates/base.html`
**Depends on**: T8
**Reuses**: o `<nav>` da INOV-38; o helper `_navegacao_principal` de `inovacoes/tests/test_views_cabecalho.py`
**Requirement**: CONS-10

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `<a href="{% url 'inovacoes:lista' %}">Inovações</a>` antes do link de cadastro
- [x] Testes e2e em `inovacoes/tests/test_views_cabecalho.py`: autenticado vê o link em `/inovacoes/`, `/inovacoes/nova/` e `/inovacoes/<id>/` (parametrizado), antes de "Cadastrar inovação" (CONS-10); anônimo em `/entrar/` não vê o link
- [x] Gate check passa: `.venv/bin/pytest -q`
- [x] Test count: 249 testes passam (+4)

**Tests**: e2e
**Gate**: full

**Commit**: `feat(nucleo): adiciona o link de inovacoes ao cabecalho`

**Status**: ✅ Complete — 251 passed (+4); três páginas parametrizadas (lista, cadastro, detalhe) e o anônimo; estimativa de 249 do Done when defasada

---

### T10: Listagem e detalhe acessíveis por teclado ✅

**What**: A evidência de que lista e detalhe usam só controles nativos, sem `tabindex` positivo e com foco visível; o ajuste entra aqui se a evidência acusar falta.
**Where**: `inovacoes/tests/test_views_acessibilidade_consulta.py`
**Depends on**: T9
**Reuses**: padrões de `inovacoes/tests/test_views_acessibilidade.py` (INOV-34, INOV-35); `:focus-visible` do `base.html`
**Requirement**: CONS-41 (parte A), CONS-38, CONS-39, CONS-42 (reafirmados na página completa)

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] Testes e2e para `/inovacoes/` (com paginação ativa) e `/inovacoes/<id>/`: nenhum `tabindex` com valor positivo; todo elemento interativo é `a[href]`, `button`, `input`, `select` ou `textarea`; a regra `:focus-visible` com `outline` está na folha de estilo da página (CONS-41)
- [x] Na T18 este arquivo ganha a página com o formulário de busca; o teste é escrito para varrer a página inteira, então a T18 só acrescenta parâmetros
- [x] Gate check passa: `.venv/bin/pytest -q`
- [x] Test count: 253 testes passam (+4)

**Tests**: e2e
**Gate**: full

**Commit**: `test(inovacoes): prova a navegacao por teclado na listagem e no detalhe`

**Status**: ✅ Complete — 257 passed (+6); três testes (tabindex, controles nativos, :focus-visible) parametrizados em lista paginada e detalhe; a evidência não acusou falta, nenhum ajuste de implementação. Estimativa de 253 defasada

---

### T11: Banco indisponível na listagem e no detalhe ✅

**What**: A evidência de que `OperationalError` na consulta vira a página 500 do projeto sem detalhes de conexão.
**Where**: `inovacoes/tests/test_views_erro_500.py`
**Depends on**: T10
**Reuses**: fixture e `DETALHE_DA_CONEXAO` do próprio arquivo (INOV-42); `templates/500.html` (AUTH-26)
**Requirement**: CONS-53

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] Testes e2e: com `InovacaoQuerySet.para_listagem` e com `InovacaoDetailView.get_object` forçados a lançar `OperationalError(DETALHE_DA_CONEXAO)`, `GET /inovacoes/` e `GET /inovacoes/<id>/` → 500, `500.html` usado, nenhum trecho de `DETALHE_DA_CONEXAO` no corpo (CONS-53, parametrizado)
- [x] Gate check passa: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q` (fecha a parte A)
- [x] Test count: 255 testes passam (+2)

**Tests**: e2e
**Gate**: build

**Commit**: `test(inovacoes): prova a pagina 500 na consulta com o banco fora do ar`

**Status**: ✅ Complete — 259 passed (+2); parametrizado em listagem e detalhe; a evidência não acusou falta, nenhum ajuste de implementação. Build gate (ruff, format, makemigrations, pytest) verde: fecha a Fase 2 e a parte A. Estimativa de 255 defasada

---

### T12: Normalização de texto para busca (`inovacoes/busca.py`) ✅

**What**: As funções puras `normalizar`, `palavras` e `texto_de_busca`.
**Where**: `inovacoes/busca.py`
**Depends on**: T11
**Reuses**: `unicodedata` da biblioteca padrão
**Requirement**: CONS-19 (separador), CONS-20, CONS-21

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `normalizar(texto)`: NFKD, descarta `unicodedata.combining`, `casefold()`
- [x] `palavras(termo)`: `normalizar(termo).split()`
- [x] `texto_de_busca(titulo, problema, solucao)`: os três normalizados unidos por `"\n"`
- [x] Testes unit (`@pytest.mark.unit`) em `inovacoes/tests/test_busca.py`: `"SOLUÇÃO"` → `"solucao"`; `"Conciliação"`, `"AÇÃO"`, `"pão"`, `"Über"` (CONS-20); `"Straße"` → `"strasse"` (`casefold`); `palavras("  Planilha   CAIXA ")` == `["planilha", "caixa"]`; `palavras("")` e `palavras("   ")` == `[]` (CONS-21); `texto_de_busca` separa os campos por `\n` e nenhuma palavra de `palavras()` contém `\n` (CONS-19)
- [x] Gate check passa: `.venv/bin/pytest -q -m unit`
- [x] Test count: 263 testes passam (+8)

**Tests**: unit
**Gate**: quick

**Commit**: `feat(inovacoes): adiciona a normalizacao de texto para busca`

**Status**: ✅ Complete — 272 passed (+13); 13 casos unit (quick gate: 25 unit) no lugar dos 8 estimados: acentos parametrizados (inclusive texto em forma decomposta NFD), palavras() normalizando o termo e termo em branco parametrizado. Mutações casefold→lower, separador `\n` → espaço e sem descarte de combinantes derrubam os testes. Estimativa de 263 defasada (base 259)

---

### T13: Coluna `texto_busca` mantida pelo `save()` (AD-008) ✅

**What**: O campo `texto_busca` e o `save()` que o recalcula, inclusive com `update_fields`.
**Where**: `inovacoes/models.py`
**Depends on**: T12
**Reuses**: `texto_de_busca` da T12
**Requirement**: CONS-19, CONS-20, CONS-22 (base de dados)

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `texto_busca = models.TextField(editable=False, default="")` com comentário citando a AD-008
- [x] `save()` recalcula antes do `super().save()`; se `update_fields` contém `titulo`, `problema` ou `solucao`, acrescenta `"texto_busca"`
- [x] Migration `0005_inovacao_texto_busca` gerada por `makemigrations` (só `AddField`)
- [x] `InovacaoForm` continua com os mesmos sete campos (o campo é `editable=False`); `inovacoes/tests/test_forms.py` passa sem alteração
- [x] Testes de integração em `inovacoes/tests/test_models.py`: após `create()`, `texto_busca == texto_de_busca(...)`; após mudar `problema` e `save()`, idem; após `save(update_fields=["titulo"])`, o valor relido do banco reflete o título novo; `save(update_fields=["status"])` não toca `texto_busca`; resultado e contato **não** entram na coluna (CONS-22)
- [x] Gate check passa: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q`
- [x] Test count: 268 testes passam (+5)

**Tests**: integration
**Gate**: build

**Commit**: `feat(inovacoes): mantem o texto de busca normalizado da inovacao`

**Status**: ✅ Complete — 281 passed (+9); 9 testes no lugar dos 5 estimados: update_fields parametrizado nos três campos da busca e em tupla/frozenset (o save() copia o iterável para um set, sem mutar o do chamador). O teste de update_fields=["status"] afirma que a coluna segue o título gravado, e não o da memória. Migration 0005 gerada por makemigrations (só AddField). test_forms.py inalterado e verde; Model.full_clean() não acusa texto_busca vazio porque Field.validate ignora campos editable=False. Mutações (sem acrescentar texto_busca, acrescentar sempre, resultado no lugar da solução) derrubam os testes. Build gate verde. Estimativa de 268 defasada

---

### T14: Preencher `texto_busca` nas inovações existentes ✅

**What**: A data migration `0006` que calcula `texto_busca` das linhas gravadas antes da `0005`.
**Where**: `inovacoes/migrations/0006_preenche_texto_busca.py`
**Depends on**: T13
**Reuses**: padrão de teste de migration de `inovacoes/tests/test_migracoes.py` (`MigrationExecutor`)
**Requirement**: CONS-19, CONS-20 (para dados já existentes; AD-008)

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `RunPython(preencher, migrations.RunPython.noop)`; `preencher` usa o model histórico e uma **cópia local** da normalização (não importa `inovacoes.busca`), com comentário explicando por quê
- [x] Teste de integração em `inovacoes/tests/test_migracoes.py`: migra até `0005`, cria uma inovação com "Conciliação" pelo model histórico (com `texto_busca` vazio), migra até `0006` e afirma `texto_busca == inovacoes.busca.texto_de_busca(...)` com a função atual; a reversão para `0005` não falha
- [x] Gate check passa: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q`
- [x] Test count: 270 testes passam (+2)

**Tests**: integration
**Gate**: build

**Commit**: `feat(inovacoes): preenche o texto de busca das inovacoes existentes`

**Status**: ✅ Complete — 283 passed (+2); o teste volta o banco de teste a 0005 com MigrationExecutor (o test_migracoes.py não tinha esse padrão; ele nasce aqui), cria duas linhas pelo model histórico com texto_busca vazio, migra para 0006 e compara com inovacoes.busca.texto_de_busca; a fixture devolve o banco aos leaf nodes no fim, e a transação do teste desfaz o resto. O segundo teste reverte para 0005 e confirma que o texto gravado fica (noop). Mutações na cópia local (lower no lugar de casefold) e no laço (só a primeira linha) derrubam o teste. design.md ajustado: seção Migrations e risco da cópia passam a citar a 0006. Build gate verde

---

### T15: `InovacaoQuerySet.buscar()` ✅

**What**: A busca por palavras: cada palavra normalizada precisa aparecer em `texto_busca`.
**Where**: `inovacoes/models.py`
**Depends on**: T14
**Reuses**: `palavras` da T12; lookup `contains` (escape de `%`, `_`, `\`)
**Requirement**: CONS-19, CONS-20, CONS-21, CONS-22, CONS-23

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `buscar(termo)`: um `.filter(texto_busca__contains=palavra)` por palavra; termo `None`, vazio ou em branco devolve o queryset intacto
- [x] Testes de integração em `inovacoes/tests/test_consultas.py`: "conciliacao planilha" acha a inovação com "Conciliação" no título e "planilha" no problema, e não acha a que tem só uma das duas (CONS-19); "caix" acha "Caixa" (trecho); "SOLUÇÃO" acha "solucao" e "solucao" acha "Solução" (CONS-20); termo em branco devolve todas (CONS-21); palavra só no resultado, só no contato, só no nome da categoria ou só no nome da unidade não acha (CONS-22, parametrizado); "100%" acha só a que contém "100%" e não a que contém "1000"; "a_b" não acha "axb"; `\` literal (CONS-23)
- [x] Gate check passa: `.venv/bin/pytest -q`
- [x] Test count: 283 testes passam (+13)

**Tests**: integration
**Gate**: full

**Commit**: `feat(inovacoes): adiciona a busca por palavras sem acento`

**Status**: ✅ Complete — 300 passed (+17); 17 casos no lugar dos 13 estimados: os três campos da busca parametrizados (CONS-19) e None/vazio/espaços (CONS-21). Os testes partem de textos neutros, porque o problema e a solução padrão do conftest falam de caixa e planilha. CONS-22 tem controle positivo (a mesma inovação é achada pelo título). CONS-23 com pares literal × curinga: "100%" não acha "1000", "a_b" não acha "axb", "c:\\temp" não acha "c:temp"; com LIKE sem escape (extra) os três falham. Mutações OR no lugar de E e termo sem normalizar também derrubam os testes. Estimativa de 283 defasada

---

### T16: `InovacaoQuerySet.filtrar()` ✅

**What**: Os filtros por categoria, unidade e status, isolados ou combinados, e com a busca.
**Where**: `inovacoes/models.py`
**Depends on**: T15
**Reuses**: `buscar()` da T15
**Requirement**: CONS-27, CONS-28

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `filtrar(*, categoria=None, unidade=None, status="")`: cada valor informado restringe; `None` e `""` são ignorados
- [x] Testes de integração com três inovações (Financeiro/Sede/Validada, Financeiro/Filial Norte/Em teste, RH/Sede/Validada): só categoria → 2; só unidade → 2; só status → 2 (CONS-27, parametrizado); categoria + unidade → 1; os três → 1; os três + `buscar()` com palavra da primeira → 1 e com palavra da terceira → 0; `filtrar()` sem argumentos → 3 (CONS-28)
- [x] Gate check passa: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q` (fecha a Fase 3)
- [x] Test count: 292 testes passam (+9)

**Tests**: integration
**Gate**: build

**Commit**: `feat(inovacoes): adiciona os filtros combinados de inovacoes`

**Status**: ✅ Complete — 309 passed (+9); três inovações sobre Financeiro, RH, Sede e Filial Norte da carga 0004, buscadas pelo nome. Além do Done when, um caso do teste independente da spec (Sede + Validada + palavra da terceira → a terceira). Mutações (status ignorado, status vazio filtrando, OR no lugar de E) derrubam os testes. Build gate (ruff, format, makemigrations, pytest) verde: fecha a Fase 3. Estimativa de 292 defasada

---

### T17: `BuscaForm` ✅

**What**: O formulário GET com busca, categoria, unidade e status, com mensagens e ajuda da spec.
**Where**: `inovacoes/forms.py`
**Depends on**: T16
**Reuses**: `MENSAGEM_TAMANHO`; `campo.html` via `template_name`; padrão de `error_messages` do `InovacaoForm`
**Requirement**: CONS-24, CONS-26, CONS-30 (mensagens), CONS-36, CONS-52

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] Campos `q` (`CharField`, `required=False`, `max_length=100`, `strip=True`, `SearchInput`), `categoria` e `unidade` (`ModelChoiceField`, `required=False`, `empty_label` "Todas as categorias"/"Todas as unidades"), `status` (`ChoiceField` com `("", "Todos os status")` + `StatusInovacao.choices`), com rótulos "Buscar", "Categoria", "Unidade", "Status", `label_suffix = ""`, `help_text` da tabela de Assumptions e `template_name = "inovacoes/campo.html"`
- [x] Testes de integração em `inovacoes/tests/test_forms_busca.py`: form vazio é válido e devolve `q=""`, `None`, `None`, `""`; 101 caracteres → "Use no máximo 100 caracteres (você digitou 101)." e 100 é aceito (CONS-24); opções de categoria e unidade = "Todas …" + registros em ordem alfabética; opções de status na ordem do ciclo após "Todos os status" (CONS-26); pk inexistente, pk não numérico e status `"X"` → as três mensagens da spec (CONS-30, parametrizado); cada controle tem `<label for>` com o `id` do controle (CONS-36); cada um dos quatro textos de ajuda abaixo do controle e no `aria-describedby` (CONS-52)
- [x] Gate check passa: `.venv/bin/pytest -q`
- [x] Test count: 305 testes passam (+13)

**Tests**: integration
**Gate**: full

**Commit**: `feat(inovacoes): adiciona o formulario de busca e filtros`

**Status**: ✅ Complete — 331 passed (+22); 22 casos no lugar dos 13 estimados: campos parametrizados (rótulo e ajuda × 4, mensagens fora da lista × 5). Opções de categoria e unidade testadas com um registro criado depois da carga e alfabeticamente antes, para provar a ordem por nome e não por id. SPEC_DEVIATION de forma: o `label_suffix = ""` vai no `__init__` (`kwargs.setdefault`), porque o `Form.__init__` sobrescreve o atributo de classe com ":". Estimativa de 305 defasada

---

### T18: Busca e filtros na listagem ✅

**What**: A listagem passa a ler o `BuscaForm`, aplicar `buscar()` e `filtrar()` e renderizar o formulário dentro de `role="search"`.
**Where**: `inovacoes/views.py`
**Depends on**: T17
**Reuses**: `BuscaForm` (T17); `buscar`/`filtrar` (T15, T16); paginação com `{% querystring %}` (T5)
**Requirement**: CONS-04, CONS-19, CONS-20, CONS-25, CONS-27, CONS-28, CONS-29, CONS-31, CONS-37, CONS-41 (página com o formulário)

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `get_queryset()`: `self.form = BuscaForm(self.request.GET)`; válido → `para_listagem().buscar(q).filtrar(...)`; `get_context_data()` expõe `form`
- [x] `inovacao_list.html`: `<div role="search">` com `<form method="get" action="{% url 'inovacoes:lista' %}">`, os quatro campos por `as_field_group` e `<button type="submit">Buscar</button>`; nenhum `onchange`/script
- [x] Testes e2e em `inovacoes/tests/test_views_busca.py`: `?q=CONCILIACAO+planilha` lista só a inovação esperada (CONS-19, CONS-20); o campo mostra o termo enviado (CONS-25); `?categoria=<pk>`, `?unidade=<pk>`, `?status=VALIDADA` isolados (CONS-27); combinações com e sem `q` (CONS-28); o `option` enviado sai `selected` (CONS-29); um único `form[method=get]` com botão "Buscar" e nenhum atributo `on*` nos `select` (CONS-31); o form está dentro de `[role=search]` (CONS-37); com 25 resultados para `?q=x&status=EM_TESTE`, o link "Próxima" carrega `q=x`, `status=EM_TESTE` e `page=2` (CONS-04)
- [x] `inovacoes/tests/test_views_acessibilidade_consulta.py` (T10) passa a varrer também `/inovacoes/?q=x&status=VALIDADA` (CONS-41)
- [x] Gate check passa: `.venv/bin/pytest -q`
- [x] Test count: 318 testes passam (+13)

**Tests**: e2e
**Gate**: full

**Commit**: `feat(inovacoes): aplica busca e filtros na listagem`

**Status**: ✅ Complete — 345 passed (+14); 11 casos novos em `test_views_busca.py` (filtros isolados parametrizados) mais o parâmetro `lista_com_busca` na varredura de acessibilidade (a fixture ganhou um ramo para escolher a URL). CONS-04 com 25 resultados, ruído fora do filtro de status e fora da busca, e o par Próxima/Anterior com `q`, categoria, unidade, status e `page` comparados por `parse_qs`. A view já devolve `none()` com o form inválido (necessário para não quebrar sem `cleaned_data`); o alerta e a cobertura de teste ficam na T19. Estimativa de 318 defasada

---

### T19: Parâmetros inválidos na busca ✅

**What**: Busca longa ou filtro inexistente mostram o erro no campo e o resumo em `role="alert"`, e não listam nada.
**Where**: `inovacoes/templates/inovacoes/inovacao_list.html`
**Depends on**: T18
**Reuses**: `aria-invalid`/`aria-describedby` do Django via `campo.html`; padrão do resumo da INOV-30
**Requirement**: CONS-24, CONS-30, CONS-43

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `get_queryset()` devolve `Inovacao.objects.none()` com o form inválido (o ramo é da view; o `Where` nomeia o template, onde está a maior parte da mudança)
- [x] Template: com `form.errors`, `<div role="alert"><p>Não foi possível buscar. Corrija os campos indicados.</p></div>` antes dos resultados, sem contagem, sem tabela e sem as mensagens de vazio
- [x] Testes e2e: `?q=<101 caracteres>` → 200, a mensagem de tamanho junto ao campo, o alerta e nenhuma linha, mesmo com inovações que casariam com os 100 primeiros caracteres (CONS-24); `?categoria=999999`, `?unidade=abc`, `?status=X` → mensagem do campo, alerta, nenhuma linha (CONS-30, parametrizado); o controle com erro tem `aria-invalid="true"` e `aria-describedby` contendo o id do erro (CONS-43); nenhuma das duas mensagens de vazio aparece
- [x] Gate check passa: `.venv/bin/pytest -q`
- [x] Test count: 325 testes passam (+7)

**Tests**: e2e
**Gate**: full

**Commit**: `feat(inovacoes): trata parametros invalidos na busca`

**Status**: ✅ Complete — 358 passed (+13); 13 casos no lugar dos 7 estimados: os quatro parâmetros inválidos parametrizados em três testes (mensagem no campo + alerta + sem linha; sem contagem nem vazio; aria-invalid + aria-describedby) e um controle sem erro. As duas inovações do fixture casariam se o parâmetro inválido fosse ignorado (inclusive o título com os 100 primeiros caracteres da busca longa). O alerta fica antes do formulário, como no resumo da INOV-30; o ramo `none()` da view já veio na T18. Estimativa de 325 defasada

---

### T20: "Limpar filtros" e consulta sem resultado ✅

**What**: O link "Limpar filtros" quando há busca ou filtro ativo, e a mensagem de vazio com filtro.
**Where**: `inovacoes/templates/inovacoes/inovacao_list.html`
**Depends on**: T19
**Reuses**: ramos de resultado da T4
**Requirement**: CONS-32, CONS-34 (sem regressão), CONS-35

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `get_context_data()` expõe `filtros_ativos` (algum de `q` sem espaços nas pontas, `categoria`, `unidade`, `status` não vazio no GET); o template mostra `<a href="{% url 'inovacoes:lista' %}">Limpar filtros</a>` só nesse caso
- [x] Ramo "filtro ativo e nenhum resultado": "Nenhuma inovação encontrada para a busca e os filtros informados." + "Limpar filtros", sem `<table>`
- [x] Testes e2e: sem parâmetros → sem "Limpar filtros"; `?q=+++` (só espaços) → sem "Limpar filtros" e lista completa; `?status=VALIDADA` → link presente apontando para `/inovacoes/` sem query (CONS-32); `?q=inexistente` com inovações no banco → mensagem, link e nenhuma `<table>` (CONS-35); banco vazio com `?q=x` → mensagem da CONS-35, e não a da CONS-34; banco vazio sem parâmetros → continua a da CONS-34
- [x] Gate check passa: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q` (fecha a Fase 4)
- [x] Test count: 331 testes passam (+6)

**Tests**: e2e
**Gate**: build

**Commit**: `feat(inovacoes): adiciona limpar filtros e estado vazio da busca`

**Status**: ✅ Complete — 368 passed (+10); 10 casos no lugar dos 6 estimados: cada um dos quatro parâmetros ativa o link (parametrizado), mais o filtro combinado sem correspondência (Filial Norte + Validada). O link do estado vazio é afirmado depois da mensagem; com busca ou filtro ativo e resultado, o link fica só junto ao formulário, e no vazio aparece também sob a mensagem (dois links, como no design). `filtros_ativos` lê o GET cru, e não o form, para valer também com erro. Build gate (ruff, format, makemigrations, pytest) verde: fecha a Fase 4. Estimativa de 331 defasada

---

### T21: Comando `carregar_demonstracao` ✅

**What**: O management command que cria, de forma idempotente, as 500 inovações de demonstração da conta `demo`.
**Where**: `inovacoes/management/commands/carregar_demonstracao.py`
**Depends on**: T20
**Reuses**: `Inovacao.save()` (texto de busca); listas da carga `0004`; `get_user_model()` (AD-005)
**Requirement**: CONS-44, CONS-45

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `inovacoes/management/__init__.py` e `inovacoes/management/commands/__init__.py` criados
- [x] Comando em `transaction.atomic()`: `get_or_create` da conta `demo` (`demo@demonstracao.invalid`, perfil `USUARIO`, `set_unusable_password()` só na criação); `CommandError` se houver menos de 5 unidades ou 5 categorias; `i` de 1 a 500 com título `f"Demonstração {i:03d}"`, `unidades[i % 5]`, `categorias[(i // 5) % 5]`, `StatusInovacao.values[i % 3]`, problema e solução de um vocabulário fixo com acentos por `random.Random(i)`; cria só os títulos ausentes, com `save()` um a um; imprime "N inovações de demonstração criadas (500 no total)."
- [x] Testes de integração em `inovacoes/tests/test_carregar_demonstracao.py` (`call_command`): 500 inovações "Demonstração 001" … "Demonstração 500" da conta `demo` com perfil `USUARIO` e `has_usable_password()` falso; cada unidade, categoria e status em ≥ 20 (CONS-44); toda inovação criada tem `texto_busca` preenchido; segunda execução → ainda 500 e uma conta `demo`, saída "0 inovações de demonstração criadas" (CONS-45); com uma unidade a menos → `CommandError` e nenhuma inovação gravada
- [x] Gate check passa: `.venv/bin/pytest -q`
- [x] Test count: 336 testes passam (+5)

**Tests**: integration
**Gate**: full

**Commit**: `feat(inovacoes): adiciona a carga de demonstracao com 500 inovacoes`

**Status**: ✅ Complete — 377 passed (+9); 9 casos no lugar dos 5 estimados (mensagem final, textos variados e acentuados, recriação só dos ausentes com o mesmo conteúdo, e o `CommandError` parametrizado para unidade e categoria, sem gravar inovação nem conta). `texto_busca` de cada linha é comparado com `texto_de_busca()`, o que derruba `bulk_create` (AD-008). O vocabulário tem 16 termos e cada texto sorteia 4 por `Random(i)`. A verificação de 5 unidades e 5 categorias vem antes da conta `demo`, sem efeito observável diferente do design. Estimativa de 336 defasada

---

### T22: Desempenho de listagem e busca (RNF08) ✅

**What**: A medição de até 2 s com o conjunto de demonstração e a prova de que a listagem não tem N+1.
**Where**: `inovacoes/tests/test_desempenho.py`
**Depends on**: T21
**Reuses**: `carregar_demonstracao` (T21); `django_assert_num_queries` do pytest-django
**Requirement**: CONS-46, CONS-47, CONS-48

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] Fixture que roda `call_command("carregar_demonstracao")`; o tempo medido é só o do `client.get` (`time.perf_counter`), sem a carga
- [x] Testes e2e: `GET /inovacoes/` autenticado < 2,0 s e 200 com "500 inovações encontradas" (CONS-46); `GET /inovacoes/` com duas palavras do vocabulário + categoria + unidade + status < 2,0 s, 200 e ao menos um resultado (CONS-47); o número de consultas de `GET /inovacoes/` com 1 inovação é igual ao com 20 (CONS-48)
- [x] Se algum ajuste de consulta for necessário para passar, ele entra nesta task e é descrito no commit
- [x] Gate check passa: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q` (fecha a feature)
- [x] Test count: 339 testes passam (+3)

**Tests**: e2e
**Gate**: build

**Commit**: `test(inovacoes): mede listagem e busca com o conjunto de demonstracao`

**Status**: ✅ Complete — 380 passed (+3); 3 casos, como estimado. Medido só no `client.get`: listagem 0,015 s; busca de duas palavras + categoria + unidade + status 0,006 s; consultas por GET de `/inovacoes/` com 1 e com 20 inovações: 9 e 9. Nenhum ajuste de consulta foi necessário. O trio do CONS-47 vem da distribuição da CONS-44 (`i % 5 == 2`, `(i // 5) % 5 == 1`, `i % 3 == 1`, afirmado não vazio) e o resultado esperado é calculado sem `buscar()` nem `filtrar()`. Mutações (sem `select_related`; filtro de status ignorado) derrubam os testes. Build gate verde: fecha a feature. Estimativa de 339 defasada

---

## Phase Execution Map

```
Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5

Phase 1:  T1 → T2 → T3 → T4 → T5
Phase 2:  T6 → T7 → T8 → T9 → T10 → T11
Phase 3:  T12 → T13 → T14 → T15 → T16
Phase 4:  T17 → T18 → T19 → T20
Phase 5:  T21 → T22
```

Arcos de fronteira entre fases (a primeira task de cada fase depende da última da anterior):

```
T5  → T6
T11 → T12
T16 → T17
T20 → T21
```

A execução é estritamente sequencial — não há paralelismo dentro de uma fase.

**Empacotamento previsto no Execute:** 22 tasks ⇒ com orçamento de ~7 por lote e corte apenas em
fronteira de fase: **lote 1** = Fase 1 (5 tasks), **lote 2** = Fase 2 (6), **lote 3** = Fase 3 (5),
**lote 4** = Fases 4+5 (6). Os lotes 1 e 2 fecham a parte A; os lotes 3 e 4, a parte B. Mais de um
lote ⇒ o Execute deve **oferecer** sub-agentes antes de começar.

---

## Task Granularity Check

| Task | Scope | Status |
| ---- | ----- | ------ |
| T1 | 1 método de queryset + manager + `get_absolute_url` em `models.py` | ✅ Granular (coeso, mesmo arquivo) |
| T2 | 1 tela = view + rota + template | ⚠️ 3 arquivos, coeso — ver nota |
| T3 | 1 método de view + 1 template | ⚠️ 2 arquivos, coeso — ver nota |
| T4 | 1 tela = view + rota + template | ⚠️ 3 arquivos, coeso — ver nota |
| T5 | 1 método de view + 1 trecho de template | ✅ Granular |
| T6 | 1 linha removida da view (+ testes reapontados e nota na spec da F2) | ✅ Granular |
| T7 | 1 atributo do template (+ testes reapontados e nota na spec da F2) | ✅ Granular |
| T8 | 1 rota (+ remoção da view e template provisórios) | ✅ Granular |
| T9 | 1 trecho do `base.html` | ✅ Granular |
| T10, T11, T22 | 1 arquivo de teste (o código já existe) | ✅ Granular |
| T12 | 3 funções puras em 1 módulo | ✅ Granular (coeso) |
| T13 | 1 campo + `save()` (+ migration gerada) | ✅ Granular |
| T14 | 1 data migration | ✅ Granular |
| T15, T16 | 1 método de queryset cada | ✅ Granular |
| T17 | 1 formulário | ✅ Granular |
| T18 | 1 método de view + 1 trecho de template | ⚠️ 2 arquivos, coeso — ver nota |
| T19, T20 | 1 ramo do template (+ 1 linha de view) | ✅ Granular |
| T21 | 1 management command (+ `__init__.py` dos pacotes) | ✅ Granular |

**Nota sobre T2, T3, T4 e T18:** uma view Django não é testável sem rota e template, e um template
sem a view que o alimenta não renderiza o comportamento. Separar deixaria código não verificado, o
que a co-locação de testes proíbe. O `Where` nomeia o arquivo principal; os demais estão no
`Done when` e cobertos pelos mesmos testes. É o mesmo merge backward da T13 da F2.

**Nota sobre T1:** `get_absolute_url()` só é resolvível depois que a T2 cria a rota; o teste da URL
entra na T2 (merge forward), e a T1 prova a ordem e o carregamento.

**Nota sobre T10, T11 e T22:** o comportamento vem do Django, da F1 ou das tasks anteriores. A task é
a evidência das ACs; se a evidência acusar falta, o ajuste entra na mesma task.

---

## Diagram-Definition Cross-Check

| Task | Depends On (task body) | Diagram Shows | Status |
| ---- | ---------------------- | ------------- | ------ |
| T1 | None | (início da Fase 1) | ✅ Match |
| T2 | T1 | T1 → T2 | ✅ Match |
| T3 | T2 | T2 → T3 | ✅ Match |
| T4 | T3 | T3 → T4 | ✅ Match |
| T5 | T4 | T4 → T5 | ✅ Match |
| T6 | T5 | T5 → T6 (arco de fronteira) | ✅ Match |
| T7 | T6 | T6 → T7 | ✅ Match |
| T8 | T7 | T7 → T8 | ✅ Match |
| T9 | T8 | T8 → T9 | ✅ Match |
| T10 | T9 | T9 → T10 | ✅ Match |
| T11 | T10 | T10 → T11 | ✅ Match |
| T12 | T11 | T11 → T12 (arco de fronteira) | ✅ Match |
| T13 | T12 | T12 → T13 | ✅ Match |
| T14 | T13 | T13 → T14 | ✅ Match |
| T15 | T14 | T14 → T15 | ✅ Match |
| T16 | T15 | T15 → T16 | ✅ Match |
| T17 | T16 | T16 → T17 (arco de fronteira) | ✅ Match |
| T18 | T17 | T17 → T18 | ✅ Match |
| T19 | T18 | T18 → T19 | ✅ Match |
| T20 | T19 | T19 → T20 | ✅ Match |
| T21 | T20 | T20 → T21 (arco de fronteira) | ✅ Match |
| T22 | T21 | T21 → T22 | ✅ Match |

Nenhuma dependência aponta para fase posterior.

---

## Test Co-location Validation

| Task | Code Layer Created/Modified | Matrix Requires | Task Says | Status |
| ---- | --------------------------- | --------------- | --------- | ------ |
| T1 | Model e QuerySet | integration | integration | ✅ OK |
| T2 | Views, rotas e templates de página | e2e | e2e | ✅ OK |
| T3 | Views e template de página | e2e | e2e | ✅ OK |
| T4 | Views, rotas e templates de página | e2e | e2e | ✅ OK |
| T5 | Views e template de página | e2e | e2e | ✅ OK |
| T6 | Views | e2e | e2e | ✅ OK |
| T7 | Template de página | e2e | e2e | ✅ OK |
| T8 | Rotas (`nucleo/urls.py`) | e2e | e2e | ✅ OK |
| T9 | Template de página (`base.html`) | e2e | e2e | ✅ OK |
| T10 | Templates de página (só testes, ajuste se faltar) | e2e | e2e | ✅ OK |
| T11 | Views (só testes) | e2e | e2e | ✅ OK |
| T12 | Normalização pura | unit | unit | ✅ OK |
| T13 | Model (+ migration de esquema) | integration | integration | ✅ OK |
| T14 | Data migration | integration | integration | ✅ OK |
| T15 | QuerySet | integration | integration | ✅ OK |
| T16 | QuerySet | integration | integration | ✅ OK |
| T17 | Formulário | integration | integration | ✅ OK |
| T18 | Views e template de página | e2e | e2e | ✅ OK |
| T19 | Template de página (+ view) | e2e | e2e | ✅ OK |
| T20 | Template de página (+ view) | e2e | e2e | ✅ OK |
| T21 | Management command | integration | integration | ✅ OK |
| T22 | Views (só testes) | e2e | e2e | ✅ OK |

Nenhuma violação e nenhum `Tests: none`.

---

## Cobertura de requisitos por task

| Requirement | Task(s) |
| ----------- | ------- |
| CONS-01 | T4 |
| CONS-02 | T1, T4 |
| CONS-03 | T5 |
| CONS-04 | T18 |
| CONS-05 | T5 |
| CONS-06 | T2, T4 |
| CONS-07 | T2, T4 |
| CONS-08 | T2, T4 |
| CONS-09 | T8 |
| CONS-10 | T9 |
| CONS-11 | T8 |
| CONS-12 | T2 |
| CONS-13 | T2 |
| CONS-14 | T2 |
| CONS-15 | T3 |
| CONS-16 | T2 |
| CONS-17 | T2 |
| CONS-18 | T2 |
| CONS-19 | T12, T13, T14, T15, T18 |
| CONS-20 | T12, T13, T14, T15, T18 |
| CONS-21 | T12, T15 |
| CONS-22 | T13, T15 |
| CONS-23 | T15 |
| CONS-24 | T17, T19 |
| CONS-25 | T18 |
| CONS-26 | T17 |
| CONS-27 | T16, T18 |
| CONS-28 | T16, T18 |
| CONS-29 | T18 |
| CONS-30 | T17, T19 |
| CONS-31 | T18 |
| CONS-32 | T20 |
| CONS-33 | T4, T5 |
| CONS-34 | T4, T20 |
| CONS-35 | T20 |
| CONS-36 | T17 |
| CONS-37 | T18 |
| CONS-38 | T4, T10 |
| CONS-39 | T5, T10 |
| CONS-40 | T4 |
| CONS-41 | T10, T18 |
| CONS-42 | T2, T10 |
| CONS-43 | T19 |
| CONS-44 | T21 |
| CONS-45 | T21 |
| CONS-46 | T22 |
| CONS-47 | T22 |
| CONS-48 | T1, T22 |
| CONS-49 | T6 |
| CONS-50 | T6 |
| CONS-51 | T7 |
| CONS-52 | T17 |
| CONS-53 | T11 |

**Cobertura:** 53 requisitos, 53 mapeados para tasks, nenhum órfão.
