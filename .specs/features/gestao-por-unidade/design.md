# Gestão por Unidade Design

**Spec**: `.specs/features/gestao-por-unidade/spec.md`
**Status**: Approved (2026-11-23)

---

## Architecture Overview

Três peças novas, todas dentro do desenho que já existe (MVT sem camada de serviço, AD-002):

1. **Dados em `contas.Usuario`**: perfil com terceiro valor, unidade opcional e o marcador de
   senha provisória. As regras de quem administra quem moram no modelo, como a
   `pode_ser_alterada_por` da AD-009.
2. **Área do gestor em `contas`**: um módulo de URLs próprio (`contas/urls_gestao.py`, namespace
   `gestao`, montado em `/minha-unidade/`), views com o `GestaoDeUnidadeMixin` (porteiro do
   papel) e as telas com os componentes da §6 v2.
3. **Senha provisória**: o `contas.middleware.SenhaProvisoriaMiddleware`, logo depois do
   `LoginRequiredMiddleware`, e a tela `/conta/senha/` no namespace `contas`.

A curadoria entra pelo método que já existe (`Inovacao.pode_ser_alterada_por`); editar, excluir,
avançar status e o detalhe da R2 (`pode_alterar`) herdam sem mudar as views.

```mermaid
graph TD
    R[Requisição] --> A[AuthenticationMiddleware]
    A --> L[LoginRequiredMiddleware · AD-006]
    L -->|anônimo em rota interna| LOGIN[/entrar/?next=]
    L --> S[SenhaProvisoriaMiddleware · AD-017]
    S -->|senha_provisoria e rota não liberada| TROCA[/conta/senha/]
    S --> V{View}
    V --> G[GestaoDeUnidadeMixin]
    G -->|não é gestor| G403[403 contas/gestao/acesso_restrito.html]
    G --> GV[Minha unidade · criar · situação · redefinir]
    GV -->|conta fora de administraveis_por| G404[404 contas/gestao/conta_nao_encontrada.html]
    V --> M[AlteracaoDeInovacaoMixin · AD-009]
    M --> P[Inovacao.pode_ser_alterada_por]
    P -->|autor · ADMINISTRADOR · gestor da unidade de origem| OK[edita · exclui · avança]
```

### Abordagens consideradas

| Eixo | Recomendada | Alternativas | Por que a recomendada |
| ---- | ----------- | ------------ | --------------------- |
| Onde ficam as telas do gestor | App `contas`, com `urls_gestao.py` (namespace `gestao`) | (b) app nova `gestao`; (c) admin do Django com filtro por unidade | (b) separa o que é do mesmo modelo e dos mesmos formulários de senha; (c) quebra a AD-007, recusada no Discuss |
| Troca obrigatória de senha | Middleware depois do `LoginRequiredMiddleware` | (b) mixin em cada view; (c) só redirecionar no login | (b) repete o erro que a AD-006 evitou: view nova esquece o mixin e abre; (c) não cumpre a GEST-40 (a pessoa digita a URL) |
| Situação da conta | Derivada (`Usuario.situacao`) de `is_active` e de marcadores; enum `SituacaoConta` | (b) coluna `situacao` sincronizada com `is_active` por CHECK | (b) obriga trocar o `is_active` do admin pelo campo novo, e `contas/tests/test_admin_perfil.py:107,145` posta `is_active`: mudança fora do inventário |

---

## Code Reuse Analysis

### Existing Components to Leverage

