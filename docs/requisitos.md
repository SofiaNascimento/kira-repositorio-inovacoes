# Documento de Regras de Negócio e Requisitos

**Sistema de Repositório e Compartilhamento de Inovações de Back Office**

*Escopo de MVP (Minimum Viable Product) — Trabalho de Conclusão de Curso*

---

## 1. Introdução e Objetivo do Documento

Este documento especifica as regras de negócio (RN), os requisitos funcionais (RF) e os requisitos não funcionais (RNF) do Sistema de Repositório e Compartilhamento de Inovações de Back Office. Seu propósito é servir de referência única para o desenvolvimento do protótipo funcional (MVP) proposto no Trabalho de Conclusão de Curso, garantindo rastreabilidade entre a necessidade organizacional identificada, as regras que governam o domínio e as funcionalidades a serem implementadas.

O escopo aqui definido corresponde a um MVP: o conjunto mínimo de funcionalidades capaz de entregar valor e comprovar a viabilidade técnica e organizacional da proposta. Requisitos não essenciais à validação da hipótese central são explicitamente classificados como desejáveis ou fora do escopo, evitando a dispersão de esforço característica de projetos acadêmicos com prazo limitado.

Nesta revisão, os requisitos de interação com o usuário foram reforçados com base em dois referenciais consolidados de qualidade de uso: as dez heurísticas de usabilidade de Nielsen (1994) e as diretrizes de acessibilidade web WCAG 2.1 (nível AA), complementadas pelo modelo de acessibilidade brasileiro eMAG (Modelo de Acessibilidade em Governo Eletrônico). Com isso, o eixo de IHC e UX/UI passa a ter cobertura explícita e rastreável, não restrita à métrica de satisfação (SUS).

### 1.1 Convenções de nomenclatura e priorização

Cada item recebe um identificador único (RN, RF ou RNF seguido de numeração sequencial) para permitir referência cruzada na matriz de rastreabilidade. A priorização adota a técnica MoSCoW, amplamente utilizada em métodos ágeis:

- **Essencial (Must have):** indispensável ao MVP; sem ele o produto não cumpre seu propósito.
- **Importante (Should have):** agrega valor relevante, mas o MVP funciona sem ele.
- **Desejável (Could have):** melhoria incremental, implementada apenas se houver tempo.

### 1.2 Perfis de usuário

O sistema define dois perfis de acesso, cuja distinção governa as regras de autoria, edição e exclusão descritas nas seções seguintes:

- **Usuário comum:** colaborador autenticado da organização. Pode consultar todas as inovações e cadastrar novas; pode editar e excluir apenas as inovações que ele próprio cadastrou.
- **Administrador:** perfil com poderes ampliados de governança do repositório. Além de todas as ações do usuário comum, pode editar e excluir inovações de qualquer autor, assegurando a curadoria e a integridade do conteúdo institucional.

---

## 2. Regras de Negócio (RN)

As regras de negócio descrevem as restrições, políticas e comportamentos do domínio que o sistema deve respeitar, independentemente da tecnologia empregada. Elas derivam diretamente do problema de pesquisa: viabilizar o registro, a busca e o reaproveitamento de inovações de back office entre unidades de uma mesma empresa.

| ID | Descrição da regra | Prioridade |
| --- | --- | --- |
| RN01 | Toda inovação registrada deve pertencer obrigatoriamente a uma única unidade de origem (sede/filial) e a uma única categoria. | Essencial |
| RN02 | O registro de uma inovação só é válido se contiver, no mínimo, os campos: título, problema/dor, solução aplicada, categoria e unidade de origem. | Essencial |
| RN03 | Toda inovação possui um status do ciclo de vida: 'Em teste', 'Validada' ou 'Disponível para replicação'. O status inicial padrão é 'Em teste'. | Essencial |
| RN04 | Apenas usuários autenticados podem cadastrar, editar ou excluir inovações; a consulta é permitida a qualquer usuário autenticado da organização. | Essencial |
| RN05 | Um usuário comum só pode editar ou excluir inovações que ele próprio cadastrou. O perfil de administrador pode editar ou excluir inovações de qualquer autor, para fins de curadoria e integridade do repositório. | Essencial |
| RN06 | Cada inovação deve indicar um contato responsável, para que outras unidades possam esclarecer dúvidas sobre a implementação. | Essencial |
| RN07 | Categorias e unidades são valores controlados (listas pré-definidas), não texto livre, garantindo consistência na busca e nos filtros. | Essencial |
| RN08 | O sistema deve registrar automaticamente a data de criação e o autor de cada inovação, sem intervenção do usuário. | Essencial |
| RN09 | Uma inovação 'Disponível para replicação' pode ser sinalizada como reaproveitada por outra unidade, alimentando a métrica de reuso. | Importante |
| RN10 | O sistema não deve permitir o cadastro de duas inovações com título idêntico dentro da mesma unidade de origem. | Importante |
| RN11 | A atribuição do perfil de administrador é restrita e feita apenas por outro administrador, não sendo passível de autoconcessão pelo usuário comum. | Importante |
| RN12 | Toda ação destrutiva ou irreversível (exclusão de inovação) deve exigir confirmação explícita do usuário antes de ser efetivada, prevenindo perdas acidentais de conteúdo. | Importante |

