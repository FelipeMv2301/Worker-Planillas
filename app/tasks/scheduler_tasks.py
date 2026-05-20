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
    Tarea programada para cargar ventas con margen (SOLO AYER Y HOY).
    Sincronización rápida frecuente.
    """
    ahora = datetime.now()
    hoy = ahora.strftime("%d-%m-%Y")
    ayer = (ahora - timedelta(days=1)).strftime("%d-%m-%Y")

    logger.info(f"[Ventas-Hoy] Sincronización rápida: {ayer} al {hoy}...")
    try:
        result = await client.sync_ventas_margen(fecha_desde=ayer, fecha_hasta=hoy)
        total = result.get('total_procesados', 0)
        logger.info(f"[Ventas-Hoy] Finalizado. Registros procesados: {total}")
    except Exception as e:
        logger.error(f"[Ventas-Hoy] Falló la sincronización rápida: {e}")

async def sync_ventas_margen_deep_task():
    """
    Tarea programada para cargar ventas con margen (REVISIÓN PROFUNDA: 60 DÍAS).
    Se ejecuta pocas veces al día para capturar anulaciones o cambios antiguos.
    """
    ahora = datetime.now()
    hoy = ahora.strftime("%d-%m-%Y")
    desde = (ahora - timedelta(days=60)).strftime("%d-%m-%Y")

    logger.info(f"[Ventas-60D] Iniciando revisión profunda: {desde} al {hoy}...")
    try:
        result = await client.sync_ventas_margen(fecha_desde=desde, fecha_hasta=hoy)
        total = result.get('total_procesados', 0)
        logger.info(f"[Ventas-60D] Finalizado. Registros actualizados: {total}")
    except Exception as e:
        logger.error(f"[Ventas-60D] Falló la revisión profunda: {e}")

async def sync_pipeline_task():
    """
    Tarea programada para sincronizar el Pipeline Comercial (REVISIÓN PROFUNDA: 60 días).
    Se ejecuta pocas veces al día para corregir estados de cotizaciones antiguas.
    """
    ahora = datetime.now()
    hoy = ahora.strftime("%d-%m-%Y")
    desde = (ahora - timedelta(days=60)).strftime("%d-%m-%Y")

    logger.info(f"[Pipeline-60D] Iniciando revisión profunda: {desde} al {hoy}...")
    try:
        result = await client.sync_pipeline(fecha_desde=desde, fecha_hasta=hoy)
        total = result.get('total_procesados', 0)
        logger.info(f"[Pipeline-60D] Finalizado. Cotizaciones actualizadas: {total}")
    except Exception as e:
        logger.error(f"[Pipeline-60D] Falló la revisión profunda: {e}")

async def sync_pipeline_hoy_task():
    """
    Tarea programada para sincronizar el Pipeline Comercial (SOLO HOY).
    Se ejecuta frecuentemente para capturar nuevas cotizaciones al instante.
    """
    hoy = datetime.now().strftime("%d-%m-%Y")

    logger.info(f"[Pipeline-Hoy] Sincronizando cotizaciones del día: {hoy}...")
    try:
        result = await client.sync_pipeline(fecha_desde=hoy, fecha_hasta=hoy)
        total = result.get('total_procesados', 0)
        logger.info(f"[Pipeline-Hoy] Finalizado. Nuevos registros: {total}")
    except Exception as e:
        logger.error(f"[Pipeline-Hoy] Falló la sincronización rápida: {e}")

async def sync_guias_abiertas_hoy_task():
    """
    Tarea programada para sincronizar las Guías Abiertas (AYER Y HOY).
    Sincronización rápida frecuente.
    """
    ahora = datetime.now()
    hoy = ahora.strftime("%d-%m-%Y")
    ayer = (ahora - timedelta(days=1)).strftime("%d-%m-%Y")

    logger.info(f"[Guias-Hoy] Sincronización rápida: {ayer} al {hoy}...")
    try:
        result = await client.sync_guias_abiertas(fecha_desde=ayer, fecha_hasta=hoy)
        total = result.get('total_extraidas', 0)
        logger.info(f"[Guias-Hoy] Finalizado. Guías procesadas: {total}")
    except Exception as e:
        logger.error(f"[Guias-Hoy] Falló la sincronización rápida: {e}")

async def sync_guias_abiertas_deep_task():
    """
    Tarea programada para sincronizar las Guías Abiertas (REVISIÓN PROFUNDA: 30 DÍAS).
    Se ejecuta pocas veces al día.
    """
    ahora = datetime.now()
    hoy = ahora.strftime("%d-%m-%Y")
    desde = (ahora - timedelta(days=30)).strftime("%d-%m-%Y")

    logger.info(f"[Guias-Deep] Iniciando revisión profunda: {desde} al {hoy}...")
    try:
        result = await client.sync_guias_abiertas(fecha_desde=desde, fecha_hasta=hoy)
        total = result.get('total_extraidas', 0)
        logger.info(f"[Guias-Deep] Finalizado. Guías actualizadas: {total}")
    except Exception as e:
        logger.error(f"[Guias-Deep] Falló la revisión profunda: {e}")

async def refrescar_pipeline_abiertos_task():
    """
    Tarea programada para refrescar el estado de cotizaciones 'Abierto' en el Pipeline,
    sin importar su fecha de creación. Complementa la revisión profunda de 60 días.
    """
    logger.info("[Pipeline-Abiertos] Iniciando refresco de estados de cotizaciones abiertas...")
    try:
        result = await client.refrescar_pipeline_abiertos()
        total = result.get('total_procesados', 0)
        logger.info(f"[Pipeline-Abiertos] Finalizado. Cotizaciones actualizadas: {total}")
    except Exception as e:
        logger.error(f"[Pipeline-Abiertos] Falló el refresco: {e}")

async def sync_gestor_despachos_task():
    """
    Tarea programada para sincronizar el Gestor de Despachos (últimos 7 días).
    """
    ahora = datetime.now()
    hoy = ahora.strftime("%d-%m-%Y")
    desde = (ahora - timedelta(days=7)).strftime("%d-%m-%Y")

    logger.info(f"[Gestor-Despachos] Iniciando sincronización masiva: {desde} al {hoy}...")
    try:
        result = await client.sync_gestor_despachos(fecha_desde=desde, fecha_hasta=hoy)
        total = result.get('total_procesados', 0)
        logger.info(f"[Gestor-Despachos] Finalizado. Registros sincronizados: {total}")
    except Exception as e:
        logger.error(f"[Gestor-Despachos] Falló la sincronización: {e}")
