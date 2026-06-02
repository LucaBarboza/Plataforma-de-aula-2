import os
import sys
import json
import re
import time
from google import genai
from google.genai import types

# ==============================================================================
# FALLBACK DE SEGURANÇA PARA A CHAVE DE API (GEMINI_API_KEY)
# ==============================================================================
def carregar_chave_api():
    """Garante a leitura da API key a partir do ambiente, do st.secrets (Streamlit Cloud) ou do secrets.toml local."""
    if "GEMINI_API_KEY" in os.environ and os.environ["GEMINI_API_KEY"].strip():
        return True
        
    # Tenta obter do st.secrets do Streamlit
    try:
        import streamlit as st
        if "GEMINI_API_KEY" in st.secrets:
            val = st.secrets["GEMINI_API_KEY"]
            if val and val.strip():
                os.environ["GEMINI_API_KEY"] = val.strip()
                return True
    except Exception:
        pass
        
    path = os.path.join(".streamlit", "secrets.toml")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                for linha in f:
                    if "GEMINI_API_KEY" in linha:
                        match = re.search(r'(?:GEMINI_API_KEY\s*=\s*["\'])(.*?)(?:["\'])', linha)
                        if match:
                            os.environ["GEMINI_API_KEY"] = match.group(1).strip()
                            print(f"[KEY] Chave de API carregada com sucesso a partir de '{path}'.")
                            return True
        except Exception as e:
            print(f"[ALERTA] Erro ao tentar ler {path}: {e}")
    return False

# Inicializa o carregamento da chave de API no escopo do módulo
carregar_chave_api()

