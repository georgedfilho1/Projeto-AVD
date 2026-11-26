# [IA] Codex – apoio com pandas, controles Streamlit e renderização das escolhas do grupo.
# [IA] Claude – apoio com Streamlit: editor com destaque, novos tipos de gráfico, notas em três partes,
#               gravação direta da configuração e página da Parte Comum.
import base64
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

from eda import carregar_dados, resumir_adesao, tabelas
from graficos import (CAMPOS_NOTA, MEDIDAS, TIPOS, configuracao_completa, desenhar,
                      nome_campo, nota_completa, opcoes_eixo, opcoes_grupo, recorte)

PASTA = Path(__file__).resolve().parent
RAIZ = PASTA.parents[1]
sys.path.insert(0, str(RAIZ / "src"))
from parte_comum.agrupamento import ajustar, avaliar, carregar_vinhos, padronizar, projetar  # noqa: E402

ARQUIVO_VIS = PASTA / "visualizacoes.json"
PERGUNTA = (
    "Entre os clientes já contatados em campanhas anteriores, como a taxa de adesão "
    "ao depósito a prazo na campanha atual varia conforme o resultado registrado "
    "na campanha anterior?"
)
NOMES_FIGURAS = [f"Exploratória {i + 1}" for i in range(4)] + [f"Explanatória {i + 1}" for i in range(2)]


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


def ler_visualizacoes():
    if ARQUIVO_VIS.exists():
        salvos = json.loads(ARQUIVO_VIS.read_text(encoding="utf-8"))
        return (salvos + [{} for _ in range(6)])[:6]
    return [{} for _ in range(6)]


def mostrar_figura(painel, dados, nome):
    fig, conferencia, avisos = desenhar(painel, dados)
    st.pyplot(fig)
    plt.close(fig)
    for aviso in avisos:
        st.caption(aviso)
    if painel.get("destaque") and painel.get("justificativa_destaque"):
        st.markdown(f"**Destaque visual.** {painel['justificativa_destaque']}")
    for campo, rotulo in CAMPOS_NOTA.items():
        if painel.get(campo):
            st.markdown(f"**{rotulo}.** {painel[campo]}")
    if painel.get("nota") and not any(painel.get(c) for c in CAMPOS_NOTA):
        st.write(painel["nota"])
    with st.expander(f"{nome} · conferir contagens e denominadores"):
        st.dataframe(conferencia)


st.set_page_config(page_title="Bank Marketing", layout="wide")
css = estilo((PASTA / "painel.css").read_text(),
             (PASTA / "assets/InstrumentSerif-latin.ttf").read_bytes(),
             (PASTA / "assets/gravura.png").read_bytes())
st.html(f"<style>{css}</style>")
dados, resultados = carregar()
st.html('<header class="mast"><div class="ident"><span aria-hidden="true" class="selo">B</span>'
        '<span>Bank Marketing</span></div><span class="fonte">UCI · Análise e Visualização de Dados</span></header>')
rotulos = {"Histórico de campanhas": "Visão geral", "Exploração": "Explorar dados",
           "Visualizações": "Visualizações", "Parte Comum": "Parte Comum · vinhos"}
pagina = st.radio("Navegação", list(rotulos), format_func=rotulos.get, horizontal=True,
                  label_visibility="collapsed", key="menu")

