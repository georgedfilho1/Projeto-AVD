<!--
Texto-fonte da nova versão da declaração de uso de IA.
1. Cada integrante confere o registro e resolve os itens [CONFIRMAR ...] com a descrição real do próprio uso.
2. Gere o PDF:  python src/relatorio/gerar_relatorio.py --declaracao
3. Os quatro assinam o PDF gerado (gov.br) e o arquivo assinado substitui docs/DECLARACAO_IA.pdf.
Não substitua docs/DECLARACAO_IA.pdf antes de ter a versão nova assinada pelos quatro.
-->

# Declaração de uso de IA

Análise e Visualização de Dados · AV2 · 2026.2

Declaramos que o uso de IA generativa neste projeto está descrito abaixo de forma completa. Os trechos de código feitos com apoio de IA estão marcados com `# [IA] <ferramenta> – <finalidade>`. As análises, discussões, conclusões e notas analíticas são do grupo, e todos os integrantes sabem explicar o código e os resultados entregues.

## Ferramentas e finalidades

**Codex (OpenAI).** Apoio com pandas nas tabelas de exploração da Parte Específica (`src/parte_especifica/eda.py`); controles Streamlit, interface e renderização Matplotlib do dashboard (`src/parte_especifica/dashboard.py`); testes de execução; apoio no cálculo e na verificação da acurácia por nota no notebook da Parte Comum. [CONFIRMAR PELO GRUPO: a versão anterior registrava "apoio na formulação da pergunta". Descrevam exatamente o que foi feito, por exemplo revisão da redação de uma pergunta escrita pelo grupo.]

**Claude (Anthropic).** Revisão de conformidade do repositório com o enunciado; divisão do notebook da Parte Comum em `eda.ipynb` e `kmeans_metricas.ipynb` e exportação das figuras para `out/`; correção do cálculo de IQR com o marcador de "sem contato anterior"; novos tipos de gráfico, destaque por cor, legendas e notas em três partes no editor do dashboard; página da Parte Comum no dashboard; gerador do relatório em PDF; script de verificação da entrega; revisão do README, do guia da Parte Específica e da matriz de contribuição; rascunho deste texto. O Claude não escreveu análises, notas analíticas, discussões ou conclusões e não escolheu os gráficos do grupo.

## Uso por integrante

**George Diógenes Pessoa Filho.** [CONFIRMAR PELO INTEGRANTE: a versão anterior dizia "Refinar as figuras do notebook original com as respectivas análises". O enunciado proíbe usar IA para gerar análises. Se algum texto analítico do notebook foi escrito por IA, ele precisa ser reescrito pelo grupo antes da entrega. Registre aqui apenas o uso efetivo, por exemplo ajuste de código das figuras, e marque essas células com `# [IA]`.]

**João Cláudio Cavalcanti Beltrão Filho.** Codex e Claude no desenvolvimento da interface, na renderização das figuras, na documentação e na revisão de conformidade descrita acima.

**Lucas Souto Maior Caldas.** [CONFIRMAR PELO INTEGRANTE: a versão anterior dizia "Montar a minuta a partir do notebook e das tabelas já existentes". Indique a ferramenta e se a IA apenas organizou e revisou a forma de textos do grupo.]

**Rafael de Lima Cavalcanti Loyo Fernandes.** Documentação da instalação e da execução; apoio para corrigir o pull request e fazer os merges.

## Assinaturas

| Integrante | Data | Assinatura |
|---|---|---|
| George Diógenes Pessoa Filho | | |
| João Cláudio Cavalcanti Beltrão Filho | | |
| Lucas Souto Maior Caldas | | |
| Rafael de Lima Cavalcanti Loyo Fernandes | | |
