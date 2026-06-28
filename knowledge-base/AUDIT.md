{
  "audit": "2026-06-28",
  "total_items": 223,
  "sources": {
    "engine_api": {
      "count": 43,
      "utility": "HIGH",
      "verdict": "Contenido valioso pero crudo. El markdown tiene propiedades, métodos y eventos mezclados en texto plano. Un LLM no puede diferenciar fácilmente 'Instance.Archivable' de 'Instance.Clone()' sin parsear.",
      "issues": [
        "Properties/Methods/Events están en markdown, no como datos estructurados",
        "No hay separación clara entre lo que es propiedad vs método vs evento",
        "El frontmatter es útil (type, inherits, tags) pero no se explota"
      ]
    },
    "creator_hub": {
      "count": 13,
      "utility": "MEDIUM",
      "verdict": "Guías introductorias útiles pero sin metadata de clasificación. No se distingue un tutorial de una referencia.",
      "issues": [
        "Frontmatter no se extrae correctamente (summary siempre vacío)",
        "No hay tipo (guide/tutorial/reference)",
        "Títulos en raw (scripting en vez de Scripting)"
      ]
    },
    "devforum": {
      "count": 149,
      "utility": "LOW",
      "verdict": "Demasiado ruido. 149 tópicos incluyen hiring posts, showcases, preguntas de soporte básicas. Solo ~20-30 tienen valor arquitectónico real.",
      "issues": [
        "Contenido en HTML crudo con <p>, <img>, <a> tags",
        "Búsqueda sin filtrar: incluye hiring, showcases, bug reports",
        "category_id es numérico, no human-readable",
        "No hay campo 'accepted_answer' a nivel de tópico",
        "Respuestas aceptadas no se marcan correctamente"
      ]
    },
    "github": {
      "count": 8,
      "utility": "HIGH",
      "verdict": "Bien estructurado. README es markdown limpio. Metadata completa.",
      "issues": [
        "ProfileStore repo devolvió 404 - se perdió",
        "Podría incluir dependencias y APIs expuestas"
      ]
    },
    "examples": {
      "count": 10,
      "utility": "LOW-MEDIUM",
      "verdict": "Esqueletos vacíos. Tienen categorías y best practices genéricas pero no código real ni arquitecturas concretas.",
      "issues": [
        "No hay pseudocódigo ni diagramas de arquitectura",
        "Best practices genéricas (\"Use ModuleScripts\")",
        "No hay implementaciones de referencia",
        "Los patrones son descripciones vagas"
      ]
    }
  },
  "overall_verdict": "La base de conocimiento tiene materias primas valiosas (especialmente engine API y GitHub), pero necesita una reestructuración profunda para ser consumible por un LLM de forma efectiva. El DevForum y Examples requieren trabajo significativo."
}
