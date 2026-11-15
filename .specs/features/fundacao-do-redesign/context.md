# Fundação do Redesign (R1) Context

**Gathered:** 2026-11-15
**Spec:** `.specs/features/fundacao-do-redesign/spec.md`
**Status:** Concluída (2026-11-15), com risco residual de teste aceito

---

## Feature Boundary

A casca comum da v2 da `docs/design-spec.md` (tokens, fonte Inter servida pelo projeto, barra de
acessibilidade com atalhos 1/2/3, faixa da marca, menu com ícones e página atual, área do
usuário, cabeçalho de página com trilha, rodapé com Acessibilidade e Ajuda, alto contraste por
POST) e os componentes da §6 v2 na `kira.css` com todos os estados. O miolo de cada tela fica
para as features seguintes do redesign.

---

## Implementation Decisions

### Alto contraste

- Cookie `kira_contraste=alto` (1 ano, `HttpOnly`, `SameSite=Lax`, `Secure` sob HTTPS), lido no
  servidor pelo base; "normal" apaga o cookie. Nada no perfil, nenhuma migration, nada no Neon.
- Valor explícito no POST (`alto`/`normal`), não alternância: reenviar é idempotente.

### Atalhos

- `accesskey` 1, 2, 3 nos links da barra, como o eMAG prescreve; sem ouvinte de teclado.
- A página Acessibilidade documenta a combinação por navegador (Alt+n no Chrome/Edge do Windows,
  Alt+Shift+n no Firefox, Control+Option+n no macOS) e avisa que o atalho do leitor de tela ou
  do sistema, quando coincide, prevalece. Conferir com um leitor de tela na UAT.

### Ícones

- Lucide (ISC; parte derivada do Feather, MIT), SVG embutido em parciais `templates/icones/`,
  `aria-hidden="true"`, `focusable="false"`, traço `currentColor`; aviso de licença em
  `templates/icones/LICENSE`.

### Páginas públicas

- `/acessibilidade/`, `/acessibilidade/contraste/` e `/ajuda/` com `@login_not_required`
  (AD-006); sem sessão, cabeçalho só com a marca.

### Fonte

- Inter variável, subconjunto latino, woff2, em `static/fontes/` com `OFL.txt`;
  `STATICFILES_DIRS = [BASE_DIR / "static"]`.
- `kira.css` traz a URL `/static/fontes/…` literal (o DS-02 compara o CSS cru); um teste amarra a
  URL ao `STATIC_URL` e ao `collectstatic`. O base faz o `preload` com `{% static %}`.

### Menu no celular

- Sem `<details>` (decisão contrária ao pedido inicial, aceita): os itens quebram de linha, como
  a §5.2. Motivo: sem JS o `details` fechado esconde o menu no desktop, e o REAP-28 reprovaria.

### Escopo nas telas

- Todas as telas preenchem o bloco do h1; as nove da §5.3 ganham a trilha; login, 403, 404 e 500
  sem trilha. Blocos de descrição e ação principal ficam vazios até o passe de cada tela.
- Textos atuais mantidos: "Ir para o conteúdo principal" e o sufixo "· Repositório de Inovações".
- Sem `tabindex` no `main` e no `nav` (o `<main id="conteudo">` exato é fixado por testes).
- Barra de acessibilidade e formulário de contraste fora do `<header>` e do `<main>`.

### Testes antigos autorizados

- T-A a T-D da spec (cabeçalho INOV-38/CONS-10/REAP-28; `ROTAS_PUBLICAS`; DS-01; fixture
  `paginas`). Qualquer outro teste antigo que precise mudar: parar e pedir.

### Agent's Discretion

- Nomes exatos dos parciais e da view de contraste; conteúdo textual da página Ajuda dentro das
  quatro seções da RED-35.

### Declined / Undiscussed Gray Areas → Assumptions

Nenhuma: todas as propostas foram confirmadas e estão na tabela de premissas da spec.

---

## Specific References

- Protótipo da v2 citado na `design-spec.md` (os textos dele são fictícios; vale a spec).

---

## Deferred Ideas

- Preferência de contraste por usuário no perfil (sincronizada entre dispositivos).
- Menu recolhível no celular, se um dia houver JavaScript progressivo.
- Escapes na `kira.css` (Execute, T4 e T5): `[aria-\69 nvalid=true]` e `.cartao-ino\76 acao`, porque o CONS-30 (`"aria-invalid" not in html`) e o DS-02 (nenhum nome de usuário dos testes, e "nova" está em "inovacao") leem a página inteira com a folha embutida. Quando esses testes passarem a ler o DOM sem o `<style>`, voltar à grafia direta.
- Separador da trilha escapado na `kira.css` (Execute, T12): `content: "\203A" / ""`, porque a folha embutida poria o "›" na página inteira. Se a folha sair do `<style>` (supersedendo a AD-010), voltar ao literal.
- Tela autenticada fora da seção do menu (Execute, T10): quando existir (ex.: Acessibilidade e Ajuda na T15/T16), trocar o teste de "nenhum `aria-current`" que renderiza o `base.html` direto por um pelo `client`. **Feito na T15** (ver Ajustes do Execute, Lote 3).
- Fechar o risco residual da R1 (`validation.md`, iteração 2): guarda de esconder sobre a folha com os escapes CSS decodificados e por efeito (quase-zero, cor igual ao fundo, fora da tela, `clip-path` parcial, `content-visibility`), altura de botão conferida pelos elementos reais da página (não pelo texto do seletor) e `max-height`, e oráculo dos ícones pelo nome do ícone do Lucide (não pelo arquivo copiado). Melhor ainda: um teste de navegador real (Playwright) que mede o menu e os botões renderizados.
