# Edição e Exclusão de Inovações (F4) Validation

**Date**: 2026-10-11
**Iteration**: 1
**Spec**: `.specs/features/edicao-exclusao/spec.md` (EDEX-01 … EDEX-45)
**Diff range**: `8ac62d4..b749ff3` em `main` (HEAD = `b749ff3`). 14 commits de task (T1 `55b6fe0` … T14 `b749ff3`). 18 arquivos, +1573/−153 (`git diff --stat 8ac62d4..b749ff3`).
**Verifier**: independent sub-agent (author ≠ verifier)

**Verdict**: FAIL ❌

O build gate passa com 470 testes. As 45 ACs têm evidência `file:line`, e 43 afirmam o valor exato que a spec define. A EDEX-09 e a EDEX-11 estão cobertas em parte: falta afirmar uma cláusula de cada uma na rota de edição. O sensor injetou 31 mutações num `git worktree` descartável. 27 morreram e 4 sobreviveram, e nenhuma delas é equivalente. Três estão no caminho de segurança: a AD-009 diz que `is_staff`/`is_superuser` não dão acesso a inovações de terceiros, mas isso só é provado no modelo (`test_permissoes.py:39-45`). Nenhum teste de rota ou de tela usa um `USUARIO` com `is_staff` ou `is_superuser`. Por isso, uma exceção para superusuário no `dispatch()` do mixin (M23b) e links "Editar"/"Excluir" exibidos a staff ou superusuário no detalhe (M22, M22b) passam com a suíte inteira verde. O caso é real: no banco local, a `maria` é `USUARIO` com `is_staff` (`STATE.md` Handoff). A quarta sobrevivente (M24) mostra que a varredura da AD-009 só encontra rotas cujo padrão contém o texto literal `<int:pk>`. As correções são só de teste, e nenhum defeito de produção foi encontrado.

---

## Task Completion

| Task | Status | Notes |
| ---- | ------ | ----- |
| T1–T14 | ✅ Done | `tasks.md`: 14 de 14 com `**Status**: ✅ Complete` e todos os Done when marcados; contagens 389 → 470 conferem com o gate |
| T7 | ✅ Done · fix | `0403acc`: `select_for_update().exists()` em `InovacaoUpdateView.gravar` (`views.py:148`) impede o INSERT do `Model.save()` quando a linha some entre o `dispatch()` e a gravação. O teste `test_views_edicao.py:496-513` falhava antes da trava (confirmado pela M6) |

---

## Spec-Anchored Acceptance Criteria

Caminhos relativos a `inovacoes/tests/`, salvo indicação. Relidos no HEAD `b749ff3`.

