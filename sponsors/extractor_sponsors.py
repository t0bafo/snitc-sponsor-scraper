"""
extractor.py — Extracts structured brand data from fetched HTML and search snippets.
"""
import re
import logging
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from sponsors.config_sponsors import (
    CATEGORIES, DIVERSITY_KEYWORDS, NYC_KEYWORDS,
    FOUNDER_KEYWORDS, EMAIL_PRIORITY_PREFIXES,
)

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# EMAIL EXTRACTION
# ──────────────────────────────────────────────
EMAIL_REGEX = re.compile(
    r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}',
    re.IGNORECASE
)

IGNORE_EMAIL_DOMAINS = {
    "example.com", "sentry.io", "w3.org", "schema.org", "google.com",
    "apple.com", "cloudflare.com", "wix.com", "squarespace.com",
    "shopify.com", "bigcommerce.com", "godaddy.com", "wordpress.com",
    "gmail.com", "yahoo.com", "hotmail.com", "domain.com", "email.com",
}

IGNORE_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".pdf", ".mp4",
    ".js", ".css", ".ico", ".woff", ".woff2", ".ashx",
}

IGNORE_EMAIL_PREFIXES = {
    "noreply", "no-reply", "support", "abuse", "postmaster",
    "security", "webmaster", "privacy", "legal", "billing", "help",
}


def is_valid_email(email: str) -> bool:
    """Check if email looks like a real business contact."""
    e = email.lower().strip()
    if "@" not in e: return False
    
    if any(e.endswith(ext) for ext in IGNORE_EXTENSIONS):
        return False
        
    local, domain = e.rsplit("@", 1)
    if any(s in domain for s in ["sentry", "wix-code", "squarespace", "shopify", "example"]): 
        return False
    if domain in IGNORE_EMAIL_DOMAINS: return False
    if len(domain) < 4 or "." not in domain: return False
    if domain.split(".")[-1] in {"png", "jpg", "js", "css"}: return False
    
    if len(local) < 2 or len(local) > 40: return False
    if re.match(r'^[a-f0-9]{20,}$', local): return False
    if local in IGNORE_EMAIL_PREFIXES: return False
    
    return True


def extract_emails(text: str, html: str = "") -> List[str]:
    """Extract and rank contact emails from page text and HTML."""
    raw_emails = set(EMAIL_REGEX.findall(text + " " + html))
    valid = [e.lower() for e in raw_emails if is_valid_email(e)]

    # Sort: prioritize partnership-relevant prefixes
    def _priority(e):
        local = e.split("@")[0]
        for i, prefix in enumerate(EMAIL_PRIORITY_PREFIXES):
            if local.startswith(prefix):
                return i
        return 99

    return sorted(valid, key=_priority)


# ──────────────────────────────────────────────
# INSTAGRAM EXTRACTION
# ──────────────────────────────────────────────
INSTAGRAM_PATTERNS = [
    re.compile(r'instagram\.com/([A-Za-z0-9._]{2,30})', re.IGNORECASE),
    re.compile(r'@([A-Za-z0-9._]{2,30})\b', re.IGNORECASE),
]

INSTAGRAM_IGNORE = {
    "p", "explore", "accounts", "stories", "reels",
    "tv", "direct", "share", "sharer", "login", "signup",
}


def extract_instagram(html: str, text: str = "") -> Optional[str]:
    """Extract the most relevant Instagram handle from page."""
    all_handles = []

    # First try href links in HTML (most reliable)
    try:
        soup = BeautifulSoup(html[:30000], "lxml")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            m = re.search(r'instagram\.com/([A-Za-z0-9._]{2,30})', href, re.I)
            if m:
                handle = m.group(1).rstrip("/").lower()
                if handle not in INSTAGRAM_IGNORE:
                    all_handles.append(handle)
    except Exception:
        pass

    # Fallback: regex on full text+html
    combined = (text + " " + html)[:20000]
    for pattern in INSTAGRAM_PATTERNS:
        for m in pattern.finditer(combined):
            handle = m.group(1).rstrip("/").lower()
            if handle not in INSTAGRAM_IGNORE and len(handle) > 2:
                all_handles.append(handle)

    if all_handles:
        # Return most-common handle (handles can repeat across page)
        from collections import Counter
        most_common = Counter(all_handles).most_common(1)[0][0]
        return f"@{most_common}"
    return None


