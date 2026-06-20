# Autor: Héctor Payeras Rubio
# TFG: Análisis de la estabilidad y variabilidad de las huellas digitales JA4 en distintos contextos
# Universidad Autónoma de Madrid - Escuela Politécnica Superior, 2026
#
# Descripción:
#   Calcula estadísticas de latencia y TTL del servidor agrupando por navegador.


import pandas as pd
import os

archivo_windows = 'BASE_DATOS_PRUEBA_W.csv'
archivo_linux = 'BASE_DATOS_PRUEBA_L.csv'

def generar_analisis_ja4l_servidor_navegador():
    nombre_carpeta = "Navegador"
    if not os.path.exists(nombre_carpeta):
        os.makedirs(nombre_carpeta)
        print(f"Carpeta '{nombre_carpeta}' creada.")

    print(f"--- ANALIZANDO ESTADISTICAS LATENCIA SERVIDOR (JA4L_S) ---")
    try:
        # Cargamos columnas incluyendo navegador
        columnas = ['id_captura', 'web_buscada', 'ja4l_servidor', 'tls_server_name', 'navegador']
        df_w = pd.read_csv(archivo_windows, sep=';', dtype=str, usecols=columnas)
        df_l = pd.read_csv(archivo_linux, sep=';', dtype=str, usecols=columnas)
        
        df_total = pd.concat([df_w, df_l], ignore_index=True)
        df_total['tls_server_name'] = df_total['tls_server_name'].str.strip().str.lower()
        df_total['web_buscada'] = df_total['web_buscada'].str.replace('www.', '', regex=False).str.strip().str.lower()
        df_total['navegador'] = df_total['navegador'].str.strip().str.upper()
        
        # Limpieza y separacion de JA4L_S (Retardo_TTL)
        df_total = df_total[df_total['ja4l_servidor'].notna() & (df_total['ja4l_servidor'].str.contains('_'))]
        df_total[['latencia', 'ttl']] = df_total['ja4l_servidor'].str.split('_', expand=True).astype(int)
        
    except Exception as e:
        print(f"Error: {e}")
        return

    # Analisis global por navegador
    global_nav = df_total.groupby('navegador').agg({
        'latencia': ['mean', 'std', 'min', 'max'],
        'ttl': [lambda x: x.mode()[0], 'mean', 'std']
    })
    
    global_nav.columns = [
        'Latencia_Media', 'Latencia_Desv', 'Latencia_Min', 'Latencia_Max', 
        'TTL_Moda', 'TTL_Media', 'TTL_Desv'
    ]
    
    print("\n" + "="*95)
    print(f"{'ESTADISTICA GLOBAL SERVIDOR POR NAVEGADOR':^95}")
    print("="*95)
    print(global_nav.to_string())
    
    ruta_global = os.path.join(nombre_carpeta, 'SV_NAV_LATENCIA_GLOBAL.csv')
    global_nav.to_csv(ruta_global, sep=';')

    # Analisis por web y navegador
    resumen_web_nav = df_total.groupby(['web_buscada', 'navegador']).agg({
        'latencia': ['mean', 'std', 'min', 'max'],
        'ttl': [lambda x: x.mode()[0], 'mean']
    }).reset_index()
    
    resumen_web_nav.columns = [
        'Web', 'Navegador', 'Latencia_Media', 'Latencia_Desv', 'Latencia_Min', 'Latencia_Max', 'TTL_Moda', 'TTL_Media'
    ]
    
    print("\n" + "="*95)
    print(f"{'RESUMEN SERVIDOR POR WEB Y NAVEGADOR (PRIMERAS 10 FILAS)':^95}")
    print("="*95)
    print(resumen_web_nav.head(10).to_string())
    
    ruta_web = os.path.join(nombre_carpeta, 'SV_NAV_LATENCIA_POR_WEB.csv')
    resumen_web_nav.to_csv(ruta_web, index=False, sep=';')

    # Analisis por SNI y navegador
    resumen_sni_nav = df_total.groupby(['tls_server_name', 'navegador']).agg({
        'latencia': ['mean', 'std', 'min', 'max'],
        'ttl': [lambda x: x.mode()[0], 'mean']
    }).reset_index()
    
    resumen_sni_nav.columns = [
        'SNI', 'Navegador', 'Latencia_Media', 'Latencia_Desv', 'Latencia_Min', 'Latencia_Max', 'TTL_Moda', 'TTL_Media'
    ]
    
    ruta_detalle = os.path.join(nombre_carpeta, 'SV_NAV_LATENCIA_POR_SNI.csv')
    resumen_sni_nav.to_csv(ruta_detalle, index=False, sep=';')
    
    print("\n" + "="*95)
    print(f"Archivos de latencia de servidor generados en la carpeta '{nombre_carpeta}':")
    print(f"1. Global Nav: {ruta_global}")
    print(f"2. Por Web y Nav: {ruta_web}")
    print(f"3. Por SNI y Nav: {ruta_detalle}")
    print("="*95)

if __name__ == "__main__":
    generar_analisis_ja4l_servidor_navegador()