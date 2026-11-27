"""Confere o repositório contra os requisitos do enunciado do Projeto Final de AVD 2026.2.

Uso, na raiz:  python src/verificar_entrega.py
Sai com código 1 se houver pendência automática. Os itens manuais aparecem no fim.
"""
# [IA] Claude – apoio na automação da conferência dos requisitos de entrega.
import json
import re
import subprocess
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src/parte_especifica"))
from graficos import configuracao_completa, nota_completa  # noqa: E402

falhas, avisos = [], []


def checar(condicao, mensagem):
    print(("  ok   " if condicao else "  FALTA ") + mensagem)
    if not condicao:
        falhas.append(mensagem)
    return condicao


def texto_pdf(caminho):
    try:
        return subprocess.run(["pdftotext", str(caminho), "-"], capture_output=True, text=True, check=True).stdout
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


print("Requisitos técnicos")
checar(sys.version_info >= (3, 11), f"Python 3.11+ (em uso: {sys.version.split()[0]})")
permitidas = {"pandas", "numpy", "matplotlib", "seaborn", "plotly", "scikit-learn", "streamlit", "jupyterlab", "nbconvert"}
pacotes = {re.split(r"[<>=\[ ]", linha)[0].strip().lower() for linha in (RAIZ / "requirements.txt").read_text().splitlines() if linha.strip()}
checar(pacotes <= permitidas, f"requirements.txt só com bibliotecas permitidas e ferramentas do Jupyter ({', '.join(sorted(pacotes))})")

print("\nEstrutura de pastas obrigatória")
for caminho in ["README.md", "requirements.txt", "docs/DECLARACAO_IA.pdf", "notebooks/parte_comum/eda.ipynb",
                "notebooks/parte_comum/kmeans_metricas.ipynb", "src/parte_especifica/eda.py",
                "src/parte_especifica/dashboard.py", "relatorio.pdf", "docs/MATRIZ_CONTRIBUICAO.md"]:
    checar((RAIZ / caminho).is_file(), caminho)
for pasta in ["data/parte_comum", "data/parte_especifica", "out/parte_comum", "out/parte_especifica"]:
    checar(any((RAIZ / pasta).iterdir()), f"{pasta}/ com arquivos")
for sobra in ["Relatorio-para-revisao.pdf", "relatorio-rascunho.pdf"]:
    rastreado = subprocess.run(["git", "ls-files", sobra], cwd=RAIZ, capture_output=True, text=True).stdout.strip()
    checar(not rastreado, f"{sobra} fora do repositório")

print("\nParte Comum")
for nome in ["eda", "kmeans_metricas"]:
    nb = json.loads((RAIZ / f"notebooks/parte_comum/{nome}.ipynb").read_text())
    codigo = [c for c in nb["cells"] if c["cell_type"] == "code" and "".join(c["source"]).strip()]
    erros = [o for c in codigo for o in c.get("outputs", []) if o["output_type"] == "error"]
    checar(all(c.get("execution_count") for c in codigo) and not erros, f"{nome}.ipynb executado inteiro e sem erros")
for figura in ["cotovelo.png", "passadas_pca.png", "matriz_confusao_k4.png", "matriz_confusao_k7.png"]:
    checar((RAIZ / "out/parte_comum" / figura).is_file(), f"out/parte_comum/{figura}")

print("\nParte Específica")
dados = pd.read_csv(RAIZ / "data/parte_especifica/bank-full.csv", sep=";")
checar(len(dados) >= 500 and dados.shape[1] >= 10, f"Dataset com ≥ 500 linhas e ≥ 10 colunas ({dados.shape[0]} × {dados.shape[1]})")
checar(len(dados.select_dtypes("number").columns) > 0 and len(dados.select_dtypes(exclude="number").columns) > 0,
       "Variáveis quantitativas e qualitativas")
