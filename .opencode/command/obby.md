---
description: Build or review an obby using genre patterns without adding unrequested systems.
agent: roblox-dev
---

Use `roblox-agent-audits` genre template guidance for an obby request:

```text
$ARGUMENTS
```

Rules:

- Treat obby patterns as optional context: stages, hazards, checkpoints, respawn, timers, movement challenges.
- Implement only what the user asked for.
- Do not add shops, skip-stage, GamePasses, coins, leaderboards, pets, or analytics unless requested.
- Ask if a necessary design choice is missing.
- Verify before/after if Studio is modified.

Answer in Spanish.
