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
spec nem sensor de discriminação. O UAT veio depois (seção abaixo).

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

## Interactive UAT Results (2026-11-25)

Feito pelo usuário no navegador, servidor local (`runserver`, banco local `localhost:5433/kira`, com
`contas 0005` aplicada só ali) e contas `uat_*` criadas para o teste. **8 de 8 passaram**, sem
problema registrado. O UAT não substitui o Verifier: confirma o comportamento visível, não que os
testes automatizados discriminem regressões.

| # | Teste | ACs exercidas | Resultado |
| - | ----- | ------------- | --------- |
| 1 | Menu e tela "Minha unidade" (item no menu, `aria-current`, tabela com 7 colunas, escopo, ordem, "Nunca", ações só em USUARIO) | Área "Minha unidade" AC 1, 3, 5–11 (GEST-13 com E-4) | ✅ Pass |
| 2 | Criar conta: formulário, erros de usuário/e-mail (maiúsculas)/confirmação, resumo de erros, campos devolvidos, sucesso | Criar conta AC 1–3, 5, 6, 8, 9; Formulários AC 1, 2 | ✅ Pass |
| 3 | Troca obrigatória da senha provisória: bloqueio (inclusive `/admin/`), sem "Cancelar", senha atual errada, nova igual à atual, troca certa | Redefinir/troca AC 4–9; Formulários AC 1, 2 | ✅ Pass |
| 4 | Desativar e reativar: alertas, "Desativada" por escrito, sessão aberta vira anônima, login recusado com a mensagem genérica, GET → 405 | Desativar/reativar AC 1, 2, 4–6 | ✅ Pass |
| 5 | Redefinir senha: erro de validador, sucesso, sessão aberta cai, senha antiga recusada, troca obrigatória no próximo acesso | Redefinir/troca AC 1–4 | ✅ Pass |
| 6 | Acesso negado: USUARIO e ADMINISTRADOR recebem "Acesso restrito"; gestor da Sul só vê a Sul e recebe 404 em conta da Norte e de outro gestor; gestor sem staff vai ao login do admin | Área "Minha unidade" AC 2, 4, 7; GEST-07 (E-1) | ✅ Pass |
| 7 | Curadoria: gestor da origem edita, avança status e exclui inovação de outro autor; gestor de outra unidade sem ações e 403 nas três rotas; USUARIO da mesma unidade sem ações | Curadoria AC 1–5 | ✅ Pass |
| 8 | Unidade pré-preenchida: cadastro com e sem unidade, troca para outra unidade grava a escolhida, edição mostra a gravada, reaproveitamento elegível e não elegível | Unidade pré-preenchida AC 1–6 | ✅ Pass |

Não exercitado no UAT: campos extras no POST de criar conta (Criar conta AC 4), validador de senha
na criação (AC 7), "Cancelar" (AC 10), idempotência do POST de situação (Desativar AC 3), autoria
mantida após desativar (AC 7), mudança de unidade/perfil pelo ADMINISTRADOR (Curadoria AC 6, 7),
migration sobre os dados existentes além do banco local.

## Requirement Traceability Update

GEST-01 a GEST-69: `Implementing (não verificada, risco aceito)`. Nenhuma passa a `Verified`.

## Gate de fechamento

`validate_state.py gestao-por-unidade` sai com erro de propósito: o relatório não tem veredito de
aprovação ou reprovação, porque a verificação não foi feita.
