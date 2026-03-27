#!/usr/bin/env python3
"""
CityScout — Minimalist digital nomad city recommender.
Usage:
    python cityscout.py
    python cityscout.py "olcsó, tenger, jó wifi, nyugodt"
    python cityscout.py --query "cheap, beach, fast wifi, quiet"
    python cityscout.py "cheap beach" --json-only
"""

import argparse
import json
import os
import re
import sys

import anthropic

# ---------------------------------------------------------------------------
# City knowledge base — edit freely
# ---------------------------------------------------------------------------
CITIES = [
    {
        "name": "Chiang Mai", "country": "Thailand",
        "cost": "budget", "internet": "good", "beach": False,
        "climate": "tropical", "vibe": ["chill", "digital nomad hub", "cultural"],
        "safety": "high", "english": "ok", "visa_ease": "easy",
        "timezone": "UTC+7", "crowded": "medium",
        "cons": ["hot summers", "seasonal air pollution", "touristy in peak season"],
    },
    {
        "name": "Bali (Canggu)", "country": "Indonesia",
        "cost": "budget", "internet": "ok", "beach": True,
        "climate": "tropical", "vibe": ["surf", "digital nomad hub", "party", "wellness"],
        "safety": "high", "english": "good", "visa_ease": "easy",
        "timezone": "UTC+8", "crowded": "high",
        "cons": ["very crowded", "inconsistent internet", "tourist trap pricing"],
    },
    {
        "name": "Lisbon", "country": "Portugal",
        "cost": "mid", "internet": "excellent", "beach": True,
        "climate": "mediterranean", "vibe": ["cultural", "digital nomad hub", "chill"],
        "safety": "high", "english": "good", "visa_ease": "easy",
        "timezone": "UTC+0", "crowded": "high",
        "cons": ["rising rents", "very touristy", "hilly terrain"],
    },
    {
        "name": "Medellín", "country": "Colombia",
        "cost": "budget", "internet": "good", "beach": False,
        "climate": "spring-like year-round", "vibe": ["social", "digital nomad hub", "cultural"],
        "safety": "medium", "english": "poor", "visa_ease": "easy",
        "timezone": "UTC-5", "crowded": "medium",
        "cons": ["language barrier", "safety concerns in some areas", "no beach"],
    },
    {
        "name": "Budapest", "country": "Hungary",
        "cost": "budget", "internet": "excellent", "beach": False,
        "climate": "temperate", "vibe": ["cultural", "party", "chill"],
        "safety": "high", "english": "ok", "visa_ease": "easy",
        "timezone": "UTC+1", "crowded": "medium",
        "cons": ["cold winters", "no beach", "limited English outside center"],
    },
    {
        "name": "Prague", "country": "Czech Republic",
        "cost": "mid", "internet": "excellent", "beach": False,
        "climate": "temperate", "vibe": ["cultural", "historical", "party"],
        "safety": "high", "english": "ok", "visa_ease": "easy",
        "timezone": "UTC+1", "crowded": "high",
        "cons": ["cold winters", "no beach", "very touristy center"],
    },
    {
        "name": "Berlin", "country": "Germany",
        "cost": "mid", "internet": "good", "beach": False,
        "climate": "temperate", "vibe": ["creative", "tech", "party", "alternative"],
        "safety": "high", "english": "good", "visa_ease": "easy",
        "timezone": "UTC+1", "crowded": "medium",
        "cons": ["cold grey winters", "no beach", "expensive vs eastern Europe"],
    },
    {
        "name": "Barcelona", "country": "Spain",
        "cost": "mid", "internet": "good", "beach": True,
        "climate": "mediterranean", "vibe": ["social", "cultural", "beach", "party"],
        "safety": "medium", "english": "ok", "visa_ease": "easy",
        "timezone": "UTC+1", "crowded": "high",
        "cons": ["pickpockets", "high rent", "noisy party scene"],
    },
    {
        "name": "Tbilisi", "country": "Georgia",
        "cost": "budget", "internet": "good", "beach": False,
        "climate": "temperate", "vibe": ["cultural", "chill", "emerging"],
        "safety": "high", "english": "ok", "visa_ease": "easy",
        "timezone": "UTC+4", "crowded": "low",
        "cons": ["no beach", "language barrier", "limited direct flights"],
    },
    {
        "name": "Mexico City", "country": "Mexico",
        "cost": "mid", "internet": "good", "beach": False,
        "climate": "temperate", "vibe": ["cultural", "food", "social", "digital nomad hub"],
        "safety": "medium", "english": "ok", "visa_ease": "easy",
        "timezone": "UTC-6", "crowded": "high",
        "cons": ["air pollution", "traffic", "altitude for some", "no beach"],
    },
    {
        "name": "Ho Chi Minh City", "country": "Vietnam",
        "cost": "budget", "internet": "good", "beach": False,
        "climate": "tropical", "vibe": ["energetic", "food", "social"],
        "safety": "high", "english": "ok", "visa_ease": "medium",
        "timezone": "UTC+7", "crowded": "high",
        "cons": ["chaotic traffic", "humidity and heat", "no beach in city"],
    },
    {
        "name": "Bangkok", "country": "Thailand",
        "cost": "budget", "internet": "excellent", "beach": False,
        "climate": "tropical", "vibe": ["energetic", "food", "digital nomad hub"],
        "safety": "high", "english": "ok", "visa_ease": "easy",
        "timezone": "UTC+7", "crowded": "high",
        "cons": ["extreme heat", "traffic", "air pollution in dry season"],
    },
    {
        "name": "Kuala Lumpur", "country": "Malaysia",
        "cost": "budget", "internet": "excellent", "beach": False,
        "climate": "tropical", "vibe": ["multicultural", "food", "tech"],
        "safety": "high", "english": "good", "visa_ease": "easy",
        "timezone": "UTC+8", "crowded": "medium",
        "cons": ["heavy rain", "car-dependent layout", "no beach in city"],
    },
    {
        "name": "Tallinn", "country": "Estonia",
        "cost": "mid", "internet": "excellent", "beach": False,
        "climate": "temperate", "vibe": ["digital", "quiet", "historical"],
        "safety": "high", "english": "good", "visa_ease": "easy",
        "timezone": "UTC+2", "crowded": "low",
        "cons": ["cold winters", "no beach", "small city"],
    },
    {
        "name": "Porto", "country": "Portugal",
        "cost": "mid", "internet": "excellent", "beach": True,
        "climate": "mediterranean", "vibe": ["chill", "cultural", "creative"],
        "safety": "high", "english": "good", "visa_ease": "easy",
        "timezone": "UTC+0", "crowded": "medium",
        "cons": ["rainy winters", "hilly", "fewer coworking options than Lisbon"],
    },
    {
        "name": "Split", "country": "Croatia",
        "cost": "mid", "internet": "good", "beach": True,
        "climate": "mediterranean", "vibe": ["chill", "beach", "historical"],
        "safety": "high", "english": "good", "visa_ease": "easy",
        "timezone": "UTC+1", "crowded": "high",
        "cons": ["very touristy in summer", "expensive in peak season", "quiet off-season"],
    },
    {
        "name": "Playa del Carmen", "country": "Mexico",
        "cost": "mid", "internet": "good", "beach": True,
        "climate": "tropical", "vibe": ["beach", "social", "digital nomad hub"],
        "safety": "medium", "english": "good", "visa_ease": "easy",
        "timezone": "UTC-5", "crowded": "high",
        "cons": ["touristy", "safety concerns nearby", "expensive for Mexico"],
    },
    {
        "name": "Dubai", "country": "UAE",
        "cost": "expensive", "internet": "excellent", "beach": True,
        "climate": "arid", "vibe": ["luxury", "business", "modern"],
        "safety": "high", "english": "excellent", "visa_ease": "easy",
        "timezone": "UTC+4", "crowded": "medium",
        "cons": ["extreme summer heat", "very expensive", "cultural restrictions"],
    },
    {
        "name": "Singapore", "country": "Singapore",
        "cost": "expensive", "internet": "excellent", "beach": False,
        "climate": "tropical", "vibe": ["business", "tech", "multicultural"],
        "safety": "high", "english": "excellent", "visa_ease": "easy",
        "timezone": "UTC+8", "crowded": "high",
        "cons": ["very expensive", "small", "humidity"],
    },
    {
        "name": "Seoul", "country": "South Korea",
        "cost": "mid", "internet": "excellent", "beach": False,
        "climate": "temperate", "vibe": ["tech", "cultural", "food", "social"],
        "safety": "high", "english": "ok", "visa_ease": "easy",
        "timezone": "UTC+9", "crowded": "high",
        "cons": ["language barrier", "cold winters", "no beach in city"],
    },
    {
        "name": "Tokyo", "country": "Japan",
        "cost": "mid", "internet": "excellent", "beach": False,
        "climate": "temperate", "vibe": ["cultural", "tech", "unique", "quiet"],
        "safety": "high", "english": "poor", "visa_ease": "medium",
        "timezone": "UTC+9", "crowded": "high",
        "cons": ["language barrier", "expensive", "strict social norms"],
    },
    {
        "name": "Cape Town", "country": "South Africa",
        "cost": "budget", "internet": "good", "beach": True,
        "climate": "mediterranean", "vibe": ["outdoor", "chill", "scenic"],
        "safety": "medium", "english": "excellent", "visa_ease": "easy",
        "timezone": "UTC+2", "crowded": "low",
        "cons": ["safety concerns", "load shedding (power cuts)", "inequality"],
    },
    {
        "name": "Buenos Aires", "country": "Argentina",
        "cost": "budget", "internet": "ok", "beach": False,
        "climate": "temperate", "vibe": ["cultural", "social", "food", "nightlife"],
        "safety": "medium", "english": "poor", "visa_ease": "easy",
        "timezone": "UTC-3", "crowded": "medium",
        "cons": ["economic instability", "language barrier", "internet can be unreliable"],
    },
    {
        "name": "Bucharest", "country": "Romania",
        "cost": "budget", "internet": "excellent", "beach": False,
        "climate": "temperate", "vibe": ["emerging", "quiet", "digital"],
        "safety": "high", "english": "good", "visa_ease": "easy",
        "timezone": "UTC+2", "crowded": "low",
        "cons": ["cold winters", "no beach", "less vibrant nomad scene"],
    },
    {
        "name": "Warsaw", "country": "Poland",
        "cost": "mid", "internet": "excellent", "beach": False,
        "climate": "temperate", "vibe": ["business", "growing", "cultural"],
        "safety": "high", "english": "good", "visa_ease": "easy",
        "timezone": "UTC+1", "crowded": "low",
        "cons": ["cold winters", "no beach", "grey city aesthetic"],
    },
    {
        "name": "Istanbul", "country": "Turkey",
        "cost": "budget", "internet": "good", "beach": False,
        "climate": "mediterranean", "vibe": ["cultural", "food", "historical", "social"],
        "safety": "medium", "english": "ok", "visa_ease": "easy",
        "timezone": "UTC+3", "crowded": "high",
        "cons": ["political uncertainty", "traffic", "occasional safety concerns"],
    },
    {
        "name": "Tulum", "country": "Mexico",
        "cost": "mid", "internet": "ok", "beach": True,
        "climate": "tropical", "vibe": ["wellness", "beach", "eco", "chill"],
        "safety": "medium", "english": "good", "visa_ease": "easy",
        "timezone": "UTC-5", "crowded": "high",
        "cons": ["overpriced", "weak internet infrastructure", "safety concerns nearby"],
    },
    {
        "name": "Las Palmas", "country": "Spain (Gran Canaria)",
        "cost": "mid", "internet": "good", "beach": True,
        "climate": "spring-like year-round", "vibe": ["chill", "surf", "digital nomad hub"],
        "safety": "high", "english": "ok", "visa_ease": "easy",
        "timezone": "UTC+0", "crowded": "low",
        "cons": ["island isolation", "limited nightlife", "flights can be expensive"],
    },
    {
        "name": "Florianópolis", "country": "Brazil",
        "cost": "mid", "internet": "good", "beach": True,
        "climate": "subtropical", "vibe": ["beach", "surf", "chill", "social"],
        "safety": "medium", "english": "poor", "visa_ease": "easy",
        "timezone": "UTC-3", "crowded": "medium",
        "cons": ["language barrier", "safety concerns", "expensive for Brazil"],
    },
    {
        "name": "Da Nang", "country": "Vietnam",
        "cost": "budget", "internet": "good", "beach": True,
        "climate": "tropical", "vibe": ["chill", "beach", "emerging nomad hub"],
        "safety": "high", "english": "ok", "visa_ease": "medium",
        "timezone": "UTC+7", "crowded": "low",
        "cons": ["rainy season Oct–Dec", "less vibrant than Hanoi/HCMC", "language barrier"],
    },
]

# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------
SYSTEM_PROMPT_TEMPLATE = """\
You are CityScout, a precise and analytical digital nomad city recommendation engine.

CITY KNOWLEDGE BASE (30 cities):
{cities_json}

TASK:
The user describes what they are looking for in a destination. Analyze their preferences,
score all 30 cities, and return the top 3 recommendations.

SCORING RULES:
1. Extract the criteria from the user's input (e.g. cost, beach, wifi quality, vibe, safety, climate).
2. Assign a relevance weight to each criterion based on how strongly the user emphasized it.
3. Score each city 0–10 on each relevant criterion using the knowledge base.
4. Compute a weighted average score (0–10, one decimal place).
5. Return the top 3 cities by score.

OUTPUT FORMAT — STRICT:
Return ONLY a valid JSON object. No markdown. No code fences. No explanation outside the JSON.
The JSON must match this exact schema:

{{
  "query": "<the user's original query>",
  "criteria": ["<criterion1>", "<criterion2>", ...],
  "results": [
    {{
      "rank": 1,
      "city": "<city name>",
      "country": "<country>",
      "score": <float, one decimal>,
      "confidence": <integer 0–100>,
      "score_breakdown": {{
        "<criterion>": <int 0-10>,
        ...
      }},
      "why_good": "<2–3 sentences explaining why this city fits the user's needs>",
      "why_not": "<1–2 sentences on who this city is NOT ideal for>",
      "next_step": "<concrete, actionable recommendation>"
    }},
    {{ "rank": 2, ... }},
    {{ "rank": 3, ... }}
  ],
  "summary": "<3–5 sentence friendly summary of the recommendations for this user>"
}}

"confidence" (0–100): Estimate how well this city matches the user's stated intent.
  90–100: near-perfect match across all criteria.
  70–89: strong match with minor trade-offs.
  50–69: partial match, notable gaps.
  Below 50: weak match, only if no better option.
  Vague queries → lower confidence even for good matches.

"next_step": A concrete action the user should take.
  Must be specific (not "consider visiting").
  Include a time frame if possible (e.g. "1 month stay").
  Include a neighborhood or area hint if relevant.
  Must be practical and immediately actionable.

IMPORTANT: Output only the JSON object. Nothing before it, nothing after it.
"""


