"""
Interfaz Streamlit de la app de presupuesto.
Usa sheets_client para leer/escribir Google Sheets y logica.totalizar()
para reproducir el comportamiento de la macro 'Totalizar' original.
"""

from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st

import config
import logica
import sheets_client

st.set_page_config(page_title="Presupuesto", page_icon="💰", layout="wide")


@st.cache_resource
def obtener_spreadsheet():
    cliente = sheets_client.conectar()
    return sheets_client.abrir_spreadsheet(cliente)


def cargar_datos(spreadsheet):
    df_proyeccion = sheets_client.leer_hoja(spreadsheet, config.HOJA_PROYECCION)
    df_gastos = sheets_client.leer_hoja(spreadsheet, config.HOJA_GASTOS)
    df_servicios = sheets_client.leer_hoja(spreadsheet, config.HOJA_SERVICIOS)
    return df_proyeccion, df_gastos, df_servicios


def color_estado(fila):
    color = "#f8d7da" if fila["Estado"] == "excedido" else "#d4edda"
    return [f"background-color: {color}"] * len(fila)


def inicializar_estado(spreadsheet):
    if "df_proyeccion" not in st.session_state:
        df_proyeccion, df_gastos, df_servicios = cargar_datos(spreadsheet)
        st.session_state.df_proyeccion = df_proyeccion
        st.session_state.df_gastos = df_gastos
        st.session_state.df_servicios = df_servicios


def main():
    st.title("💰 Presupuesto")

    spreadsheet = obtener_spreadsheet()
    inicializar_estado(spreadsheet)

    resultado = logica.totalizar(st.session_state.df_proyeccion, st.session_state.df_gastos)

    tab_resumen, tab_registrar, tab_servicios = st.tabs(
        ["Resumen", "Registrar gasto", "Servicios"]
    )

    with tab_resumen:
        if st.button("🔄 Actualizar desde Google Sheets"):
            df_proyeccion, df_gastos, df_servicios = cargar_datos(spreadsheet)
            st.session_state.df_proyeccion = df_proyeccion
            st.session_state.df_gastos = df_gastos
            st.session_state.df_servicios = df_servicios
            st.rerun()

        columnas_moneda = ["Proyectado", "Gastado", "Disponible"]
        st.dataframe(
            resultado["proyeccion"]
            .style.apply(color_estado, axis=1)
            .format({col: "${:,.0f}" for col in columnas_moneda}),
            use_container_width=True,
            hide_index=True,
        )

        st.subheader("Proyectado vs Gastado")
        df_grafico = resultado["grafico"].melt(
            id_vars="Rubro",
            value_vars=["Proyectado", "Gastado"],
            var_name="Tipo",
            value_name="Valor",
        )
        fig = px.bar(df_grafico, x="Rubro", y="Valor", color="Tipo", barmode="group")
        st.plotly_chart(fig, use_container_width=True)

    with tab_registrar:
        st.subheader("Registrar nuevo gasto")
        with st.form("form_gasto", clear_on_submit=True):
            fecha = st.date_input("Fecha", value=date.today())
            item = st.text_input("Item")
            valor = st.number_input("Valor", min_value=0, step=1000)
            categoria = st.selectbox("Categoria", resultado["categorias_vigentes"])
            enviado = st.form_submit_button("Guardar gasto")

        if enviado:
            if not item or valor <= 0:
                st.warning("Completa Item y Valor antes de guardar.")
            else:
                nueva_fila = pd.DataFrame([{
                    "Fecha": fecha.isoformat(),
                    "Item": item,
                    "Valor": valor,
                    "Categoria": categoria,
                }])
                df_actualizado = pd.concat(
                    [st.session_state.df_gastos, nueva_fila], ignore_index=True
                )
                sheets_client.escribir_hoja(spreadsheet, config.HOJA_GASTOS, df_actualizado)
                st.session_state.df_gastos = df_actualizado
                st.success("Gasto guardado.")
                st.rerun()

        st.divider()
        st.subheader("Gastos registrados")
        st.caption(
            "Puedes editar cualquier celda, o borrar una fila con el ícono de "
            "la izquierda. Los cambios no se guardan hasta que presiones "
            "'Guardar cambios'."
        )

        df_editado = st.data_editor(
            st.session_state.df_gastos,
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
            key="editor_gastos",
            column_config={
                "Categoria": st.column_config.SelectboxColumn(
                    "Categoria", options=resultado["categorias_vigentes"]
                ),
                "Valor": st.column_config.NumberColumn("Valor", format="$%d"),
            },
        )

        if st.button("💾 Guardar cambios"):
            sheets_client.escribir_hoja(spreadsheet, config.HOJA_GASTOS, df_editado)
            st.session_state.df_gastos = df_editado
            st.success("Cambios guardados.")
            st.rerun()

    with tab_servicios:
        st.subheader("Estado de pago de servicios")
        st.caption(
            "Se marca en verde si hay un gasto con esa palabra clave en el Item "
            "clasificado como Categoria = Servicios. El Agua además se marca en "
            "verde automáticamente en meses impares."
        )
        for palabra in config.PALABRAS_SERVICIOS:
            en_verde = logica.servicio_esta_en_verde(palabra, st.session_state.df_gastos)
            emoji = "🟢" if en_verde else "⚪"
            es_agua_por_mes = (
                palabra == "Agua" and resultado["agua_mes_impar"] and en_verde
            )
            nota = " (Bimensual)" if es_agua_por_mes else ""
            st.write(f"{emoji} {palabra}{nota}")

        st.divider()
        st.subheader("Valores estimados por servicio")
        st.dataframe(st.session_state.df_servicios, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