# ==============================================================================
# FASE A: FUNÇÃO ESPECIALISTA EM PROCESSAR UMA FATIA DE TEORIA
# ==============================================================================
def programar_fatia_teoria(dados_subtopico: dict, nome_simulador: str, motor_grafico: str = "plotly", chave_suffix: str = "") -> str:
    # Garante a inicialização da chave
    carregar_chave_api()
    client = genai.Client()
    
    if motor_grafico.lower() == "seaborn":
        grafico_especifico = f"""Crie um gráfico Seaborn/Matplotlib premium altamente científico e estilizado. 
        Configure o tema usando `sns.set_theme(style="whitegrid", rc={{"grid.linestyle": "--", "grid.alpha": 0.5, "grid.color": "#E2E8F0"}})` e use a fonte 'sans-serif'.
        Use `fig, ax = plt.subplots(figsize=(10, 5), dpi=300)` e garanta a remoção de bordas com `sns.despine(left=True, bottom=False, right=True, top=True)`.
        Assegure que as cores usadas sigam a paleta estrita: PRIMARY_BLUE = "#1E3A8A", SECONDARY_GREEN = "#10B981", WARNING_AMBER = "#F59E0B", CRITICAL_RED = "#991B1B".
        Renderize no Streamlit usando `st.pyplot(fig)`. Libere a memória no final chamando `plt.close(fig)`."""
    else:
        grafico_especifico = f"""Crie um gráfico Plotly premium altamente interativo e condizente com a proposta. 
        Configure o gráfico com eixos travados para mobile se for um gráfico 2D (`fixedrange=True` nas propriedades de `xaxis` e `yaxis` do `fig.update_layout()`, NUNCA no layout raiz). Se for um gráfico 3D (que utiliza scene=dict(...)), NUNCA use fixedrange em scene, xaxis, yaxis ou zaxis, pois o Plotly não suporta essa propriedade em gráficos 3D e lançará um ValueError.
        Assegure que as cores usadas sigam a paleta estrita: PRIMARY_BLUE = "#1E3A8A", SECONDARY_GREEN = "#10B981", WARNING_AMBER = "#F59E0B", CRITICAL_RED = "#991B1B".
        Renderize no Streamlit usando `st.plotly_chart(fig, use_container_width=True, key=r"plotly_chart_{chave_suffix}")`."""

    prompt = f"""
    Você é um UI/UX Designer Frontend especialista em Streamlit para Educação Executiva.
    Sua missão é ler o JSON do subtópico, pegar a prosa densa recebida e criar um layout de livro acadêmico de luxo com um "ritmo de leitura" dinâmico e elegante.
    
    O código que você gerar será injetado diretamente dentro do bloco 'with tab_conteudo:' do script principal.
    
    CRÍTICO - CÓDIGO 100% ESTÁTICO E HARDCODED (TOLERÂNCIA ZERO PARA AVALIAÇÕES DINÂMICAS OU LOOPS EM TEMPO DE EXECUÇÃO):
    É TERMINANTEMENTE PROIBIDO gerar código Python que faça referências ou tente ler variáveis, parâmetros ou dicionários dinâmicos (como tentar acessar `data`, `dados_subtopico`, `pagina`, `exemplo`, `passo` em tempo de execução no script gerado).
    Toda prosa teórica, títulos, equações matemáticas, exemplos práticos e laudos contidos no JSON recebido devem ser extraídos durante a geração e escritos diretamente como **strings literais estáticas (hardcoded)** usando o prefixo 'r' (raw string) no código Streamlit gerado.
    
    Se houver listas de exemplos (`exemplos_praticos_ricos`) ou deduções (`deducao_analitica_linhas`), você deve iterar sobre elas durantes a geração do código e gerar fisicamente blocos de código estáticos sequenciais para cada item individualmente na string de saída (por exemplo, gerando múltiplos blocos `with st.container(border=True):` estáticos com os textos reais já escritos por extenso no código Python, sem loops `for` no script final).
    
    DIRETRIZES OBRIGATÓRIAS DE LAYOUT (RITMO E QUEBRA DE TEXTO):
    1. PARCELAMENTO DE TEXTO: Nunca exiba mais de 2 parágrafos corridos seguidos. Quebre a monotonia do texto transformando explicações sequenciais, propriedades ou pressupostos em listas de tópicos (bullet points) limpas.
    2. BLOCOS COLORIDOS DE DESTAQUE: 
       - Use as classes HTML/CSS injetadas no topo do script para envelopar partes do texto.
       - Fragmentos teóricos muito complexos ou intuições devem entrar dentro de caixas usando os estilos customizados ou os componentes nativos (`st.info()`, `st.warning()`).
    3. CONTAINER PARA EXEMPLOS RESOLVIDOS: Cada exemplo prático da lista DEVE ser isolado visualmente dentro de um `with st.container(border=True):`. Use títulos em markdown bem definidos (ex: "##### 📖 Exemplo Prático: ...") e use `st.success()` ou um bloco destacado para a conclusão/laudo comercial do exemplo.
    4. FORMALISMO MATEMÁTICO: Centralize e destaque todas as equações principais em blocos de `st.latex(r"...")`.
    5. TABELAS E DATAFRAMES ESTILIZADOS (RITMO E ESTRUTURA): Sempre que o JSON contiver dados formatados como tabelas Markdown (ou estruturas comparativas/descritivas de dados), você deve convertê-los e renderizá-los como tabelas Streamlit nativas premium (`st.dataframe` ou `st.table`) criadas dinamicamente com Pandas (`pd.DataFrame`). Nunca exiba dados tabulares estruturados como puro texto corrido sem necessidade.
    
    REGRAS ESTRITAS DE INTERFACE (TOLERÂNCIA ZERO PARA NOMES DE SEÇÕES GENÉRICOS):
    - É terminantemente proibido utilizar títulos de seções genéricos como 'Exemplos Práticos', 'Demonstração Analítica e Propriedades' ou 'Formalismo Matemático'.
    - Todos os cabeçalhos de seções (`st.subheader`, `st.markdown("### ...")`) devem ser contextualizados dinamicamente com o tema específico do subtópico (Exemplo: em vez de 'Demonstração Analítica e Propriedades', use '### 📐 O Coração Matemático: [Nome do Subtópico]'; em vez de 'Exemplos Práticos', use '### 📈 Casos de Aplicação Prática: [Nome do Subtópico]').
    
    1. CABEÇALHO DO SUBTÓPICO: Crie o cabeçalho usando `st.header(r"[Título do Subtópico literal e estático]")` (NUNCA acesse dinamicamente variáveis como `data["titulo_subtopico"]`).
    
    2. DEMONSTRAÇÃO FORA DO EXPANDER: É terminantemente proibido colocar as deduções matemáticas em expanders. Exiba cada linha contida no campo 'deducao_analitica_linhas' de forma estática sequencialmente usando `st.latex(r"...")` uma abaixo da outra, intercaladas por pequenas frases explicativas que conectem os passos logicamente.
    
    3. CARDS DE EXEMPLOS RESOLVIDOS: Para cada item da lista 'exemplos_praticos_ricos', monte uma seção estruturada contínua física utilizando um container com borda:
       with st.container(border=True):
           st.markdown(r"##### 📖 Exemplo Resolvido: [Título do Exemplo]")
           st.markdown(r"[Enunciado literal e estático do exemplo]")
           st.latex(r"[Dados sumarizados literais e estáticos em LaTeX]")
           st.markdown(r"**Desenvolvimento Aritmético Passo a Passo:**")
           st.markdown(r"- [Passo 1 literal e estático]")
           st.markdown(r"- [Passo 2 literal e estático]")
           st.success(r"[Conclusão e laudo comercial literal e estático]")
            
    4. GRÁFICOS NO MEIO DO TEXTO: Se o parâmetro 'nome_simulador' for fornecido (não vazio), insira os sliders e o gráfico correspondente a esse conceito (utilizando a biblioteca '{motor_grafico}') imediatamente após o bloco de formalismo matemático (`st.info` / `st.latex`), dividindo as variáveis em colunas elegantes (`st.columns`) para que os seletores/sliders não fiquem gigantes na tela.
       O simulador a ser programado é: '{nome_simulador}'.
       {grafico_especifico}
       Use chaves únicas baseadas no título do subtópico para os sliders do Streamlit para evitar DuplicateWidgetID.
        
    5. TRATAMENTO DE LATEX E BARRAS INVERTIDAS: Use raw strings (prefixadas por 'r', ex: st.write(r"...") ou st.markdown(r"...")) em absolutamente todos os componentes markdown e latex para evitar SyntaxWarnings ou quebras de renderização no Streamlit. NUNCA use f-strings dinâmicas combinadas com chaves matemáticas (como rf"...") pois isso quebra a sintaxe do Python.
     
    6. PROIBIÇÃO DE SCIKIT-LEARN: É terminantemente proibido importar, utilizar ou depender de `sklearn` ou `scikit-learn` no código gerado. Para qualquer cálculo estatístico ou ajuste de regressão linear nos simuladores, utilize `scipy.stats` (como `stats.linregress`) ou álgebra linear/cálculo manual com `numpy` (ambas já estão importadas no script pai).
    
    7. EVITAR TRIPLE QUOTES QUEBRADOS E CARACTERES ESCAPADOS INCORRETOS: Garanta que todas as strings de texto longas geradas em Python sejam raw strings válidas (ex: r\"\"\"texto\"\"\"). Se o texto contiver aspas triplas internas, substitua-as por aspas normais simples ou duplas. Não termine uma raw string com uma barra invertida (ex: r"texto\"), pois isso causa erro de sintaxe no compilador do Python (a barra invertida antes das aspas finais escapa as aspas, deixando a string aberta).
    
    8. COMPATIBILIDADE SINTÁTICA TOTAL: Seu código gerado DEVE ser código Python 3.12+ sintaticamente correto. Ele será analisado pelo parser AST do Python. Não inclua comentários fora de blocos válidos, nem códigos incompletos ou blocos interrompidos.
    
    9. Escreva o seu código iniciando no recuo base de 0 espaços. O orquestrador cuidará do alinhamento.
    
    Retorne APENAS o código Python puro dentro do bloco de marcação:
    ```python
    # Seu código aqui
    ```
    """
    
    config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_level="high"),
        temperature=1.0
    )
    
    max_tentativas = 5
    for tentativa in range(max_tentativas):
        try:
            resposta = client.models.generate_content(
                model="gemini-3.1-flash-lite",
                contents=[json.dumps(dados_subtopico, ensure_ascii=False), prompt],
                config=config
            )
            
            match = re.search(r"```python\s*(.*?)\s*```", resposta.text, re.DOTALL)
            return match.group(1).strip() if match else resposta.text.strip()
        except Exception as e:
            print(f"[AVISO] Tentativa {tentativa+1}/{max_tentativas} falhou na fatia de teoria: {e}")
            if tentativa < max_tentativas - 1:
                tempo_espera = 2 ** tentativa
                print(f"[AVISO] Aguardando {tempo_espera}s antes de tentar novamente...")
                time.sleep(tempo_espera)
            else:
                print(f"[ERRO] Todas as {max_tentativas} tentativas falharam na fatia de teoria: {e}")
                return f"# Falha na geracao do subtopico apos {max_tentativas} tentativas: {e}"

