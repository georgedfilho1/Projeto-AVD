<!--
Textos da Parte Específica que entram no relatorio.pdf.
Tudo marcado com [A PREENCHER PELO GRUPO] deve ser escrito pelo grupo, sem IA
(regra do enunciado: análises, discussões, conclusões e notas analíticas são autorais).
As linhas {{...}} são substituídas automaticamente por tabelas e figuras.
Gere o PDF com: python src/relatorio/gerar_relatorio.py
-->

# Parte Específica · Bank Marketing

**Integrantes.** George Diógenes Pessoa Filho · João Cláudio Cavalcanti Beltrão Filho · Lucas Souto Maior Caldas · Rafael de Lima Cavalcanti Loyo Fernandes

**Base.** `bank-full.csv` (Moro, Rita e Cortez, 2014, UCI Machine Learning Repository, CC BY 4.0), aprovada pela professora no checkpoint de 27/10/2026.

{{FICHA_BASE}}

**Tipo de problema escolhido pelo grupo.** [A PREENCHER PELO GRUPO: classificação ou agrupamento, e por quê]

**Público-alvo.** Gestores de campanhas bancárias. [A PREENCHER PELO GRUPO: por que esse público e como ele orientou linguagem, nível de detalhe e tipos de gráfico]

**Pergunta de pesquisa.** Entre os clientes já contatados em campanhas anteriores, como a taxa de adesão ao depósito a prazo na campanha atual varia conforme o resultado registrado na campanha anterior?

## Estrutura e qualidade dos dados

{{TABELA_ESTRUTURA}}

## Dados ausentes: mecanismo e tratamento

[A PREENCHER PELO GRUPO: para cada variável com `unknown` (job, education, contact, poutcome) e para o marcador pdays = −1 / previous = 0, discutir o mecanismo provável de ausência e justificar o tratamento adotado. O enunciado proíbe simplesmente remover os faltantes.]

[A PREENCHER PELO GRUPO: justificar por que o recorte pdays ≠ −1 define o escopo da pergunta e não é uma remoção de faltantes.]

## Valores extremos

{{TABELA_IQR}}

[A PREENCHER PELO GRUPO: decisão final sobre os valores sinalizados pelo IQR (manter, tratar ou excluir), com justificativa por variável quando necessário.]

## Exploração

{{FIGURAS_EXPLORATORIAS}}

## Da exploração à explicação

[A PREENCHER PELO GRUPO: o que a exploração encontrou, que história os dados contam, por que essa mensagem é a mais relevante para gestores de campanha e qual atributo pré-atentivo (cor, tamanho, posição) foi usado para destacá-la.]

## Visualizações explanatórias

{{FIGURAS_EXPLANATORIAS}}

## Resposta à pergunta de pesquisa

{{TABELA_ADESAO}}

[A PREENCHER PELO GRUPO: resposta do grupo à pergunta de pesquisa, com os limites da análise.]

## Uso de IA

O uso de IA está registrado em `docs/DECLARACAO_IA.pdf`, assinada pelos quatro integrantes, e marcado no código com comentários `# [IA]`.
