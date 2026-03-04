# SNITC Sponsor & Venue Scraper

A specialized web scraping and enrichment engine designed for **Saturday Night in the City (SNITC)**. This tool automates the process of identifying high-quality brand sponsors and event venues across multiple cities, providing detailed lead generation for cultural event organizers.

## 🌟 Use Case Strategy
The primary goal of this tool is to bridge the gap between "searching for prospects" and "sending outreach." It is optimized for events like **SNITC** and **Stargazing**, which require specific, high-vibe spaces (rooftops, lounges) and community-aligned brand sponsors (Black/Caribbean/Latin-owned, local NYC brands).

### How to use this data:
1. **Lead Discovery**: Use the scraper to find 30-50 venues or sponsors in minutes.
2. **Quality Vetting**: Review the **Priority A/B/C** rankings based on real-time website signals (rooftop access, capacity, nightlife status).
3. **Outreach**: Use the extracted, filtered contact emails to send personalized proposals.

---

## ✨ Features
- **Multi-City Discovery**: Support for **NYC**, **Atlanta**, and **Dallas**.
- **Smart Enrichment**: Goes beyond a simple search by scraping the target website to find:
    - **Capacity**: Prioritizes event/buyout numbers over restaurant seating.
    - **Signals**: Detects presence of Rooftops, DJ/Nightlife setups, Private Event options, and Cultural relevance.
    - **Clean Contacts**: Filters out image assets, script IDs (like Sentry hashes), and junk generic emails.
- **Fail-Safe Mode**: If search engines rate-limit the tool, it falls back to a curated `seeds_venues.py` list to ensure you always have high-quality leads.
- **Deduplication**: Automatically removes duplicate venues or websites before export.

---

## 🛠 Setup

1. **Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Permissions**:
   Ensure the run script is executable:
   ```bash
   chmod +x run.sh
   ```

---

## 📖 Commands

### 🏟 Venue Scraping
Identifies rooftops and event spaces based on capacity and vibe.

- **NYC (Full Search)**:
  ```bash
  ./run.sh --mode venues --city nyc
  ```
- **Atlanta (Seeds Only - Fastest)**:
  ```bash
  ./run.sh --mode venues --city atlanta --seeds_only
  ```
- **Test Mode (5 venues only)**:
  ```bash
  ./run.sh --mode venues --city dallas --test
  ```

### 🤝 Sponsor Scraping
Identifies brand sponsors based on ownership and location criteria.
```bash
./run.sh --mode sponsors --city nyc
```

---

## 📂 Project Architecture

- `main.py`: Entrypoint for CLI commands.
- `venues/`: 
    - `pipeline.py`: Orchestrates the search → scrape → classify → export loop.
    - `searcher_venues.py`: Custom DuckDuckGo scraper (bypasses standard search API limits).
    - `extractor_venues.py`: High-accuracy parsing logic (regex-based email/capacity extraction).
    - `seeds_venues.py`: Curated list of "Gold Standard" venues to ensure data quality.
- `sponsors/`: Dedicated logic for discovering and ranking brand partners.
- `scraper.py`: Core page-fetching utility with built-in "politeness" delays.

---

## 📊 Understanding the Output
Finished CSVs are saved in the `output/` folder and named by city and timestamp (e.g., `v_nyc_0304_1755.csv`).

| Column | Description |
| :--- | :--- |
| **Priority** | A = Perfect Match, B = Strong Fit, C = Needs Review |
| **Capacity** | Estimated guest count for private events/buyouts |
| **Contact** | Cleaned business email and/or phone number |
| **Notes** | Summary of why the venue was ranked that way |

---

## 🧑‍💻 Development
This tool was built to be agentic and robust, using direct HTML scraping to avoid expensive API keys while maintaining high accuracy for niche cultural events.
