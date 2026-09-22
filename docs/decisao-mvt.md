# Documento de Decisão Arquitetural

**Padrão de Projeto MVT (Model-View-Template) — KIRA**

---

## 1. O Padrão MVT

O MVT (Model-View-Template) é a arquitetura própria do Django, uma variação do clássico MVC (Model-View-Controller). Ele divide a aplicação em três camadas de responsabilidade bem definidas, favorecendo a separação de interesses e a manutenibilidade do código.

| Camada | Responsabilidade | Onde vive no Django |
| --- | --- | --- |
| Model | Representa os dados e o acesso ao banco: a entidade Inovação, seus campos e regras de persistência. | `models.py` |
| View | Recebe a requisição, coordena a lógica e devolve a resposta. Corresponde ao 'Controller' do MVC. | `views.py` |
| Template | Camada de apresentação: o HTML exibido ao usuário (formulários, listagens, detalhe). | arquivos `.html` |

A ligação entre as camadas é feita pelo roteador de URLs (**URLconf**), que direciona cada requisição à View correspondente. A View consulta ou altera os Models e escolhe qual Template renderizar como resposta.

---

## 2. MVT e sua Relação com o MVC

Embora derive do MVC, o MVT redistribui responsabilidades de uma forma característica do Django, o que é útil esclarecer na fundamentação teórica:

| MVC clássico | Equivalente no MVT | Observação |
| --- | --- | --- |
| Model | Model | Papel idêntico: dados e regras de persistência. |
| Controller | View | No Django, a View faz o papel do Controller. |
| View (apresentação) | Template | O Template cuida exclusivamente da apresentação. |

O ponto essencial é que, no MVT, boa parte do 'Controller' é executada pelo próprio framework: o roteamento, a resolução de URLs e o ciclo requisição-resposta são responsabilidade do Django, cabendo ao desenvolvedor apenas escrever a lógica específica da aplicação. Isso reduz a quantidade de código a ser produzido e reforça a **simplicidade de implementação** buscada no MVP.

---

## 3. Aplicação ao Sistema Proposto

No contexto do repositório de inovações, cada camada do MVT concretiza partes específicas dos requisitos e regras já especificados:

### 3.1 Model

Concentra a entidade **Inovação** com seus campos e as listas controladas de categoria, unidade e status. Atende diretamente às regras de estrutura e integridade: RN01 (unidade e categoria únicas), RN02 (campos obrigatórios), RN07 (valores controlados) e RN08 (registro automático de autor e data). Também é onde o mapeamento objeto-relacional garante a persistência em PostgreSQL exigida pelo RNF05.

### 3.2 View

Coordena as funcionalidades observáveis: cadastro (RF02), listagem (RF03), visualização detalhada (RF04), busca (RF05), filtros (RF06), edição (RF07), exclusão (RF08) e gestão de status (RF09). É também na View que se aplica o controle de acesso por perfil — autenticação (RF01), permissões de autor versus administrador (RN04, RN05) e a restrição de autorização do RNF07.

### 3.3 Template

Responsável pela interface apresentada ao usuário: o formulário estruturado de registro, a lista de inovações, a página de detalhe com o contato do responsável (RN06) e os controles de filtro. É a camada onde se materializam as preocupações de usabilidade (RNF01, meta SUS ≥ 68) e de responsividade em desktop e tablet (RNF03).

---

## 4. Vantagens da Adoção do MVT

- **Simplicidade de implementação:** é o padrão nativo do Django; não há camadas adicionais a construir.
- **Separação de camadas (RNF04):** Model, View e Template isolam dados, lógica e apresentação, atendendo à exigência de código modular.
- **Rastreabilidade:** cada regra e requisito tem um lugar previsível (Model, View ou Template), facilitando a demonstração na banca.
