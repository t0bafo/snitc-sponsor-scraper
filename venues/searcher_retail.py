"""
venues/searcher_retail.py — DuckDuckGo search engine for OTMB retail/gallery/showroom spaces.
"""
import logging
import requests
import time
import random
from typing import List, Dict
from urllib.parse import urlparse, parse_qs, unquote
from bs4 import BeautifulSoup
from config_core import RETAIL_EXCLUDE_KEYWORDS

logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
]

# Domains to skip (aggregators, map/review sites)
IGNORE_DOMAINS = {
    "yelp.com", "tripadvisor.com", "google.com", "bing.com", "duckduckgo.com",
    "facebook.com", "instagram.com", "twitter.com", "reddit.com", "pinterest.com",
    "zillow.com", "realtor.com", "loopnet.com", "costar.com", "airbnb.com",
    "eventbrite.com", "meetup.com",
}


def _ddg_search(query: str, num_results: int = 10) -> List[Dict]:
    """Execute a single DuckDuckGo search and return result dicts."""
    results = []
    for attempt in range(3):
        try:
            headers = {"User-Agent": random.choice(USER_AGENTS)}
            resp = requests.get(
                "https://html.duckduckgo.com/html/",
                params={"q": query},
                headers=headers,
                timeout=15,
            )
            if resp.status_code == 202:
                wait = (attempt + 1) * 5
                logger.warning(f"    HTTP 202 (Rate Limited). Retrying in {wait}s...")
                time.sleep(wait)
                continue
            if resp.status_code != 200:
                logger.warning(f"    HTTP {resp.status_code} for query: {query}")
                break

            soup = BeautifulSoup(resp.text, "html.parser")

            for a in soup.find_all("a", class_="result__url"):
                raw_url = a.get("href", "")
                if not raw_url:
                    continue

                # Decode DuckDuckGo redirect URL
                clean_url = raw_url
                if "uddg=" in raw_url:
                    parsed_q = parse_qs(urlparse(raw_url).query)
                    if "uddg" in parsed_q:
                        clean_url = unquote(parsed_q["uddg"][0])

                if not clean_url.startswith("http"):
                    continue

                domain = urlparse(clean_url).netloc.replace("www.", "").lower()
                if any(d in domain for d in IGNORE_DOMAINS):
                    continue

                # Grab snippet text from sibling
                snippet = ""
                result_div = a.find_parent("div", class_=lambda c: c and "result" in c)
                if result_div:
                    snippet_tag = result_div.find("a", class_="result__snippet")
                    if snippet_tag:
                        snippet = snippet_tag.get_text(strip=True)[:300]

                results.append({
                    "url": clean_url,
                    "snippet": snippet,
                    "name": "",
                    "source": "duckduckgo",
                })

                if len(results) >= num_results:
                    break

            break  # Success - exit retry loop
        except Exception as e:
            logger.warning(f"    Search attempt {attempt + 1} failed: {e}")
            time.sleep(2)

    return results


def search_retail_venues(city: str, config: dict) -> List[Dict]:
    """
    Search for retail/gallery/showroom spaces suitable for OTMB.

    Args:
        city:   Target city (e.g., "dallas", "nyc").
        config: Full YAML event profile dict (search_queries, neighborhoods).

    Returns:
        Deduplicated list of venue candidate dicts.
    """
    raw_queries = config.get("search_queries", {})
    # Flatten all query categories into a single list
    all_queries: List[str] = []
    if isinstance(raw_queries, dict):
        for category_queries in raw_queries.values():
            all_queries.extend(category_queries)
    elif isinstance(raw_queries, list):
        all_queries = raw_queries

    # Also include neighborhood keywords in snippet detection
    target_neighborhoods = [n.lower() for n in config.get("neighborhoods", [])]

    all_results: List[Dict] = []
    seen_domains: set = set()

    for query in all_queries:
        logger.info(f"    Searching: '{query}'")
        results = _ddg_search(query, num_results=8)
        time.sleep(random.uniform(2.5, 4.5))  # Polite delay

        for r in results:
            domain = urlparse(r["url"]).netloc.replace("www.", "").lower()
            if domain in seen_domains:
                continue

            # Filter out nightlife/events-only venues
            snippet_lower = r["snippet"].lower()
            if any(kw in snippet_lower for kw in RETAIL_EXCLUDE_KEYWORDS):
                logger.debug(f"    ⛔ Excluded (nightlife signal): {r['url']}")
                continue

            # Try to detect neighborhood from snippet
            neighborhood = ""
            for hood in target_neighborhoods:
                if hood in snippet_lower or hood in r["url"].lower():
                    neighborhood = hood.title()
                    break

            r["neighborhood"] = neighborhood
            seen_domains.add(domain)
            all_results.append(r)
            logger.info(f"      ✓ Discovered: {r['url']}")

    logger.info(f"  Found {len(all_results)} unique retail venue candidates")
    return all_results
