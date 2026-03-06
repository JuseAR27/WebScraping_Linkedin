import pandas as pd
from typing import Dict
from .base_exporter import DataExporter

class ExcelExporter(DataExporter):
    """
    Exportador responsable de guardar los diccionarios de datos en formato .xlsx usando Pandas.
    """
    
    def exportar(self, datos: Dict, ruta_salida: str) -> str:
        """
        Crea DataFrames de Pandas y los guarda en múltiples hojas de un Excel.
        """
        # 1. Crear DataFrame para la lista de habilidades
        df_habilidades = pd.DataFrame({
            'Número': range(1, len(datos['habilidades']) + 1),
            'Habilidad': datos['habilidades']
        })
        
        # 2. Crear DataFrame para el resumen general de la oferta
        df_info = pd.DataFrame({
            'Campo': [
                'Término de Búsqueda', 
                'Título de la Oferta', 
                'URL', 
                'Fecha de Extracción', 
                'Total de Habilidades'
            ],
            'Valor': [
                datos.get('termino_busqueda', 'N/A'),
                datos.get('titulo_oferta', 'N/A'),
                datos.get('url', 'N/A'),
                datos.get('fecha_extraccion', 'N/A'),
                len(datos.get('habilidades', []))
            ]
        })
        
        # 3. Guardar en Excel creando diferentes pestañas (hojas)
        # Usamos openpyxl como motor (engine) para escribir el .xlsx
        with pd.ExcelWriter(ruta_salida, engine='openpyxl') as writer:
            df_info.to_excel(writer, sheet_name='Información General', index=False)
            df_habilidades.to_excel(writer, sheet_name='Habilidades', index=False)
        
        print(f"[DATOS] Archivo Excel guardado con éxito: {ruta_salida}")
        return ruta_salida