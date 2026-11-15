# Mapa de Features — Sistema de Repositório de Inovações de Back Office

Quebra do MVP em features (fatias verticais) para o fluxo Specify → Design → Tasks → Execute.
Cada feature reúne os RF/RN/RNF que a concretizam. A ordem segue a dependência: cada feature só
começa quando as anteriores existem.

**Escopo (auto-sizing):** Large = model + view(s) + template(s) + testes, roda o fluxo completo.
Medium = uma operação clara, pula Design/Tasks e implementa inline. Cross-cutting = não é uma
feature isolada; aplica-se em várias.

---

## Ordem de construção

```
F1 autenticacao  →  F2 cadastro-inovacao  →  F3 consulta-inovacoes
                                          →  F4 edicao-exclusao
                                          →  F5 ciclo-de-vida-status  →  F6 reaproveitamento-indicadores
```

| ID | Feature | Escopo | MoSCoW | Depende de | Situação (2026-10-27) |
| -- | ------- | ------ | ------ | ---------- | --------------------- |
| F1 | autenticacao | Large | Essencial | — | Concluída (Verifier PASS) |
| F2 | cadastro-inovacao | Large | Essencial | F1 | Concluída (Verifier PASS) |
| F3 | consulta-inovacoes | Large | Essencial | F2 | Concluída (Verifier PASS); CONS-44/45 substituídas pelo acervo-realista |
| F4 | edicao-exclusao | Large | Essencial (RF07) / Importante (RF08) | F1, F2 | Concluída (Verifier PASS) |
| F5 | ciclo-de-vida-status | Large | Importante | F2 | Concluída com risco de teste aceito; conferência do controle novo no navegador pendente |
| F6 | reaproveitamento-indicadores | Large | Desejável | F3, F5 | Concluída com risco de teste aceito; conferência no navegador pendente |

### Passes e features além do plano original

| Feature | O que entregou | Situação (2026-10-27) |
| ------- | -------------- | --------------------- |
| sistema-de-design | Template base único e folha `kira.css` a partir da `design-spec.md` (AD-010) | Concluída (Verifier PASS) |
| deploy-producao | RNF06: publicação na Vercel (CLI, Python 3.13) com PostgreSQL no Neon (plano gratuito, São Paulo); roteiro em `docs/roteiro-deploy.md` | **Concluída** em 2026-11-15: publicada em `https://kira-nu-green.vercel.app` com o banco no Neon (reaberta em 2026-11-09 para a troca); UAT da Parte 4 aprovada, acervo de 500 inovações carregado |
| acervo-realista | Carga de demonstração com 500 inovações plausíveis, 15 autores, histórico e reaproveitamentos | Concluída (Verifier PASS); carga no banco de produção (Neon) pendente |

---

## F1 — autenticacao

Fundação. Sem ela nenhuma outra feature roda, porque autor e perfil vêm daqui.

- **RF:** RF01 (login/logout)
- **RN:** RN04 (só autenticados cadastram/editam/excluem; consulta por qualquer autenticado), RN11 (perfil de admin só é atribuído por outro admin)
- **RNF:** RNF02 (senha em hash, LGPD, sessão do Django), RNF07 (base da autorização por perfil)
- **Descrição:** login por usuário/e-mail e senha; sessão gerenciada pelo Django; modelo de usuário com campo de perfil enum (USUARIO / ADMINISTRADOR).
- **Notas:** no MVP, o primeiro admin nasce como superuser via `createsuperuser`; RN11 se materializa restringindo a troca de perfil ao admin (Django admin resolve isso sem tela própria). Aplica AD-001 e AD-004.

## F2 — cadastro-inovacao

Coração do sistema: o fluxo problema → solução → resultado → unidade.

- **RF:** RF02 (cadastro por formulário), RF12 (feedback de ações), RF13 (validação e recuperação de erros), RF14 (cancelar sem salvar)
- **RN:** RN01 (uma unidade + uma categoria), RN02 (campos obrigatórios), RN03 (status inicial "Em teste"), RN07 (listas controladas), RN08 (autor e data automáticos), RN10 (título único por unidade)
- **RNF:** RNF05 (persistência PostgreSQL), RNF01 (usabilidade), RNF09 (acessibilidade do formulário: rótulos, teclado, foco visível)
- **Descrição:** formulário estruturado que grava a entidade Inovacao, define autor/data/status pelo sistema e valida campos antes de persistir.
- **Notas:** **RF12 e RF13 devem ser construídos aqui, junto do CRUD** — não deixe para depois, senão vira retrabalho. É o lembrete que já tinha surgido na revisão da ordem de features.

## F3 — consulta-inovacoes

O outro lado do valor: encontrar antes de resolver do zero.

- **RF:** RF03 (listagem), RF04 (visualização detalhada), RF05 (busca por palavra-chave), RF06 (filtros combinados)
- **RN:** RN06 (detalhe exibe o contato responsável), RN07 (listas controladas alimentam os filtros)
- **RNF:** RNF08 (busca/listagem ≤ 2 s no conjunto de demonstração), RNF01, RNF09
- **Descrição:** lista resumida, página de detalhe completa, busca textual em título/problema/solução e filtros por categoria, unidade e status, isolados ou combinados.
- **Notas:** se ficar grande demais, divida em duas: `consulta-listagem-detalhe` (RF03, RF04) e `busca-filtros` (RF05, RF06). RF15 (ajuda contextual) entra nos filtros aqui.

## F4 — edicao-exclusao

