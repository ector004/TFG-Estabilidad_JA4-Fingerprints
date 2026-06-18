#!/bin/bash

# 1 para ver mensajes, 0 para silencio
IMPRIMIR=1

# Configuracion
URLS=("https://www.google.com" "https://www.wikipedia.org" "https://www.youtube.com" "https://www.github.com" "https://www.facebook.com")
NAVEGADORES=("chrome" "edge" "firefox")
DISPOSITIVOS=("desktop" "mobile")

WAIT_NAVEGACION=4000
INTERVALO_ENTRE_CAPTURAS=6

# Carpeta de salida
OUTPUT_DIR="$(pwd)/Capturas/mis_capturas"
mkdir -p "$OUTPUT_DIR"

if [ "$IMPRIMIR" -eq 1 ]; then
    echo "======================================================"
    echo "INICIANDO BUCLE INFINITO - PRIORIDAD NAVEGADOR"
    echo "Orden: Navegador -> Dispositivo -> URL"
    echo "======================================================"
fi

# Bucle infinito
while true; do
    # Navegador
    for nav in "${NAVEGADORES[@]}"; do
        # Dispositivo
        for disp in "${DISPOSITIVOS[@]}"; do
            # URL
            for url in "${URLS[@]}"; do
                
                HORA=$(date +"%H:%M:%S")
                if [ "$IMPRIMIR" -eq 1 ]; then
                    echo
                    echo "[$HORA] >> Proceso: $nav | $disp | $url"
                fi

                # Ejecucion de Docker
                sudo docker run --rm --cap-add=NET_ADMIN \
                    -v "$OUTPUT_DIR":/app/capturas \
                    trafico_scanner -u "$url" -b "$nav" -d "$disp" -w $WAIT_NAVEGACION

                # Pausa para que el servidor respire
                sleep $INTERVALO_ENTRE_CAPTURAS
            done
        done
        if [ "$IMPRIMIR" -eq 1 ]; then
            echo "--- Finalizado bloque completo de $nav. Pasando al siguiente... ---"
        fi

        sleep 5
    done
    
    if [ "$IMPRIMIR" -eq 1 ]; then
        echo "======================================================"
        echo "Ciclo global (todos los navegadores) terminado. Reiniciando..."
    fi
    sleep 30
done
