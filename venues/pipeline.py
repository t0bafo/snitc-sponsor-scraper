"""
venues/pipeline.py — Venue scraping pipeline for SNITC.

Runs the full venue discovery loop:
  1. Load seed venues
  2. Fetch each venue's website live
  3. Enrich with capacity, signals, description, contact
  4. Classify Priority A / B / C
  5. Export to output/snitc_venues.csv
"""
import logging
import time
from typing import List, Dict
from urllib.parse import urlparse

from scraper import fetch_page, fetch_contact_page, polite_sleep
from venues.seeds_venues import SEED_VENUES
from venues.extractor_venues import (
    extract_contact, extract_phone, extract_capacity,
    detect_venue_type, detect_neighborhood,
    extract_description, detect_signals, generate_venue_notes,
)
from venues.classifier_venues import classify_priority
from venues.exporter_venues import export_venues_to_csv, print_venue_preview
from venues.config_venues import EVENT_NAME, EVENT_DATE, EVENT_CAPACITY

logger = logging.getLogger(__name__)


def _base_url(url: str) -> str:
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}"


def enrich_venue(venue: Dict) -> Dict:
    """
    Given a venue dict (from seeds or discovered), fetch its website live
    and enrich with live contact, capacity, description, type, signals.
    Seed-provided fields are kept when scraping finds nothing better.
    """
    url = venue.get("website", "")
    if not url:
        # If no website, score from seed data only
        signals = detect_signals(
            venue.get("description", "") + " " + venue.get("notes", "")
        )
        venue["priority"] = classify_priority(venue, signals)
        venue["notes"]    = generate_venue_notes(venue, signals, venue.get("notes", ""))
        return venue

    # ── Fetch homepage ────────────────────────────
    page_data = fetch_page(url)
    html = ""
    text = ""

    if page_data:
        venue["website"] = page_data["url"]   # follow redirects
        html = page_data["html"]
        text = page_data["text"]
    else:
        logger.debug(f"  Could not fetch {url}, using seed data only")

    # ── Also try for more content (events/contact pages) ──
    extra_html = ""
    if page_data:
        base = _base_url(page_data["url"])
        for path in ["/events", "/private-events", "/contact", "/venue"]:
            try:
                from scraper import fetch_page as _fp
                extra = _fp(base.rstrip("/") + path)
                if extra:
                    extra_html += extra["html"]
                    break
            except Exception:
                pass

    combined_text = text + " " + _html_to_text(extra_html)
    combined_html = html + " " + extra_html

    if page_data:
        # Capacity — only overwrite if seed didn't provide one
        cap = extract_capacity(combined_text)
        if cap and not venue.get("capacity"):
            venue["capacity"] = cap

        # Contact — only overwrite if seed didn't have one
        contact = extract_contact(combined_text, combined_html)
        if contact and not venue.get("contact"):
            venue["contact"] = contact

        phone = extract_phone(combined_text)
        if phone and not venue.get("phone"):
            venue["phone"] = phone

        # Venue type — only overwrite if seed didn't specify
        if not venue.get("venue_type"):
            venue["venue_type"] = detect_venue_type(combined_text, url=url)

        # Neighborhood / borough — only fill if missing
        if not venue.get("neighborhood") or not venue.get("borough"):
            hood, boro = detect_neighborhood(combined_text, venue.get("location", ""))
            if hood and not venue.get("neighborhood"):
                venue["neighborhood"] = hood
            if boro and not venue.get("borough"):
                venue["borough"] = boro

        # Description — prefer live meta over seed if longer
        live_desc = extract_description(html)
        seed_desc = venue.get("description", "")
        if live_desc and len(live_desc) > len(seed_desc):
            venue["description"] = live_desc

    # ── Signal detection + classify ───────────────────────
    seed_notes = venue.get("notes", "")
    # Combine seed content + live content for signal detection
    signal_text = (
        combined_text + " " + combined_html + " " +
        venue.get("description", "") + " " + seed_notes
    )
    signals = detect_signals(signal_text)

    # Supplement signals with seed notes keywords
    seed_lower = seed_notes.lower()
    if any(kw in seed_lower for kw in ["afrobeats", "afro house", "amapiano", "caribbean", "diaspora"]):
        signals["has_afrocultural"] = True
    if any(kw in seed_lower for kw in ["dj", "nightlife", "dance", "music"]):
        signals["has_nightlife"] = True
    if "indoor backup" in seed_lower or "indoor option" in seed_lower:
        signals["has_indoor_backup"] = True

    venue["priority"] = classify_priority(venue, signals)
    venue["notes"]    = generate_venue_notes(venue, signals, seed_notes)

    return venue


