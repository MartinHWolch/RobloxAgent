---
description: Audit Roblox performance across scripts, memory, networking, parts, and mobile readiness.
agent: roblox-dev
---

Use the `roblox-agent-audits` Performance Audit workflow for this request:

```text
$ARGUMENTS
```

Rules:

- Inspect scripts and scene state before recommending fixes.
- Check deprecated APIs, hot loops, event cleanup, Heartbeat abuse, remote frequency, part count, unanchored static parts, and mobile risks.
- Report findings by severity before applying changes.
- Apply only safe, requested mechanical fixes automatically.
- Ask before architectural rewrites or broad scene changes.

Answer in Spanish with before/after verification if changes are made.
