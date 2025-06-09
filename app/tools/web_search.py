import logging
import httpx  # Using httpx for async requests
from app.config.config import settings

logger = logging.getLogger(__name__)

# Note: logging.basicConfig is removed as it's handled in config.py

async def search_brave(query: str):  # Changed signature
    logger.info(f"Brave Search request for query: '{query}'")
    if not query:
        logger.warning("Brave Search: Query parameter is missing.")
        return {"error": "Query parameter is required"}
    if not settings.BRAVE_API_KEY:
        logger.error("Brave Search: BRAVE_API_KEY is not configured.")
        return {"error": "Brave Search API key is not configured."}

    headers = {"X-Subscription-Token": settings.BRAVE_API_KEY, "Accept": "application/json"}
    api_url = f"https://api.search.brave.com/res/v1/web/search?q={query}"
    logger.info(f"Brave Search: Requesting URL: {api_url}")

    response_obj = None
    async with httpx.AsyncClient() as client:
        try:
            response_obj = await client.get(api_url, headers=headers)
            logger.info(f"Brave Search: Response status for '{query}': {response_obj.status_code}")
            response_obj.raise_for_status()
            search_results = response_obj.json()
            logger.info(f"Brave Search: Successfully decoded JSON for '{query}'.")
            logger.debug(f"Brave Search results for '{query}': {search_results}")
            return search_results
        except httpx.HTTPStatusError as http_err:
            logger.error(f"Brave Search: HTTP error for '{query}': {http_err}")
            if response_obj is not None:
                logger.debug(f"Brave Search: HTTPError content for '{query}': {response_obj.text}")
            return {"error": f"Brave Search HTTP error: {http_err}"}
        except httpx.RequestError as req_err:
            logger.error(f"Brave Search: Request error for '{query}': {req_err}")
            return {"error": f"Brave Search request error: {req_err}"}
        except ValueError as json_err:  # JSON decoding error
            logger.error(f"Brave Search: JSON decoding error for '{query}': {json_err}")
            if response_obj is not None:
                logger.debug(f"Brave Search: Content failing JSON decode for '{query}': {response_obj.text}")
            return {"error": "Brave Search: Failed to decode JSON response."}

async def search_google(query: str):  # Changed signature
    logger.info(f"Google Search request for query: '{query}'")
    if not query:
        logger.warning("Google Search: Query parameter is missing.")
        return {"error": "Query parameter is required"}
    
    # Placeholder: Google Search API integration requires API key and potentially a Custom Search Engine ID (cx)
    # For example, using Google Custom Search JSON API:
    # if not settings.GOOGLE_API_KEY or not getattr(settings, "GOOGLE_CSE_ID", None):
    #     logger.error("Google Search: GOOGLE_API_KEY or GOOGLE_CSE_ID is not configured.")
    #     return {"error": "Google Search API key or CSE ID is not configured."}
    # api_url = f"https://www.googleapis.com/customsearch/v1?key={settings.GOOGLE_API_KEY}&cx={settings.GOOGLE_CSE_ID}&q={query}"
    # ... (httpx call similar to search_brave) ...

    logger.warning("Google Search tool is not fully implemented with live API calls. Returning placeholder.")
    return {"message": f"Google Search for '{query}' would be performed here (currently a placeholder)."}
