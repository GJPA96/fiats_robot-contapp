import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px
import datetime as dt




if "autenticado" not in st.session_state or not st.session_state["autenticado"]:
    st.warning("⚠️ Acceso denegado. Por favor, inicia sesión en la página principal.")
    st.page_link("main.py", label="Ir al Inicio para Loguearse", icon="🏠")
    st.stop()



######################  Opciones ######################
tipo_movimiento = ("Ingreso", "Egreso","Ahorro", "Inversiones", "Otros")
tipo_fiat = ("VES","USD", "USDT" )
conceptos_egresos = ("Basicos", "Ropa" ,"Entretenimiento", "Ahorro", "Definir" )
conceptos_ingresos = ("Sueldo ", "Freelance", "Inversiones","Colaboración", "Otros", "Definir")
opciones_busqueda = ("Fecha","Rango de fechas", "Tipo de movimiento", "Concepto", "Rango de montos","Fiat" )
Hoy = dt.datetime.now().strftime("%Y-%m-%d")
#########################################################


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








    

 # Conexión (usando tus datos de Railway)
conn =  mysql.connector.connect(
            host="mysql-1ff576c5-yaquinito-846f.g.aivencloud.com",
            port=28957,
            user="avnadmin",
            password="AVNS_4S6PBoz7B5vPQs3eRPZ",
            database="defaultdb"
        )

    #@st.cache_data(ttl=600)
    
def borrar_registro(id):
        try:
            cursor = conn.cursor()
            query = "DELETE FROM flujo where id = %s"
            cursor.execute(query,(id,))
            conn.commit()
            st.success("Registro borrado exitosamente") 
        except Exception as e:
            st.error(f"Error al borrar el registro: {e}")
        finally:
            cursor.close()
    
    

def buscar_movimientos(opciones_busqueda,):
    busqueda_tipo=st.selectbox("Buscar por", opciones_busqueda)
    
    with st.form("Buscar Movimientos"):
        print("1",st.session_state.busqueda_realizada)
        df_query = ""

        match busqueda_tipo:
            
            case "Fecha":
                    fecha_busqueda=st.date_input("Selecciona la fecha", value=dt.datetime.now(),format="DD/MM/YYYY")
                    df_query = f"SELECT id,Fecha,Fiat,Monto_$BCV,Tipo FROM flujo WHERE Fecha = '{fecha_busqueda.strftime('%Y-%m-%d')}'"
                    print("Algunas fechas tienen una hora diferente de 00:00:00, por lo que es importante formatearlas correctamente para la consulta SQL.")

            case "tipo de Fiat":
                    tipo_fiat_busqueda = st.selectbox("Selecciona el tipo de moneda", tipo_fiat)
                    df_query = f"SELECT id,Fecha,Fiat,Monto_$BCV,Tipo FROM flujo WHERE Fiat = '{tipo_fiat_busqueda}'"

            case "Tipo de movimiento":
                    tipo_busqueda = st.selectbox("Selecciona el tipo de movimiento", tipo_movimiento    )
                    df_query = f"SELECT id,Fecha,Fiat,Monto_$BCV,Tipo FROM flujo WHERE Tipo = '{tipo_busqueda}'"

            case "Concepto":
                    concepto_busqueda = st.selectbox("Selecciona el concepto", conceptos_egresos + conceptos_ingresos)
                    df_query = f"SELECT id,Fecha,Fiat,Monto_$BCV,Tipo FROM flujo WHERE Concepto = '{concepto_busqueda}'"
                    
            case "Rango de montos":
                    col_monto_min, col_monto_max = st.columns(2,border=False)
                    monto_min=col_monto_min.number_input("Monto mínimo", min_value=0.01, step=0.01)
                    monto_max=col_monto_max.number_input("Monto máximo", min_value=0.01, step=0.01)
                    df_query = f"SELECT id,Fecha,Fiat,Monto_$BCV,Tipo FROM flujo WHERE Monto_$BCV BETWEEN {monto_min} AND {monto_max}"
                    
            case "Rango de fechas":
                    col_fecha_inicio, col_fecha_fin = st.columns(2,border=False)
                    fecha_inicio=col_fecha_inicio.date_input("Desde", value=dt.datetime.now(),format="DD/MM/YYYY")
                    fecha_fin=col_fecha_fin.date_input("Hasta", value=dt.datetime.now(),format="DD/MM/YYYY")
                    print(type(fecha_inicio), type(fecha_fin))
                    df_query = f"SELECT id,Fecha,Fiat,Monto_$BCV,Tipo FROM flujo WHERE Fecha BETWEEN '{fecha_inicio.strftime('%Y-%m-%d')}' AND '{fecha_fin.strftime('%Y-%m-%d')}'"
    
        boton_buscar = st.form_submit_button("Buscar")
        
        print("2",st.session_state.busqueda_realizada)
        
    if boton_buscar or st.session_state.busqueda_realizada: 
        print("3",st.session_state.busqueda_realizada)
        df = pd.DataFrame()  # Inicializamos el DataFrame vacío
    
        df = pd.read_sql(df_query, conn)
        print(df)
    


            

        st.session_state.df_busqueda = df
        st.session_state.busqueda_realizada = True
        print("4",st.session_state.busqueda_realizada)
        print(st.session_state.df_busqueda)
        if not st.session_state.df_busqueda.empty and st.session_state.busqueda_realizada :
            st.write("Resultados de la búsqueda:")
            print("5",st.session_state.busqueda_realizada)
            #print(st.session_state.df_busqueda)
            st.session_state.df_busqueda.insert(0, "Seleccionar", False)
            print(st.session_state.df_busqueda.columns)
            with st.form("a"):
                df_editado = st.data_editor(
                    st.session_state.df_busqueda,
                    column_config={
                        "id": None,  # Ocultamos la columna ID para que se vea más limpio
                        "Fecha": st.column_config.DateColumn("Fecha", format="DD/MM/YYYY"),
                        "Seleccionar": st.column_config.CheckboxColumn("Borrar", default=False)
                    },
                    hide_index=True,
                    use_container_width=True,
                    disabled=["id", "Fecha", "Concepto", "Monto_$BCV", "Tipo"]
                    
                )

                
                botton_submitted = st.form_submit_button("Eliminar filas seleccionadas")
                
            print("antes")
            if botton_submitted:
                print("entro")
                filas_a_borrar = df_editado[df_editado["Seleccionar"] == True]
                #print("Filas a borrar:", filas_a_borrar)
                if not filas_a_borrar.empty:
                    
                
                    ids_a_eliminar = filas_a_borrar["id"].tolist()
                    
                    try:
                        cursor =  conn.cursor()
                        formalizador = ", ".join(['%s']*len(ids_a_eliminar))
                        query_delete = f"DELETE FROM flujo where id IN ({formalizador}) "
                        cursor.execute(query_delete,tuple(ids_a_eliminar))
                        conn.commit()
                        cursor.close()

                        st.success(f"✅ Se eliminaron {len(ids_a_eliminar)} registros correctamente.")

                        st.rerun() # Reiniciamos una sola vez para actualizar la lista de la pantalla
                        st.session_state.busqueda_realizada = False  # Reiniciamos la búsqueda
                        st.session_state.df_busqueda = pd.DataFrame()  # Reiniciamos el Data
                    except Exception as e:
                        print(f"Error al conectar con Aiven para eliminar datos en el registro: {e}")
                    

        else:
            st.warning("⚠️ No se encontraron registros que coincidan con la búsqueda.")        
    return None 


