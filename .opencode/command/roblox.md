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

If Roblox Studio MCP tools are available and the request refers to the open Studio place, use the MCP connection to inspect or modify Studio state.

When the request involves UI QA, playtest validation, spatial/placement checks, or before/after verification, use the `roblox-agent-workflows` skill. Do not integrate WEPPY; recreate useful workflows using only the current project tools.

Answer in Spanish, cite the relevant RAG sources, avoid React Luau/Roact/Rodux/Reflex, and provide practical Luau guidance using native Studio patterns.