| Component | Location | How to Use |
| --------- | -------- | ---------- |
| `PerfilUsuario`, CHECK `usuario_perfil_valido` | `contas/models.py:7-18`, `:59-62` | Ganha `GESTOR_DE_UNIDADE`; a CHECK lê `PerfilUsuario.values` e acompanha sozinha (a migration recria a constraint) |
| `Usuario.save()` (is_staff só para ADMINISTRADOR) | `contas/models.py:72-83` | Sem mudança: o gestor nasce sem `is_staff` |
| `AcessoSomenteAdministradorMixin`, `UsuarioAdmin` | `contas/admin.py:8-61` | Ganha unidade e senha provisória na seção "Perfil", coluna e filtro "Unidade" |
| `UsuarioAlteracaoForm` | `contas/forms.py:38-42` | Ganha o `clean()` da GEST-05 |
| `UsernameOrEmailBackend` (herda `user_can_authenticate` e `get_user`) | `contas/backends.py` | Conta desativada não entra e a sessão aberta vira anônima (GEST-34, GEST-35) sem código |
| Verificação do hash da senha na sessão (`django.contrib.auth`) | Django 5.2 | Redefinir derruba a sessão da pessoa (GEST-39); `update_session_auth_hash` mantém a de quem troca a própria (GEST-43) |
| `BaseUserCreationForm`, `SetPasswordForm`, `PasswordChangeForm` | `django.contrib.auth.forms` (5.2.17) | Base dos três formulários; validadores do `AUTH_PASSWORD_VALIDATORS` já embutidos |
| `Inovacao.pode_ser_alterada_por` | `inovacoes/models.py:259-268` | Ganha o ramo do gestor; nenhuma view muda |
| `AlteracaoDeInovacaoMixin` | `inovacoes/views.py:40-65` | Modelo do `GestaoDeUnidadeMixin` (porteiro no `dispatch`, página própria) |
| `InovacaoCreateView.get_initial` | `inovacoes/views.py:105-109` | Ganha `unidade` (GEST-55) |
| `ReaproveitamentoForm` | `inovacoes/forms.py:170-197` | Ganha `unidade_sugerida` opcional (GEST-59, GEST-60) |
| `casca` e `PAGINA_ATUAL` | `nucleo/context_processors.py:5-29` | Entrada `("gestao", "painel")` e o ramo de seção do namespace `gestao` |
| Menu e área do usuário | `templates/base.html:43-67` | Quarto item, só com `user.is_gestor_de_unidade` |
| Trilha | `templates/paginas/trilha.html` | Ganha o parâmetro `unidade` (raiz "Minha unidade"); sem ele, tudo igual |
| `.tabela`, `.resumo-erros`, `.barra-acoes`, `.grupo`, `.alerta`, `[role=alert]`, `.cabecalho-pagina` | `templates/kira.css:299-307`, `:490-522`, `:554`, `:1008-1097` | As telas novas são as primeiras a usar o resumo de erros, a barra de ações e o grupo; nenhuma regra nova de cor |
| `inovacoes/acesso_negado.html` | `inovacoes/templates/inovacoes/acesso_negado.html` | Modelo da 403 do gestor; recebe o texto novo (T-1) |

### Integration Points

| System | Integration Method |
| ------ | ------------------ |
| Banco | Migration `contas 0005` (dependência em `inovacoes 0001`): `AlterField perfil` (17 caracteres, choices), `AddField unidade` (FK nula, PROTECT), `AddField senha_provisoria` (default False), CHECK `usuario_perfil_valido` recriada, CHECK `usuario_gestor_tem_unidade` nova. Todas as contas atuais ficam `unidade=NULL`, `senha_provisoria=False` e continuam válidas nas duas CHECKs |
| URLs | `config/urls.py`: `path("minha-unidade/", include("contas.urls_gestao"))`; `contas/urls.py`: `path("conta/senha/", …, name="trocar_senha")` |
| Middleware | `config/settings.py:68`: `contas.middleware.SenhaProvisoriaMiddleware` logo depois do `LoginRequiredMiddleware` |
| Varredura AD-006 (`contas/tests/test_controle_acesso.py:69`) | Cobre as rotas novas sem mudança: todas redirecionam o anônimo |
| Varredura AD-009 (`inovacoes/tests/test_controle_autoria.py:46`) | Só o namespace `inovacoes`; as rotas do gestor ficam fora |

---

## Components

### Modelo `Usuario` (dados e regras)

- **Purpose**: Guardar perfil, unidade e senha provisória e responder quem administra quem.
- **Location**: `contas/models.py`
- **Interfaces**:
  - `PerfilUsuario.GESTOR_DE_UNIDADE = "GESTOR_DE_UNIDADE", "Gestor de unidade"`
  - `SituacaoConta(TextChoices)`: `ATIVA` "Ativa", `DESATIVADA` "Desativada" (AD-016)
  - `Usuario.unidade: ForeignKey("inovacoes.Unidade", null=True, blank=True, on_delete=PROTECT, related_name="usuarios", verbose_name="unidade")`
  - `Usuario.senha_provisoria: BooleanField("senha provisória", default=False)`
  - `Usuario.is_gestor_de_unidade -> bool` (propriedade, como `is_administrador`)
  - `Usuario.situacao -> SituacaoConta` (propriedade: `ATIVA if is_active else DESATIVADA`)
  - `UsuarioQuerySet.da_unidade(unidade)`: contas da unidade, ordem `first_name`, `last_name`, `username` (GEST-14, GEST-15)
  - `UsuarioQuerySet.administraveis_por(gestor)`: `perfil=USUARIO`, `unidade_id=gestor.unidade_id`; vazio se `gestor` não é gestor (GEST-61)
  - `Usuario.pode_ser_administrada_por(gestor) -> bool`: a mesma regra, sem consulta (para a tabela, GEST-17, GEST-18)
  - `Usuario.mudar_situacao(para)`: grava `is_active` com `save(update_fields=["is_active"])` (GEST-30 a GEST-32)
- **Constraints**: `usuario_perfil_valido` (três valores); `usuario_gestor_tem_unidade`:
  `~Q(perfil="GESTOR_DE_UNIDADE") | Q(unidade__isnull=False)`, com
  `violation_error_message="Gestor de unidade precisa de uma unidade."`.