---

## 3. Requisitos Funcionais (RF)

Os requisitos funcionais descrevem o que o sistema deve fazer — as funcionalidades observáveis pelo usuário. O conjunto abaixo está delimitado ao MVP e organizado segundo as funcionalidades centrais: autenticação, cadastro, consulta, visualização e suporte à interação. Os requisitos RF12 a RF15 foram acrescentados nesta revisão para materializar heurísticas de usabilidade de Nielsen no comportamento observável do sistema.

| ID | Nome | Descrição | Prioridade |
| --- | --- | --- | --- |
| RF01 | Autenticação de usuário | Permitir o acesso ao sistema mediante login e senha, utilizando o sistema de autenticação nativo do Django (sessão gerenciada por cookie de sessão do framework). | Essencial |
| RF02 | Cadastro de inovação | Permitir o registro de uma inovação por formulário estruturado, contemplando os campos definidos na estrutura de dados. | Essencial |
| RF03 | Listagem de inovações | Exibir a lista de inovações cadastradas com informações resumidas (título, categoria, unidade e status). | Essencial |
| RF04 | Visualização detalhada | Exibir a página de detalhe de uma inovação, com todos os campos e o contato do responsável. | Essencial |
| RF05 | Busca por palavra-chave | Permitir a pesquisa textual por termos presentes no título, problema ou solução. | Essencial |
| RF06 | Filtros combinados | Permitir filtrar por categoria, unidade de origem e status, de forma isolada ou combinada. | Essencial |
| RF07 | Edição de inovação | Permitir que o autor altere os dados de uma inovação já cadastrada. O perfil de administrador pode editar inovações de qualquer autor. | Essencial |
| RF08 | Exclusão de inovação | Permitir que o autor remova uma inovação, mediante confirmação. O perfil de administrador pode excluir inovações de qualquer autor. | Importante |
| RF09 | Gestão do status | Permitir a atualização do status da inovação ao longo de seu ciclo de vida. | Importante |
| RF10 | Painel de indicadores | Exibir um dashboard com métricas consolidadas (total, distribuição por categoria/unidade e reaproveitamentos). | Desejável |
| RF11 | Sinalização de reuso | Permitir que uma unidade sinalize ter reaproveitado uma inovação, alimentando a métrica de reuso. | Desejável |
| RF12 | Feedback de ações | Após cada ação relevante (cadastro, edição, exclusão, alteração de status), exibir mensagem de confirmação clara sobre o resultado (sucesso ou falha), mantendo o usuário informado sobre o estado do sistema. | Essencial |
| RF13 | Validação e recuperação de erros | Validar os dados dos formulários e, em caso de erro, exibir mensagens em linguagem clara, indicando o campo afetado e como corrigi-lo, sem descartar os dados já preenchidos pelo usuário. | Essencial |
| RF14 | Prevenção de perda e cancelamento | Oferecer, nas ações destrutivas ou irreversíveis, confirmação prévia (RN12) e, nos formulários, a opção de cancelar/retornar sem salvar, permitindo ao usuário desfazer com facilidade. | Importante |
| RF15 | Ajuda contextual | Disponibilizar textos de apoio, rótulos descritivos e dicas nos campos e filtros (por exemplo, exemplos de preenchimento), reduzindo a necessidade de conhecimento prévio para operar o sistema. | Desejável |