arquivo_vis = RAIZ / "src/parte_especifica/visualizacoes.json"
paineis = json.loads(arquivo_vis.read_text()) if arquivo_vis.exists() else []
paineis = (paineis + [{} for _ in range(6)])[:6]
nomes = [f"Exploratória {i + 1}" for i in range(4)] + [f"Explanatória {i + 1}" for i in range(2)]
for nome, painel in zip(nomes, paineis):
    checar(configuracao_completa(painel) and nota_completa(painel),
           f"{nome}: título, tipo, eixos e nota (o que mostra, insight, por que o gráfico)")
    if painel.get("destaque"):
        checar(bool(str(painel.get("justificativa_destaque", "")).strip()), f"{nome}: justificativa do destaque")
checar(any(p.get("responde_pergunta") and configuracao_completa(p) for p in paineis[4:]),
       "Uma explanatória responde diretamente à pergunta de pesquisa")
textos = re.sub(r"<!--.*?-->", "", (RAIZ / "docs/relatorio_parte_especifica.md").read_text(), flags=re.S)
checar("[A PREENCHER" not in textos, "docs/relatorio_parte_especifica.md sem trechos [A PREENCHER PELO GRUPO]")

print("\nDocumentação e IA")
matriz = (RAIZ / "docs/MATRIZ_CONTRIBUICAO.md").read_text()
checar(not re.search(r"A preencher|A PREENCHER|completar nome|conferir nome", matriz), "Matriz de contribuição sem pendências")
declaracao = texto_pdf(RAIZ / "docs/DECLARACAO_IA.pdf")
if declaracao is None:
    avisos.append("pdftotext indisponível: confira a declaração manualmente.")
else:
    checar("Modelo de trabalho" not in declaracao and "deve conferir" not in declaracao,
           "Declaração sem texto de rascunho")
    checar("Claude" in declaracao, "Declaração registra o uso do Claude")
    checar("respectivas análises" not in declaracao, "Declaração sem registro de IA gerando análises (uso proibido)")
fonte_decl = (RAIZ / "docs/declaracao_ia_texto.md").read_text()
checar("[CONFIRMAR" not in re.sub(r"<!--.*?-->", "", fonte_decl, flags=re.S), "docs/declaracao_ia_texto.md sem itens [CONFIRMAR]")
for arquivo in sorted((RAIZ / "src").rglob("*.py")):
    if arquivo.name == "__init__.py":
        continue
    checar("# [IA]" in arquivo.read_text(), f"Marcação # [IA] em {arquivo.relative_to(RAIZ)}")
relatorio = texto_pdf(RAIZ / "relatorio.pdf") if (RAIZ / "relatorio.pdf").exists() else ""
if relatorio is not None and (RAIZ / "relatorio.pdf").exists():
    checar("A PREENCHER" not in relatorio and "RASCUNHO" not in relatorio and "Minuta" not in relatorio,
           "relatorio.pdf sem pendências nem marcas de rascunho")

autores = subprocess.run(["git", "log", "--format=%an"], cwd=RAIZ, capture_output=True, text=True).stdout.split("\n")
print("\nAutores de commits:", ", ".join(sorted({a for a in autores if a})))

print("\nConferência manual (o script não consegue verificar)")
for item in [
    "Os textos analíticos dos notebooks, as notas e os textos do relatório foram escritos pelo grupo, sem IA.",
    "As células do notebook feitas com apoio de IA estão marcadas com # [IA], como diz a declaração.",
    "A nova declaração foi assinada pelos quatro e substituiu docs/DECLARACAO_IA.pdf.",
    "Todos os integrantes sabem explicar cada trecho de código e cada resultado.",
    "Cada integrante postou o link do repositório no Classroom.",
]:
    print("  [ ] " + item)
for aviso in avisos:
    print("Aviso: " + aviso)
print(f"\n{len(falhas)} pendência(s) automática(s)." if falhas else "\nNenhuma pendência automática.")
sys.exit(1 if falhas else 0)
