"""
main.py — Unified entry point for the SNITC Multipurpose Scraper.

MODES
─────
  venues   → Find rooftop event venues for SNITC (Saturday Night in the City)
  sponsors → Find brand sponsors for SNITC

USAGE
─────
  python main.py --mode venues --city nyc   # Default city
  python main.py --mode venues --city dallas --test
  python main.py --mode venues --city nyc --config events/stargazing_nyc.yaml

  python main.py --mode sponsors --city dallas # Sponsor mode with city filter

  python main.py                            # Defaults to BOTH modes, NYC city

PIPELINE (per mode)
───────────────────
  1. Load curated seed data (seeds_venues.py / seeds.py)
  2. Scrape each website live
  3. Extract/enrich key fields
  4. Classify priority/tier
  5. Export sorted CSV
"""
import sys
import time
import logging

# ──────────────────────────────────────────────
# LOGGING SETUP
# ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-7s %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def _parse_args():
    """Parse CLI arguments."""
    args = sys.argv[1:]
    mode       = None
    city       = "nyc"
    config_path = None
    test_mode  = "--test"  in args
    seeds_only = "--seeds" in args or "--seeds_only" in args

    for a in args:
        if a.startswith("--mode="):
            mode = a.split("=", 1)[1].lower()
        elif a == "--mode" and args.index(a) + 1 < len(args):
            mode = args[args.index(a) + 1].lower()

        elif a.startswith("--city="):
            city = a.split("=", 1)[1].lower()
        elif a == "--city" and args.index(a) + 1 < len(args):
            city = args[args.index(a) + 1].lower()

        elif a.startswith("--config="):
            config_path = a.split("=", 1)[1]
        elif a == "--config" and args.index(a) + 1 < len(args):
            config_path = args[args.index(a) + 1]

    # Also accept positional: python main.py venues dallas
    if mode is None:
        for a in args:
            if a in ("venues", "sponsors", "both"):
                mode = a
                break

    if mode is None:
        mode = "both"

    return mode, city, test_mode, seeds_only, config_path


def main():
    mode, city, test_mode, seeds_only, config_path = _parse_args()

    valid_modes = ("venues", "sponsors", "both")
    if mode not in valid_modes:
        print(f"❌  Unknown mode '{mode}'. Use: {', '.join(valid_modes)}")
        sys.exit(1)
        
    valid_cities = ("nyc", "dallas", "atlanta")
    if city not in valid_cities:
        print(f"❌  Unknown city '{city}'. Use: {', '.join(valid_cities)}")
        sys.exit(1)

    start = time.time()

    if mode in ("venues", "both"):
        from venues.pipeline import run_venue_pipeline
        from venues.config_venues import initialize_config
        initialize_config(config_path, city=city)

        # Also load raw YAML so pipeline can detect venue_type (retail vs nightlife)
        raw_config = {}
        if config_path:
            import yaml, os
            if os.path.exists(config_path):
                with open(config_path) as f:
                    raw_config = yaml.safe_load(f) or {}

        run_venue_pipeline(city=city, test_mode=test_mode, seeds_only=seeds_only,
                           raw_config=raw_config)

    if mode in ("sponsors", "both"):
        from sponsors.pipeline import run_sponsor_pipeline
        from sponsors.config_sponsors import initialize_config as init_sponsors
        init_sponsors(config_path, city=city)
        run_sponsor_pipeline(city=city, test_mode=test_mode, seeds_only=seeds_only)

    elapsed = time.time() - start
    logger.info(f"\n⏱  Total runtime: {elapsed:.1f}s")


if __name__ == "__main__":
    main()
