# Gestão por Unidade Tasks

## Execution Protocol (MANDATORY -- do not skip)

Implement these tasks with the `tlc-spec-driven` skill: **activate it by name and follow its Execute flow and Critical Rules.** Do not search for skill files by filesystem path. The skill is the source of truth for the full flow (per-task cycle, sub-agent delegation, adequacy review, Verifier, discrimination sensor).

**If the skill cannot be activated, STOP and tell the user - do not proceed without it.**

---

**Spec**: `.specs/features/gestao-por-unidade/spec.md`
**Design**: `.specs/features/gestao-por-unidade/design.md`
**Status**: Approved (2026-11-23) · Execute não iniciado (o usuário pediu para aguardar)

---

## Test Coverage Matrix

> Gerada a partir do código, das diretrizes do projeto e da spec — confirmar antes do Execute.
> **Guidelines encontradas: nenhuma** (sem `AGENTS.md`, `CONTRIBUTING.md` nem CI; o
> `pyproject.toml` só configura o pytest, o marcador `unit` e o Ruff, sem limite de cobertura).
> Valem os **strong defaults**. Estilo e piso: `contas/tests/test_admin_perfil.py`,
> `contas/tests/test_controle_acesso.py`, `contas/tests/test_constraints.py`,
> `inovacoes/tests/test_controle_autoria.py`, `inovacoes/tests/test_views_detalhe_v2.py`,
> `nucleo/tests/test_casca.py`, `inovacoes/tests/visibilidade.py`.

| Code Layer | Required Test Type | Coverage Expectation | Location Pattern | Run Command |
| ---------- | ------------------ | -------------------- | ---------------- | ----------- |
| Modelo, QuerySet e CHECKs (`contas.Usuario`, `Inovacao.pode_ser_alterada_por`) | integration | Todo ramo, 1:1 com as ACs; CHECK por `create()` e por `update()` em massa; migration sobre contas existentes | `contas/tests/test_*.py`, `inovacoes/tests/test_permissoes.py` | `.venv/bin/pytest -q` |
| Formulários (`contas/forms.py`, `ReaproveitamentoForm`) | integration | Cada mensagem de erro da spec no campo certo, uma vez só; campos que voltam e que não voltam (RF13) | `contas/tests/test_forms_gestao.py`, `inovacoes/tests/test_forms_reaproveitamento.py` | `.venv/bin/pytest -q` |
| Views, middleware e templates | e2e | Cada AC de tela pelo `client`, com o exibido sobre o DOM parseado (`exibido(html, rigoroso=True)`, L-028, L-030); varredura por papel em toda rota nova (L-003: anônimo, USUARIO, USUARIO staff, USUARIO superusuário, ADMINISTRADOR, superusuário, gestor de outra unidade, gestor da unidade); recusas sem gravar (estado do banco antes e depois); cada cláusula na camada da AC (L-005) | `contas/tests/test_views_gestao_*.py`, `contas/tests/test_senha_provisoria.py`, `inovacoes/tests/test_*.py` | `.venv/bin/pytest -q` |
| Casca e peças (`nucleo/context_processors.py`, `nucleo/formularios.py`, parciais) | unit | Todo ramo do `PAGINA_ATUAL` novo; a parcial de campo e a de resumo com e sem erro | `nucleo/tests/test_*.py` | `.venv/bin/pytest -q -m unit` |
| Ícone | unit | Formas iguais às do `users.svg` do `lucide-static@1.78.0`; atributos decorativos da pasta | `nucleo/tests/test_casca.py` | `.venv/bin/pytest -q -m unit` |
| Documentação (`docs/design-spec.md`) | none | — (build gate) | — | build gate |

## Gate Check Commands

> Pelo `.venv/`, com o PostgreSQL 16 na porta 5433 em execução. Nada de `migrate` no Neon.

| Gate Level | When to Use | Command |
| ---------- | ----------- | ------- |
| Quick | Task só com teste unitário | `.venv/bin/pytest -q -m unit` |
| Full | Task com teste e2e ou de integração | `.venv/bin/pytest -q` |
| Build | Ao fechar cada fase e em toda task que mexe em migration, `settings.py`, `base.html` ou `kira.css` | `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q` |