def build_system_prompt() -> str:
    cities_json = json.dumps(CITIES, ensure_ascii=False, indent=2)
    return SYSTEM_PROMPT_TEMPLATE.format(cities_json=cities_json)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def normalize_query(text: str) -> str:
    return text.strip()


def parse_response(raw: str) -> dict:
    """Strip markdown fences, parse JSON, validate structure."""
    cleaned = raw.strip()

    # Remove ```json ... ``` or ``` ... ``` fences
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    cleaned = cleaned.strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"Error: Could not parse model response as JSON.\nDetails: {e}", file=sys.stderr)
        print(f"Raw response:\n{raw[:500]}", file=sys.stderr)
        sys.exit(1)

    required_keys = {"query", "results", "summary"}
    missing = required_keys - data.keys()
    if missing:
        print(f"Error: Model response is missing required keys: {missing}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(data["results"], list) or len(data["results"]) == 0:
        print("Error: Model response contains no results.", file=sys.stderr)
        sys.exit(1)

    for result in data["results"]:
        if "confidence" not in result:
            print("Error: result missing 'confidence' field.", file=sys.stderr)
            sys.exit(1)
        if not isinstance(result["confidence"], int) or not (0 <= result["confidence"] <= 100):
            print(f"Error: 'confidence' must be an integer 0–100, got: {result.get('confidence')}", file=sys.stderr)
            sys.exit(1)
        if not result.get("next_step", "").strip():
            print("Error: result missing or empty 'next_step' field.", file=sys.stderr)
            sys.exit(1)

    return data


def query_claude(user_input: str) -> dict:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print(
            "Error: ANTHROPIC_API_KEY environment variable is not set.\n"
            "Set it with: export ANTHROPIC_API_KEY=sk-ant-...",
            file=sys.stderr,
        )
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2000,
        temperature=0.2,
        system=build_system_prompt(),
        messages=[{"role": "user", "content": user_input}],
    )

    raw = response.content[0].text
    return parse_response(raw)