### P1: Editar uma inovação que cadastrei

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| EDEX-01 | 200; `<title>`/`h1` "Editar inovação"; exatamente os 7 campos | `test_views_edicao.py:41` - `status_code == 200`; `:45-46` - title começa com e `h1 == ["Editar inovação"]`; `:47` - `list(form.fields) == CAMPOS`; `:49` - `name=` do form == os 7; `:50-51` - sem `autor`/`status`/`data_criacao`; `:70-72` - botão `["Salvar alterações"]` | ✅ PASS |
| EDEX-02 | todos os campos com o valor salvo, inclusive o contato salvo | `test_views_edicao.py:83-91` - `{campo: form[campo].value()} ==` os 7 valores salvos; `:93` - `value="Setor Financeiro (fin@x.com)"`; `:95` - sem o pré-preenchimento da INOV-39; `:96-97` - `option selected` de unidade e categoria | ✅ PASS (M12 morta) |
| EDEX-03 | link "Editar" → `/inovacoes/<id>/editar/` para quem pode alterar | `test_views_detalhe.py:199` - autor: `_links(html,"Editar") == ["/inovacoes/<pk>/editar/"]`; `:209` - administrador em inovação alheia | ✅ PASS (M9b morta) |
| EDEX-04 | mesma inovação atualizada, textos aparados, nenhuma nova | `test_views_edicao.py:217-220` - envio com espaços nas pontas; `count() == 1`; `:206-209` - cada campo `== dados[campo].strip()`, unidade e categoria por id | ✅ PASS (payload: os 7 valores; M25 morta) |
| EDEX-05 | 302 → `/inovacoes/<id>/` | `test_views_edicao.py:226` - `assertRedirects(…, f"/inovacoes/{pk}/")` | ✅ PASS (M13 morta) |
| EDEX-06 | "Inovação “<título salvo>” atualizada com sucesso." no `role="status"` do detalhe | `test_views_edicao.py:233` - `redirect_chain == [("/inovacoes/<pk>/", 302)]`; `:235` - texto exato com o título aparado dentro de `_regiao_de_status` | ✅ PASS (M21 morta) |
| EDEX-07 | mensagem não reaparece ao recarregar | `test_views_edicao.py:242` - presente na 1ª; `:244` - `"atualizada com sucesso" not in` no reload | ✅ PASS |
| EDEX-08 | autor, status e data forjados ignorados | `test_views_edicao.py:251-257` - POST com `autor`, `status=VALIDADA`, `data_criacao`; `:261-263` - `autor_id == autor.pk`, `status == EM_TESTE`, `data_criacao == DATA_ORIGINAL` | ✅ PASS (M20 morta) |
| EDEX-09 | mensagens da INOV-09, INOV-10, INOV-12, INOV-17; 200; valores enviados (INOV-11); resumo da INOV-30 em `role="alert"` | `test_views_edicao.py:347-351` - 200 e `errors == {"titulo": ["Informe o título da inovação."], "problema": ["Descreva o problema ou dor."]}` (INOV-09); `:355` - RESUMO no alerta; `:357-361` - valores preservados; `:371` - "Selecione uma unidade da lista." (INOV-17); `:381-383` - "Use no máximo 150 caracteres (você digitou 151)." (INOV-12) | ⚠️ PARCIAL: a INOV-10 (campo só com espaços tratado como vazio) não tem teste na rota de edição. Coberta só no formulário da F2. Fix 3 |
| EDEX-10 | qualquer recusa mantém todos os valores salvos | `test_views_edicao.py:362`, `:372`, `:384`, `:407`, `:449` - `_linha(inovacao) == antes` (todas as colunas) | ✅ PASS |
| EDEX-11 | busca acha pelas palavras novas de título, problema ou solução, e não pelas substituídas | `test_views_edicao.py:462` - antes: "manual" acha; `:465` - "divergencias" (problema novo) acha; `:466` - "manual" (só no problema antigo) não acha | ⚠️ PARCIAL: só o problema é afirmado. Título e solução mudam no envio (`dados`), mas nenhuma busca prova a troca deles. O mecanismo é o `Inovacao.save()` (AD-008, `models.py:157`), já provado na F3. Fix 3 |
| EDEX-12 | mesmo título, com ou sem mudança de caixa, mesma unidade → aceito | `test_views_edicao.py:387-393` - parametrizado `"Controle de Caixa"`/`"CONTROLE DE CAIXA"`; `assertRedirects` ao detalhe e título gravado | ✅ PASS |
| EDEX-13 | título de outra inovação da unidade (ignorando caixa) → recusa com "Já existe uma inovação com este título nesta unidade. Escolha outro título." no campo | `test_views_edicao.py:402-407` - `"planilha de COMPRAS"`; `errors == {"titulo": [MENSAGEM_DUPLICADO]}`; mensagem dentro de `id_titulo_error`; linha intacta. Outra unidade aceita (`:410-419`), acento distinto (`:422-430`) | ✅ PASS |
| EDEX-14 | corrida → só uma persiste; a outra 200 com a mensagem da EDEX-13, nunca 500 | `test_views_edicao.py:444-450` - validação neutralizada, constraint real do PostgreSQL; 200, `errors == {"titulo": [MENSAGEM_DUPLICADO]}`, resumo, linha intacta, `count == 1` | ✅ PASS (M10 morta) |
| EDEX-15 | duas edições em sequência → vale a última | `test_views_edicao.py:293-296` - autor e depois administrador; `_afirma_gravado(inovacao, segunda)` | ✅ PASS |
| EDEX-16 | "Cancelar" → `/inovacoes/<id>/`, sem alterar, sem confirmação | `test_views_edicao.py:105-110` - único link "Cancelar" com `href == "/inovacoes/<pk>/"`; o GET dele abre o detalhe (200); linha intacta | ✅ PASS (M11 morta) |

