"""Query router: classifies user intent and determines which sources to consult."""

import re


_INTENT_PATTERNS: list[tuple[str, str, list[str]]] = [
    ("knowledge_query", "general roblox knowledge", [
        r"how\s+(to|do|does|can)",
        r"c[oó]mo\s+(hacer|funciona|puedo|se)",
        r"what\s+is\s+a",
        r"qu[eé]\s+es\s+",
        r"what\s+are\s+",
        r"cu[aá]les\s+son\s+",
        r"explain",
        r"explica",
        r"difference\s+between",
        r"diferencia\s+entre",
        r"best\s+practice",
        r"mejor(es)?\s+pr[aá]ctica(s)?",
        r"documentation",
        r"documentaci[oó]n",
        r"api\s+reference",
        r"how\s+does\s+\w+\s+work",
        r"what's\s+the\s+",
        r"tell\s+me\s+about",
        r"guide\s+to",
        r"gu[ií]a\s+(de|para)",
        r"example\s+of",
        r"ejemplo\s+(de|para)",
        r"tutorial",
    ]),
    ("project_query", "current project", [
        r"project\s*(structure|layout|tree)",
        r"estructura\s+del\s+proyecto",
        r"show\s+(me\s+)?(the\s+)?(project|structure)",
        r"what\s+(scripts|services|modules)\s+",
        r"qu[eé]\s+(scripts|servicios|m[oó]dulos)\s+",
        r"list\s+(scripts|services|modules|files)",
        r"listar\s+(scripts|servicios|m[oó]dulos|archivos)",
        r"index\s+(the\s+)?project",
        r"analyze\s+(the\s+)?project",
        r"analiza(r)?\s+(el\s+)?proyecto",
        r"scan\s+(the\s+)?project",
        r"escanea(r)?\s+(el\s+)?proyecto",
    ]),
    ("code_gen", "code generation", [
        r"(create|make|build|write|implement|add|generate)\s+(a\s+|an\s+|the\s+)?",
        r"(crea(r)?|hacer|haz|constru(ir|ye)|escrib(e|ir)|implementa(r)?|agrega(r)?|genera(r)?)\s+",
        r"code\s+(for|to|that)",
        r"c[oó]digo\s+(para|que)",
        r"need\s+(a\s+|an\s+)?(system|module|script|function)",
        r"necesito\s+(un\s+|una\s+)?(sistema|m[oó]dulo|script|funci[oó]n)",
        r"script\s+(that|to|for)",
        r"script\s+(que|para)",
        r"module\s+(that|to|for)",
        r"m[oó]dulo\s+(que|para)",
    ]),
    ("memory_write", "save to memory", [
        r"remember\s+",
        r"recuerda\s+",
        r"save\s+(this|that|rule|decision)",
        r"guarda\s+(esto|eso|regla|decisi[oó]n)",
        r"note\s+(that|this|down)",
        r"anota\s+(que|esto)",
        r"record\s+",
        r"add\s+(rule|case|note)",
        r"agrega\s+(regla|caso|nota)",
        r"we\s+(use|follow|have|decided)",
        r"(usamos|seguimos|decidimos)\s+",
    ]),
    ("memory_query", "query memory", [
        r"(rules|decisions|patterns|notes)",
        r"(reglas|decisiones|patrones|notas)",
        r"show\s+.*(rules|memory|notes|patterns)",
        r"muestra\s+.*(reglas|memoria|notas|patrones)",
        r"list\s+.*rules",
        r"lista\s+.*reglas",
        r"what\s+(rules|decisions|patterns|notes)",
        r"qu[eé]\s+(reglas|decisiones|patrones|notas)",
        r"how\s+did\s+we\s+",
        r"c[oó]mo\s+(lo\s+)?hicimos\s+",
        r"past\s+(case|solution)",
        r"caso\s+pasado|soluci[oó]n\s+pasada",
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
