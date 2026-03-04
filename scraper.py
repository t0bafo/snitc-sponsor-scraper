"""
scraper.py — Fetches raw HTML from brand websites.
"""
import time
import logging
import requests
from typing import Optional, Dict
from config_core import HEADERS, REQUEST_TIMEOUT, SCRAPE_DELAY

logger = logging.getLogger(__name__)


def fetch_page(url: str) -> Optional[Dict]:
    """
    Fetch a brand's homepage and return raw content.
    Returns None if the page fails to load.
    """
    if not url or not url.startswith("http"):
        return None
    try:
        resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT, allow_redirects=True)
        if resp.status_code == 200:
            return {
                "url": resp.url,
                "html": resp.text,
                "text": _clean_text(resp.text),
            }
        else:
            logger.debug(f"  HTTP {resp.status_code} for {url}")
            return None
    except Exception as e:
        logger.debug(f"  Failed to fetch {url}: {e}")
        return None


def fetch_contact_page(base_url: str) -> Optional[str]:
    """
    Try to fetch a /contact page for more email addresses.
    """
    contact_paths = ["/contact", "/contact-us", "/about", "/about-us", "/team"]
    for path in contact_paths:
        try:
            url = base_url.rstrip("/") + path
            resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT, allow_redirects=True)
            if resp.status_code == 200:
                return resp.text
        except Exception:
            pass
    return None


def _clean_text(html: str) -> str:
    """Strip HTML tags and return plain text (limited to first 15k chars)."""
    from bs4 import BeautifulSoup
    try:
        soup = BeautifulSoup(html[:50000], "lxml")
        # Remove script/style noise
        for tag in soup(["script", "style", "nav", "footer", "head"]):
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)[:15000]
    except Exception:
        return html[:5000]


def polite_sleep():
    """Politely wait between fetches."""
    time.sleep(SCRAPE_DELAY)
