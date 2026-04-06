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

    async def _post(self, endpoint: str):
        """
        Realiza una petición POST asíncrona al endpoint especificado.
        """
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(url)
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
    async def send_emails(self):
        """
        Inicia la revisión de la planilla y el envío de correos autorizados.
        """
        return await self._post("/notificaciones-despacho/sheets/revisar-correos")

    @retry(
        stop=stop_after_attempt(3), 
        wait=wait_exponential(multiplier=1, min=2, max=10),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )
    async def sync_sap_retiros(self):
        """
        Sincroniza las órdenes de retiro en tienda desde ayer con Google Sheets.
        """
        return await self._post("/notificaciones-despacho/sap/sincronizar/retiros-hoy")

    @retry(
        stop=stop_after_attempt(3), 
        wait=wait_exponential(multiplier=1, min=2, max=10),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )
    async def sync_woo_recent(self, dias: int):
        """
        Inicia la sincronización masiva de pedidos recientes desde WooCommerce.
        """
        return await self._get("/notificaciones-despacho/woocommerce/sincronizar", params={"dias": dias})