- **Manager**: `UsuarioManager` passa a sair de `UserManager.from_queryset(UsuarioQuerySet)`;
  `create_superuser` continua igual.
- **Reuses**: `is_administrador`, a CHECK da AD-004.

### `Inovacao.pode_ser_alterada_por` (extensão da AD-009)

- **Location**: `inovacoes/models.py:259`
- **Interface**: `usuario.is_authenticated and (usuario.is_administrador or self.autor_id == usuario.pk or (usuario.is_gestor_de_unidade and usuario.unidade_id == self.unidade_id))`. Lê só ids: nenhuma consulta nova no detalhe (os testes de número de consultas da R2 seguem iguais).
- Lê o perfil e a unidade do `request.user` carregado a cada requisição: mudar unidade ou perfil no admin vale na próxima (GEST-53, GEST-54).

### Admin de usuários

- **Location**: `contas/admin.py`, `contas/forms.py`
- **Mudanças**: seção "Perfil" com `("perfil", "unidade", "senha_provisoria")` (GEST-04); `list_display` ganha `"unidade"` e `list_filter` ganha `"unidade"` (GEST-06); `list_select_related = ("unidade",)`.
- **GEST-05**: `UsuarioAlteracaoForm.clean()` chama `add_error("unidade", "Gestor de unidade precisa de uma unidade.")` quando o perfil é gestor e a unidade está vazia. Com o campo em erro, o `_post_clean` do ModelForm exclui `unidade` da validação do modelo, e a CHECK não repete a mensagem como erro geral. **Conferir no Execute** com teste (o comportamento é do Django 5.2: `CheckConstraint.validate` ignora a constraint quando um campo dela está excluído).
- **GEST-08**: o PROTECT já faz a tela de exclusão do admin listar os usuários e recusar. Sem código.

### `GestaoDeUnidadeMixin`

- **Purpose**: Porteiro de toda view sob `/minha-unidade/`.
- **Location**: `contas/views_gestao.py`
- **Interfaces**:
  - `dispatch()`: se `not request.user.is_gestor_de_unidade`, renderiza `contas/gestao/acesso_restrito.html` com 403 (GEST-12; vale para USUARIO, USUARIO staff, ADMINISTRADOR e superusuário: o perfil é o único critério).
  - `conta_alvo(pk)`: `Usuario.objects.administraveis_por(request.user).get(pk=pk)`; `DoesNotExist` vira `contas/gestao/conta_nao_encontrada.html` com 404 (GEST-61, GEST-62). A conta de outra unidade, sem unidade, o próprio gestor, outro gestor e o ADMINISTRADOR caem todos aqui, com a mesma resposta.
- **Reuses**: o desenho do `AlteracaoDeInovacaoMixin`.

### Views da área do gestor

| View | Rota (`gestao:`) | Métodos | Specs |
| ---- | ---------------- | ------- | ----- |
| `MinhaUnidadeView` (ListView) | `/minha-unidade/` (`painel`) | GET | GEST-13 a GEST-19, GEST-64, GEST-65 |
| `CriarContaView` (CreateView) | `/minha-unidade/contas/nova/` (`criar_conta`) | GET, POST | GEST-20 a GEST-29 |
| `SituacaoDaContaView` (View) | `/minha-unidade/contas/<int:pk>/situacao/` (`situacao`) | POST (GET → 405, `http_method_names = ["post"]`) | GEST-30 a GEST-33, GEST-63 |
| `RedefinirSenhaView` (FormView) | `/minha-unidade/contas/<int:pk>/senha/` (`redefinir_senha`) | GET, POST | GEST-37, GEST-38 |

- **Criar conta**: o formulário só tem `username`, `first_name`, `last_name`, `email`, `password1`, `password2`. A view fixa na instância `perfil=USUARIO`, `unidade=request.user.unidade`, `senha_provisoria=True`, `is_active=True`, `is_staff=False`, `is_superuser=False` antes de gravar: campo extra no POST não chega ao modelo (GEST-23).
- **Situação**: o POST leva `situacao=ATIVA` ou `situacao=DESATIVADA`. A view aceita o valor se está em `TRANSICOES[conta.situacao] | {conta.situacao}` (repetir dá o mesmo estado e o mesmo alerta, GEST-32); valor fora disso → 400 sem gravar. O alerta sai da tabela `ALERTA_DA_SITUACAO = {ATIVA: "Conta “{u}” reativada.", DESATIVADA: "Conta “{u}” desativada."}`, pelo estado de destino.
  `TRANSICOES = {ATIVA: {DESATIVADA}, DESATIVADA: {ATIVA}}` mora em `contas/models.py`, junto do enum (AD-016).
