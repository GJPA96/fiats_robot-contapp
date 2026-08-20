import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px
import datetime as dt
import requests 
import datetime
#import WebScrapping_fiats_SQL 

st.set_page_config(
    page_title="Control Financiero",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed" # Mantiene el menú cerrado al principio
)

def verificar_password():
    """Devuelve True si el usuario ingresó la contraseña correcta."""
    # Inicializamos el estado de autenticación si no existe
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    # Si ya está autenticado, pasa directo
    if st.session_state["autenticado"]:
        return True

    # Interfaz de la pantalla de bloqueo
    st.markdown("<h2 style='text-align: center;'>🔒 Panel Restringido</h2>", unsafe_allow_html=True)
    st.write("Este sistema contiene información financiera privada. Por favor, introduce la credencial de acceso:")
    
    # Formulario para agrupar el texto y el botón (evita recargas molestas)
    with st.form("formulario_login"):
        password_ingresada = st.text_input("Contraseña", type="password", placeholder="Introduce la contraseña aquí...")
        boton_enviar = st.form_submit_button("Entrar")
        
        if boton_enviar:
            # Compara directamente con el archivo secrets.toml
            if password_ingresada == st.secrets[mysql]["password"]:
                st.session_state["autenticado"] = True
                st.rerun()  # Forza a Streamlit a recargar el código ya autenticado
            else:
                st.error("❌ Contraseña incorrecta. Inténtalo de nuevo.")
                
    return False






if verificar_password():

    st.title("Bienvenido!")
    st.write("Has ingresado a un proyecto  financiero 💰." \
    " Los objetivos de este proyecto es la creacion de un dashboard para el control de gastos personales, con el fin de mejorar la gestion financiera personal y tomar mejores decisiones sobre los gastos e inversiones. "  
         "El dashboard se alimenta de datos obtenidos a través de web scrapping de sitios como Binance y la pagina del BCV para obtener las tasas de cambio del dolar y Euro segundo el BCV y el precio del USDT en el mercado " \
        " P2P de Binance. Todos los datos son guardados en una base de datos **MYSQL** en la nube." )

    st.header(" Lenguajes y Librerias Usadas")

    st.subheader("-Python: Como lenguaje principal para el desarrollo del proyecto.")
    st.markdown("**Pandas**: Para la manipulación y análisis de datos.")
    st.markdown("**Streamlit**: Para la creación de dashboards interactivos.")
    st.markdown("**Plotly**: Para la creación de gráficos y visualizaciones.")
    st.markdown("**Requests**: Para realizar solicitudes HTTP.")
    st.markdown("**MySQL Connector**: Para conectarse a una base de datos MySQL.")
    st.subheader("-SQL: Usando MySQL para la gestión de la base de datos.")
    
    st.header("Plataformas y Herramientas Usadas")
    st.markdown(" -**Aiven** como servidor  en la nube para la base de datos MySQL.") 
    st.markdown(" -**Streamlit** como herramienta para la creación de la pagina de dashboards interactivos.") 
    st.markdown(" -**Github** para el almacenamiento, gestión y funcionamiento del código fuente en la nube. Junto con Streamlit, se " \
    "mantiene la página actualizada y en linea.")

    st.header("Estructura del Proyecto")
    st.markdown(" -**main.py**: Es la página de inicio del proyecto, donde se encuentra la pantalla de bloqueo y una introducción al proyecto.")
    st.markdown(" -**Regristro Datos**: Se registran o eliminan los datos (Ingresos y Egresos).")
    st.markdown(" -**Visualizacion**: Es la página donde se encuentran las visualizaciones y gráficos de los resgistro.")
    st.markdown(" -**Indicadores**: Se muestran los valores del dolar oficial (dolar BCV) y la  cotizacion del dolar cotizada en el mercado P2P de Binance.")