---

## 4. Requisitos Não Funcionais (RNF)

Os requisitos não funcionais descrevem como o sistema deve se comportar — atributos de qualidade que restringem a solução. Cada item é associado a uma característica da norma ISO/IEC 25010, reforçando a preocupação com a qualidade de software. Nesta revisão, o RNF01 (usabilidade) foi ancorado nas heurísticas de Nielsen e foi acrescentado o RNF09, dedicado à acessibilidade web (WCAG 2.1 AA e eMAG).

| ID | Atributo (ISO/IEC 25010) | Descrição | Prioridade |
| --- | --- | --- | --- |
| RNF01 | Usabilidade | A interface deve observar as dez heurísticas de usabilidade de Nielsen (1994) e ser submetida a avaliação heurística; deve, ainda, obter nota mínima de 68 pontos na escala SUS (System Usability Scale) em teste com usuários. | Essencial |
| RNF02 | Segurança | As senhas devem ser armazenadas com hash (mecanismo nativo do Django); o controle de acesso deve seguir boas práticas e estar em conformidade com a LGPD. A sessão do usuário é gerenciada pelo framework de autenticação do Django. | Essencial |
| RNF03 | Compatibilidade | O sistema deve ser acessível em navegadores modernos (Chrome, Firefox, Edge) e responsivo em desktop e tablet. | Importante |
| RNF04 | Manutenibilidade | O código deve ser modular, com separação entre front-end, back-end e camada de dados, facilitando manutenção e evolução. | Importante |
| RNF05 | Persistência | Os dados devem ser armazenados de forma persistente em banco relacional (PostgreSQL), com integridade referencial. | Essencial |
| RNF06 | Portabilidade | A solução deve ser publicável em plataformas de hospedagem em nuvem de camada gratuita (Render, Railway ou Vercel). | Desejável |
| RNF07 | Segurança (autorização) | O sistema deve restringir as ações de edição e exclusão conforme o perfil do usuário (comum ou administrador), impedindo que um usuário comum altere registros de terceiros. | Essencial |
| RNF08 | Desempenho | As operações de busca e listagem devem retornar resultados em tempo adequado à interação (referência: até 2 segundos para o conjunto de dados de demonstração). | Desejável |
| RNF09 | Acessibilidade | A interface deve estar em conformidade com as diretrizes WCAG 2.1 no nível AA e com o modelo eMAG, contemplando, entre outros: alternativa textual para imagens, contraste mínimo de cor (4.5:1 para texto), rótulos associados a todos os campos de formulário, navegação completa por teclado, foco visível, uso de HTML semântico e não dependência exclusiva de cor para transmitir informação. | Essencial |

### 4.1 Aderência às Heurísticas de Nielsen

A tabela a seguir relaciona cada uma das dez heurísticas de usabilidade de Nielsen aos requisitos e regras deste documento que a concretizam, permitindo que a avaliação heurística prevista no RNF01 verifique a cobertura de forma rastreável.

| # | Heurística de Nielsen | Requisitos/Regras que a atendem |
| --- | --- | --- |
| H1 | Visibilidade do status do sistema | RF12, RF09, RNF08 |
| H2 | Correspondência entre o sistema e o mundo real | RF15, RN07 (listas com vocabulário do domínio), RNF01 |
| H3 | Controle e liberdade do usuário | RF14, RN12 |
| H4 | Consistência e padrões | RNF01, RNF04, RN07 |
| H5 | Prevenção de erros | RF13, RF14, RN02, RN10, RN12 |
| H6 | Reconhecimento em vez de memorização | RF06, RF15, RN07 |
| H7 | Flexibilidade e eficiência de uso | RF05, RF06 |
| H8 | Design estético e minimalista | RNF01, RF03 (informações resumidas) |
| H9 | Ajudar a reconhecer, diagnosticar e recuperar-se de erros | RF13, RF12 |
| H10 | Ajuda e documentação | RF15 |

---

## 5. Estrutura de Dados da Inovação

