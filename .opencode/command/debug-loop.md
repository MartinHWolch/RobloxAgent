---
description: Diagnose and fix Roblox errors with a bounded iterative debug loop.
agent: roblox-dev
---

Use the `roblox-agent-audits` Debug Loop workflow for this request:

```text
$ARGUMENTS
```

Rules:

- Capture exact error text, stack trace, script path, line number, and client/server origin.
- Read relevant code before proposing a fix.
- Apply the smallest plausible fix.
- Verify with logs or playtest.
- Stop after 5 unsuccessful iterations and report hypotheses, attempts, and next steps.

Answer in Spanish with evidence from logs or readback.
