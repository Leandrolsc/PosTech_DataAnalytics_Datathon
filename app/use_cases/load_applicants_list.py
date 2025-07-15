import pandas as pd
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from interface_adapters.repositories import Repositories

class LoadApplicantsListUseCase:
    def __init__(self, data_path="app/data/silver"):
        self.repositories = Repositories(data_path)

    def load_applicants(self):
        return self.repositories.load_applicants()

    def load_applicants_list(self):
        df_applicants = self.load_applicants()
        df_applicants["nome"] = df_applicants["codigo"].astype(str) + " - " + df_applicants["infos_basicas.nome"]
        return df_applicants[["nome", "codigo"]]
