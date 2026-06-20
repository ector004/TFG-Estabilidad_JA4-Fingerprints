# Autor: Héctor Payeras Rubio
# TFG: Análisis de la estabilidad y variabilidad de las huellas digitales JA4 en distintos contextos
# Universidad Autónoma de Madrid - Escuela Politécnica Superior, 2026
#
# Descripción:
#   Procesa los JSON generados por el motor JA4, aplica criterios de limpieza y genera las bases de datos BASE_DATOS_PRUEBA_L.csv y BASE_DATOS_PRUEBA_W.csv.
#   Contiene una variable `ELEGIR` al inicio del script. Ponla a `0` para procesar las capturas de Windows y a `1` para las de Linux.

import pandas as pd
import glob
import os
import io
import re

# 0 para Windows, 1 para Linux
elegir = 1

def indexar_sin_redundancia(ruta_carpeta):
    todos_los_datos = []
    archivos = glob.glob(os.path.join(ruta_carpeta, "*.json"))
    
    print(f"Iniciando limpieza y procesado.")

    contador_exitos = 0

    for archivo in archivos:
        
        # if contador_exitos >= 1:
        #     break

        if os.path.getsize(archivo) < 1:
            continue

        nombre = os.path.basename(archivo)
        
        try:
            try:
                # Formato lista (Windows). Añadimos dtype=False para mantener el guion bajo en latencia
                df_temp = pd.read_json(archivo, dtype=False)
            except ValueError:
                try:
                    # Formato JSON en lineas estricto
                    df_temp = pd.read_json(archivo, lines=True, dtype=False)
                except ValueError:
                    # Formato Linux
                    with open(archivo, 'r', encoding='utf-8') as f:
                        texto = f.read().strip()
                    # Buscamos donde coinciden una llave de cierre con una de apertura y metemos una coma para separar objetos
                    texto_arreglado = '[' + re.sub(r'\}\s*\{', '},{', texto) + ']'
                    df_temp = pd.read_json(io.StringIO(texto_arreglado), dtype=False)
            
            if df_temp.empty:
                continue

            # Buscamos la columna principal de la huella del cliente (JA4.1) sin coger JA4_r, JA4_ro, JA4H ni JA4L
            cols_ja4 = [c for c in df_temp.columns if "JA4" in c and "JA4H" not in c and "JA4L" not in c and "JA4_" not in c]
            
            if not cols_ja4:
                continue
                
            # Usamos la primera que encuentre (JA4.1)
            col_principal = cols_ja4[0]
            
            # Extraemos el sufijo (ej. el ".1" de "JA4.1") para buscar sus hermanas (JA4_r.1, JA4_ro.1, JA4_o.1)
            sufijo = col_principal.replace("JA4", "")

            # Filtramos y limpiamos
            df_filtrado = df_temp.dropna(subset=[col_principal]).copy()
            
            if not df_filtrado.empty:
                
                # Identificador secuencial para cada captura, con W o L según el sistema operativo
                contador_exitos += 1
                letra_id = 'W' if elegir == 0 else 'L'
                
                # Extraemos la info del nombre
                if elegir == 0:
                    partes = nombre.replace('.json', '').split('_')
                elif elegir == 1:
                    partes = nombre.replace('.pcap.json', '').replace('.json', '').split('_')
                    
                nav, plat, web_obj, fecha, hora = partes[0], partes[1], partes[2], partes[3], partes[4].replace('-', ':')
                
                # Unificamos el dominio
                col_dominio = 'domain' if 'domain' in df_filtrado.columns else 'tls_server_name'
                if col_dominio in df_filtrado.columns:
                    df_filtrado['tls_server_name'] = df_filtrado[col_dominio]
                else:
                    df_filtrado['tls_server_name'] = 'Desconocido'
                
                # Una fila por cada combinacion de Huella y Dominio
                df_filtrado = df_filtrado.drop_duplicates(subset=[col_principal, 'tls_server_name'])
                
                # Lista identidicadora (Ej: 1_1W, 1_2W...)
                ids_filas = [f"{contador_exitos}_{i}{letra_id}" for i in range(1, len(df_filtrado) + 1)]
                
                # Guardamos nombres para el CSV final
                df_filtrado['id_captura'] = ids_filas
                df_filtrado['ja4'] = df_filtrado[col_principal]
                df_filtrado['navegador'] = nav  
                df_filtrado['plataforma'] = plat
                df_filtrado['web_buscada'] = web_obj
                df_filtrado['timestamp'] = f"{fecha} {hora}"
                
                mapa_columnas_extra = {
                    'JA4S': 'ja4s',
                    'JA4L-C': 'ja4l_cliente',
                    'JA4L-S': 'ja4l_servidor',
                    f'JA4_r{sufijo}': 'ja4_r',
                    f'JA4_ro{sufijo}': 'ja4_ro',
                    f'JA4_o{sufijo}': 'ja4_o'
                }

                # Revisamos si existen los argumentos extra en el JSON, si no, vacio
                for col_orig, col_nueva in mapa_columnas_extra.items():
                    if col_orig in df_filtrado.columns:
                        df_filtrado[col_nueva] = df_filtrado[col_orig]
                    else:
                        df_filtrado[col_nueva] = pd.NA
                
                todos_los_datos.append(df_filtrado)
                
                print(f"[Captura {contador_exitos}{letra_id}]: {nombre}")

        except Exception as e:
            print(f"Error en {nombre}: {e}")
            continue

    if todos_los_datos:
        df_master = pd.concat(todos_los_datos, ignore_index=True)
        
        columnas_utiles = [
            'id_captura',
            'navegador',
            'plataforma',
            'web_buscada',
            'timestamp', # Tiempo
            'tls_server_name', # Servidor TLS conectado
            'ja4', # Huella Cliente
            'ja4s', # Huella Servidor
            'ja4l_cliente', # Latencia Cliente
            'ja4l_servidor', # Latencia Servidor
            'ja4_o', # Huella Original (_o)
            'ja4_ro', # Huella Cruda-Original (_ro)
            'ja4_r' # Huella Cruda (_r)
        ]
        
        # Filtramos solo las columnas que existan en el resultado y aplicamos el orden
        existentes = [c for c in columnas_utiles if c in df_master.columns]
        df_final = df_master[existentes]
        
        if elegir == 0:
            df_final.to_csv('BASE_DATOS_PRUEBA_W.csv', index=False, sep=';')
            print(f"\nSe han guardado de Windows {len(df_final)} filas en: BASE_DATOS_PRUEBA_W.csv")
        elif elegir == 1:
            df_final.to_csv('BASE_DATOS_PRUEBA_L.csv', index=False, sep=';')
            print(f"\nSe han guardado de Linux {len(df_final)} filas en: BASE_DATOS_PRUEBA_L.csv")
            
    else:
        print("\nNo se encontraron huellas TLS validas (JA4.1) en ningun archivo.")

if elegir == 0:
    indexar_sin_redundancia('Capturas/salidasWindows')
elif elegir == 1:
    indexar_sin_redundancia('Capturas/salidasLinux')
    
    
# python3 ./generar_indices.py