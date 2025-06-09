import requests
import logging  # Added
from app.core.mcp_core import MCPTool

# Configure basic logging. In a larger app, this would be centralized.
# Set level to logging.DEBUG to see more verbose output including full JSON responses.
logging.basicConfig(level=logging.INFO) 
logger = logging.getLogger(__name__)

async def get_weather(params: dict):
    location = params.get("location")
    logger.info(f"Weather request received for location: '{location}'")

    if not location:
        logger.warning("Location parameter is missing for weather request.")
        return {"error": "Location parameter is required"}
    
    api_url = f"https://wttr.in/{location}?format=j1"
    logger.info(f"Requesting weather data from URL: {api_url}")
    
    response_obj = None # Initialize in case request fails early
    try:
        response_obj = requests.get(api_url)
        logger.info(f"Response status code for {location}: {response_obj.status_code}")
        response_obj.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        
        weather_data = response_obj.json()
        logger.info(f"Successfully decoded JSON response for {location}.")
        # For more detailed debugging, you can log the keys or the full data:
        # logger.debug(f"Weather data keys for {location}: {list(weather_data.keys()) if isinstance(weather_data, dict) else 'Not a dict'}")
        # logger.debug(f"Full weather data for {location}: {weather_data}")
        return weather_data
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error for {location}: {http_err}")
        if response_obj is not None:
            logger.debug(f"HTTPError response content for {location}: {response_obj.text}")
        return {"error": f"HTTP error occurred: {http_err} - Check if the location is valid."}
    except requests.exceptions.RequestException as req_err:
        logger.error(f"Request error for {location}: {req_err}")
        return {"error": f"Request error occurred: {req_err}"}
    except ValueError as json_err: # More specific for JSON decoding errors
        logger.error(f"JSON decoding error for {location}: {json_err}")
        if response_obj is not None:
            logger.debug(f"Content that failed JSON decoding for {location}: {response_obj.text}")
        return {"error": "Failed to decode JSON response from weather service."}

weather_tool = MCPTool(
    name="get_weather",
    description="Gets the current weather for a specified location using wttr.in.",
    func=get_weather
)

weather_tools = [weather_tool]
