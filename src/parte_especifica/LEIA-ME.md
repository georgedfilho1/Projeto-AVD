# Parte Específica · Bank Marketing

Painel para gestores de campanhas bancárias. A professora aprovou o dataset Bank Marketing no checkpoint. A pergunta de pesquisa aparece na tela inicial do dashboard e em `docs/relatorio_parte_especifica.md`.

**Base.** `data/parte_especifica/bank-full.csv` (delimitador ponto e vírgula, 45.211 registros, 17 colunas) e o dicionário original `bank-names.txt`. Fonte: Moro, S., Rita, P. e Cortez, P. (2014), Bank Marketing, UCI Machine Learning Repository, https://doi.org/10.24432/C5K306 (CC BY 4.0).

## Arquivos

| Arquivo | Função |
|---|---|
| `eda.py` | Gera as tabelas de estrutura, frequências, distribuições, correlações e limites de IQR em `out/parte_especifica/`. |
| `graficos.py` | Desenha as visualizações a partir da configuração escolhida pelo grupo. |
| `dashboard.py` | App Streamlit: visão geral, exploração, visualizações do grupo e página da Parte Comum. |
| `visualizacoes.json` | Configuração e notas das seis visualizações, gravada pelo próprio dashboard. |

## Convenções de cálculo

- A taxa de adesão é o número de registros com `y = yes` dividido pelo total de registros da mesma categoria.
- O recorte "com contato anterior" usa `pdays ≠ −1`. `pdays = −1` e `previous = 0` ocorrem exatamente nos mesmos 36.954 registros. Nesses registros, os dois campos marcam ausência de contato anterior e ficam fora dos resumos numéricos e do IQR desses campos. O CSV original não é alterado.
- Os valores `unknown` continuam identificados e contados na tabela de estrutura.
- Os limites de IQR (1,5 × IQR) são diagnósticos. Nenhum registro é excluído automaticamente.
- Os gráficos avisam quando uma categoria tem menos de 30 registros.

## Como preencher as seis visualizações

1. Rode `python -m streamlit run src/parte_especifica/dashboard.py` e abra **Visualizações**.
2. Para cada figura, o grupo escolhe o título, o tipo (barras, barras agrupadas, linha, histograma ou boxplot), as variáveis, o recorte e, se quiser, uma categoria para destacar com cor (atributo pré-atentivo), com a justificativa do destaque.
3. Escreva a nota autoral nos três campos: o que a figura mostra, o insight e por que este tipo de gráfico. O enunciado proíbe usar IA nessas notas.
4. Em uma das explanatórias, marque "Esta figura responde diretamente à pergunta de pesquisa".
5. Clique em **Salvar em visualizacoes.json** e faça o commit do arquivo.

As explanatórias também aparecem na tela inicial e entram automaticamente no relatório.
