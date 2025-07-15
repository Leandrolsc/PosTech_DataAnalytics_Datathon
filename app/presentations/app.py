import streamlit as st
import pandas as pd
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from use_cases.load_vagas_list import LoadVagasListUseCase
from use_cases.load_applicants_list import LoadApplicantsListUseCase
from use_cases.compatibility import CompatibilityUseCase
from use_cases.match_predictor import MatchPredictor
from use_cases.featureengineering import CandidateFeatureEngineer
    
# Configurações da página
st.set_page_config(
    page_title="Rankeamento de Candidatos",
    page_icon=":briefcase:"
    )


st.title(":briefcase: Rankeamento de Candidatos")

## https://www.linkedin.com/company/decisionbr-consultants/


st.markdown(""" Introdução: """)



# processor = CandidateFeatureEngineer()
    
#     # Executa o pipeline completo
# df_final = processor.process_all(
#     applicants_path="app/data/bronze/applicants.json",
#     prospects_path="app/data/bronze/prospects.json",
#     vagas_path="app/data/bronze/vagas.json",
#     output_path="app/data/silver/df_ML_tunado.parquet"
# )

# st.write("Features criadas:")
# st.write(df_final.columns.tolist())


# Exemplo de uso:

# 1. Treinar e salvar o modelo
predictor = MatchPredictor()
predictor.train_model("app/data/silver/df_ML_tunado.parquet")
predictor.save_model()

# 2. Carregar modelo já treinado
predictor.load_model()



# 3. Fazer predição individual
# exemplo_candidato = {
#     'feature1': 0.5,
#     'feature2': 1.2,
#     'feature3': 0.8,
#     # ... outras features
# }
# probabilidade = predictor.predict_match(exemplo_candidato)
# print(f"Probabilidade de match: {probabilidade:.4f}")

# 4. Fazer predição em lote
# df_novos_candidatos = pd.read_csv("novos_candidatos.csv")
# ranking = predictor.create_ranking(df_novos_candidatos)
# print(ranking[['id_vaga', 'dict_prospect_codigo', 'probabilidade_match']].head(10))


