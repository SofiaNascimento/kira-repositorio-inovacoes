# Autenticação (F1) — Specification

**Fontes:** `docs/requisitos.md` (RF01, RN04, RN11, RNF02, RNF07) · `docs/mapa-de-features.md` (F1)
**Decisões vinculantes:** AD-001 (sessão nativa do Django, não JWT) · AD-004 (perfil como campo enum)
**Contexto da discussão:** `.specs/features/autenticacao/context.md`

> **Nota de notação:** os critérios de aceite estão em EARS, a sintaxe controlada em inglês
> (WHEN / WHILE / WHERE / IF-THEN / ubíquo + SHALL). O restante do documento está em português.
> Misturar aqui é proposital: EARS só é verificável — pelo `validate_spec.py` e por quem escreve o
> teste — nas palavras-chave originais.

## Problem Statement

O repositório de inovações é um sistema interno cujo conteúdo pertence à organização e cuja autoria
governa quem pode alterar o quê. Sem identidade não há autor, não há perfil e não há como restringir
consulta e edição — ou seja, nenhuma outra feature do MVP roda. Hoje não existe nenhuma barreira de
acesso nem modelo de usuário: F1 é a fundação que precisa existir antes de F2.

## Goals

- [ ] Um colaborador com conta consegue entrar no sistema informando usuário **ou** e-mail e senha, e
      permanece autenticado por sessão do Django entre requisições.
- [ ] Nenhuma tela interna é alcançável sem sessão autenticada — acesso anônimo é redirecionado ao login.
- [ ] Nenhuma senha existe em texto puro no banco, em log ou em resposta HTTP; apenas o hash do Django.
- [ ] O modelo de usuário carrega um campo de perfil restrito a `USUARIO` / `ADMINISTRADOR`, com ponto
      único de consulta que F4 usará para autorizar edição e exclusão.

## Out of Scope

Excluído explicitamente. Documentado para impedir scope creep.

| Feature | Reason |
| ------- | ------ |
| Autocadastro de usuários | Decidido: contas são criadas por administrador via Django admin; o primeiro admin nasce por `createsuperuser`. Nenhum RF pede tela de registro. |
| Bloqueio / throttling após N tentativas | Nenhum RN ou RNF exige. Mitigado por mensagem de erro genérica (não enumera contas) e log de tentativas. |
| Recuperação de senha ("esqueci minha senha") | Não consta em nenhum RF e exige serviço de e-mail no deploy gratuito (RNF06). Registrado em Deferred Ideas. |
| Autenticação multifator | Não consta nos requisitos; desproporcional ao MVP. |
| SSO, login social, LDAP / integração com diretório corporativo | Seção 8 do documento de requisitos coloca integração com sistemas legados fora do escopo. |
| Token / JWT / autenticação de API | Vedado por AD-001. |
| Tela própria de gestão de usuários | A nota da F1 resolve via Django admin; tela própria é incremento pós-MVP. |
| Autorização de edição e exclusão de inovações (RN05) | Pertence à F4. F1 entrega só o campo de perfil e seu ponto de consulta. |

---

## Assumptions & Open Questions

Toda ambiguidade está resolvida ou registrada aqui — nada fica silenciosamente indefinido.

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --------------------- | -------------- | --------- | ---------- |
| Como as contas passam a existir | Somente administrador cria contas; sem autocadastro | Decidido com o usuário; alinha à RN11 e ao contexto de sistema interno | y |
| Identificador aceito no login | Campo único aceita username **ou** e-mail, case-insensitive | Decidido com o usuário; leitura literal do RF01 e da modelagem UML | y |
| Bloqueio após tentativas malsucedidas | Fora do escopo do MVP | Decidido com o usuário; nenhum RN/RNF exige e é a parte mais cara de auth | y |
| E-mail obrigatório e único no modelo de usuário | Sim, unicidade case-insensitive | Login por e-mail é ambíguo sem unicidade; consequência direta da decisão acima | n |
| Duração da sessão | Expira após 8 horas sem requisições | Cobre uma jornada de trabalho sem forçar relogin; nenhum requisito fixa valor | n |
| Política de senha | Validadores padrão do Django (mín. 8 caracteres, não comum, não numérica, não similar ao usuário) | RNF02 pede boas práticas sem fixar regra; o default do framework já as atende | n |
| Texto e granularidade do erro de login | Mensagem única "Usuário ou senha inválidos.", sem distinguir qual campo falhou | RF13 pede clareza, RNF02 pede segurança; não revelar o campo evita enumeração de contas | n |
| Destino após login bem-sucedido | Página inicial interna (lista de inovações da F3); enquanto F3 não existir, uma página interna mínima | Evita bloquear F1 na dependência de F3; o `next` tem precedência quando presente | n |
| Idioma dos critérios de aceite | EARS em inglês, restante do documento em português | `validate_spec.py` exige a palavra-chave `SHALL`; EARS é sintaxe controlada em inglês | n |

