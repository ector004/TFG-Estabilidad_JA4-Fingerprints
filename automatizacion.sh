# Autor: Héctor Payeras Rubio
# TFG: Análisis de la estabilidad y variabilidad de las huellas digitales JA4 en distintos contextos
# Universidad Autónoma de Madrid - Escuela Politécnica Superior, 2026
#
# Descripción:
#   Script principal de captura. Recorre todas las combinaciones de navegador, dispositivo y URL lanzando un contenedor Docker por cada visita.

#!/bin/bash

# 1 para ver mensajes, 0 para silencio
IMPRIMIR=1

# Configuracion
URLS=(
    "https://google.com" "https://googleapis.com" "https://gstatic.com" "https://cloudflare.com" "https://apple.com"
    "https://microsoft.com" "https://facebook.com" "https://amazonaws.com" "https://googlevideo.com" "https://amazon.com"
    "https://fbcdn.net" "https://chatgpt.com" "https://whatsapp.net" "https://instagram.com" "https://youtube.com"
    "https://doubleclick.net" "https://netflix.com" "https://akadns.net" "https://ntp.org" "https://apple-dns.net"
    "https://googleusercontent.com" "https://bing.com" "https://icloud.com" "https://googlesyndication.com" "https://live.com"
    "https://akamai.net" "https://tiktokcdn.com" "https://tiktokv.com" "https://cloudflare-dns.com" "https://aaplimg.com"
    "https://cloudfront.net" "https://ui.com" "https://ytimg.com" "https://akamaiedge.net" "https://yahoo.com"
    "https://gvt2.com" "https://spotify.com" "https://fastly.net" "https://wikipedia.org" "https://office.com"
    "https://cdninstagram.com" "https://samsung.com" "https://gvt1.com" "https://roblox.com" "https://dns.google"
    "https://steamserver.net" "https://one.one" "https://baidu.com" "https://google-analytics.com" "https://app-measurement.com"
    "https://criteo.com" "https://app-analytics-services.com" "https://sentry.io" "https://3gppnetwork.org" "https://applovin.com"
    "https://googleadservices.com" "https://msftncsi.com" "https://appsflyersdk.com" "https://googletagmanager.com" "https://msn.com"
    "https://snapchat.com" "https://trafficmanager.net" "https://whatsapp.com" "https://ggpht.com" "https://azure.com"
    "https://unity3d.com" "https://windows.com" "https://amazon-adsystem.com" "https://amazon.dev" "https://windows.net"
    "https://linkedin.com" "https://a2z.com" "https://0xrpc.io" "https://playstation.net" "https://microsoftonline.com"
    "https://tiktokcdn-us.com" "https://xiaomi.com" "https://skype.com" "https://merkle.io" "https://avast.com"
    "https://llamarpc.com" "https://windowsupdate.com" "https://msftconnecttest.com" "https://vungle.com" "https://mzstatic.com"
    "https://taboola.com" "https://cdn-apple.com" "https://digicert.com" "https://qq.com" "https://aws.dev"
    "https://rubiconproject.com" "https://avsxappcaptiveportal.com" "https://publicnode.com" "https://discord.com" "https://gmail.com"
    "https://adtrafficquality.google" "https://android.com" "https://miui.com" "https://office.net" "https://kwai-pro.com"
)
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
