"""
venues/config_venues.py — Dynamic configuration for Venues.
Loads event-specific data from YAML and shared keywords from config_core.
"""
from config_core import *
from config_loader import get_config

# --- EVENT CONTEXT (Defaults) ---
EVENT_NAME     = "Saturday Night in the City (SNITC)"
EVENT_DATE     = "May 23, 2026 (Memorial Day Weekend)"
EVENT_CAPACITY = "200-300"
EVENT_TYPE     = "Nightlife / Cultural — Afro House, Amapiano, Afrobeats"

# --- SEARCH QUERIES (Defaults) ---
SEARCH_QUERIES = {
    "nyc": [
        "rooftop event venues Brooklyn NYC 200 300 capacity private",
        "outdoor terrace private events Manhattan buyout 2026",
    ],
    "atlanta": [
        "rooftop event venues Atlanta 200 300 capacity private",
    ],
    "dallas": [
        "rooftop event venues Dallas 200 300 capacity private",
    ]
}

# --- PRIORITY NEIGHBORHOODS (Defaults) ---
_NYC_HOODS = [
    "williamsburg", "greenpoint", "dumbo", "brooklyn heights", 
    "park slope", "bed-stuy", "crown heights", "les", "chelsea",
]
PRIORITY_NEIGHBORHOODS = {
    "nyc": _NYC_HOODS,
    "atlanta": ["midtown", "buckhead"],
    "dallas": ["deep ellum", "uptown"]
}

# --- CAPACITY BOUNDS (Defaults) ---
CAPACITY_MIN = 150
CAPACITY_MAX = 400
CAPACITY_IDEAL_MIN = 200
CAPACITY_IDEAL_MAX = 300

# --- DIRECTORY URLS (Shared) ---
VENUE_DIRECTORY_URLS = [
    "https://www.peerspace.com/s/new-york--ny/rooftop",
    "https://thebash.com/venues/ny/brooklyn",
]


def initialize_config(config_path=None, city="nyc"):
    """
    Call this at startup to load a YAML config.
    Updates the global variables in this module.
    """
    global EVENT_NAME, EVENT_DATE, EVENT_CAPACITY, EVENT_TYPE
    global CAPACITY_MIN, CAPACITY_MAX, CAPACITY_IDEAL_MIN, CAPACITY_IDEAL_MAX
    global SEARCH_QUERIES, PRIORITY_NEIGHBORHOODS
    
    cfg = get_config(config_path)
    
    # Overwrite with YAML values if present
    EVENT_NAME = cfg.event_name
    EVENT_DATE = cfg.event_date
    EVENT_TYPE = cfg.event_type
    
    CAPACITY_MIN = cfg.capacity_min
    CAPACITY_MAX = cfg.capacity_max
    CAPACITY_IDEAL_MIN = cfg.capacity_ideal_min
    CAPACITY_IDEAL_MAX = cfg.capacity_ideal_max
    
    EVENT_CAPACITY = f"{CAPACITY_IDEAL_MIN}-{CAPACITY_IDEAL_MAX}"

    # If the YAML provided search queries, use them for the active city
    if cfg.search_queries:
        SEARCH_QUERIES[city.lower()] = cfg.search_queries
        
    # If the YAML provided neighborhoods, use them for the active city
    if cfg.priority_neighborhoods:
        PRIORITY_NEIGHBORHOODS[city.lower()] = [n.lower() for n in cfg.priority_neighborhoods]
        
    # Add target vibes to shared signal lists if they exist in YAML
    if cfg.target_vibe:
        for vibe in cfg.target_vibe:
            v_low = vibe.lower()
            if v_low not in ROOFTOP_KEYWORDS:
                ROOFTOP_KEYWORDS.append(v_low)
