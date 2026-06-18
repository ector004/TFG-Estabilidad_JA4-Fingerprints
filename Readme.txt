# TFG - Estabilidad de huellas digitales JA4+

Repositorio de scripts y resultados del Trabajo Fin de Grado:
**Análisis de la estabilidad y variabilidad de las huellas digitales JA4 en distintos contextos**

Universidad Autónoma de Madrid (Escuela Politécnica Superior)
Autor: Héctor Payeras Rubio
Tutor: Francisco Javier Ramos de Santiago
2026

## Requisitos
```bash
pip install -r requirements.txt
```

Comprobar permisos de ejecución en los ficheros ejecutables:
```bash
chmod +x automatizacion.sh lanzador.sh
```


### Pasos de ejecución

1. Activar el entorno virtual:
```bash
source venv/bin/activate
```

2. Construir la imagen Docker (primera vez o tras modificar el Dockerfile):
```bash
sudo docker build --no-cache -t trafico_scanner .
```

3. Lanzar la automatización:
```bash
./automatizacion.sh
```

### Modo debug
Los scripts imprimen por pantalla el progreso de la ejecución. Para desactivarlo, en cada archivo hay una variable `IMPRIMIR` que se puede poner a `0`. Tras modificarla hay que recargar la imagen Docker:
```bash
sudo docker build -t trafico_scanner .
```

### Nota sobre las capturas
En `Capturas/` se organizan dos carpetas, `salidasLinux/` y `salidasWindows/`, que contienen los archivos .pcap generados durante el experimento. No se incluyen en el repositorio por su tamaño, pero las bases de datos limpias resultantes de procesarlos están disponibles en `BASE_DATOS_PRUEBA_L.csv` y `BASE_DATOS_PRUEBA_W.csv`.


## Estructura del repositorio

### Scripts de captura
**automatizacion.sh** — Script principal de captura. Implementa un bucle infinito que recorre todas las combinaciones de navegador, dispositivo y URL, lanzando un contenedor Docker por cada visita.

**lanzador.sh** — Coordina cada visita individual: inicia tcpdump, lanza el script de navegación y detiene la captura al terminar.

**navegador.py** — Controla el navegador mediante Selenium WebDriver y gestiona la emulación de dispositivo móvil.

**Dockerfile** — Define el contenedor Docker usado en Linux para aislar cada captura.

### Scripts de procesamiento
**generar_indices.py** — Procesa los JSON generados por el motor JA4, aplica criterios de limpieza y genera las bases de datos BASE_DATOS_PRUEBA_L.csv y BASE_DATOS_PRUEBA_W.csv.

### Scripts de análisis de similitud de huellas del cliente (JA4)
**distancia_huellas_so_cl.py** — Calcula la similitud de huellas JA4 del cliente agrupando por sistema operativo.

**distancia_huellas_nav_cl.py** — Calcula la similitud de huellas JA4 del cliente agrupando por navegador.

**distancia_huellas_disp_cl.py** — Calcula la similitud de huellas JA4 del cliente agrupando por tipo de dispositivo.

**igualdad_huellas.py** — Calcula la tasa de colisión exacta entre huellas JA4 del cliente.

### Scripts de análisis de similitud de huellas del servidor (JA4S)
**distancia_huellas_so_servidor.py** — Calcula la similitud de huellas JA4S del servidor agrupando por sistema operativo.

**distancia_huellas_nav_servidor.py** — Calcula la similitud de huellas JA4S del servidor agrupando por navegador.

**distancia_huellas_disp_servidor.py** — Calcula la similitud de huellas JA4S del servidor agrupando por tipo de dispositivo.

**igualdad_huellas_serv.py** — Calcula la tasa de colisión exacta entre huellas JA4S del servidor.

### Scripts de análisis de cipher suites y trazabilidad
**estudio_cipher_servidor.py** — Analiza la distribución de frecuencias de cipher suites elegidos por el servidor agrupando por SO, navegador y dispositivo.

