import pandas as pd
import os

# Archivos de entrada
archivo_windows = 'BASE_DATOS_PRUEBA_W.csv'
archivo_linux = 'BASE_DATOS_PRUEBA_L.csv'

def clasificar_so_servidor(ttl):
    if ttl <= 64:
        return 'Servidor_Linux'
    elif ttl <= 128:
        return 'Servidor_Windows'
    else:
        return 'Servidor_Otro'

def analizar_cruce_so():
    print(f"--- ANALIZANDO: ¿QUIÉN ME RESPONDE SEGÚN MI SO? ---")
    try:
        # Carga de datos
        df_w = pd.read_csv(archivo_windows, sep=';', dtype=str)
        df_w['SO_CLIENTE'] = 'Windows'
        
        df_l = pd.read_csv(archivo_linux, sep=';', dtype=str)
        df_l['SO_CLIENTE'] = 'Linux'
        
        df_total = pd.concat([df_w, df_l], ignore_index=True)
        df_total.columns = df_total.columns.str.strip().str.lower()
        
        # Limpieza y procesamiento
        df_total = df_total[df_total['ja4l_servidor'].notna() & (df_total['ja4l_servidor'].str.contains('_'))]
        df_total['ttl_srv'] = df_total['ja4l_servidor'].str.split('_').str[1].astype(int)
        df_total['so_servidor'] = df_total['ttl_srv'].apply(clasificar_so_servidor)
        df_total['navegador'] = df_total['navegador'].str.strip().str.upper()
        
        # 1. Crear la tabla pivote (Cruce)
        tabla_cruce = df_total.groupby(['so_cliente', 'navegador', 'so_servidor']).size().unstack(fill_value=0)
        
        # 2. MOSTRAR POR TERMINAL (Mantenemos el formato visual)
        print("\n" + "="*80)
        print(f"{'RESULTADO: TU SO -> NAVEGADOR -> SO QUE RESPONDE':^80}")
        print("="*80)
        print(tabla_cruce.to_string())
        print("="*80)
        
        # 3. PREPARAR PARA GUARDAR (Aplanamos los índices para que el CSV sea perfecto)
        # reset_index() convierte 'so_cliente' y 'navegador' en columnas normales.
        df_salida = tabla_cruce.reset_index()
        
        # Opcional: Eliminar el nombre de la jerarquía de columnas para un CSV más limpio
        df_salida.columns.name = None 
        
        if not os.path.exists('Navegador'): 
            os.makedirs('Navegador')
            
        ruta_csv = 'Navegador/ESTUDIO_CRUCE_SO.csv'
        df_salida.to_csv(ruta_csv, sep=';', index=False) # index=False porque ya hicimos reset_index
        
        print(f"\nArchivo corregido y guardado en: {ruta_csv}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analizar_cruce_so()