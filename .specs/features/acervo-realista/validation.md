# Acervo Realista Validation

**Date**: 2026-10-27
**Iteration**: 2 (a iteração 1 fica abaixo, intacta; a iteração 2 está em [Iteração 2](#iteração-2), no fim)
**Spec**: `.specs/features/acervo-realista/spec.md` (ACER-01 … ACER-22 + 3 Edge Cases). Supersede CONS-44/CONS-45.
**Diff range (iteração 2)**: `a6aaaa8..63410d5` em `main` (HEAD = `63410d5`). Correção: `63410d5`, em `spec.md`, `inovacoes/acervo.py` e `inovacoes/tests/test_carregar_demonstracao.py`. O comando não mudou.
**Diff range (iteração 1)**: `b4b3f79..a6aaaa8` em `main` (spec `b4b3f79`; implementação `1c97fba`, `fb798d8`, `e06039b`, `808653b`, `a6aaaa8`). 8 arquivos, +1846/−151. Produção: `inovacoes/acervo.py`, `inovacoes/management/commands/carregar_demonstracao.py`.
**Verifier**: independent sub-agent (author ≠ verifier)

**Verdict**: PASS ✅ na iteração 2 (HEAD `63410d5`), ver [Iteração 2](#iteração-2). M07, M15 e M18 agora morrem, e as 5 mutações novas também (8/8). A spec emendada (ACER-14 e ACER-16 com "before the command started", e a ACER-23 nova) tem as 23 ACs com o valor afirmado. Gate: 933 passed.

**Iteração 1 (registro original):** FAIL ❌ — o código de produção cumpre todas as ACs que conferi. O FAIL vem do sensor: 3 de 18 mutantes sobrevivem. O principal (M18) é uma carga que **não retroage** as datas do histórico de status nem dos reaproveitamentos. Todo `MudancaDeStatus.data` e todo `Reaproveitamento.data` ficam no minuto da carga, e a suíte inteira passa. É exatamente o sintoma do Problem Statement ("todas as datas são o minuto da carga"). ACER-14 e ACER-16 só exigem ordem e limite superior, então a lacuna é de precisão da spec, com teste correspondente. Os outros dois são M07 (só os reusos sem retroagir) e M15 (reuso registrado pelo próprio autor, regra que está só nas Assumptions, sem AC).

---

## Task Completion

Plano inline, sem `tasks.md` (a spec diz "22 mapeadas aos 5 passos do Execute"). Os 5 commits de implementação estão em `main`. O gate passa.

| Passo | Commit | Status |
| ----- | ------ | ------ |
| Testes de desempenho sem depender do conteúdo | `1c97fba` | ✅ |
| Acervo realista (catálogo + montagem) | `fb798d8` | ✅ |
| Datas, histórico e reusos | `e06039b` | ✅ |
| Idempotência com histórico e reusos | `808653b` | ✅ |
| Roteiro de deploy e supersede CONS-44/45 | `a6aaaa8` | ✅ |

---

## Spec-Anchored Acceptance Criteria

Arquivo de teste abreviado: `T` = `inovacoes/tests/test_carregar_demonstracao.py`.

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| ACER-01 | 500 inovações, pares (título, unidade) únicos | `T:79` `len(pares) == TOTAL`; `T:80` `len(set(pares)) == TOTAL` | ✅ PASS |
| ACER-02 | ≥ 90 títulos; nenhum em > 5 | `T:86` `len(por_titulo) >= 90`; `T:87` `max(...) <= 5` | ✅ PASS |
| ACER-03 | 500 problemas e 500 soluções distintos | `T:92`, `T:93` `...distinct().count() == TOTAL` | ✅ PASS |
| ACER-04 | nenhum dos 5 termos nos 5 campos, sem acento/caixa | `T:31-32` (termos e campos da spec); `T:103` `vetada in normalizar(...)`; `T:105` `achados == []` | ✅ PASS |
| ACER-05 | `resultado` não vazio em Validada e Disponível | `T:110-112` `exclude(EM_TESTE)` … `== []` | ✅ PASS |
| ACER-06 | "<setor>, <unidade da própria inovação> — ramal <4 dígitos>" | `T:118-119` `re.fullmatch(rf"[^,]+, {unidade} — ramal \d{4}", contato)` | ✅ PASS |
| ACER-07 | cada unidade, categoria e status em ≥ 20 | `T:127-132` conjuntos completos + `min(...) >= 20` | ✅ PASS |
| ACER-08 | "conciliacao" = "conciliação", não vazio | `T:138` `assert com_acento`; `T:139` igualdade de conjuntos | ✅ PASS |
| ACER-09 | 15 contas, nome e sobrenome, USUARIO, sem senha, `@acervo.invalid`, todas com inovação | `T:152` `len(autores) == 15` (autores com inovação); `T:154-157`; `T:158` `count() == 15` | ✅ PASS |
| ACER-10 | conta `demo` nem criada nem usada | `T:163`, `T:164` | ✅ PASS |
| ACER-11 | detalhe mostra "Cadastrada por <nome completo>" | `T:172` `f"Cadastrada por {get_full_name()} em" in exibido(html)`; `T:173` nome = first + last | ✅ PASS |
| ACER-12 | `data_criacao` em [execução − 540 d, execução]; ≥ 12 meses | `T:199` `antes - 540d <= d <= depois`; `T:201` `len(meses) >= 12` | ✅ PASS |
| ACER-13 | Validada: 1 mudança; Disponível: 2, na ordem; Em teste: 0 | `T:206-216` lista exata de transições por status | ✅ PASS |
| ACER-14 | por `avancar_status`, responsável = autor, depois da criação e da anterior, até a execução | `T:223` `avancar.call_count == MudancaDeStatus.count()`; `T:228` `responsavel_id == autor_id`; `T:229` `anterior < data <= agora` | ⚠️ Spec-precision gap (ver G1) |
| ACER-15 | ≥ 60 reusos pelo método, só em Disponível, fora da origem, ≥ 30 inovações | `T:237` `>= 60`; `T:238` `registrar.call_count == count()`; `T:240-241`; `T:242` `>= 30` | ⚠️ Spec-precision gap (ver G2) |
| ACER-16 | reuso depois da mudança para Disponível e até a execução | `T:252` `disponivel.data < reuso.data <= depois` | ⚠️ Spec-precision gap (ver G1) |
| ACER-17 | 2ª execução: "0 … (500 no total)."; 500 inovações, 15 contas, mesmas contagens | `T:284` mensagem exata; `T:285` `_contagens() == antes`; `T:286` `antes[:2] == (500, 15)` | ✅ PASS |
| ACER-18 | apagar 2 → "2 … (500 no total)."; recriadas iguais (9 campos + autor), com histórico e reusos | `T:301` mensagem exata; `T:302` contagens; `T:305` `_retrato(recriada) == retrato` (`T:264-278`: os 9 campos, transições e pares de reuso); `T:306` uma delas tem reuso | ✅ PASS |
| ACER-19 | "N inovações de demonstração criadas (500 no total)." | `T:180` mensagem exata com N = 500; `T:284` N = 0; `T:301` N = 2 | ✅ PASS |
| ACER-20 | < 5 unidades ou categorias → CommandError; nada criado | `T:184-192` parametrizado; `pytest.raises(CommandError)`; `Inovacao.count() == 0`; `Usuario.count() == contas_antes` | ✅ PASS |
| ACER-21 | CONS-46/47/48 continuam valendo, termos do conteúdo carregado | `inovacoes/tests/test_desempenho.py:46-47` "500 inovações encontradas" e `< 2 s`; `:59-95` termos tirados de `alvo.problema`, esperado calculado sem `buscar()`, `:89` `< 2 s`, `:91` títulos exatos; `:118-119` contagem de consultas igual | ✅ PASS |
| ACER-22 | REAP-41 (< 2 s) e REAP-42 (consultas constantes) com 500 + 200 reusos a mais | `indicadores/tests/test_desempenho_painel.py:73-87` card = total do banco, `< 2 s`; `:121-124` "501", card = contagem, `len(grande) == len(pequeno)` | ✅ PASS |

**Status**: 19/22 com o valor da spec afirmado; 3 com ⚠️ spec-precision gap.

### Os testes de desempenho alterados (autorização da Code Reuse Analysis)

- CONS-46 (`test_desempenho.py:46-47`) e CONS-48 (`:106-119`): sem mudança de asserção nem de limite.
- CONS-47: troca o `VOCABULARIO` e o "Demonstração NNN" por duas palavras do problema da primeira "Validada". O esperado continua calculado à parte (`:69-75`), a lista é comparada exata (`:91`) e o trio de filtros também (`:92-94`). O limite de 2 s não mudou. Não enfraqueceu.
- REAP-41: antes afirmava o card "200" exato. Agora afirma `str(total)`, com `total` = reusos da carga + 200 (`:74`, `:82`, `:86`). Continua exato e cruzado com o banco. O limite não mudou.
- REAP-42: antes "201" exato. Agora o card = `Reaproveitamento.count()` e `>= 201` (`:122-123`). Um pouco menos rígido no valor, mas o que a REAP-42 mede (`len(grande) == len(pequeno)`, `:124`) ficou intacto. Aceitável.

---

## Discrimination Sensor

Scratch: `git worktree` em `<scratchpad>/wt` no HEAD `a6aaaa8`. Testes rodados com o `.venv/bin/pytest` do repositório, de dentro do worktree, sem `DATABASE_URL`, contra o Postgres local (5433). Confirmado que `inovacoes.acervo.__file__` resolvia para o worktree, e a execução sem mutante deu 27 passed. Escopo: `T`, `inovacoes/tests/test_desempenho.py`, `indicadores/tests/test_desempenho_painel.py`.

| # | File:line | Mutação | Killed? |
| - | --------- | ------- | ------- |
| M01 | `inovacoes/acervo.py:69` | "por exemplo" numa solução | ✅ Killed (ACER-04) |
| M02 | `carregar_demonstracao.py:48` | sem o pulo da idempotência (`if False`) | ✅ Killed (ACER-17, ACER-18) |
| M03 | `carregar_demonstracao.py:58,69` | nasce no status final; `MudancaDeStatus.objects.create` direto | ✅ Killed (ACER-14, espião) |
| M04 | `carregar_demonstracao.py:73` | `Reaproveitamento.objects.create` direto | ✅ Killed (ACER-15, espião) |
| M05 | `carregar_demonstracao.py:67` | sem retroagir `data_criacao` | ✅ Killed (ACER-12, ACER-14) |
| M06 | `carregar_demonstracao.py:70` | sem retroagir `MudancaDeStatus.data` | ✅ Killed (ACER-16, por tabela: o reuso retroagido fica antes da mudança) |
| M07 | `carregar_demonstracao.py:74` | sem retroagir `Reaproveitamento.data` | ❌ Survived |
| M08 | `inovacoes/acervo.py:1438` | reuso pode cair na unidade de origem | ✅ Killed (o guarda do modelo, AD-012, levanta ValidationError) |
| M09 | `carregar_demonstracao.py:69` | responsável da mudança = outro autor | ✅ Killed (ACER-14) |
| M10 | `inovacoes/acervo.py:1407` | contato com a unidade seguinte | ✅ Killed (ACER-06) |
| M11 | `inovacoes/acervo.py:1408` | todos os registros com um único autor | ✅ Killed (ACER-09) |
| M12 | `inovacoes/acervo.py:1416` | janela de 900 dias | ✅ Killed (ACER-12) |
| M13 | `inovacoes/acervo.py:1397` | `resultado` vazio nas Validadas | ✅ Killed (ACER-05) |
| M14 | `inovacoes/acervo.py:1437` | chance de reuso 0,5 → 0,1 | ✅ Killed (ACER-15) |
| M15 | `inovacoes/acervo.py:1441` | reuso registrado pelo próprio autor da inovação | ❌ Survived |
| M16 | `inovacoes/acervo.py:1434` | mudanças depois de `agora` | ✅ Killed (ACER-13, ACER-14) |
| M17 | `carregar_demonstracao.py:42` | apaga as inovações de outros autores antes de carregar | ✅ Killed (`indicadores/tests/test_desempenho_painel.py:121`, por tabela) |
| M18 | `carregar_demonstracao.py:70,74` | M06 + M07: histórico e reusos ficam no minuto da carga | ❌ Survived |

**Sensor depth**: expandido (18 mutantes; a carga roda à mão no banco publicado).
**Isolamento**: worktree removido (`git worktree remove --force`, `git worktree prune`; `git worktree list` só mostra o principal). O baseline do `git status --porcelain` era vazio. Depois, apareceu ` M .gitignore` (+`.vercel`, +`.env*`, mtime 16:07). Não é do sensor: as mutações só tocaram `inovacoes/acervo.py` e o comando dentro do worktree, nenhuma toca `.gitignore`, e o conteúdo é o que `vercel link` acrescenta. Foi alteração externa e concorrente na árvore real. Não mexi nela.
**Resultado (iteração 1)**: 15/18 killed — FAIL ❌

---

## Code Quality

| Principle | Status |
| --------- | ------ |
| Minimum code | ✅ `montar_registros` e `linha_do_tempo` são puras; o comando só grava |
| Surgical changes | ✅ só os arquivos da Code Reuse Analysis |
| No scope creep | ✅ |
| Matches patterns | ✅ `save()` um a um (AD-008), `avancar_status` (AD-011), `registrar_reaproveitamento` (AD-012), datas por `update()` fora da busca |
| Spec-anchored outcome check | ⚠️ G1/G2 |
| Per-layer Coverage Expectation | ✅ integração sobre o banco para cada AC; ACER-11 pela tela, com `exibido` (L-028, L-030) |
| Every test maps to a spec requirement | ✅ `T:142-146` mapeia AD-008 (decisão do projeto) |
| Documented guidelines followed | ✅ `.specs/LESSONS.md` (L-005, L-028, L-030) |

Observação menor: `_conferir_catalogo()` roda no import do módulo. É uma guarda de catálogo barata e determinística. Aceitável.

---

## Edge Cases

- [x] Inovação apagada com histórico e reusos é recriada na próxima execução: `T:289-306`.
- [~] Inovações de outros autores ficam intocadas: sem teste dedicado. Coberto por tabela em `indicadores/tests/test_desempenho_painel.py:99-121` (uma inovação de outro autor, depois a carga, depois o card "501"); M17 morre aí. O subcaso "a menos que o par coincida" não tem teste. Advisory (G3).
- [x] Qualquer data de calendário: as datas são relativas a `timezone.now()` (`T:199`, `T:229`, `T:252`). Mas veja G1: hoje "dentro da janela" também aceita datas no minuto da carga.

---

## Gate Check

- **Gate command**: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q` (sem `DATABASE_URL`)
- **Resultado (iteração 1)**: 932 passed, 0 failed, 0 skipped (30,09 s). Ruff ok, format ok, sem migração pendente.
- **Test count before feature**: 919 (o arquivo antigo tinha 9 itens; o novo tem 22; os de desempenho mantêm a contagem)
- **Test count after feature**: 932
- **Delta**: +13
- **Skipped tests**: nenhum
- **Failures**: nenhuma

---

## Fix Plans

### G1 (Major): datas do histórico e dos reusos sem retroagir passam (M07, M18) — ACER-14, ACER-16

- **Root cause**: ACER-14 e ACER-16 só pedem ordem (`> criação`, `> anterior`, `> mudança para Disponível`) e limite superior (`<= execução`). Datas no minuto da carga cumprem as duas coisas. O objetivo da spec ("datas espalhadas", "o painel e o detalhe pareçam de um sistema em uso há meses") e a Code Reuse Analysis ("retroagidas por `QuerySet.update()`") pedem mais. O código atual já cumpre a intenção: `linha_do_tempo` põe cada data numa fração estrita do intervalo até `agora`, sempre dias antes.
- **Fix task**:
  1. Emenda na spec: em ACER-14 e ACER-16, "dated before the command started", ou um espalhamento mínimo (por exemplo, "spread over at least N distinct calendar months"). Para valer com uma carga cronometrada: datas `< antes`.
  2. Teste: em `T:229`, `mudanca.data < antes` (fixture `carga_cronometrada` ou equivalente com o espião); em `T:252`, `reuso.data < antes`; ou contar os meses distintos de `MudancaDeStatus.data` e de `Reaproveitamento.data`.
  3. Verify: M07 e M18 morrem.
- **Priority**: Major (é o sintoma do Problem Statement, visível no histórico do detalhe).

### G2 (Minor): quem registra o reuso não tem AC (M15) — ACER-15

- **Root cause**: "Um autor do acervo diferente do autor da inovação" está só em Assumptions. Nenhuma AC nem teste o exige. O código cumpre: `autores_da_unidade(u)` da unidade de destino é disjunto do da origem com 5 unidades × 3 autores.
- **Fix task**: decidir se vira AC (acrescentar a ACER-15 "registered by an acervo author other than the Inovacao's author" e afirmar `reuso.registrado_por_id != reuso.inovacao.autor_id` em `T:239-241`) ou se fica como premissa não verificada.
- **Priority**: Minor.

### G3 (Advisory): edge case "outros autores intocados" só por tabela

- Um teste dedicado em `T` (criar uma inovação de outro autor, carregar, conferir que ela está igual e que há 501) deixaria a garantia fora dos testes de desempenho. Não bloqueia.

---

## Realism spot-check (advisory, não é AC)

16 registros sorteados de `montar_registros([...5 unidades...])`, mais uma varredura dos 123 casos. As frases leem bem, e a preposição antes da ferramenta não quebra a concordância ("em Power Automate", "por SharePoint"). Observações não bloqueantes:

1. **Percentual de cobertura com `{pct}` em 18–78%**: em resultados que descrevem um nível alcançado, valores baixos soam como fracasso. Exemplos: "Inventário automático de equipamentos" ("O inventário passou a refletir 46% do parque real"); "Cotação padronizada com três fornecedores" ("As compras auditadas sem pendência passaram a {pct}%"); "Liberação de acessos para novos colaboradores" ("prontos no primeiro dia em {pct}% das admissões"); "Pesquisa de satisfação dos atendimentos internos" ("chegou a {pct}% de avaliações positivas"); "Trilha de integração" ("subiu para {pct}%"); "Controle de treinamentos obrigatórios"; "Registro de achados e perdidos". Sugestão: um campo próprio (por exemplo 80–98) para "nível atingido".
2. **Economia alta demais**: "Negociação anual consolidada" ("economia média … de 78%"); "Calendário de renovação de contratos" ("redução média de 54%"); "Controle de licenças de software" ("economia de {pct}% no contrato"); "Migração dos ramais para telefonia IP" ("A conta de telefonia caiu 72%").
3. **Ferramenta que não combina com a ação**: o sorteio põe "Microsoft Forms" ou "Google Sheets" onde se espera publicação ou mural. Exemplos: "Guia de procedimentos internos" ("publicado em Microsoft Forms"); "Calendário de renovação de contratos" ("reunião … registrada em Microsoft Forms"); "Planejamento anual de férias" ("em Microsoft Forms, com alerta ao gestor"); "Aviso de interrupções programadas" ("enviado por Smartsheet"); "Emissão de notas de serviço em lote" ("conferência por Google Workspace").
4. **Gramática**: "Planejamento anual de férias": "Nenhuma férias venceu" (melhor "Nenhum período de férias venceu"). "Aviso de interrupções programadas": "Falta de energia, água ou internet programadas pegavam" (concordância; melhor "Faltas … programadas pegavam").

---

## Requirement Traceability Update

| Requirement | Previous Status | New Status |
| ----------- | --------------- | ---------- |
| ACER-01 … ACER-13 | Implementing | ✅ Verified |
| ACER-14 | Implementing | ⚠️ Needs spec precision (G1) |
| ACER-15 | Implementing | ✅ Verified (G2 é premissa sem AC) |
| ACER-16 | Implementing | ⚠️ Needs spec precision (G1) |
| ACER-17 … ACER-22 | Implementing | ✅ Verified |

(Verifier não edita `spec.md`; o orquestrador atualiza.)

---

## Summary

**Overall**: ❌ Not Ready (só lacunas de spec e de teste; nenhum defeito de produção)

**Spec-anchored check**: 19/22 com o valor da spec afirmado; 3 spec-precision gaps (ACER-14, ACER-15, ACER-16)
**Sensor**: 15/18 killed (M07, M15, M18 sobrevivem)
**Gate**: 932 passed

**What works**: 500 registros únicos e variados, sem palavra vetada; contato da própria unidade; 15 autores colaboradores sem senha; histórico pelo `avancar_status` do autor; reusos pelo `registrar_reaproveitamento`, fora da origem; idempotência e recriação idêntica; CommandError sem gravar; RNF08 mantido.

**Issues found**: G1 (Major): precisar ACER-14/16 e afirmar datas antes da execução. G2 (Minor): decidir se "quem registra o reuso" vira AC. G3 (Advisory): teste dedicado para "outros autores intocados".

**Next steps**: emenda de spec e fix task só de teste para G1 (e G2, se aceito); re-verificar M07, M15, M18.

---

## Iteração 2

**Date**: 2026-10-27
**HEAD**: `63410d5` (validação 1 commitada em `25246b9`; o `.gitignore` do `vercel link` foi commitado à parte em `fea5a7b`)

### O que mudou

- **Spec**: ACER-14 e ACER-16 exigem "before the command started". A ACER-23 nova exige que todo Reaproveitamento seja registrado por uma das 15 contas de autor, diferente do autor da inovação. A emenda está registrada nas Assumptions e na traceability.
- **Testes**: `carga_espionada` devolve `antes` (`T:57`, `T:70`). ACER-14 afirma `anterior < mudanca.data < antes` (`T:229`). ACER-16 afirma `disponivel.data < reuso.data < antes` (`T:252`). Teste novo para a ACER-23 (`T:255-262`).
- **Catálogo** (`inovacoes/acervo.py`): slots `{nivel}` (82–98) e `{economia}` (6–24); `FERRAMENTAS` (depois de "por"/"com") separadas de `PLATAFORMAS` (depois de "em"); sem Microsoft Forms nem Smartsheet; as duas concordâncias corrigidas.
- **Comando**: sem mudança.

### Spec-anchored (ACs que mudaram ou são novas)

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| ACER-14 | por `avancar_status`, responsável = autor, depois da criação e da anterior, **antes do início da execução** | `T:57` `antes = timezone.now()` antes de `_carregar()`; `T:224` `avancar.call_count == MudancaDeStatus.count()`; `T:228` `responsavel_id == autor_id`; `T:229` `anterior < mudanca.data < antes` | ✅ PASS |
| ACER-16 | depois da mudança para Disponível e **antes do início da execução** | `T:49` `antes` antes da carga; `T:252` `disponivel.data < reuso.data < antes` | ✅ PASS |
| ACER-23 | todo reuso registrado por uma das 15 contas de autor, diferente do autor da inovação | `T:257` `autores` = contas com inovação (= as 15 da ACER-09, `T:152`); `T:259` `reusos.exists()`; `T:261` `registrado_por_id in autores`; `T:262` `registrado_por_id != inovacao.autor_id` | ✅ PASS |

As outras 20 ACs não mudaram; as evidências da iteração 1 continuam valendo (o gate passa com os mesmos testes). **Status**: 23/23.

### Discrimination Sensor (iteração 2)

Scratch: novo `git worktree` no HEAD `63410d5`. Mesmo runner, sem `DATABASE_URL`, Postgres local 5433. Escopo: `T`, `inovacoes/tests/test_desempenho.py`, `indicadores/tests/test_desempenho_painel.py` (28 testes).

| # | File:line | Mutação | Killed? |
| - | --------- | ------- | ------- |
| M07 | `carregar_demonstracao.py:74` | sem retroagir `Reaproveitamento.data` | ✅ Killed (`T:252`) |
| M15 | `inovacoes/acervo.py` `linha_do_tempo` | reuso registrado pelo próprio autor | ✅ Killed (`T:262`) |
| M18 | `carregar_demonstracao.py:70,74` | histórico e reusos no minuto da carga | ✅ Killed (`T:229`, `T:252`) |
| M19 | `inovacoes/acervo.py` `JANELA_EM_DIAS` | janela de 560 dias (cadastros até 559 dias antes) | ✅ Killed (`T:199`) |
| M20 | `carregar_demonstracao.py:73` | reuso registrado por uma conta "externo" fora do acervo | ✅ Killed (`T:261`) |
| M21 | `inovacoes/acervo.py` `linha_do_tempo` | reuso na mesma data da mudança para Disponível | ✅ Killed (`T:252`) |
| M22 | `inovacoes/acervo.py` `linha_do_tempo` | reuso depois de `agora` (fração 1,01–1,1) | ✅ Killed (`T:252`) |
| M23 | `inovacoes/acervo.py` `linha_do_tempo` | mudança na mesma data da anterior (fração 0) | ✅ Killed (`T:229`) |

**Isolamento**: baseline do `git status --porcelain` vazio antes do sensor. Worktree removido (`git worktree remove --force`, `git worktree prune`; `git worktree list` só mostra o principal). Porcelain igual ao baseline depois.
**Result**: 8/8 killed — PASS ✅

### Gate Check (iteração 2)

- **Gate command**: o mesmo da iteração 1, sem `DATABASE_URL`.
- **Resultado (iteração 2)**: 933 passed, 0 failed, 0 skipped (32,96 s). Ruff ok, format ok (147 arquivos), sem migração pendente.
- **Delta sobre a iteração 1**: +1 (teste da ACER-23). Nenhuma asserção enfraquecida: `<= agora`/`<= depois` viraram `< antes`, que é mais estrito.

### Edge Cases (iteração 2)

- Sem mudança. G3 (outros autores intocados, só por tabela em `indicadores/tests/test_desempenho_painel.py:121`) continua advisory e não bloqueia.

### Realism spot-check (iteração 2, advisory)

15 registros sorteados (semente diferente da iteração 1), mais a varredura dos 123 casos. As observações da iteração 1 estão resolvidas: nível 82–98 ("refletir 94% do parque", "98% dos desvios"), economia 6–24 ("redução média de 9%/15%"), "em" + plataforma, sem Forms/Smartsheet, concordâncias corrigidas. Restam pontos menores, não bloqueantes:

1. "Histórico de preços por item" (`inovacoes/acervo.py:699`): "com alerta para alta acima de {pct}%" sai com 18–78% ("acima de 64%"). Um limiar de alerta de preço plausível fica perto de 5–15%.
2. "Reserva dos veículos da unidade" (`inovacoes/acervo.py:1182`): "A ocupação dos veículos subiu {pct}%" chega a 78%. É alto, mas possível.
3. "Arquivo digital de comprovantes": "{pct}% do arquivo físico foi descartado" com 18–78%. Plausível.
4. Ferramenta como agente: "Estoque mínimo com reposição automática" — "sugestão de compra gerada por Google Workspace". Uma suíte não "gera"; Power Automate, Apps Script ou Zapier combinam melhor. Acontece só quando o sorteio cai num item de suíte na lista `FERRAMENTAS`.

### Requirement Traceability Update (iteração 2)

| Requirement | Previous Status | New Status |
| ----------- | --------------- | ---------- |
| ACER-14 | ⚠️ Needs spec precision | ✅ Verified |
| ACER-16 | ⚠️ Needs spec precision | ✅ Verified |
| ACER-23 | (nova) | ✅ Verified |
| demais ACER-01 … ACER-22 | ✅ Verified | ✅ Verified |

### Summary (iteração 2)

**Overall**: ✅ Ready

**Spec-anchored check**: 23/23 ACs com o valor da spec afirmado.
**Sensor**: 8/8 killed (M07, M15, M18 re-injetados + 5 novos).
**Gate**: 933 passed.

**Pendências não bloqueantes**: G3 (teste dedicado para "outros autores intocados") e os 4 pontos de realismo acima.

---

## Depois do PASS (orquestrador, 2026-10-27)

Não é uma iteração do Verifier. As observações de realismo 1 e 4 da iteração 2 foram aplicadas
em `inovacoes/acervo.py`: "alerta para alta acima de {economia}%" (6 a 24%) e `FERRAMENTAS`
sem as suítes (Power Automate, Google Apps Script, Zapier, n8n, um script em Python). Só conteúdo:
nenhuma AC, teste ou regra muda. Gate depois da mudança: 933 passed; os 500 problemas e as 500
soluções seguem distintos. As observações 2 e 3 ficam como estão (plausíveis).

