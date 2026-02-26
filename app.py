from logica_negocio import logica
from presentacion import presentacion

def main():
    """
    Función principal que inicia el sistema
    """
    try:
        # Crear capa de presentación
        capa_presentacion = presentacion.CapaPresentacion()
        
        # Crear capa de lógica de negocio
        capa_logic = logica.CapaLogicaNegocio()
        
        # Conectar capas
        capa_presentacion.set_capa_logica(capa_logic)

        # Ejecutar sistema
        capa_presentacion.lanzar_interfaz()
        
    except KeyboardInterrupt:
        print("\n\n[SISTEMA] Operación cancelada por el usuario.")
    except Exception as e:
        print(f"\n[SISTEMA] Error fatal: {str(e)}")

if __name__ == "__main__":
    main()