# Autor: Héctor Payeras Rubio
# TFG: Análisis de la estabilidad y variabilidad de las huellas digitales JA4 en distintos contextos
# Universidad Autónoma de Madrid - Escuela Politécnica Superior, 2026
#
# Descripción:
#   Analiza la distribución de frecuencias de cipher suites y hash de extensiones elegidos por el servidor
#   agrupando por sistema operativo, navegador y tipo de dispositivo.

import pandas as pd
import os

def realizar_estudio_cipher_avanzado_csv(archivos_dict):
    # Unificar datos
    lista_df = []
    for so, ruta in archivos_dict.items():
        if os.path.exists(ruta):
            df = pd.read_csv(ruta, sep=';')
            df['so_origen'] = so
            lista_df.append(df)
    
    if not lista_df:
        print("Error: No se encontraron archivos.")
        return

    df_total = pd.concat(lista_df, ignore_index=True)

    # JA4S (t130200_1302_hash) -> Cipher Sección B índice [1], Hash Extensiones Sección C índice [2]
    df_total['cipher_elegido'] = df_total['ja4s'].apply(
        lambda x: str(x).split('_')[1] if len(str(x).split('_')) > 1 else "N/A"
    )
    df_total['seccion_c_hash'] = df_total['ja4s'].apply(
        lambda x: str(x).split('_')[2] if len(str(x).split('_')) > 2 else "N/A"
    )

    resultados_csv = []

    def recolectar_avanzado(df_sub, categoria, valor):
        # Cipher (Sección B)
        counts_b = df_sub['cipher_elegido'].value_counts()
        top1_b = counts_b.index[0] if len(counts_b) > 0 else "N/A"
        top1_b_perc = (counts_b.iloc[0] / len(df_sub)) * 100 if len(counts_b) > 0 else 0
        
        top2_b = counts_b.index[1] if len(counts_b) > 1 else "N/A"
        top2_b_perc = (counts_b.iloc[1] / len(df_sub)) * 100 if len(counts_b) > 1 else 0
        
        # Hash Extensiones (Sección C)
        counts_c = df_sub['seccion_c_hash'].value_counts()
        top1_c = counts_c.index[0] if len(counts_c) > 0 else "N/A"
        top1_c_perc = (counts_c.iloc[0] / len(df_sub)) * 100 if len(counts_c) > 0 else 0

        resultados_csv.append({
            'Agrupacion': categoria,
            'Valor': valor,
            'Num_Ciphers_Dist': len(counts_b),
            'Top1_Cipher': top1_b,
            'Top1_Cipher_%': round(top1_b_perc, 2),
            'Top2_Cipher': top2_b,
            'Top2_Cipher_%': round(top2_b_perc, 2),
            'Top1_Hash_Sec_C': top1_c,
            'Top1_Hash_Sec_C_%': round(top1_c_perc, 2)
        })

    for so in df_total['so_origen'].unique():
        recolectar_avanzado(df_total[df_total['so_origen'] == so], 'SO', so)

    for nav in df_total['navegador'].unique():
        recolectar_avanzado(df_total[df_total['navegador'] == nav], 'Navegador', nav)

    for plat in df_total['plataforma'].unique():
        recolectar_avanzado(df_total[df_total['plataforma'] == plat], 'Dispositivo', plat)

    df_final = pd.DataFrame(resultados_csv)
    nombre_archivo = "ESTUDIO_CIPHER_SRV.csv"
    df_final.to_csv(nombre_archivo, sep=';', index=False)
    
    print(f"\n--- ESTUDIO FINALIZADO DEL CIPHER DE LOS SERVIDORES: {nombre_archivo} ---")
    print(df_final.to_string(index=False))

if __name__ == "__main__":
    mis_archivos = {
        'LINUX': 'BASE_DATOS_PRUEBA_L.csv',
        'WINDOWS': 'BASE_DATOS_PRUEBA_W.csv'
    }
    realizar_estudio_cipher_avanzado_csv(mis_archivos)