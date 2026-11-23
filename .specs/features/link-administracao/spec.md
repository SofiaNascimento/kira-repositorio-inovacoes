# Link da Administração — Specification

**Status:** Aprovada (2026-11-23). Escopo Small/Medium: spec breve, sem Design nem Tasks
formais; plano inline no Execute. Escrita em 2026-11-15 e conferida em 2026-11-23 contra o código
depois da R2 (`redesign-consulta`): referências de código válidas; a R2 fixou a pasta de ícones
(ver "Testes antigos que mudam").

## Problem Statement

O admin do Django (`/admin/`) é a única superfície de gestão de contas, unidades e categorias
(RN07, RN11), mas nenhuma tela do KIRA leva até ele: o ADMINISTRADOR precisa saber o endereço de
cor. Dentro do admin, também não há caminho claro de volta ao sistema.

## Goals

- [ ] Um ADMINISTRADOR chega ao admin a partir de qualquer página interna, com um clique.
- [ ] Quem não é ADMINISTRADOR não vê o link (inclusive um USUARIO com `is_staff`).
- [ ] O admin se identifica como KIRA e volta ao sistema pelo "Ver o site".

## Code Reuse Analysis

| Item | Onde | Reuso |
| ---- | ---- | ----- |
| Área do usuário | `templates/base.html:51` (`div.usuario`: iniciais, nome, Sair) | Ganha o link antes do Sair |
| Ícones | `templates/icones/*.svg` (AD-013), incluídos com `{% include %}` | Ganha `engrenagem.svg` (Lucide `settings`, copiado do repositório oficial), no padrão de nome em português da pasta |
| Regra de acesso ao admin | `contas.admin.AcessoSomenteAdministradorMixin` (AD-007), `Usuario.is_administrador` | O link usa a mesma pergunta (`user.is_administrador`) |
| Visibilidade | `inovacoes/tests/visibilidade.py` (`exibido()`) | Toda AC de "exibido" (L-028, L-030, L-044) |

## Out of Scope

| Feature | Reason |
| ------- | ------ |
| Telas próprias no lugar do admin | O admin segue como superfície do ADMINISTRADOR (AD-007). A área do gestor de unidade é outra feature (`gestao-por-unidade`). |
| Tema visual do admin igual à `kira.css` | Só título e "Ver o site"; restilizar o admin foge do escopo. |
| Item no menu principal | O menu é de navegação do acervo; a administração é ferramenta da conta. |

---

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --------------------- | -------------- | --------- | ---------- |
| Onde fica o link | Na área do usuário do cabeçalho, entre o nome e o "Sair" | É ferramenta da conta, não navegação do acervo; não mexe no `nav` Principal que a T-A fixa | y (aprovação de 2026-11-23) |
| Quem vê | Só `user.is_administrador` | Um USUARIO com `is_staff` cairia num 403 (AD-007, L-003) | y (aprovação de 2026-11-23) |
| Aba | Mesma aba, link comum | Sem `target="_blank"` (H3, eMAG: não abrir janela sem avisar) | y (aprovação de 2026-11-23) |
| Texto e estilo | "Administração", com ícone Lucide `settings` decorativo, estilo de link secundário | Consistente com os ícones do menu (AD-013) | y (aprovação de 2026-11-23) |
| Título do admin | `site_header` "KIRA — Administração", `site_title` "KIRA", `index_title` "Administração do KIRA" | Identifica o sistema dentro do admin | y (aprovação de 2026-11-23) |
| "Ver o site" | `site_url = "/inovacoes/"` | A raiz redireciona; a lista é a página inicial real | y (aprovação de 2026-11-23) |

**Open questions:** none - all resolved or logged above.

---

## User Stories

### P1: Acesso ao admin pela interface ⭐ MVP

**User Story**: Como ADMINISTRADOR, quero um link para a administração no cabeçalho para gerir
contas, unidades e categorias sem decorar o endereço.

**Acceptance Criteria**:

1. WHILE o usuário autenticado tem perfil ADMINISTRADOR, o sistema SHALL exibir, em toda página interna, um link com texto "Administração" e `href="/admin/"` dentro da área do usuário do cabeçalho, antes do botão "Sair".
2. WHILE o usuário autenticado tem perfil USUARIO (com ou sem `is_staff`), o sistema SHALL não ter na página nenhum link para `/admin/`.
3. WHILE não há sessão, o sistema SHALL não ter na página nenhum link para `/admin/`.
4. The sistema SHALL renderizar o ícone do link com `aria-hidden="true"`, de modo que o nome acessível do link seja exatamente "Administração".
5. WHEN o ADMINISTRADOR abre `/admin/` THEN o sistema SHALL exibir o cabeçalho "KIRA — Administração" e um link "Ver o site" com `href="/inovacoes/"`.

**Independent Test**: entrar como `admin`, clicar em "Administração" e voltar por "Ver o site";
entrar como `maria` (USUARIO staff) e não achar o link.

---

## Edge Cases

- IF um ADMINISTRADOR é rebaixado a USUARIO enquanto tem sessão aberta THEN o sistema SHALL deixar de exibir o link na próxima página carregada.
- WHEN a página está em alto contraste THEN o link SHALL usar os pares de cor do alto contraste já definidos para os links da casca.

---

## Testes antigos que mudam (autorização na aprovação)

- `nucleo/tests/test_casca.py:148` (`test_pasta_traz_os_icones_da_casca_e_da_consulta`, T-O da
  R2): a pasta `templates/icones/` deixa de ter exatamente os 14 ícones da R1 e da R2 e passa a ter
  esses 14 mais `engrenagem` (ADM-04), nem mais nem menos. A mudança só acrescenta o nome à lista
  esperada; a garantia da RED-16, da RED-23 e da RCON-15 continua. Autorizada pelo usuário em
  2026-11-23, na conferência da spec antes do Execute.

DS-05 (`<span>nome</span>` e o "Sair" depois do `nav`) continua valendo sem mudança: o link entra
entre os dois sem mudar a ordem que o teste fixa. Se o Execute achar outro teste antigo que precise
mudar, para e pede.

---

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
| -------------- | ----- | ----- | ------ |
| ADM-01 | P1: Acesso ao admin (AC 1) | Execute | Implemented |
| ADM-02 | P1: Acesso ao admin (AC 2) | Execute | Implemented |
| ADM-03 | P1: Acesso ao admin (AC 3) | Execute | Implemented |
| ADM-04 | P1: Acesso ao admin (AC 4) | Execute | Implemented |
| ADM-05 | P1: Acesso ao admin (AC 5) | Execute | Implemented |
| ADM-06 | Edge: rebaixamento | Execute | Implemented |
| ADM-07 | Edge: alto contraste | Execute | Implemented |

**Coverage:** 7 total, 0 mapped to tasks (plano inline), 0 unmapped.

---

## Success Criteria

- [ ] O ADMINISTRADOR chega ao admin em um clique de qualquer página interna.
- [ ] Nenhuma conta sem perfil ADMINISTRADOR vê o link.
- [ ] Suíte e build gate verdes, sem teste antigo alterado.
