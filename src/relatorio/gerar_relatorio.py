"""Gera relatorio.pdf na raiz a partir dos notebooks, das figuras e dos textos do grupo.

Uso, na raiz do repositório:
    python src/relatorio/gerar_relatorio.py             # versão final: recusa se houver pendências
    python src/relatorio/gerar_relatorio.py --rascunho  # gera relatorio-rascunho.pdf mesmo com pendências

Fontes do conteúdo:
- Parte Comum: textos e resultados de notebooks/parte_comum/eda.ipynb e kmeans_metricas.ipynb
  (o código fica oculto; os notebooks precisam estar executados).
- Parte Específica: docs/relatorio_parte_especifica.md (textos do grupo) e
  src/parte_especifica/visualizacoes.json (seis figuras e notas do grupo).
O PDF é impresso pelo Google Chrome ou Chromium em modo headless.
"""
# [IA] Claude – apoio com nbformat/nbconvert e impressão em PDF para montar o relatório.
import argparse
import base64
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import nbformat  # noqa: E402
import pandas as pd  # noqa: E402
from nbconvert import HTMLExporter  # noqa: E402

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src/parte_especifica"))
from eda import carregar_dados, resumir_adesao, tabelas  # noqa: E402
from graficos import CAMPOS_NOTA, configuracao_completa, desenhar, nota_completa  # noqa: E402

NOTEBOOKS = [RAIZ / "notebooks/parte_comum/eda.ipynb", RAIZ / "notebooks/parte_comum/kmeans_metricas.ipynb"]
TEXTOS = RAIZ / "docs/relatorio_parte_especifica.md"
VISUALIZACOES = RAIZ / "src/parte_especifica/visualizacoes.json"
DECLARACAO = RAIZ / "docs/declaracao_ia_texto.md"
MARCADOR = "[A PREENCHER"
NOMES = [f"Exploratória {i + 1}" for i in range(4)] + [f"Explanatória {i + 1}" for i in range(2)]

CSS = """
<style>
@page { size: A4; margin: 18mm 16mm; }
body { font-family: Georgia, 'Times New Roman', serif; font-size: 11pt; }
.jp-Notebook { padding: 0 !important; }
.jp-Cell { padding: 0 !important; break-inside: auto; }
.jp-OutputArea-output img { max-width: 100% !important; break-inside: avoid; }
.jp-RenderedHTMLCommon table { font-size: 7.5pt; }
.jp-OutputArea-output, .jp-RenderedHTMLCommon { overflow: visible !important; }
.quebra { break-before: page; }
h1 { break-before: page; } h1:first-of-type { break-before: auto; }
.pendente { background: #fff1c2; padding: 2px 4px; }
.aviso-rascunho { border: 2px solid #b44; padding: 8px 12px; color: #b44; font-weight: bold; }
</style>
"""


def md(texto):
    return nbformat.v4.new_markdown_cell(texto)


def saida_html(html):
    celula = nbformat.v4.new_code_cell("")
    celula.outputs = [nbformat.v4.new_output("display_data", data={"text/html": html})]
    return celula


def saida_imagem(fig):
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    celula = nbformat.v4.new_code_cell("")
    celula.outputs = [nbformat.v4.new_output(
        "display_data", data={"image/png": base64.b64encode(buffer.getvalue()).decode()})]
    return celula


def tabela_html(df, casas=2):
    return df.round(casas).to_html(classes="dataframe", border=0)


def celulas_parte_comum():
    celulas = []
    for caminho in NOTEBOOKS:
        nb = nbformat.read(caminho, as_version=4)
        for celula in nb.cells:
            if celula.cell_type == "code" and "[IA] Claude – recarga da base" in celula.source:
                continue  # carga repetida no segundo notebook
            if celula.cell_type == "markdown" and celula.source.startswith("# Wine Quality · K-Means"):
                continue
            celulas.append(celula)
    return celulas


def pendencias_visualizacoes(paineis):
    pendentes = []
    for nome, painel in zip(NOMES, paineis):
        if not configuracao_completa(painel):
            pendentes.append(f"{nome}: configuração incompleta")
        elif not nota_completa(painel):
            pendentes.append(f"{nome}: nota analítica incompleta (o que mostra, insight, por que o gráfico)")
        elif painel.get("destaque") and not str(painel.get("justificativa_destaque", "")).strip():
            pendentes.append(f"{nome}: destaque sem justificativa")
    if not any(p.get("responde_pergunta") and configuracao_completa(p) for p in paineis[4:]):
        pendentes.append("Nenhuma explanatória marcada como resposta à pergunta de pesquisa")
    return pendentes


