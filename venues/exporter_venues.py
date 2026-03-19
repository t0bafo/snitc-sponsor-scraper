"""
venues/exporter_venues.py — Builds and exports the venue CSV.
"""
import os
import logging
import pandas as pd
from typing import List, Dict
from datetime import datetime
import venues.config_venues as cfg

logger = logging.getLogger(__name__)


def export_venues_to_csv(venues: List[Dict], city: str = "nyc") -> str:
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
            "City":         v.get("city", ""),
            "Capacity":     v.get("capacity", ""),
            "Venue Type":   v.get("venue_type", ""),
            "Description":  v.get("description", ""),
            "Website":      v.get("website", ""),
            "Contact":      contact_str,
            "Priority":     v.get("priority", "Priority C"),
            "Notes":        v.get("notes", ""),
            "Source URL":   v.get("source_url", ""),
        })

    df = pd.DataFrame(rows, columns=cfg.CSV_COLUMNS)

    # Deduplicate
    df = df.drop_duplicates(subset=["Venue Name"], keep="first")
    df = df.drop_duplicates(subset=["Website"],    keep="first")

    # Sort by City, then Priority (A > B > C)
    priority_order  = {"Priority A": 0, "Priority B": 1, "Priority C": 2}

    df["_priority_sort"]  = df["Priority"].map(priority_order).fillna(2)
    df = df.sort_values(["City", "_priority_sort"]).drop(
        columns=["_priority_sort"]
    )
    df = df.reset_index(drop=True)

    # Export to CSV with short timestamped filename
    os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)
    # Format: v_dallas_0304_1521.csv (v for venues, month-day_hour-minute)
    ts = datetime.now().strftime("%m%d_%H%M")
    filename = f"v_{city.lower()}_{ts}.csv"
    output_path = os.path.join(cfg.OUTPUT_DIR, filename)
    
    df.to_csv(output_path, index=False)

    # Summary
    pa = len(df[df["Priority"] == "Priority A"])
    pb = len(df[df["Priority"] == "Priority B"])
    pc = len(df[df["Priority"] == "Priority C"])

    logger.info("\n" + "=" * 60)
    logger.info(f"✅ EXPORT COMPLETE: {output_path}")
    logger.info(f"   Total venues : {len(df)}")
    logger.info(f"   Priority A   : {pa}")
    logger.info(f"   Priority B   : {pb}")
    logger.info(f"   Priority C   : {pc}")
    logger.info("=" * 60)

    return output_path
