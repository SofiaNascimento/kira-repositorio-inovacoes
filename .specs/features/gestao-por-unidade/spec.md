# Gestão por Unidade — Specification

**Status:** Aprovada (2026-11-23), com o inventário de testes refeito depois da R2 e as emendas
E-1 a E-3 do Design. Escopo
Complex: Discuss feito (`context.md`); segue para Design e Tasks formais.

## Problem Statement

Hoje toda conta nasce à mão no admin, por um ADMINISTRADOR global, e o `Usuario` não sabe a que
unidade pertence. Numa organização com muitas sedes e muitos funcionários, o administrador vira
gargalo (cada admissão, desligamento e senha esquecida passa por ele) e a curadoria das inovações
de cada unidade depende de alguém que não conhece a unidade. A feature vincula cada pessoa a uma
unidade e cria o gestor de unidade, que cuida das contas e da curadoria da própria unidade.

## Goals

- [ ] Um gestor de unidade cria, desativa, reativa e redefine a senha das contas da sua unidade sem passar pelo ADMINISTRADOR.
- [ ] Um gestor de unidade edita, exclui e avança o status das inovações cuja unidade de origem é a sua.
- [ ] Nenhuma senha definida pelo gestor continua valendo depois do primeiro acesso da pessoa.
- [ ] O admin do Django segue fechado a quem não é ADMINISTRADOR (AD-007 intacta).
- [ ] Só os testes antigos do inventário (T-1 a T-6) mudam; suíte e build gate verdes.

## Code Reuse Analysis

| Item | Onde | Situação | Reuso |
| ---- | ---- | -------- | ----- |
| Perfil | `contas.models.PerfilUsuario` (`USUARIO`, `ADMINISTRADOR`), CHECK `usuario_perfil_valido`, `Usuario.is_administrador` (AD-004) | Enum de dois valores; `max_length=13` | Ganha `GESTOR_DE_UNIDADE` (17 caracteres: a coluna cresce na mesma migration); a CHECK acompanha o enum |
| Unidade | `inovacoes.models.Unidade` (`ItemDeLista`, RN07) | Lista controlada, renomeável pelo admin | FK nova em `Usuario` |
| Admin de usuários | `contas.admin.UsuarioAdmin` + `AcessoSomenteAdministradorMixin` (AD-007) | Única superfície de criação de conta e troca de perfil | Ganha o campo Unidade, coluna e filtro; continua só do ADMINISTRADOR |
| Regra de alteração | `Inovacao.pode_ser_alterada_por` + `AlteracaoDeInovacaoMixin` (AD-009) | "Autor ou ADMINISTRADOR" num lugar só | Ganha "ou gestor da unidade de origem"; editar, excluir e status herdam sem mudar as views |
| Login e sessão | `contas.backends`, `LoginRequiredMiddleware` (AD-006) | Recusa conta inativa; sessão invalida quando o hash da senha muda | Desativação e redefinição derrubam a sessão sem código novo |
| Casca | `nucleo.context_processors.casca` (`PAGINA_ATUAL`, AD-015), `templates/base.html` | Menu de 3 itens | Ganha o item "Minha unidade" só para o gestor |
| Página de recusa | `inovacoes/acesso_negado.html` | 403 própria da AD-009 | Modelo para a 403 da área do gestor |
| Validadores de senha | `AUTH_PASSWORD_VALIDATORS` (settings) | Usados pelo admin | Mesmos validadores nas telas novas |

---

## Out of Scope

| Feature | Reason |
| ------- | ------ |
| Login pelo diretório da organização (SSO/OIDC/SAML) | Depende de provedor de identidade e da TI da organização; vai no texto do TCC como caminho de produção. |
| Hierarquia de unidades (sede → regional → filial) | As unidades ainda são provisórias; só faz sentido com a estrutura real definida. |
| Filtro "minha unidade" na lista e no painel | Capacidade nova de consulta; feature própria. |
| Importação de usuários em lote (CSV) | Paliativo para escala; feature própria. |
| Recuperação de senha por e-mail e autocadastro | Exigem provedor de e-mail; ideias adiadas da F1. |
| Excluir contas | Apagar a conta apagaria a autoria (RN08); o gestor desativa. |
| Gestor nomear gestor ou mudar alguém de unidade | Fica com o ADMINISTRADOR, pelo admin (RN11 estendida). |
| Link "Trocar senha" no cabeçalho para qualquer usuário | A rota existe para todos, mas o link fica para depois (troca opcional não foi a escolha). |
| Trilha de auditoria (quem criou, desativou, redefiniu) | Desejável para LGPD, mas é capacidade nova; ideia adiada. |
| Vincular unidade aos autores do acervo de demonstração | O `carregar_demonstracao` segue igual; contas sem unidade são válidas. |

