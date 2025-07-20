import streamlit as st
import sys
import os
from streamlit_option_menu import option_menu

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from presentations.custom_pages import ranking, modelo, glossario

st.set_page_config(
    page_title="Aderis X",
    page_icon="bar-chart",
    layout="wide", #centered
    initial_sidebar_state="expanded",
    menu_items={
        'Report a bug': "https://github.com/Leandrolsc/PosTech_DataAnalytics_Datathon/issues",
        'About': """
        ## Sobre o Projeto
        Esta aplicação foi desenvolvida como parte do trabalho da Fase 4 da Pós Tech em Data Analytics na FIAP.  
        O objetivo é realizar uma análise do preço do petróleo Brent, utilizando dados históricos extraídos do IPEA (Instituto de Pesquisa Econômica Aplicada).  
        A aplicação permite visualizar os dados, gerar gráficos temporais, realizar previsões com Machine Learning e baixar as informações em formato CSV.
        """
    }
)

with st.sidebar:
    escolha = option_menu(
        "",
        ["Introdução", 
         "Ranking de Candidatos", 
         "Guia Aderis X",
         "Glossário Aderis"
         ],
        icons=['', 
               'bar-chart', 
               'gear',
               ],
        menu_icon="cast",
        default_index=0
    )

if escolha == "Ranking de Candidatos":
    ranking.exibir()
elif escolha == "Guia Aderis X":
    modelo.exibir()
elif escolha == "Glossário Aderis":
    glossario.exibir()
elif escolha == "Introdução":
    st.title("Aderis X – Datathon")

    st.markdown("""
    🚀 **Este projeto faz parte do Datathon da Pós Tech em Data Analytics da FIAP.**

    ---

    ### **Nosso Propósito**

    Acreditamos em **contratações com 100% de certeza**.  
    O processo seletivo **não deveria ser um jogo de azar**: cada contratação errada custa tempo, dinheiro e, mais importante, **potencial perdido**.

    Criamos esta ferramenta porque confiamos que a tecnologia de ponta pode **eliminar a incerteza do recrutamento**.  
    Queremos transformar a busca por talentos em uma **ciência exata**, garantindo que cada pessoa contratada não apenas preencha uma vaga, mas **impulsione o futuro da empresa** e **construa uma carreira duradoura**.

    *Traduzindo dados em decisões, com total transparência.*

    ---

    ###  **Como Funciona**

    Nosso motor de inteligência preditiva utiliza uma **rede neural avançada**, capaz de analisar simultaneamente **dezenas de variáveis críticas**, como:

    - Competências técnicas  
    - Experiência profissional  
    - Localização  
    - Formação acadêmica  

    ---

    ### **Funcionalidades Principais**

    1. **Match Preditivo**  
    Em segundos, a plataforma cruza os requisitos da vaga com o perfil de cada candidato, gerando um nível de **aderência preciso e instantâneo**.

    2. **Diagnóstico Claro**  
    Não entregamos apenas um número.  
    Para cada candidato, nossa ferramenta apresenta **explicações claras e objetivas** sobre o resultado.

    > *Exemplo:*  
    > *"O candidato X tem **86% de aderência** a esta vaga. Ele possui o conhecimento em SAP exigido, é fluente em inglês e mora no local da vaga. O principal ponto de atenção é a ausência da pós-graduação, que foi listada como um diferencial."*

    ---

    ### **Aderis X: Inteligência a Serviço do Recrutamento**

    Este é o **Aderis X**: sua **plataforma de inteligência preditiva** para recrutamento de alto desempenho.  
    Capacite sua equipe a tomar decisões **mais rápidas**, **mais inteligentes** e com **maior taxa de sucesso**.

    Com o Aderis X, ofereça aos seus clientes o que ninguém mais pode:  
    **a certeza de encontrar o candidato ideal. Sempre.**
    """)



    #st.markdown("Repositório do projeto: [GitHub - Leandrolsc/PosTech_DataAnalytics_Datathon](https://github.com/Leandrolsc/PosTech_DataAnalytics_Datathon)")

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; font-size: 0.95em;'>
        <b>Datathon da PosTech em Data Analytics da FIAP</b><br>
        Desenvolvido por: 
        <a href='https://www.linkedin.com/in/leandro-victor-silva-8a319b228/' target='_blank'><b>Leandro Victor Silva</b></a> e 
        <a href='https://www.linkedin.com/in/murilo-maioli-21195aaa/' target='_blank'><b>Murilo Maioli</b></a><br>
        Repositório do projeto: 
        <a href='https://github.com/Leandrolsc/PosTech_DataAnalytics_Datathon' target='_blank'>
           <b>GitHub - Leandrolsc/PosTech_DataAnalytics_Datathon</b>
        </a>
    </div>
    """,
    unsafe_allow_html=True
)