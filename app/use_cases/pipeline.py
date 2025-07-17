import json
import pandas as pd
from pathlib import Path


class Pipeline:
    
    def bronze():
        vagas_path = Path("app/data/bronze/vagas.json")
        applicants_path = Path("app/data/bronze/applicants.json")

        def json_to_flat_df(json_path):
            with open(json_path, encoding="utf-8") as f:
                data = json.load(f)
            records = []
            for codigo, info in data.items():
                if not isinstance(info, dict):
                    info = {}
                rec = {"codigo": codigo}
                rec.update(info)
                records.append(rec)
            return pd.json_normalize(records)

        df_vagas = json_to_flat_df(vagas_path)
        df_applicants = json_to_flat_df(applicants_path)

        df_vagas.to_parquet("app/data/bronze/vagas.parquet", index=False)
        df_applicants.to_parquet("app/data/bronze/applicants.parquet", index=False)

        print("Arquivos Parquet gerados com sucesso!")

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
        df_prospects_filtrado.to_parquet('app/data/silver/prospects.parquet', index=False, compression='gzip')

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
        df_vagas_filtrado.to_parquet('app/data/silver/vagas.parquet', index=False, compression='gzip')



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
        df_applicants_filtrado.to_parquet('app/data/silver/applicants.parquet', index=False, compression='gzip')


    def silver_feature():
        df_vagas = pd.read_parquet('app/data/silver/vagas.parquet')               
        cols_vagas = ['codigo',
                        'informacoes_basicas.titulo_vaga',
                        'informacoes_basicas.origem_vaga',
                        'informacoes_basicas.tipo_contratacao',
                        'informacoes_basicas.prazo_contratacao',
                        'informacoes_basicas.prioridade_vaga',
                        'perfil_vaga.demais_observacoes',
                        'perfil_vaga.principais_atividades',
                        'perfil_vaga.competencia_tecnicas_e_comportamentais',                  
                        'perfil_vaga.estado',
                        'perfil_vaga.nivel profissional',
                        'perfil_vaga.nivel_academico',
                        'perfil_vaga.nivel_ingles',
                        'perfil_vaga.nivel_espanhol',
                        'perfil_vaga.viagens_requeridas',
                        'perfil_vaga.areas_atuacao'
                        ]
        df_vagas = df_vagas[cols_vagas]


        df_applicants = pd.read_parquet('app/data/silver/applicants.parquet')
        cols_applicants = ['codigo',
                            'infos_basicas.codigo_profissional',
                            'informacoes_profissionais.area_atuacao',
                            'formacao_e_idiomas.nivel_academico',
                            'formacao_e_idiomas.nivel_ingles',
                            'formacao_e_idiomas.nivel_espanhol',
                            'cv_pt'
                            ]
        
        df_applicants = df_applicants[cols_applicants]


        df_prospects = pd.read_parquet('app/data/silver/prospects.parquet')

        cols_prospects = ['vaga_codigo',
                        'codigo',
                        'modalidade',
                        'titulo',
                        'situacao_candidado'
                        ]
        
        df_prospects = df_prospects[cols_prospects]


        return df_applicants, df_prospects, df_vagas
    


