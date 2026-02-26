from typing import List
import gradio as gr
import pandas as pd

class CapaPresentacion:
    """
    Capa de Presentación: Maneja la interacción con el usuario usando Gradio.
    """
    
    def __init__(self):
        # Esta referencia se establecerá desde app.py
        self.capa_logica = None
    
    def set_capa_logica(self, capa_logica):
        """Establece la referencia a la capa de lógica de negocio"""
        self.capa_logica = capa_logica
    
    def _buscar_y_generar_descargas(self, termino_busqueda: str):
        """
        Función interna que llama la lógica de negocio y genera los archivos.
        """
        
        # 1. Estado INICIAL
        yield (
            "Iniciando búsqueda y análisis IA... (Esto puede tardar un poco)", # Estado
            None, # Título
            None, # Habilidades (DataFrame)
            "⏳ Esperando análisis de la IA...", # Resumen IA
            gr.DownloadButton(visible=False), # Botón JSON
            gr.DownloadButton(visible=False)  # Botón Excel
        )
        
        # 2. Ejecutar la lógica de negocio
        resultado = self.capa_logica.procesar_busqueda(termino_busqueda)
        
        if not resultado['exito']:
            # 3. Manejar error
            yield (
                f"[ERROR] {resultado['mensaje']}", 
                None, 
                None, 
                "❌ No se pudo generar el análisis.", 
                gr.DownloadButton(visible=False), 
                gr.DownloadButton(visible=False)
            )
            return

        # 4. Procesar resultados exitosos
        datos_completos = resultado['datos_completos']
        titulo = resultado['titulo_oferta']
        habilidades = resultado['habilidades']
        resumen = resultado['resumen_ia'] 
        
        # Convertir lista de habilidades a un DataFrame de Pandas
        df_habilidades = pd.DataFrame(habilidades, columns=["Habilidades Encontradas"])

        # Estado INTERMEDIO (Generando archivos)
        yield (
            "Búsqueda exitosa. Generando archivos...", 
            titulo, 
            df_habilidades, 
            resumen,
            gr.DownloadButton(visible=False), 
            gr.DownloadButton(visible=False)
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
                resumen,
                gr.DownloadButton(visible=False),
                gr.DownloadButton(visible=False)
            )
            return

        # 6. Finalizar y mostrar los botones
        yield (
            "¡Análisis completo! Archivos listos.", 
            titulo, 
            df_habilidades, 
            resumen, 
            gr.DownloadButton(
                label="Descargar JSON", 
                value=ruta_json, 
                visible=True
            ),
            gr.DownloadButton(
                label="Descargar Excel", 
                value=ruta_excel, 
                visible=True
            )
        )

    def lanzar_interfaz(self):
        """
        Construye y lanza la interfaz gráfica de Gradio.
        """
        with gr.Blocks(title="Analista de Vacantes LinkedIn con IA") as iface:
            gr.Markdown("# 🤖 Analista de Vacantes LinkedIn + ChatGPT")
            gr.Markdown("Ingresa un puesto (ej. 'Software Tester Linkedin') y la IA extraerá las habilidades y te dará un resumen estratégico.")

            with gr.Column():
                with gr.Row():
                    termino_input = gr.Textbox(
                        label="Puesto a buscar",
                        placeholder="Ej: React Frontend Developer",
                        scale=4
                    )
                    buscar_btn = gr.Button("🔍 Analizar Oferta", variant="primary", scale=1)
            
            gr.Markdown("---")
            
            with gr.Row():
                # Columna Izquierda: Datos crudos
                with gr.Column(scale=1):
                    status_output = gr.Textbox(
                        label="Estado del Sistema", 
                        interactive=False
                    )
                    titulo_output = gr.Textbox(
                        label="Título Detectado", 
                        interactive=False
                    )
                    # --- CAMBIO AQUÍ: Eliminamos height=400 ---
                    habilidades_output = gr.DataFrame(
                        headers=["Habilidades Detectadas"], 
                        interactive=False
                    )
                    
                    with gr.Row():
                        json_download_btn = gr.DownloadButton(
                            label="Descargar JSON", 
                            visible=False
                        )
                        excel_download_btn = gr.DownloadButton(
                            label="Descargar Excel", 
                            visible=False
                        )

                # Columna Derecha: Análisis de IA
                with gr.Column(scale=1):
                    gr.Markdown("### 🧠 Análisis de Inteligencia Artificial")
                    resumen_output = gr.Markdown(value="El análisis de la vacante aparecerá aquí...")

            # --- LÓGICA DE CLIC ---
            buscar_btn.click(
                fn=self._buscar_y_generar_descargas,
                inputs=[termino_input],
                outputs=[
                    status_output,
                    titulo_output,
                    habilidades_output,
                    resumen_output,
                    json_download_btn,
                    excel_download_btn
                ]
            )
        
        print("[INFO] Lanzando interfaz con IA...")
        iface.launch()