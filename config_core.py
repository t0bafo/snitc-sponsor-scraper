"""
config_core.py — Shared keyword lists and extraction patterns across all scrapers.
"""

# ──────────────────────────────────────────────
# NETWORKING & BOT SETTINGS
# ──────────────────────────────────────────────
REQUEST_TIMEOUT = 12       # seconds
SCRAPE_DELAY    = 1.2      # seconds between page fetches

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
# SHARED VENUE TYPE KEYWORDS
# ──────────────────────────────────────────────
VENUE_TYPE_KEYWORDS = {
    "Hotel Rooftop": [
        "hotel rooftop", "hotel roof", "rooftop bar hotel",
        "hotel terrace", "rooftop lounge hotel",
    ],
    "Restaurant Rooftop": [
        "restaurant rooftop", "rooftop restaurant", "rooftop dining",
        "rooftop patio restaurant", "terrace restaurant",
    ],
    "Rooftop Bar": [
        "rooftop bar", "sky bar", "rooftop lounge", "rooftop cocktail",
        "rooftop happy hour",
    ],
    "Event/Private Space": [
        "event space", "private event", "event venue", "event hall",
        "buyout", "private hire", "exclusive venue",
    ],
    "Outdoor Terrace": [
        "outdoor terrace", "rooftop terrace", "outdoor patio",
        "al fresco", "garden terrace",
    ],
    "Cultural Space": [
        "cultural space", "art space", "gallery rooftop",
        "creative space rooftop",
    ],
}

# ──────────────────────────────────────────────
# SHARED QUALITY SIGNALS (Must-Haves)
# ──────────────────────────────────────────────
ROOFTOP_KEYWORDS = [
    "rooftop", "roof top", "roof deck", "roofdecks",
    "rooftop terrace", "terrace", "outdoor event",
    "outdoor space", "skyline views", "sky lounge",
    "open-air", "open air", "al fresco",
]

PRIVATE_EVENT_KEYWORDS = [
    "private event", "private events", "private hire",
    "buyout", "full buyout", "event rental", "venue rental",
    "corporate events", "rent the venue", "exclusive use",
    "event space", "event venue",
]

BAR_SERVICE_KEYWORDS = [
    "bar service", "full bar", "open bar", "cash bar",
    "cocktail service", "bar program", "bartender",
    "beverage package", "drink package",
]

# ──────────────────────────────────────────────
# EXCLUSION SIGNALS
# ──────────────────────────────────────────────
EXCLUDE_KEYWORDS = [
    "wedding only", "weddings only", "no dj", "no dancing",
    "permanently closed", "closed permanently", "out of business",
]

# ──────────────────────────────────────────────
# CAPACITY BRAIN
# ──────────────────────────────────────────────
CAPACITY_PATTERNS = [
    r'(?:up to|capacity[:\s]+|accommodates?[:\s]+|holds?[:\s]+|max[:\s]+)'
    r'(\d{2,4})\s*(?:guests?|people|persons?|attendees?)?',
    r'(\d{2,4})\s*(?:guests?|people|standing)',
]

# ──────────────────────────────────────────────
# NICE-TO-HAVE SIGNALS
# ──────────────────────────────────────────────
VIEWS_KEYWORDS = [
    "skyline view", "manhattan skyline", "city view", "waterfront",
    "river view", "panoramic", "stunning view", "scenic",
]

INDOOR_BACKUP_KEYWORDS = [
    "indoor backup", "indoor option", "indoor space", "rain plan",
    "enclosed space", "retractable roof", "covered terrace",
]

NIGHTLIFE_KEYWORDS = [
    "nightlife", "dj", "dance floor", "dancing", "live music",
    "music venue", "nightclub", "late night", "lounge",
    "beats", "amapiano", "afrobeats", "afro house",
]

AFROCULTURAL_KEYWORDS = [
    "afrobeats", "amapiano", "afro house", "afro-caribbean",
    "caribbean", "african music", "diaspora", "pan-african",
    "black culture", "cultural events",
]

# ──────────────────────────────────────────────
# SCORING ENGINE
# ──────────────────────────────────────────────
PRIORITY_SCORE_RULES = {
    "has_rooftop": 3,
    "has_private_events": 2,
    "primary_location": 2,
    "secondary_location": 1,
    "capacity_in_range": 2,
    "has_bar_service": 1,
    "has_views": 1,
    "has_indoor_backup": 1,
    "has_nightlife": 2,
    "has_afrocultural": 3,
    "has_website": 1,
    "has_contact": 1,
}

PRIORITY_HIGH_SCORE  = 8
PRIORITY_MED_SCORE   = 5

# ──────────────────────────────────────────────
# OUTPUT DATA SCHEMA
# ──────────────────────────────────────────────
OUTPUT_DIR   = "output"
CSV_COLUMNS = [
    "Venue Name",
    "Location",
    "Neighborhood",
    "City",
    "Capacity",
    "Venue Type",
    "Description",
    "Website",
    "Contact",
    "Priority",
    "Notes",
    "Source URL",
]

