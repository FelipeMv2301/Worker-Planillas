import sys
import logging
from logging import StreamHandler, Formatter

def setup_logging():
    # ANSI Color Codes
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"

    class ColorFormatter(logging.Formatter):
        FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
        
        LEVEL_COLORS = {
            logging.INFO: GREEN,
            logging.WARNING: YELLOW,
            logging.ERROR: RED,
            logging.CRITICAL: RED,
        }

        def format(self, record):
            color = self.LEVEL_COLORS.get(record.levelno, RESET)
            log_fmt = f"{color}{self.FORMAT}{RESET}"
            formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
            return formatter.format(record)

    # Configuración de consola
    console_handler = StreamHandler(sys.stdout)
    console_handler.setFormatter(ColorFormatter())

    # Configuración del logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Evitar duplicados si se llama varias veces
    if not root_logger.handlers:
        root_logger.addHandler(console_handler)

    # Suprimir logs irrelevantes de librerías de terceros (opcional)
    logging.getLogger("apscheduler").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    logging.info("Logging configurado correctamente.")
