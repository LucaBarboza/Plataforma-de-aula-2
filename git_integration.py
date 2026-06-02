import os
import base64
import requests

def obter_credencial_github():
    """Recupera as credenciais do GitHub a partir do ambiente ou do st.secrets."""
    token = os.environ.get("GITHUB_PAT") or os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPO")
    branch = os.environ.get("GITHUB_BRANCH", "main")
    
    try:
        import streamlit as st
        if not token and "GITHUB_PAT" in st.secrets:
            token = st.secrets["GITHUB_PAT"]
        if not token and "GITHUB_TOKEN" in st.secrets:
            token = st.secrets["GITHUB_TOKEN"]
        if not repo and "GITHUB_REPO" in st.secrets:
            repo = st.secrets["GITHUB_REPO"]
        if branch == "main" and "GITHUB_BRANCH" in st.secrets:
            branch = st.secrets["GITHUB_BRANCH"]
    except Exception:
        pass
        
    return token, repo, branch

def commitar_arquivo_github(caminho_local: str, caminho_repositorio: str, mensagem_commit: str):
    """
    Envia um arquivo local diretamente para o repositório do GitHub do usuário via API REST.
    """
    token, repo, branch = obter_credencial_github()
    
    if not token or not repo:
        print("[GITHUB] Integração com GitHub pulada: GITHUB_PAT ou GITHUB_REPO não configurados.")
        return False
        
    # Garante formatação correta do caminho
    caminho_repositorio = caminho_repositorio.replace("\\", "/")
    
    try:
        if not os.path.exists(caminho_local):
            print(f"[GITHUB] Arquivo local não encontrado: {caminho_local}")
            return False
            
        with open(caminho_local, "rb") as f:
            conteudo_binario = f.read()
            
        conteudo_base64 = base64.b64encode(conteudo_binario).decode("utf-8")
        
        # URL da API do GitHub para criar/atualizar conteúdo
        url = f"https://api.github.com/repos/{repo}/contents/{caminho_repositorio}"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        # 1. Verifica se o arquivo já existe para obter o SHA
        sha = None
        params = {"ref": branch}
        res_get = requests.get(url, headers=headers, params=params)
        if res_get.status_code == 200:
            sha = res_get.json().get("sha")
            
        # 2. Prepara o payload
        payload = {
            "message": mensagem_commit,
            "content": conteudo_base64,
            "branch": branch
        }
        if sha:
            payload["sha"] = sha
            
        # 3. Executa a escrita
        res_put = requests.put(url, headers=headers, json=payload)
        
        if res_put.status_code in [200, 201]:
            print(f"[GITHUB] Sucesso ao commitar '{caminho_repositorio}' no GitHub!")
            return True
        else:
            print(f"[GITHUB] Erro ao commitar (HTTP {res_put.status_code}): {res_put.text}")
            return False
            
    except Exception as e:
        print(f"[GITHUB] Falha operacional ao tentar commitar: {e}")
        return False
