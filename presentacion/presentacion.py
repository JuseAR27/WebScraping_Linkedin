import gradio as gr
import pandas as pd

class CapaPresentacion:
    """
    Capa de Presentación: Maneja la interacción con el usuario usando Gradio.
    """
    
    def __init__(self):
        # Esta referencia ahora será un objeto de JobService (El Orquestador/Fachada)
        self.servicio = None
    
    def set_capa_logica(self, servicio):
        """Establece la referencia al servicio principal (JobService)"""
        self.servicio = servicio
    
    def _buscar_y_generar_descargas(self, termino_busqueda: str):
        """
        Función que llama al servicio, extrae datos y genera los archivos.
        """
        # 1. Estado INICIAL (Limpiando la pantalla)
        yield (
            "⏳ Iniciando búsqueda en LinkedIn... (Esto puede tardar unos segundos)", # Estado
            None, # Título
            None, # Habilidades (DataFrame)
            gr.Button(visible=False), # Ocultar botón IA
            gr.DownloadButton(visible=False), # Ocultar JSON
            gr.DownloadButton(visible=False), # Ocultar Excel
            [], # Limpiar estado interno
            "El análisis de la vacante aparecerá aquí..." # Limpiar resumen
        )
        
        # 2. Ejecutar la búsqueda en el servicio
        resultado = self.servicio.procesar_busqueda(termino_busqueda)
        
        if not resultado.get('exito', False):
            # 3. Manejar error
            yield (
                f"❌ [ERROR] {resultado.get('mensaje', 'Error desconocido')}", 
                None, None, 
                gr.Button(visible=False), gr.DownloadButton(visible=False), gr.DownloadButton(visible=False),
                [], "❌ Ocurrió un error en la búsqueda."
            )
            return

        # 4. Procesar resultados exitosos
        datos_completos = resultado['datos_completos']
        titulo = resultado['titulo_oferta']
        habilidades = resultado['habilidades']
        
        # Convertir a DataFrame para que Gradio lo muestre como tabla
        df_habilidades = pd.DataFrame(habilidades, columns=["Habilidades Encontradas"])

        # Estado INTERMEDIO
        yield (
            "✅ Búsqueda exitosa. Generando archivos de exportación...", 
            titulo, df_habilidades, 
            gr.Button(visible=False), gr.DownloadButton(visible=False), gr.DownloadButton(visible=False),
            habilidades, "Archivos generados. Puedes solicitar el resumen con IA."
        )

        # 5. Guardar los datos (Usando la Fábrica internamente)
        try:
            rutas = self.servicio.guardar_datos(datos_completos, '3') # '3' guarda ambos (JSON y Excel)
            ruta_json = next(r for r in rutas if r.endswith('.json'))
            ruta_excel = next(r for r in rutas if r.endswith('.xlsx'))
        except Exception as e:
            yield (
                f"⚠️ [ADVERTENCIA] Extracción exitosa, pero falló el guardado: {str(e)}",
                titulo, df_habilidades,
                gr.Button(visible=True), # Permitimos usar la IA aunque no se guarde
                gr.DownloadButton(visible=False), gr.DownloadButton(visible=False),
                habilidades, "Archivos no guardados, pero la IA está lista."
            )
            return

        # 6. Finalizar y mostrar todos los botones
        yield (
            "🎉 ¡Proceso completado! Archivos listos para descarga. ¿Deseas un resumen con IA?", 
            titulo, 
            df_habilidades, 
            gr.Button(visible=True), # Mostramos botón IA
            gr.DownloadButton(label="📥 Descargar JSON", value=ruta_json, visible=True),
            gr.DownloadButton(label="📊 Descargar Excel", value=ruta_excel, visible=True),
            habilidades, # Guardamos en memoria para la IA
            "Esperando acción..."
        )

    def _generar_resumen_ia(self, titulo: str, habilidades: list):
        """
        Detona la llamada a OpenAI solo cuando el usuario lo solicita.
        """
        if not titulo or not habilidades:
            yield "⚠️ No hay datos para analizar. Por favor, extrae una oferta primero."
            return
            
        yield "🧠 Analizando requerimientos con IA. Por favor espera..."
        
        resumen = self.servicio.generar_resumen_ia(titulo, habilidades)
        
        yield resumen

    def lanzar_interfaz(self):
        """
        Construye y lanza la interfaz web.
        """
        # Tema visual un poco más moderno
        tema = gr.themes.Soft(primary_hue="blue", secondary_hue="indigo")
        
        with gr.Blocks(title="Scraper de Vacantes LinkedIn", theme=tema) as iface:
            gr.Markdown("# 🤖 Extractor Inteligente de Vacantes en LinkedIn")
            gr.Markdown("Busca un puesto, extrae las habilidades técnicas requeridas y, de forma **opcional**, genera un análisis estratégico con ChatGPT.")

            # Estado oculto en la interfaz para pasar datos entre funciones
            state_habilidades = gr.State([])

            with gr.Row():
                termino_input = gr.Textbox(
                    label="Puesto a buscar",
                    placeholder="Ej: Node.js Backend Developer",
                    scale=4
                )
                buscar_btn = gr.Button("🔍 Extraer Datos", variant="primary", scale=1)
            
            gr.Markdown("---")
            
            with gr.Row():
                # Columna Izquierda (Resultados Crudos)
                with gr.Column(scale=1):
                    status_output = gr.Textbox(label="Estado del Sistema", interactive=False)
                    titulo_output = gr.Textbox(label="Título de la Oferta Detectada", interactive=False)
                    habilidades_output = gr.DataFrame(headers=["Habilidades Detectadas"], interactive=False)
                    
                    with gr.Row():
                        json_download_btn = gr.DownloadButton(label="📥 Descargar JSON", visible=False)
                        excel_download_btn = gr.DownloadButton(label="📊 Descargar Excel", visible=False)

                # Columna Derecha (Resumen de IA)
                with gr.Column(scale=1):
                    gr.Markdown("### 🧠 Análisis de Inteligencia Artificial")
                    resumen_btn = gr.Button("✨ Generar Resumen Estratégico", variant="secondary", visible=False)
                    resumen_output = gr.Markdown(value="El análisis de la vacante aparecerá aquí una vez que lo solicites...")

            # --- CONEXIÓN DE EVENTOS ---
            
            # 1. Al presionar "Extraer Datos"
            buscar_btn.click(
                fn=self._buscar_y_generar_descargas,
                inputs=[termino_input],
                outputs=[
                    status_output, titulo_output, habilidades_output,
                    resumen_btn, json_download_btn, excel_download_btn,
                    state_habilidades, resumen_output
                ]
            )
            
            # 2. Al presionar "Generar Resumen Estratégico"
            resumen_btn.click(
                fn=self._generar_resumen_ia,
                inputs=[titulo_output, state_habilidades],
                outputs=[resumen_output]
            )
        
        print("\n[SISTEMA] Iniciando interfaz gráfica...")
        iface.launch()