- **Redefinir senha**: `SetPasswordForm` da conta-alvo; o `save()` também liga `senha_provisoria`.

### Formulários novos

- **Location**: `contas/forms.py`
- `ContaDaUnidadeForm(BaseUserCreationForm)`: `Meta.fields = ("username", "first_name", "last_name", "email")`, todos obrigatórios; rótulos "Usuário", "Nome", "Sobrenome", "E-mail", "Senha provisória", "Confirmação da senha provisória"; `clean_username` e `clean_email` sem diferenciar caixa, com "Já existe uma conta com este usuário." e "Já existe uma conta com este e-mail." no campo (GEST-24, GEST-25); `password_mismatch` = "As duas senhas não são iguais." (GEST-27). Com o campo em erro, a `UniqueConstraint` de e-mail não repete a mensagem (mesmo mecanismo da GEST-05; conferir no Execute).
- `SenhaProvisoriaForm(SetPasswordForm)`: rótulos "Nova senha provisória" e "Confirmação da nova senha provisória", mesma mensagem de divergência; `save()` grava `password` e `senha_provisoria=True`.
- `TrocarSenhaForm(PasswordChangeForm)`: rótulos "Senha atual", "Nova senha", "Confirmação da nova senha"; `password_incorrect` = "Senha atual incorreta." (GEST-44); `clean_new_password1` recusa a senha igual à atual com "A nova senha precisa ser diferente da atual." (GEST-45); `save()` grava `senha_provisoria=False`.
- RF13 (GEST-28): os campos de senha do Django já voltam vazios (`render_value=False`); os demais voltam preenchidos.
- Os três usam o `FormularioV2Mixin` (abaixo).

### Peças da §6 v2 para formulário (novas, reaproveitáveis pelo redesign dos formulários de inovação)

| Peça | Location | O que faz |
| ---- | -------- | --------- |
| `FormularioV2Mixin` | `nucleo/formularios.py` | Põe `template_name = "paginas/campo.html"` em cada campo e `label_suffix=""` |
| Campo v2 | `templates/paginas/campo.html` | Ordem rótulo → ajuda → campo → erro (§6); "(obrigatório)" por escrito no rótulo; `aria-describedby` com o erro antes da ajuda |
| Resumo de erros | `templates/paginas/resumo_erros.html` | `div.resumo-erros` com `role="alert"` e `tabindex="-1"`, título "Não foi possível {ação}. Corrija {n} campo(s):" e um link por campo, na ordem do formulário; não existe no DOM sem erro |
| Tabela de contas | `contas/templates/contas/gestao/parciais/tabela_contas.html` | `table.tabela` com `caption`, `th scope="col"`, uma linha por conta, ações por linha; recebe `contas` e `legenda` |

O `inovacoes/campo.html` (ordem rótulo → campo → erro → ajuda, INOV-41) continua servindo aos
formulários de inovação, que não mudam nesta feature.

### Telas

Todas estendem o base, sem `<style>` nem `style=` (DS-01); trilha por `paginas/trilha.html` com
`unidade=True`, salvo as páginas de recusa, que ficam sem trilha como toda 403 e 404 (RED-30; decisão do usuário em 2026-11-23); o h1 pelo bloco `titulo`; a ação principal pelo bloco `acao_principal`.

| Tela | Template | Trilha | h1 / descrição | Conteúdo |
| ---- | -------- | ------ | -------------- | -------- |
| Minha unidade | `contas/gestao/minha_unidade.html` | Minha unidade | "Minha unidade" / "{nome da unidade}" | Ação principal "Criar conta" (botão primário, link). Seção "Contas da unidade" com a tabela (caption "Contas da unidade {nome}"; colunas Nome, Usuário, E-mail, Perfil, Situação, Último acesso; "Nunca" quando não há acesso). Ações: link "Redefinir senha" e um `form` POST por linha com o botão "Desativar" ou "Reativar", os dois secundários (decisão do usuário em 2026-11-23: desativar pode ser desfeito, e o perigo da §6 é só para ação destrutiva) |
| Criar conta | `contas/gestao/conta_form.html` | Minha unidade › Criar conta | "Criar conta" / "A conta nasce como Usuário da unidade {nome}." | Resumo de erros; cartão com `fieldset.grupo` "Identificação" (Usuário, Nome, Sobrenome, E-mail) e "Senha provisória" (as duas senhas); barra de ações "Criar conta", "Cancelar" → `/minha-unidade/`, nota |
| Redefinir senha | `contas/gestao/redefinir_senha.html` | Minha unidade › Redefinir senha | "Redefinir senha" / "Conta “{usuário}” ({nome}). A pessoa troca a senha no próximo acesso." | Resumo de erros; cartão com os dois campos; barra de ações "Redefinir senha", "Cancelar", nota |
| Trocar senha | `contas/trocar_senha.html` | Trocar senha | "Trocar senha" | Com senha provisória, alerta de aviso "Sua senha é provisória. Defina uma nova senha para continuar." (GEST-42) e barra de ações sem "Cancelar" (o cancelamento cairia de novo aqui); sem senha provisória, "Cancelar" → `/inovacoes/` |
| Acesso restrito | `contas/gestao/acesso_restrito.html` | sem trilha (RED-30) | "Acesso restrito" | `cartao estado-erro` com "Acesso restrito a gestores de unidade." e o link "Voltar para as inovações" |
| Conta não encontrada | `contas/gestao/conta_nao_encontrada.html` | sem trilha (RED-30) | "Conta não encontrada" | "Esta conta não existe ou não pertence à sua unidade." e o link "Voltar para Minha unidade" |