**Linha de base:** 1594 testes coletados (`.venv/bin/pytest -q --co`, 2026-11-23). A contagem nunca cai.

**Testes antigos que mudam (inventário aprovado em 2026-11-23):** só T-1 a T-7, cada um na task
indicada. Mudam no mesmo commit da task que os quebra, preservando a garantia da AC original
(docstring com a AC). **Se outro teste antigo quebrar, a task para e pergunta ao usuário.**

| # | Task |
| - | ---- |
| T-1, T-2 | T4 |
| T-3 | T1 |
| T-4 | T6 |
| T-5 (`PECAS`) | T7 (`paginas/campo.html`, `paginas/resumo_erros.html`), T8 (`tabela_contas.html`) |
| T-5 (contagem 13 → 19) | T8 (+3: minha unidade, acesso restrito, conta não encontrada → 16), T10 (+1 → 17), T12 (+1 → 18), T13 (+1 → 19) |
| T-6 (fixture `paginas`) | T8, T10, T12, T13 (cada tela nova entra na task que a cria) |
| T-7 (`PAGINAS_DA_FIXTURE`, achado no Execute, autorizado em 2026-11-23) | T8, T10, T12, T13 (junto com a T-6) |

---

## Execution Plan

Fases em sequência; tarefas em ordem dentro de cada fase.

### Phase 1: Dados e regras

```
T1 → T2 → T3 → T4 → T5
```

### Phase 2: Peças da casca e do formulário

```
T6 → T7
```

### Phase 3: Área do gestor

```
T8 → T9 → T10 → T11 → T12
```

### Phase 4: Senha provisória e unidade pré-preenchida

```
T13 → T14 → T15
```

### Phase 5: Documentação

```
T16
```

---

## Task Breakdown

### T1: Perfil, unidade e senha provisória no `Usuario` ✅

**What**: `GESTOR_DE_UNIDADE` no `PerfilUsuario`, `perfil` com 17 caracteres, `Usuario.unidade` (FK nula, PROTECT, `related_name="usuarios"`), `Usuario.senha_provisoria`, `is_gestor_de_unidade`, CHECK `usuario_gestor_tem_unidade` e a migration `contas/migrations/0005_gestao_por_unidade.py`.
**Where**: `contas/models.py`
**Depends on**: None
**Reuses**: `PerfilUsuario`, `is_administrador`, CHECK `usuario_perfil_valido` (AD-004)
**Requirement**: GEST-01, GEST-02, GEST-03

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [x] T-3: `contas/tests/test_models.py:13-15` afirma os três valores, em ordem, com a docstring da AUTH-16 estendida
- [x] Testes: rótulo "Gestor de unidade"; `is_gestor_de_unidade` verdadeiro só para o gestor (e falso para USUARIO, ADMINISTRADOR e superusuário USUARIO); gestor sem unidade recusado pelo banco no `create()` e no `update()` em massa (`IntegrityError`, valor inalterado); gestor com unidade, USUARIO e ADMINISTRADOR sem unidade gravam; `GESTOR_DE_UNIDADE` cabe na coluna; `unidade` com `on_delete=PROTECT`; `senha_provisoria` falso por padrão; gestor não ganha `is_staff` no `save()`
- [x] Teste de migração: banco em `contas 0004` com uma conta USUARIO e uma ADMINISTRADOR; depois da 0005, as duas iguais, com unidade nula e senha provisória falsa
- [x] Gate build passa; test count ≥ 1594 + 10

**Tests**: integration
**Gate**: build

**Commit**: `feat(contas): adiciona o gestor de unidade e a unidade da conta`

---

### T2: Situação da conta e escopo do gestor ✅

