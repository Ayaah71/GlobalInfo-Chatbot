"""
chatbot_service.py
Parses user intent from natural language messages and generates
friendly, structured responses using the country_service.
"""

import re
from services.country_service import (
    get_country_info,
    format_population,
    format_area,
)

# ---------------------------------------------------------------------------
# Intent keywords
# ---------------------------------------------------------------------------

INTENT_PATTERNS = {
    "capital": [
        r"\bcapital\b", r"\bcapital city\b", r"\bwhere is the capital\b",
    ],
    "population": [
        r"\bpopulation\b", r"\bhow many people\b", r"\bhow populated\b",
        r"\bnumber of people\b", r"\binhabitants\b",
    ],
    "currency": [
        r"\bcurrenc(?:y|ies)\b", r"\bmoney\b", r"\bwhat currency\b",
        r"\bused currency\b",
    ],
    "language": [
        r"\blanguage[s]?\b", r"\bspoken\b", r"\bofficial language\b",
        r"\bwhat language\b",
    ],
    "region": [
        r"\bregion\b", r"\bcontinent\b", r"\bsubregion\b", r"\bwhere is\b",
        r"\blocated\b", r"\blocation\b", r"\bpart of the world\b",
    ],
    "flag": [
        r"\bflag\b",
    ],
    "area": [
        r"\barea\b", r"\bsize\b", r"\bhow big\b", r"\bkm\b",
        r"\bsquare\b", r"\bkm²\b", r"\bland mass\b",
    ],
    "timezone": [
        r"\btimezone[s]?\b", r"\btime zone[s]?\b", r"\btime difference\b",
        r"\bwhat time\b",
    ],
    "border": [
        r"\bborder[s]?\b", r"\bneighbor[s]?\b", r"\bneighbour[s]?\b",
        r"\bnext to\b", r"\bsurrounded by\b", r"\badjacent\b",
    ],
    "calling_code": [
        r"\bcalling code\b", r"\bphone code\b", r"\bdialing code\b",
        r"\bcountry code\b",
    ],
    "general": [
        r"\btell me about\b", r"\binfo(?:rmation)? (?:about|on)\b",
        r"\bwhat (?:do you know|can you tell me) about\b",
        r"\bdetails? (?:about|on|for)\b", r"\bfacts? (?:about|on)\b",
        r"\boverview\b",
    ],
}

# Words to strip before trying to extract the country name
FILLER_WORDS = re.compile(
    r"\b(?:tell|me|about|what|is|the|of|in|for|does|do|use|speak|are|"
    r"official|language|languages|capital|population|currency|currencies|"
    r"region|flag|area|size|timezone|timezones|border|borders|neighbor|"
    r"neighbours|neighbors|calling|code|dialing|phone|people|how|big|"
    r"many|located|where|know|you|can|info|information|details|facts|"
    r"overview|spoken|lived|inhabited|inhabited|and|or|a|an|its|their|"
    r"country|countries)\b",
    re.IGNORECASE,
)

# Explicit country extraction patterns
EXPLICIT_PATTERNS = [
    re.compile(r"\babout\s+([A-Za-z\s]+?)(?:\?|$)", re.IGNORECASE),
    re.compile(r"\bof\s+([A-Za-z\s]+?)(?:\?|$)", re.IGNORECASE),
    re.compile(r"\bin\s+([A-Za-z\s]+?)(?:\?|$)", re.IGNORECASE),
    re.compile(r"\bfor\s+([A-Za-z\s]+?)(?:\?|$)", re.IGNORECASE),
]

# ---------------------------------------------------------------------------
# Intent detection
# ---------------------------------------------------------------------------

def detect_intent(message: str) -> str:
    """
    Return the most specific intent found in the message.
    Falls back to 'general' if nothing specific is detected.
    """
    msg_lower = message.lower()
    for intent, patterns in INTENT_PATTERNS.items():
        if intent == "general":
            continue
        for pattern in patterns:
            if re.search(pattern, msg_lower):
                return intent
    # Check general last
    for pattern in INTENT_PATTERNS["general"]:
        if re.search(pattern, msg_lower):
            return "general"
    return "general"


def extract_country(message: str) -> str:
    """
    Extract the most likely country name from the user message.
    Tries explicit patterns first, then falls back to stripping filler words.
    """
    # Try explicit extraction patterns
    for pattern in EXPLICIT_PATTERNS:
        match = pattern.search(message)
        if match:
            candidate = match.group(1).strip().rstrip("?., ")
            candidate = candidate.strip()
            if len(candidate) >= 2:
                return candidate

    # Fallback: strip filler words and take what remains
    cleaned = FILLER_WORDS.sub("", message)
    cleaned = re.sub(r"\s+", " ", cleaned).strip().rstrip("?.,! ")
    return cleaned


# ---------------------------------------------------------------------------
# Response builders
# ---------------------------------------------------------------------------

def _currencies_str(currencies: dict) -> str:
    if not currencies:
        return "N/A"
    return ", ".join(f"{name} ({code})" for code, name in currencies.items())


def _languages_str(languages: list) -> str:
    return ", ".join(languages) if languages else "N/A"


def _timezones_str(timezones: list) -> str:
    if not timezones:
        return "N/A"
    if len(timezones) == 1:
        return timezones[0]
    return f"{timezones[0]} to {timezones[-1]} ({len(timezones)} zones)"


