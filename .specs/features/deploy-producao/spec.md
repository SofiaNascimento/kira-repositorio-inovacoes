# Deploy em Produção — Specification

Atende ao RNF06 (`docs/requisitos.md:90`; `docs/mapa-de-features.md:100`, "infraestrutura, fase
final"). Hospedagem: Vercel (runtime Python, função serverless) para a aplicação e Neon (plano
gratuito, região AWS São Paulo) para o PostgreSQL, pela conexão *pooled* (PgBouncer em modo
transação). É configuração: não muda tela, view, form, model nem URL.

> **Emenda de 2026-11-09 — troca do Supabase pelo Neon.** O banco de produção sai do Supabase e
> vai para o Neon, com conta direta no neon.com (decisão do usuário). O banco novo começa do zero
> (`migrate` + `createsuperuser` + acervo opcional), sem copiar dados do Supabase, e a
> documentação deixa de citar o Supabase. DEPL-06 e DEPL-17 são emendadas; DEPL-21 a DEPL-23 são
> novas. O comportamento do `config/settings.py` não muda: o pooler do Neon também opera em modo
> transação, e as DEPL-07 a DEPL-09 seguem como estão.

## Problem Statement

O KIRA só roda no `runserver` local contra o Postgres da porta 5433. O RNF06 pede que a solução
seja publicável numa hospedagem gratuita em nuvem, e hoje faltam peças para isso: não há
`CSRF_TRUSTED_ORIGINS` (todo POST atrás do proxy HTTPS da Vercel cai em 403), o banco não fala SSL
nem tolera o pooler em modo transação, não há `STATIC_ROOT` (o admin sairia sem CSS) e nada fixa a
versão do Python (a Vercel cairia no 3.12 padrão, e o projeto mira 3.13).

## Goals

- [ ] O mesmo `config/settings.py` roda local (Postgres 5433, sem SSL) e na Vercel (Neon pelo pooler; Supabase até a emenda de 2026-11-09), trocando só variáveis de ambiente.
- [ ] Todo comportamento de produção é verificável por teste automatizado sem nuvem; o que só a nuvem mostra fica no roteiro de UAT manual.
- [ ] Um README com o passo a passo leva do repositório ao sistema publicado, com login e admin funcionando.

## Fontes consultadas (Knowledge Verification Chain, passo 4)

| Fonte | O que define para esta spec |
| ----- | --------------------------- |
| Vercel, "Using the Python Runtime with Vercel Functions" (`vercel.com/docs/functions/runtimes/python`, atualizada em 2026-08-12) | Versões disponíveis: **3.12 (padrão), 3.13, 3.14**. A versão vem de `pyproject.toml`, `.python-version` ou `Pipfile.lock`; sem ela, ou com versão não suportada, vale o padrão. Bundle até 500 MB; `excludeFiles` em `vercel.json` corta arquivos. |
| Vercel, "Deploy a Django app on Vercel" (`vercel.com/docs/frameworks/full-stack/django`, atualizada em 2026-07-24) | Detecta `manage.py`, lê `DJANGO_SETTINGS_MODULE` e usa `WSGI_APPLICATION`. Com `STATIC_ROOT` definido, roda o `collectstatic` no build e serve `STATIC_URL` pela CDN. O WhiteNoise "is only active when running locally with `vercel dev`". `functions` em `vercel.json` usa como chave o arquivo de entrada resolvido (`config/wsgi.py`). |
| Django 5.2, "Databases" (`docs.djangoproject.com/en/5.2/ref/databases/`) | Pooler em modo transação exige `DISABLE_SERVER_SIDE_CURSORS = True`. Com psycopg 3.1.8+, o Django usa ligação de parâmetros do lado do cliente por padrão, sem prepared statements no servidor. |
| Neon, "Connection pooling" (`neon.com/docs/connect/connection-pooling`), consultada em 2026-11-09 | O pooler é PgBouncer em **modo transação**. O host *pooled* leva o sufixo `-pooler` no ID do endpoint. Migrations e operações de sessão devem usar a conexão direta (host sem `-pooler`). |
| Neon, "Regions" (`neon.com/docs/introduction/regions`), consultada em 2026-11-09 | Postgres disponível em **AWS South America (São Paulo), `aws-sa-east-1`**. A região é fixada na criação do projeto e não pode ser trocada depois. |
| Neon, "Free plan limits and quotas" (`neon.com/faqs/free-plan-limits-and-quotas`) e "Plans" (`neon.com/docs/introduction/plans`), consultadas em 2026-11-09 | Plano gratuito: 1 GB de armazenamento e 100 CU-hora por mês por projeto; o banco suspende após 5 min ocioso (não desativável no gratuito); estourar um limite pausa ou bloqueia escrita, sem apagar dados. |
| Experimento local, 2026-11-09 (`dj_database_url.parse` na `.venv`) | Uma URL do Neon sem porta e com `?sslmode=require&channel_binding=require` dá `PORT` `""` (o Django usa 5432) e `OPTIONS` `{"sslmode": "require", "channel_binding": "require"}`; com `ssl_require=True`, `sslmode=disable` na query continua virando `require`. |

