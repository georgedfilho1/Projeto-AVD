# [IA] Codex – apoio com pandas, controles Streamlit e renderização das escolhas do grupo.
import base64
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from eda import carregar_dados, resumir_adesao, tabelas


PASTA = Path(__file__).resolve().parent
PERGUNTA = (
    "Entre os clientes já contatados em campanhas anteriores, como a taxa de adesão "
    "ao depósito a prazo na campanha atual varia conforme o resultado registrado "
    "na campanha anterior?"
)


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


def nome_campo(campo):
    return f"{CAMPOS.get(campo, campo)} · {campo}"


@st.cache_data
def carregar():
    base = carregar_dados()
    resultados = tabelas(base)
    meses = "jan feb mar apr may jun jul aug sep oct nov dec".split()
    base["month"] = pd.Categorical(base["month"], categories=meses, ordered=True)
    return base, resultados


def inteiro(valor):
    return f"{valor:,}".replace(",", ".")


def percentual(valor):
    return f"{valor:.2f}%".replace(".", ",")


@st.cache_data
def estilo(css, fonte, gravura):
    return css.replace("FONTE_LOCAL", base64.b64encode(fonte).decode()).replace(
        "GRAVURA_LOCAL", base64.b64encode(gravura).decode()
    )


def desenhar(painel, dados):
    base = dados.loc[dados["pdays"].ne(-1)] if painel["historico"] else dados
    x, medida = painel["variavel"], painel["medida"]
    contagens = base.groupby(x, observed=True)["y"].agg(
        registros="size", adesoes=lambda valores: valores.eq("yes").sum()
    )
    contagens["taxa"] = 100 * contagens["adesoes"] / contagens["registros"]
    coluna = {"Registros": "registros", "Adesões": "adesoes", "Taxa de adesão (%)": "taxa"}[medida]
    serie = contagens[coluna]
    fig, ax = plt.subplots(figsize=(9, 4), layout="constrained")
    if painel["tipo"] == "Barras":
        ax.bar(serie.index.astype(str), serie, label=medida, color="#266657")
    else:
        ax.plot(serie.index.astype(str), serie, marker="o", label=medida, color="#266657")
    ax.set(xlabel=nome_campo(x), ylabel=medida, title=painel["titulo"])
    ax.tick_params(axis="x", labelrotation=40)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=.17)
    ax.set_axisbelow(True)
    ax.legend(frameon=False)
    st.pyplot(fig)
    plt.close(fig)
    st.write(painel["nota"])
    with st.expander("Conferir contagens e denominadores"):
        st.dataframe(contagens)


st.set_page_config(page_title="Bank Marketing", layout="wide")
css = estilo((PASTA / "painel.css").read_text(),
             (PASTA / "assets/InstrumentSerif-latin.ttf").read_bytes(),
             (PASTA / "assets/gravura.png").read_bytes())
st.html(f"<style>{css}</style>")
dados, resultados = carregar()
st.html('<header class="mast"><div class="ident"><span aria-hidden="true" class="selo">B</span>'
        '<span>Bank Marketing</span></div><span class="fonte">UCI · Análise e Visualização de Dados</span></header>')
rotulos = {"Histórico de campanhas": "Visão geral", "Exploração": "Explorar dados", "Visualizações": "Visualizações"}
pagina = st.radio("Navegação", list(rotulos), format_func=rotulos.get, horizontal=True,
                  label_visibility="collapsed", key="menu")
