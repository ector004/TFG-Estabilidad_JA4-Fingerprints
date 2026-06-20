# Autor: Héctor Payeras Rubio
# TFG: Análisis de la estabilidad y variabilidad de las huellas digitales JA4 en distintos contextos
# Universidad Autónoma de Madrid - Escuela Politécnica Superior, 2026
#
# Descripción:
#   Genera las gráficas comparativas globales de latencia del cliente y del servidor a partir de LATENCIA_GENERALES.csv.


import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

ruta_base = 'Graficas_LAT_TTL'
os.makedirs(ruta_base, exist_ok=True)

def generar_comparativas_latencia(archivo_csv):
    if not os.path.exists(archivo_csv):
        print(f"Error: No se encuentra {archivo_csv}")
        return

    df = pd.read_csv(archivo_csv, sep=';')
    labels = df['Variable']
    x = np.arange(len(labels))
    width = 0.5

    graficas = [
        ('LAT_GLOBAL_CLIENTE', 'CL_Latencia', 'Latencia Media (ms)', 'Comparativa Latencia Global del Cliente'),
        ('LAT_GLOBAL_SERVIDOR', 'SRV_Latencia', 'Latencia Media (ms)', 'Comparativa Latencia Global del Servidor')
    ]

    for nombre_fich, col, ylabel, titulo in graficas:
        plt.figure(figsize=(10, 6))

        color = '#3498db' if 'CLIENTE' in nombre_fich else '#e74c3c'

        barras = plt.bar(x, df[col], width, color=color, alpha=0.8, edgecolor='navy' if 'CLIENTE' in nombre_fich else 'darkred')

        plt.axvline(x=1.5, color='grey', linestyle='--', linewidth=0.8)
        plt.axvline(x=4.5, color='grey', linestyle='--', linewidth=0.8)

        # Valor encima de cada barra
        for barra in barras:
            yval = barra.get_height()
            plt.text(barra.get_x() + barra.get_width()/2, yval + (yval*0.01), round(yval, 2), ha='center', va='bottom', fontweight='bold', fontsize=9)

        plt.title(titulo, fontsize=12, fontweight='bold')
        plt.ylabel(ylabel)
        plt.xticks(x, labels)
        plt.grid(axis='y', linestyle=':', alpha=0.6)
        plt.tight_layout()

        path_out = os.path.join(ruta_base, f"{nombre_fich}.png")
        plt.savefig(path_out, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Generada: {path_out}")

if __name__ == "__main__":
    generar_comparativas_latencia('LATENCIA_GENERALES.csv')