**What**: `SituacaoConta`, `TRANSICOES`, `Usuario.situacao`, `Usuario.mudar_situacao(para)`, `Usuario.pode_ser_administrada_por(gestor)` e o `UsuarioQuerySet` com `da_unidade(unidade)` e `administraveis_por(gestor)`, ligado ao `UsuarioManager` por `from_queryset` (AD-016).
**Where**: `contas/models.py`
**Depends on**: T1
**Reuses**: `UsuarioManager.create_superuser`
**Requirement**: GEST-14, GEST-15, GEST-17, GEST-18, GEST-32, GEST-61

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [x] Testes: `situacao` ATIVA/DESATIVADA pelo `is_active`; `TRANSICOES` exatamente `{ATIVA: {DESATIVADA}, DESATIVADA: {ATIVA}}`; `mudar_situacao` grava só `is_active` (outro campo alterado em memória não vai ao banco); `da_unidade` com todas as contas da unidade, inclusive desativadas e o gestor, sem outra unidade nem unidade nula, na ordem nome, sobrenome, usuário; `administraveis_por` só USUARIO da unidade do gestor (fora: outra unidade, sem unidade, o próprio gestor, outro gestor, ADMINISTRADOR da unidade) e vazio para quem não é gestor; `pode_ser_administrada_por` igual ao queryset para cada um desses casos, sem consulta
- [x] `createsuperuser` continua nascendo ADMINISTRADOR (AUTH-20 verde)
- [x] Gate full passa; test count ≥ T1 + 12

**Tests**: integration
**Gate**: full

**Commit**: `feat(contas): define a situacao da conta e o alcance do gestor`

---

### T3: Curadoria pela unidade de origem ✅

**What**: `Inovacao.pode_ser_alterada_por` ganha o gestor da unidade de origem (extensão da AD-009), lendo só ids.
**Where**: `inovacoes/models.py`
**Depends on**: T2
**Reuses**: `AlteracaoDeInovacaoMixin`, `pode_alterar` do detalhe
**Requirement**: GEST-48, GEST-49, GEST-50, GEST-51, GEST-53, GEST-54

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [x] Testes do método: verdadeiro para autor, ADMINISTRADOR e gestor da unidade de origem (inovação de outro autor); falso para gestor de outra unidade, USUARIO da mesma unidade, USUARIO staff e superusuário USUARIO, anônimo; sem consulta ao banco
- [x] Testes e2e: gestor da unidade de origem vê "Editar", "Excluir" e "Avançar para…" no detalhe exibido (Em teste e Validada); edita, exclui com confirmação e avança o status de inovação de outro autor; gestor de outra unidade recebe 403 com `inovacoes/acesso_negado.html` em editar, excluir e status (GET e POST) e nada muda no banco; troca de unidade e perda do perfil no banco valem na requisição seguinte
- [x] Os testes de número de consultas do detalhe seguem iguais
- [x] Gate full passa; test count ≥ T2 + 14

**Tests**: e2e
**Gate**: full

**Commit**: `feat(inovacoes): da a curadoria ao gestor da unidade de origem`

---

### T4: Textos de permissão com o gestor ✅

**What**: Os textos novos de recusa e de explicação no `acesso_negado.html` e no `inovacao_detail.html:96`, e o mesmo texto na Ajuda (`templates/paginas/ajuda.html:29`) e na `docs/design-spec.md` (§10, detalhe, linhas 556 e 574).
**Where**: `inovacoes/templates/inovacoes/acesso_negado.html`
**Depends on**: T3
**Reuses**: textos da spec (T-1, T-2)
**Requirement**: GEST-52

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [x] T-1: `SO_AUTOR` em `test_views_edicao.py:16` e `test_views_exclusao.py:13` com o texto novo
- [x] T-2: `QUEM_PODE_AVANCAR` em `test_views_detalhe.py:451` e `test_views_detalhe_v2.py:303` com o texto novo
- [x] Teste novo: a Ajuda exibe o texto novo de avançar status (exibido no DOM parseado)
- [x] `grep` sem o texto antigo em templates, `docs/design-spec.md` e testes
- [x] Gate full passa; test count ≥ T3 + 1

**Tests**: e2e
**Gate**: full

**Commit**: `feat(inovacoes): cita o gestor nos textos de permissao`

---

### T5: Unidade e senha provisória no admin ✅