**Open questions:** none - todas resolvidas com o usuário ou registradas como assumption acima.

---

## Dimensions Sweep

Escopo Large ⇒ varredura completa: cada dimensão vira requisito ou recebe `N/A because…` explícito.

| Dimensão | Resolução |
| -------- | --------- |
| Input validation & bounds | AUTH-04 (campos vazios), AUTH-18 (valor de perfil fora do enum), AUTH-25 (e-mail duplicado) |
| Failure / partial-failure states | AUTH-03 (credencial inválida), AUTH-23 (conta inativa), AUTH-26 (banco indisponível) |
| Idempotency / retry / duplicate handling | AUTH-12 (usuário já autenticado pede a tela de login → redireciona em vez de duplicar sessão). Retry de login não tem efeito colateral a deduplicar: cada POST é independente e não cria registro. |
| Auth boundaries & rate limits | Boundaries: AUTH-09, AUTH-11, AUTH-21, AUTH-22. Rate limits: **N/A because** throttling ficou fora do escopo por decisão registrada; mitigação por mensagem genérica (AUTH-03) e log (AUTH-27). |
| Concurrency / ordering | **N/A because** sessões são independentes por navegador e o Django serializa o acesso à sessão; F1 não tem operação concorrente sobre um mesmo recurso mutável. |
| Data lifecycle / expiry | AUTH-13 (logout encerra), AUTH-14 (cookie revogado é anônimo), AUTH-15 (expiração por inatividade) |
| Observability | AUTH-27 (log de tentativa malsucedida, sem senha) |
| External-dependency failure | AUTH-26 (PostgreSQL indisponível durante autenticação). **N/A** para serviços externos além do banco: F1 não chama nenhum. |
| State-transition integrity | AUTH-05 (rotação da chave de sessão na transição anônimo → autenticado), AUTH-13/AUTH-14 (autenticado → anônimo), AUTH-17 (perfil inicial) |

---

## User Stories

### P1: Login por usuário ou e-mail com sessão do Django ⭐ MVP

**User Story**: Como colaborador da organização, quero entrar no sistema com meu usuário ou e-mail e
minha senha, para que minhas ações fiquem associadas a mim.

**Why P1**: É o RF01 e o pré-requisito de toda a F1. Sem sessão não há autor (RN08) nem perfil (RN05).

**Acceptance Criteria**:

1. WHEN an anonymous visitor submits the login form with an existing username and its matching password THEN the system SHALL authenticate the account, open a Django session and redirect to the internal home page.
2. WHEN an anonymous visitor submits the login form with the e-mail address of an existing account and its matching password THEN the system SHALL authenticate that same account, comparing the e-mail case-insensitively.
3. IF the submitted credentials match no active account THEN the system SHALL leave the visitor anonymous, re-render the login form with HTTP 200 and display exactly one message, "Usuário ou senha inválidos.", without indicating which field was wrong.
4. IF the login form is submitted with an empty identifier field or an empty password field THEN the system SHALL reject the submission, show an error message bound to the offending field and preserve the identifier value already typed.
5. WHEN authentication succeeds THEN the system SHALL rotate the session key before returning the response, so the session identifier held before login is no longer accepted.

**Independent Test**: criar uma conta pelo admin; entrar com o username, sair, entrar com o e-mail em
caixa alta; tentar entrar com senha errada e observar a mensagem única; inspecionar o cookie de
sessão antes e depois do login e confirmar que o identificador mudou.

---

### P1: Senha armazenada apenas como hash ⭐ MVP

**User Story**: Como organização sujeita à LGPD, quero que nenhuma senha exista em texto puro em
lugar nenhum, para que um vazamento de banco ou de log não exponha credenciais.

**Why P1**: É o RNF02, classificado Essencial, e a premissa `senhaHash` da modelagem UML.

**Acceptance Criteria**:

1. The system SHALL store every user password only as a hash produced by Django's configured password hashers, never as plain text nor as a reversible encoding.
2. WHEN a password is created or changed for any account THEN the system SHALL persist only the resulting hash.
3. The system SHALL NOT write a plain-text password to the application log, to any HTTP response body or to any error page, including on failed login attempts.

**Independent Test**: criar um usuário, consultar a linha na tabela de usuários e confirmar que o
campo de senha traz o prefixo do algoritmo do Django e não a senha; provocar um login malsucedido e
conferir que a senha submetida não aparece no log nem na resposta.

---

### P1: Telas internas restritas a usuário autenticado ⭐ MVP

