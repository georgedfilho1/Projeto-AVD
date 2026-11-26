# Análise e Visualização de Dados · AV2
Projeto em Python 3.11+ sobre agrupamento de vinhos (Parte Comum) e campanhas de marketing bancário (Parte Específica).

**Integrantes:** George Diógenes Pessoa Filho, João Cláudio Cavalcanti Beltrão Filho, Lucas Souto Maior Caldas e Rafael de Lima Cavalcanti Loyo Fernandes. Contribuições em [docs/MATRIZ_CONTRIBUICAO.md](docs/MATRIZ_CONTRIBUICAO.md). Uso de IA declarado em [docs/DECLARACAO_IA.pdf](docs/DECLARACAO_IA.pdf).

## Instalação
Na raiz do repositório, crie e ative um ambiente virtual com Python 3.11 ou superior. No macOS ou Linux:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

No Windows (PowerShell), use `py -m venv .venv` e `.venv\Scripts\Activate.ps1`.

## Parte Comum · Wine Quality
Os CSVs de vinhos tintos e brancos estão em `data/parte_comum/` ([Wine Quality · UCI](https://archive.ics.uci.edu/dataset/186/wine+quality)). Execute os dois notebooks em ordem:

```sh
python -m jupyterlab notebooks/parte_comum/eda.ipynb
python -m jupyterlab notebooks/parte_comum/kmeans_metricas.ipynb
```

`eda.ipynb` cobre as dimensões estrutural, distribucional e relacional e os outliers. `kmeans_metricas.ipynb` cobre a padronização, as duas passadas do K-Means (k pelo cotovelo e k igual ao número de notas), as matrizes de confusão, as métricas e a discussão crítica. As figuras são gravadas em `out/parte_comum/`.

Para executar sem abrir o Jupyter:

```sh
python -m jupyter nbconvert --to notebook --execute --inplace notebooks/parte_comum/eda.ipynb notebooks/parte_comum/kmeans_metricas.ipynb
```

## Parte Específica · Bank Marketing
O dashboard usa `data/parte_especifica/bank-full.csv` ([Bank Marketing · UCI](https://doi.org/10.24432/C5K306)). Na raiz:

```sh
python src/parte_especifica/eda.py
python -m streamlit run src/parte_especifica/dashboard.py
```

As tabelas da exploração são gravadas em `out/parte_especifica/`. O guia da Parte Específica, com o passo a passo das seis visualizações, está em [src/parte_especifica/LEIA-ME.md](src/parte_especifica/LEIA-ME.md). O dashboard também tem uma página da Parte Comum com o cotovelo e a comparação lado a lado das passadas.

## Relatório
O `relatorio.pdf` da raiz é gerado a partir dos notebooks executados, de `docs/relatorio_parte_especifica.md` e de `src/parte_especifica/visualizacoes.json`. O gerador usa o Google Chrome ou o Chromium instalado:

```sh
python src/relatorio/gerar_relatorio.py             # recusa gerar enquanto houver pendências
python src/relatorio/gerar_relatorio.py --rascunho  # gera relatorio-rascunho.pdf com as pendências marcadas
```

## Verificação da entrega
```sh
python src/verificar_entrega.py
```

O script confere a estrutura de pastas, os notebooks, as seis visualizações, os textos autorais, a matriz, a declaração e o relatório, e lista o que ainda falta.