def celulas_figuras(paineis, dados, indices):
    celulas = []
    for i in indices:
        painel, nome = paineis[i], NOMES[i]
        if not configuracao_completa(painel):
            celulas.append(md(f"**Figura {i + 1} · {nome}.** <span class='pendente'>[A PREENCHER PELO GRUPO: figura não configurada no dashboard]</span>"))
            continue
        fig, _, avisos = desenhar(painel, dados)
        celulas.append(md(f"**Figura {i + 1} · {nome}.** {painel['titulo']}"))
        celulas.append(saida_imagem(fig))
        partes = [f"*{a}*" for a in avisos]
        if painel.get("responde_pergunta"):
            partes.append("*Esta figura responde diretamente à pergunta de pesquisa.*")
        if painel.get("destaque"):
            partes.append(f"**Destaque visual.** {painel.get('justificativa_destaque') or '[A PREENCHER PELO GRUPO]'}")
        for campo, rotulo in CAMPOS_NOTA.items():
            partes.append(f"**{rotulo}.** {painel.get(campo) or '[A PREENCHER PELO GRUPO]'}")
        celulas.append(md("\n\n".join(partes)))
    return celulas


def celulas_parte_especifica(texto, paineis):
    dados = carregar_dados()
    meses = "jan feb mar apr may jun jul aug sep oct nov dec".split()
    dados["month"] = pd.Categorical(dados["month"], categories=meses, ordered=True)
    resultado = tabelas(dados)
    recorte = dados.loc[dados["pdays"].ne(-1)]
    ficha = pd.DataFrame({"valor": {
        "Registros": f"{len(dados):,}".replace(",", "."),
        "Colunas": dados.shape[1],
        "Quantitativas": len(dados.select_dtypes("number").columns),
        "Qualitativas": len(dados.select_dtypes(exclude="number").columns),
        "Registros com contato anterior (pdays ≠ −1)": f"{len(recorte):,}".replace(",", "."),
    }})
    blocos = {
        "{{FICHA_BASE}}": [saida_html(ficha.to_html(border=0))],
        "{{TABELA_ESTRUTURA}}": [saida_html(tabela_html(resultado["estrutura"]))],
        "{{TABELA_IQR}}": [saida_html(tabela_html(resultado["limites_iqr"]))],
        "{{TABELA_ADESAO}}": [saida_html(tabela_html(resumir_adesao(recorte)))],
        "{{FIGURAS_EXPLORATORIAS}}": celulas_figuras(paineis, dados, range(4)),
        "{{FIGURAS_EXPLANATORIAS}}": celulas_figuras(paineis, dados, range(4, 6)),
    }
    texto = re.sub(r"<!--.*?-->", "", texto, flags=re.S)
    celulas = []
    for parte in re.split(r"(\{\{[A-Z_]+\}\})", texto):
        if parte in blocos:
            celulas.extend(blocos[parte])
        elif parte.strip():
            destacado = re.sub(r"(\[A PREENCHER[^\]]*\])", r"<span class='pendente'>\1</span>", parte.strip())
            celulas.append(md(destacado))
    return celulas


def localizar_chrome():
    candidatos = [os.environ.get("CHROME"), shutil.which("google-chrome"), shutil.which("chromium"),
                  shutil.which("chromium-browser"), shutil.which("chrome"),
                  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                  r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                  r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                  "/opt/pw-browsers/chromium/chrome-linux/chrome"]
    candidatos += [str(p) for p in Path("/opt/pw-browsers").glob("chromium-*/chrome-linux*/chrome")]
    return next((c for c in candidatos if c and Path(c).exists()), None)


def imprimir_pdf(html, destino):
    chrome = localizar_chrome()
    if not chrome:
        alternativo = destino.with_suffix(".html")
        alternativo.write_text(html, encoding="utf-8")
        sys.exit(f"Chrome/Chromium não encontrado. HTML salvo em {alternativo}; abra no navegador e use "
                 "Imprimir > Salvar como PDF, ou defina a variável CHROME com o caminho do navegador.")
    with tempfile.TemporaryDirectory() as pasta:
        pagina = Path(pasta) / "relatorio.html"
        pagina.write_text(html, encoding="utf-8")
        subprocess.run([chrome, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                        f"--print-to-pdf={destino}", pagina.as_uri()],
                       check=True, capture_output=True, timeout=180)


