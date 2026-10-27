"""Acervo realista da carga de demonstracao (acervo-realista, ACER-01 a ACER-09).

Catalogo de casos de back office escritos a mao e a montagem deterministica dos 500
registros. Sem banco: recebe os nomes das unidades e devolve dicionarios; o comando
carregar_demonstracao grava. Cada caso aparece em 1 a 5 unidades, com numeros,
sistemas e ramal proprios de cada unidade.
"""

import random
import re

TOTAL = 500
UNIDADES_POR_CASO = (1, 5)
AUTORES_POR_UNIDADE = 3

# ACER-09: colaboradores, perfil USUARIO, sem senha. O e-mail nao aparece nas telas.
AUTORES = (
    ("Carla", "Mendes"),
    ("Rafael", "Teixeira"),
    ("Juliana", "Prado"),
    ("Marcos", "Albuquerque"),
    ("Patrícia", "Nogueira"),
    ("André", "Figueiredo"),
    ("Luciana", "Barros"),
    ("Thiago", "Moreira"),
    ("Fernanda", "Castilho"),
    ("Diego", "Siqueira"),
    ("Renata", "Lacerda"),
    ("Gustavo", "Pacheco"),
    ("Aline", "Rezende"),
    ("Eduardo", "Campos"),
    ("Simone", "Vasconcelos"),
)
DOMINIO_DOS_AUTORES = "acervo.invalid"

# Valores que variam de unidade para unidade dentro do mesmo caso.
ERPS = ("TOTVS Protheus", "SAP Business One", "Senior", "Sankhya", "Oracle NetSuite")
# Sem artigo. FERRAMENTAS entram depois de "por" e "com" (o que executa);
# PLATAFORMAS, depois de "em" (onde fica publicado ou registrado).
# Ao menos 5 em cada: um caso pode ocupar 5 unidades e a solucao tem de variar.
FERRAMENTAS = (
    "Power Automate",
    "Google Apps Script",
    "Zapier",
    "n8n",
    "um script em Python",
)
PLATAFORMAS = (
    "SharePoint",
    "Microsoft 365",
    "Google Workspace",
    "Google Sheets",
    "Microsoft Teams",
)

# Resultado parcial de quem ainda esta "Em teste" (vazio em parte deles).
RESULTADOS_EM_TESTE = (
    "Piloto em andamento há {semanas} semanas; a equipe estima redução de {pct}% no tempo "
    "gasto, ainda sem medição formal.",
    "Primeiras {semanas} semanas de uso com boa adesão da equipe; os números serão "
    "consolidados no próximo fechamento.",
    "",
)