# ---------------------------------------------------------------------------
# Output formatter
# ---------------------------------------------------------------------------
def format_output(data: dict, json_only: bool) -> None:
    if not json_only:
        print()
        print("=" * 60)
        print(f"  CityScout — Top 3 picks for: \"{data['query']}\"")
        print("=" * 60)

        for result in data["results"]:
            score = round(result["score"], 1)
            confidence = result.get("confidence", "?")
            print(f"\n#{result['rank']}  {result['city']}, {result['country']}  [{score}/10 | confidence: {confidence}%]")

            breakdown = result.get("score_breakdown", {})
            if breakdown:
                parts = [f"{k}: {v}" for k, v in breakdown.items()]
                print(f"    Scores: {' | '.join(parts)}")

            print(f"\n    Why good: {result['why_good']}")
            print(f"    Watch out: {result['why_not']}")
            print(f"    Next step: {result['next_step']}")

        print()
        print("-" * 60)
        print(data["summary"])
        print("-" * 60)
        print()
        print("Full JSON:")
        print()

    print(json.dumps(data, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description="CityScout — Find your next nomad city with AI reasoning.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            '  python cityscout.py "olcsó, tenger, jó wifi, nyugodt"\n'
            '  python cityscout.py --query "cheap, beach, fast wifi, quiet"\n'
            '  python cityscout.py "Europe, safe, cold" --json-only'
        ),
    )
    parser.add_argument(
        "query",
        nargs="?",
        default=None,
        help="Your preferences as a free-form string (e.g. 'cheap, beach, good wifi')",
    )
    parser.add_argument(
        "--query", "-q",
        dest="query_flag",
        default=None,
        metavar="QUERY",
        help="Alternative way to pass the query",
    )
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Print only the JSON output, no human-readable summary",
    )
    args = parser.parse_args()

    # Resolve query: positional arg takes precedence, then --query flag, then interactive
    raw_query = args.query or args.query_flag
    if not raw_query:
        try:
            raw_query = input("What are you looking for? (e.g. cheap, beach, good wifi): ")
        except (EOFError, KeyboardInterrupt):
            print("\nAborted.", file=sys.stderr)
            sys.exit(0)

    query = normalize_query(raw_query)
    if not query:
        print("Error: Please provide a search query.", file=sys.stderr)
        sys.exit(1)

    if not args.json_only:
        print("Thinking...", end="", flush=True)

    data = query_claude(query)

    if not args.json_only:
        # Clear "Thinking..." line
        print("\r" + " " * 12 + "\r", end="", flush=True)

    format_output(data, args.json_only)


if __name__ == "__main__":
    main()