### P1: Curadoria pelo administrador

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| EDEX-17 | ADMINISTRADOR em inovação alheia → 200 e o form da EDEX-01 | `test_views_edicao.py:118` - `_afirma_formulario_de_edicao` completo; `test_permissoes.py:31` - regra `is True` | ✅ PASS |
| EDEX-18 | aplica EDEX-04 a 06 e mantém autor e data originais | `test_views_edicao.py:271-280` - 302 ao detalhe, 7 valores gravados, `autor_id == autor.pk`, `data_criacao == DATA_ORIGINAL`, mensagem no `role="status"`, "Cadastrada por Ana Souza em 01/09/2026" | ✅ PASS (M14 morta) |
| EDEX-19 | autor USUARIO e autor ADMINISTRADOR editam e excluem do mesmo jeito | `test_permissoes.py:15`, `:21`; `test_views_edicao.py:124`, `:286-288`; `test_views_exclusao.py:70`, `:197-199` | ✅ PASS |

### P1: Negar a alteração de inovações de terceiros

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| EDEX-20 | GET de USUARIO não autor nas duas rotas → 403 com os dois textos exatos | `test_views_edicao.py:56-60` - 403, `acesso_negado.html`, NEGADO e SO_AUTOR (textos exatos `:15-16`); `test_views_exclusao.py:113-117`; `test_controle_autoria.py:69` - toda rota descoberta | ✅ PASS para o terceiro sem bandeiras · ❌ sem prova na rota para `USUARIO` com `is_staff`/`is_superuser` (AD-009; M23b sobreviveu). Fix 1 |
| EDEX-21 | link "Voltar para a inovação" → `/inovacoes/<id>/` | `test_views_edicao.py:61-62` - `links == ["/inovacoes/<pk>/"]`; `test_views_exclusao.py:118-120` | ✅ PASS (M17 morta) |
| EDEX-22 | POST de edição do terceiro → 403, todos os valores intactos | `test_views_edicao.py:302-305` - página de acesso negado, `_linha == antes` (todas as colunas), `count == 1`; `test_controle_autoria.py:66-71` - POST com dados válidos e diferentes | ✅ PASS (M4 morta) · ❌ mesma lacuna de staff/superuser (Fix 1) |
| EDEX-23 | POST de exclusão do terceiro → 403, inovação continua | `test_views_exclusao.py:224-228` - 403, template, NEGADO, `values() == antes`; `test_controle_autoria.py:69-71` | ✅ PASS · ❌ mesma lacuna (Fix 1) |
| EDEX-24 | sem "Editar"/"Excluir" no detalhe para quem não é autor nem ADMINISTRADOR | `test_views_detalhe.py:217-218`, `:254-255` - `_links == []` e o caminho ausente do HTML (terceiro sem bandeiras) | ✅ PASS para o terceiro sem bandeiras · ❌ staff/superuser `USUARIO` e administrador rebaixado não testados na tela (M22, M22b sobreviveram). Fix 2 |
| EDEX-25 | perfil lido a cada requisição; rebaixado → 403 na seguinte | `test_permissoes.py:52-54`; `test_views_edicao.py:141-143` - 200, rebaixa, `_afirma_acesso_negado`; `test_views_exclusao.py:237-242` - POST de exclusão negado e a inovação continua | ✅ PASS |
| EDEX-26 | anônimo em GET e POST nas duas rotas → login com `next`, nada muda | `test_views_edicao.py:160` (GET), `:313-314` (POST, linha intacta); `test_views_exclusao.py:250-253` (GET e POST, continua) | ✅ PASS |
| EDEX-27 | `editar` com id inexistente em GET e POST → 404 da CONS-15 | `test_views_edicao.py:149-151` - 404, template, `h1` "Inovação não encontrada."; `:480-482` POST, nada criado | ✅ PASS (M5, M15 mortas) |
| EDEX-28 | `excluir` com id inexistente em GET → CONS-15 | `test_views_exclusao.py:128-130` | ✅ PASS |
| EDEX-29 | edição de inovação excluída no meio → CONS-15, nada criado | `test_views_edicao.py:490-493` (sequencial); `:509-513` (mesma requisição, `count == 0`) | ✅ PASS (M6 morta) |

