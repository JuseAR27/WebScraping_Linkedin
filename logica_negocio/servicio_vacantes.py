from datetime import datetime
from typing import Dict, List
from scraping.base_scraper import ScraperStrategy
from utilidades.text_cleaner import TextCleaner
from inteligencia_artificial.gpt_analyzer import AIAnalyzer
from exportadores.exporter_factory import ExporterFactory
import os

class JobService:
    """
    Patrón Facade: Orquesta el flujo entre el Scraper, el Limpiador, la IA y los Exportadores.
    """
    def __init__(self, scraper: ScraperStrategy):
        # Recibimos el scraper mediante "Inyección de Dependencias"
        self.scraper = scraper
        self.analyzer = AIAnalyzer()
        self.directorio_salida = "datos_extraidos"
        
        if not os.path.exists(self.directorio_salida):
            os.makedirs(self.directorio_salida)

    def procesar_busqueda(self, termino_busqueda: str) -> Dict:
        # 1. Delegar extracción
        resultado = self.scraper.extraer_datos(termino_busqueda)
        if not resultado['exito']:
            return resultado
            
        # 2. Delegar limpieza
        habilidades_limpias = TextCleaner.limpiar_habilidades(resultado['habilidades_brutas'])
        
        # 3. Empaquetar datos completos
        datos_completos = {
            'termino_busqueda': termino_busqueda,
            'titulo_oferta': resultado['titulo_oferta'],
            'url': resultado['url'],
            'habilidades': habilidades_limpias,
            'fecha_extraccion': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return {
            'exito': True,
            'habilidades': habilidades_limpias,
            'titulo_oferta': resultado['titulo_oferta'],
            'datos_completos': datos_completos
        }

    def generar_resumen_ia(self, titulo: str, habilidades: List[str]) -> str:
        # Delegar a la IA
        return self.analyzer.generar_resumen(titulo, habilidades)

    def guardar_datos(self, datos: Dict, formato: str) -> List[str]:
        # Usar la fábrica para guardar
        rutas = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ruta_base = f"{self.directorio_salida}/linkedin_{timestamp}"
        
        if formato in ['1', '3']:
            exportador_json = ExporterFactory.obtener_exportador('json')
            rutas.append(exportador_json.exportar(datos, f"{ruta_base}.json"))
            
        if formato in ['2', '3']:
            exportador_excel = ExporterFactory.obtener_exportador('excel')
            rutas.append(exportador_excel.exportar(datos, f"{ruta_base}.xlsx"))
            
        return rutas