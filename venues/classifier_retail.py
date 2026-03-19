"""
venues/classifier_retail.py — Scores and prioritizes retail venues based on YAML event profile.

Handles both empty/rentable spaces AND operating stores.
Key rule: Operating stores without explicit private event info are capped at Priority B.
"""
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


def _score_retail_venue(venue: Dict, config: dict) -> tuple:
    """
    Calculate a score for a single retail venue and build fit_reasons list.

    Returns:
        (score: int, fit_reasons: list[str])
    """
    w = config.get("scoring", {})
    sqft_req = config.get("space_requirements", {})
    sqft_min = sqft_req.get("sqft_min", 1000)
    sqft_max = sqft_req.get("sqft_max", 1500)
    sqft_acc_min = sqft_req.get("sqft_acceptable_min", sqft_min - 200)
    sqft_acc_max = sqft_req.get("sqft_acceptable_max", sqft_max + 500)
    neighborhoods = [n.lower() for n in config.get("neighborhoods", [])]

    score = 0
    reasons = []

    # ── Square footage ────────────────────────────────────────────────────
    sqft = venue.get("sqft")
    if sqft:
        if sqft_min <= sqft <= sqft_max:
            score += w.get("sqft_perfect_range", 25)
            reasons.append(f"Perfect size ({sqft:,} sq ft)")
        elif sqft_acc_min <= sqft <= sqft_acc_max:
            score += w.get("sqft_acceptable", 15)
            reasons.append(f"Acceptable size ({sqft:,} sq ft)")
        else:
            tag = "Small" if sqft < sqft_min else "Large"
            reasons.append(f"⚠ {tag} ({sqft:,} sq ft)")

    # ── Physical space signals ────────────────────────────────────────────
    if venue.get("has_storefront_windows"):
        score += w.get("storefront_windows", 20)
        reasons.append("Storefront windows (street visibility)")

    if venue.get("has_natural_light"):
        score += w.get("natural_light", 15)
        reasons.append("Natural light (daytime event)")

    if venue.get("has_high_ceilings"):
        score += w.get("high_ceilings", 15)
        ceiling = venue.get("ceiling_height")
        reasons.append(f"High ceilings{f' ({ceiling} ft)' if ceiling else ''}")

    if venue.get("has_open_floor"):
        score += w.get("open_floor_plan", 10)
        reasons.append("Open floor plan")

    if venue.get("has_retail_fixtures"):
        score += w.get("retail_fixtures", 10)
        reasons.append("Retail fixtures present")

    if venue.get("has_white_walls"):
        score += w.get("white_walls", 10)
        reasons.append("White / neutral walls")

    if venue.get("is_transformable"):
        score += w.get("transformable", 10)
        reasons.append("Adaptable / transformable layout")

    if venue.get("short_term_available"):
        score += w.get("short_term_available", 10)
        reasons.append("Short-term / pop-up rental available")

    # ── Operating store type bonuses ──────────────────────────────────────
    store_type = venue.get("store_type", "")

    if store_type == "furniture_showroom":
        score += w.get("furniture_showroom", 20)
        reasons.append("Furniture showroom — editorial backdrop")

    elif store_type == "concept_store":
        score += w.get("concept_store", 20)
        reasons.append("Concept / lifestyle store")

    elif store_type == "sneaker_boutique":
        score += w.get("sneaker_boutique", 15)
        reasons.append("Sneaker boutique — cultural resonance")

    elif store_type == "vintage_boutique":
        score += w.get("vintage_boutique", 15)
        reasons.append("Vintage boutique — distinct aesthetic")

    # ── Aesthetic tags ────────────────────────────────────────────────────
    aesthetic_tags = venue.get("aesthetic_tags", "")
    if "curated" in aesthetic_tags:
        score += w.get("curated_aesthetic", 10)
        reasons.append("Curated aesthetic")

    # ── Event rental availability (CRITICAL) ─────────────────────────────
    if venue.get("private_events_available"):
        score += w.get("private_events_available", 25)
        reasons.append("Explicit private event / rental availability ✓")

    # ── Neighborhood match ────────────────────────────────────────────────
    venue_hood = (venue.get("neighborhood") or "").lower()
    if venue_hood and any(n in venue_hood or venue_hood in n for n in neighborhoods):
        score += w.get("neighborhood_match", 15)
        reasons.append(f"{venue.get('neighborhood')} location")
    else:
        score += w.get("central_location", 10)

    # ── Contact bonus ─────────────────────────────────────────────────────
    if venue.get("contact_email"):
        score += 5
        reasons.append("Contact email found")

    # ── DEDUCTIONS ────────────────────────────────────────────────────────
    if venue.get("is_chain_store"):
        penalty = w.get("chain_store", -15)
        score += penalty  # penalty is negative
        reasons.append(f"⚠ Chain store (−{abs(penalty)} pts)")

    if venue.get("is_fast_fashion"):
        penalty = w.get("fast_fashion", -10)
        score += penalty
        reasons.append(f"⚠ Fast fashion brand (−{abs(penalty)} pts)")

    return score, reasons


def classify_retail_venues(venues: List[Dict], config: dict) -> List[Dict]:
    """
    Score and prioritize retail venues based on YAML event profile.

    Key rules:
    - Operating stores WITHOUT private event info are capped at Priority B.
    - Chain stores and fast-fashion brands are excluded (Priority D).

    Args:
        venues: List of enriched venue dicts.
        config: Full YAML event profile.

    Returns:
        Sorted, filtered venues with score, priority, fit_reasons.
    """
    tiers = config.get("priority_tiers", {"A": 80, "B": 60, "C": 40})
    tier_a = tiers.get("A", 80)
    tier_b = tiers.get("B", 60)
    tier_c = tiers.get("C", 40)

    results = []

    for venue in venues:
        score, reasons = _score_retail_venue(venue, config)

        # Assign raw priority
        if score >= tier_a:
            priority = "Priority A"
        elif score >= tier_b:
            priority = "Priority B"
        elif score >= tier_c:
            priority = "Priority C"
        else:
            priority = "Priority D"

        # ── Special rules for operating stores ──────────────────────────
        # Cap ops stores without rental confirmation at B (needs human outreach)
        if (priority == "Priority A"
                and venue.get("manual_outreach_needed")
                and venue.get("store_type") not in {"art_gallery", "pop-up_space",
                                                     "creative_space", "showroom"}):
            priority = "Priority B"
            reasons.append("⚠ Manual outreach needed (no rental info found)")

        venue["score"]       = score
        venue["priority"]    = priority
        venue["fit_reasons"] = reasons

        logger.info(
            f"    {venue.get('name', venue.get('url', '?'))[:45]} "
            f"→ {priority} ({score} pts)"
        )

        if priority != "Priority D":
            results.append(venue)

    # Sort A → B → C
    order = {"Priority A": 0, "Priority B": 1, "Priority C": 2}
    results.sort(key=lambda v: order.get(v["priority"], 3))

    return results
