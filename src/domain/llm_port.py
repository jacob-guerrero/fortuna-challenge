from abc import ABC, abstractmethod

class LLMPort(ABC):
    """
    Puerto (Interfaz) para interactuar con modelos de lenguaje (IA).
    Asegura que el sistema esté desacoplado del proveedor específico.
    """
    @abstractmethod
    def clasificar_ticket(self, texto: str) -> dict:
        """
        Analiza el texto de un ticket y devuelve un diccionario 
        con las claves 'categoria' y 'prioridad'.
        """
        pass
