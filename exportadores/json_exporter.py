import json
from typing import Dict
from .base_exporter import DataExporter

class JSONExporter(DataExporter):
    """
    Exportador responsable de guardar los diccionarios de datos en formato .json.
    """
    
    def exportar(self, datos: Dict, ruta_salida: str) -> str:
        """
        Guarda los datos en un archivo JSON usando la ruta proporcionada.
        """
        # Abrimos el archivo en modo escritura ('w') con soporte para caracteres latinos (utf-8)
        with open(ruta_salida, 'w', encoding='utf-8') as f:
            # ensure_ascii=False permite guardar acentos y ñ correctamente
            # indent=4 le da un formato legible para humanos
            json.dump(datos, f, ensure_ascii=False, indent=4)
        
        print(f"[DATOS] Archivo JSON guardado con éxito: {ruta_salida}")
        return ruta_salida