def build_response(intent: str, data: dict) -> str:
    name = data["name"]
    flag = data["flag_emoji"]

    if intent == "capital":
        return (
            f"{flag} The capital of **{name}** is **{data['capital']}**."
        )

    elif intent == "population":
        pop = format_population(data["population"])
        return (
            f"{flag} **{name}** has a population of approximately **{pop}**."
        )

    elif intent == "currency":
        currencies = _currencies_str(data["currencies"])
        return (
            f"{flag} The official currenc{'y' if len(data['currencies']) == 1 else 'ies'} "
            f"of **{name}** {'is' if len(data['currencies']) == 1 else 'are'} **{currencies}**."
        )

    elif intent == "language":
        langs = _languages_str(data["languages"])
        count = len(data["languages"])
        verb = "is" if count == 1 else "are"
        return (
            f"{flag} The official language{'s' if count > 1 else ''} spoken in **{name}** "
            f"{verb} **{langs}**."
        )

    elif intent == "region":
        sub = f" (Subregion: **{data['subregion']}**)" if data["subregion"] != "N/A" else ""
        conts = ", ".join(data["continents"]) if data["continents"] else data["region"]
        return (
            f"{flag} **{name}** is located in **{data['region']}**{sub}. "
            f"Continent: **{conts}**."
        )

    elif intent == "flag":
        return (
            f"The flag of **{name}** is: **{flag}**\n"
            f"🔗 [View flag image]({data['flag_url']})"
        )

    elif intent == "area":
        area_str = format_area(data["area"])
        return (
            f"{flag} **{name}** covers an area of **{area_str}**."
        )

    elif intent == "timezone":
        tz = _timezones_str(data["timezones"])
        return (
            f"{flag} **{name}** observes the following timezone(s): **{tz}**."
        )

    elif intent == "border":
        borders = data["borders"]
        if not borders:
            return (
                f"{flag} **{name}** has no land borders — it is an island nation "
                f"or entirely surrounded by water."
            )
        border_list = ", ".join(borders)
        return (
            f"{flag} **{name}** shares land borders with **{len(borders)}** "
            f"countr{'y' if len(borders) == 1 else 'ies'}: **{border_list}**."
        )

    elif intent == "calling_code":
        return (
            f"{flag} The international calling code for **{name}** is **{data['calling_code']}**."
        )

    else:
        # General / overview
        pop = format_population(data["population"])
        area_str = format_area(data["area"])
        langs = _languages_str(data["languages"])
        currencies = _currencies_str(data["currencies"])
        tz = _timezones_str(data["timezones"])
        border_count = len(data["borders"])

        return (
            f"{flag} Here's an overview of **{data['name']}** ({data['official_name']}):\n\n"
            f"🏛️ **Capital:** {data['capital']}\n"
            f"🌍 **Region:** {data['region']}" + (f" / {data['subregion']}" if data['subregion'] != 'N/A' else "") + "\n"
            f"🌐 **Continent:** {', '.join(data['continents']) if data['continents'] else data['region']}\n"
            f"👥 **Population:** {pop}\n"
            f"📐 **Area:** {area_str}\n"
            f"💰 **Currency:** {currencies}\n"
            f"🗣️ **Languages:** {langs}\n"
            f"⏰ **Timezone(s):** {tz}\n"
            f"🤝 **Land Borders:** {border_count} countr{'y' if border_count == 1 else 'ies'}\n"
            f"📞 **Calling Code:** {data['calling_code']}"
        )


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def process_message(message: str) -> dict:
    """
    Parse the user message, fetch country data, and return a response dict.
    Returns: { "response": str, "data": dict | None, "intent": str }
    """
    # Handle greetings
    greetings = re.compile(
        r"^\s*(?:hi|hello|hey|good\s+(?:morning|afternoon|evening)|greetings|howdy)[!?.,\s]*$",
        re.IGNORECASE,
    )
    if greetings.match(message.strip()):
        return {
            "response": (
                "👋 Hello! I'm **GlobalInfo**, your world knowledge assistant.\n\n"
                "You can ask me things like:\n"
                "- *Tell me about Japan*\n"
                "- *What is the capital of Brazil?*\n"
                "- *Currency of Egypt*\n"
                "- *Languages spoken in Switzerland*\n"
                "- *Population of India*\n\n"
                "What country would you like to explore? 🌍"
            ),
            "data": None,
            "intent": "greeting",
        }

    # Handle help
    help_keywords = re.compile(r"\b(?:help|what can you do|commands|options)\b", re.IGNORECASE)
    if help_keywords.search(message):
        return {
            "response": (
                "🤖 I can answer questions about any country in the world!\n\n"
                "**Try asking:**\n"
                "- *Capital of France*\n"
                "- *Population of China*\n"
                "- *What currency does Japan use?*\n"
                "- *Languages in Canada*\n"
                "- *Where is Australia located?*\n"
                "- *Borders of Germany*\n"
                "- *Area of Russia*\n"
                "- *Timezone of New Zealand*\n"
                "- *Tell me about Egypt* (full overview)"
            ),
            "data": None,
            "intent": "help",
        }

    intent = detect_intent(message)
    country_name = extract_country(message)

    if not country_name or len(country_name) < 2:
        return {
            "response": (
                "🤔 I couldn't identify a country in your message. "
                "Try something like:\n"
                "- *Tell me about Germany*\n"
                "- *Capital of Egypt*\n"
                "- *Population of Brazil*"
            ),
            "data": None,
            "intent": "unknown",
        }

    data = get_country_info(country_name)

    if data is None:
        return {
            "response": (
                f"❌ I couldn't find any information about **\"{country_name}\"**. "
                "Please check the spelling, or try a different name.\n\n"
                "Examples: *France*, *South Korea*, *United States*, *Saudi Arabia*"
            ),
            "data": None,
            "intent": intent,
        }

    response_text = build_response(intent, data)

    return {
        "response": response_text,
        "data": data,
        "intent": intent,
    }
