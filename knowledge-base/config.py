import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

DATA_DIR.mkdir(exist_ok=True)

REQUEST_DELAY = 1.0
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

DEVFORUM_BASE = "https://devforum.roblox.com"
CREATE_HUB_BASE = "https://create.roblox.com"
API_REF_BASE = "https://create.roblox.com/docs/reference/engine"

DEVFORUM_TOPICS = [
    "how-should-i-structure-a-large-robux-game",
    "what-is-the-best-way-to-store-data",
    "networking-best-practices",
    "optimization-guide-for-large-games",
]

DEVFORUM_CURATED_TOPIC_IDS = [
    1133216,  # How to properly utilize UpdateAsync
    667805,   # Save your player data with ProfileService
    1275421,  # DataStores: Beginners to Advanced
    2845439,  # DataStore Best Practices
    3127146,  # Real world building and scripting optimization
    3358345,  # The Hitchhiker's Guide to Optimization
    4378272,  # Luau Optimizations: Make Your Game Run Faster
    1997394,  # Guide to Type Checking with OOP
    2135043,  # OOP with Luau in 2023
    2070691,  # A New OOP Idiom (and why you should ditch the old one)
    1664447,  # All About Entity Component System
    2189165,  # BridgeNet2 v1.0.0
    1909935,  # BridgeNet (original)
    767594,   # A Complete Guide: How Exploits Work & How to Prevent Them
    4139321,  # Server Authority: Studio Beta Insights from Engineers
    684187,   # Best Rojo Use for Multi-Placed Game
    2959803,  # My Problem with SSA Frameworks (notably Knit)
    2511448,  # Optimization Tips on NPCs (1500 NPCs)
    4603494,  # Simulating thousands of moving NPCs
    3095489,  # Optimized A* Pathfinding
    2425597,  # Suphi's DataStore module
    2820400,  # Global matchmaking with MemoryStoreService
    3652856,  # Custom matchmaking with MemoryStore
    1731594,  # MemoryStoreService tutorial
    2707983,  # Cross-server matchmaking tutorial
    3471837,  # Is UnreliableRemoteEvent actually that fast?
    3573907,  # Packet networking library
    2917430,  # Networking libraries: Warp/FastNet2/etc.
    2443196,  # Automate place publishing with partially managed Rojo
    3494179,  # Workflow with Rojo and scripts inside tools
    838182,   # Setup Rojo fast with Git support
    2185389,  # Luau language server for external editors
    260694,   # How useful is StreamingEnabled?
    2641353,  # Your experience with StreamingEnabled
    3818624,  # EditableMesh and EditableImage improvements
    3685336,  # EditableMesh and EditableImage permissions
    2977379,  # MemoryStore HashMap beta
]

DEVFORUM_EXCLUDED_TOPIC_IDS = [
    4566806,  # Evolving Luau OSS thread includes UI framework discussion; not relevant for this agent.
]

DEVFORUM_SEARCH_QUERIES = [
    "order:likes category:scripting-support",
    "order:likes category:art-design-support",
    "order:likes category:tutorials",
    "order:likes tags:accepted",
    "roblox game architecture order:likes",
    "roblox networking best practices order:likes",
    "roblox datastore order:likes",
]

