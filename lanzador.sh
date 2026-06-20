# Autor: Héctor Payeras Rubio
# TFG: Análisis de la estabilidad y variabilidad de las huellas digitales JA4 en distintos contextos
# Universidad Autónoma de Madrid - Escuela Politécnica Superior, 2026
#
# Descripción:
#   Coordina cada visita individual iniciando tcpdump, lanzando el script de navegación y deteniendo la captura al terminar.


#!/bin/bash

# 1 para ver mensajes, 0 para silencio
IMPRIMIR=1

# Guardar argumentos originales
ORIG_ARGS=("$@")

# Valores por defecto para el nombre del archivo
URL_CLEAN="unknown"
BROWSER="chrome"
DEV="desktop"

# Parsear argumentos para el nombre del archivo
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -u|--url) URL_CLEAN=$(echo "$2" | sed 's~http[s]*://~~g' | sed 's~/~_~g' | sed 's/[^a-zA-Z0-9_.-]/_/g'); shift 2 ;;
        -b|--browser) BROWSER="$2"; shift 2 ;;
        -d|--device) DEV="$2"; shift 2 ;;
        *) shift ;;
    esac
done

DATE=$(date +"%Y-%m-%d_%H-%M-%S")
FILENAME="${BROWSER}_${DEV}_${URL_CLEAN}_${DATE}.pcap"
FILEPATH="/app/capturas/$FILENAME"

# Lógica de bandera para imprimir
if [ "$IMPRIMIR" -eq 1 ]; then
    echo "================================================"
    echo "[TCPDUMP] Iniciando captura: $FILENAME"
fi

tcpdump -i any -w "$FILEPATH" > /dev/null 2>&1 &
TCP_PID=$!

sleep 1

if [ "$IMPRIMIR" -eq 1 ]; then
    echo "------------------------------------------------"
fi
python3 navegador.py "${ORIG_ARGS[@]}"

if [ "$IMPRIMIR" -eq 1 ]; then
    echo "------------------------------------------------"
    echo "[TCPDUMP] Deteniendo captura..."
fi
kill $TCP_PID
sleep 1

if [ "$IMPRIMIR" -eq 1 ]; then
    echo "[V] Proceso finalizado con éxito."
fi
