"""
searcher.py — Web search module using Google Search (no API key needed).
Uses the `googlesearch-python` package which queries Google directly.
"""
import time
import logging
from typing import List, Dict
from googlesearch import search as google_search
from config import SEARCH_QUERIES, MAX_RESULTS_PER_QUERY, SEARCH_DELAY

logger = logging.getLogger(__name__)


def run_all_searches(test_mode: bool = False) -> List[Dict]:
    """
    Run all configured search queries using Google and return deduplicated results.

    Each result is a dict with: title, url, snippet, query
    """
    queries = SEARCH_QUERIES[:2] if test_mode else SEARCH_QUERIES
    all_results: List[Dict] = []
    seen_domains: set = set()

    logger.info(f"▶ Running {len(queries)} Google search queries...")

    for i, query in enumerate(queries):
        logger.info(f"  [{i+1}/{len(queries)}] Searching: \"{query}\"")
        try:
            urls = list(google_search(
                query,
                num_results=MAX_RESULTS_PER_QUERY,
                lang="en",
                region="us",
                sleep_interval=1,   # built-in politeness
            ))

            added = 0
            for url in urls:
                domain = _extract_domain(url)
                if _is_skip_domain(domain):
                    continue
                if domain and domain not in seen_domains:
                    seen_domains.add(domain)
                    all_results.append({
                        "title": "",          # will be extracted from page
                        "url": url,
                        "snippet": "",        # will be extracted from page
                        "query": query,
                    })
                    added += 1

            logger.info(f"     → {len(urls)} raw results, {added} new unique brands (total: {len(all_results)})")

        except Exception as e:
            logger.warning(f"     ⚠ Search failed for '{query}': {e}")

        if i < len(queries) - 1:
            time.sleep(SEARCH_DELAY)

    logger.info(f"✓ Search complete. {len(all_results)} unique URLs to process.")
    return all_results


def _extract_domain(url: str) -> str:
    """Extract base domain from a URL."""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc.lower().replace("www.", "")
    except Exception:
        return ""


def _is_skip_domain(domain: str) -> bool:
    """Return True for domains that are clearly not brand websites."""
    SKIP_DOMAINS = {
        "instagram.com", "facebook.com", "twitter.com", "x.com",
        "tiktok.com", "youtube.com", "pinterest.com", "reddit.com",
        "wikipedia.org", "wikimedia.org",
        "amazon.com", "etsy.com", "shopify.com",
        "buzzfeed.com", "huffpost.com", "medium.com",
        "theguardian.com", "nytimes.com", "wsj.com", "forbes.com",
        "bloomberg.com", "businessinsider.com", "techcrunch.com",
        "google.com", "bing.com", "yahoo.com", "duckduckgo.com",
        "indeed.com", "glassdoor.com", "linkedin.com",
        "yelp.com", "tripadvisor.com", "mapquest.com",
    }
    return domain in SKIP_DOMAINS
