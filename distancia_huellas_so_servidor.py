import pandas as pd
import Levenshtein
import os

def realizar_estudio_huellas_ja4s(ruta_csv, so_label):
    carpeta_salida = "estudio_huellas_srv"
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)

    if not os.path.exists(ruta_csv):
        print(f"Error: No se encontro {ruta_csv}")
        return

    df = pd.read_csv(ruta_csv, sep=';')
    records = df.to_dict('records')
    res = []

    print(f"--- PROCESANDO SIMILITUD JA4S (SERVIDOR) EN SO: {so_label} Y POR WEB ---")

    for i in range(len(records)):
        for j in range(i + 1, len(records)):
            r1, r2 = records[i], records[j]
            
            # Solo comparar si es la misma web buscada
            if r1['web_buscada'] == r2['web_buscada']:
                
                # Desglose de JA4S: t130200_1302_a56c5b993250
                # JA4S_a = [0], JA4S_b = [1], JA4S_c = [2]
                p1 = str(r1['ja4s']).split('_')
                p2 = str(r2['ja4s']).split('_')

                if len(p1) < 3 or len(p2) < 3:
                    continue

                # 1. JA4S_a: Levenshtein (Protocolo, TLS, ALPN)
                a1, a2 = p1[0], p2[0]
                dist_lev_a = Levenshtein.distance(a1, a2)
                sim_lev_a = 1 / (1 + dist_lev_a)

                # 2. JA4S_b: Cipher Suite elegido (Comparación exacta)
                b1, b2 = p1[1], p2[1]
                sim_cipher_b = 1.0 if b1 == b2 else 0.0

                # 3. JA4S_c: Hash de Extensiones (Comparación exacta / Efecto avalancha)
                c1, c2 = p1[2], p2[2]
                sim_hash_c = 1.0 if c1 == c2 else 0.0
                
                # Similitud Total Media del Servidor
                sim_conjunta_bc = (sim_cipher_b + sim_hash_c) / 2
                sim_total_media = (sim_lev_a + sim_conjunta_bc) / 2

                res.append({
                    'Web_Comun': r1['web_buscada'],
                    'ID_A': r1['id_captura'],
                    'ID_B': r2['id_captura'],
                    'JA4S_Identicas': (r1['ja4s'] == r2['ja4s']),
                    'Levenshtein_Dist_a': dist_lev_a,
                    'Igualdad_Cipher_b': sim_cipher_b,
                    'Igualdad_Hash_c': sim_hash_c,
                    'Similitud_Total_Media': round(sim_total_media, 4),
                    'JA4S_A': r1['ja4s'],
                    'JA4S_B': r2['ja4s']
                })

    if not res:
        print(f"No hay comparaciones de misma web en {so_label}.")
        return

    df_output = pd.DataFrame(res)

    # Ordenar N3: Web -> Identicas (True arriba)
    df_output = df_output.sort_values(by=['Web_Comun', 'JA4S_Identicas'], ascending=[True, False])

    ruta_save = os.path.join(carpeta_salida, f"DIST_JA4S_SRV_SO_{so_label}.csv")
    df_output.to_csv(ruta_save, sep=';', index=False)

    # Imprimir resumen por pantalla
    total = len(df_output)
    iguales = df_output['JA4S_Identicas'].sum()
    
    # Reflejamos el SO en los resultados finales por pantalla
    print("-" * 40) 
    print(f" RESULTADOS FINALES SERVIDOR (JA4S): {so_label}")
    print("-" * 40)
    print(f"Capturas comparadas (Misma Web):   {total}")
    print(f"JA4S idénticas (Misma respuesta):  {iguales}")
    print(f"JA4S diferentes:                   {total - iguales}")
    print("-" * 40)
    print(f"Promedio Dist. Levenshtein (a):    {df_output['Levenshtein_Dist_a'].mean():.4f}")
    print(f"Promedio Igualdad Cipher (b):      {df_output['Igualdad_Cipher_b'].mean():.4f}")
    print(f"Promedio Igualdad Hash Ext (c):    {df_output['Igualdad_Hash_c'].mean():.4f}")
    print(f"INDICE SIMILITUD TOTAL MEDIA SRV:  {df_output['Similitud_Total_Media'].mean():.4f}")
    print("-" * 40)
    print(f"Fichero generado: {ruta_save}\n")

if __name__ == "__main__":
    realizar_estudio_huellas_ja4s('BASE_DATOS_PRUEBA_L.csv', 'LINUX')
    realizar_estudio_huellas_ja4s('BASE_DATOS_PRUEBA_W.csv', 'WINDOWS')