## Code Reuse Analysis

| Item | Onde | Situação | Reuso |
| ---- | ---- | -------- | ----- |
| `SECRET_KEY` | `config/settings.py:28` | `os.environ["DJANGO_SECRET_KEY"]`: sem a variável, o carregamento falha | Mantido; passa a ter teste |
| `DEBUG` | `config/settings.py:31` | Só `"True"` liga; padrão `False` | Mantido; passa a ter teste |
| `ALLOWED_HOSTS` | `config/settings.py:33` | Lista por vírgula, descarta vazios, **não tira espaços** | Ganha `strip` |
| `CSRF_TRUSTED_ORIGINS` | — | Não existe | Novo, mesmo formato do `ALLOWED_HOSTS` |
| Cookies seguros | `config/settings.py:171-172` | `SESSION_COOKIE_SECURE` e `CSRF_COOKIE_SECURE` = `not DEBUG` | Mantidos sem mudança |
| `DATABASES` | `config/settings.py:85-94` | Só `POSTGRES_*`, sem SSL | Vira o ramo local; o ramo de produção lê `DATABASE_URL` |
| `.env` | `config/settings.py:21` | `load_dotenv(BASE_DIR / ".env")`, que não sobrescreve variável já definida | Mantido; na Vercel não há `.env` |
| Entrada WSGI | `config/wsgi.py`, `WSGI_APPLICATION` em `config/settings.py:80` | Já expõe `application` | Mantida sem mudança; a Vercel a detecta |
| Estáticos | `STATIC_URL = "static/"` | Sem `STATIC_ROOT` | Ganha `STATIC_ROOT` |
| CSS das telas | `templates/kira.css` embutido pelo `base.html` (AD-010) | Não depende de estáticos | **Mantido embutido**; a AD-010 continua ativa |
| Python local | `.venv` | 3.13.0; `pyproject.toml` só tem `target-version = "py313"` do ruff, sem `requires-python` | `.python-version` fixa 3.13 para a Vercel |

## Out of Scope

