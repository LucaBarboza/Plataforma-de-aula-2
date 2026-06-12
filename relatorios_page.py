import streamlit as st
import os
import json
import re
from gerador_page import construir_relatorio_prosa_txt

def run_page():
    # Estilização CSS premium para visualização de relatórios
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
            
            .main-title {
                font-size: 2.5rem;
                font-weight: 800;
                background: linear-gradient(135deg, #0F172A 0%, #2563EB 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 0.5rem;
                text-align: center;
            }
            .subtitle {
                font-size: 1.1rem;
                color: #64748B;
                margin-bottom: 2rem;
                text-align: center;
                font-style: italic;
            }
            
            /* Estilização dos blocos de métricas e KPIs */
            div[data-testid="metric-container"] {
                background: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
                padding: 1rem;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
                transition: all 0.3s ease;
            }
            div[data-testid="metric-container"]:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
                border-color: #3B82F6;
            }
            
            /* Tabs estilizadas */
            div[data-baseweb="tab-list"] {
                gap: 12px;
            }
            button[data-baseweb="tab"] {
                border-radius: 8px 8px 0 0 !important;
                background-color: #F8FAFC !important;
                border: 1px solid #E2E8F0 !important;
                border-bottom: none !important;
                color: #475569 !important;
                padding: 8px 16px !important;
            }
            button[aria-selected="true"] {
                background-color: #FFFFFF !important;
                border-top: 3px solid #2563EB !important;
                color: #1E293B !important;
                font-weight: 600 !important;
            }
            
            /* Caixas de Texto de Relatório */
            textarea {
                font-family: 'Courier New', Courier, monospace !important;
                background-color: #0F172A !important;
                color: #38BDF8 !important;
                border-radius: 8px !important;
                border: 1px solid #1E293B !important;
                padding: 12px !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # Título premium
    st.markdown("""
        <div style="margin-bottom: 2rem;">
            <h1 class="main-title">📊 Relatório de Auditoria e Logs dos Agentes</h1>
            <p class="subtitle">
                Monitore o histórico detalhado, métricas de revisão científica e tempos do pipeline de inteligência artificial.
            </p>
        </div>
    """, unsafe_allow_html=True)

    opcoes_log = {}
    
    # 1. Faz a varredura dinâmica na pasta /logdasaulasgeradas por logs específicos de aulas
    if os.path.exists("logdasaulasgeradas"):
        arquivos_aulas = sorted(os.listdir("logdasaulasgeradas"))
        for f in arquivos_aulas:
            if f.endswith(".log.json"):
                caminho_log = os.path.join("logdasaulasgeradas", f)
                try:
                    with open(caminho_log, "r", encoding="utf-8") as lf:
                        data = json.load(lf)
                        tema = data.get("tema", "Sem Tema")
                        disciplina = data.get("disciplina", "Geral")
                        match = re.match(r'^aula(\d+)', f, flags=re.IGNORECASE)
                        num_str = f"Aula {int(match.group(1)):02d}" if match else "Aula"
                        label_bonito = f"📊 {num_str}: {tema} ({disciplina})"
                        opcoes_log[label_bonito] = caminho_log
                except Exception:
                    pass

    if opcoes_log:
        lista_opcoes = ["Selecione um relatório..."] + list(opcoes_log.keys())
        log_selecionado_label = st.selectbox("Selecione o Relatório de Auditoria:", options=lista_opcoes, index=0)
        
        if log_selecionado_label == "Selecione um relatório...":
            st.info("💡 Por favor, selecione um relatório de auditoria acima para visualizar as métricas de geração e histórico dos agentes.")
            return
            
        log_path = opcoes_log[log_selecionado_label]
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                log_data = json.load(f)
            
            # 1. KPIs
            tempo_total = log_data.get("tempo_total_segundos", 0.0)
            status_exec = log_data.get("status", "desconhecido")
            
            subtopicos_log = log_data.get("etapas", {}).get("3_escrita_revisao", {}).get("subtopicos", [])
            total_tentativas = sum(sub.get("tentativas", 0) for sub in subtopicos_log)
            total_reprovacoes = sum(sub.get("reprovacoes", 0) for sub in subtopicos_log)
            
            # Contagem de erros API
            total_erros_429 = sum(sub.get("erros_api", {}).get("429", 0) for sub in subtopicos_log)
            total_erros_503 = sum(sub.get("erros_api", {}).get("503", 0) for sub in subtopicos_log)
            total_erros_outros = sum(sub.get("erros_api", {}).get("outros", 0) for sub in subtopicos_log)
            total_erros_api = total_erros_429 + total_erros_503 + total_erros_outros
            
            status_color = "#10B981" if status_exec == "sucesso" else "#EF4444"
            status_text = "🟢 SUCESSO" if status_exec == "sucesso" else "🔴 ERRO"
            
            col_kpi1, col_kpi2, col_kpi3, col_kpi4, col_kpi5 = st.columns(5)
            with col_kpi1:
                st.metric("Status da Execução", status_text)
            with col_kpi2:
                if tempo_total > 60:
                    minutos = int(tempo_total // 60)
                    segundos = int(tempo_total % 60)
                    st.metric("Duração Total", f"{minutos}m {segundos}s", help="Tempo decorrido do início ao fim de todas as etapas.")
                else:
                    st.metric("Duração Total", f"{tempo_total}s", help="Tempo decorrido do início ao fim de todas as etapas.")
            with col_kpi3:
                st.metric("Tentativas do Escritor", f"{total_tentativas} tent.", help="Quantidade de vezes que o Agente Escritor redigiu conteúdo.")
            with col_kpi4:
                st.metric("Reprovações do Revisor", f"{total_reprovacoes} recusas", help="Número de vezes que o Revisor Científico mandou refazer.")
            with col_kpi5:
                st.metric("Falhas de API (429/503)", f"{total_erros_api} erros", help=f"Detalhamento: {total_erros_429} limite de cota (429) | {total_erros_503} indisp. servidor (503) | {total_erros_outros} outros.")
                
            # 2. Abas do painel
            tab_relatorio_txt, tab_duracao, tab_auditoria = st.tabs(["📄 Relatório Completo (TXT)", "⏱️ Cronograma das Etapas", "🤖 Auditoria do Loop de Escrita"])
            
            with tab_relatorio_txt:
                log_txt_path = log_path.replace(".log.json", ".log.txt")
                if os.path.exists(log_txt_path):
                    try:
                        with open(log_txt_path, "r", encoding="utf-8") as tf:
                            conteudo_txt = tf.read()
                        
                        st.markdown("##### 📥 Baixar Relatório Descritivo Completo")
                        st.download_button(
                            label="Download do Relatório (.txt)",
                            data=conteudo_txt,
                            file_name=os.path.basename(log_txt_path),
                            mime="text/plain",
                            use_container_width=True
                        )
                        
                        st.markdown("##### 🔍 Visualização do Histórico e Prosa")
                        st.text_area(
                            "Histórico de Geração e Conteúdo:",
                            value=conteudo_txt,
                            height=500,
                            disabled=True
                        )
                    except Exception as txt_read_err:
                        st.error(f"Erro ao ler arquivo de texto do log: {txt_read_err}")
                else:
                    st.info("O relatório completo em texto (.txt) não está disponível para esta aula (aulas geradas anteriormente não o possuem).")
            
            with tab_duracao:
                st.markdown("##### Duração proporcional por etapa do pipeline:")
                
                etapas = log_data.get("etapas", {})
                chaves_etapas = sorted(etapas.keys())
                
                for chave in chaves_etapas:
                    etapa = etapas[chave]
                    duracao = etapa.get("duracao_segundos", 0.0)
                    desc = etapa.get("descricao", "Etapa")
                    status_etapa = etapa.get("status", "sucesso")
                    
                    porcentagem = (duracao / max(tempo_total, 1.0)) * 100
                    porcentagem = min(porcentagem, 100.0)
                    
                    badge = "✓" if status_etapa == "sucesso" else ("ℹ" if status_etapa == "pulado" else "✗")
                    badge_color = "#10b981" if status_etapa == "sucesso" else ("#64748b" if status_etapa == "pulado" else "#ef4444")
                    
                    st.markdown(f"""
                        <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 12px; margin-bottom: 12px; font-family: 'sans-serif';">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                                <span style="font-weight: 600; color: #1E293B; font-size: 0.95rem;">
                                    <span style="background-color: {badge_color}; color: white; border-radius: 50%; padding: 2px 6px; font-size: 0.75rem; margin-right: 6px;">{badge}</span>
                                    {desc}
                                </span>
                                <span style="color: #475569; font-weight: 700; font-size: 0.9rem;">{duracao}s ({porcentagem:.1f}%)</span>
                            </div>
                            <div style="background-color: #E2E8F0; height: 8px; border-radius: 4px; overflow: hidden;">
                                <div style="background-color: #1E3A8A; height: 100%; width: {porcentagem}%;"></div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
            with tab_auditoria:
                st.markdown("##### Relatório científico de geração e refações por subtópico:")
                
                if not subtopicos_log:
                    st.info("Nenhum detalhe de subtópico disponível nesta execução.")
                else:
                    for i, sub in enumerate(subtopicos_log):
                        titulo_sub = sub.get("titulo", "Subtópico")
                        tentativas_sub = sub.get("tentativas", 1)
                        reprovacoes_sub = sub.get("reprovacoes", 0)
                        tempo_sub = sub.get("tempo_segundos", 0.0)
                        aprovado_sub = sub.get("aprovado", True)
                        
                        sub_erros_429 = sub.get("erros_api", {}).get("429", 0)
                        sub_erros_503 = sub.get("erros_api", {}).get("503", 0)
                        sub_erros_outros = sub.get("erros_api", {}).get("outros", 0)
                        sub_total_erros = sub_erros_429 + sub_erros_503 + sub_erros_outros
                        
                        status_icon = "🟢" if aprovado_sub else "🟡"
                        status_lbl = "Aprovado" if aprovado_sub else "Aprovado via Fallback"
                        
                        header_label = f"{status_icon} Subtópico {i+1}: {titulo_sub} — {tentativas_sub} tent. | {tempo_sub}s"
                        
                        with st.expander(header_label):
                            col_sub1, col_sub2, col_sub3 = st.columns(3)
                            with col_sub1:
                                st.write(f"**Status da Revisão:** {status_lbl}")
                                st.write(f"**Tempo de Processamento:** {tempo_sub}s")
                            with col_sub2:
                                st.write(f"**Tentativas do Escritor:** {tentativas_sub} de 3")
                                st.write(f"**Rejeições do Revisor:** {reprovacoes_sub}")
                            with col_sub3:
                                st.write(f"**Falhas de API enfrentadas:** {sub_total_erros}")
                                st.write(f"└ *429 (Cota): {sub_erros_429} | 503 (Indisp.): {sub_erros_503} | Outros: {sub_erros_outros}*")
                                
                            feedbacks_list = sub.get("feedbacks", [])
                            if feedbacks_list:
                                st.markdown("<div style='margin-top: 10px; font-weight: 600; color: #991B1B;'>❌ Histórico de Rejeições e Feedbacks de Correção:</div>", unsafe_allow_html=True)
                                for f_idx, f_text in enumerate(feedbacks_list):
                                    st.markdown(f"""
                                        <div style="background-color: #FEF2F2; border-left: 4px solid #EF4444; padding: 12px; border-radius: 4px; margin-bottom: 10px;">
                                            <div style="color: #991B1B; font-weight: 700; font-size: 0.85rem; margin-bottom: 4px;">TENTATIVA #{f_idx+1} REPROVADA PELO REVISOR CIENTÍFICO:</div>
                                            <div style="color: #7F1D1D; font-size: 0.9rem; line-height: 1.4; white-space: pre-wrap;">{f_text}</div>
                                        </div>
                                    """, unsafe_allow_html=True)
                            else:
                                st.markdown("<div style='margin-top: 10px; font-weight: 600; color: #065F46;'>✓ Aprovado de primeira tentativa sem correções solicitadas.</div>", unsafe_allow_html=True)
                                
        except Exception as log_err:
            st.warning(f"Não foi possível carregar o log selecionado: {log_err}")
    else:
        st.info("Nenhum relatório de auditoria ou log foi encontrado. Crie uma aula primeiro para gerar os logs.")

if __name__ == "__main__":
    run_page()