if pagina == "Histórico de campanhas":
    st.html('<section class="capa"><div class="gravura" aria-hidden="true"></div>'
            '<div class="texto-capa"><h1>Histórico de campanhas</h1>'
            '<p>Adesão a depósitos a prazo entre clientes com contato anterior.</p></div></section>')
    st.markdown(f"**Pergunta de pesquisa.** {PERGUNTA}")
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
        st.caption("Resposta na campanha atual, agrupada pelo desfecho do contato anterior. "
                   "Categorias com menos de 30 registros aparecem marcadas com *.")
        if n:
            nomes = {"failure": "Fracasso", "other": "Outro", "success": "Sucesso", "unknown": "Desconhecido"}
            linhas = "".join(
                f'<tr><th scope="row">{nomes[c]}{" *" if r < 30 else ""}</th><td>{inteiro(r)}</td><td>{inteiro(a)}</td>'
                f'<td>{percentual(t)}</td></tr>' for c, r, a, t in resumo.itertuples())
            st.html('<div class="resultados"><table aria-label="Adesão por resultado anterior">'
                    '<thead><tr><th>Resultado anterior</th><th>Registros</th><th>Adesões</th><th>Taxa</th>'
                    '</tr></thead><tbody>' + linhas + '</tbody></table></div>')
            st.download_button("Exportar esta tabela", resumo.rename_axis("poutcome").to_csv(
                sep=";", decimal=","), file_name="adesao-por-resultado.csv", mime="text/csv", icon=":material/download:")
        else:
            st.info("Este recorte não tem registros. Altere um filtro ou use Limpar filtros.")
    explanatorias = [(nome, p) for nome, p in zip(NOMES_FIGURAS, ler_visualizacoes())
                     if nome.startswith("Explanatória") and configuracao_completa(p)]
    explanatorias.sort(key=lambda item: not item[1].get("responde_pergunta"))
    if explanatorias:
        st.subheader("O que o grupo quer mostrar")
        for nome, painel in explanatorias:
            if painel.get("responde_pergunta"):
                st.caption(f"{nome} · responde à pergunta de pesquisa")
            mostrar_figura(painel, dados, nome)
    with st.expander("Método"):
        st.write(f"Base completa: {inteiro(len(dados))} registros. O recorte inclui pdays diferente de −1. "
                 "A taxa divide as adesões pelos registros da mesma categoria após os filtros. "
                 "O resultado anterior desconhecido permanece identificado.")

elif pagina == "Exploração":
    st.html('<section class="pagina"><h1>Exploração da base</h1><p>Consulte as 17 variáveis ou cruze duas delas para investigar uma relação.</p></section>')
    st.caption("Nas estatísticas numéricas, pdays = −1 e previous = 0 (os mesmos registros, sem contato anterior) "
               "ficam fora dos cálculos de dias e de contatos. O CSV original é preservado. "
               "Os limites de outliers usam 1,5 × IQR.")
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
        sem_contato = consulta["pdays"].eq(-1)
        consulta[["pdays", "previous"]] = consulta[["pdays", "previous"]].mask(
            pd.concat([sem_contato, sem_contato], axis=1, keys=["pdays", "previous"]))
        if y in dados.select_dtypes("number"):
            st.dataframe(consulta.groupby(x, observed=True)[y].describe())
        else:
            st.dataframe(consulta.groupby([x, y], observed=True).size().unstack(fill_value=0))
    else:
        st.dataframe(resultados[opcoes[escolha]])

