# Especificação de Design — KIRA

**Sistema de Repositório e Compartilhamento de Inovações de Back Office**

Fonte única do visual. Citada com `@docs/design-spec.md` nos passes de design.
UI/UX guiada pelas 10 heurísticas de Nielsen, conformidade WCAG 2.1 AA e modelo eMAG.

> Os hexes abaixo foram derivados da logo. São ponto de partida; se houver valores oficiais,
> substitua. O que não pode mudar sem reverificação são as **combinações seguras de contraste**.

**Versão 2 (2026-11-15).** Referência visual: [protótipo da v2](https://claude.ai/artifact/TB5QrYVMt4fYAGKuLERgGn).
Os textos, números e nomes de unidades e categorias do protótipo são fictícios. Esta spec usa as
listas reais (RN07) e só os campos que o modelo tem: a unidade do `Usuario` é opcional e o
contato responsável é um texto livre. Quando o protótipo e esta spec divergirem, vale a spec.

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

### Tokens de cor novos (v2)

Somam-se aos de cima; nenhum valor da paleta muda. Os quatro fundos suaves já existiam no
`kira.css` e passam a constar da spec.

```css
:root {
  /* Interação */
  --brand-blue-hover: #28529A;  /* fundo do botão primário em hover */
  --borda-campo:      #7A879B;  /* borda de campo, select e alternador: 3:1 sobre o branco */
  --on-brand:         #FFFFFF;  /* texto sobre --brand-blue / --brand-navy */

  /* Fundos suaves */
  --info-tint:    #E8EFFA;  /* item atual do menu, etiqueta de filtro, selo "Validada", hover do secundário */
  --success-tint: #EDF7F1;  /* selo "Disponível para replicação", alerta de sucesso, variação de alta */
  --warning-tint: #FBF3E0;  /* selo "Em teste", alerta de aviso */
  --error-tint:   #FBEAE9;  /* alerta e resumo de erros, hover do botão de perigo, variação de queda */

  /* Gráficos e medidores */
  --trilho: #EEF2F8;        /* trilho das barras; a barra usa uma cor de texto da paleta */
}

/* Alto contraste (§5.5): os mesmos tokens, outros valores. */
:root[data-contraste="alto"] {
  --text: #FFFFFF;  --text-muted: #FFFFFF;  --brand-navy: #FFFFFF;
  --bg: #000000;    --surface: #000000;
  --border: #FFFFFF;  --borda-campo: #FFFFFF;
  --brand-blue: #FFFF00;  --brand-blue-hover: #FFFF00;  --on-brand: #000000;
  --success: #FFFFFF;  --warning: #FFFFFF;  --error: #FFFF00;  --info: #FFFFFF;
  --info-tint: #000000;  --success-tint: #000000;  --warning-tint: #000000;  --error-tint: #000000;
  --trilho: #000000;
  --brand-gradient: none;
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
| Texto secundário (v2) | `--text-muted` #566072 | `--bg` #F0F5FC | ~5.8:1 | ✔ AA |
| Texto branco em botão, hover (v2) | #FFFFFF | `--brand-blue-hover` #28529A | ~7.6:1 | ✔ AA/AAA |
| Borda de campo (v2, componente) | `--borda-campo` #7A879B | `--surface` #FFFFFF | ~3.6:1 | ✔ 3:1 |
| Borda de campo (v2, componente) | `--borda-campo` #7A879B | `--bg` #F0F5FC | ~3.3:1 | ✔ 3:1 |
| Mensagem de erro do campo (v2) | `--error` #B3261E | `--surface` | ~6.5:1 | ✔ AA |
| Texto de sucesso (v2) | `--success` #1E7D46 | `--surface` | ~5.2:1 | ✔ AA |
| Texto de aviso (v2) | `--warning` #8A5A00 | `--surface` | ~5.9:1 | ✔ AA |
| Selo "Em teste" (v2) | `--warning` #8A5A00 | `--warning-tint` #FBF3E0 | ~5.4:1 | ✔ AA |
| Selo "Validada" (v2) | `--info` #2E5EAA | `--info-tint` #E8EFFA | ~5.5:1 | ✔ AA |
| Selo "Disponível para replicação" (v2) | `--success` #1E7D46 | `--success-tint` #EDF7F1 | ~4.7:1 | ✔ AA (margem curta: não escurecer o fundo) |
| Menu atual, etiqueta de filtro (v2) | `--brand-navy` #1E3A6E | `--info-tint` #E8EFFA | ~9.6:1 | ✔ AA/AAA |
| Texto secundário em fundo suave (v2) | `--text-muted` #566072 | `--info-tint` #E8EFFA | ~5.5:1 | ✔ AA |
| Marca da página atual no menu (v2, componente) | `--brand-blue` #2E5EAA | `--info-tint` #E8EFFA | ~5.5:1 | ✔ 3:1 |
| Alerta / resumo de erros (v2) | `--text` #1A2332 | `--error-tint` #FBEAE9 | ~13.6:1 | ✔ AA/AAA |
| Título do alerta de erro, variação de queda (v2) | `--error` #B3261E | `--error-tint` #FBEAE9 | ~5.6:1 | ✔ AA |
| Alerta de sucesso (v2) | `--text` #1A2332 | `--success-tint` #EDF7F1 | ~14.4:1 | ✔ AA/AAA |
| Variação de alta (v2) | `--success` #1E7D46 | `--success-tint` #EDF7F1 | ~4.7:1 | ✔ AA |
| Botão desabilitado (v2) | `--text-muted` #566072 | `--bg` #F0F5FC | ~5.8:1 | ✔ AA (o critério isenta, mas o rótulo fica legível) |
| Barra de gráfico (v2, componente) | `--brand-navy` #1E3A6E | `--trilho` #EEF2F8 | ~9.9:1 | ✔ 3:1 |
| Barra de gráfico (v2, componente) | `--brand-blue` #2E5EAA | `--trilho` #EEF2F8 | ~5.7:1 | ✔ 3:1 |
| Barra de status "Em teste" (v2, componente) | `--warning` #8A5A00 | `--trilho` #EEF2F8 | ~5.3:1 | ✔ 3:1 |
| Barra de status "Disponível" (v2, componente) | `--success` #1E7D46 | `--trilho` #EEF2F8 | ~4.6:1 | ✔ 3:1 |
| Texto e foco na barra de acessibilidade (v2) | #FFFFFF | `--brand-navy` #1E3A6E | ~11:1 | ✔ AA/AAA |
| Alto contraste: texto (v2) | #FFFFFF | #000000 | 21:1 | ✔ AAA |
| Alto contraste: link, foco, erro (v2) | #FFFF00 | #000000 | ~19.6:1 | ✔ AAA |
| Alto contraste: texto do botão primário (v2) | #000000 | #FFFF00 | ~19.6:1 | ✔ AAA |

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

## 4. Espaçamento, grid e forma

Escala base de 4px: `4 · 8 · 12 · 16 · 24 · 32 · 48`. Conteúdo com largura máxima confortável de
leitura (~1100px) centralizado; margens generosas (H8).

### Tokens de forma e números (v2)

```css
:root {
  --raio-cartao: 16px;      /* cartões, painéis, resumo de erros */
  --raio-pilula: 999px;     /* selos, etiquetas de filtro, variação */
  --numeros: tabular-nums;  /* font-variant-numeric de todo número que se compara */
}
```

- Botões e campos seguem com o `--raio` atual; só cartões e painéis ganham 16px.
- `font-variant-numeric: var(--numeros)` vale para: número do cartão de indicador, colunas
  numéricas de tabela, contagens ("12 inovações encontradas"), datas e horas, paginação e valores
  ao lado das barras. Com algarismos de largura fixa, colunas e totais alinham.
- Alvo de toque e clique com 44px de altura mínima (botões, itens de menu, links de paginação,
  botão de remover etiqueta incluído na área da etiqueta).

---

## 5. Layout base

Toda tela usa HTML semântico com marcos (landmarks): `header`, `nav`, `main`, `footer`.

Ordem de cima para baixo, igual em todas as telas autenticadas:

1. barra de acessibilidade (§5.1);
2. faixa de 4px com `--brand-gradient` (decorativa, sem texto);
3. cabeçalho do sistema: logo, menu principal (§5.2), usuário;
4. `main id="conteudo"`, que abre com o cabeçalho de página (§5.3);
5. rodapé.

- **Cabeçalho:** logo KIRA à esquerda (link para a home), navegação principal, menu do usuário à direita.
- **Usuário no cabeçalho:** nome completo (ou o nome de usuário, se o nome estiver vazio) e o botão
  "Sair" (secundário, pequeno). Iniciais num círculo `--brand-navy` são decorativas (`aria-hidden`).
  A unidade da conta não aparece no cabeçalho: ela é opcional (só o gestor de unidade precisa
  de uma) e o gestor a vê em "Minha unidade" (§10).
- **Administração:** só para o perfil ADMINISTRADOR (nunca por `is_staff`), um link "Administração"
  entre o nome e o "Sair", com o ícone de engrenagem decorativo (`aria-hidden`), que leva ao admin
  (`/admin/`). Cor e sublinhado são os dos links da casca, inclusive no alto contraste. O admin se
  identifica como "KIRA — Administração" e o "Ver o site" volta à lista de inovações.
- **Navegação consistente** em todas as telas (H4 — consistência; eMAG — apresentação consistente).
- **Pular para o conteúdo:** primeiro link focável da página, "Ir para o conteúdo", dentro da barra de acessibilidade (§5.1) (eMAG; WCAG 2.4.1).
- **Idioma:** `<html lang="pt-br">`.
- **Título de página** único e descritivo por tela (WCAG 2.4.2), refletindo onde o usuário está (H1 — visibilidade do status). Formato: `<h1 da tela> · KIRA`; com erro de formulário, `Erro: <h1 da tela> · KIRA`.
- **Rodapé:** identificação do sistema ("KIRA · Repositório de Inovações · uso interno") e links "Acessibilidade" e "Ajuda".

### 5.1 Barra de acessibilidade (eMAG)

Faixa `--brand-navy` acima do cabeçalho, texto branco 14px, presente em todas as telas, inclusive
o login.

- À esquerda, `nav aria-label="Atalhos de acessibilidade"` com os atalhos do eMAG:

  | Link | Destino | `accesskey` |
  | ---- | ------- | ----------- |
  | Ir para o conteúdo `1` | `#conteudo` (o `main`) | `1` |
  | Ir para o menu `2` | `#menu` (o menu principal) | `2` |
  | Ir para a busca `3` | `#id_q` (campo de busca da lista) | `3` |

- O número aparece num `kbd` ao lado do texto. O atalho é o `accesskey` do link, e não um ouvinte
  global de teclado: o navegador decide a combinação (Alt+n no Chrome e no Edge do Windows,
  Alt+Shift+n no Firefox, Control+Option+n no macOS). A página "Acessibilidade" explica isso.
- O alvo de cada atalho recebe foco ao ser alcançado (`tabindex="-1"` no `main` e no `nav`).
- Só existe atalho para o que existe na tela: o login tem só o `1`. Fora da lista, o `3` leva à
  busca da lista (`/inovacoes/#id_q`), porque a busca só existe lá.
- À direita: link "Acessibilidade" (§5.4) e o botão "Alto contraste" (§5.5).
- Foco nessa faixa: anel branco (11:1 sobre o navy).

### 5.2 Menu principal

`nav id="menu" aria-label="Principal"`, com três itens, sempre ícone **e** texto, e um quarto
só para o gestor de unidade:

| Item | Ícone (traço) | Destino |
| ---- | ------------- | ------- |
| Inovações | lâmpada | lista |
| Cadastrar inovação | círculo com "+" | formulário de cadastro |
| Indicadores | barras | painel |
| Minha unidade | pessoas (Lucide `users`) | área do gestor (`/minha-unidade/`) |

- **"Minha unidade"** vem depois de "Indicadores" e existe só para o perfil "Gestor de unidade":
  o critério é o perfil, nunca `is_staff` ou `is_superuser`. Os outros perfis não têm o item nem
  o link no HTML.

- **Página atual:** o item recebe `aria-current="page"` quando a tela é o próprio destino, e
  `aria-current="true"` quando a tela pertence à seção (detalhe, edição, avançar status,
  sinalizar, excluir pertencem a "Inovações"; criar conta e redefinir senha pertencem a "Minha
  unidade").
- **Sinal além da cor:** o item atual tem fundo `--info-tint` **e** uma barra de 3px
  `--brand-blue` na base (forma, 5.5:1 sobre o fundo). A barra continua no alto contraste.
- Estados: padrão (texto `--brand-navy`, peso 600), hover (fundo `--bg`), foco (anel padrão),
  atual (acima).
- Ícone `aria-hidden="true"`; o nome acessível é o texto. Em tela estreita os itens quebram de
  linha; o menu nunca vira só ícones.

### 5.3 Cabeçalho de página

Abre o `main` de toda tela autenticada, sempre na mesma ordem (DOM e visual):

1. **Trilha de navegação:** `nav aria-label="Você está em"` com uma `ol`; separador "›" por CSS;
   o último item é texto com `aria-current="page"`, sem link. A raiz é "Inovações" (a home
   redireciona para a lista); telas de primeiro nível mostram só o item atual, para o cabeçalho
   ter a mesma forma em todas.
2. **h1**, único na página, `--fs-2xl`, `--brand-navy`.
3. **Descrição** opcional, uma linha em `--text-muted`.
4. **Ação principal à direita**, alinhada à base do bloco de título: um botão primário, quando a
   tela tem uma. Em tela estreita ela desce para baixo da descrição.

Trilhas:

| Tela | Trilha |
| ---- | ------ |
| Lista | Inovações |
| Detalhe | Inovações › {título} |
| Cadastrar | Inovações › Cadastrar inovação |
| Editar | Inovações › {título} › Editar |
| Avançar status | Inovações › {título} › Avançar status |
| Sinalizar reaproveitamento | Inovações › {título} › Sinalizar reaproveitamento |
| Excluir | Inovações › {título} › Excluir |
| Indicadores | Indicadores |
| Acessibilidade | Acessibilidade |
| Minha unidade | Minha unidade |
| Criar conta | Minha unidade › Criar conta |
| Redefinir senha | Minha unidade › Redefinir senha |
| Trocar senha | Trocar senha |

As páginas de recusa ("Acesso restrito", "Conta não encontrada") não têm trilha, como toda 403 e
404.

A mensagem de feedback de uma ação (§6, alerta) aparece logo acima do cabeçalho de página.

### 5.4 Página "Acessibilidade"

Rota pública (`login_not_required`), porque o login aponta para ela. Usa o layout base; sem
sessão, o cabeçalho mostra só a logo, sem menu nem usuário. Trilha "Acessibilidade", h1
"Acessibilidade". Conteúdo, em seções com h2:

- **Compromisso:** o sistema segue o eMAG e a WCAG 2.1 nível AA.
- **Atalhos de teclado:** tabela com os três atalhos e a combinação por navegador (§5.1).
- **Alto contraste:** onde fica o botão e o que ele muda.
- **Ampliação:** zoom do navegador até 200% sem perda de conteúdo.
- **Relatar uma barreira:** a quem recorrer (o administrador do sistema).

### 5.5 Alto contraste

- Botão "Alto contraste" na barra de acessibilidade, com ícone de meio círculo e
  `aria-pressed="true|false"`.
- Ativo, o `html` recebe `data-contraste="alto"` e os tokens trocam de valor (§2): fundo preto,
  texto branco, links, foco e erro em amarelo, links sempre sublinhados.
- O gradiente, as formas decorativas do login e a ilustração do estado vazio somem
  (`--brand-gradient: none`; decorativos com `display: none`).
- Selos, alertas e variações mantêm ícone e texto; perdem o fundo e ganham borda de 1px na cor
  do texto. Barras de gráfico ficam brancas sobre preto, com borda.
- A escolha persiste entre páginas (cookie, lido no servidor para o primeiro desenho já vir em
  alto contraste, sem piscar).

---

## 6. Componentes

Cada componente é reutilizável e tem todos os estados definidos. As telas estendem estes
componentes; não recriam estilo.

### Botão
- **Primário:** fundo `--brand-blue`, texto `--on-brand`. Ação principal da tela (uma por contexto).
- **Secundário:** contorno `--brand-blue`, texto `--brand-blue`, fundo `--surface`.
- **Perigo:** contorno e texto `--error`, fundo `--surface`; hover com fundo `--error-tint`. Só para ações destrutivas. No passo de confirmação da exclusão, vira cheio: fundo `--error`, texto branco.
- **Estados:** hover (primário: fundo `--brand-blue-hover`; secundário: fundo `--info-tint`), **foco visível** (anel de 2px `--brand-blue` com afastamento de 2px, contraste ≥ 3:1), ativo, desabilitado (fundo `--bg`, texto `--text-muted`, cursor `not-allowed` + `aria-disabled`).
- Ícone opcional à esquerda, `aria-hidden`. Rótulo em texto, nunca só ícone sem rótulo acessível.

### Campo de formulário
- **Rótulo sempre visível**, associado ao campo por `for`/`id` (eMAG; WCAG 1.3.1, 3.3.2). Placeholder não substitui rótulo.
- Campo obrigatório indicado por texto ("obrigatório") ou asterisco **com legenda**, não só por cor.
- Borda de 1.5px `--borda-campo` (3:1); foco com o anel padrão.
- Ordem: rótulo → ajuda → campo → erro. A ajuda vem antes do campo para ser lida antes de digitar; `aria-describedby` aponta para o erro e depois para a ajuda.
- **Estado de erro:** borda `--error` de 2px + `aria-invalid="true"` + mensagem de texto abaixo, ligada por `aria-describedby`, dizendo o que corrigir (H5 prevenção, H9 recuperação; WCAG 3.3.1, 3.3.3). Os dados já digitados são preservados (RF13).
- Dica de preenchimento / ajuda contextual quando útil (RF15, H10).

### Mensagem de feedback (alerta)
- Quatro variantes: sucesso, aviso, erro, informação.
- Sempre **ícone + texto + borda colorida à esquerda** — a cor é reforço, não a única pista (WCAG 1.4.1; eMAG).
- Fundo no tint da variante (`--success-tint`, `--warning-tint`, `--error-tint`, `--info-tint`); texto `--text`.
- Mensagens dinâmicas anunciadas por `aria-live` (leitor de tela percebe a mudança).
- Exibida após cada ação relevante: cadastro, edição, exclusão, mudança de status (RF12, H1).

### Cartão
- Superfície `--surface`, borda `--border`, `--raio-cartao`, sombra discreta. Usado em listagem, detalhe e painel.

### Tabela
- `caption` descritivo, `th` com `scope`, cabeçalho fixo quando longa. Zebra só com contraste suficiente. Alternativa a tabela em telas estreitas (ver responsividade).
- Colunas numéricas alinhadas à direita, com `--numeros`. Tabela larga rola dentro da própria caixa, nunca a página.

### Badge de status (selo)
- Rótulo textual sempre presente ("Em teste", "Validada", "Disponível para replicação") + cor + forma/ícone. Nunca a cor sozinha.
- Formato pílula (`--raio-pilula`). Ícone por status: frasco (Em teste), visto (Validada), seta saindo de caixa (Disponível para replicação). Cores conforme a tabela da §2.

### Cartão de inovação (v2)
Item da lista de resultados (`li` > `article`).
- **Conteúdo, nesta ordem:** selo de status e data de cadastro na mesma linha; título (`h2`, link para o detalhe); resumo; rodapé de metadados separado por um divisor, com ícone + texto: unidade de origem, categoria, número de reaproveitamentos ("Nenhum reaproveitamento", "1 reaproveitamento", "5 reaproveitamentos").
- **Resumo:** o início do campo "Problema ou dor", cortado no servidor em ~160 caracteres com "…". O texto completo fica no detalhe.
- **Link:** só o título é link; o cartão inteiro não vira um link gigante. O cartão mantém a altura da linha da grade.
- **Estados:** padrão; hover (borda `--brand-blue`, título sublinhado); foco (anel no link do título); carregando (esqueleto com a mesma geometria, `aria-hidden`, e o anúncio fica no contador de resultados).

### Indicador de etapas (v2)
Mostra o ciclo de vida: Em teste → Validada → Disponível para replicação.
- `ol` vertical; cada etapa com um marcador circular de 32px ligado ao próximo por uma linha.
- **Estados da etapa:** concluída (marcador `--success` com visto, texto "· concluída"); atual (marcador cheio, ícone do status, texto em negrito e "(status atual)", `aria-current="step"`); futura (marcador vazado `--borda-campo`, texto "· próxima etapa").
- A situação de cada etapa está no texto, não só no marcador (o marcador é `aria-hidden`).

### Linha do tempo (v2)
Histórico de status em ordem cronológica, do mais antigo ao mais recente (STAT-24).
- `ol`; cada item tem um ponto de 20px ligado ao próximo por uma linha de 2px `--border` (decorativos), a data e hora num `time` em negrito com `--numeros` e a frase do evento.
- **Itens:** o primeiro é o cadastro ("Cadastrada como “Em teste”, por {autor}"), com ponto vazado `--borda-campo`; os seguintes vêm de cada mudança de status ("De “Validada” para “Disponível para replicação”, por {responsável}"), com ponto `--brand-blue`.
- **Vazio:** sem mudanças, aparece só o item do cadastro.

### Cartão de contato (v2)
- Cartão com borda superior de 4px `--brand-blue` (o contato fica em destaque, F3) e título "Contato responsável".
- Mostra o texto livre do campo `contato` como foi digitado, em `--fs-base`, preservando quebras de linha. Não separa nome, e-mail ou ramal, nem inventa cargo ou foto: o campo é um texto só.
- Abaixo, uma linha em `--text-muted`: "Procure esta pessoa para tirar dúvidas antes de replicar."

### Fieldset com legenda (v2)
- `fieldset` sem borda própria; entre dois fieldsets, um divisor `--border`. Respiro interno de 28px.
- `legend` em `--fs-lg`, peso 700, `--brand-navy`, precedida de um número em círculo `--info-tint` (decorativo, `aria-hidden`). O texto da legenda é o nome do grupo, sem o número.
- **Estados:** padrão; com erro dentro (a legenda não muda; os campos mostram o erro e o resumo no topo lista os campos).

### Etiqueta de filtro ativo (v2)
Uma por filtro aplicado na lista (busca, categoria, unidade, status).
- Pílula `--info-tint`, texto `--brand-navy`, peso 600: "Categoria: Financeiro".
- A remoção é um **link** com ícone "×" e nome acessível completo ("Remover filtro Categoria: Financeiro"), que leva à mesma lista sem aquele parâmetro. Funciona sem JavaScript.
- Grupo rotulado "Filtros ativos:", seguido do link "Limpar filtros" quando há pelo menos uma etiqueta. Sem filtros, o grupo não aparece.
- **Estados:** padrão; hover do "×" (fundo `--border`); foco (anel no "×").

### Resumo de erros (v2)
Aparece no topo do formulário quando o envio falha.
- Cartão `--error-tint`, borda `--error`, ícone de alerta, `role="alert"`, `tabindex="-1"`; recebe foco ao carregar a página com erro.
- Título: "Não foi possível salvar a inovação. Corrija {n} campo(s):" e uma lista de links, um por campo com erro, no formato "{rótulo}: {mensagem}", apontando para o `id` do campo. Erros gerais, sem campo, entram na lista como texto, sem link.
- A ordem da lista é a ordem dos campos no formulário. O título da página ganha o prefixo "Erro:".
- Sem erro, não existe no DOM.

### Barra de ações (v2)
Fecha todo formulário.
- Faixa com fundo `--bg` e divisor superior, dentro do cartão do formulário.
- Ordem: botão primário (enviar), botão secundário "Cancelar" (link de volta, sem gravar) e, à direita, a nota "Nada é gravado se você cancelar."
- Não fica fixa na tela: com zoom de 200% ela cobriria os campos.

### Cartão de indicador com variação (v2)
- Rótulo (`h2`, `--fs-base`, peso 600, `--text`), número em destaque (~40px, peso 800, `--brand-navy`, `--numeros`) e uma linha de variação.
- **Variação:** pílula com seta e sinal + frase que compara os últimos 30 dias com os 30 anteriores, ex.: "+5 · 8 nos últimos 30 dias, 3 nos 30 anteriores".
- **Estados da variação:** alta (seta para cima, `--success` sobre `--success-tint`); queda (seta para baixo, `--error` sobre `--error-tint`); igual (traço, `--text-muted` sobre `--bg`, "igual aos 30 dias anteriores"); sem base (sem pílula, "Sem cadastros nos 30 dias anteriores para comparar"). A direção está no sinal e no texto, não só na cor e na seta.
- **Drill-down:** quando o número corresponde a um filtro da lista, o cartão tem um link "Ver na lista" (nome acessível completo, ex.: "Ver na lista as inovações disponíveis para replicação").

---

## 7. Estados de tela

- **Vazio:** mensagem clara do que aconteceu e o próximo passo (ex.: "Nenhuma inovação encontrada. Cadastre a primeira."), com ação visível. (H1, H10)
  - Na lista, uma ilustração SVG decorativa (`aria-hidden="true"`, traço `--brand-navy`, acentos `--brand-blue-light`) acima da mensagem, até 160px de altura. Some no alto contraste.
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
- Mudar um filtro não envia o formulário sozinho (WCAG 3.2.2): o envio é pelo botão.

**Robusto**
- HTML semântico e marcos (`header`/`nav`/`main`/`footer`).
- Estados e mensagens dinâmicas expostos por ARIA (`aria-describedby`, `aria-live`, `aria-disabled`).

**eMAG (ênfases do modelo brasileiro)**
- Marcação: HTML semântico, landmarks, ordem de leitura coerente com a visual.
- Comportamento: foco visível, navegação por teclado, link de pular para o conteúdo.
- Conteúdo/Informação: linguagem clara, não depender de cor, descrever a página.
- Apresentação/Design: contraste adequado, layout consistente.
- Formulários: rótulos, agrupamento lógico, mensagens de erro claras.
- Recursos do modelo: barra de acessibilidade com atalhos `accesskey` 1, 2 e 3 (§5.1), página "Acessibilidade" (§5.4) e opção de alto contraste (§5.5).

---

## 9. Aderência às 10 heurísticas de Nielsen

Mapa das heurísticas para decisões concretas deste sistema. Serve à avaliação heurística do RNF01
e à defesa na banca.

| # | Heurística | Como o design atende | Requisitos |
| - | ---------- | -------------------- | ---------- |
| H1 | Visibilidade do status | título de página, trilha, item atual do menu, feedback após cada ação, estados de carregando/vazio, indicador de etapas | RF12, RF09 |
| H2 | Correspondência com o mundo real | vocabulário do domínio (categoria, unidade, status), narrativa problema → solução → resultado, ajuda contextual | RF15, RN07 |
| H3 | Controle e liberdade | cancelar/voltar nos formulários, remover filtro por etiqueta, confirmação antes de excluir | RF14, RN12 |
| H4 | Consistência e padrões | cabeçalho de página, navegação e componentes reutilizados em todas as telas | RNF01, RNF04, RN07 |
| H5 | Prevenção de erros | validação, confirmação de ações destrutivas, perigo separado das demais ações, listas controladas | RF13, RF14, RN02, RN10, RN12 |
| H6 | Reconhecimento em vez de memorização | filtros por lista, etiquetas de filtro ativo, rótulos descritivos, dicas | RF06, RF15, RN07 |
| H7 | Flexibilidade e eficiência | busca + filtros combinados, atalhos de teclado, drill-down do painel para a lista | RF05, RF06 |
| H8 | Estético e minimalista | layout limpo, respiro, informação resumida na listagem, tabelas do painel recolhidas | RNF01, RF03 |
| H9 | Reconhecer e recuperar-se de erros | resumo de erros com links para os campos, mensagens em texto claro indicando campo e correção | RF13, RF12 |
| H10 | Ajuda e documentação | textos de apoio e exemplos nos campos e filtros, página "Acessibilidade" | RF15 |

---

## 10. Telas

O que é específico de cada tela. A parte global (§2–§8) vale para todas. Listas e campos são os
reais: categorias Atendimento interno, Compras, Financeiro, RH, TI interno; unidades Filial Leste,
Filial Norte, Filial Oeste, Filial Sul, Sede (provisórias, o administrador as renomeia); status
Em teste, Validada, Disponível para replicação.

### Login (F1)

- **Tela dividida** num cartão com `--raio-cartao` maior (24px), centralizado: painel de marca à
  esquerda, formulário à direita, cada um com metade da largura.
- **Painel de marca:** fundo `--brand-navy` sólido, texto branco (11:1). Logo, nome KIRA e
  tagline (o itálico da marca); uma frase curta ("Antes de resolver do zero, veja quem já
  resolveu.") e três linhas com ícone: encontrar soluções que outras unidades já testaram,
  registrar o que funcionou, acompanhar o que já foi replicado. Os textos são `p`, não títulos:
  o primeiro título da página é o h1 "Entrar".
- **Gradiente só decorativo:** formas circulares com `--brand-gradient` no canto inferior do
  painel, `aria-hidden`, sem nenhum texto por cima. Somem no alto contraste.
- **Formulário:** h1 "Entrar"; linha "Use seu usuário ou e-mail institucional."; nota "Os dois
  campos são obrigatórios."; campos "Usuário ou e-mail" (`autocomplete="username"`) e "Senha"
  (`autocomplete="current-password"`) com um botão "Mostrar" ao lado (`aria-pressed`,
  `aria-controls`); botão primário "Entrar" na largura do formulário; abaixo, separado por um
  divisor, "Problemas para entrar? Fale com o administrador do sistema."
- **Credencial inválida:** alerta de erro acima dos campos, sem revelar qual campo falhou (por
  segurança). O usuário digitado é preservado; a senha, não.
- **Barra de acessibilidade** só com "Ir para o conteúdo `1`", "Acessibilidade" e "Alto
  contraste". Sem menu e sem usuário no cabeçalho.
- **Tela estreita (< 720px):** o painel vira uma faixa curta acima do formulário, só com logo e
  tagline; a frase e a lista somem.

### Lista de inovações (F3)

- **Cabeçalho de página:** trilha "Inovações", h1 "Inovações", descrição "Encontre soluções que
  outras unidades já testaram antes de começar do zero.", ação principal "Cadastrar inovação".
- **Busca em destaque:** cartão `form role="search"` logo abaixo do cabeçalho. Campo
  "Buscar" (`q`, `id="id_q"`, alvo do atalho `3`), maior que os demais (52px de altura, ícone de
  lupa decorativo à esquerda, 17px), com a ajuda atual ("Procura em título, problema e solução.
  Ex.: planilha conciliação") e o botão primário "Buscar" ao lado.
- **Filtros em linha:** no mesmo formulário, abaixo da busca, três selects lado a lado em grade
  que quebra em telas estreitas: Categoria ("Todas as categorias"), Unidade
  ("Todas as unidades"), Status ("Todos os status"). O botão "Buscar" aplica busca e filtros
  juntos; mudar um select não envia nada.
- **Etiquetas de filtro ativo** no rodapé do cartão de busca (§6), com "Limpar filtros".
- **Barra de resultados:** contador `role="status"` ("12 inovações encontradas", `--numeros`) e,
  à direita, o alternador "Cartões | Tabela": dois links com ícone e texto, o atual com
  `aria-current="true"` e fundo `--brand-navy`. A escolha vai na URL (`exibicao=tabela`) e
  sobrevive à paginação e aos filtros.
- **Cartões (padrão):** grade de cartões de inovação (§6), `ul aria-label="Resultados"`,
  colunas automáticas com mínimo de 320px, ordem mais recentes primeiro (CONS-02).
- **Tabela (alternativa):** `caption` "Inovações encontradas"; colunas Título (link), Status
  (selo), Unidade de origem, Categoria, Cadastrada em, Reaproveitamentos. Mesmos itens e ordem
  dos cartões.
- **Paginação** (20 por página): "Anterior", números das páginas (o atual com
  `aria-current="page"`), "Próxima"; abaixo, "Página 1 de 3". "Anterior" na primeira página é
  texto desabilitado, não link.
- **Estado vazio** com ilustração decorativa (§7), em duas variantes:
  - acervo vazio: "Nenhuma inovação cadastrada ainda." + botão "Cadastrar a primeira inovação";
  - sem resultado para a busca ou os filtros: "Nenhuma inovação encontrada para esta busca." +
    sugestão "Tente outras palavras ou remova algum filtro." + link "Limpar filtros". As
    etiquetas continuam visíveis.

### Detalhe da inovação (F3, F4, F5, F6)

- **Cabeçalho de página:** trilha "Inovações › {título}"; selo de status acima do h1; h1 com o
  título; linha em `--text-muted` "Cadastrada por {autor} em {data} · {unidade de origem} ·
  {categoria}".
- **Ações em hierarquia**, à direita do cabeçalho:
  - **primária** (uma, conforme o status): "Avançar para “{próximo status}”" em Em teste e
    Validada, só para quem pode alterar (autor, gestor da unidade de origem ou administrador,
    RN05); "Sinalizar reaproveitamento" em Disponível para replicação, para qualquer usuário
    (RN09);
  - **secundária:** "Editar", só para quem pode alterar;
  - **perigo separada:** "Excluir", por último, afastada das outras por um divisor vertical e
    32px de respiro. Leva à confirmação (F4).
  - Usuário sem permissão não vê Editar, Excluir nem Avançar.
- **Coluna principal (≈ 2/3):**
  - **Narrativa Problema → Solução → Resultado:** um cartão "Como a inovação funciona" com três
    passos numerados ligados por uma linha (decorativa): h3 "Problema ou dor", "Solução
    aplicada", "Resultado ou impacto", cada um com o texto completo. Resultado vazio (é
    opcional, INOV-14): "Resultado ainda não informado." em `--text-muted`.
  - **Reaproveitamentos ({n}):** cartão com tabela Unidade, Registrado por, Data (`caption`
    visualmente oculto). Vazio: "Nenhum reaproveitamento registrado."
  - **Histórico de status:** linha do tempo (§6).
- **Coluna lateral (≈ 1/3, `aside aria-label="Resumo da inovação"`):**
  - **Ciclo de vida:** indicador de etapas (§6). No último estágio, o botão desabilitado
    "Avançar status" com a explicação "Último estágio do ciclo. O status avança um estágio por
    vez e não volta." (F5: desabilitado, não escondido). Para quem não pode alterar: "Só quem
    cadastrou a inovação, um gestor da unidade de origem ou um administrador pode avançar o
    status."
  - **Contato responsável:** cartão de contato (§6).
  - **Ficha:** `dl` com Unidade de origem, Categoria, Cadastrada por, Cadastrada em,
    Reaproveitamentos (`--numeros`).
- **Tela estreita:** uma coluna; a lateral vem depois da narrativa, com o contato em primeiro.
- O alerta de feedback (avanço de status, reaproveitamento registrado, edição salva) aparece
  acima do cabeçalho de página.

### Formulários: cadastrar e editar (F2, F4)

O mesmo formulário serve às duas telas.

- **Cabeçalho de página:** trilha (§5.3); h1 "Cadastrar inovação" ou "Editar inovação";
  descrição "Conte a história na ordem problema → solução → resultado: fica mais fácil para outra
  unidade reaproveitar."
- **Resumo de erros** no topo, entre o cabeçalho e o formulário, quando o envio falha (§6).
- **Cartão do formulário**, coluna única com largura de leitura (~720px):
  - nota inicial: "Campos marcados com “obrigatório” precisam ser preenchidos. Autor, data e
    status inicial (“Em teste”) são preenchidos pelo sistema.";
  - **fieldset "Identificação":** Título (obrigatório; ajuda "Um nome curto que diga o que mudou.
    Ex.: “Conciliação bancária automatizada”."); Unidade de origem e Categoria (obrigatórios),
    lado a lado em tela larga, selects em ordem alfabética (INOV-15) com a primeira opção
    "Selecione…";
  - **fieldset "A inovação":** Problema ou dor (obrigatório; "Como era antes? Quem era afetado e
    quanto custava em tempo, retrabalho ou erros?"); Solução aplicada (obrigatório; "O que foi
    feito, com quais ferramentas e em quais passos."); Resultado ou impacto (opcional; "Se
    puder, use números: horas economizadas, erros evitados, prazo reduzido."). Áreas de texto
    com 120px de altura mínima, redimensionáveis na vertical;
  - **fieldset "Contato":** Contato responsável (obrigatório; "Quem outra unidade deve procurar
    para tirar dúvidas: nome e e-mail, ramal ou os dois."). Um campo de texto livre só.
- **"Obrigatório" por escrito** no rótulo de cada campo obrigatório ("(obrigatório)", peso 500,
  `--text-muted`) e "(opcional)" no Resultado. Nada de asterisco.
- **Ajuda por campo** em todos os campos, na ordem do §6 (rótulo → ajuda → campo → erro).
- **Erros:** campo com borda de erro e mensagem abaixo; título duplicado na mesma unidade acusa
  no campo Título (INOV-22). Tudo o que foi digitado volta preenchido (RF13).
- **Barra de ações** (§6): "Salvar inovação" (cadastro) ou "Salvar alterações" (edição);
  "Cancelar" volta à lista (cadastro) ou ao detalhe (edição).
- Depois de salvar, o detalhe abre com o alerta de sucesso.

### Painel de indicadores (F6)

- **Cabeçalho de página:** trilha "Indicadores", h1 "Painel de indicadores", descrição "Dados de
  {data e hora}. Os números se atualizam a cada visita." (REAP-38). Sem ação principal.
- **Cartões com variação** (§6), numa grade de colunas automáticas (mínimo 250px):
  - Inovações cadastradas: total; variação de cadastros nos últimos 30 dias contra os 30
    anteriores; "Ver na lista" leva à lista sem filtros.
  - Reaproveitamentos: total; variação de sinalizações no mesmo critério; sem drill-down (a lista
    não filtra por reaproveitamento).
  - Disponíveis para replicação: total e a fração do acervo ("35% das inovações cadastradas");
    "Ver na lista" leva a `?status=DISPONIVEL_PARA_REPLICACAO`.
- **Gráficos em grade**, colunas automáticas com mínimo de 360px, um cartão por gráfico:
  - Inovações por categoria;
  - Inovações de origem por unidade;
  - Reaproveitamentos feitos por unidade;
  - Inovações por status, com a cor e o ícone de cada selo.
  Barras horizontais sobre `--trilho`, rótulo à esquerda e valor à direita (`--numeros`), maior
  valor ocupando a largura toda (REAP-35). Cada gráfico é `svg role="img"` com nome acessível
  igual ao título do cartão.
- **Drill-down para a lista filtrada:** cada linha de gráfico que corresponde a um filtro da lista
  é um link para ela, com nome acessível completo ("Financeiro: 12 inovações. Ver na lista"):
  categoria → `?categoria={id}`, unidade de origem → `?unidade={id}`, status → `?status={valor}`.
  A linha de "Reaproveitamentos feitos por unidade" não é link, porque a lista filtra pela
  unidade de origem, não pela que reaproveitou. Hover da linha: fundo `--bg`.
- **"Ver dados em tabela":** abaixo de cada gráfico, um `details` fechado com `summary` "Ver dados
  em tabela" e a tabela acessível com os mesmos números (`caption`, `th scope`, `--numeros`).
- **Painel vazio** (sem inovação, REAP-37): sem cartões de gráfico; estado vazio com
  "Ainda não há dados para o painel." e o botão "Cadastrar inovação".

### Minha unidade e contas (gestão por unidade)

Telas do gestor de unidade e a troca da própria senha. Os três formulários usam o campo, o resumo
de erros e a barra de ações da §6 v2: "(obrigatório)" por escrito no rótulo, o resumo no topo com
o título "Não foi possível {criar a conta | redefinir a senha | trocar a senha}. Corrija {n}
campo(s):" e o foco nele, e o prefixo "Erro:" no título da página. As senhas voltam vazias depois
de um envio com erro; os outros campos voltam preenchidos (RF13).

- **Minha unidade** (`/minha-unidade/`, só o gestor):
  - **Cabeçalho de página:** trilha "Minha unidade", h1 "Minha unidade", descrição com o nome da
    unidade do gestor, ação principal "Criar conta" (botão primário). A ação continua disponível
    quando a unidade só tem o gestor.
  - **Seção "Contas da unidade"** (`h2`) com a tabela (§6) de `caption` "Contas da unidade
    {nome}" e as colunas Nome, Usuário, E-mail, Perfil, Situação, Último acesso e Ações. Lista
    todas as contas da unidade, inclusive a do gestor e as desativadas, por nome completo e depois
    por usuário. Situação por escrito ("Ativa", "Desativada"), nunca só por cor; "Nunca" quando a
    conta ainda não entrou.
  - **Ações por linha**, só nas contas de perfil Usuário: o link "Redefinir senha" e um botão
    "Desativar" (conta ativa) ou "Reativar" (conta desativada), os dois secundários: desativar se
    desfaz, e o perigo da §6 é só para ação destrutiva. Sem confirmação; o botão envia o estado de
    destino e volta à lista com o alerta "Conta “{usuário}” desativada." ou "Conta “{usuário}”
    reativada.". Na linha do gestor, de outro gestor ou de um administrador, a célula fica vazia.
- **Criar conta** (`/minha-unidade/contas/nova/`):
  - **Cabeçalho de página:** trilha "Minha unidade › Criar conta", h1 "Criar conta", descrição "A
    conta nasce como Usuário da unidade {nome}.".
  - **Cartão do formulário** com dois fieldsets (§6): "Identificação" (Usuário, Nome, Sobrenome,
    E-mail) e "Senha provisória" (Senha provisória, Confirmação da senha provisória). Todos
    obrigatórios; sem campo de perfil ou de unidade.
  - **Barra de ações:** "Criar conta", "Cancelar" (volta a "Minha unidade") e a nota.
  - Depois de criar, "Minha unidade" abre com o alerta "Conta “{usuário}” criada. Informe a senha
    provisória à pessoa: ela vai trocá-la no primeiro acesso.".
- **Redefinir senha** (`/minha-unidade/contas/{id}/senha/`):
  - **Cabeçalho de página:** trilha "Minha unidade › Redefinir senha", h1 "Redefinir senha",
    descrição "Conta “{usuário}” ({nome}). A pessoa troca a senha no próximo acesso.".
  - **Cartão do formulário** com Nova senha provisória e Confirmação da nova senha provisória.
  - **Barra de ações:** "Redefinir senha", "Cancelar" (volta a "Minha unidade") e a nota.
  - Depois de redefinir, "Minha unidade" abre com o alerta "Senha de “{usuário}” redefinida.
    Informe a senha provisória à pessoa.".
- **Trocar senha** (`/conta/senha/`, qualquer conta autenticada):
  - **Cabeçalho de página:** trilha "Trocar senha" (primeiro nível), h1 "Trocar senha".
  - **Com senha provisória:** alerta de aviso (§6) "Sua senha é provisória. Defina uma nova senha
    para continuar." entre o resumo de erros e o cartão. Toda outra tela interna leva de volta a
    esta até a troca; "Sair" continua disponível.
  - **Cartão do formulário** com Senha atual, Nova senha e Confirmação da nova senha.
  - **Barra de ações:** "Trocar senha"; sem senha provisória, também "Cancelar" (volta à lista de
    inovações) e a nota. Com senha provisória, a barra não tem "Cancelar" nem a nota: cancelar
    cairia de novo aqui.
  - Depois de trocar, a sessão continua aberta e a lista de inovações abre com o alerta "Senha
    alterada.".
- **Acesso restrito** (403, quem não é gestor em qualquer tela de "Minha unidade"): h1 "Acesso
  restrito", sem trilha; cartão de estado de erro com "Acesso restrito a gestores de unidade." e o
  link "Voltar para as inovações".
- **Conta não encontrada** (404, conta de outra unidade, fora do alcance do gestor ou
  inexistente): h1 "Conta não encontrada", sem trilha; cartão de estado de erro com "Esta conta
  não existe ou não pertence à sua unidade." e o link "Voltar para Minha unidade".