| Feature | Reason |
| ------- | ------ |
| E-mail (SMTP, recuperação de senha por e-mail) | Fora do escopo pedido. |
| Domínio próprio | Fora do escopo pedido; o sistema fica no domínio `*.vercel.app`. |
| CI (build, testes ou deploy automáticos) | Fora do escopo pedido. O deploy acontece pelo `vercel deploy --prod` da máquina local (emenda de 2026-10-27). |
| Upload de arquivos (media, Vercel Blob) | Fora do escopo pedido; o sistema não tem campo de arquivo. |
| Mover `kira.css` para `static/` (supersedir a AD-010) | Decidido com o usuário: manter o CSS embutido. Fica para quando houver motivo além do cache. |
| WhiteNoise | Decidido com o usuário: a Vercel serve `/static/` pela CDN e o WhiteNoise fica inativo lá. Um deploy futuro em Render ou Railway volta a pedir um servidor de estáticos. |
| `SECURE_PROXY_SSL_HEADER`, `SECURE_SSL_REDIRECT`, HSTS | A Vercel já força HTTPS na borda. O POST atrás do proxy é resolvido por `CSRF_TRUSTED_ORIGINS` (DEPL-05). Os avisos de `check --deploy` sobre isso ficam aceitos. |
| Separar dependências de desenvolvimento (`requirements-dev.txt`) | O pytest e o ruff entram no bundle, mas ficam longe do limite de 500 MB. |
| Migrations ou criação de usuários automáticas no build | Rodar `migrate` no build da Vercel acoplaria o deploy ao banco. Migrations rodam à mão pelo README (UAT). |
| Copiar dados do Supabase para o Neon (emenda de 2026-11-09) | Decisão do usuário: o Supabase só tem as tabelas do `migrate`. O Neon começa do zero. |
| Apagar o projeto no Supabase (emenda de 2026-11-09) | Ação do usuário na conta dele, fora do roteiro e do código. |
| Integração Neon pelo Vercel Marketplace (emenda de 2026-11-09) | Decisão do usuário: conta direta no neon.com, sem cartão. Há relato de conta Hobby que não conseguiu remover o cartão depois de contratar o Neon pelo Marketplace. |
| Segundo alias de banco no Django para a conexão direta | As migrations rodam da máquina local com a URL direta na própria `DATABASE_URL` do comando; a aplicação na Vercel só usa a *pooled*. |