Pensado para a `autocadastro-com-aprovacao` (AD-016; seção própria para os pendentes, confirmada pelo usuário em 2026-11-23): a tela "Minha unidade" é uma sequência de
seções, cada uma com seu `h2` e a parcial de tabela. Hoje há uma ("Contas da unidade"); a feature
seguinte acrescenta "Pedidos pendentes" antes dela, com outra legenda e outras ações (Aprovar,
Recusar), sem tocar na seção que existe. A seção atual recebe `contas` já filtradas pela view, e
o filtro de pendentes entra no queryset, não no template.

### Menu e casca

- `templates/base.html`: depois de "Indicadores", `{% if user.is_gestor_de_unidade %}` o link
  `{% url 'gestao:painel' %}` com `{% include "icones/usuarios.svg" %}Minha unidade` e o
  `aria-current` pelo `menu_atual == "unidade"` (GEST-09, GEST-10).
- `nucleo/context_processors.py`: `PAGINA_ATUAL[("gestao", "painel")] = ("unidade", "page")` e
  um ramo `elif chave[0] == "gestao"` → `("unidade", "true")` (GEST-11).
- Ícone `templates/icones/usuarios.svg`: cópia do `users.svg` oficial do `lucide-static@1.78.0`
  (a mesma versão de que a `engrenagem.svg` é cópia exata, conferido em 2026-11-23), com a
  abertura da pasta (`aria-hidden="true" focusable="false" width="20" height="20"`, sem `class`
  nem `xmlns`). Formas, nesta ordem:
  `<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>`,
  `<path d="M16 3.128a4 4 0 0 1 0 7.744"/>`,
  `<path d="M22 21v-2a4 4 0 0 0-3-3.87"/>`,
  `<circle cx="9" cy="7" r="4"/>`.
  Um teste fixa as formas contra esse texto.

### Senha provisória (AD-017)

- **Location**: `contas/middleware.py`, `config/settings.py:68`
- **Interface**: `SenhaProvisoriaMiddleware.process_view(request, view_func, args, kwargs)`:
  1. anônimo → segue (o `LoginRequiredMiddleware`, que roda antes, já tratou);
  2. `request.user.senha_provisoria` falso → segue;
  3. view pública (`getattr(view_func, "login_required", True) is False`, a marca do
     `@login_not_required` que o `LoginRequiredMiddleware` também lê) → segue;
  4. rota `contas:trocar_senha` ou `contas:sair` → segue;
  5. senão → 302 para `/conta/senha/`.
- Roda no `process_view`, antes de qualquer view: a GEST-66 vale sozinha para `/minha-unidade/`
  e para o admin (o `admin:login` é público e segue; o índice e as telas do admin redirecionam).
- URL inexistente não chega ao `process_view` (sem `resolver_match`): continua 404.
- `TrocarSenhaView` (`PasswordChangeView`, `contas/views.py`): `form_class = TrocarSenhaForm`,
  `success_url = /inovacoes/`, alerta "Senha alterada."; o `update_session_auth_hash` do Django
  mantém a sessão (GEST-43).

### Cadastro e reaproveitamento (P2)

- `InovacaoCreateView.get_initial()` ganha `"unidade": usuario.unidade_id` (nulo → "Selecione…",
  GEST-56). A edição não muda (GEST-58).
- `ReaproveitamentoForm(data=None, *, inovacao, unidade_sugerida=None)`: quando
  `unidade_sugerida` está no queryset de elegíveis, vira o `initial` do campo (GEST-59, GEST-60).
  A view passa `request.user.unidade_id`. A chamada atual sem o argumento continua válida
  (`inovacoes/tests/test_forms_reaproveitamento.py`).

---

## Data Models

