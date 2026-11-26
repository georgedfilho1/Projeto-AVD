"""K-Means da Parte Comum para a página do dashboard.

Reproduz o procedimento de notebooks/parte_comum/kmeans_metricas.ipynb
(StandardScaler, KMeans com n_init=10 e random_state=42, mapeamento pela nota
majoritária). A análise e a discussão ficam nos notebooks.
"""
# [IA] Claude – apoio com scikit-learn para reutilizar o procedimento do notebook no Streamlit.
from pathlib import Path

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import confusion_matrix, silhouette_score
from sklearn.preprocessing import StandardScaler

RAIZ = Path(__file__).resolve().parents[2]
PASTA = RAIZ / "data/parte_comum"


def carregar_vinhos():
    tintos = pd.read_csv(PASTA / "winequality-red.csv", sep=";").assign(tipo_vinho="tinto")
    brancos = pd.read_csv(PASTA / "winequality-white.csv", sep=";").assign(tipo_vinho="branco")
    return pd.concat([tintos, brancos], ignore_index=True)


def padronizar(vinhos):
    medidas = vinhos.drop(columns=["quality", "tipo_vinho"])
    return pd.DataFrame(StandardScaler().fit_transform(medidas), columns=medidas.columns)


def ajustar(X, k):
    return KMeans(n_clusters=k, n_init=10, random_state=42).fit(X)


def projetar(X):
    pca = PCA(n_components=2)
    return pca.fit_transform(X), pca.explained_variance_ratio_ * 100


def avaliar(vinhos, X, rotulos):
    notas = vinhos["quality"]
    classes = sorted(notas.unique())
    clusters = pd.Series(rotulos, name="cluster")
    contingencia = pd.crosstab(notas, clusters).reindex(index=classes, fill_value=0)
    nota_majoritaria = contingencia.idxmax(axis=0)
    atribuidas = clusters.map(nota_majoritaria)
    matriz = pd.DataFrame(
        confusion_matrix(notas, atribuidas, labels=classes),
        index=pd.Index(classes, name="nota real"),
        columns=pd.Index(classes, name="nota atribuída"),
    )
    acertos = pd.Series(matriz.to_numpy().diagonal(), index=classes)
    reais, atrib = matriz.sum(axis=1), matriz.sum(axis=0)
    total = int(matriz.to_numpy().sum())
    metricas = pd.DataFrame({
        "amostras reais": reais,
        "amostras atribuídas": atrib,
        "acurácia (1 vs. demais)": (total - reais - atrib + 2 * acertos) / total,
        "precisão": acertos.div(atrib.where(atrib.gt(0))),
        "recall": acertos.div(reais),
    })
    resumo = {
        "acurácia": acertos.sum() / total,
        "silhueta": silhouette_score(X, rotulos),
    }
    return contingencia, matriz, metricas, resumo
