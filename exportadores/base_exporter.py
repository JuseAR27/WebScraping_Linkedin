from abc import ABC, abstractmethod
from typing import Dict

class DataExporter(ABC):
    @abstractmethod
    def exportar(self, datos: Dict, ruta_salida: str) -> str:
        pass