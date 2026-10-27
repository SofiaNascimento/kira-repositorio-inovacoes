# Roteiro de deploy: Supabase + Vercel

Passo a passo para publicar o KIRA pela primeira vez. O banco fica no Supabase e a aplicação na
Vercel, ambos no plano gratuito. O deploy sai da sua máquina pela **Vercel CLI**, sem GitHub: as
duas contas são criadas por e-mail. Leva de 30 a 45 minutos.

Os nomes de menus e botões são os da documentação oficial consultada em 27/10/2026. Se a tela
estiver diferente, procure pelo nome do campo (por exemplo, "Transaction pooler").

**Convenção:** tudo entre `<sinais>` é valor seu. Troque o trecho todo, incluindo os sinais.

---

## Parte 0 — Antes de começar

1. **Node.js instalado.** A Vercel CLI roda pelo `npx`, sem instalação global. Confira com
   `node --version`; qualquer versão 20 ou mais nova serve.
2. **Python local.** Os comandos da Parte 2 rodam pelo `.venv`. Confira com
   `.venv/bin/python --version`; a saída deve ser `Python 3.13.x`.
3. **Árvore limpa.** A CLI envia a pasta do jeito que ela está, inclusive mudanças sem commit.
   Antes de cada deploy, `git status` deve sair limpo.
4. **O `.env` não sobe.** O `.vercelignore` do projeto barra o `.env` e os arquivos só de
   desenvolvimento. Não apague nem edite esse arquivo. A Parte 3.8 confere isso na nuvem.
5. **Gerenciador de senhas aberto.** Você vai gerar duas senhas que não podem se perder: a do
   banco e a `DJANGO_SECRET_KEY`.

---

## Parte 1 — Supabase (banco de dados)

### 1.1 Criar a conta e o projeto

1. Acesse `https://supabase.com`, clique em **Start your project** e use a opção de cadastro por
   **e-mail e senha** (não use "Continue with GitHub"). Confirme o e-mail pelo link que chegar.
2. Se pedir uma organização, crie uma com plano **Free**.
3. Clique em **New project** e preencha:
   - **Project name:** `kira`.
   - **Database Password:** clique em **Generate a password**, copie e guarde no gerenciador de
     senhas. Ela não aparece de novo.
   - **Region:** **South America (São Paulo)**. A Parte 3 coloca a Vercel na mesma cidade. Cada
     tela faz várias consultas, e banco e aplicação em continentes diferentes deixam cada página
     visivelmente lenta.
   - Se aparecerem opções de segurança: **desmarque Enable Data API** e **marque** a opção de
     ativar RLS automaticamente. O motivo está no passo 1.2.
4. Clique em **Create new project** e espere o provisionamento, que leva cerca de 2 minutos.

### 1.2 Desligar a Data API (segurança)

O Supabase oferece uma API REST automática (Data API) sobre as tabelas do schema `public`. As
migrations do Django criam as tabelas nesse schema, inclusive a de usuários, com os hashes de
senha, e sem RLS. O KIRA não usa essa API: ele fala direto com o Postgres. Deixá-la ligada só
abre uma porta desnecessária.

1. No menu do projeto, abra **Integrations → Data API** (endereço
   `/integrations/data_api/overview` dentro do projeto).
2. Desligue **Enable Data API** e confirme.

Depois disso, o **Security Advisor** do painel pode avisar sobre tabelas sem RLS. Com a Data API
desligada, nenhuma delas fica acessível por ela, e o aviso pode ser ignorado.

### 1.3 Copiar as strings de conexão

1. No topo da página do projeto, clique em **Connect** (em português: **Conectar**). Abre a
   janela "Conecte-se ao seu projeto", com cinco cards: Estrutura, Servidor, Direto, ORM e MCP.
2. Clique no card **Direto — Cadeia de conexão**. A janela abre na aba **Estrutura**, que é para
   apps JavaScript e não serve ao KIRA.
3. Se aparecer o aviso laranja "O acesso ao banco de dados requer a API de dados", **ignore-o e
   não clique em "Habilitar API de dados"**. Ele vale para as bibliotecas cliente; o Django fala
   direto com o Postgres, e a Data API continua desligada (passo 1.2).
