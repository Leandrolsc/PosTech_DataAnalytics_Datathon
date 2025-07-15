import pandas as pd
import os
import sys

# Adiciona o diretório pai ao path para permitir importações relativas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from interface_adapters.repositories import Repositories

class GetProspectsUseCase:
    def __init__(self, data_path="app/data/silver"):
        """
        Inicializa o caso de uso com o caminho para os dados.
        """
        self.repositories = Repositories(data_path)

    def get_prospects(self, vaga_codigo: str) -> pd.DataFrame:
        """
        Retorna um DataFrame do Pandas com os prospects para uma vaga específica,
        contendo apenas as colunas pré-definidas.

        Args:
            vaga_codigo: O código da vaga para a qual os prospects serão retornados.

        Returns:
            Um DataFrame do Pandas com os prospects filtrados.
        """
        # Carrega os DataFrames de vagas e prospects
        df_vagas = self.repositories.load_vagas()
        df_prospects = self.repositories.load_prospects()

        # Filtra para encontrar a vaga selecionada pelo código
        # Usar .get(0) com um default ou verificar se o dataframe não está vazio é mais seguro
        vaga_selecionada_series = df_vagas[df_vagas["codigo"] == vaga_codigo]
        if vaga_selecionada_series.empty:
            # Retorna um DataFrame vazio se a vaga não for encontrada
            return pd.DataFrame()
            
        vaga_selecionada = vaga_selecionada_series.iloc[0]

        # Filtra os prospects que aplicaram para a vaga selecionada
        df_prospects_vaga = df_prospects[df_prospects["vaga_codigo"] == vaga_selecionada["codigo"]].copy()

        # Define a lista de colunas que devem ser retornadas
        df_prospects_columns = [
            'vaga_codigo',
            'codigo',  # Codigo do aplicante
            'nome',
            'data_candidatura',
            'situacao_candidado'
        ]

        # Garante que todas as colunas existem no DataFrame antes de filtrar,
        # para evitar KeyErrors.
        cols_existentes = [col for col in df_prospects_columns if col in df_prospects_vaga.columns]
        
        # Filtra o DataFrame para conter apenas as colunas desejadas
        df_prospects_vaga_final = df_prospects_vaga[cols_existentes]

        # Retorna o DataFrame filtrado e com as colunas corretas
        return df_prospects_vaga_final

