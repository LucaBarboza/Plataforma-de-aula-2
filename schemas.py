from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal

# ==========================================
# SUB-OBJETOS AUXILIARES
# ==========================================

class EstruturaExemplo(BaseModel):
    enunciado: str = Field(description="O problema proposto com contextualização acadêmica detalhada.")
    passo_a_passo_solucao: List[str] = Field(description="Lista contendo os passos lógicos e cálculos intermediários em LaTeX.")
    resultado_final: str = Field(description="A conclusão direta e interpretação prática do problema.")

class ExemploResolvidoRico(BaseModel):
    contexto_e_enunciado: str = Field(
        description="Enunciado longo e contextualizado em um cenário real (mínimo 2 parágrafos). Deve descrever o problema prático, a origem dos dados e os objetivos da análise."
    )
    dados_brutos_sumarizados: str = Field(
        description="Exibição clara e organizada dos dados descritivos em LaTeX (ex: sum_x, sum_y, n, barras) necessários para o cálculo."
    )
    desenvolvimento_aritmético_passo_a_passo: List[str] = Field(
        description="Lista exaustiva mostrando a substituição numérica em cada fórmula. Proibido pular etapas de cálculo ou jogar resultados diretos."
    )
    conclusao_e_laudo_comercial: str = Field(
        description="Interpretação prática e qualitativa do resultado final para o tomador de decisão (mínimo 1 parágrafo denso)."
    )

class FonteRDetalhada(BaseModel):
    livro_autor: str = Field(description="Nome do livro e sobrenome do autor (ex: Bussab & Morettin, Wooldridge).")
    capitulo: str = Field(description="Capítulo específico consultado no documento RAG.")
    paginas_utilizadas: str = Field(description="Número exato da página ou intervalo de páginas de onde o conteúdo foi extraído (ex: p. 234, pp. 112-115). Obrigatório.")

# ==========================================
# SCHEMAS DO AGENTE 2 (ESCRITOR TEÓRICO)
# ==========================================

class ConteudoSubtopico(BaseModel):
    """
    Modelo unificado e determinístico de conteúdo do subtópico.
    Evita o uso de Union (anyOf/oneOf) que gera erros de compatibilidade na API do Gemini (Structured Outputs).
    """
    tipo_bloco: Literal["teorico"] = Field(
        default="teorico",
        description="O tipo do bloco: sempre 'teorico'."
    )
    
    # ----------------------------------------------------
    # CAMPOS COMUNS
    # ----------------------------------------------------
    conceito_intuitivo: str = Field(description="Explicação profunda do conceito em linguagem natural e fluida, sem formalismo matemático ainda.")
    conceito_formal: str = Field(description="Definição matemática precisa ou enunciado acadêmico formal do conceito em LaTeX.")
    propriedades_do_conceito: List[str] = Field(description="Lista de regras, teoremas ou leis que este conceito sempre segue.")
    pre_requisitos_e_auxiliares: List[str] = Field(description="Mapeamento de ferramentas matemáticas ou aulas passadas necessárias aqui.")
    condicoes_de_contorno: List[str] = Field(description="Suposições obrigatórias para que a teoria seja válida. Se não houver, responda 'N/A'.")
    
    # --- O NOVO CAMPO ACIONADOR DE INTERATIVIDADE ---
    simulador_interativo_recomendado: Optional[str] = Field(
        default=None, 
        description="Se o subtópico se beneficiar de um gráfico parametrizado por sliders, descreva detalhadamente qual simulação deve ser renderizada aqui (Ex: 'Plotar curva gaussiana bicaudal onde o slider altera alfa'). Se não precisar, deixe None."
    )
    
    # ----------------------------------------------------
    # CAMPOS ESPECÍFICOS DE CONTEÚDO TEÓRICO
    # ----------------------------------------------------
    deducao_formal_passo_a_passo: Optional[List[str]] = Field(
        default=None,
        description="O passo a passo detalhado da derivação matemática das fórmulas em LaTeX."
    )
    interpretacao_geometrica_grafica: Optional[str] = Field(
        default=None,
        description="A descrição de como visualizar esse teorema espacialmente ou em gráficos."
    )
    
    # ----------------------------------------------------
    # EXEMPLO CANÔNICO
    # ----------------------------------------------------
    exemplo_canonico: Optional[EstruturaExemplo] = Field(
        default=None,
        description="O exemplo (clássico ou prático) estruturado ou None."
    )

