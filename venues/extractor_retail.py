"""
venues/extractor_retail.py — Extracts retail-specific signals from venue web pages (OTMB).

Handles both:
  - Empty spaces / galleries (physical space signals)
  - Operating retail stores (private event availability, store type, aesthetics)
"""
import re
import logging
from typing import Dict, List, Optional
from urllib.parse import urlparse

from scraper import fetch_page, fetch_contact_page
from config_core import RETAIL_SIGNALS, RETAIL_VENUE_TYPES, RETAIL_STORE_SIGNALS
from venues.extractor_nightlife import extract_contact, extract_phone

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# GENERIC HELPERS
# ──────────────────────────────────────────────

def _kw_hit(text: str, keywords: List[str]) -> bool:
    """Return True if any keyword appears in the text (case-insensitive)."""
    t = text.lower()
    return any(kw.lower() in t for kw in keywords)


def _kw_matches(text: str, keywords: List[str]) -> List[str]:
    """Return the list of keywords that appeared in the text."""
    t = text.lower()
    return [kw for kw in keywords if kw.lower() in t]


# ──────────────────────────────────────────────
# PHYSICAL SPACE SIGNALS
# ──────────────────────────────────────────────

def _extract_sqft(text: str) -> Optional[int]:
    """Parse square footage from page text."""
    m = re.search(RETAIL_SIGNALS["sqft_pattern"], text, re.IGNORECASE)
    if m:
        try:
            return int(m.group(1).replace(",", ""))
        except (ValueError, IndexError):
            pass
    return None


def _extract_ceiling_height(text: str) -> Optional[int]:
    """Parse ceiling height (in feet) from page text."""
    m = re.search(RETAIL_SIGNALS["ceiling_pattern"], text, re.IGNORECASE)
    if m:
        for group in m.groups():
            if group:
                try:
                    return int(group)
                except ValueError:
                    pass
    fallback = re.search(r'(\d{1,2})[\s\-]?foot\s+ceiling', text, re.IGNORECASE)
    if fallback:
        try:
            return int(fallback.group(1))
        except ValueError:
            pass
    return None


# ──────────────────────────────────────────────
# VENUE TYPE CLASSIFICATION
# ──────────────────────────────────────────────

def _classify_venue_type(text: str, url: str, name: str, seed_type: str = "") -> str:
    """
    Classify retail venue type: prefer seed type if provided, else infer from content.
    Prioritizes operating store types over generic 'creative_space'.
    """
    # Honor the seed-provided type if it's a meaningful operating store type
    operating_types = {
        "furniture_showroom", "sneaker_boutique", "streetwear_store",
        "vintage_boutique", "concept_store",
    }
    if seed_type in operating_types:
        return seed_type

    combined = (name + " " + url + " " + text).lower()

    # Rank each type
    scores = {vt: 0 for vt in RETAIL_VENUE_TYPES + [
        "furniture_showroom", "sneaker_boutique", "streetwear_store",
        "vintage_boutique", "concept_store",
    ]}

    mapping = {
        "art_gallery":        ["gallery", "art gallery", "fine art", "contemporary art"],
        "design_studio":      ["design studio", "architecture studio"],
        "showroom":           ["showroom", "show room"],
        "warehouse":          ["warehouse", "industrial"],
        "loft":               ["loft", "raw loft"],
        "pop-up_space":       ["pop-up", "popup", "temporary retail"],
        "storefront":         ["storefront", "retail space"],
        "creative_space":     ["creative space", "creative hub"],
        "furniture_showroom": ["furniture", "home goods", "furnishings", "home decor"],
        "sneaker_boutique":   ["sneakers", "kicks", "footwear", "sneaker boutique"],
        "streetwear_store":   ["streetwear", "urban fashion", "hype"],
        "vintage_boutique":   ["vintage", "secondhand", "thrift", "consignment"],
        "concept_store":      ["concept store", "multi-brand", "editorial retail"],
    }

    for vtype, kws in mapping.items():
        for kw in kws:
            if kw in combined:
                scores[vtype] = scores.get(vtype, 0) + 1

    best = max(scores, key=lambda v: scores[v])
    return best if scores[best] > 0 else "creative_space"


