import streamlit as st
import pandas as pd
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from use_cases.load_vagas_list import LoadVagasListUseCase
from use_cases.get_prospects import GetProspectsUseCase
from use_cases.load_applicants_list import LoadApplicantsListUseCase
#from use_cases.match_predictor import MatchPredictor
from use_cases.featureengineering import CandidateFeatureEngineer
from use_cases.get_features import GetFeaturesCase    

# Configurações da página
st.set_page_config(
    page_title="Rankeamento de Candidatos",
    page_icon=":briefcase:"
    )

st.title(":briefcase: Rankeamento de Candidatos")

## https://www.linkedin.com/company/decisionbr-consultants/

st.markdown(""" Introdução: """)

#predictor = MatchPredictor()
#predictor.load_model()

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

st.dataframe(prospects_df)


features_case = GetFeaturesCase()
features_df = features_case.get_features(vaga_selecionada_codigo)

st.dataframe(features_df)