"""Tabelas da Parte Específica. Execute com Python 3.11+."""
# [IA] Codex – apoio com pandas para tabulação e exportação reproduzível.
# [IA] Claude – revisão do IQR (marcador de ausência em previous) e colunas de diagnóstico.
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


def sem_marcadores(dados):
    """Numéricas com o marcador de "sem contato anterior" tratado como ausente.

    pdays = −1 e previous = 0 ocorrem exatamente nos mesmos 36.954 registros
    (clientes nunca contatados antes). Nesses registros, os dois campos não
    medem dias nem contatos; por isso ficam fora dos resumos numéricos.
    O CSV original não é alterado.
    """
    numericas = dados.select_dtypes("number").copy()
    sem_contato = dados["pdays"].eq(-1)
    numericas.loc[sem_contato, ["pdays", "previous"]] = float("nan")
    return numericas


def resumir_adesao(historico):
    adesao = (
        historico.assign(aderiu=historico["y"].eq("yes"))
        .groupby("poutcome")["aderiu"].agg(Registros="size", Adesões="sum")
    )
    adesao["Taxa de adesão (%)"] = 100 * adesao["Adesões"] / adesao["Registros"]
    adesao.index.name = "Resultado anterior"
    return adesao


def tabelas(dados):
    adesao = resumir_adesao(dados.loc[dados["pdays"].ne(-1)])
    numericas = sem_marcadores(dados)
    q1, q3 = numericas.quantile(.25), numericas.quantile(.75)
    iqr = q3 - q1
    inferior, superior = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    frequencias = pd.concat(
        {c: dados[c].value_counts(dropna=False) for c in dados.select_dtypes(exclude="number")},
        names=["variável", "valor"],
    ).to_frame("registros")
    estrutura = pd.DataFrame({
        "tipo": dados.dtypes.astype(str), "distintos": dados.nunique(),
        "nulos": dados.isna().sum(), "unknown": dados.eq("unknown").sum(),
    })
    estrutura["% unknown"] = 100 * estrutura["unknown"] / len(dados)
    estrutura["sem contato anterior (marcador)"] = 0
    estrutura.loc[["pdays", "previous"], "sem contato anterior (marcador)"] = int(dados["pdays"].eq(-1).sum())
    return {
        "adesao_por_historico": adesao,
        "estrutura": estrutura,
        "frequencias_categoricas": frequencias,
        "distribuicoes_numericas": numericas.describe().T,
        "correlacoes_pearson": numericas.corr(),
        "limites_iqr": pd.DataFrame({
            "Q1": q1, "Q3": q3, "IQR": iqr,
            "inferior": inferior, "superior": superior,
            "abaixo": numericas.lt(inferior).sum(), "acima": numericas.gt(superior).sum(),
            "registros avaliados": numericas.notna().sum(),
        }),
    }


if __name__ == "__main__":
    SAIDA.mkdir(parents=True, exist_ok=True)
    for nome, tabela in tabelas(carregar_dados()).items():
        tabela.round(6).to_csv(SAIDA / f"{nome}.csv")
