# Modelagem UML do Sistema

**Sistema de Repositório e Compartilhamento de Inovações de Back Office**

*Diagramas de Caso de Uso, de Classes e de Sequência — Trabalho de Conclusão de Curso*

---

## 1. Diagrama de Caso de Uso

O diagrama de caso de uso representa a fronteira do sistema: quem interage com ele (os atores) e quais funcionalidades cada ator pode acionar (os casos de uso). É a visão mais próxima do usuário, pois descreve o comportamento observável do sistema sem entrar em detalhes de implementação.

*Figura 1 — Diagrama de Caso de Uso*

### 1.1 Lógica por trás do diagrama

Há dois atores. O ator Usuário representa o colaborador comum autenticado, e o ator Administrador representa o perfil de curadoria. A relação de generalização entre eles é a decisão central do diagrama: o Administrador herda todos os casos de uso do Usuário e adiciona poderes ampliados. Na prática, isso significa que tudo o que um usuário comum faz, o administrador também faz — evitando duplicar dezenas de associações no desenho.

**Autenticação:** os casos 'Realizar login' e 'Sair da plataforma' governam a entrada e saída do sistema. As relações «include» com 'Validar credenciais', 'Iniciar sessão autenticada' e 'Encerrar sessão' explicitam que essas verificações são partes obrigatórias do fluxo de autenticação — materializando o RF01 e a RN04.

**Autoria e permissões:** os rótulos 'próprias inovações' (nas associações do Usuário para 'Editar inovação' e 'Excluir inovação') versus 'qualquer inovação' (nas associações do Administrador) traduzem visualmente a RN05: o usuário comum só altera o que cadastrou; o administrador atua sobre qualquer registro, para fins de curadoria e integridade.

**Ciclo de vida e reuso:** a relação «include» condicional entre 'Alterar status da inovação' e 'Sinalizar reaproveitamento da inovação', guardada pela condição [status = Disponível para replicação], reflete a RN03 e a RN09: só faz sentido sinalizar reuso de uma inovação que já esteja disponível para replicação.

As notas na base do diagrama fixam três premissas que amarram o desenho às regras: login por usuário/e-mail e senha; campos obrigatórios com status inicial 'Em teste', listas controladas e título único por unidade (RN01, RN02, RN03, RN07, RN10); e a política de permissões (RN04).

---

## 2. Diagrama de Classes

O diagrama de classes é a visão estrutural do sistema: descreve as entidades do domínio (classes), seus atributos e operações, e como se relacionam entre si por meio de associações com multiplicidade. É a ponte direta entre o modelo conceitual e o modelo de dados que será implementado no PostgreSQL.

*Figura 2 — Diagrama de Classes (versão refinada)*

### 2.1 Lógica por trás do diagrama

**Inovacao como entidade central:** a classe Inovacao concentra o núcleo do domínio, materializando o fluxo problema → solução → resultado → unidade de origem. Seus atributos correspondem um a um aos campos da estrutura de dados do documento de requisitos. As operações `alterarStatus()`, `atualizarDados()` e `podeSerReaproveitada()` encapsulam as regras de comportamento: a transição de status (RN03), a edição controlada (RN05) e a verificação que habilita o reuso (RN09).

**Usuario e o perfil:** a classe Usuario guarda o atributo perfil, do tipo enumerado PerfilUsuario (USUARIO ou ADMINISTRADOR). É assim que a generalização vista no caso de uso se materializa em dados: em vez de duas classes distintas, um único tipo de usuário com um campo que determina seus poderes — abordagem alinhada ao modelo de usuário do Django. O atributo senhaHash reforça o RNF02 (senha nunca armazenada em texto puro).

**Listas controladas — Unidade e Categoria:** Unidade e Categoria são classes próprias, e não texto livre, o que concretiza a RN07. Uma Inovacao pertence a exatamente uma Unidade (origem) e a exatamente uma Categoria — daí a multiplicidade 0..* para 1 em ambas as associações: muitas inovações podem compartilhar a mesma unidade ou categoria, mas cada inovação tem apenas uma de cada.