GITHUB_REPOS = [
    # Existing
    ("Sleitnick", "Knit"),
    ("dphfox", "Fusion"),
    ("evaera", "matter"),
    ("evaera", "roblox-lua-promise"),
    ("Roblox", "testez"),
    ("LPGhatguy", "luajson"),
    # New curated
    ("Sleitnick", "RbxUtil"),
    ("matter-ecs", "matter"),
    ("MadStudioRoblox", "ProfileStore"),
    ("Roblox", "jest-roblox"),
    ("ffrostfall", "BridgeNet2"),
    ("ffrostfall", "ByteNet"),
    ("1Axen", "blink"),
    ("howmanysmall", "Janitor"),
    ("evaera", "Cmdr"),
    ("Quenty", "NevermoreEngine"),
    ("Roblox", "tarmac"),
    ("Roblox", "place-ci-cd-demo"),
    ("Roblox", "studio-rust-mcp-server"),
    # Tooling / file formats / language infrastructure
    ("rojo-rbx", "rojo"),
    ("rojo-rbx", "rbx-dom"),
    ("UpliftGames", "wally"),
    ("lpghatguy", "aftman"),
    ("lune-org", "lune"),
    ("Kampfkarren", "selene"),
    ("JohnnyMorganz", "StyLua"),
    ("seaofvoices", "darklua"),
    ("rojo-rbx", "remodel"),
    ("Anaminus", "rbxmk"),
    ("luau-lang", "luau"),
    ("JohnnyMorganz", "luau-lsp"),
    ("roblox-ts", "roblox-ts"),
    ("roblox-ts", "vscode-roblox-ts"),
    ("Roblox", "chalk-lua"),
    ("Roblox", "signals"),
    ("littensy", "charm"),
    ("littensy", "remo"),
    ("red-blox", "zap"),
    ("csqrl", "sift"),
    ("Sleitnick", "Component"),
    ("Sleitnick", "Loader"),
    ("Sleitnick", "Option"),
    ("Sleitnick", "RbxCameraShaker"),
    ("Sleitnick", "AeroGameFramework"),
    ("osyrisrblx", "rbxts-build"),
    ("christopher-buss", "roblox-ts-project-template"),
    ("grilme99", "roblox-project-template"),
    ("devsarim", "roblox-project-template"),
    ("takoyakisoft", "roblox-rojo-wally-template"),
    ("dig1t", "rojo-template"),
    ("nightcycle", "roblox-benchmarks"),
    ("latte-soft", "maui"),
    ("JohnnyMorganz", "wally-package-types"),
    ("Sleitnick", "rbxcloud"),
    ("YetAnotherClown", "YetAnotherNet"),
    ("sircfenner", "png-luau"),
    ("mathtechstudio", "roblox-slang"),
    ("atomic-horizon", "order"),
    ("Stratiz", "Eden"),
    ("FxllenCode", "roxios"),
]

OFFICIAL_DOCS_EXTRA = [
    # Cloud / Open Cloud
    "/docs/cloud",
    # Luau
    "/docs/luau/type-checking",
    "/docs/luau/comments",
    # Services
    "/docs/reference/engine/classes/CollectionService",
    "/docs/scripting/attributes",
    "/docs/cloud-services/memory-stores",
    "/docs/cloud-services/memory-stores/best-practices",
    "/docs/cloud-services/memory-stores/sorted-map",
    "/docs/cloud-services/memory-stores/hash-map",
    "/docs/cloud-services/memory-stores/per-partition-limits",
    # Cloud reference
    "/docs/cloud/reference/patterns",
    "/docs/cloud/auth/api-keys",
    "/docs/cloud/reference/domains/apis",
    "/docs/cloud/webhooks/automate-right-to-erasure",
    "/docs/cloud/guides/usage-messaging",
    "/docs/cloud-services/data-stores",
    "/docs/reference/engine/classes/GlobalDataStore/UpdateAsync",
    "/docs/cloud-services/ordered-data-stores",
    "/docs/reference/engine/classes/MessagingService",
    "/docs/reference/engine/classes/TeleportService",
    "/docs/reference/engine/classes/TeleportService/TeleportAsync",
    "/docs/reference/engine/classes/PathfindingService",
    "/docs/reference/engine/classes/PhysicsService",
    "/docs/reference/engine/classes/Workspace/StreamingEnabled",
    "/docs/workspace/streaming",
    "/docs/performance-optimization/microprofiler",
    "/docs/performance-optimization/microprofiler/use-microprofiler",
    "/docs/performance-optimization/microprofiler/network",
    "/docs/studio/plugins",
    "/docs/reference/engine/classes/Plugin",
    "/docs/reference/engine/classes/ScriptEditorService",
    "/docs/reference/engine/classes/EditableMesh",
    "/docs/reference/engine/classes/EditableImage",
    "/docs/reference/engine/classes/MaterialService",
    "/docs/reference/engine/classes/TextChatService",
    "/docs/reference/engine/classes/VoiceChatService",
    "/docs/reference/engine/classes/PolicyService",
    "/docs/reference/engine/classes/MarketplaceService",
    "/docs/release-notes",
    "/docs/release-notes/release-notes-711",
    "/docs/release-notes/release-notes-712",
]

GITHUB_REPOS = list(dict.fromkeys(GITHUB_REPOS))
DEVFORUM_CURATED_TOPIC_IDS = list(dict.fromkeys(DEVFORUM_CURATED_TOPIC_IDS))
DEVFORUM_EXCLUDED_TOPIC_IDS = set(DEVFORUM_EXCLUDED_TOPIC_IDS)
OFFICIAL_DOCS_EXTRA = list(dict.fromkeys(OFFICIAL_DOCS_EXTRA))

