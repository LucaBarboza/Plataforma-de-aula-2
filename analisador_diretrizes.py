import os
import json
from google import genai
from google.genai import types
from schemas import DiretrizesProfessorMapeadas
from gerador_conteudo import carregar_chave_api

def processar_arquivo_diretrizes_ia(caminho_arquivo: str, nome_original: str) -> dict:
    """
    Envia o arquivo de diretrizes do professor para o Gemini para mapear as preferências
    nos campos de notação matemática e design de estilo usando Structured Outputs.
    """
    # Garante a carga da chave de API
    carregar_chave_api()
    if not os.environ.get("GEMINI_API_KEY"):
        raise ValueError("Chave de API 'GEMINI_API_KEY' não configurada no ambiente ou secrets.")

    client = genai.Client()
    
    # Determina o tipo de arquivo
    extensao = os.path.splitext(nome_original.lower())[1]
    
    prompt = """
    Você é um Engenheiro Pedagógico e Assistente Especialista de IA para análise de diretrizes acadêmicas.
    Sua tarefa é analisar o documento de diretrizes ou preferências do professor fornecido e categorizar as preferências nos campos correspondentes do schema 'DiretrizesProfessorMapeadas'.
    
    INSTRUÇÕES DE PREENCHIMENTO:
    1. Preencha apenas os campos que forem explicitamente mencionados ou que puderem ser claramente deduzidos das preferências do professor no arquivo.
    2. Para notações matemáticas (como média populacional, hipótese nula, etc.), você deve retornar a notação exata em formato LaTeX (ex: $n$, $\\mu$, $\\bar{X}$, $H_0$). Certifique-se de que a barra invertida seja escapada corretamente para JSON.
    3. Se houver alguma outra notação específica que não se enquadre nos campos padrão, crie um item correspondente na lista 'notacoes_customizadas' com chaves 'conceito' e 'simbolo'.
    4. Se forem mencionadas cores preferidas para a identidade visual da plataforma, extraia-as em formato hex (ex: #1E3A8A) no dicionário 'cores_preferidas' (chaves válidas: 'cor_primaria', 'cor_secundaria', 'cor_alerta', 'cor_critica').
    5. No campo 'diretrizes_estilo_livre', consolide quaisquer outras diretrizes gerais sobre tom de escrita, foco de exemplos (ex: "focar em exemplos de ciências da saúde"), proibição de termos em inglês, etc.
    6. Se o campo não for citado ou não puder ser extraído, deixe-o como null (ou omitido).
    """

    try:
        # Se for PDF, faz upload do arquivo para o Gemini Cloud
        if extensao == ".pdf":
            print(f"[Analisador Diretrizes] Fazendo upload do arquivo PDF '{caminho_arquivo}' para o Gemini Cloud...")
            pdf_ref = client.files.upload(file=caminho_arquivo)
            
            resposta = client.models.generate_content(
                model="gemini-3.1-flash-lite", # Usamos o modelo padrão configurado na plataforma
                contents=[pdf_ref, prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=DiretrizesProfessorMapeadas,
                    temperature=0.2
                )
            )
            # Limpa o arquivo da nuvem
            try:
                client.files.delete(name=pdf_ref.name)
            except Exception as e_del:
                print(f"[Analisador Diretrizes] Erro ao deletar arquivo temporário da nuvem: {e_del}")
                
        else:
            # Se for TXT ou MD, lê localmente e envia como string de texto
            print(f"[Analisador Diretrizes] Lendo arquivo de texto local '{caminho_arquivo}'...")
            with open(caminho_arquivo, "r", encoding="utf-8", errors="ignore") as f:
                conteudo_texto = f.read()
                
            resposta = client.models.generate_content(
                model="gemini-3.1-flash-lite",
                contents=[
                    f"### CONTEÚDO DO DOCUMENTO DO PROFESSOR:\n{conteudo_texto}\n\n",
                    prompt
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=DiretrizesProfessorMapeadas,
                    temperature=0.2
                )
            )
            
        # Retorna o dicionário parseado
        dados_dicionario = json.loads(resposta.text)
        return dados_dicionario

    except Exception as e:
        print(f"[Analisador Diretrizes] Erro durante o processamento das diretrizes: {e}")
        raise e