---

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --------------------- | -------------- | --------- | ---------- |
| CSS das telas | Continua embutido (`<style>{% include "kira.css" %}</style>`); a AD-010 não é supersedida | Decisão do usuário no Specify; a feature fica só em configuração e nenhum teste da F1 à F6 muda | y |
| Configuração do banco | `DATABASE_URL`, lida por `dj-database-url`, quando definida e não vazia; senão as `POSTGRES_*` atuais | Decisão do usuário. A string do pooler do Supabase entra em uma variável só, e a presença dela é o que liga o modo produção do banco | y |
| WhiteNoise | Não incluir; só `STATIC_ROOT` | Decisão do usuário, com base na documentação da Vercel (CDN + `collectstatic` automático) | y |
| Versão do Python | Arquivo `.python-version` com `3.13` | A Vercel aceita 3.13 (fonte acima). Premissa original de evitar a tabela `[project]` substituída pela DEPL-20 (emenda de 2026-10-27): a Vercel instala do `pyproject.toml` | y |
| `sslmode` com `DATABASE_URL` | Sempre `require`, mesmo que a URL traga outro `sslmode` na query | O provedor exige SSL (Supabase até a emenda de 2026-11-09, hoje o Neon); uma URL copiada com `sslmode=disable` não pode desligar isso em produção | y |
| `CONN_MAX_AGE` com `DATABASE_URL` | `0` (uma conexão por requisição) | O pooler já reaproveita conexões; uma conexão persistente numa função serverless fica pendurada quando a instância congela | y |
| Prepared statements no pooler | Nenhum ajuste; `server_side_binding` fica desligado (padrão) | Django 5.2 + psycopg 3 usa ligação do lado do cliente por padrão (fonte acima) | y |
| Pasta do `STATIC_ROOT` | `BASE_DIR / "staticfiles"`, no `.gitignore` | Nome usado pela documentação do Django e da Vercel; é saída de build, não código | y |
| Formato das listas no ambiente | Vírgula como separador, espaços em volta descartados, itens vazios ignorados | Mesmo formato do `DJANGO_ALLOWED_HOSTS` atual; o `strip` evita que `"a, b"` vire o host `" b"` | y |
| `vercel.json` | Existe só para `functions["config/wsgi.py"].excludeFiles` (testes, `docs/`, `.specs/`) | A detecção do Django dispensa configuração de entrada; cortar o que não roda deixa o bundle menor | y |
| Testes de settings e o `.env` local | Cada teste de ambiente carrega `config/settings.py` num processo ou módulo isolado, com o ambiente controlado e sem ler o `.env` do desenvolvedor | O `load_dotenv` preencheria as variáveis que o teste removeu (por exemplo `DJANGO_SECRET_KEY`), e o teste passaria pelo motivo errado. O mecanismo é decidido no Execute | y |
| URL de banco inválida (esquema desconhecido) | O carregamento das settings falha com a exceção do `dj-database-url` | Falhar no build é melhor que subir sem banco; não vira AC própria | y |
| Idioma dos critérios | EARS em inglês, restante em português | Padrão das features anteriores | y |
| Dependências no `pyproject.toml` (emenda de 2026-10-27) | `[project]` com as mesmas dependências de runtime do `requirements.txt` e `requires-python` 3.13; o `requirements.txt` continua para o desenvolvimento local | O primeiro `vercel --prod` não instalou nada e falhou ao ler o `manage.py` (`No module named 'django'`). Com dependências nos dois arquivos, o build não depende de qual a Vercel prefere. Substitui a premissa anterior de evitar a tabela `[project]` | y |
| Origem do deploy (emenda de 2026-10-27) | Vercel CLI (`npx vercel --prod`) enviando a pasta local, sem Git conectado | A conta do GitHub do usuário está suspensa; decisão do usuário (caminho B). A CLI não ignora o `.env` por padrão (só `.env.local` e `.env.*.local`), e o `load_dotenv` preencheria com ele o que faltar no painel, inclusive `DJANGO_DEBUG=True` | y |
| Semântica do `.vercelignore` nos testes | A do `.gitignore`, conferida por `git check-ignore --no-index` num repositório temporário vazio | A Vercel descreve o arquivo como "similar a um `.gitignore`"; o repositório temporário isola o `.gitignore` do projeto, que já ignora o `.env` | y |

| Provedor do banco (emenda de 2026-11-09) | Neon, plano gratuito, conta direta no neon.com por e-mail | Decisão do usuário. O uso do KIRA fica longe dos limites do gratuito (fonte acima) | y |
| Região do Neon (emenda de 2026-11-09) | AWS São Paulo (`aws-sa-east-1`) | Mesma região da função na Vercel (`gru1`, roteiro 3.6); a região não muda depois de criado o projeto | y |
| URL de cada uso (emenda de 2026-11-09) | Na Vercel, a *pooled* (host com `-pooler`); nos comandos locais de `migrate` e `createsuperuser`, a direta (host sem `-pooler`) | Recomendação do Neon (fonte acima). Substitui o par transaction pooler 6543 / session pooler 5432 do Supabase | y |
| `channel_binding=require` na URL do Neon (emenda de 2026-11-09) | Mantido em `OPTIONS` como vem na URL; nenhuma mudança no settings | O `dj-database-url` já o repassa (experimento acima) e o psycopg o envia à libpq. Fica fixado pela DEPL-21 | y |
| Dados no banco novo (emenda de 2026-11-09) | Começa do zero: `migrate`, `createsuperuser` e, opcionalmente, o acervo | Decisão do usuário | y |
| Referências ao Supabase (emenda de 2026-11-09) | Removidas do README, do roteiro, do `.env.example`, do `config/settings.py`, dos testes e do mapa de features; o histórico em `.specs/` fica como está | Decisão do usuário. Os artefatos de `.specs/` registram o que aconteceu e não são reescritos | y |

**Open questions:** none (nenhuma); as três decisões pedidas foram tomadas com o usuário e o resto está registrado acima. Emenda de 2026-11-09: as três decisões (provedor e forma de conta, dados, referências) foram tomadas com o usuário.

