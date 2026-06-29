"""Query router: classifies user intent and determines which sources to consult."""

import re


_INTENT_PATTERNS: list[tuple[str, str, list[str]]] = [
    ("knowledge_query", "general roblox knowledge", [
        r"how\s+(to|do|does|can)",
        r"what\s+is\s+a",
        r"what\s+are\s+",
        r"explain",
        r"difference\s+between",
        r"best\s+practice",
        r"documentation",
        r"api\s+reference",
        r"how\s+does\s+\w+\s+work",
        r"what's\s+the\s+",
        r"tell\s+me\s+about",
        r"guide\s+to",
        r"example\s+of",
        r"tutorial",
    ]),
    ("project_query", "current project", [
        r"project\s*(structure|layout|tree)",
        r"show\s+(me\s+)?(the\s+)?(project|structure)",
        r"what\s+(scripts|services|modules)\s+",
        r"list\s+(scripts|services|modules|files)",
        r"index\s+(the\s+)?project",
        r"analyze\s+(the\s+)?project",
        r"scan\s+(the\s+)?project",
    ]),
    ("code_gen", "code generation", [
        r"(create|make|build|write|implement|add|generate)\s+(a\s+|an\s+|the\s+)?",
        r"code\s+(for|to|that)",
        r"need\s+(a\s+|an\s+)?(system|module|script|function)",
        r"script\s+(that|to|for)",
        r"module\s+(that|to|for)",
    ]),
    ("memory_write", "save to memory", [
        r"remember\s+",
        r"save\s+(this|that|rule|decision)",
        r"note\s+(that|this|down)",
        r"record\s+",
        r"add\s+(rule|case|note)",
        r"we\s+(use|follow|have|decided)",
    ]),
    ("memory_query", "query memory", [
        r"(rules|decisions|patterns|notes)",
        r"show\s+.*(rules|memory|notes|patterns)",
        r"list\s+.*rules",
        r"what\s+(rules|decisions|patterns|notes)",
        r"how\s+did\s+we\s+",
        r"past\s+(case|solution)",
    ]),
]


def classify(query: str) -> list[dict]:
    """Classify a user query into one or more intents with confidence."""
    query_lower = query.lower().strip()
    results = []

    for intent_name, description, patterns in _INTENT_PATTERNS:
        score = 0
        for pattern in patterns:
            matches = re.findall(pattern, query_lower)
            score += len(matches)
        if score > 0:
            results.append({
                "intent": intent_name,
                "description": description,
                "confidence": min(score / 3, 1.0),
            })

    if not results:
        results.append({
            "intent": "general",
            "description": "general query",
            "confidence": 0.5,
        })

    results.sort(key=lambda x: x["confidence"], reverse=True)
    return results


def needs_rag(intents: list[dict]) -> bool:
    return any(i["intent"] in ("knowledge_query", "code_gen", "general") for i in intents)


def needs_project(intents: list[dict]) -> bool:
    return any(i["intent"] == "project_query" for i in intents)


def needs_memory(intents: list[dict]) -> bool:
    return any(i["intent"] in ("memory_query", "memory_write") for i in intents)
