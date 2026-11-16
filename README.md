# KIRA - CONHECIMENTO, INOVAÇÃO E REPLICAÇÃO ADMINISTRATIVA

Sistema web para registro, compartilhamento, consulta e reaproveitamento de inovações de back office entre unidades de uma organização, desenvolvido como protótipo funcional (MVP) de Trabalho de Conclusão de Curso (TCC).

**LINK DE ACESSO:** <https://kira-nu-green.vercel.app>

![Status](https://img.shields.io/badge/status-MVP%20publicado-brightgreen)
![Projeto](https://img.shields.io/badge/projeto-TCC-blue)
![Python](https://img.shields.io/badge/Python-3.13-blue)
![Django](https://img.shields.io/badge/Django-5.2-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)
![License](https://img.shields.io/badge/license-a%20definir-lightgrey)

---

## Sobre o Projeto

O **KIRA — Conhecimento, Inovação e Replicação Administrativa** parte do problema de que soluções administrativas desenvolvidas localmente podem permanecer restritas à unidade onde surgiram, fazendo com que outras unidades enfrentem problemas semelhantes e desenvolvam novamente soluções que já existem dentro da própria organização.

O sistema propõe um repositório centralizado no qual essas iniciativas possam ser documentadas, pesquisadas e disponibilizadas para replicação, atendendo processos internos de back office como:

- Financeiro;
- Recursos Humanos;
- Tecnologia da Informação interna;
- Compras;
- Atendimento interno;
- Processos administrativos e outras atividades de back office.

---

## Vídeo de Apresentação do Projeto

> Assista à apresentação do KIRA: `https://drive.google.com/file/d/1lzaDeKNcFgfPukyogZX5cC8l889GbfQQ/view?usp=sharing`

---

## Capturas de Tela

### Tela de Autenticação (`/entrar/`)
<img width="1861" height="939" alt="image" src="https://github.com/user-attachments/assets/6c28d5f6-5f1f-4afc-bb0f-bb44936eb815" />

### Repositório e Consulta de Inovações
<img width="1848" height="948" alt="image" src="https://github.com/user-attachments/assets/a04eaa3b-53cc-4f29-bc4c-607bdc8bb845" />

<img width="1854" height="946" alt="image" src="https://github.com/user-attachments/assets/0cb8fe25-98c9-4118-8bc6-2cc54164f31c" />

### Cadastro de Inovações(`/user/`)
<img width="1848" height="944" alt="image" src="https://github.com/user-attachments/assets/90b9bbf7-3a54-4bc2-9dc6-0a759844f7bb" />

### Painel de Indicadores (Gráficos SVG)
<img width="1846" height="937" alt="image" src="https://github.com/user-attachments/assets/7ff24fef-f091-4e2a-8fdd-7481434a625b" />

---

## Funcionalidades

- [x] Cadastro e consulta centralizada de inovações administrativas de back office
- [x] Compartilhamento e histórico de status e reaproveitamentos entre unidades
- [x] Autenticação e gerenciamento de sessão de usuários via Django
- [x] Painel de indicadores com gráficos SVG gerados no servidor
- [x] Carga de acervo de demonstração com 500 inovações, autores, histórico de status e reaproveitamentos (`RNF08`)
- [x] Design responsivo para desktop e tablet (sem aplicativo móvel nativo no escopo)
- [x] Conformidade de acessibilidade com **WCAG 2.1 — nível AA** e **eMAG** (contraste adequado, navegação por teclado, foco visível, HTML semântico, rótulos associados aos formulários, alternativas textuais e independência exclusiva de cores)
- [x] Compatibilidade com navegadores modernos (Google Chrome, Mozilla Firefox e Microsoft Edge)

---

## Estrutura do Projeto

```text
kira-repositorio-inovacoes/
├── config/                    # Configurações globais do Django e entradas WSGI/ASGI
├── contas/                    # Autenticação, perfis de usuário e permissões
├── indicadores/               # Painel de métricas e geração de gráficos SVG
├── inovacoes/                 # Cadastro, busca, histórico e reaproveitamento de inovações
├── nucleo/                    # Recursos base compartilhados do sistema
├── templates/
│   └── kira.css               # Folha de estilo própria (sem framework CSS)
├── docs/
│   ├── decisao-mvt.md         # Justificativa da arquitetura MVT
│   ├── design-spec.md         # Especificação visual da interface
│   ├── mapa-de-features.md    # Mapeamento de funcionalidades do MVP
│   ├── modelagem-uml.md       # Diagramas e modelagem UML
│   ├── requisitos.md          # Requisitos funcionais e não funcionais
│   └── roteiro-deploy.md      # Roteiro detalhado de deploy (Vercel + Neon)
├── .env.example               # Modelo de variáveis de ambiente
├── manage.py                  # Utilitário de linha de comando do Django
├── requirements.txt           # Dependências do projeto Python
└── README.md                  # Este arquivo
```

---

## Tecnologias Utilizadas

| Tecnologia | Descrição |
| :--- | :--- |
| **Python 3.13** | Linguagem principal do back-end e runtime na Vercel |
| **Django 5.2** | Framework principal, templates HTML semântico, autenticação e gerenciamento de sessão |
| **PostgreSQL 16** | Banco de dados relacional para persistência e integridade referencial |
| **HTML5 & CSS3 (`kira.css`)** | Estrutura semântica e estilização própria baseada no `docs/design-spec.md`, sem framework CSS |
| **SVG (Server-side)** | Gráficos do painel de indicadores gerados diretamente no servidor |
| **Pytest** | Execução da suíte de testes automatizados |
| **Vercel** | Hospedagem da aplicação web em produção (runtime Python) |
| **Neon (AWS São Paulo)** | Hospedagem do PostgreSQL 16 em nuvem (`aws-sa-east-1`) com connection pooling (PgBouncer) |

---

## Pré-requisitos

Antes de começar, você precisará ter:

- **Python 3.13** instalado
- **PostgreSQL 16** instalado localmente (para ambiente de desenvolvimento)
- Navegador web moderno (Google Chrome, Mozilla Firefox ou Microsoft Edge)
- Conta na **Vercel** e no **Neon** (apenas para deploy em produção)

---

## Configuração e Como Executar o Projeto (Local)

### 1. Clone o repositório e acesse a pasta

```bash
git clone <URL_DO_REPOSITORIO>
cd kira-repositorio-inovacoes
```

### 2. Crie e ative o ambiente virtual

```bash
python -m venv .venv
```

- **Windows:**
  ```bash
  .venv\Scripts\activate
  ```
- **Linux/macOS:**
  ```bash
  source .venv/bin/activate
  ```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente e o banco de dados

Copie o arquivo modelo e preencha a chave secreta, `DJANGO_DEBUG=True` e as credenciais do PostgreSQL local (`POSTGRES_*`):

```bash
cp .env.example .env
```

Crie o banco de dados indicado em `POSTGRES_DB` no PostgreSQL local (sem `DATABASE_URL` definida, o sistema utiliza automaticamente as variáveis `POSTGRES_*`).

### 5. Execute as migrações e inicie o servidor

```bash
python manage.py migrate
python manage.py runserver
```

Acesse `http://127.0.0.1:8000/` no navegador.

### 6. (Opcional) Carregue o acervo de demonstração e rode os testes

```bash
# Criar superusuário e carregar 500 inovações de demonstração (RNF08)
python manage.py createsuperuser
python manage.py carregar_demonstracao

# Executar testes
pytest -q
```

---

## Deploy em Produção (Vercel + Neon)

A aplicação roda na **Vercel** como função Python (`config/wsgi.py`, Python 3.13) conectada ao **PostgreSQL 16** hospedado no **Neon** (plano gratuito, região `aws-sa-east-1`) utilizando conexão **pooled** (`-pooler` via PgBouncer). O `kira.css` é embutido nas páginas e o CSS do Django Admin é coletado via `collectstatic` no build.

### Variáveis de Ambiente (Production)

Configure em **Settings → Environments → Production** na Vercel:

| Variável | Valor em produção |
| :--- | :--- |
| `DJANGO_SECRET_KEY` | Chave longa e aleatória exclusiva de produção |
| `DJANGO_DEBUG` | `False` |
| `DJANGO_ALLOWED_HOSTS` | `<projeto>.vercel.app` (sem `https://`) |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://<projeto>.vercel.app` (sem barra no final) |
| `DATABASE_URL` | String de conexão **pooled** do Neon (host com `-pooler`) |

> Para gerar uma `DJANGO_SECRET_KEY`:
> ```bash
> .venv/bin/python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
> ```

### Passo a Passo Resumido

1. **Neon:** Crie um projeto com **Postgres 16** na região **AWS São Paulo (`aws-sa-east-1`)** e copie as strings de conexão **pooled** (com `-pooler`) e **direta** (sem `-pooler`).
2. **Migrações no banco em nuvem:** Utilize a string **direta** para rodar as migrações e criar o superusuário:
   ```bash
   read -rs 'U?URL direta do Neon: ' && print -r -- "DATABASE_URL=$U" > ~/.kira-neon.env && chmod 600 ~/.kira-neon.env && unset U
   export DATABASE_URL="$(sed -n 's/^DATABASE_URL=//p' ~/.kira-neon.env)"
   .venv/bin/python manage.py migrate
   .venv/bin/python manage.py createsuperuser
   unset DATABASE_URL
   ```
3. **Vercel:** Rode `npx vercel login` e `npx vercel link` na raiz do projeto, cadastre as 5 variáveis de ambiente acima (usando a `DATABASE_URL` **pooled**) e execute o deploy de produção:
   ```bash
   npx vercel --prod --logs
   ```
4. **Conferência:** Acesse `https://<projeto>.vercel.app/entrar/`, faça login com o administrador criado e valide `/admin/`.

> O roteiro completo com resolução de problemas está disponível em [`docs/roteiro-deploy.md`](docs/roteiro-deploy.md). Sempre que houver alteração nos *models*, execute `manage.py migrate` antes do deploy do código dependente.

---

## Funcionalidades Detalhadas & Objetivos

O sistema busca contribuir diretamente para a gestão do conhecimento organizacional ao:

- **Reduzir retrabalho entre unidades:** centralizando iniciativas de back office já validadas ou em andamento;
- **Facilitar a descoberta e replicação:** permitindo consultar soluções existentes e acompanhar seu histórico de reaproveitamento;
- **Preservar o conhecimento organizacional:** documentando autores, histórico de status e detalhes das soluções;
- **Apoiar a tomada de decisão:** oferecendo uma visão estruturada das iniciativas por meio de indicadores.

---

## Contexto Acadêmico e Referências

Projeto desenvolvido como **Trabalho de Conclusão de Curso (TCC)** integrando áreas de Engenharia de Software, Engenharia de Requisitos, Desenvolvimento Web, Banco de Dados, Interação Humano-Computador (IHC), UX/UI, Acessibilidade, Segurança da Informação, Gestão do Conhecimento, Governança de TI e Qualidade de Software.

### Referenciais Considerados

- **ISO/IEC 25010** — Qualidade de Software
- **Heurísticas de Usabilidade de Nielsen** e **System Usability Scale (SUS)**
- **WCAG 2.1 (Nível AA)** e **eMAG** (Modelo de Acessibilidade em Governo Eletrônico)
- **Lei Geral de Proteção de Dados Pessoais (LGPD)**
- **Objetivos de Desenvolvimento Sustentável (ODS)**

---

## Autoria

- **Ruan Almeida**
- **Sofia Nascimento**

**Curso:** `Sistemas de Informação`  
**Instituição:** `Centro Universitário Fametro`  
**Orientador(a):** `Luana Leal`  
**Ano:** `2026`

---

## Licença

A licença de distribuição do projeto ainda será definida. Enquanto não houver uma licença explicitamente associada ao repositório, o código não deve ser considerado disponibilizado sob uma licença open source.

---

<p align="center">
  <strong>KIRA — Conhecimento, Inovação e Replicação Administrativa</strong><br>
  <em>Transformando soluções locais em conhecimento compartilhado.</em>
</p>
