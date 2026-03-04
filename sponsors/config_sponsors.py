"""
sponsors/config_sponsors.py — All configuration for the SNITC sponsor scraper.
Event: Saturday Night in the City (SNITC), April 25, 2026, Brooklyn NY

(Moved from root config.py — root config.py retained for backwards compat)
"""
# Re-export everything from the root config for the sponsors pipeline.
# This allows sponsors/ to import from here cleanly.
from config import (
    SEARCH_QUERIES,
    CATEGORIES,
    DIVERSITY_KEYWORDS,
    NYC_KEYWORDS,
    FOUNDER_KEYWORDS,
    EMAIL_PRIORITY_PREFIXES,
    TIER_1_SCORE,
    TIER_2_SCORE,
    TIER_SCORE_RULES,
    REQUEST_TIMEOUT,
    SEARCH_DELAY,
    SCRAPE_DELAY,
    MAX_RESULTS_PER_QUERY,
    MAX_BRANDS,
    HEADERS,
    OUTPUT_DIR,
    OUTPUT_FILE,
    CSV_COLUMNS,
)

__all__ = [
    "SEARCH_QUERIES", "CATEGORIES", "DIVERSITY_KEYWORDS", "NYC_KEYWORDS",
    "FOUNDER_KEYWORDS", "EMAIL_PRIORITY_PREFIXES", "TIER_1_SCORE",
    "TIER_2_SCORE", "TIER_SCORE_RULES", "REQUEST_TIMEOUT", "SEARCH_DELAY",
    "SCRAPE_DELAY", "MAX_RESULTS_PER_QUERY", "MAX_BRANDS", "HEADERS",
    "OUTPUT_DIR", "OUTPUT_FILE", "CSV_COLUMNS",
]
