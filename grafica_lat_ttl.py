import pandas as pd
import matplotlib.pyplot as plt
import os
import sys

# Configuracion dinamica para localizar carpetas y detectar nombres de columnas
CONFIGURACION = {
    'navegador': {
        'carpeta': 'Navegador',
        'archivo_sv': 'SV_NAV_LATENCIA_POR_WEB.csv',
        'archivo_cl': 'CL_NAV_LATENCIA_POR_WEB.csv',
        'archivo_global_sv': 'SV_NAV_LATENCIA_GLOBAL.csv',
        'archivo_global_cl': 'CL_NAV_LATENCIA_GLOBAL.csv',
        'posibles_cols': ['Navegador', 'navegador', 'nav'],
        'titulo': 'Navegador'
    },
    'so': {
        'carpeta': 'SO',
        'archivo_sv': 'SV_SO_LATENCIA_POR_WEB.csv',
        'archivo_cl': 'CL_SO_LATENCIA_POR_WEB.csv',
        'archivo_global_sv': 'SV_SO_LATENCIA_GLOBAL.csv',
        'archivo_global_cl': 'CL_SO_LATENCIA_GLOBAL.csv',
        'posibles_cols': ['SO', 'SO_Origen', 'so_real', 'so_origen'],
        'titulo': 'Sistema Operativo'
    },
    'dispositivo': {
        'carpeta': 'Dispositivo',
        'archivo_sv': 'SV_DISP_LATENCIA_POR_WEB.csv',
        'archivo_cl': 'CL_DISP_LATENCIA_POR_WEB.csv',
        'archivo_global_sv': 'SV_DISP_LATENCIA_GLOBAL.csv',
        'archivo_global_cl': 'CL_DISP_LATENCIA_GLOBAL.csv',
        'posibles_cols': ['Dispositivo', 'plataforma', 'dispositivo', 'PLATAFORMA'],
        'titulo': 'Dispositivo'
    }
}