# (categoria, setor, titulo, problema, solucao, resultado). Os campos com {} sao
# preenchidos por unidade. Todo problema e toda solucao tem ao menos um campo variavel.
CASOS = (
    # Financeiro
    (
        "Financeiro",
        "Tesouraria",
        "Conciliação bancária automática",
        "A conciliação bancária era feita à mão, linha a linha, comparando o extrato com os "
        "lançamentos do {erp}. Com cerca de {qtd} movimentos por mês, o fechamento atrasava "
        "{dias} dias úteis.",
        "Importação diária dos extratos em OFX e regras de conciliação por valor, data e "
        "histórico, montadas com {ferramenta}. Só as divergências vão para análise manual.",
        "O fechamento passou a sair até o {dias_menor}º dia útil e {nivel}% dos movimentos são "
        "conciliados sem intervenção.",
    ),
    (
        "Financeiro",
        "Contabilidade",
        "Checklist compartilhado do fechamento contábil",
        "Cada analista seguia sua própria lista no fechamento mensal, e etapas eram "
        "esquecidas. A equipe de {pessoas} pessoas gastava cerca de {horas} horas por mês "
        "só em retrabalho.",
        "Checklist único com responsável, prazo e evidência de cada etapa, publicado em "
        "{ferramenta} e revisado no início de cada mês.",
        "As pendências no fechamento caíram {pct}% e o retrabalho ficou abaixo de "
        "{horas_menor} horas mensais.",
    ),
    (
        "Financeiro",
        "Contas a Pagar",
        "Aprovação eletrônica de pagamentos",
        "Os pagamentos dependiam de assinatura física do gestor. Cerca de {qtd} documentos por "
        "mês circulavam em pastas, e alguns venciam antes da aprovação.",
        "Fluxo de aprovação em {plataforma}, com alçada por valor e anexo da nota fiscal. O "
        "gestor aprova pelo celular e o {erp} recebe o status.",
        "O tempo médio de aprovação caiu de {dias} dias para menos de um, e os pagamentos com "
        "multa por atraso caíram {pct}%.",
    ),
    (
        "Financeiro",
        "Tesouraria",
        "Controle de adiantamentos para viagens",
        "Adiantamentos de viagem ficavam abertos por meses sem prestação de contas. Havia "
        "cerca de {qtd} adiantamentos por ano e nenhum controle de prazo.",
        "Planilha de controle com alerta automático {dias} dias após o retorno da viagem, "
        "integrada ao cadastro de colaboradores do {erp}.",
        "Adiantamentos em aberto há mais de 30 dias caíram {pct}%.",
    ),
    (
        "Financeiro",
        "Contas a Pagar",
        "Prestação de contas do cartão corporativo",
        "A fatura do cartão corporativo chegava sem os comprovantes, e a conferência de cerca "
        "de {qtd} transações por mês tomava {horas} horas da equipe.",
        "Cada portador anexa o comprovante num formulário em até {dias} dias; {ferramenta} "
        "cruza com a fatura e aponta as transações sem comprovante.",
        "A conferência caiu para cerca de {horas_menor} horas mensais e {nivel}% das transações "
        "chegam com comprovante no prazo.",
    ),
    (
        "Financeiro",
        "Contas a Receber",
        "Conciliação das vendas no cartão de crédito",
        "Os recebíveis de cartão eram conciliados com o relatório da adquirente em planilhas "
        "separadas. Taxas cobradas a mais passavam despercebidas em cerca de {qtd} "
        "transações mensais.",
        "Conciliação diária entre o arquivo da adquirente e o {erp}, com {ferramenta} "
        "destacando taxas fora do contrato.",
        "Foram recuperados valores cobrados a mais em {meses} meses seguidos, e a conferência "
        "ficou {pct}% mais rápida.",
    ),
    (
        "Financeiro",
        "Tesouraria",
        "Previsão semanal de fluxo de caixa",
        "O fluxo de caixa era montado só no fim do mês, a partir de {qtd} lançamentos "
        "exportados do {erp}, e não antecipava semanas de caixa apertado.",
        "Previsão semanal alimentada pelos títulos a pagar e a receber, com cenários "
        "atualizados por {ferramenta} toda segunda-feira.",
        "A diretoria passou a decidir antecipações com {dias} dias de folga, e o uso de "
        "cheque especial caiu {pct}%.",
    ),
    (
        "Financeiro",
        "Contas a Receber",
        "Régua de cobrança automática",
        "A cobrança de títulos vencidos dependia de ligações manuais. Cerca de {qtd} títulos "
        "por mês ficavam sem contato nos primeiros {dias} dias de atraso.",
        "Régua com lembretes por e-mail antes e depois do vencimento, disparados por "
        "{ferramenta} a partir dos títulos abertos no {erp}.",
        "A inadimplência acima de 30 dias caiu {pct}% e a equipe liga só para os casos que "
        "não responderam.",
    ),
    (
        "Financeiro",
        "Faturamento",
        "Emissão de notas de serviço em lote",
        "As notas fiscais de serviço eram emitidas uma a uma no portal da prefeitura. Com "
        "cerca de {qtd} notas por mês, a emissão ocupava {horas} horas.",
        "Geração do arquivo de lote a partir do {erp} e envio único ao portal, com conferência "
        "por {ferramenta}.",
        "A emissão mensal caiu para menos de {horas_menor} horas e os erros de digitação "
        "deixaram de acontecer.",
    ),
    (
        "Financeiro",
        "Controladoria",
        "Rateio de despesas entre centros de custo",
        "Despesas compartilhadas, como energia e aluguel, eram rateadas por percentuais "
        "antigos. O ajuste manual de {qtd} lançamentos por mês gerava contestação dos "
        "gestores.",
        "Critérios de rateio revisados com os gestores e aplicados por {ferramenta} antes da "
        "integração com o {erp}.",
        "As contestações de rateio caíram {pct}% e o lançamento passou a levar {horas_menor} "
        "horas.",
    ),
    (
        "Financeiro",
        "Controladoria",
        "Controle de contratos e reajustes",
        "Os reajustes de cerca de {poucos} contratos eram lembrados só quando o fornecedor "
        "cobrava. Índices eram aplicados com atraso de até {dias} semanas.",
        "Cadastro único dos contratos com data-base e índice, e alerta automático em "
        "{ferramenta} 30 dias antes de cada reajuste.",
        "Nenhum reajuste foi aplicado fora de prazo em {meses} meses.",
    ),
    (
        "Financeiro",
        "Controladoria",
        "Painel de orçamento por centro de custo",
        "Os gestores recebiam o realizado do orçamento em planilhas enviadas por e-mail, "
        "{dias} dias depois do fechamento, e não conseguiam corrigir o rumo a tempo.",
        "Painel em Power BI com orçado e realizado por centro de custo, atualizado "
        "diariamente a partir do {erp}, para cerca de {pessoas} gestores.",
        "Os pedidos de relatório avulso caíram {pct}% e os desvios passaram a ser discutidos "
        "no próprio mês.",
    ),
    (
        "Financeiro",
        "Contas a Receber",
        "Baixa automática de boletos recebidos",
        "A baixa dos boletos pagos era digitada a partir do extrato. Cerca de {qtd} boletos "
        "por mês eram baixados à mão, com erros de valor e de data.",
        "Leitura do arquivo de retorno do banco e baixa automática no {erp}; {ferramenta} "
        "lista o que não encontrou título correspondente.",
        "{nivel}% dos boletos passaram a ser baixados sem digitação.",
    ),
    (
        "Financeiro",
        "Fiscal",
        "Validação de notas fiscais de entrada",
        "Notas de entrada com CFOP ou alíquota errada só eram percebidas na apuração. Cerca "
        "de {qtd} notas por mês passavam sem conferência fiscal.",
        "Validação do XML na chegada, com regras por fornecedor e por produto, e devolução "
        "automática ao comprador quando há divergência, via {ferramenta}.",
        "Os ajustes na apuração mensal caíram {pct}%.",
    ),
    (
        "Financeiro",
        "Contas a Pagar",
        "Reembolso de despesas pelo celular",
        "Pedidos de reembolso chegavam em papel, com comprovantes soltos. Cerca de {qtd} "
        "pedidos por mês levavam {dias} dias para serem pagos.",
        "Formulário no celular com foto do comprovante e aprovação do gestor em "
        "{ferramenta}; o lote aprovado segue para pagamento semanal.",
        "O prazo de reembolso caiu para uma semana e o papel deixou de circular.",
    ),
    (
        "Financeiro",
        "Fiscal",
        "Calendário fiscal com alertas",
        "As obrigações acessórias eram acompanhadas pela memória de {pessoas} pessoas. Em um "
        "ano houve {multas} entregas fora do prazo, com multa.",
        "Calendário com todas as obrigações, responsável e alerta {dias} dias antes do prazo, "
        "mantido em {plataforma}.",
        "Nenhuma obrigação foi entregue com atraso em {meses} meses.",
    ),
    (
        "Financeiro",
        "Tesouraria",
        "Controle do fundo fixo de caixa",
        "O fundo fixo de caixa da unidade era reposto sem conferência dos vales. Cerca de "
        "{qtd} vales por mês ficavam sem comprovante.",
        "Reposição só com a planilha de vales conferida e assinada; {ferramenta} soma os "
        "comprovantes e aponta diferenças.",
        "As diferenças de caixa caíram {pct}% e a reposição passou a ser quinzenal.",
    ),
    (
        "Financeiro",
        "Fiscal",
        "Conferência das retenções de impostos",
        "As retenções de ISS, INSS e IR em notas de serviço eram calculadas à mão. Em {qtd} "
        "notas por mês, erros geravam recolhimento complementar.",
        "Tabela de retenções por tipo de serviço e município aplicada por {ferramenta} antes "
        "do lançamento no {erp}.",
        "Os recolhimentos complementares caíram {pct}%.",
    ),
    (
        "Financeiro",
        "Contabilidade",
        "Arquivo digital de comprovantes",
        "Os comprovantes contábeis ficavam em caixas físicas. Localizar um documento para a "
        "auditoria levava em média {horas_curtas} horas.",
        "Digitalização na entrada, com nome padronizado por data, fornecedor e número do "
        "lançamento no {erp}; {ferramenta} organiza as pastas.",
        "Qualquer comprovante é localizado em minutos, e {pct}% do arquivo físico foi "
        "descartado conforme a tabela de temporalidade.",
    ),
    (
        "Financeiro",
        "Contabilidade",
        "Inventário do imobilizado com etiquetas",
        "O controle patrimonial de cerca de {qtd} bens não batia com a contabilidade, e "
        "ninguém sabia onde estavam itens baixados.",
        "Etiquetas com código de barras e inventário anual com leitura pelo celular, "
        "conciliado com o {erp} por {ferramenta}.",
        "A diferença entre o físico e o contábil caiu {pct}% no primeiro inventário.",
    ),
    (
        "Financeiro",
        "Controladoria",
        "Apuração de comissões",
        "As comissões de {pessoas} representantes eram apuradas em planilhas diferentes, e "
        "cada fechamento gerava contestação. A apuração levava {horas} horas.",
        "Regra de comissão única, calculada por {ferramenta} a partir do faturamento e do "
        "recebido no {erp}, com extrato para cada representante.",
        "As contestações caíram {pct}% e a apuração cabe em {horas_menor} horas.",
    ),
    (
        "Financeiro",
        "Contas a Receber",
        "Conciliação do contas a receber",
        "O saldo do contas a receber no {erp} não batia com o razão contábil, e a diferença "
        "era investigada todo mês em cerca de {qtd} títulos.",
        "Conciliação automática entre o relatório de títulos e o razão, com {ferramenta} "
        "agrupando as diferenças por causa.",
        "A diferença mensal foi zerada em {meses} meses.",
    ),
    (
        "Financeiro",
        "Contas a Pagar",
        "Agenda única de pagamentos",
        "Cada setor mandava pagamentos urgentes por e-mail, fora da programação. Cerca de "
        "{qtd} pagamentos por mês furavam a agenda.",
        "Dois dias fixos de pagamento por semana e agenda consolidada em {plataforma}; "
        "urgências só com justificativa aprovada.",
        "Os pagamentos fora da agenda caíram {pct}% e as tarifas de TED avulsa também.",
    ),
    (
        "Financeiro",
        "Controladoria",
        "Controle de seguros e garantias",
        "Apólices de seguro e garantias contratuais de cerca de {poucos} itens venciam sem "
        "renovação, e só se percebia no sinistro.",
        "Cadastro das apólices com vigência e cobertura, e aviso automático em {plataforma} "
        "{dias} semanas antes do vencimento.",
        "Nenhuma apólice venceu sem renovação desde a implantação.",
    ),
    (
        "Financeiro",
        "Controladoria",
        "Análise mensal de variação orçamentária",
        "Os desvios do orçamento eram explicados só na reunião anual. Cerca de {poucos} contas "
        "tinham variação acima de 10% sem justificativa.",
        "Relatório mensal em {plataforma} que destaca as contas fora da tolerância e pede "
        "justificativa ao gestor em até {dias} dias.",
        "{nivel}% dos desvios passaram a ter justificativa registrada no próprio mês.",
    ),
    # RH
    (
        "RH",
        "Departamento Pessoal",
        "Admissão digital",
        "A admissão exigia que o candidato trouxesse cópias de cerca de {docs} documentos. O "
        "processo levava {dias} dias e travava o registro no eSocial.",
        "Formulário de admissão em {plataforma} com envio das fotos dos documentos e "
        "checklist automático do que falta.",
        "O prazo de admissão caiu para {dias_menor} dias e nenhum registro foi enviado fora "
        "do prazo legal.",
    ),
    (
        "RH",
        "Desenvolvimento Humano",
        "Trilha de integração de novos colaboradores",
        "Os novos colaboradores passavam a primeira semana sem saber a quem procurar. Cerca "
        "de {poucos} admissões por ano dependiam da boa vontade de cada gestor.",
        "Trilha de integração com agenda dos primeiros {dias} dias, padrinho definido e "
        "vídeos curtos dos setores, organizada em {plataforma}.",
        "A satisfação com a integração subiu para {nivel}% e os desligamentos nos primeiros "
        "90 dias diminuíram.",
    ),
    (
        "RH",
        "Departamento Pessoal",
        "Planejamento anual de férias",
        "As férias eram marcadas em cima da hora, e {poucos} colaboradores chegaram perto do "
        "limite do período concessivo no mesmo ano.",
        "Planejamento anual por setor em {plataforma}, com alerta ao gestor {dias} meses "
        "antes do vencimento do período.",
        "Nenhum período de férias venceu sem gozo e os setores deixaram de ficar descobertos.",
    ),
    (
        "RH",
        "Departamento Pessoal",
        "Banco de horas com alerta ao gestor",
        "O saldo do banco de horas só era visto no fechamento. Cerca de {poucos} colaboradores "
        "acumulavam mais de {horas} horas sem compensação.",
        "Relatório semanal do saldo por equipe enviado ao gestor por {ferramenta}, com "
        "destaque para quem passa do limite acordado.",
        "Os saldos acima do limite caíram {pct}%.",
    ),
    (
        "RH",
        "Departamento Pessoal",
        "Conferência da folha antes do fechamento",
        "Erros na folha de cerca de {qtd} colaboradores só eram percebidos depois do "
        "pagamento, e cada correção exigia folha complementar.",
        "Comparação automática com a folha anterior em {plataforma}, destacando variações "
        "acima de {pct}% por evento, antes do fechamento no {erp}.",
        "As folhas complementares por erro caíram de {multas} para uma no ano.",
    ),
    (
        "RH",
        "Desenvolvimento Humano",
        "Avaliação de desempenho em formulário único",
        "Cada setor avaliava seus {qtd} colaboradores num modelo diferente, e não havia "
        "como comparar resultados nem acompanhar planos de melhoria.",
        "Formulário único de avaliação em {plataforma}, com etapa de autoavaliação e "
        "reunião de retorno registrada.",
        "{nivel}% das avaliações foram concluídas no prazo no primeiro ciclo.",
    ),
    (
        "RH",
        "Departamento Pessoal",
        "Checklist de desligamento entre setores",
        "No desligamento, equipamentos, acessos e crachás eram recolhidos de forma "
        "desencontrada. Em {poucos} desligamentos por ano, sempre faltava algo.",
        "Checklist com TI, patrimônio, financeiro e gestor, disparado por {ferramenta} no "
        "registro do aviso, com prazo de {dias} dias.",
        "Nenhum acesso ficou ativo após o desligamento desde a implantação.",
    ),
    (
        "RH",
        "Desenvolvimento Humano",
        "Pesquisa de clima trimestral",
        "A pesquisa de clima era anual e em papel. Com {qtd} colaboradores, a tabulação "
        "levava {semanas} semanas e os resultados chegavam velhos.",
        "Pesquisa curta trimestral em {plataforma}, anônima, com painel por setor liberado "
        "aos gestores.",
        "A participação subiu para {nivel}% e cada setor passou a ter um plano de ação.",
    ),
    (
        "RH",
        "Saúde Ocupacional",
        "Gestão de atestados médicos",
        "Atestados chegavam por foto no celular do gestor e se perdiam. Cerca de {poucos} "
        "atestados por mês eram lançados com atraso na folha.",
        "Canal único de envio em {plataforma}, com registro automático e aviso ao "
        "Departamento Pessoal em até {dias} dias.",
        "Os lançamentos fora do mês de competência caíram {pct}%.",
    ),
    (
        "RH",
        "Departamento Pessoal",
        "Escala de plantões compartilhada",
        "A escala de plantões de {pessoas} equipes era feita em papel no quadro do setor, e "
        "trocas não eram registradas. Isso gerou {multas} pagamentos de hora extra errados.",
        "Escala publicada em {plataforma}, com troca solicitada e aprovada pelo próprio "
        "sistema e exportação para a folha.",
        "Os ajustes de hora extra por escala errada deixaram de acontecer.",
    ),
    (
        "RH",
        "Saúde Ocupacional",
        "Controle de treinamentos obrigatórios",
        "Os treinamentos obrigatórios de segurança de cerca de {qtd} colaboradores venciam "
        "sem reciclagem, e a fiscalização encontrou pendências.",
        "Matriz de treinamentos por função com vencimento e aviso {dias} semanas antes, "
        "mantida em {plataforma}.",
        "{nivel}% dos colaboradores ficaram com os treinamentos em dia.",
    ),
    (
        "RH",
        "Recrutamento e Seleção",
        "Triagem de candidatos por formulário",
        "Cada vaga recebia cerca de {poucos} currículos por e-mail, lidos um a um. A triagem "
        "tomava {horas} horas por vaga.",
        "Formulário de candidatura com perguntas eliminatórias em {plataforma}; o "
        "recrutador recebe só quem atende aos requisitos.",
        "A triagem caiu para cerca de {horas_menor} horas por vaga.",
    ),
    (
        "RH",
        "Departamento Pessoal",
        "Adesão ao vale-transporte pelo formulário",
        "A adesão e as mudanças no vale-transporte eram feitas em papel. Cerca de {poucos} "
        "pedidos por mês chegavam depois do corte da compra.",
        "Formulário com prazo de corte visível e confirmação automática, em {plataforma}, "
        "integrado à planilha de compra.",
        "Os pedidos fora do prazo caíram {pct}%.",
    ),
    (
        "RH",
        "Departamento Pessoal",
        "Controle dos contratos de experiência",
        "O fim dos contratos de experiência era lembrado em cima da hora. Em {multas} casos "
        "no ano, o contrato virou indeterminado sem avaliação do gestor.",
        "Alerta ao gestor {dias} dias antes do fim de cada período, com formulário de "
        "decisão em {plataforma}.",
        "Todas as experiências passaram a ter decisão registrada antes do prazo.",
    ),
    (
        "RH",
        "Departamento Pessoal",
        "Holerite pelo portal",
        "Os holerites de cerca de {qtd} colaboradores eram impressos e entregues em "
        "envelope, com custo de papel e {horas} horas de trabalho por mês.",
        "Publicação mensal no portal do colaborador do {erp}, com aviso por e-mail e "
        "assinatura de ciência eletrônica.",
        "A impressão foi eliminada e as dúvidas sobre holerite caíram {pct}%.",
    ),
    (
        "RH",
        "Desenvolvimento Humano",
        "Entrevista de desligamento estruturada",
        "As entrevistas de desligamento eram informais e nada era registrado. Em {poucos} "
        "saídas por ano, os motivos se perdiam.",
        "Roteiro padrão de entrevista com registro em {plataforma} e relatório trimestral "
        "dos motivos por setor.",
        "Os três principais motivos de saída foram identificados e dois setores mudaram "
        "suas práticas.",
    ),
    (
        "RH",
        "Recrutamento e Seleção",
        "Controle de estágios",
        "Os {pessoas} contratos de estágio venciam sem renovação ou desligamento formal, e "
        "relatórios para a instituição de ensino atrasavam.",
        "Cadastro dos estágios com vencimento, supervisor e relatórios pendentes, com "
        "alertas por {ferramenta}.",
        "Nenhum estágio ficou com contrato vencido em {meses} meses.",
    ),
    (
        "RH",
        "Saúde Ocupacional",
        "Agenda automática de exames periódicos",
        "Os exames periódicos de {qtd} colaboradores eram agendados quando o atestado "
        "vencia, e alguns trabalharam com ASO vencido.",
        "Lista mensal dos exames a vencer em {dias} semanas, gerada por {ferramenta} e "
        "enviada à clínica conveniada.",
        "{nivel}% dos exames passaram a ser feitos antes do vencimento.",
    ),
    (
        "RH",
        "Saúde Ocupacional",
        "Controle de entrega de EPIs",
        "A entrega de equipamentos de proteção a cerca de {qtd} colaboradores era anotada "
        "em fichas de papel, difíceis de achar na fiscalização.",
        "Ficha digital de EPI com assinatura no tablet e validade de cada item, mantida em "
        "{ferramenta}.",
        "As fichas passaram a ser localizadas em segundos e a troca por validade ficou "
        "{pct}% mais pontual.",
    ),
    (
        "RH",
        "Desenvolvimento Humano",
        "Mapa de sucessão das funções-chave",
        "Quando alguém de função-chave saía, ninguém estava preparado. Das {pessoas} funções "
        "críticas, nenhuma tinha sucessor indicado.",
        "Mapa de sucessão revisado a cada semestre em {plataforma}, com plano de "
        "desenvolvimento para cada sucessor.",
        "{nivel}% das funções críticas passaram a ter ao menos um sucessor preparado.",
    ),
    (
        "RH",
        "Comunicação Interna",
        "Central única de comunicados",
        "Comunicados do RH saíam por e-mail, mural e grupos de mensagem, e {pct}% dos "
        "colaboradores diziam não ficar sabendo das mudanças.",
        "Central de comunicados em {plataforma} com confirmação de leitura para avisos "
        "obrigatórios e resumo semanal.",
        "A confirmação de leitura dos avisos obrigatórios passou de {pct_menor}% para mais de 90%.",
    ),
    (
        "RH",
        "Departamento Pessoal",
        "Solicitação de declarações pelo autoatendimento",
        "Declarações de vínculo e de rendimentos eram pedidas no balcão do RH. Cerca de "
        "{poucos} pedidos por mês levavam {dias} dias para ficar prontos.",
        "Modelos padronizados gerados por {ferramenta} a partir do cadastro do {erp}, com "
        "assinatura eletrônica.",
        "As declarações saem no mesmo dia e o balcão foi liberado para outros atendimentos.",
    ),
    (
        "RH",
        "Departamento Pessoal",
        "Tratamento das inconsistências do ponto",
        "As marcações de ponto incompletas de cerca de {qtd} colaboradores eram tratadas no "
        "último dia do fechamento, em mutirão.",
        "Relatório diário das inconsistências enviado a cada gestor por {ferramenta}, com "
        "prazo de {dias} dias para justificar.",
        "O mutirão de fechamento acabou e as inconsistências pendentes caíram {pct}%.",
    ),
    (
        "RH",
        "Desenvolvimento Humano",
        "Programa de reconhecimento entre colegas",
        "Não havia forma de reconhecer boas práticas no dia a dia, e a pesquisa de clima "
        "apontava valorização como o item mais baixo, com {pct}% de satisfação.",
        "Mural de reconhecimento em {plataforma}, com destaque mensal escolhido pelos "
        "próprios colegas entre cerca de {poucos} indicações.",
        "O item de valorização na pesquisa de clima subiu {pts} pontos.",
    ),
    # Compras
    (
        "Compras",
        "Suprimentos",
        "Cotação padronizada com três fornecedores",
        "Cada comprador montava a cotação do seu jeito, e a auditoria não conseguia "
        "comparar propostas em cerca de {qtd} compras por ano.",
        "Modelo único de mapa de cotação em {plataforma}, com no mínimo três propostas e "
        "justificativa da escolha.",
        "As compras auditadas sem pendência passaram a {nivel}%.",
    ),
    (
        "Compras",
        "Suprimentos",
        "Cadastro de fornecedores com validação de documentos",
        "Fornecedores eram cadastrados no {erp} sem conferir CNPJ, certidões e dados "
        "bancários. Houve {multas} pagamentos devolvidos por conta errada no ano.",
        "Formulário de cadastro com consulta automática do CNPJ e anexos obrigatórios, "
        "validado por {ferramenta} antes da liberação.",
        "Os pagamentos devolvidos por cadastro errado deixaram de acontecer.",
    ),
    (
        "Compras",
        "Suprimentos",
        "Requisição de compras por formulário",
        "As requisições chegavam por e-mail, telefone e corredor. Cerca de {qtd} pedidos "
        "por mês ficavam sem registro de quem pediu e quando.",
        "Formulário único de requisição em {plataforma}, com centro de custo, justificativa e "
        "acompanhamento do status pelo solicitante.",
        "As cobranças sobre andamento de pedidos caíram {pct}%.",
    ),
    (
        "Compras",
        "Suprimentos",
        "Catálogo de itens de compra recorrente",
        "Itens comprados todo mês eram cotados do zero a cada pedido. Cerca de {qtd} "
        "requisições por ano repetiam os mesmos produtos.",
        "Catálogo com especificação, fornecedor homologado e preço negociado, publicado em "
        "{ferramenta}.",
        "O prazo de compra dos itens do catálogo caiu para {dias} dias e o preço médio "
        "caiu {economia}%.",
    ),
    (
        "Compras",
        "Suprimentos",
        "Acompanhamento de pedidos em atraso",
        "Atrasos de entrega só eram percebidos quando o solicitante reclamava. Cerca de "
        "{qtd} pedidos por mês passavam da data prometida.",
        "Lista diária dos pedidos com entrega vencida, gerada do {erp} por {ferramenta}, "
        "com cobrança ao fornecedor no mesmo dia.",
        "Os atrasos acima de {dias} dias caíram {pct}%.",
    ),
    (
        "Compras",
        "Suprimentos",
        "Avaliação periódica de fornecedores",
        "Não havia histórico de desempenho dos fornecedores, e problemas de entrega se "
        "repetiam com os mesmos {pessoas} parceiros.",
        "Avaliação trimestral de prazo, qualidade e atendimento em {plataforma}, com nota "
        "usada como critério nas próximas cotações.",
        "Dois fornecedores com nota baixa foram substituídos e as não conformidades caíram {pct}%.",
    ),
    (
        "Compras",
        "Almoxarifado",
        "Compra consolidada de material de escritório",
        "Cada setor comprava material de escritório separadamente. Eram cerca de {qtd} "
        "pedidos pequenos por ano, com frete em quase todos.",
        "Pedido mensal consolidado, com janela de solicitação de {dias} dias organizada em "
        "{ferramenta}.",
        "O gasto com frete caiu {economia}% e o número de pedidos caiu para doze por ano.",
    ),
    (
        "Compras",
        "Contratos",
        "Gestão dos contratos de serviços terceirizados",
        "Os {pessoas} contratos de serviços terceirizados não tinham fiscal designado, e "
        "medições eram pagas sem conferência.",
        "Fiscal nomeado por contrato e checklist mensal de medição em {plataforma} antes da "
        "liberação do pagamento no {erp}.",
        "Glosas por serviço não prestado passaram a ser aplicadas, com economia de {economia}% em "
        "dois contratos.",
    ),
    (
        "Compras",
        "Almoxarifado",
        "Recebimento com leitura de código de barras",
        "A conferência do recebimento de cerca de {qtd} itens por mês era feita no olho, "
        "contra a nota impressa.",
        "Leitura do código de barras no recebimento, comparada ao pedido de compra no {erp} "
        "por {ferramenta}.",
        "As divergências descobertas depois do recebimento caíram {pct}%.",
    ),
    (
        "Compras",
        "Almoxarifado",
        "Estoque mínimo com reposição automática",
        "Itens básicos faltavam no almoxarifado por falta de controle. Em um ano houve "
        "{multas} rupturas de itens de uso diário.",
        "Estoque mínimo definido para cerca de {qtd} itens, com sugestão de compra gerada "
        "por {ferramenta} a partir do saldo do {erp}.",
        "As rupturas caíram {pct}% e o estoque parado também diminuiu.",
    ),
    (
        "Compras",
        "Suprimentos",
        "Aprovação de compras por alçada",
        "Toda compra, de qualquer valor, passava pela diretoria. Cerca de {qtd} aprovações "
        "por mês ficavam paradas {dias} dias.",
        "Tabela de alçadas por valor e tipo de despesa, aplicada no fluxo de aprovação em "
        "{ferramenta}.",
        "{nivel}% das compras passaram a ser aprovadas pelo próprio gestor no mesmo dia.",
    ),
    (
        "Compras",
        "Suprimentos",
        "Histórico de preços por item",
        "Os compradores não sabiam quanto se pagou da última vez. Em cerca de {qtd} "
        "compras por ano, aumentos passavam sem negociação.",
        "Histórico de preços extraído do {erp} e consultado por {ferramenta} em toda nova "
        "cotação, com alerta para alta acima de {economia}%.",
        "Os aumentos acima da inflação passaram a ser negociados em todos os casos.",
    ),
    (
        "Compras",
        "Suprimentos",
        "Registro das compras emergenciais",
        "Compras emergenciais eram feitas sem registro e justificadas depois. Cerca de "
        "{poucos} por ano não tinham cotação nem aprovação.",
        "Formulário rápido de compra emergencial com justificativa e aprovação posterior "
        "em até {dias} dias, em {plataforma}.",
        "As emergenciais caíram {pct}% quando os setores passaram a ver o próprio volume.",
    ),
    (
        "Compras",
        "Almoxarifado",
        "Inventário rotativo do almoxarifado",
        "O inventário anual fechava o almoxarifado por {dias} dias e ainda assim terminava "
        "com diferenças em cerca de {qtd} itens.",
        "Contagem semanal de um grupo de itens, sorteado por {ferramenta}, com ajuste no "
        "{erp} no mesmo dia.",
        "O almoxarifado deixou de fechar para inventário e a acuracidade passou de "
        "{pct_menor}% para mais de 95%.",
    ),
    (
        "Compras",
        "Frota",
        "Controle de abastecimento da frota",
        "Os abastecimentos de {pessoas} veículos eram pagos por nota avulsa, sem relação "
        "com quilometragem. O consumo médio era desconhecido.",
        "Cartão de abastecimento por veículo e registro da quilometragem em {plataforma}, "
        "com alerta de consumo fora do padrão.",
        "O gasto com combustível caiu {economia}% em {meses} meses.",
    ),
    (
        "Compras",
        "Manutenção Predial",
        "Chamados de manutenção predial terceirizada",
        "Os pedidos à empresa de manutenção eram feitos por telefone. Cerca de {qtd} "
        "serviços por mês não tinham prazo nem registro de conclusão.",
        "Abertura de chamado em {plataforma}, com prazo por prioridade e foto do serviço "
        "concluído antes da medição.",
        "{nivel}% dos chamados passaram a ser atendidos dentro do prazo do contrato.",
    ),
    (
        "Compras",
        "Contratos",
        "Calendário de renovação de contratos",
        "Contratos de fornecimento renovavam automaticamente sem renegociação. Dos cerca de "
        "{poucos} contratos ativos, poucos eram revistos.",
        "Calendário com aviso {dias} meses antes de cada renovação e reunião de "
        "renegociação registrada em {plataforma}.",
        "As renegociações renderam redução média de {economia}% nos contratos revistos.",
    ),
    (
        "Compras",
        "Almoxarifado",
        "Devolução de mercadorias a fornecedores",
        "Mercadorias com defeito ficavam paradas no almoxarifado esperando devolução. "
        "Cerca de {poucos} itens por ano viravam perda.",
        "Fluxo de devolução com prazo de {dias} dias, registro em {plataforma} e nota de "
        "devolução emitida pelo {erp}.",
        "As perdas por mercadoria não devolvida caíram {pct}%.",
    ),
    (
        "Compras",
        "Suprimentos",
        "Padronização das compras de equipamentos de TI",
        "Cada setor pedia um modelo de notebook diferente, e a TI mantinha {pessoas} "
        "configurações distintas, com {qtd} equipamentos no parque.",
        "Três perfis padrão de equipamento, definidos com a TI e cotados uma vez por "
        "semestre; o pedido é feito por {ferramenta}.",
        "O preço por equipamento caiu {economia}% e o suporte ficou mais simples.",
    ),
    (
        "Compras",
        "Suprimentos",
        "Negociação anual consolidada",
        "Itens comprados por várias unidades eram negociados separadamente. Cerca de {qtd} "
        "itens tinham preços diferentes entre unidades.",
        "Negociação anual única dos itens comuns, com tabela de preços publicada em "
        "{ferramenta} para todas as unidades.",
        "A economia média nos itens negociados foi de {economia}%.",
    ),
    (
        "Compras",
        "Viagens",
        "Central de reservas de viagens",
        "Passagens e hotéis eram comprados por cada colaborador, sem política. Cerca de "
        "{qtd} viagens por ano eram compradas com menos de {dias} dias de antecedência.",
        "Política de viagens com antecedência mínima e pedido único em {plataforma}, "
        "atendido pela central de reservas.",
        "O custo médio por viagem caiu {economia}%.",
    ),
    (
        "Compras",
        "Contratos",
        "Gestão das linhas de telefonia móvel",
        "Ninguém sabia quem usava cada uma das cerca de {qtd} linhas corporativas, e "
        "linhas de ex-colaboradores continuavam pagas.",
        "Inventário das linhas com responsável e conferência mensal da fatura em "
        "{ferramenta}, cruzando com o cadastro de ativos do {erp}.",
        "{multas} linhas sem uso foram canceladas e a fatura caiu {economia}%.",
    ),
    (
        "Compras",
        "Manutenção Predial",
        "Descarte de resíduos com controle",
        "Resíduos eletrônicos e lâmpadas eram acumulados sem destino certo. Cerca de {qtd} "
        "quilos ficavam parados por ano.",
        "Contrato com empresa licenciada e coleta trimestral agendada em {plataforma}, com "
        "certificado de destinação arquivado.",
        "Todo o resíduo passou a ter destinação comprovada.",
    ),
    (
        "Compras",
        "Contratos",
        "Indicadores no contrato de limpeza",
        "O contrato de limpeza era pago pelo valor cheio todo mês, mesmo com {poucos} "
        "reclamações registradas no período.",
        "Indicadores de qualidade no contrato, com vistoria semanal em {plataforma} e "
        "desconto proporcional na medição.",
        "As reclamações caíram {pct}% em {meses} meses.",
    ),
    # TI interno
    (
        "TI interno",
        "Suporte Técnico",
        "Central de chamados com categorias",
        "Os pedidos à TI chegavam por mensagem, telefone e corredor. Cerca de {qtd} "
        "atendimentos por mês não tinham registro nem prazo.",
        "Central de chamados com categorias, prioridade e prazo por tipo, implantada com "
        "{ferramenta}.",
        "{nivel}% dos chamados passaram a ser resolvidos dentro do prazo.",
    ),
    (
        "TI interno",
        "Suporte Técnico",
        "Base de conhecimento de soluções",
        "Os mesmos problemas eram resolvidos do zero por técnicos diferentes. Cerca de "
        "{qtd} chamados por mês eram repetidos.",
        "Base de conhecimento com passo a passo das soluções mais comuns, em {plataforma}, "
        "consultada antes de escalar o chamado.",
        "O tempo médio de solução caiu {pct}%.",
    ),
    (
        "TI interno",
        "Infraestrutura",
        "Inventário automático de equipamentos",
        "O inventário de cerca de {qtd} computadores era uma planilha desatualizada, e "
        "máquinas sumiam sem registro.",
        "Agente de inventário instalado nas máquinas e relatório semanal em {plataforma} "
        "com localização e responsável.",
        "O inventário passou a refletir {nivel}% do parque real.",
    ),
    (
        "TI interno",
        "Infraestrutura",
        "Controle de licenças de software",
        "As licenças de cerca de {poucos} softwares eram renovadas sem saber quantas estavam "
        "em uso. Parte era paga sem uso.",
        "Painel de licenças com uso real, vencimento e responsável, alimentado por {ferramenta}.",
        "{multas} licenças ociosas foram canceladas, com economia de {economia}% no contrato.",
    ),
    (
        "TI interno",
        "Suporte Técnico",
        "Redefinição de senha pelo próprio usuário",
        "Pedidos de troca de senha eram {pct}% dos chamados e paravam o colaborador até o "
        "atendimento, cerca de {qtd} por mês.",
        "Portal de redefinição com verificação em duas etapas, ligado ao diretório da "
        "empresa e divulgado aos {pessoas} setores com um passo a passo.",
        "Os chamados de senha caíram para menos de {pct_menor}% do total.",
    ),
    (
        "TI interno",
        "Infraestrutura",
        "Backup automatizado dos servidores locais",
        "O backup dos servidores da unidade dependia de alguém trocar o disco toda sexta. "
        "Em {meses} meses houve {multas} semanas sem cópia.",
        "Rotina automática diária com cópia externa, retenção de {semanas} semanas e "
        "relatório de sucesso por e-mail, verificada com uma restauração mensal.",
        "Nenhuma falha de backup ficou sem tratamento desde a implantação.",
    ),
    (
        "TI interno",
        "Sistemas",
        "Liberação de acessos para novos colaboradores",
        "Novos colaboradores esperavam {dias} dias por e-mail e acessos ao {erp}, e "
        "trabalhavam com o login de colegas.",
        "Pedido de acessos disparado pelo RH na admissão, com perfil por função e "
        "execução acompanhada em {plataforma}.",
        "Os acessos ficam prontos no primeiro dia em {nivel}% das admissões.",
    ),
    (
        "TI interno",
        "Sistemas",
        "Revogação de acessos no desligamento",
        "Contas de ex-colaboradores continuavam ativas no {erp} e no e-mail. A auditoria "
        "encontrou {multas} acessos indevidos.",
        "Bloqueio automático disparado pelo registro do desligamento, com relatório mensal "
        "de contas sem uso gerado por {ferramenta}.",
        "Nenhum acesso ativo de ex-colaborador foi encontrado na auditoria seguinte.",
    ),
    (
        "TI interno",
        "Suporte Técnico",
        "Monitoramento de impressoras e toner",
        "O toner acabava sem aviso nas cerca de {poucos} impressoras, e cada troca virava "
        "chamado urgente.",
        "Monitoramento do nível de toner pela rede com pedido automático de reposição "
        "quando o nível cai abaixo de {pct_menor}%.",
        "Os chamados urgentes de impressão caíram quase a zero.",
    ),
    (
        "TI interno",
        "Suporte Técnico",
        "Imagem padrão para notebooks",
        "Cada notebook novo levava {horas_curtas} horas para ser configurado à mão, e as máquinas "
        "ficavam diferentes entre si.",
        "Imagem padrão com sistema, antivírus e programas da empresa, aplicada pela rede "
        "em cerca de {minutos} minutos.",
        "A preparação de um notebook caiu para menos de uma hora.",
    ),
    (
        "TI interno",
        "Infraestrutura",
        "Migração dos ramais para telefonia IP",
        "A central telefônica antiga tinha manutenção cara e {poucos} ramais sem uso, e "
        "mudanças de ramal levavam {dias} dias.",
        "Telefonia IP com ramais no computador e no celular para {pessoas} setores, "
        "administrada pela própria equipe.",
        "A conta de telefonia caiu {economia}% e as mudanças de ramal são feitas no mesmo dia.",
    ),
    (
        "TI interno",
        "Infraestrutura",
        "Atualizações agendadas do sistema operacional",
        "As atualizações de segurança eram instaladas quando o usuário lembrava. Cerca de "
        "{qtd} máquinas estavam com meses de atraso.",
        "Política de atualização automática fora do horário de trabalho, com prazo de "
        "{dias} dias e relatório semanal das máquinas pendentes.",
        "{nivel}% das máquinas passaram a estar atualizadas em até {dias} dias.",
    ),
    (
        "TI interno",
        "Sistemas",
        "Relatórios automáticos do ERP",
        "Os setores pediam à TI os mesmos relatórios do {erp} toda semana. Eram cerca de "
        "{qtd} pedidos por mês.",
        "Relatórios agendados com envio automático por e-mail, configurados com {ferramenta}.",
        "Os pedidos de relatório à TI caíram {pct}%.",
    ),
    (
        "TI interno",
        "Sistemas",
        "Integração entre o ERP e a planilha de orçamento",
        "A planilha de orçamento era atualizada copiando dados do {erp}, cerca de {horas} "
        "horas por mês, com erros de colagem.",
        "Conexão direta da planilha com a base do {erp}, atualizada por {ferramenta}.",
        "A atualização passou a ser automática e os erros de colagem acabaram.",
    ),
    (
        "TI interno",
        "Suporte Técnico",
        "Empréstimo controlado de equipamentos",
        "Projetores, notebooks e câmeras emprestados não voltavam no prazo. Cerca de {poucos} "
        "empréstimos por mês não tinham registro.",
        "Reserva e retirada registradas em {plataforma}, com lembrete de devolução no dia "
        "anterior.",
        "As devoluções em atraso caíram {pct}%.",
    ),
    (
        "TI interno",
        "Infraestrutura",
        "Mapa da rede e dos pontos de acesso",
        "Ninguém sabia a que porta do switch cada ponto estava ligado. Um problema de rede "
        "levava {horas_curtas} horas para ser localizado.",
        "Mapeamento e etiquetagem de cerca de {qtd} pontos, com o mapa publicado em {plataforma}.",
        "O tempo para localizar falhas de rede caiu {pct}%.",
    ),
    (
        "TI interno",
        "Infraestrutura",
        "Controle de domínios e certificados digitais",
        "Domínios e certificados digitais venciam sem aviso. Em {meses} meses, {multas} "
        "serviços ficaram fora do ar por certificado vencido.",
        "Cadastro dos {poucos} domínios e certificados com vencimento e alerta {dias} semanas "
        "antes.",
        "Nenhum serviço ficou fora do ar por vencimento desde a implantação.",
    ),
    (
        "TI interno",
        "Segurança da Informação",
        "Treinamento contra golpes de phishing",
        "Em uma campanha interna, {pct}% dos colaboradores clicaram num link suspeito. "
        "Cerca de {qtd} pessoas nunca tinham recebido orientação.",
        "Treinamento curto em vídeo e simulações trimestrais, com resultado por setor "
        "acompanhado em {plataforma}.",
        "A taxa de clique nas simulações caiu para menos de {pct_menor}%.",
    ),
    (
        "TI interno",
        "Segurança da Informação",
        "Autenticação em dois fatores no e-mail",
        "Duas contas de e-mail foram invadidas em {meses} meses, e cerca de {qtd} usuários "
        "usavam senhas fracas.",
        "Autenticação em dois fatores obrigatória para todos, com implantação por setor "
        "ao longo de {semanas} semanas.",
        "Não houve nenhuma invasão de conta desde a implantação.",
    ),
    (
        "TI interno",
        "Infraestrutura",
        "Migração dos arquivos para a nuvem",
        "Os arquivos dos setores ficavam no servidor local, com cerca de {qtd} GB e acesso "
        "lento fora da unidade.",
        "Migração para o armazenamento em nuvem da empresa em {semanas} semanas, com "
        "permissões por setor e sincronização no computador.",
        "O acesso externo deixou de depender de VPN e o servidor local foi desligado.",
    ),
    (
        "TI interno",
        "Sistemas",
        "Painel de disponibilidade dos sistemas",
        "Quando um sistema caía, a TI ficava sabendo pelos usuários. Cerca de {poucos} "
        "chamados repetidos chegavam a cada queda.",
        "Painel de disponibilidade com verificação a cada minuto e aviso automático aos "
        "usuários, configurado com {ferramenta}.",
        "Os chamados durante quedas caíram {pct}%.",
    ),
    (
        "TI interno",
        "Sistemas",
        "Cadastro automático de usuários no diretório",
        "Cada novo usuário era criado à mão no diretório, no e-mail e no {erp}, em cerca "
        "de {horas_curtas} horas por admissão.",
        "Script de cadastro a partir da planilha do RH, executado por {ferramenta}.",
        "O cadastro passou a levar minutos e os erros de grafia acabaram.",
    ),
    (
        "TI interno",
        "Suporte Técnico",
        "Manutenção preventiva dos computadores",
        "Os cerca de {qtd} computadores só eram vistos quando quebravam, e muitos "
        "esquentavam por poeira.",
        "Checklist semestral de limpeza e verificação, agendado por setor em {plataforma}.",
        "Os chamados de falha de hardware caíram {pct}%.",
    ),
    (
        "TI interno",
        "Sistemas",
        "Registro de mudanças nos sistemas",
        "Alterações no {erp} eram feitas sem registro, e problemas apareciam sem saber o "
        "que tinha mudado. Houve {multas} incidentes assim em {meses} meses.",
        "Registro de toda mudança com responsável, data e plano de volta, aprovado em "
        "{ferramenta}.",
        "Os incidentes causados por mudança não registrada acabaram.",
    ),
    (
        "TI interno",
        "Suporte Técnico",
        "Assistente para dúvidas frequentes",
        "Perguntas simples, como configurar a impressora ou o e-mail no celular, eram "
        "{pct}% dos chamados, cerca de {qtd} por mês.",
        "Assistente no portal interno com respostas às dúvidas mais comuns, montado com "
        "{ferramenta}.",
        "As dúvidas simples na fila de chamados caíram para menos de {pct_menor}%.",
    ),
    # Atendimento interno
    (
        "Atendimento interno",
        "Serviços Administrativos",
        "Balcão único de solicitações administrativas",
        "O colaborador não sabia a que setor pedir cada coisa e rodava a unidade. Cerca de "
        "{qtd} pedidos por mês eram encaminhados ao lugar errado.",
        "Balcão único com cardápio de serviços e encaminhamento interno, registrado em "
        "{ferramenta}.",
        "Os pedidos encaminhados ao setor errado caíram {pct}%.",
    ),
    (
        "Atendimento interno",
        "Serviços Administrativos",
        "Agendamento de salas de reunião",
        "As {pessoas} salas de reunião eram reservadas num caderno na recepção, e havia "
        "reuniões duplicadas quase toda semana.",
        "Agenda das salas no calendário corporativo, com reserva pelo próprio "
        "colaborador e liberação automática se não houver confirmação em {minutos} minutos.",
        "Os conflitos de sala deixaram de acontecer.",
    ),
    (
        "Atendimento interno",
        "Protocolo",
        "Protocolo digital de documentos",
        "Documentos entre setores circulavam em papel com livro de protocolo. Cerca de "
        "{qtd} documentos por mês não tinham rastreio.",
        "Protocolo digital com número, remetente, destinatário e prazo, em {plataforma}.",
        "Qualquer documento é localizado em segundos e o prazo médio de tramitação caiu {pct}%.",
    ),
    (
        "Atendimento interno",
        "Recepção",
        "Cadastro de visitantes na recepção",
        "Os visitantes eram anotados à mão, e não se sabia quem estava no prédio. Eram "
        "cerca de {qtd} visitas por mês.",
        "Cadastro rápido em tablet com foto e aviso automático ao anfitrião por {ferramenta}.",
        "O tempo de espera na recepção caiu {pct}%.",
    ),
    (
        "Atendimento interno",
        "Protocolo",
        "Malote entre unidades com rastreio",
        "Documentos enviados por malote se perdiam entre as unidades. Cerca de {qtd} "
        "envios por mês não tinham comprovante de entrega.",
        "Lacre numerado, registro de envio e recebimento em {plataforma} e confirmação do "
        "destinatário.",
        "Nenhum documento foi extraviado em {meses} meses.",
    ),
    (
        "Atendimento interno",
        "Serviços Administrativos",
        "Pesquisa de satisfação dos atendimentos internos",
        "Os setores de apoio não sabiam como eram avaliados. Dos cerca de {qtd} "
        "atendimentos por mês, nenhum tinha retorno.",
        "Pesquisa de uma pergunta enviada ao fim de cada atendimento por {ferramenta}, com "
        "resultado mensal por setor.",
        "A satisfação média chegou a {nivel}% de avaliações positivas.",
    ),
    (
        "Atendimento interno",
        "Serviços Administrativos",
        "Guia de procedimentos internos",
        "Cada colaborador perguntava aos colegas como pedir férias, reembolso ou material. "
        "Cerca de {qtd} dúvidas por mês chegavam aos setores de apoio.",
        "Guia de procedimentos com passo a passo e formulários, publicado em {plataforma}.",
        "As dúvidas repetidas caíram {pct}%.",
    ),
    (
        "Atendimento interno",
        "Recepção",
        "Fila de atendimento por senha",
        "O atendimento presencial no balcão não tinha ordem, e quem chegava depois era "
        "atendido antes. Cerca de {qtd} pessoas por semana passavam pelo balcão.",
        "Senha com prioridade, painel de chamada e {pessoas} guichês com tempo de espera "
        "registrado.",
        "O tempo médio de espera caiu para {minutos} minutos.",
    ),
    (
        "Atendimento interno",
        "Serviços Administrativos",
        "Caixa de entrada única do atendimento ao colaborador",
        "Dúvidas de colaboradores chegavam no e-mail pessoal de {pessoas} analistas e "
        "ficavam sem resposta nas férias de cada um.",
        "Caixa compartilhada com etiquetas por assunto e prazo de resposta de {dias} dias, "
        "acompanhada em {plataforma}.",
        "{nivel}% das mensagens passaram a ser respondidas no prazo.",
    ),
    (
        "Atendimento interno",
        "Recepção",
        "Gestão de correspondências recebidas",
        "Correspondências e encomendas ficavam na recepção sem aviso. Cerca de {qtd} itens "
        "por mês eram retirados com dias de atraso.",
        "Registro na chegada e aviso automático ao destinatário por {ferramenta}.",
        "O tempo de retirada caiu para menos de um dia.",
    ),
    (
        "Atendimento interno",
        "Serviços Administrativos",
        "Quadro de controle de chaves",
        "As cerca de {poucos} chaves da unidade ficavam numa gaveta, e salas eram abertas sem "
        "registro.",
        "Quadro numerado com retirada registrada em {plataforma} e conferência no fim do "
        "expediente.",
        "Nenhuma chave foi perdida em {meses} meses.",
    ),
    (
        "Atendimento interno",
        "Frota",
        "Reserva dos veículos da unidade",
        "Os {pessoas} veículos eram reservados por telefone, e havia conflitos e carros "
        "parados sem uso.",
        "Agenda de reservas com checklist de saída e retorno em {plataforma}.",
        "A ocupação dos veículos subiu {pct}% e os conflitos de reserva acabaram.",
    ),
    (
        "Atendimento interno",
        "Manutenção Predial",
        "Solicitação de manutenção pelo celular",
        "Problemas como lâmpada queimada ou vazamento eram avisados de boca. Cerca de "
        "{qtd} pedidos por mês se perdiam.",
        "Formulário com foto e local do problema em {plataforma}, com prazo por prioridade.",
        "{nivel}% dos pedidos passaram a ser atendidos no prazo.",
    ),
    (
        "Atendimento interno",
        "Serviços Administrativos",
        "Controle das refeições do refeitório",
        "A quantidade de refeições era estimada todo dia, e sobravam cerca de {poucos} "
        "refeições por semana.",
        "Confirmação de presença até as {hora} horas em {plataforma}, enviada à cozinha "
        "com o total do dia.",
        "O desperdício de refeições caiu {pct}%.",
    ),
    (
        "Atendimento interno",
        "Serviços Administrativos",
        "Atendimento interno por aplicativo de mensagens",
        "Os colaboradores das unidades externas não conseguiam falar com o administrativo "
        "por telefone. Cerca de {qtd} ligações por mês não eram atendidas.",
        "Número corporativo de mensagens com respostas rápidas e registro de cada "
        "atendimento em {plataforma}.",
        "{nivel}% das mensagens são respondidas no mesmo dia.",
    ),
    (
        "Atendimento interno",
        "Serviços Administrativos",
        "Catálogo de serviços internos",
        "Ninguém sabia o que os setores de apoio ofereciam nem em quanto tempo. Cerca de "
        "{qtd} pedidos por mês vinham sem as informações necessárias.",
        "Catálogo com cada serviço, o que é preciso enviar e o prazo, publicado em {plataforma}.",
        "Os pedidos devolvidos por falta de informação caíram {pct}%.",
    ),
    (
        "Atendimento interno",
        "Serviços Administrativos",
        "Prazo de resposta para pedidos internos",
        "Pedidos entre setores ficavam sem resposta por semanas. Cerca de {qtd} pedidos por "
        "mês passavam de {dias} dias.",
        "Prazos de resposta acordados entre os setores e acompanhados em {plataforma}, com "
        "alerta antes do vencimento.",
        "{nivel}% dos pedidos passaram a ser respondidos no prazo.",
    ),
    (
        "Atendimento interno",
        "Comunicação Interna",
        "Organização de eventos internos",
        "Cada evento interno era organizado do zero, e itens como som e lanche faltavam. "
        "Havia cerca de {poucos} eventos por ano.",
        "Checklist padrão de eventos com responsáveis e prazos em {plataforma}.",
        "Os problemas de última hora caíram {pct}% e a montagem leva menos tempo.",
    ),
    (
        "Atendimento interno",
        "Recepção",
        "Registro de achados e perdidos",
        "Objetos esquecidos ficavam numa caixa na recepção sem registro. Cerca de {poucos} "
        "itens por mês não voltavam ao dono.",
        "Registro com foto em {plataforma} e aviso no mural digital da unidade.",
        "{nivel}% dos objetos passaram a ser devolvidos.",
    ),
    (
        "Atendimento interno",
        "Segurança Patrimonial",
        "Controle de crachás de acesso",
        "Crachás de ex-colaboradores e de visitantes continuavam liberados. Havia cerca de "
        "{poucos} crachás ativos a mais do que pessoas.",
        "Cadastro de crachás ligado à admissão e ao desligamento, com conferência mensal "
        "em {plataforma}.",
        "Os crachás ativos passaram a bater com o quadro de pessoal.",
    ),
    (
        "Atendimento interno",
        "Ouvidoria",
        "Canal de ouvidoria interna",
        "Reclamações e sugestões internas não tinham canal. Em pesquisa, {pct}% dos "
        "colaboradores disseram não ter onde falar.",
        "Canal de ouvidoria com opção anônima e prazo de resposta de {dias} dias, "
        "registrado em {plataforma}.",
        "Foram recebidas cerca de {poucos} manifestações no primeiro semestre, todas respondidas.",
    ),
    (
        "Atendimento interno",
        "Comunicação Interna",
        "Aviso de interrupções programadas",
        "Interrupções programadas de energia, água ou internet pegavam os setores de surpresa. "
        "Em {meses} meses, {multas} reuniões foram canceladas por isso.",
        "Aviso automático por e-mail e no mural digital {dias} dias antes de cada "
        "interrupção, enviado por {ferramenta}.",
        "Nenhuma atividade foi perdida por falta de aviso desde a implantação.",
    ),
    (
        "Atendimento interno",
        "Serviços Administrativos",
        "Guia de boas-vindas da unidade",
        "Colaboradores transferidos não sabiam onde ficava cada setor nem as regras locais. "
        "Cerca de {poucos} pessoas chegaram à unidade no último ano.",
        "Guia de boas-vindas com mapa, contatos e rotinas, publicado em {plataforma}.",
        "As dúvidas de recém-chegados na recepção caíram {pct}%.",
    ),
    (
        "Atendimento interno",
        "Serviços Administrativos",
        "Rodízio das vagas de estacionamento",
        "As {poucos} vagas do estacionamento eram ocupadas por ordem de chegada, e quem "
        "chegava cedo sempre ficava com elas.",
        "Rodízio semanal das vagas definido por {ferramenta}, com prioridade para gestantes "
        "e pessoas com deficiência.",
        "As reclamações sobre estacionamento caíram {pct}%.",
    ),
    (
        "Atendimento interno",
        "Protocolo",
        "Endereçamento do arquivo físico",
        "As cerca de {qtd} caixas do arquivo físico não tinham endereço, e achar uma pasta "
        "levava {horas_curtas} horas.",
        "Endereçamento por estante, prateleira e caixa, com índice pesquisável em {plataforma}.",
        "Qualquer caixa é encontrada em poucos minutos.",
    ),
)