### P2: Excluir uma inovação com confirmação

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| EDEX-30 | autor/ADMINISTRADOR GET → 200, "Excluir inovação", texto exato com título, unidade e categoria | `test_views_exclusao.py:38-44` - 200, template, title/`h1`, `AVISO` exato (`:13-16`); `:56`, `:64` | ✅ PASS (M16 morta) |
| EDEX-31 | link "Excluir" → `/inovacoes/<id>/excluir/` para quem pode alterar | `test_views_detalhe.py:236`, `:246` | ✅ PASS |
| EDEX-32 | botão "Excluir definitivamente" com POST à própria rota | `test_views_exclusao.py:78` - `method="post"`; `:80` - `action` vazio ou a rota; `:81` - csrf; `:83-84` - único botão, sem `type="button"` | ✅ PASS |
| EDEX-33 | link "Cancelar" → `/inovacoes/<id>/` | `test_views_exclusao.py:91-92` | ✅ PASS |
| EDEX-34 | seguir "Cancelar" → detalhe e a inovação continua | `test_views_exclusao.py:93-96` | ✅ PASS (M7b morta) |
| EDEX-35 | POST de autor/ADMINISTRADOR → apaga e 302 a `/inovacoes/` | `test_views_exclusao.py:152-153`, `:190-191` | ✅ PASS |
| EDEX-36 | GET nunca apaga | `test_views_exclusao.py:104-106` - 3 GETs com 200, `values() == antes` | ✅ PASS (M7, M7b mortas) |
| EDEX-37 | linha sai do banco; some da lista, da busca e da contagem da CONS-33 | `test_views_exclusao.py:153`; `:161` "2 inovações encontradas" → `:164-166` títulos `["Planilha de Compras"]` e "1 inovação encontrada"; `:168` fora da tabela; `:170-173` busca vazia | ✅ PASS |
| EDEX-38 | segundo POST → CONS-15, nunca 500 | `test_views_exclusao.py:206-207` - 302 e depois 404 com `inovacao_nao_encontrada.html` | ✅ PASS |
| EDEX-39 | detalhe da excluída → CONS-15 | `test_views_exclusao.py:214-215` | ✅ PASS |
| EDEX-40 | "Inovação “<título>” excluída com sucesso." no `role="status"` da lista, uma vez só | `test_views_exclusao.py:181-183` - `redirect_chain == [("/inovacoes/", 302)]`, `SUCESSO` exato (`:135`) na região, ausente no reload | ✅ PASS (M8, M8b mortas) |

### P1: Edição, confirmação e acesso negado acessíveis

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| EDEX-41 | rótulos, marcadores, ajudas e erros iguais ao cadastro (INOV-31/32/33/41) | `test_views_acessibilidade_alteracao.py:69-72` (label `for`), `:79-84` (`required` + "(obrigatório)" só nos 6), `:91-92` (ajuda no `aria-describedby`), `:113-115` (`aria-invalid="true"` só no campo com erro + `id_titulo_error`) | ✅ PASS |
| EDEX-42 | só controles nativos, sem `tabindex` positivo, foco visível, nas 3 páginas | `test_views_acessibilidade_alteracao.py:126-136` (parametrizado nas 3); `:142-146` - `:focus-visible` com `outline: Npx solid`, sem `outline: none` (`templates/base.html:11`) | ✅ PASS |
| EDEX-43 | um `h1` e `<title>` "Editar inovação", "Excluir inovação", "Acesso negado" | `test_views_acessibilidade_alteracao.py:153-155` (parametrizado nas 3) | ✅ PASS |

### Edge Cases da spec

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| EDEX-44 | banco fora → 500 do projeto, nada muda, sem detalhes da conexão | `test_views_erro_500.py:110-133` - parametrizado edição (`save`) e exclusão (`delete`); 500, `500.html`, nenhum trecho da conexão, `values() == antes` | ✅ PASS |
| EDEX-45 | POST sem CSRF nas duas rotas → 403, nada muda | `test_controle_autoria.py:79-85` - o próprio autor, `enforce_csrf_checks=True`; 403, não é a página de acesso negado, `values() == antes` | ✅ PASS (M19 morta) |

**Status**: ❌ Gaps presentes. 43/45 ACs com o valor da spec afirmado. EDEX-09 e EDEX-11 parciais. A AD-009 (staff/superuser `USUARIO`) não é provada na rota nem na tela (EDEX-20, 22, 23, 24). Nenhum spec-precision gap.

### RNF07 — "usuário comum tenta alterar registro de terceiro"