---

## Testes antigos que mudam (autorização na aprovação)

Inventário refeito em 2026-11-23 contra o código atual (depois da R2 e do link-administracao),
com varredura em todos os `*/tests/*.py` por: textos de permissão, enum e CHECK de perfil, menu
Principal, `PAGINA_ATUAL`, contagem de telas do DS-01, pasta de ícones e fixtures de páginas.

**Mudam (quebrariam sem a mudança):**

| # | Teste | Feature / AC | Muda o quê | Por quê |
| - | ----- | ------------ | ---------- | ------- |
| T-1 | `inovacoes/tests/test_views_edicao.py:16` e `inovacoes/tests/test_views_exclusao.py:13` (`SO_AUTOR`) | F4 (403 própria) | Texto passa a "Só quem cadastrou a inovação, um gestor da unidade de origem ou um administrador pode editá-la ou excluí-la." | A regra ganha o gestor (GEST-48, GEST-52) |
| T-2 | `inovacoes/tests/test_views_detalhe.py:451` e `inovacoes/tests/test_views_detalhe_v2.py:303` (`QUEM_PODE_AVANCAR`) | F5 STAT-41, R2 | Texto passa a "Só quem cadastrou a inovação, um gestor da unidade de origem ou um administrador pode avançar o status." | Idem (GEST-48, GEST-52) |
| T-3 | `contas/tests/test_models.py:13-15` (`test_perfil_tem_exatamente_usuario_e_administrador`) | F1 AUTH-16 | Afirma exatamente três valores, `["USUARIO", "ADMINISTRADOR", "GESTOR_DE_UNIDADE"]` | GEST-02 |
| T-4 | `nucleo/tests/test_casca.py:137-153` (`NOMES_DOS_ICONES` e `test_pasta_traz_os_icones_da_casca_e_da_consulta`) | R1 RED-16, RED-23 | A pasta passa a ter os 15 de hoje mais o ícone do item "Minha unidade" (Lucide `users`), nem mais nem menos | GEST-09 |
| T-5 | `inovacoes/tests/test_views_sistema_design.py:401-436` (`PECAS` e `assert len(telas) == 13`) | DS-01 | A contagem sobe pelas telas novas, número fixado no Design; parciais novas entram em `PECAS` | Telas novas estendem o base |

**Estendidos (continuam afirmando o mesmo, ganham casos):**

| # | Teste | Muda o quê | Por quê |
| - | ----- | ---------- | ------- |
| T-6 | `inovacoes/tests/test_views_sistema_design.py:71` (fixture `paginas`) | Ganha as telas novas (Minha unidade, criar conta, redefinir senha, trocar senha, recusa do gestor), renderizadas por um gestor | DS-02 a DS-05 e as checagens da casca em `test_casca.py` (atalho 1, faixa) passam a cobri-las |

**Conferidos e sem mudança:**

- `nucleo/tests/test_casca.py:286` (`MENU` de 3 itens), `:314`, `nucleo/tests/test_paginas_apoio.py:183-184` e `:243-244`: usam `autor` (USUARIO), que continua sem "Minha unidade".
- `nucleo/tests/test_casca.py:42-80` (`PAGINA_ATUAL`, RED-17, RED-18): casos parametrizados; nenhum fixa a tabela inteira.
- `contas/tests/test_constraints.py:15-52` (CHECK `usuario_perfil_valido` com `"CHEFE"` e os dois válidos): continuam verdadeiros com três valores.
- `contas/tests/test_controle_acesso.py:23-75` (varredura AD-006): rotas novas entram sozinhas e precisam redirecionar o anônimo; `ROTAS_PUBLICAS` não muda.
- `inovacoes/tests/test_controle_autoria.py:46` (varredura AD-009): só o namespace `inovacoes`; as rotas do gestor ficam fora dele.
- `contas/tests/test_admin.py:47-72`: afirma pertinência (`"perfil" in ...`), não a lista inteira.
- `inovacoes/tests/test_link_administracao.py`, `inovacoes/tests/test_views_cabecalho.py`: USUARIO e ADMINISTRADOR, sem gestor.
- `nucleo/tests/test_paginas_apoio.py:201-230` (Ajuda): fixa as seções, não o texto de permissão.
- Cadastro e reaproveitamento (INOV-15, `inovacoes/tests/test_forms.py`, `test_forms_reaproveitamento.py`): os usuários de teste não têm unidade; o Design mantém opcional o novo argumento de usuário nos formulários.