4. Na aba Direto, deixe **Tipo** em **URI**. Em **Método de conexão**, marque cada opção abaixo,
   role a janela e copie a string. Guarde as duas no gerenciador de senhas:
   - **Agrupador de transações** (*transaction pooler*, porta **6543**): é a `DATABASE_URL` da Vercel.
     Formato: `postgresql://postgres.<ref>:[YOUR-PASSWORD]@aws-<n>-sa-east-1.pooler.supabase.com:6543/postgres`
   - **Agrupador de sessões** (*session pooler*, porta **5432**): é a usada nos comandos da sua
     máquina (Parte 2).
     Mesmo formato, com `:5432`.
   - **Conexão direta** (*direct connection*, host `db.<ref>.supabase.co`): não use (veja abaixo).
     O atalho "Copiar → Cadeia de conexão direta" da página inicial do projeto também é esta.
5. Confira cada string: o usuário é `postgres.<ref>` (não só `postgres`), o host termina em
   `pooler.supabase.com` e a porta é a esperada.
6. Em cada uma, troque `[YOUR-PASSWORD]` (na tela em português, `[SUA SENHA]`), com os
   colchetes, pela senha do banco.
7. Se a senha tiver caracteres especiais, codifique-os: `@` vira `%40`, `#` vira `%23`, `&` vira
   `%26`, `?` vira `%3F`, `/` vira `%2F`, `:` vira `%3A`, espaço vira `%20`. Uma senha gerada pelo
   Supabase costuma ter só letras e números.

**Por que não a "Direct connection"?** No plano gratuito ela só funciona por IPv6, e muitas redes
domésticas e corporativas só têm IPv4. Os poolers funcionam por IPv4. Se a sua rede tiver IPv6, a
direct connection também serve para a Parte 2, e é a que o Supabase recomenda para migrations.

---

## Parte 2 — Preparar o banco, da sua máquina

Todos os comandos rodam na raiz do projeto, no terminal. O Postgres local não precisa estar ligado.

**Cuidado no zsh:** cole um comando por vez, sem comentários `#`, e mantenha a URL entre **aspas
simples**.

### 2.1 Testar a conexão (só leitura)

```bash
DATABASE_URL='<string do session pooler>' .venv/bin/python manage.py showmigrations
```

O esperado é a lista das apps com `[ ]` em todas as migrations: a conexão funcionou e o banco está
vazio. Se der erro, veja a Parte 5.

### 2.2 Criar as tabelas

```bash
DATABASE_URL='<string do session pooler>' .venv/bin/python manage.py migrate
```

O esperado é uma linha `Applying ... OK` por migration, até `inovacoes.0008_reaproveitamento`. A
`inovacoes.0004_listas_iniciais` já cadastra as unidades e categorias iniciais.

### 2.3 Criar o administrador

```bash
DATABASE_URL='<string do session pooler>' .venv/bin/python manage.py createsuperuser
```

Informe usuário, e-mail e senha. A conta nasce com perfil **ADMINISTRADOR**. Use uma senha
diferente da do banco e da que você usa localmente.

### 2.4 (Opcional) Carregar a demonstração

Só se quiser as 500 inovações de exemplo da conta `demo` (RNF08) no ambiente publicado:

```bash
DATABASE_URL='<string do session pooler>' .venv/bin/python manage.py carregar_demonstracao
```

A conta `demo` não tem senha utilizável, então ninguém entra com ela. Os dados aparecem na lista
para quem estiver logado.

### 2.5 Conferir no painel

No Supabase, abra **Table Editor**. As tabelas do Django (`contas_usuario`,
`inovacoes_inovacao`, `django_migrations` e as demais) devem aparecer no schema `public`.

---

## Parte 3 — Vercel (aplicação), pela CLI

### 3.1 Gerar a chave secreta

No terminal:

```bash
.venv/bin/python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Guarde a saída no gerenciador de senhas como `DJANGO_SECRET_KEY` de produção. Ela deve ser
diferente da chave do seu `.env`.

### 3.2 Criar a conta por e-mail

1. Acesse `https://vercel.com/signup` e escolha o plano **Hobby**.
2. Escolha **Continue with Email**, informe o e-mail e digite o código de 6 dígitos que chegar.
3. Sem um provedor Git conectado, a Vercel pede esse código a cada login. É o esperado.

> Há relatos de contas novas sendo levadas para o checkout do plano Pro. Se acontecer, volte e
> procure a opção **Hobby**; o KIRA não precisa de nada pago.

### 3.3 Entrar pela CLI

Na raiz do projeto:

```bash
npx vercel login
```

Na primeira vez, o `npx` pergunta se pode baixar o pacote `vercel`: responda `y`. Escolha
**Continue with Email**, use o mesmo e-mail e confirme pelo código ou link que chegar. Para
conferir:

```bash
npx vercel whoami
```

