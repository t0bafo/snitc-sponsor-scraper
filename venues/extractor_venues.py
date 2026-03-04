"""
venues/extractor_venues.py — Extracts venue-specific data from fetched HTML.

Extracts: capacity, venue type, neighborhood, description, contact,
          priority signals (rooftop, private events, bar, views, nightlife).
"""
import re
import logging
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup
from venues.config_venues import (
    ROOFTOP_KEYWORDS, PRIVATE_EVENT_KEYWORDS, BAR_SERVICE_KEYWORDS,
    VIEWS_KEYWORDS, INDOOR_BACKUP_KEYWORDS, NIGHTLIFE_KEYWORDS,
    AFROCULTURAL_KEYWORDS, EXCLUDE_KEYWORDS,
    BROOKLYN_NEIGHBORHOODS, MANHATTAN_NEIGHBORHOODS,
    VENUE_TYPE_KEYWORDS, CAPACITY_PATTERNS,
)

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# EMAIL / CONTACT EXTRACTION (re-use from sponsors)
# ──────────────────────────────────────────────
EMAIL_REGEX = re.compile(
    r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}',
    re.IGNORECASE
)

IGNORE_EMAIL_DOMAINS = {
    "example.com", "sentry.io", "w3.org", "schema.org", "google.com",
    "apple.com", "cloudflare.com", "wix.com", "squarespace.com",
    "shopify.com", "wordpress.com", "godaddy.com",
}

CONTACT_EMAIL_PREFIXES = [
    "events", "booking", "book", "hire", "private", "info",
    "contact", "hello", "reservations", "parties",
]


def extract_contact(text: str, html: str = "") -> str:
    """Extract most relevant contact email for venue booking."""
    raw = set(EMAIL_REGEX.findall(text + " " + html))
    valid = []
    for email in raw:
        local, domain = email.lower().rsplit("@", 1)
        if domain in IGNORE_EMAIL_DOMAINS:
            continue
        if len(local) < 2 or len(domain) < 4:
            continue
        valid.append(email.lower())

    def _priority(e):
        local = e.split("@")[0]
        for i, prefix in enumerate(CONTACT_EMAIL_PREFIXES):
            if local.startswith(prefix):
                return i
        return 99

    valid = sorted(valid, key=_priority)
    return valid[0] if valid else ""


def extract_phone(text: str) -> str:
    """Extract a phone number from text if present."""
    phone_re = re.compile(
        r'(?:\+1[\s\-.]?)?\(?\d{3}\)?[\s\-.]?\d{3}[\s\-.]?\d{4}',
        re.IGNORECASE
    )
    m = phone_re.search(text)
    return m.group(0).strip() if m else ""


# ──────────────────────────────────────────────
# CAPACITY EXTRACTION
# ──────────────────────────────────────────────
def extract_capacity(text: str) -> str:
    """Try to parse venue capacity from page text. Returns string."""
    for pattern in CAPACITY_PATTERNS:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            num = int(m.group(1))
            if 50 < num < 2000:   # sanity bounds
                return str(num)
    return ""


# ──────────────────────────────────────────────
# VENUE TYPE DETECTION
# ──────────────────────────────────────────────
def detect_venue_type(text: str, title: str = "", url: str = "") -> str:
    """Classify venue type from page content."""
    combined = (title + " " + url + " " + text).lower()
    scores = {vtype: 0 for vtype in VENUE_TYPE_KEYWORDS}

    for vtype, kws in VENUE_TYPE_KEYWORDS.items():
        for kw in kws:
            if kw in combined:
                scores[vtype] += 1

    best = max(scores, key=lambda v: scores[v])
    return best if scores[best] > 0 else "Event Space"


# ──────────────────────────────────────────────
# NEIGHBORHOOD DETECTION
# ──────────────────────────────────────────────
def detect_neighborhood(text: str, address: str = "") -> Tuple[str, str]:
    """
    Returns (neighborhood, borough) tuple.
    Searches text and address for known NYC neighborhoods.
    """
    combined = (address + " " + text).lower()

    for hood in BROOKLYN_NEIGHBORHOODS:
        if hood in combined:
            return hood.title(), "Brooklyn"

    for hood in MANHATTAN_NEIGHBORHOODS:
        if hood in combined:
            return hood.title(), "Manhattan"

    # Fallback: detect borough only
    if "brooklyn" in combined:
        return "", "Brooklyn"
    if "manhattan" in combined or "new york, ny" in combined:
        return "", "Manhattan"

    return "", ""