A página Ajuda (`templates/paginas/ajuda.html:28`) e a `design-spec.md` (§10, detalhe, linhas
556 e 574) recebem o texto novo. Qualquer outro teste antigo que precise mudar: parar e pedir.

---

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --------------------- | -------------- | --------- | ---------- |
| Onde o gestor trabalha | Telas próprias ("Minha unidade"), com o visual da `design-spec.md` | Admin segue só do ADMINISTRADOR (AD-007); escopo testável | y (2026-11-15) |
| Alcance da curadoria | Inovações cuja unidade de origem é a do gestor, qualquer autor | Coerente com a RN01 e os filtros | y |
| Poderes sobre contas | Criar (já na sua unidade), desativar, reativar, definir senha provisória | Tira o gargalo do ADMINISTRADOR | y |
| Unidade no cadastro de inovação | Pré-preenchida com a do usuário, editável | Muda pouco o formulário e os testes da F2 | y |
| Senha provisória | Troca obrigatória no próximo login | O gestor nunca conhece a senha definitiva (RNF02, LGPD) | y |
| Papel | Terceiro valor do perfil, `GESTOR_DE_UNIDADE` ("Gestor de unidade") | Estende a AD-004 sem segunda classe de usuário | y (2026-11-23) |
| Unidade do usuário | Opcional (nula), obrigatória só para o gestor (CHECK no banco) | Contas atuais, autores do acervo e ADMINISTRADORES seguem válidos | y (2026-11-23) |
| Gestores por unidade | Uma unidade pode ter vários gestores | Férias, substituição; nada pede exclusividade | y (2026-11-23) |
| Quem nomeia gestor | Só o ADMINISTRADOR, pelo admin (perfil + unidade) | RN11 estendida | y (2026-11-23) |
| Contas que o gestor administra | Só perfil USUARIO da própria unidade; nunca a si mesmo, outro gestor ou ADMINISTRADOR | Evita escalada lateral entre gestores | y (2026-11-23) |
| Resposta a alvo fora do escopo | 404 (a conta "não existe" para aquele gestor) | Não revela contas de outras unidades | y (2026-11-23) |
| Quem abre "Minha unidade" | Só o gestor; USUARIO e ADMINISTRADOR recebem a 403 própria | O ADMINISTRADOR tem o admin; evita escopo sem unidade | y (2026-11-23) |
| Desativar exige confirmação? | Não: é um POST com valor explícito, reversível | A RN12 é para ação destrutiva ou irreversível | y (2026-11-23) |
| Contas criadas pelo ADMINISTRADOR no admin | Fluxo igual ao de hoje; o campo "senha provisória" aparece no admin e começa desmarcado | Não muda os testes AUTH do admin | y (2026-11-23) |
| Rota de troca de senha | `/conta/senha/`, aberta a qualquer autenticado, obrigatória só com senha provisória | Uma tela só para os dois casos | y (2026-11-23) |
| Reaproveitamento | Unidade do usuário pré-selecionada quando é elegível; editável | Mesma lógica do cadastro | y (2026-11-23) |

**Open questions:** none - all resolved or logged above.

---

## User Stories

### P1: Unidade no usuário e papel de gestor ⭐ MVP

**User Story**: Como ADMINISTRADOR, quero vincular cada conta a uma unidade e nomear gestores de
unidade, para delegar a gestão de contas e a curadoria.

**Acceptance Criteria**:

1. The `Usuario` SHALL ter o campo opcional "unidade" (chave estrangeira para `Unidade`, `on_delete=PROTECT`).
2. The perfil SHALL aceitar o valor `GESTOR_DE_UNIDADE`, rotulado "Gestor de unidade", além de `USUARIO` e `ADMINISTRADOR`.
3. IF um `Usuario` com perfil `GESTOR_DE_UNIDADE` é gravado sem unidade THEN o banco SHALL recusar a gravação pela CHECK `usuario_gestor_tem_unidade`.
4. WHEN o ADMINISTRADOR abre a edição de um usuário no admin THEN o sistema SHALL exibir o campo "Unidade" na seção "Perfil", junto do campo "Perfil".
5. IF o ADMINISTRADOR salva no admin um usuário com perfil "Gestor de unidade" e unidade vazia THEN o sistema SHALL exibir no campo Unidade o erro "Gestor de unidade precisa de uma unidade." e não gravar.
6. WHEN o ADMINISTRADOR abre a lista de usuários no admin THEN o sistema SHALL exibir a coluna "Unidade" e o filtro por unidade.
7. WHILE o usuário tem perfil `GESTOR_DE_UNIDADE`, o sistema SHALL negar toda tela do admin como nega ao USUARIO (AD-007): sem `is_staff`, redireciona ao login do admin; com `is_staff`, responde 403. (Emenda E-1, 2026-11-23.)
8. IF o ADMINISTRADOR tenta excluir no admin uma unidade com usuários vinculados THEN o sistema SHALL recusar a exclusão e manter a unidade.