A saída é o seu usuário na Vercel.

### 3.4 Criar e vincular o projeto

Ainda na raiz do projeto:

```bash
npx vercel link
```

Responda às perguntas assim:

- **Set up "…/kira-repositorio-inovacoes"?** → `y`
- **Which scope / team?** → a sua conta Hobby
- **Link to existing project?** → `N` (ou, se ele sugerir um projeto com o nome da pasta, `n`)
- **Name?** → `kira`
- **In which directory is your code located?** (se perguntar) → `./`
- A CLI deve mostrar **Detected Django**. Em **Customize settings?** → `N`

O comando cria a pasta `.vercel/` com o vínculo. Ela já está no `.gitignore` e não entra no
repositório.

### 3.5 Cadastrar as variáveis

Abra o projeto no painel:

```bash
npx vercel open
```

Em **Settings → Environment Variables**, adicione as cinco abaixo, marcando só o ambiente
**Production**. O endereço exato só aparece depois do primeiro deploy, então os dois valores de
domínio começam amplos (qualquer `*.vercel.app`); o passo 3.9 os restringe.

| Key | Value | Tipo |
| --- | ----- | ---- |
| `DJANGO_SECRET_KEY` | a chave do passo 3.1 | **Secret** |
| `DJANGO_DEBUG` | `False` | Config |
| `DJANGO_ALLOWED_HOSTS` | `.vercel.app` | Config |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://*.vercel.app` | Config |
| `DATABASE_URL` | a string do **transaction pooler** (porta **6543**) | **Secret** |

Atenção ao `DATABASE_URL`: aqui é a de **6543**, não a de 5432 usada na Parte 2. Cole o valor
**sem aspas**; as aspas só existiam por causa do terminal.

> Alternativa pelo terminal: `npx vercel env add DJANGO_SECRET_KEY production` pede o valor e
> grava a variável. Repita para cada uma.

### 3.6 Região da função (São Paulo)

Por padrão, a função roda nos EUA. Com o banco em São Paulo, cada consulta atravessaria o
continente.

1. No painel do projeto, abra **Settings → Functions**.
2. Em **Function Region**, escolha **São Paulo, Brazil (gru1)** e salve.

> Não confirmei se essa opção está liberada no plano Hobby. Se ela estiver bloqueada, a aplicação
> funciona igual, só mais lenta.

### 3.7 Primeiro deploy

1. Confira que a árvore está limpa:

   ```bash
   git status
   ```

2. Publique em produção, vendo o log do build:

   ```bash
   npx vercel --prod --logs
   ```

3. No log, confira:
   - a linha da versão do Python, que deve indicar **3.13**;
   - a instalação do `requirements.txt` (Django, psycopg, dj-database-url…);
   - a execução do `collectstatic` (algo como "N static files copied").
4. No fim, a CLI imprime o endereço do deploy. O deploy aparece no painel como **Ready**.

### 3.8 Conferir que o `.env` não subiu

No painel, abra **Deployments**, entre no deploy e abra a aba **Source**. Na raiz da lista de
arquivos **não** devem aparecer `.env`, `.specs`, `.claude` nem `docs`.

Se o `.env` aparecer, pare: apague esse deploy (menu `⋯` → **Delete**) e confira se o
`.vercelignore` está na raiz do projeto, sem alterações.

### 3.9 Restringir os domínios

1. No painel, veja o endereço de produção em **Settings → Domains**, por exemplo
   `kira-xyz.vercel.app`.
2. Em **Settings → Environment Variables**, edite:
   - `DJANGO_ALLOWED_HOSTS` → `kira-xyz.vercel.app`
   - `DJANGO_CSRF_TRUSTED_ORIGINS` → `https://kira-xyz.vercel.app` (com `https://` e **sem**
     barra no final)
3. Variáveis novas só valem para deploys novos. Publique de novo:

   ```bash
   npx vercel --prod
   ```

---

## Parte 4 — Conferência (UAT)

Com o endereço `https://<domínio>`:

1. **Login:** abra `https://<domínio>/entrar/`. A tela aparece com o visual do KIRA (navy/azul).
   Entre com o administrador da Parte 2.
2. **Lista:** você é levado para a lista de inovações (vazia, ou com 500 se rodou o 2.4).
3. **Cadastro:** cadastre uma inovação de teste. Salvar sem erro 403 prova que o CSRF atrás do
   proxy funciona. Ela deve aparecer na lista e no detalhe.