if pagina == "Histórico de campanhas":
    st.html('<section class="capa"><div class="gravura" aria-hidden="true"></div>'
            '<div class="texto-capa"><h1>Histórico de campanhas</h1>'
            '<p>Adesão a depósitos a prazo entre clientes com contato anterior.</p></div></section>')
    metricas = st.empty()
    principal, controles = st.columns([2.15, 1], gap="large")
    with controles:
        with st.container(border=True):
            st.subheader("Filtrar comparação")
            canais = {"Todos": None, "Celular": "cellular", "Telefone fixo": "telephone", "Desconhecido": "unknown"}
            canal = st.selectbox("Canal da campanha atual", list(canais), key="canal")
            opcoes = {"Todos": None, "Sim": "yes", "Não": "no"}
            emprestimo = st.selectbox("Empréstimo pessoal", list(opcoes), key="emprestimo")

            def limpar():
                st.session_state.canal = "Todos"
                st.session_state.emprestimo = "Todos"

            st.button("Limpar filtros", on_click=limpar, disabled=canal == emprestimo == "Todos")
    base = dados.loc[dados["pdays"].ne(-1)]
    if canais[canal]:
        base = base.loc[base["contact"].eq(canais[canal])]
    if opcoes[emprestimo]:
        base = base.loc[base["loan"].eq(opcoes[emprestimo])]
    resumo = resumir_adesao(base)
    n, adesoes = len(base), int(resumo["Adesões"].sum())
    medidas = [("Registros no recorte", inteiro(n)), ("Adesões", inteiro(adesoes)),
               ("Taxa de adesão", percentual(100 * adesoes / n) if n else "—")]
    metricas.html('<dl class="faixa">' + ''.join(
        f'<div><dt>{nome}</dt><dd>{valor}</dd></div>' for nome, valor in medidas) + '</dl>')
    with principal:
        st.subheader("Adesão por resultado anterior")
        st.caption("Resposta na campanha atual, agrupada pelo desfecho do contato anterior.")
        if n:
            nomes = {"failure": "Fracasso", "other": "Outro", "success": "Sucesso", "unknown": "Desconhecido"}
            linhas = "".join(
                f'<tr><th scope="row">{nomes[c]}</th><td>{inteiro(r)}</td><td>{inteiro(a)}</td>'
                f'<td>{percentual(t)}</td></tr>' for c, r, a, t in resumo.itertuples())
            st.html('<div class="resultados"><table aria-label="Adesão por resultado anterior">'
                    '<thead><tr><th>Resultado anterior</th><th>Registros</th><th>Adesões</th><th>Taxa</th>'
                    '</tr></thead><tbody>' + linhas + '</tbody></table></div>')
            st.download_button("Exportar esta tabela", resumo.rename_axis("poutcome").to_csv(
                sep=";", decimal=","), file_name="adesao-por-resultado.csv", mime="text/csv", icon=":material/download:")
        else:
            st.info("Este recorte não tem registros. Altere um filtro ou use Limpar filtros.")
    with st.expander("Pergunta de pesquisa e método"):
        st.write(PERGUNTA)
        st.write(f"Base completa: {inteiro(len(dados))} registros. O recorte inclui pdays diferente de −1. "
                 "A taxa divide as adesões pelos registros da mesma categoria após os filtros. "
                 "O resultado anterior desconhecido permanece identificado.")
elif pagina == "Exploração":
    st.html('<section class="pagina"><h1>Exploração da base</h1><p>Consulte as 17 variáveis ou cruze duas delas para investigar uma relação.</p></section>')
    st.caption("Nas estatísticas numéricas, pdays = −1 é excluído apenas dos cálculos de dias. "
               "O CSV original é preservado. Os limites de outliers usam 1,5 × IQR.")
    opcoes = {
        "Estrutura e ausências": "estrutura", "Frequências por categoria": "frequencias_categoricas",
        "Distribuições numéricas": "distribuicoes_numericas", "Correlações numéricas": "correlacoes_pearson",
        "Outliers por variável": "limites_iqr",
    }
    escolha = st.selectbox("Tabela", [*opcoes, "Relação entre duas variáveis", "Dados originais"])
    if escolha == "Dados originais":
        campos = st.multiselect("Colunas", dados.columns, default=list(dados.columns), format_func=nome_campo)
        if campos:
            st.dataframe(dados[campos], hide_index=True)
        else:
            st.info("Selecione uma coluna para consultar os registros.")
    elif escolha == "Relação entre duas variáveis":
        campos = list(dados.columns)
        x = st.selectbox("Agrupar por", campos, format_func=nome_campo)
        y = st.selectbox("Examinar", [c for c in campos if c != x], format_func=nome_campo)
        consulta = dados.copy()
        consulta["pdays"] = consulta["pdays"].mask(consulta["pdays"].eq(-1))
        if y in dados.select_dtypes("number"):
            st.dataframe(consulta.groupby(x, observed=True)[y].describe())
        else:
            st.dataframe(consulta.groupby([x, y], observed=True).size().unstack(fill_value=0))
    else:
        st.dataframe(resultados[opcoes[escolha]])