def gerar_declaracao():
    from nbconvert.filters.markdown_mistune import markdown2html_mistune

    texto = re.sub(r"<!--.*?-->", "", DECLARACAO.read_text(encoding="utf-8"), flags=re.S)
    if "[CONFIRMAR" in texto:
        sys.exit(f"{DECLARACAO.relative_to(RAIZ)} ainda tem itens [CONFIRMAR ...]. Resolva-os antes de gerar o PDF.")
    estilo = ("<style>@page{size:A4;margin:20mm} body{font-family:Georgia,serif;font-size:11pt;line-height:1.45}"
              "table{width:100%;border-collapse:collapse} td,th{border:1px solid #999;padding:6px;height:2.2em}"
              "td:last-child{width:45%}</style>")
    corpo = re.sub(r"<a class=.anchor-link.*?</a>", "", markdown2html_mistune(texto))
    html = f"<!doctype html><html><head><meta charset='utf-8'>{estilo}</head><body>{corpo}</body></html>"
    destino = RAIZ / "docs/DECLARACAO_IA_para_assinar.pdf"
    imprimir_pdf(html, destino)
    print(f"Gerado: {destino.relative_to(RAIZ)}. Depois de assinado pelos quatro, substitua docs/DECLARACAO_IA.pdf.")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--rascunho", action="store_true", help="gera relatorio-rascunho.pdf mesmo com pendências")
    parser.add_argument("--declaracao", action="store_true",
                        help="gera docs/DECLARACAO_IA_para_assinar.pdf a partir de docs/declaracao_ia_texto.md")
    args = parser.parse_args()
    if args.declaracao:
        gerar_declaracao()
        return

    texto = TEXTOS.read_text(encoding="utf-8")
    paineis = json.loads(VISUALIZACOES.read_text(encoding="utf-8")) if VISUALIZACOES.exists() else []
    paineis = (paineis + [{} for _ in range(6)])[:6]
    pendencias = pendencias_visualizacoes(paineis)
    textos_pendentes = len(re.findall(re.escape(MARCADOR), re.sub(r"<!--.*?-->", "", texto, flags=re.S)))
    if textos_pendentes:
        pendencias.append(f"{TEXTOS.relative_to(RAIZ)}: {textos_pendentes} trecho(s) [A PREENCHER PELO GRUPO]")
    for caminho in NOTEBOOKS:
        nb = nbformat.read(caminho, as_version=4)
        if any(c.cell_type == "code" and c.source.strip() and not c.get("outputs") for c in nb.cells):
            pendencias.append(f"{caminho.relative_to(RAIZ)}: há células sem saída; execute o notebook inteiro")

    if pendencias and not args.rascunho:
        print("relatorio.pdf não foi gerado. Pendências:")
        print("\n".join(f"- {p}" for p in pendencias))
        sys.exit(1)

    capa = ("# Análise e Visualização de Dados · Projeto final AV2 · 2026.2\n\n"
            "Parte Comum: Wine Quality · EDA e agrupamento com K-Means. "
            "Parte Específica: Bank Marketing · exploração, storytelling e dashboard.")
    celulas = [md(capa)]
    if pendencias:
        celulas.append(md("<div class='aviso-rascunho'>RASCUNHO · pendências: "
                          + "; ".join(pendencias) + "</div>"))
    celulas += celulas_parte_comum() + [md("<div class='quebra'></div>")] + celulas_parte_especifica(texto, paineis)
    nb = nbformat.v4.new_notebook(cells=celulas, metadata={"title": "Relatório · AVD 2026.2"})

    exportador = HTMLExporter(template_name="lab", exclude_input=True, exclude_input_prompt=True,
                              exclude_output_prompt=True)
    exportador.mathjax_url = ""
    html, _ = exportador.from_notebook_node(nb)
    html = html.replace("</head>", CSS + "</head>")

    destino = RAIZ / ("relatorio-rascunho.pdf" if pendencias else "relatorio.pdf")
    imprimir_pdf(html, destino)
    print(f"Gerado: {destino.relative_to(RAIZ)}" + (f" ({len(pendencias)} pendência(s))" if pendencias else ""))


if __name__ == "__main__":
    main()
