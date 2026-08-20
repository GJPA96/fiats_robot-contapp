import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px
import datetime as dt
import numpy as np
from plotly.subplots import make_subplots

#import WebScrapping_fiats_SQL 



if "autenticado" not in st.session_state or not st.session_state["autenticado"]:
    st.warning("⚠️ Acceso denegado. Por favor, inicia sesión en la página principal.")
    st.page_link("main.py", label="Ir al Inicio para Loguearse", icon="🏠")
    st.stop()






conn =  mysql.connector.connect(
            host="mysql-1ff576c5-yaquinito-846f.g.aivencloud.com",
            port=28957,
            user="avnadmin",
            password="AVNS_4S6PBoz7B5vPQs3eRPZ",
            database="defaultdb"
        )


fiats = ["VES", "USD", "USDT"]
query_gastos = "SELECT * FROM flujo "
#df_gastos = pd.read_sql(query_gastos, con=conn)   

@st.cache_data(ttl=3600)  # Cachea los datos por 1 hora
def generar_datos_simulados(num_registros):
    # 1. Definir los parámetros de simulación
    #fecha_inicio = dt.date(2026, 1, 1)
    fecha_inicio = dt.date.today()  # Usamos la fecha actual como referencia
    dias_desde_fecha_inicio = (dt.date.today() - dt.date(2026, 1, 1)).days
    # Listas de conceptos reales del negocio
    conceptos_ingresos = [
        "Sueldo",
        "Servicio Técnico",
        "Abono Cliente",
        "Clases Particulares",
    ]
    conceptos_egresos = [
        "Pago de Alquiler",
        "Comida",
        "Transporte",
        "Pago de Internet",
    ]

    tipo_fiat = ["VES","USD", "USDT"]  # Lista de monedas fiat

    # 2. Generar vectores aleatorios usando Numpy
    np.random.seed(42)  # Para que los datos no cambien en cada recarga

    # Generar fechas aleatorias que se van a repetir (dentro de un rango de 60 días)
    fechas = [
        fecha_inicio - dt.timedelta(days=int(np.random.randint(0, dias_desde_fecha_inicio)))
        for _ in range(num_registros)
    ]

    # Decidir aleatoriamente si es Ingreso o Gasto (50% de probabilidad cada uno)
    tipos = np.random.choice(["ingreso", "gasto"], size=num_registros)

    conceptos = []
    montos = []
    Fiat = []
    # 3. Asignar conceptos y montos lógicos según el tipo de movimiento
    for tipo in tipos:
        if tipo == "ingreso":
            conceptos.append(np.random.choice(conceptos_ingresos))
            # Los ingresos suelen ser montos más altos
            montos.append(round(np.random.uniform(20.0, 150.0), 2))
        else:
            conceptos.append(np.random.choice(conceptos_egresos))
            # Los gastos suelen ser montos más pequeños pero más comunes
            montos.append(round(np.random.uniform(5.0, 50.0), 2))


    # 4. Asignar aleatoriamente un tipo de moneda fiat a cada registro
    Fiat  = np.random.choice(tipo_fiat, size=num_registros)

    # 4. Armar el DataFrame final de Pandas de forma automática
    df_simulado = pd.DataFrame(
        {
            "Fecha": fechas,
            "Concepto": conceptos,
            "Monto_$BCV": montos,
            "Tipo": tipos,
            "Fiat": Fiat
        }
    )

    # Ordenar por fecha cronológicamente
    return df_simulado.sort_values(by="Fecha").reset_index(drop=True)









df_flujo = generar_datos_simulados(300)  # Genera 100 registros simulados




####################################Total de Ingresos y Egresos ####################################
st.title("Resumen Financiero")
st.table(df_flujo.groupby("Tipo")["Monto_$BCV"].sum().reset_index().rename(columns={"Monto_$BCV": "Total ($BCV)"}))

################# Flujo de Ingresos y Egresos por fecha ####################


st.title("Visualización de Movimientos")
tipo_fiat = st.selectbox("Selecciona el tipo de moneda para la grafica", fiats, key="tipo_fiat_bar")

plot = px.bar(df_flujo[df_flujo["Fiat"] == tipo_fiat], x='Fecha', y='Monto_$BCV', color='Tipo', title='Flujo de Ingresos y Egresos por fecha')

