from abc import ABC, abstractmethod
from typing import Dict

class ScraperStrategy(ABC):
    """Interfaz base para cualquier scraper de vacantes."""
    
    @abstractmethod
    def extraer_datos(self, termino_busqueda: str) -> Dict:
        """Debe retornar un diccionario con el éxito, título, url y habilidades brutas."""
        pass