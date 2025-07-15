import json
import pandas as pd
from pathlib import Path


class Pipeline:
    
    def bronze():
        # Caminhos dos arquivos
        vagas_path = Path("app/data/bronze/vagas.json")
        applicants_path = Path("app/data/bronze/applicants.json")

        def json_to_flat_df(json_path):
            with open(json_path, encoding="utf-8") as f:
                data = json.load(f)
            # Adiciona o código como campo
            records = []
            for codigo, info in data.items():
                if not isinstance(info, dict):
                    info = {}
                rec = {"codigo": codigo}
                rec.update(info)
                records.append(rec)
            # Normaliza para DataFrame
            return pd.json_normalize(records)

        # Processa os dois arquivos
        df_vagas = json_to_flat_df(vagas_path)
        df_applicants = json_to_flat_df(applicants_path)

        # Salva em Parquet
        df_vagas.to_parquet("app/data/bronze/vagas.parquet", index=False)
        df_applicants.to_parquet("app/data/bronze/applicants.parquet", index=False)

        print("Arquivos Parquet gerados com sucesso!")


        # Para o prospects.json por se tratar de um arquivo que tem as vagas x aplicantes, preciso que traga o  primeiro nivel apenas do json, e deixe um aplicante por linha ai traga as informações do apliocante
        # ...existing code...

        prospects_path = Path("app/data/bronze/prospects.json")

        def prospects_json_to_flat_df(json_path):
            with open(json_path, encoding="utf-8") as f:
                data = json.load(f)
            records = []
            for vaga_codigo, vaga_info in data.items():
                # Copia todas as características da vaga (exceto prospects)
                vaga_base = {"vaga_codigo": vaga_codigo}
                for k, v in vaga_info.items():
                    if k != "prospects":
                        vaga_base[k] = v
                prospects = vaga_info.get("prospects", [])
                if prospects:
                    for prospect in prospects:
                        rec = vaga_base.copy()
                        if isinstance(prospect, dict):
                            rec.update(prospect)
                        else:
                            rec["applicant"] = prospect
                        records.append(rec)
                else:
                    # Caso não haja prospects, ainda assim registra a vaga
                    records.append(vaga_base)
            return pd.json_normalize(records)

        # Processa o prospects.json
        df_prospects = prospects_json_to_flat_df(prospects_path)
        df_prospects.to_parquet("app/data/bronze/prospects.parquet", index=False)

        print("Arquivo Parquet de prospects gerado com sucesso!")


    def silver():
        df_vagas = pd.read_parquet('app/data/bronze/vagas.parquet')
        df_applicants = pd.read_parquet('app/data/bronze/applicants.parquet')
        df_prospects = pd.read_parquet('app/data/bronze/prospects.parquet')


        #prospects

        df_prospects_vagas = df_prospects.merge(
            df_vagas,
            left_on='vaga_codigo',
            right_on='codigo',
            how='inner',
            suffixes=('', '_vaga')
        )

        df_prospects_full = df_prospects_vagas.merge(
            df_applicants,
            on='codigo',
            how='inner',
            suffixes=('', '_applicant')
        )

        prospects_cols = [col for col in df_prospects.columns]
        df_prospects_filtrado = df_prospects_full[prospects_cols]
        df_prospects_filtrado.to_parquet('app/data/silver/prospects.parquet', index=False)

        # vagas

        df_vagas_filtrado = df_vagas.merge(
            df_prospects_filtrado,
            left_on='codigo',
            right_on='vaga_codigo',
            how='inner',
            suffixes=('', '_prospects')
        )

        df_vagas_cols = [col for col in df_vagas.columns]
        df_vagas_filtrado = df_vagas_filtrado[df_vagas_cols]
        df_vagas_filtrado = df_vagas_filtrado.drop_duplicates()
        df_vagas_filtrado.to_parquet('app/data/silver/vagas.parquet', index=False)



        # applicants

        df_applicants_filtrado = df_applicants.merge(
            df_prospects_filtrado,
            left_on='codigo',
            right_on='codigo',
            how='inner',
            suffixes=('', '_prospects')
        )

        df_applicants_cols = [col for col in df_applicants.columns]
        df_applicants_filtrado = df_applicants_filtrado[df_applicants_cols]
        df_applicants_filtrado = df_applicants_filtrado.drop_duplicates()
        df_applicants_filtrado.to_parquet('app/data/silver/applicants.parquet', index=False)