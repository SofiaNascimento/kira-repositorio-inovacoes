# Especificação de Design — KIRA

**Sistema de Repositório e Compartilhamento de Inovações de Back Office**

Fonte única do visual. Citada com `@docs/design-spec.md` nos passes de design.
UI/UX guiada pelas 10 heurísticas de Nielsen, conformidade WCAG 2.1 AA e modelo eMAG.

> Os hexes abaixo foram derivados da logo. São ponto de partida; se houver valores oficiais,
> substitua. O que não pode mudar sem reverificação são as **combinações seguras de contraste**.

---

## 1. Identidade

- **Marca:** KIRA — Conhecimento · Inovação · Replicação Administrativa.
- **Tom visual:** sóbrio, administrativo, confiável. Azul institucional, bastante respiro, pouco ruído (heurística H8 — estético e minimalista).
- **Logo:** usada no cabeçalho (canto superior esquerdo) e na tela de login. O gradiente navy → azul-claro aparece só na marca e em áreas de destaque (hero), nunca atrás de texto de leitura.

### 1.1 Direção de design: clean e moderno

O sistema deve ser **clean e moderno ao mesmo tempo**, sem abrir mão de nada do que está
especificado neste documento (paleta, contraste, Nielsen, WCAG 2.1 AA, eMAG). "Moderno" aqui é
decisão concreta, não estética vaga:

- **Clean:** muito espaço em branco, uma ação primária por tela, nada de ornamento sem função. Só o essencial em cada superfície (H8); o resto vem sob demanda (ajuda contextual, detalhe).
- **Moderno:** superfícies planas com profundidade sutil (sombras leves, não pesadas), cantos arredondados, hierarquia tipográfica clara, ícones de traço consistente, microinterações discretas (hover/foco suaves, transições curtas).
- **Consistência acima de tendência:** o mesmo componente se parece e se comporta igual em toda tela (H4). Modernidade não justifica telas que destoam entre si.

**O moderno nunca passa por cima do que você definiu.** Em caso de conflito, a restrição vence:

- nada de texto cinza-claro de baixo contraste em nome do "minimalismo" — vale a tabela de contraste da §2;
- placeholder não substitui rótulo, mesmo que pareça mais limpo (§6, acessibilidade);
- status, erro e sucesso nunca comunicados só por cor, por mais elegante que fique;
- animação sempre discreta e respeitando "reduzir movimento" (`prefers-reduced-motion`);
- foco sempre visível — não some em nome do visual.

Em resumo: clean e moderno **dentro** dos limites de acessibilidade e usabilidade, não contra eles.

---

## 2. Paleta de cores

### Tokens

```css
:root {
  /* Marca */
  --brand-navy:        #1E3A6E;  /* títulos, marca, alta ênfase */
  --brand-blue:        #2E5EAA;  /* ações primárias, links, foco */
  --brand-blue-light:  #6AA0E0;  /* decorativo: gradiente, acentos grandes — NUNCA texto */
  --brand-gradient: linear-gradient(90deg, #1E3A6E 0%, #6AA0E0 100%);

  /* Neutros */
  --text:        #1A2332;  /* texto de leitura */
  --text-muted:  #566072;  /* texto secundário, legendas */
  --border:      #D4DEEC;  /* bordas, divisores */
  --bg:          #F0F5FC;  /* fundo da aplicação */
  --surface:     #FFFFFF;  /* cards, campos, superfícies */

  /* Semânticos (feedback) */
  --success:  #1E7D46;
  --warning:  #8A5A00;
  --error:    #B3261E;
  --info:     #2E5EAA;
}
```

### Combinações seguras de contraste (a regra que garante o AA)

WCAG AA exige 4.5:1 para texto normal, 3:1 para texto grande (≥ 24px, ou ≥ 18.7px negrito) e 3:1
para componentes de interface e foco. Use só estas combinações para texto:

| Uso | Cor | Sobre | Contraste | Veredito |
| --- | --- | ----- | --------- | -------- |
| Texto de leitura | `--text` #1A2332 | `--surface` / `--bg` | ~14:1 | ✔ AA/AAA |
| Texto secundário | `--text-muted` #566072 | `--surface` | ~6:1 | ✔ AA |
| Título / marca | `--brand-navy` #1E3A6E | branco/claro | ~11:1 | ✔ AA/AAA |
| Link / ação | `--brand-blue` #2E5EAA | branco/claro | ~6.5:1 | ✔ AA |
| Texto branco em botão | #FFFFFF | `--brand-blue` #2E5EAA | ~6.5:1 | ✔ AA |
| Texto branco em botão | #FFFFFF | `--brand-navy` #1E3A6E | ~11:1 | ✔ AA/AAA |