| Exigência | Evidência | Result |
| --------- | --------- | ------ |
| GET e POST nas duas rotas, 403 | `test_controle_autoria.py:55-71` (rotas × métodos); `test_views_edicao.py:127-132`, `:299-305`; `test_views_exclusao.py:109-122`, `:218-228` | ✅ |
| Banco intacto campo a campo | `Inovacao.objects.values().get(pk=…) == antes` (todas as colunas) em `test_controle_autoria.py:70`, `test_views_edicao.py:304`, `test_views_exclusao.py:228` | ✅ |
| Links escondidos | `test_views_detalhe.py:212-218`, `:249-255` (terceiro sem bandeiras) | ✅ · ❌ staff/superuser (M22, M22b) |
| Administrador rebaixado | `test_views_edicao.py:135-143`, `test_views_exclusao.py:231-242` | ✅ |
| `is_staff`/`is_superuser` sem perfil | só `test_permissoes.py:39-45` (modelo) | ❌ não chega à rota nem à tela (M23b, M22, M22b) |
| Varredura AD-009 dinâmica | `test_controle_autoria.py:18-32` percorre o `get_resolver()` em tempo de coleta, com a sanidade em `:35-38`. Uma rota nova sem guarda com `<int:pk>` é pega (M18 morta) | ⚠️ filtra por `"<int:pk>" in str(padrao.pattern)`. Uma rota com `<int:id>`, `<pk>` ou `<slug:…>` fica fora sem aviso (M24 sobreviveu). Fix 4 |

---

## Discrimination Sensor

Executado num `git worktree add --detach` temporário a partir de `b749ff3` (scratchpad da sessão), com o `.env` copiado e o mesmo PostgreSQL de teste (porta 5433). Uma mutação por vez, `pytest -q -x` da suíte inteira e `git checkout -- .` no worktree depois de cada uma, em sequência. No fim: `git worktree remove --force` + `git worktree prune`. `git status --porcelain` da árvore real: vazio antes e vazio depois (idêntico ao baseline). HEAD inalterado.

