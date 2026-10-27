# Deploy em Produção Context

**Gathered:** 2026-10-27
**Spec:** `.specs/features/deploy-producao/spec.md`
**Status:** Ready for execute

---

## Feature Boundary

Configuração para publicar o KIRA na Vercel (runtime Python) com o PostgreSQL no Supabase, pelo
transaction pooler: settings lidas do ambiente, banco de produção por `DATABASE_URL`, `STATIC_ROOT`
para o admin, `.python-version` e `vercel.json`, `.env.example` e README. Sem tela nova.

---

## Implementation Decisions

### CSS das telas (AD-010)

- `kira.css` continua embutido pelo `base.html`. A AD-010 não é supersedida e nenhum teste da F1 à F6 muda.

### Configuração do banco

- `DATABASE_URL` (via `dj-database-url`) quando definida e não vazia, com `sslmode=require`, `DISABLE_SERVER_SIDE_CURSORS=True` e `CONN_MAX_AGE=0`.
- Sem ela, as `POSTGRES_*` atuais: o Postgres local da porta 5433, sem SSL, continua igual.

### Arquivos estáticos

- Só `STATIC_ROOT`, sem WhiteNoise. A Vercel roda o `collectstatic` no build e serve `/static/` pela CDN.

### Versão do Python

- `.python-version` com `3.13`. A Vercel aceita 3.12 (padrão), 3.13 e 3.14, segundo a documentação consultada em 2026-10-27.

### Origem do deploy (emenda de 2026-10-27)

- A conta do GitHub do usuário está suspensa. O deploy sai da pasta local pela Vercel CLI (`npx vercel --prod`), com conta na Vercel e no Supabase por e-mail (caminho B, decisão do usuário).
- Um `.vercelignore` impede o upload do `.env` e do que é só de desenvolvimento (DEPL-18); `.vercel/` fica fora do git (DEPL-19).

### Agent's Discretion

- Como os testes isolam o carregamento de `config/settings.py` do `.env` do desenvolvedor.
- Os globs exatos do `excludeFiles`, dentro do que a DEPL-14 fixa.

### Declined / Undiscussed Gray Areas → Assumptions

- `SECURE_PROXY_SSL_HEADER`, redirecionamento SSL e HSTS: fora (a Vercel força HTTPS na borda).
- Migrations e `createsuperuser`: rodados à mão pelo README, nunca no build.

---

## Specific References

- Vercel, "Deploy a Django app on Vercel" e "Using the Python Runtime with Vercel Functions" (ver a spec, "Fontes consultadas").
- Django 5.2, "Databases", seção sobre transaction pooling.

---

## Deferred Ideas

- Mover `kira.css` para `static/` com `<link>` e cache do navegador (exige supersedir a AD-010).
- WhiteNoise, se o deploy for para Render ou Railway.
- Separar `requirements-dev.txt`.
