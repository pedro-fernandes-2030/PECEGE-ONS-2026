import sys
from pathlib import Path
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# # # # #
# Dataframe com agrupamento anual+mensal pela média
# # # # #
def agrega_df_mensal(df_input):
    df_output = (
        df_input
        .groupby(["Ano", "Mes"])[
            ["UHE", "UTE", "EOL", "UFV", "Carga", "Intercambio"]
        ]
        .mean()
        .reset_index()
    )

    df_output["Ano-Mes"] = df_output["Ano"].astype(str) + "-" + df_output["Mes"].astype(str).str.zfill(2)

    return df_output

# # # # #
# Dataframe com agrupamento anual+mensal+diário pela média
# # # # #
def agrega_df_diario(df_input):
    df_output = (
        df_input
        .groupby(["Ano", "Mes","Dia"])[
            ["UHE", "UTE", "EOL", "UFV", "Carga", "Intercambio"]
        ]
        .mean()
        .reset_index()
    )

    df_output["Ano-Mes"] = df_output["Ano"].astype(str) + "-" + df_output["Mes"].astype(str).str.zfill(2)
    df_output["Ano-Mes-Dia"] = df_output["Ano"].astype(str) + "-" + df_output["Mes"].astype(str).str.zfill(2) + "-" + df_output["Dia"].astype(str).str.zfill(2)

    return df_output

# # # # #
# Média móvel em 7 dias, para dados horários
# # # # #
def media_movel_7d(df_input, grandeza):

    df_output = (
        df_input
        .sort_values(["SME", "Data-Hora"])
        .copy()
    )

    df_output["media_movel_7d"] = (
        df_output
        .groupby("SME")[grandeza]
        .transform(
            lambda s: s.rolling(
                window=168, # 7*24 = 168
                min_periods=1
            ).mean()
        )
    )

    return df_output

# # # # #
# Média móvel em 1 dia, para dados horários
# # # # #
def media_movel_1d(df_input, grandeza):

    df_output = (
        df_input
        .sort_values(["SME", "Data-Hora"])
        .copy()
    )

    df_output["media_movel_1d"] = (
        df_output
        .groupby("SME")[grandeza]
        .transform(
            lambda s: s.rolling(
                window=24, # 1*24 = 24
                min_periods=1
            ).mean()
        )
    )

    return df_output

# # # # #
# Normalização pelo máximo
# # # # #
def norm_max_df(df_input,coluna):
    nome_coluna_nova = coluna + "_norm_max"
    df_input[nome_coluna_nova] = df_input[coluna] / df_input[coluna].abs().max()

    return df_input


# # # # #
# Patamares de carga conforme RO-EP.BR.01
# # # # #
def cria_patamar(df):

    def classifica(linha):

        hora = linha["Hora"]
        dia_semana = linha["Data-Hora"].weekday()

        if dia_semana == 8:  # domingo

            if 0 <= hora < 17:
                return "Leve"
            elif 17 <= hora < 22:
                return "Média"
            else:
                return "Leve"

        else:  # segunda a sábado

            if 0 <= hora < 7:
                return "Leve"
            elif 7 <= hora < 17:
                return "Média"
            elif 17 <= hora < 22:
                return "Pesada"
            else:
                return "Média"

    df["Patamar"] = df.apply(classifica, axis=1)

    return df


# # # # #
# Diagnóstico de outliers para carga
# # # # #
def outlier_carga(df_input, id_subsistema):

    dados_N   = df_input[df_input[id_subsistema] == "N"]
    dados_S   = df_input[df_input[id_subsistema] == "S"]
    dados_NE  = df_input[df_input[id_subsistema] == "NE"]
    dados_SE  = df_input[df_input[id_subsistema] == "SE"]
    dados_SIN = df_input[df_input[id_subsistema] == "SIN"]

    
    max_N   = dados_N["val_carga"].max()
    max_S   = dados_S["val_carga"].max()
    max_NE  = dados_NE["val_carga"].max()
    max_SE  = dados_SE["val_carga"].max()
    max_SIN = dados_SIN["val_carga"].max()

    min_N   = dados_N["val_carga"].min()
    min_S   = dados_S["val_carga"].min()
    min_NE  = dados_NE["val_carga"].min()
    min_SE  = dados_SE["val_carga"].min()
    min_SIN = dados_SIN["val_carga"].min()

    print("\nMáximos:")
    print(f"Máximo N  : {max_N:.2f}")
    print(f"Máximo S  : {max_S:.2f}")
    print(f"Máximo NE : {max_NE:.2f}")
    print(f"Máximo SE : {max_SE:.2f}")
    print(f"Máximo SIN: {max_SIN:.2f}")

    print("\nMínimos:")
    print(f"Mínimo N  : {min_N:.2f}")
    print(f"Mínimo S  : {min_S:.2f}")
    print(f"Mínimo NE : {min_NE:.2f}")
    print(f"Mínimo SE : {min_SE:.2f}")
    print(f"Mínimo SIN: {min_SIN:.2f}")

    print("\nVerificações:")
    print(f"N > min(NE)?  {max_N > min_SE}")
    print(f"S > min(SE)?  {max_S > min_SE}")
    print(f"NE > min(SE)? {max_NE > min_SE}")
    print(f"SE > min(SIN)? {max_SE > min_SIN*1.5}")



