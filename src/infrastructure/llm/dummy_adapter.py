import time
import logging
from src.domain.llm_port import LLMPort

logger = logging.getLogger(__name__)

class DummyLLMAdapter(LLMPort):
    """
    Simulación de una IA para desarrollo y pruebas.
    Implementa el contrato de LLMPort.
    """
    def clasificar_ticket(self, texto: str) -> dict:
        logger.info("IA Dummy analizando ticket...")
        # Simulamos latencia de red
        time.sleep(1)
        
        texto = texto.lower()
        if "teclado" in texto or "pantalla" in texto or "impresora" in texto:
            return {"categoria": "Hardware", "prioridad": "Alta"}
        if "acceso" in texto or "bloque" in texto:
            return {"categoria": "Gestión de Accesos", "prioridad": "Crítica"}
            
        return {"categoria": "Sin Clasificar", "prioridad": "Media"}
