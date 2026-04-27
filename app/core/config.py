from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    """
    Gestiona las variables de entorno y configuraciones del Worker.
    Valida que los tipos sean correctos al arrancar la aplicación.
    """
    API_BASE_URL: str
    API_VERSION: str = "v1"
    
    # Intervalos de tareas en minutos
    INTERVAL_SYNC_STOCKS: int = 60
    INTERVAL_SYNC_VENTAS_MARGEN: int = 1440
    
    # Puertos (8080 es el estándar de DigitalOcean)
    WORKER_PORT: int = 8080
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def full_api_url(self) -> str:
        """
        Calcula la URL completa de la API combinando base y versión.
        """
        return f"{self.API_BASE_URL.rstrip('/')}/{self.API_VERSION}"

@lru_cache()
def get_settings():
    """
    Retorna una instancia única (singleton) de la configuración.
    """
    return Settings()
