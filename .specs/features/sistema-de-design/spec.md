# Sistema de Design — Specification

Fonte do visual: `docs/design-spec.md` (§1–§8, a parte global "Sistema de design"). Este passe
consolida o template base e a folha de estilo central e faz as telas da F1 à F4 os usarem. Não
muda regra de negócio, view, form, model nem URL.

## Problem Statement

As telas da F1 à F4 estendem um `base.html` com um `<style>` inline de cinco regras: sem paleta,
sem tipografia, sem componentes. Cada feature nova (F5, F6) ia inventar o próprio visual, e a
spec de design (`docs/design-spec.md`) exige o oposto: um componente se parece e se comporta igual
em toda tela (H4) e as telas não recriam estilo (§6).

## Goals

- [ ] Um template base único com cabeçalho, navegação, menu do usuário, link de pular, `main` e rodapé (§5).
- [ ] Uma folha de estilo central com os tokens da §2–§4 e os componentes da §6, sem estilo em nenhuma tela.
- [ ] As oito telas existentes usam os componentes sem que nenhum teste da F1 à F4 mude.

## Code Reuse Analysis

Levantamento do que já existe de template e estilo, F1 a F4.

| Item | Onde | Situação | Reuso |
| ---- | ---- | -------- | ----- |
| Template base | `templates/base.html` | Já é a raiz única: as 8 telas fazem `{% extends "base.html" %}`; blocos `title`, `cabecalho` (sem uso) e `conteudo` | Mantido como o base; ganha o layout da §5 |
| Estilo | `<style>` inline em `base.html` | 5 regras: corpo, `:focus-visible` (3px `#1a5fb4`), lista de mensagens | Substituído pela folha central; o `:focus-visible` universal fica (INOV-35, CONS-41, EDEX-42) |
| Estilo por tela | nenhuma tela | Nenhum `<style>` nem `style=` fora do base | Nada a remover; a regra passa a ser testada |
| Cabeçalho e navegação | `base.html` | `<header>`, `nav aria-label="Principal"` (Inovações, Cadastrar inovação), formulário POST "Sair" | Mantidos; os testes INOV-38, CONS-10 e AUTH (logout) fixam o HTML |
| Mensagens (feedback) | `base.html` | `div role="status"` com `ul.mensagens` | Mantido; cada item ganha a variante pelo nível da mensagem |
| Resumo de erro | `login.html`, `inovacao_form.html`, `inovacao_list.html` | `div role="alert"` | Mantido sem atributo novo (CONS-30 fixa `<div role="alert">`); estilizado pelo papel ARIA |
| Campo de formulário | `inovacoes/campo.html` + `field.html` do Django (login) | Rótulo, controle, erros, ajuda; `aria-describedby` automático | Mantido; os templates de tela só envolvem cada campo num `div.campo` |
| Páginas de erro | `templates/500.html`, `acesso_negado.html`, `inovacao_nao_encontrada.html` | Estendem o base | Ganham o componente de estado de erro |
| Arquivos estáticos | `STATIC_URL` só | Sem `STATIC_ROOT`, sem servidor de estáticos com `DEBUG=False` | Não usados: ver AD-010 |

**HTML fixado por testes** (não pode receber atributo): `<header>`, `<nav aria-label="Principal">`
e seus links, `<form method="post" action="/sair/">`, `<div role="alert">` da busca, `<table>`,
`<th scope="col">`, os links "Editar", "Excluir", "Limpar filtros", "Voltar para…", "Cadastrar
inovação" do estado vazio, os links de paginação e o texto puro do `<dd>` de status. Esses
elementos recebem estilo por seletor de estrutura ou de papel ARIA, ou por um contêiner.

## Out of Scope