class SubtopicoValidado(BaseModel):
    titulo_subtopico: str
    conteudo: ConteudoSubtopico = Field(description="O conteúdo do subtópico estruturado (teórico).")
    fontes_rag: List[FonteRDetalhada] = Field(description="Lista de fontes bibliográficas detalhadas extraídas estritamente do RAG.")

# ==========================================
# SCHEMAS DO AGENTE 3 (CRIADOR DE EXERCÍCIOS)
# ==========================================

class AlternativasFechadas(BaseModel):
    A: str = Field(description="Opção alternativa A.")
    B: str = Field(description="Opção alternativa B.")
    C: str = Field(description="Opção alternativa C.")
    D: str = Field(description="Opção alternativa D.")
    E: Optional[str] = Field(default=None, description="Opção alternativa E (opcional).")

class QuestaoFechada(BaseModel):
    enunciado: str = Field(description="O problema prático com uma situação estatística clara.")
    alternativas: AlternativasFechadas = Field(description="As alternativas estruturadas contendo exatamente de A a D (e opcionalmente E).")
    alternativa_correta: str = Field(description="A letra da alternativa correta (Ex: 'A', 'B', 'C', 'D' ou 'E').")
    dica: str = Field(description="Orientação sutil para o aluno pensar, sem dar a resposta direta.")
    gabarito_comentado: str = Field(description="Explicação detalhada do porquê aquela alternativa é a correta.")
    codigo_plotly: Optional[str] = Field(
        default=None,
        description="Código Python puro utilizando Plotly para gerar um gráfico interativo de suporte para esta questão (ex: curvas de distribuição, dispersão, boxplot). O código deve criar um objeto de figura chamado 'fig'. Não inclua importações, utilize a paleta do professor e use chaves únicas. Se não for necessário gráfico, deixe None."
    )
    referencia_livro: Optional[str] = Field(
        default=None,
        description="Se a questão for inspirada ou extraída de um livro/material do RAG, forneça a referência exata (ex: 'Bussab & Morettin, Estatística Básica, Cap 5, p. 115'). Caso contrário, deixe None."
    )

class QuestaoAberta(BaseModel):
    enunciado: str = Field(description="Pergunta discursiva ou problema de cálculo estatístico detalhado.")
    dica: str = Field(description="Diretriz conceitual ou fórmula que o aluno deve lembrar para resolver.")
    gabarito_passo_a_passo: List[str] = Field(description="Passo a passo matemático para se chegar à resolução completa.")
    codigo_plotly: Optional[str] = Field(
        default=None,
        description="Código Python puro utilizando Plotly para gerar um gráfico interativo de suporte para esta questão (ex: densidades, distribuições). O código deve criar um objeto de figura chamado 'fig'. Não inclua importações, utilize a paleta do professor. Se não for necessário gráfico, deixe None."
    )
    referencia_livro: Optional[str] = Field(
        default=None,
        description="Se a questão for inspirada ou extraída de um livro/material do RAG, forneça a referência exata (ex: 'Wooldridge, Introdução à Econometria, Cap 2, p. 45'). Caso contrário, deixe None."
    )
    resposta_numerica_esperada: Optional[float] = Field(
        default=None,
        description="Se a questão exigir um cálculo numérico específico (ex: 2.34 ou 0.05), forneça o valor float final esperado para validação automática na interface. Se for de cunho puramente discursivo-prosa, deixe None."
    )

class CadernoExerciciosSubtopico(BaseModel):
    questoes_multipla_escolha: List[QuestaoFechada] = Field(
        description="Lista contendo obrigatoriamente exatamente 2 questões de múltipla escolha complexas baseadas no subtópico."
    )
    questoes_discursivas: List[QuestaoAberta] = Field(
        description="Lista contendo obrigatoriamente exatamente 3 questões discursivas/cálculos complexas baseadas no subtópico."
    )

