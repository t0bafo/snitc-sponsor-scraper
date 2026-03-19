"""
venues/exporter_retail.py — Exports OTMB retail venue results to a timestamped CSV.
Includes both empty-space and operating-store columns.
"""
import os
import logging
import pandas as pd
from typing import List, Dict
from datetime import datetime

from config_core import OUTPUT_DIR

logger = logging.getLogger(__name__)

RETAIL_CSV_COLUMNS = [
    "Name",
    "Website",
    "Neighborhood",
    "Store Type",
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
    "Private Events Available",
    "Manual Outreach Needed",
    "Instagram Handle",
    "Aesthetic Tags",
    "Is Chain Store",
    "Is Fast Fashion",
    "Contact Email",
    "Contact Phone",
    "Booking URL",
    "Score",
    "Priority",
    "Fit Reasons",
    "Source",
]


def export_retail_venues(venues: List[Dict], city: str) -> str:
    """
    Export enriched retail venues to a timestamped CSV file.

    Args:
        venues: Classified venue dicts (with score, priority, fit_reasons).
        city:   Target city string (e.g., "dallas", "nyc").

    Returns:
        Absolute path to the created CSV file.
    """
    rows = []
    for v in venues:
        fit_str = " | ".join(v.get("fit_reasons", []))
        rows.append({
            "Name":                    v.get("name", ""),
            "Website":                 v.get("url",  ""),
            "Neighborhood":            v.get("neighborhood", ""),
            "Store Type":              v.get("store_type", ""),
            "Sq Ft":                   v.get("sqft", ""),
            "Ceiling Height":          v.get("ceiling_height", ""),
            "Has Storefront":          v.get("has_storefront", False),
            "Has Natural Light":       v.get("has_natural_light", False),
            "Has White Walls":         v.get("has_white_walls", False),
            "Has High Ceilings":       v.get("has_high_ceilings", False),
            "Has Open Floor":          v.get("has_open_floor", False),
            "Has Retail Fixtures":     v.get("has_retail_fixtures", False),
            "Has Storefront Windows":  v.get("has_storefront_windows", False),
            "Is Transformable":        v.get("is_transformable", False),
            "Short Term Available":    v.get("short_term_available", False),
            "Private Events Available": v.get("private_events_available", False),
            "Manual Outreach Needed":  v.get("manual_outreach_needed", True),
            "Instagram Handle":        v.get("instagram_handle", ""),
            "Aesthetic Tags":          v.get("aesthetic_tags", ""),
            "Is Chain Store":          v.get("is_chain_store", False),
            "Is Fast Fashion":         v.get("is_fast_fashion", False),
            "Contact Email":           v.get("contact_email", ""),
            "Contact Phone":           v.get("contact_phone", ""),
            "Booking URL":             v.get("booking_url", ""),
            "Score":                   v.get("score", 0),
            "Priority":                v.get("priority", ""),
            "Fit Reasons":             fit_str,
            "Source":                  v.get("source", "seed"),
        })

    df = pd.DataFrame(rows, columns=RETAIL_CSV_COLUMNS)
    df = df.drop_duplicates(subset=["Website"], keep="first")

    # Sort Priority A → B → C
    order_map = {"Priority A": 0, "Priority B": 1, "Priority C": 2}
    df["_sort"] = df["Priority"].map(order_map).fillna(3)
    df = df.sort_values("_sort").drop(columns=["_sort"]).reset_index(drop=True)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    ts = datetime.now().strftime("%m%d_%H%M")
    filename = f"v_{city.lower()}_retail_{ts}.csv"
    output_path = os.path.join(OUTPUT_DIR, filename)

    df.to_csv(output_path, index=False)
    logger.info(f"  ✓ Exported {len(df)} venues → {output_path}")
    return output_path
