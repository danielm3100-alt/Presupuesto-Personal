"""
Conexión a Google Sheets vía gspread + service account.
Todas las lecturas/escrituras pasan por aquí, para no repetir
la lógica de autenticación en el resto del proyecto.
"""

import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials

import config

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def conectar():
    """Crea el cliente autenticado de gspread. Se llama una sola vez por sesión.

    En Streamlit Cloud usa las credenciales guardadas en Secrets (bajo la
    clave 'gcp_service_account'). En tu PC, como no existe ese secreto,
    usa el archivo local credentials.json.
    """
    if "gcp_service_account" in st.secrets:
        info = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(info, scopes=SCOPES)
    else:
        creds = Credentials.from_service_account_file(
            config.RUTA_CREDENCIALES, scopes=SCOPES
        )
    cliente = gspread.authorize(creds)
    return cliente


def abrir_spreadsheet(cliente):
    return cliente.open(config.NOMBRE_SPREADSHEET)


def leer_hoja(spreadsheet, nombre_hoja: str) -> pd.DataFrame:
    """Lee una pestaña completa y la devuelve como DataFrame.
    La primera fila de la pestaña debe contener los encabezados.
    Si la pestaña todavía no tiene filas de datos, se conservan al
    menos los encabezados (si no, pd.DataFrame([]) queda sin columnas
    y cualquier acceso posterior a df["Rubro"] revienta con KeyError).
    """
    ws = spreadsheet.worksheet(nombre_hoja)
    valores = ws.get_all_records()
    if not valores:
        encabezados = ws.row_values(1)
        return pd.DataFrame(columns=encabezados)
    return pd.DataFrame(valores)


def escribir_hoja(spreadsheet, nombre_hoja: str, df: pd.DataFrame) -> None:
    """Sobrescribe una pestaña completa con el contenido del DataFrame
    (encabezados + filas). Igual que 'crea si no existe, actualiza si ya existe'
    del proyecto SAPy: aquí simplemente se limpia y se vuelve a escribir todo.
    """
    ws = spreadsheet.worksheet(nombre_hoja)
    ws.clear()
    datos = [df.columns.tolist()] + df.values.tolist()
    ws.update(datos)