plot.update_layout(
                    barmode='group',
                    bargap=0.2,      # Spacing between Q1, Q2, and Q3 clusters
                    bargroupgap=0.05, 
                hovermode="x unified", # Muestra ambos precios al mismo tiempo al pasar el cursor
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), # Leyenda horizontal arriba
                xaxis=dict(
                    type="date", # Nos aseguramos de que Plotly trate el eje X como fechas reales
                    autorange=False,
                    range=[df_flujo["Fecha"].min(), df_flujo["Fecha"].max()],
                    minallowed=df_flujo["Fecha"].min(),
                    maxallowed=df_flujo["Fecha"].max(), 
                    rangeselector=dict(
                        buttons=list([
                            # Botón para 7 días
                            dict(count=7, label="7D", step="day", stepmode="backward"),
                            # Botón para 15 días
                            dict(count=15, label="15D", step="day", stepmode="backward"),
                            # Botón para 1 mes
                            dict(count=30, label="1M", step="day", stepmode="backward"),
                            # Botón para 3 meses
                            dict(count=90, label="3M", step="day", stepmode="backward"),
                            # Botón para ver todo el histórico disponible
                            dict(step="all", label="Todo")

                        ]),
                        # Estética de los botones (opcional, para que combinen con el modo oscuro de Streamlit)
                        bgcolor="rgba(150, 150, 150, 0.5)",
                        activecolor="rgba(100, 100, 255, 0.3)",
                        font=dict(color="white" if "dark" else "black")
                    ),
                
                )
                
            )
st.plotly_chart(plot, use_container_width=True) 








st.write("### 🍩 Distribución porcentual de Gastos y Egresos por Concepto")

tipo_fiat_donut = st.selectbox("Selecciona el tipo de moneda para la grafica", fiats, key="tipo_fiat_donut")
ultima_fecha= df_flujo["Fecha"].max()
opciones_fecha_pie = {"Todo":0,"7D": 7, "30D": 30, "60D" : 60 , "180D" : 180 }
fecha_pie = st.selectbox("Desde", list(opciones_fecha_pie.keys()) )
print(opciones_fecha_pie[fecha_pie])

if opciones_fecha_pie[fecha_pie]>0:
    df_flujo = df_flujo[df_flujo["Fecha"]>=ultima_fecha-pd.Timedelta(days=opciones_fecha_pie[fecha_pie])]


df_flujo_grouped = df_flujo.groupby(["Tipo", "Fiat", "Concepto"])["Monto_$BCV"].sum().reset_index()




#df_flujo_grouped = df_flujo_grouped[df_flujo_grouped["Fecha"]>=ultima_fecha-pd.Timedelta(days=opciones_fecha_pie[fecha_pie])]
#print(ultima_fecha-pd.Timedelta(days=opciones_fecha_pie[fecha_pie]))
df_gastos = df_flujo_grouped[(df_flujo_grouped["Tipo"] == "gasto") & (df_flujo_grouped["Fiat"] == tipo_fiat_donut)]
df_ingresos = df_flujo_grouped[(df_flujo_grouped["Tipo"] == "ingreso") & (df_flujo_grouped["Fiat"] == tipo_fiat_donut)]

total_gastos = df_gastos.groupby("Concepto")["Monto_$BCV"].sum().reset_index()["Monto_$BCV"].sum()

fig_dona_gastos = px.pie(
    df_gastos,
    values="Monto_$BCV",
    names="Concepto",
    hole=0.5,
    title="Egresos",
    color_discrete_sequence=px.colors.qualitative.Pastel,
)


fig_dona_gastos.update_layout(
    title_text="Egresos ",
    # Add annotations in the center of the donut pies.
    annotations=[dict(text=f'Total: ${total_gastos:.2f}', x=0.5, y=0.5,
                      font_size=15, showarrow=False, xanchor="center")],
                     
              )






df_ingresos = df_flujo_grouped[df_flujo_grouped["Tipo"] == "ingreso"]
total_ingresos= df_ingresos["Monto_$BCV"].sum()


fig_dona_ingresos = px.pie(
    df_ingresos,
    values="Monto_$BCV",
    names="Concepto",
    hole=0.5,
    title="Ingresos ",
    color_discrete_sequence=px.colors.qualitative.Pastel,
)
fig_dona_ingresos.update_layout(
    title_text="Ingresos ",
    # Add annotations in the center of the donut pies.
    annotations=[dict(text=f'Total: ${total_ingresos:.2f}', x=0.5, y=0.5,
                      font_size=15, showarrow=False, xanchor="center")]
              )


column_ingreso, column_gastos = st.columns(2)

with column_ingreso:

    st.plotly_chart(fig_dona_ingresos, use_container_width=True)
with column_gastos:
    
    st.plotly_chart(fig_dona_gastos, use_container_width=True)