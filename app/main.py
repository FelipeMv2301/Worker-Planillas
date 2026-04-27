import asyncio
import logging
import uvicorn
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.core.config import get_settings
from app.core.logging_conf import setup_logging
from app.tasks import scheduler_tasks

# Inicializar configuración y logs
setup_logging()
settings = get_settings()
logger = logging.getLogger("WorkerMain")

# Crear aplicación FastAPI para Health Check
app = FastAPI()

@app.get("/")
@app.get("/health")
async def health_check():
    """
    Endpoint para que Docker/DigitalOcean verifiquen que el servicio está vivo.
    """
    return {"status": "ok", "worker": "Worker-Planillas"}

async def run_scheduler():
    """
    Configura e inicia el scheduler de tareas.
    """
    scheduler = AsyncIOScheduler()
    
    # Programar tareas
    scheduler.add_job(scheduler_tasks.sync_stocks_task, 'interval', minutes=settings.INTERVAL_SYNC_STOCKS, id='sync_stocks')
    scheduler.add_job(scheduler_tasks.sync_backorders_task, 'interval', minutes=settings.INTERVAL_SYNC_STOCKS, id='sync_backorders')
    scheduler.add_job(scheduler_tasks.sync_ventas_margen_task, 'interval', minutes=settings.INTERVAL_SYNC_VENTAS_MARGEN, id='sync_ventas_margen')
    scheduler.add_job(scheduler_tasks.sync_pipeline_task, 'interval', minutes=settings.INTERVAL_SYNC_PIPELINE, id='sync_pipeline')
    
    scheduler.start()
    logger.info("Tareas programadas y scheduler activo.")
    
    while True:
        await asyncio.sleep(1)

async def main():
    """
    Lanza el servidor de Health Check y el Scheduler simultáneamente.
    """
    logger.info("Worker-Planillas iniciando...")
    
    # Ejecutamos el servidor web en el puerto configurado y el scheduler simultáneamente
    config = uvicorn.Config(app, host="0.0.0.0", port=settings.WORKER_PORT, log_level="warning")
    server = uvicorn.Server(config)
    
    await asyncio.gather(
        server.serve(),
        run_scheduler()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Deteniendo worker por interrupción de usuario...")
