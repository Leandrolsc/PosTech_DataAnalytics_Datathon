import streamlit as st
import sys
import os
from streamlit_option_menu import option_menu

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from presentations.custom_pages import ranking, modelo

st.set_page_config(
    page_title="Datathon - Decision - Recrutamento e Seleção",
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
         "Explicacao do Modelo ML",
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
elif escolha == "Explicacao do Modelo ML":
    modelo.exibir()
elif escolha == "Introdução":
    st.title("Datathon - Decision - Recrutamento e Seleção")
    st.markdown("""
    Este projeto faz parte do **Datathon da Pós Tech em Data Analytics na FIAP**.  
    O objetivo é .....)**.

    A aplicação permite .....
    """)


    st.markdown("Repositório do projeto: [GitHub - Leandrolsc/PosTech_DataAnalytics_Datathon](https://github.com/Leandrolsc/PosTech_DataAnalytics_Datathon)")

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