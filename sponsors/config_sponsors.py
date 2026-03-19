"""
sponsors/config_sponsors.py — Dynamic configuration for Sponsors.
Loads event-specific data from YAML and shared networking from config_core.
"""
from config_core import *
from config_loader import get_config

# --- EVENT CONTEXT (Defaults) ---
EVENT_NAME     = "Saturday Night in the City (SNITC)"
EVENT_DATE     = "May 23, 2026 (Memorial Day Weekend)"

# --- SEARCH QUERIES (Defaults) ---
SEARCH_QUERIES = [
    "Black-owned spirits brands NYC",
    "Caribbean rum brands New York",
    "Brooklyn-based lifestyle brands",
    "Black-owned beauty brands New York",
    "Afrobeats culture brand NYC sponsor",
]

# --- CATEGORIES (Static) ---
CATEGORIES = {
    "alcohol": [
        "spirits", "rum", "whiskey", "whisky", "vodka", "gin", "tequila",
        "wine", "beer", "cocktail",
    ],
    "beauty_wellness": [
        "skincare", "beauty", "cosmetics", "wellness", "hair care",
    ],
    "fashion_streetwear": [
        "fashion", "streetwear", "apparel", "clothing",
    ],
    "lifestyle": [
        "lifestyle", "culture", "community",
    ],
    "food_beverage": [
        "food", "beverage", "drink", "juice", "tea", "coffee",
    ],
}

# --- DIVERSITY KEYWORDS (Static) ---
DIVERSITY_KEYWORDS = {
    "Black-owned": ["black-owned", "black owned", "black founder"],
    "Caribbean-owned": ["caribbean", "jamaican-owned", "haitian-owned"],
    "African-owned": ["african-owned", "african owned", "pan-african"],
    "Latino/Latina-owned": ["latino-owned", "latina-owned", "latinx"],
    "BIPOC-owned": ["bipoc", "minority-owned"],
    "Women-owned": ["women-owned", "woman-owned", "female-founded"],
}

# --- NYC CONNECTION (Static) ---
NYC_KEYWORDS = [
    "brooklyn", "harlem", "bronx", "queens", "manhattan", "nyc", "new york",
    "bed-stuy", "bushwick", "crown heights", "williamsburg",
]

# --- FOUNDER CONTEXT (Static) ---
FOUNDER_KEYWORDS = ["founded by", "co-founder", "founder", "ceo", "owner"]

# --- EMAIL PATTERNS (Static) ---
EMAIL_PRIORITY_PREFIXES = ["partnerships", "sponsor", "collab", "hello", "info"]

# --- TIER SCORING (Static) ---
TIER_1_SCORE = 4
TIER_2_SCORE = 2
TIER_SCORE_RULES = {
    "has_email": 2,
    "has_instagram": 1,
    "nyc_based": 2,
    "diversity_owned": 2,
    "founder_led": 1,
    "has_website": 1,
}

def initialize_config(config_path=None, city="nyc"):
    """
    Call this at startup to load a YAML config.
    Updates the global variables in this module.
    """
    global EVENT_NAME, EVENT_DATE, SEARCH_QUERIES
    
    cfg = get_config(config_path)
    
    EVENT_NAME = cfg.event_name
    EVENT_DATE = cfg.event_date
    
    if cfg.sponsor_search_queries:
        SEARCH_QUERIES = cfg.sponsor_search_queries