```python
class PerfilUsuario(models.TextChoices):
    USUARIO = "USUARIO", "Usuário"
    ADMINISTRADOR = "ADMINISTRADOR", "Administrador"
    GESTOR_DE_UNIDADE = "GESTOR_DE_UNIDADE", "Gestor de unidade"


class SituacaoConta(models.TextChoices):  # AD-016: derivada, sem coluna
    ATIVA = "ATIVA", "Ativa"
    DESATIVADA = "DESATIVADA", "Desativada"


TRANSICOES = {
    SituacaoConta.ATIVA: {SituacaoConta.DESATIVADA},
    SituacaoConta.DESATIVADA: {SituacaoConta.ATIVA},
}


class Usuario(AbstractUser):
    perfil = CharField(max_length=17, choices=PerfilUsuario.choices, default=USUARIO)
    unidade = ForeignKey(
        "inovacoes.Unidade", null=True, blank=True, on_delete=PROTECT, related_name="usuarios"
    )
    senha_provisoria = BooleanField(default=False)
    # Meta.constraints: usuario_perfil_valido (3 valores), usuario_email_unico_ci,
    #                   usuario_gestor_tem_unidade
```

**Relationships**: `Usuario.unidade` → `inovacoes.Unidade` (N:1, PROTECT). `Unidade` ganha o
reverso `usuarios`. O `UnidadeQuerySet.com_indicadores` (`inovacoes/models.py:61`) usa subconsulta
por `Inovacao` e `Reaproveitamento` e não é afetado pelo reverso novo.

**Migration**: `contas/migrations/0005_gestao_por_unidade.py`, só de esquema, reversível. Não
toca linhas: as contas atuais e os 15 autores do acervo (`@acervo.invalid`) ficam com unidade nula
e senha provisória falsa, válidos nas duas CHECKs. Um teste de migração aplica a 0005 sobre um
banco com contas USUARIO e ADMINISTRADOR em 0004 e confere que continuam iguais.

---

## Error Handling Strategy

| Error Scenario | Handling | User Impact |
| -------------- | -------- | ----------- |
| Não gestor em `/minha-unidade/…` | `GestaoDeUnidadeMixin` → 403 própria | "Acesso restrito a gestores de unidade." |
| Conta fora do escopo ou inexistente | `conta_alvo()` → 404 própria, nada gravado | "Esta conta não existe ou não pertence à sua unidade." |
| GET em `situacao/` | `http_method_names = ["post"]` → 405 | — (só chega por URL digitada) |
| `situacao` com valor inválido | 400, nada gravado | — (só por POST forjado) |
| Formulário inválido (criar, redefinir, trocar) | 200 com resumo de erros, erros nos campos, `<title>` com "Erro:" | Corrige sem perder os dados (exceto senhas) |
| Gestor sem unidade no admin | `clean()` no campo; CHECK como rede | Erro no campo Unidade |
| Gravação direta de gestor sem unidade | CHECK `usuario_gestor_tem_unidade` → `IntegrityError` | — |
| Excluir unidade com contas | PROTECT; tela do admin lista as contas | Exclusão recusada |
| CSRF inválido | `CsrfViewMiddleware` → 403 padrão | Sem alteração (GEST-67) |
| Senha provisória em qualquer rota interna | Middleware → 302 `/conta/senha/` | Precisa trocar antes de seguir |
| Desativação simultânea | `update_fields=["is_active"]`; mesmo destino, mesmo alerta | Os dois veem "desativada" |

---

## Risks & Concerns

| Concern | Location (file:line) | Impact | Mitigation |
| ------- | -------------------- | ------ | ---------- |
| GEST-07 diz "403, como faz com o USUARIO", mas o admin manda o USUARIO sem `is_staff` ao login do admin (302); só o USUARIO com `is_staff` recebe 403 | `contas/admin.py:8-35`; `contas/tests/test_admin_perfil.py:66-84` | AC impossível como escrita: o gestor nasce sem `is_staff` | **Emenda E-1** abaixo: sem `is_staff`, o admin manda ao login do admin; com `is_staff`, 403 |
| Resumo de erros, prefixo "Erro:" e barra de ações não têm AC | spec P1 Criar conta e Senha | O Verifier não teria âncora para o visual das telas novas | **Emendas E-2 e E-3** abaixo (GEST-68, GEST-69) |
| `perfil` com `max_length=13` | `contas/models.py:46-51` | `GESTOR_DE_UNIDADE` (17) estouraria a coluna | A 0005 altera para 17 |
| A CHECK e a `UniqueConstraint` de e-mail podem repetir como erro geral a mensagem que o formulário já põe no campo | `contas/models.py:59-70` | Mensagem duplicada no resumo de erros | Erro no campo exclui o campo da validação do modelo; um teste fixa "uma ocorrência" no resumo e no campo |
| Senha provisória só tem efeito pelo middleware: script ou view nova com `@login_not_required` escapa | `contas/middleware.py` (novo) | A pessoa com senha provisória chega a uma rota pública, que não mostra nada interno | Aceito: rota pública já é exceção visível (AD-006). Um teste varre as rotas internas com uma conta de senha provisória e exige 302 para `/conta/senha/` em todas, salvo a troca e o sair |
| Gestor trocado de unidade com abas abertas | `inovacoes/models.py:259` | Ação vista antes, recusada depois | Aceito: a regra roda no POST, e a tela recusa com a 403/404 própria |
| Sem trilha de auditoria das ações do gestor | — | LGPD: não se sabe quem desativou ou redefiniu | Fora do escopo (spec, Out of Scope); ideia adiada no `context.md` |
| Varredura por papel (L-003) não existe para a área do gestor | `contas/tests/` | Rota nova da área pode abrir a outro papel em silêncio | Teste novo de varredura das rotas do namespace `gestao` para USUARIO, USUARIO staff, USUARIO superusuário, ADMINISTRADOR, superusuário (403) e gestor de outra unidade (404 nas rotas com `pk`, sem gravar) |