**Independent Test**: no admin, pôr a `maria` como gestora da Filial Norte; tentar salvar um
gestor sem unidade e ver o erro; entrar como `maria` e ser mandada ao login do admin em `/admin/`.

---

### P1: Área "Minha unidade" ⭐ MVP

**User Story**: Como gestor de unidade, quero ver as contas da minha unidade num só lugar, para
saber quem está ativo e agir sobre cada conta.

**Acceptance Criteria**:

1. WHILE o usuário autenticado tem perfil `GESTOR_DE_UNIDADE`, o sistema SHALL exibir no menu Principal, depois de "Indicadores", o item "Minha unidade" com `href="/minha-unidade/"`.
2. WHILE o usuário autenticado não tem perfil `GESTOR_DE_UNIDADE`, o sistema SHALL não exibir o item "Minha unidade".
3. WHEN o gestor está em qualquer página sob `/minha-unidade/` THEN o item "Minha unidade" SHALL ter `aria-current` ("page" na lista, "true" nas demais).
4. IF um usuário sem perfil `GESTOR_DE_UNIDADE` (USUARIO, ADMINISTRADOR ou superusuário) abre qualquer rota sob `/minha-unidade/` THEN o sistema SHALL responder 403 com a página própria "Acesso restrito a gestores de unidade.".
5. WHEN o gestor abre `/minha-unidade/` THEN o sistema SHALL exibir o h1 "Minha unidade", o nome da sua unidade e uma tabela com `caption` "Contas da unidade {nome}" e as colunas Nome, Usuário, E-mail, Perfil, Situação e Último acesso.
6. The tabela SHALL listar todas as contas cuja unidade é a do gestor, inclusive a dele e as desativadas, ordenadas por nome completo e depois por usuário.
7. The tabela SHALL não listar contas de outra unidade nem contas sem unidade.
8. The coluna Situação SHALL mostrar "Ativa" ou "Desativada" por escrito, nunca só por cor.
9. WHILE uma conta da tabela tem perfil USUARIO, o sistema SHALL exibir na linha as ações "Redefinir senha" e "Desativar" (conta ativa) ou "Reativar" (conta desativada).
10. WHILE uma conta da tabela não tem perfil USUARIO (o próprio gestor, outro gestor, um ADMINISTRADOR), o sistema SHALL não exibir ação na linha.
11. WHEN o gestor abre `/minha-unidade/` THEN o sistema SHALL exibir a ação principal "Criar conta" com `href="/minha-unidade/contas/nova/"`.

**Independent Test**: como gestora da Filial Norte, ver só as contas da Filial Norte, com ações
apenas nas contas USUARIO; como `joao` (ADMINISTRADOR), receber 403.

---

### P1: Criar conta na unidade ⭐ MVP

**User Story**: Como gestor de unidade, quero criar a conta de quem chega à minha unidade, sem
pedir ao ADMINISTRADOR.

**Acceptance Criteria**:

1. WHEN o gestor abre `/minha-unidade/contas/nova/` THEN o sistema SHALL exibir o formulário com os campos Usuário, Nome, Sobrenome, E-mail, Senha provisória e Confirmação da senha provisória, todos obrigatórios, e sem campo de perfil ou de unidade.
2. WHEN o gestor envia o formulário válido THEN o sistema SHALL criar a conta com perfil USUARIO, unidade igual à do gestor, ativa e com senha provisória marcada.
3. WHEN a conta é criada THEN o sistema SHALL redirecionar para `/minha-unidade/` com o alerta de sucesso "Conta “{usuário}” criada. Informe a senha provisória à pessoa: ela vai trocá-la no primeiro acesso.".
4. IF o POST traz campos de perfil, unidade, `is_staff` ou `is_superuser` THEN o sistema SHALL ignorá-los e criar a conta como USUARIO da unidade do gestor, sem `is_staff` nem `is_superuser`.
5. IF o e-mail já existe em outra conta, sem diferenciar maiúsculas THEN o sistema SHALL exibir no campo E-mail o erro "Já existe uma conta com este e-mail." e não criar a conta.
6. IF o usuário já existe THEN o sistema SHALL exibir no campo Usuário o erro "Já existe uma conta com este usuário." e não criar a conta.
7. IF a senha provisória é recusada por um dos `AUTH_PASSWORD_VALIDATORS` THEN o sistema SHALL exibir no campo Senha provisória a mensagem do validador e não criar a conta.
8. IF a confirmação difere da senha provisória THEN o sistema SHALL exibir no campo de confirmação o erro "As duas senhas não são iguais." e não criar a conta.
9. IF o envio falha THEN o sistema SHALL devolver preenchidos Usuário, Nome, Sobrenome e E-mail, e vazios os dois campos de senha (RF13).
10. WHEN o gestor clica em "Cancelar" THEN o sistema SHALL voltar para `/minha-unidade/` sem criar conta (RF14).

