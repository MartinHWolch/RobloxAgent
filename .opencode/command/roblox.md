---
description: Ask the local Roblox RAG-augmented OpenCode agent for Roblox/Luau help.
agent: roblox-dev
---

Use the `roblox-dev` workflow for this request:

```text
$ARGUMENTS
```

Before answering, query the local Roblox RAG knowledge base with the request and any relevant English Roblox keywords:

```bash
python -m rag query "$ARGUMENTS" --score -k 8
```

If this is about the current Roblox project structure, also run:

```bash
python -m project-indexer .
```

If Roblox Studio MCP tools are available and the request refers to the open Studio place, use the MCP connection to inspect or modify Studio state.

Answer in Spanish, cite the relevant RAG sources, avoid React Luau/Roact/Rodux/Reflex, and provide practical Luau/Rojo guidance.