WEB_RESOURCES = [
    ("https://luau.org/types/", "Luau types", "Luau type system"),
    ("https://luau-lang.org/typecheck", "Luau typecheck", "Luau type checking config"),
    ("https://sleitnick.github.io/Knit/", "Knit docs", "Framework docs"),
    ("https://sleitnick.github.io/RbxUtil/", "RbxUtil docs", "Utility framework docs"),
    ("https://elttob.uk/Fusion/0.3/", "Fusion docs", "Reactive UI framework docs"),
    ("https://eryn.io/matter/docs/intro/", "Matter docs", "ECS framework docs"),
    ("https://madstudioroblox.github.io/ProfileStore/", "ProfileStore docs", "DataStore session locking docs"),
    ("https://madstudioroblox.github.io/ProfileService/", "ProfileService docs", "Legacy data profile docs"),
    ("https://ffrostflame.github.io/BridgeNet2/", "BridgeNet2 docs", "Networking framework docs"),
    ("https://data-oriented-house.github.io/ByteNet/", "ByteNet docs", "Buffer networking docs"),
    ("https://1axen.github.io/blink/", "Blink docs", "Networking IDL docs"),
    ("https://eryn.io/roblox-lua-promise/", "Promise docs", "Async Promise docs"),
    ("https://sleitnick.github.io/RbxUtil/api/Trove/", "Trove docs", "Resource cleanup docs"),
    ("https://howmanysmall.github.io/Janitor/", "Janitor docs", "Resource cleanup docs"),
    ("https://sleitnick.github.io/RbxUtil/api/Signal/", "Signal docs", "Signal utility docs"),
    ("https://eryn.io/Cmdr/", "Cmdr docs", "Command framework docs"),
    ("https://quenty.github.io/NevermoreEngine/", "NevermoreEngine docs", "Large framework docs"),
    ("https://lune-org.github.io/docs/", "Lune docs", "Standalone Luau runtime docs"),
    ("https://rojo.space/docs/", "Rojo docs", "Rojo project tooling docs"),
    ("https://rojo.space/docs/v7/project-format/", "Rojo project format", "default.project.json docs"),
    ("https://rojo.space/docs/v7/sourcemap/", "Rojo sourcemap", "Sourcemap docs"),
    ("https://wally.run/", "Wally docs", "Package manager docs"),
    ("https://wally.run/package-format/", "Wally package format", "wally.toml docs"),
    ("https://kampfkarren.github.io/selene/", "Selene docs", "Linter docs"),
    ("https://kampfkarren.github.io/selene/usage/configuration.html", "Selene config", "selene.toml docs"),
    ("https://stylua.com/", "StyLua docs", "Formatter docs"),
    ("https://stylua.com/configuration/", "StyLua config", "stylua.toml docs"),
    ("https://darklua.com/", "Darklua docs", "Luau build tooling docs"),
    ("https://darklua.com/docs/configuration/", "Darklua config", "darklua.json docs"),
    ("https://dom.rojo.space/", "rbx-dom docs", "Roblox file format docs"),
    ("https://github.com/rojo-rbx/rbx-dom/blob/master/docs/binary.md", ".rbxm/.rbxl binary", "Roblox binary format"),
    ("https://github.com/rojo-rbx/rbx-dom/blob/master/docs/xml.md", ".rbxmx/.rbxlx XML", "Roblox XML format"),
    ("https://github.com/lpghatguy/aftman#configuration", "Aftman config", "aftman.toml docs"),
    ("https://roblox-ts.com/docs/", "roblox-ts docs", "TypeScript to Luau docs"),
    ("https://luau.org/news/2024-07-23-luau-recap-july-2024/", "Luau July 2024 recap", "Luau release notes"),
    ("https://devforum.roblox.com/c/updates/release-notes/62", "DevForum release notes", "Roblox release notes category"),
    ("https://devforum.roblox.com/c/updates/45", "Roblox updates", "Platform updates category"),
    ("https://medium.com/@sleitnick/knit-its-history-and-how-to-build-it-better-3100da97b36", "Knit architecture", "Framework tradeoff article"),
]

# New GitHub repos discovered; maintained separately for tracking
GITHUB_REPOS_NEWLY_ADDED = [
    "Sleitnick/RbxUtil",
    "matter-ecs/matter",
    "MadStudioRoblox/ProfileStore",
    "Roblox/jest-roblox",
    "ffrostfall/BridgeNet2",
    "ffrostfall/ByteNet",
    "1Axen/blink",
    "howmanysmall/Janitor",
    "evaera/Cmdr",
    "Quenty/NevermoreEngine",
    "Roblox/tarmac",
    "Roblox/place-ci-cd-demo",
    "Roblox/studio-rust-mcp-server",
]