class CadernoExerciciosValidado(BaseModel):
    topico_aula: str
    questoes_multipla_escolha: List[QuestaoFechada] = Field(
        description="Lista contendo obrigatoriamente pelo menos 5 questões de múltipla escolha complexas."
    )
    questoes_discursivas: List[QuestaoAberta] = Field(
        description="Lista contendo obrigatoriamente pelo menos 3 questões discursivas/cálculos complexas."
    )

class PaginaLapidada(BaseModel):
    titulo_subtopico: str
    discussao_teorica_prosa: str = Field(description="Texto longo e denso em prosa acadêmica sem bullets. O conteúdo deve se conectar fluentemente com o subtópico anterior.")
    prosa_longa_expandida: Optional[str] = Field(default=None, description="Texto extremamente longo, denso e exaustivo em prosa fluida gerado pelo Construtor de Prosa.")
    formalismo_latex: str = Field(description="Bloco de fórmulas em LaTeX ($$) sem repetições de equações que já apareceram na aula.")
    
    # Mudança de String para List para forçar a abertura de todas as linhas matemáticas
    deducao_analitica_linhas: List[str] = Field(
        description="A derivação matemática completa dividida linha por linha em LaTeX ($$). Cada item da lista deve ser uma equação que se desdobra logicamente da anterior."
    )
    
    # Transformado em lista obrigatória para garantir volume de conteúdo prático
    exemplos_praticos_ricos: List[ExemploResolvidoRico] = Field(
        description="Lista contendo obrigatoriamente de 2 a 3 exemplos práticos e resolvidos de alta complexidade sobre o subtópico."
    )
    
    simulador_interativo_recomendado: Optional[str] = Field(
        default=None,
        description="Descrição detalhada do simulador interativo recomendado para esta página se houver."
    )

class MapeamentoSimulador(BaseModel):
    indice_pagina: str = Field(description="O índice da página (ex: '1', '2', '3') onde o simulador interativo deve ser carregado.")
    nome_simulador: str = Field(description="O nome descritivo do simulador interativo correspondente (ex: 'Visualizador de Erros').")
    descricao_simulador: str = Field(default="", description="Diretrizes de parâmetros, sliders e o comportamento detalhado da simulação estatística a ser programada.")

class AulaUnificadaELapidada(BaseModel):
    tema_global: str
    paginas_conteudo: List[PaginaLapidada] = Field(description="A sequência de páginas da aula, livre de repetições textuais ou conceituais.")
    # --- MAPEAMENTO CENTRALIZADO DE SIMULADORES (Acaba com gráficos repetidos) ---
    simuladores_da_aula: List[MapeamentoSimulador] = Field(
        description="Lista contendo o mapeamento de onde os gráficos devem entrar. Atribua gráficos apenas onde for vital, garantindo que nenhum gráfico seja igual ao outro."
    )
    # --- O RODAPÉ EXIGIDO PELO PROFESSOR ---
    referencias_bibliograficas_finais: List[str] = Field(description="Lista consolidada e unificada de livros e páginas reais utilizadas em toda a extensão da aula (sem duplicatas).")

class CoresMapeadas(BaseModel):
    cor_primaria: Optional[str] = Field(None, description="Cor primária em formato hexadecimal (ex: #1E3A8A)")
    cor_secundaria: Optional[str] = Field(None, description="Cor secundária em formato hexadecimal (ex: #10B981)")
    cor_alerta: Optional[str] = Field(None, description="Cor de alerta em formato hexadecimal (ex: #F59E0B)")
    cor_critica: Optional[str] = Field(None, description="Cor crítica em formato hexadecimal (ex: #991B1B)")

class NotacaoCustomizadaMapeada(BaseModel):
    conceito: str = Field(description="Nome do conceito matemático personalizado (ex: taxa de falha)")
    simbolo: str = Field(description="Símbolo em LaTeX correspondente (ex: $\\lambda_f$)")