Onde a política de permissões vira comportamento observável.

- **RF:** RF07 (edição), RF08 (exclusão com confirmação), RF14 (confirmar/cancelar)
- **RN:** RN05 (autor edita/exclui só o próprio; admin, qualquer um), RN12 (confirmação explícita antes de ação destrutiva)
- **RNF:** RNF07 (restrição de edição/exclusão por perfil)
- **Descrição:** telas de edição e exclusão que respeitam autoria; exclusão pede confirmação explícita.
- **Notas:** é a feature que mais depende de teste de autorização — vale caprichar nos casos "usuário comum tenta editar registro de terceiro".

## F5 — ciclo-de-vida-status

- **RF:** RF09 (gestão de status)
- **RN:** RN03 (transição Em teste → Validada → Disponível para replicação)
- **Descrição:** operação que avança o status da inovação ao longo do ciclo.
- **Notas:** Reclassificada de Medium para Large no Specify (2026-10-18): o histórico de mudanças acrescenta modelo, migration e tela de confirmação; roda Design e Tasks formais. Conforma com AD-009 e AD-010.

## F6 — reaproveitamento-indicadores

Fecha o eixo "Dados, Inteligência e Infra" do ENADE.

- **RF:** RF11 (sinalização de reuso), RF10 (painel de indicadores)
- **RN:** RN09 (só inovação "Disponível para replicação" pode ser sinalizada; alimenta a métrica)
- **RNF:** RNF08
- **Descrição:** botão de "reaproveitei esta inovação" registrando a entidade Reaproveitamento, e um dashboard com total, distribuição por categoria/unidade e contagem de reusos.
- **Notas:** Desejável. Se o prazo apertar, entregue RF11 + um dashboard mínimo e trate RF10 completo como incremento. (A reclassificação de RF10 Desejável→Importante continua sendo sua decisão em aberto; se subir para Importante, esta feature sai de "corta primeiro".)
- **Andamento (2026-10-19):** RF11 e RF10 completos (painel com cards, gráficos SVG e tabelas, app `indicadores`). Decisões: unidade escolhida no formulário, uma sinalização por unidade, qualquer usuário autenticado sinaliza; regra da RN09 em `Inovacao.registrar_reaproveitamento` (AD-012). Verifier FAIL nas 3 iterações só por lacunas de teste; o risco residual foi aceito e a feature fechada (`.specs/features/reaproveitamento-indicadores/validation.md`).

---

## Requisitos transversais (aplicam-se a várias features, não são feature única)

| Item | Onde se materializa | Quando validar |
| ---- | ------------------- | -------------- |
| RF15 — ajuda contextual | formulários (F2) e filtros (F3) | junto de cada feature |
| RNF01 — usabilidade / Nielsen / SUS ≥ 68 | toda a UI | avaliação heurística contínua; teste SUS isolado no fim |
| RNF03 — compatibilidade / responsivo (desktop, tablet) | toda a UI | passe dedicado de responsividade (semana 6 do cronograma) |
| RNF04 — manutenibilidade / modular | decorre do MVT | garantido por AD-002 |
| RNF06 — portabilidade / deploy | infraestrutura | fase final — **feito** (deploy-producao, 2026-10-27; banco no Neon em 2026-11-15) |
| RNF09 — acessibilidade (WCAG 2.1 AA, eMAG) | toda a UI | por feature + auditoria final |

---

## Decisões de projeto para o `.specs/STATE.md`

Estas entram como entradas `AD-NNN` no log de decisões. Toda feature conforma com elas; o Design
lê o log antes de decidir qualquer coisa. (Critério: difícil de reverter, surpreendente sem
contexto, fruto de um trade-off real.)

- **AD-001 — Autenticação por sessão nativa do Django.** Não JWT. Fecha de vez o resíduo de JWT dos artefatos antigos.
- **AD-002 — Arquitetura MVT sem Service Layer.** O ORM do Django cumpre o papel de repositório; camada de serviço foi avaliada como over-engineering para o MVP.
- **AD-003 — PostgreSQL 16 como persistência relacional.** Integridade referencial exigida pelo RNF05.
- **AD-004 — Perfil via campo enum no modelo de usuário do Django (USUARIO / ADMINISTRADOR).** Um único tipo de usuário com um campo que determina poderes, em vez de duas classes.

> A paleta teal é convenção de estilo, não AD: é fácil de reverter e não carrega trade-off — mantenha-a nos documentos, mas fora do log de decisões.

---

## Checagem de cobertura

Todos os RF, RN e RNF do documento de requisitos estão alocados. Nenhum órfão.

- **RF01–RF15:** RF01→F1 · RF02→F2 · RF03→F3 · RF04→F3 · RF05→F3 · RF06→F3 · RF07→F4 · RF08→F4 · RF09→F5 · RF10→F6 · RF11→F6 · RF12→F2 · RF13→F2 · RF14→F2+F4 · RF15→transversal (F2/F3)
- **RN01–RN12:** RN01→F2 · RN02→F2 · RN03→F2+F5 · RN04→F1 · RN05→F4 · RN06→F3 · RN07→F2+F3 · RN08→F2 · RN09→F6 · RN10→F2 · RN11→F1 · RN12→F4
- **RNF01–RNF09:** RNF01→transversal · RNF02→F1 · RNF03→transversal · RNF04→AD-002 · RNF05→F2 · RNF06→transversal · RNF07→F1+F4 · RNF08→F3+F6 · RNF09→transversal
