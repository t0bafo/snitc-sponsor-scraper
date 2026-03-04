"""
exporter.py — Builds the final DataFrame and exports to CSV.
"""
import os
import logging
import pandas as pd
from typing import List, Dict
from config import OUTPUT_DIR, OUTPUT_FILE, CSV_COLUMNS

logger = logging.getLogger(__name__)


def export_to_csv(brands: List[Dict]) -> str:
    """
    Deduplicate, sort by tier, and export to CSV.
    Returns the path to the output file.
    """
    if not brands:
        logger.error("No brands to export!")
        return ""

    # Normalize rows
    rows = []
    for b in brands:
        emails = b.get("emails", [])
        email_str = emails[0] if emails else ""

        rows.append({
            "Brand Name": b.get("brand_name", "Unknown"),
            "Category": b.get("category", ""),
            "Website": b.get("website", ""),
            "Instagram": b.get("instagram", ""),
            "Email": email_str,
            "Founder(s)": b.get("founder", ""),
            "Diversity": b.get("diversity", ""),
            "NYC Connection": b.get("nyc_connection", ""),
            "Tier": b.get("tier", "Tier 3"),
            "Notes": b.get("notes", ""),
            "Source URL": b.get("source_url", ""),
        })

    df = pd.DataFrame(rows, columns=CSV_COLUMNS)

    # Deduplicate by Brand Name (keep first occurrence)
    df = df.drop_duplicates(subset=["Brand Name"], keep="first")
    df = df.drop_duplicates(subset=["Website"], keep="first")

    # Sort by tier
    tier_order = {"Tier 1": 0, "Tier 2": 1, "Tier 3": 2}
    df["_tier_sort"] = df["Tier"].map(tier_order).fillna(3)
    df = df.sort_values("_tier_sort").drop(columns=["_tier_sort"])
    df = df.reset_index(drop=True)

    # Export
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    df.to_csv(output_path, index=False)

    # Print summary to terminal
    t1 = len(df[df["Tier"] == "Tier 1"])
    t2 = len(df[df["Tier"] == "Tier 2"])
    t3 = len(df[df["Tier"] == "Tier 3"])
    logger.info("\n" + "="*60)
    logger.info(f"✅ EXPORT COMPLETE: {output_path}")
    logger.info(f"   Total brands: {len(df)}")
    logger.info(f"   Tier 1 (best fit): {t1}")
    logger.info(f"   Tier 2 (good fit): {t2}")
    logger.info(f"   Tier 3 (possible): {t3}")
    logger.info("="*60)

    return output_path


def print_preview(brands: List[Dict], n: int = 10):
    """Print a quick preview table to terminal."""
    print(f"\n{'='*80}")
    print(f"{'BRAND':<30} {'TIER':<8} {'CATEGORY':<18} {'NYC':<15} {'EMAIL'}")
    print(f"{'-'*80}")
    for b in brands[:n]:
        emails = b.get("emails", [])
        email = emails[0] if emails else "—"
        print(
            f"{b.get('brand_name','?')[:29]:<30} "
            f"{b.get('tier','?'):<8} "
            f"{b.get('category','?')[:17]:<18} "
            f"{str(b.get('nyc_connection','?'))[:14]:<15} "
            f"{email[:30]}"
        )
    print(f"{'='*80}\n")
