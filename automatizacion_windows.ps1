# Autor: Héctor Payeras Rubio
# TFG: Análisis de la estabilidad y variabilidad de las huellas digitales JA4 en distintos contextos
# Universidad Autónoma de Madrid - Escuela Politécnica Superior, 2026
#
# Descripción:
#   Script principal de captura para Windows. Equivalente a automatizacion.sh para entornos Linux. Recorre todas las combinaciones de navegador, dispositivo
#   y URL usando TShark para capturar el tráfico TLS en lugar de tcpdump, e integra la lógica del lanzador directamente sin necesidad de Docker.
#   Configura la variable $INTERFAZ con el número de interfaz de red obtenido con el comando: "C:\Program Files\Wireshark\tshark.exe" -D


# 1 para ver mensajes, 0 para silencio
$IMPRIMIR = 1

# Configuracion
$URLS = @(
    "https://google.com", "https://googleapis.com", "https://gstatic.com", "https://cloudflare.com", "https://apple.com", "https://microsoft.com", "https://facebook.com", "https://amazonaws.com", "https://googlevideo.com", "https://amazon.com",
    "https://fbcdn.net", "https://chatgpt.com", "https://whatsapp.net", "https://instagram.com", "https://youtube.com", "https://doubleclick.net", "https://netflix.com", "https://akadns.net", "https://ntp.org", "https://apple-dns.net",
    "https://googleusercontent.com", "https://bing.com", "https://icloud.com", "https://googlesyndication.com", "https://live.com", "https://akamai.net", "https://tiktokcdn.com", "https://tiktokv.com", "https://cloudflare-dns.com", "https://aaplimg.com",
    "https://cloudfront.net", "https://ui.com", "https://ytimg.com", "https://akamaiedge.net", "https://yahoo.com", "https://gvt2.com", "https://spotify.com", "https://fastly.net", "https://wikipedia.org", "https://office.com",
    "https://cdninstagram.com", "https://samsung.com", "https://gvt1.com", "https://roblox.com", "https://dns.google", "https://steamserver.net", "https://one.one", "https://baidu.com", "https://google-analytics.com", "https://app-measurement.com",
    "https://criteo.com", "https://app-analytics-services.com", "https://sentry.io", "https://3gppnetwork.org", "https://applovin.com", "https://googleadservices.com", "https://msftncsi.com", "https://appsflyersdk.com", "https://googletagmanager.com", "https://msn.com",
    "https://snapchat.com", "https://trafficmanager.net", "https://whatsapp.com", "https://ggpht.com", "https://azure.com", "https://unity3d.com", "https://windows.com", "https://amazon-adsystem.com", "https://amazon.dev", "https://windows.net",
    "https://linkedin.com", "https://a2z.com", "https://0xrpc.io", "https://playstation.net", "https://microsoftonline.com", "https://tiktokcdn-us.com", "https://xiaomi.com", "https://skype.com", "https://merkle.io", "https://avast.com",
    "https://llamarpc.com", "https://windowsupdate.com", "https://msftconnecttest.com", "https://vungle.com", "https://mzstatic.com", "https://taboola.com", "https://cdn-apple.com", "https://digicert.com", "https://qq.com", "https://aws.dev",
    "https://rubiconproject.com", "https://avsxappcaptiveportal.com", "https://publicnode.com", "https://discord.com", "https://gmail.com", "https://adtrafficquality.google", "https://android.com", "https://miui.com", "https://office.net", "https://kwai-pro.com"
)
$NAVEGADORES = @("chrome", "edge", "firefox")
$DISPOSITIVOS = @("desktop", "mobile")

$WAIT_NAVEGACION = 4000
$INTERVALO_ENTRE_CAPTURAS = 6

# Interfaz de red de Wireshark con el comando de programador de comandos_cmd_windows.txt
$INTERFAZ = 4

# Carpeta de salida
$OUTPUT_DIR = "$PSScriptRoot\Capturas\mis_capturas"
if (-Not (Test-Path $OUTPUT_DIR)) {
    New-Item -ItemType Directory -Force -Path $OUTPUT_DIR | Out-Null
}

if ($IMPRIMIR -eq 1) {
    Write-Host "======================================================"
    Write-Host "INICIANDO BUCLE INFINITO - PRIORIDAD NAVEGADOR"
    Write-Host "Orden: Navegador -> Dispositivo -> URL"
    Write-Host "======================================================"
}

# Bucle infinito
while ($true) {
    # Navegador
    foreach ($nav in $NAVEGADORES) {
        # Dispositivo
        foreach ($disp in $DISPOSITIVOS) {
            # URL
            foreach ($url in $URLS) {
                
                $HORA = Get-Date -Format "HH:mm:ss"
                if ($IMPRIMIR -eq 1) {
                    Write-Host ""
                    Write-Host "[$HORA] >> Proceso: $nav | $disp | $url"
                }

                $UrlClean = $url -replace "https?://", "" -replace "/", "_" -replace "[^a-zA-Z0-9_.-]", "_"
                $DATE = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
                $FILENAME = "${nav}_${disp}_${UrlClean}_${DATE}.pcap"
                $FILEPATH = Join-Path $OUTPUT_DIR $FILENAME

                if ($IMPRIMIR -eq 1) {
                    Write-Host "================================================"
                    Write-Host "[TSHARK] Iniciando captura: $FILENAME"
                }

                # Equivalente a: tcpdump -i any -w "$FILEPATH" &
                $TsharkArgs = "-i $INTERFAZ -w `"$FILEPATH`""
                $TsharkProcess = Start-Process -FilePath "C:\Program Files\Wireshark\tshark.exe" -ArgumentList $TsharkArgs -PassThru -WindowStyle Hidden
                
                Start-Sleep -Seconds 1

                if ($IMPRIMIR -eq 1) {
                    Write-Host "------------------------------------------------"
                }

                # Equivalente a: python3 navegador.py
                python navegador_windows.py -u $url -b $nav -d $disp -w $WAIT_NAVEGACION

                if ($IMPRIMIR -eq 1) {
                    Write-Host "------------------------------------------------"
                    Write-Host "[TSHARK] Deteniendo captura..."
                }

                # Equivalente a: kill $TCP_PID
                Stop-Process -Id $TsharkProcess.Id -Force -ErrorAction SilentlyContinue
                Start-Sleep -Seconds 1

                if ($IMPRIMIR -eq 1) {
                    Write-Host "[V] Proceso finalizado con exito."
                }

                # Pausa
                Start-Sleep -Seconds $INTERVALO_ENTRE_CAPTURAS
            }
        }
        if ($IMPRIMIR -eq 1) {
            Write-Host "--- Finalizado bloque completo de $nav. Pasando al siguiente... ---"
        }

        Start-Sleep -Seconds 5
    }
    
    if ($IMPRIMIR -eq 1) {
        Write-Host "======================================================"
        Write-Host "Ciclo global (todos los navegadores) terminado. Reiniciando..."
    }
    Start-Sleep -Seconds 30
}