from typing import List
import gradio as gr
import pandas as pd

class CapaPresentacion:
    """
    Capa de Presentación: Maneja la interacción con el usuario usando Gradio.
    """
    
    def __init__(self):
        self.capa_logica = None
    
    def set_capa_logica(self, capa_logica):
        """Establece la referencia a la capa de lógica de negocio"""
        self.capa_logica = capa_logica
    
    def _buscar_y_generar_descargas(self, termino_busqueda: str):
        """
        Función que llama la lógica de negocio, extrae datos y genera los archivos.
        """
        # 1. Estado INICIAL
        yield (
            "Iniciando búsqueda en LinkedIn... (Esto puede tardar un poco)", # status_output
            None, # titulo_output
            None, # habilidades_output
            gr.Button(visible=False), # resumen_btn (Oculto)
            gr.DownloadButton(visible=False), # json_download_btn
            gr.DownloadButton(visible=False), # excel_download_btn
            [], # state_habilidades (Vacío)
            "El análisis de la vacante aparecerá aquí..." # Limpiar resumen
        )
        
        # 2. Ejecutar la lógica de negocio
        resultado = self.capa_logica.procesar_busqueda(termino_busqueda)
        
        if not resultado['exito']:
            # 3. Manejar error
            yield (
                f"[ERROR] {resultado['mensaje']}", 
                None, 
                None, 
                gr.Button(visible=False), 
                gr.DownloadButton(visible=False), 
                gr.DownloadButton(visible=False),
                [],
                "❌ Ocurrió un error en la búsqueda."
            )
            return

        # 4. Procesar resultados exitosos
        datos_completos = resultado['datos_completos']
        titulo = resultado['titulo_oferta']
        habilidades = resultado['habilidades']
        
        # Convertir lista de habilidades a un DataFrame de Pandas
        df_habilidades = pd.DataFrame(habilidades, columns=["Habilidades Encontradas"])

        # Estado INTERMEDIO (Generando archivos)
        yield (
            "Búsqueda exitosa. Generando archivos...", 
            titulo, 
            df_habilidades, 
            gr.Button(visible=False), 
            gr.DownloadButton(visible=False), 
            gr.DownloadButton(visible=False),
            habilidades, # Guardamos la lista en el estado
            "Archivos generados. Puedes solicitar el resumen con IA."
        )

        # 5. Guardar los datos
        try:
            rutas = self.capa_logica.guardar_datos(datos_completos, '3')
            ruta_json = next(r for r in rutas if r.endswith('.json'))
            ruta_excel = next(r for r in rutas if r.endswith('.xlsx'))
        except Exception as e:
            yield (
                f"[ERROR] No se pudieron guardar los archivos: {str(e)}",
                titulo,
                df_habilidades,
                gr.Button(visible=True), # Permitir IA aunque fallen los archivos
                gr.DownloadButton(visible=False),
                gr.DownloadButton(visible=False),
                habilidades,
                "Archivos no guardados, pero puedes solicitar el resumen."
            )
            return

        # 6. Finalizar y mostrar los botones
        yield (
            "¡Extracción completa! Archivos listos. Puedes generar un resumen con IA si lo deseas.", 
            titulo, 
            df_habilidades, 
            gr.Button(visible=True), # Mostramos el botón de IA
            gr.DownloadButton(label="Descargar JSON", value=ruta_json, visible=True),
            gr.DownloadButton(label="Descargar Excel", value=ruta_excel, visible=True),
            habilidades, # Mantenemos las habilidades en estado
            "Esperando acción del usuario..."
        )

    def _generar_resumen_ia(self, titulo: str, habilidades: list):
        """
        Función que se ejecuta al presionar el botón de IA.
        """
        if not titulo or not habilidades:
            yield "⚠️ No hay datos para analizar. Realiza una búsqueda primero."
            return
            
        yield "⏳ Analizando con Inteligencia Artificial. Por favor espera..."
        
        # Llamamos al nuevo método público de la capa de lógica
        resumen = self.capa_logica.generar_resumen_ia(titulo, habilidades)
        
        yield resumen

    def lanzar_interfaz(self):
        """
        Construye y lanza la interfaz gráfica de Gradio.
        """
        with gr.Blocks(title="Analista de Vacantes LinkedIn con IA") as iface:
            gr.Markdown("# 🤖 Analista de Vacantes LinkedIn + ChatGPT")
            gr.Markdown("Ingresa un puesto (ej. 'Software Tester Linkedin'), extrae las habilidades y **opcionalmente** genera un resumen con IA.")

            # Variable de estado oculta para almacenar las habilidades en crudo
            state_habilidades = gr.State([])

            with gr.Column():
                with gr.Row():
                    termino_input = gr.Textbox(
                        label="Puesto a buscar",
                        placeholder="Ej: React Frontend Developer",
                        scale=4
                    )
                    buscar_btn = gr.Button("🔍 Extraer Oferta", variant="primary", scale=1)
            
            gr.Markdown("---")
            
            with gr.Row():
                # Columna Izquierda: Datos crudos
                with gr.Column(scale=1):
                    status_output = gr.Textbox(label="Estado del Sistema", interactive=False)
                    titulo_output = gr.Textbox(label="Título Detectado", interactive=False)
                    habilidades_output = gr.DataFrame(headers=["Habilidades Detectadas"], interactive=False)
                    
                    with gr.Row():
                        json_download_btn = gr.DownloadButton(label="Descargar JSON", visible=False)
                        excel_download_btn = gr.DownloadButton(label="Descargar Excel", visible=False)

                # Columna Derecha: Análisis de IA
                with gr.Column(scale=1):
                    gr.Markdown("### 🧠 Análisis de Inteligencia Artificial")
                    # Botón para detonar la IA, oculto por defecto
                    resumen_btn = gr.Button("✨ Generar Resumen con IA", variant="secondary", visible=False)
                    resumen_output = gr.Markdown(value="El análisis de la vacante aparecerá aquí...")

            # --- LÓGICA DE EVENTOS (CLICS) ---
            
            # Evento 1: Botón de buscar (Solo Scraping)
            buscar_btn.click(
                fn=self._buscar_y_generar_descargas,
                inputs=[termino_input],
                outputs=[
                    status_output,
                    titulo_output,
                    habilidades_output,
                    resumen_btn,          # Mostraremos este botón al terminar
                    json_download_btn,
                    excel_download_btn,
                    state_habilidades,    # Guardamos las habilidades extraídas
                    resumen_output        # Reiniciamos el texto
                ]
            )
            
            # Evento 2: Botón de Resumen con IA (Solo API OpenAI)
            resumen_btn.click(
                fn=self._generar_resumen_ia,
                inputs=[titulo_output, state_habilidades],
                outputs=[resumen_output]
            )
        
        print("[INFO] Lanzando interfaz con IA...")
        iface.launch()