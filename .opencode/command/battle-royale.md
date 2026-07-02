---
description: Build or review battle royale systems using genre patterns without adding unrequested systems.
agent: roblox-dev
---

Use `roblox-agent-audits` genre template guidance for a battle royale request:

```text
$ARGUMENTS
```

Rules:

- Treat battle royale patterns as optional context: match lifecycle, spawn/loot, storm, eliminations, spectating.
- Implement only what the user asked for.
- Do not add matchmaking, loot tables, storm, monetization, ranking, or spectating unless requested.
- Ask if match size, team mode, or lifecycle state is unclear.
- Verify before/after if Studio is modified.

Answer in Spanish.
