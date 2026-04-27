import httpx
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, before_sleep_log
from app.core.config import get_settings

logger = logging.getLogger("APIClient")

class APIClient:
    """
    Cliente asíncrono para gestionar las peticiones HTTP hacia la API-Planillas-1.
    Utiliza HTTPX.AsyncClient para una mejor gestión de recursos y concurrencia.
    """
    def __init__(self):
        settings = get_settings()
        self.base_url = settings.full_api_url
        self.timeout = httpx.Timeout(120.0, connect=10.0)

    async def _post(self, endpoint: str, json: dict = None, params: dict = None):
        """
        Realiza una petición POST asíncrona al endpoint especificado.
        """
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(url, json=json, params=params)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"Error HTTP en {url}: {e.response.status_code} - {e.response.text}")
                raise
            except Exception as e:
                logger.error(f"Error de conexión en {url}: {type(e).__name__} - {str(e)}")
                raise

    async def _get(self, endpoint: str, params: dict = None):
        """
        Realiza una petición GET asíncrona al endpoint especificado.
        """
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"Error HTTP en {url}: {e.response.status_code} - {e.response.text}")
                raise
            except Exception as e:
                logger.error(f"Error de conexión en {url}: {type(e).__name__} - {str(e)}")
                raise

    @retry(
        stop=stop_after_attempt(3), 
        wait=wait_exponential(multiplier=1, min=2, max=10),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )
    async def sync_stocks(self):
        """
        Dispara la sincronización de stocks en la API principal.
        """
        return await self._post("/visualizador-stock/sync-stock")

    @retry(
        stop=stop_after_attempt(3), 
        wait=wait_exponential(multiplier=1, min=2, max=10),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )
    async def sync_backorders(self):
        """
        Dispara la sincronización de pedidos pendientes (backorders) en la API principal.
        """
        return await self._post("/visualizador-stock/sync-backorders")


    @retry(
        stop=stop_after_attempt(3), 
        wait=wait_exponential(multiplier=1, min=2, max=10),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )
    async def send_billing_email(self, order_id: str):
        """
        Delega a la API-Planillas-1 el envío del correo de notificación de facturación (Brevo).
        """
        return await self._post(f"/facturacion/ordenes/{order_id}/reenviar-correo")

    @retry(
        stop=stop_after_attempt(3), 
        wait=wait_exponential(multiplier=1, min=2, max=10),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )
    async def sync_pipeline(self, fecha_desde: str, fecha_hasta: str):
        """
        Solicita a la API principal la sincronización del Pipeline Comercial.
        """
        params = {
            "fecha_desde": fecha_desde,
            "fecha_hasta": fecha_hasta
        }
        return await self._post("/comercial/pipeline", params=params)

    @retry(
        stop=stop_after_attempt(3), 
        wait=wait_exponential(multiplier=1, min=2, max=10),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )
    async def sync_ventas_margen(self, fecha_desde: str, fecha_hasta: str):
        """
        Solicita a la API principal la carga de ventas con margen por rango de fechas.
        """
        payload = {
            "fecha_desde": fecha_desde,
            "fecha_hasta": fecha_hasta
        }
        return await self._post("/comercial/ventas-con-margen", json=payload)
