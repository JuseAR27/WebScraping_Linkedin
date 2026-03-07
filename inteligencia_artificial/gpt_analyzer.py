import os
from typing import List
from openai import OpenAI
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

class AIAnalyzer:
    """
    Clase responsable de la comunicación con modelos de Inteligencia Artificial (OpenAI).
    """
    
    def __init__(self):
        # Buscamos la llave de API en las variables de entorno
        api_key = os.getenv("OPENAI_API_KEY")
        
        # Inicializamos el cliente solo si existe la llave
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            self.client = None
            print("[IA] Advertencia: No se encontró OPENAI_API_KEY en el archivo .env")

    def generar_resumen(self, titulo: str, habilidades: List[str]) -> str:
        """
        Envía las habilidades a ChatGPT para obtener un resumen profesional estructurado.
        """
        # Verificación de seguridad por si no hay API Key
        if not self.client:
            return "⚠️ No se ha configurado la API Key de OpenAI. Crea un archivo .env con OPENAI_API_KEY=..."

        # Verificación de seguridad por si la lista de habilidades está vacía
        if not habilidades:
            return "⚠️ No se encontraron habilidades para analizar."

        try:
            print("[IA] Generando resumen con ChatGPT...")
            
            # Convertimos la lista a texto (Limitamos a las primeras 30 para ahorrar tokens/dinero)
            lista_texto = "\n- ".join(habilidades[:30]) 
            
            # Construcción del Prompt (Instrucciones para la IA)
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

            # Llamada a la API de OpenAI
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo", # Si es neccesario, se puede actualizar a gpt-4o-mini o gpt-4
                messages=[
                    {"role": "system", "content": "Eres un asistente experto en RRHH y tecnología."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # Retornamos el contenido del mensaje generado
            return response.choices[0].message.content

        except Exception as e:
            # Manejo de errores en la comunicación con la API
            return f"❌ Error al consultar ChatGPT: {str(e)}"