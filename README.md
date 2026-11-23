# KIRA — Conhecimento, Inovação e Replicação Administrativa

> Sistema web para registro, compartilhamento, consulta e reaproveitamento de inovações de back office entre unidades de uma organização.

**Sistema publicado:** <https://kira-nu-green.vercel.app>

![Status](https://img.shields.io/badge/status-MVP%20publicado-brightgreen)
![Projeto](https://img.shields.io/badge/projeto-TCC-blue)
![Python](https://img.shields.io/badge/Python-3.13-blue)
![Django](https://img.shields.io/badge/Django-5.2-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)
![License](https://img.shields.io/badge/license-a%20definir-lightgrey)

---

## 📌 Sobre o projeto

O **KIRA — Conhecimento, Inovação e Replicação Administrativa** é uma aplicação web desenvolvida como protótipo funcional (MVP) de um Trabalho de Conclusão de Curso.

O sistema tem como objetivo apoiar o **registro, a consulta e o compartilhamento de inovações de back office** desenvolvidas por diferentes unidades de uma mesma organização.

A proposta parte do problema de que soluções administrativas desenvolvidas localmente podem permanecer restritas à unidade onde surgiram. Como consequência, outras unidades podem enfrentar problemas semelhantes e desenvolver novamente soluções que já existem dentro da própria organização.

O KIRA propõe um repositório centralizado no qual essas iniciativas possam ser documentadas, pesquisadas e disponibilizadas para replicação.

A aplicação é voltada para inovações relacionadas aos processos internos da organização, como:

- Financeiro;
- Recursos Humanos;
- Tecnologia da Informação interna;
- Compras;
- Atendimento interno;
- Processos administrativos;
- Outras atividades de back office.

---

## 🎯 Objetivo

Desenvolver um sistema web capaz de centralizar o conhecimento relacionado às inovações administrativas desenvolvidas nas diferentes unidades de uma organização, permitindo seu registro, consulta e reaproveitamento.

O sistema busca contribuir para:

- reduzir retrabalho entre unidades;
- facilitar a descoberta de soluções já desenvolvidas internamente;
- estimular o compartilhamento de conhecimento;
- apoiar a replicação de boas práticas;
- preservar conhecimento organizacional;
- facilitar o contato entre unidades interessadas em uma solução;
- fornecer uma visão estruturada das iniciativas existentes.

---

## 🛠️ Tecnologias

### Back-end

- **Python**
- **Django**

O Django é utilizado como framework principal da aplicação e também fornece os mecanismos de autenticação e gerenciamento de sessão.

### Banco de dados

- **PostgreSQL**

O banco relacional é responsável pela persistência dos dados e manutenção da integridade referencial.

### Front-end

A interface usa templates do Django com HTML semântico e uma folha de estilo própria (`templates/kira.css`), sem framework de CSS. O visual segue o `docs/design-spec.md`; os gráficos do painel de indicadores são SVG gerados no servidor.

### Hospedagem

- **Vercel** (runtime Python) para a aplicação;
- **Neon** (plano gratuito, região São Paulo) para o PostgreSQL, acessado pelo pooler de conexões.

---

## ♿ Acessibilidade

O KIRA considera acessibilidade como um requisito essencial da interface.

O projeto busca conformidade com:

- **WCAG 2.1 — nível AA**;
- **eMAG — Modelo de Acessibilidade em Governo Eletrônico**.

Entre os aspectos considerados estão:

- contraste adequado;
- navegação por teclado;
- foco visível;
- HTML semântico;
- rótulos associados aos campos dos formulários;
- alternativas textuais para imagens;
- interface que não dependa exclusivamente de cores para transmitir informação.

---

## 🌐 Compatibilidade

A aplicação será desenvolvida para navegadores modernos, incluindo:

- Google Chrome;
- Mozilla Firefox;
- Microsoft Edge.

A interface também deverá ser responsiva para utilização em:

- desktop;
- tablet.

O desenvolvimento de aplicativo móvel nativo não faz parte do escopo.

---

## ⚙️ Instalação

Requisitos: Python 3.13 e PostgreSQL 16.

### 1. Clone o repositório

```bash
git clone <URL_DO_REPOSITORIO>
cd kira-repositorio-inovacoes
```

### 2. Crie um ambiente virtual

```bash
python -m venv .venv
```

### 3. Ative o ambiente virtual

#### Windows

```bash
.venv\Scripts\activate
```

#### Linux/macOS

```bash
source .venv/bin/activate
```

### 4. Instale as dependências

```bash
pip install -r requirements.txt
```

### 5. Configure o ambiente e o banco de dados

Copie o modelo de variáveis e ajuste-o (chave secreta, `DJANGO_DEBUG=True` e os dados do PostgreSQL local):

```bash
cp .env.example .env
```

Crie o banco indicado em `POSTGRES_DB` no PostgreSQL local. Sem `DATABASE_URL` definida, o sistema usa as variáveis `POSTGRES_*`.

### 6. Execute as migrações

```bash
python manage.py migrate
```

### 7. Inicie o servidor

```bash
python manage.py runserver
```

A aplicação estará disponível, por padrão, em:

```text
http://127.0.0.1:8000/
```

### 8. (Opcional) Carregue o acervo de demonstração

```bash
python manage.py createsuperuser
python manage.py carregar_demonstracao
```

O segundo comando cria 500 inovações de demonstração, com autores, histórico de status e reaproveitamentos (RNF08).

### 9. Rode os testes

```bash
pytest -q
```

---

## Deploy em produção (Vercel + Neon)

A aplicação roda na Vercel como uma função Python (Django detectado pelo `manage.py`, entrada
`config/wsgi.py`, Python 3.13 pelo `.python-version`). O PostgreSQL 16 fica no Neon, no
plano gratuito e na região AWS São Paulo (`aws-sa-east-1`). A aplicação usa a conexão **pooled** (host
com `-pooler`, PgBouncer em modo transação). As telas não dependem de arquivos estáticos (o
`kira.css` vai embutido na página); o CSS do admin é coletado no build e servido pela CDN da
Vercel.

### Variáveis de ambiente

Defina na Vercel (**Settings → Environments → Production**). O deploy é sempre de produção
(`npx vercel --prod`), então o ambiente Preview não é usado. O build executa o `manage.py`, então
as variáveis precisam estar disponíveis também no build.

| Variável | Valor em produção |
| -------- | ----------------- |
| `DJANGO_SECRET_KEY` | Chave longa e aleatória, só da produção (comando abaixo) |
| `DJANGO_DEBUG` | `False` (qualquer valor diferente de `True` também desliga) |
| `DJANGO_ALLOWED_HOSTS` | `<projeto>.vercel.app` (sem `https://`) |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://<projeto>.vercel.app` (sem barra no final) |
| `DATABASE_URL` | String **pooled** do Neon (host com `-pooler`) |

As listas são separadas por vírgula. Com `DATABASE_URL` definida, o sistema liga
`sslmode=require`, desliga os cursores do servidor e não mantém conexão aberta entre requisições.
Sem ela, valem as variáveis `POSTGRES_*` do `.env` local (veja o `.env.example`).

Para gerar a chave:

```bash
.venv/bin/python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Passo a passo

1. **Neon**: crie a conta no neon.com (plano gratuito, sem cartão) e um projeto com
   **Postgres 16** na região **AWS São Paulo (`aws-sa-east-1`)**. A região não muda depois. Em **Connect**, copie duas
   strings: a **pooled** (com **Connection pooling** ligado; o host tem `-pooler`) e a **direta**
   (com o pooling desligado; o host não tem `-pooler`).
2. **Banco**: da sua máquina, crie as tabelas e o primeiro administrador no Neon. Use a string
   **direta**, que o Neon recomenda para migrations. Ela fica no arquivo `~/.kira-neon.env`, fora
   do projeto, para a senha não aparecer na tela nem no histórico do terminal. Grave o arquivo
   colando só a URL quando o terminal pedir (nada aparece enquanto você cola):

   ```bash
   read -rs 'U?URL direta do Neon: ' && print -r -- "DATABASE_URL=$U" > ~/.kira-neon.env && chmod 600 ~/.kira-neon.env && unset U
   ```

   O arquivo fica com uma linha só, no formato
   `DATABASE_URL=postgresql://neondb_owner:<senha>@ep-<endpoint>.sa-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require`
   (host sem `-pooler`). Depois, carregue a URL no terminal, rode os comandos e desligue a
   variável no fim, para os próximos comandos voltarem ao banco local:

   ```bash
   export DATABASE_URL="$(sed -n 's/^DATABASE_URL=//p' ~/.kira-neon.env)"
   .venv/bin/python manage.py migrate
   .venv/bin/python manage.py createsuperuser
   unset DATABASE_URL
   ```

3. **Vercel**: o deploy sai da pasta local pela Vercel CLI, sem Git conectado. Crie a conta (pode
   ser por e-mail), rode `npx vercel login` e, na raiz do projeto, `npx vercel link` para criar o
   projeto (o preset de Django é detectado sozinho). No painel, cadastre as cinco variáveis da
   tabela, com a `DATABASE_URL` **pooled** do Neon. O `.vercelignore` impede que o
   `.env` local suba junto.
4. **Deploy**: rode `npx vercel --prod --logs`. No log de build, confira o Python 3.13 e a
   execução do `collectstatic`. A CLI envia a pasta como está: faça o commit antes.
5. **Conferência**: abra `https://<projeto>.vercel.app/entrar/`, entre com o administrador
   criado no passo 2 e clique em **Administração** no cabeçalho (ou abra `/admin/`) para ver o
   admin, com o título "KIRA — Administração" e o CSS carregado.

O roteiro detalhado, com telas, conferência e problemas comuns, está em
[`docs/roteiro-deploy.md`](docs/roteiro-deploy.md).

A cada mudança de model, repita o `manage.py migrate` do passo 2 (com o `export` e o `unset`) **antes** do deploy do código
que depende dela.

---

## 📚 Contexto acadêmico

Este projeto é desenvolvido como parte de um **Trabalho de Conclusão de Curso (TCC)**.

O MVP busca integrar conhecimentos relacionados a:

- Engenharia de Software;
- Engenharia de Requisitos;
- Desenvolvimento Web;
- Banco de Dados;
- Interação Humano-Computador;
- UX/UI;
- Acessibilidade;
- Segurança da Informação;
- Gestão do Conhecimento;
- Governança de TI;
- Qualidade de Software.

---

## 📖 Referências e fundamentos

O desenvolvimento e a avaliação do projeto consideram, entre outros referenciais:

- ISO/IEC 25010 — qualidade de software;
- Heurísticas de Usabilidade de Nielsen;
- System Usability Scale (SUS);
- Web Content Accessibility Guidelines (WCAG) 2.1;
- eMAG — Modelo de Acessibilidade em Governo Eletrônico;
- Lei Geral de Proteção de Dados Pessoais (LGPD);
- Objetivos de Desenvolvimento Sustentável (ODS).

As referências bibliográficas completas serão mantidas no trabalho acadêmico.

---

## 👩‍💻 Autoria

**Ruan Almeida**
**Sofia Nascimento**

Projeto desenvolvido como Trabalho de Conclusão de Curso.

**Curso:** `Sistemas de Informação`  
**Instituição:** `Centro Universitário Fametro`  
**Orientador(a):** `Luana Leal`  
**Ano:** `2026`

---

## 📄 Licença

A licença de distribuição do projeto ainda será definida.

Enquanto não houver uma licença explicitamente associada ao repositório, o código não deve ser considerado disponibilizado sob uma licença open source.

---

<p align="center">
  <strong>KIRA — Conhecimento, Inovação e Replicação Administrativa</strong>
</p>

<p align="center">
  Transformando soluções locais em conhecimento compartilhado.
</p>