_CAMPO = re.compile(r"\{(\w+)\}")


def _valores(rng):
    """Os campos variaveis de um registro: numeros, sistema e ferramenta proprios."""
    pct = rng.randint(18, 78)
    horas = rng.randint(8, 60)
    dias = rng.randint(3, 15)
    return {
        "qtd": rng.randrange(80, 1500, 10),
        "poucos": rng.randint(12, 90),
        "docs": rng.randint(8, 16),
        "horas": horas,
        "horas_menor": max(2, horas // rng.randint(3, 6)),
        "horas_curtas": rng.randint(2, 6),
        "dias": dias,
        "dias_menor": max(1, dias // 3),
        "pct": pct,
        "pct_menor": max(3, pct // rng.randint(3, 6)),
        "pts": rng.randint(8, 25),
        "pessoas": rng.randint(3, 12),
        "semanas": rng.randint(3, 10),
        "meses": rng.randint(6, 14),
        "multas": rng.randint(3, 11),
        "minutos": rng.randint(5, 20),
        "hora": rng.choice((9, 10)),
        "erp": rng.choice(ERPS),
        "ferramenta": rng.choice(FERRAMENTAS),
        "plataforma": rng.choice(PLATAFORMAS),
        "nivel": rng.randint(82, 98),
        "economia": rng.randint(6, 24),
    }


def _contagens():
    """Quantas unidades cada caso ocupa: 1 a 5, somando TOTAL. Deterministico."""
    rng = random.Random("acervo-contagens")
    minimo, maximo = UNIDADES_POR_CASO
    contagens = [rng.choice((2, 3, 4, 4, 5, 5)) for _ in CASOS]
    while sum(contagens) > TOTAL:
        i = rng.randrange(len(contagens))
        if contagens[i] > minimo:
            contagens[i] -= 1
    while sum(contagens) < TOTAL:
        i = rng.randrange(len(contagens))
        if contagens[i] < maximo:
            contagens[i] += 1
    return contagens


def _status(rng):
    return rng.choices(
        ("EM_TESTE", "VALIDADA", "DISPONIVEL_PARA_REPLICACAO"), weights=(30, 35, 35)
    )[0]


def username(nome, sobrenome):
    """carla.mendes; sem acento, para o login e o e-mail."""
    from inovacoes.busca import normalizar

    return f"{normalizar(nome)}.{normalizar(sobrenome)}"


def autores_da_unidade(indice_da_unidade):
    """Os AUTORES_POR_UNIDADE autores ligados a uma unidade, pelo indice dela."""
    inicio = indice_da_unidade * AUTORES_POR_UNIDADE
    return [AUTORES[(inicio + k) % len(AUTORES)] for k in range(AUTORES_POR_UNIDADE)]


def montar_registros(unidades):
    """Os TOTAL registros do acervo para as unidades dadas (nomes, na ordem do banco).

    Cada registro: titulo, unidade (indice), categoria (nome), status, problema,
    solucao, resultado, contato, autor (nome, sobrenome) e semente (para datas).
    Problemas e solucoes saem todos diferentes: em colisao, o registro e sorteado de
    novo com a proxima tentativa da mesma semente.
    """
    registros, problemas, solucoes = [], set(), set()
    for indice, (contagem, caso) in enumerate(zip(_contagens(), CASOS, strict=True)):
        categoria, setor, titulo, problema, solucao, resultado = caso
        escolhidas = random.Random(f"acervo-caso-{indice}").sample(range(len(unidades)), contagem)
        for u in sorted(escolhidas):
            for tentativa in range(50):
                semente = f"acervo-{indice}-{u}-{tentativa}"
                rng = random.Random(semente)
                valores = _valores(rng)
                texto_problema = problema.format(**valores)
                texto_solucao = solucao.format(**valores)
                if texto_problema not in problemas and texto_solucao not in solucoes:
                    break
            else:
                raise RuntimeError(f"sem variacao suficiente no caso {titulo!r}")
            problemas.add(texto_problema)
            solucoes.add(texto_solucao)
            status = _status(rng)
            if status == "EM_TESTE":
                texto_resultado = rng.choice(RESULTADOS_EM_TESTE).format(**valores)
            else:
                texto_resultado = resultado.format(**valores)
            registros.append(
                {
                    "titulo": titulo,
                    "unidade": u,
                    "categoria": categoria,
                    "status": status,
                    "problema": texto_problema,
                    "solucao": texto_solucao,
                    "resultado": texto_resultado,
                    "contato": f"{setor}, {unidades[u]} — ramal {rng.randint(2000, 7999)}",
                    "autor": rng.choice(autores_da_unidade(u)),
                    "semente": semente,
                }
            )
    return registros


# ACER-12: cadastros entre 20 e JANELA_EM_DIAS dias antes da execucao.
JANELA_EM_DIAS = 540
ESTAGIOS = ("EM_TESTE", "VALIDADA", "DISPONIVEL_PARA_REPLICACAO")


def linha_do_tempo(registro, agora, total_de_unidades):
    """Datas e reusos de um registro, relativos a `agora` (ACER-12 a ACER-16).

    Devolve criacao, as datas das mudancas de status ate o status do registro (uma
    por estagio avancado) e os reusos (indice da unidade, data, autor). Cada data
    cai entre a anterior e `agora`, entao a ordem nunca se inverte. Os
    deslocamentos saem da semente do registro: reproduziveis dado o mesmo `agora`.
    """
    from datetime import timedelta

    rng = random.Random(f"{registro['semente']}-tempo")
    criacao = agora - timedelta(days=rng.uniform(20, JANELA_EM_DIAS - 1))
    mudancas, anterior = [], criacao
    for _ in range(ESTAGIOS.index(registro["status"])):
        anterior = anterior + (agora - anterior) * rng.uniform(0.15, 0.5)
        mudancas.append(anterior)
    reusos = []
    if registro["status"] == ESTAGIOS[-1] and rng.random() < 0.5:
        outras = [u for u in range(total_de_unidades) if u != registro["unidade"]]
        for u in sorted(rng.sample(outras, min(len(outras), rng.randint(1, 3)))):
            data = anterior + (agora - anterior) * rng.uniform(0.1, 0.9)
            reusos.append((u, data, rng.choice(autores_da_unidade(u))))
    return {"criacao": criacao, "mudancas": mudancas, "reusos": reusos}


def _conferir_catalogo():
    """Guarda do catalogo: todo problema e toda solucao tem um campo variavel conhecido."""
    conhecidos = set(_valores(random.Random(0)))
    for caso in CASOS:
        for texto in caso[3:5]:
            campos = set(_CAMPO.findall(texto))
            if not campos:
                raise ValueError(f"texto sem campo variavel: {texto[:40]!r}")
        for texto in caso[3:6]:
            desconhecidos = set(_CAMPO.findall(texto)) - conhecidos
            if desconhecidos:
                raise ValueError(f"campos desconhecidos {desconhecidos} em {caso[2]!r}")


_conferir_catalogo()
