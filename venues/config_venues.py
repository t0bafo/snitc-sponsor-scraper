"""
venues/config_venues.py — Configuration for the SNITC Rooftop Venue Scraper.

Event: Saturday Night in the City (SNITC)
Date : Memorial Day Weekend — Target Saturday May 23, 2026
Need : Rooftop / outdoor terrace, 200-300 capacity, Brooklyn or Manhattan
"""

# ──────────────────────────────────────────────
# EVENT CONTEXT
# ──────────────────────────────────────────────
EVENT_NAME     = "Saturday Night in the City (SNITC)"
EVENT_DATE     = "May 23, 2026 (Memorial Day Weekend)"
EVENT_CAPACITY = "200-300"
EVENT_TYPE     = "Nightlife / Cultural — Afro House, Amapiano, Afrobeats"

# ──────────────────────────────────────────────
# SEARCH QUERIES
# ──────────────────────────────────────────────
SEARCH_QUERIES = {
    "nyc": [
        "rooftop event venues Brooklyn NYC 200 300 capacity private",
        "outdoor terrace private events Manhattan buyout 2026",
        "rooftop bar buyout NYC 200-300 people nightlife",
        "Brooklyn rooftop party venue private event space",
        "rooftop event space Williamsburg Bushwick private hire",
        "Manhattan rooftop venue private events nightlife",
    ],
    "atlanta": [
        "rooftop event venues Atlanta 200 300 capacity private",
        "Midtown Atlanta outdoor terrace private events buyout",
        "rooftop bar buyout Atlanta 200-300 people nightlife",
        "Atlanta West Midtown party venue private event space",
        "rooftop venue Atlanta Afrobeats cultural event",
    ],
    "dallas": [
        "rooftop event venues Dallas 200 300 capacity private",
        "Deep Ellum outdoor terrace private events buyout",
        "rooftop bar buyout Dallas 200-300 people nightlife",
        "Uptown Dallas party venue private event space",
        "rooftop event space Dallas arts district private hire",
    ]
}

# ──────────────────────────────────────────────
# VENUE LISTING SITES (to search directly)
# ──────────────────────────────────────────────
VENUE_DIRECTORY_URLS = [
    "https://www.peerspace.com/s/new-york--ny/rooftop",
    "https://www.venuelust.com/venues/rooftop",
    "https://thebash.com/venues/ny/brooklyn",
    "https://www.eventup.com/venues/new-york/brooklyn",
]

# ──────────────────────────────────────────────
# PRIORITY NEIGHBORHOODS
# ──────────────────────────────────────────────
PRIORITY_NEIGHBORHOODS = {
    "nyc": [
        "williamsburg", "bushwick", "greenpoint", "dumbo",
        "brooklyn heights", "park slope", "bedford-stuyvesant",
        "bed-stuy", "crown heights", "red hook", "gowanus",
        "lower east side", "les", "east village", "chelsea",
        "meatpacking", "meatpacking district", "midtown",
        "soho", "tribeca", "flatiron",
    ],
    "atlanta": [
        "midtown", "west midtown", "buckhead", "old fourth ward",
        "inman park", "downtown", "virginia-highland", "poncey-highland",
        "sweet auburn", "grant park", "reynoldstown", "east atlanta village",
    ],
    "dallas": [
        "deep ellum", "uptown", "downtown", "design district",
        "oak lawn", "knox-henderson", "lower greenville", "bishop arts",
        "trinity groves", "victory park",
    ]
}

# ──────────────────────────────────────────────
# VENUE TYPE KEYWORDS
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
# MUST-HAVE SIGNALS (venue qualifies if ANY match)
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
# EXCLUSION SIGNALS (skip if these dominate)
# ──────────────────────────────────────────────
EXCLUDE_KEYWORDS = [
    "wedding only", "weddings only", "no dj", "no dancing",
    "permanently closed", "closed permanently", "out of business",
]

# ──────────────────────────────────────────────
# CAPACITY EXTRACTION PATTERNS
# ──────────────────────────────────────────────
# Used to pull capacity numbers from page text
CAPACITY_PATTERNS = [
    r'(?:up to|capacity[:\s]+|accommodates?[:\s]+|holds?[:\s]+|max[:\s]+)'
    r'(\d{2,4})\s*(?:guests?|people|persons?|attendees?)?',
    r'(\d{2,4})\s*(?:guests?|people|standing)',
]

# Capacity range for SNITC — flag outside this
CAPACITY_MIN = 150
CAPACITY_MAX = 400
CAPACITY_IDEAL_MIN = 200
CAPACITY_IDEAL_MAX = 300

# ──────────────────────────────────────────────
# NICE-TO-HAVE SIGNALS (boost priority score)
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
# SCORING RULES (for priority ranking)
# ──────────────────────────────────────────────
PRIORITY_SCORE_RULES = {
    "has_rooftop": 3,
    "has_private_events": 2,
    "primary_location": 2,    # Replaces brooklyn
    "secondary_location": 1,  # Replaces manhattan
    "capacity_in_range": 2,
    "has_bar_service": 1,
    "has_views": 1,
    "has_indoor_backup": 1,
    "has_nightlife": 2,
    "has_afrocultural": 3,
    "has_website": 1,
    "has_contact": 1,
}

PRIORITY_HIGH_SCORE  = 8   # Priority A
PRIORITY_MED_SCORE   = 5   # Priority B
# Below PRIORITY_MED_SCORE → Priority C

# ──────────────────────────────────────────────
# OUTPUT
# ──────────────────────────────────────────────
OUTPUT_DIR   = "output"
OUTPUT_FILE  = "snitc_venues.csv"

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
