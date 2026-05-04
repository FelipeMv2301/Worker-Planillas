import logging
from datetime import datetime, timedelta
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


async def sync_ventas_margen_task():
    """
    Tarea programada para cargar ventas con margen (ayer y hoy) desde SAP.
    """
    ahora = datetime.now()
    hoy = ahora.strftime("%d-%m-%Y")
    ayer = (ahora - timedelta(days=1)).strftime("%d-%m-%Y")

    logger.info(f"[Ventas-Margen] Iniciando sincronización para el rango: {ayer} al {hoy}...")
    try:
        result = await client.sync_ventas_margen(fecha_desde=ayer, fecha_hasta=hoy)
        total = result.get('total_procesados', 0)
        logger.info(f"[Ventas-Margen] Finalizado. Registros procesados: {total}")
    except Exception as e:
        logger.error(f"[Ventas-Margen] Falló la sincronización: {e}")

async def sync_pipeline_task():
    """
    Tarea programada para sincronizar el Pipeline Comercial (ayer y hoy).
    """
    ahora = datetime.now()
    hoy = ahora.strftime("%d-%m-%Y")
    ayer = (ahora - timedelta(days=30)).strftime("%d-%m-%Y")

    logger.info(f"[Pipeline] Iniciando sincronización para el rango: {ayer} al {hoy}...")
    try:
        result = await client.sync_pipeline(fecha_desde=ayer, fecha_hasta=hoy)
        total = result.get('total_procesados', 0)
        logger.info(f"[Pipeline] Finalizado. Cotizaciones sincronizadas: {total}")
    except Exception as e:
        logger.error(f"[Pipeline] Falló la sincronización: {e}")

async def sync_guias_abiertas_task():
    """
    Tarea programada para sincronizar las Guías Abiertas de Contabilidad (ayer y hoy).
    """
    ahora = datetime.now()
    hoy = ahora.strftime("%Y-%m-%d")
    ayer = (ahora - timedelta(days=1)).strftime("%Y-%m-%d")

    logger.info(f"[Guias-Abiertas] Iniciando sincronización para el rango: {ayer} al {hoy}...")
    try:
        result = await client.sync_guias_abiertas(fecha_desde=ayer, fecha_hasta=hoy)
        total = result.get('total_extraidas', 0)
        logger.info(f"[Guias-Abiertas] Finalizado. Guías procesadas: {total}")
    except Exception as e:
        logger.error(f"[Guias-Abiertas] Falló la sincronización: {e}")
