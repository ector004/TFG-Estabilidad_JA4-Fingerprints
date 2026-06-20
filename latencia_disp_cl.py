# Autor: Héctor Payeras Rubio
# TFG: Análisis de la estabilidad y variabilidad de las huellas digitales JA4 en distintos contextos
# Universidad Autónoma de Madrid - Escuela Politécnica Superior, 2026
#
# Descripción:
#   Calcula estadísticas de latencia y TTL del cliente agrupando por tipo de dispositivo.


import pandas as pd
import os

archivo_windows = 'BASE_DATOS_PRUEBA_W.csv'
archivo_linux = 'BASE_DATOS_PRUEBA_L.csv'

def generar_analisis_ja4l_cliente_dispositivo():
    nombre_carpeta = "Dispositivo"
    if not os.path.exists(nombre_carpeta):
        os.makedirs(nombre_carpeta)
        print(f"Carpeta '{nombre_carpeta}' creada.")

    print(f"--- ANALIZANDO ESTADISTICAS LATENCIA CLIENTE (JA4L) ---")
    try:
        # Cargamos columnas incluyendo plataforma (dispositivo)
        columnas = ['id_captura', 'navegador', 'plataforma', 'web_buscada', 'ja4l_cliente']
        df_w = pd.read_csv(archivo_windows, sep=';', dtype=str, usecols=columnas)
        df_l = pd.read_csv(archivo_linux, sep=';', dtype=str, usecols=columnas)
        
        df_total = pd.concat([df_w, df_l], ignore_index=True)
        df_total['web_buscada'] = df_total['web_buscada'].str.replace('www.', '', regex=False).str.strip().str.lower()
        df_total['plataforma'] = df_total['plataforma'].str.strip().str.upper()
        
        # Limpieza y separacion de JA4L (Retardo_TTL)
        df_total = df_total[df_total['ja4l_cliente'].notna() & (df_total['ja4l_cliente'].str.contains('_'))]
        df_total[['latencia', 'ttl']] = df_total['ja4l_cliente'].str.split('_', expand=True).astype(int)
        
    except Exception as e:
        print(f"Error: {e}")
        return

    # Analisis global por dispositivo
    global_disp = df_total.groupby('plataforma').agg({
        'latencia': ['mean', 'std', 'min', 'max'],
        'ttl': [lambda x: x.mode()[0], 'mean', 'std']
    })
    
    global_disp.columns = [
        'Latencia_Media', 'Latencia_Desv', 'Latencia_Min', 'Latencia_Max', 
        'TTL_Moda', 'TTL_Media', 'TTL_Desv'
    ]
    
    print("\n" + "="*95)
    print(f"{'ESTADISTICA GLOBAL POR DISPOSITIVO':^95}")
    print("="*95)
    print(global_disp.to_string())
    
    ruta_global = os.path.join(nombre_carpeta, 'CL_DISP_LATENCIA_GLOBAL.csv')
    global_disp.to_csv(ruta_global, sep=';')

    # Analisis por web y dispositivo
    resumen_web_disp = df_total.groupby(['web_buscada', 'plataforma']).agg({
        'latencia': ['mean', 'std', 'min', 'max'],
        'ttl': [lambda x: x.mode()[0], 'mean']
    }).reset_index()
    
    resumen_web_disp.columns = [
        'Web', 'Dispositivo', 'Latencia_Media', 'Latencia_Desv', 'Latencia_Min', 'Latencia_Max', 'TTL_Moda', 'TTL_Media'
    ]
    
    print("\n" + "="*95)
    print(f"{'RESUMEN POR WEB Y DISPOSITIVO (PRIMERAS 10 FILAS)':^95}")
    print("="*95)
    print(resumen_web_disp.head(10).to_string())
    
    ruta_web = os.path.join(nombre_carpeta, 'CL_DISP_LATENCIA_POR_WEB.csv')
    resumen_web_disp.to_csv(ruta_web, index=False, sep=';')
    
    print("\n" + "="*95)
    print(f"Archivos de latencia de cliente generados en la carpeta '{nombre_carpeta}':")
    print(f"1. Global Disp: {ruta_global}")
    print(f"2. Por Web y Disp: {ruta_web}")
    print("="*95)

if __name__ == "__main__":
    generar_analisis_ja4l_cliente_dispositivo()