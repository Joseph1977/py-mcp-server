import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

class Settings:
    BRAVE_API_KEY: str = os.getenv("BRAVE_API_KEY", "")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    OPENWEATHERMAP_API_KEY: str = os.getenv("OPENWEATHERMAP_API_KEY", "")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    MCP_TRANSPORT_MODE: str = os.getenv("MCP_TRANSPORT_MODE", "http") # Default to http
    MCP_SERVER_HOST: str = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
    MCP_SERVER_PORT: int = int(os.getenv("MCP_SERVER_PORT", "8001")) # Original port 8001

    def __init__(self):
        logger.info("Initializing settings...")
        if not self.BRAVE_API_KEY:
            logger.warning("BRAVE_API_KEY is not set.")
        if not self.GOOGLE_API_KEY:
            logger.warning("GOOGLE_API_KEY is not set.")
        
        logger.info(f"LOG_LEVEL set to: {self.LOG_LEVEL}")
        logger.info(f"MCP_TRANSPORT_MODE set to: {self.MCP_TRANSPORT_MODE}")
        logger.info(f"MCP_SERVER_HOST set to: {self.MCP_SERVER_HOST}")
        logger.info(f"MCP_SERVER_PORT set to: {self.MCP_SERVER_PORT}")

settings = Settings()

# Configure logging
log_level_setting = settings.LOG_LEVEL.upper()
actual_log_level = logging.INFO  # Default if parsing fails or level is unknown

if hasattr(logging, log_level_setting):
    actual_log_level = getattr(logging, log_level_setting)
elif log_level_setting == "TRACE":
    actual_log_level = 5  # TRACE level (often set to 5, as Uvicorn does)
    logging.addLevelName(actual_log_level, "TRACE")
    # Add a trace method to Logger instances if it doesn't exist
    if not hasattr(logging.Logger, 'trace'):
        def trace(self, message, *args, **kws):
            if self.isEnabledFor(actual_log_level):
                self._log(actual_log_level, message, args, **kws)
        logging.Logger.trace = trace
else:
    logging.warning(f"Unknown LOG_LEVEL '{settings.LOG_LEVEL}'. Defaulting to INFO.")
    actual_log_level = logging.INFO

logging.basicConfig(level=actual_log_level,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger.info("Logging configured.")
logger.info(f"Settings loaded: MCP_TRANSPORT_MODE='{settings.MCP_TRANSPORT_MODE}', MCP_SERVER_HOST='{settings.MCP_SERVER_HOST}', MCP_SERVER_PORT={settings.MCP_SERVER_PORT}")
