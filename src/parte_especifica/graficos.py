"""Desenho das seis visualizações configuradas pelo grupo.

O módulo só executa as escolhas gravadas em visualizacoes.json (tipo, variáveis,
destaque, título). A escolha dos gráficos e as notas são do grupo.
"""
# [IA] Claude – apoio com Matplotlib para os tipos de gráfico, destaque e legendas.
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch
from matplotlib.lines import Line2D


CAMPOS = {
    "age": "Idade", "job": "Ocupação", "marital": "Estado civil",
    "education": "Escolaridade", "default": "Crédito em inadimplência",
    "balance": "Saldo médio anual (€)", "housing": "Financiamento habitacional",
    "loan": "Empréstimo pessoal", "contact": "Canal de contato", "day": "Dia do mês",
    "month": "Mês do contato", "duration": "Duração do contato (s)",
    "campaign": "Contatos na campanha atual", "pdays": "Dias desde contato anterior",
    "previous": "Contatos em campanhas anteriores", "poutcome": "Resultado anterior",
    "y": "Adesão ao depósito",
}

TIPOS = ["Barras", "Barras agrupadas", "Linha", "Histograma", "Boxplot"]
MEDIDAS = ["Registros", "Adesões", "Taxa de adesão (%)"]
CATEGORICAS = ["job", "marital", "education", "default", "housing", "loan",
               "contact", "month", "poutcome", "y"]
DISCRETAS = ["day", "campaign", "previous", "age"]
CONTINUAS = ["age", "balance", "day", "duration", "campaign", "pdays", "previous"]
# Linha só faz sentido quando o eixo horizontal tem ordem natural.
ORDENADAS = ["month", "day", "campaign", "previous", "age"]
# Variáveis com poucas categorias, legíveis como séries em barras agrupadas ou boxplots.
GRUPOS = ["marital", "education", "default", "housing", "loan", "contact", "poutcome", "y"]

COR_BASE = "#266657"
COR_DESTAQUE = "#C2512E"
COR_APAGADA = "#BCC5BF"
PALETA = ["#266657", "#C2512E", "#3E6FA8", "#B08A1E", "#7A4E8C", "#5C6B63"]
N_MINIMO = 30


def nome_campo(campo):
    return f"{CAMPOS.get(campo, campo)} · {campo}"


def opcoes_eixo(tipo):
    """Variáveis permitidas no eixo horizontal para cada tipo de gráfico."""
    if tipo == "Linha":
        return ORDENADAS
    if tipo in ("Histograma", "Boxplot"):
        return CONTINUAS
    return CATEGORICAS + DISCRETAS


def opcoes_grupo(tipo):
    if tipo == "Barras agrupadas":
        return [g for g in GRUPOS if g != "y"]
    if tipo in ("Histograma", "Boxplot"):
        return GRUPOS
    return []


def recorte(dados, painel):
    return dados.loc[dados["pdays"].ne(-1)] if painel.get("historico") else dados


def contagens(base, colunas):
    tabela = base.groupby(colunas, observed=True)["y"].agg(
        registros="size", adesoes=lambda valores: valores.eq("yes").sum()
    )
    tabela["taxa"] = 100 * tabela["adesoes"] / tabela["registros"]
    return tabela


COLUNA_MEDIDA = {"Registros": "registros", "Adesões": "adesoes", "Taxa de adesão (%)": "taxa"}


def _valores_numericos(base, variavel):
    """pdays = −1 e previous = 0 marcam ausência de contato anterior; não são medidas."""
    valores = base[variavel]
    if variavel in ("pdays", "previous"):
        valores = valores.where(base["pdays"].ne(-1))
    return valores


def _rotular_barras(ax, barras, valores, ns, medida):
    for barra, valor, n in zip(barras, valores, ns):
        texto = f"{valor:.1f}%".replace(".", ",") if medida == "Taxa de adesão (%)" else f"{int(valor):,}".replace(",", ".")
        if medida == "Taxa de adesão (%)":
            texto += f"\nn={int(n):,}".replace(",", ".")
        ax.annotate(texto, (barra.get_x() + barra.get_width() / 2, barra.get_height()),
                    xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=8)


