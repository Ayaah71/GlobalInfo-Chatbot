"""
country_service.py
Provides country information using the mledoze/countries GitHub dataset
(free, no API key, same schema as former restcountries v3.1).
Data is fetched once and cached in-memory.

Population and extra data is supplemented from a static lookup for
countries that don't carry those fields in the base dataset.
"""

import requests
from typing import Optional
import threading

# ---------------------------------------------------------------------------
# Primary source: mledoze/countries (GitHub raw JSON, ~250 countries)
# ---------------------------------------------------------------------------
COUNTRIES_JSON_URL = (
    "https://raw.githubusercontent.com/mledoze/countries/master/countries.json"
)

# ---------------------------------------------------------------------------
# Supplemental population data (2024 estimates) + continents + timezones
# keyed by CCA3 code (ISO 3166-1 alpha-3)
# ---------------------------------------------------------------------------
_SUPPLEMENT: dict = {
    "AFG": {"population": 43356890, "continents": ["Asia"], "timezones": ["UTC+04:30"]},
    "ALB": {"population": 2854191, "continents": ["Europe"], "timezones": ["UTC+01:00"]},
    "DZA": {"population": 46010000, "continents": ["Africa"], "timezones": ["UTC+01:00"]},
    "AND": {"population": 79824, "continents": ["Europe"], "timezones": ["UTC+01:00"]},
    "AGO": {"population": 36010000, "continents": ["Africa"], "timezones": ["UTC+01:00"]},
    "ATG": {"population": 93763, "continents": ["North America"], "timezones": ["UTC-04:00"]},
    "ARG": {"population": 46654581, "continents": ["South America"], "timezones": ["UTC-03:00"]},
    "ARM": {"population": 2777970, "continents": ["Asia"], "timezones": ["UTC+04:00"]},
    "AUS": {"population": 26177413, "continents": ["Oceania"], "timezones": ["UTC+05:00", "UTC+06:30", "UTC+07:00", "UTC+08:00", "UTC+09:30", "UTC+10:00", "UTC+10:30", "UTC+11:30"]},
    "AUT": {"population": 9027999, "continents": ["Europe"], "timezones": ["UTC+01:00"]},
    "AZE": {"population": 10358075, "continents": ["Asia"], "timezones": ["UTC+04:00"]},
    "BHS": {"population": 393248, "continents": ["North America"], "timezones": ["UTC-05:00"]},
    "BHR": {"population": 1463265, "continents": ["Asia"], "timezones": ["UTC+03:00"]},
    "BGD": {"population": 169356251, "continents": ["Asia"], "timezones": ["UTC+06:00"]},
    "BRB": {"population": 281200, "continents": ["North America"], "timezones": ["UTC-04:00"]},
    "BLR": {"population": 9449323, "continents": ["Europe"], "timezones": ["UTC+03:00"]},
    "BEL": {"population": 11555997, "continents": ["Europe"], "timezones": ["UTC+01:00"]},
    "BLZ": {"population": 400031, "continents": ["North America"], "timezones": ["UTC-06:00"]},
    "BEN": {"population": 12996895, "continents": ["Africa"], "timezones": ["UTC+01:00"]},
    "BTN": {"population": 771612, "continents": ["Asia"], "timezones": ["UTC+06:00"]},
    "BOL": {"population": 12079472, "continents": ["South America"], "timezones": ["UTC-04:00"]},
    "BIH": {"population": 3280815, "continents": ["Europe"], "timezones": ["UTC+01:00"]},
    "BWA": {"population": 2630296, "continents": ["Africa"], "timezones": ["UTC+02:00"]},
    "BRA": {"population": 215313498, "continents": ["South America"], "timezones": ["UTC-05:00", "UTC-04:00", "UTC-03:00", "UTC-02:00"]},
    "BRN": {"population": 441532, "continents": ["Asia"], "timezones": ["UTC+08:00"]},
    "BGR": {"population": 6465761, "continents": ["Europe"], "timezones": ["UTC+02:00"]},
    "BFA": {"population": 22100683, "continents": ["Africa"], "timezones": ["UTC"]},
    "BDI": {"population": 12574571, "continents": ["Africa"], "timezones": ["UTC+02:00"]},
    "CPV": {"population": 593149, "continents": ["Africa"], "timezones": ["UTC-01:00"]},
    "KHM": {"population": 16718965, "continents": ["Asia"], "timezones": ["UTC+07:00"]},
    "CMR": {"population": 27911548, "continents": ["Africa"], "timezones": ["UTC+01:00"]},
    "CAN": {"population": 38246108, "continents": ["North America"], "timezones": ["UTC-08:00", "UTC-07:00", "UTC-06:00", "UTC-05:00", "UTC-04:00", "UTC-03:30"]},
    "CAF": {"population": 4900274, "continents": ["Africa"], "timezones": ["UTC+01:00"]},
    "TCD": {"population": 17414108, "continents": ["Africa"], "timezones": ["UTC+01:00"]},
    "CHL": {"population": 19116201, "continents": ["South America"], "timezones": ["UTC-06:00", "UTC-04:00"]},
    "CHN": {"population": 1412600000, "continents": ["Asia"], "timezones": ["UTC+08:00"]},
    "COL": {"population": 50882891, "continents": ["South America"], "timezones": ["UTC-05:00"]},
    "COM": {"population": 806153, "continents": ["Africa"], "timezones": ["UTC+03:00"]},
    "COD": {"population": 99010212, "continents": ["Africa"], "timezones": ["UTC+01:00", "UTC+02:00"]},
    "COG": {"population": 5835806, "continents": ["Africa"], "timezones": ["UTC+01:00"]},
    "CRI": {"population": 5153957, "continents": ["North America"], "timezones": ["UTC-06:00"]},
    "CIV": {"population": 26811790, "continents": ["Africa"], "timezones": ["UTC"]},
    "HRV": {"population": 3879074, "continents": ["Europe"], "timezones": ["UTC+01:00"]},
    "CUB": {"population": 11326616, "continents": ["North America"], "timezones": ["UTC-05:00"]},
    "CYP": {"population": 1237088, "continents": ["Europe", "Asia"], "timezones": ["UTC+02:00"]},
    "CZE": {"population": 10701777, "continents": ["Europe"], "timezones": ["UTC+01:00"]},
    "DNK": {"population": 5910913, "continents": ["Europe"], "timezones": ["UTC-04:00", "UTC-03:00", "UTC+01:00"]},
    "DJI": {"population": 1105557, "continents": ["Africa"], "timezones": ["UTC+03:00"]},
    "DMA": {"population": 71986, "continents": ["North America"], "timezones": ["UTC-04:00"]},
    "DOM": {"population": 10953703, "continents": ["North America"], "timezones": ["UTC-04:00"]},
    "ECU": {"population": 18001000, "continents": ["South America"], "timezones": ["UTC-06:00", "UTC-05:00"]},
    "EGY": {"population": 102334404, "continents": ["Africa", "Asia"], "timezones": ["UTC+02:00"]},
    "SLV": {"population": 6314167, "continents": ["North America"], "timezones": ["UTC-06:00"]},
    "GNQ": {"population": 1402985, "continents": ["Africa"], "timezones": ["UTC+01:00"]},
    "ERI": {"population": 3546421, "continents": ["Africa"], "timezones": ["UTC+03:00"]},
    "EST": {"population": 1331057, "continents": ["Europe"], "timezones": ["UTC+02:00"]},
    "SWZ": {"population": 1160164, "continents": ["Africa"], "timezones": ["UTC+02:00"]},
    "ETH": {"population": 117876227, "continents": ["Africa"], "timezones": ["UTC+03:00"]},
    "FJI": {"population": 929766, "continents": ["Oceania"], "timezones": ["UTC+12:00"]},
    "FIN": {"population": 5530719, "continents": ["Europe"], "timezones": ["UTC+02:00"]},
    "FRA": {"population": 67391582, "continents": ["Europe"], "timezones": ["UTC-10:00", "UTC-09:30", "UTC-09:00", "UTC-08:00", "UTC-04:00", "UTC-03:00", "UTC+01:00", "UTC+03:00", "UTC+04:00", "UTC+05:00", "UTC+11:00", "UTC+12:00"]},
    "GAB": {"population": 2278825, "continents": ["Africa"], "timezones": ["UTC+01:00"]},
    "GMB": {"population": 2416664, "continents": ["Africa"], "timezones": ["UTC"]},
    "GEO": {"population": 3716858, "continents": ["Asia", "Europe"], "timezones": ["UTC+04:00"]},
    "DEU": {"population": 83240525, "continents": ["Europe"], "timezones": ["UTC+01:00"]},
    "GHA": {"population": 31732129, "continents": ["Africa"], "timezones": ["UTC"]},
    "GRC": {"population": 10432481, "continents": ["Europe"], "timezones": ["UTC+02:00"]},
    "GRD": {"population": 112519, "continents": ["North America"], "timezones": ["UTC-04:00"]},
    "GTM": {"population": 17109746, "continents": ["North America"], "timezones": ["UTC-06:00"]},
    "GIN": {"population": 13531906, "continents": ["Africa"], "timezones": ["UTC"]},
    "GNB": {"population": 1967998, "continents": ["Africa"], "timezones": ["UTC"]},
    "GUY": {"population": 786559, "continents": ["South America"], "timezones": ["UTC-04:00"]},
    "HTI": {"population": 11402528, "continents": ["North America"], "timezones": ["UTC-05:00"]},
    "HND": {"population": 10278345, "continents": ["North America"], "timezones": ["UTC-06:00"]},
    "HUN": {"population": 9749763, "continents": ["Europe"], "timezones": ["UTC+01:00"]},
    "ISL": {"population": 366425, "continents": ["Europe"], "timezones": ["UTC"]},
    "IND": {"population": 1428627663, "continents": ["Asia"], "timezones": ["UTC+05:30"]},
    "IDN": {"population": 273523615, "continents": ["Asia"], "timezones": ["UTC+07:00", "UTC+08:00", "UTC+09:00"]},
    "IRN": {"population": 85028759, "continents": ["Asia"], "timezones": ["UTC+03:30"]},
    "IRQ": {"population": 40222493, "continents": ["Asia"], "timezones": ["UTC+03:00"]},
    "IRL": {"population": 5123536, "continents": ["Europe"], "timezones": ["UTC"]},
    "ISR": {"population": 9449000, "continents": ["Asia"], "timezones": ["UTC+02:00"]},
    "ITA": {"population": 59554023, "continents": ["Europe"], "timezones": ["UTC+01:00"]},
    "JAM": {"population": 2961161, "continents": ["North America"], "timezones": ["UTC-05:00"]},
    "JPN": {"population": 125681593, "continents": ["Asia"], "timezones": ["UTC+09:00"]},
    "JOR": {"population": 10203140, "continents": ["Asia"], "timezones": ["UTC+02:00"]},
    "KAZ": {"population": 19397998, "continents": ["Asia", "Europe"], "timezones": ["UTC+05:00", "UTC+06:00"]},
    "KEN": {"population": 54985698, "continents": ["Africa"], "timezones": ["UTC+03:00"]},
    "KIR": {"population": 119446, "continents": ["Oceania"], "timezones": ["UTC+12:00", "UTC+13:00", "UTC+14:00"]},
    "KWT": {"population": 4270563, "continents": ["Asia"], "timezones": ["UTC+03:00"]},
    "KGZ": {"population": 6592000, "continents": ["Asia"], "timezones": ["UTC+06:00"]},
    "LAO": {"population": 7379358, "continents": ["Asia"], "timezones": ["UTC+07:00"]},
    "LVA": {"population": 1830211, "continents": ["Europe"], "timezones": ["UTC+02:00"]},
    "LBN": {"population": 6769000, "continents": ["Asia"], "timezones": ["UTC+02:00"]},
    "LSO": {"population": 2159000, "continents": ["Africa"], "timezones": ["UTC+02:00"]},
    "LBR": {"population": 5218450, "continents": ["Africa"], "timezones": ["UTC"]},
    "LBY": {"population": 6959000, "continents": ["Africa"], "timezones": ["UTC+02:00"]},
    "LIE": {"population": 38128, "continents": ["Europe"], "timezones": ["UTC+01:00"]},
    "LTU": {"population": 2794090, "continents": ["Europe"], "timezones": ["UTC+02:00"]},
    "LUX": {"population": 632275, "continents": ["Europe"], "timezones": ["UTC+01:00"]},
    "MDG": {"population": 27691019, "continents": ["Africa"], "timezones": ["UTC+03:00"]},
    "MWI": {"population": 19129952, "continents": ["Africa"], "timezones": ["UTC+02:00"]},
    "MYS": {"population": 32657400, "continents": ["Asia"], "timezones": ["UTC+08:00"]},
    "MDV": {"population": 540985, "continents": ["Asia"], "timezones": ["UTC+05:00"]},
    "MLI": {"population": 22395489, "continents": ["Africa"], "timezones": ["UTC"]},
    "MLT": {"population": 525285, "continents": ["Europe"], "timezones": ["UTC+01:00"]},
    "MHL": {"population": 42050, "continents": ["Oceania"], "timezones": ["UTC+12:00"]},
    "MRT": {"population": 4614974, "continents": ["Africa"], "timezones": ["UTC"]},
    "MUS": {"population": 1271768, "continents": ["Africa"], "timezones": ["UTC+04:00"]},
    "MEX": {"population": 126705138, "continents": ["North America"], "timezones": ["UTC-08:00", "UTC-07:00", "UTC-06:00"]},
    "FSM": {"population": 115021, "continents": ["Oceania"], "timezones": ["UTC+10:00", "UTC+11:00"]},
    "MDA": {"population": 2617820, "continents": ["Europe"], "timezones": ["UTC+02:00"]},
    "MCO": {"population": 39242, "continents": ["Europe"], "timezones": ["UTC+01:00"]},
    "MNG": {"population": 3278292, "continents": ["Asia"], "timezones": ["UTC+07:00", "UTC+08:00"]},
    "MNE": {"population": 621718, "continents": ["Europe"], "timezones": ["UTC+01:00"]},
    "MAR": {"population": 37344795, "continents": ["Africa"], "timezones": ["UTC+01:00"]},
    "MOZ": {"population": 32790338, "continents": ["Africa"], "timezones": ["UTC+02:00"]},
    "MMR": {"population": 54409800, "continents": ["Asia"], "timezones": ["UTC+06:30"]},
    "NAM": {"population": 2550226, "continents": ["Africa"], "timezones": ["UTC+02:00"]},
    "NRU": {"population": 10824, "continents": ["Oceania"], "timezones": ["UTC+12:00"]},
    "NPL": {"population": 29136808, "continents": ["Asia"], "timezones": ["UTC+05:45"]},
    "NLD": {"population": 17441139, "continents": ["Europe"], "timezones": ["UTC-04:00", "UTC+01:00"]},
    "NZL": {"population": 5122600, "continents": ["Oceania"], "timezones": ["UTC+12:00", "UTC+12:45", "UTC+13:00"]},
    "NIC": {"population": 6624554, "continents": ["North America"], "timezones": ["UTC-06:00"]},
    "NER": {"population": 24206636, "continents": ["Africa"], "timezones": ["UTC+01:00"]},
    "NGA": {"population": 213401323, "continents": ["Africa"], "timezones": ["UTC+01:00"]},
    "PRK": {"population": 25778815, "continents": ["Asia"], "timezones": ["UTC+09:00"]},
    "MKD": {"population": 2077132, "continents": ["Europe"], "timezones": ["UTC+01:00"]},
    "NOR": {"population": 5379475, "continents": ["Europe"], "timezones": ["UTC+01:00"]},
    "OMN": {"population": 4520471, "continents": ["Asia"], "timezones": ["UTC+04:00"]},
    "PAK": {"population": 220892331, "continents": ["Asia"], "timezones": ["UTC+05:00"]},
    "PLW": {"population": 18094, "continents": ["Oceania"], "timezones": ["UTC+09:00"]},
    "PAN": {"population": 4351267, "continents": ["North America"], "timezones": ["UTC-05:00"]},
    "PNG": {"population": 9119829, "continents": ["Oceania"], "timezones": ["UTC+10:00", "UTC+11:00"]},
    "PRY": {"population": 7132538, "continents": ["South America"], "timezones": ["UTC-04:00"]},
    "PER": {"population": 32971854, "continents": ["South America"], "timezones": ["UTC-05:00"]},
    "PHL": {"population": 109581085, "continents": ["Asia"], "timezones": ["UTC+08:00"]},
    "POL": {"population": 37950802, "continents": ["Europe"], "timezones": ["UTC+01:00"]},
    "PRT": {"population": 10305564, "continents": ["Europe"], "timezones": ["UTC-01:00", "UTC"]},
    "QAT": {"population": 2930524, "continents": ["Asia"], "timezones": ["UTC+03:00"]},
    "ROU": {"population": 19237691, "continents": ["Europe"], "timezones": ["UTC+02:00"]},
    "RUS": {"population": 144104080, "continents": ["Europe", "Asia"], "timezones": ["UTC+02:00", "UTC+03:00", "UTC+04:00", "UTC+05:00", "UTC+06:00", "UTC+07:00", "UTC+08:00", "UTC+09:00", "UTC+10:00", "UTC+11:00", "UTC+12:00"]},
    "RWA": {"population": 13461888, "continents": ["Africa"], "timezones": ["UTC+02:00"]},
    "KNA": {"population": 53544, "continents": ["North America"], "timezones": ["UTC-04:00"]},
    "LCA": {"population": 183627, "continents": ["North America"], "timezones": ["UTC-04:00"]},
    "VCT": {"population": 110947, "continents": ["North America"], "timezones": ["UTC-04:00"]},
    "WSM": {"population": 218764, "continents": ["Oceania"], "timezones": ["UTC+13:00"]},
    "SMR": {"population": 33931, "continents": ["Europe"], "timezones": ["UTC+01:00"]},
    "STP": {"population": 219159, "continents": ["Africa"], "timezones": ["UTC"]},
    "SAU": {"population": 34813871, "continents": ["Asia"], "timezones": ["UTC+03:00"]},
    "SEN": {"population": 17196301, "continents": ["Africa"], "timezones": ["UTC"]},
    "SRB": {"population": 6804596, "continents": ["Europe"], "timezones": ["UTC+01:00"]},
    "SYC": {"population": 98347, "continents": ["Africa"], "timezones": ["UTC+04:00"]},
    "SLE": {"population": 8233234, "continents": ["Africa"], "timezones": ["UTC"]},
    "SGP": {"population": 5685807, "continents": ["Asia"], "timezones": ["UTC+08:00"]},
    "SVK": {"population": 5460185, "continents": ["Europe"], "timezones": ["UTC+01:00"]},
    "SVN": {"population": 2100126, "continents": ["Europe"], "timezones": ["UTC+01:00"]},
    "SLB": {"population": 720424, "continents": ["Oceania"], "timezones": ["UTC+11:00"]},
    "SOM": {"population": 17065581, "continents": ["Africa"], "timezones": ["UTC+03:00"]},
    "ZAF": {"population": 59308690, "continents": ["Africa"], "timezones": ["UTC+02:00"]},
    "KOR": {"population": 51780579, "continents": ["Asia"], "timezones": ["UTC+09:00"]},
    "SSD": {"population": 11381378, "continents": ["Africa"], "timezones": ["UTC+03:00"]},
    "ESP": {"population": 47351567, "continents": ["Europe"], "timezones": ["UTC", "UTC+01:00"]},
    "LKA": {"population": 21919000, "continents": ["Asia"], "timezones": ["UTC+05:30"]},
    "SDN": {"population": 43849260, "continents": ["Africa"], "timezones": ["UTC+03:00"]},
    "SUR": {"population": 586632, "continents": ["South America"], "timezones": ["UTC-03:00"]},
    "SWE": {"population": 10353442, "continents": ["Europe"], "timezones": ["UTC+01:00"]},
    "CHE": {"population": 8654622, "continents": ["Europe"], "timezones": ["UTC+01:00"]},
    "SYR": {"population": 21324000, "continents": ["Asia"], "timezones": ["UTC+02:00"]},
    "TWN": {"population": 23503349, "continents": ["Asia"], "timezones": ["UTC+08:00"]},
    "TJK": {"population": 9537645, "continents": ["Asia"], "timezones": ["UTC+05:00"]},
    "TZA": {"population": 61498437, "continents": ["Africa"], "timezones": ["UTC+03:00"]},
    "THA": {"population": 69799978, "continents": ["Asia"], "timezones": ["UTC+07:00"]},
    "TLS": {"population": 1317780, "continents": ["Asia"], "timezones": ["UTC+09:00"]},
    "TGO": {"population": 8278724, "continents": ["Africa"], "timezones": ["UTC"]},
    "TON": {"population": 99532, "continents": ["Oceania"], "timezones": ["UTC+13:00"]},
    "TTO": {"population": 1399488, "continents": ["North America"], "timezones": ["UTC-04:00"]},
    "TUN": {"population": 11818619, "continents": ["Africa"], "timezones": ["UTC+01:00"]},
    "TUR": {"population": 84339067, "continents": ["Asia", "Europe"], "timezones": ["UTC+03:00"]},
    "TKM": {"population": 6117924, "continents": ["Asia"], "timezones": ["UTC+05:00"]},
    "TUV": {"population": 11792, "continents": ["Oceania"], "timezones": ["UTC+12:00"]},
    "UGA": {"population": 45741007, "continents": ["Africa"], "timezones": ["UTC+03:00"]},
    "UKR": {"population": 43467000, "continents": ["Europe"], "timezones": ["UTC+02:00"]},
    "ARE": {"population": 9890400, "continents": ["Asia"], "timezones": ["UTC+04:00"]},
    "GBR": {"population": 67215293, "continents": ["Europe"], "timezones": ["UTC-08:00", "UTC-05:00", "UTC-04:00", "UTC-03:00", "UTC-02:00", "UTC", "UTC+01:00", "UTC+02:00", "UTC+06:00"]},
    "USA": {"population": 331449281, "continents": ["North America"], "timezones": ["UTC-12:00", "UTC-11:00", "UTC-10:00", "UTC-09:00", "UTC-08:00", "UTC-07:00", "UTC-06:00", "UTC-05:00", "UTC-04:00", "UTC+10:00", "UTC+12:00"]},
    "URY": {"population": 3473727, "continents": ["South America"], "timezones": ["UTC-03:00"]},
    "UZB": {"population": 35300000, "continents": ["Asia"], "timezones": ["UTC+05:00"]},
    "VUT": {"population": 307145, "continents": ["Oceania"], "timezones": ["UTC+11:00"]},
    "VEN": {"population": 28435943, "continents": ["South America"], "timezones": ["UTC-04:00"]},
    "VNM": {"population": 97338583, "continents": ["Asia"], "timezones": ["UTC+07:00"]},
    "YEM": {"population": 33696614, "continents": ["Asia"], "timezones": ["UTC+03:00"]},
    "ZMB": {"population": 18383956, "continents": ["Africa"], "timezones": ["UTC+02:00"]},
    "ZWE": {"population": 14862927, "continents": ["Africa"], "timezones": ["UTC+02:00"]},
}

# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------
_cache: list = []
_cache_lock = threading.Lock()


def _load_countries() -> list:
    """Load and cache all country data (thread-safe, loads once)."""
    global _cache
    with _cache_lock:
        if _cache:
            return _cache
        resp = requests.get(COUNTRIES_JSON_URL, timeout=20)
        resp.raise_for_status()
        _cache = resp.json()
    return _cache


def _find_country(name: str) -> Optional[dict]:
    """
    Search countries by common name, official name, or alt spellings.
    Case-insensitive, with fuzzy partial matching.
    """
    countries = _load_countries()
    name_lower = name.strip().lower()

    # 1. Exact common name
    for c in countries:
        if c["name"]["common"].lower() == name_lower:
            return c
    # 2. Exact official name
    for c in countries:
        if c["name"]["official"].lower() == name_lower:
            return c
    # 3. Partial common name (starts-with)
    for c in countries:
        if c["name"]["common"].lower().startswith(name_lower):
            return c
    # 4. Alternative spellings
    for c in countries:
        alts = [a.lower() for a in c.get("altSpellings", [])]
        if name_lower in alts:
            return c
    # 5. Substring match in common name
    for c in countries:
        if name_lower in c["name"]["common"].lower():
            return c
    # 6. Translation names
    for c in countries:
        for _lang, trans in c.get("translations", {}).items():
            if trans.get("common", "").lower() == name_lower:
                return c
    return None


