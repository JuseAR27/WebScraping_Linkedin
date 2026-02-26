import json
import os
from datetime import datetime
from typing import Dict
import pandas as pd

class CapaAccesoDatos:
    """
    Capa de Acceso a Datos: Maneja el almacenamiento persistente
    Recibe: Solicitudes de datos de la Capa de Lógica
    Procesa: Guarda en JSON/XLS (Pandas)
    Salida: Datos brutos guardados hacia la Capa de Lógica de Negocio
    """
    
    def __init__(self):
        self.directorio_salida = "datos_extraidos"
        self._crear_directorio()
    
    def _crear_directorio(self):
        """Crea el directorio de salida si no existe"""
        import os
        if not os.path.exists(self.directorio_salida):
            os.makedirs(self.directorio_salida)
    
    def _generar_nombre_archivo(self, extension: str) -> str:
        """Genera un nombre de archivo único con timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{self.directorio_salida}/habilidades_linkedin_{timestamp}.{extension}"
    
    def guardar_json(self, datos: Dict) -> str:
        """
        Guarda los datos en formato JSON
        """
        ruta = self._generar_nombre_archivo("json")
        
        with open(ruta, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=4)
        
        print(f"[DATOS] Archivo JSON guardado: {ruta}")
        return ruta
    
    def guardar_excel(self, datos: Dict) -> str:
        """
        Guarda los datos en formato Excel usando Pandas
        """
        ruta = self._generar_nombre_archivo("xlsx")
        
        # Crear DataFrame con las habilidades
        df_habilidades = pd.DataFrame({
            'Número': range(1, len(datos['habilidades']) + 1),
            'Habilidad': datos['habilidades']
        })
        
        # Crear DataFrame con información general
        df_info = pd.DataFrame({
            'Campo': ['Término de Búsqueda', 'Título de la Oferta', 'URL', 
                     'Fecha de Extracción', 'Total de Habilidades'],
            'Valor': [
                datos['termino_busqueda'],
                datos['titulo_oferta'],
                datos['url'],
                datos['fecha_extraccion'],
                datos['total_habilidades']
            ]
        })
        
        # Guardar en Excel con múltiples hojas
        with pd.ExcelWriter(ruta, engine='openpyxl') as writer:
            df_info.to_excel(writer, sheet_name='Información General', index=False)
            df_habilidades.to_excel(writer, sheet_name='Habilidades', index=False)
        
        print(f"[DATOS] Archivo Excel guardado: {ruta}")
        return ruta