---

## User Stories

### P1: Configuração de produção lida do ambiente ⭐ MVP

**User Story**: Como responsável pelo deploy, quero que segredo, depuração, hosts e origens
confiáveis venham de variáveis de ambiente, para publicar sem editar código e sem expor a chave.

**Why P1**: Sem `CSRF_TRUSTED_ORIGINS` o login falha com 403 atrás do HTTPS da Vercel; sem a chave
fora do código, o deploy expõe o segredo.

**Acceptance Criteria**:

1. DEPL-01: IF `DJANGO_SECRET_KEY` is not set THEN loading the settings SHALL fail with `KeyError` naming `DJANGO_SECRET_KEY`.
2. DEPL-02: IF `DJANGO_DEBUG` is unset or holds any value other than `True` (for example `true`, `1`, empty) THEN the system SHALL set `DEBUG = False`.
3. DEPL-03: WHEN `DJANGO_ALLOWED_HOSTS` is `kira.vercel.app, localhost,` THEN the system SHALL set `ALLOWED_HOSTS = ["kira.vercel.app", "localhost"]`.
4. DEPL-04: WHEN `DJANGO_CSRF_TRUSTED_ORIGINS` is `https://kira.vercel.app, https://kira-git-main.vercel.app` THEN the system SHALL set `CSRF_TRUSTED_ORIGINS = ["https://kira.vercel.app", "https://kira-git-main.vercel.app"]`, and WHEN it is unset THEN the system SHALL set `CSRF_TRUSTED_ORIGINS = []`.
5. DEPL-05: WHILE `DEBUG = False` and `https://kira.vercel.app` is in `CSRF_TRUSTED_ORIGINS`, WHEN a POST with a valid CSRF token reaches `/entrar/` over HTTP with `Host: kira.vercel.app` and `Origin: https://kira.vercel.app` (as the Vercel proxy forwards it) THEN the system SHALL NOT answer 403.

**Independent Test**: carregar as settings com cada combinação de ambiente e conferir os valores;
fazer o POST de login com `Client(enforce_csrf_checks=True)` e `override_settings`.

---

### P1: Banco de produção pelo pooler do Neon ⭐ MVP

**User Story**: Como responsável pelo deploy, quero colar a string *pooled* do Neon numa
variável e ter SSL e compatibilidade com o modo transação ligados, sem mudar nada no banco local.

**Why P1**: Sem SSL o Neon recusa a conexão; sem desligar cursores do servidor, consultas
iteradas quebram no pooler em modo transação.

**Acceptance Criteria**:

