import pandas as pd
import os

# Archivos de entrada
archivo_windows = 'BASE_DATOS_PRUEBA_W.csv'
archivo_linux = 'BASE_DATOS_PRUEBA_L.csv'

def generar_analisis_ja4l_cliente_navegador():
    # Crear la carpeta Navegador si no existe para evitar errores
    nombre_carpeta = "Navegador"
    if not os.path.exists(nombre_carpeta):
        os.makedirs(nombre_carpeta)
        print(f"Carpeta '{nombre_carpeta}' creada.")

    print(f"--- ANALIZANDO ESTADISTICAS LATENCIA CLIENTE (JA4L) ---")
    try:
        # Cargamos columnas incluyendo navegador
        columnas = ['id_captura', 'navegador', 'plataforma', 'web_buscada', 'ja4l_cliente']
        df_w = pd.read_csv(archivo_windows, sep=';', dtype=str, usecols=columnas)
        df_l = pd.read_csv(archivo_linux, sep=';', dtype=str, usecols=columnas)
        
        df_total = pd.concat([df_w, df_l], ignore_index=True)
        df_total['web_buscada'] = df_total['web_buscada'].str.replace('www.', '', regex=False).str.strip().str.lower()
        df_total['navegador'] = df_total['navegador'].str.strip().str.upper()
        
        # Limpieza y separacion de JA4L (Retardo_TTL)
        df_total = df_total[df_total['ja4l_cliente'].notna() & (df_total['ja4l_cliente'].str.contains('_'))]
        df_total[['latencia', 'ttl']] = df_total['ja4l_cliente'].str.split('_', expand=True).astype(int)
        
    except Exception as e:
        print(f"Error: {e}")
        return

    # ANALISIS GLOBAL POR NAVEGADOR
    global_nav = df_total.groupby('navegador').agg({
        'latencia': ['mean', 'std', 'min', 'max'],
        'ttl': [lambda x: x.mode()[0], 'mean', 'std']
    })
    
    global_nav.columns = [
        'Latencia_Media', 'Latencia_Desv', 'Latencia_Min', 'Latencia_Max', 
        'TTL_Moda', 'TTL_Media', 'TTL_Desv'
    ]
    
    print("\n" + "="*95)
    print(f"{'ESTADISTICA GLOBAL POR NAVEGADOR':^95}")
    print("="*95)
    print(global_nav.to_string())
    
    # Guardar en carpeta Navegador
    ruta_global = os.path.join(nombre_carpeta, 'CL_NAV_LATENCIA_GLOBAL.csv')
    global_nav.to_csv(ruta_global, sep=';')

    # ANALISIS DETALLADO POR WEB Y NAVEGADOR
    resumen_web_nav = df_total.groupby(['web_buscada', 'navegador']).agg({
        'latencia': ['mean', 'std', 'min', 'max'],
        'ttl': [lambda x: x.mode()[0], 'mean']
    }).reset_index()
    
    resumen_web_nav.columns = [
        'Web', 'Navegador', 'Latencia_Media', 'Latencia_Desv', 'Latencia_Min', 'Latencia_Max', 'TTL_Moda', 'TTL_Media'
    ]
    
    print("\n" + "="*95)
    print(f"{'RESUMEN POR WEB Y NAVEGADOR (PRIMERAS 10 FILAS)':^95}")
    print("="*95)
    print(resumen_web_nav.head(10).to_string())
    
    # Guardar en carpeta Navegador
    ruta_web = os.path.join(nombre_carpeta, 'CL_NAV_LATENCIA_POR_WEB.csv')
    resumen_web_nav.to_csv(ruta_web, index=False, sep=';')
    
    print("\n" + "="*95)
    print(f"Archivos de latencia de cliente generados en la carpeta '{nombre_carpeta}':")
    print(f"1. Global Nav: {ruta_global}")
    print(f"2. Por Web y Nav: {ruta_web}")
    print("="*95)

if __name__ == "__main__":
    generar_analisis_ja4l_cliente_navegador()