# ──────────────────────────────────────────────
# DESCRIPTION EXTRACTION
# ──────────────────────────────────────────────
def extract_description(html: str, text: str = "") -> str:
    """
    Try meta description first, then first substantive paragraph.
    Returns a 1-2 sentence description.
    """
    try:
        soup = BeautifulSoup(html[:30000], "lxml")

        # Try meta description
        meta = soup.find("meta", attrs={"name": "description"})
        if meta and meta.get("content"):
            return meta["content"].strip()[:250]

        # Try og:description
        og = soup.find("meta", property="og:description")
        if og and og.get("content"):
            return og["content"].strip()[:250]

        # Try first substantial paragraph
        for p in soup.find_all("p"):
            t = p.get_text(strip=True)
            if len(t) > 60:
                return t[:250]

    except Exception:
        pass

    # Fallback: first 200 chars of clean text
    clean = text.strip()
    if clean:
        return clean[:200] + ("..." if len(clean) > 200 else "")
    return ""


# ──────────────────────────────────────────────
# SIGNAL DETECTION (must-have / nice-to-have)
# ──────────────────────────────────────────────
def _keyword_hit(text: str, keywords: List[str]) -> bool:
    t = text.lower()
    return any(kw in t for kw in keywords)


def detect_signals(text: str, html: str = "") -> Dict[str, bool]:
    """
    Detect all venue quality signals. Returns a dict of bool flags.
    """
    combined = (text + " " + html).lower()
    return {
        "has_rooftop":        _keyword_hit(combined, ROOFTOP_KEYWORDS),
        "has_private_events": _keyword_hit(combined, PRIVATE_EVENT_KEYWORDS),
        "has_bar_service":    _keyword_hit(combined, BAR_SERVICE_KEYWORDS),
        "has_views":          _keyword_hit(combined, VIEWS_KEYWORDS),
        "has_indoor_backup":  _keyword_hit(combined, INDOOR_BACKUP_KEYWORDS),
        "has_nightlife":      _keyword_hit(combined, NIGHTLIFE_KEYWORDS),
        "has_afrocultural":   _keyword_hit(combined, AFROCULTURAL_KEYWORDS),
        "should_exclude":     _keyword_hit(combined, EXCLUDE_KEYWORDS),
    }


# ──────────────────────────────────────────────
# NOTES GENERATION
# ──────────────────────────────────────────────
def generate_venue_notes(venue: Dict, signals: Dict, existing_notes: str = "") -> str:
    """Build a rich notes field from signals and seed notes."""
    parts = []

    if existing_notes:
        parts.append(existing_notes)
    else:
        if signals.get("has_afrocultural"):
            parts.append("⭐ Has hosted Afrobeats/cultural events — Priority lead")
        if signals.get("has_nightlife"):
            parts.append("DJ/nightlife programming verified")
        if signals.get("has_views"):
            parts.append("Views confirmed")
        if signals.get("has_indoor_backup"):
            parts.append("Indoor backup option available")
        if signals.get("has_bar_service"):
            parts.append("Bar service available")
        if signals.get("has_private_events"):
            parts.append("Private events/buyout available")

        cap = venue.get("capacity", "")
        if cap:
            try:
                n = int(cap)
                if n < 150:
                    parts.append(f"⚠ Capacity {n} — below 150 minimum")
                elif n > 400:
                    parts.append(f"⚠ Capacity {n} — above 400 max")
                elif 200 <= n <= 300:
                    parts.append(f"Capacity {n} — ideal range ✓")
                else:
                    parts.append(f"Capacity {n}")
            except ValueError:
                pass

    # Pricing hints extracted from text if we can detect them
    # (handled in main enrichment loop by checking text for "$")

    if signals.get("should_exclude"):
        parts.insert(0, "⚠ POSSIBLE EXCLUSION: Check for wedding-only or DJ restrictions")

    return "; ".join(parts[:6]) if parts else "Verify private event availability and capacity"
