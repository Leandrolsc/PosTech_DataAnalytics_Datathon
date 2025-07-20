import pandas as pd
import numpy as np
import pickle
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from imblearn.over_sampling import SMOTE
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping

class MatchPredictor:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_columns = None
        self.is_trained = False
    
    def train_model(self, df_path):
        df_final_total = pd.read_parquet(df_path)
        
        y = df_final_total['status_geral_codificado']
        colunas_para_remover = ['status_geral_codificado', 'id_vaga', 'codigo']
        X = df_final_total.drop(columns=colunas_para_remover)
        
        self.feature_columns = X.columns.tolist()
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        smote = SMOTE(random_state=42)
        X_train, y_train = smote.fit_resample(X_train, y_train)
        
        self.scaler = StandardScaler()
        X_train = self.scaler.fit_transform(X_train)
        X_test = self.scaler.transform(X_test)
        
        n_features = X_train.shape[1]
        
        self.model = Sequential()
        self.model.add(Dense(64, activation='relu', input_shape=(n_features,)))
        self.model.add(Dropout(0.4))
        self.model.add(Dense(32, activation='relu'))
        self.model.add(Dropout(0.2))
        self.model.add(Dense(16, activation='relu'))
        self.model.add(Dense(1, activation='sigmoid'))
        
        self.model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        
        callback_early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
        
        self.model.fit(
            X_train, 
            y_train, 
            epochs=100, 
            batch_size=32, 
            validation_data=(X_test, y_test),
            callbacks=[callback_early_stopping],
            verbose=1
        )
        
        probabilidades = self.model.predict(X_test)
        y_pred = (probabilidades > 0.5).astype(int)
        
        print("Relatório de Classificação:")
        print(classification_report(y_test, y_pred))
        
        self.is_trained = True
        
        return accuracy_score(y_test, y_pred)
    
    def save_model(self, model_path="app/model/match_model.h5", scaler_path="app/model/scaler.pkl", features_path="app/model/features.pkl"):
        if not self.is_trained:
            raise ValueError("Modelo não foi treinado ainda!")
        
        self.model.save(model_path)
        joblib.dump(self.scaler, scaler_path)
        joblib.dump(self.feature_columns, features_path)
        
        print(f"Modelo salvo em: {model_path}")
        print(f"Scaler salvo em: {scaler_path}")
        print(f"Features salvas em: {features_path}")
    
    def load_model(self, model_path="app/model/match_model.h5", scaler_path="app/model/scaler.pkl", features_path="app/model/features.pkl"):
        self.model = load_model(model_path)
        self.scaler = joblib.load(scaler_path)
        self.feature_columns = joblib.load(features_path)
        self.is_trained = True
        
        print("Modelo carregado com sucesso!")
    
    def predict_match(self, input_data):
        if not self.is_trained:
            raise ValueError("Modelo não foi treinado ou carregado!")
        
        if isinstance(input_data, dict):
            df_input = pd.DataFrame([input_data])
        elif isinstance(input_data, pd.DataFrame):
            df_input = input_data.copy()
        else:
            raise ValueError("input_data deve ser um dict ou DataFrame")
        
        for col in self.feature_columns:
            if col not in df_input.columns:
                df_input[col] = 0
        
        df_input = df_input[self.feature_columns]
        
        X_scaled = self.scaler.transform(df_input)
        
        probabilidades = self.model.predict(X_scaled)
        prob_match = 1 - probabilidades.flatten()
        
        return prob_match[0] if len(prob_match) == 1 else prob_match
    
    def predict_batch(self, input_data):
        if not self.is_trained:
            raise ValueError("Modelo não foi treinado ou carregado!")
        
        if isinstance(input_data, pd.DataFrame):
            df_input = input_data.copy()
        else:
            raise ValueError("input_data deve ser um DataFrame")
        
        for col in self.feature_columns:
            if col not in df_input.columns:
                df_input[col] = 0
        
        df_input = df_input[self.feature_columns]
        
        X_scaled = self.scaler.transform(df_input)
        
        probabilidades = self.model.predict(X_scaled)
        prob_match = 1 - probabilidades.flatten()
        
        return prob_match
    
    def create_ranking(self, df_candidates,parameters=False):
        probs = self.predict_batch(df_candidates)
        
        df_ranking = df_candidates.copy()
        df_ranking['probabilidade_match'] = probs
        df_ranking = df_ranking.sort_values('probabilidade_match', ascending=False)
        
        
        if parameters:
            return df_ranking
        else:
            colunas_para_exibir = ['codigo', 'id_vaga', 'probabilidade_match']
            df_ranking = df_ranking[colunas_para_exibir]

        return df_ranking


if __name__ == "__main__":
    # --- Etapa 1: Treinamento e Salvamento do Modelo ---
    
    # Instanciar o preditor
    predictor = MatchPredictor()
    
    # Definir o caminho para o dataset de treinamento
    # Certifique-se de que este arquivo .parquet exista no caminho especificado.
    data_path = "app/data/silver/df_features_train.parquet"
    
    # Treinar o modelo
    print("🚀 Iniciando o treinamento do modelo...")
    try:
        accuracy = predictor.train_model(df_path=data_path)
        print(f"\n✅ Treinamento concluído! Acurácia no conjunto de teste: {accuracy:.4f}")
        
        # Salvar o modelo treinado e os artefatos
        print("\n💾 Salvando o modelo, scaler e features...")
        predictor.save_model(
            model_path="app/model_teste/match_model.h5",
            scaler_path="app/model_teste/scaler.pkl",
            features_path="app/model_teste/features.pkl"
        )
    except FileNotFoundError:
        print(f"❌ Erro: Arquivo de dados não encontrado em '{data_path}'.")
        print("Por favor, verifique o caminho e execute o script novamente.")
        exit() # Encerra o script se o arquivo de dados não for encontrado

