# Autenticação — Context

**Gathered:** 2026-09-21
**Spec:** `.specs/features/autenticacao/spec.md`
**Status:** Ready for design

---

## Feature Boundary

F1 entrega a fundação de identidade do sistema: login por usuário/e-mail e senha com sessão nativa
do Django, logout, restrição das telas internas a usuários autenticados, armazenamento da senha
apenas em hash e o campo de perfil (`USUARIO` / `ADMINISTRADOR`) no modelo de usuário.

Fora da fronteira: as regras que *usam* o perfil para autorizar edição e exclusão de inovações
(RN05) pertencem à F4. F1 entrega apenas o ponto único de consulta do perfil que a F4 consumirá.

---

## Implementation Decisions

### Criação de contas

- Não há autocadastro no MVP. O primeiro administrador nasce via `createsuperuser`; as demais contas
  são criadas por um administrador pelo Django admin.
- Consequência: F1 não tem tela de registro, nem validação de formulário de cadastro, nem fluxo de
  ativação por e-mail. O escopo fica em login, logout, proteção de rotas e perfil.
- Alinha com a RN11 (atribuição de perfil restrita a administrador) e com o contexto de sistema
  interno corporativo.

### Identificador de login

- Um único campo no formulário aceita **username ou e-mail**. O backend tenta primeiro o username e,
  não encontrando, tenta o e-mail, comparando de forma case-insensitive.
- Exige um authentication backend customizado somado ao `ModelBackend` padrão.
- Exige que o e-mail seja obrigatório e único (case-insensitive) no modelo de usuário — do contrário
  o login por e-mail é ambíguo.
- Leitura literal do RF01 e das notas do diagrama de casos de uso ("login por usuário/e-mail e senha").

### Bloqueio por tentativas malsucedidas

- Fora do escopo do MVP. Nenhum RN ou RNF pede lockout ou throttling, e é a parte mais cara de um
  módulo de autenticação (estado persistido de tentativas, relógio, testes de expiração).
- Mitigação adotada no lugar: a mensagem de erro é genérica e idêntica para usuário inexistente,
  senha errada e conta inativa, evitando enumeração de contas; toda tentativa malsucedida é
  registrada em log (sem a senha), deixando rastro para auditoria posterior.
- Registrado na tabela Out of Scope e na tabela de Assumptions da spec.

### Agent's Discretion

Defaults escolhidos pelo agente por não haver requisito que os fixe; cada um está registrado na
tabela **Assumptions & Open Questions** da spec e pode ser sobrescrito antes do Design:

- Duração da sessão (8 horas de inatividade).
- Política de senha (validadores padrão do Django).
- Texto exato das mensagens de erro e de logout.
- Destino do redirecionamento após login bem-sucedido.

### Declined / Undiscussed Gray Areas → Assumptions

Nenhuma área cinzenta foi recusada. As três apresentadas foram decididas; as demais dimensões
implícitas estão resolvidas na spec (requisito ou `N/A because…`) na seção Dimensions Sweep.

---

## Specific References

- `docs/modelagem-uml.md` §2.1 — a classe `Usuario` com atributo `perfil` do tipo `PerfilUsuario`
  e `senhaHash`; é a fonte do AD-004 e do RNF02 nesta feature.
- `docs/modelagem-uml.md` §3.1 — o fragmento `alt` do diagrama de sequência define o comportamento
  esperado do login: credencial inválida → recusa + mensagem de erro; credencial válida → sessão
  iniciada pelo Django. As ACs do P1-1 são a tradução direta desse fragmento.
- `.specs/STATE.md` — AD-001 (sessão nativa, não JWT) e AD-004 (perfil como enum) governam a feature.

---

## Deferred Ideas

- **Recuperação de senha por e-mail.** Surgiu como lacuna natural do login, mas não consta em nenhum
  RF e exige serviço de e-mail no deploy de camada gratuita (RNF06). Candidata a feature própria.
- **Tela de gestão de usuários fora do Django admin.** A nota da F1 no mapa de features já resolve
  via admin; uma tela própria seria incremento pós-MVP.
- **`maxlength` do campo de login para e-mails longos** *(achado no Execute, T14)*. O
  `AuthenticationForm` limita o identificador ao tamanho do username (150), e o `EmailField` aceita
  até 254. Um e-mail com mais de 150 caracteres não caberia no campo. Irrelevante para o volume do
  MVP; a correção é elevar o `maxlength` do campo para 254 no `LoginForm`.
- **Travar `is_staff`, `groups` e `user_permissions` para não administradores** *(achado no Execute,
  T24)*. Hoje só `perfil` e `is_superuser` ficam readonly. Um `USUARIO` com acesso manual ao admin
  poderia ampliar as próprias permissões de modelo. Correção de uma linha em
  `UsuarioAdmin.campos_so_do_administrador`, mais o teste correspondente.
