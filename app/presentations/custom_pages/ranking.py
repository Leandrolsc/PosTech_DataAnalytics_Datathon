import streamlit as st
import pandas as pd
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from use_cases.load_vagas_list import LoadVagasListUseCase
from use_cases.get_prospects import GetProspectsUseCase
#from use_cases.load_applicants_list import LoadApplicantsListUseCase
from use_cases.match_predictor import MatchPredictor
#from use_cases.featureengineering import CandidateFeatureEngineer
from use_cases.get_features import GetFeaturesCase    


def exibir():
    st.title(":briefcase: Rankeamento de Candidatos")

    ## https://www.linkedin.com/company/decisionbr-consultants/

    st.markdown(""" Introdução: """)

    predictor = MatchPredictor()
    predictor.load_model()

    listvagasuse = LoadVagasListUseCase()

    lista_vagas = listvagasuse.load_vagas_list()

    vaga_selecionada = st.selectbox(
        "Selecione uma vaga",
        options=lista_vagas
        )

    st.markdown(f"**Vaga selecionada:** {vaga_selecionada}")

    prospects = GetProspectsUseCase()

    vaga_selecionada_codigo = lista_vagas[lista_vagas['titulo'] == vaga_selecionada]['codigo'].values[0]

    prospects_df = prospects.get_prospects(vaga_selecionada_codigo)


    features_case = GetFeaturesCase()
    features_df = features_case.get_features(vaga_selecionada_codigo)


    probabilidade = predictor.create_ranking(features_df)

    prospects_df = prospects_df.merge(probabilidade, on='codigo', how='left')

    prospects_df = prospects_df.sort_values(by='probabilidade_match', ascending=False)

    colunas_para_exibir = ['nome', 
                        'data_candidatura', 
                        'situacao_candidado', 
                        'probabilidade_match']
    prospects_df = prospects_df[colunas_para_exibir]


    st.write(prospects_df)

