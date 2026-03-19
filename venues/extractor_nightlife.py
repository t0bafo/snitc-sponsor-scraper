"""
venues/extractor_venues.py — Extracts venue-specific data from fetched HTML.

Extracts: capacity, venue type, neighborhood, description, contact,
          priority signals (rooftop, private events, bar, views, nightlife).
"""
import re
import logging
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup
import venues.config_venues as cfg

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
    "shopify.com", "wordpress.com", "godaddy.com", "sentry.wix.com",
    "sentry-cdn.com", "domain.com", "yoursite.com", "email.com",
}

IGNORE_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".pdf", ".mp4",
    ".js", ".css", ".ico", ".woff", ".woff2", ".ashx",
}

CONTACT_EMAIL_PREFIXES = [
    "events", "booking", "book", "hire", "private", "info",
    "contact", "hello", "reservations", "parties", "sales", "group",
]


def is_valid_email(email: str) -> bool:
    """Check if email looks like a real business contact."""
    e = email.lower().strip()
    
    # Basic structural check
    if "@" not in e: return False
    
    # Ignore image assets and common non-email files
    if any(e.endswith(ext) for ext in IGNORE_EXTENSIONS):
        return False
        
    local, domain = e.rsplit("@", 1)
    
    # Domain validation
    if any(s in domain for s in ["sentry", "wix-code", "squarespace", "shopify", "example"]): 
        return False
    if domain in IGNORE_EMAIL_DOMAINS: return False
    if len(domain) < 4 or "." not in domain: return False
    if domain.split(".")[-1] in {"png", "jpg", "js", "css"}: return False
    
    # Local part validation
    if len(local) < 2 or len(local) > 40: return False
    # Block long hex-looking strings (likely crash reporting IDs)
    if re.match(r'^[a-f0-9]{20,}$', local): return False
    
    if local in {"noreply", "no-reply", "support", "abuse", "webmaster"}:
        return False
        
    return True


def extract_contact(text: str, html: str = "") -> str:
    """Extract most relevant contact email for venue booking."""
    # Narrow the focus to improve accuracy
    raw = set(EMAIL_REGEX.findall(text + " " + html))
    valid = [e.lower() for e in raw if is_valid_email(e)]
    
    if not valid:
        return ""

    def _priority(e):
        local = e.split("@")[0]
        # Prioritize prefixes like 'events@' or 'booking@'
        for i, prefix in enumerate(CONTACT_EMAIL_PREFIXES):
            if local == prefix or local.startswith(prefix + "."):
                return i
        return 99

    valid = sorted(valid, key=_priority)
    return valid[0]


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
    """
    Parse all capacity candidates from text and return the 'best' one.
    Prioritizes numbers in the target 150-400 range.
    """
    candidates = []
    for pattern in cfg.CAPACITY_PATTERNS:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for m in matches:
            try:
                num = int(m.group(1))
                if 50 < num < 2000:
                    candidates.append(num)
            except (ValueError, IndexError):
                continue
                
    if not candidates:
        return ""
        
    # Pick the best candidate:
    # 1. Prefer numbers in the 200-300 range
    ideal = [c for c in candidates if cfg.CAPACITY_IDEAL_MIN <= c <= cfg.CAPACITY_IDEAL_MAX]
    if ideal: return str(max(ideal))
    
    # 2. Prefer numbers in the 150-400 range
    acceptable = [c for c in candidates if cfg.CAPACITY_MIN <= c <= cfg.CAPACITY_MAX]
    if acceptable: return str(max(acceptable))
    
    # 3. Otherwise return the largest reasonable number
    return str(max(candidates))


# ──────────────────────────────────────────────
# VENUE TYPE DETECTION
# ──────────────────────────────────────────────
def detect_venue_type(text: str, title: str = "", url: str = "") -> str:
    """Classify venue type from page content."""
    combined = (title + " " + url + " " + text).lower()
    scores = {vtype: 0 for vtype in cfg.VENUE_TYPE_KEYWORDS}

    for vtype, kws in cfg.VENUE_TYPE_KEYWORDS.items():
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
    Returns (neighborhood, city) tuple.
    Searches text and address for known priority neighborhoods across cities.
    """
    combined = (address + " " + text).lower()

    for city, neighborhoods in cfg.PRIORITY_NEIGHBORHOODS.items():
        for hood in neighborhoods:
            if hood in combined:
                return hood.title(), city.capitalize()

    # Fallback: detect city only
    if "new york" in combined or "nyc" in combined or "brooklyn" in combined or "manhattan" in combined:
        return "", "Nyc"
    if "atlanta" in combined or "atl" in combined:
        return "", "Atlanta"
    if "dallas" in combined or "dfw" in combined:
        return "", "Dallas"

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
    for kw in keywords:
        if kw in t:
            # Check for negative context within 20 chars before the keyword
            idx = t.find(kw)
            context = t[max(0, idx-20):idx]
            if any(neg in context for neg in ["no ", "not ", "don't ", "cannot ", "closed "]):
                continue
            return True
    return False


def detect_signals(text: str, html: str = "") -> Dict[str, bool]:
    """
    Detect all venue quality signals. Returns a dict of bool flags.
    """
    combined = (text + " " + html).lower()
    return {
        "has_rooftop":        _keyword_hit(combined, cfg.ROOFTOP_KEYWORDS),
        "has_private_events": _keyword_hit(combined, cfg.PRIVATE_EVENT_KEYWORDS),
        "has_bar_service":    _keyword_hit(combined, cfg.BAR_SERVICE_KEYWORDS),
        "has_views":          _keyword_hit(combined, cfg.VIEWS_KEYWORDS),
        "has_indoor_backup":  _keyword_hit(combined, cfg.INDOOR_BACKUP_KEYWORDS),
        "has_nightlife":      _keyword_hit(combined, cfg.NIGHTLIFE_KEYWORDS),
        "has_afrocultural":   _keyword_hit(combined, cfg.AFROCULTURAL_KEYWORDS),
        "should_exclude":     _keyword_hit(combined, cfg.EXCLUDE_KEYWORDS),
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
                if n < cfg.CAPACITY_MIN:
                    parts.append(f"⚠ Capacity {n} — below {cfg.CAPACITY_MIN} minimum")
                elif n > cfg.CAPACITY_MAX:
                    parts.append(f"⚠ Capacity {n} — above {cfg.CAPACITY_MAX} max")
                elif cfg.CAPACITY_IDEAL_MIN <= n <= cfg.CAPACITY_IDEAL_MAX:
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