**Independent Test**: criar a conta `pedro` como gestora da Filial Norte e conferir no admin
perfil USUARIO, unidade Filial Norte e senha provisória marcada.

---

### P1: Desativar e reativar conta ⭐ MVP

**User Story**: Como gestor de unidade, quero desativar a conta de quem saiu e reativar a de quem
voltou, sem apagar o que a pessoa cadastrou.

**Acceptance Criteria**:

1. WHEN o gestor aciona "Desativar" numa conta USUARIO da sua unidade THEN o sistema SHALL gravar a conta como inativa e voltar para `/minha-unidade/` com o alerta "Conta “{usuário}” desativada.".
2. WHEN o gestor aciona "Reativar" numa conta USUARIO desativada da sua unidade THEN o sistema SHALL gravar a conta como ativa e voltar com o alerta "Conta “{usuário}” reativada.".
3. The ação SHALL levar o estado desejado no POST (desativar ou reativar), de modo que repetir o envio deixe a conta no mesmo estado e mostre o mesmo alerta.
4. The ação SHALL aceitar só POST; IF chega um GET THEN o sistema SHALL responder 405.
5. WHILE a conta está desativada, o sistema SHALL recusar o login dela com a mensagem atual de credencial inválida.
6. WHEN uma conta com sessão aberta é desativada THEN a próxima requisição dessa sessão SHALL ser tratada como anônima (redirecionada ao login).
7. The desativação SHALL manter as inovações, mudanças de status e reaproveitamentos da conta, com a autoria intacta.

**Independent Test**: desativar `pedro` com ele logado em outro navegador; a próxima página dele
vai para o login; reativar e ele entra de novo.

---

### P1: Redefinir senha e troca obrigatória ⭐ MVP

**User Story**: Como gestor de unidade, quero redefinir a senha de quem esqueceu; como pessoa da
unidade, quero trocar a senha provisória no primeiro acesso, para que só eu a conheça.

**Acceptance Criteria**:

1. WHEN o gestor envia uma nova senha provisória válida (com confirmação igual) para uma conta USUARIO da sua unidade THEN o sistema SHALL trocar a senha, marcar a senha como provisória e voltar para `/minha-unidade/` com o alerta "Senha de “{usuário}” redefinida. Informe a senha provisória à pessoa.".
2. IF a nova senha provisória é recusada por um validador ou a confirmação difere THEN o sistema SHALL exibir o erro no campo, como na criação, e não trocar a senha.
3. WHEN a senha de uma conta com sessão aberta é redefinida THEN a próxima requisição dessa sessão SHALL ser tratada como anônima.
4. WHILE a conta autenticada tem senha provisória, o sistema SHALL redirecionar (302) toda requisição autenticada para `/conta/senha/`, exceto `/conta/senha/`, `/sair/` e as rotas públicas (AD-006).
5. WHEN a pessoa abre `/conta/senha/` THEN o sistema SHALL exibir o h1 "Trocar senha" e os campos Senha atual, Nova senha e Confirmação da nova senha.
6. WHILE a conta tem senha provisória, a tela `/conta/senha/` SHALL exibir o aviso "Sua senha é provisória. Defina uma nova senha para continuar.".
7. WHEN a pessoa envia a senha atual correta e uma nova senha válida com confirmação igual THEN o sistema SHALL trocar a senha, desmarcar a senha provisória, manter a sessão aberta e redirecionar para `/inovacoes/` com o alerta "Senha alterada.".
8. IF a senha atual está errada THEN o sistema SHALL exibir no campo Senha atual o erro "Senha atual incorreta." e não trocar a senha.
9. IF a nova senha é igual à atual THEN o sistema SHALL exibir no campo Nova senha o erro "A nova senha precisa ser diferente da atual." e não trocar a senha.
10. IF a nova senha é recusada por um validador ou a confirmação difere THEN o sistema SHALL exibir o erro no campo e não trocar a senha.
11. WHILE a conta autenticada não tem senha provisória, o sistema SHALL permitir abrir `/conta/senha/` e trocar a senha pelo mesmo formulário, sem redirecionamento forçado.

