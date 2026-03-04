"""
venues/exporter_venues.py — Builds and exports the venue CSV.
"""
import os
import logging
import pandas as pd
from typing import List, Dict
from venues.config_venues import OUTPUT_DIR, OUTPUT_FILE, CSV_COLUMNS

logger = logging.getLogger(__name__)


def export_venues_to_csv(venues: List[Dict]) -> str:
    """
    Deduplicate, sort (Brooklyn first by Priority, then Manhattan by Priority),
    and export to CSV.  Returns the output file path.
    """
    if not venues:
        logger.error("No venues to export!")
        return ""

    rows = []
    for v in venues:
        contact = v.get("contact", "")
        # Combine email + phone if both available
        phone = v.get("phone", "")
        if contact and phone:
            contact_str = f"{contact} | {phone}"
        else:
            contact_str = contact or phone

        rows.append({
            "Venue Name":   v.get("venue_name", "Unknown"),
            "Location":     v.get("location", ""),
            "Neighborhood": v.get("neighborhood", ""),
            "Borough":      v.get("borough", ""),
            "Capacity":     v.get("capacity", ""),
            "Venue Type":   v.get("venue_type", ""),
            "Description":  v.get("description", ""),
            "Website":      v.get("website", ""),
            "Contact":      contact_str,
            "Priority":     v.get("priority", "Priority C"),
            "Notes":        v.get("notes", ""),
            "Source URL":   v.get("source_url", ""),
        })

    df = pd.DataFrame(rows, columns=CSV_COLUMNS)

    # Deduplicate
    df = df.drop_duplicates(subset=["Venue Name"], keep="first")
    df = df.drop_duplicates(subset=["Website"],    keep="first")

    # Sort: Borough (Brooklyn first), then Priority (A > B > C)
    borough_order   = {"Brooklyn": 0, "Manhattan": 1, "": 2}
    priority_order  = {"Priority A": 0, "Priority B": 1, "Priority C": 2}

    df["_borough_sort"]   = df["Borough"].map(borough_order).fillna(2)
    df["_priority_sort"]  = df["Priority"].map(priority_order).fillna(2)
    df = df.sort_values(["_borough_sort", "_priority_sort"]).drop(
        columns=["_borough_sort", "_priority_sort"]
    )
    df = df.reset_index(drop=True)

    # Export
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    df.to_csv(output_path, index=False)

    # Summary
    pa = len(df[df["Priority"] == "Priority A"])
    pb = len(df[df["Priority"] == "Priority B"])
    pc = len(df[df["Priority"] == "Priority C"])
    bk = len(df[df["Borough"] == "Brooklyn"])
    mn = len(df[df["Borough"] == "Manhattan"])

    logger.info("\n" + "=" * 60)
    logger.info(f"✅ EXPORT COMPLETE: {output_path}")
    logger.info(f"   Total venues : {len(df)}")
    logger.info(f"   Brooklyn     : {bk}")
    logger.info(f"   Manhattan    : {mn}")
    logger.info(f"   Priority A   : {pa}")
    logger.info(f"   Priority B   : {pb}")
    logger.info(f"   Priority C   : {pc}")
    logger.info("=" * 60)

    return output_path


def print_venue_preview(venues: List[Dict], n: int = 20):
    """Print a quick terminal preview table."""
    print(f"\n{'=' * 90}")
    print(
        f"{'VENUE':<30} {'BOROUGH':<10} {'NEIGHBORHOOD':<18} "
        f"{'CAP':<6} {'PRIORITY':<12} {'CONTACT'}"
    )
    print(f"{'-' * 90}")
    for v in venues[:n]:
        cap     = str(v.get("capacity", "?"))[:5]
        contact = str(v.get("contact", "—"))[:30]
        print(
            f"{str(v.get('venue_name', '?'))[:29]:<30} "
            f"{str(v.get('borough', '?'))[:9]:<10} "
            f"{str(v.get('neighborhood', '?'))[:17]:<18} "
            f"{cap:<6} "
            f"{str(v.get('priority', '?')):<12} "
            f"{contact}"
        )
    print(f"{'=' * 90}\n")