| Feature | Reason |
| ------- | ------ |
| Logo em imagem | Nenhum arquivo de logo no repositório. A marca é o texto "KIRA" com a tagline; trocar por `<img alt="KIRA">` depois não muda o resto. |
| Fonte Inter carregada da web | Sistema interno; nenhuma dependência externa nova. A pilha da §3 cai em Segoe UI/system-ui. |
| Modal de exclusão com foco preso (§10 F4) | A F4 decidiu página de confirmação sem JavaScript; o passe só estiliza essa página. |
| Agrupar o formulário em problema → solução → resultado (§10 F2) | Mexe na ordem e na estrutura do formulário da F2; fica para um passe da F2. |
| `aria-current` no item de navegação da página atual | Os testes INOV-38/CONS-10 fixam `<a href="...">` sem atributo extra. |
| Cabeçalho fixo de tabela, cards de métrica e gráficos | Sem tabela longa rolável nem dashboard ainda (F6). |
| Links de apoio no rodapé | Não existe página de ajuda ou contato no sistema. O rodapé traz a identificação. |
| Modo escuro | A spec de design não define. |
| Auditoria WCAG completa e teste SUS | Validação transversal no fim (RNF09, RNF01). |

---

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --------------------- | -------------- | --------- | ---------- |
| Paleta | Os tokens da §2 (navy/azul), não "teal" | O pedido fala em "paleta teal", mas a `design-spec.md` é a fonte única e define navy `#1E3A6E` e azul `#2E5EAA` | n |
| Onde mora a folha | `templates/kira.css`, embutida pelo base com `<style>{% include "kira.css" %}</style>` | Ver AD-010: um arquivo só, sem estáticos para servir, e os testes de foco continuam lendo o CSS real | y |
| Borda de campo | `--text-muted` (6.3:1), não `--border` (1.4:1) | WCAG 1.4.11 pede 3:1 para o limite de um controle; `--border` fica para cards e divisores | y |
| Anel de foco | `outline: 2px solid var(--brand-blue)` com `outline-offset: 2px` | §6: anel de 2px com contraste ≥ 3:1 (azul sobre branco 6.4:1) | y |
| Cor de fundo dos selos e alertas | Tintas claras das cores semânticas, cada par texto/fundo ≥ 4.5:1 | §2: todo par novo passa por verificador de contraste; o teste DS-08 refaz a conta | y |
| Selo de status | Texto + cor + forma (círculo, quadrado, losango) desenhada em CSS, sem texto gerado | §6 badge; a forma é pista não cromática | y |
| Ícone dos alertas | Glifo em `::before` com texto alternativo vazio (`content: "✓" / ""`) | O texto da mensagem já diz tudo; o glifo não é lido duas vezes | y |
| Variante da mensagem | Pela tag do nível da mensagem do Django (`success`, `info`, `warning`, `error`) | Já é como as views gravam a mensagem; nada muda na view | y |
| Idioma dos critérios | EARS em inglês, restante em português | Padrão das features anteriores | y |

**Open questions:** nenhuma; a paleta está registrada acima como premissa a confirmar.

---

## User Stories

### P1: Telas com o mesmo layout e componentes ⭐ MVP

**User Story**: Como usuário do KIRA, quero que toda tela tenha o mesmo cabeçalho, navegação e componentes para reconhecer onde estou e o que posso fazer (H4, H1).

**Why P1**: É a base da §5 e da §6; a F5 e a F6 dependem dela.

**Acceptance Criteria**:

1. DS-01: The system SHALL render every page from `templates/base.html`, and no other template SHALL contain a `<style>` element or a `style=` attribute.
2. DS-02: The system SHALL embed exactly one `<style>` element per page, whose content is `templates/kira.css`.
3. DS-03: The system SHALL render, as the first focusable element of every page, the link "Ir para o conteúdo principal" pointing to `#conteudo`, the `id` of the page's single `<main>`.
4. DS-04: The system SHALL render on every page a `<header>` with the "KIRA" brand linking to `/`, a `<main>` and a `<footer>` with the text "KIRA · Repositório de Inovações".
5. DS-05: WHILE the user is authenticated the system SHALL render, inside the `<header>`, the username and the "Sair" button after the navigation.
6. DS-06: The stylesheet SHALL declare on `:root` every color token of §2 with its exact hex value and every type token of §3 with its exact value.
7. DS-07: The stylesheet SHALL style `:focus-visible` with a `2px solid` outline in `var(--brand-blue)`, and SHALL NOT remove the outline anywhere.
8. DS-08: The system SHALL use only text/background pairs with contrast ≥ 4.5:1 in the components (body, muted, links, buttons, alerts, badges), and SHALL NOT use `--brand-blue-light` as a text color or as the background of a component.
9. DS-09: WHERE the user prefers reduced motion the stylesheet SHALL disable transitions and animations.

