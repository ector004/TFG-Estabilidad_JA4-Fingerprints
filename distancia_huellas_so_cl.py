# Autor: Héctor Payeras Rubio
# TFG: Análisis de la estabilidad y variabilidad de las huellas digitales JA4 en distintos contextos
# Universidad Autónoma de Madrid - Escuela Politécnica Superior, 2026
#
# Descripción:
#   Calcula la similitud de huellas JA4 del cliente agrupando por sistema operativo mediante la distancia de Levenshtein normalizada
#   y el coeficiente de Jaccard sobre las listas en crudo de cipher suites y extensiones.

import pandas as pd
import Levenshtein
import os

def calcular_jaccard_detallado(raw_ro_1, raw_ro_2):
    try:
        p1 = str(raw_ro_1).split('_')
        p2 = str(raw_ro_2).split('_')
        
        # Bloque 1-> Ciphers, Bloque 2-> Extensions
        c1 = set(p1[1].split(',')) if len(p1) > 1 else set()
        c2 = set(p2[1].split(',')) if len(p2) > 1 else set()
        
        e1 = set(p1[2].split(',')) if len(p1) > 2 else set()
        e2 = set(p2[2].split(',')) if len(p2) > 2 else set()

        def jaccard(set_a, set_b):
            union = len(set_a.union(set_b))
            return len(set_a.intersection(set_b)) / union if union > 0 else 0.0

        return jaccard(c1, c2), jaccard(e1, e2)
    except:
        return 0.0, 0.0

def realizar_estudio_huellas_hibrido(ruta_csv, so_label):
    carpeta_salida = "estudio_huellas_cl"
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)

    if not os.path.exists(ruta_csv):
        print(f"Error: No se encontro {ruta_csv}")
        return

    df = pd.read_csv(ruta_csv, sep=';')
    records = df.to_dict('records')
    res = []

    print(f"--- PROCESANDO SIMILITUD DE HUELLAS DE CL POR {so_label} Y POR WEB ---")

    for i in range(len(records)):
        for j in range(i + 1, len(records)):
            r1, r2 = records[i], records[j]
            
            # Comparar si es la misma web
            if r1['web_buscada'] == r2['web_buscada']:
                # Levenshtein sobre prefijo JA4_a
                a1 = str(r1['ja4']).split('_')[0]
                a2 = str(r2['ja4']).split('_')[0]
                dist_lev = Levenshtein.distance(a1, a2)
                sim_lev = 1 / (1 + dist_lev)

                # Jaccard sobre ja4_ro
                j_ciph, j_ext = calcular_jaccard_detallado(r1['ja4_ro'], r2['ja4_ro'])
                sim_jaccard_conjunta = (j_ciph + j_ext) / 2
                
                # Similitud Total Media
                sim_total_media = (sim_lev + sim_jaccard_conjunta) / 2

                res.append({
                    'Web_Comun': r1['web_buscada'],
                    'ID_A': r1['id_captura'],
                    'ID_B': r2['id_captura'],
                    'JA4_Identicas': (r1['ja4'] == r2['ja4']),
                    'Levenshtein_Dist_a': dist_lev,
                    'Jaccard_Ciphers': round(j_ciph, 4),
                    'Jaccard_Extensions': round(j_ext, 4),
                    'Similitud_Jaccard_Conjunta': round(sim_jaccard_conjunta, 4),
                    'Similitud_Total_Media': round(sim_total_media, 4),
                    'JA4_A': r1['ja4'],
                    'JA4_B': r2['ja4']
                })

    if not res:
        print(f"No hay comparaciones de misma web en {so_label}.")
        return

    df_output = pd.DataFrame(res)

    # ORDENACIÓN: 1. Web -> 2. Igualdad (True arriba) -> 3. SO_A
    df_output = df_output.sort_values(by=['Web_Comun', 'JA4_Identicas'], ascending=[True, False])

    ruta_save = os.path.join(carpeta_salida, f"DIST_HUELLAS_CL_SO_{so_label}.csv")
    df_output.to_csv(ruta_save, sep=';', index=False)

    total = len(df_output)
    iguales = df_output['JA4_Identicas'].sum()
    
    print("-" * 40)
    print(f" RESULTADOS FINALES: {so_label}")
    print("-" * 40)
    print(f"Capturas comparadas (Misma Web):   {total}")
    print(f"Huellas identicas (Colisiones):    {iguales}")
    print(f"Huellas diferentes:                {total - iguales}")
    print("-" * 40)
    print(f"Promedio Dist. Levenshtein (a):    {df_output['Levenshtein_Dist_a'].mean():.4f}")
    print(f"Promedio Sim. Jaccard Ciphers:     {df_output['Jaccard_Ciphers'].mean():.4f}")
    print(f"Promedio Sim. Jaccard Extensions:  {df_output['Jaccard_Extensions'].mean():.4f}")
    print(f"Promedio Similitud Conjunta:       {df_output['Similitud_Jaccard_Conjunta'].mean():.4f}")
    print(f"INDICE SIMILITUD TOTAL MEDIA:      {df_output['Similitud_Total_Media'].mean():.4f}")
    print("-" * 40)
    print(f"Fichero generado: {ruta_save}\n")

if __name__ == "__main__":
    realizar_estudio_huellas_hibrido('BASE_DATOS_PRUEBA_L.csv', 'LINUX')
    realizar_estudio_huellas_hibrido('BASE_DATOS_PRUEBA_W.csv', 'WINDOWS')