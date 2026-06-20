# Autor: Héctor Payeras Rubio
# TFG: Análisis de la estabilidad y variabilidad de las huellas digitales JA4 en distintos contextos
# Universidad Autónoma de Madrid - Escuela Politécnica Superior, 2026
#
# Descripción:
#   Calcula la tasa de colisión exacta entre huellas JA4 del cliente, determinando qué proporción de pares de capturas del mismo dominio producen huellas idénticas.


import pandas as pd
import itertools

# Archivos de entrada
archivo_windows = 'BASE_DATOS_PRUEBA_W.csv'
archivo_linux = 'BASE_DATOS_PRUEBA_L.csv'
archivo_salida = 'RESULTADO_JA4_COMPARACION_FINAL.csv'

def generar_analisis_tfg_completo():
    print(f"--- INICIANDO COMPARACION DE HUELLAS JA4 (W y L) ---")
    try:
        # Añadimos 'tls_server_name' a las columnas a leer
        columnas = ['id_captura', 'navegador', 'plataforma', 'web_buscada', 'ja4', 'tls_server_name']
        
        # Carga y etiqueta de SO
        df_w = pd.read_csv(archivo_windows, sep=';', dtype=str, usecols=columnas)
        df_w['so_real'] = 'WINDOWS'
        
        df_l = pd.read_csv(archivo_linux, sep=';', dtype=str, usecols=columnas)
        df_l['so_real'] = 'LINUX'
        
        # Union y limpieza de webs
        df_total = pd.concat([df_w, df_l], ignore_index=True)
        df_total['web_buscada'] = df_total['web_buscada'].str.replace('www.', '', regex=False).str.strip().str.lower()
        df_total = df_total[df_total['ja4'].notna()]
        
    except Exception as e:
        print(f"Error al leer archivos: {e}")
        return

    resultados = []
    grupos = df_total.groupby('web_buscada')

    for web, datos_web in grupos:
        if len(datos_web) < 2: continue
        filas = datos_web.to_dict('records')
        
        for f1, f2 in itertools.combinations(filas, 2):
            # No se comparar con si mismo
            if f1['id_captura'] == f2['id_captura']: continue
                
            # Logica de comparacion de los 3 argumentos
            mismo_so = f1['so_real'] == f2['so_real']
            mismo_disp = f1['plataforma'] == f2['plataforma']
            mismo_nav = f1['navegador'] == f2['navegador']
            
            # Construccion de la etiqueta Sistema-Dispositivo-Navegador
            s_p = "MS" if mismo_so else "DS"
            d_p = "MD" if mismo_disp else "DD"
            n_p = "MN" if mismo_nav else "DN"
            etiqueta = f"{s_p}{d_p}{n_p}"
            
            # Comparacion de huella JA4
            son_identicos = (f1['ja4'] == f2['ja4'])
            res_str = "IGUALES" if son_identicos else "DIFERENTES"
            
            resultados.append({
                'web': web,
                'etiqueta_comparativa': etiqueta,
                'resultado': res_str,
                'id_1': f1['id_captura'],
                'so_1': f1['so_real'],
                'plat_1': f1['plataforma'],
                'nav_1': f1['navegador'],
                'tls_1': f1['tls_server_name'],
                'ja4_1': f1['ja4'],
                'id_2': f2['id_captura'],
                'so_2': f2['so_real'],
                'plat_2': f2['plataforma'],
                'nav_2': f2['navegador'],
                'tls_2': f2['tls_server_name'],
                'ja4_2': f2['ja4']
            })

    if resultados:
        df_final = pd.DataFrame(resultados)
        orden_etiquetas = ["MSMDMN", "MSMDDN", "MSDDMN", "MSDDDN", "DSMDMN", "DSMDDN", "DSDDMN", "DSDDDN"]
        df_final['etiqueta_comparativa'] = pd.Categorical(df_final['etiqueta_comparativa'], categories=orden_etiquetas, ordered=True)
        
        df_final = df_final.sort_values(by=['etiqueta_comparativa', 'resultado', 'web'], ascending=[True, False, True])
        df_final.to_csv(archivo_salida, index=False, sep=';')
        
        # Calculo de estadisticas
        stats = df_final.groupby(['etiqueta_comparativa', 'resultado'], observed=False).size().unstack(fill_value=0)
        
        if 'IGUALES' not in stats: stats['IGUALES'] = 0
        if 'DIFERENTES' not in stats: stats['DIFERENTES'] = 0

        print("\n" + "="*80)
        print(f"{'RESUMEN DE COMPARACION DE HUELLAS JA4':^80}")
        print("="*80)
        print(f"{'ETIQUETA':<12} | {'IGUALES':<12} | {'DIFERENTES':<12} | {'TOTAL':<10} | {'% IGUALDAD':<12}")
        print("-" * 80)
        
        for etiqueta in orden_etiquetas:
            i, d = stats.loc[etiqueta, 'IGUALES'], stats.loc[etiqueta, 'DIFERENTES']
            total = i + d
            porc = (i / total * 100) if total > 0 else 0
            print(f"{etiqueta:<12} | {i:<12} | {d:<12} | {total:<10} | {porc:>10.2f}%")

        print("-" * 80)
        t_i, t_d = stats['IGUALES'].sum(), stats['DIFERENTES'].sum()
        print(f"{'TOTALES':<12} | {t_i:<12} | {t_d:<12} | {t_i+t_d:<10} | {(t_i/(t_i+t_d)*100):>10.2f}%")
        print("="*80)
        print(f"Archivo generado en {archivo_salida}\n")
    else:
        print("Error: No se pudieron cruzar los datos de Windows y Linux.")

if __name__ == "__main__":
    generar_analisis_tfg_completo()