# [IA] Codex – apoio com pandas, controles Streamlit e renderização das escolhas do grupo.
import json
from pathlib import Path

import matplotlib.pyplot as plt
import streamlit as st

from eda import carregar_dados, tabelas


PASTA = Path(__file__).resolve().parent
PERGUNTA = (
    "Entre os clientes já contatados em campanhas anteriores, como a taxa de adesão "
    "ao depósito a prazo na campanha atual varia conforme o resultado registrado "
    "na campanha anterior?"
)


@st.cache_data
def carregar():
    base = carregar_dados()
    return base, tabelas(base)


def desenhar(painel, dados):
    base = dados.loc[dados["pdays"].ne(-1)] if painel["historico"] else dados
    x, medida = painel["variavel"], painel["medida"]
    contagens = base.groupby(x)["y"].agg(
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
    ax.set(xlabel=x, ylabel=medida, title=painel["titulo"])
    ax.tick_params(axis="x", labelrotation=40)
    ax.legend()
    st.pyplot(fig)
    plt.close(fig)
    st.write(painel["nota"])
    with st.expander("Conferir contagens e denominadores"):
        st.dataframe(contagens)


st.set_page_config(page_title="Bank Marketing", layout="wide")
st.html(f"<style>{(PASTA / 'painel.css').read_text()}</style>")
st.title("Campanhas de marketing bancário")
st.caption("Bank Marketing · UCI   /   Painel para gestores de campanhas")
dados, resultados = carregar()
pagina = st.radio("Navegação", ["Histórico de campanhas", "Exploração", "Visualizações"],
                  horizontal=True, label_visibility="collapsed")

if pagina == "Histórico de campanhas":
    resumo = resultados["adesao_por_historico"]
    st.subheader("Adesão por resultado anterior")
    st.html(f'<p class="pesquisa">{PERGUNTA}</p>')
    total = f"{len(dados):,}".replace(",", ".")
    recorte = f"{resumo.Registros.sum():,}".replace(",", ".")
    st.html(f'<p class="escopo"><strong>{recorte}</strong> registros com contato anterior '
            f' em um total de {total} registros.</p>')
    nomes = {"failure": "Fracasso", "other": "Outro", "success": "Sucesso", "unknown": "Desconhecido"}
    tabela = resumo.rename(index=nomes, columns={"Taxa de adesão (%)": "Taxa de adesão"}).copy()
    tabela.index.name = "Resultado anterior"
    for campo in ["Registros", "Adesões"]:
        tabela[campo] = tabela[campo].map(lambda v: f"{v:,}".replace(",", "."))
    tabela["Taxa de adesão"] = tabela["Taxa de adesão"].map(lambda v: f"{v:.2f}%".replace(".", ","))
    html = tabela.reset_index().to_html(index=False, border=0)
    st.html(f'<div class="resultados">{html}</div>')
    st.caption("Taxa de adesão = adesões ÷ registros do mesmo resultado anterior. "
               "O recorte considera pdays diferente de −1.")
elif pagina == "Exploração":
    st.subheader("Exploração da base")
    st.caption("Nas estatísticas numéricas, pdays = −1 é excluído apenas dos cálculos de dias. "
               "O CSV original é preservado. Os limites de outliers usam 1,5 × IQR.")
    opcoes = {
        "Estrutura e ausências": "estrutura", "Frequências por categoria": "frequencias_categoricas",
        "Distribuições numéricas": "distribuicoes_numericas", "Correlações numéricas": "correlacoes_pearson",
        "Outliers por variável": "limites_iqr",
    }
    escolha = st.selectbox("Tabela", [*opcoes, "Relação entre duas variáveis", "Dados originais"])
    if escolha == "Dados originais":
        campos = st.multiselect("Colunas", dados.columns, default=list(dados.columns))
        if campos:
            st.dataframe(dados[campos], hide_index=True)
    elif escolha == "Relação entre duas variáveis":
        campos = list(dados.columns)
        x = st.selectbox("Agrupar por", campos)
        y = st.selectbox("Examinar", [c for c in campos if c != x])
        consulta = dados.copy()
        consulta["pdays"] = consulta["pdays"].mask(consulta["pdays"].eq(-1))
        if y in dados.select_dtypes("number"):
            st.dataframe(consulta.groupby(x)[y].describe())
        else:
            st.dataframe(consulta.groupby([x, y]).size().unstack(fill_value=0))
    else:
        st.dataframe(resultados[opcoes[escolha]])
else:
    st.subheader("Visualizações do grupo")
    arquivo = PASTA / "visualizacoes.json"
    if "rascunho" not in st.session_state:
        st.session_state.rascunho = json.loads(arquivo.read_text()) if arquivo.exists() else [{} for _ in range(6)]
    salvos = st.session_state.rascunho
    editar = st.toggle("Editar visualizações", value=not arquivo.exists())
    paineis = []
    for i, salvo in enumerate(salvos):
        nome = f"Exploratória {i + 1}" if i < 4 else f"Explanatória {i - 3}"
        with st.expander(nome, expanded=not editar):
            if editar:
                def selecionar(rotulo, opcoes, campo):
                    anterior = salvo.get(campo)
                    indice = opcoes.index(anterior) if anterior in opcoes else None
                    return st.selectbox(rotulo, opcoes, index=indice, key=f"{i}_{campo}")

                painel = {
                    "titulo": st.text_input("Título", salvo.get("titulo", ""), key=f"titulo{i}"),
                    "tipo": selecionar("Tipo", ["Barras", "Linha"], "tipo"),
                    "variavel": selecionar("Variável do eixo horizontal",
                        list(dados.select_dtypes(exclude="number").columns) + ["day", "campaign", "previous", "age"], "variavel"),
                    "medida": selecionar("Medida", ["Registros", "Adesões", "Taxa de adesão (%)"], "medida"),
                    "historico": st.checkbox("Apenas registros com contato anterior", salvo.get("historico", False), key=f"historico{i}"),
                    "nota": st.text_area("Nota autoral · o que mostra, interpretação e motivo da escolha",
                        salvo.get("nota", ""), key=f"nota{i}"),
                }
            else:
                painel = salvo
            paineis.append(painel)
            if not editar and not painel.get("titulo"):
                st.caption("Abra a edição para configurar esta visualização.")
            if all(painel.get(c) for c in ["titulo", "tipo", "variavel", "medida"]):
                desenhar(painel, dados)
    if editar:
        st.session_state.rascunho = paineis
        completos = sum(all(p.get(c) for c in ["titulo", "tipo", "variavel", "medida", "nota"]) for p in paineis)
        st.caption(f"{completos} de 6 visualizações com configuração e nota. "
                   "Para publicar as escolhas, coloque o arquivo baixado ao lado de dashboard.py.")
        st.download_button("Baixar configuração", json.dumps(paineis, ensure_ascii=False, indent=2),
                           file_name="visualizacoes.json", mime="application/json")

st.markdown("[Dados e dicionário · UCI Bank Marketing](https://archive.ics.uci.edu/dataset/222/bank+marketing)")