**What**: Seção "Perfil" com perfil, unidade e senha provisória; coluna e filtro "Unidade"; `UsuarioAlteracaoForm.clean()` com o erro da GEST-05 no campo.
**Where**: `contas/admin.py`
**Depends on**: T4 (usa os campos novos do modelo)
**Reuses**: `UsuarioAdmin`, `UsuarioAlteracaoForm`, `AcessoSomenteAdministradorMixin` (AD-007)
**Requirement**: GEST-04, GEST-05, GEST-06, GEST-07, GEST-08

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [x] Testes e2e: o formulário de edição tem `unidade` e `senha_provisoria` na seção "Perfil", junto de `perfil`; salvar gestor sem unidade mostra "Gestor de unidade precisa de uma unidade." no campo Unidade, uma vez só na página, e não grava; salvar gestor com unidade grava; lista com coluna e filtro "Unidade"; conta criada no admin nasce com senha provisória desmarcada
- [x] Testes e2e (L-003): gestor sem `is_staff` é mandado ao login do admin em toda tela de usuário e de unidade; gestor com `is_staff` recebe 403 nelas; POST forjado do gestor com staff não muda perfil nem unidade
- [x] Teste e2e: excluir no admin uma unidade com conta vinculada é recusado e a unidade continua
- [x] Testes antigos de `contas/tests/test_admin*.py` verdes sem mudança
- [x] Gate full passa; test count ≥ T4 + 9

**Tests**: e2e
**Gate**: full

**Commit**: `feat(contas): mostra a unidade e a senha provisoria no admin`

---

### T6: Ícone "usuarios" ✅

**What**: `templates/icones/usuarios.svg`, cópia do `users.svg` do `lucide-static@1.78.0` com a abertura decorativa da pasta (formas no `design.md`).
**Where**: `templates/icones/usuarios.svg`
**Depends on**: None (a Fase 1 inteira antes)
**Reuses**: `templates/icones/engrenagem.svg` (mesma versão), `templates/icones/LICENSE`
**Requirement**: GEST-09

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [x] T-4: `NOMES_DOS_ICONES` ganha `usuarios` numa lista própria da gestão (`nucleo/tests/test_casca.py:137-153`), com a docstring da RED-16 estendida; o teste de atributos decorativos passa a cobri-lo
- [x] Teste novo: as formas do SVG, em ordem, são exatamente os três `path` e o `circle` do `users.svg` oficial
- [x] Gate quick passa; test count ≥ T5 + 2

**Tests**: unit
**Gate**: quick

**Commit**: `feat(design): adiciona o icone de usuarios do lucide`

---

### T7: Campo e resumo de erros da §6 v2 ✅

**What**: `nucleo/formularios.py` com o `FormularioV2Mixin` e as parciais `templates/paginas/campo.html` (rótulo → ajuda → campo → erro, "(obrigatório)" por escrito, `aria-describedby` erro antes da ajuda) e `templates/paginas/resumo_erros.html`.
**Where**: `nucleo/formularios.py`
**Depends on**: T6
**Reuses**: `.resumo-erros`, `[role=alert]` da `kira.css`; ids `_helptext` e `_error` do Django
**Requirement**: GEST-68

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [x] T-5: `paginas/campo.html` e `paginas/resumo_erros.html` em `PECAS` (`inovacoes/tests/test_views_sistema_design.py:401`)
- [x] Testes com um formulário de teste de dois campos: ordem rótulo, ajuda, campo, erro; "(obrigatório)" no rótulo do campo obrigatório; `aria-invalid` e `aria-describedby="{erro} {ajuda}"` com erro; sem erro, nenhum resumo no DOM; com dois erros, título "Não foi possível {ação}. Corrija 2 campo(s):", links `#id_…` na ordem dos campos com "{rótulo}: {mensagem}", `role="alert"` e `tabindex="-1"`; erro sem campo entra como texto sem link
- [x] Gate full passa; test count ≥ T6 + 7

**Tests**: unit
**Gate**: full

**Commit**: `feat(nucleo): cria o campo e o resumo de erros da v2`

---

### T8: "Minha unidade", porteiro e páginas de recusa ✅

