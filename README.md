# Análise e Visualização de Dados · AV2
Projeto em Python 3.11+ sobre agrupamento de vinhos e campanhas de marketing bancário.

## Instalação
Na raiz do repositório, crie e ative um ambiente virtual. No macOS ou Linux:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

No Windows (PowerShell), use `py -m venv .venv` e `.venv\Scripts\Activate.ps1`.

## Parte Comum · Wine Quality
Os CSVs de vinhos tintos e brancos estão em data/parte_comum/. Abra o notebook e execute todas as células em ordem:

```sh
python -m jupyterlab notebooks/parte_comum/eda.ipynb
```

O notebook reúne as quatro dimensões da EDA, a padronização, as duas passadas do K-Means, a avaliação e a discussão crítica. [Wine Quality · UCI](https://archive.ics.uci.edu/dataset/186/wine+quality)

## Parte Específica · Bank Marketing
O dashboard usa bank-full.csv para investigar a adesão por resultado de campanha anterior. Na raiz, execute:

```sh
python src/parte_especifica/eda.py
python -m streamlit run src/parte_especifica/dashboard.py
```

As tabelas são gravadas em out/parte_especifica/. O dicionário acompanha a base em data/parte_especifica/. O guia de edição de visualizações está em src/parte_especifica/LEIA-ME.md. [Bank Marketing · UCI](https://doi.org/10.24432/C5K306)
