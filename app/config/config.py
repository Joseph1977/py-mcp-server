import os
from dotenv import load_dotenv
import logging

print("START OF app.config.config.py execution") # New print

load_dotenv()
print(f"dotenv loaded. MCP_TRANSPORT_MODE from os.getenv: {os.getenv('MCP_TRANSPORT_MODE')}") # New print

logger = logging.getLogger(__name__)

class Settings:
    print("Inside Settings class definition: About to define class attributes.") # New print
    BRAVE_API_KEY: str = os.getenv("BRAVE_API_KEY", "")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    OPENWEATHERMAP_API_KEY: str = os.getenv("OPENWEATHERMAP_API_KEY", "")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    # Ensure MCP_TRANSPORT_MODE is defined as a class attribute
    MCP_TRANSPORT_MODE: str = os.getenv("MCP_TRANSPORT_MODE", "sse")
    print(f"Inside Settings class definition: MCP_TRANSPORT_MODE class attribute defined as: {MCP_TRANSPORT_MODE}") # New print

    def __init__(self):
        print("START Settings.__init__") # New print
        logger.info("Initializing settings...")
        # Diagnostic logging:
        print(f"Settings __init__: self.__dict__ before checks: {self.__dict__}") # New print
        logger.info(f"Settings instance __dict__ before checks: {self.__dict__}")
        print(f"Settings __init__: dir(Settings): {dir(Settings)}") # New print
        logger.info(f"Settings class attributes (dir(Settings)): {dir(Settings)}")
        
        # Try accessing the attribute directly, which should be inherited from the class
        try:
            # This will now be an instance variable if not already set by class.
            # Let's ensure it's explicitly set on the instance if that's the desired pattern,
            # or consistently accessed via self.MCP_TRANSPORT_MODE which should pick up the class var.
            # For clarity, let's assign it to self if it's meant to be an instance property
            # based on the class property.
            # self.MCP_TRANSPORT_MODE = Settings.MCP_TRANSPORT_MODE # Explicitly set from class attribute
            
            print(f"Settings __init__: MCP_TRANSPORT_MODE from instance via self: {self.MCP_TRANSPORT_MODE}") # New print
            logger.info(f"MCP_TRANSPORT_MODE from instance via self: {self.MCP_TRANSPORT_MODE}")
        except AttributeError:
            print("Settings __init__: ERROR - MCP_TRANSPORT_MODE is NOT FOUND on instance via self in __init__") # New print
            logger.error("MCP_TRANSPORT_MODE is NOT FOUND on instance via self in __init__")

        if not self.BRAVE_API_KEY:
            logger.warning("BRAVE_API_KEY is not set.")
        if not self.GOOGLE_API_KEY:
            logger.warning("GOOGLE_API_KEY is not set.")
        
        logger.info(f"LOG_LEVEL set to: {self.LOG_LEVEL}")
        print(f"Settings __init__: LOG_LEVEL set to: {self.LOG_LEVEL}") # New print
        
        # Check again after other initializations
        print(f"Settings __init__: MCP_TRANSPORT_MODE successfully initialized to (checked again): {self.MCP_TRANSPORT_MODE}") # New print
        logger.info(f"MCP_TRANSPORT_MODE successfully initialized to (checked again): {self.MCP_TRANSPORT_MODE}")
        print("END Settings.__init__") # New print

print("app.config.config.py: About to create settings instance") # New print
settings = Settings()
print(f"app.config.config.py: settings instance created. MCP_TRANSPORT_MODE: {settings.MCP_TRANSPORT_MODE}") # New print
print("END OF app.config.config.py execution") # New print