**Independent Test**: abrir qualquer tela, apertar Tab uma vez e ver "Ir para o conteúdo principal"; inspecionar a página e achar um só `<style>`, o de `kira.css`.

---

### P1: Componentes nas telas existentes ⭐ MVP

**User Story**: Como usuário, quero botões, campos, alertas, tabelas e selos que se pareçam iguais em toda tela, sem depender só da cor.

**Why P1**: §6 e §7; é o que o usuário vê.

**Acceptance Criteria**:

1. DS-10: WHEN a page shows a Django message THEN the system SHALL render it inside `role="status"` with the class `alerta alerta--<tag>`, where `<tag>` is the message level tag (`success`, `info`, `warning`, `error`).
2. DS-11: The stylesheet SHALL give each alert variant and the `role="alert"` summary a non-color cue (an icon in `::before`) and a colored left border.
3. DS-12: WHEN the list or the detail shows an innovation THEN the system SHALL render its status text inside an element with the class `selo selo--<status>` (`em_teste`, `validada`, `disponivel_para_replicacao`).
4. DS-13: The stylesheet SHALL give each status badge a distinct shape in `::before`, so the status is not conveyed by color alone.
5. DS-14: The system SHALL render the destructive submit "Excluir definitivamente" with the class `botao--perigo`, and every other submit button of the screens with the primary button style.
6. DS-15: The system SHALL render the login form inside a card (`cartao`) headed by the KIRA brand.
7. DS-16: The system SHALL wrap the innovations table in a container that scrolls horizontally on narrow screens, so the page itself does not scroll sideways.

**Independent Test**: cadastrar uma inovação e ver o alerta de sucesso com ícone; na lista, ver o selo "Em teste" com a forma; excluir e ver o botão vermelho "Excluir definitivamente".

---

## Edge Cases

- IF the 500 page renders without a request context THEN the system SHALL still render the skip link, the brand and the stylesheet (DS-02, DS-03 on `500.html`).
- IF the user is anonymous THEN the system SHALL NOT render the main navigation nor the user menu (as INOV-38 and CONS-10 already require).

---

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
| -------------- | ----- | ----- | ------ |
| DS-01 | P1: Layout | Execute | Pending |
| DS-02 | P1: Layout | Execute | Implemented |
| DS-03 | P1: Layout | Execute | Implemented |
| DS-04 | P1: Layout | Execute | Implemented |
| DS-05 | P1: Layout | Execute | Implemented |
| DS-06 | P1: Layout | Execute | Implemented |
| DS-07 | P1: Layout | Execute | Implemented |
| DS-08 | P1: Layout | Execute | Implemented |
| DS-09 | P1: Layout | Execute | Implemented |
| DS-10 | P1: Componentes | Execute | Implemented |
| DS-11 | P1: Componentes | Execute | Implemented |
| DS-12 | P1: Componentes | Execute | Pending |
| DS-13 | P1: Componentes | Execute | Pending |
| DS-14 | P1: Componentes | Execute | Pending |
| DS-15 | P1: Componentes | Execute | Pending |
| DS-16 | P1: Componentes | Execute | Pending |

**Coverage:** 16 total, 16 mapped to execution steps, 0 unmapped.

---

## Success Criteria

- [ ] Os 492 testes da F1 à F4 passam sem nenhuma alteração.
- [ ] Nenhum template de tela tem `<style>` ou `style=`.
- [ ] O Verifier dá PASS em `validation.md`.
