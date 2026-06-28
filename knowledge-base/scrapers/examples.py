import logging
from typing import Any

from .base import BaseScraper

logger = logging.getLogger(__name__)

EXAMPLE_CATEGORIES = {
    "inventory": {
        "title": "Inventory System",
        "patterns": [
            "Inventory system for Roblox with backend data storage",
            "Item management with categories and stacking",
            "Player inventory UI with drag and drop",
        ],
        "key_services": ["DataStoreService", "ReplicatedStorage"],
        "architecture": "Client-Server with ModuleScripts",
    },
    "combat": {
        "title": "Combat & NPC AI",
        "patterns": [
            "Turn-based or real-time combat with damage calculation",
            "NPC behavior trees and state machines",
            "Wave spawning with difficulty scaling",
        ],
        "key_services": ["PathfindingService", "ReplicatedStorage", "TweenService"],
        "architecture": "ECS or OOP with State Machines",
    },
    "quests": {
        "title": "Quest System",
        "patterns": [
            "Quest progression with objectives and rewards",
            "Quest journal UI with tracking",
            "Dynamic quest generation from templates",
        ],
        "key_services": ["DataStoreService"],
        "architecture": "Modular with task-based objectives",
    },
    "economy": {
        "title": "Economy & Trading",
        "patterns": [
            "Virtual currency systems (soft and hard currency)",
            "Player-to-player trading with validation",
            "Marketplace with dynamic pricing",
        ],
        "key_services": ["MarketplaceService", "DataStoreService"],
        "architecture": "Server-authoritative with transaction logs",
    },
    "persistence": {
        "title": "Data Persistence",
        "patterns": [
            "Profile-based data saving with auto-save",
            "Leaderboard and stat tracking",
            "Cross-server data with MessagingService",
        ],
        "key_services": ["DataStoreService", "MemoryStoreService", "MessagingService"],
        "architecture": "Profile pattern with ProfileStore",
    },
    "multiplayer": {
        "title": "Multiplayer & Matchmaking",
        "patterns": [
            "Party system with invite and join",
            "Matchmaking with skill-based or party-based queues",
            "Server teleportation between game instances",
        ],
        "key_services": ["MessagingService", "TeleportService"],
        "architecture": "Teleport + MessagingService coordination",
    },
    "ui": {
        "title": "UI Components",
        "patterns": [
            "Inventory UI with GridLayout and scrolling",
            "Shop UI with categories and buying flow",
            "Loading screen with animations and tips",
        ],
        "key_services": ["UserInputService", "TweenService"],
        "architecture": "Component-based with React Lua or Fusion",
    },
    "animation": {
        "title": "Animation System",
        "patterns": [
            "Character animation blending and layering",
            "Procedural animation with IK",
            "Animation events and keyframe callbacks",
        ],
        "key_services": ["AnimationController", "AnimationTrack"],
        "architecture": "AnimationController + AnimationTrack pipeline",
    },
    "vehicles": {
        "title": "Vehicle System",
        "patterns": [
            "Seat-based vehicle with BodyMovers",
            "Networked vehicle physics",
            "Vehicle customization and upgrades",
        ],
        "key_services": ["VehicleSeat", "BodyPosition", "BodyVelocity"],
        "architecture": "Server-authoritative physics with client interpolation",
    },
    "pets": {
        "title": "Pet System",
        "patterns": [
            "AI follower pet with idle/walk animations",
            "Pet evolution and stat growth",
            "Pet collection and gacha mechanics",
        ],
        "key_services": ["PathfindingService"],
        "architecture": "NPC clone with reduced complexity",
    },
}


class ExamplesScraper(BaseScraper):
    def scrape(self) -> list[dict[str, Any]]:
        results = []
        for key, category in EXAMPLE_CATEGORIES.items():
            results.append({
                "category": key,
                "title": category["title"],
                "patterns": category["patterns"],
                "key_services": category["key_services"],
                "architecture": category["architecture"],
                "best_practices": self._generate_best_practices(key),
                "source": "examples",
            })
            logger.info("Added example category: %s", key)
        return results

    def _generate_best_practices(self, category: str) -> list[str]:
        common = [
            "Use ModuleScripts for all logic",
            "Separate client and server concerns",
            "Validate all client requests on the server",
        ]
        specific = {
            "inventory": [
                "Store inventory data in DataStore with serialization",
                "Use RemoteEvents for inventory actions",
                "Cache inventory on player join",
            ],
            "combat": [
                "Use raycasting for hit detection",
                "Server-authoritative damage calculation",
                "Damage numbers with BillboardGui",
            ],
            "quests": [
                "Store quest progress per-player in DataStore",
                "Use BindableEvents for quest progression",
            ],
            "economy": [
                "Log all transactions for anti-exploit",
                "Use MarketPlaceService for premium purchases",
            ],
            "persistence": [
                "Auto-save every 60 seconds",
                "Use profile pattern with bindToClose",
            ],
            "multiplayer": [
                "Validate party membership on server",
                "Use TeleportService with join data",
            ],
            "ui": [
                "Use React Lua for complex UI state",
                "Pool UI elements to reduce GC pressure",
            ],
            "animation": [
                "Use AnimationBlend for smooth transitions",
                "Load animations in ReplicatedStorage",
            ],
            "vehicles": [
                "Use constraints instead of BodyMovers for stability",
                "Client-side interpolation for smooth movement",
            ],
            "pets": [
                "Use simple AI pathfinding to follow player",
                "Attach pet to player via WeldConstraint",
            ],
        }
        return common + specific.get(category, [])