# ==============================================================================
# FASE B: FUNÇÃO ESPECIALISTA EM PROCESSAR A FATIA DE EXERCÍCIOS
# ==============================================================================
def programar_fatia_exercicios(dados_exercicios: dict) -> str:
    carregar_chave_api()
    client = genai.Client()
    
    prompt = """
    Você é um Engenheiro de Software especialista em interfaces educacionais interativas no Streamlit.
    Sua tarefa é gerar o código Python/Streamlit interativo para renderizar a aba de exercícios da aula.
    
    O código gerado será injetado diretamente dentro do bloco 'with tab_exercicios:' do script principal.
    
    CRÍTICO - DESACOPLAMENTO DE DADOS (TOLERÂNCIA ZERO PARA TRANSCRIÇÃO OU HARDCODING DOS DADOS DO CADERNO):
    É TERMINANTEMENTE PROIBIDO transcrever, copiar ou escrever no código gerado os textos, enunciados, alternativas ou gabaritos das questões de forma estática (hardcoded). 
    Assuma que um dicionário chamado 'dados_exercicios' já foi carregado e está disponível no escopo atual. Este dicionário possui a seguinte estrutura de dados:
    {
        "topico_aula": "Tema",
        "questoes_multipla_escolha": [
            {
                "enunciado": "...",
                "alternativas": {"A": "...", "B": "...", ...},
                "alternativa_correta": "A",
                "dica": "...",
                "gabarito_comentado": "..."
            }
        ],
        "questoes_discursivas": [
            {
                "enunciado": "...",
                "dica": "...",
                "gabarito_passo_a_passo": ["Passo 1", "Passo 2", ...]
            }
        ]
    }
    
    REGRAS DE INTERATIVIDADE E SEGURANÇA CONTRA KEYERRORS:
    1. Crie uma interface interativa que itera dinamicamente sobre a lista 'dados_exercicios["questoes_multipla_escolha"]'.
       - Transcreva e monte as alternativas utilizando `st.radio()` com chaves únicas baseadas no índice da iteração (key=f"radio_mcq_{i}").
       - Crie um botão de dica usando a estrutura de acesso seguro: `st.info(questao.get("dica", "Dica indisponível"))` ativado por um `st.button()` com chave única.
       - Crie um botão de verificação: `if st.button("✅ Verificar Resposta", key=...):` que extrai a letra marcada pelo aluno e exibe `st.success("Correto! Muito bem.")` ou `st.error` com explicação a partir de questao.get("alternativa_correta").
       - Oculte o gabarito comentado dentro de um `st.expander("✅ Ver Gabarito Comentado")`. Você DEVE extrair as chaves do dicionário usando sempre o método seguro `.get("gabarito_comentado", "Gabarito indisponível")` para evitar KeyErrors.
    2. Crie uma interface para iterar sobre a lista 'dados_exercicios["questoes_discursivas"]'.
       - Crie um campo `st.text_area("Sua resposta:", key=...)`.
       - Renderize a dica de forma segura com `.get("dica", "Dica indisponível")` num botão de dica.
       - Oculte a resolução detalhada passo a passo dentro de um `st.expander("✅ Ver Resolução Detalhada")` iterando de forma segura sobre a lista obtida por `.get("gabarito_passo_a_passo", [])`.
    3. NÃO inclua importações globais ou redefinição de variáveis globais. O código deve iniciar no recuo de 0 espaços.
    
    4. SEGURANÇA SINTÁTICA E COMPATIBILIDADE SINTÁTICA TOTAL: Seu código gerado DEVE ser código Python 3.12+ sintaticamente correto. Nunca coloque aspas triplas dentro de outras aspas triplas sem escapar, e evite colocar barras invertidas no final de raw strings (ex: r"texto\"). Não inclua comentários soltos ou blocos incompletos.
    
    Retorne APENAS o código Python puro dentro do bloco:
    ```python
    # Seu código aqui
    ```
    """
    
    config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_level="high"),
        temperature=1.0
    )
    
    max_tentativas = 5
    for tentativa in range(max_tentativas):
        try:
            resposta = client.models.generate_content(
                model="gemini-3.1-flash-lite",
                contents=[json.dumps(dados_exercicios, ensure_ascii=False), prompt],
                config=config
            )
            
            match = re.search(r"```python\s*(.*?)\s*```", resposta.text, re.DOTALL)
            return match.group(1).strip() if match else resposta.text.strip()
        except Exception as e:
            print(f"[AVISO] Tentativa {tentativa+1}/{max_tentativas} falhou na fatia de exercicios: {e}")
            if tentativa < max_tentativas - 1:
                tempo_espera = 2 ** tentativa
                print(f"[AVISO] Aguardando {tempo_espera}s antes de tentar novamente...")
                time.sleep(tempo_espera)
            else:
                print(f"[ERRO] Todas as {max_tentativas} tentativas falharam na fatia de exercicios: {e}")
                return f"# Falha na geracao de exercicios apos {max_tentativas} tentativas: {e}"

