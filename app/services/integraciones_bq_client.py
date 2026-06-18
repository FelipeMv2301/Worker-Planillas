import httpx
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, before_sleep_log
from app.core.config import get_settings

logger = logging.getLogger("Integraciones-BQ")

class IntegracionesBQ:
    """
    Cliente que se conecta directamente a Integraciones-BQ para llamar específicamente al endpoint de STOCK
    Endpoint: GET /api/v1/stock/sap
    """

    def __init__(self):
        settings = get_settings()
        self.base_url = settings.full_integraciones_bq_url
        self.key_integraciones_bq = settings.key_integraciones_bq
        self.timeout = httpx.Timeout(300.0, connect=10.0)

    async def _post(self, endpoint: str, json: dict = None, params: dict = None, headers: dict = None):
        """
        Realiza una petición POST asíncrona al endpoint especificado.
        """
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(url, json=json, params=params, headers=headers)
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

    async def sync_stock_integraciones_bq(self):
        """
        Dispara la sincronización de stocks en la API principal.
        """

        headers = {
        "X-API-Key": self.key_integraciones_bq
        }

        return await self._post("/stock/sap", headers=headers)