**Proibido:** `--brand-blue-light` (#6AA0E0) como fundo de texto ou como cor de texto — não atinge
4.5:1. Ele é decorativo (gradiente da marca, faixas grandes, ícones grandes). Todo par novo de
cores passa por um verificador de contraste antes de entrar.

**Não dependa só de cor (WCAG 1.4.1 / eMAG):** status, erros e sucesso sempre trazem também
texto e/ou ícone, nunca apenas a cor.

---

## 3. Tipografia

```css
:root {
  --font-sans: "Inter", "Segoe UI", system-ui, -apple-system, Arial, sans-serif;

  --fs-xs: 0.75rem;   /* 12px — rótulos, legendas */
  --fs-sm: 0.875rem;  /* 14px — texto auxiliar */
  --fs-base: 1rem;    /* 16px — corpo (mínimo para leitura) */
  --fs-lg: 1.25rem;   /* 20px — subtítulos */
  --fs-xl: 1.5rem;    /* 24px — títulos de seção */
  --fs-2xl: 2rem;     /* 32px — título de página */

  --lh-body: 1.5;     /* altura de linha do corpo */
}
```

- Corpo em 16px no mínimo; a interface deve suportar zoom até 200% sem quebrar (WCAG 1.4.4).
- Hierarquia por tamanho e peso, não por cor isolada.
- A tagline da marca é o único uso de itálico.

---

## 4. Espaçamento e grid

Escala base de 4px: `4 · 8 · 12 · 16 · 24 · 32 · 48`. Conteúdo com largura máxima confortável de
leitura (~1100px) centralizado; margens generosas (H8).

---

## 5. Layout base

Toda tela usa HTML semântico com marcos (landmarks): `header`, `nav`, `main`, `footer`.

- **Cabeçalho:** logo KIRA à esquerda (link para a home), navegação principal, menu do usuário à direita.
- **Navegação consistente** em todas as telas (H4 — consistência; eMAG — apresentação consistente).
- **Pular para o conteúdo:** primeiro link focável da página, "Ir para o conteúdo principal", visível ao receber foco (eMAG; WCAG 2.4.1).
- **Idioma:** `<html lang="pt-br">`.
- **Título de página** único e descritivo por tela (WCAG 2.4.2), refletindo onde o usuário está (H1 — visibilidade do status).
- **Rodapé:** identificação do sistema e links de apoio.

---

## 6. Componentes

Cada componente é reutilizável e tem todos os estados definidos. As telas estendem estes
componentes; não recriam estilo.

### Botão
- **Primário:** fundo `--brand-blue`, texto branco. Ação principal da tela (uma por contexto).
- **Secundário:** contorno `--brand-blue`, texto `--brand-blue`, fundo transparente.
- **Perigo:** fundo `--error`, texto branco. Só para ações destrutivas.
- **Estados:** hover (escurece ~8%), **foco visível** (anel de 2px com contraste ≥ 3:1), ativo, desabilitado (opacidade reduzida + `aria-disabled`).
- Rótulo em texto, nunca só ícone sem rótulo acessível.

### Campo de formulário
- **Rótulo sempre visível**, associado ao campo por `for`/`id` (eMAG; WCAG 1.3.1, 3.3.2). Placeholder não substitui rótulo.
- Campo obrigatório indicado por texto ("obrigatório") ou asterisco **com legenda**, não só por cor.
- **Estado de erro:** borda `--error` + mensagem de texto abaixo, ligada por `aria-describedby`, dizendo o que corrigir (H5 prevenção, H9 recuperação; WCAG 3.3.1, 3.3.3). Os dados já digitados são preservados (RF13).
- Dica de preenchimento / ajuda contextual quando útil (RF15, H10).

### Mensagem de feedback (alerta)
- Quatro variantes: sucesso, aviso, erro, informação.
- Sempre **ícone + texto + borda colorida à esquerda** — a cor é reforço, não a única pista (WCAG 1.4.1; eMAG).
- Mensagens dinâmicas anunciadas por `aria-live` (leitor de tela percebe a mudança).
- Exibida após cada ação relevante: cadastro, edição, exclusão, mudança de status (RF12, H1).

### Card
- Superfície branca, borda `--border`, cantos suaves, sombra discreta. Usado em listagem e no dashboard.

### Tabela
- `caption` descritivo, `th` com `scope`, cabeçalho fixo quando longa. Zebra só com contraste suficiente. Alternativa a tabela em telas estreitas (ver responsividade).

### Badge de status
- Rótulo textual sempre presente ("Em teste", "Validada", "Disponível para replicação") + cor + forma/ícone. Nunca a cor sozinha.

---

## 7. Estados de tela

- **Vazio:** mensagem clara do que aconteceu e o próximo passo (ex.: "Nenhuma inovação encontrada. Cadastre a primeira."), com ação visível. (H1, H10)
- **Carregando:** indicador (spinner ou skeleton) com `aria-live="polite"`; nunca tela congelada sem sinal. (H1)
- **Erro:** explica o problema em linguagem simples e oferece ação (tentar de novo, voltar). (H9)

---

## 8. Acessibilidade — WCAG 2.1 AA + eMAG

Checklist aplicável a toda tela. O RNF09 é Essencial; esta seção é o critério da auditoria final.

**Perceptível**
- Contraste de texto ≥ 4.5:1 (≥ 3:1 para texto grande) — ver §2.
- Alternativa textual (`alt`) para imagens informativas; imagem decorativa com `alt=""`.
- Não depender só de cor para transmitir informação.
- Layout funciona com zoom de 200% e em telas estreitas.

**Operável**
- Tudo acessível por teclado, na ordem lógica; sem armadilha de foco.
- **Foco sempre visível** (anel com contraste ≥ 3:1).
- Link "Ir para o conteúdo" como primeiro elemento focável.
- Título de página único e descritivo.

**Compreensível**
- `lang="pt-br"` no documento.
- Rótulos associados a todos os campos; erros identificados em texto, com instrução de correção.
- Navegação e componentes consistentes entre telas.

**Robusto**
- HTML semântico e marcos (`header`/`nav`/`main`/`footer`).
- Estados e mensagens dinâmicas expostos por ARIA (`aria-describedby`, `aria-live`, `aria-disabled`).

**eMAG (ênfases do modelo brasileiro)**
- Marcação: HTML semântico, landmarks, ordem de leitura coerente com a visual.
- Comportamento: foco visível, navegação por teclado, link de pular para o conteúdo.
- Conteúdo/Informação: linguagem clara, não depender de cor, descrever a página.
- Apresentação/Design: contraste adequado, layout consistente.
- Formulários: rótulos, agrupamento lógico, mensagens de erro claras.

---

## 9. Aderência às 10 heurísticas de Nielsen

Mapa das heurísticas para decisões concretas deste sistema. Serve à avaliação heurística do RNF01
e à defesa na banca.

| # | Heurística | Como o design atende | Requisitos |
| - | ---------- | -------------------- | ---------- |
| H1 | Visibilidade do status | título de página, feedback após cada ação, estados de carregando/vazio | RF12, RF09 |
| H2 | Correspondência com o mundo real | vocabulário do domínio (categoria, unidade, status), ajuda contextual | RF15, RN07 |
| H3 | Controle e liberdade | cancelar/voltar nos formulários, confirmação antes de excluir | RF14, RN12 |
| H4 | Consistência e padrões | navegação e componentes reutilizados em todas as telas | RNF01, RNF04, RN07 |
| H5 | Prevenção de erros | validação, confirmação de ações destrutivas, listas controladas | RF13, RF14, RN02, RN10, RN12 |
| H6 | Reconhecimento em vez de memorização | filtros por lista, rótulos descritivos, dicas | RF06, RF15, RN07 |
| H7 | Flexibilidade e eficiência | busca + filtros combinados | RF05, RF06 |
| H8 | Estético e minimalista | layout limpo, respiro, informação resumida na listagem | RNF01, RF03 |
| H9 | Reconhecer e recuperar-se de erros | mensagens de erro em texto claro, indicando campo e correção | RF13, RF12 |
| H10 | Ajuda e documentação | textos de apoio e exemplos nos campos e filtros | RF15 |

---

## 10. Notas por feature

O que é específico de cada tela. A parte global (§2–§8) vale para todas.

### autenticacao (F1)
Card de login centralizado, marca KIRA no topo, formulário mínimo (usuário/e-mail + senha).
Credencial inválida: mensagem de erro em texto, sem revelar qual campo falhou por segurança.

### cadastro-inovacao (F2)
Formulário estruturado seguindo o fluxo problema → solução → resultado. Campos agrupados, validação
em linha, ajuda contextual (RF15), botões Salvar (primário) e Cancelar (secundário). Feedback de
sucesso ao gravar.

### consulta-inovacoes (F3)
Lista em cards ou tabela com título, categoria, unidade e status (badge). Barra de busca e painel de
filtros reconhecíveis. Estado vazio claro. Página de detalhe com todos os campos e o contato do
responsável em destaque.

### edicao-exclusao (F4)
Edição reusa o formulário de F2. Exclusão abre diálogo de confirmação (modal com foco preso, ação de
perigo clara e opção de cancelar). Usuário sem permissão não vê a ação.

### ciclo-de-vida-status (F5)
Controle que mostra o ciclo Em teste → Validada → Disponível para replicação, com o estado atual
evidente e feedback ao mudar. Transições inválidas desabilitadas, não escondidas sem explicação.

### reaproveitamento-indicadores (F6)
Dashboard com cards de métrica e gráficos. Gráficos trazem rótulos de dado e uma alternativa em
tabela acessível (não dependem de cor). Ação "sinalizar reaproveitamento" só aparece em inovação
"Disponível para replicação".
