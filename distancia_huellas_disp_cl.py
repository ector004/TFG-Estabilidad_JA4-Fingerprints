# Autor: Héctor Payeras Rubio
# TFG: Análisis de la estabilidad y variabilidad de las huellas digitales JA4 en distintos contextos
# Universidad Autónoma de Madrid - Escuela Politécnica Superior, 2026
#
# Descripción:
#   Calcula la similitud de huellas JA4 del cliente agrupando por tipo de dispositivo.


import pandas as pd
import Levenshtein
import os

def calcular_jaccard_detallado(raw_ro_1, raw_ro_2):
    try:
        p1 = str(raw_ro_1).split('_')
        p2 = str(raw_ro_2).split('_')
        
        # Bloque 1 -> Ciphers, Bloque 2-> Extensions
        c1 = set(p1[1].split(',')) if len(p1) > 1 else set()
        c2 = set(p2[1].split(',')) if len(p2) > 1 else set()
        
        e1 = set(p1[2].split(',')) if len(p1) > 2 else set()
        e2 = set(p2[2].split(',')) if len(p2) > 2 else set()

        def jaccard(set_a, set_b):
            union = len(set_a.union(set_b))
            return len(set_a.intersection(set_b)) / union if union > 0 else 0.0

        j_ciph, j_ext = jaccard(c1, c2), jaccard(e1, e2)
        return j_ciph, j_ext
    except:
        return 0.0, 0.0

def realizar_estudio_unificado_por_dispositivo(archivos_dict):
    carpeta_salida = "estudio_huellas_cl"
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)

    # Cargar y unificar las capturas (Linux + Windows)
    lista_df = []
    for so_nombre, ruta in archivos_dict.items():
        if os.path.exists(ruta):
            temp_df = pd.read_csv(ruta, sep=';')
            temp_df['SO_Origen'] = so_nombre
            lista_df.append(temp_df)
    
    if not lista_df:
        print("Error: No se encontraron los archivos base.")
        return

    df_total = pd.concat(lista_df, ignore_index=True)
    
    # Obtenemos las plataformas (PC/Desktop, Móvil, etc.)
    plataformas_unicas = df_total['plataforma'].unique()

    for plat in plataformas_unicas:
        print(f"--- PROCESANDO SIMILITUD DE HUELLAS POR DISPOSITIVO ({plat.upper()}) Y POR WEB ---")
        
        # Filtramos por la plataforma actual
        df_plat = df_total[df_total['plataforma'] == plat].copy()
        records = df_plat.to_dict('records')
        res = []

        for i in range(len(records)):
            for j in range(i + 1, len(records)):
                r1, r2 = records[i], records[j]
                
                # Filtro: Misma Web (ya estamos dentro del mismo dispositivo)
                if r1['web_buscada'] == r2['web_buscada']:
                    
                    # Levenshtein sobre JA4_a
                    a1, a2 = str(r1['ja4']).split('_')[0], str(r2['ja4']).split('_')[0]
                    dist_lev = Levenshtein.distance(a1, a2)
                    sim_lev = 1 / (1 + dist_lev)

                    # Jaccard sobre datos raw
                    j_ciph, j_ext = calcular_jaccard_detallado(r1['ja4_ro'], r2['ja4_ro'])
                    sim_jacc_conjunta = (j_ciph + j_ext) / 2
                    
                    # Similitud Total
                    sim_total_media = (sim_lev + sim_jacc_conjunta) / 2

                    res.append({
                        'Web_Comun': r1['web_buscada'],
                        'JA4_Identicas': (r1['ja4'] == r2['ja4']),
                        'SO_A': r1['SO_Origen'],
                        'SO_B': r2['SO_Origen'],
                        'ID_A': r1['id_captura'],
                        'ID_B': r2['id_captura'],
                        'Levenshtein_Dist_a': dist_lev,
                        'Jaccard_Ciphers': round(j_ciph, 4),
                        'Jaccard_Extensions': round(j_ext, 4),
                        'Similitud_Jaccard_Conjunta': round(sim_jacc_conjunta, 4),
                        'Similitud_Total_Media': round(sim_total_media, 4),
                        'JA4_A': r1['ja4'],
                        'JA4_B': r2['ja4']
                    })

        if res:
            df_output = pd.DataFrame(res)
            
            # ORDENACIÓN: 1. Web -> 2. Igualdad (True arriba) -> 3. SO_A
            df_output = df_output.sort_values(
                by=['Web_Comun', 'JA4_Identicas', 'SO_A'], 
                ascending=[True, False, True]
            )

            # Nombre de fichero según dispositivo
            nombre_fichero = f"DIST_HUELLAS_CL_DISP_{plat.upper()}.csv"
            ruta_save = os.path.join(carpeta_salida, nombre_fichero)
            df_output.to_csv(ruta_save, sep=';', index=False)

            # Imprimir Resumen por pantalla
            total = len(df_output)
            iguales = df_output['JA4_Identicas'].sum()
            diferentes = total - iguales
            
            print("-" * 40)
            print(f" RESULTADOS FINALES: DISPOSITIVO {plat.upper()}")
            print("-" * 40)
            print(f"Capturas comparadas (Misma Web):   {total}")
            print(f"Huellas identicas (Colisiones):    {iguales}")
            print(f"Huellas diferentes:                {diferentes}")
            print("-" * 40)
            print(f"Promedio Dist. Levenshtein (a):    {df_output['Levenshtein_Dist_a'].mean():.4f}")
            print(f"Promedio Sim. Jaccard Ciphers:     {df_output['Jaccard_Ciphers'].mean():.4f}")
            print(f"Promedio Sim. Jaccard Extensions:  {df_output['Jaccard_Extensions'].mean():.4f}")
            print(f"Promedio Similitud Conjunta:       {df_output['Similitud_Jaccard_Conjunta'].mean():.4f}")
            print(f"INDICE SIMILITUD TOTAL MEDIA:      {df_output['Similitud_Total_Media'].mean():.4f}")
            print("-" * 40)
            print(f"Fichero generado: {ruta_save}\n")

if __name__ == "__main__":
    mis_archivos = {
        'LINUX': 'BASE_DATOS_PRUEBA_L.csv',
        'WINDOWS': 'BASE_DATOS_PRUEBA_W.csv'
    }
    realizar_estudio_unificado_por_dispositivo(mis_archivos)