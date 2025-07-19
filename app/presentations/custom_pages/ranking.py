import streamlit as st
import pandas as pd
import os
import sys
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

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

    #st.markdown(""" Introdução: """)

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

    colunas_para_exibir = [
                        'codigo',
                        'nome', 
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

    #st.dataframe(prospects_df_vaga)

    gb = GridOptionsBuilder.from_dataframe(prospects_df_vaga)
    gb.configure_default_column(
            resizable=True,
            filter=False,
            editable=False,
            sortable=True
        )
    gb.configure_selection('single')  # apenas uma linha selecionável
    grid_options = gb.build()

    grid_response = AgGrid(
        prospects_df_vaga,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        height=200,
        theme="streamlit", 
        fit_columns_on_grid_load=True,
        allow_unsafe_jscode=False
        
    )

    selected = grid_response["selected_rows"]

    

########################################################################

    if selected is not None and not pd.DataFrame(selected).empty:

        candidato_selecionado = selected['codigo'].values[0]
        nome_selecionado = selected['Nome'].values[0]

        #st.markdown(f"**Aplicante selecionado:** {nome_selecionado}")

        st.markdown(f"Vagas aplicadas pelo(a) **{nome_selecionado}**")
        prospects_df_applicants = prospects.get_prospects_applicants(candidato_selecionado)

        features_df_applicants = features_case.get_features_applicants(candidato_selecionado)

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

        #st.dataframe(prospects_df_applicants)
        
        gb = GridOptionsBuilder.from_dataframe(prospects_df_applicants)
        gb.configure_default_column(
            resizable=True,
            filter=False,
            editable=False,
            sortable=True
        )
        # Não configure seleção!

        grid_options = gb.build()

        # Exibição sem seleção
        AgGrid(
            prospects_df_applicants,
            gridOptions=grid_options,
            update_mode="NO_UPDATE",
            height=400,
            theme="streamlit",  # mantém o visual similar ao st.dataframe
            fit_columns_on_grid_load=True,
            allow_unsafe_jscode=False
        )
    else:
        st.info("Selecione um candidato para ver detalhes.", icon="ℹ️")