### Emendas à spec (aprovadas com o design em 2026-11-23)

- **E-1 (GEST-07)**: "WHILE o usuário tem perfil `GESTOR_DE_UNIDADE`, o sistema SHALL negar toda
  tela do admin como nega ao USUARIO (AD-007): sem `is_staff`, redireciona ao login do admin; com
  `is_staff`, responde 403."
- **E-2 (GEST-68, nova)**: "IF o envio de criar conta, redefinir senha ou trocar senha falha THEN
  o sistema SHALL exibir no topo o resumo de erros da §6 v2, com o título 'Não foi possível
  {criar a conta | redefinir a senha | trocar a senha}. Corrija {n} campo(s):' e um link por campo
  com erro, e o `<title>` SHALL começar por 'Erro:'."
- **E-3 (GEST-69, nova)**: "The formulários de criar conta, redefinir senha e trocar senha SHALL
  terminar na barra de ações da §6 v2: o botão de envio, o link 'Cancelar' e a nota 'Nada é
  gravado se você cancelar.'; WHILE a conta tem senha provisória, a tela de trocar senha SHALL
  não exibir 'Cancelar' nem a nota."

---

## Tech Decisions (only non-obvious ones)

| Decision | Choice | Rationale |
| -------- | ------ | --------- |
| Namespace da área | `gestao` (módulo `contas/urls_gestao.py`), não `contas` | O `PAGINA_ATUAL` marca seções por namespace (AD-015): um namespace só para a área dá o "true" de toda a seção numa linha |
| Ação de situação | Uma rota, valor de destino no POST | Idempotente (GEST-32) e pronta para "Aprovar" de uma conta pendente (AD-016) sem rota nova |
| 404 do gestor | Página própria, não o `Http404` padrão | Com `DEBUG=False`, o 404 padrão sai sem a casca; a área tem link de volta |
| Campo v2 em `templates/paginas/` | Parcial nova, não alterar `inovacoes/campo.html` | Os formulários de inovação ficam fora desta feature; a parcial nova serve ao redesign deles depois |
| `SituacaoConta` derivada | Propriedade, sem coluna | AD-016 |
| Senha provisória por middleware | `process_view` depois do `LoginRequiredMiddleware` | AD-017 |

Decisões de projeto registradas no `STATE.md`: extensão da AD-004 e da AD-009, AD-016 (situação da
conta) e AD-017 (senha provisória).

---

## Testes antigos (inventário aprovado, T-1 a T-6)

Ligados às tasks: T-1, T-2 com a curadoria; T-3 com o modelo; T-4 com o menu; T-5 e T-6 com as
telas. Contagem do DS-01: **13 → 19** (as seis telas da tabela acima); `PECAS` ganha
`paginas/campo.html`, `paginas/resumo_erros.html` e `contas/gestao/parciais/tabela_contas.html`.

---

## Ajustes do Execute

- **T1, dependência da 0005**: o `makemigrations` pôs a 0005 dependendo de `inovacoes 0008`
  (a última da app). Fixada em `inovacoes 0001_initial`, como este design já dizia: com a 0008,
  o teste antigo `inovacoes/tests/test_migracoes.py` (que volta a `inovacoes 0005`) desfazia
  também a `contas 0005` e quebrava. A 0001 já cria a `Unidade`, e a FK só precisa dela.
- **T1, formatação deste arquivo**: o Ruff 0.16 formata os blocos Python de Markdown, e o bloco
  de Data Models acima falhava o `ruff format --check .` do build gate. Só a formatação mudou.
- **T5, GEST-05 conferida**: o `add_error("unidade", …)` no `clean()` faz o Django tirar a
  `unidade` da validação do modelo, como previsto. O formulário tem só
  `{"unidade": ["Gestor de unidade precisa de uma unidade."]}` e a mensagem aparece uma vez na
  página. Sem o `clean()`, a CHECK vira erro geral (`__all__`): o teste pega a diferença.
