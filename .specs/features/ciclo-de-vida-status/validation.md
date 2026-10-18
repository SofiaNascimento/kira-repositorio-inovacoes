# Ciclo de Vida do Status (F5) Validation

**Date**: 2026-10-18
**Iteration**: 2 (a iteração 1 fica abaixo, intacta; a iteração 2 está em [Iteração 2](#iteração-2), no fim)
**Spec**: `.specs/features/ciclo-de-vida-status/spec.md` (STAT-01 … STAT-37)
**Diff range (iteração 2)**: feature `6616da1..ef25406` em `main` (HEAD = `ef25406`). Correções: `f1d3de1` (T12) e `ef25406` (T13), só em `inovacoes/tests/`. `git diff f48bb1a..ef25406 -- ':!inovacoes/tests' ':!.specs'` vazio: nenhum código de produção mudou desde a iteração 1.
**Diff range (iteração 1)**: `6616da1..f48bb1a` em `main` (HEAD = `f48bb1a`), 11 commits (T1 `fd1ee9c`, T2 `0f09ede`, T3 `0a6307d`, T4 `8ad7dad`, T5 `10603fd`, T6 `73eccf5`, T7 `9f417d1`, T8 `4a48733`, T9 `0b4f8f4`, T10 `36fa95a`, T11 `f48bb1a`). 17 arquivos, +1604/−115. Produção: `inovacoes/models.py`, `views.py`, `urls.py`, `migrations/0007_mudancadestatus.py`, `templates/inovacoes/inovacao_detail.html`, `inovacao_status.html` e `templates/kira.css`.
**Verifier**: independent sub-agent (author ≠ verifier)

**Verdict**: FAIL ❌ (iteração 2, HEAD `ef25406`)

**Iteração 2 em resumo:** o gate passa com 685 testes. T12 mata a M11 e T13 mata a M27, e as duas correções afirmam o valor da spec sem enfraquecer nenhuma checagem anterior. Das 15 mutações novas, 14 morrem. A **N14** sobrevive: `.historico li { background: var(--brand-blue) }` (`templates/kira.css:521`) põe o texto do histórico a 2,48:1 e a data a 1,0:1, e a suíte inteira passa. O teste da STAT-37 só confere o par das regras que declaram `color`. Uma regra que só declara fundo não tem o texto herdado conferido, e o `FUNDO_HERDADO` é fixo, não derivado do fundo do ancestral. A STAT-37 cobre o caso ("every color the cycle control and the history add"), então a lacuna é de teste: 36/37 ACs, Fix 3 abaixo. Nenhum código de produção precisa mudar.

**Iteração 1 (registro original):** O gate passa com 684 testes, e 35 das 37 ACs têm evidência `file:line` com o valor da spec afirmado. O código de produção cumpre a spec em tudo o que conferi, inclusive nos dois pontos com lacuna. O FAIL vem do sensor: 2 dos 29 mutantes sobreviveram. **M11**: o detalhe mostra o histórico de *todas* as inovações em vez do histórico só daquela, e a suíte inteira passa (STAT-24, "every history record **of that Inovacao**"). Todo teste do histórico usa uma inovação só, então nenhum distingue "desta inovação" de "de todas". **M27**: `.ciclo li` passa a usar texto branco sobre fundo branco (`color: var(--surface)` sobre `background: var(--surface)`), e o teste da STAT-37 continua verde. O teste confere cada cor isoladamente contra o conjunto de textos e o conjunto de fundos do DS-08, nunca o par que a regra forma, e `surface` está nos dois conjuntos. Os dois viram fix tasks só de teste. Nenhum código de produção precisa mudar.

---

## Task Completion

| Task | Status | Notes |
| ---- | ------ | ----- |
| T1–T11 | ✅ Done | `tasks.md`, 11 de 11 marcadas completas; contagens por task (588 → 684) conferem com o gate |

---

## Spec-Anchored Acceptance Criteria

Caminhos relativos a `inovacoes/tests/`, salvo indicação. Lidos no HEAD `f48bb1a`.

### P1: Ver em que estágio do ciclo a inovação está

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| STAT-01 | h2 "Ciclo de vida"; `ol` com "Em teste", "Validada", "Disponível para replicação" nessa ordem | `test_views_detalhe.py:309` - `findall(h2) == ["Ciclo de vida"]`; `:311` - itens sem o sufixo `== ETAPAS`; `test_views_acessibilidade_alteracao.py:238-251` - `listas == [("ol", "ciclo")]` | ✅ PASS (M15 morta) |
| STAT-02 | "(status atual)" só no estágio gravado | `test_views_detalhe.py:322` - `html.count("(status atual)") == 1`; `:325` - lista inteira igual à esperada, nos 3 status | ✅ PASS (M15 morta) |
| STAT-03 | autor/administrador, status "Em teste" ou "Validada" → link "Avançar para “<próximo>”" → `/inovacoes/<id>/status/` | `test_views_detalhe.py:340` - `_links(secao, f"Avançar para “{proximo}”") == [f"/inovacoes/{pk}/status/"]`, 2 contas × 2 status | ✅ PASS (M3, M14 mortas) |
| STAT-04 | "Último estágio do ciclo." e nenhum link "Avançar", para qualquer conta | `test_views_detalhe.py:350` - `"<p>Último estágio do ciclo.</p>" in secao`; `:351-352` - `"Avançar" not in html`, caminho ausente; autor, administrador e terceiro | ✅ PASS (M4, M14 mortas) |
| STAT-05 | quem não pode alterar não vê o link | `test_views_detalhe.py:362-363` (terceiro, 2 status); `test_views_status.py:335-336` - `nao_autor_usuario` (terceiro, staff, superusuário) | ✅ PASS (M8 morta) |

### P1: Avançar o status um estágio

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| STAT-06 | 200; página "Avançar status"; texto exato; botão "Avançar para “Validada”"; "Cancelar" → `/inovacoes/<id>/` | `test_views_status.py:46` - 200; `:51` - `h1 == ["Avançar status"]`; `:52-55` - texto exato; `:60-61` - um botão submit com o rótulo exato; `:62-65` - `status_visto` oculto com o status gravado; `:66-67` - `cancelar == [f"/inovacoes/{pk}/"]`. Autor (`:70`), segundo passo (`:77`), administrador (`:84`). `<title>` por prefixo (`:50`), ver *Spec-Precision Gaps* | ✅ PASS ⚠️ (M16, M22 mortas) |
| STAT-07 | "Em teste" → "Validada"; 302 a `/inovacoes/<id>/` | `test_views_status.py:175` - `assertRedirects(…, f"/inovacoes/{pk}/", fetch_redirect_response=False)`; `:176` - `_status_no_banco == VALIDADA` | ✅ PASS |
| STAT-08 | "Validada" → "Disponível para replicação"; 302 ao detalhe | `test_views_status.py:204` - `redirect_chain == [(f"/inovacoes/{pk}/", 302)]`; `:205` - `== DISPONIVEL`; `:207` | ✅ PASS |
| STAT-09 | só o próximo estágio; nunca pula nem volta | `test_ciclo_de_vida.py:131-133` - `proximo_status` para os 3 status (último `None`); `:138-151` - avança um estágio; `:69-73` - os 7 pares inválidos recusados pelo banco | ✅ PASS (M3, M4, M4b mortas) |
| STAT-10 | GET: 200, texto exato, sem botão, "Voltar para a inovação" → detalhe. POST: status igual, sem registro, redirect com o mesmo texto como aviso | GET `test_views_status.py:98-105` - 200, `ULTIMO_ESTAGIO in conteudo`, sem `<form`/`<button`, `voltar == [f"/inovacoes/{pk}/"]`, autor e administrador. POST `:231-234` - redirect, `== DISPONIVEL`, `count() == 0`, `_mensagens == [("warning", ULTIMO_ESTAGIO)]` | ✅ PASS (M4, M4b, M17 mortas) |
| STAT-11 | GET nunca muda status nem cria registro | `test_views_status.py:113-116` - 3 GETs × 3 status, status igual e `count() == 0` | ✅ PASS (M24 morta) |
| STAT-12 | status enviado ausente ou diferente → nada muda; redirect com o aviso exato citando o status gravado | `test_views_status.py:244-247` - `[None, VALIDADA, "APROVADA"]`: redirect, `== EM_TESTE`, `count() == 0`, `[("warning", _conflito("Em teste"))]`; modelo `test_ciclo_de_vida.py:171-175` | ✅ PASS (M2, M25 mortas) |
| STAT-13 | duas confirmações simultâneas → exatamente um estágio e um registro | `test_views_status.py:255-259` (reenvio: `== VALIDADA`, `count() == 1`, aviso com "Validada"); `:262-278` (outra pessoa avança entre o `dispatch()` e a trava: nada gravado, aviso com o status gravado); `test_ciclo_de_vida.py:209-211` - primeira leitura termina em `FOR UPDATE`; `:191-200` - recusa pelo valor gravado, não pelo da instância | ✅ PASS (M1, M2b, M12b mortas). Sem teste com duas conexões reais; a trava é provada pelo SQL emitido |

### P1: Registrar cada mudança e dar feedback claro

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| STAT-14 | um registro com inovação, anterior, novo, responsável = usuário logado, data/hora | Payload completo: `test_ciclo_de_vida.py:145-151` - `MudancaDeStatus.objects.get()` (exatamente um), `inovacao_id == pk`, `(anterior, novo)`, `responsavel == autor`, `antes <= data <= now()`. Pela rota: `test_views_status.py:177-183` | ✅ PASS (M6 morta) |
| STAT-15 | status e registro na mesma transação | `test_ciclo_de_vida.py:215-225` - `create` falha → status `EM_TESTE`, `count() == 0`; `test_views_erro_500.py:147-170` (falha no `save` e no `create`) | ✅ PASS (M5, M5b mortas) |
| STAT-16 | mensagem de sucesso exata em `role="status"`; não reaparece ao recarregar | `test_views_status.py:185`, `:194`, `:208-210`, `:224` - `_mensagens(...) == [("success", _sucesso(...))]` (a função lê a região `role="status"`, `:153-157`); `:196-197` - recarregado `== []` | ✅ PASS (M12, M13 mortas) |
| STAT-24 | h2 "Histórico de status" com **todo registro daquela inovação**, do mais antigo ao mais recente | `test_views_detalhe.py:372` - h2; `:398-401` - ordem pela data, contra a ordem de criação; `test_ciclo_de_vida.py:101-117` - `ordering` com desempate pelo id. **Nenhum teste tem registros de outra inovação**: trocar a consulta por `MudancaDeStatus.objects` (todas as inovações) passa a suíte inteira (M11) | ❌ GAP (M11 sobreviveu) |
| STAT-25 | "<dd/mm/aaaa HH:MM> — de “X” para “Y”, por <nome completo ou username>", no fuso do projeto | `test_views_detalhe.py:398-401` - nome completo ("Ana Souza") e username ("carla"); `:409` - 02:30 UTC → "14/09/2026 23:30"; `:437-439` - sem N+1 com 3 responsáveis | ✅ PASS (M10 morta) |
| STAT-26 | sem registros → "Nenhuma mudança de status registrada." | `test_views_detalhe.py:416-417` - parágrafo exato e nenhum `<li`, com a inovação já em "Validada" (caso pré-F5) | ✅ PASS |
| STAT-27 | histórico visível para quem não pode alterar | `test_views_detalhe.py:426` - terceiro vê a linha exata | ✅ PASS |

### P1: Só o autor ou um administrador avança

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| STAT-17 | autor `USUARIO` avança como em STAT-07/08 | `test_views_status.py:170-185`, `:200-210` (fixture `autor` é `USUARIO`) | ✅ PASS |
| STAT-18 | ADMINISTRADOR avança a de outro autor; autor igual; administrador é o responsável | `test_views_status.py:220-224` - `== VALIDADA`, `gravada.autor == autor`, `responsavel == administrador`, mensagem; `test_ciclo_de_vida.py:233-234` | ✅ PASS (M6 morta) |
| STAT-19 | USUARIO não autor, GET e POST → 403 com a página da EDEX-20/21; nada muda | `test_views_status.py:323-327` - 403, `acesso_negado.html`, texto da EDEX-20, `== EM_TESTE`, `count() == 0`, GET e POST com `status_visto` correto; `test_controle_autoria.py:104-121` (varredura AD-009 inclui `inovacoes:status`, `:50`) | ✅ PASS (M7 morta) |
| STAT-20 | idem com `is_staff`/`is_superuser` | `test_views_status.py:309-327` com `nao_autor_usuario` = terceiro, staff, superusuário (`conftest.py:60-76` confere perfil e bandeiras) | ✅ PASS (M7 morta) |
| STAT-21 | perfil lido por requisição; rebaixado → 403 na próxima | `test_views_status.py:345-356` - 200 antes; rebaixado por `update()` (mantém `is_staff`, `:350`); POST → 403, nada gravado | ✅ PASS (M7, M24 mortas) |
| STAT-22 | id inexistente, GET e POST → 404 "Inovação não encontrada."; nenhum registro | `test_views_status.py:133-136` (GET, h1 exato); `:300-303` (POST); `:281-295` (apagada entre o `dispatch()` e a trava) | ✅ PASS (M18 morta) |
| STAT-23 | anônimo, GET e POST → login com `next`; nada muda | `test_views_status.py:369-371` - `assertRedirects(…, f"/entrar/?next={caminho}")`, status e contagem | ✅ PASS |

### P1: Histórico íntegro

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| STAT-28 | apagar a inovação apaga o histórico dela | `test_ciclo_de_vida.py:85-87` - `list(MudancaDeStatus.objects.all()) == [da_outra]` | ✅ PASS (M20 morta) |
| STAT-29 | apagar a conta responsável é recusado; registro fica | `test_ciclo_de_vida.py:94-97` - `ProtectedError`, mesmo registro, mesmo `responsavel_id` | ✅ PASS (M19 morta) |
| STAT-30 | nenhuma rota, tela ou admin edita/apaga o histórico | `test_ciclo_de_vida.py:311` - fora do `admin.site._registry`; `:318-320` - 404 em lista/alteração/exclusão para superusuário ADMINISTRADOR, registro intacto; `:331-336` - as 6 rotas exatas, nenhuma view com `MudancaDeStatus` | ✅ PASS |
| STAT-31 | banco recusa par fora das duas transições | `test_ciclo_de_vida.py:69-73` - 7 pares, `IntegrityError` nomeando `mudanca_de_status_transicao_valida`; `:49` - sanidade (7) | ✅ PASS |
| STAT-32 | cadastro → "Em teste", sem registro | `test_ciclo_de_vida.py:284-288` - com `status=DISPONIVEL` forjado: `== EM_TESTE`, `count() == 0` | ✅ PASS |
| STAT-33 | edição com status forjado → status igual, sem registro | `test_ciclo_de_vida.py:298-305` - título gravado, `== EM_TESTE`, `count() == 0`, 2 valores forjados | ✅ PASS |

### P1: Ciclo, confirmação e histórico acessíveis

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| STAT-34 | só nativos (`ol`/`ul`, links, `form` + `button`); sem `tabindex` positivo; foco visível; um `h1` e `<title>` "Avançar status" | `test_views_acessibilidade_alteracao.py:220-235` - um `button type=submit` dentro do `form`, um link; `:203-216` - nenhum papel de controle, `tabindex <= 0`; `:238-256` - seções `section aria-labelledby` + h2, uma `ol`; `:259-265` - `:focus-visible` com `outline` sólido nas 3 páginas; `:276-278` - `h1 == ["Avançar status"]`, `<title>` por prefixo | ✅ PASS ⚠️ (título por prefixo) |
| STAT-37 | estágio atual por texto; toda cor do ciclo e do histórico nos pares do DS-08 | Texto: `test_views_acessibilidade_alteracao.py:293` - sem CSS, `["Em teste", "Validada (status atual)", "Disponível para replicação"]`. Cor: `test_views_sistema_design.py:548-564` - cada `color` ∈ textos de `PARES_DE_TEXTO` e cada `background` ∈ fundos, **separadamente**; `:568-572` - `brand-navy` no estágio atual. O par formado não é conferido: texto `surface` sobre fundo `surface` passa (M27) | ❌ GAP (M27 sobreviveu). O CSS atual cumpre o DS-08 (conferido à mão abaixo) |

### Edge Cases da spec

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| STAT-35 | banco fora → 500 do projeto, nada gravado, sem detalhes | `test_views_erro_500.py:163` - 500; `:164` - `500.html`; `:166-168` - host, usuário, senha e traceback ausentes; `:169-170` - `== EM_TESTE`, `count() == 0`; falha no `save` e no `create` | ✅ PASS (M5, M5b mortas) |
| STAT-36 | POST sem CSRF → 403, status igual | `test_views_erro_500.py:179-183` - o próprio autor, `enforce_csrf_checks=True`: 403, não é o acesso negado, `== EM_TESTE`, `count() == 0` | ✅ PASS (M26 morta) |

**Status**: ❌ 35/37 ACs com o valor da spec afirmado e discriminante. STAT-24 e STAT-37 têm asserção, mas o sensor mostra que ela não distingue a violação. 1 spec-precision gap de redação (STAT-06/STAT-34), que não bloqueia.

### Conferência manual do DS-08 (STAT-37, código atual)

O CSS de produção está correto. A lacuna é só do teste. Pares que as regras novas formam (`templates/kira.css:493-523`): `.ciclo li` `text`/`surface`; `.ciclo li + li::before` `text-muted` sobre o `surface` do item; `[aria-current=step]` `brand-navy`/`surface` e borda `brand-blue`/`surface` (3:1, `test_views_sistema_design.py:286-289`); `.historico time` `text-muted` sobre `bg` ou `surface`. Os pares de texto estão em `PARES_DE_TEXTO` (`test_views_sistema_design.py:255-269`), com contraste ≥ 4,5 provado em `:279-282`.

---

## Discrimination Sensor

Executado num `git worktree add --detach` temporário a partir de `f48bb1a`, no scratchpad da sessão, com o `.env` copiado e o mesmo PostgreSQL de teste (porta 5433). O `import inovacoes` no worktree resolve para o próprio worktree. Linha de base no worktree: 684 passed. Uma mutação por vez, por substituição exata de texto (cada trecho conferido como único), `pytest -q` da suíte inteira e `git checkout -- .` depois de cada uma. M27 rodou num segundo worktree, criado e removido do mesmo jeito. No fim: `git worktree remove --force` + `git worktree prune`. `git status --porcelain` da árvore real: vazio antes e vazio depois. HEAD inalterado (`f48bb1a`).

| # | File:line | Mutação | Killed? (testes que falharam) |
| - | --------- | ------- | ----------------------------- |
| M1 | `inovacoes/models.py:223` | `select_for_update()` → `all()` | ✅ `test_ciclo_de_vida.py::test_avancar_trava_a_linha_ao_ler_o_status` |
| M2 | `inovacoes/models.py:227` | sem a checagem `status_visto != gravado` | ✅ 10 falhas: `test_status_visto_diferente_do_gravado…[3]`, `test_segundo_avanco…`, `test_recusa_pelo_status_gravado…`, `test_views_status.py::test_status_visto_ausente_ou_diferente…[3]`, `test_reenvio…`, `test_status_mudado_durante_o_envio…` |
| M2b | `inovacoes/models.py:227` | compara com `self.status` (instância velha) em vez do gravado | ✅ `test_recusa_pelo_status_gravado_e_nao_pelo_da_instancia`, `test_status_mudado_durante_o_envio_avisa_e_nao_grava` |
| M3 | `inovacoes/models.py:28` | `PROXIMO_STATUS` pula: "Em teste" → "Disponível" | ✅ 19 falhas, entre elas `test_proximo_status_segue_o_ciclo[EM_TESTE-VALIDADA]`, `test_avancar_status_avanca_um_estagio_e_registra[…]`, `test_quem_pode_alterar_ve_o_link_de_avancar[…]` |
| M4 | `inovacoes/models.py:29` | estágio final avança para "Em teste" | ✅ 9 falhas: `test_proximo_status_segue_o_ciclo[DISPONIVEL…]`, `test_avancar_no_ultimo_estagio…`, `test_ultimo_estagio_explica_e_ninguem_ve_o_link[3]`, `test_ultimo_estagio_explica_e_nao_oferece_botao[2]`, `test_envio_no_ultimo_estagio…`, acessibilidade `[ultimo_estagio]` |
| M4b | `inovacoes/models.py:229` | `PROXIMO_STATUS.get(gravado, gravado)` (repete o estágio final) | ✅ `test_avancar_no_ultimo_estagio_e_recusado_sem_gravar`, `test_envio_no_ultimo_estagio_avisa_e_nao_grava` |
| M5 | `inovacoes/models.py:234-237` | registro criado fora da transação, depois do status | ✅ `test_falha_ao_registrar_desfaz_o_novo_status`, `test_banco_indisponivel_na_troca_de_status…[criacao-do-registro]` |
| M5b | `inovacoes/models.py:233-237` | registro criado antes, dentro da transação; status gravado fora dela | ✅ `test_banco_indisponivel_na_troca_de_status…[gravacao-do-status]` |
| M6 | `inovacoes/models.py:236` | `responsavel=self.autor` em vez de `por` | ✅ `test_responsavel_e_quem_avanca_e_o_autor_nao_muda`, `test_administrador_avanca_a_inovacao_de_outro_autor` |
| M7 | `inovacoes/views.py:199` | `InovacaoStatusView` sem o `AlteracaoDeInovacaoMixin` (`model = Inovacao`) | ✅ 46+ falhas, entre elas `test_nao_autor_usuario_recebe_403…[terceiro|staff|superusuario-get|post]`, `test_administrador_rebaixado…`, `test_controle_autoria.py::test_terceiro_recebe_403…[…status…]` |
| M8 | `inovacao_detail.html:58` | link "Avançar" sem checar `pode_alterar` (`{% else %}`) | ✅ 5 falhas: `test_terceiro_nao_ve_o_link_de_avancar[2]`, `test_nao_autor_usuario_nao_ve_o_link_de_avancar[3]` |
| M9 | `inovacoes/views.py:132` | `.order_by("-data", "-id")` na consulta do detalhe | ✅ `test_historico_lista_as_mudancas_do_mais_antigo_ao_mais_recente` |
| M9b | `inovacoes/models.py:291` | `ordering = ["-data", "-id"]` | ✅ `test_historico_sai_do_mais_antigo…`, `test_historico_com_a_mesma_data…`, `test_historico_lista_as_mudancas…` |
| M10 | `inovacoes/views.py:132` | sem `select_related("responsavel")` | ✅ `test_historico_nao_cresce_em_consultas_com_os_registros[3]` |
| **M11** | `inovacoes/views.py:132` | `mudancas = MudancaDeStatus.objects.select_related("responsavel")` (histórico de **todas** as inovações) | ❌ **Survived**: 684 passed. Uma sonda descartável no scratch (outra inovação com registro; o detalhe da primeira deveria mostrar "Nenhuma mudança…") falha com a mutação, então a mutação é efetiva |
| M12 | `inovacoes/views.py:240` | mensagem de sucesso "mudado de" | ✅ 4 falhas: `test_autor_avanca_de_em_teste…`, `test_mensagem_de_sucesso_nao_reaparece…`, `test_autor_avanca_de_validada…`, `test_administrador_avanca…` |
| M12b | `inovacoes/views.py:224` | aviso de conflito com o status da instância em vez do gravado | ✅ `test_status_mudado_durante_o_envio_avisa_e_nao_grava` |
| M13 | `inovacoes/views.py:241` | mensagem de sucesso com o status novo no lugar do anterior | ✅ 4 falhas (as mesmas da M12) |
| M14 | `inovacao_detail.html:56` | condição do estágio final invertida | ✅ 11 falhas: `test_quem_pode_alterar_ve_o_link…[4]`, `test_ultimo_estagio_explica_e_ninguem_ve_o_link[3]`, `test_terceiro_nao_ve_o_link…[2]`, acessibilidade `[ciclo]` |
| M15 | `inovacao_detail.html:48` | "(status atual)" nos estágios que não são o atual | ✅ `test_ciclo_marca_so_o_estagio_atual_com_texto[3]`, `test_estagio_atual_e_identificavel_sem_css` |
| M16 | `inovacao_status.html:17` | `status_visto` oculto com o próximo status | ✅ `test_autor_ve_a_confirmacao…[2]`, `test_administrador_ve_a_confirmacao…` |
| M17 | `inovacoes/views.py:232` | aviso do estágio final como `info` | ✅ `test_envio_no_ultimo_estagio_avisa_e_nao_grava` |
| M18 | `inovacoes/views.py:233` | `except Inovacao.DoesNotExist` → `except LookupError` | ✅ `test_inovacao_excluida_durante_o_envio_responde_404` |
| M19 | `inovacoes/models.py:281` | `responsavel` com `CASCADE` | ✅ `test_excluir_a_conta_responsavel_e_recusado` |
| M20 | `inovacoes/models.py:270` | `inovacao` com `PROTECT` | ✅ `test_excluir_a_inovacao_apaga_so_o_historico_dela` |
| M21 | `inovacoes/models.py:234` | `self.save()` sem `update_fields` | ✅ `test_avancar_grava_so_o_status` |
| M22 | `inovacao_status.html:19` | "Cancelar" aponta para a lista | ✅ `test_autor_ve_a_confirmacao…[2]`, `test_administrador_ve_a_confirmacao…`, acessibilidade `[avancar]` |
| M24 | `inovacoes/views.py:208` | o GET avança o status ao montar o contexto | ✅ 6 falhas, entre elas `test_get_nunca_muda_o_status_nem_registra[EM_TESTE|VALIDADA]` |
| M25 | `inovacoes/views.py:220` | `status_visto` ausente tratado como o status da instância | ✅ `test_status_visto_ausente_ou_diferente_avisa_e_nao_grava[None]` |
| M26 | `inovacoes/views.py:199` | `csrf_exempt` na view | ✅ `test_views_erro_500.py::test_troca_de_status_sem_token_csrf_e_recusada` |
| **M27** | `templates/kira.css:510` | `.ciclo li { color: var(--surface) }` (branco sobre o `background: var(--surface)`) | ❌ **Survived**: 684 passed |

**Sensor depth**: expandido (integridade de transição de estado e autorização): 29 mutações de comportamento, cobrindo trava, checagem do status visto, sequência, estágio final, transação, responsável, mixin, CSRF, GET sem efeito, link condicional, ordem, N+1, filtro por inovação, mensagens, `on_delete` e contraste.
**Result**: 27/29 mortas, 2 sobreviventes (M11, M27) - FAIL ❌

---

## Code Quality

| Principle | Status |
| --------- | ------ |
| Minimum code | ✅ A regra fica em `Inovacao.avancar_status` (AD-011), sem camada nova; a view só traduz exceções em mensagens |
| Surgical changes | ✅ Testes existentes só ganharam acréscimos previstos (`CONSULTAS_DO_DETALHE` 6 → 7, telas 8 → 9, sanidade da varredura com `inovacoes:status`) |
| No scope creep | ✅ |
| Matches patterns | ✅ Confirmação por página com POST (F4), mixin da AD-009, 404 da CONS-15, mensagens em `role="status"` |
| Spec-anchored outcome check | ❌ 35/37 (STAT-24 e STAT-37 sem discriminação) |
| Per-layer Coverage Expectation met | ⚠️ Modelo 1:1 com as ACs; rota com caminho feliz, borda e erro. Falta, na tela, o caso de registros de outra inovação (STAT-24) |
| Every test maps to a spec requirement | ✅ Toda docstring nova cita STAT-NN, AD-008/009/011 ou L-003 |
| Documented guidelines followed | ✅ `.specs/LESSONS.md` (L-003 aplicada na rota e na tela; L-005 aplicada: o histórico e o link são conferidos no detalhe, não só no modelo) |

---

## Edge Cases

- [x] Inovação pré-F5 já em "Validada": controle no estágio gravado e histórico vazio (`test_views_detalhe.py:412-417`, `:317-325`).
- [x] Inovação excluída entre abrir a confirmação e enviar: 404, sem registro (`test_views_status.py:281-295`).
- [x] Duplo clique: o segundo POST cai no aviso de conflito (`test_views_status.py:250-259`).
- [ ] Administrador avança a própria inovação: sem teste próprio; a regra é a mesma do autor (`pode_ser_alterada_por`). Não bloqueia.
- [ ] Filtro "Validada" da listagem logo depois do avanço: sem teste na F5; o filtro da CONS-27 lê a coluna `status`, que o avanço grava (`test_ciclo_de_vida.py:145`). Não bloqueia.
- [ ] Id não numérico em `/inovacoes/abc/status/`: sem teste próprio; a rota usa `<int:pk>` (`inovacoes/urls.py:20`), como na F4. Não bloqueia.

---

## Gate Check

- **Gate command**: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q` (árvore real, HEAD `f48bb1a`)
- **Result**: exit 0. `ruff check`: All checks passed · `ruff format --check`: 109 files already formatted · `makemigrations --check`: No changes detected · `pytest -q`: 684 passed, 0 failed, 0 skipped (15.9 s)
- **Test count before feature**: 574 (`tasks.md`, linha de base)
- **Test count after feature**: 684
- **Delta**: +110. Nenhum teste removido; as três alterações em testes existentes são acréscimos previstos nas tasks
- **Skipped tests**: nenhum
- **Failures**: nenhuma

---

## Spec-Precision Gaps

1. **STAT-06 / STAT-34, `<title>`**: a AC pede o `<title>` "reading 'Avançar status'", mas o `base.html` acrescenta " · Repositório de Inovações" a toda página. Os testes conferem o prefixo (`test_views_status.py:50`, `test_views_acessibilidade_alteracao.py:278`), como na EDEX-43. Julgamento: a página cumpre a intenção da AC (o nome da página abre o título), e o texto da AC é que está impreciso. **Não bloqueia.** Sugestão: na próxima revisão da spec, escrever "um `<title>` que começa por 'Avançar status'".
2. **STAT-37, "contrast pairs of DS-08"**: a AC exige pares, mas o teste trata texto e fundo como conjuntos independentes. Não é ambiguidade da spec: o teste não chega ao que a spec diz, e isso está registrado como GAP (M27), não aqui.

---

## Fix Plans

### Fix 1: STAT-24 não distingue "desta inovação" de "de todas" (M11) — Major

- **Root cause**: todo teste do histórico no detalhe cria registros de uma única inovação, então a consulta `self.object.mudancas_de_status` nunca é confrontada com registros alheios.
- **Fix task**: em `inovacoes/tests/test_views_detalhe.py`, acrescentar um teste com duas inovações. A outra tem um registro, e a do detalhe tem zero ou um. Afirmar que `_historico(html)` lista só os itens da inovação aberta e que, com zero, aparece "Nenhuma mudança de status registrada.".
- **Verify**: com a mutação M11 (`mudancas=MudancaDeStatus.objects.select_related("responsavel")`) num scratch, o teste novo falha; no HEAD passa.
- **Done when**: M11 morta; gate de build verde; nenhum código de produção alterado.
- **Priority**: Major (STAT-24, AC MVP)

### Fix 2: STAT-37 confere cores soltas, não pares (M27) — Minor

- **Root cause**: `test_ciclo_e_historico_so_usam_cores_de_pares_conferidos` (`test_views_sistema_design.py:548-564`) testa `color ∈ textos` e `background ∈ fundos` separadamente; `surface` está nos dois conjuntos.
- **Fix task**: afirmar o par efetivo de cada regra de `.ciclo`/`.historico` contra `PARES_DE_TEXTO`: `(color, background)` quando a regra declara os dois; quando só declara `color`, usar o fundo herdado explícito no teste (`.ciclo li` e o `::before` sobre `surface`; `.historico time` sobre `bg` e `surface`).
- **Verify**: com M27 (`.ciclo li { color: var(--surface) }`) num scratch, o teste falha; no HEAD passa.
- **Done when**: M27 morta; gate verde; nenhum código de produção alterado.
- **Priority**: Minor (o CSS atual cumpre o DS-08; o risco é regressão futura não detectada)

---

## Requirement Traceability Update

Não aplicada (FAIL). Proposta para depois da iteração 2:

| Requirement | Previous Status | New Status |
| ----------- | --------------- | ---------- |
| STAT-01 … STAT-23, STAT-25 … STAT-36 | Implementing | ✅ Verified (evidência acima) |
| STAT-24 | Implementing | ❌ Needs Fix (Fix 1) |
| STAT-37 | Implementing | ❌ Needs Fix (Fix 2) |

---

## Histórico

- **Iteração 1** (HEAD `f48bb1a`): FAIL ❌. 35/37 ACs; 27/29 mutantes mortos. Sobreviveram M11 (histórico de todas as inovações no detalhe) e M27 (texto branco sobre branco no ciclo). Viram Fix 1 e Fix 2, só em teste.

---

## Summary

**Overall**: ❌ Not Ready (evidência das lacunas: `inovacoes/views.py:132` sob M11 com 684 passed; `inovacoes/tests/test_views_sistema_design.py:548-564` sob M27 com 684 passed)

**Spec-anchored check**: 35/37 ACs com o valor da spec afirmado e discriminante; 1 spec-precision gap de redação (título, não bloqueia)
**Sensor**: 27/29 mortas (sobreviventes: M11, M27)
**Gate**: 684 passed, 0 failed
**validate_state.py**: `python3 .claude/skills/tlc-spec-driven/scripts/validate_state.py ciclo-de-vida-status` → exit 1, "validation.md verdict is FAIL - route the ranked gaps to fix tasks, then re-verify (feature is not done)". É o resultado esperado para um FAIL.

**What works**: a transição é atômica e serializada. `select_for_update` lê o valor gravado, o `status_visto` recusa reenvio e corrida, e o registro é criado na mesma transação (`inovacoes/models.py:211-237`). O banco recusa os 7 pares inválidos. A autorização reaproveita o mixin da AD-009 e é provada com terceiro, staff, superusuário e administrador rebaixado. O GET nunca grava, e o CSRF e o banco fora do ar não deixam nada pela metade. As mensagens são exatas e têm o nível certo.

**Issues found**: Fix 1 (STAT-24, M11) e Fix 2 (STAT-37, M27), ambos de teste.

**Lessons recorded**: L-019 (M11, filtro por pai), L-020 (M27, contraste por par) e L-021 (título com sufixo do layout), todas `candidate` em `.specs/lessons.json`.

**Next steps**: o orquestrador encaminha Fix 1 e Fix 2 a um implementador, que só mexe em teste, e depois despacha a iteração 2 do Verifier.

---

## Iteração 2

**Date**: 2026-10-18
**HEAD**: `ef25406` (feature `6616da1..ef25406`; correções `f1d3de1` T12 e `ef25406` T13)
**Verifier**: novo sub-agente independente (não escreveu código, testes nem correções); cobertura re-derivada da spec
**Produção inalterada**: `git diff --stat f48bb1a..ef25406 -- ':!inovacoes/tests' ':!.specs'` vazio. Os dois commits de correção só tocam `inovacoes/tests/test_views_detalhe.py` (+27) e `inovacoes/tests/test_views_sistema_design.py` (+30/−11), e o `tasks.md`

### Task Completion

| Task | Status | Notes |
| ---- | ------ | ----- |
| T1–T11 | ✅ Done | Inalteradas desde a iteração 1 |
| T12 (Fix 1) | ✅ Done | `f1d3de1`: `test_views_detalhe.py:429-453`. 685 passed (+1), confere com o gate |
| T13 (Fix 2) | ✅ Done | `ef25406`: `test_views_sistema_design.py:546-585`, reescrito no lugar (+0 testes) |

### Reconferência das correções

**T12 (STAT-24, STAT-26)**: `test_historico_lista_so_as_mudancas_da_inovacao_aberta` (`test_views_detalhe.py:429-453`) cria três inovações. A primeira tem um registro, a segunda dois e a terceira nenhum. `:441` afirma `_historico(html) == ["01/10/2026 09:05 — de “Em teste” para “Validada”, por Ana Souza"]` no detalhe da primeira, e `:444-447` afirma a lista exata de dois itens, em ordem, no da segunda. Isso prova "every history record **of that Inovacao**, from the oldest to the most recent", e o texto é o da STAT-25. `:452-453` afirma `'<p class="vazio">Nenhuma mudança de status registrada.</p>' in secao` e `"<li" not in secao` na terceira, enquanto as outras têm histórico (STAT-26 com dados alheios presentes). Com a M11, só esse teste falha. O resultado bate com a spec. ✅

**T13 (STAT-37)**: comparei com `git show ef25406^:inovacoes/tests/test_views_sistema_design.py`. As checagens antigas eram quatro: nenhuma cor literal, todo `var(--x)` existente no `:root`, `color` ser `var()` de um token que aparece como texto em algum par, e `background*` ser `var()` de um token que aparece como fundo em algum par. As quatro continuam, em `:569`, `:573` e `:574-576` (o `_token_de` de `:557-560` exige `var(--x)` em todo `background*` e no `color`). A checagem de texto ficou mais estrita: `(texto, fundo) in PARES_DE_TEXTO` (`:585`) implica a pertinência antiga. Regra com `color` sem fundo próprio nem entrada em `FUNDO_HERDADO` faz o teste falhar (`:583`). Dois mais `background*` na mesma regra quebram o desempacotamento `(fundo,) = fundos` (`:581`), o que é conservador. Só existe uma diferença de forma: `dict(re.findall(...))` guarda a última declaração de cada propriedade. Para `color`, a última é a que o navegador aplica, então isso não enfraquece nada. `FUNDO_HERDADO` (`:549-553`) confere com o CSS e o HTML atuais: `.ciclo li` tem `background: var(--surface)` (`kira.css:509`), e a seção do histórico fica fora do `.cartao` (`inovacao_detail.html:20-41` contra `:63-75`), sobre o `body` com `--bg` (`kira.css:71`). Nenhuma checagem foi enfraquecida. ✅ A M27 morre. **Lacuna residual**: só as regras que declaram `color` têm o par conferido. Uma regra que só declara fundo deixa o texto herdado sem conferência, e `FUNDO_HERDADO` não acompanha o fundo real do ancestral. A N14, abaixo, explora isso.

### Spec-Anchored Acceptance Criteria (re-derivado no HEAD `ef25406`)

Caminhos relativos a `inovacoes/tests/`. "Reli" quer dizer que esta iteração leu a linha no HEAD e conferiu que a asserção afirma o valor da spec. "Herdado" quer dizer que a iteração 1 já tinha a evidência, o arquivo não mudou e a célula não foi relida aqui.

| AC | `file:line` + assertion (HEAD) | Conferência | Result |
| -- | ------------------------------ | ----------- | ------ |
| STAT-01 | `test_views_detalhe.py:309` h2 `== ["Ciclo de vida"]`; `:311` itens `== ETAPAS` | Reli; N5 morta | ✅ |
| STAT-02 | `test_views_detalhe.py:322` `count("(status atual)") == 1`; `:325` lista exata, 3 status | Reli; N5 morta | ✅ |
| STAT-03 | `test_views_detalhe.py:340` `_links(secao, f"Avançar para “{proximo}”") == [f"/inovacoes/{pk}/status/"]` | Reli; N4 morta | ✅ |
| STAT-04 | `test_views_detalhe.py:350-352` "<p>Último estágio do ciclo.</p>", sem "Avançar", 3 contas | Reli | ✅ |
| STAT-05 | `test_views_detalhe.py:362-363`; `test_views_status.py:335-336` (terceiro, staff, superusuário) | Reli | ✅ |
| STAT-06 | `test_views_status.py:46` 200; `:51` h1; `:52-55` texto exato; `:60-61` botão; `:66-67` "Cancelar" → detalhe; `<title>` por prefixo `:50` | Reli; N10, N11 mortas | ✅ ⚠️ (título, ver *Spec-precision*) |
| STAT-07 | `test_views_status.py:175` `assertRedirects(…, f"/inovacoes/{pk}/")`; `:176` `== VALIDADA` | Reli; N7, N9 mortas | ✅ |
| STAT-08 | `test_views_status.py:204` (`redirect_chain == [(…, 302)]` em `:166`); `:205` `== DISPONIVEL`; `:207` | Reli; N7, N9 mortas | ✅ |
| STAT-09 | `test_ciclo_de_vida.py:131-133` `proximo_status`; `:138-151`; `:69-73` | Reli | ✅ |
| STAT-10 | GET `test_views_status.py:98-105`; POST `:231-234` `[("warning", ULTIMO_ESTAGIO)]` | Reli | ✅ |
| STAT-11 | `test_views_status.py:113-116` 3 GETs, status igual, `count() == 0` | Reli | ✅ |
| STAT-12 | `test_views_status.py:244-247` `[None, VALIDADA, "APROVADA"]` → `[("warning", _conflito("Em teste"))]`; `test_ciclo_de_vida.py:171-175` | Reli; N6, N8 mortas | ✅ |
| STAT-13 | `test_views_status.py:255-259`, `:262-278`; `test_ciclo_de_vida.py:191-200`, `:209-211` (`FOR UPDATE`) | Reli | ✅ |
| STAT-14 | `test_ciclo_de_vida.py:145-151` payload completo; `test_views_status.py:177-183` | Reli; N9 morta | ✅ |
| STAT-15 | `test_ciclo_de_vida.py:215-225`; `test_views_erro_500.py:147-170` | Reli | ✅ |
| STAT-16 | `test_views_status.py:185`, `:194`, `:208-210`, `:224` (região `role="status"`, `:153-157`); `:196-197` recarregado `== []` | Reli; N7 morta | ✅ |
| STAT-17 | `test_views_status.py:170-185`, `:200-210` (`conftest.py:8-11`: `autor` criado por `create_user`, perfil padrão) | Reli | ✅ |
| STAT-18 | `test_views_status.py:220-224`; `test_ciclo_de_vida.py:233-234` | Reli | ✅ |
| STAT-19 | `test_views_status.py:323-327` 403, `acesso_negado.html`, texto da EDEX-20, nada gravado | Reli | ✅ |
| STAT-20 | `test_views_status.py:309-327` com `nao_autor_usuario` (terceiro, staff, superusuário) | Reli | ✅ |
| STAT-21 | `test_views_status.py:345-356` | Reli | ✅ |
| STAT-22 | `test_views_status.py:133-136`, `:300-303`, `:281-295` | Reli | ✅ |
| STAT-23 | `test_views_status.py:369-371` `assertRedirects(…, f"/entrar/?next={caminho}")` | Reli | ✅ |
| STAT-24 | `test_views_detalhe.py:372` h2; `:398-401` ordem pela data; **`:441`, `:444-447` só os registros da inovação aberta** | Re-derivado (T12); M11 morta | ✅ |
| STAT-25 | `test_views_detalhe.py:398-401` nome/username; `:409` fuso; `:441`, `:444-447` | Reli; N1, N2, N3 mortas | ✅ |
| STAT-26 | `test_views_detalhe.py:416-417`; **`:452-453` com outras inovações tendo histórico** | Re-derivado (T12); N15 morta | ✅ |
| STAT-27 | `test_views_detalhe.py:420-426` terceiro vê a linha exata | Reli | ✅ |
| STAT-28 | `test_ciclo_de_vida.py:85-87` `== [da_outra]` | Reli | ✅ |
| STAT-29 | `test_ciclo_de_vida.py:94-97` `ProtectedError` | Reli | ✅ |
| STAT-30 | `test_ciclo_de_vida.py:311-320`, `:331-336` | Reli | ✅ |
| STAT-31 | `test_ciclo_de_vida.py:69-73` 7 pares, `IntegrityError` com o nome da constraint | Reli | ✅ |
| STAT-32 | `test_ciclo_de_vida.py:284-288` | Reli | ✅ |
| STAT-33 | `test_ciclo_de_vida.py:298-305` | Reli | ✅ |
| STAT-34 | `test_views_acessibilidade_alteracao.py:220-234`, `:205-216`, `:246-255`, `:259-265`, `:276-278` (`<title>` por prefixo) | Reli; N11 morta | ✅ ⚠️ (título) |
| STAT-35 | `test_views_erro_500.py:163-170` | Reli | ✅ |
| STAT-36 | `test_views_erro_500.py:179-183` | Reli | ✅ |
| STAT-37 | Texto: `test_views_acessibilidade_alteracao.py:293`. Cor: `test_views_sistema_design.py:585` `(texto, fundo) in PARES_DE_TEXTO` só para regras com `color`. **Regra com fundo e sem `color` não tem o texto herdado conferido**: `.historico li { background: var(--brand-blue) }` passa a suíte (N14), com o texto a 2,48:1 e a data a 1,0:1 | Re-derivado (T13); M27, N12, N13 mortas; **N14 sobreviveu** | ❌ GAP |

**Status**: ❌ 36/37 ACs com o valor da spec afirmado e discriminante. A STAT-37 tem asserção, mas ela não distingue um fundo novo sem `color` (N14). Há 1 spec-precision gap de redação (título, STAT-06/STAT-34), que não bloqueia.

### Discrimination Sensor (iteração 2)

Rodado num `git worktree add --detach` em `scratchpad/wt`, a partir de `ef25406`, com o `.env` copiado e o PostgreSQL de teste (porta 5433). O `inovacoes.__file__` resolve para a worktree, e a linha de base nela é 685 passed. Cada mutação foi feita por substituição exata, com o trecho conferido como único (`count == 1`). Para cada uma rodei a suíte inteira (`.venv/bin/pytest -q -p no:cacheprovider`) e depois `git checkout -- .` e `git diff --quiet`. No fim, `git worktree remove --force` e `git worktree prune`. O `git status --porcelain` da árvore real ficou vazio antes e depois, o HEAD continua `ef25406` e `git worktree list` só mostra a árvore principal.

#### Sobreviventes da iteração 1, re-injetadas como descritas

| # | File:line | Mutação | Killed? |
| - | --------- | ------- | ------- |
| M11 | `inovacoes/views.py:132` | `mudancas=MudancaDeStatus.objects.select_related("responsavel")`, com `MudancaDeStatus` acrescentado ao import da linha 9 | ✅ `test_views_detalhe.py::test_historico_lista_so_as_mudancas_da_inovacao_aberta` (único) |
| M27 | `templates/kira.css:510` | `.ciclo li { … color: var(--surface) }` | ✅ `test_views_sistema_design.py::test_ciclo_e_historico_so_usam_cores_de_pares_conferidos[.ciclo]` (único) |

#### Mutações novas (iteração 2)

| # | File:line | Mutação | Killed? (testes que falharam) |
| - | --------- | ------- | ----------------------------- |
| N1 | `inovacao_detail.html:69` | responsável só pelo username (sem nome completo) | ✅ 4: `test_historico_lista_as_mudancas_do_mais_antigo…`, `…_no_fuso_de_sao_paulo`, `test_terceiro_ve_o_historico`, `…_so_as_mudancas_da_inovacao_aberta` |
| N2 | `inovacao_detail.html:69` | data `"m/d/Y H:i"` | ✅ os mesmos 4 |
| N3 | `inovacao_detail.html:69` | anterior e novo trocados no item do histórico | ✅ os mesmos 4 |
| N4 | `inovacao_detail.html:59` | link "Avançar para “<status atual>”" em vez do próximo | ✅ 4: `test_quem_pode_alterar_ve_o_link_de_avancar[em_teste|validada × autor|administrador]` |
| N5 | `inovacoes/views.py:130` | `etapas=StatusInovacao.choices[::-1]` (ordem invertida) | ✅ 5: `test_ciclo_de_vida_lista_os_tres_estagios_em_ordem`, `test_ciclo_marca_so_o_estagio_atual…[3]`, `test_estagio_atual_e_identificavel_sem_css` |
| N6 | `inovacoes/views.py:224` | aviso de conflito com o valor cru (`VALIDADA`) em vez do rótulo | ✅ 5: `test_status_visto_ausente_ou_diferente…[3]`, `test_reenvio…`, `test_status_mudado_durante_o_envio…` |
| N7 | `inovacoes/views.py:244` | toda resposta do POST redireciona para a lista | ✅ 10: sucesso, estágio final, conflito e reenvio em `test_views_status.py` |
| N8 | `inovacoes/models.py:227` | `status_visto` ausente aceito (`is not None and …`) | ✅ 2: `test_status_visto_diferente_do_gravado…[None]`, `test_status_visto_ausente_ou_diferente…[None]` |
| N9 | `inovacoes/models.py:234` | sem `self.save(update_fields=["status"])`: o registro é criado e o status não muda | ✅ 9+: `test_avancar_status_avanca_um_estagio_e_registra[2]`, `test_avancar_grava_so_o_status`, `test_autor_avanca…[2]`, `test_administrador_avanca…`, `test_views_erro_500…[gravacao-do-status]` |
| N10 | `inovacao_status.html:11` | sem "Depois de avançar, não é possível voltar ao status anterior." | ✅ 3: `test_autor_ve_a_confirmacao…[2]`, `test_administrador_ve_a_confirmacao…` |
| N11 | `inovacao_status.html:3` | `<title>` com o título da inovação em vez de "Avançar status" | ✅ 5: as 3 de STAT-06 e `test_avancar_status_tem_um_unico_h1_e_title[avancar|ultimo_estagio]` |
| N12 | `templates/kira.css:523` | `.historico time { color: var(--bg) }` (texto da cor do fundo) | ✅ `test_ciclo_e_historico_so_usam_cores_de_pares_conferidos[.historico]` |
| N13 | `templates/kira.css:518` | `.ciclo [aria-current=step]` ganha `background: var(--brand-blue)` (navy sobre azul) | ✅ `test_ciclo_e_historico_so_usam_cores_de_pares_conferidos[.ciclo]` |
| **N14** | `templates/kira.css:521` | `.historico li` ganha `background: var(--brand-blue)`: texto `--text` herdado a 2,48:1 e `.historico time` (`--text-muted`) a 1,0:1 | ❌ **Survived**: 685 passed |
| N15 | `inovacao_detail.html:66` | `{% if mudancas|length > 1 %}` (off-by-one: um registro só mostra "Nenhuma mudança…") | ✅ 4: `…_no_fuso_de_sao_paulo`, `test_terceiro_ve_o_historico`, `…_so_as_mudancas_da_inovacao_aberta`, `test_secoes_do_detalhe…[historico]` |

**Sensor depth**: expandido (integridade de transição de estado, autorização e acessibilidade): 2 re-injeções e 15 mutações novas, cobrindo o texto e a ordem do histórico, o rótulo do link, a ordem dos estágios, as mensagens, o redirect, o status visto ausente, a gravação do status, o texto e o título da confirmação, o off-by-one do histórico vazio e o contraste.
**Result**: 16/17 mortas, 1 sobrevivente (N14) - FAIL ❌

### Gate Check (iteração 2)

- **Gate command**: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q` (árvore real, HEAD `ef25406`)
- **Result**: exit 0. `ruff check`: All checks passed · `ruff format --check`: 110 files already formatted · `makemigrations --check`: No changes detected · `pytest -q`: 685 passed, 0 failed, 0 skipped (16.0 s)
- **Test count**: 574 antes da feature → 684 na iteração 1 → 685 agora (+1, T12; a T13 reescreveu um teste parametrizado existente). Nenhum teste removido; nenhuma asserção enfraquecida (ver *Reconferência das correções*)

### Spec-Precision Gaps (iteração 2): julgamento do `<title>`

**STAT-06 / STAT-34, `<title>` "reading 'Avançar status'"**: a página renderiza `Avançar status · Repositório de Inovações`, porque `templates/base.html:6` acrescenta o sufixo do site a toda página, e os testes conferem o prefixo (`test_views_status.py:50`, `test_views_acessibilidade_alteracao.py:278`). **Julgamento: spec-precision gap de redação, não GAP de implementação. Não bloqueia.** O sufixo é convenção global do layout, anterior à F5 e vigente na F1–F4. A AC da F4 equivalente (EDEX-43, "a `<title>` that name the page") aceitou o mesmo formato. O que a AC protege (WCAG 2.4.2: o título identifica a página, e o `h1` é único) está afirmado: o `h1` exato em `:51`/`:276` e o nome da página no começo do `<title>`. A N11, que troca o nome da página, morre. Limite conhecido: um sufixo inesperado depois de "Avançar status" passaria pelo prefixo. Sugestão para a próxima revisão da spec, sem editar as ACs agora: "a `<title>` that begins with 'Avançar status'", ou afirmar nos testes o título renderizado completo. Lição L-021 (candidate) mantida.

### Fix Plans (iteração 2)

#### Fix 3: STAT-37 não confere o texto herdado sob uma regra que só declara fundo (N14) — Minor

- **Root cause**: `test_ciclo_e_historico_so_usam_cores_de_pares_conferidos` (`test_views_sistema_design.py:564-585`) só monta o par `(texto, fundo)` quando a regra declara `color` (`:577-578`, `continue`). Uma regra de `.ciclo`/`.historico` que declara `background` sem `color` passa só porque o fundo é um fundo de algum par (`:576`). O texto herdado (`--text` do `body`) e os descendentes com `color` (`.historico time`, `.ciclo li + li::before`, `.ciclo [aria-current=step]`) continuam conferidos contra o fundo fixo de `FUNDO_HERDADO`, não contra o novo.
- **Fix task**: no mesmo teste, toda regra de `.ciclo`/`.historico` que declara `background*` precisa ter o par do texto que fica sobre ela em `PARES_DE_TEXTO`. Usar o `color` da própria regra ou, sem ele, o texto herdado `text` (o `color` do `body`, `kira.css:72`). Além disso, o fundo de cada entrada de `FUNDO_HERDADO` deve ser conferido contra o `background` real da regra ancestral (`.ciclo li` para o `::before` e o estágio atual; `.historico li`, se declarar fundo, e senão `bg` para o `.historico time`). Uma alternativa mais simples e aceitável: exigir que toda regra com `background*` declare também `color`, e derivar `FUNDO_HERDADO` do ancestral em vez de fixá-lo.
- **Verify**: num scratch, com N14 (`.historico li { …; background: var(--brand-blue); }`) o teste falha; com N14 trocado por `background: var(--surface)` (par do DS-08) ele passa; no HEAD passa; M27, N12 e N13 continuam mortas.
- **Done when**: N14 morta; gate de build verde; nenhum código de produção alterado.
- **Priority**: Minor (o CSS atual cumpre o DS-08; o risco é regressão futura não detectada na mesma classe da M27)

### Requirement Traceability Update (iteração 2)

Não aplicada (FAIL). Proposta para a iteração 3:

| Requirement | Previous Status | New Status |
| ----------- | --------------- | ---------- |
| STAT-01 … STAT-36 | Implementing | ✅ Verified (evidência acima; STAT-24 fechada pela T12) |
| STAT-37 | Implementing | ❌ Needs Fix (Fix 3) |

### Histórico (continuação)

- **Iteração 2** (HEAD `ef25406`): FAIL ❌. 36/37 ACs; 16/17 mutantes mortos. M11 e M27 agora morrem. Sobreviveu N14 (fundo sem `color` no histórico, mesma classe da M27), que vira Fix 3, só em teste. Restam 1 iteração de correção e re-verificação antes de escalar ao usuário (limite de 3).

### Summary (iteração 2)

**Overall**: ❌ Not Ready (evidência da lacuna: `templates/kira.css:521` sob N14 com 685 passed; `inovacoes/tests/test_views_sistema_design.py:577-578` pula regras sem `color`)

**Spec-anchored check**: 36/37 ACs com o valor da spec afirmado e discriminante; 1 spec-precision gap de redação (título, não bloqueia)
**Sensor**: 16/17 mortas (sobrevivente: N14)
**Gate**: 685 passed, 0 failed
**validate_state.py**: `python3 .claude/skills/tlc-spec-driven/scripts/validate_state.py ciclo-de-vida-status` → exit 1, "validation.md verdict is FAIL - route the ranked gaps to fix tasks, then re-verify (feature is not done)". É o resultado esperado para um FAIL.

**What works**: tudo o que a iteração 1 já provava continua provado, e as correções fecham a STAT-24 (histórico só da inovação aberta, com o vazio ao lado de inovações com histórico) e o caso "texto com `color` sobre fundo da mesma regra" da STAT-37.

**Issues found**: Fix 3 (STAT-37, N14), só de teste.

**Lessons**: L-020 (candidate) recorreu nesta feature com a N14, e o `lessons.py add` acrescentou a evidência; L-019 não recorreu (M11 morta); L-021 continua (o título segue como spec-precision gap), e o `lessons.py add` acrescentou a evidência. Nenhuma lição nova; nenhuma promovida, porque a recorrência é na mesma feature.

**Next steps**: o orquestrador encaminha o Fix 3 a um implementador, que só mexe em teste, e depois despacha a iteração 3 do Verifier (a última antes de escalar).