def desenhar(painel, dados):
    """Devolve (figura, tabela de conferência, avisos) para um painel configurado."""
    base = recorte(dados, painel)
    tipo, x = painel["tipo"], painel["variavel"]
    medida = painel.get("medida")
    grupo = painel.get("grupo") or None
    destaque = painel.get("destaque") or None
    avisos = []
    fig, ax = plt.subplots(figsize=(9, 4.6), layout="constrained")

    if tipo in ("Barras", "Linha"):
        tabela = contagens(base, x)
        serie = tabela[COLUNA_MEDIDA[medida]]
        rotulos = serie.index.astype(str)
        if tipo == "Barras":
            cores = [COR_BASE] * len(serie)
            if destaque in list(rotulos):
                cores = [COR_DESTAQUE if r == destaque else COR_APAGADA for r in rotulos]
            barras = ax.bar(rotulos, serie, color=cores)
            if painel.get("rotulos", True) and len(serie) <= 15:
                _rotular_barras(ax, barras, serie, tabela["registros"], medida)
            if destaque in list(rotulos):
                ax.legend(handles=[Patch(color=COR_DESTAQUE, label=f"Destaque: {destaque}"),
                                   Patch(color=COR_APAGADA, label="Demais categorias")], frameon=False)
            else:
                ax.legend(handles=[Patch(color=COR_BASE, label=medida)], frameon=False)
        else:
            ax.plot(rotulos, serie, marker="o", color=COR_BASE, label=medida)
            if destaque in list(rotulos):
                pos = list(rotulos).index(destaque)
                ax.plot([rotulos[pos]], [serie.iloc[pos]], marker="o", markersize=11,
                        color=COR_DESTAQUE, linestyle="none", label=f"Destaque: {destaque}")
            ax.legend(frameon=False)
        ax.set(xlabel=nome_campo(x), ylabel=medida)
        if medida == "Taxa de adesão (%)":
            ax.set_ylim(0, max(serie.max() * 1.18, 1))
        pequenos = tabela.index[tabela["registros"] < N_MINIMO].astype(str).tolist()

    elif tipo == "Barras agrupadas":
        tabela = contagens(base, [x, grupo])
        matriz = tabela[COLUNA_MEDIDA[medida]].unstack(fill_value=0)
        rotulos = matriz.index.astype(str)
        series = matriz.columns.astype(str)
        largura = 0.8 / len(series)
        posicoes = np.arange(len(rotulos))
        for j, serie in enumerate(series):
            if destaque:
                cor = COR_DESTAQUE if serie == destaque else PALETA[5]
                alfa = 1 if serie == destaque else 0.25 + 0.5 * j / max(len(series), 1)
            else:
                cor, alfa = PALETA[j % len(PALETA)], 1
            ax.bar(posicoes + (j - (len(series) - 1) / 2) * largura, matriz.iloc[:, j],
                   width=largura, color=cor, alpha=alfa, label=f"{CAMPOS.get(grupo, grupo)}: {serie}")
        ax.set_xticks(posicoes, rotulos)
        ax.set(xlabel=nome_campo(x), ylabel=medida)
        ax.set_ylim(0, max(matriz.to_numpy().max() * 1.25, 1))  # espaço para a legenda acima das barras
        ax.legend(frameon=False, fontsize=8, ncols=min(len(series), 4), loc="upper left")
        pequenos = [" / ".join(map(str, i)) for i in tabela.index[tabela["registros"] < N_MINIMO]]

    elif tipo == "Histograma":
        valores = _valores_numericos(base, x)
        limite = None
        if painel.get("limitar_p99"):
            limite = valores.quantile(.99)
            fora = int(valores.gt(limite).sum())
            avisos.append(f"Eixo limitado ao percentil 99 ({limite:,.0f}); {fora:,} registros acima dele não aparecem.".replace(",", "."))
            valores = valores.where(valores.le(limite))
        faixa = (valores.min(), valores.max())
        if grupo:
            for j, (nome, parte) in enumerate(valores.groupby(base[grupo], observed=True)):
                ax.hist(parte.dropna(), bins=40, range=faixa, density=True, histtype="step", linewidth=1.8,
                        color=COR_DESTAQUE if str(nome) == destaque else PALETA[j % len(PALETA)],
                        label=f"{CAMPOS.get(grupo, grupo)}: {nome} (n={parte.notna().sum():,})".replace(",", "."))
            ax.set_ylabel("Densidade (área de cada grupo = 1)")
        else:
            ax.hist(valores.dropna(), bins=40, color=COR_BASE, edgecolor="white", label="Registros")
            ax.set_ylabel("Registros")
        ax.set_xlabel(nome_campo(x))
        ax.legend(frameon=False, fontsize=8)
        tabela = (valores.groupby(base[grupo], observed=True) if grupo else valores).describe()
        pequenos = []

    elif tipo == "Boxplot":
        valores = _valores_numericos(base, x)
        if grupo:
            partes = [(str(nome), parte.dropna()) for nome, parte in valores.groupby(base[grupo], observed=True)]
        else:
            partes = [("Todos", valores.dropna())]
        caixa = ax.boxplot([p for _, p in partes], tick_labels=[n for n, _ in partes], patch_artist=True,
                           flierprops={"marker": ".", "markersize": 3, "alpha": .4})
        for nome_parte, patch in zip([n for n, _ in partes], caixa["boxes"]):
            patch.set_facecolor(COR_DESTAQUE if nome_parte == destaque else "#CFE0D7")
            patch.set_edgecolor("#1F3A30")
        for mediana in caixa["medians"]:
            mediana.set_color("#1F3A30")
        if painel.get("limitar_p99"):
            limite = valores.quantile(.99)
            ax.set_ylim(top=limite)
            avisos.append(f"Eixo vertical cortado no percentil 99 ({limite:,.0f}); os valores acima continuam no cálculo das caixas.".replace(",", "."))
        ax.set(xlabel=nome_campo(grupo) if grupo else "Todos os registros do recorte", ylabel=nome_campo(x))
        legenda = [Patch(facecolor="#CFE0D7", edgecolor="#1F3A30", label="Caixa: Q1 a Q3"),
                   Line2D([], [], color="#1F3A30", label="Linha: mediana"),
                   Line2D([], [], color="#1F3A30", marker=".", linestyle="none", label="Pontos: além de 1,5 × IQR")]
        if destaque in [n for n, _ in partes]:
            legenda.insert(0, Patch(facecolor=COR_DESTAQUE, label=f"Destaque: {destaque}"))
        ax.legend(handles=legenda, frameon=False, fontsize=8)
        tabela = (valores.groupby(base[grupo], observed=True) if grupo else valores).describe()
        pequenos = [n for n, p in partes if len(p) < N_MINIMO]
    else:
        raise ValueError(f"Tipo de gráfico desconhecido: {tipo}")

    if pequenos:
        avisos.append(f"Categorias com menos de {N_MINIMO} registros (leitura instável): {', '.join(pequenos)}.")
    if painel.get("historico"):
        avisos.append(f"Recorte: {len(base):,} registros com contato anterior (pdays ≠ −1).".replace(",", "."))
    ax.set_title(painel["titulo"])
    ax.tick_params(axis="x", labelrotation=40 if tipo != "Boxplot" else 0)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=.17)
    ax.set_axisbelow(True)
    return fig, tabela, avisos


def configuracao_completa(painel):
    """Campos mínimos para desenhar: título, tipo e eixo; medida ou grupo quando o tipo exige."""
    if not all(painel.get(c) for c in ("titulo", "tipo", "variavel")):
        return False
    if painel["tipo"] in ("Barras", "Linha", "Barras agrupadas") and not painel.get("medida"):
        return False
    if painel["tipo"] == "Barras agrupadas" and not painel.get("grupo"):
        return False
    return painel["variavel"] in opcoes_eixo(painel["tipo"])


CAMPOS_NOTA = {
    "nota_mostra": "O que a figura mostra",
    "nota_insight": "Insight que o grupo extrai",
    "nota_por_que": "Por que este tipo de gráfico",
}


def nota_completa(painel):
    if painel.get("nota") and not any(painel.get(c) for c in CAMPOS_NOTA):
        return False  # formato antigo, com um campo só: falta separar as três respostas
    return all(str(painel.get(c, "")).strip() for c in CAMPOS_NOTA)