- **T5, GEST-07 com `is_staff`**: o 403 vale em toda tela de usuário e de unidade. Nos índices
  dos apps (`/admin/contas/`, `/admin/inovacoes/`), o Django responde 404, como já faz ao USUARIO
  com `is_staff` (`contas/tests/test_admin_perfil.py`). É a mesma negação da AD-007 ("como nega
  ao USUARIO"), e o teste fixa os dois códigos.
- **T7, renderizador**: o renderizador padrão de formulários do Django só lê os templates das
  apps e os dele, e não acha `templates/paginas/campo.html`. O `FormularioV2Mixin` usa
  `nucleo.formularios.RenderizadorV2` (`default_renderer`), que soma a pasta `templates/` do
  projeto. O `FORM_RENDERER` do projeto não muda; os formulários de inovação seguem iguais.
- **T7, `aria-describedby`**: o Django põe a ajuda antes do erro. O mixin troca o BoundField
  (`bound_field_class = CampoV2`, Django 5.2) para pôr o erro antes da ajuda.
- **T7, peças**: a parcial do campo não traz o `div.campo`; a tela o põe em volta, como no
  `inovacao_form.html`. "(obrigatório)" vai num `span.legenda`, classe que já existe (muted).
  O resumo conta só os campos com erro ("Corrija {n} campo(s)"), um link por campo com as
  mensagens juntas, e põe os erros gerais, sem link, antes dos campos (a §6 não diz a posição).
  O foco no resumo ao carregar a página (§6 v2) fica para as telas que o usam.
- **T8, coluna "Ações"**: a tabela ganha um sétimo cabeçalho, "Ações", depois dos seis da
  GEST-13. A célula das ações precisa de cabeçalho de coluna (`th scope="col"`); as contas sem
  ação ficam com a célula vazia (GEST-18).
- **T8, links antes das rotas**: "Criar conta", "Redefinir senha" e o `form` de situação saem com
  os caminhos do design escritos no template (`/minha-unidade/contas/nova/`,
  `/minha-unidade/contas/{pk}/senha/`, `/minha-unidade/contas/{pk}/situacao/`). A T10, a T11 e a
  T12 trocam cada um por `{% url %}` quando a rota nasce (decisão do usuário em 2026-11-23).
- **T8, contexto**: a view põe a unidade como `unidade_do_gestor`, não `unidade`, porque
  `unidade` é o parâmetro da trilha e o `include` herda o contexto. Cada linha recebe
  `administravel` (`pode_ser_administrada_por`, sem consulta), já que o template não passa
  argumento a método.
- **T8, porteiro**: nas rotas com `pk`, o `GestaoDeUnidadeMixin` busca a conta no `dispatch`,
  antes do método HTTP. Um GET do gestor de outra unidade na rota de situação dá 404, não 405;
  o 405 da GEST-33 vale para a conta do escopo.
- **T9, "true" da seção**: na T9 só existe a rota `gestao:painel`; o ramo do namespace `gestao`
  é testado com o `resolver_match` das rotas futuras (`criar_conta`, `situacao`,
  `redefinir_senha`). O `aria-current="true"` exibido entra no teste e2e da T10 e da T12, junto
  com cada tela.
- **T10, validador no campo certo**: o `BaseUserCreationForm` põe a mensagem do validador de
  senha na confirmação (`password2`). A GEST-26 pede no campo "Senha provisória": o
  `ContaDaUnidadeForm._post_clean` valida pelo `password1`.
- **T10, foco no resumo**: a parcial `paginas/resumo_erros.html` ganhou `autofocus` (o resumo
  recebe o foco ao carregar a página com erro, §6 v2, sem script). O teste do Lote A em
  `nucleo/tests/test_formularios.py` passou a exigir o atributo. Com erro, o formulário tira o
  `autofocus` que o Django põe no campo Usuário, para o foco ir só ao resumo.
- **T10, rota**: "Criar conta" da lista passou a `{% url 'gestao:criar_conta' %}`.
- **T11, rota**: o `form` de situação da tabela passou a `{% url 'gestao:situacao' conta.pk %}`.
  A varredura por papel ganhou a sanidade de enxergar essa rota, a primeira com `pk`.
- **T12, validador no campo da senha**: como na T10, o `SenhaProvisoriaForm.clean` valida pelo
  `new_password1` (o `SetPasswordForm` usaria o `new_password2`), para a GEST-38 acusar "como na
  criação". O link "Redefinir senha" da tabela passou a `{% url 'gestao:redefinir_senha' conta.pk %}`.
- **T13, trocar senha**: como na T10 e na T12, o `TrocarSenhaForm.clean` valida pelo
  `new_password1`, e com erro o formulário tira o `autofocus` que o Django põe na Senha atual. O
  aviso da GEST-42 é um `p.alerta.alerta--warning` no conteúdo, depois do resumo de erros e antes
  do cartão.
