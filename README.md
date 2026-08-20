* # Objetivos : Crear un dashboard que muestre información financiera relevante para ayudar en las toma de decisiones.

* # Estado del proyecto : En desarrollo
  Actualmente el dashboard puede mostrar los ingresos/gastos  para diferentes periodos de tiempos[1], el tipo de cambio en bolivares del dólar americano y el euro  fijados por el BCV, y el valor en bolivares del USDT manejado en el P2P de Binance. Próximamente se implementara un actualización para mostrar otros indicadores.


* # Lenguajes y librerías:
 - Python como lenguaje principal en el desarrollo del proyecto.
 - - Librerias :
   - Pandas para el manejo de datos.
   - Streamlit para crear el dashboard interactivo.
   - Plotly para visualizar los datos.
   - Request para hacer solicitudes HTTP.
   - Beautifulsoap para hacer web scrapping y obtener los tipos de cambio de las fiats y la cripto moneda. 
   - MySQL Connector para conectar a una base de datos  MySQL en la nube.
 - SQL (MySQL) para la creación y gestión de la base de datos.

* # Plataforma y herramientas usadas:
- Aiven : servidor en la nube donde se encuentra la base de datos.
- Servidor de Streamlit : Se utiliza para mantener el dashboard  online en la web.
- GitHub : Aloja el programa que ejecuta el servidor de Streamlit y ejecuta un programa para actualizar la base de datos diariamente.
- Gemini : el IA chatbot de Google como herramienta de consulta.

  
Notas:
[1] Los datos de ingresos y gastos son generados artificialmente.  
