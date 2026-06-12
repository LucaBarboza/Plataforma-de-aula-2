import os
import json
import re
import time
from google import genai
from google.genai import types

# Importando o contrato estruturado do caderno de exercícios
from schemas import CadernoExerciciosSubtopico

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
        
    # Tenta ler do secrets.toml da pasta local
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

# Inicializa o carregamento da chave de API
carregar_chave_api()

# ==============================================================================
# FUNÇÃO PRINCIPAL DE ORQUESTRAÇÃO DE EXERCÍCIOS
# ==============================================================================
def gerar_caderno_exercicios(caminho_payload_teoria: str, nome_professor: str = None, codigo_disciplina: str = None, diretrizes_texto: str = None):
    # Garante que temos a chave configurada
    if not os.environ.get("GEMINI_API_KEY"):
        raise ValueError("Chave de API 'GEMINI_API_KEY' não configurada. Configure a chave nos Secrets do Streamlit ou no ambiente.")

    try:
        client = genai.Client()
    except Exception as e:
        print(f"[ERRO] Erro ao inicializar o cliente do Google GenAI: {e}")
        return None
    
    # 1. Valida se o insumo do Agente 2 existe na máquina local
    if not os.path.exists(caminho_payload_teoria):
        print(f"[ERRO] Erro crítico: O arquivo '{caminho_payload_teoria}' não foi encontrado. Gere a teoria primeiro.")
        return None
        
    with open(caminho_payload_teoria, "r", encoding="utf-8") as f:
        payload_teoria = json.load(f)
        
    tema_aula = payload_teoria["tema"]
    print(f"\n[Agente 3] Iniciando a criação do caderno de exercícios fatiado por subtópico para a aula: '{tema_aula}'...")

    # 2. Valida as diretrizes de estilo do professor (enviadas obrigatoriamente pelo Streamlit)
    if not diretrizes_texto or not diretrizes_texto.strip():
        raise ValueError("As diretrizes de notação e estilo são obrigatórias e devem ser fornecidas pelo Streamlit.")

    # 3. Busca e Configuração das Stores do RAG (File Search)
    store_names = []
    if nome_professor and codigo_disciplina:
        NOME_STORE = f"store-{nome_professor.lower().strip()}-{codigo_disciplina.lower().strip()}"
        NOME_STORE_FALLBACK = "plataforma-estatistica-db"
        try:
            stores_disponiveis = list(client.file_search_stores.list())
            # Busca store específica
            for store in stores_disponiveis:
                if store.display_name == NOME_STORE:
                    store_names.append(store.name)
                    print(f"[RAG Exercícios] RAG específico do professor ativado! Store: {store.display_name}")
            # Busca store global
            for store in stores_disponiveis:
                if store.display_name == NOME_STORE_FALLBACK:
                    store_names.append(store.name)
                    print(f"[RAG Exercícios] RAG de livros ativado! Store: {store.display_name}")
        except Exception as e:
            print(f"[ALERTA Exercícios] Erro ao pesquisar stores de arquivos RAG: {e}")

    questoes_multipla_escolha_acumuladas = []
    questoes_discursivas_acumuladas = []

    # 4. Processamento e Geração por Subtópico
    paginas = payload_teoria.get("conteudo_paginas", [])
    for idx, pag in enumerate(paginas):
        titulo_sub = pag.get("titulo_subtopico", f"Subtópico {idx+1}")
        conteudo_sub = pag.get("conteudo", {})
        intencao_sub = conteudo_sub.get("conceito_intuitivo", "")
        formalismo_sub = conteudo_sub.get("conceito_formal", "")
        
        print(f"   -> [Subtópico {idx+1}/{len(paginas)}] Gerando 2 fechadas e 3 abertas com RAG/Plotly para: '{titulo_sub}'...")

        # Configura as tools RAG por subtópico se existirem
        tools_config = None
        if store_names:
            tools_config = [
                types.Tool(
                    file_search=types.FileSearch(
                        file_search_store_names=store_names,
                        metadata_filter=f'discipline="{codigo_disciplina.upper().strip()}"',
                        top_k=25
                    )
                )
            ]

        prompt_exercicios = fr"""
Você é um Professor Adjunto de Estatística e Avaliador Acadêmico da UFBA.

### CONTEXTO E MISSÃO
Você receberá o [SUBTOPICO_DA_AULA] que acabou de ser gerado, acesso ao RAG (livros-texto e notas de aula do professor) e as [DIRETRIZES_DE_ESTILO] estritas de notação.
Sua missão é projetar um caderno de exercícios de altíssimo nível universitário e rigor conceitual sobre este subtópico específico, preenchendo a estrutura 'CadernoExerciciosSubtopico'.

---

### DIRETRIZES DE ESCOPO E SEGURANÇA (MANDATÓRIO)
1. RESTRIÇÃO DE ESCOPO CONCEITUAL E TEÓRICO (TOLERÂNCIA ZERO):
   - Suas questões devem se limitar estritamente e exclusivamente aos conceitos descritos e contidos no [SUBTOPICO_DA_AULA] fornecido. 
   - Mesmo que você encontre tópicos avançados ou conceitos relacionados nos livros do RAG, é terminantemente proibido exigir ou introduzir na questão qualquer conceito que não conste do [SUBTOPICO_DA_AULA] (por exemplo, não cobre distribuições, estimadores ou testes de hipóteses que não foram explicados aqui).
2. USO DO RAG PARA REFERÊNCIAS E CRÉDITOS:
   - Consulte os livros de estatística do RAG (File Search) para buscar inspiração de problemas práticos, conjuntos de dados reais ou estilo de enunciados.
   - Se a questão gerada for baseada, inspirada ou extraída de um exercício de um livro das stores RAG, você DEVE preencher o campo 'referencia_livro' com a citação exata (ex: 'Bussab & Morettin, Estatística Básica, Cap 5, p. 115' ou 'Wooldridge, Cap 2, p. 45'). 
   - Se for criação própria original ou se você não consultou uma questão específica de livro para elaborá-la, deixe 'referencia_livro' como null.
3. Cenários Reais e Práticos: Crie enunciados contextualizados em problemas reais de engenharia, negócios, ensaios clínicos, economia ou IoT. Banir formulações puramente abstratas (ex: "Seja X...").
4. Rigor de LaTeX e Cálculos Completos: Toda notação e equações devem ser escritas em LaTeX ($ ou $$) usando os símbolos obrigatórios do professor. No gabarito, descreva numericamente todas as etapas da substituição algébrica.
5. Suporte a Gráficos Plotly (codigo_plotly):
   - Se a questão se beneficiar visualmente de um gráfico interativo de suporte (ex: densidade de probabilidade, áreas de cauda de testes de hipótese, dispersão de dados, boxplots comparativos), escreva um código Python Plotly completo e limpo no campo 'codigo_plotly'.
   - O código deve criar e configurar um objeto de figura chamado 'fig'. Ex: fig = go.Figure(...) ou fig = px.scatter(...).
   - IMPORTANTE: NÃO inclua nenhuma importação (como import plotly.graph_objects as go), assuma que go, px, np, pd e stats já estão importadas no escopo global.
   - Configure o layout do gráfico para usar a paleta estrita do professor (PRIMARY_BLUE, SECONDARY_GREEN, etc. que já estão disponíveis no escopo do Streamlit). Se as diretrizes do professor contiverem cores hexadecimais específicas, use-as.
   - Mantenha o template como "plotly_white", configure as margens adequadamente e defina fixedrange=True em ambos os eixos se for gráfico 2D.
   - Se a questão NÃO precisar de gráfico de suporte, deixe o campo 'codigo_plotly' como None.

---

### INSTRUÇÕES PARA PREENCHIMENTO DO SCHEMA DE RETORNO

1. 'questoes_multipla_escolha' (lista contendo exatamente 2 objetos QuestaoFechada):
   Cada item representa uma questão de múltipla escolha e deve conter:
   - 'enunciado' (string): Enunciado realista, complexo e detalhado que introduz a situação estatística e a pergunta de forma envolvente.
   - 'alternativas' (objeto AlternativasFechadas): Deve possuir exatamente as opções 'A', 'B', 'C', 'D' e 'E' com respostas completas e cientificamente plausíveis.
   - 'alternativa_correta' (string): Uma única letra correspondente à opção correta ('A', 'B', 'C', 'D' ou 'E').
   - 'dica' (string): Insight conceitual sutil que ajude o aluno sem entregar o gabarito.
   - 'gabarito_comentado' (string): Demonstração aritmética completa de todos os cálculos e justificativa minuciosa da alternativa correta.
   - 'codigo_plotly' (string ou null): O código Plotly para gerar o gráfico interativo de apoio, se aplicável.
   - 'referencia_livro' (string ou null): A citação da referência bibliográfica exata se vier do RAG, caso contrário null.

2. 'questoes_discursivas' (lista contendo exatamente 3 objetos QuestaoAberta):
   Cada item representa uma questão discursiva/problema de cálculo e deve conter:
   - 'enunciado' (string): Problema discursivo que exija contas complexas ou análise qualitativa.
   - 'dica' (string): Direcionamento ou fórmula teórica inicial que guie a resposta.
   - 'gabarito_passo_a_passo' (lista de strings): As passagens e etapas de cálculo passo a passo expressas detalhadamente em LaTeX ($$).
   - 'codigo_plotly' (string ou null): O código Plotly para gerar o gráfico interativo de apoio, se aplicável.
   - 'referencia_livro' (string ou null): A citação da referência bibliográfica exata se vier do RAG, caso contrário null.
   - 'resposta_numerica_esperada' (float ou null): Se a questão exigir a realização de cálculos aritméticos/numéricos fechados e resultar em um valor numérico exato final (ex: probabilidade, estatística calculada, limite de intervalo, p-valor, etc.), você DEVE obrigatoriamente preencher este campo com o valor float correspondente. Se a resposta correta for 0.05, coloque 0.05. Se a questão for de cunho puramente discursivo-prosa ou teórica qualitativa sem um único número de resultado, defina como null.

---

### ENTRADAS DO USUÁRIO
- [SUBTOPICO_DA_AULA]:
  * Subtópico: {titulo_sub}
  * Intuição: {intencao_sub}
  * Formalismo: {formalismo_sub}
- [DIRETRIZES_DE_ESTILO]:
{diretrizes_texto}
"""

        config_exercicios = types.GenerateContentConfig(
            tools=tools_config,
            thinking_config=types.ThinkingConfig(thinking_level="high"),
            temperature=1.0,
            response_mime_type="application/json",
            response_schema=CadernoExerciciosSubtopico
        )
        
        try:
            resposta_exercicios = client.models.generate_content(
                model="gemini-3.1-flash-lite",
                contents=[f"Subtópico: {titulo_sub}", prompt_exercicios],
                config=config_exercicios
            )
            
            subtopico_caderno = CadernoExerciciosSubtopico.model_validate_json(resposta_exercicios.text)
            
            questoes_multipla_escolha_acumuladas.extend(subtopico_caderno.questoes_multipla_escolha)
            questoes_discursivas_acumuladas.extend(subtopico_caderno.questoes_discursivas)
            
            print(f"   [OK] Subtópico '{titulo_sub}' concluído: 2 fechadas e 3 abertas adicionadas!")
            
            time.sleep(1)
            
        except Exception as e:
            print(f"   [ERRO] Falha ao gerar exercícios para o subtópico '{titulo_sub}': {e}")
            continue

    # 5. Consolida e formata em dicionário
    caderno_final = {
        "topico_aula": tema_aula,
        "questoes_multipla_escolha": [q.model_dump() if hasattr(q, "model_dump") else q for q in questoes_multipla_escolha_acumuladas],
        "questoes_discursivas": [q.model_dump() if hasattr(q, "model_dump") else q for q in questoes_discursivas_acumuladas]
    }
    
    print(f"   [SUCESSO] Caderno de exercícios concluído! Total: {len(caderno_final['questoes_multipla_escolha'])} fechadas e {len(caderno_final['questoes_discursivas'])} abertas.")
    return caderno_final

if __name__ == "__main__":
    print("[AVISO] A geração de exercícios deve ser executada a partir da interface do Streamlit.")
    print("Por favor, execute o comando: streamlit run app.py")
