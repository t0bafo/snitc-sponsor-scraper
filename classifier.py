"""
classifier.py — Assigns sponsorship tiers to brands based on extracted data.
"""
from typing import Dict
from config import TIER_SCORE_RULES, TIER_1_SCORE, TIER_2_SCORE


def classify_tier(brand: Dict) -> str:
    """
    Score a brand and return its sponsorship tier.

    Tier 1: Strong fit — local, diverse, founder-led, contactable
    Tier 2: Good fit — NYC presence or diversity signals
    Tier 3: Possible fit — relevant category, less information
    """
    score = 0

    if brand.get("email"):
        score += TIER_SCORE_RULES["has_email"]
    if brand.get("instagram"):
        score += TIER_SCORE_RULES["has_instagram"]
    if brand.get("nyc_connection") and brand["nyc_connection"] not in {"No", "", None}:
        score += TIER_SCORE_RULES["nyc_based"]
    if brand.get("diversity"):
        score += TIER_SCORE_RULES["diversity_owned"]
    if brand.get("founder"):
        score += TIER_SCORE_RULES["founder_led"]
    if brand.get("website"):
        score += TIER_SCORE_RULES["has_website"]

    if score >= TIER_1_SCORE:
        return "Tier 1"
    elif score >= TIER_2_SCORE:
        return "Tier 2"
    else:
        return "Tier 3"
