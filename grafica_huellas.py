import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 1. Crear estructura de carpetas
ruta_base = 'Graficas_huellas'
os.makedirs(ruta_base, exist_ok=True)

def generar_comparativas_individuales(archivo_csv):
    if not os.path.exists(archivo_csv):
        print(f"Error: No se encuentra {archivo_csv}")
        return

    df = pd.read_csv(archivo_csv, sep=';')
    
    # Convertir distancia Levenshtein a similitud normalizada
    df['CL_Levenshtein'] = 1 / (1 + df['CL_Levenshtein'])
    df['SRV_Levenshtein'] = 1 / (1 + df['SRV_Levenshtein'])

    labels = df['Variable']
    x = np.arange(len(labels))
    width = 0.35

    # Definimos cada argumento de tu TFG como una métrica
    metricas = [
        ('ESTRUCTURA_LEVENSHTEIN', 'CL_Levenshtein', 'SRV_Levenshtein', 'Índice (0-1)', 'Comparativa Similitud Estructural (Levenshtein)'),
        ('SIMILITUD_CIPHERS', 'CL_Sim_Ciphers', 'SRV_Sim_Ciphers', 'Índice (0-1)', 'Comparativa Similitud ALG Cifrado'),
        ('SIMILITUD_EXTENSIONES', 'CL_Sim_Ext', 'SRV_Sim_Ext', 'Índice (0-1)', 'Comparativa Similitud de Extensiones'),
        ('ESTABILIDAD_TOTAL', 'CL_Sim_Total', 'SRV_Sim_Total', 'Índice (0-1)', 'Comparativa de Estabilidad General de la Huella')
    ]

    for nombre_fich, col_cl, col_srv, ylabel, titulo in metricas:
        plt.figure(figsize=(10, 6))
        
        # Barras comparativas
        plt.bar(x - width/2, df[col_cl], width, label='Cliente (JA4)', color='#3498db', alpha=0.8)
        plt.bar(x + width/2, df[col_srv], width, label='Servidor (JA4S)', color='#e74c3c', alpha=0.8)

        # Separadores de categoría
        plt.axvline(x=1.5, color='grey', linestyle='--', linewidth=0.8)
        plt.axvline(x=4.5, color='grey', linestyle='--', linewidth=0.8)

        # Títulos y formato
        plt.title(titulo, fontsize=12, fontweight='bold')
        plt.ylabel(ylabel)
        plt.xticks(x, labels)
        plt.legend()
        plt.grid(axis='y', linestyle=':', alpha=0.6)
        
        plt.tight_layout()
        
        # Guardar
        path_out = os.path.join(ruta_base, f"{nombre_fich}.png")
        plt.savefig(path_out)
        plt.close()
        print(f"Generada: {path_out}")

if __name__ == "__main__":
    generar_comparativas_individuales('DATOS_HUELLAS_GENERALES.csv')