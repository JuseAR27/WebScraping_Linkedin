import time
import re
from typing import Dict
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from .base_scraper import ScraperStrategy

class LinkedInScraper(ScraperStrategy):
    """Implementación específica para extraer datos de LinkedIn."""
    
    def __init__(self):
        self.driver = None

    def _iniciar_navegador(self):
        """Inicia el navegador Selenium (Código original de logica.py)"""
        options = webdriver.ChromeOptions()
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"        
        options.add_argument(f'user-agent={user_agent}')
        options.add_argument('--start-maximized')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        servicio = ChromeService(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=servicio, options=options) 
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    def _cerrar_navegador(self):
        if self.driver:
            self.driver.quit()

    def extraer_datos(self, termino_busqueda: str) -> Dict:
        """
        Genera la URL, navega, maneja modales y extrae el HTML.
        """
        try:
            # 1. Preparar la URL
            termino_limpio = termino_busqueda.lower().replace("linkedin", "").strip()
            termino_codificado = quote_plus(termino_limpio)
            url = f"https://www.linkedin.com/jobs/search/?keywords={termino_codificado}&location=M%C3%A9xico"
            
            print(f"[SCRAPER] Navegando a la búsqueda: {url}")
            self._iniciar_navegador()
            self.driver.get(url)
            time.sleep(3) 
            wait = WebDriverWait(self.driver, 10) 
            
            # --- 2. MANEJO DE COOKIES Y MODALES ---
            try:
                cookie_wait = WebDriverWait(self.driver, 3) 
                css_selector = "button[data-tracking-control-name='cookie-consent-accept'], button.artdeco-global-banner__accept"
                cookie_button = cookie_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
                cookie_button.click()
            except: pass

            try:
                wait_popup = WebDriverWait(self.driver, 3) 
                close_button = wait_popup.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.modal__dismiss, button[aria-label='Dismiss']")))
                close_button.click()
            except: 
                try: self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                except: pass

            # --- 3. CAPTURAR URL DEL PRIMER EMPLEO Y NAVEGAR ---
            if "/jobs/search/" in self.driver.current_url:
                print("[SCRAPER] Buscando enlace del primer empleo...")
                try:
                    enlace_empleo = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 
                        "ul.jobs-search__results-list li a.base-card__full-link," + 
                        "a.job-search-card__url-overlay," +
                        "div.job-search-card a"
                    )))
                    url_oferta_especifica = enlace_empleo.get_attribute("href")
                    
                    self.driver.get(url_oferta_especifica)
                    time.sleep(3) 
                except Exception as e:
                    print(f"[SCRAPER] No se pudo obtener el link del primer empleo: {e}")
            
            # --- 4. EXPANDIR DESCRIPCIÓN (Botón "Ver más") ---
            try:
                boton_ver_mas_selector = (By.CSS_SELECTOR, 
                    "button.show-more-less-html__button," +
                    "button[aria-label='Show more, visually expands previously read content']," +
                    "button.description__footer-button"
                )
                boton_ver_mas = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(boton_ver_mas_selector))
                self.driver.execute_script("arguments[0].click();", boton_ver_mas)
                time.sleep(1)
            except:
                pass

            # --- 5. EXTRACCIÓN DE DATOS (BeautifulSoup) ---
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            titulo = "Oferta sin título"
            titulo_elem = soup.find('h1', class_=re.compile('top-card-layout__title|jobs-top-card__job-title'))
            if not titulo_elem: titulo_elem = soup.find('a', class_=re.compile('top-card-layout__title'))
            if titulo_elem: titulo = titulo_elem.get_text(strip=True)

            habilidades = []
            description_container = soup.find('div', class_=re.compile(r'show-more-less-html__markup|description__text|job-description-content'))
            
            if description_container:
                items = description_container.find_all('li')
                for item in items:
                    habilidades.append(item.get_text(strip=True))
                
                if len(habilidades) < 3:
                    parrafos = description_container.find_all('p')
                    for p in parrafos:
                        texto = p.get_text(strip=True)
                        if len(texto) > 10: 
                            habilidades.append(texto)
                            
                if not habilidades:
                    texto_bruto = description_container.get_text(separator='\n')
                    lines = texto_bruto.split('\n')
                    habilidades = [line for line in lines if len(line) > 10]

            print(f"[SCRAPER] Extracción bruta finalizada. Textos encontrados: {len(habilidades)}")

            # OJO: Retornamos las habilidades_brutas SIN LIMPIAR. 
            # La limpieza ocurrirá en tu nueva clase TextCleaner.
            return {
                'exito': True,
                'titulo_oferta': titulo,
                'url': self.driver.current_url,
                'habilidades_brutas': habilidades 
            }
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                'exito': False,
                'mensaje': f"Error al extraer: {str(e)}"
            }
        
        finally:
            self._cerrar_navegador()