# ──────────────────────────────────────────────
# FOUNDER EXTRACTION
# ──────────────────────────────────────────────
NAME_PATTERN = re.compile(
    r'(?:' + '|'.join(re.escape(k) for k in FOUNDER_KEYWORDS) + r')\s+'
    r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})',
    re.IGNORECASE
)


def extract_founders(text: str) -> Optional[str]:
    """Extract founder/CEO names from page text."""
    found = []
    matches = NAME_PATTERN.findall(text)
    for name in matches:
        name = name.strip()
        # Filter out generic words
        if len(name.split()) < 2:
            continue
        if any(word.lower() in {"our", "the", "a", "an", "this", "its"} for word in name.split()):
            continue
        if name not in found:
            found.append(name)

    if found:
        return ", ".join(found[:3])  # max 3 names
    return None


# ──────────────────────────────────────────────
# DIVERSITY DETECTION
# ──────────────────────────────────────────────
def detect_diversity(text: str) -> Optional[str]:
    """Detect diversity/ownership signals from page text."""
    text_lower = text.lower()
    found_tags = []

    for label, keywords in DIVERSITY_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                if label not in found_tags:
                    found_tags.append(label)
                break

    return ", ".join(found_tags) if found_tags else None


# ──────────────────────────────────────────────
# NYC CONNECTION
# ──────────────────────────────────────────────
def detect_nyc_connection(text: str) -> Optional[str]:
    """Detect NYC presence signals and return location description."""
    text_lower = text.lower()
    found = []
    for kw in NYC_KEYWORDS:
        if kw in text_lower:
            found.append(kw.title())
    if found:
        # Return most specific first (borough > city)
        boroughs = [f for f in found if f.lower() in
                    {"brooklyn", "harlem", "bronx", "queens", "manhattan",
                     "bed-stuy", "bushwick", "crown heights", "flatbush",
                     "williamsburg", "fort greene", "bedford-stuyvesant"}]
        if boroughs:
            return f"Yes – {boroughs[0]}"
        return f"Yes – NYC"
    return "No"


# ──────────────────────────────────────────────
# CATEGORY DETECTION
# ──────────────────────────────────────────────
def detect_category(text: str, title: str = "", url: str = "") -> str:
    """Infer the brand category from page text."""
    combined = (title + " " + url + " " + text).lower()
    scores = {cat: 0 for cat in CATEGORIES}

    for cat, keywords in CATEGORIES.items():
        for kw in keywords:
            if kw in combined:
                scores[cat] += 1

    best = max(scores, key=lambda c: scores[c])
    if scores[best] == 0:
        return "Lifestyle"
    return best.replace("_", "/").title()


# ──────────────────────────────────────────────
# BRAND NAME EXTRACTION
# ──────────────────────────────────────────────
def extract_brand_name(title: str, url: str) -> str:
    """Extract a clean brand name from the page title or URL."""
    # Clean common suffixes from page titles
    clean = re.sub(
        r'\s*[|\-–—:]\s*.+$', '', title
    ).strip()

    # If title is too long or generic, fall back to domain
    if not clean or len(clean) > 60 or clean.lower() in {
        "home", "welcome", "index", "homepage", "shop", "store"
    }:
        from urllib.parse import urlparse
        domain = urlparse(url).netloc.replace("www.", "")
        clean = domain.split(".")[0].replace("-", " ").replace("_", " ").title()

    return clean.strip()


# ──────────────────────────────────────────────
# GENERATE NOTES
# ──────────────────────────────────────────────
def generate_notes(brand: Dict) -> str:
    """Auto-generate a notes field explaining why a brand is a good fit."""
    parts = []

    if brand.get("diversity"):
        parts.append(brand["diversity"])
    if brand.get("nyc_connection") and brand["nyc_connection"] != "No":
        parts.append(brand["nyc_connection"])
    if brand.get("founder"):
        parts.append(f"Founded by {brand['founder']}")
    if brand.get("category"):
        parts.append(f"{brand['category']} brand")
    if brand.get("instagram"):
        parts.append("Active on Instagram")
    if brand.get("email"):
        parts.append("Contact available")

    if not parts:
        return "Potential sponsor – verify fit manually"

    return "; ".join(parts[:5])
