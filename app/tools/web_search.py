import logging
import httpx  # Using httpx for async requests
from app.config.config import settings
from typing import List, Optional

logger = logging.getLogger(__name__)

# Note: logging.basicConfig is removed as it's handled in config.py

async def search_brave(query: str, count: int = 10):
    """Search using Brave Search API - matches TypeScript implementation"""
    logger.info(f"Brave Search request for query: '{query}' with count: {count}")
    
    if not query:
        logger.warning("Brave Search: Query parameter is missing.")
        return {"error": "Query parameter is required"}
    if not settings.BRAVE_API_KEY:
        logger.error("Brave Search: BRAVE_API_KEY is not configured.")
        return {"error": "Brave Search API key is not configured."}

    # Use proper URL encoding and count parameter like TypeScript version
    import urllib.parse
    encoded_query = urllib.parse.quote_plus(query)  # Use quote_plus for better compatibility
    api_url = f"https://api.search.brave.com/res/v1/web/search?q={encoded_query}&count={count}"
    
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": settings.BRAVE_API_KEY
    }
    
    logger.info(f"Brave Search: Requesting URL: {api_url}")

    async with httpx.AsyncClient() as client:
        try:
            response_obj = await client.get(api_url, headers=headers)
            logger.info(f"Brave Search: Response status for '{query}': {response_obj.status_code}")
            
            if not response_obj.is_success:
                error_text = response_obj.text
                logger.error(f"Brave Search: HTTP error! status: {response_obj.status_code}, response: {error_text}")
                return {"error": f"HTTP error! status: {response_obj.status_code}, details: {error_text}"}
            
            data = response_obj.json()
            logger.info(f"Brave Search: Successfully decoded JSON for '{query}'.")
            
            # Process results like TypeScript version - extract web results
            web_results = data.get('web', {}).get('results', [])
            
            # Transform to consistent format
            search_results = []
            for result in web_results:
                search_results.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "description": result.get("description", "")
                })
            
            logger.info(f"Brave Search: Found {len(search_results)} results for '{query}'")
            logger.debug(f"Brave Search processed results for '{query}': {search_results}")
            
            return {
                "query": query,
                "results": search_results,
                "total_results": len(search_results)
            }
            
        except httpx.HTTPStatusError as http_err:
            logger.error(f"Brave Search: HTTP error for '{query}': {http_err}")
            return {"error": f"Brave Search HTTP error: {http_err}"}
        except httpx.RequestError as req_err:
            logger.error(f"Brave Search: Request error for '{query}': {req_err}")
            return {"error": f"Brave Search request error: {req_err}"}
        except ValueError as json_err:
            logger.error(f"Brave Search: JSON decoding error for '{query}': {json_err}")
            return {"error": "Brave Search: Failed to decode JSON response."}
        except Exception as e:
            logger.error(f"Brave Search: Unexpected error for '{query}': {e}")
            return {"error": f"Brave Search unexpected error: {e}"}

async def search_google(query: str, count: int = 10, sites: Optional[List[str]] = None):
    """Search using Google Custom Search JSON API. Optionally restrict to a list of sites."""
    logger.info(f"Google Search request for query: '{query}' with count: {count} and sites: {sites}")
    
    if not query:
        logger.warning("Google Search: Query parameter is missing.")
        return {"error": "Query parameter is required"}
    if not settings.GOOGLE_API_KEY or not getattr(settings, "GOOGLE_CSE_ID", None):
        logger.error("Google Search: GOOGLE_API_KEY or GOOGLE_CSE_ID is not configured.")
        return {"error": "Google Search API key or CSE ID is not configured."}

    # If sites are provided, add site restriction to the query
    if sites:
        site_query = " OR ".join([f"site:{site}" for site in sites])
        query = f"{query} {site_query}"

    # Proper URL encoding for the query
    import urllib.parse
    encoded_query = urllib.parse.quote_plus(query)
    api_url = (
        f"https://www.googleapis.com/customsearch/v1?key={settings.GOOGLE_API_KEY}"
        f"&cx={settings.GOOGLE_CSE_ID}&q={encoded_query}&num={count}"
    )
    logger.info(f"Google Search: Requesting URL: {api_url}")

    async with httpx.AsyncClient() as client:
        try:
            response_obj = await client.get(api_url)
            logger.info(f"Google Search: Response status for '{query}': {response_obj.status_code}")
            
            if not response_obj.is_success:
                error_text = response_obj.text
                logger.error(f"Google Search: HTTP error! status: {response_obj.status_code}, response: {error_text}")
                return {"error": f"HTTP error! status: {response_obj.status_code}, details: {error_text}"}
            
            data = response_obj.json()
            logger.info(f"Google Search: Successfully decoded JSON for '{query}'.")
            
            items = data.get('items', [])
            search_results = []
            for item in items:
                search_results.append({
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "description": item.get("snippet", "")
                })
            
            logger.info(f"Google Search: Found {len(search_results)} results for '{query}'")
            logger.debug(f"Google Search processed results for '{query}': {search_results}")
            
            return {
                "query": query,
                "results": search_results,
                "total_results": len(search_results)
            }
        except httpx.HTTPStatusError as http_err:
            logger.error(f"Google Search: HTTP error for '{query}': {http_err}")
            return {"error": f"Google Search HTTP error: {http_err}"}
        except httpx.RequestError as req_err:
            logger.error(f"Google Search: Request error for '{query}': {req_err}")
            return {"error": f"Google Search request error: {req_err}"}
        except ValueError as json_err:
            logger.error(f"Google Search: JSON decoding error for '{query}': {json_err}")
            return {"error": "Google Search: Failed to decode JSON response."}
        except Exception as e:
            logger.error(f"Google Search: Unexpected error for '{query}': {e}")
            return {"error": f"Google Search unexpected error: {e}"}
