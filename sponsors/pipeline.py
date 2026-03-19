"""
sponsors/pipeline.py — Sponsor scraping pipeline for SNITC.

Extracted from the original root main.py so both sponsors/ and venues/
pipelines live cleanly in their own modules.

The logic here is identical to the original main.py sponsor flow.
"""
import os
import json
import logging
import time
from typing import List, Dict
from urllib.parse import urlparse

from scraper import fetch_page, fetch_contact_page, polite_sleep
from sponsors.seeds_sponsors import SEED_BRANDS
from sponsors.extractor_sponsors import (
    extract_emails, extract_instagram, extract_founders,
    detect_diversity, detect_nyc_connection, detect_category,
    extract_brand_name, generate_notes,
)
from sponsors.classifier_sponsors import classify_tier
from sponsors.exporter_sponsors import export_to_csv
import sponsors.config_sponsors as cfg

logger = logging.getLogger(__name__)

EXTRA_URLS_FILE = os.path.join(cfg.OUTPUT_DIR, "extra_urls.json")


def _base_url(url: str) -> str:
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}"


def enrich_brand(brand: Dict) -> Dict:
    """Fetch a brand's website and enrich with live contact info."""
    url = brand.get("website", "")
    if not url:
        return brand

    page_data = fetch_page(url)
    html  = ""
    text  = ""

    if page_data:
        brand["website"] = page_data["url"]
        html = page_data["html"]
        text = page_data["text"]
    else:
        logger.debug(f"  Could not fetch {url}, using seed data only")

    contact_html = ""
    if page_data:
        base = _base_url(page_data["url"])
        contact_html = fetch_contact_page(base) or ""

    combined_text = text
    combined_html = html + " " + contact_html

    if page_data:
        emails = extract_emails(combined_text, combined_html)
        brand["emails"] = emails

        ig = extract_instagram(combined_html, combined_text)
        if ig:
            brand["instagram"] = ig

        founder = extract_founders(combined_text)
        if founder and not brand.get("founder"):
            brand["founder"] = founder

        diversity = detect_diversity(combined_text)
        if diversity and not brand.get("diversity"):
            brand["diversity"] = diversity

        nyc = detect_nyc_connection(combined_text)
        if nyc and nyc != "No" and not brand.get("nyc_connection"):
            brand["nyc_connection"] = nyc

        if not brand.get("category"):
            brand["category"] = detect_category(combined_text, "", url)
    else:
        brand["emails"] = []
        if not brand.get("instagram"):
            brand["instagram"] = None

    brand["tier"]  = classify_tier(brand)
    brand["notes"] = generate_notes(brand)
    return brand


def process_discovered_url(entry: Dict) -> Dict:
    """Process a URL discovered via browser search (minimal seed data)."""
    url = entry.get("url", "")
    brand: Dict = {
        "brand_name":    entry.get("title", extract_brand_name("", url)),
        "website":       url,
        "category":      "",
        "diversity":     None,
        "nyc_connection": None,
        "founder":       None,
        "instagram":     None,
        "emails":        [],
        "source_url":    url,
    }
    return enrich_brand(brand)


def load_extra_urls() -> List[Dict]:
    """Load browser-collected brand URLs from extra_urls.json if it exists."""
    if not os.path.exists(EXTRA_URLS_FILE):
        return []
    try:
        with open(EXTRA_URLS_FILE) as f:
            data = json.load(f)
        logger.info(f"  Loaded {len(data)} extra URLs from {EXTRA_URLS_FILE}")
        return data
    except Exception as e:
        logger.warning(f"  Could not read extra_urls.json: {e}")
        return []


def run_sponsor_pipeline(city: str = "nyc", test_mode: bool = False, seeds_only: bool = False) -> str:
    """Main sponsor pipeline. Returns path to output CSV."""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║         SNITC BRAND SPONSOR SCRAPER — Antigravity Agent       ║
║  Event : {cfg.EVENT_NAME:<53}║
║  Date  : {cfg.EVENT_DATE:<53}║
╚═══════════════════════════════════════════════════════════════╝
"""
    print(banner)

    if test_mode:
        logger.info("⚡ TEST MODE — processing 5 seeds only, skipping CSV export")

    logger.info("STEP 1/4 — Loading curated seed brands...")
    seeds = SEED_BRANDS[:5] if test_mode else SEED_BRANDS
    logger.info(f"  {len(seeds)} seed brands loaded")

    extra_urls = [] if (test_mode or seeds_only) else load_extra_urls()
    total = len(seeds) + len(extra_urls)
    logger.info(f"\nSTEP 2/4 — Enriching {total} brands (scraping live websites)...")
    logger.info(f"  Target local connection context: {city.upper()}\n")

    brands: List[Dict] = []
    failed = 0

    for i, seed in enumerate(seeds):
        name = seed.get("brand_name", "?")
        url  = seed.get("website", "")
        logger.info(f"  [{i+1}/{total}] {name} — {url[:60]}")
        try:
            enriched = enrich_brand(dict(seed))
            brands.append(enriched)
            emails    = enriched.get("emails", [])
            email_str = emails[0] if emails else "—"
            ig        = enriched.get("instagram") or "—"
            logger.info(
                f"     ✓ Tier: {enriched['tier']} | "
                f"NYC: {enriched.get('nyc_connection','?')} | "
                f"Email: {email_str} | IG: {ig}"
            )
        except Exception as e:
            logger.warning(f"     ⚠ Failed: {e}")
            failed += 1
        polite_sleep()

    for j, entry in enumerate(extra_urls):
        idx = len(seeds) + j + 1
        url = entry.get("url", "")
        logger.info(f"  [{idx}/{total}] (Discovered) {url[:70]}")
        try:
            brand = process_discovered_url(entry)
            brands.append(brand)
            logger.info(f"     ✓ {brand.get('brand_name','?')} | Tier: {brand['tier']}")
        except Exception as e:
            logger.warning(f"     ⚠ Failed: {e}")
            failed += 1
        polite_sleep()

    logger.info(f"\n✓ Enriched {len(brands)} brands ({failed} errors)")

    tier1   = [b for b in brands if b.get("tier") == "Tier 1"]
    tier2   = [b for b in brands if b.get("tier") == "Tier 2"]
    tier3   = [b for b in brands if b.get("tier") == "Tier 3"]
    ordered = tier1 + tier2 + tier3

    if test_mode:
        logger.info("TEST MODE: skipping CSV export.")
        return ""

    logger.info("\nSTEP 3/4 — Formatting data layout...")
    logger.info("STEP 4/4 — Exporting to CSV...")
    output_path = export_to_csv(ordered, city=city)

    logger.info(f"""
┌──────────────────────────────────────────────────────────────┐
│  🎉  DONE!  Your sponsor list is ready.                      │
│                                                              │
│  📄  {output_path:<52}│
│                                                              │
│  Open with:  open "{output_path}"         │
└──────────────────────────────────────────────────────────────┘
""")
    return output_path