class DiretrizesProfessorMapeadas(BaseModel):
    # População & Amostra
    tamanho_amostral: Optional[str] = Field(None, description="Notação LaTeX para tamanho amostral (ex: $n$)")
    tamanho_populacional: Optional[str] = Field(None, description="Notação LaTeX para tamanho populacional (ex: $N$)")
    media_populacional: Optional[str] = Field(None, description="Notação LaTeX para média populacional (ex: $\\mu$)")
    media_amostral: Optional[str] = Field(None, description="Notação LaTeX para média amostral (ex: $\\bar{X}$)")
    variancia_populacional: Optional[str] = Field(None, description="Notação LaTeX para variância populacional (ex: $\\sigma^2$)")
    variancia_amostral: Optional[str] = Field(None, description="Notação LaTeX para variância amostral (ex: $S^2$)")
    desvio_padrao_populacional: Optional[str] = Field(None, description="Notação LaTeX para desvio padrão populacional (ex: $\\sigma$)")
    desvio_padrao_amostral: Optional[str] = Field(None, description="Notação LaTeX para desvio padrão amostral (ex: $S$)")
    proporcao_populacional: Optional[str] = Field(None, description="Notação LaTeX para proporção populacional (ex: $p$)")
    proporcao_amostral: Optional[str] = Field(None, description="Notação LaTeX para proporção amostral (ex: $\\hat{p}$)")
    margem_erro: Optional[str] = Field(None, description="Notação LaTeX para margem de erro (ex: $E$)")
    intervalo_confianca: Optional[str] = Field(None, description="Notação LaTeX para intervalo de confiança (ex: $IC$)")
    erro_padrao_media: Optional[str] = Field(None, description="Notação LaTeX para erro padrão da média (ex: $EP(\\bar{X})$)")

    # Inferência & Hipóteses
    hipotese_nula: Optional[str] = Field(None, description="Notação LaTeX para hipótese nula (ex: $H_0$)")
    hipotese_alternativa: Optional[str] = Field(None, description="Notação LaTeX para hipótese alternativa (ex: $H_1$ ou $H_a$)")
    nivel_significancia: Optional[str] = Field(None, description="Notação LaTeX para nível de significância / alfa (ex: $\\alpha$)")
    nivel_confianca: Optional[str] = Field(None, description="Notação LaTeX para nível de confiança (ex: $1 - \\alpha$)")
    erro_tipo_2: Optional[str] = Field(None, description="Notação LaTeX para erro tipo II / beta (ex: $\\beta$)")
    poder_teste: Optional[str] = Field(None, description="Notação LaTeX para poder do teste (ex: $1 - \\beta$)")
    p_valor: Optional[str] = Field(None, description="Notação LaTeX para p-valor (ex: $p\\text{-valor}$)")
    regiao_rejeicao: Optional[str] = Field(None, description="Notação LaTeX para região de rejeição / crítica (ex: $RC$)")
    graus_liberdade: Optional[str] = Field(None, description="Notação LaTeX para graus de liberdade (ex: $gl$)")
    graus_liberdade_num: Optional[str] = Field(None, description="Notação LaTeX para graus de liberdade do numerador (ex: $gl_{\\text{num}}$)")
    graus_liberdade_den: Optional[str] = Field(None, description="Notação LaTeX para graus de liberdade do denominador (ex: $gl_{\\text{den}}$)")
    estatistica_z_calc: Optional[str] = Field(None, description="Notação LaTeX para estatística Z calculada (ex: $Z_{\\text{calc}}$)")
    estatistica_t_calc: Optional[str] = Field(None, description="Notação LaTeX para estatística t calculada (ex: $t_{\\text{calc}}$)")
    estatistica_chi2_calc: Optional[str] = Field(None, description="Notação LaTeX para estatística Qui-Quadrado calculada (ex: $\\chi^2_{\\text{calc}}$)")
    estatistica_f_calc: Optional[str] = Field(None, description="Notação LaTeX para estatística F calculada (ex: $F_{\\text{calc}}$)")
    valor_critico_z: Optional[str] = Field(None, description="Notação LaTeX para valor crítico de Z (ex: $Z_{\\text{crit}}$)")
    valor_critico_t: Optional[str] = Field(None, description="Notação LaTeX para valor crítico de t (ex: $t_{\\text{crit}}$)")
    valor_critico_chi2: Optional[str] = Field(None, description="Notação LaTeX para valor crítico de Qui-Quadrado (ex: $\\chi^2_{\\text{crit}}$)")
    valor_critico_f: Optional[str] = Field(None, description="Notação LaTeX para valor crítico de F (ex: $F_{\\text{crit}}$)")

    # Regressão & Correlação
    correlacao_populacional: Optional[str] = Field(None, description="Notação LaTeX para correlação populacional (ex: $\\rho$)")
    correlacao_amostral: Optional[str] = Field(None, description="Notação LaTeX para correlação amostral (ex: $r$)")
    coeficiente_determinacao: Optional[str] = Field(None, description="Notação LaTeX para coeficiente de determinação (ex: $R^2$)")
    covariancia_populacional: Optional[str] = Field(None, description="Notação LaTeX para covariância populacional (ex: $\\sigma_{XY}$)")
    covariancia_amostral: Optional[str] = Field(None, description="Notação LaTeX para covariância amostral (ex: $S_{XY}$)")
    intercepto_populacional: Optional[str] = Field(None, description="Notação LaTeX para intercepto populacional (ex: $\\beta_0$)")
    inclinacao_populacional: Optional[str] = Field(None, description="Notação LaTeX para inclinação populacional (ex: $\\beta_1$)")
    intercepto_estimado: Optional[str] = Field(None, description="Notação LaTeX para intercepto estimado (ex: $\\hat{\\beta}_0$)")
    inclinacao_estimado: Optional[str] = Field(None, description="Notação LaTeX para inclinação estimada (ex: $\\hat{\\beta}_1$)")
    residuo_amostral: Optional[str] = Field(None, description="Notação LaTeX para resíduo amostral (ex: $e_i$)")
    soma_quadrados_regressao: Optional[str] = Field(None, description="Notação LaTeX para soma de quadrados da regressão (ex: $SQR$)")
    soma_quadrados_erro: Optional[str] = Field(None, description="Notação LaTeX para soma de quadrados do erro (ex: $SQE$)")
    soma_quadrados_total: Optional[str] = Field(None, description="Notação LaTeX para soma de quadrados total (ex: $SQT$)")

    # Distribuições & Funções
    distribuicao_normal: Optional[str] = Field(None, description="Notação LaTeX para distribuição normal (ex: $N(\\mu, \\sigma^2)$)")
    distribuicao_normal_padrao: Optional[str] = Field(None, description="Notação LaTeX para distribuição normal padrão (ex: $N(0, 1)$)")
    distribuicao_t: Optional[str] = Field(None, description="Notação LaTeX para distribuição t de Student (ex: $t(gl)$)")
    distribuicao_qui_quadrado: Optional[str] = Field(None, description="Notação LaTeX para distribuição Qui-Quadrado (ex: $\\chi^2(gl)$)")
    distribuicao_f: Optional[str] = Field(None, description="Notação LaTeX para distribuição F de Snedecor (ex: $F(gl_{\\text{num}}, gl_{\\text{den}})$)")
    distribuicao_binomial: Optional[str] = Field(None, description="Notação LaTeX para distribuição binomial (ex: $Bin(n, p)$)")
    distribuicao_poisson: Optional[str] = Field(None, description="Notação LaTeX para distribuição de Poisson (ex: $Poi(\\lambda)$)")
    funcao_densidade: Optional[str] = Field(None, description="Notação LaTeX para função de densidade (ex: $f(x)$)")
    funcao_acumulada: Optional[str] = Field(None, description="Notação LaTeX para função acumulada (ex: $F(x)$)")
    somatorio: Optional[str] = Field(None, description="Notação LaTeX para somatório (ex: $\\sum$)")
    productorio: Optional[str] = Field(None, description="Notação LaTeX para produtório (ex: $\\prod$)")
    integral: Optional[str] = Field(None, description="Notação LaTeX para integral (ex: $\\int$)")

    # Adicionais e Cores
    cores_preferidas: Optional[CoresMapeadas] = Field(None, description="Cores preferidas de identidade visual extraídas do texto.")
    diretrizes_estilo_livre: Optional[str] = Field(None, description="Outras diretrizes didáticas, de escrita, tom de voz, exemplos ou restrições gerais extraídas.")
    notacoes_customizadas: Optional[List[NotacaoCustomizadaMapeada]] = Field(None, description="Lista de notações extras personalizadas não mapeadas nos campos padrão.")
