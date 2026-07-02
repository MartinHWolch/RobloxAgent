---
description: Build or review a simulator using genre patterns without adding unrequested systems.
agent: roblox-dev
---

Use `roblox-agent-audits` genre template guidance for a simulator request:

```text
$ARGUMENTS
```

Rules:

- Treat simulator patterns as optional context: collection loop, upgrades, zones, pets, rebirth.
- Implement only what the user asked for.
- Do not add pets, eggs, rebirth, boosts, GamePasses, shops, or currencies unless requested.
- Ask if the core loop or progression resource is unclear.
- Verify before/after if Studio is modified.

Answer in Spanish.
