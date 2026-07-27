"""
Réplica en Python de la macro 'Totalizar' del Excel original.
Cada función corresponde a un paso de la macro, para que sea fácil
comparar contra la lógica VBA de origen.
"""

from datetime import date

import pandas as pd

import config


def calcular_gastado_y_disponible(df_proyeccion: pd.DataFrame, df_gastos: pd.DataFrame) -> pd.DataFrame:
    """Paso 1-2 de la macro: para cada rubro, suma los gastos de esa
    categoría y calcula Disponible = Proyectado - Gastado.
    Agrega también la fila 'Total' al final.
    """
    df = df_proyeccion.copy()

    gastado_por_rubro = (
        df_gastos.groupby("Categoria")["Valor"].sum() if not df_gastos.empty else pd.Series(dtype=float)
    )

    df["Gastado"] = df["Rubro"].map(gastado_por_rubro).fillna(0)
    df["Disponible"] = df["Proyectado"] - df["Gastado"]

    total = pd.DataFrame([{
        "Rubro": "Total",
        "Proyectado": df["Proyectado"].sum(),
        "Gastado": df["Gastado"].sum(),
        "Disponible": df["Disponible"].sum(),
    }])

    return pd.concat([df, total], ignore_index=True)


def estado_disponible(valor_disponible: float) -> str:
    """Paso 3 de la macro: en vez de colorear una celda (rojo/databar),
    devolvemos un estado que la interfaz pinta como corresponda.
    """
    if valor_disponible < 0:
        return "excedido"      # equivalente al rojo
    return "en_progreso"       # equivalente a la barra de datos


def categorias_vigentes(df_proyeccion: pd.DataFrame) -> list:
    """Paso 4: lista de rubros vigentes (excluyendo la fila Total),
    para poblar el selector de Categoria al registrar un gasto nuevo.
    """
    return [r for r in df_proyeccion["Rubro"].tolist() if r != "Total"]


def resumen_para_grafico(df_totalizado: pd.DataFrame) -> pd.DataFrame:
    """Paso 5: datos listos para graficar Proyectado vs Gastado por rubro
    (excluyendo la fila Total, igual que el rango B8:D(ultfila-1) original)."""
    return df_totalizado[df_totalizado["Rubro"] != "Total"][["Rubro", "Proyectado", "Gastado"]]


def servicios_pagados(df_gastos: pd.DataFrame) -> dict:
    """Paso 6: para cada palabra clave de servicio, revisa si aparece en
    el Item de algún gasto Y que ese gasto esté clasificado con la
    categoria 'Servicios' (equivalente a CountIf sobre columna C, pero
    restringido a los gastos que además caen en el rubro Servicios).
    """
    if df_gastos.empty:
        items = pd.Series(dtype=str)
    else:
        df_servicios = df_gastos[df_gastos["Categoria"] == config.CATEGORIA_SERVICIOS]
        items = df_servicios["Item"].astype(str)

    return {
        palabra: items.str.contains(palabra, case=False, na=False).any()
        for palabra in config.PALABRAS_SERVICIOS
    }


def agua_mes_impar(hoy: date | None = None) -> bool:
    """Paso 7: regla especial del agua, se marca como 'pagada' visualmente
    también si el mes actual es impar, sin importar si ya se registró el pago.
    """
    hoy = hoy or date.today()
    return hoy.month % 2 != 0


def servicio_esta_en_verde(nombre_servicio: str, df_gastos: pd.DataFrame, hoy: date | None = None) -> bool:
    """Combina los pasos 6 y 7: un servicio se muestra en verde si ya se
    pagó, o -solo para Agua- si el mes es impar."""
    pagados = servicios_pagados(df_gastos)
    if nombre_servicio == "Agua" and agua_mes_impar(hoy):
        return True
    return pagados.get(nombre_servicio, False)


def totalizar(df_proyeccion: pd.DataFrame, df_gastos: pd.DataFrame) -> dict:
    """Orquesta todos los pasos, tal como hacía Sub Totalizar() en VBA.
    Devuelve un diccionario con todo lo que la interfaz necesita mostrar.
    """
    df_totalizado = calcular_gastado_y_disponible(df_proyeccion, df_gastos)
    df_totalizado["Estado"] = df_totalizado["Disponible"].apply(estado_disponible)

    return {
        "proyeccion": df_totalizado,
        "categorias_vigentes": categorias_vigentes(df_totalizado),
        "grafico": resumen_para_grafico(df_totalizado),
        "servicios_pagados": servicios_pagados(df_gastos),
        "agua_mes_impar": agua_mes_impar(),
    }
