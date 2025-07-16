


if __name__ == "__main__":
    # Inicializa o processador
    processor = CandidateFeatureEngineer()
    
    # Executa o pipeline completo
    df_final = processor.process_all(
        applicants_path="app/data/bronze/applicants.json",
        prospects_path="app/data/bronze/prospects.json",
        vagas_path="app/data/bronze/vagas.json",
        output_path="df_ML_tunado.parquet"
    )
    
    print("Features criadas:")
    print(df_final.columns.tolist())