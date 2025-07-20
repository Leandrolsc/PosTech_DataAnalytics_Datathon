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
import shap
import os


class MatchPredictor:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_columns = None
        self.background_data = {}  # Dados gerados durante treinamento/inferência
        self.is_trained = False
    
    def _initialize_background_data(self):
        """Inicializa estrutura do background_data"""
        self.background_data = {
            'training_stats': {},
            'feature_importance': {}, # Preenchido pelo SHAP
            'model_performance': {},
            'prediction_history': [],
            'data_distribution': {},
            'validation_metrics': {},
            'model_architecture': {},
            'preprocessing_stats': {},
            'shap_background_sample': None # <--- NOVO: Chave para a amostra do SHAP
        }
    
    def _capture_training_background(self, X_train, X_test, y_train, y_test):
        """Captura informações de background durante o treinamento"""
        self.background_data['training_stats'] = {
            'n_samples_train': len(X_train),
            'n_samples_test': len(X_test),
            'n_features': X_train.shape[1],
            'class_distribution_train': np.bincount(y_train).tolist(),
            'class_distribution_test': np.bincount(y_test).tolist(),
            'feature_means': np.mean(X_train, axis=0).tolist(),
            'feature_stds': np.std(X_train, axis=0).tolist()
        }
        self.background_data['data_distribution'] = {
            'train_mean': float(np.mean(X_train)),
            'train_std': float(np.std(X_train)),
            'test_mean': float(np.mean(X_test)),
            'test_std': float(np.std(X_test))
        }
    
    def _capture_model_architecture(self):
        """Captura informações da arquitetura do modelo"""
        if self.model:
            self.background_data['model_architecture'] = {
                'total_params': self.model.count_params(),
                'layers': len(self.model.layers),
                'optimizer': self.model.optimizer.get_config(),
                'loss': self.model.loss,
                'metrics': self.model.metrics_names if hasattr(self.model, 'metrics_names') else []
            }
    
    def _capture_preprocessing_stats(self, original_data):
        """Captura estatísticas do pré-processamento"""
        if self.scaler:
            self.background_data['preprocessing_stats'] = {
                'scaler_mean': self.scaler.mean_.tolist() if hasattr(self.scaler, 'mean_') else None,
                'scaler_scale': self.scaler.scale_.tolist() if hasattr(self.scaler, 'scale_') else None,
                'original_data_shape': original_data.shape,
                'feature_columns': self.feature_columns
            }
    
    def _update_prediction_history(self, input_data, prediction, probability=None):
        """
        Atualiza histórico de predições, tratando diferentes tipos de entrada.
        """

        if 'prediction_history' not in self.background_data:
            self.background_data['prediction_history'] = []

        if isinstance(prediction, np.ndarray):
            processed_prediction = prediction.tolist()
        elif np.isscalar(prediction):
            processed_prediction = float(prediction)
        else: 
            processed_prediction = prediction
            
        prediction_entry = {
            'timestamp': pd.Timestamp.now(),
            'input_shape': input_data.shape if hasattr(input_data, 'shape') else len(input_data),
            'prediction': processed_prediction,
            'probability': float(probability) if probability is not None and np.isscalar(probability) else None
        }
        
        self.background_data['prediction_history'].append(prediction_entry)
        if len(self.background_data['prediction_history']) > 100:
            self.background_data['prediction_history'].pop(0)
    
    def train_model(self, df_path):
        self._initialize_background_data()
        
        df_final_total = pd.read_parquet(df_path)
        
        y = df_final_total['status_geral_codificado']
        colunas_para_remover = ['status_geral_codificado', 'id_vaga', 'codigo']
        X = df_final_total.drop(columns=colunas_para_remover)
        
        self.feature_columns = X.columns.tolist()
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        smote = SMOTE(random_state=42)
        X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)
        
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train_resampled)
        X_test_scaled = self.scaler.transform(X_test)
        
        self.background_data['shap_background_sample'] = shap.sample(X_train_scaled, 100)
        
        self._capture_preprocessing_stats(df_final_total)
        self._capture_training_background(X_train_scaled, X_test_scaled, y_train_resampled, y_test)
        
        n_features = X_train_scaled.shape[1]
        
        self.model = Sequential([
            Dense(64, activation='relu', input_shape=(n_features,)),
            Dropout(0.4),
            Dense(32, activation='relu'),
            Dropout(0.2),
            Dense(16, activation='relu'),
            Dense(1, activation='sigmoid')
        ])
        
        self.model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        
        self._capture_model_architecture()
        
        callback_early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
        
        history = self.model.fit(
            X_train_scaled, y_train_resampled, 
            epochs=100, batch_size=32, 
            validation_data=(X_test_scaled, y_test),
            callbacks=[callback_early_stopping],
            verbose=1
        )
        
        self.background_data['validation_metrics'] = {
            'final_train_loss': float(history.history['loss'][-1]),
            'final_val_loss': float(history.history['val_loss'][-1]),
            'final_train_accuracy': float(history.history['accuracy'][-1]),
            'final_val_accuracy': float(history.history['val_accuracy'][-1]),
            'epochs_trained': len(history.history['loss']),
            'training_history': {k: [float(x) for x in v] for k, v in history.history.items()}
        }
        
        probabilidades = self.model.predict(X_test_scaled)
        y_pred = (probabilidades > 0.5).astype(int)
        accuracy = accuracy_score(y_test, y_pred)
        
        self.background_data['model_performance'] = {
            'test_accuracy': float(accuracy),
            'test_predictions': y_pred.flatten().tolist(),
            'test_probabilities': probabilidades.flatten().tolist(),
            'classification_report': classification_report(y_test, y_pred, output_dict=True)
        }
        
        print("Relatório de Classificação:")
        print(classification_report(y_test, y_pred))
        
        self.is_trained = True
        return accuracy
    
    # ... (save_model, load_model, e outros métodos permanecem os mesmos, pois já salvam/carregam o dicionário inteiro) ...
    def save_model(self, model_path="app/model/match_model.h5", scaler_path="app/model/scaler.pkl", 
                   features_path="app/model/features.pkl", background_path="app/model/background_data.pkl"):
        if not self.is_trained:
            raise ValueError("Modelo não foi treinado ainda!")
        
        # Garante que os diretórios existem
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        self.model.save(model_path)
        joblib.dump(self.scaler, scaler_path)
        joblib.dump(self.feature_columns, features_path)
        joblib.dump(self.background_data, background_path)
        
        print(f"Modelo salvo em: {model_path}")
        print(f"Scaler salvo em: {scaler_path}")
        print(f"Features salvas em: {features_path}")
        print(f"Background data salvo em: {background_path}")

    def load_model(self, model_path="app/model/match_model.h5", scaler_path="app/model/scaler.pkl", 
                   features_path="app/model/features.pkl", background_path="app/model/background_data.pkl"):
        self.model = load_model(model_path)
        self.scaler = joblib.load(scaler_path)
        self.feature_columns = joblib.load(features_path)
        
        try:
            self.background_data = joblib.load(background_path)
            print("Background data carregado com sucesso!")
        except FileNotFoundError:
            print("⚠️ Arquivo de background data não encontrado. Inicializando estrutura vazia.")
            self._initialize_background_data()
        
        self.is_trained = True
        print("Modelo carregado com sucesso!")

    def explain_batch_with_shap(self, df_candidates, top_n=3):
        """
        Gera explicações SHAP para um lote de candidatos usando GradientExplainer.

        Parâmetros:
        -----------
        df_candidates : pd.DataFrame
            DataFrame com os dados dos candidatos a serem explicados.
        
        top_n : int
            Número de features a serem retornadas para os melhores (positivos) e piores (negativos) 
            contribuidores. Ex: top_n=3 retorna até 3 positivos e 3 negativos.

        Retorno:
        --------
        df_explanations : pd.DataFrame
            DataFrame com as explicações, contendo as features mais importantes
            para cada candidato, seus valores SHAP e valores originais.
        """
        if not self.is_trained:
            raise ValueError("Modelo não foi treinado ou carregado!")
        
        shap_background_sample = self.background_data.get('shap_background_sample')
        if shap_background_sample is None:
            raise ValueError("Amostra de background para SHAP não encontrada. O modelo foi treinado corretamente?")

        df_input = df_candidates.copy()
        for col in self.feature_columns:
            if col not in df_input.columns:
                df_input[col] = 0
        df_input = df_input[self.feature_columns]

        X_scaled = self.scaler.transform(df_input)

        explainer = shap.GradientExplainer(self.model, shap_background_sample)
        shap_values = explainer.shap_values(X_scaled)

        if isinstance(shap_values, list):
            shap_values = shap_values[0]

        explanations = []
        for idx in range(len(df_input)):
            shap_row = shap_values[idx].flatten()
            shap_series = pd.Series(shap_row, index=self.feature_columns)
            
            top_positive = shap_series[shap_series > 0].sort_values(ascending=False).head(top_n)
            
            top_negative = shap_series[shap_series < 0].sort_values(ascending=True).head(top_n)

            combined_series = pd.concat([top_positive, top_negative])

            for feature, shap_val in combined_series.items():
                explanations.append({
                    'codigo': df_candidates.iloc[idx].get('codigo', f'instancia_{idx}'),
                    'feature': feature,
                    'shap_value': shap_val,
                    'valor_original': df_input.loc[df_input.index[idx], feature]
                })

        df_explanations = pd.DataFrame(explanations)
        
        squeezed_shap_values = np.squeeze(shap_values)

        if squeezed_shap_values.ndim == 1:
            data_for_df = squeezed_shap_values.reshape(1, -1)
        else:
            data_for_df = squeezed_shap_values

        self.background_data['feature_importance'] = pd.DataFrame(
            data_for_df, columns=self.feature_columns
        ).abs().mean().sort_values(ascending=False).to_dict()

        return df_explanations

    def predict_match(self, input_data):
        if not self.is_trained: raise ValueError("Modelo não foi treinado ou carregado!")
        if isinstance(input_data, dict): df_input = pd.DataFrame([input_data])
        elif isinstance(input_data, pd.DataFrame): df_input = input_data.copy()
        else: raise ValueError("input_data deve ser um dict ou DataFrame")
        for col in self.feature_columns:
            if col not in df_input.columns: df_input[col] = 0
        df_input = df_input[self.feature_columns]
        X_scaled = self.scaler.transform(df_input)
        probabilidades = self.model.predict(X_scaled)
        prob_match = 1 - probabilidades.flatten()
        result = prob_match[0] if len(prob_match) == 1 else prob_match
        self._update_prediction_history(df_input, result, result)
        return result

    def create_ranking(self, df_candidates, parameters=False):
        probs = self.predict_batch(df_candidates)
        df_ranking = df_candidates.copy()
        df_ranking['probabilidade_match'] = probs
        df_ranking = df_ranking.sort_values('probabilidade_match', ascending=False)
        if parameters: return df_ranking
        else:
            colunas_para_exibir = ['codigo', 'id_vaga', 'probabilidade_match']
            return df_ranking[colunas_para_exibir]

    def predict_batch(self, input_data):
        if not self.is_trained: raise ValueError("Modelo não foi treinado ou carregado!")
        if isinstance(input_data, pd.DataFrame): df_input = input_data.copy()
        else: raise ValueError("input_data deve ser um DataFrame")
        for col in self.feature_columns:
            if col not in df_input.columns: df_input[col] = 0
        df_input = df_input[self.feature_columns]
        X_scaled = self.scaler.transform(df_input)
        probabilidades = self.model.predict(X_scaled)
        prob_match = 1 - probabilidades.flatten()
        self._update_prediction_history(df_input, prob_match.tolist(), np.mean(prob_match))
        return prob_match
        
    def get_background_data(self, section=None):
        if section: return self.background_data.get(section, {})
        return self.background_data

    def get_model_insights(self):
        if not self.background_data: return "Nenhum background data disponível"
        insights = {'data_quality': {}, 'model_health': {}, 'predictions_analysis': {}}
        if 'training_stats' in self.background_data:
            stats = self.background_data['training_stats']
            insights['data_quality'] = {
                'dataset_size': stats.get('n_samples_train', 0) + stats.get('n_samples_test', 0),
                'feature_count': stats.get('n_features', 0),
                'class_balance': stats.get('class_distribution_train', [])
            }
        if 'model_performance' in self.background_data:
            perf = self.background_data['model_performance']
            insights['model_health'] = {
                'accuracy': perf.get('test_accuracy', 0),
                'prediction_confidence': np.mean(perf.get('test_probabilities', [])) if perf.get('test_probabilities') else 0
            }
        if self.background_data.get('prediction_history'):
            recent_predictions = self.background_data['prediction_history'][-10:]
            insights['predictions_analysis'] = {
                'recent_predictions_count': len(recent_predictions),
                'average_recent_confidence': np.mean([p.get('probability', 0.5) for p in recent_predictions if p.get('probability')])
            }
        return insights