**User Story**: Como organização, quero que o conteúdo do repositório só seja alcançável por quem
está autenticado, para que inovações internas não fiquem expostas.

**Why P1**: É a RN04 e a base do RNF07; sem isso F2 e F3 nascem abertas.

**Acceptance Criteria**:

1. WHILE the visitor has no authenticated session the system SHALL deny every internal screen and redirect the request to the login page, carrying the originally requested path in the `next` query parameter.
2. WHEN a visitor authenticates on a login page that carries a `next` parameter pointing to an internal path THEN the system SHALL redirect to that path instead of the default home page.
3. WHILE an authenticated session is active the system SHALL grant access to the consultation screens regardless of the user's profile value.
4. WHEN an already-authenticated user requests the login page THEN the system SHALL redirect to the internal home page instead of rendering the form again.

**Independent Test**: com o navegador anônimo, pedir uma URL interna e observar o redirecionamento
com `next`; autenticar e confirmar que cai na URL originalmente pedida; já autenticado, pedir
`/login/` e confirmar o redirecionamento.

---

### P1: Encerramento de sessão ⭐ MVP

**User Story**: Como colaborador, quero sair do sistema e ter certeza de que minha sessão acabou,
para que ninguém use meu acesso em um computador compartilhado.

**Why P1**: O caso de uso 'Sair da plataforma' faz par com 'Realizar login' no RF01; uma sessão que
não pode ser encerrada contraria o RNF02.

**Acceptance Criteria**:

1. WHEN an authenticated user activates the logout action THEN the system SHALL terminate the session server-side, clear the session cookie and redirect to the login page showing the message "Sessão encerrada.".
2. WHEN a request arrives carrying a session cookie that a previous logout terminated THEN the system SHALL treat that request as anonymous.
3. The system SHALL expire an authenticated session after 8 hours without requests, returning the visitor to the anonymous state.

**Independent Test**: autenticar, sair, usar o botão voltar do navegador em uma tela interna e
confirmar o redirecionamento ao login; reenviar manualmente o cookie antigo e confirmar que o acesso
é negado.

---

### P1: Perfil USUARIO / ADMINISTRADOR no modelo de usuário ⭐ MVP

**User Story**: Como administrador do repositório, quero que cada conta carregue um perfil explícito,
para que a curadoria (F4) saiba quem pode editar e excluir registros de terceiros.

**Why P1**: Materializa o AD-004 e é a base do RNF07; F4 não pode ser especificada sem este campo.

**Acceptance Criteria**:

1. The system SHALL represent the user profile as a single field on the Django user model, constrained to exactly the values `USUARIO` and `ADMINISTRADOR`.
2. WHEN an account is created without an explicit profile THEN the system SHALL assign the profile `USUARIO`.
3. IF a profile value outside `USUARIO` and `ADMINISTRADOR` is assigned to an account THEN the system SHALL reject the save with a validation error and leave the stored value unchanged.
4. The system SHALL provide one query point that reports whether an account holds administrator powers, and every other feature SHALL use it rather than comparing the raw field.
5. WHEN a superuser is created through `createsuperuser` THEN the system SHALL assign it the profile `ADMINISTRADOR`.

**Independent Test**: criar uma conta pelo admin sem informar perfil e conferir que nasce `USUARIO`;
tentar gravar um perfil inválido pelo shell e observar o `ValidationError`; rodar `createsuperuser` e
confirmar que a conta sai como `ADMINISTRADOR`.

---

### P2: Atribuição de perfil restrita a administrador

**User Story**: Como organização, quero que apenas um administrador possa promover outra conta a
administrador, para que ninguém se autoconceda poderes de curadoria.

**Why P2**: A RN11 é classificada Importante no documento de requisitos; o MVP funciona sem ela
enquanto houver um único admin criado por `createsuperuser`.

**Acceptance Criteria**:

1. WHILE the authenticated user holds the profile `USUARIO` the system SHALL reject any request that changes a profile field, on their own account or on another account, returning HTTP 403 when the request reaches the change handler and redirecting to the login page when the account cannot open the administration area.
2. WHERE the Django admin is enabled the system SHALL allow only accounts holding the profile `ADMINISTRADOR` to open the user administration screens and change another account's profile.

**Independent Test**: autenticar como `USUARIO`, tentar abrir a tela de usuários do admin e observar
o 403; autenticar como `ADMINISTRADOR`, promover uma conta e confirmar a alteração.

---

## Edge Cases