**Independent Test**: redefinir a senha do `pedro`; ao entrar, ele cai em "Trocar senha" e não
abre a lista pela URL; troca a senha e chega à lista.

---

### P1: Curadoria pela unidade de origem ⭐ MVP

**User Story**: Como gestor de unidade, quero editar, excluir e avançar o status das inovações da
minha unidade, para cuidar da qualidade do que ela publica.

**Acceptance Criteria**:

1. The `Inovacao.pode_ser_alterada_por(usuario)` SHALL responder verdadeiro para o autor, para o ADMINISTRADOR e para o gestor cuja unidade é a unidade de origem da inovação, e falso para os demais.
2. WHEN o gestor da unidade de origem abre o detalhe de uma inovação de outro autor THEN o sistema SHALL exibir "Editar", "Excluir" e, em Em teste e Validada, a ação de avançar o status.
3. WHEN o gestor da unidade de origem envia a edição, a exclusão confirmada ou o avanço de status THEN o sistema SHALL concluir a ação como faz para o autor.
4. IF um gestor de outra unidade abre editar, excluir ou status de uma inovação THEN o sistema SHALL responder 403 com a página própria da AD-009.
5. The página própria de recusa e o detalhe SHALL usar os textos novos da T-1 e da T-2.
6. WHEN o ADMINISTRADOR muda a unidade de um gestor THEN a curadoria SHALL seguir a unidade atual a partir da próxima requisição.
7. WHEN o ADMINISTRADOR tira o perfil de gestor de uma conta THEN a conta SHALL perder a curadoria e o acesso a "Minha unidade" a partir da próxima requisição.

**Independent Test**: como gestora da Filial Norte, editar uma inovação da Filial Norte cadastrada
por outra pessoa; tentar editar uma da Sede e receber 403.

---

### P2: Unidade pré-preenchida

**User Story**: Como pessoa vinculada a uma unidade, quero que o cadastro e o reaproveitamento já
venham com a minha unidade, para preencher menos.

**Acceptance Criteria**:

1. WHEN um usuário com unidade abre `/inovacoes/nova/` THEN o select "Unidade de origem" SHALL vir com a unidade dele selecionada e continuar editável.
2. WHEN um usuário sem unidade abre `/inovacoes/nova/` THEN o select SHALL vir em "Selecione…", como hoje (INOV-15).
3. WHEN um usuário com unidade envia o cadastro com outra unidade de origem THEN o sistema SHALL gravar a unidade escolhida no formulário.
4. The formulário de edição SHALL continuar mostrando a unidade gravada na inovação, não a do usuário.
5. WHEN um usuário com unidade abre o reaproveitamento e a unidade dele está entre as elegíveis THEN o select SHALL vir com ela selecionada.
6. IF a unidade do usuário não é elegível (é a de origem ou já reaproveitou) THEN o select de reaproveitamento SHALL vir sem seleção, como hoje.

**Independent Test**: como `pedro` (Filial Norte), abrir o cadastro e ver "Filial Norte" já
escolhida; abrir o reaproveitamento de uma inovação da Sede e ver "Filial Norte" escolhida.

---

### P1: Formulários das telas novas ⭐ MVP

**User Story**: Como gestor ou pessoa da unidade, quero que os formulários de conta e de senha
digam o que corrigir e como sair sem gravar, como pede a §6 v2 da `design-spec.md`.

**Acceptance Criteria** (emendas E-2 e E-3, 2026-11-23):

1. IF o envio de criar conta, redefinir senha ou trocar senha falha THEN o sistema SHALL exibir no topo o resumo de erros da §6 v2, com o título "Não foi possível {criar a conta | redefinir a senha | trocar a senha}. Corrija {n} campo(s):" e um link por campo com erro, e o `<title>` SHALL começar por "Erro:".
2. The formulários de criar conta, redefinir senha e trocar senha SHALL terminar na barra de ações da §6 v2: o botão de envio, o link "Cancelar" e a nota "Nada é gravado se você cancelar."; WHILE a conta tem senha provisória, a tela de trocar senha SHALL não exibir "Cancelar" nem a nota.