def _html_to_text(html: str) -> str:
    """Quick strip of HTML to text, gracefully."""
    if not html:
        return ""
    from bs4 import BeautifulSoup
    try:
        soup = BeautifulSoup(html[:30000], "lxml")
        for tag in soup(["script", "style", "nav", "footer", "head"]):
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)[:8000]
    except Exception:
        return html[:2000]


def run_venue_pipeline(test_mode: bool = False, seeds_only: bool = False) -> str:
    """
    Main venue pipeline. Returns path to output CSV.
    """
    banner = f"""
╔═══════════════════════════════════════════════════════════════════════╗
║           SNITC ROOFTOP VENUE SCRAPER — Antigravity Agent             ║
║  Event : {EVENT_NAME:<55}║
║  Date  : {EVENT_DATE:<55}║
║  Need  : Rooftop/Outdoor · {EVENT_CAPACITY} cap · Brooklyn or Manhattan         ║
╚═══════════════════════════════════════════════════════════════════════╝
"""
    print(banner)

    if test_mode:
        logger.info("⚡ TEST MODE — processing 5 seeds only, skipping CSV export")

    # ── Step 1: Load seeds ──────────────────────────────────
    logger.info("STEP 1/4 — Loading curated seed venues...")
    seeds = SEED_VENUES[:5] if test_mode else SEED_VENUES
    logger.info(f"  {len(seeds)} seed venues loaded")

    total = len(seeds)
    logger.info(f"\nSTEP 2/4 — Enriching {total} venues (scraping live websites)...")
    logger.info(f"  Output will be saved to: output/snitc_venues.csv\n")

    venues: List[Dict] = []
    failed = 0

    for i, seed in enumerate(seeds):
        name = seed.get("venue_name", "?")
        url  = seed.get("website", "")
        logger.info(f"  [{i+1}/{total}] {name} — {url[:65]}")
        try:
            enriched = enrich_venue(dict(seed))
            venues.append(enriched)
            cap      = enriched.get("capacity", "?")
            priority = enriched.get("priority", "?")
            contact  = enriched.get("contact", "—")
            logger.info(
                f"     ✓ Priority: {priority} | "
                f"Cap: {cap} | "
                f"Contact: {contact[:40]}"
            )
        except Exception as e:
            logger.warning(f"     ⚠ Failed: {e}")
            failed += 1
        polite_sleep()

    logger.info(f"\n✓ Enriched {len(venues)} venues ({failed} errors)")

    # ── Step 3: Preview ──────────────────────────────────────
    logger.info("\nSTEP 3/4 — Results preview:")
    pa  = [v for v in venues if v.get("priority") == "Priority A"]
    pb  = [v for v in venues if v.get("priority") == "Priority B"]
    pc  = [v for v in venues if v.get("priority") == "Priority C"]
    bk  = [v for v in venues if v.get("borough") == "Brooklyn"]
    mn  = [v for v in venues if v.get("borough") == "Manhattan"]

    # Sort: Brooklyn A→B→C, then Manhattan A→B→C
    priority_ord = {"Priority A": 0, "Priority B": 1, "Priority C": 2}
    bk_sorted = sorted(bk, key=lambda v: priority_ord.get(v.get("priority", ""), 2))
    mn_sorted = sorted(mn, key=lambda v: priority_ord.get(v.get("priority", ""), 2))
    ordered = bk_sorted + mn_sorted

    print_venue_preview(ordered, n=20)

    if test_mode:
        logger.info("TEST MODE: skipping CSV export.")
        return ""

    # ── Step 4: Export ───────────────────────────────────────
    logger.info("STEP 4/4 — Exporting CSV...")
    output_path = export_venues_to_csv(ordered)

    logger.info(f"""
┌──────────────────────────────────────────────────────────────────┐
│  🎉  DONE!  Your venue list is ready.                            │
│                                                                  │
│  📄  {output_path:<56}│
│                                                                  │
│  Open with:  open "{output_path}"             │
└──────────────────────────────────────────────────────────────────┘
""")
    return output_path
