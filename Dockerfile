FROM python:3.12-bookworm

ENV DEBIAN_FRONTEND=noninteractive

# Instalar repo oficial Firefox
RUN apt-get update && apt-get install -y \
    wget curl gnupg tcpdump firefox-esr \
    && rm -rf /var/lib/apt/lists/*

# Instalar Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update && apt-get install -y google-chrome-stable

# instalar Microsoft Edge
RUN curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg \
    && install -o root -g root -m 644 microsoft.gpg /etc/apt/trusted.gpg.d/ \
    && echo "deb [arch=amd64] https://packages.microsoft.com/repos/edge stable main" > /etc/apt/sources.list.d/microsoft-edge.list \
    && apt-get update && apt-get install -y microsoft-edge-stable

WORKDIR /app

# Instalamos selenium y el gestor de drivers
RUN pip install --no-cache-dir selenium webdriver-manager

COPY navegador.py .
COPY lanzador.sh .
RUN chmod +x lanzador.sh && mkdir /app/capturas

ENTRYPOINT ["/app/lanzador.sh"]
