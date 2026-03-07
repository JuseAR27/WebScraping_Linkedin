from flask import Flask, render_template, request, jsonify, send_from_directory
from logica_negocio.servicio_vacantes import JobService
from scraping.linkedin_scraper import LinkedInScraper
import os

app = Flask(__name__)

# Configuración de los servicios
scraper = LinkedInScraper()
servicio = JobService(scraper=scraper) #

@app.route('/')
def index():
    """Ruta principal: Muestra el formulario de búsqueda."""
    return render_template('index.html')

@app.route('/buscar', methods=['POST'])
def buscar():
    """Ruta para ejecutar el scraping."""
    termino = request.form.get('puesto')
    resultado = servicio.procesar_busqueda(termino) #
    
    if resultado['exito']:
        rutas = servicio.guardar_datos(resultado['datos_completos'], '3') 
        resultado['rutas_archivos'] = rutas
        return jsonify(resultado)
    return jsonify({"error": resultado['mensaje']}), 400

@app.route('/analizar_ia', methods=['POST'])
def analizar_ia():
    """Ruta para solicitar el resumen de ChatGPT."""
    datos = request.json
    resumen = servicio.generar_resumen_ia(datos['titulo'], datos['habilidades'])
    return jsonify({"resumen": resumen})

@app.route('/descargar/<filename>')
def descargar(filename):
    """Ruta para descargar los archivos generados."""
    return send_from_directory('datos_extraidos', filename) #

if __name__ == '__main__':
    app.run(debug=True)