**What**: `contas/views_gestao.py` com `GestaoDeUnidadeMixin` e `MinhaUnidadeView`; `contas/urls_gestao.py` (namespace `gestao`) montado em `/minha-unidade/`; templates `minha_unidade.html`, `acesso_restrito.html`, `conta_nao_encontrada.html`, a parcial `parciais/tabela_contas.html` e o parâmetro `unidade` da trilha.
**Where**: `contas/views_gestao.py`
**Depends on**: None (as Fases 1 e 2 inteiras antes: usa o escopo do gestor e as peças de formulário)
**Reuses**: `AlteracaoDeInovacaoMixin` (desenho), `.tabela`, `.cabecalho-pagina`, `paginas/trilha.html`
**Requirement**: GEST-12, GEST-13, GEST-14, GEST-15, GEST-16, GEST-17, GEST-18, GEST-19, GEST-64, GEST-65

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [x] T-5: contagem 13 → 16 e `contas/gestao/parciais/tabela_contas.html` em `PECAS`; T-6: `minha_unidade` e `acesso_restrito` na fixture `paginas`
- [x] Testes e2e da tela (DOM parseado): h1 "Minha unidade", nome da unidade, `caption` "Contas da unidade {nome}", cabeçalhos Nome, Usuário, E-mail, Perfil, Situação, Último acesso (`th scope="col"`); linhas na ordem da GEST-14 e só da unidade; "Ativa"/"Desativada" por escrito; "Nunca" sem acesso; ações "Redefinir senha" + "Desativar" (ativa) ou "Reativar" (desativada) só nas contas USUARIO, nenhuma ação nas outras; "Criar conta" com `href="/minha-unidade/contas/nova/"`; nome novo da unidade depois de renomear; unidade só com o gestor
- [x] Varredura por papel (L-003) sobre toda rota do namespace `gestao`, lida do resolver: USUARIO, USUARIO staff, USUARIO superusuário, ADMINISTRADOR e superusuário recebem 403 com "Acesso restrito a gestores de unidade." exibido; nas rotas com `pk`, gestor de outra unidade recebe 404 com a página própria e nada muda no banco; anônimo vai ao login (AD-006 verde)
- [x] Trilha "Minha unidade" com `aria-current="page"`
- [x] Gate build passa; test count ≥ T7 + 20

**Tests**: e2e
**Gate**: build

**Commit**: `feat(contas): cria a area minha unidade do gestor`

---

### T9: Item "Minha unidade" no menu ✅

**What**: O quarto item do menu Principal só para o gestor, com o ícone `usuarios`, e a página atual da seção `gestao` no `PAGINA_ATUAL`.
**Where**: `nucleo/context_processors.py`
**Depends on**: T8 (usa o ícone da Fase 2)
**Reuses**: `casca`, `PAGINA_ATUAL` (AD-015), `templates/base.html:46-52`
**Requirement**: GEST-09, GEST-10, GEST-11

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [x] Testes unit da casca: `/minha-unidade/` → `("unidade", "page")`; `/minha-unidade/contas/nova/` e as rotas com `pk` → `("unidade", "true")`; os casos antigos iguais
- [x] Testes e2e (DOM parseado): gestor vê 4 itens, "Minha unidade" depois de "Indicadores", `href="/minha-unidade/"`, ícone SVG decorativo antes do texto, `aria-current="page"` na lista e `"true"` nas demais telas da área; USUARIO, USUARIO staff, ADMINISTRADOR e superusuário não têm o item nem o `href` no HTML
- [x] Os testes de menu antigos (`MENU` de 3 itens com `autor`) verdes sem mudança
- [x] Gate build passa; test count ≥ T8 + 10

**Tests**: e2e
**Gate**: build

**Commit**: `feat(nucleo): mostra minha unidade no menu do gestor`

---

### T10: Criar conta na unidade ✅

**What**: `ContaDaUnidadeForm` em `contas/forms.py`, `CriarContaView` e o template `contas/gestao/conta_form.html` (dois `fieldset.grupo`, resumo de erros, barra de ações).
**Where**: `contas/views_gestao.py`
**Depends on**: T9
**Reuses**: `BaseUserCreationForm`, `FormularioV2Mixin`, `.grupo`, `.barra-acoes`, `AUTH_PASSWORD_VALIDATORS`
**Requirement**: GEST-20, GEST-21, GEST-22, GEST-23, GEST-24, GEST-25, GEST-26, GEST-27, GEST-28, GEST-29, GEST-68, GEST-69

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [x] T-5: contagem 16 → 17; T-6: `criar_conta` (e a versão com erro) na fixture `paginas`
- [x] Testes de formulário: cada mensagem da spec no campo certo, uma vez só na página (e-mail e usuário duplicados sem diferenciar caixa, validador de senha, confirmação diferente)
- [x] Testes e2e: os seis campos obrigatórios e nenhum de perfil ou unidade; envio válido cria USUARIO da unidade do gestor, ativa, com senha provisória e senha em hash, e volta a `/minha-unidade/` com o alerta exato da GEST-22; POST com `perfil`, `unidade`, `is_staff`, `is_superuser` é ignorado; envio inválido não cria, devolve usuário, nome, sobrenome e e-mail e esvazia as senhas, mostra o resumo e o `<title>` com "Erro:"; barra de ações com "Criar conta", "Cancelar" → `/minha-unidade/` e a nota; trilha "Minha unidade › Criar conta"; CSRF inválido → 403 sem criar
- [x] Gate full passa; test count ≥ T9 + 16

