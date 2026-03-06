from .json_exporter import JSONExporter
from .excel_exporter import ExcelExporter

class ExporterFactory:
    """Fábrica que decide qué exportador instanciar."""
    
    @staticmethod
    def obtener_exportador(formato: str):
        if formato == 'json':
            return JSONExporter()
        elif formato == 'excel':
            return ExcelExporter()
        else:
            raise ValueError(f"Formato {formato} no soportado")