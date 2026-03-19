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
from venues.extractor_nightlife import (
    extract_contact, extract_phone, extract_capacity,
    detect_venue_type, detect_neighborhood,
    extract_description, detect_signals, generate_venue_notes,
)
from venues.classifier_venues import classify_priority
from venues.exporter_venues import export_venues_to_csv
from venues.searcher_nightlife import discover_venues
import venues.config_venues as cfg

logger = logging.getLogger(__name__)


def _base_url(url: str) -> str:
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}"


def enrich_venue(venue: Dict, city: str = "nyc") -> Dict:
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
        
        # If venue name is missing (because it was dynamically discovered), grab the <title>
        if not venue.get("venue_name"):
            from bs4 import BeautifulSoup
            import re
            try:
                soup = BeautifulSoup(html[:10000], "lxml")
                title = soup.title.string.strip() if soup.title else "Unknown Venue"
                # Strip off common tags like " | Home" or " - Dallas"
                clean_title = re.sub(r'\s*[|\-–—:]\s*.+$', '', title).strip()
                venue["venue_name"] = clean_title if clean_title else title
            except Exception:
                venue["venue_name"] = "Unknown Venue"
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

        # Neighborhood / city — only fill if missing
        if not venue.get("neighborhood") or not venue.get("city"):
            hood, boro = detect_neighborhood(combined_text, venue.get("location", ""))
            if hood and not venue.get("neighborhood"):
                venue["neighborhood"] = hood
            if not venue.get("city"):
                venue["city"] = city.capitalize()

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
    signals["city"] = city

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


def run_venue_pipeline(city: str = "nyc", test_mode: bool = False, seeds_only: bool = False,
                       raw_config: dict = None) -> str:
    """
    Main venue pipeline. Routes to retail or nightlife sub-pipeline based on venue_type in config.
    Returns path to output CSV.
    """
    venue_type = (raw_config or {}).get("venue_type", "nightlife")

    if venue_type == "retail":
        return _run_retail_pipeline(city, test_mode, seeds_only, raw_config or {})
    else:
        return _run_nightlife_pipeline(city, test_mode, seeds_only)


def _run_retail_pipeline(city: str, test_mode: bool, seeds_only: bool, config: dict) -> str:
    """Retail pipeline for OTMB-type events."""
    from venues.seeds.retail import get_retail_seeds
    from venues.searcher_retail import search_retail_venues
    from venues.extractor_retail import extract_retail_signals
    from venues.classifier_retail import classify_retail_venues
    from venues.exporter_retail import export_retail_venues

    event_name = config.get("event_name", "OTMB")
    cap = config.get("capacity", {})
    cap_str = f"{cap.get('min', '?')}-{cap.get('max', '?')}"
    sqft = config.get("space_requirements", {})
    sqft_str = f"{sqft.get('sqft_min', '?')}-{sqft.get('sqft_max', '?')} sq ft"

    banner = f"""
╔═══════════════════════════════════════════════════════════════════════╗
║        OTMB RETAIL VENUE SCRAPER — Antigravity Agent                  ║
║  Event : {event_name:<55}║
║  City  : {city.upper():<55}║
║  Need  : Retail/Gallery · {cap_str} cap · {sqft_str:<26}║
╚═══════════════════════════════════════════════════════════════════════╝
"""
    print(banner)

    if test_mode:
        logger.info("⚡ TEST MODE — processing 5 seeds only, skipping CSV export")

    # Step 1: Load seeds
    logger.info("STEP 1/4 — Loading curated retail seed venues...")
    all_seeds = get_retail_seeds(city)
    seeds = all_seeds[:5] if test_mode else all_seeds
    logger.info(f"  {len(seeds)} seed venues loaded")

    venues: List[Dict] = list(seeds)

    # Step 2: Web discovery
    if not seeds_only:
        logger.info("\nSTEP 2/4 — Searching for retail venues...")
        discovered = search_retail_venues(city=city, config=config)
        venues.extend(discovered)
        logger.info(f"  Found {len(discovered)} additional candidates")
    else:
        logger.info("STEP 2/4 — Seeds-only mode, skipping web search.")

    # Step 3: Extraction
    logger.info(f"\nSTEP 3/4 — Extracting signals from {len(venues)} venues...")
    venues = extract_retail_signals(venues)

    # Step 4: Classify
    logger.info("\nSTEP 4/4 — Classifying venues...")
    venues = classify_retail_venues(venues, config)

    a_count = sum(1 for v in venues if v.get("priority") == "Priority A")
    b_count = sum(1 for v in venues if v.get("priority") == "Priority B")
    c_count = sum(1 for v in venues if v.get("priority") == "Priority C")

    if test_mode:
        logger.info("TEST MODE: skipping CSV export.")
        return ""

    output_path = export_retail_venues(venues, city=city)

    logger.info(f"""
╔══════════════════════════════════════════════════════════════════╗
║  ✅  EXPORT COMPLETE: {output_path:<42}║
║     Total venues : {len(venues):<46}║
║     Priority A   : {a_count:<46}║
║     Priority B   : {b_count:<46}║
║     Priority C   : {c_count:<46}║
╚══════════════════════════════════════════════════════════════════╝
""")
    return output_path


def _run_nightlife_pipeline(city: str, test_mode: bool, seeds_only: bool) -> str:
    """Original nightlife pipeline for SNITC/Stargazing events."""
    banner = f"""
╔═══════════════════════════════════════════════════════════════════════╗
║           SNITC ROOFTOP VENUE SCRAPER — Antigravity Agent             ║
║  Event : {cfg.EVENT_NAME:<55}║
║  Date  : {cfg.EVENT_DATE:<55}║
║  Need  : Rooftop/Outdoor · {cfg.EVENT_CAPACITY} cap · Brooklyn or Manhattan         ║
╚═══════════════════════════════════════════════════════════════════════╝
"""
    print(banner)

    if test_mode:
        logger.info("⚡ TEST MODE — processing 5 seeds only, skipping CSV export")

    # ── Step 1: Load seeds ──────────────────────────────────
    logger.info("STEP 1/4 — Loading curated seed venues...")
    city_seeds = SEED_VENUES.get(city.lower(), [])
    seeds = city_seeds[:5] if test_mode else city_seeds
    logger.info(f"  {len(seeds)} seed venues loaded")

    if not seeds_only:
        logger.info("\n── LIVE DISCOVERY (Phase 3) ──")
        logger.info("  Searching the web for new venues...")
        discovered = discover_venues(city=city, num_results=2 if test_mode else 15)
        logger.info(f"  Found {len(discovered)} new unverified venue URLs")
        seeds.extend(discovered)

    total = len(seeds)
    logger.info(f"\nSTEP 2/4 — Enriching {total} venues (scraping live websites)...")
    logger.info(f"  Target city: {city}")

    venues: List[Dict] = []
    failed = 0

    for i, seed in enumerate(seeds):
        name = seed.get("venue_name", "")
        url  = seed.get("website", "")
        display_name = name if name else "(Discovered Venue)"
        logger.info(f"  [{i+1}/{total}] {display_name} — {url[:65]}")
        try:
            enriched = enrich_venue(dict(seed), city=city)
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

    priority_ord = {"Priority A": 0, "Priority B": 1, "Priority C": 2}
    ordered = sorted(venues, key=lambda v: priority_ord.get(v.get("priority", ""), 2))

    if test_mode:
        logger.info("TEST MODE: skipping CSV export.")
        return ""

    logger.info("\nSTEP 3/4 — Formatting data layout...")
    logger.info("STEP 4/4 — Exporting to CSV...")
    output_path = export_venues_to_csv(ordered, city=city)

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
