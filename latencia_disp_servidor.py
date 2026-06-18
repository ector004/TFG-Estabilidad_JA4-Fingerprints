import pandas as pd
import os

# Archivos de entrada
archivo_windows = 'BASE_DATOS_PRUEBA_W.csv'
archivo_linux = 'BASE_DATOS_PRUEBA_L.csv'

def generar_analisis_ja4l_servidor_dispositivo():
    # Crear la carpeta Dispositivo si no existe para evitar errores
    nombre_carpeta = "Dispositivo"
    if not os.path.exists(nombre_carpeta):
        os.makedirs(nombre_carpeta)
        print(f"Carpeta '{nombre_carpeta}' creada.")

    print(f"--- ANALIZANDO ESTADISTICAS LATENCIA SERVIDOR (JA4L_S) ---")
    try:
        # Cargamos columnas incluyendo plataforma
        columnas = ['id_captura', 'web_buscada', 'ja4l_servidor', 'tls_server_name', 'plataforma']
        df_w = pd.read_csv(archivo_windows, sep=';', dtype=str, usecols=columnas)
        df_w['so_origen'] = 'WINDOWS'
        df_l = pd.read_csv(archivo_linux, sep=';', dtype=str, usecols=columnas)
        df_l['so_origen'] = 'LINUX'
        
        df_total = pd.concat([df_w, df_l], ignore_index=True)
        df_total['tls_server_name'] = df_total['tls_server_name'].str.strip().str.lower()
        df_total['web_buscada'] = df_total['web_buscada'].str.replace('www.', '', regex=False).str.strip().str.lower()
        df_total['plataforma'] = df_total['plataforma'].str.strip().str.upper()
        
        # Limpieza y separacion de JA4L_S (Retardo_TTL)
        df_total = df_total[df_total['ja4l_servidor'].notna() & (df_total['ja4l_servidor'].str.contains('_'))]
        df_total[['latencia', 'ttl']] = df_total['ja4l_servidor'].str.split('_', expand=True).astype(int)
        
    except Exception as e:
        print(f"Error: {e}")
        return

    # ANALISIS GLOBAL POR DISPOSITIVO (PLATAFORMA)
    global_disp = df_total.groupby('plataforma').agg({
        'latencia': ['mean', 'std', 'min', 'max'],
        'ttl': [lambda x: x.mode()[0], 'mean', 'std']
    })
    
    global_disp.columns = [
        'Latencia_Media', 'Latencia_Desv', 'Latencia_Min', 'Latencia_Max', 
        'TTL_Moda', 'TTL_Media', 'TTL_Desv'
    ]
    
    print("\n" + "="*95)
    print(f"{'ESTADISTICA GLOBAL SERVIDOR POR DISPOSITIVO':^95}")
    print("="*95)
    print(global_disp.to_string())
    
    # Guardar en carpeta Dispositivo
    ruta_global = os.path.join(nombre_carpeta, 'SV_DISP_LATENCIA_GLOBAL.csv')
    global_disp.to_csv(ruta_global, sep=';')

    # ANALISIS DETALLADO POR WEB Y DISPOSITIVO
    resumen_web_disp = df_total.groupby(['web_buscada', 'plataforma']).agg({
        'latencia': ['mean', 'std', 'min', 'max'],
        'ttl': [lambda x: x.mode()[0], 'mean']
    }).reset_index()
    
    resumen_web_disp.columns = [
        'Web', 'Dispositivo', 'Latencia_Media', 'Latencia_Desv', 'Latencia_Min', 'Latencia_Max', 'TTL_Moda', 'TTL_Media'
    ]
    
    print("\n" + "="*95)
    print(f"{'RESUMEN SERVIDOR POR WEB Y DISPOSITIVO (PRIMERAS 10 FILAS)':^95}")
    print("="*95)
    print(resumen_web_disp.head(10).to_string())
    
    # Guardar en carpeta Dispositivo
    ruta_web = os.path.join(nombre_carpeta, 'SV_DISP_LATENCIA_POR_WEB.csv')
    resumen_web_disp.to_csv(ruta_web, index=False, sep=';')

    # ANALISIS DETALLADO POR SNI Y DISPOSITIVO
    resumen_sni_disp = df_total.groupby(['tls_server_name', 'plataforma']).agg({
        'latencia': ['mean', 'std', 'min', 'max'],
        'ttl': [lambda x: x.mode()[0], 'mean']
    }).reset_index()
    
    resumen_sni_disp.columns = [
        'SNI', 'Dispositivo', 'Latencia_Media', 'Latencia_Desv', 'Latencia_Min', 'Latencia_Max', 'TTL_Moda', 'TTL_Media'
    ]
    
    # Guardar en carpeta Dispositivo
    ruta_detalle = os.path.join(nombre_carpeta, 'SV_DISP_LATENCIA_POR_SNI.csv')
    resumen_sni_disp.to_csv(ruta_detalle, index=False, sep=';')
    
    print("\n" + "="*95)
    print(f"Archivos de latencia de servidor generados en la carpeta '{nombre_carpeta}':")
    print(f"1. Global Disp: {ruta_global}")
    print(f"2. Por Web y Disp: {ruta_web}")
    print(f"3. Por SNI y Disp: {ruta_detalle}")
    print("="*95)

if __name__ == "__main__":
    generar_analisis_ja4l_servidor_dispositivo()