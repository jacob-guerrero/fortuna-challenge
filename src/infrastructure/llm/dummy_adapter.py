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
        categoria = "Sin Clasificar"
        prioridad = "Media"
        if "teclado" in texto or "pantalla" in texto or "impresora" in texto:
            categoria, prioridad = "Hardware", "Alta"
        elif "acceso" in texto or "bloque" in texto:
            categoria, prioridad = "Gestión de Accesos", "Crítica"
            
        return {
            "categoria": categoria,
            "prioridad": prioridad,
            "respuesta_usuario": "Esta es una respuesta simulada por el sistema Dummy.",
            "resumen_tecnico": "Resumen simulado (Dummy Mode)."
        }
