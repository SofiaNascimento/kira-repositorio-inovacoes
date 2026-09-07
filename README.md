# KIRA — Conhecimento, Inovação e Replicação Administrativa

> Sistema web para registro, compartilhamento, consulta e reaproveitamento de inovações de back office entre unidades de uma organização.

![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)
![Projeto](https://img.shields.io/badge/projeto-TCC-blue)
![Python](https://img.shields.io/badge/Python-3.x-blue)
![Django](https://img.shields.io/badge/Django-Web%20Framework-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue)
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

A interface é construída utilizando tecnologias web integradas à aplicação Django.

> A definição final das tecnologias e bibliotecas utilizadas no front-end será atualizada conforme a implementação do MVP.

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

> As instruções abaixo representam o fluxo planejado para o ambiente Django e deverão ser atualizadas conforme a configuração definitiva do projeto.

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

### 5. Configure o banco de dados

O projeto utiliza PostgreSQL. As configurações de conexão deverão ser definidas por variáveis de ambiente.

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
