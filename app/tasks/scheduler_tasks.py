import logging
from datetime import datetime
from app.services.api_client import APIClient
from app.core.config import get_settings

logger = logging.getLogger("SchedulerTasks")
client = APIClient()
settings = get_settings()

async def sync_stocks_task():
    """
    Tarea programada para sincronizar el stock desde SAP hacia la planilla.
    """
    logger.info("Iniciando sincronización de stocks...")
    try:
        result = await client.sync_stocks()
        logger.info(f"[Stocks] {result.get('mensaje', 'Exito')}")
    except Exception as e:
        logger.error(f"Fallo sincronización de stocks: {e}")

async def sync_backorders_task():
    """
    Tarea programada para sincronizar pedidos pendientes enriquecidos.
    """
    logger.info("Iniciando sincronización de backorders...")
    try:
        result = await client.sync_backorders()
        logger.info(f"[Backorders] {result.get('mensaje', 'Exito')}")
    except Exception as e:
        logger.error(f"Fallo sincronización de backorders: {e}")

async def send_emails_task():
    """
    Tarea programada para revisar la planilla y disparar correos autorizados.
    """
    logger.info("Iniciando revisión y envío de correos...")
    try:
        result = await client.send_emails()
        logger.info(f"[Correos] {result.get('detalle', 'Revision en segundo plano lanzada.')}")
    except Exception as e:
        logger.error(f"Fallo envío de correos: {e}")

async def sync_sap_retiros_task():
    """
    Tarea programada para sincronizar retiros en tienda de SAP hacia la planilla.
    """
    logger.info("Iniciando sincronización de retiros SAP...")
    try:
        result = await client.sync_sap_retiros()
        logger.info(f"[SAP Retiros] Sincronización completada.")
    except Exception as e:
        logger.error(f"Fallo sincronización de retiros SAP: {e}")

async def sync_woo_recent_task():
    """
    Tarea programada para la sincronización masiva periódica de WooCommerce.
    """
    logger.info(f"Iniciando sincronización de WooCommerce (ultimos {settings.WOO_SYNC_DAYS} días)...")
    try:
        result = await client.sync_woo_recent(dias=settings.WOO_SYNC_DAYS)
        total = result.get('total_procesados', 0)
        logger.info(f"[Woo] Sincronización masiva terminada. Procesados: {total}")
    except Exception as e:
        logger.error(f"Fallo sincronización masiva WooCommerce: {e}")

async def sync_cotizaciones_task():
    """
    Tarea programada para cargar cotizaciones del día actual desde SAP.
    """
    hoy = datetime.now().strftime("%Y-%m-%d")
    logger.info(f"Iniciando carga de cotizaciones para el día {hoy}...")
    try:
        result = await client.sync_cotizaciones(fecha_desde=hoy, fecha_hasta=hoy)
        total = result.get('total_procesados', 0)
        logger.info(f"[Cotizaciones] Sync completado. Procesadas: {total}")
    except Exception as e:
        logger.error(f"Fallo carga de cotizaciones: {e}")