**Independent Test**: enviar "Criar conta" vazio e ver o resumo com os seis campos e o título
"Erro: …"; entrar com senha provisória e ver "Trocar senha" sem "Cancelar".

---

## Edge Cases

- IF o gestor manda POST de desativar, reativar ou redefinir para uma conta de outra unidade, sem unidade, para si mesmo, para outro gestor ou para um ADMINISTRADOR THEN o sistema SHALL responder 404 e não alterar a conta.
- IF o gestor manda POST para um id de conta que não existe THEN o sistema SHALL responder 404.
- IF dois gestores da mesma unidade desativam a mesma conta ao mesmo tempo THEN a conta SHALL terminar desativada e os dois SHALL ver o alerta de desativação.
- IF a unidade do gestor é renomeada pelo ADMINISTRADOR THEN a área "Minha unidade" SHALL mostrar o nome novo na próxima requisição.
- WHEN a unidade do gestor não tem outra conta além da dele THEN a tabela SHALL listar só a conta dele, sem ação, e a ação "Criar conta" SHALL continuar disponível.
- IF uma conta com senha provisória tenta abrir `/minha-unidade/` ou o admin THEN o sistema SHALL redirecionar para `/conta/senha/` antes de qualquer outra checagem de papel.
- IF um POST com token CSRF inválido chega a qualquer ação nova THEN o sistema SHALL responder 403 sem alterar nada.

---

## Implicit-requirement dimensions

| Dimension | Resolution |
| --------- | ---------- |
| Input validation & bounds | Criação: GEST-20 a GEST-27; senhas: GEST-38, GEST-44 a GEST-46; tamanhos de campo herdados do `AbstractUser` |
| Failure / partial-failure states | Formulário inválido não grava nada e devolve os dados (GEST-28); criação é uma gravação só |
| Idempotency / retry / duplicate handling | Desativar/reativar com estado explícito (GEST-32); duplicidade de e-mail e usuário (GEST-24, GEST-25) |
| Auth boundaries & rate limits | 403 para não gestor (GEST-12), 404 fora do escopo (GEST-61), admin fechado ao gestor (GEST-07), troca obrigatória antes de tudo (GEST-40, GEST-66). Rate limit: N/A because o login não tem limite hoje e nenhuma tela nova autentica |
| Concurrency / ordering | Desativação simultânea (GEST-63); papel e unidade lidos a cada requisição (GEST-53, GEST-54) |
| Data lifecycle / expiry | Desativar em vez de excluir, autoria preservada (GEST-36); unidade com contas não se exclui (GEST-08) |
| Observability | N/A because o MVP não tem logs de auditoria; trilha de quem fez o quê fica em Deferred Ideas do `context.md` |
| External-dependency failure | N/A because nada novo fala com serviço externo (sem e-mail, sem SSO) |
| State-transition integrity | Senha provisória → definitiva só pela troca (GEST-40 a GEST-47); ativa ↔ desativada só pelo gestor (GEST-30 a GEST-32) ou pelo admin |

