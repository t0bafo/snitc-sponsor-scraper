import logging
import requests
import time
import random
from typing import List, Dict
from urllib.parse import urlparse, parse_qs, unquote
from bs4 import BeautifulSoup
import venues.config_venues as cfg

logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/122.0.6261.62 Mobile/15E148 Safari/604.1"
]

IGNORE_DOMAINS = {
    "yelp.com", "tripadvisor.com", "theknot.com", "weddingwire.com",
    "eventup.com", "peerspace.com", "partyslate.com", "opentable.com",
    "foursquare.com", "zomato.com", "timeout.com", "theinfatuation.com",
    "eater.com", "thrillist.com", "reddit.com", "twitter.com",
    "facebook.com", "instagram.com", "pinterest.com", "linkedin.com",
    "tiktok.com", "youtube.com", "airbnb.com", "venuereport.com",
    "bizbash.com", "rooftopguiden.com", "therooftopguide.com", "venuelust.com",
    "google.com", "bing.com", "duckduckgo.com", "giggster.com", "eventective.com",
    "thevendry.com", "tagvenue.com", "eventify.io", "venuenook.com", "splacer.co"
}

def discover_venues(city: str = "nyc", num_results: int = 15) -> List[Dict]:
    """
    Search for new venues using direct DuckDuckGo HTML scraping.
    Filters out aggregator sites to get direct venue websites.
    """
    queries = cfg.SEARCH_QUERIES.get(city.lower(), [])
    discovered_urls = []
    seen_domains = set()
    
    for query in queries:
        logger.info(f"    Searching: '{query}'")
        
        # Retry loop for rate limiting
        for attempt in range(3):
            try:
                headers = {"User-Agent": random.choice(USER_AGENTS)}
                resp = requests.get(
                    "https://html.duckduckgo.com/html/",
                    params={"q": query},
                    headers=headers,
                    timeout=15
                )
                
                if resp.status_code == 202:
                    wait = (attempt + 1) * 5
                    logger.warning(f"      HTTP 202 (Rate Limited). Retrying in {wait}s...")
                    time.sleep(wait)
                    continue
                
                if resp.status_code != 200:
                    logger.warning(f"      HTTP {resp.status_code} from DuckDuckGo")
                    break

                soup = BeautifulSoup(resp.text, "html.parser")
                results = soup.find_all("a", class_="result__url")
                
                count_before = len(discovered_urls)
                for a in results:
                    raw_url = a.get("href", "")
                    if not raw_url: continue
                    
                    clean_url = raw_url
                    if "uddg=" in raw_url:
                        parsed_query = parse_qs(urlparse(raw_url).query)
                        if "uddg" in parsed_query:
                            clean_url = unquote(parsed_query["uddg"][0])
                    
                    if not clean_url.startswith("http"): continue

                    parsed = urlparse(clean_url)
                    domain = parsed.netloc.replace("www.", "").lower()
                    
                    if any(ignored in domain for ignored in IGNORE_DOMAINS): continue
                    if domain in seen_domains: continue
                    
                    logger.info(f"      ✓ Discovered: {clean_url}")
                    seen_domains.add(domain)
                    discovered_urls.append(clean_url)
                    
                    if len(discovered_urls) >= (num_results * len(queries)): break
                
                if len(discovered_urls) > count_before:
                    break # Success!
                    
            except Exception as e:
                logger.warning(f"    Search attempt {attempt+1} failed: {e}")
                time.sleep(2)
            
        time.sleep(random.uniform(2.0, 4.0)) # Randomized delay
                
    # Convert into the seed dictionary format
    venues = []
    for url in discovered_urls:
        venues.append({
            "venue_name": "", # extracted later in pipeline
            "website": url,
            "city": city.capitalize()
        })
        
    return venues


