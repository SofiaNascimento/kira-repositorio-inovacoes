# Deploy em Produção — Specification

Atende ao RNF06 (`docs/requisitos.md:90`; `docs/mapa-de-features.md:100`, "infraestrutura, fase
final"). Hospedagem: Vercel (runtime Python, função serverless) para a aplicação e Supabase para o
PostgreSQL, pelo transaction pooler (porta 6543). É configuração: não muda tela, view, form, model
nem URL.

## Problem Statement

O KIRA só roda no `runserver` local contra o Postgres da porta 5433. O RNF06 pede que a solução
seja publicável numa hospedagem gratuita em nuvem, e hoje faltam peças para isso: não há
`CSRF_TRUSTED_ORIGINS` (todo POST atrás do proxy HTTPS da Vercel cai em 403), o banco não fala SSL
nem tolera o pooler em modo transação, não há `STATIC_ROOT` (o admin sairia sem CSS) e nada fixa a
versão do Python (a Vercel cairia no 3.12 padrão, e o projeto mira 3.13).

## Goals

- [ ] O mesmo `config/settings.py` roda local (Postgres 5433, sem SSL) e na Vercel (Supabase pelo pooler), trocando só variáveis de ambiente.
- [ ] Todo comportamento de produção é verificável por teste automatizado sem nuvem; o que só a nuvem mostra fica no roteiro de UAT manual.
- [ ] Um README com o passo a passo leva do repositório ao sistema publicado, com login e admin funcionando.

## Fontes consultadas (Knowledge Verification Chain, passo 4)

| Fonte | O que define para esta spec |
| ----- | --------------------------- |
| Vercel, "Using the Python Runtime with Vercel Functions" (`vercel.com/docs/functions/runtimes/python`, atualizada em 2026-08-12) | Versões disponíveis: **3.12 (padrão), 3.13, 3.14**. A versão vem de `pyproject.toml`, `.python-version` ou `Pipfile.lock`; sem ela, ou com versão não suportada, vale o padrão. Bundle até 500 MB; `excludeFiles` em `vercel.json` corta arquivos. |
| Vercel, "Deploy a Django app on Vercel" (`vercel.com/docs/frameworks/full-stack/django`, atualizada em 2026-07-24) | Detecta `manage.py`, lê `DJANGO_SETTINGS_MODULE` e usa `WSGI_APPLICATION`. Com `STATIC_ROOT` definido, roda o `collectstatic` no build e serve `STATIC_URL` pela CDN. O WhiteNoise "is only active when running locally with `vercel dev`". `functions` em `vercel.json` usa como chave o arquivo de entrada resolvido (`config/wsgi.py`). |
| Django 5.2, "Databases" (`docs.djangoproject.com/en/5.2/ref/databases/`) | Pooler em modo transação exige `DISABLE_SERVER_SIDE_CURSORS = True`. Com psycopg 3.1.8+, o Django usa ligação de parâmetros do lado do cliente por padrão, sem prepared statements no servidor. |

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
| CI (build, testes ou deploy automáticos) | Fora do escopo pedido. O deploy acontece pelo Git conectado à Vercel ou pelo `vercel deploy`. |
| Upload de arquivos (media, Vercel Blob) | Fora do escopo pedido; o sistema não tem campo de arquivo. |
| Mover `kira.css` para `static/` (supersedir a AD-010) | Decidido com o usuário: manter o CSS embutido. Fica para quando houver motivo além do cache. |
| WhiteNoise | Decidido com o usuário: a Vercel serve `/static/` pela CDN e o WhiteNoise fica inativo lá. Um deploy futuro em Render ou Railway volta a pedir um servidor de estáticos. |
| `SECURE_PROXY_SSL_HEADER`, `SECURE_SSL_REDIRECT`, HSTS | A Vercel já força HTTPS na borda. O POST atrás do proxy é resolvido por `CSRF_TRUSTED_ORIGINS` (DEPL-05). Os avisos de `check --deploy` sobre isso ficam aceitos. |
| Separar dependências de desenvolvimento (`requirements-dev.txt`) | O pytest e o ruff entram no bundle, mas ficam longe do limite de 500 MB. |
| Migrations ou criação de usuários automáticas no build | Rodar `migrate` no build da Vercel acoplaria o deploy ao banco. Migrations rodam à mão pelo README (UAT). |

---

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --------------------- | -------------- | --------- | ---------- |
| CSS das telas | Continua embutido (`<style>{% include "kira.css" %}</style>`); a AD-010 não é supersedida | Decisão do usuário no Specify; a feature fica só em configuração e nenhum teste da F1 à F6 muda | y |
| Configuração do banco | `DATABASE_URL`, lida por `dj-database-url`, quando definida e não vazia; senão as `POSTGRES_*` atuais | Decisão do usuário. A string do pooler do Supabase entra em uma variável só, e a presença dela é o que liga o modo produção do banco | y |
| WhiteNoise | Não incluir; só `STATIC_ROOT` | Decisão do usuário, com base na documentação da Vercel (CDN + `collectstatic` automático) | y |
| Versão do Python | Arquivo `.python-version` com `3.13` | A Vercel aceita 3.13 (fonte acima). O `.python-version` evita criar a tabela `[project]` no `pyproject.toml`, que poderia mudar como a Vercel instala as dependências (hoje pelo `requirements.txt`) | y |
| `sslmode` com `DATABASE_URL` | Sempre `require`, mesmo que a URL traga outro `sslmode` na query | O Supabase exige SSL; uma URL copiada com `sslmode=disable` não pode desligar isso em produção | y |
| `CONN_MAX_AGE` com `DATABASE_URL` | `0` (uma conexão por requisição) | O pooler já reaproveita conexões; uma conexão persistente numa função serverless fica pendurada quando a instância congela | y |
| Prepared statements no pooler | Nenhum ajuste; `server_side_binding` fica desligado (padrão) | Django 5.2 + psycopg 3 usa ligação do lado do cliente por padrão (fonte acima) | y |
| Pasta do `STATIC_ROOT` | `BASE_DIR / "staticfiles"`, no `.gitignore` | Nome usado pela documentação do Django e da Vercel; é saída de build, não código | y |
| Formato das listas no ambiente | Vírgula como separador, espaços em volta descartados, itens vazios ignorados | Mesmo formato do `DJANGO_ALLOWED_HOSTS` atual; o `strip` evita que `"a, b"` vire o host `" b"` | y |
| `vercel.json` | Existe só para `functions["config/wsgi.py"].excludeFiles` (testes, `docs/`, `.specs/`) | A detecção do Django dispensa configuração de entrada; cortar o que não roda deixa o bundle menor | y |
| Testes de settings e o `.env` local | Cada teste de ambiente carrega `config/settings.py` num processo ou módulo isolado, com o ambiente controlado e sem ler o `.env` do desenvolvedor | O `load_dotenv` preencheria as variáveis que o teste removeu (por exemplo `DJANGO_SECRET_KEY`), e o teste passaria pelo motivo errado. O mecanismo é decidido no Execute | y |
| URL de banco inválida (esquema desconhecido) | O carregamento das settings falha com a exceção do `dj-database-url` | Falhar no build é melhor que subir sem banco; não vira AC própria | y |
| Idioma dos critérios | EARS em inglês, restante em português | Padrão das features anteriores | y |

**Open questions:** none (nenhuma); as três decisões pedidas foram tomadas com o usuário e o resto está registrado acima.

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

### P1: Banco de produção pelo pooler do Supabase ⭐ MVP

**User Story**: Como responsável pelo deploy, quero colar a string do pooler do Supabase numa
variável e ter SSL e compatibilidade com o modo transação ligados, sem mudar nada no banco local.

**Why P1**: Sem SSL o Supabase recusa a conexão; sem desligar cursores do servidor, consultas
iteradas quebram no pooler em modo transação.

**Acceptance Criteria**:

1. DEPL-06: WHEN `DATABASE_URL` is `postgresql://postgres.abcd:s%40nha@aws-0-sa-east-1.pooler.supabase.com:6543/postgres` THEN the system SHALL set the default database to `ENGINE` `django.db.backends.postgresql`, `NAME` `postgres`, `USER` `postgres.abcd`, `PASSWORD` `s@nha`, `HOST` `aws-0-sa-east-1.pooler.supabase.com` and `PORT` `6543`.
2. DEPL-07: WHEN `DATABASE_URL` is set and not empty THEN the system SHALL set `OPTIONS["sslmode"] = "require"` on the default database, including when the URL query carries `sslmode=disable`.
3. DEPL-08: WHEN `DATABASE_URL` is set and not empty THEN the system SHALL set `DISABLE_SERVER_SIDE_CURSORS = True` and `CONN_MAX_AGE = 0` on the default database.
4. DEPL-09: WHILE `DATABASE_URL` is unset or empty the system SHALL build the default database from `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST` and `POSTGRES_PORT` (with `POSTGRES_PORT=5433` giving `PORT` `5433`), with no `sslmode` option and without `DISABLE_SERVER_SIDE_CURSORS = True`.

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

**Independent Test**: ler os arquivos do repositório e conferir conteúdo e casamento de globs;
importar `config.wsgi`.

---

### P2: Variáveis e passo a passo documentados

**User Story**: Como quem vai publicar ou avaliar o projeto, quero saber quais variáveis definir e
em que ordem fazer o deploy, sem ler o código.

**Why P2**: O deploy funciona sem o README, mas quem não escreveu a configuração não chega lá.

**Acceptance Criteria**:

1. DEPL-16: The system SHALL list in `.env.example` every environment variable name that `config/settings.py` reads, including `DJANGO_CSRF_TRUSTED_ORIGINS` and `DATABASE_URL`.
2. DEPL-17: The README SHALL contain a deploy section that names `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS` and `DATABASE_URL`, and the commands `migrate` and `createsuperuser` run against the Supabase database.

**Independent Test**: comparar os nomes lidos por `os.environ` em `config/settings.py` com as
chaves do `.env.example`; procurar os nomes e comandos na seção de deploy do README.

---

## Edge Cases

- IF `DATABASE_URL` is set to an empty string THEN the system SHALL use the `POSTGRES_*` branch (DEPL-09).
- IF the URL query of `DATABASE_URL` carries `sslmode=disable` THEN the system SHALL still set `sslmode` to `require` (DEPL-07).
- IF a POST reaches `/entrar/` with `Origin: https://outro.vercel.app` not in `CSRF_TRUSTED_ORIGINS` THEN the system SHALL answer 403 (part of DEPL-05's test, so the trusted-origin case is not passing by accident).
- WHEN `DJANGO_ALLOWED_HOSTS` or `DJANGO_CSRF_TRUSTED_ORIGINS` has spaces around items or a trailing comma THEN the system SHALL drop the spaces and the empty item (DEPL-03, DEPL-04).

---

## Roteiro de UAT manual (só na nuvem)

Fora das ACs automatizadas. Roda depois do Execute, com o go-ahead explícito do usuário para cada
operação remota (deploy, migrate no Supabase).

1. Criar o projeto no Supabase e copiar a string do **transaction pooler** (porta 6543).
2. Na Vercel, importar o repositório e definir `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS` e `DATABASE_URL`, todas também no ambiente de build (o build roda o `manage.py`).
3. Rodar `migrate` e `createsuperuser` da máquina local com `DATABASE_URL` apontando para o Supabase.
4. Fazer o deploy e conferir no log de build: Python 3.13 e `collectstatic` executado.
5. Abrir `https://<projeto>.vercel.app/entrar/`, entrar e ver a lista de inovações com o visual do `kira.css`.
6. Cadastrar uma inovação (POST com CSRF atrás do proxy) e vê-la na lista e no detalhe.
7. Abrir `/admin/` e conferir o CSS do admin, servido de `/static/admin/...` pela CDN.
8. Nas ferramentas do navegador, conferir que os cookies `sessionid` e `csrftoken` estão marcados como `Secure`.
9. Abrir uma URL inexistente e conferir a página de erro do projeto, sem a página de depuração do Django.

---

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
| -------------- | ----- | ----- | ------ |
| DEPL-01 | P1: Configuração do ambiente | Execute | Implementing |
| DEPL-02 | P1: Configuração do ambiente | Execute | Implementing |
| DEPL-03 | P1: Configuração do ambiente | Execute | Implementing |
| DEPL-04 | P1: Configuração do ambiente | Execute | Implementing |
| DEPL-05 | P1: Configuração do ambiente | Execute | Implementing |
| DEPL-06 | P1: Banco de produção | Execute | Implementing |
| DEPL-07 | P1: Banco de produção | Execute | Implementing |
| DEPL-08 | P1: Banco de produção | Execute | Implementing |
| DEPL-09 | P1: Banco de produção | Execute | Implementing |
| DEPL-10 | P1: Estáticos do admin | Execute | Implementing |
| DEPL-11 | P1: Estáticos do admin | Execute | Implementing |
| DEPL-12 | P1: Runtime da Vercel | Execute | Pending |
| DEPL-13 | P1: Runtime da Vercel | Execute | Pending |
| DEPL-14 | P1: Runtime da Vercel | Execute | Pending |
| DEPL-15 | P1: Runtime da Vercel | Execute | Implementing |
| DEPL-16 | P2: Documentação | Execute | Pending |
| DEPL-17 | P2: Documentação | Execute | Pending |

**Coverage:** 17 total, 0 mapped to tasks (Tasks a definir no Execute), 17 unmapped ⚠️

---

## Success Criteria

- [ ] As 17 ACs passam em testes automatizados sem acesso à rede, e a suíte existente continua verde contra o Postgres local da porta 5433.
- [ ] O roteiro de UAT manual chega ao passo 9 sem editar código.