# ──────────────────────────────────────────────
# OPERATING STORE SIGNALS
# ──────────────────────────────────────────────

def _detect_private_events(text: str) -> bool:
    """Return True if the store explicitly mentions private event availability."""
    return _kw_hit(text, RETAIL_STORE_SIGNALS["private_events"])


def _detect_aesthetics(text: str) -> str:
    """Extract aesthetic tags as a comma-separated string."""
    tags = []
    for tag, kws in [
        ("modern",      RETAIL_STORE_SIGNALS["modern_aesthetic"]),
        ("curated",     RETAIL_STORE_SIGNALS["curated"]),
        ("vintage",     RETAIL_STORE_SIGNALS["vintage"]),
        ("editorial",   ["editorial"]),
        ("minimalist",  ["minimalist", "minimal"]),
        ("industrial",  ["industrial"]),
    ]:
        if _kw_hit(text, kws):
            tags.append(tag)
    return ", ".join(tags)


def _detect_chain_store(text: str, name: str) -> bool:
    """Return True if the venue is likely a chain / mass-market store."""
    combined = (name + " " + text).lower()
    return _kw_hit(combined, RETAIL_STORE_SIGNALS["chain_store"])


def _detect_fast_fashion(text: str, name: str) -> bool:
    """Return True if the venue is a fast-fashion brand."""
    combined = (name + " " + text).lower()
    return _kw_hit(combined, RETAIL_STORE_SIGNALS["fast_fashion"])


def _extract_instagram(html: str, text: str) -> str:
    """Extract Instagram handle from page HTML or text."""
    patterns = [
        re.compile(r'instagram\.com/([A-Za-z0-9._]{2,30})', re.I),
        re.compile(r'@([A-Za-z0-9._]{2,30})\b', re.I),
    ]
    ignore = {"p", "explore", "accounts", "stories", "reels", "tv", "direct",
               "share", "login", "signup"}
    from collections import Counter
    all_handles = []

    # Try href links first
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html[:30000], "lxml")
        for a in soup.find_all("a", href=True):
            m = re.search(r'instagram\.com/([A-Za-z0-9._]{2,30})', a["href"], re.I)
            if m:
                h = m.group(1).rstrip("/").lower()
                if h not in ignore:
                    all_handles.append(h)
    except Exception:
        pass

    # Fallback: regex on text + html
    combined = (text + " " + html)[:20000]
    for pat in patterns:
        for m in pat.finditer(combined):
            h = m.group(1).rstrip("/").lower()
            if h not in ignore and len(h) > 2:
                all_handles.append(h)

    if all_handles:
        handle = Counter(all_handles).most_common(1)[0][0]
        return f"@{handle}"
    return ""


def _extract_booking_url(html: str, base_url: str) -> str:
    """Look for a booking/inquiry link in the page."""
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html[:30000], "lxml")
        for a in soup.find_all("a", href=True):
            href = a["href"].lower()
            label = a.get_text(strip=True).lower()
            if any(kw in href or kw in label for kw in
                   ["book", "inquire", "inquiry", "contact", "rent", "reserve", "hire"]):
                raw = a["href"]
                if raw.startswith("http"):
                    return raw
                if raw.startswith("/"):
                    parsed = urlparse(base_url)
                    return f"{parsed.scheme}://{parsed.netloc}{raw}"
    except Exception:
        pass
    return ""


# ──────────────────────────────────────────────
# MAIN EXTRACTOR
# ──────────────────────────────────────────────

