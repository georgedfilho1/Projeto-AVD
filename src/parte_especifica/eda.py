"""Tabelas da Parte Específica. Execute com Python 3.11+."""
# [IA] Codex – apoio com pandas para tabulação e exportação reproduzível.
from pathlib import Path

import pandas as pd


RAIZ = Path(__file__).resolve().parents[2]
ARQUIVO = RAIZ / "data/parte_especifica/bank-full.csv"
SAIDA = RAIZ / "out/parte_especifica"


def carregar_dados():
    dados = pd.read_csv(ARQUIVO, sep=";")
    if not dados["y"].isin(["yes", "no"]).all():
        raise ValueError("A coluna y deve conter somente yes ou no.")
    return dados


def tabelas(dados):
    historico = dados.loc[dados["pdays"].ne(-1)]
    adesao = (
        historico.assign(aderiu=historico["y"].eq("yes"))
        .groupby("poutcome")["aderiu"].agg(Registros="size", Adesões="sum")
    )
    adesao["Taxa de adesão (%)"] = 100 * adesao["Adesões"] / adesao["Registros"]
    adesao.index.name = "Resultado anterior"
    numericas = dados.select_dtypes("number").copy()
    numericas["pdays"] = numericas["pdays"].mask(numericas["pdays"].eq(-1))
    q1, q3 = numericas.quantile(.25), numericas.quantile(.75)
    iqr = q3 - q1
    inferior, superior = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    frequencias = pd.concat(
        {c: dados[c].value_counts(dropna=False) for c in dados.select_dtypes(exclude="number")},
        names=["variável", "valor"],
    ).to_frame("registros")
    return {
        "adesao_por_historico": adesao,
        "estrutura": pd.DataFrame({
            "tipo": dados.dtypes.astype(str), "distintos": dados.nunique(),
            "nulos": dados.isna().sum(), "unknown": dados.eq("unknown").sum(),
        }),
        "frequencias_categoricas": frequencias,
        "distribuicoes_numericas": numericas.describe().T,
        "correlacoes_pearson": numericas.corr(),
        "limites_iqr": pd.DataFrame({
            "inferior": inferior, "superior": superior,
            "abaixo": numericas.lt(inferior).sum(), "acima": numericas.gt(superior).sum(),
        }),
    }


if __name__ == "__main__":
    SAIDA.mkdir(parents=True, exist_ok=True)
    for nome, tabela in tabelas(carregar_dados()).items():
        tabela.to_csv(SAIDA / f"{nome}.csv")
