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

    st.markdown("""
                <style>
                        /* Cor do texto do label "Selecione uma vaga" */
                        .stSelectbox > label {
                            color: white;
                        }
                        
                        /* Cor do texto do item selecionado dentro da caixa */
                        div[data-baseweb="select"] > div {
                            color: white;
                        }
                    </style>
                    """, unsafe_allow_html=True)
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

    def classificar_aderencia(prob):
        if prob >= 0.8:
            return 'Alta'
        elif prob >= 0.5:
            return 'Média'
        else:
            return 'Baixa'

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

    prospects_df_vaga['probabilidade_match'] = prospects_df_vaga['probabilidade_match'].round(2)
    prospects_df_vaga['Nível de Aderência'] = prospects_df_vaga['probabilidade_match'].apply(classificar_aderencia)
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
    gb.configure_column(
            "Nível de Aderência à vaga (Match)",
            type=["numericColumn", "numberColumnFilter", "customNumericFormat"],
            precision=2,
            valueFormatter="x.toFixed(2)"
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

        st.markdown(f"Vagas aplicadas pelo(a): **{nome_selecionado}**")
        prospects_df_applicants = prospects.get_prospects_applicants(candidato_selecionado)

        features_df_applicants = features_case.get_features_applicants(candidato_selecionado)

        probabilidade_applicants = predictor.create_ranking(features_df_applicants)

        prospects_df_applicants = prospects_df_applicants.merge(probabilidade_applicants, left_on='vaga_codigo', right_on='id_vaga', how='left')

        prospects_df_applicants = prospects_df_applicants.sort_values(by='probabilidade_match', ascending=False)

        colunas_para_exibir = ['id_vaga',
                            'titulo',
                            'data_candidatura', 
                            'situacao_candidado', 
                            'probabilidade_match']
        prospects_df_applicants = prospects_df_applicants[colunas_para_exibir]

        prospects_df_applicants['probabilidade_match'] = prospects_df_applicants['probabilidade_match'].round(2)
        prospects_df_applicants['Nível de Aderência'] = prospects_df_applicants['probabilidade_match'].apply(classificar_aderencia)

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

        gb.configure_column(
            "Nível de Aderência à vaga (Match)",
            type=["numericColumn", "numberColumnFilter", "customNumericFormat"],
            precision=2,
            valueFormatter="x.toFixed(2)"
        )

        grid_options = gb.build()
        gb.configure_selection('single')  # apenas uma linha selecionável
        grid_response_v = AgGrid(
            prospects_df_applicants,
            gridOptions=grid_options,
            update_mode=GridUpdateMode.SELECTION_CHANGED,
            height=400,
            theme="streamlit",  # mantém o visual similar ao st.dataframe
            fit_columns_on_grid_load=True,
            allow_unsafe_jscode=False
        )

        selected_v = grid_response_v["selected_rows"]

        if selected_v is not None and not pd.DataFrame(selected_v).empty:
            vaga_selecionada = selected_v['Vaga'].values[0]
            st.markdown(f"\n🧠 Tabela descritiva SHAP para o(a) **{nome_selecionado}** na vaga **{vaga_selecionada}** com as variaveis que mais impactaram o modelo.")
            
            id_vaga_selecionada = selected_v['id_vaga'].values[0]

            feature_selecionada = features_df_applicants[features_df_applicants['id_vaga'] == id_vaga_selecionada]
           
            #st.write(feature_selecionada)


            # # --- Etapa 3: Gerar e Exibir Explicações SHAP ---
            try:
                df_shap_explanations = predictor.explain_batch_with_shap(feature_selecionada, top_n=3)

                top_3_asc = df_shap_explanations[:3]
              
                top_3_desc = df_shap_explanations[3:]

                st.markdown(f"""
                    ### Principais variáveis que **mais contribuíram** para a previsão

                    1. **{top_3_asc['feature'][0]}**  
                    Impacto no modelo: **+{top_3_asc['shap_value'][0].round(2)}**

                    2. **{top_3_asc['feature'][1]}**  
                    Impacto no modelo: **+{top_3_asc['shap_value'][1].round(2)}**

                    3. **{top_3_asc['feature'][2]}**  
                    Impacto no modelo: **+{top_3_asc['shap_value'][2].round(2)}**

                    ---

                    ### Principais variáveis que **mais prejudicaram** a previsão

                    1. **{top_3_desc['feature'][3]}**  
                    Impacto no modelo: **{top_3_desc['shap_value'][3].round(2)}**

                    2. **{top_3_desc['feature'][4]}**  
                    Impacto no modelo: **{top_3_desc['shap_value'][4].round(2)}**

                    3. **{top_3_desc['feature'][5]}**  
                    Impacto no modelo: **{top_3_desc['shap_value'][5].round(2)}**
                    """)


            except Exception as e:
                st.write(f"❌ Ocorreu um erro ao gerar as explicações SHAP: {e}")

        else:
            st.info("Selecione uma vaga.", icon="ℹ️")

    else:
        st.info("Selecione um candidato para ver detalhes.", icon="ℹ️")


                        # # Mostrar a importância global das features que foi salva no background_data
                # st.write("\n🌟 Importância Global das Features (média dos valores SHAP absolutos):")
                # feature_importance = predictor.get_background_data('feature_importance')
                # for feature, imp in list(feature_importance.items())[:5]:
                #     st.write(f"  - {feature}: {imp:.4f}")