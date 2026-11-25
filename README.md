<div align="center">

# 🚀 KIRA — Conhecimento, Inovação e Replicação Administrativa

**Sistema web para registro, compartilhamento, consulta e reaproveitamento de inovações de back office entre unidades de uma organização.**

![Status](https://img.shields.io/badge/status-MVP%20publicado-brightgreen?style=for-the-badge)
![Projeto](https://img.shields.io/badge/projeto-TCC-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.2-092E20?style=for-the-badge&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![License](https://img.shields.io/badge/license-a%20definir-lightgrey?style=for-the-badge)

[**🌐 Demo ao Vivo**](https://kira-nu-green.vercel.app) · [**🎬 Vídeo de Apresentação**](https://drive.google.com/file/d/1lzaDeKNcFgfPukyogZX5cC8l889GbfQQ/view?usp=sharing) · [**📄 Documentação**](docs/)

</div>

---

## 📋 Sobre o Projeto

O **KIRA — Conhecimento, Inovação e Replicação Administrativa** é um protótipo funcional (MVP) desenvolvido como Trabalho de Conclusão de Curso (TCC).

O sistema parte do problema de que soluções administrativas criadas localmente costumam ficar restritas à unidade onde surgiram, fazendo com que outras unidades enfrentem problemas semelhantes e desenvolvam novamente soluções que já existem na própria organização. O KIRA centraliza essas iniciativas para consulta, acompanhamento e reaproveitamento em áreas de back office como:

- **Financeiro** e **Compras**;
- **Recursos Humanos**;
- **Tecnologia da Informação interna**;
- **Atendimento interno** e **Processos administrativos**.

---

## ✨ Principais Funcionalidades

- 🎯 **Repositório Centralizado:** Registro, busca e consulta estruturada de inovações administrativas de back office entre unidades.
- 🔄 **Rastreabilidade e Replicação:** Compartilhamento de soluções com histórico de status e acompanhamento de reaproveitamentos.
- 📊 **Painel de Indicadores (SVG):** Visualização gerencial com gráficos SVG gerados diretamente no servidor.
- 🔒 **Autenticação e Sessões:** Controle de acesso, perfis de usuário e administração via Django.
- ⚡ **Acervo de Demonstração (`RNF08`):** Comando automatizado para carga de 500 inovações com autores, histórico de status e reaproveitamentos.
- ♿ **Acessibilidade e Responsividade:** Conformidade com **WCAG 2.1 (Nível AA)** e **eMAG** (contraste adequado, navegação por teclado, foco visível, HTML semântico e independência exclusiva de cores), responsivo para desktop e tablet.

---

## 🎬 Demonstração

### Vídeo de Apresentação
> 🎥 Assista à apresentação completa do sistema: [**Vídeo de Demonstração (Google Drive)**](https://drive.google.com/file/d/1lzaDeKNcFgfPukyogZX5cC8l889GbfQQ/view?usp=sharing)

### Screenshots

<div align="center">
  <img src="https://github.com/user-attachments/assets/6c28d5f6-5f1f-4afc-bb0f-bb44936eb815" alt="Tela de Autenticação (/entrar/)" width="48%">
  <img src="https://github.com/user-attachments/assets/a04eaa3b-53cc-4f29-bc4c-607bdc8bb845" alt="Repositório e Consulta de Inovações" width="48%">
</div>

<br>

<div align="center">
  <img src="https://github.com/user-attachments/assets/0cb8fe25-98c9-4118-8bc6-2cc54164f31c" alt="Detalhes da Inovação" width="48%">
  <img src="https://github.com/user-attachments/assets/90b9bbf7-3a54-4bc2-9dc6-0a759844f7bb" alt="Cadastro de Inovações (/user/)" width="48%">
</div>

<br>

<div align="center">
  <img src="https://github.com/user-attachments/assets/7ff24fef-f091-4e2a-8fdd-7481434a625b" alt="Painel de Indicadores (Gráficos SVG)" width="70%">
</div>

---

## 🛠️ Tecnologias Utilizadas

### Frontend
![HTML5](https://img.shields.io/badge/HTML5_Semântico-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3_(kira.css)-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![SVG](https://img.shields.io/badge/SVG_Server--Side-FFB13B?style=for-the-badge&logo=svg&logoColor=black)

### Backend & Banco de Dados
![Python](https://img.shields.io/badge/Python_3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django_5.2_(MVT)-092E20?style=for-the-badge&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL_16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)

### Ferramentas, Testes & Infraestrutura
![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)
![Vercel](https://img.shields.io/badge/Vercel_(Python_Runtime)-000000?style=for-the-badge&logo=vercel&logoColor=white)
![Neon](https://img.shields.io/badge/Neon_Postgres_(AWS_SP)-00E599?style=for-the-badge&logo=postgresql&logoColor=black)

---

## 🚀 Começando

### 📦 Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- **Python 3.13**
- **PostgreSQL 16** (para execução local)
- **Git** e navegador moderno (Google Chrome, Mozilla Firefox ou Microsoft Edge)

### 💻 Instalação (Ambiente Local)

1. **Clone o repositório**
   ```bash
   git clone <URL_DO_REPOSITORIO>
   ```

2. **Acesse a pasta do projeto**
   ```bash
   cd kira-repositorio-inovacoes
   ```

3. **Crie e ative o ambiente virtual**
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```

4. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure as variáveis de ambiente e o banco local**
   ```bash
   cp .env.example .env
   ```
   Ajuste a chave secreta, `DJANGO_DEBUG=True` e as credenciais `POSTGRES_*` no `.env`. Crie no PostgreSQL local o banco indicado em `POSTGRES_DB` (sem `DATABASE_URL` definida, o sistema utiliza as variáveis `POSTGRES_*`).

6. **Execute as migrações e inicie o servidor**
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

7. **Acesse no navegador**
   ```text
   [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
   ```

8. *(Opcional)* **Crie um administrador e carregue o acervo de demonstração (`RNF08`)**
   ```bash
   python manage.py createsuperuser
   python manage.py carregar_demonstracao
   ```

---

## ☁️ Deploy em Produção (Vercel + Neon)

A aplicação roda na **Vercel** (`config/wsgi.py`, Python 3.13) conectada ao **PostgreSQL 16** no **Neon** (região `aws-sa-east-1`, plano gratuito) via conexão **pooled** (`-pooler` com PgBouncer).

| Variável | Valor em Produção (`Settings → Environments → Production`) |
| :--- | :--- |
| `DJANGO_SECRET_KEY` | Chave longa e aleatória exclusiva de produção |
| `DJANGO_DEBUG` | `False` |
| `DJANGO_ALLOWED_HOSTS` | `kira-nu-green.vercel.app` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://kira-nu-green.vercel.app` |
| `DATABASE_URL` | String de conexão **pooled** do Neon (host com `-pooler`) |

- **Migrações em nuvem:** utilize a URL **direta** do Neon (sem `-pooler`) para rodar `manage.py migrate` e `manage.py createsuperuser`.
- **Publicação:** execute `npx vercel --prod --logs` e valide em `https://kira-nu-green.vercel.app/inovacoes/` e `/admin/`.
- O passo a passo completo está documentado em [`docs/roteiro-deploy.md`](docs/roteiro-deploy.md).

---

## 🗂️ Estrutura de Pastas

```text
📦 kira-repositorio-inovacoes
├── 📁 config/                  # Configurações globais do Django e entradas WSGI/ASGI
├── 📁 contas/                  # Autenticação, perfis de usuário e permissões
├── 📁 indicadores/             # Painel de métricas e geração de gráficos SVG
├── 📁 inovacoes/               # Cadastro, busca, histórico e reaproveitamento de inovações
├── 📁 nucleo/                  # Recursos base compartilhados do sistema
├── 📁 templates/
│   └── 📄 kira.css             # Folha de estilo própria (sem framework CSS)
├── 📁 docs/
│   ├── 📄 decisao-mvt.md       # Justificativa da arquitetura MVT
│   ├── 📄 design-spec.md       # Especificação visual da interface
│   ├── 📄 mapa-de-features.md  # Mapeamento de funcionalidades do MVP
│   ├── 📄 modelagem-uml.md     # Diagramas e modelagem UML
│   ├── 📄 requisitos.md        # Requisitos funcionais e não funcionais
│   └── 📄 roteiro-deploy.md    # Roteiro detalhado de deploy (Vercel + Neon)
├── 📄 .env.example             # Modelo de variáveis de ambiente
├── 📄 manage.py                # Utilitário de linha de comando do Django
├── 📄 requirements.txt         # Dependências do projeto Python
└── 📄 README.md                # Este arquivo
```

---

## 🧪 Testes

Execute a suíte de testes automatizados com:

```bash
pytest -q
```

---

## 📚 Contexto Acadêmico e Referências

Projeto desenvolvido como **Trabalho de Conclusão de Curso (TCC)** integrando Engenharia de Software, Engenharia de Requisitos, Desenvolvimento Web, Banco de Dados, IHC, UX/UI, Acessibilidade, Segurança da Informação, Gestão do Conhecimento, Governança de TI e Qualidade de Software.

**Referenciais considerados:** ISO/IEC 25010 · Heurísticas de Nielsen · System Usability Scale (SUS) · WCAG 2.1 (Nível AA) · eMAG · LGPD · ODS.

---

## 📄 Licença

A licença de distribuição do projeto ainda será definida. Enquanto não houver uma licença explicitamente associada ao repositório, o código não deve ser considerado disponibilizado sob uma licença open source.

---

## 👨‍💻 Autoria

- **Ruan Almeida**
- **Sofia Nascimento**

**Curso:** `Sistemas de Informação` · **Instituição:** `Centro Universitário Fametro`  
**Orientador(a):** `Luana Leal` · **Ano:** `2026`

---

<div align="center">

⭐ **KIRA — Conhecimento, Inovação e Replicação Administrativa**  
*Transformando soluções locais em conhecimento compartilhado.*

</div>