def validar_execucao_codigo(codigo_python: str):
    """
    Tenta executar o código gerado em um ambiente mockado para detectar erros de runtime
    (como chamadas de layout inválidas no Plotly, erros de tipo, variáveis indefinidas, etc.)
    antes de salvar o arquivo no disco.
    """
    import numpy as np
    import pandas as pd
    import scipy.stats as stats
    from scipy.stats import norm
    import plotly.graph_objects as go
    import plotly.express as px
    import json
    import base64
    
    # 1. Definição do Mock de Streamlit e Valores
    class MockValue:
        def __add__(self, other): return self
        def __radd__(self, other): return self
        def __sub__(self, other): return self
        def __rsub__(self, other): return self
        def __mul__(self, other): return self
        def __rmul__(self, other): return self
        def __truediv__(self, other): return self
        def __rtruediv__(self, other): return self
        def __pow__(self, other): return self
        def __rpow__(self, other): return self
        def __neg__(self): return self
        def __pos__(self): return self
        def __abs__(self): return self
        def __getitem__(self, item): return self
        def __setitem__(self, key, value): pass
        def __len__(self): return 1
        def __iter__(self): return iter([self])
        def __lt__(self, other): return False
        def __le__(self, other): return False
        def __gt__(self, other): return False
        def __ge__(self, other): return False
        def __eq__(self, other): return True
        def __ne__(self, other): return False
        def __float__(self): return 1.0
        def __int__(self): return 1
        def __str__(self): return "1.0"

    class MockStreamlitWidget:
        def __getattr__(self, name): return MockStreamlitWidget()
        def __enter__(self): return self
        def __exit__(self, exc_type, exc_val, exc_tb): pass
        def __call__(self, *args, **kwargs): return MockValue()
        def __iter__(self): return iter([MockStreamlitWidget(), MockStreamlitWidget()])

    class MockStreamlit:
        def __init__(self):
            self.sidebar = MockStreamlitWidget()
        def __getattr__(self, name):
            if name in ['columns', 'tabs']:
                def func(spec, *args, **kwargs):
                    if isinstance(spec, int):
                        return [MockStreamlitWidget() for _ in range(spec)]
                    else:
                        return [MockStreamlitWidget() for _ in range(len(spec))]
                return func
            return MockStreamlitWidget()

    # Mocks para Matplotlib / Seaborn
    class MockPlot:
        def __getattr__(self, name):
            return lambda *args, **kwargs: MockPlot()
        def __enter__(self): return self
        def __exit__(self, exc_type, exc_val, exc_tb): pass

    globals_dict = {
        'st': MockStreamlit(),
        'np': np,
        'pd': pd,
        'go': go,
        'px': px,
        'stats': stats,
        'norm': norm,
        'plt': MockPlot(),
        'sns': MockPlot(),
        'json': json,
        'base64': base64,
        '__name__': '__main__'
    }
    
    # Executa o código. Se disparar qualquer erro, nós capturamos e levantamos.
    exec(codigo_python, globals_dict)

