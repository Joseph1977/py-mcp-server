import requests
from app.config.config import settings # This import is needed for GOOGLE_API_KEY
from app.core.mcp_core import MCPTool
import logging # Added

logger = logging.getLogger(__name__)

async def search_brave(params: dict):
    query = params.get("query")
    logger.info(f"Brave Search request for query: '{query}'")
    if not query:
        logger.warning("Brave Search: Query parameter is missing.")
        return {"error": "Query parameter is required"}
    if not settings.BRAVE_API_KEY:
        logger.error("Brave Search: BRAVE_API_KEY is not configured.")
        return {"error": "Brave Search API key is not configured."}
    
    headers = {"X-Subscription-Token": settings.BRAVE_API_KEY}
    api_url = f"https://api.search.brave.com/res/v1/web/search?q={query}"
    logger.info(f"Brave Search: Requesting URL: {api_url}")
    
    response_obj = None
    try:
        response_obj = requests.get(api_url, headers=headers)
        logger.info(f"Brave Search: Response status for '{query}': {response_obj.status_code}")
        response_obj.raise_for_status()
        search_results = response_obj.json()
        logger.info(f"Brave Search: Successfully decoded JSON for '{query}'.")
        # logger.debug(f"Brave Search results for '{query}': {search_results}")
        return search_results
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"Brave Search: HTTP error for '{query}': {http_err}")
        if response_obj is not None:
            logger.debug(f"Brave Search: HTTPError content for '{query}': {response_obj.text}")
        return {"error": f"Brave Search HTTP error: {http_err}"}
    except requests.exceptions.RequestException as req_err:
        logger.error(f"Brave Search: Request error for '{query}': {req_err}")
        return {"error": f"Brave Search request error: {req_err}"}
    except ValueError as json_err:
        logger.error(f"Brave Search: JSON decoding error for '{query}': {json_err}")
        if response_obj is not None:
            logger.debug(f"Brave Search: Content failing JSON decode for '{query}': {response_obj.text}")
        return {"error": "Brave Search: Failed to decode JSON response."}

async def search_google(params: dict):
    query = params.get("query")
    logger.info(f"Google Search request for query: '{query}'")
    if not query:
        logger.warning("Google Search: Query parameter is missing.")
        return {"error": "Query parameter is required"}
    if not settings.GOOGLE_API_KEY:
        logger.error("Google Search: GOOGLE_API_KEY is not configured.")
        return {"error": "Google Search API key is not configured."}
    # Note: Google Custom Search also requires a CX (Custom Search Engine ID)
    # This is not currently in settings and needs to be added or hardcoded if used.
    cx = "YOUR_CX" # Placeholder - this needs to be configured!
    if cx == "YOUR_CX":
        logger.error("Google Search: CX (Custom Search Engine ID) is not configured.")
        return {"error": "Google Search CX is not configured."}

    api_url = f"https://www.googleapis.com/customsearch/v1?key={settings.GOOGLE_API_KEY}&cx={cx}&q={query}"
    logger.info(f"Google Search: Requesting URL: {api_url}")
    
    response_obj = None
    try:
        response_obj = requests.get(api_url)
        logger.info(f"Google Search: Response status for '{query}': {response_obj.status_code}")
        response_obj.raise_for_status()
        search_results = response_obj.json()
        logger.info(f"Google Search: Successfully decoded JSON for '{query}'.")
        # logger.debug(f"Google Search results for '{query}': {search_results}")
        return search_results
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"Google Search: HTTP error for '{query}': {http_err}")
        if response_obj is not None:
            logger.debug(f"Google Search: HTTPError content for '{query}': {response_obj.text}")
        return {"error": f"Google Search HTTP error: {http_err}"}
    except requests.exceptions.RequestException as req_err:
        logger.error(f"Google Search: Request error for '{query}': {req_err}")
        return {"error": f"Google Search request error: {req_err}"}
    except ValueError as json_err:
        logger.error(f"Google Search: JSON decoding error for '{query}': {json_err}")
        if response_obj is not None:
            logger.debug(f"Google Search: Content failing JSON decode for '{query}': {response_obj.text}")
        return {"error": "Google Search: Failed to decode JSON response."}

brave_search_tool = MCPTool(
    name="brave_search",
    description="Searches the web using Brave Search.",
    func=search_brave
)

google_search_tool = MCPTool(
    name="google_search",
    description="Searches the web using Google Search.",
    func=search_google
)

web_search_tools = [brave_search_tool, google_search_tool]
