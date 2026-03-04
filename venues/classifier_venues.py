"""
venues/classifier_venues.py — Assigns Priority A/B/C to venues based on signals.

Priority A: Strong fit — rooftop + private events + right capacity + nightlife
Priority B: Good fit — most criteria met, minor gaps
Priority C: Possible lead — needs verification
"""
from typing import Dict
from venues.config_venues import (
    PRIORITY_SCORE_RULES, PRIORITY_HIGH_SCORE, PRIORITY_MED_SCORE,
    CAPACITY_IDEAL_MIN, CAPACITY_IDEAL_MAX, CAPACITY_MIN,
)


def score_venue(venue: Dict, signals: Dict) -> int:
    """Score a venue 0..N based on quality signals."""
    score = 0

    if signals.get("has_rooftop"):
        score += PRIORITY_SCORE_RULES["has_rooftop"]
    if signals.get("has_private_events"):
        score += PRIORITY_SCORE_RULES["has_private_events"]
    if signals.get("has_bar_service"):
        score += PRIORITY_SCORE_RULES["has_bar_service"]
    if signals.get("has_views"):
        score += PRIORITY_SCORE_RULES["has_views"]
    if signals.get("has_indoor_backup"):
        score += PRIORITY_SCORE_RULES["has_indoor_backup"]
    if signals.get("has_nightlife"):
        score += PRIORITY_SCORE_RULES["has_nightlife"]
    if signals.get("has_afrocultural"):
        score += PRIORITY_SCORE_RULES["has_afrocultural"]

    # Adjusting location-based scoring based on neighborhood
    # Assuming config imports PRIORITY_NEIGHBORHOODS
    # We will pass city in via signals.
    city = signals.get("city", "nyc")
    from venues.config_venues import PRIORITY_NEIGHBORHOODS
    hood = venue.get("neighborhood", "").lower()
    
    if hood in PRIORITY_NEIGHBORHOODS.get(city, []):
        score += PRIORITY_SCORE_RULES["primary_location"]
    else:
        score += PRIORITY_SCORE_RULES["secondary_location"]

    cap_str = venue.get("capacity", "")
    if cap_str:
        try:
            cap = int(str(cap_str).split("-")[0])
            if CAPACITY_IDEAL_MIN <= cap <= CAPACITY_IDEAL_MAX:
                score += PRIORITY_SCORE_RULES["capacity_in_range"]
            elif cap >= CAPACITY_MIN:
                score += 1  # partial credit
        except ValueError:
            pass

    if venue.get("website"):
        score += PRIORITY_SCORE_RULES["has_website"]
    if venue.get("contact"):
        score += PRIORITY_SCORE_RULES["has_contact"]

    return score


def classify_priority(venue: Dict, signals: Dict) -> str:
    """
    Return Priority A, B, or C.
    Priority A: Score >= PRIORITY_HIGH_SCORE (8)
    Priority B: Score >= PRIORITY_MED_SCORE  (5)
    Priority C: Below PRIORITY_MED_SCORE
    """
    s = score_venue(venue, signals)
    if s >= PRIORITY_HIGH_SCORE:
        return "Priority A"
    elif s >= PRIORITY_MED_SCORE:
        return "Priority B"
    else:
        return "Priority C"