else:
    st.html('<section class="pagina"><h1>Visualizações do grupo</h1><p>Explore as figuras ou edite os recortes e as notas da equipe.</p></section>')
    arquivo = PASTA / "visualizacoes.json"
    if "rascunho" not in st.session_state:
        st.session_state.rascunho = json.loads(arquivo.read_text()) if arquivo.exists() else [{} for _ in range(6)]
    salvos = st.session_state.rascunho
    editar = st.toggle("Editar visualizações", value=not arquivo.exists())
    paineis = list(salvos)
    nomes_figuras = [f"Exploratória {i + 1}" if i < 4 else f"Explanatória {i - 3}" for i in range(6)]
    escolhida = st.selectbox("Figura em edição", nomes_figuras) if editar else None
    for i, salvo in enumerate(salvos):
        nome = f"Exploratória {i + 1}" if i < 4 else f"Explanatória {i - 3}"
        if editar and nome != escolhida:
            continue
        if editar:
            editor, previa = st.columns([1, 1.2], gap="large")
            with editor:
                def selecionar(rotulo, opcoes, campo):
                    anterior = salvo.get(campo)
                    indice = opcoes.index(anterior) if anterior in opcoes else None
                    return st.selectbox(rotulo, opcoes, index=indice, key=f"{i}_{campo}",
                                        format_func=nome_campo if campo == "variavel" else str)

                painel = {
                    "titulo": st.text_input("Título", salvo.get("titulo", ""), key=f"titulo{i}"),
                    "tipo": selecionar("Tipo de gráfico", ["Barras", "Linha"], "tipo"),
                    "variavel": selecionar("Eixo horizontal",
                        list(dados.select_dtypes(exclude="number").columns) + ["day", "campaign", "previous", "age"], "variavel"),
                    "medida": selecionar("Medida", ["Registros", "Adesões", "Taxa de adesão (%)"], "medida"),
                    "historico": st.checkbox("Apenas registros com contato anterior", salvo.get("historico", False), key=f"historico{i}"),
                    "nota": st.text_area("Nota autoral", salvo.get("nota", ""), key=f"nota{i}",
                        help="Descreva o que a figura mostra, a interpretação do grupo e por que escolheram esse gráfico."),
                }
        else:
            previa = st.container()
            painel = salvo
        paineis[i] = painel
        with previa:
            if all(painel.get(c) for c in ["titulo", "tipo", "variavel", "medida"]):
                desenhar(painel, dados)
            elif editar:
                st.html('<div class="previsual"><strong>Prévia da figura</strong>'
                        '<p>Preencha o título, o tipo de gráfico, o eixo e a medida para conferir o resultado.</p></div>')
            else:
                st.caption(f"{nome} · Aguardando configuração do grupo.")
    if editar:
        st.session_state.rascunho = paineis
        completos = sum(all(p.get(c) for c in ["titulo", "tipo", "variavel", "medida", "nota"]) for p in paineis)
        st.caption(f"{completos} de 6 visualizações com configuração e nota. "
                   "Para publicar as escolhas, coloque o arquivo baixado ao lado de dashboard.py.")
        st.download_button("Baixar configuração", json.dumps(paineis, ensure_ascii=False, indent=2),
                           file_name="visualizacoes.json", mime="application/json")

st.html('<footer class="rodape"><span>Bank Marketing · AVD 2026.2</span>'
        '<a href="https://archive.ics.uci.edu/dataset/222/bank+marketing" target="_blank" rel="noopener">'
        'Dados e dicionário na UCI ↗</a></footer>')
