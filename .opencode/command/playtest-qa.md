---
description: Validate Roblox runtime behavior with a temporary playtest runner workflow.
agent: roblox-dev
---

Use the `roblox-agent-workflows` Playtest Runner workflow for this request:

```text
$ARGUMENTS
```

Rules:

- Check Studio state first.
- Do not interrupt an active play session unless the user asked for it or confirms.
- Use temporary test scripts only when needed and name them `__AgentTestRunner`.
- Emit clear `[AGENT_TEST]` log markers for pass/fail/done.
- Start play, collect console output, stop play, and clean up temporary test artifacts.
- Ask before tests that touch purchases, DataStores, teleports, external services, or long-running loops.

Answer in Spanish with observed pass/fail evidence, not assumptions.
