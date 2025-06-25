import os
from dotenv import load_dotenv
import logging
from pathlib import Path

# Configure logging BEFORE any logger usage or .env loading
log_level_setting = os.getenv('LOG_LEVEL', 'INFO').upper()
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
    logging.warning(f"Unknown LOG_LEVEL '{log_level_setting}'. Defaulting to INFO.")
    actual_log_level = logging.INFO

logging.basicConfig(level=actual_log_level,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

def is_running_in_kubernetes():
    """Check if we're running inside a Kubernetes pod"""
    return os.path.exists('/var/run/secrets/kubernetes.io/serviceaccount')

# Check if we're running in Kubernetes
IS_K8S = is_running_in_kubernetes()
logger.info(f"IS_K8S = {IS_K8S}")

if IS_K8S:
    logger.info("Running in Kubernetes, using environment variables")
else:
    try:
        # Only load .env file if we're not in Kubernetes
        env_file = Path(__file__).parent.parent.parent / '.env'
        logger.info(f"Looking for .env file at: {env_file}")
        if env_file.exists():
            logger.info(f"Running locally, loading environment from: {env_file}")
            load_dotenv(env_file)
        else:
            logger.warning(f"Environment file not found: {env_file}")
    except Exception as e:
        logger.warning(f"Failed to load .env file: {str(e)}")

class Settings:
    def __init__(self):
        logger.info("Initializing settings constructor...")
          # Load ALL environment variables dynamically
        self.env_vars = dict(os.environ)
        logger.info("Initializing settings with all environment variables...")
        
        # Log key configuration variables
        logger.info(f"LOG_LEVEL set to: {self.get('LOG_LEVEL', 'INFO')}")
        logger.info(f"MCP_TRANSPORT_MODE set to: {self.get('MCP_TRANSPORT_MODE', 'http')}")
        logger.info(f"MCP_SERVER_HOST set to: {self.get('MCP_SERVER_HOST', '0.0.0.0')}")
        logger.info(f"MCP_SERVER_PORT set to: {self.get('MCP_SERVER_PORT', '8001')}")
        
        def is_missing(val):
            return val is None or str(val).strip() == "" or str(val).lower() == "null" or str(val).lower() == "none"

        # Check API keys and log status (without exposing values)
        brave_key = self.get('BRAVE_API_KEY')
        google_key = self.get('GOOGLE_API_KEY')
        google_cse = self.get('GOOGLE_CSE_ID')
        
        logger.info(f"BRAVE_API_KEY: {'SET' if not is_missing(brave_key) else 'NOT SET'}")
        logger.info(f"GOOGLE_API_KEY: {'SET' if not is_missing(google_key) else 'NOT SET'}")
        logger.info(f"GOOGLE_CSE_ID: {'SET' if not is_missing(google_cse) else 'NOT SET'}")
        
        if is_missing(brave_key):
            logger.warning("BRAVE_API_KEY is not set.")
        if is_missing(google_key):
            logger.warning("GOOGLE_API_KEY is not set.")
        if is_missing(google_cse):
            logger.warning("GOOGLE_CSE_ID is not set.")
    
    def __getitem__(self, key):
        """Allow settings['KEY'] syntax"""
        return self.env_vars.get(key, "")
    
    def get(self, key, default=None):
        """Allow settings.get('KEY', 'default') syntax"""
        return self.env_vars.get(key, default)
    
    def __contains__(self, key):
        """Allow 'KEY' in settings syntax"""
        return key in self.env_vars
    
    # Convenience properties for commonly used variables
    @property
    def BRAVE_API_KEY(self):
        return self.get('BRAVE_API_KEY', '')
    
    @property
    def GOOGLE_API_KEY(self):
        return self.get('GOOGLE_API_KEY', '')
    
    @property
    def GOOGLE_CSE_ID(self):
        return self.get('GOOGLE_CSE_ID', '')
    
    @property
    def LOG_LEVEL(self):
        return self.get('LOG_LEVEL', 'INFO')
    
    @property
    def MCP_TRANSPORT_MODE(self):
        return self.get('MCP_TRANSPORT_MODE', 'http')
    
    @property
    def MCP_SERVER_HOST(self):
        return self.get('MCP_SERVER_HOST', '0.0.0.0')
    
    @property
    def MCP_SERVER_PORT(self):
        return int(self.get('MCP_SERVER_PORT', '8001'))

# Now instantiate Settings with logging properly configured
settings = Settings()

logger.info("Logging configured.")
logger.info(f"Settings loaded: MCP_TRANSPORT_MODE='{settings.MCP_TRANSPORT_MODE}', MCP_SERVER_HOST='{settings.MCP_SERVER_HOST}', MCP_SERVER_PORT={settings.MCP_SERVER_PORT}")
