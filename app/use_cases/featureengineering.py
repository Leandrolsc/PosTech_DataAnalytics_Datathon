import pandas as pd
import numpy as np
import re
import os
import sys
from typing import Set, Optional, Dict, List
import nltk
from nltk.corpus import stopwords

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from use_cases.pipeline import Pipeline

class CandidateFeatureEngineer:
    """
    Classe para realizar feature engineering em dados de candidatos e vagas.
    
    Esta classe processa dados de candidatos (applicants), prospects e vagas,
    criando features para modelos de machine learning de matching.
    """
    
    def __init__(self):
        """Inicializa a classe com configurações padrão."""
        self.stopwords_pt = self._load_stopwords()
        self.vagas_cache = {}
        self.mapa_niveis_idioma = {
            'Nenhum': 0,
            '': 0,
            np.nan: 0,
            'Básico': 1,
            'Intermediário': 2,
            'Técnico': 2,
            'Avançado': 3,
            'Fluente': 4
        }
        self.mapa_academico = {
            # Nível 0 - Nulos e Vazios
            np.nan: 0,
            '': 0,
            
            # Nível 1 a 3 - Fundamental
            'Ensino Fundamental Incompleto': 1,
            'Ensino Fundamental Cursando': 2,
            'Ensino Fundamental Completo': 3,

            # Nível 4 a 6 - Médio
            'Ensino Médio Incompleto': 4,
            'Ensino Médio Cursando': 5,
            'Ensino Médio Completo': 6,

            # Nível 7 a 9 - Técnico
            'Ensino Técnico Incompleto': 7,
            'Ensino Técnico Cursando': 8,
            'Ensino Técnico Completo': 9,

            # Nível 10 a 12 - Superior
            'Ensino Superior Incompleto': 10,
            'Ensino Superior Cursando': 11,
            'Ensino Superior Completo': 12,

            # Nível 13 a 15 - Pós-Graduação
            'Pós Graduação Incompleto': 13,
            'Pós Graduação Cursando': 14,
            'Pós Graduação Completo': 15,

            # Nível 16 a 18 - Mestrado
            'Mestrado Incompleto': 16,
            'Mestrado Cursando': 17,
            'Mestrado Completo': 18,

            # Nível 19 a 21 - Doutorado
            'Doutorado Incompleto': 19,
            'Doutorado Cursando': 20,
            'Doutorado Completo': 21
        }
        
        self.mapeamento_status = {
            # Categoria Sucesso
            'Aprovado': 'Sucesso',
            'Contratado como Hunting': 'Sucesso',
            'Contratado pela Decision': 'Sucesso',
            'Documentação Cooperado': 'Sucesso',
            'Documentação CLT': 'Sucesso',
            'Documentação PJ': 'Sucesso',
            'Proposta Aceita': 'Sucesso',

            # Categoria Insucesso
            'Não Aprovado pelo RH': 'Insucesso',
            'Não Aprovado pelo Cliente': 'Insucesso',
            'Não Aprovado pelo Requisitante': 'Insucesso',
            'Recusado': 'Insucesso',
            'Desistiu da Contratação': 'Insucesso', 
            'Desistiu': 'Insucesso',              
            'Sem interesse nesta vaga': 'Insucesso',

            # Categoria Andamento
            'Encaminhado ao Requisitante': 'Andamento',
            'Inscrito': 'Andamento',
            'Prospect': 'Andamento',
            'Entrevista Técnica': 'Andamento',
            'Em avaliação pelo RH': 'Andamento',
            'Entrevista com Cliente': 'Andamento',
            'Encaminhar Proposta': 'Andamento'
        }
        
        self.colunas_modelo = [
            'id_vaga',
            'dict_prospect_codigo',
            'compatibilidade_vaga_cv_palavras',
            'compatibilidade_vaga_cv_percentual',
            'match_academico',
            'match_ingles',
            'match_espanhol',
            'match_areas_contagem', 
            'match_areas_percentual',
            'informacoes_basicas.tipo_contratacao_codificada',
            'informacoes_basicas_prazo_contratacao_codificada',
            'informacoes_basicas_prioridade_vaga_codificada',
            'informacoes_basicas_origem_vaga_codificada',
            'perfil_vaga_estado_codificada',
            'perfil_vaga_nivel profissional_codificado',
            'perfil_vaga_nivel_ingles_codificado',
            'perfil_vaga_nivel_espanhol_codificado',
            'perfil_vaga_viagens_requeridas_codificado',
            'formacao_e_idiomas_nivel_academico_codificado',
            'formacao_e_idiomas_nivel_ingles_codificado',
            'formacao_e_idiomas_nivel_espanhol_codificado',
            'status_geral_codificado'
        ]
    
    def _load_stopwords(self) -> Set[str]:
        """Carrega stopwords em português."""
        try:
            return set(stopwords.words('portuguese'))
        except LookupError:
            print("Baixando recurso 'stopwords' do NLTK...")
            nltk.download('stopwords')
            return set(stopwords.words('portuguese'))
    
    def _clean_and_remove_stopwords(self, text: Optional[str]) -> str:
        """
        Limpa o texto, removendo pontuações e stopwords.
        
        Args:
            text: Texto a ser limpo
            
        Returns:
            Texto limpo sem stopwords
        """
        if not isinstance(text, str) or not text:
            return ""
        
        text_cleaned = re.sub(r'[^\w\s]', '', text)
        words = text_cleaned.lower().split()
        filtered_words = [word for word in words if word not in self.stopwords_pt]
        
        return " ".join(filtered_words)
    
    def _get_vaga_text(self, df_vagas: pd.DataFrame, vaga_codigo: str) -> Optional[str]:
        """
        Busca, concatena e limpa os textos de uma vaga específica.
        
        Args:
            df_vagas: DataFrame com informações das vagas
            vaga_codigo: Código da vaga
            
        Returns:
            Texto limpo da vaga ou None se não encontrada
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
    
    def _calcular_compatibilidade(self, cv_text: str, palavras_vaga: Set[str], 
                                 caracteres_totais_vaga: int) -> pd.Series:
        """
        Calcula a compatibilidade entre CV e vaga.
        
        Args:
            cv_text: Texto do CV
            palavras_vaga: Set de palavras da vaga
            caracteres_totais_vaga: Total de caracteres da vaga
            
        Returns:
            Series com contagem de palavras em comum e percentual
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
            
        return pd.Series([contagem_palavras_comuns, round(percentual, 2)], 
                        index=['palavras_em_comum', 'percentual_compatibilidade'])
    
    def _normalize_json_columns(self, df: pd.DataFrame, json_columns: List[str]) -> pd.DataFrame:
        """
        Normaliza colunas que contêm dados JSON.
        
        Args:
            df: DataFrame com colunas JSON
            json_columns: Lista de colunas para normalizar
            
        Returns:
            DataFrame normalizado
        """
        dfs_normalizados = []
        
        for col in json_columns:
            if col in df.columns:
                df_temp = pd.json_normalize(df[col])
                df_temp.columns = [f"{col}_{subcol}" for subcol in df_temp.columns]
                dfs_normalizados.append(df_temp)
        
        return pd.concat([df.drop(columns=json_columns)] + dfs_normalizados, axis=1)
    
    def _limpar_e_padronizar_separadores(self, texto: str) -> str:
        """
        Limpa e padroniza separadores em texto.
        
        Args:
            texto: Texto a ser limpo
            
        Returns:
            Texto com separadores padronizados
        """
        if pd.isna(texto):
            return ""
        
        texto_str = str(texto)
        texto_limpo = re.sub(r'-$', '', texto_str.strip())
        texto_limpo = re.sub(r'(\S)-(\S)', r'\1, \2', texto_limpo)
        
        return texto_limpo
    
    def _calcular_match_profissional(self, row: pd.Series) -> pd.Series:
        """
        Calcula match entre áreas profissionais da vaga e candidato.
        
        Args:
            row: Linha do DataFrame
            
        Returns:
            Series com contagem e percentual de match
        """
        str_vaga = row['areas_atuacao_limpas']
        str_candidato = row['informacoes_profissionais.area_atuacao']

        if pd.isna(str_vaga):
            str_vaga = ''
        if pd.isna(str_candidato):
            str_candidato = ''

        set_vaga = set(item.strip() for item in str_vaga.split(',') if item.strip())
        set_candidato = set(item.strip() for item in str_candidato.split(',') if item.strip())

        if not set_vaga:
            return pd.Series([0, 1.0], index=['match_areas_contagem', 'match_areas_percentual'])

        competencias_em_comum = set_vaga.intersection(set_candidato)
        
        match_contagem = len(competencias_em_comum)
        match_percentual = match_contagem / len(set_vaga)
        
        return pd.Series([match_contagem, match_percentual], 
                        index=['match_areas_contagem', 'match_areas_percentual'])
    
    def load_data(self) -> tuple:
        """
        Carrega os dados dos arquivos JSON.
        
        Args:
            applicants_path: Caminho para o arquivo de candidatos
            prospects_path: Caminho para o arquivo de prospects
            vagas_path: Caminho para o arquivo de vagas
            
        Returns:
            Tupla com os três DataFrames
        """
        df_applicants, df_prospects, df_vagas = Pipeline.silver_feature()
        
        return df_applicants, df_prospects, df_vagas
    

    def merge_dataframes(self, df_prospects: pd.DataFrame, df_vagas: pd.DataFrame, 
                        df_applicants: pd.DataFrame) -> pd.DataFrame:
        """
        Junta os três DataFrames em um único.
        
        Args:
            df_prospects: DataFrame de prospects processado
            df_vagas: DataFrame de vagas processado
            df_applicants: DataFrame de candidatos processado
            
        Returns:
            DataFrame unificado
        """
        # Renomeia para fazer o merge
        df_vagas_renamed = df_vagas.rename(columns={'codigo': 'id_vaga'})
        
        # Primeiro merge: prospects + vagas
        df_merged = pd.merge(df_prospects, 
                             df_vagas_renamed, 
                             left_on='vaga_codigo',
                             right_on='id_vaga', 
                             how='left'
                             )
        
        # Segundo merge: resultado + candidatos
        df_final = pd.merge(
            df_merged, 
            df_applicants,
            left_on='codigo',
            right_on='codigo',
            how='left'
        )
        
        return df_final
    
    def create_compatibility_features(self, df: pd.DataFrame, df_vagas_original: pd.DataFrame) -> pd.DataFrame:
        """
        Cria features de compatibilidade entre CV e vaga.
        
        Args:
            df: DataFrame principal
            df_vagas_original: DataFrame original das vagas
            
        Returns:
            DataFrame com features de compatibilidade
        """
        print("Pré-processando descrições das vagas...")
        
        # Garante que a coluna 'codigo' existe
        if 'codigo' not in df_vagas_original.columns:
            df_vagas_original.reset_index(inplace=True)
            df_vagas_original.rename(columns={'index': 'codigo'}, inplace=True)
        
        # Cria cache das vagas
        for vaga_id in df['id_vaga'].unique():
            texto_vaga_limpo = self._get_vaga_text(df_vagas_original, vaga_id)
            if texto_vaga_limpo:
                palavras_vaga = set(texto_vaga_limpo.split())
                caracteres_totais_vaga = len(texto_vaga_limpo)
                self.vagas_cache[vaga_id] = {
                    'palavras_vaga': palavras_vaga,
                    'caracteres_totais_vaga': caracteres_totais_vaga
                }
        
        # Função para aplicar a cada linha
        def calcular_compatibilidade_por_linha(row):
            vaga_id = row['id_vaga']
            cv_text = row['cv_pt']
            
            info_vaga = self.vagas_cache.get(vaga_id)
            
            if not info_vaga or not cv_text:
                return pd.Series([0, 0.0], index=['compatibilidade_vaga_cv_palavras', 
                                                 'compatibilidade_vaga_cv_percentual'])
            
            resultado = self._calcular_compatibilidade(
                cv_text, 
                info_vaga['palavras_vaga'], 
                info_vaga['caracteres_totais_vaga']
            )
            resultado.index = ['compatibilidade_vaga_cv_palavras', 'compatibilidade_vaga_cv_percentual']
            return resultado
        
        print("Calculando compatibilidade entre CV e Vaga...")
        compatibilidade_df = df.apply(calcular_compatibilidade_por_linha, axis=1)
        
        return pd.concat([df, compatibilidade_df], axis=1)
    
    def create_language_matches(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cria features de match de idiomas (inglês e espanhol).
        
        Args:
            df: DataFrame principal
            
        Returns:
            DataFrame com features de match de idiomas
        """
        # Match inglês
        nivel_candidato_ingles = df['formacao_e_idiomas.nivel_ingles'].map(self.mapa_niveis_idioma).fillna(0)
        nivel_vaga_ingles = df['perfil_vaga.nivel_ingles'].map(self.mapa_niveis_idioma).fillna(0)
        df['match_ingles'] = (nivel_candidato_ingles >= nivel_vaga_ingles).astype(int)
        
        # Match espanhol
        nivel_candidato_espanhol = df['formacao_e_idiomas.nivel_espanhol'].map(self.mapa_niveis_idioma).fillna(0)
        nivel_vaga_espanhol = df['perfil_vaga.nivel_espanhol'].map(self.mapa_niveis_idioma).fillna(0)
        df['match_espanhol'] = (nivel_candidato_espanhol >= nivel_vaga_espanhol).astype(int)
        
        return df
    
    def create_academic_match(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cria feature de match acadêmico.
        
        Args:
            df: DataFrame principal
            
        Returns:
            DataFrame com feature de match acadêmico
        """
        nivel_candidato = df['formacao_e_idiomas.nivel_academico'].map(self.mapa_academico).fillna(0)
        nivel_vaga = df['perfil_vaga.nivel_academico'].map(self.mapa_academico).fillna(0)
        df['match_academico'] = (nivel_candidato >= nivel_vaga).astype(int)
        
        return df
    
    def create_categorical_encodings(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cria encodings categóricos para variáveis relevantes.
        
        Args:
            df: DataFrame principal
            
        Returns:
            DataFrame com encodings categóricos
        """
        # Lista de colunas para fazer label encoding
        colunas_para_encoding = [
            'informacoes_basicas.tipo_contratacao',
            'informacoes_basicas.prazo_contratacao',
            'informacoes_basicas.prioridade_vaga',
            'informacoes_basicas.origem_vaga',
            'perfil_vaga.estado',
            'perfil_vaga.nivel profissional',
            'perfil_vaga.nivel_academico',
            'perfil_vaga.nivel_ingles',
            'perfil_vaga.nivel_espanhol',
            'perfil_vaga.viagens_requeridas',
            'formacao_e_idiomas.nivel_academico',
            'formacao_e_idiomas.nivel_ingles',
            'formacao_e_idiomas.nivel_espanhol'
        ]
        
        # Trata coluna de tipo contratação
        df['informacoes_basicas.tipo_contratacao'] = df['informacoes_basicas.tipo_contratacao'].fillna('').astype(str)
        df['informacoes_basicas.tipo_contratacao'] = df['informacoes_basicas.tipo_contratacao'].str.replace(', ', ',')
        df['informacoes_basicas.tipo_contratacao'] = df['informacoes_basicas.tipo_contratacao'].str.strip()
        
        # Aplica label encoding
        for col in colunas_para_encoding:
            if col in df.columns:
                df[f'{col}_codificada'] = pd.factorize(df[col])[0]
        
        return df
    
    def create_area_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cria features de áreas de atuação com one-hot encoding e matches.
        
        Args:
            df: DataFrame principal
            
        Returns:
            DataFrame com features de áreas
        """
        # Limpa áreas da vaga
        df['areas_atuacao_limpas'] = df['perfil_vaga.areas_atuacao'].apply(
            self._limpar_e_padronizar_separadores
        )
        
        # One-hot encoding para áreas da vaga
        df_areas_vaga = df['areas_atuacao_limpas'].str.get_dummies(sep=', ')
        df_areas_vaga = df_areas_vaga.add_prefix('perfil_vaga.areas_atuacao_')
        
        # One-hot encoding para áreas do candidato
        df_areas_candidato = df['informacoes_profissionais.area_atuacao'].str.get_dummies(sep=', ')
        df_areas_candidato = df_areas_candidato.add_prefix('informacoes_profissionais.area_atuacao_')
        
        # Junta as features
        df = pd.concat([df, df_areas_vaga, df_areas_candidato], axis=1)
        
        # Calcula matches profissionais
        match_features = df.apply(self._calcular_match_profissional, axis=1)
        df = pd.concat([df, match_features], axis=1)
        
        return df
    
    def create_status_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cria features de status e filtra dados para o modelo.
        
        Args:
            df: DataFrame principal
            
        Returns:
            DataFrame filtrado com features de status
        """
        # Mapeia status
        df['status_geral'] = df['situacao_candidado'].map(self.mapeamento_status)
        
        # Remove linhas com status 'Andamento' e NaN
        df = df.dropna(subset=['status_geral'])
        #df = df[df['status_geral'] != 'Andamento']
        
        # Label encoding do status
        df['status_geral_codificado'] = pd.factorize(df['status_geral'])[0]
        
        return df
    
    def prepare_model_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepara dados finais para o modelo.
        
        Args:
            df: DataFrame processado
            
        Returns:
            DataFrame final para o modelo
        """
        # Encontra colunas que existem no DataFrame
        colunas_existentes = [col for col in self.colunas_modelo if col in df.columns]
        
        # Adiciona colunas de áreas que foram criadas dinamicamente
        colunas_areas = [col for col in df.columns if 
                        col.startswith('perfil_vaga.areas_atuacao_') or 
                        col.startswith('informacoes_profissionais.area_atuacao_')]
        
        colunas_finais = colunas_existentes + colunas_areas + ['codigo']
        
        # Filtra DataFrame
        df_modelo = df[colunas_finais]
        
        # Preenche NaNs
        df_modelo = df_modelo.fillna(0)
        
        return df_modelo
    
    def process_all(self, output_path: str = "app/data/silver/df_ML_tunado.parquet") -> pd.DataFrame:
        """
        Executa todo o pipeline de processamento.
        
        Args:
            applicants_path: Caminho para arquivo de candidatos
            prospects_path: Caminho para arquivo de prospects
            vagas_path: Caminho para arquivo de vagas
            output_path: Caminho para salvar o resultado
            
        Returns:
            DataFrame final processado
        """
        print("Carregando dados...")
        df_applicants, df_prospects, df_vagas = self.load_data()     
        
        print("Juntando DataFrames...")
        df_merged = self.merge_dataframes(
            df_prospects, df_vagas, df_applicants
        )
        
        print("Criando features de compatibilidade...")
        df_merged = self.create_compatibility_features(df_merged, df_vagas)
        
        print("Criando features de match de idiomas...")
        df_merged = self.create_language_matches(df_merged)
        
        print("Criando features de match acadêmico...")
        df_merged = self.create_academic_match(df_merged)
        
        print("Criando encodings categóricos...")
        df_merged = self.create_categorical_encodings(df_merged)
        
        print("Criando features de áreas...")
        df_merged = self.create_area_features(df_merged)
        
        print("Criando features de status...")
        df_merged = self.create_status_features(df_merged)
        
        print("Preparando dados para o modelo...")
        df_final = self.prepare_model_data(df_merged)
        
        print(f"Salvando resultado em {output_path}...")
        df_final.to_parquet(output_path, index=False, compression='gzip')
        
        print(f"Processamento concluído!")
        print(f"DataFrame final contém {df_final.shape[0]} linhas e {df_final.shape[1]} colunas.")
        
        return df_final


if __name__ == "__main__":
    # Inicializa o processador
    processor = CandidateFeatureEngineer()
    
    # Executa o pipeline completo
    df_final = processor.process_all(
        output_path="app/data/silver/df_features.parquet"
    )
    
    print("Features criadas:")
    print(df_final.columns.tolist())