1. DEPL-06: WHEN `DATABASE_URL` is `postgresql://neondb_owner:s%40nha@ep-calm-sun-a1b2c3d4-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require` THEN the system SHALL set the default database to `ENGINE` `django.db.backends.postgresql`, `NAME` `neondb`, `USER` `neondb_owner`, `PASSWORD` `s@nha`, `HOST` `ep-calm-sun-a1b2c3d4-pooler.sa-east-1.aws.neon.tech` and `PORT` `""` (empty: Django's default 5432). *(Emenda de 2026-11-09: a URL de exemplo era a do pooler do Supabase.)*
2. DEPL-07: WHEN `DATABASE_URL` is set and not empty THEN the system SHALL set `OPTIONS["sslmode"] = "require"` on the default database, including when the URL query carries `sslmode=disable`.
3. DEPL-08: WHEN `DATABASE_URL` is set and not empty THEN the system SHALL set `DISABLE_SERVER_SIDE_CURSORS = True` and `CONN_MAX_AGE = 0` on the default database.
4. DEPL-09: WHILE `DATABASE_URL` is unset or empty the system SHALL build the default database from `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST` and `POSTGRES_PORT` (with `POSTGRES_PORT=5433` giving `PORT` `5433`), with no `sslmode` option and without `DISABLE_SERVER_SIDE_CURSORS = True`.
5. DEPL-21: WHEN `DATABASE_URL` carries `channel_binding=require` in its query THEN the system SHALL set `OPTIONS["channel_binding"] = "require"` on the default database. *(Emenda de 2026-11-09: a string do Neon traz o parâmetro, e ele não pode se perder no caminho até o psycopg.)*

**Independent Test**: carregar as settings com e sem `DATABASE_URL` e comparar o dicionário
`DATABASES["default"]`; a suíte inteira continua passando contra o Postgres local da 5433.

---

### P1: Estáticos do admin coletáveis ⭐ MVP

**User Story**: Como administrador, quero o admin do Django com CSS em produção para usá-lo como
uso localmente.

**Why P1**: Sem `STATIC_ROOT` a Vercel não roda o `collectstatic` e o admin sai sem estilo.

**Acceptance Criteria**:

1. DEPL-10: The system SHALL set `STATIC_ROOT` to `BASE_DIR / "staticfiles"`, and `.gitignore` SHALL ignore `staticfiles/`.
2. DEPL-11: WHEN `collectstatic --noinput` runs THEN the system SHALL write `admin/css/base.css` under `STATIC_ROOT`.

**Independent Test**: rodar `call_command("collectstatic", interactive=False)` com
`override_settings(STATIC_ROOT=tmp_path)` e conferir o arquivo.

---

### P1: Projeto reconhecido pelo runtime Python da Vercel ⭐ MVP

**User Story**: Como responsável pelo deploy, quero que a Vercel detecte o projeto, use o Python
3.13 e empacote só o que roda, para publicar sem configuração manual no painel.

**Why P1**: Sem a versão fixada a Vercel usa 3.12; sem as dependências novas no
`requirements.txt` o build falha.

**Acceptance Criteria**:

1. DEPL-12: The repository SHALL contain `.python-version` whose content, stripped, is `3.13`.
2. DEPL-13: The system SHALL keep `WSGI_APPLICATION = "config.wsgi.application"`, and importing `config.wsgi` SHALL expose a callable named `application`.
3. DEPL-14: The repository SHALL contain a `vercel.json` that parses as JSON and whose `functions["config/wsgi.py"].excludeFiles` glob matches `inovacoes/tests/test_models.py`, `docs/requisitos.md` and `.specs/STATE.md` and does not match `inovacoes/views.py` nor `templates/kira.css`.
4. DEPL-15: `requirements.txt` SHALL list `dj-database-url` in its runtime section, before the development section.
5. DEPL-20: `pyproject.toml` SHALL have a `[project]` table whose `dependencies` equal, line by line, the runtime section of `requirements.txt`, and whose `requires-python` is `>=3.13,<3.14`. *(Emenda de 2026-10-27: o primeiro deploy pela CLI falhou com `No module named 'django'`; o `pyproject.toml` sem dependências deixou a Vercel sem nada para instalar.)*

**Independent Test**: ler os arquivos do repositório e conferir conteúdo e casamento de globs;
importar `config.wsgi`.

---

### P1: Deploy pela CLI sem vazar o `.env` ⭐ MVP (emenda de 2026-10-27)

**User Story**: Como responsável pelo deploy, sem acesso ao GitHub, quero publicar a pasta local
pela CLI da Vercel sem que o meu `.env` de desenvolvimento suba junto.

**Why P1**: Sem exclusão, o `.env` sobe com a chave local e `DJANGO_DEBUG=True`, e o `load_dotenv`
o aplicaria a qualquer variável ausente no painel.

**Acceptance Criteria**:

1. DEPL-18: The repository SHALL contain a `.vercelignore` that, read with `.gitignore` semantics, ignores `.env`, `.env.producao`, `.specs/STATE.md`, `.claude/skills/x.md`, `.agents/x.json` and `docs/requisitos.md`, and does not ignore `manage.py`, `config/settings.py`, `config/wsgi.py`, `inovacoes/views.py`, `templates/kira.css`, `requirements.txt`, `.python-version` nor `vercel.json`.
2. DEPL-19: `.gitignore` SHALL ignore `.vercel/`, the link directory the CLI creates.

**Independent Test**: copiar o `.vercelignore` para o `.gitignore` de um repositório temporário
vazio e consultar cada caminho com `git check-ignore --no-index`.

---

### P2: Variáveis e passo a passo documentados

**User Story**: Como quem vai publicar ou avaliar o projeto, quero saber quais variáveis definir e
em que ordem fazer o deploy, sem ler o código.

**Why P2**: O deploy funciona sem o README, mas quem não escreveu a configuração não chega lá.

**Acceptance Criteria**:

1. DEPL-16: The system SHALL list in `.env.example` every environment variable name that `config/settings.py` reads, including `DJANGO_CSRF_TRUSTED_ORIGINS` and `DATABASE_URL`.
2. DEPL-17: The README SHALL contain a deploy section that names `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS` and `DATABASE_URL`, and every line of that deploy section that runs `python manage.py migrate` or `python manage.py createsuperuser` SHALL set `DATABASE_URL` to a single-quoted `postgresql://` URL whose host ends in `.neon.tech` and does not contain `-pooler` (the Neon direct connection). *(Emenda de 2026-11-09: antes, os comandos apontavam para o Supabase.)*

**Independent Test**: comparar os nomes lidos por `os.environ` em `config/settings.py` com as
chaves do `.env.example`; procurar os nomes e comandos na seção de deploy do README.

---

### P2: Documentação só do Neon (emenda de 2026-11-09)

**User Story**: Como quem vai publicar ou avaliar o projeto, quero que o README e o roteiro
descrevam só o banco que está em uso, para não seguir passos de um provedor abandonado.

**Why P2**: O deploy funciona com a documentação desatualizada, mas um passo do Supabase seguido
por engano aponta a aplicação para o banco errado.

**Acceptance Criteria**:

1. DEPL-22: The files `README.md`, `docs/roteiro-deploy.md`, `docs/mapa-de-features.md`, `.env.example` and `config/settings.py` SHALL NOT contain the word `supabase` in any letter case.
2. DEPL-23: `docs/roteiro-deploy.md` SHALL contain the strings `neon.tech`, `aws-sa-east-1` and `-pooler`.

**Independent Test**: ler cada arquivo e procurar os termos, sem diferenciar maiúsculas na
DEPL-22.

---

## Edge Cases

- IF `DATABASE_URL` is set to an empty string THEN the system SHALL use the `POSTGRES_*` branch (DEPL-09).
- IF the URL query of `DATABASE_URL` carries `sslmode=disable` THEN the system SHALL still set `sslmode` to `require` (DEPL-07).
- IF a POST reaches `/entrar/` with `Origin: https://outro.vercel.app` not in `CSRF_TRUSTED_ORIGINS` THEN the system SHALL answer 403 (part of DEPL-05's test, so the trusted-origin case is not passing by accident).
- WHEN `DJANGO_ALLOWED_HOSTS` or `DJANGO_CSRF_TRUSTED_ORIGINS` has spaces around items or a trailing comma THEN the system SHALL drop the spaces and the empty item (DEPL-03, DEPL-04).

---

## Roteiro de UAT manual (só na nuvem)

Fora das ACs automatizadas. Roda depois do Execute, com o go-ahead explícito do usuário para cada
operação remota (deploy, migrate no Neon). *(Emenda de 2026-11-09: passos 1 a 3 trocados para o
Neon; o projeto na Vercel já existe e só tem a `DATABASE_URL` substituída.)*

1. Criar a conta no neon.com (plano gratuito) e o projeto na região AWS São Paulo (`aws-sa-east-1`); copiar a string *pooled* (host com `-pooler`) e a direta (host sem `-pooler`).
2. Na Vercel, substituir a `DATABASE_URL` pela string *pooled* do Neon, também no ambiente de build; as demais variáveis ficam como estão.
3. Rodar `migrate` e `createsuperuser` (e, se quiser, a carga do acervo) da máquina local com `DATABASE_URL` apontando para a string direta do Neon.
4. Fazer o deploy com `npx vercel --prod --logs` e conferir no log de build: Python 3.13, `collectstatic` executado e, na aba Source do deploy, ausência do `.env`.
5. Abrir `https://<projeto>.vercel.app/entrar/`, entrar e ver a lista de inovações com o visual do `kira.css`.
6. Cadastrar uma inovação (POST com CSRF atrás do proxy) e vê-la na lista e no detalhe.
7. Abrir `/admin/` e conferir o CSS do admin, servido de `/static/admin/...` pela CDN.
8. Nas ferramentas do navegador, conferir que os cookies `sessionid` e `csrftoken` estão marcados como `Secure`.
9. Abrir uma URL inexistente e conferir a página de erro do projeto, sem a página de depuração do Django.

---

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
| -------------- | ----- | ----- | ------ |
| DEPL-01 | P1: Configuração do ambiente | Execute | Verified |
| DEPL-02 | P1: Configuração do ambiente | Execute | Verified |
| DEPL-03 | P1: Configuração do ambiente | Execute | Verified |
| DEPL-04 | P1: Configuração do ambiente | Execute | Verified |
| DEPL-05 | P1: Configuração do ambiente | Execute | Verified |
| DEPL-06 | P1: Banco de produção | Execute | Implementing (emendada em 2026-11-09) |
| DEPL-07 | P1: Banco de produção | Execute | Verified |
| DEPL-08 | P1: Banco de produção | Execute | Verified |
| DEPL-09 | P1: Banco de produção | Execute | Verified |
| DEPL-10 | P1: Estáticos do admin | Execute | Verified |
| DEPL-11 | P1: Estáticos do admin | Execute | Verified |
| DEPL-12 | P1: Runtime da Vercel | Execute | Verified |
| DEPL-13 | P1: Runtime da Vercel | Execute | Verified |
| DEPL-14 | P1: Runtime da Vercel | Execute | Verified |
| DEPL-15 | P1: Runtime da Vercel | Execute | Verified |
| DEPL-16 | P2: Documentação | Execute | Verified |
| DEPL-17 | P2: Documentação | Execute | Implementing (emendada em 2026-11-09) |
| DEPL-18 | P1: Deploy pela CLI | Execute | Implementing (risco residual aceito) |
| DEPL-19 | P1: Deploy pela CLI | Execute | Verified |
| DEPL-20 | P1: Runtime da Vercel | Execute | Verified |
| DEPL-21 | P1: Banco de produção | Execute | Implementing |
| DEPL-22 | P2: Documentação só do Neon | Execute | Pending |
| DEPL-23 | P2: Documentação só do Neon | Execute | Pending |

**Coverage (emenda de 2026-11-09):** 23 total; 16 Verified; DEPL-06 e DEPL-17 reabertas pela emenda e DEPL-21 a DEPL-23 novas, todas Pending; DEPL-18 segue com o risco residual aceito.

**Coverage anterior:** 20 total (DEPL-18, DEPL-19 e DEPL-20 das emendas de 2026-10-27), 19 Verified (DEPL-20 na verificação da emenda) (DEPL-01 a 17 no PASS da iteração 2; DEPL-19 na iteração 3), DEPL-18 com risco residual de teste aceito (validation.md, Decisão do usuário de 2026-10-27)

---

## Success Criteria

- [ ] As 23 ACs (emenda de 2026-11-09) passam em testes automatizados sem acesso à rede, e a suíte existente continua verde contra o Postgres local da porta 5433.
- [ ] O roteiro de UAT manual chega ao passo 9 sem editar código.
