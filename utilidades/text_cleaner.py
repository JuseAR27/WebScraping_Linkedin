import re
from typing import List

class TextCleaner:
    """
    Clase de utilidad responsable de procesar, limpiar y filtrar 
    el texto extraído de las vacantes.
    """
    
    @staticmethod
    def limpiar_habilidades(habilidades: List[str]) -> List[str]:
        """
        Limpia espacios, elimina caracteres especiales no deseados 
        y filtra palabras comunes del diseño de la página.
        """
        limpiadas = []
        vistas = set()
        
        # Palabras que suelen aparecer por el scraping pero no son habilidades
        palabras_excluir = [
            'click', 'show', 'more', 'less', 'see', 'view', 
            'apply', 'job', 'description', 'ver', 'más'
        ]
        
        for habilidad in habilidades:
            # 1. Limpiar espacios extra y saltos de línea
            limpia = re.sub(r'\s+', ' ', habilidad).strip()
            
            # 2. Eliminar caracteres especiales (manteniendo los técnicos como # o +)
            limpia = re.sub(r'[^\w\s\+\#\.-_,\(\)]', '', limpia) 
            
            # 3. Validaciones de calidad
            if len(limpia) < 3 or len(limpia) > 250: 
                continue
                
            if limpia.lower() in palabras_excluir: 
                continue
            
            # 4. Evitar duplicados (case-insensitive)
            if limpia.lower() not in vistas:
                vistas.add(limpia.lower())
                limpiadas.append(limpia)
                
        return limpiadas