import pandas as pd
import sqlalchemy as sa
import requests 
import numpy as np
from datetime import datetime
import mysql.connector
import locale
from bs4 import BeautifulSoup
import pytz
import os
zona_ve = pytz.timezone('America/Caracas')

conn =  mysql.connector.connect(
            host=os.environ.get("DB_HOST"),
            port=28957,
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASSWORD"),
            database=os.environ.get("DB_NAME")
        )




########## Mapas y Listas #############

###Meses  a Numero
mes_dict={
        'Enero': '01',
        'Febrero': '02',
        'Marzo': '03',
        'Abril': '04',
        'Mayo': '05',
        'Junio': '06',
        'Julio': '07',
        'Agosto': '08',
        'Sepiembre': '09',
        'Octubre': '10',
        'Noviembre': '11',
        'Diciembre': '12'
}
#### Lista de Fiats
fiats_BCV=["dolar", "euro"]




###### Funciones ########


def obtener_precio_bcv( fiat:str):   ### Obtiene por WebScrapping el valor del USD y la fecha del dia presente #####
    url = "https://www.bcv.org.ve/"
    

    try:

        response = requests.get( url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:150.0) Gecko/20100101 Firefox/150.0" 
            }, verify=False)
        response.raise_for_status() # Por si no se conecta, python lance una  Exception y se detenga el programa.

        soup=BeautifulSoup(response.text, "html.parser") # reescribrimos la respuesta en un objeto 
        #de beautifulsoup para trabajar con el,
        fiat_bcv = soup.find("div",{"id":fiat})
        fiat_bcv = fiat_bcv.find("div",{"class":"col-sm-6 col-xs-6 centrado textp"}).text.strip()
        fiat_bcv=float(fiat_bcv.replace(",","."))
       

        fecha= soup.find("span",{'class':"date-display-single"}).get_text().split()
        
        fecha[2]=mes_dict[fecha[2]] # Convertimos el mes de texto a número usando el diccionario
        
        fecha="%s %s %s" %(fecha[1],fecha[2],fecha[3])
        
        try:
            # 3. Configuramos Python temporalmente en español para que entienda "Mayo" y "Martes"
            # (En Windows se usa 'es_ES' o 'spanish'. En Linux/Google Cloud se usa 'es_ES.UTF-8')
            # try:
            #    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
            #except locale.Error:
            #     locale.setlocale(locale.LC_TIME, 'spanish') # Alternativa para Windows
                
            fecha=datetime.strptime(fecha.strip(), "%d %m %Y")
            #print(fecha)
        except Exception as e:
            print(f"Error al convertir la fecha: {e}")

        
        return fecha,fiat_bcv
    except requests.exceptions.HTTPError as err:
        print("Error al obtener datos del BCV (HTTP): {response.status_code}")
        #st.error(f"Error al obtener datos del BCV (HTTP): {response.status_code}")
        return None
    except Exception as e:
        print("Error al obtener datos del BCV: {e}")
        #st.error(f"Error al obtener datos del BCV: {e}")
        return None

def obtener_precio_binance_p2p(): ### Obtiene por WebScrapping el valor del Dolar o Euro segun el BCV en su pagina y la fecha
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
        
        precio = data['data'][1]['adv']['price']  # Esto asume que siempre habrá al menos una oferta. En producción, deberías verificar esto.
        
        return  datetime.now(zona_ve).replace(hour=0, minute=0, second=0, microsecond=0),precio
        
    except requests.exceptions.HTTPError as err:
        print(f"Error geográfico o de bloqueo (HTTP): {response.status_code}")
        return None
    except Exception as e:
        print(f"El servidor no devolvió JSON válido. Detalles: {e}")
        # Imprimimos en la consola de Python lo que realmente llegó para poder leerlo
        print("Respuesta del servidor:", response.text)
        return None

def Actualizacion_fiats_SQL() : ### Actualiza en la base de datos el valor del dolar y euro segun el BCV y el dolar en Binance USDT

    try:
        cursor = conn.cursor()
        cursor.execute("SET time_zone = '-04:00';")
    except Exception as e:
        print(f'Error al configurar la zona horaria: {e}')  
    finally:    
        cursor.close()
    
    try:
        cursor = conn.cursor()
        query = "INSERT into indicadores(Fecha, dolar_Binance  ) values (%s,%s)  ON DUPLICATE   KEY  UPDATE  Dolar_Binance = (%s) ;"
        fecha,precio = obtener_precio_binance_p2p()
        cursor.execute(query,(fecha,precio,precio))
        conn.commit()
    except Exception as e:
        print(f'Error al introduccir el precio del dolar Binance {e}')
    finally:
        cursor.close()



    try:
        
        fecha, precio_dolar = obtener_precio_bcv("dolar")
        fecha, precio_euro = obtener_precio_bcv("euro")
        cursor = conn.cursor()
        query = "CALL datecheck_loop(%s,%s,%s);"
        cursor.execute(query,(fecha,precio_dolar,precio_euro))
        conn.commit()
    except Exception as e:
         print(f'Error al introduccir el precio del dolar o euro BCV {e}')
    finally:
        cursor.close()

Actualizacion_fiats_SQL()
