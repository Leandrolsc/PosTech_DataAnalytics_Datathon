import pandas as pd


class Repositories:
    def __init__(self, data_path="app/data/silver"):
        self.data_path = data_path

    def load_vagas(self):
        return pd.read_parquet(f"{self.data_path}/vagas.parquet",)
 
    def load_prospects(self):
        return pd.read_parquet(f"{self.data_path}/prospects.parquet")

    def load_applicants(self):
        return pd.read_parquet(f"{self.data_path}/applicants.parquet")
    