if __name__ == "__main__":
    # --- Configuração de Caminhos ---
    DATA_PATH = "app/data/silver/df_features_train.parquet"
    MODEL_DIR = "app/model/"
    MODEL_PATH = os.path.join(MODEL_DIR, "match_model.h5")
    SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")
    FEATURES_PATH = os.path.join(MODEL_DIR, "features.pkl")
    BACKGROUND_PATH = os.path.join(MODEL_DIR, "background_data.pkl")

    # Criar diretórios se não existirem
    os.makedirs(MODEL_DIR, exist_ok=True)
    # Criar um DataFrame de exemplo se o arquivo não existir
    if not os.path.exists(DATA_PATH):
        print(f"Arquivo de dados não encontrado em {DATA_PATH}. Criando um arquivo de exemplo.")
        os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
        num_samples = 500
        num_features = 20
        data = {f'feature_{i}': np.random.rand(num_samples) for i in range(num_features)}
        data['status_geral_codificado'] = np.random.randint(0, 2, num_samples)
        data['id_vaga'] = np.random.randint(1000, 2000, num_samples)
        data['codigo'] = [f'cand_{i}' for i in range(num_samples)]
        df_dummy = pd.DataFrame(data)
        df_dummy.to_parquet(DATA_PATH)
        print("Arquivo de dados de exemplo criado.")

    # --- Etapa 1: Treinamento e Salvamento do Modelo ---
    predictor_train = MatchPredictor()
    print("🚀 Iniciando o treinamento do modelo...")
    accuracy = predictor_train.train_model(df_path=DATA_PATH)
    print(f"\n✅ Treinamento concluído! Acurácia no conjunto de teste: {accuracy:.4f}")
    print("\n💾 Salvando o modelo e artefatos...")
    predictor_train.save_model(MODEL_PATH, SCALER_PATH, FEATURES_PATH, BACKGROUND_PATH)

    print("\n" + "="*50 + "\n")

    # --- Etapa 2: Carregamento e Uso do Modelo (Simulando uma nova sessão) ---
    print("🔄 Carregando o modelo para inferência e explicação...")
    predictor_load = MatchPredictor()
    predictor_load.load_model(MODEL_PATH, SCALER_PATH, FEATURES_PATH, BACKGROUND_PATH)

    # Pegar alguns candidatos do dataset original para explicar
    df_all_candidates = pd.read_parquet(DATA_PATH)
    df_to_explain = df_all_candidates.sample(3, random_state=42)

    print(f"\n🧠 Gerando explicações SHAP para {len(df_to_explain)} candidatos...")
    
    # --- Etapa 3: Gerar e Exibir Explicações SHAP ---
    try:
        df_shap_explanations = predictor_load.explain_batch_with_shap(df_to_explain, top_n=5)
        
        print("\n" + "---" * 15)
        print("📊 RESULTADO DAS EXPLICAÇÕES SHAP 📊")
        print("---" * 15)
        
        # Exibir explicações de forma legível
        for codigo in df_shap_explanations['codigo'].unique():
            print(f"\n▶️ Explicação para o Candidato: {codigo}")
            explanation_subset = df_shap_explanations[df_shap_explanations['codigo'] == codigo]
            print(explanation_subset[['feature', 'shap_value', 'valor_original']].to_string(index=False))
            print("---")

        # Mostrar a importância global das features que foi salva no background_data
        print("\n🌟 Importância Global das Features (média dos valores SHAP absolutos):")
        feature_importance = predictor_load.get_background_data('feature_importance')
        for feature, imp in list(feature_importance.items())[:5]:
            print(f"  - {feature}: {imp:.4f}")

    except Exception as e:
        print(f"❌ Ocorreu um erro ao gerar as explicações SHAP: {e}")

