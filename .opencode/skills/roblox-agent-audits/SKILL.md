---
name: roblox-agent-audits
description: Use for Roblox security audits, performance audits, debug loops, code reviews, publish checklists, monetization reviews, sharp-edge checks, or genre-specific game template guidance.
---

# Roblox Agent Audits

Use this skill for structured Roblox reviews and genre guidance. These workflows are project-native and based on reviewed Roblox skill patterns, adapted to our rules: do not invent scope, ask when unsure, and verify work.

## Global Rules

- Do not implement extra systems just because a checklist mentions them.
- Ask one concise clarifying question if the audit scope, genre scope, target scripts, or risk tolerance is unclear.
- Default to reporting findings first. Apply fixes only when the user asked for implementation or the fix is small and clearly within scope.
- For risky areas, ask before changing DataStores, MarketplaceService, TeleportService, Open Cloud, destructive deletes, purchases, or monetization logic.
- Use exact script paths and line references when available.
- Order findings by severity: Critical, High, Medium, Low.

## Security Audit

Use for remotes, exploit prevention, server authority, data exposure, anti-cheat, inventory, currency, trading, combat, or admin systems.

Checklist:

- Inventory RemoteEvents and RemoteFunctions.
- Search for `OnServerEvent`, `OnServerInvoke`, `FireServer`, `InvokeServer`, `FireClient`, `FireAllClients`.
- For every server handler, check type validation, range validation, ownership/authorization, cooldown/rate limit, and payload size limits.
- Check that the client sends intent, not authoritative results like currency totals, damage values, inventory grants, or purchase success.
- Check replicated containers for sensitive data: `ReplicatedStorage`, `Workspace`, `StarterPlayer`, `StarterGui`, attributes, value objects, and shared modules.
- Flag RemoteFunctions that can block or be spammed.
- Re-verify after fixes by rescanning modified handlers.

Security report format:

```text
Critical:
- path:line - issue - exploit impact - fix

High:
- path:line - issue - impact - fix

Medium:
- path:line - issue - fix

Low:
- path:line - issue - suggestion

Summary:
- remotes audited
- remotes missing validation
- client-trusted logic found
- data exposure findings
- rate-limit gaps
```

## Performance Audit

Use for lag, FPS drops, mobile optimization, memory growth, networking load, large maps, or pre-release optimization.

Script checks:

- Deprecated APIs: `wait`, `spawn`, `delay`.
- `RunService.Heartbeat`, `RenderStepped`, `Stepped` abuse.
- Tight loops, especially `while true do` without controlled yielding.
- `Instance.new` in loops or hot paths.
- `game:GetService` repeatedly inside functions or loops.
- Deep `FindFirstChild`/`WaitForChild` chains in hot paths.
- String concatenation in loops.
- `:Connect(` without stored cleanup path.
- Tables that grow without pruning.

Scene checks:

- Total `BasePart` count and unanchored static parts.
- `StreamingEnabled` for large maps.
- Transparent colliders and unnecessary renderable objects.
- Mesh/union complexity when inspectable.

Network checks:

- Remotes fired inside frame loops.
- Large tables or full state replication.
- `FireAllClients` where `FireClient` would be enough.
- Frequently changing replicated attributes.

Only apply safe mechanical fixes automatically when requested, such as `wait` to `task.wait`. Architectural fixes require confirmation.

## Debug Loop

Use for runtime errors, failing behavior, console warnings, broken scripts, or regressions.

Flow:

1. Capture exact error text, stack trace, script path, line number, and client/server origin.
2. Read the implicated script and related modules/remotes.
3. Categorize root cause: syntax, runtime nil/type issue, logic error, security issue, or performance issue.
4. Apply the smallest plausible fix.
5. Run playtest or targeted verification.
6. Read logs and compare against the original error.
7. Repeat at most 5 iterations.

If unresolved after 5 iterations, stop and report hypotheses, attempts, observed results, and next diagnostic steps.

## Code Review

Use when the user asks for a review, architecture review, quality check, or maintainability review.

Review dimensions:

- Organization: script placement, folder structure, naming consistency.
- Code quality: deprecated APIs, globals, type clarity, magic numbers, duplicate code.
- Architecture: module boundaries, dependency direction, circular requires, event flow.
- Security quick-check: remotes, client trust, sensitive data exposure.
- Performance quick-check: hot loops, connections, memory cleanup, remote frequency.

Grade only when useful: A, B, C, D, F. Findings remain more important than the grade.

## Publish Checklist

Use before public release or major updates.

Categories:

- Data: save/load, session locking, `BindToClose`, retry/error handling, data versioning, budgets.
- Security: validated remotes, rate limits, server authority, no sensitive replicated data.
- Performance: mobile FPS target, part count, cleanup, StreamingEnabled, network load.
- Monetization: GamePasses, Developer Products, ProcessReceipt, Premium benefits, policy checks.
- Mobile: touch controls, readable text, safe areas, tap targets, performance.
- Gameplay: core loop, FTUE, progression, respawn, edge cases, multiplayer behavior.
- Metadata: icon, thumbnails, description, genre, max players, allowed devices, age rating.
- Social/analytics: chat filtering, moderation, key events, error logging.

Report blockers first. Do not mark unknown items as passed.

## Monetization Audit

Use for GamePasses, Developer Products, Premium, ads, shop UX, pricing, or ethical monetization.

Technical checks:

- `MarketplaceService` usage.
- `PromptGamePassPurchase`, `PromptProductPurchase`, `UserOwnsGamePassAsync`.
- Exactly one `MarketplaceService.ProcessReceipt` assignment.
- ProcessReceipt idempotency and unknown ProductId handling.
- Grant before acknowledging purchase.
- Persist grant before returning `PurchaseGranted` when possible.
- Handle player leaving before receipt processing.
- Server-authoritative granting only.

Ethical checks:

- Free players can enjoy the core loop.
- Purchase prompts do not interrupt critical gameplay.
- Avoid pay-to-win advantages in competitive contexts unless explicitly intended and disclosed.
- Avoid hidden odds, pressure tactics, artificial friction, and currency obfuscation.

Never invent GamePass IDs, Product IDs, prices, or sales claims. Ask for missing IDs/benefits.

## Sharp Edges To Remember

- Player data needs session safety; prefer ProfileStore/ProfileService for production persistence.
- Never let the client own currency, damage, inventory, purchases, or progression decisions.
- ProcessReceipt bugs can duplicate grants or charge players without rewards.
- Store and clean up `RBXScriptConnection`s.
- Rate-limit remotes per player and per action.
- `BindToClose` has a limited shutdown window.
- High part count and unanchored static parts hurt mobile performance.
- Be careful yielding during module initialization.
- Do not use `#table` when nil gaps matter.
- Replace `wait`, `spawn`, and `delay` with `task.wait`, `task.spawn`, and `task.delay`.
- Avoid infinite yield from unchecked `WaitForChild`; use timeouts when appropriate.
- Luau string patterns are not regex.

## Genre Templates Are Optional Context

Use genre templates only when the user explicitly asks for or describes a genre such as simulator, tycoon, obby, RPG, horror, or battle royale.

Rules:

- Genre templates are checklists of common patterns, not required features.
- Implement only the features the user asked for.
- If the user says "obby de backrooms con linterna y puertas falsas", do not add shop, skip-stage, GamePasses, pets, coins, leaderboards, or extra progression unless asked.
- Ask before adding monetization, external assets, inventory, shops, leaderboards, combat, pets, rebirth, quests, or analytics.
- If a core genre decision is missing and blocks implementation, ask one concise question.

Genre cues:

- Obby: stages, checkpoints, hazards, timers, respawn, movement challenge.
- Tycoon: plot claiming, droppers, collectors, buttons, income, upgrades.
- Simulator: collection loop, upgrades, zones, pets/companions, rebirth only if requested.
- RPG: stats, quests, NPCs, combat, inventory, zones.
- Horror: atmosphere, lighting, sound, monster AI, chase/avoidance, scripted events.
- Battle royale: match lifecycle, spawn/loot, storm/zone, eliminations, spectating.