**Enumerações como valores controlados:** StatusInovacao (EM_TESTE, VALIDADA, DISPONIVEL_PARA_REPLICACAO) e PerfilUsuario são modelados como «enumeration». Isso garante, já no modelo, que esses campos só assumam valores válidos e pré-definidos — a mesma lógica das listas controladas, aplicada a estados e papéis.

**Reaproveitamento como métrica:** a classe Reaproveitamento registra cada vez que uma unidade aproveita uma inovação de outra. A associação 'Inovacao 1 → 0..* Reaproveitamento' (recebe) e 'Reaproveitamento 0..* → 1 Unidade' (realizado por) permite responder à pergunta que sustenta a proposta: quantas vezes, e por quais unidades, uma solução foi reutilizada. É essa entidade que alimenta o painel de indicadores (RF10) e a métrica de reuso (RF11).

---

## 3. Diagrama de Sequência

O diagrama de sequência é a visão dinâmica do sistema: mostra, ao longo do tempo, como os objetos e componentes trocam mensagens para realizar cada funcionalidade. Enquanto o caso de uso diz o quê e o diagrama de classes diz com quais estruturas, o diagrama de sequência diz em que ordem e por quais camadas a informação passa.

Os participantes representam a arquitetura em camadas do sistema (RNF04): o ator, a Interface Web, a API/Backend, os serviços de Autenticação e de Inovação, e o Banco de Dados PostgreSQL. Essa separação de responsabilidades é justamente o atributo de manutenibilidade exigido nos requisitos não funcionais.

A figura completa é apresentada na página seguinte, dado seu formato vertical, para preservar a legibilidade das trocas de mensagens entre as camadas.

*Figura 3 — Diagrama de Sequência: Login e Inovação*

### 3.1 Lógica por trás do diagrama

**Login com tratamento de erro:** o fluxo começa com o acesso à plataforma e a solicitação de autenticação. O fragmento 'alt' (alternativa) é o coração do login: se as credenciais forem inválidas, o Serviço de Autenticação recusa e a interface exibe mensagem de erro; se forem válidas, o Django inicia a sessão autenticada e devolve os dados do usuário. Esse ramo condicional cobre tanto o caminho feliz quanto o de falha, exigência de um bom modelo de autenticação (RF01, RN04).

**Consulta antes de detalhe:** após o login, o usuário solicita a lista de inovações (RF03) e, ao selecionar uma, solicita os detalhes por id (RF04). O diagrama mostra a mensagem descendo pelas camadas — Interface → API → Serviço de Inovação → Banco — e a resposta subindo de volta. Essa ida e volta explícita é o que evidencia a arquitetura em camadas.

**Cadastro com regras automáticas:** no cadastro (RF02), a mensagem 'Registrar autor + data; status = Em teste' que a API envia ao serviço materializa a RN08 (autor e data preenchidos automaticamente) e a RN03 (status inicial padrão). O usuário não informa esses dados — o sistema os define, e o diagrama torna isso visível.

**Ciclo de vida e reuso:** a alteração de status percorre a transição Em teste → Validada → Disponível para replicação (RN03). Só então a sinalização de reaproveitamento é validada e registrada, atualizando a métrica de reuso (RN09, RF11) — a mesma condição que aparece guardada no caso de uso.

**Indicadores e logout:** por fim, o acesso aos indicadores (RF10) dispara o cálculo de métricas consolidadas a partir dos dados de reaproveitamento, e o logout encerra a sessão do lado do servidor, coerente com o encerramento de sessão do Django.

Em conjunto, os três diagramas descrevem o mesmo sistema sob ângulos diferentes: o caso de uso delimita as funcionalidades e os atores, o diagrama de classes fixa a estrutura de dados e comportamento, e o diagrama de sequência ordena as interações no tempo. A consistência entre eles — mesmos atores, mesmas regras, mesma política de autenticação — é o que dá solidez à modelagem.
