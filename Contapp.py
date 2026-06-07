import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px
import datetime as dt
import requests 
import datetime
#import WebScrapping_fiats_SQL 



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
            if password_ingresada == st.secrets["PASSWORD_GENERAL"]:
                st.session_state["autenticado"] = True
                st.rerun()  # Forza a Streamlit a recargar el código ya autenticado
            else:
                st.error("❌ Contraseña incorrecta. Inténtalo de nuevo.")
                
    return False






if verificar_password():

    

    # Conexión (usando tus datos de Railway)
    conn =  mysql.connector.connect(
            host="mysql-1ff576c5-yaquinito-846f.g.aivencloud.com",
            port=28957,
            user="avnadmin",
            password="AVNS_4S6PBoz7B5vPQs3eRPZ",
            database="defaultdb"
        )

    #@st.cache_data(ttl=600)
    def cargar_datos_indicadores():
        # Usamos una consulta limpia ordenando por fecha para evitar desórdenes
        query = "SELECT * FROM indicadores ORDER BY Fecha ASC"
        df = pd.read_sql(query, conn)
        return df
    def borrar_registro(id):
        try:
            cursor = conn.cursor()
            query = "DELETE FROM flujo where id = %s"
            cursor.execute(query,(id,))
            conn.commit()
            st.success("Registro borrado exitosamente") 
        except Exception as e:
            st.error(f"Error al borrar el registro: {e}")
    def obtener_precio_binance_p2p():
            url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
            payload = {
                "fiat": "VES",
                "page": 1,
                "rows": 10,
                "tradeType": "BUY",  # Recuerda: "BUY" aquí te mostrará la pestaña "Vender" de la web
                "asset": "USDT",
                "countries": [],
                "proMerchantAds": False,       # Cambiado a False con mayúscula para Python
                "shieldMerchantAds": False,    # Cambiado a False con mayúscula para Python
                "filterType": "tradable",
                "periods": [],
                "additionalKycVerifyFilter": 0,
                "publisherType": 'merchant',   # Esto filtra solo usuarios que son "Comerciantes"
                "payTypes": ["PagoMovil"],     # Tu filtro actual es Pago Móvil
                "classifies": ["mass", "profession", "fiat_trade"],
                "tradedWith": False,           # Cambiado a False
                "followed": False              # Cambiado a False
                }
        
            # AGREGAMOS HEADERS: Esto le dice a Binance que somos un navegador normal
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "*/*",
                "Content-Type": "application/json"
            }
            
            try:
                # Pasamos los headers en la petición
                
                
                response = requests.post(url,json=payload, headers=headers)
                # Si el estatus no es 200, esto lanzará un error automáticamente
                response.raise_for_status() 
                
                # Ahora sí es seguro usar .json()
                data = response.json()
                st.write(f"{data['data'][1]['adv']['price']}")  # Esto es para depuración, para ver qué estructura tiene realmente la respuesta
                precio = data['data'][1]['adv']['price']  # Esto asume que siempre habrá al menos una oferta. En producción, deberías verificar esto.
                return precio
                
            except requests.exceptions.HTTPError as err:
                st.error(f"Error geográfico o de bloqueo (HTTP): {response.status_code}")
                return None
            except Exception as e:
                st.error(f"El servidor no devolvió JSON válido. Detalles: {e}")
                # Imprimimos en la consola de Python lo que realmente llegó para poder leerlo
                print("Respuesta del servidor:", response.text)
                return None
    def today_info(df):
            df=df.sort_values(by=df.columns[0],ascending=True)
            y = df.loc[df[df.columns[0]]==datetime.datetime.today().date()-datetime.timedelta(days=1)].iloc[:,1:].reset_index(drop=True)
            t = df.loc[df[df.columns[0]]==datetime.datetime.today().date()].iloc[:,1:].reset_index(drop=True)
            date = datetime.datetime.today().date() ### 
            
            
            variation=((t-y)/y)*100
            resultado = {
            'Fecha': date,
            'valores_hoy': t.to_dict(), # Contiene los precios de hoy
            'deltas': variation.to_dict() # Contiene los porcentajes de cambio
                }
            return resultado


    df_indicadores = cargar_datos_indicadores()
    df_indicadores['Fecha']=pd.to_datetime(df_indicadores['Fecha']).dt.date


    conceptos_egresos = ("Basicos", "Ropa" ,"Entretenimiento", "Ahorro", "Definir" )
    conceptos_ingresos = ("Sueldo ", "Freelance", "Inversiones","Colaboración", "Otros", "Definir")
    Hoy = dt.datetime.now().strftime("%Y-%m-%d")


    with st.sidebar:
        st.title("Navegación")
        modo = st.radio(
            "Selecciona una función:",
            ("Movimientos", "📊 Gráficas de Análisis", "💲Indicadores")
        )


    if modo == "Movimientos":

        st.header("Ultimos Movimientos Financieros")

        df = pd.read_sql("SELECT * FROM flujo", conn)
        st.dataframe(df.iloc[-1:-6:-1],column_config={
                    "Fecha": st.column_config.DatetimeColumn(
                        "Fecha",
                        format="DD/MM/YYYY",  # Aquí defines el formato
                    )},
                hide_index=True)

        col_agregar, col_borrar = st.columns(2,border=False)

        if 'accion' not in st.session_state:
            st.session_state.accion = None


            # 2. Lógica del Botón 1: AGREGAR
        if col_agregar.button("Agregar"):
        # Si ya estaba en 'agregar', lo cerramos (None), si no, lo activamos
            if st.session_state.accion == "agregar":
                st.session_state.accion = None
            else:
                st.session_state.accion = "agregar"
                st.rerun() # Forzamos recarga para ver el cambio inmediatamente

        # 3. Lógica del Botón 2: BORRAR
        if col_borrar.button("Borrar"):
        # Si ya estaba en 'borrar', lo cerramos, si no, lo activamos
            if st.session_state.accion == "borrar":
                st.session_state.accion = None
            else:
                st.session_state.accion = "borrar"
                st.rerun()            

        if st.session_state.accion == "agregar":

            Fecha_ = st.selectbox("Fecha", ("Hoy", "Ingresar fecha"))
            if Fecha_ == "Hoy":
                Fecha = Hoy
            elif Fecha_ == "Ingresar fecha":        
                Fecha = st.date_input("Selecciona la fecha", value=dt.datetime.now(),format="DD/MM/YYYY").strftime("%d-%m-%y")


            tipo = st.selectbox("Selecciona el tipo de movimiento", ("Ingreso", "Egreso"))
                    
            monto = st.number_input("Monto en $(BCV)", min_value=0.01, step=0.01)
            if tipo == "Egreso":
                    concepto = st.selectbox("Concepto (opcional)", conceptos_egresos)
            else:
                    concepto = st.selectbox("Concepto (opcional)", conceptos_ingresos)
            if concepto == "Definir":
                    concepto = st.text_input("Escribir el concepto")
            if st.button("Confirmar"):
                try:
                    cursor = conn.cursor()
                    query = "INSERT INTO flujo (Fecha, Monto_$BCV, Tipo, Concepto) VALUES (%s, %s, %s, %s)"
                    cursor.execute(query, (Fecha, monto, tipo, concepto))
                    conn.commit()
                    st.success("Movimiento agregado exitosamente")
                        
                except Exception as e:
                    st.error(f"Error al agregar el movimiento: {e}")
                finally:
                    cursor.close()
                        
        elif st.session_state.accion == "borrar":

                if "mostrando_lista" not in st.session_state:
                    st.session_state.mostrando_lista = False


                if st.session_state.mostrando_lista:
                            cursor = conn.cursor(dictionary=True) # Usamos dictionary=True para leer por nombre
                            cursor.execute("SELECT  * FROM flujo")
                            mis_gastos = cursor.fetchall()
                            # 2. Creamos la lista en Streamlit
                        # st.header(f"Fecha - Monto_$BCV - Tipo -Concepto")
                            for gasto in mis_gastos:
                            # Creamos columnas para que se vea ordenado
                                
                                col_info, col_borrar = st.columns([9, 1],border=False)
                                
                                with col_info:
                                    st.write(f" {gasto['Fecha']} - {gasto['Monto_$BCV']} $BCV - {gasto['Tipo']}- {gasto['Concepto']} ")
                                with col_borrar:
                                        with st.popover("🗑️"):
                                            if st.button("Borrar", key=f"borrar_{gasto['id']}"):
                                                borrar_registro(gasto['id'])
                                                st.session_state.accion  = None
                                                st.warning("Registro borrado")
                                                st.rerun() 

    elif modo == "📊 Gráficas de Análisis":
        
        st.header("Gráficas de Análisis")
        st.info("Aquí puedes agregar tus gráficas de análisis financiero.")
        
    
    elif modo == "💲Indicadores":
        
        st.markdown("<h1 style='text-align: center;'>Indicadores Financieros</h1>", unsafe_allow_html=True)
        
        
        fila_df_today = df_indicadores.loc[df_indicadores['Fecha'] >= datetime.datetime.today().date()-datetime.timedelta(days=1)]
        #st.write(df_indicadores.iloc[-1:-3:-1].sort_values(by=df_indicadores.columns[0],ascending=False).iloc[0,0] )
        #st.write(df_indicadores.sort_values(by=df_indicadores.columns[0],ascending=True).iloc[-1:-3:-1].iloc[:1,1:] )


        Fecha_today, dolar_binance_today, dolar_BCV_today, euro_BCV_today = fila_df_today.iloc[-1].values    
        st.subheader("Dia de Hoy")
        col_dolar_Binance,col_dolar_BCV, col_euro_BCV = st.columns(3,border=True)


        #st.write(df_indicadores.loc[df_indicadores['Fecha'] == datetime.datetime.today().date()-datetime.timedelta(days=1)])

        
        
        today = today_info(df_indicadores)
        #st.write(today['valores_hoy']["dolar_Binance"])
        ultima_fecha_real = df_indicadores[df_indicadores['Fecha'] == datetime.datetime.today().date()].iloc[0,0]   
        fecha_inicio_defecto =  df_indicadores['Fecha'].max()- datetime.timedelta(days=150)  # Mostrar por defecto los últimos 90 días
        fecha_inicio_all = df_indicadores['Fecha'].min()
        try : 
            col_dolar_Binance.metric(label=" $/Bs Binance", value = f"{today['valores_hoy']["dolar_Binance"][0]:.2f}", delta = f"{today['deltas']["dolar_Binance"][0]:.2f}%" )
            col_dolar_BCV.metric(label=" $/Bs BCV", value = f"{today['valores_hoy']["dolar_BCV"][0]:.2f}" , delta = f"{today['deltas']["dolar_BCV"][0]:.2f}%")
            col_euro_BCV.metric(label="€/Bs BCV", value = f"{today['valores_hoy']["euro_BCV"][0]:.2f}"  , delta = f"{today['deltas']["euro_BCV"][0]:.2f}%")
            #print(df_indicadores)
        except Exception as e:
            st.error(f"Error al mostrar los indicadores del día: {e}")


        fig = px.line(
                df_indicadores, 
                x="Fecha", 
                y=["dolar_BCV", "dolar_Binance"], # Puedes pasar una lista para graficar ambas líneas juntas
                title="Evolución del Dólar (BCV vs Binance P2P)",
                labels={"value": "Precio en VES", "Fecha": "Fecha", "variable": "Tipo de Dólar"},
                markers=True # Agrega un puntito en cada día para que se vea más detallado,

            )
        
            # 4. Personalizamos el diseño para que se adapte al modo oscuro/claro de Streamlit
        fig.update_layout(
                hovermode="x unified", # Muestra ambos precios al mismo tiempo al pasar el cursor
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), # Leyenda horizontal arriba
                xaxis=dict(
                    type="date", # Nos aseguramos de que Plotly trate el eje X como fechas reales
                    autorange=False,
                    range=[fecha_inicio_defecto, ultima_fecha_real],
                    minallowed=fecha_inicio_all,
                    maxallowed=ultima_fecha_real, 
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
                        bgcolor="rgba(150, 150, 150, 0.1)",
                        activecolor="rgba(100, 100, 255, 0.3)",
                        font=dict(color="white" if "dark" else "black")
                    ),
                
                )
                
            )
        
        fig.update_xaxes(
        range=[fecha_inicio_defecto, ultima_fecha_real],
        constrain="domain",
        autorange=False  # Bloquea el margen estético del 5% que mete Plotly por defecto
        )   
            # 5. ¡El toque mágico! Mostramos la gráfica en Streamlit
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("Ultimos 5 dias"):
                st.dataframe(df_indicadores.iloc[-1:-6:-1], column_config={
                    "Fecha": st.column_config.DatetimeColumn(
                        "Fecha",
                        format="DD/MM/YYYY",  # Aquí defines el formato
                    )},
                    hide_index=True)
    