def generar_graficas_separadas(modo):
    modo = modo.lower()
    if modo not in CONFIGURACION:
        print(f"Error: Parametro '{modo}' no reconocido. Use: navegador, so o dispositivo.")
        return

    conf = CONFIGURACION[modo]
    # Nombre de la carpeta
    nombre_carpeta_graficas = "Graficas_LAT_TTL"
    
    if not os.path.exists(nombre_carpeta_graficas):
        os.makedirs(nombre_carpeta_graficas)

    print(f"--- INICIANDO GENERACION DE GRAFICAS PARA: {conf['titulo'].upper()} ---")
    
    # 1. GENERACION DE GRAFICAS DETALLADAS (POR WEB)
    tareas_web = [
        (conf['archivo_sv'], f"SERVIDOR_{modo.upper()}", "Servidor"),
        (conf['archivo_cl'], f"CLIENTE_{modo.upper()}", "Cliente")
    ]

    for nombre_archivo, nombre_salida, tipo_texto in tareas_web:
        ruta_csv = os.path.join(conf['carpeta'], nombre_archivo)
        if not os.path.exists(ruta_csv):
            print(f"Advertencia: No se encontro el archivo detallado en {ruta_csv}")
            continue

        try:
            df = pd.read_csv(ruta_csv, sep=';')
            col_id = next((col for col in conf['posibles_cols'] if col in df.columns), None)
            if col_id is None: continue

            num_webs = len(df['Web'].unique())
            ancho_ajustado = max(24, num_webs * 0.25)

            # --- GRAFICA LATENCIA WEB ---
            plt.figure(figsize=(ancho_ajustado, 8))
            df_pivot_lat = df.pivot(index='Web', columns=col_id, values='Latencia_Media')
            df_pivot_lat.plot(kind='bar', figsize=(ancho_ajustado, 8), width=0.8, alpha=0.8, ax=plt.gca())
            plt.title(f'Análisis de Latencia Media ({tipo_texto}) - Detalle por Web ({conf["titulo"]})', fontsize=15)
            plt.ylabel('Latencia (ms)')
            plt.grid(axis='y', linestyle='--', alpha=0.5)
            
            # Etiquetas mas pequeñas y con espacio para que sean legibles
            plt.xticks(rotation=90, fontsize=8) 
            plt.tight_layout()
            
            ruta_save_lat = os.path.join(nombre_carpeta_graficas, f'LAT_{nombre_salida}.png')
            plt.savefig(ruta_save_lat, bbox_inches='tight')
            plt.close()
            print(f"Archivo LAT WEB con grafica guardada en {ruta_save_lat}")

            # --- GRAFICA TTL WEB ---
            plt.figure(figsize=(ancho_ajustado, 6))
            df_pivot_ttl = df.pivot(index='Web', columns=col_id, values='TTL_Moda')
            offsets = [0.5, 0, -0.5]
            for i, col in enumerate(df_pivot_ttl.columns):
                plt.plot(df_pivot_ttl.index, df_pivot_ttl[col] + offsets[i%3], marker='o', linestyle=':', label=f"TTL {col}")
            
            plt.title(f'Análisis de TTL ({tipo_texto}) - Estabilidad por Web ({conf["titulo"]})', fontsize=15)
            plt.yticks([0, 32, 64, 100, 128, 255])
            
            # Etiquetas mas pequeñas en el TTL tambien
            plt.xticks(rotation=90, fontsize=8)
            plt.grid(True, linestyle=':', alpha=0.5)
            plt.legend(title=conf['titulo'], bbox_to_anchor=(1.01, 1), loc='upper left')
            plt.tight_layout()
            
            ruta_save_ttl = os.path.join(nombre_carpeta_graficas, f'TTL_{nombre_salida}.png')
            plt.savefig(ruta_save_ttl, bbox_inches='tight')
            plt.close()
            print(f"Archivo TTL WEB con grafica guardada en {ruta_save_ttl}")

        except Exception as e:
            print(f"Error procesando {nombre_archivo}: {e}")

    # 2. GENERACION DE GRAFICAS RESUMEN (GLOBAL CON PREFIJO LAT_GL_)
    tareas_global = [
        (conf['archivo_global_sv'], f"SERVIDOR_{modo.upper()}", "Servidor"),
        (conf['archivo_global_cl'], f"CLIENTE_{modo.upper()}", "Cliente")
    ]

    for nombre_archivo, nombre_salida, tipo_texto in tareas_global:
        ruta_csv = os.path.join(conf['carpeta'], nombre_archivo)
        if not os.path.exists(ruta_csv):
            print(f"Nota: No se encontro archivo global en {ruta_csv}")
            continue

        try:
            df_global = pd.read_csv(ruta_csv, sep=';')
            col_id = next((col for col in conf['posibles_cols'] if col in df_global.columns), None)
            
            if col_id:
                plt.figure(figsize=(10, 6))
                barras = plt.bar(df_global[col_id], df_global['Latencia_Media'], color='skyblue', edgecolor='navy', alpha=0.8)
                
                plt.title(f'Comparativa de Latencia Global ({tipo_texto}) por {conf["titulo"]}', fontsize=14)
                plt.ylabel('Latencia Media (ms)')
                plt.grid(axis='y', linestyle='--', alpha=0.6)

                for barra in barras:
                    yval = barra.get_height()
                    plt.text(barra.get_x() + barra.get_width()/2, yval + (yval*0.01), round(yval, 2), ha='center', va='bottom', fontweight='bold')

                plt.tight_layout()
                ruta_save_gl = os.path.join(nombre_carpeta_graficas, f'LAT_GL_{nombre_salida}.png')
                plt.savefig(ruta_save_gl, bbox_inches='tight')
                plt.close()
                print(f"Archivo global LAT con grafica guardada en {ruta_save_gl}")

        except Exception as e:
            print(f"Error procesando archivo global {nombre_archivo}: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        generar_graficas_separadas(sys.argv[1])
    else:
        print("Uso: python3 script.py [navegador|so|dispositivo]")