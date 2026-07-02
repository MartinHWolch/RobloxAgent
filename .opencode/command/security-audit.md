---
description: Audit Roblox remotes, client trust, data exposure, and server-authoritative security.
agent: roblox-dev
---

Use the `roblox-agent-audits` Security Audit workflow for this request:

```text
$ARGUMENTS
```

Rules:

- Inspect before changing anything.
- Build an inventory of RemoteEvents/RemoteFunctions and relevant handlers.
- Report missing type checks, range checks, authorization, ownership checks, cooldowns, and sensitive replicated data.
- Sort findings by Critical, High, Medium, Low.
- Do not apply broad fixes unless the user confirms.

Answer in Spanish with concrete paths/lines when available.
