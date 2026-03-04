"""
config.py — All configuration for the SNITC sponsor scraper.
Event: Saturday Night in the City (SNITC), April 25, 2026, Brooklyn NY
"""

# ──────────────────────────────────────────────
# SEARCH QUERIES
# ──────────────────────────────────────────────
SEARCH_QUERIES = [
    "Black-owned spirits brands NYC",
    "Caribbean rum brands New York",
    "Brooklyn-based lifestyle brands",
    "Black-owned beauty brands New York",
    "Afro-Latino beverage brands NYC",
    "Harlem-based streetwear brands",
    "Black women-owned wine brands New York",
    "Caribbean-founded brands Brooklyn",
    "Minority-owned alcohol brands New York",
    "Diaspora lifestyle brands NYC",
    "Black-owned cocktail mixer brands",
    "African diaspora fashion brand New York",
    "BIPOC-owned wellness brands Brooklyn",
    "Black-owned food beverage brand NYC founder",
    "Caribbean-owned fashion brand NYC",
    "Black-owned skincare beauty brand New York",
    "Latino-owned spirits brand NYC",
    "Black founder alcohol brand Brooklyn",
    "Afrobeats culture brand NYC sponsor",
    "Black-owned streetwear NYC indie brand",
]

# ──────────────────────────────────────────────
# CATEGORIES
# ──────────────────────────────────────────────
CATEGORIES = {
    "alcohol": [
        "spirits", "rum", "whiskey", "whisky", "vodka", "gin", "tequila",
        "mezcal", "wine", "beer", "brewery", "distillery", "cocktail",
        "bitters", "liqueur", "hard seltzer", "hard cider", "mead",
    ],
    "beauty_wellness": [
        "skincare", "beauty", "cosmetics", "wellness", "hair care",
        "haircare", "self-care", "spa", "lotion", "serum", "makeup",
        "organic beauty", "natural hair", "fragrance", "perfume",
    ],
    "fashion_streetwear": [
        "fashion", "streetwear", "apparel", "clothing", "wear", "hoodie",
        "sneaker", "shoes", "accessories", "jewelry", "bags", "handbags",
        "urban wear", "designer", "collection",
    ],
    "lifestyle": [
        "lifestyle", "culture", "community", "magazine", "media",
        "creative", "agency", "pop-up", "event", "experiences",
        "merch", "merchandise",
    ],
    "food_beverage": [
        "food", "beverage", "drink", "juice", "kombucha", "tea", "coffee",
        "snack", "sauce", "hot sauce", "seasoning", "spice", "catering",
        "restaurant", "café", "cafe", "bakery", "sweets",
    ],
}

# ──────────────────────────────────────────────
# DIVERSITY KEYWORDS (indicates brand identity)
# ──────────────────────────────────────────────
DIVERSITY_KEYWORDS = {
    "Black-owned": [
        "black-owned", "black owned", "black founder", "black woman-owned",
        "black women-owned", "african american owned", "african-american owned",
        "black entrepreneur", "by black", "proudly black",
    ],
    "Caribbean-owned": [
        "caribbean", "jamaican-owned", "haitian-owned", "trinidadian",
        "barbadian", "bahamian", "west indian", "caribbean diaspora",
        "afro-caribbean",
    ],
    "African-owned": [
        "african-owned", "african owned", "nigerian-owned", "ghanaian-owned",
        "senegalese", "kenyan", "african diaspora", "pan-african",
    ],
    "Latino/Latina-owned": [
        "latino-owned", "latina-owned", "latinx", "hispanic-owned",
        "afro-latino", "afrolatino", "dominican-owned", "puerto rican-owned",
        "colombian-owned", "salvadoran-owned",
    ],
    "BIPOC-owned": [
        "bipoc", "minority-owned", "people of color", "poc-owned",
        "woman of color", "women of color", "diversity",
    ],
    "Women-owned": [
        "women-owned", "woman-owned", "female-founded", "female founder",
        "women founded", "woman-founded",
    ],
}

# ──────────────────────────────────────────────
# NYC CONNECTION KEYWORDS
# ──────────────────────────────────────────────
NYC_KEYWORDS = [
    "brooklyn", "harlem", "bronx", "queens", "manhattan", "new york city",
    "nyc", "new york", "bed-stuy", "bushwick", "crown heights",
    "flatbush", "fort greene", "williamsburg", "bedford-stuyvesant",
    "brownsville", "east new york", "jamaica queens", "the bronx",
]

# ──────────────────────────────────────────────
# FOUNDER CONTEXT KEYWORDS
# ──────────────────────────────────────────────
FOUNDER_KEYWORDS = [
    "founded by", "co-founded by", "co-founder", "founder", "created by",
    "started by", "started in", "launched by", "ceo", "chief executive",
    "owner", "entrepreneur", "visionary", "behind the brand",
]

# ──────────────────────────────────────────────
# EMAIL PATTERNS PRIORITY
# ──────────────────────────────────────────────
EMAIL_PRIORITY_PREFIXES = [
    "partnerships", "sponsor", "collab", "hello", "hi", "contact",
    "info", "press", "pr", "sales", "team", "us",
]

# ──────────────────────────────────────────────
# TIER RULES
# ──────────────────────────────────────────────
# Scoring thresholds for tier assignment
TIER_1_SCORE = 4   # Very strong fit
TIER_2_SCORE = 2   # Good fit
# Below TIER_2_SCORE → Tier 3

# Point values for tier scoring
TIER_SCORE_RULES = {
    "has_email": 2,
    "has_instagram": 1,
    "nyc_based": 2,
    "diversity_owned": 2,
    "founder_led": 1,
    "has_website": 1,
}

# ──────────────────────────────────────────────
# SCRAPER SETTINGS
# ──────────────────────────────────────────────
REQUEST_TIMEOUT = 12       # seconds
SEARCH_DELAY = 2.5         # seconds between search queries
SCRAPE_DELAY = 1.2         # seconds between page fetches
MAX_RESULTS_PER_QUERY = 8  # DuckDuckGo results per query
MAX_BRANDS = 60            # max total brands to process

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

# ──────────────────────────────────────────────
# OUTPUT
# ──────────────────────────────────────────────
OUTPUT_DIR = "output"
OUTPUT_FILE = "snitc_sponsors.csv"

CSV_COLUMNS = [
    "Brand Name",
    "Category",
    "Website",
    "Instagram",
    "Email",
    "Founder(s)",
    "Diversity",
    "NYC Connection",
    "Tier",
    "Notes",
    "Source URL",
]
