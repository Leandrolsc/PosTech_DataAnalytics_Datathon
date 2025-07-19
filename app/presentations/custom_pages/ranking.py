import streamlit as st
import pandas as pd
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from use_cases.load_vagas_list import LoadVagasListUseCase
from use_cases.get_prospects import GetProspectsUseCase
from use_cases.load_applicants_list import LoadApplicantsListUseCase
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
    prospects_df_vaga = prospects.get_prospects_vaga(vaga_selecionada_codigo)


    features_case = GetFeaturesCase()
    features_df_vaga = features_case.get_features_vaga(vaga_selecionada_codigo)


    probabilidade = predictor.create_ranking(features_df_vaga)
    prospects_df_vaga = prospects_df_vaga.merge(probabilidade, on='codigo', how='left')
    prospects_df_vaga = prospects_df_vaga.sort_values(by='probabilidade_match', ascending=False)

    colunas_para_exibir = ['nome', 
                        'data_candidatura', 
                        'situacao_candidado', 
                        'probabilidade_match']
    prospects_df_vaga = prospects_df_vaga[colunas_para_exibir]
    prospects_df_vaga = prospects_df_vaga.rename(columns={
        'nome': 'Nome',
        'data_candidatura': 'Data de Aplicação',
        'situacao_candidado': 'Situação do Candidato',
        'probabilidade_match': 'Nível de Aderência à vaga (Match)'
    })

    st.write(prospects_df_vaga)



########################################################################




    listapplicantsuse = LoadApplicantsListUseCase()
    lista_applicants = listapplicantsuse.load_applicants_list()
    apliccants_selecionado = st.selectbox(
                                    "Selecione um Candidato",
                                    options=lista_applicants
                                    )
    st.markdown(f"**Aplicante selecionado:** {apliccants_selecionado}")

    apliccants_selecionado_codigo = lista_applicants[lista_applicants['nome'] == apliccants_selecionado]['codigo'].values[0]
    prospects_df_applicants = prospects.get_prospects_applicants(apliccants_selecionado_codigo)

    features_df_applicants = features_case.get_features_applicants(apliccants_selecionado_codigo)

    probabilidade_applicants = predictor.create_ranking(features_df_applicants)

    prospects_df_applicants = prospects_df_applicants.merge(probabilidade_applicants, left_on='vaga_codigo', right_on='id_vaga', how='left')

    prospects_df_applicants = prospects_df_applicants.sort_values(by='probabilidade_match', ascending=False)

    colunas_para_exibir = ['titulo',
                        'data_candidatura', 
                        'situacao_candidado', 
                        'probabilidade_match']
    prospects_df_applicants = prospects_df_applicants[colunas_para_exibir]
    prospects_df_applicants = prospects_df_applicants.rename(columns={
        'titulo': 'Vaga',
        'data_candidatura': 'Data de Aplicação',
        'situacao_candidado': 'Situação do Candidato',
        'probabilidade_match': 'Nível de Aderência à vaga (Match)'
    })

    st.write(prospects_df_applicants)