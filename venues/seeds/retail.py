"""
venues/seeds/retail.py — Curated seed list of retail/gallery/showroom spaces for OTMB.
Includes both empty/rentable spaces AND operating stores with event potential.
"""

DALLAS_RETAIL_SEEDS = [
    # ── Art Galleries & Flex Spaces ────────────────────────────────────────
    {
        "name": "The Guild Dallas",
        "url": "https://www.theguilddallas.com",
        "neighborhood": "Deep Ellum",
        "venue_type": "art_gallery",
        "notes": "Contemporary art gallery with flexible open space",
    },
    {
        "name": "Kettle Art",
        "url": "https://www.kettleart.com",
        "neighborhood": "Deep Ellum",
        "venue_type": "art_gallery",
        "notes": "Artist-run gallery, open floor, industrial aesthetic",
    },
    {
        "name": "Ro2 Art",
        "url": "https://www.ro2art.com",
        "neighborhood": "Design District",
        "venue_type": "art_gallery",
        "notes": "Contemporary gallery in the Design District",
    },
    {
        "name": "Kirk Hopper Fine Art",
        "url": "https://www.kirkhopper.com",
        "neighborhood": "Design District",
        "venue_type": "art_gallery",
    },
    {
        "name": "Cris Worley Fine Arts",
        "url": "https://www.crisworley.com",
        "neighborhood": "Design District",
        "venue_type": "art_gallery",
    },
    {
        "name": "Liliana Bloch Gallery",
        "url": "https://www.lilianablochgallery.com",
        "neighborhood": "Design District",
        "venue_type": "art_gallery",
    },
    {
        "name": "Trinity Groves",
        "url": "https://www.trinitygroves.com",
        "neighborhood": "Trinity Groves",
        "venue_type": "creative_space",
        "notes": "Developer-backed creative/commercial incubator cluster",
    },

    # ── Furniture Showrooms ────────────────────────────────────────────────
    {
        "name": "CB2 Dallas",
        "url": "https://www.cb2.com/stores/tx/dallas",
        "neighborhood": "Knox-Henderson",
        "venue_type": "furniture_showroom",
        "notes": "Modern furniture, editorial aesthetic — inquire for private events",
    },
    {
        "name": "West Elm Dallas",
        "url": "https://www.westelm.com/stores/tx/dallas",
        "neighborhood": "Knox-Henderson",
        "venue_type": "furniture_showroom",
        "notes": "Mid-century modern furnishings, event hosting history",
    },
    {
        "name": "Room & Board Dallas",
        "url": "https://www.roomandboard.com/stores/dallas",
        "neighborhood": "Design District",
        "venue_type": "furniture_showroom",
    },
    {
        "name": "Design Within Reach Dallas",
        "url": "https://www.dwr.com/stores/dallas",
        "neighborhood": "Design District",
        "venue_type": "furniture_showroom",
        "notes": "High-design furniture, Design District flagship",
    },

    # ── Sneaker Boutiques ──────────────────────────────────────────────────
    {
        "name": "Sneaker Politics Dallas",
        "url": "https://www.sneakerpolitics.com",
        "neighborhood": "Deep Ellum",
        "venue_type": "sneaker_boutique",
        "notes": "Premium sneaker boutique with cultural credibility",
    },

    # ── Vintage / Concept ─────────────────────────────────────────────────
    {
        "name": "Dolly Python",
        "url": "https://www.dollypython.com",
        "neighborhood": "Bishop Arts",
        "venue_type": "vintage_boutique",
        "notes": "Curated vintage clothing and gifts",
    },
    {
        "name": "Lula B's Antiques",
        "url": "https://www.lulabantiques.com",
        "neighborhood": "Deep Ellum",
        "venue_type": "vintage_boutique",
        "notes": "Eclectic vintage and antique shop",
    },
]

NYC_RETAIL_SEEDS = [
    # ── Art Galleries & Flex Spaces ────────────────────────────────────────
    {
        "name": "Spring Studios",
        "url": "https://www.springstudios.com",
        "neighborhood": "Tribeca",
        "venue_type": "creative_space",
        "notes": "High-end creative event space, 70,000 sq ft campus",
    },
    {
        "name": "Fotografiska New York",
        "url": "https://www.fotografiska.com/nyc",
        "neighborhood": "Flatiron",
        "venue_type": "art_gallery",
        "notes": "Photography museum with event/pop-up rental spaces",
    },
    {
        "name": "Superchief Gallery",
        "url": "https://superchiefgallery.com",
        "neighborhood": "Williamsburg",
        "venue_type": "art_gallery",
        "notes": "Contemporary pop art gallery, available for events",
    },

    # ── Furniture Showrooms ────────────────────────────────────────────────
    {
        "name": "CB2 SoHo",
        "url": "https://www.cb2.com/stores/ny/soho",
        "neighborhood": "SoHo",
        "venue_type": "furniture_showroom",
        "notes": "Modern furniture flagship — known to host private events",
    },
    {
        "name": "West Elm SoHo",
        "url": "https://www.westelm.com/stores/ny/soho",
        "neighborhood": "SoHo",
        "venue_type": "furniture_showroom",
    },
    {
        "name": "Room & Board NYC",
        "url": "https://www.roomandboard.com/stores/new-york",
        "neighborhood": "Flatiron",
        "venue_type": "furniture_showroom",
    },

    # ── Concept Stores ─────────────────────────────────────────────────────
    {
        "name": "Dover Street Market NYC",
        "url": "https://newyork.doverstreetmarket.com",
        "neighborhood": "Lower East Side",
        "venue_type": "concept_store",
        "notes": "Multi-brand concept store, editorial, Comme des Garçons flagship",
    },
    {
        "name": "Kith SoHo",
        "url": "https://kith.com",
        "neighborhood": "SoHo",
        "venue_type": "concept_store",
        "notes": "Premium lifestyle/sneaker concept store with event history",
    },

    # ── Sneaker Boutiques ──────────────────────────────────────────────────
    {
        "name": "Extra Butter NYC",
        "url": "https://extrabutterny.com",
        "neighborhood": "Lower East Side",
        "venue_type": "sneaker_boutique",
        "notes": "Cinema-themed sneaker boutique, strong cultural identity",
    },
    {
        "name": "Stadium Goods SoHo",
        "url": "https://www.stadiumgoods.com",
        "neighborhood": "SoHo",
        "venue_type": "sneaker_boutique",
        "notes": "Premium resale sneaker marketplace with large retail floor",
    },
]


def get_retail_seeds(city: str) -> list:
    """Return curated retail seeds for a given city."""
    city = city.lower()
    if city == "dallas":
        return [dict(s) for s in DALLAS_RETAIL_SEEDS]
    elif city == "nyc":
        return [dict(s) for s in NYC_RETAIL_SEEDS]
    return []
