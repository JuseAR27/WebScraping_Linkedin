from presentacion.presentacion import CapaPresentacion
from logica_negocio.servicio_vacantes import JobService
from scraping.linkedin_scraper import LinkedInScraper

def main():
    try:
        # 1. Instanciar la Estrategia concreta que queremos usar hoy
        scraper_linkedin = LinkedInScraper()
        
        # 2. Instanciar el Servicio (Fachada) inyectando la estrategia
        servicio = JobService(scraper=scraper_linkedin)
        
        # 3. Configurar la Presentación
        presentacion = CapaPresentacion()
        presentacion.set_capa_logica(servicio) # Ahora recibe el JobService
        
        # 4. Iniciar
        presentacion.lanzar_interfaz()
        
    except Exception as e:
        print(f"Error fatal: {e}")

if __name__ == "__main__":
    main()