**Tests**: e2e
**Gate**: full

**Commit**: `feat(contas): permite ao gestor criar conta na unidade`

---

### T11: Desativar e reativar conta ✅

**What**: `SituacaoDaContaView` (só POST, destino no corpo) e o `form` de cada linha da tabela, com os botões secundários.
**Where**: `contas/views_gestao.py`
**Depends on**: T10
**Reuses**: `Usuario.mudar_situacao`, `TRANSICOES` (AD-016), `UsernameOrEmailBackend` (login e sessão)
**Requirement**: GEST-30, GEST-31, GEST-32, GEST-33, GEST-34, GEST-35, GEST-36, GEST-62, GEST-63, GEST-67

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [x] Testes e2e: desativar e reativar com os alertas exatos; repetir o mesmo destino mantém o estado e o alerta; valor inválido → 400 sem gravar; GET → 405; conta desativada recusa o login com "Usuário ou senha inválidos."; sessão aberta da conta desativada vira anônima na requisição seguinte (vai ao login); inovações, mudanças de status e reaproveitamentos da conta continuam com a autoria; alvo fora do escopo (outra unidade, sem unidade, o próprio gestor, outro gestor, ADMINISTRADOR) e id inexistente → 404 sem gravar; CSRF inválido → 403 sem gravar; duas desativações seguidas por dois gestores terminam desativada com o mesmo alerta
- [x] Os botões "Desativar" e "Reativar" exibidos são secundários (sem classe de perigo)
- [x] Gate full passa; test count ≥ T10 + 15

**Tests**: e2e
**Gate**: full

**Commit**: `feat(contas): permite ao gestor desativar e reativar contas`

---

### T12: Redefinir senha ✅

**What**: `SenhaProvisoriaForm` em `contas/forms.py`, `RedefinirSenhaView` e o template `contas/gestao/redefinir_senha.html`.
**Where**: `contas/views_gestao.py`
**Depends on**: T11
**Reuses**: `SetPasswordForm`, `FormularioV2Mixin`, `.barra-acoes`
**Requirement**: GEST-37, GEST-38, GEST-39, GEST-62, GEST-68, GEST-69

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [x] T-5: contagem 17 → 18; T-6: `redefinir_senha` na fixture `paginas`
- [x] Testes e2e: envio válido troca a senha, liga a senha provisória e volta com o alerta exato; validador ou confirmação diferente mostra o erro no campo, o resumo e "Erro:" e não troca; sessão aberta da conta vira anônima; alvo fora do escopo e id inexistente → 404 em GET e POST sem trocar; barra de ações e trilha "Minha unidade › Redefinir senha"; descrição com o usuário da conta
- [x] Gate full passa; test count ≥ T11 + 10

**Tests**: e2e
**Gate**: full

**Commit**: `feat(contas): permite ao gestor redefinir a senha da conta`

---

### T13: Trocar a própria senha ✅

**What**: `TrocarSenhaForm` em `contas/forms.py`, `TrocarSenhaView` em `contas/views.py`, a rota `/conta/senha/` (`contas:trocar_senha`) e o template `contas/trocar_senha.html`.
**Where**: `contas/views.py`
**Depends on**: None (a Fase 3 inteira antes)
**Reuses**: `PasswordChangeView`, `PasswordChangeForm`, `FormularioV2Mixin`, `.alerta--warning`, `.barra-acoes`
**Requirement**: GEST-41, GEST-42, GEST-43, GEST-44, GEST-45, GEST-46, GEST-47, GEST-68, GEST-69

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [x] T-5: contagem 18 → 19; T-6: `trocar_senha` (com e sem senha provisória) na fixture `paginas`
- [x] Testes e2e: h1 "Trocar senha" e os três campos; aviso exato da GEST-42 só com senha provisória; troca válida desliga a senha provisória, mantém a sessão, vai a `/inovacoes/` com "Senha alterada."; "Senha atual incorreta.", "A nova senha precisa ser diferente da atual.", validador e confirmação no campo certo, com resumo e "Erro:", sem trocar; sem senha provisória, "Cancelar" → `/inovacoes/` e a nota; com senha provisória, nem "Cancelar" nem a nota
- [x] Gate full passa; test count ≥ T12 + 12