---

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
| -------------- | ----- | ----- | ------ |
| GEST-01 | P1 Unidade e papel (AC 1) | Design | Pending |
| GEST-02 | P1 Unidade e papel (AC 2) | Design | Pending |
| GEST-03 | P1 Unidade e papel (AC 3) | Design | Pending |
| GEST-04 | P1 Unidade e papel (AC 4) | Design | Pending |
| GEST-05 | P1 Unidade e papel (AC 5) | Design | Pending |
| GEST-06 | P1 Unidade e papel (AC 6) | Design | Pending |
| GEST-07 | P1 Unidade e papel (AC 7) | Design | Pending |
| GEST-08 | P1 Unidade e papel (AC 8) | Design | Pending |
| GEST-09 | P1 Minha unidade (AC 1) | Design | Pending |
| GEST-10 | P1 Minha unidade (AC 2) | Design | Pending |
| GEST-11 | P1 Minha unidade (AC 3) | Design | Pending |
| GEST-12 | P1 Minha unidade (AC 4) | Design | Pending |
| GEST-13 | P1 Minha unidade (AC 5) | Design | Pending |
| GEST-14 | P1 Minha unidade (AC 6) | Design | Pending |
| GEST-15 | P1 Minha unidade (AC 7) | Design | Pending |
| GEST-16 | P1 Minha unidade (AC 8) | Design | Pending |
| GEST-17 | P1 Minha unidade (AC 9) | Design | Pending |
| GEST-18 | P1 Minha unidade (AC 10) | Design | Pending |
| GEST-19 | P1 Minha unidade (AC 11) | Design | Pending |
| GEST-20 | P1 Criar conta (AC 1) | Design | Pending |
| GEST-21 | P1 Criar conta (AC 2) | Design | Pending |
| GEST-22 | P1 Criar conta (AC 3) | Design | Pending |
| GEST-23 | P1 Criar conta (AC 4) | Design | Pending |
| GEST-24 | P1 Criar conta (AC 5) | Design | Pending |
| GEST-25 | P1 Criar conta (AC 6) | Design | Pending |
| GEST-26 | P1 Criar conta (AC 7) | Design | Pending |
| GEST-27 | P1 Criar conta (AC 8) | Design | Pending |
| GEST-28 | P1 Criar conta (AC 9) | Design | Pending |
| GEST-29 | P1 Criar conta (AC 10) | Design | Pending |
| GEST-30 | P1 Desativar (AC 1) | Design | Pending |
| GEST-31 | P1 Desativar (AC 2) | Design | Pending |
| GEST-32 | P1 Desativar (AC 3) | Design | Pending |
| GEST-33 | P1 Desativar (AC 4) | Design | Pending |
| GEST-34 | P1 Desativar (AC 5) | Design | Pending |
| GEST-35 | P1 Desativar (AC 6) | Design | Pending |
| GEST-36 | P1 Desativar (AC 7) | Design | Pending |
| GEST-37 | P1 Senha (AC 1) | Design | Pending |
| GEST-38 | P1 Senha (AC 2) | Design | Pending |
| GEST-39 | P1 Senha (AC 3) | Design | Pending |
| GEST-40 | P1 Senha (AC 4) | Design | Pending |
| GEST-41 | P1 Senha (AC 5) | Design | Pending |
| GEST-42 | P1 Senha (AC 6) | Design | Pending |
| GEST-43 | P1 Senha (AC 7) | Design | Pending |
| GEST-44 | P1 Senha (AC 8) | Design | Pending |
| GEST-45 | P1 Senha (AC 9) | Design | Pending |
| GEST-46 | P1 Senha (AC 10) | Design | Pending |
| GEST-47 | P1 Senha (AC 11) | Design | Pending |
| GEST-48 | P1 Curadoria (AC 1) | Design | Pending |
| GEST-49 | P1 Curadoria (AC 2) | Design | Pending |
| GEST-50 | P1 Curadoria (AC 3) | Design | Pending |
| GEST-51 | P1 Curadoria (AC 4) | Design | Pending |
| GEST-52 | P1 Curadoria (AC 5) | Design | Pending |
| GEST-53 | P1 Curadoria (AC 6) | Design | Pending |
| GEST-54 | P1 Curadoria (AC 7) | Design | Pending |
| GEST-55 | P2 Pré-preenchida (AC 1) | Design | Pending |
| GEST-56 | P2 Pré-preenchida (AC 2) | Design | Pending |
| GEST-57 | P2 Pré-preenchida (AC 3) | Design | Pending |
| GEST-58 | P2 Pré-preenchida (AC 4) | Design | Pending |
| GEST-59 | P2 Pré-preenchida (AC 5) | Design | Pending |
| GEST-60 | P2 Pré-preenchida (AC 6) | Design | Pending |
| GEST-61 | Edge: alvo fora do escopo → 404 | Design | Pending |
| GEST-62 | Edge: id inexistente → 404 | Design | Pending |
| GEST-63 | Edge: desativação simultânea | Design | Pending |
| GEST-64 | Edge: unidade renomeada | Design | Pending |
| GEST-65 | Edge: unidade só com o gestor | Design | Pending |
| GEST-66 | Edge: senha provisória antes do papel | Design | Pending |
| GEST-67 | Edge: CSRF inválido | Design | Pending |
| GEST-68 | P1 Formulários (AC 1) | Design | Pending |
| GEST-69 | P1 Formulários (AC 2) | Design | Pending |

**Coverage:** 69 total, 0 mapped to tasks (Tasks ainda não rodou), 69 pendentes.

---

## Success Criteria

- [ ] Um gestor cria uma conta e a pessoa entra, troca a senha e chega à lista, sem nenhum passo do ADMINISTRADOR.
- [ ] Nenhuma tela nova ou ação nova alcança conta ou inovação fora da unidade do gestor (varredura de rotas por papel, L-003).
- [ ] Suíte e build gate verdes, com só T-1 a T-6 alterados.