elif pagina == "Visualizações":
    st.html('<section class="pagina"><h1>Visualizações do grupo</h1><p>Quatro figuras exploratórias e duas explanatórias, com nota autoral do grupo.</p></section>')
    if "rascunho" not in st.session_state:
        st.session_state.rascunho = ler_visualizacoes()
    salvos = st.session_state.rascunho
    editar = st.toggle("Editar visualizações", value=not ARQUIVO_VIS.exists())
    paineis = list(salvos)
    escolhida = st.selectbox("Figura em edição", NOMES_FIGURAS) if editar else None
    for i, salvo in enumerate(salvos):
        nome = NOMES_FIGURAS[i]
        if editar and nome != escolhida:
            continue
        if editar:
            editor, previa = st.columns([1, 1.2], gap="large")
            with editor:
                def selecionar(rotulo, opcoes, campo, formato=str, ajuda=None):
                    anterior = salvo.get(campo)
                    indice = opcoes.index(anterior) if anterior in opcoes else None
                    return st.selectbox(rotulo, opcoes, index=indice, key=f"{i}_{campo}",
                                        format_func=formato, help=ajuda)

                painel = {"titulo": st.text_input("Título", salvo.get("titulo", ""), key=f"titulo{i}")}
                painel["tipo"] = selecionar("Tipo de gráfico", TIPOS, "tipo",
                                            ajuda="Linha só aceita eixos com ordem natural (mês, dia, idade, contagens).")
                tipo = painel["tipo"]
                if tipo:
                    painel["variavel"] = selecionar("Variável do eixo horizontal" if tipo != "Boxplot" else "Variável medida",
                                                    opcoes_eixo(tipo), "variavel", nome_campo)
                    if tipo in ("Barras", "Linha", "Barras agrupadas"):
                        painel["medida"] = selecionar("Medida", MEDIDAS, "medida")
                    if opcoes_grupo(tipo):
                        rotulo_grupo = "Séries (segunda variável)" if tipo == "Barras agrupadas" else "Separar por (opcional)"
                        painel["grupo"] = selecionar(rotulo_grupo, opcoes_grupo(tipo), "grupo", nome_campo)
                    if tipo in ("Histograma", "Boxplot"):
                        painel["limitar_p99"] = st.checkbox(
                            "Limitar o eixo ao percentil 99 (a figura informa quantos registros ficam de fora)",
                            salvo.get("limitar_p99", False), key=f"p99{i}")
                    if tipo in ("Barras", "Barras agrupadas"):
                        painel["rotulos"] = st.checkbox("Mostrar valores e n sobre as barras",
                                                        salvo.get("rotulos", True), key=f"rotulos{i}")
                painel["historico"] = st.checkbox("Apenas registros com contato anterior (pdays ≠ −1)",
                                                  salvo.get("historico", False), key=f"historico{i}")
                if tipo and painel.get("variavel"):
                    base_destaque = recorte(dados, painel)
                    # Nas barras e na linha, destaca-se uma categoria do eixo; nos demais, uma série.
                    coluna = painel["variavel"] if tipo in ("Barras", "Linha") else painel.get("grupo")
                    valores = ([str(v) for v in base_destaque.groupby(coluna, observed=True).size().index]
                               if coluna else [])
                    destaque = selecionar("Destaque pré-atentivo (cor)", ["(sem destaque)"] + valores, "destaque",
                                          ajuda="A categoria escolhida recebe cor de contraste e as demais ficam neutras.")
                    painel["destaque"] = None if destaque in (None, "(sem destaque)") else destaque
                    if painel["destaque"]:
                        painel["justificativa_destaque"] = st.text_area(
                            "Por que destacar essa categoria", salvo.get("justificativa_destaque", ""),
                            key=f"justdest{i}")
                if nome.startswith("Explanatória"):
                    painel["responde_pergunta"] = st.checkbox("Esta figura responde diretamente à pergunta de pesquisa",
                                                              salvo.get("responde_pergunta", False), key=f"resp{i}")
                st.markdown("**Nota analítica autoral** · escrita pelo grupo, sem IA.")
                for campo, rotulo in CAMPOS_NOTA.items():
                    painel[campo] = st.text_area(rotulo, salvo.get(campo, ""), key=f"{campo}{i}")
        else:
            previa = st.container()
            painel = salvo
        paineis[i] = painel
        with previa:
            if configuracao_completa(painel):
                st.subheader(nome)
                mostrar_figura(painel, dados, nome)
            elif editar:
                st.html('<div class="previsual"><strong>Prévia da figura</strong>'
                        '<p>Preencha título, tipo, eixo e, conforme o tipo, a medida ou a segunda variável.</p></div>')
            else:
                st.caption(f"{nome} · aguardando configuração do grupo.")
    if editar:
        st.session_state.rascunho = paineis
        completos = sum(configuracao_completa(p) and nota_completa(p) for p in paineis)
        responde = any(p.get("responde_pergunta") for p in paineis[4:])
        st.caption(f"{completos} de 6 visualizações com configuração e nota completa. "
                   f"Explanatória que responde à pergunta: {'marcada' if responde else 'ainda não marcada'}.")
        gravar, baixar = st.columns(2)
        with gravar:
            if st.button("Salvar em visualizacoes.json", type="primary"):
                ARQUIVO_VIS.write_text(json.dumps(paineis, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                st.success(f"Configuração gravada em {ARQUIVO_VIS.relative_to(RAIZ)}. Faça o commit do arquivo.")
        with baixar:
            st.download_button("Baixar configuração", json.dumps(paineis, ensure_ascii=False, indent=2),
                               file_name="visualizacoes.json", mime="application/json")

else:
    st.html('<section class="pagina"><h1>Parte Comum · Wine Quality</h1><p>K-Means sobre as 11 medidas padronizadas. '
            'Compare lado a lado o k do cotovelo e o k igual ao número de notas.</p></section>')
    st.caption("Mesmo procedimento de notebooks/parte_comum/kmeans_metricas.ipynb: StandardScaler, "
               "KMeans(n_init=10, random_state=42) e mapeamento de cada cluster para a nota majoritária. "
               "A discussão crítica está no notebook e no relatório.")

    @st.cache_data
    def preparar_vinhos():
        vinhos = carregar_vinhos()
        X = padronizar(vinhos)
        coords, variancia = projetar(X)
        inercias = {k: ajustar(X, k).inertia_ for k in range(2, 11)}
        return vinhos, X, coords, variancia, inercias

    @st.cache_data
    def passada(k):
        vinhos, X, *_ = preparar_vinhos()
        modelo = ajustar(X, k)
        return modelo.labels_, avaliar(vinhos, X, modelo.labels_)

    vinhos, X, coords, variancia, inercias = preparar_vinhos()
    fig, ax = plt.subplots(figsize=(9, 3.2), layout="constrained")
    ax.plot(list(inercias), list(inercias.values()), marker="o", color="#426D91", label="Inércia")
    for k, cor, rotulo in [(4, "#C2512E", "k do cotovelo (4)"), (7, "#266657", "k = número de notas (7)")]:
        ax.plot([k], [inercias[k]], marker="o", markersize=11, linestyle="none", color=cor, label=rotulo)
    ax.set(title="Método do Cotovelo", xlabel="Número de clusters (k)", ylabel="Inércia", xticks=list(inercias))
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False)
    st.pyplot(fig)
    plt.close(fig)

    colunas = st.columns(2, gap="large")
    for coluna, padrao, titulo in [(colunas[0], 4, "Passada 1 · k livre"), (colunas[1], 7, "Passada 2 · k fixo")]:
        with coluna:
            k = st.slider(f"{titulo}: k", 2, 10, padrao, key=f"k_{padrao}")
            rotulos_k, (contingencia, matriz, metricas_k, resumo_k) = passada(k)
            st.metric("Acurácia após o mapeamento", percentual(100 * resumo_k["acurácia"]))
            st.metric("Silhueta", f"{resumo_k['silhueta']:.3f}".replace(".", ","))
            fig, ax = plt.subplots(figsize=(6, 4.4), layout="constrained")
            for cluster in range(k):
                pontos = rotulos_k == cluster
                ax.scatter(coords[pontos, 0], coords[pontos, 1], s=6, alpha=.5, label=f"Cluster {cluster}")
            ax.set(title=f"{titulo} (k = {k}) · projeção PCA",
                   xlabel=f"PC1 ({variancia[0]:.1f}% da variância)", ylabel=f"PC2 ({variancia[1]:.1f}% da variância)")
            ax.legend(fontsize=7, markerscale=2, ncols=2, frameon=False)
            st.pyplot(fig)
            plt.close(fig)
            fig, ax = plt.subplots(figsize=(6, 4.4), layout="constrained")
            sns.heatmap(matriz, annot=True, fmt="d", cmap="Blues", cbar_kws={"label": "Amostras"}, ax=ax)
            ax.set_title(f"Matriz de confusão · k = {k}")
            st.pyplot(fig)
            plt.close(fig)
            st.dataframe(metricas_k.round(3))
            with st.expander("Notas reais por cluster"):
                st.dataframe(contingencia)

st.html('<footer class="rodape"><span>Bank Marketing · AVD 2026.2</span>'
        '<a href="https://archive.ics.uci.edu/dataset/222/bank+marketing" target="_blank" rel="noopener">'
        'Dados e dicionário na UCI ↗</a></footer>')