**Tests**: e2e
**Gate**: full

**Commit**: `feat(contas): cria a tela de trocar senha`

---

### T14: Troca obrigatória da senha provisória ✅

**What**: `contas.middleware.SenhaProvisoriaMiddleware` (AD-017) no `MIDDLEWARE`, logo depois do `LoginRequiredMiddleware`.
**Where**: `contas/middleware.py`
**Depends on**: T13
**Reuses**: marca `login_required = False` do `@login_not_required` (AD-006)
**Requirement**: GEST-40, GEST-66

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [x] Varredura: com uma conta de senha provisória, toda rota interna lida do resolver (a mesma coleta da `contas/tests/test_controle_acesso.py`) responde 302 para `/conta/senha/`, salvo `/conta/senha/` (200) e `/sair/` (POST encerra a sessão); as rotas públicas (`ROTAS_PUBLICAS`) respondem como hoje
- [x] Testes e2e: gestor com senha provisória em `/minha-unidade/` e USUARIO com senha provisória em `/admin/` vão para `/conta/senha/` antes da checagem de papel; POST também redireciona sem gravar; sem senha provisória, nada muda; anônimo continua indo ao login com `next`; fluxo completo: gestor cria a conta, a pessoa entra, cai em "Trocar senha", não abre a lista pela URL, troca e chega à lista
- [x] Gate build passa; test count ≥ T13 + 8

**Tests**: e2e
**Gate**: build

**Commit**: `feat(contas): exige a troca da senha provisoria`

---

### T15: Unidade pré-preenchida no cadastro e no reaproveitamento

**What**: `InovacaoCreateView.get_initial()` com a unidade do usuário e `ReaproveitamentoForm(…, unidade_sugerida=None)` com a unidade sugerida quando elegível.
**Where**: `inovacoes/views.py`
**Depends on**: T14 (usa a unidade da conta, da Fase 1)
**Reuses**: `get_initial`, `ReaproveitamentoForm`, `UnidadeElegivelField`
**Requirement**: GEST-55, GEST-56, GEST-57, GEST-58, GEST-59, GEST-60

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [ ] Testes e2e: usuário com unidade vê a unidade selecionada no cadastro (exibido) e pode trocar; envio com outra unidade grava a escolhida; usuário sem unidade vê "Selecione…"; a edição mostra a unidade da inovação, não a do usuário; reaproveitamento com a unidade do usuário elegível vem com ela selecionada; com a unidade de origem ou já reaproveitada, sem seleção
- [ ] Teste de formulário: `ReaproveitamentoForm` sem `unidade_sugerida` igual a hoje
- [ ] Gate full passa; test count ≥ T14 + 7

**Tests**: e2e
**Gate**: full

**Commit**: `feat(inovacoes): pre-preenche a unidade do usuario`

---

### T16: Design-spec da gestão por unidade

**What**: `docs/design-spec.md`: §5 (usuário no cabeçalho deixa de dizer que não há unidade), §5.2 (quarto item "Minha unidade" só para o gestor, ícone de pessoas), §5.3 (trilhas das telas novas) e §10 (seção "Minha unidade e contas", com as quatro telas e as duas páginas de recusa).
**Where**: `docs/design-spec.md`
**Depends on**: None (a Fase 4 inteira antes)
**Reuses**: textos do `design.md`
**Requirement**: GEST-09, GEST-13, GEST-41

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [ ] A design-spec descreve o que as telas fazem (conferido contra os templates)
- [ ] Gate build passa; test count igual ao da T15

**Tests**: none
**Gate**: build

**Commit**: `docs: descreve a gestao por unidade na design-spec`

---

## Phase Execution Map

