# Parte Específica · Bank Marketing

Painel para gestores de campanhas. Segundo confirmação da equipe, a professora aprovou o dataset Bank Marketing submetido no checkpoint. A pergunta de pesquisa está na tela inicial. Usamos o arquivo original bank-full.csv, com delimitador ponto e vírgula, e o dicionário original bank-names.txt em data/parte_especifica/. Fonte: Moro, S., Rita, P. e Cortez, P. (2014), Bank Marketing, UCI Machine Learning Repository, https://doi.org/10.24432/C5K306 (CC BY 4.0).

Na raiz do repositório, usando um ambiente virtual com Python 3.11 ou superior:

```sh
python -m pip install pandas matplotlib streamlit
python src/parte_especifica/eda.py
python -m streamlit run src/parte_especifica/dashboard.py
```

O primeiro script reproduz as seis tabelas em out/parte_especifica/. A taxa usa a contagem de y igual a yes dividida pelo total de registros de cada categoria entre registros com pdays diferente de −1. Cada linha conta como um registro. Os valores unknown continuam identificados no quadro de estrutura. Nos resumos numéricos de pdays, o código desconsidera o marcador de ausência de contato anterior. As contagens fora dos limites de IQR são diagnósticos. No recorte com contato anterior, mantemos os cinco registros com poutcome igual a unknown em uma categoria própria, com contagem visível. Os registros com pdays igual a −1 permanecem na base completa. A equipe aprovou preservar as observações sinalizadas pelo IQR durante a inspeção e avaliar domínio e impacto antes de decidir qualquer exclusão.

Em **Visualizações**, a equipe escolhe o recorte, o tipo, os eixos e o título, confere as contagens e registra uma nota em cada um dos seis espaços. Pelo menos uma das duas explanatórias deve responder à pergunta aprovada. Baixe a configuração antes de fechar a sessão, salve-a como src/parte_especifica/visualizacoes.json e reabra o app para conferir o modo de apresentação. O colega responsável pelo relatório deve receber também o raciocínio do grupo sobre público, ausências, outliers, história e destaques visuais.

Apoio de IA para registrar na declaração: Codex, no uso de pandas, na interface Streamlit, no suporte técnico à renderização com Matplotlib e nos testes de execução. A equipe deve complementar o registro com as atividades que efetivamente realizar.
