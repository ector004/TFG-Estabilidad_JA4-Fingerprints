import pandas as pd
import Levenshtein
import os

def realizar_estudio_ja4s_por_dispositivo(archivos_dict):
    carpeta_salida = "estudio_huellas_srv"
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)

    # 1. Cargar y unificar todas las capturas (Linux + Windows)
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
    
    # Obtenemos las plataformas únicas (Desktop, Mobile)
    plataformas_unicas = df_total['plataforma'].unique()

    for plat in plataformas_unicas:
        print(f"--- PROCESANDO SIMILITUD JA4S (SERVIDOR) POR DISPOSITIVO: {plat.upper()} Y POR WEB ---")
        
        # Filtramos por el tipo de dispositivo
        df_plat = df_total[df_total['plataforma'] == plat].copy()
        records = df_plat.to_dict('records')
        res = []

        for i in range(len(records)):
            for j in range(i + 1, len(records)):
                r1, r2 = records[i], records[j]
                
                # Filtro: Misma Web (dentro de la misma plataforma)
                if r1['web_buscada'] == r2['web_buscada']:
                    
                    # Desglose de JA4S: t130200_1302_a56c5b993250
                    p1 = str(r1['ja4s']).split('_')
                    p2 = str(r2['ja4s']).split('_')

                    if len(p1) < 3 or len(p2) < 3:
                        continue

                    # 1. JA4S_a: Levenshtein (Estructura)
                    a1, a2 = p1[0], p2[0]
                    dist_lev_a = Levenshtein.distance(a1, a2)
                    sim_lev_a = 1 / (1 + dist_lev_a)

                    # 2. JA4S_b: Cipher Suite elegido (Binario)
                    b1, b2 = p1[1], p2[1]
                    sim_cipher_b = 1.0 if b1 == b2 else 0.0

                    # 3. JA4S_c: Hash de Extensiones (Binario)
                    c1, c2 = p1[2], p2[2]
                    sim_hash_c = 1.0 if c1 == c2 else 0.0
                    
                    # Similitud Total Media del Servidor
                    sim_conjunta_bc = (sim_cipher_b + sim_hash_c) / 2
                    sim_total_media = (sim_lev_a + sim_conjunta_bc) / 2

                    res.append({
                        'Web_Comun': r1['web_buscada'],
                        'JA4S_Identicas': (r1['ja4s'] == r2['ja4s']),
                        'SO_A': r1['SO_Origen'],
                        'SO_B': r2['SO_Origen'],
                        'ID_A': r1['id_captura'],
                        'ID_B': r2['id_captura'],
                        'Levenshtein_Dist_a': dist_lev_a,
                        'Igualdad_Cipher_b': sim_cipher_b,
                        'Igualdad_Hash_c': sim_hash_c,
                        'Similitud_Total_Media': round(sim_total_media, 4),
                        'JA4S_A': r1['ja4s'],
                        'JA4S_B': r2['ja4s']
                    })

        if res:
            df_output = pd.DataFrame(res)
            
            # ORDENACIÓN N3: 1. Web -> 2. Igualdad (True arriba) -> 3. SO_A
            df_output = df_output.sort_values(
                by=['Web_Comun', 'JA4S_Identicas', 'SO_A'], 
                ascending=[True, False, True]
            )

            nombre_fichero = f"DIST_JA4S_SRV_DISP_{plat.upper()}.csv"
            ruta_save = os.path.join(carpeta_salida, nombre_fichero)
            df_output.to_csv(ruta_save, sep=';', index=False)

            # Estadísticas por pantalla
            total = len(df_output)
            iguales = df_output['JA4S_Identicas'].sum()
            
            print("-" * 40)
            print(f" RESULTADOS FINALES JA4S: DISPOSITIVO {plat.upper()}")
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
    mis_archivos = {
        'LINUX': 'BASE_DATOS_PRUEBA_L.csv',
        'WINDOWS': 'BASE_DATOS_PRUEBA_W.csv'
    }
    realizar_estudio_ja4s_por_dispositivo(mis_archivos)