| # | File:line | Mutação | Killed? (primeiro teste que falhou) |
| - | --------- | ------- | ----------------------------------- |
| M1 | `inovacoes/models.py:176-178` | regra → `True` para todo autenticado | ✅ `test_controle_autoria.py::…[editar-get]` |
| M2 | `inovacoes/models.py:176` | sem a guarda `is_authenticated` | ✅ `test_permissoes.py::test_anonimo_nao_pode_alterar` |
| M3 | `inovacoes/models.py:177` | `is_staff` no lugar de `is_administrador` | ✅ `test_permissoes.py::…[is_staff]` |
| M3b | `inovacoes/models.py:177` | `is_administrador or is_staff or is_superuser or autor` | ✅ `test_permissoes.py::…[is_staff]` |
| M3c | `inovacoes/views.py:41` | mixin aceita também `is_staff or is_superuser` | ✅ `test_views_edicao.py::test_administrador_rebaixado…` (por acaso: o rebaixado por `.update()` mantém o `is_staff`) |
| M4 | `inovacoes/views.py:41` | mixin pula a regra no POST | ✅ `test_controle_autoria.py::…[editar-post]` |
| M4b | `inovacoes/views.py:41` | mixin pula a regra no GET | ✅ `test_controle_autoria.py::…[editar-get]` |
| M5 | `inovacoes/views.py:40` | id inexistente → 403 (ordem 404/403 trocada) | ✅ `test_views_edicao.py::test_id_sem_inovacao…` |
| M6 | `inovacoes/views.py:148-149` | `gravar` sem a checagem `select_for_update` | ✅ `test_views_edicao.py::test_inovacao_excluida_durante_o_envio_nao_e_recriada` |
| M7 | `inovacoes/views.py:177` | DeleteView apaga no GET (`self.object.delete()`) | ✅ (500 no GET) |
| M7b | `inovacoes/views.py:177` | GET apaga por queryset e ainda renderiza a confirmação | ✅ `test_views_exclusao.py::test_cancelar_leva_ao_detalhe…` |
| M8 | `inovacoes/views.py:183` | sem a mensagem de exclusão | ✅ `test_views_exclusao.py::test_exclusao_confirma_na_lista_uma_vez_so` |
| M8b | `inovacoes/views.py:183` | mensagem com o pk no lugar do título | ✅ idem |
| M9 | `inovacao_detail.html:12` | links para todos | ✅ `test_views_detalhe.py::test_terceiro_nao_ve_o_link_editar` |
| M9b | `inovacao_detail.html:12` | links para ninguém | ✅ `test_views_detalhe.py::test_autor_ve_o_link_editar_no_detalhe` |
| M10 | `inovacoes/views.py:75-76` | `IntegrityError` da constraint relançado | ✅ (500 no cadastro, INOV-25) |
| M11 | `inovacoes/views.py:164` | `url_cancelar` da edição → lista | ✅ `test_views_edicao.py::test_cancelar_leva_ao_detalhe…` |
| M12 | `inovacoes/views.py:142` | edição ganha `get_initial` com o contato da INOV-39 | ✅ `test_views_edicao.py::test_formulario_vem_preenchido…` |
| M13 | `inovacoes/views.py:142` | `success_url` da edição → lista | ✅ `test_views_edicao.py::test_envio_valido_redireciona_ao_detalhe` |
| M14 | `inovacoes/views.py:150` | edição atribui o autor da sessão | ✅ `test_views_edicao.py::test_administrador_edita…_mantem_autor_e_data` |
| M15 | `inovacoes/views.py:39-40` | `Http404` do mixin relançado (404 padrão) | ✅ `test_views_edicao.py::test_id_sem_inovacao…` |
| M16 | `inovacao_confirm_delete.html:9` | aviso sem a unidade | ✅ `test_views_exclusao.py::test_autor_ve_a_confirmacao_com_o_aviso` |
| M17 | `acesso_negado.html:13` | sem o link "Voltar para a inovação" | ✅ `test_views_edicao.py::test_terceiro_recebe_403…` |
| M18 | `inovacoes/urls.py:18` | rota nova `<int:pk>/status/` sem guarda (`InovacaoDetailView`) | ✅ `test_controle_autoria.py::…[inovacoes:status-get]` |
| M19 | `inovacoes/views.py:35` | `@method_decorator(csrf_exempt)` no `dispatch` do mixin | ✅ `test_controle_autoria.py::test_post_sem_token_csrf…[editar]` |
| M20 | `inovacoes/forms.py:24` | `Meta.fields` ganha `status` | ✅ `test_forms.py` (F2) |
| M21 | `inovacoes/views.py:142` | mensagem da edição diz "cadastrada" | ✅ `test_views_edicao.py::test_edicao_bem_sucedida_confirma…` |
| M22 | `inovacoes/views.py:128` | `pode_alterar` também para `is_staff` | ❌ **Survived**: staff `USUARIO` vê "Editar"/"Excluir" na inovação alheia → Fix 2 |
| M22b | `inovacoes/views.py:128` | `pode_alterar` também para `is_superuser` | ❌ **Survived** → Fix 2 |
| M23b | `inovacoes/views.py:41` | mixin aceita `is_superuser` (sem tocar o modelo) | ❌ **Survived**: superusuário `USUARIO` edita e exclui inovação alheia em GET e POST → Fix 1 |
| M24 | `inovacoes/urls.py:18` | rota nova `<int:id>/status/` sem guarda | ❌ **Survived**: a varredura não a enxerga → Fix 4 |
| (M23) | `inovacoes/views.py:41` | exceção artificial só para o username `dora` | Survived; diagnóstico, não contado. Confirma que nenhum teste de rota usa uma conta com bandeira |

**Sensor depth**: expandido (caminho de segurança RNF07/AD-009): 31 mutações contadas.
**Result**: 27/31 mortas; 4 sobreviventes não equivalentes (M22, M22b, M23b, M24) → FAIL ❌

---

## Code Quality

| Principle | Status |
| --------- | ------ |
| Minimum code | ✅ Um método no modelo, dois mixins, duas views de prateleira, dois templates pequenos |
| Surgical changes | ✅ Produção limitada a `models.py`, `views.py`, `urls.py` e 4 templates, como o design lista |
| No scope creep | ✅ Sem status na edição, sem ações na listagem, sem exclusão lógica |
| Matches patterns | ✅ O 404 da CONS-15 foi reaproveitado em `_inovacao_nao_encontrada` (`views.py:19`), e o 403 é renderizado pela view (AD-009) |
| Spec-anchored outcome check | ⚠️ 43/45; EDEX-09 e EDEX-11 parciais |
| Per-layer Coverage Expectation met | ❌ A matriz (`tasks.md`) pede o `is_staff`/`is_superuser` só no modelo, mas a mesma regra é reaplicada no mixin e no detalhe sem prova nessas camadas |
| Every test maps to a spec requirement | ✅ Toda docstring cita EDEX-NN, AD-009 ou a INOV reaplicada |
| Documented guidelines followed | ✅ nenhuma diretriz no projeto; strong defaults da Test Coverage Matrix |
| Testes da F1/F2/F3 intocados | ✅ `git diff 8ac62d4..b749ff3 -- contas inovacoes/tests`: só adições (+1214, nenhuma linha removida). As refatorações T2/T3/T4 passam na suíte da F2/F3 sem alteração, e a M10 é morta pelo teste do cadastro |