def get_country_info(country_name: str) -> Optional[dict]:
    """
    Return a structured dict of country information, or None if not found.
    """
    try:
        raw = _find_country(country_name)
        if raw is None:
            return None

        cca3 = raw.get("cca3", "")
        sup = _SUPPLEMENT.get(cca3, {})

        # --- Name ---
        name_common = raw["name"]["common"]
        name_official = raw["name"].get("official", name_common)

        # --- Capital ---
        capitals = raw.get("capital", [])
        capital = capitals[0] if capitals else "N/A"

        # --- Population (supplement first, fallback to raw) ---
        population = sup.get("population", raw.get("population", 0))

        # --- Region / Subregion ---
        region = raw.get("region", "N/A")
        subregion = raw.get("subregion", "N/A")

        # --- Currencies ---
        raw_currencies = raw.get("currencies", {})
        currencies = {
            code: info.get("name", code)
            for code, info in raw_currencies.items()
        }

        # --- Languages ---
        languages = list(raw.get("languages", {}).values())

        # --- Flag emoji ---
        flag_emoji = raw.get("flag", "")

        # --- Flag image URL ---
        flags = raw.get("flags", {})
        flag_url = flags.get("png", flags.get("svg", ""))

        # --- Area ---
        area = raw.get("area", 0)

        # --- Timezones (supplement first) ---
        timezones = sup.get("timezones", raw.get("timezones", []))

        # --- Borders ---
        borders = raw.get("borders", [])

        # --- Continents (supplement first) ---
        continents = sup.get("continents", raw.get("continents", [region]))

        # --- Calling code ---
        idd = raw.get("idd", {})
        root = idd.get("root", "")
        suffixes = idd.get("suffixes", [])
        calling_code = f"{root}{suffixes[0]}" if root and suffixes else "N/A"

        return {
            "name": name_common,
            "official_name": name_official,
            "capital": capital,
            "population": population,
            "region": region,
            "subregion": subregion,
            "currencies": currencies,
            "languages": languages,
            "flag_emoji": flag_emoji,
            "flag_url": flag_url,
            "area": area,
            "timezones": timezones,
            "borders": borders,
            "continents": continents,
            "calling_code": calling_code,
        }

    except Exception:
        return None


def format_population(population: int) -> str:
    """Return a human-readable population string."""
    if population >= 1_000_000_000:
        return f"{population / 1_000_000_000:.2f} billion"
    elif population >= 1_000_000:
        return f"{population / 1_000_000:.2f} million"
    elif population >= 1_000:
        return f"{population / 1_000:.1f} thousand"
    return str(population)


def format_area(area: float) -> str:
    """Return a human-readable area string."""
    if area >= 1_000_000:
        return f"{area:,.0f} km\u00b2 ({area / 1_000_000:.2f} million km\u00b2)"
    return f"{area:,.0f} km\u00b2"