O núcleo do sistema é a entidade Inovação, cujo modelo de campos é apresentado a seguir. Esta estrutura materializa o fluxo problema → solução → resultado → unidade de origem que sustenta a proposta.

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| Título da inovação | Texto | Sim | Nome curto e descritivo da solução. |
| Unidade de origem | Lista controlada | Sim | Sede/filial que desenvolveu a solução. |
| Problema/dor | Texto longo | Sim | Descrição objetiva do problema que motivou a solução. |
| Solução aplicada | Texto longo | Sim | Descrição de como o problema foi resolvido na prática. |
| Categoria | Lista controlada | Sim | Financeiro, RH, TI interno, Compras, Atendimento interno etc. |
| Resultado/impacto | Texto | Não | Ganho percebido (tempo, custo, erro evitado). |
| Status | Lista controlada | Sim | Em teste, Validada, Disponível para replicação. |
| Contato responsável | Texto | Sim | Pessoa a ser procurada por outras unidades. |

---

## 6. Matriz de Rastreabilidade

A matriz relaciona cada objetivo específico do projeto às regras e requisitos que o concretizam, permitindo verificar a cobertura da solução. Foi acrescentada a linha de qualidade de interação, que reúne os requisitos de usabilidade e acessibilidade.

| Objetivo específico | Regras (RN) | Requisitos (RF/RNF) |
| --- | --- | --- |
| Definir modelo estruturado de registro | RN01, RN02, RN07 | RF02, RF04 |
| Permitir consulta e reaproveitamento | RN04, RN09 | RF03, RF05, RF06, RF11 |
| Garantir controle e integridade | RN05, RN08, RN10, RN11, RN12 | RF01, RF07, RF08, RF14 |
| Apoiar a gestão do conhecimento (indicadores) | RN09 | RF09, RF10 |
| Assegurar qualidade, portabilidade e segurança | RN11 | RNF01, RNF02, RNF04, RNF07 |
| Assegurar qualidade de interação (usabilidade e acessibilidade) | RN12 | RF12, RF13, RF14, RF15, RNF01, RNF09 |

---

## 7. Aderência aos Eixos de Conhecimento (ENADE)

A tabela abaixo evidencia como os requisitos e regras deste documento se articulam com os eixos de conhecimento avaliados, tornando a aderência explícita e rastreável.

| Eixo | Descritores contemplados | Onde é atendido |
| --- | --- | --- |
| 1. Tecnologia e Desenvolvimento de Software | Engenharia de requisitos, modelagem, Kanban, qualidade (ISO/IEC 25010), persistência. | Todo o documento; RF01–RF09; RNF05, RNF06. |
| 2. IHC e UX/UI | Design de interface, usabilidade (heurísticas de Nielsen), acessibilidade e testes empíricos. | RF12–RF15; RNF01 (Nielsen + SUS ≥ 68); RNF09 (WCAG 2.1 AA, eMAG); seção 4.1. |
| 3. Dados, Inteligência e Infraestrutura | Business Intelligence (dashboards) e segurança da informação. | RF10, RF11; RNF02 (LGPD, autenticação Django), RNF05, RNF07. |
| 4. Gestão, Negócios e Governança de TI | Mapeamento de processos, análise de viabilidade e otimização processual. | Seção 2 (RN); matriz de rastreabilidade. |
| 5. Ética, Sustentabilidade e Sociedade (ODS) | Uso ético de dados, inclusão digital e alinhamento aos ODS da ONU. | RNF02 (LGPD); RNF09 (acessibilidade/inclusão); ODS 8, 9, 10 e 12. |

**Nota sobre ODS:** a proposta alinha-se ao ODS 8 (trabalho decente e crescimento econômico, via ganho de produtividade), ao ODS 9 (indústria, inovação e infraestrutura), ao ODS 10 (redução das desigualdades, por meio da acessibilidade e inclusão digital promovidas pelo RNF09) e ao ODS 12 (consumo e produção responsáveis, ao reduzir retrabalho e desperdício de esforço).

---

## 8. Delimitações e Itens Fora do Escopo do MVP

- Compartilhamento entre empresas distintas (o sistema é multi-sede, não multi-empresa).
- Inovação de produto ou serviço voltada ao cliente final.
- Integração automática com sistemas legados da organização (ERP, RH etc.).
- Aprovação/moderação em fluxo de workflow com múltiplos níveis hierárquicos.
- Aplicativo móvel nativo (o MVP é web responsivo).
- Conformidade WCAG no nível AAA e auditoria de acessibilidade por terceiros (o MVP visa o nível AA).
