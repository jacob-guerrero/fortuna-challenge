import logging
from src.infrastructure.external_api.mock_client import MockAPIClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_demo():
    client = MockAPIClient()
    
    logger.info("--- Probando GET /solicitudes (Sin filtros) ---")
    try:
        solicitudes = client.get_solicitudes(limite=5)
        logger.info("Éxito! GET (todas) respondió correctamente.")
    except Exception as e:
        logger.error(f"El GET falló irremediablemente: {str(e)}")

    logger.info("\n--- Probando GET /solicitudes (Filtrado por Área) ---")
    try:
        solicitudes_area = client.get_solicitudes(area="Operaciones", limite=5)
        logger.info("Éxito! GET (con filtros) respondió correctamente.")
    except Exception as e:
        logger.error(f"El GET filtrado falló: {str(e)}")

    logger.info("\n--- Probando POST /solicitudes (Solicitud Válida) ---")
    try:
        response = client.create_solicitud(
            asunto="El teclado dejó de funcionar",
            area="Operaciones",
            solicitante="empleado1@lafortuna.com.co",
            descripcion="El teclado presenta intermitencia desde el lunes."
        )
        logger.info(f"Éxito! POST respondió correctamente: {response}")
    except Exception as e:
        logger.error(f"El POST falló irremediablemente: {str(e)}")
        
    logger.info("\n--- Probando POST /solicitudes (Lanzar error de validación 422 a propósito) ---")
    try:
        # Falla porque el asunto debe tener minLength: 5
        client.create_solicitud(asunto="A", area="TI", solicitante="abc")
    except Exception as e:
        logger.info(f"Error! La API rechazó los datos inválidos: {str(e)}")

if __name__ == "__main__":
    logger.info("Iniciando consumo de API Mock. (Ejecuta 'python -m uvicorn servicio_mock.app:app --port 8080' en otra terminal)")
    run_demo()
