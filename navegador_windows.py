# Autor: Héctor Payeras Rubio
# TFG: Análisis de la estabilidad y variabilidad de las huellas digitales JA4 en distintos contextos
# Universidad Autónoma de Madrid - Escuela Politécnica Superior, 2026
#
# Descripción:
#   Equivalente a navegador.py para entornos Windows. Controla el navegador mediante Selenium WebDriver sin depender del entorno Docker. Soporta
#   Chrome, Edge y Firefox con emulación de dispositivo móvil mediante iPhone X para navegadores Chromium y ajuste de User-Agent y resolución para Firefox.


import argparse
import time
import sys
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions

# Si se quiere imprimir para depurar poner en 1
IMPRIMIR=1

class NavegadorWeb:
    def __init__(self, url, browser, device, wait_ms):
        self.url = url
        self.browser = browser.lower()
        self.device = device.lower()
        self.wait_sec = wait_ms / 1000.0
        self.driver = self._set_up_driver()

    def _set_up_driver(self):
        # Firefox
        if self.browser == 'firefox':
            opts = FirefoxOptions()
            opts.add_argument("--headless")
            if self.device == 'mobile':
                agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
                opts.set_preference("general.useragent.override", agent)
            driver = webdriver.Firefox(options=opts)
            if self.device == 'mobile': driver.set_window_size(375, 812)

        # Microsoft Edge
        elif self.browser == 'edge':
            opts = EdgeOptions()
            opts.add_argument("--headless")
            opts.add_argument("--no-sandbox")
            opts.add_argument("--disable-dev-shm-usage")
            if self.device == 'mobile':
                opts.add_experimental_option("mobileEmulation", {"deviceName": "iPhone X"})
            driver = webdriver.Edge(options=opts)

        # Chrome, Brave, Opera (Motores Chromium)
        else:
            opts = ChromeOptions()
            opts.add_argument("--headless")
            opts.add_argument("--no-sandbox")
            opts.add_argument("--disable-dev-shm-usage")
            
            if self.device == 'mobile':
                opts.add_experimental_option("mobileEmulation", {"deviceName": "iPhone X"})
            
            driver = webdriver.Chrome(options=opts)

        return driver

    def navegar(self):
        if (IMPRIMIR==1):
            print(f"\n[*] NAVEGACIÓN: {self.url} | {self.browser} | {self.device}")
        try:
            self.driver.get(self.url)
            # Verificaciones reales
            res = self.driver.get_window_size()
            ua = self.driver.execute_script("return navigator.userAgent;")
            if (IMPRIMIR==1):
                print(f"[+] Validación -> Resolución: {res['width']}x{res['height']}")
                print(f"[+] Validación -> User-Agent: {ua}")
                print(f"[*] Título: '{self.driver.title}'")
            time.sleep(self.wait_sec)
        except Exception as e:
            print(f"[!] Error navegando: {e}")

    def cerrar(self):
        if self.driver:
            self.driver.quit()
            if (IMPRIMIR==1):
                print("[*] Driver cerrado.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", required=True)
    parser.add_argument("-b", "--browser", choices=['chrome', 'firefox', 'edge'], default='chrome')
    parser.add_argument("-d", "--device", choices=['desktop', 'mobile'], default='desktop')
    parser.add_argument("-w", "--wait", type=int, default=2000)
    args = parser.parse_args()

    nav = NavegadorWeb(args.url, args.browser, args.device, args.wait)
    try:
        nav.navegar()
    finally:
        nav.cerrar()