def extract_retail_signals(venues: List[Dict]) -> List[Dict]:
    """
    Enrich each venue dict with signals scraped from its website.
    Handles both empty spaces and operating retail stores.

    Args:
        venues: List of venue dicts (from seeds or searcher).

    Returns:
        Enhanced dicts with physical space signals, store type signals,
        contact info, and Instagram handle.
    """
    enriched = []

    for i, venue in enumerate(venues):
        url  = venue.get("url", "")
        name = venue.get("name", f"Venue {i+1}")
        seed_type = venue.get("venue_type", "")
        logger.info(f"  [{i+1}/{len(venues)}] {name or url[:60]}")

        page_data = fetch_page(url)
        html = ""
        text = ""

        if page_data:
            venue["url"] = page_data["url"]
            html = page_data["html"]
            text = page_data["text"]
            # Pull page title if name is blank
            if not venue.get("name"):
                title_m = re.search(r"<title[^>]*>([^<]+)</title>", html, re.I)
                if title_m:
                    venue["name"] = re.sub(
                        r"\s*[\|\-–]\s*.+$", "", title_m.group(1)).strip()[:60]
        else:
            logger.debug(f"    Could not fetch {url}")

        # Fetch contact/about page for deeper signal detection
        contact_html = ""
        if page_data:
            base = (f"{urlparse(page_data['url']).scheme}://"
                    f"{urlparse(page_data['url']).netloc}")
            contact_html = fetch_contact_page(base) or ""

        combined_text = (text + " " + contact_html).lower()
        combined_html  = html + " " + contact_html

        # ── Physical space signals ──────────────────────────────────────
        sqft    = _extract_sqft(combined_text)
        ceiling = _extract_ceiling_height(combined_text)

        signals = {
            "sqft":                   sqft,
            "ceiling_height":         ceiling,
            "has_storefront":         _kw_hit(combined_text, RETAIL_SIGNALS["storefront"]),
            "has_natural_light":      _kw_hit(combined_text, RETAIL_SIGNALS["natural_light"]),
            "has_white_walls":        _kw_hit(combined_text, RETAIL_SIGNALS["white_walls"]),
            "has_high_ceilings":      (ceiling is not None and ceiling >= 10) or
                                      _kw_hit(combined_text, RETAIL_SIGNALS["high_ceilings"]),
            "has_open_floor":         _kw_hit(combined_text, RETAIL_SIGNALS["open_floor"]),
            "has_retail_fixtures":    _kw_hit(combined_text, RETAIL_SIGNALS["retail_fixtures"]),
            "has_storefront_windows": _kw_hit(combined_text, RETAIL_SIGNALS["storefront_windows"]),
            "is_transformable":       (_kw_hit(combined_text, RETAIL_SIGNALS["transformable"]) or
                                       _kw_hit(combined_text, RETAIL_SIGNALS["blank_canvas"])),
            "short_term_available":   _kw_hit(combined_text, RETAIL_SIGNALS["short_term"]),
        }

        # ── Operating store signals ─────────────────────────────────────
        private_events = _detect_private_events(combined_text)
        signals.update({
            "store_type":              _classify_venue_type(
                                           combined_text, url,
                                           venue.get("name", ""), seed_type),
            "private_events_available": private_events,
            "manual_outreach_needed":   not private_events,
            "instagram_handle":         _extract_instagram(combined_html, combined_text),
            "aesthetic_tags":           _detect_aesthetics(combined_text),
            "is_chain_store":           _detect_chain_store(combined_text, name),
            "is_fast_fashion":          _detect_fast_fashion(combined_text, name),
        })

        # ── Contact info ────────────────────────────────────────────────
        signals["contact_email"] = extract_contact(text, combined_html)
        signals["contact_phone"] = extract_phone(text)
        signals["booking_url"]   = _extract_booking_url(combined_html, url)

        venue.update(signals)
        enriched.append(venue)

        logger.info(
            f"    ✓ {signals['store_type']} | "
            f"Sqft: {sqft or '?'} | "
            f"Events: {'✓' if private_events else '—'} | "
            f"IG: {signals['instagram_handle'] or '—'}"
        )

    return enriched
