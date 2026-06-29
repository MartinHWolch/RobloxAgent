---
name: roblox-agent-rag
description: Use when working on Roblox, Luau, DataStore, RemoteEvent, Studio MCP, or Roblox architecture tasks; instructs OpenCode to consult the local Roblox RAG knowledge base.
---

# Roblox Agent RAG

This workspace contains a local Roblox knowledge base and RAG index. Use it before answering Roblox technical questions.

## Local Tools

Query Roblox knowledge:

```bash
python -m rag query "<query>" --score -k 8
```

Check indexed chunk count:

```bash
python -m rag stats
```

Use the orchestrator only for standalone smoke tests. Inside OpenCode, prefer querying `rag` directly and let OpenCode's model produce the answer.

## Guidance

- Answer in Spanish by default.
- Use Luau with `--!strict` for new scripts/modules.
- Prefer ProfileStore for new player persistence.
- Validate RemoteEvents on the server and design server-authoritative gameplay.
- Avoid React Luau, Roact, Rodux, and Reflex unless the user explicitly asks for them.
- If Roblox Studio MCP tools are available, use them for all live Studio inspection/modification.
- Cite RAG sources in final answers when giving technical recommendations.