- **AUTH-23** — IF the submitted credentials match an account flagged inactive THEN the system SHALL refuse the login with the same generic message used for wrong credentials, and SHALL NOT open a session.
- **AUTH-24** — IF the login form is submitted without a valid CSRF token THEN the system SHALL reject the request with HTTP 403 and SHALL NOT attempt authentication.
- **AUTH-25** — IF an account is created with an e-mail that differs from an existing one only by letter case THEN the system SHALL reject the creation with a uniqueness validation error.
- **AUTH-26** — IF the database is unreachable while a login attempt is being processed THEN the system SHALL return an error page, SHALL NOT open a session and SHALL NOT expose the connection details to the visitor.
- **AUTH-27** — WHEN a login attempt fails THEN the system SHALL write a log entry carrying the timestamp and the submitted identifier, and SHALL NOT carry the submitted password.

---

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
| -------------- | ----- | ----- | ------ |
| AUTH-01 | P1: Login por usuário ou e-mail | Design | Pending |
| AUTH-02 | P1: Login por usuário ou e-mail | Design | Pending |
| AUTH-03 | P1: Login por usuário ou e-mail | Design | Pending |
| AUTH-04 | P1: Login por usuário ou e-mail | Design | Pending |
| AUTH-05 | P1: Login por usuário ou e-mail | Design | Pending |
| AUTH-06 | P1: Senha apenas como hash | Design | Pending |
| AUTH-07 | P1: Senha apenas como hash | Design | Pending |
| AUTH-08 | P1: Senha apenas como hash | Design | Pending |
| AUTH-09 | P1: Telas internas restritas | Design | Pending |
| AUTH-10 | P1: Telas internas restritas | Design | Pending |
| AUTH-11 | P1: Telas internas restritas | Design | Pending |
| AUTH-12 | P1: Telas internas restritas | Design | Pending |
| AUTH-13 | P1: Encerramento de sessão | Design | Pending |
| AUTH-14 | P1: Encerramento de sessão | Design | Pending |
| AUTH-15 | P1: Encerramento de sessão | Design | Pending |
| AUTH-16 | P1: Perfil USUARIO / ADMINISTRADOR | Implementing | Implementing |
| AUTH-17 | P1: Perfil USUARIO / ADMINISTRADOR | Implementing | Implementing |
| AUTH-18 | P1: Perfil USUARIO / ADMINISTRADOR | Implementing | Implementing |
| AUTH-19 | P1: Perfil USUARIO / ADMINISTRADOR | Implementing | Implementing |
| AUTH-20 | P1: Perfil USUARIO / ADMINISTRADOR | Design | Pending |
| AUTH-21 | P2: Atribuição de perfil restrita | - | Pending |
| AUTH-22 | P2: Atribuição de perfil restrita | - | Pending |
| AUTH-23 | Edge case: conta inativa | Design | Pending |
| AUTH-24 | Edge case: CSRF ausente | Design | Pending |
| AUTH-25 | Edge case: e-mail duplicado por caixa | Design | Pending |
| AUTH-26 | Edge case: banco indisponível | Design | Pending |
| AUTH-27 | Edge case: log de tentativa malsucedida | Design | Pending |

**ID format:** `AUTH-NN`
**Status values:** Pending → In Design → In Tasks → Implementing → Verified
**Coverage:** 27 total, 0 mapeados para tasks (fase Tasks ainda não executada), 0 sem mapeamento ⚠️

---

## Rastreabilidade com o Documento de Requisitos

| Origem | Requirement IDs |
| ------ | --------------- |
| RF01 | AUTH-01 … AUTH-05, AUTH-13, AUTH-14, AUTH-23, AUTH-24 |
| RN04 | AUTH-09, AUTH-10, AUTH-11, AUTH-12 |
| RN11 | AUTH-21, AUTH-22 |
| RNF02 | AUTH-05, AUTH-06, AUTH-07, AUTH-08, AUTH-15, AUTH-26, AUTH-27 |
| RNF07 | AUTH-16 … AUTH-20 (base do perfil consumida pela F4) |
| AD-001 | AUTH-01, AUTH-05, AUTH-13, AUTH-15 |
| AD-004 | AUTH-16, AUTH-17, AUTH-18, AUTH-19, AUTH-20 |

---

## Success Criteria

- [ ] Um colaborador com conta entra com username e com e-mail (em qualquer caixa) e permanece
      autenticado entre requisições; credencial inválida devolve a mensagem única e nenhuma sessão.
- [ ] Nenhuma URL interna responde conteúdo a um cliente sem sessão — verificado varrendo as rotas
      internas registradas e confirmando redirecionamento ao login em todas.
- [ ] A coluna de senha no PostgreSQL não contém nenhum valor legível; uma busca pela senha de teste
      no log da aplicação e no corpo das respostas não retorna ocorrência.
- [ ] `createsuperuser` produz conta `ADMINISTRADOR`; conta criada pelo admin sem perfil nasce
      `USUARIO`; perfil fora do enum é rejeitado.
- [ ] Um usuário `USUARIO` recebe 403 ao tentar alterar qualquer perfil.