---

## Edge Cases

- [x] Título que existe em outra unidade é aceito (`test_views_edicao.py:410-419`).
- [x] Títulos que diferem só no acento continuam distintos (`test_views_edicao.py:422-430`).
- [x] Unidade inexistente no POST → INOV-17 (`test_views_edicao.py:365-372`). Categoria inexistente sem teste próprio na edição, coberta pelo formulário da F2.
- [ ] Id não numérico em `/inovacoes/abc/editar/`: sem teste próprio na F4. A rota `<int:pk>` não casa, e o comportamento equivale ao de `/inovacoes/abc/`, provado em `test_views_detalhe.py:176-180`. Não bloqueia.
- Observação (fora da spec): dois POSTs de exclusão que passam juntos pelo `dispatch()` antes de um deles apagar recebem os dois a mensagem de sucesso. O `Model.delete()` de uma linha já ausente não falha. A EDEX-38 só fala do reenvio depois da exclusão (coberto). Não bloqueia.

---

## Gate Check

- **Gate command**: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q` (árvore real, HEAD `b749ff3`)
- **Result**: exit 0. `ruff check`: All checks passed · `ruff format --check`: 97 files already formatted · `makemigrations --check`: No changes detected · `pytest -q`: 470 passed, 0 failed, 0 skipped (14.31 s)
- **Test count before feature**: 380 (`tasks.md`, linha de base)
- **Test count after feature**: 470
- **Delta**: +90. Nenhum teste removido nem alterado
- **Skipped tests**: nenhum
- **Failures**: nenhuma

---

## Spec-Precision Gaps

Nenhum. A EDEX-20 a 24 falam de "user with profile `USUARIO`", e a AD-009 (vinculante) fixa que `is_staff`/`is_superuser` não contam, então o resultado esperado para essas contas está definido. A lacuna está nos testes, não na spec.

---

## Fix Plans

### Fix 1: staff/superuser `USUARIO` não testado nas rotas de alteração (M23b) — Major

- **Root cause**: a varredura `test_controle_autoria.py:55-71` e os testes de recusa só usam a fixture `terceiro`, sem bandeiras. A regra da AD-009 (`is_staff`/`is_superuser` não contam) só é provada no modelo (`test_permissoes.py:39-45`), então o `dispatch()` do mixin pode ganhar uma exceção para essas contas sem que nenhum teste falhe.
- **Fix task**: em `test_controle_autoria.py`, parametrizar `test_terceiro_recebe_403_e_nada_muda` também pela conta: `terceiro`, `USUARIO` não autor com `is_staff=True` e `USUARIO` não autor com `is_superuser=True`. Manter rota × método e a comparação `values()` antes/depois.
- **Verify**: a M23b (`views.py:41` aceita `request.user.is_superuser`) e a M3c sem o caso do rebaixado precisam morrer.
- **Done when**: 403 e banco intacto para as 3 contas × 2 rotas × 2 métodos; gate verde.

### Fix 2: links do detalhe para staff/superuser `USUARIO` e para o administrador rebaixado (M22, M22b) — Major

- **Root cause**: `test_views_detalhe.py:212-218` e `:249-255` usam só o `terceiro`. O `pode_alterar` (`views.py:128`) pode passar a valer para `is_staff` ou `is_superuser` sem falha. A `maria` do banco local é exatamente esse caso.
- **Fix task**: parametrizar `test_terceiro_nao_ve_o_link_editar` e `test_terceiro_nao_ve_o_link_excluir` pelas mesmas 3 contas do Fix 1, e acrescentar o administrador rebaixado (`update(perfil=USUARIO)`) que deixa de ver os links na requisição seguinte (EDEX-24, EDEX-25).
- **Verify**: M22 e M22b morrem.
- **Done when**: nenhum dos dois links aparece para essas contas; gate verde.

### Fix 3: cláusulas sem teste na EDEX-09 e na EDEX-11 — Minor

- **Root cause**: a EDEX-09 cita a INOV-10, e a EDEX-11 cita título e solução. A rota de edição não afirma nenhum dos dois.
- **Fix task**: (a) em `test_views_edicao.py`, um envio de edição com um campo obrigatório só com espaços (p. ex. `solucao="   "`), afirmando a mensagem de obrigatório da INOV-09 no campo, 200 e a linha intacta. (b) Estender `test_busca_acha_pelo_texto_novo_e_nao_pelo_texto_substituido`, ou parametrizá-lo, para o título e a solução: palavra nova acha, palavra só do texto antigo não acha.
- **Done when**: as duas cláusulas têm `file:line`; gate verde.

### Fix 4: varredura da AD-009 presa ao texto literal `<int:pk>` (M24) — Minor

- **Root cause**: `test_controle_autoria.py:26` filtra por `"<int:pk>" in str(padrao.pattern)`. Uma rota futura de `inovacoes` com outro nome de parâmetro ou outro conversor não entra na varredura, e a sanidade (`:35-38`) não percebe.
- **Fix task**: selecionar toda rota do namespace `inovacoes` que capture algum parâmetro (`padrao.pattern.converters` não vazio, ou o regex com grupos nomeados), e falhar a coleta quando o parâmetro não for `pk`, para que a rota nova precise entrar na varredura ou na allowlist de forma explícita.
- **Verify**: a M24 (`<int:id>/status/` sem guarda) morre.
- **Done when**: a M18 e a M24 morrem; gate verde.

---

## Requirement Traceability Update

Proposta (o `spec.md` não foi editado pelo Verifier):

| Requirement | Previous Status | New Status |
| ----------- | --------------- | ---------- |
| EDEX-01 … EDEX-08, EDEX-10, EDEX-12 … EDEX-19, EDEX-21, EDEX-25 … EDEX-45 | Implementing | ✅ Verified |
| EDEX-09, EDEX-11 | Implementing | ❌ Needs Fix (Fix 3) |
| EDEX-20, EDEX-22, EDEX-23 | Implementing | ❌ Needs Fix (Fix 1) |
| EDEX-24 | Implementing | ❌ Needs Fix (Fix 2) |

---

## Summary

**Overall**: ❌ Not Ready (só correções de teste; nenhum defeito de produção encontrado)

**Spec-anchored check**: 43/45 ACs com o valor da spec afirmado; EDEX-09 e EDEX-11 parciais; 0 spec-precision gaps
**Sensor**: 27/31 mortas; sobreviventes M22, M22b, M23b, M24
**Gate**: 470 passed, 0 failed

**What works**: a regra de autoria fica num único método (`inovacoes/models.py:169-178`), aplicada no `dispatch()` antes de qualquer método HTTP (`inovacoes/views.py:35-46`), com 404 antes de 403. Terceiro sem bandeiras, rebaixado, anônimo e POST sem CSRF são recusados em GET e POST, com o banco comparado coluna a coluna (`test_controle_autoria.py:70`, `test_views_edicao.py:304`, `test_views_exclusao.py:228`). A trava contra recriar uma inovação excluída tem teste que a discrimina (`test_views_edicao.py:496-513`). O GET da exclusão nunca apaga (`test_views_exclusao.py:99-106`). As mensagens, os textos e os redirects são afirmados literalmente. Os testes da F1/F2/F3 não foram alterados.

**Issues found**:
1. AD-009 sem prova na rota para `USUARIO` com `is_staff`/`is_superuser` (M23b): Fix 1, `test_controle_autoria.py:55-71`.
2. Links do detalhe sem prova para essas contas e para o rebaixado (M22, M22b): Fix 2, `test_views_detalhe.py:212-218`, `:249-255`.
3. EDEX-09 (INOV-10) e EDEX-11 (título, solução) parciais: Fix 3, `test_views_edicao.py:339-362`, `:459-466`.
4. Varredura presa a `<int:pk>` (M24): Fix 4, `test_controle_autoria.py:26`.

**Next steps**: rodar os Fix 1–4 como tasks de teste e depois uma nova iteração do Verifier (iteração 2 de no máximo 3).
