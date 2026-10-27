# KIRA — Conhecimento, Inovação e Replicação Administrativa

## Deploy em produção (Vercel + Supabase)

A aplicação roda na Vercel como uma função Python (Django detectado pelo `manage.py`, entrada
`config/wsgi.py`, Python 3.13 pelo `.python-version`). O PostgreSQL fica no Supabase, acessado
pelo **transaction pooler** na porta 6543. As telas não dependem de arquivos estáticos (o
`kira.css` vai embutido na página); o CSS do admin é coletado no build e servido pela CDN da
Vercel.

### Variáveis de ambiente

Defina na Vercel (Project Settings → Environment Variables), para **Production** e **Preview**.
O build executa o `manage.py`, então as variáveis precisam estar disponíveis também no build.

| Variável | Valor em produção |
| -------- | ----------------- |
| `DJANGO_SECRET_KEY` | Chave longa e aleatória, só da produção (comando abaixo) |
| `DJANGO_DEBUG` | `False` (qualquer valor diferente de `True` também desliga) |
| `DJANGO_ALLOWED_HOSTS` | `<projeto>.vercel.app`; para aceitar os previews, `.vercel.app` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://<projeto>.vercel.app`; para os previews, `https://*.vercel.app` |
| `DATABASE_URL` | String do transaction pooler do Supabase (porta 6543) |

As listas são separadas por vírgula. Com `DATABASE_URL` definida, o sistema liga
`sslmode=require`, desliga os cursores do servidor e não mantém conexão aberta entre requisições.
Sem ela, valem as variáveis `POSTGRES_*` do `.env` local (veja o `.env.example`).

Para gerar a chave:

```bash
.venv/bin/python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Passo a passo

1. **Supabase**: crie o projeto. Em Connect, copie a string do **Transaction pooler** (porta
   6543) e a do **Session pooler** (porta 5432), trocando `[YOUR-PASSWORD]` pela senha do banco.
   Caracteres especiais da senha vão codificados na URL (`@` vira `%40`).
2. **Banco**: da sua máquina, crie as tabelas e o primeiro administrador no Supabase. Use a
   string do session pooler, mais adequada a migrations:

   ```bash
   DATABASE_URL='postgresql://postgres.<ref>:<senha>@aws-0-<regiao>.pooler.supabase.com:5432/postgres' .venv/bin/python manage.py migrate
   DATABASE_URL='postgresql://postgres.<ref>:<senha>@aws-0-<regiao>.pooler.supabase.com:5432/postgres' .venv/bin/python manage.py createsuperuser
   ```

3. **Vercel**: o deploy sai da pasta local pela Vercel CLI, sem Git conectado. Crie a conta (pode
   ser por e-mail), rode `npx vercel login` e, na raiz do projeto, `npx vercel link` para criar o
   projeto (o preset de Django é detectado sozinho). No painel, cadastre as cinco variáveis da
   tabela, com a `DATABASE_URL` do transaction pooler (6543). O `.vercelignore` impede que o
   `.env` local suba junto.
4. **Deploy**: rode `npx vercel --prod --logs`. No log de build, confira o Python 3.13 e a
   execução do `collectstatic`. A CLI envia a pasta como está: faça o commit antes.

O roteiro detalhado, com telas, conferência e problemas comuns, está em
[`docs/roteiro-deploy.md`](docs/roteiro-deploy.md).
5. **Conferência**: abra `https://<projeto>.vercel.app/entrar/`, entre com o administrador
   criado no passo 2 e abra `/admin/` para ver o CSS do admin.

A cada mudança de model, repita o `manage.py migrate` do passo 2 **antes** do deploy do código
que depende dela.