if  "df_busqueda" not in st.session_state:
      st.session_state.df_busqueda = pd.DataFrame()
if "busqueda_realizada" not in st.session_state:
    st.session_state.busqueda_realizada = False



st.header("Movimientos")
st.subheader("Buscar/ Eliminar Movimientos")



buscar_movimientos(opciones_busqueda)

st.header("Ultimos Movimientos ")

df = pd.read_sql("SELECT * FROM flujo order by Fecha ASC ", conn)
#print(df)


st.dataframe(df.iloc[-1:-6:-1],column_config={
                    "Fecha": st.column_config.DatetimeColumn(
                        "Fecha",
                        format="DD/MM/YYYY",  # Aquí defines el formato
                    )},
                hide_index=False)

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
                Fecha = st.date_input("Selecciona la fecha", value=dt.datetime.now(),format="DD/MM/YYYY").strftime("%y-%m-%d")
                #print(Fecha)

            tipo = st.selectbox("Selecciona el tipo de movimiento", ("Ingreso", "Egreso"))
            tipo_fiat = st.selectbox("Selecciona el tipo de moneda", tipo_fiat)
            monto = st.number_input("Monto", min_value=0.01, step=0.01)
            if tipo == "Egreso":
                    concepto = st.selectbox("Concepto (opcional)", conceptos_egresos)
            else:
                    concepto = st.selectbox("Concepto (opcional)", conceptos_ingresos)
            if concepto == "Definir":
                    concepto = st.text_input("Escribir el concepto")
            if st.button("Confirmar"):
                try:
                    cursor = conn.cursor()
                    query = "INSERT INTO flujo (Fecha, Monto_$BCV, Tipo, Concepto, Fiat) VALUES (%s, %s, %s, %s, %s)"
                    cursor.execute(query, (Fecha, monto, tipo, concepto, tipo_fiat))
                    conn.commit()
                    st.success("Movimiento agregado exitosamente")

                except Exception as e:
                    st.error(f"Error al agregar el movimiento: {e}")
                finally:
                    cursor.close()



elif st.session_state.accion == "borrar":
    
    if "mostrando_lista" not in st.session_state:
                    st.session_state.mostrando_lista = False
    

    if st.session_state.mostrando_lista is not True:
                            
                            cursor = conn.cursor(dictionary=True) # Usamos dictionary=True para leer por nombre
                            cursor.execute("SELECT  * FROM flujo")
                            mis_gastos = cursor.fetchall()
                            #print(mis_gastos)
                            cursor.close()
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