**latencia_nav_servidor_so.py** — Implementa el estudio de trazabilidad cruzada, clasificando cada conexión según el SO del servidor estimado por TTL y cruzándolo con el SO del cliente y el navegador.

### Scripts de análisis de latencia y TTL
**latencia_so_cl.py** — Calcula estadísticas de latencia y TTL del cliente agrupando por sistema operativo.

**latencia_nav_cl.py** — Calcula estadísticas de latencia y TTL del cliente agrupando por navegador.

**latencia_disp_cl.py** — Calcula estadísticas de latencia y TTL del cliente agrupando por tipo de dispositivo.

**latencia_so_servidor.py** — Calcula estadísticas de latencia y TTL del servidor agrupando por sistema operativo.

**latencia_nav_servidor.py** — Calcula estadísticas de latencia y TTL del servidor agrupando por navegador.

**latencia_disp_servidor.py** — Calcula estadísticas de latencia y TTL del servidor agrupando por tipo de dispositivo.

### Scripts de generación de gráficas
**grafica_huellas.py** — Genera las cuatro gráficas comparativas de similitud de huellas a partir de DATOS_HUELLAS_GENERALES.csv.

**grafica_lat_ttl.py** — Genera seis gráficas por variable de latencia y TTL. Acepta un parámetro: navegador, so o dispositivo.

**grafica_latencia_global.py** — Genera las gráficas comparativas globales de latencia del cliente y del servidor a partir de LATENCIA_GENERALES.csv.


### Ficheros de datos
**BASE_DATOS_PRUEBA_L.csv** — Base de datos limpia con todas las huellas capturadas desde Linux. Contiene las columnas id_captura, navegador, plataforma, web_buscada, timestamp, tls_server_name, ja4, ja4s, ja4l_cliente, ja4l_servidor, ja4_o, ja4_ro y ja4_r.

**BASE_DATOS_PRUEBA_W.csv** — Base de datos limpia con todas las huellas capturadas desde Windows. Misma estructura que la anterior.

**DATOS_HUELLAS_GENERALES.csv** — Índices de similitud agregados para todas las variables y métricas.

**ESTUDIO_CIPHER_SRV.csv** — Distribución de frecuencias de cipher suites y hash de extensiones del servidor.

**ESTUDIO_CRUCE_SO.csv** — Tabla de trazabilidad cruzada con el número de conexiones por tipo de servidor.

**LATENCIA_GENERALES.csv** — Latencia media global del cliente y del servidor por variable.


### Carpetas de resultados
**estudio_huellas_cl/ y estudio_huellas_srv/** — Contienen los resultados detallados del análisis de similitud del cliente y del servidor respectivamente. No se incluyen en el repositorio por su tamaño (algunos ficheros superan 800 MB), pero se generan ejecutando los scripts de distancia sobre las bases de datos BASE_DATOS_PRUEBA_L.csv y BASE_DATOS_PRUEBA_W.csv.

**SO/**, **Navegador/**, **Dispositivo/** — Resultados del análisis de latencia y TTL agrupados por cada variable de estudio.

**Graficas_huellas/** — Gráficas comparativas de similitud generadas por grafica_huellas.py.

**Graficas_LAT_TTL/** — Gráficas de latencia y TTL generadas por grafica_lat_ttl.py y grafica_latencia_global.py.

**Capturas/** — En `Capturas/` se organizan dos carpetas, `salidasLinux/` y `salidasWindows/`, que contienen los archivos .pcap generados durante el experimento. No se incluyen en el repositorio por su tamaño, pero las bases de datos limpias resultantes de procesarlos están disponibles en `BASE_DATOS_PRUEBA_L.csv` y `BASE_DATOS_PRUEBA_W.csv`.


## Orden de ejecución
1. `automatizacion.sh` -> genera las capturas .pcap
2. `generar_indices.py` -> genera las bases de datos limpias
3. Scripts de distancia y latencia -> generan los CSV de resultados en sus carpetas correspondientes
4. `grafica_huellas.py` y `grafica_lat_ttl.py` -> generan las gráficas finales
