import pandas as pd
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from interface_adapters.repositories import Repositories

class LoadVagasListUseCase:
    def __init__(self, data_path="app/data/silver"):
        self.repositories = Repositories(data_path)

    def load_vagas(self):
        return self.repositories.load_vagas()

    def load_vagas_list(self):
        df_vagas = self.load_vagas()
        df_vagas["titulo"] = df_vagas["codigo"].astype(str) + " - " + df_vagas["informacoes_basicas.titulo_vaga"]
        return df_vagas[["titulo", "codigo"]]