# ──────────────────────────────────────────────
# RETAIL VENUE SIGNALS (for OTMB)
# ──────────────────────────────────────────────

RETAIL_SIGNALS = {
    # Regex for square footage
    "sqft_pattern":  r"(\d{1,2},?\d{3})\s*(?:sq\.?\s*ft\.?|square feet)",
    # Regex for ceiling height
    "ceiling_pattern": r"(\d{1,2})\s*(?:\-|\s)?ft(?:\.|\s|,|$).*?ceiling|ceiling.*?(\d{1,2})\s*(?:\-|\s)?ft",

    # Space characteristics
    "storefront": [
        "storefront", "street-facing", "window display",
        "retail frontage", "ground floor retail",
    ],
    "natural_light": [
        "natural light", "skylight", "sunlight",
        "light-filled", "sun-drenched", "bright space",
    ],
    "white_walls": [
        "white walls", "neutral walls", "minimal",
        "clean aesthetic", "gallery white",
    ],
    "high_ceilings": [
        "high ceiling", "10 ft", "10-ft", "12 ft", "15 ft",
        "exposed ceiling", "soaring ceilings", "vaulted",
    ],
    "open_floor": [
        "open floor plan", "open layout", "flexible space",
        "column-free", "open plan", "loft-style",
    ],
    "retail_fixtures": [
        "racks", "shelves", "display fixtures",
        "retail fixtures", "clothing racks", "display cases",
    ],
    "storefront_windows": [
        "large windows", "floor-to-ceiling windows",
        "glass storefront", "window display", "showcase windows",
    ],
    "blank_canvas": [
        "blank canvas", "raw space", "white box",
        "empty shell", "unfinished",
    ],
    "transformable": [
        "customizable", "adaptable", "flexible",
        "transformable", "multi-use",
    ],
    "short_term": [
        "short-term", "temporary", "pop-up",
        "event rental", "daily rental", "hourly rental",
        "flexible lease", "month-to-month",
    ],
}

RETAIL_VENUE_TYPES = [
    "storefront",
    "pop-up_space",
    "art_gallery",
    "design_studio",
    "showroom",
    "warehouse",
    "loft",
    "creative_space",
]

RETAIL_EXCLUDE_KEYWORDS = [
    "nightclub", "bar ", "lounge", "restaurant",
    "hotel ballroom", "banquet hall", "conference center", "theater",
    "permanently occupied", "long-term lease only",
]

# CSV schema for retail venue exports
RETAIL_CSV_COLUMNS = [
    "Name",
    "Website",
    "Neighborhood",
    "Sq Ft",
    "Ceiling Height",
    "Has Storefront",
    "Has Natural Light",
    "Has White Walls",
    "Has High Ceilings",
    "Has Open Floor",
    "Has Retail Fixtures",
    "Has Storefront Windows",
    "Is Transformable",
    "Short Term Available",
    "Venue Type",
    "Contact Email",
    "Contact Phone",
    "Score",
    "Priority",
    "Fit Reasons",
    "Source",
]

# ──────────────────────────────────────────────
# OPERATING RETAIL STORE SIGNALS (for OTMB)
# ──────────────────────────────────────────────

RETAIL_STORE_SIGNALS = {
    # Event rental availability (CRITICAL — must actively search for these)
    "private_events": [
        "private events", "event rental", "rent the space",
        "book the store", "after-hours rental", "exclusive events",
        "private shopping", "store buyout", "book our space",
        "host your event", "venue rental", "space rental",
        "private activations", "brand partnerships", "after hours",
    ],

    # Aesthetic signals (relevant for OTMB vibe)
    "modern_aesthetic": [
        "modern", "contemporary", "minimalist", "clean lines",
        "scandinavian", "industrial", "editorial", "sleek",
    ],

    "curated": [
        "curated", "carefully selected", "hand-picked",
        "thoughtfully designed", "bespoke", "artisanal",
    ],

    # Store type keywords (for classification)
    "furniture_store": [
        "furniture", "home goods", "interior design",
        "furnishings", "home decor", "sofas", "chairs",
    ],
    "sneaker_boutique": [
        "sneakers", "kicks", "footwear", "sneaker boutique",
        "premium sneakers", "limited edition",
    ],
    "streetwear": [
        "streetwear", "urban fashion", "hype", "designer streetwear",
        "contemporary fashion",
    ],
    "vintage": [
        "vintage", "secondhand", "thrift", "consignment",
        "pre-loved", "archive",
    ],
    "concept_store": [
        "concept store", "lifestyle", "multi-brand",
        "curated brands", "editorial retail",
    ],

    # Negative signals
    "chain_store": [
        "target", "h&m", "gap", "old navy", "tj maxx",
        "homegoods", "walmart", "ikea",
    ],
    "fast_fashion": [
        "zara", "forever 21", "fashion nova", "shein",
        "fast fashion",
    ],
}

RETAIL_STORE_TYPES = [
    "furniture_showroom",
    "sneaker_boutique",
    "streetwear_store",
    "vintage_boutique",
    "concept_store",
    "empty_space",
]
