import pandas as pd
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class GetFeaturesCase:
    def __init__(self, data_path="app/data/silver"):
        """
        Inicializa o caso de uso com o caminho para os dados.
        """
        self.data_path = data_path

    def get_features(self, vaga_codigo: str) -> pd.DataFrame:
        # Carrega os DataFrames necessários
        df_features = pd.read_parquet(os.path.join(self.data_path, 'df_features.parquet'))

        # Filtra para encontrar a vaga selecionada pelo código
        
        df_features["id_vaga"] = df_features["id_vaga"].astype(str).str.replace(",", "")
        df = df_features[df_features["id_vaga"] == vaga_codigo]
         
        return df  