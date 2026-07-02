---
description: Check Roblox placement, ground, collisions, spawn positions, terrain, or walkability.
agent: roblox-dev
---

Use the `roblox-agent-workflows` Spatial QA workflow for this request:

```text
$ARGUMENTS
```

Rules:

- Inspect the scene before choosing coordinates.
- Prefer read-only Luau checks through existing Roblox Studio MCP tools.
- Check ground support and collision before placing or recommending spawn positions.
- Use raycasts, bounding boxes, and overlap checks as appropriate.
- Ask if scene scale, target area, or placement intent is unclear.
- Do not move, create, or delete objects unless the user explicitly asked for that action.

Answer in Spanish with the checked positions/objects and the verification result.
