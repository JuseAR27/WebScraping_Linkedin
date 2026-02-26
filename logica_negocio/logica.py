import time
import re
import os
from datetime import datetime
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
from acceso_datos import capa_acceso
from urllib.parse import quote_plus
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from openai import OpenAI
from dotenv import load_dotenv

# Cargar variables de entorno del archivo .env
load_dotenv()

class CapaLogicaNegocio:
    def __init__(self):
        self.capa_datos = capa_acceso.CapaAccesoDatos()
        self.driver = None
        # Inicializar cliente OpenAI
        # Si no hay key, el cliente se crea pero fallará al intentar usarlo, lo manejaremos con try/except
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if api_key else None
    
    # ... (Mantén las funciones iniciar_navegador y cerrar_navegador IGUAL que antes) ...
    def iniciar_navegador(self):
        """Inicia el navegador Selenium"""
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
           
    def cerrar_navegador(self):
        if self.driver:
            self.driver.quit()

    def extraer_habilidades_linkedin(self, url: str) -> Dict:
            """
            Extrae habilidades navegando DIRECTAMENTE a la oferta (Estrategia Robusta)
            """
            try:
                print(f"[LÓGICA] Navegando a la búsqueda: {url}")
                self.driver.get(url)
                time.sleep(3) 
                wait = WebDriverWait(self.driver, 10) 
                
                # --- 1. MANEJO DE COOKIES Y MODALES (Bloque estándar) ---
                try:
                    cookie_wait = WebDriverWait(self.driver, 3) 
                    css_selector = "button[data-tracking-control-name='cookie-consent-accept'], button.artdeco-global-banner__accept"
                    cookie_button = cookie_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
                    cookie_button.click()
                except: pass

                try:
                    # Cerrar modal de login si aparece
                    wait_popup = WebDriverWait(self.driver, 3) 
                    close_button = wait_popup.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.modal__dismiss, button[aria-label='Dismiss']")))
                    close_button.click()
                except: 
                    try: self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                    except: pass

                # --- 2. CAPTURAR URL DEL PRIMER EMPLEO Y NAVEGAR ---
                if "/jobs/search/" in self.driver.current_url:
                    print("[LÓGICA] Estamos en lista de resultados. Buscando enlace del primer empleo...")
                    try:
                        # Buscamos el enlace (tag 'a') del primer resultado
                        # Estos selectores son específicos para la vista de "invitado" que mostraste en la imagen
                        enlace_empleo = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 
                            "ul.jobs-search__results-list li a.base-card__full-link," + 
                            "a.job-search-card__url-overlay," +
                            "div.job-search-card a"
                        )))
                        
                        url_oferta_especifica = enlace_empleo.get_attribute("href")
                        print(f"[LÓGICA] Enlace encontrado: {url_oferta_especifica}")
                        print("[LÓGICA] Navegando directamente a la oferta...")
                        
                        # AQUÍ ESTÁ LA CLAVE: Vamos directo a la página, saliendo de la búsqueda
                        self.driver.get(url_oferta_especifica)
                        time.sleep(3) # Esperamos a que cargue la nueva página
                        
                    except Exception as e:
                        print(f"[LÓGICA] No se pudo obtener el link del primer empleo: {e}")
                        # Si falla, intentamos seguir en la página actual por si acaso ya se abrió
                
                # --- 3. EXPANDIR DESCRIPCIÓN (Botón "Ver más") ---
                # Ahora estamos en la página del empleo, buscamos el botón
                print("[LÓGICA] Buscando botón 'Ver más'...")
                try:
                    boton_ver_mas_selector = (By.CSS_SELECTOR, 
                        "button.show-more-less-html__button," +
                        "button[aria-label='Show more, visually expands previously read content']," +
                        "button.description__footer-button"
                    )
                    boton_ver_mas = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(boton_ver_mas_selector))
                    self.driver.execute_script("arguments[0].click();", boton_ver_mas)
                    print("[LÓGICA] Descripción expandida.")
                    time.sleep(1)
                except:
                    print("[LÓGICA] No se encontró botón 'Ver más' (o ya estaba expandido).")

                # --- 4. EXTRACCIÓN DE DATOS ---
                html = self.driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                
                # Título
                titulo = "Oferta sin título"
                titulo_elem = soup.find('h1', class_=re.compile('top-card-layout__title|jobs-top-card__job-title'))
                if not titulo_elem: titulo_elem = soup.find('a', class_=re.compile('top-card-layout__title'))
                if titulo_elem: titulo = titulo_elem.get_text(strip=True)

                habilidades = []
                
                # Contenedor de descripción (Selectores actualizados)
                # Buscamos 'show-more-less-html__markup' que es el estándar actual
                description_container = soup.find('div', class_=re.compile(r'show-more-less-html__markup|description__text|job-description-content'))
                
                if description_container:
                    # Buscar listas
                    items = description_container.find_all('li')
                    for item in items:
                        habilidades.append(item.get_text(strip=True))
                    
                    # Buscar texto en párrafos si no hay listas
                    if len(habilidades) < 3:
                        parrafos = description_container.find_all('p')
                        for p in parrafos:
                            texto = p.get_text(strip=True)
                            if len(texto) > 10: # Evita textos muy cortos
                                habilidades.append(texto)
                                
                    # Texto bruto como último recurso
                    if not habilidades:
                        texto_bruto = description_container.get_text(separator='\n')
                        lines = texto_bruto.split('\n')
                        habilidades = [line for line in lines if len(line) > 10]
                else:
                    print("[LÓGICA] ALERTA: No se encontró el contenedor de texto.")

                habilidades_limpias = self._limpiar_habilidades(habilidades)
                print(f"[LÓGICA] Total habilidades encontradas: {len(habilidades_limpias)}")

                return {
                    'exito': True,
                    'titulo_oferta': titulo,
                    'url': self.driver.current_url,
                    'habilidades': habilidades_limpias,
                    'fecha_extraccion': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            
            except Exception as e:
                import traceback
                traceback.print_exc()
                return {
                    'exito': False,
                    'mensaje': f"Error al extraer: {str(e)}"
                }
            
    def _limpiar_habilidades(self, habilidades: List[str]) -> List[str]:
        # ... (Tu código existente de limpieza) ...
        limpiadas = []
        vistas = set()
        palabras_excluir = ['click', 'show', 'more', 'less', 'see', 'view', 'apply', 'job', 'description']
        for habilidad in habilidades:
            limpia = re.sub(r'\s+', ' ', habilidad).strip()
            limpia = re.sub(r'[^\w\s\+\#\.-_,\(\)]', '', limpia) 
            if len(limpia) < 3 or len(limpia) > 250: continue
            if limpia.lower() in palabras_excluir: continue
            if limpia.lower() not in vistas:
                vistas.add(limpia.lower())
                limpiadas.append(limpia)
        return limpiadas

    # --- NUEVA FUNCIÓN: LÓGICA DE GPT ---
    def _analizar_con_gpt(self, titulo: str, habilidades: List[str]) -> str:
        """
        Envía las habilidades a ChatGPT para obtener un resumen profesional.
        """
        if not self.client:
            return "⚠️ No se ha configurado la API Key de OpenAI. Crea un archivo .env con OPENAI_API_KEY=..."

        try:
            # Convertimos la lista a texto
            lista_texto = "\n- ".join(habilidades[:30]) # Limitamos a 30 para no gastar tantos tokens
            
            prompt = f"""
            Actúa como un reclutador experto en tecnología. Analiza la siguiente oferta de trabajo.
            
            Título del puesto: {titulo}
            
            Fragmentos extraídos de la descripción:
            {lista_texto}
            
            Por favor, genera un resumen estructurado en Markdown que incluya:
            1. **Objetivo del Rol**: En una frase, ¿qué buscan?
            2. **Stack Tecnológico Principal**: Las 5 herramientas más importantes mencionadas.
            3. **Skills Blandas**: ¿Qué aptitudes personales buscan?
            4. **Nivel de Experiencia**: ¿Parece Junior, Mid o Senior? (Deduce basado en el texto).
            
            Sé conciso y profesional.
            """

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo", # Puedes usar gpt-4 si tienes acceso
                messages=[
                    {"role": "system", "content": "Eres un asistente experto en RRHH y tecnología."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content

        except Exception as e:
            return f"❌ Error al consultar ChatGPT: {str(e)}"

    def procesar_busqueda(self, termino_busqueda: str) -> Dict:
        """
        Método principal actualizado para incluir GPT
        """
        try:
            print("[LÓGICA] Iniciando proceso...")
            termino_limpio = termino_busqueda.lower().replace("linkedin", "").strip()
            termino_codificado = quote_plus(termino_limpio)
            url_seleccionada = f"https://www.linkedin.com/jobs/search/?keywords={termino_codificado}&location=M%C3%A9xico"
            
            self.iniciar_navegador()
            
            # 1. Extraer habilidades (Scraping)
            print("[LÓGICA] Extrayendo datos...")
            resultado_extraccion = self.extraer_habilidades_linkedin(url_seleccionada)
            
            if not resultado_extraccion['exito']:
                return resultado_extraccion
            
            # 2. Analizar con GPT (NUEVO PASO)
            print("[LÓGICA] Analizando con ChatGPT...")
            resumen_gpt = self._analizar_con_gpt(
                resultado_extraccion['titulo_oferta'], 
                resultado_extraccion['habilidades']
            )

            # Preparar datos completos
            datos_completos = {
                'termino_busqueda': termino_busqueda,
                'titulo_oferta': resultado_extraccion['titulo_oferta'],
                'url': resultado_extraccion['url'],
                'habilidades': resultado_extraccion['habilidades'],
                'fecha_extraccion': resultado_extraccion['fecha_extraccion'],
                'total_habilidades': len(resultado_extraccion['habilidades']),
                'resumen_ia': resumen_gpt # Guardamos también el resumen
            }
            
            return {
                'exito': True,
                'habilidades': resultado_extraccion['habilidades'],
                'titulo_oferta': resultado_extraccion['titulo_oferta'],
                'resumen_ia': resumen_gpt, # <-- Retornamos el resumen
                'datos_completos': datos_completos
            }
        
        except Exception as e:
            return {'exito': False, 'mensaje': f'Error: {str(e)}'}
        
        finally:
            self.cerrar_navegador()

    # ... (Mantén guardar_datos IGUAL) ...
    def guardar_datos(self, datos: Dict, formato: str) -> List[str]:
        rutas = []
        if formato in ['1', '3']: rutas.append(self.capa_datos.guardar_json(datos))
        if formato in ['2', '3']: rutas.append(self.capa_datos.guardar_excel(datos))
        return rutas