from brfinance import CVMAsyncBackend
import pandas as pd
from datetime import datetime, date
import numpy as np

cvm_httpclient = CVMAsyncBackend()

class Financials_Statements:
    
    def __init__(self, cod_cvm, start_date):
        self.cod_cvm = [str(cod_cvm)]
        self.start_date = start_date
        self.search_dfp = cvm_httpclient.get_consulta_externa_cvm_results(start_date= self.start_date, cod_cvm = self.cod_cvm, category=["EST_4"])
        self.search_dfp = self.search_dfp.loc[self.search_dfp["status"] == "Ativo"]
        self.search_itr = cvm_httpclient.get_consulta_externa_cvm_results(start_date= self.start_date, cod_cvm = self.cod_cvm, category=["EST_3"])
        self.search_itr = self.search_itr.loc[self.search_itr["status"] == "Ativo"]
        self.nome = self.search_itr["empresa"][0]
        self.numero_seq_documento_itr = self.search_itr[["numero_seq_documento", "ref_date"]]
        self.numero_seq_documento_dfp = self.search_dfp[["numero_seq_documento", "ref_date"]]
        self.append_balance_assets = []
    
    def balance_sheet_assets(self, date, period):
        if period == "itr":
            number = self.numero_seq_documento_itr.loc[self.numero_seq_documento_itr["ref_date"] == date].iloc[0,0]
        else:
            number = self.numero_seq_documento_dfp.loc[self.numero_seq_documento_dfp["ref_date"] == date].iloc[0,0]
        balance = cvm_httpclient.get_report(number, 1, ["Balanço Patrimonial Ativo"])
        return balance.get("Balanço Patrimonial Ativo").fillna(0)
    
    def balance_sheet_liabilities(self, date, period):
        if period == "itr":
            number = self.numero_seq_documento_itr.loc[self.numero_seq_documento_itr["ref_date"] == date].iloc[0,0]
        else:
            number = self.numero_seq_documento_dfp.loc[self.numero_seq_documento_dfp["ref_date"] == date].iloc[0,0]
        balance = cvm_httpclient.get_report(number, 1, ["Balanço Patrimonial Passivo"])
        return balance.get("Balanço Patrimonial Passivo").fillna(0)
    
    def dfc(self, date, period):
        if period == "itr":
            number = self.numero_seq_documento_itr.loc[self.numero_seq_documento_itr["ref_date"] == date].iloc[0,0]
        else:
            number = self.numero_seq_documento_dfp.loc[self.numero_seq_documento_dfp["ref_date"] == date].iloc[0,0]
        balance = cvm_httpclient.get_report(number, 1, ["Demonstração do Fluxo de Caixa"])
        return balance.get("Demonstração do Fluxo de Caixa").fillna(0)
    
    
    def income_statement(self, date, period):
        if period == "itr":
            number = self.numero_seq_documento_itr.loc[self.numero_seq_documento_itr["ref_date"] == date].iloc[0,0]
        else:
            number = self.numero_seq_documento_dfp.loc[self.numero_seq_documento_dfp["ref_date"] == date].iloc[0,0]
        balance = cvm_httpclient.get_report(number, 1, ["Demonstração do Resultado"])
        return balance.get("Demonstração do Resultado").fillna(0)
    
    def income_acum(self, account, types, report):
        append_revenue = []
        if types == "itr":
            d = self.numero_seq_documento_itr
        else:
            d = self.numero_seq_documento_dfp
        if report == 1:
            rep = self.balance_sheet_assets
        if report == 2:
            rep = self.balance_sheet_liabilities
        if report == 3:
            rep = self.income_statement
        for x in d["ref_date"]:
            r = rep(x, types).loc[rep(x, types)["Descrição"] == account].iloc[0,2]
            append_revenue.append({account:r, "Data": x })
        data = pd.json_normalize(append_revenue).iloc[::-1].reset_index(drop = True)
        data = data.set_index("Data")
        return data