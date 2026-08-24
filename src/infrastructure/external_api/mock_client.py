import os
import httpx
from dotenv import load_dotenv
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential
import logging

logger = logging.getLogger(__name__)
load_dotenv()

def should_retry(exception):
    """
    Decide si debemos reintentar la petición.
    Reintentamos si es:
    - Timeout o error de conexión
    - HTTP 500 (Error del proveedor)
    - HTTP 429 (Rate limit)
    """
    if isinstance(exception, (httpx.TimeoutException, httpx.ConnectError)):
        return True
    if isinstance(exception, httpx.HTTPStatusError):
        return exception.response.status_code in [500, 429]
    return False

class MockAPIClient:
    def __init__(self, base_url: str | None = None, token: str | None = None):
        self.base_url = (base_url or os.getenv('MOCK_API_BASE_URL', 'http://localhost:8080')).rstrip('/')
        token = token or os.getenv('MOCK_API_TOKEN')
        if not token:
            raise ValueError('Falta MOCK_API_TOKEN. Defínelo en el archivo .env local.')
        # El timeout es 3.0s porque la especificación dice que la latencia llega a 2.5s.
        self.timeout = httpx.Timeout(3.0) 
        # La spec requiere Bearer Token para los endpoints (excepto /health)
        self.headers = {"Authorization": f"Bearer {token}"}

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception(should_retry),
        reraise=True,
        before_sleep=lambda retry_state: logger.warning(
            'Fallo transitorio. Reintentando... (Intento %s)', retry_state.attempt_number
        )
    )
    def _request(self, method: str, endpoint: str, **kwargs):
        url = f"{self.base_url}{endpoint}"
        try:
            with httpx.Client(timeout=self.timeout, headers=self.headers) as client:
                response = client.request(method, url, **kwargs)
                response.raise_for_status()
                return response.json() if response.content else {"status": response.status_code}
                
        except httpx.HTTPStatusError as e:
            status = e.response.status_code
            if status == 429:
                logger.warning(f"Límite de tasa (429) en {url}.")
                raise
            elif status == 500:
                logger.warning(f"Error interno (500) del servicio mock en {url}.")
                raise
            else:
                logger.error(f"Error HTTP {status} no recuperable en {url}. Detalles: {e.response.text}")
                raise
                
        except httpx.RequestError as e:
            logger.error(f"Error de red/Timeout hacia {url}: {str(e)}")
            raise

    def get_solicitudes(self, area: str = None, estado: str = None, limite: int = 50):
        """Obtiene la lista de solicitudes con filtros opcionales"""
        params = {"limite": limite}
        if area:
            params["area"] = area
        if estado:
            params["estado"] = estado
        return self._request("GET", "/solicitudes", params=params)
        
    def get_solicitud(self, id_solicitud: str):
        """Obtiene una solicitud por ID"""
        return self._request("GET", f"/solicitudes/{id_solicitud}")
        
    def create_solicitud(self, asunto: str, area: str, solicitante: str, descripcion: str = ""):
        """Crea una nueva solicitud (Valida según OpenAPI schema)"""
        payload = {
            "asunto": asunto[:200],
            "area": area[:80],
            "solicitante": solicitante[:120],
            "descripcion": descripcion[:4000],
            "canal": "api"
        }
        return self._request("POST", "/solicitudes", json=payload)
