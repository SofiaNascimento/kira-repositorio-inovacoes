# Gestão por Unidade Context

**Gathered:** 2026-11-15
**Spec:** `.specs/features/gestao-por-unidade/spec.md`
**Status:** Spec aprovada em 2026-11-23; em Design

---

## Feature Boundary

Vincular cada conta a uma unidade e criar o papel de gestor de unidade, que, em telas próprias do
KIRA ("Minha unidade"), cria, desativa, reativa e redefine a senha das contas USUARIO da sua
unidade e tem curadoria (editar, excluir, avançar status) sobre as inovações cuja unidade de
origem é a sua. Senha provisória exige troca no próximo login. O admin do Django segue só do
ADMINISTRADOR.

Origem: conversa de 2026-11-15 sobre escala da gestão de usuários em organizações com muitas
sedes. A feature irmã `link-administracao` resolve o acesso ao admin pela interface.

---

## Implementation Decisions

### Onde o gestor trabalha

- Telas próprias dentro do KIRA, com o visual da `design-spec.md`, não o admin do Django.
- O admin continua fechado a quem não é ADMINISTRADOR (AD-007 não é supersedida).

### Alcance da curadoria

- Pela unidade de origem da inovação, qualquer que seja o autor.
- Entra pela regra única da AD-009 (`Inovacao.pode_ser_alterada_por`); as views não mudam.

### Poderes sobre contas

- Criar (a conta nasce USUARIO, na unidade do gestor), desativar, reativar e definir senha provisória.
- Nomear gestor e mudar a unidade de alguém ficam com o ADMINISTRADOR.

### Unidade no cadastro

- Pré-preenchida com a unidade do usuário e editável. A mesma lógica vale para o reaproveitamento.

### Senha provisória

- Troca obrigatória no próximo login; o gestor nunca conhece a senha definitiva.

### Agent's Discretion

- Premissas anunciadas na conversa sem objeção (papel como terceiro valor do perfil, unidade
  opcional exceto para gestor, vários gestores por unidade, alvo fora do escopo → 404, só o
  gestor abre "Minha unidade", desativar sem página de confirmação). Estão na tabela de premissas
  da spec, confirmadas pelo usuário em 2026-11-23.
- Nomes de rotas, textos de alerta e ícone do item "Minha unidade" (Lucide `users`).

### Declined / Undiscussed Gray Areas → Assumptions

- Contas criadas pelo ADMINISTRADOR no admin: fluxo igual ao de hoje, campo de senha provisória
  visível e desmarcado. Registrado na spec.
- Rota de troca de senha aberta a todos, sem link no cabeçalho. Registrado na spec.

---

## Specific References

- Nenhuma referência visual nova: as telas usam os componentes da §6 v2 (tabela, barra de ações,
  resumo de erros, alerta) e a casca da R1.

---

## Deferred Ideas

- Login pelo diretório da organização (SSO via OIDC/SAML com Microsoft Entra ID, Google Workspace
  ou LDAP), com provisionamento no primeiro acesso e unidade vinda do diretório. Caminho de
  produção; vai no texto do TCC.
- Hierarquia de unidades (sede → regional → filial), quando a estrutura real estiver definida.
- Filtro "minha unidade" na lista e no painel.
- Importação de contas em lote (CSV).
- Trilha de auditoria das ações do gestor (LGPD).
- Link "Trocar senha" na área do usuário para qualquer pessoa.
- Recuperação de senha por e-mail e autocadastro por domínio institucional (ideias da F1).
- Unidade nos autores do acervo de demonstração e um gestor de exemplo no `carregar_demonstracao`.
