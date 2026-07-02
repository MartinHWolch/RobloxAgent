---
name: roblox-agent-workflows
description: Use when doing Roblox Studio UI QA, playtest validation, spatial checks, spawn/collision placement, or before/after verification with the existing Roblox Studio MCP tools.
---

# Roblox Agent Workflows

Use this skill to make the agent more reliable when it works inside Roblox Studio. These workflows are internal guardrails for the current project; they do not require WEPPY or any external MCP.

## Core Rules

- Do only what the user asked. Do not add extra features, systems, assets, screens, effects, or refactors unless explicitly requested.
- If the request is ambiguous, ask one short clarifying question before making changes.
- Before mutating Studio, inspect the target object or service first.
- After mutating Studio, verify the result with readback, logs, screenshot, or playtest depending on the task.
- Never invent Roblox asset IDs. Use user-provided IDs or explicit accepted results from `Roblox_Studio_search_asset`.
- Prefer purpose-built Roblox Studio MCP tools over arbitrary Luau. Use `Roblox_Studio_execute_luau` only for checks or actions not covered by existing tools.
- Do not leave temporary test instances or scripts behind.

## Before/After Verification

Use for any Studio mutation that touches scripts, UI, scene objects, lighting, terrain, assets, or gameplay state.

1. Identify the smallest affected scope.
2. Capture a before state:
   - Hierarchy: `Roblox_Studio_search_game_tree` or `Roblox_Studio_inspect_instance`.
   - Scripts: `Roblox_Studio_script_read`.
   - UI/scene visuals: `Roblox_Studio_screen_capture` when visual validation matters.
   - Logs: `Roblox_Studio_get_console_output` when debugging runtime behavior.
3. Apply the minimal requested change.
4. Verify the after state:
   - Read back changed instances/properties/scripts.
   - Check console output for errors if scripts or runtime behavior changed.
   - Capture UI/scene if appearance changed.
5. Final answer should state what changed and how it was verified.

Ask before proceeding if the target scope is unclear, if multiple Studio instances are open, or if a destructive action could affect unrelated content.

## UI QA Workflow

Use when creating, modifying, reviewing, or debugging Roblox UI under `StarterGui`, `PlayerGui`, or any `ScreenGui`.

1. Clarify missing intent before building:
   - Purpose of the UI.
   - Target screen/state.
   - Primary device class: desktop, mobile, console, or all.
   - Visual direction if identity-defining.
2. Inspect existing UI first with `Roblox_Studio_search_game_tree` and `Roblox_Studio_inspect_instance`.
3. For layout edits, prefer native Roblox UI objects and constraints:
   - `ScreenGui`, `Frame`, `TextLabel`, `TextButton`, `ImageLabel`, `ImageButton`, `ScrollingFrame`.
   - `UIListLayout`, `UIGridLayout`, `UIPadding`, `UICorner`, `UIStroke`, `UIAspectRatioConstraint`, `UISizeConstraint`, `UITextSizeConstraint`, `UIScale`.
4. Validate UI quality:
   - Touch targets should be at least 44 px for mobile-facing controls.
   - Text must be readable at target resolution.
   - Avoid relying only on `TextScaled`; prefer explicit sizes plus constraints when possible.
   - Respect safe areas: `ScreenInsets`, `IgnoreGuiInset`, `ClipToDeviceSafeArea`, and related properties.
   - Do not use full-screen opaque roots unless the UI is intentionally modal.
5. Capture a screenshot after meaningful visual changes with `Roblox_Studio_screen_capture`.
6. If device-specific behavior matters, use the Roblox device simulator skill/workflow before claiming mobile/console correctness.

Do not invent images, icons, fonts, brand styles, or asset IDs. Ask before using marketplace assets.

## Playtest Runner Workflow

Use when validating runtime behavior, script execution, gameplay systems, remotes, NPC behavior, spawns, or regressions.

1. Inspect current Studio state with `Roblox_Studio_get_studio_state`.
2. If already playing, do not interrupt unless the user asked for it or confirms.
3. Create a temporary test script only when needed:
   - Name it `__AgentTestRunner`.
   - Parent it under `game.ServerScriptService` for server tests, or an appropriate client context for client tests.
   - Emit clear log markers such as `[AGENT_TEST] PASS`, `[AGENT_TEST] FAIL`, and `[AGENT_TEST] DONE`.
4. Start play with `Roblox_Studio_start_stop_play({ is_start = true })`.
5. Wait briefly or interact if required.
6. Read logs with `Roblox_Studio_get_console_output`.
7. Stop play with `Roblox_Studio_start_stop_play({ is_start = false })`.
8. Delete temporary test instances/scripts in Edit mode.
9. Report pass/fail based on observed logs, not assumptions.

Ask before running tests that may trigger purchases, datastores, teleports, external services, economy changes, or long-running gameplay loops.

## Spatial QA Workflow

Use when placing objects, spawn points, NPC targets, obstacles, terrain features, or checking collision/walkability.

Prefer read-only Luau queries through `Roblox_Studio_execute_luau` when there is no purpose-built MCP tool.

Common checks:

- Ground below point: use `Workspace:Raycast(origin, direction, params)`.
- Bounds: use `Model:GetBoundingBox()` or part `CFrame`/`Size`.
- Collision: use `Workspace:GetPartBoundsInBox(cframe, size, overlapParams)`.
- Spawn clearance: combine ground raycast, collision box, and vertical clearance.
- Walkability: sample a grid with downward raycasts and reject steep or blocked points.

Rules:

- Never place objects based only on guessed coordinates when the scene can be inspected.
- For requested spawn/placement work, check ground support and collision before final placement.
- For NPC/pathing work, verify target positions are reachable or at least physically plausible.
- If scene scale or coordinate system is unclear, ask before changing placement.

## Suggested Read-Only Luau Patterns

Ground check:

```lua
local Workspace = game:GetService("Workspace")
local origin = Vector3.new(X, Y, Z)
local result = Workspace:Raycast(origin, Vector3.new(0, -500, 0))
if result then
    return {
        hit = true,
        position = result.Position,
        normal = result.Normal,
        material = tostring(result.Material),
        instance = result.Instance:GetFullName(),
    }
end
return { hit = false }
```

Collision box check:

```lua
local Workspace = game:GetService("Workspace")
local parts = Workspace:GetPartBoundsInBox(CFrame.new(X, Y, Z), Vector3.new(SX, SY, SZ))
local hits = {}
for _, part in parts do
    table.insert(hits, part:GetFullName())
end
return hits
```

Bounding box check:

```lua
local target = game.Workspace:FindFirstChild("NAME", true)
if target and target:IsA("Model") then
    local cf, size = target:GetBoundingBox()
    return { cframe = tostring(cf), size = size }
elseif target and target:IsA("BasePart") then
    return { cframe = tostring(target.CFrame), size = target.Size }
end
return nil
```

Replace placeholders only from inspected scene data or user-provided values. If a placeholder cannot be determined confidently, ask.