```
Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5

Phase 1:  T1 → T2 → T3 → T4 → T5
Phase 2:  T6 → T7
Phase 3:  T8 → T9 → T10 → T11 → T12
Phase 4:  T13 → T14 → T15
Phase 5:  T16
```

Lotes para sub-agentes (~7 tarefas, fases inteiras): **Lote A** = Fases 1 e 2 (T1–T7);
**Lote B** = Fase 3 (T8–T12); **Lote C** = Fases 4 e 5 (T13–T16). Em sequência.

---

## Task Granularity Check

| Task | Scope | Status |
| ---- | ----- | ------ |
| T1 | Campos do modelo + a migration que eles geram | ⚠️ Coeso (a migration é gerada pelo modelo) |
| T2 | Regras de situação e escopo, um arquivo | ✅ |
| T3 | Um método | ✅ |
| T4 | Um texto em quatro lugares | ⚠️ Coeso (mesmo texto; T-1/T-2 juntos) |
| T5 | Admin de usuários + `clean()` do form do admin | ⚠️ Coeso |
| T6 | Um ícone | ✅ |
| T7 | Mixin + duas parciais do mesmo componente de formulário | ⚠️ Coeso |
| T8 | Porteiro + uma tela + duas páginas de recusa + rotas | ⚠️ Coeso (o porteiro não é testável sem a primeira rota e suas recusas) |
| T9 | Um item de menu + sua página atual | ✅ |
| T10 | Uma tela (form + view + template) | ✅ |
| T11 | Um endpoint | ✅ |
| T12 | Uma tela | ✅ |
| T13 | Uma tela + sua rota | ✅ |
| T14 | Um middleware | ✅ |
| T15 | Pré-preenchimento em duas views irmãs | ⚠️ Coeso (mesma regra, GEST-55 a GEST-60) |
| T16 | Um documento | ✅ |

## Diagram-Definition Cross-Check

Dependências fora da cadeia (T5 usa a T1, T8 usa a T2 e a T7, T9 usa a T6, T15 usa a T1) são
satisfeitas pela ordem das fases e citadas no `Depends on` entre parênteses.

| Task | Depends On (task body) | Diagram Shows | Status |
| ---- | ---------------------- | ------------- | ------ |
| T1 | None | início da fase | ✅ |
| T2 | T1 | T1 → T2 | ✅ |
| T3 | T2 | T2 → T3 | ✅ |
| T4 | T3 | T3 → T4 | ✅ |
| T5 | T4 | T4 → T5 | ✅ |
| T6 | None | início da fase | ✅ |
| T7 | T6 | T6 → T7 | ✅ |
| T8 | None | início da fase | ✅ |
| T9 | T8 | T8 → T9 | ✅ |
| T10 | T9 | T9 → T10 | ✅ |
| T11 | T10 | T10 → T11 | ✅ |
| T12 | T11 | T11 → T12 | ✅ |
| T13 | None | início da fase | ✅ |
| T14 | T13 | T13 → T14 | ✅ |
| T15 | T14 | T14 → T15 | ✅ |
| T16 | None | início da fase | ✅ |

## Test Co-location Validation

| Task | Code Layer Created/Modified | Matrix Requires | Task Says | Status |
| ---- | --------------------------- | --------------- | --------- | ------ |
| T1 | Modelo, CHECK, migration | integration | integration | ✅ |
| T2 | Modelo, QuerySet | integration | integration | ✅ |
| T3 | Modelo + comportamento das views | e2e | e2e | ✅ |
| T4 | Templates | e2e | e2e | ✅ |
| T5 | Admin, formulário | e2e | e2e | ✅ |
| T6 | Ícone | unit | unit | ✅ |
| T7 | Peças de formulário | unit | unit | ✅ |
| T8 | Views, templates, rotas | e2e | e2e | ✅ |
| T9 | Casca, template base | e2e | e2e | ✅ |
| T10 | Formulário, view, template | e2e | e2e | ✅ |
| T11 | View | e2e | e2e | ✅ |
| T12 | Formulário, view, template | e2e | e2e | ✅ |
| T13 | Formulário, view, template, rota | e2e | e2e | ✅ |
| T14 | Middleware, settings | e2e | e2e | ✅ |
| T15 | Views, formulário | e2e | e2e | ✅ |
| T16 | Documentação | none | none | ✅ |
