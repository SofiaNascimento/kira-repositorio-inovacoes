# Gestão por Unidade Validation

**Date**: 2026-11-25
**Spec**: `.specs/features/gestao-por-unidade/spec.md`
**Diff range**: `8b02efe..dd8411f` (spec `8b02efe`, design `813489b`, tasks `b86eef4`, código `20c3504..807500d`, emenda E-4 `dd8411f`)
**Verifier**: não executado

**Verdict**: NÃO VERIFICADA — fechada com risco aceito pelo usuário

---

## O que aconteceu

O Verifier independente foi disparado em 2026-11-25 e interrompido a pedido do usuário poucos
minutos depois, antes de produzir qualquer resultado. O usuário escolheu fechar a feature sem
verificação, em vez de pausar ou fazer só o sensor de discriminação nas áreas críticas.

Nenhuma afirmação deste arquivo vale como evidência de conformidade. Não há checagem ancorada na
spec, nem sensor de discriminação, nem UAT.

## O que existe de evidência (do autor, não independente)

- T1–T16 concluídas e commitadas (`tasks.md`).
- Último gate do autor, ao fim do Lote C: 1864 testes passando, `ruff check`, `ruff format --check`
  e `makemigrations --check` verdes. Não foi reexecutado por um verificador.
- Testes antigos alterados só dentro do inventário autorizado (T-1 a T-7).

## Risco aceito

A feature mexe em autorização: escopo das contas por unidade, quais contas o gestor pode
desativar, reativar ou redefinir, situação derivada da conta (AD-016) e o middleware que obriga a
troca da senha provisória (AD-017, inclusive no admin). O risco não verificado é que algum teste
passe sem discriminar o comportamento — uma regressão nessas regras pode não quebrar a suíte.

Áreas de maior risco, se a verificação for feita depois: GEST-06/07 (escopo por unidade, 404 vs
403 vs 405), ações por perfil (só USUARIO da mesma unidade), AD-016, AD-017, pré-preenchimento da
unidade, migration preservando contas e autores do acervo.

## Requirement Traceability Update

GEST-01 a GEST-69: `Implementing (não verificada, risco aceito)`. Nenhuma passa a `Verified`.

## Gate de fechamento

`validate_state.py gestao-por-unidade` sai com erro de propósito: o relatório não tem veredito de
aprovação ou reprovação, porque a verificação não foi feita.