# ==============================================================================
# FASE C: ORQUESTRADOR LOCAL DE MONTAGEM E COMPILAÇÃO (PYTHON SEWING)
# ==============================================================================
def compilar_aula_completa_por_fatias(caminho_teoria_lapidada: str, caminho_exercicios: str, motor_grafico: str = "plotly"):
    if not os.path.exists(caminho_teoria_lapidada) or not os.path.exists(caminho_exercicios):
        print("[ERRO] Erro critico: Payloads de entrada ausentes no diretorio.")
        return

    with open(caminho_teoria_lapidada, "r", encoding="utf-8") as f:
        teoria = json.load(f)
    with open(caminho_exercicios, "r", encoding="utf-8") as f:
        exercicios = json.load(f)
        
    import base64
    
    # Serialização 100% segura dos metadados da aula para evitar SyntaxError por conta de aspas ou caracteres especiais
    metadata = {
        "tema_global": teoria["tema_global"],
        "referencias_bibliograficas_finais": teoria.get("referencias_bibliograficas_finais", [])
    }
    metadata_json = json.dumps(metadata, ensure_ascii=False)
    metadata_b64 = base64.b64encode(metadata_json.encode("utf-8")).decode("utf-8")

    # Serialização 100% segura dos exercícios para evitar quebras por aspas triplas ou caracteres especiais
    exercicios_json = json.dumps(exercicios, ensure_ascii=False)
    exercicios_b64 = base64.b64encode(exercicios_json.encode("utf-8")).decode("utf-8")

    print(f"\n[OK] [Orquestrador Local] Compilando a aplicacao Streamlit por fatias incrementais usando o motor '{motor_grafico}'...")
    
    # Adiciona imports com base no motor gráfico
    imports_grafico = "import plotly.graph_objects as go"
    if motor_grafico.lower() == "seaborn":
        imports_grafico += "\nimport matplotlib.pyplot as plt\nimport seaborn as sns"

    # 1. Escreve a casca fixa de topo e estilos CSS do Livro Interativo (Economiza tokens do LLM)
    codigo_completo = f"""import streamlit as st
import numpy as np
import pandas as pd
{imports_grafico}
import scipy.stats as stats
from scipy.stats import norm
import base64
import json

# Carregamento seguro dos metadados da aula para evitar SyntaxError
metadata = json.loads(base64.b64decode('{metadata_b64}').decode('utf-8'))

# Injeção de Estilos CSS Acadêmicos Premium
st.markdown(\"\"\"
    <style>
        .premium-title {{ font-size: 2.2rem; font-weight: 800; color: #1E3A8A; margin-bottom: 0.2rem; }}
        .premium-subtitle {{ font-size: 1.1rem; color: #64748B; margin-bottom: 1.5rem; font-style: italic; }}
    </style>
\"\"\", unsafe_allow_html=True)

st.markdown(f'<div class="premium-title">{{metadata["tema_global"]}}</div>', unsafe_allow_html=True)
st.markdown('<div class="premium-subtitle">Conteúdo Acadêmico Digital e Simuladores Integrados</div>', unsafe_allow_html=True)

# Definição de Cores Globais da Paleta Premium
PRIMARY_BLUE = "#1E3A8A"
SECONDARY_GREEN = "#10B981"
WARNING_AMBER = "#F59E0B"
CRITICAL_RED = "#991B1B"

# Criação das Duas Grandes Abas Globais
tab_conteudo, tab_exercicios = st.tabs(["📚 Conteúdo Acadêmico Interativo", "📝 Caderno de Exercícios"])

with tab_conteudo:
"""

    # Converte a lista de simuladores em um dicionário de busca rápida
    simuladores_dict = {}
    for sim in teoria.get("simuladores_da_aula", []):
        simuladores_dict[str(sim.get("indice_pagina", ""))] = sim.get("nome_simulador", "")

    # 2. Laço Incremental: Processa e costura cada página de conteúdo separadamente
    for idx, pagina in enumerate(teoria["paginas_conteudo"]):
        print(f"   -> Solicitando codificação da página teórica {idx+1}: {pagina['titulo_subtopico']}")
        
        # Consulta o plano do orquestrador editorial para saber se deve carregar o plot e qual o seu nome
        chave_str = str(idx + 1)
        nome_simulador = simuladores_dict.get(chave_str, "")
        
        fatia_teoria_codigo = programar_fatia_teoria(pagina, nome_simulador=nome_simulador, motor_grafico=motor_grafico, chave_suffix=f"subtopico_{idx + 1}")
        
        # AJUSTE DEFENSIVO DE INDENTAÇÃO: Remove recuo base indesejado que a IA possa ter gerado
        linhas = fatia_teoria_codigo.split("\n")
        recuo_minimo = min([len(l) - len(l.lstrip()) for l in linhas if l.strip()] or [0])
        if recuo_minimo > 0:
            linhas = [l[recuo_minimo:] if l.strip() else l for l in linhas]
        fatia_teoria_codigo = "\n".join(linhas)
        
        # Aplica o recuo de 4 espaços para o Python não quebrar a indentação do 'with tab_conteudo:'
        codigo_indendado = "\n".join([f"    {linha}" for linha in fatia_teoria_codigo.split("\n")])
        codigo_completo += f"\n{codigo_indendado}\n"
        
    # 3. Injeta a Seção ÚNICA de Referências Bibliográficas consolidadas bem no final da primeira Aba
    codigo_completo += "\n    st.markdown('---')\n    st.markdown('##### 📚 Referências Bibliográficas Consolidadas (Rodapé da Aula)')\n"
    codigo_completo += "    for ref in metadata['referencias_bibliograficas_finais']:\n        st.markdown(f'- {ref}')\n"

    # 4. Abre a segunda Aba global e injeta a fatia dos exercícios práticos
    print("   -> Solicitando codificação do caderno de exercícios...")
    codigo_completo += "\nwith tab_exercicios:\n"
    codigo_completo += f"    import json, base64\n    dados_exercicios = json.loads(base64.b64decode('{exercicios_b64}').decode('utf-8'))\n\n"
    
    fatia_exercicios_codigo = programar_fatia_exercicios(exercicios)
    
    # Ajuste defensivo de indentação nos exercícios
    linhas_ex = fatia_exercicios_codigo.split("\n")
    recuo_min_ex = min([len(l) - len(l.lstrip()) for l in linhas_ex if l.strip()] or [0])
    if recuo_min_ex > 0:
        linhas_ex = [l[recuo_min_ex:] if l.strip() else l for l in linhas_ex]
    fatia_exercicios_codigo = "\n".join(linhas_ex)
    
    codigo_ex_indendado = "\n".join([f"    {linha}" for linha in fatia_exercicios_codigo.split("\n")])
    codigo_completo += f"\n{codigo_ex_indendado}\n"

    # 5. Descobre o número incremental e grava fisicamente o arquivo executável final na pasta /aulas
    pasta_aulas = "aulas"
    if not os.path.exists(pasta_aulas):
        os.makedirs(pasta_aulas)
    
    arquivos_existentes = [f for f in os.listdir(pasta_aulas) if f.startswith("aula") and f.endswith(".py")]
    prox_numero = 1
    for aula in arquivos_existentes:
        match = re.search(r'aula(\d+)', aula)
        if match:
            num = int(match.group(1))
            if num >= prox_numero:
                prox_numero = num + 1

    tema_limpo = re.sub(r'[^a-zA-Z0-9]', '_', teoria["tema_global"].lower())
    tema_limpo = re.sub(r'_+', '_', tema_limpo).strip('_')
    nome_arquivo = f"aula{prox_numero}_{tema_limpo}.py"
    caminho_final_script = os.path.join(pasta_aulas, nome_arquivo)

    with open(caminho_final_script, "w", encoding="utf-8") as f:
        f.write(codigo_completo)
        
    print(f"\n[SUCESSO] Aula gerada e compilada em fatias: {caminho_final_script}")

    # Teste de compilação
    try:
        import py_compile
        py_compile.compile(caminho_final_script, doraise=True)
        print("[OK] Teste de Compilação: Aprovado sem erros de sintaxe!")
    except py_compile.PyCompileError as pye:
        print(f"[ERRO] A costura apresentou problemas de compilação: {pye}")
        if os.path.exists(caminho_final_script):
            try:
                os.remove(caminho_final_script)
            except Exception:
                pass
        raise RuntimeError(f"O script gerado contém erro de sintaxe Python e foi removido para evitar falha do app. Detalhes: {pye}")

    # Teste de execução simulado em Sandbox
    try:
        validar_execucao_codigo(codigo_completo)
        print("[OK] Teste de Execução Simulado: Passou sem erros de runtime!")
    except Exception as e:
        print(f"[ERRO] Teste de Execução Simulado falhou: {e}")
        if os.path.exists(caminho_final_script):
            try:
                os.remove(caminho_final_script)
            except Exception:
                pass
        # Captura apenas o nome do erro e a mensagem para evitar estourar limites do terminal
        raise RuntimeError(f"O script gerado contém erros de execução (ex: Plotly/Pandas) e foi removido para evitar falhas no carregamento. Detalhes: {type(e).__name__}: {str(e)[:500]}")

    return caminho_final_script

if __name__ == "__main__":
    print("[AVISO] A compilação da interface deve ser executada a partir da interface do Streamlit.")
    print("Por favor, execute o comando: streamlit run app.py")
