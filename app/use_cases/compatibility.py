import pandas as pd
import os
import sys
from typing import Set, Optional
import re
import nltk
from nltk.corpus import stopwords

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from interface_adapters.repositories import Repositories

class CompatibilityUseCase:
    """
    Use case para calcular a compatibilidade entre candidatos e vagas,
    removendo stopwords para uma análise mais precisa usando a biblioteca NLTK.
    """
    
    try:
        STOPWORDS_PT = set(stopwords.words('portuguese'))
    except LookupError:
        print("Baixando recurso 'stopwords' do NLTK...")
        nltk.download('stopwords')
        STOPWORDS_PT = set(stopwords.words('portuguese'))
    # ----------------------------------------------

    def __init__(self):
        """
        Inicializa o caso de uso, preparando o acesso aos repositórios de dados.
        """
        self.repositories = Repositories()

    def _clean_and_remove_stopwords(self, text: Optional[str]) -> str:
        """
        Limpa o texto, removendo pontuações e stopwords.
        Método privado.
        """
        if not isinstance(text, str) or not text:
            return ""
        
        text_cleaned = re.sub(r'[^\w\s]', '', text)
        
        words = text_cleaned.lower().split()
        
        filtered_words = [word for word in words if word not in self.STOPWORDS_PT]
        
        return " ".join(filtered_words)

    def _get_vaga_text(self, df_vagas: pd.DataFrame, vaga_codigo: str) -> Optional[str]:
        """
        Busca, concatena e limpa os textos de uma vaga específica a partir de seu código.
        Método privado.
        """
        vaga_data = df_vagas[df_vagas['codigo'] == vaga_codigo]
        if vaga_data.empty:
            return None
        
        vagas_columns = [
            'perfil_vaga.demais_observacoes', 
            'informacoes_basicas.titulo_vaga',
            'perfil_vaga.principais_atividades', 
            'perfil_vaga.competencia_tecnicas_e_comportamentais'
        ]
        
        vagas_columns_existentes = [col for col in vagas_columns if col in vaga_data.columns]
        descricao_vaga = ' '.join(vaga_data.iloc[0][vagas_columns_existentes].dropna().astype(str))
        
        return self._clean_and_remove_stopwords(descricao_vaga)

    def _calcular_compatibilidade(self, cv_text: str, palavras_vaga: Set[str], caracteres_totais_vaga: int) -> pd.Series:
        """
        Calcula a compatibilidade com base na interseção de palavras e na proporção de caracteres.
        Método privado.
        """

        cv_limpo = self._clean_and_remove_stopwords(cv_text)
        if not cv_limpo:
            return pd.Series([0, 0.0], index=['palavras_em_comum', 'percentual_compatibilidade'])

        palavras_cv = set(cv_limpo.split())
        palavras_comuns = palavras_cv.intersection(palavras_vaga)
        
        contagem_palavras_comuns = len(palavras_comuns)
        caracteres_palavras_comuns = sum(len(palavra) for palavra in palavras_comuns)
        
        percentual = 0.0
        if caracteres_totais_vaga > 0:
            percentual = (caracteres_palavras_comuns / caracteres_totais_vaga) * 100
            
        return pd.Series([contagem_palavras_comuns, round(percentual, 2)], index=['palavras_em_comum', 'percentual_compatibilidade'])

    def get_compatibility_for_vaga(self, vaga_codigo: str) -> pd.DataFrame:
        """
        Retorna o ranking de compatibilidade dos candidatos para uma vaga específica.
        """
        if not vaga_codigo:
            raise ValueError("O código da vaga (vaga_codigo) não pode ser nulo ou vazio.")

        df_vagas = self.repositories.load_vagas()
        df_prospects = self.repositories.load_prospects()
        df_applicants = self.repositories.load_applicants()
        
        descricao_vaga_completa = self._get_vaga_text(df_vagas, vaga_codigo)
        if not descricao_vaga_completa:
            print(f"Aviso: Vaga com código '{vaga_codigo}' não encontrada ou sem texto relevante.")
            return pd.DataFrame()

        palavras_vaga_set = set(descricao_vaga_completa.split())
        caracteres_vaga_total = sum(len(p) for p in palavras_vaga_set)

        df_prospects_vaga = df_prospects[df_prospects['vaga_codigo'] == vaga_codigo]

        df_merged = pd.merge(
            df_prospects_vaga,
            df_applicants[['codigo', 'cv_pt']],
            on='codigo',
            how='inner'
        )

        if df_merged.empty:
            print(f"Aviso: Nenhum candidato encontrado para a vaga '{vaga_codigo}'.")
            return pd.DataFrame()

        df_merged[['palavras_em_comum', 'percentual_compatibilidade']] = df_merged['cv_pt'].apply(
            lambda cv: self._calcular_compatibilidade(cv, palavras_vaga_set, caracteres_vaga_total)
        )

        final_columns = [
            'nome', 
            'data_candidatura', 
            'situacao_candidado', 
            'palavras_em_comum', 
            'percentual_compatibilidade'
        ]
        
        existing_final_columns = [col for col in final_columns if col in df_merged.columns]
        df_final = df_merged[existing_final_columns]
        
        return df_final.sort_values(by='percentual_compatibilidade', ascending=False).reset_index(drop=True)

    def get_compatibilities_for_applicant(self, applicant_code: str) -> pd.DataFrame:
        """
        Para um dado aplicante, retorna a compatibilidade com todas as vagas em que ele se inscreveu.
        """
        if not applicant_code:
            raise ValueError("O código do aplicante (applicant_code) não pode ser nulo ou vazio.")

        df_vagas = self.repositories.load_vagas()
        df_prospects = self.repositories.load_prospects()
        df_applicants = self.repositories.load_applicants()

        applicant_data = df_applicants[df_applicants['codigo'] == applicant_code]
        if applicant_data.empty:
            print(f"Aviso: Aplicante com código '{applicant_code}' não encontrado.")
            return pd.DataFrame()
        cv_text = applicant_data.iloc[0]['cv_pt']

        applicant_prospects = df_prospects[df_prospects['codigo'] == applicant_code]
        if applicant_prospects.empty:
            print(f"Aviso: Nenhuma candidatura encontrada para o aplicante '{applicant_code}'.")
            return pd.DataFrame()
        
        vagas_aplicadas_codigos = applicant_prospects['vaga_codigo'].unique()

        results_list = []
        for vaga_codigo in vagas_aplicadas_codigos:
            descricao_vaga = self._get_vaga_text(df_vagas, vaga_codigo)
            
            if descricao_vaga:
                palavras_vaga_set = set(descricao_vaga.split())
                caracteres_vaga_total = sum(len(p) for p in palavras_vaga_set)
                
                compat_series = self._calcular_compatibilidade(cv_text, palavras_vaga_set, caracteres_vaga_total)
                
                vaga_info = df_vagas[df_vagas['codigo'] == vaga_codigo].iloc[0]
                prospect_info = applicant_prospects[applicant_prospects['vaga_codigo'] == vaga_codigo].iloc[0]

                results_list.append({
                    'titulo_vaga': vaga_info.get('informacoes_basicas.titulo_vaga', 'N/A'),
                    'data_candidatura': prospect_info.get('data_candidatura', 'N/A'),
                    'situacao_candidado': prospect_info.get('situacao_candidado', 'N/A'),
                    'palavras_em_comum': compat_series['palavras_em_comum'],
                    'percentual_compatibilidade': compat_series['percentual_compatibilidade']
                })

        if not results_list:
            return pd.DataFrame()

        df_final = pd.DataFrame(results_list)
        return df_final.sort_values(by='percentual_compatibilidade', ascending=False).reset_index(drop=True)