4. **Admin:** abra `https://<domínio>/admin/`. O admin deve aparecer com o estilo padrão do Django
   (barra azul, fontes). Se aparecer HTML cru, o `collectstatic` não rodou (Parte 5).
5. **Cookies seguros:** nas ferramentas do navegador (F12 → Application/Armazenamento → Cookies),
   `sessionid` e `csrftoken` aparecem com **Secure** marcado.
6. **Sem página de depuração:** abra `https://<domínio>/nao-existe/`. Deve aparecer a página de
   erro do projeto, nunca a página amarela de debug do Django.
7. **Sair:** clique em "Sair" e confirme que voltou ao login.
8. **Banco:** no Supabase, em Table Editor → `inovacoes_inovacao`, a inovação do passo 3 aparece.
9. **Sem `.env` no deploy:** a Parte 3.8 foi conferida.

Se você cadastrou dados de teste que não quer manter, exclua-os pelo próprio sistema.

---

## Parte 5 — Problemas comuns

Para ver o erro real de um 500, abra o deploy no painel → **Logs**, ou rode
`npx vercel logs --environment production --level error --since 15m`.

| Sintoma | Causa provável | O que fazer |
| ------- | -------------- | ----------- |
| `npx vercel` pede login de novo | Sessão da CLI expirou | `npx vercel login` |
| CLI pergunta de novo "Set up…?" | A pasta `.vercel/` foi apagada | `npx vercel link` e escolha o projeto `kira` existente (`Link to existing project? y`) |
| Build falha com `KeyError: 'DJANGO_SECRET_KEY'` | Variável ausente em Production | Cadastre-a (Parte 3.5) e publique de novo |
| `400 Bad Request` em toda página | Host fora do `DJANGO_ALLOWED_HOSTS` | Use o domínio exato, sem `https://` e sem barra; publique de novo |
| `403 Forbidden` (CSRF) ao entrar ou salvar | Origem fora do `DJANGO_CSRF_TRUSTED_ORIGINS` | Use `https://<domínio>`, sem barra final; publique de novo |
| `500` em toda página; no log, `password authentication failed` | Senha errada ou não codificada na URL | Confira `[YOUR-PASSWORD]` trocado e os caracteres especiais (Parte 1.3) |
| No log, `Tenant or user not found` | Usuário da URL sem o `.<ref>` | O usuário do pooler é `postgres.<ref>`, não só `postgres`; copie de novo do **Connect** |
| No log, `relation "..." does not exist` | Migrations não aplicadas no Supabase | Rode a Parte 2.2 |
| `showmigrations` ou `migrate` travam ou dão timeout | Rede sem IPv6 usando a direct connection | Use a string do **session pooler** (Parte 1.3) |
| Admin sem CSS | `collectstatic` não rodou no build | Procure "collectstatic" no log do build |
| Páginas lentas (mais de 2 s) | Função e banco em regiões diferentes | Parte 3.6 (gru1) e publique de novo |
| Supabase fora do ar depois de dias sem uso | Projetos gratuitos são pausados por inatividade | Painel do Supabase → **Restore project** |

---

## Parte 6 — Atualizações futuras

- **Sem deploy automático.** Sem Git conectado, nada é publicado sozinho. A cada versão: faça o
  commit, confira `git status` limpo e rode `npx vercel --prod`.
- **Mudança de model:** rode o `migrate` da Parte 2.2 **antes** do `npx vercel --prod` do código
  que depende da migration. Senão, o código novo vai procurar colunas que ainda não existem.
- **Trocar a senha do banco:** troque no Supabase, atualize a `DATABASE_URL` no painel da Vercel e
  rode `npx vercel --prod`.
- **Se o GitHub voltar:** dá para conectar o repositório em **Settings → Git** e passar a publicar
  a cada push no `main`. As variáveis e o domínio continuam os mesmos.

---

Fontes: [Vercel — Django](https://vercel.com/docs/frameworks/full-stack/django) ·
[Vercel — Python runtime](https://vercel.com/docs/functions/runtimes/python) ·
[Vercel — Deploy pela CLI](https://vercel.com/docs/projects/deploy-from-cli) ·
[Vercel — vercel deploy](https://vercel.com/docs/cli/deploy) ·
[Vercel — Arquivos ignorados](https://vercel.com/docs/deployments/build-features) ·
[Vercel — Environment variables](https://vercel.com/docs/environment-variables) ·
[Supabase — Connecting to Postgres](https://supabase.com/docs/guides/database/connecting-to-postgres) ·
[Supabase — Hardening the Data API](https://supabase.com/docs/guides/api/hardening-data-api)
