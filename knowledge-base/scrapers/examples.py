import logging
from typing import Any

from .base import BaseScraper

logger = logging.getLogger(__name__)

EXAMPLE_CATEGORIES = {
    "inventory": {
        "title": "Inventory System",
        "architecture": "Client-Server with ModuleScripts",
        "key_services": ["DataStoreService", "ReplicatedStorage"],
        "description": "A server-authoritative inventory system where the server validates all item operations. Items are represented as data (tables), not physical objects. The client requests actions via RemoteEvents and the server responds with updated state.",
        "code_example": """-- Server: InventoryService
local ProfileStore = require(Path.ProfileStore)
local InventoryTemplate = {
	items = {},
	maxSlots = 20,
}

function InventoryService:AddItem(player, itemId, quantity)
	local profile = self:GetProfile(player)
	local item = Config.Items[itemId]
	if not item or not item.stackable and profile.items[itemId] then
		return false
	end
	profile.items[itemId] = (profile.items[itemId] or 0) + quantity
	return true
end

-- Client: InventoryController
local remotes = ReplicatedStorage:WaitForChild("Remotes")
local addItemRemote = remotes:WaitForChild("AddItem")

function InventoryController:RequestAddItem(itemId)
	addItemRemote:FireServer(itemId)
end

addItemRemote.OnClientEvent:Connect(function(success)
	if success then
		self:RefreshUI()
	end
end)""",
        "best_practices": [
            "Store inventory as flat data (itemId -> quantity), not as Instance objects",
            "Always validate on server before committing to DataStore",
            "Use ProfileStore pattern for auto-save and bindToClose",
            "Cache inventory in memory, write to DataStore on changes and on player leave",
        ],
    },
    "combat": {
        "title": "Combat & NPC AI",
        "architecture": "Server-authoritative with state machines",
        "key_services": ["PathfindingService", "TweenService", "ReplicatedStorage"],
        "description": "NPCs run as state machines on the server. The server owns all hit detection (raycasts) and damage calculation. Clients receive visual-only updates. Use ComputeThickness for precise raycasts against complex geometry.",
        "code_example": """-- NPC State Machine
local NPC = {}
NPC.__index = NPC

function NPC.new(humanoid)
	local self = setmetatable({}, NPC)
	self.humanoid = humanoid
	self.state = "idle"
	self.attackRange = 10
	return self
end

function NPC:Update(dt)
	if self.state == "idle" then
		local target = self:FindNearestPlayer()
		if target then
			self.state = "chasing"
			self.target = target
		end
	elseif self.state == "chasing" then
		local dist = (self.target.Character.PrimaryPart.Position
			- self.humanoid.RootPart.Position).Magnitude
		if dist < self.attackRange then
			self.state = "attacking"
		else
			self.humanoid:MoveTo(self.target.Character.PrimaryPart.Position)
		end
	elseif self.state == "attacking" then
		if self:CanAttack() then
			self:PerformRaycast()
		end
	end
end""",
        "best_practices": [
            "Use PathfindingService with RVP (Roblox Velocity Predictor) for smooth NPC movement",
            "Server-authoritative damage: client sends intent, server validates and applies",
            "Use ComputeThickness for accurate raycasts against character hitboxes",
            "Pool NPCs instead of creating/destroying; disable and reposition",
        ],
    },
    "quests": {
        "title": "Quest System",
        "architecture": "Task-based objectives with event-driven progression",
        "key_services": ["DataStoreService", "ReplicatedStorage"],
        "description": "Quests are composed of objectives that listen for game events (kill enemy, collect item, reach location). Progress is tracked per-player in DataStore. The server broadcasts quest updates to clients via RemoteEvents.",
        "code_example": """-- Quest Objective
local QuestObjective = {}
QuestObjective.__index = QuestObjective

function QuestObjective.new(config)
	return setmetatable({
		id = config.id,
		type = config.type, -- "kill", "collect", "reach"
		required = config.required,
		current = 0,
		onProgress = config.onProgress,
	}, QuestObjective)
end

function QuestObjective:Progress(amount)
	self.current = math.min(self.current + amount, self.required)
	if self.onProgress then
		self.onProgress(self)
	end
	return self.current >= self.required
end

-- Server: QuestService
function QuestService:RegisterQuestEvents()
	CollectionService:GetInstanceAddedSignal("Enemy"):Connect(function(enemy)
		enemy.Destroying:Once(function()
			local killer = enemy:GetAttribute("lastHitter")
			if killer then
				self:ProgressQuest(killer, "kill_monsters", 1)
			end
		end)
	end)
end""",
        "best_practices": [
            "Use event-driven progress instead of polling",
            "Store quest state per-player in DataStore with ProfileStore",
            "Use BindableEvents for internal quest progression signals",
            "Support quest chains and branching via config tables, not hardcoded logic",
        ],
    },
    "economy": {
        "title": "Economy & Trading",
        "architecture": "Server-authoritative with transaction logs",
        "key_services": ["MarketplaceService", "DataStoreService", "MessagingService"],
        "description": "Dual-currency system (soft currency earned in-game, hard currency from purchases). All transactions logged for anti-exploit. Player trading uses a two-phase commit protocol to ensure consistency.",
        "code_example": """-- Server: EconomyService
function EconomyService:DeductCurrency(player, currencyType, amount)
	local profile = self:GetProfile(player)
	if profile.currencies[currencyType] < amount then
		return false, "insufficient_funds"
	end
	profile.currencies[currencyType] -= amount
	self:LogTransaction(player, currencyType, -amount)
	return true
end

-- Two-phase trade lock
function EconomyService:InitiateTrade(player1, player2, offer1, offer2)
	local lock = self:AcquireLock(player1, player2)
	if not lock then return false, "lock_failed" end

	local ok1, err1 = self:ValidateOffer(player1, offer1)
	local ok2, err2 = self:ValidateOffer(player2, offer2)
	if not ok1 or not ok2 then
		lock:Release()
		return false, err1 or err2
	end

	self:ExecuteSwap(player1, player2, offer1, offer2)
	lock:Release()
	return true
end""",
        "best_practices": [
            "Log every transaction with timestamp, playerId, amount, and reason",
            "Use two-phase commit for player trades to prevent item duplication",
            "MarketplaceService.ProcessReceipt must return Enum.ProductPurchaseDecision.PurchaseGranted",
            "Use MemoryStore for price caching and MarketplaceService for premium purchases",
        ],
    },
    "persistence": {
        "title": "Data Persistence",
        "architecture": "Profile pattern with ProfileStore",
        "key_services": ["DataStoreService", "MemoryStoreService", "MessagingService"],
        "description": "Profile-based data system using the ProfileStore pattern. Each player has a profile loaded on join and saved on leave. Auto-save every 60 seconds. Cross-server data sync via MessagingService. Use MemoryStore for temporary caches and cooldowns.",
        "code_example": """-- Server: DataService
local ProfileStore = require(Path.ProfileStore)

local template = {
	currency = 0,
	inventory = {},
	quests = {},
	settings = {},
}

local store = ProfileStore.New("PlayerData_v2", template)

function DataService:LoadProfile(player)
	local profile = store:LoadProfileAsync("Player_" .. player.UserId)
	if not profile then
		player:Kick("Failed to load data")
		return nil
	end
	profile:AddUserId(player.UserId)
	profile:Reconcile()
	profile:ListenToRelease(function()
		self:HandleProfileRelease(player, profile)
	end)
	self.activeProfiles[player] = profile
	return profile
end

game:BindToClose(function()
	for _, profile in self.activeProfiles do
		profile:Save()
	end
end)""",
        "best_practices": [
            "Use ProfileStore pattern for automatic saving and bindToClose",
            "Auto-save every 60 seconds, but always save on player leave",
            "Use MessagingService for cross-server data invalidation",
            "MemoryStore for temporary data (cooldowns, sessions) - not for permanent storage",
            "Version your data schema (e.g., PlayerData_v2) for migrations",
        ],
    },
    "multiplayer": {
        "title": "Multiplayer & Matchmaking",
        "architecture": "Teleport + MessagingService coordination",
        "key_services": ["MessagingService", "TeleportService", "MemoryStoreService"],
        "description": "Party system with invite/join flow using BindableEvents. Matchmaking with player skill rating or party-based queues. Cross-server communication via MessagingService. TeleportService moves players between game servers with preserved state.",
        "code_example": """-- Server: MatchmakingService
local queueTimeout = 60

function MatchmakingService:JoinQueue(player, mode)
	local entry = {
		playerId = player.UserId,
		mode = mode,
		skill = self:GetPlayerSkill(player),
		timestamp = os.time(),
	}
	self.queue:Add(entry)
	self:TryMatch()
end

function MatchmakingService:TryMatch()
	local byMode = {}
	for _, entry in self.queue:GetEntries() do
		byMode[entry.mode] = byMode[entry.mode] or {}
		table.insert(byMode[entry.mode], entry)
	end

	for mode, players in byMode do
		while #players >= self.modeConfig[mode].minPlayers do
			local match = {}
			for i = 1, self.modeConfig[mode].maxPlayers do
				table.insert(match, table.remove(players))
			end
			self:StartMatch(mode, match)
		end
	end
end""",
        "best_practices": [
            "Use TeleportService with TeleportData to pass player state between servers",
            "MessagingService for cross-server communication (rate limit: 100 msg/min)",
            "Validate party membership on the server, never trust client",
            "Use MemoryStore for matchmaking queues (automatic expiry)",
        ],
    },
    "ui": {
        "title": "UI Components",
        "architecture": "Component-based with Roact or Fusion",
        "key_services": ["UserInputService", "TweenService", "GuiService"],
        "description": "Complex UIs should use Roact (React Lua) for state-driven rendering. Simple UIs can use traditional event-based patterns. Use Scale and Offset together for responsive layouts. Pool UI elements to reduce garbage collection pressure.",
        "code_example": """-- Roact Inventory UI (simplified)
local Roact = require(Path.Roact)
local InventoryItem = Roact.Component:extend("InventoryItem")

function InventoryItem:render()
	return Roact.createElement("ImageButton", {
		Size = UDim2.fromOffset(64, 64),
		Position = UDim2.fromScale(self.props.index * 0.1, 0.5),
		Image = self.props.item.icon,
		[Roact.Event.Activated] = function()
			self.props.onSelect(self.props.item.id)
		end,
	}, {
		Label = Roact.createElement("TextLabel", {
			Size = UDim2.fromScale(1, 0.3),
			Position = UDim2.fromScale(0, 0.7),
			Text = self.props.item.name,
			TextScaled = true,
		})
	})
end

function InventoryUI:render()
	return Roact.createElement("ScrollingFrame", {
		Size = UDim2.fromScale(1, 1),
		CanvasSize = UDim2.fromScale(1, #self.props.items * 0.1),
	}, {
		Items = Roact.createFragment(
			table.map(self.props.items, function(item, i)
				return Roact.createElement(InventoryItem, {
					item = item,
					index = i,
					onSelect = self.props.onSelect,
				})
			end)
		),
	})
end""",
        "best_practices": [
            "Use Roact for complex UIs with many state transitions",
            "Use Scale for layout, Offset for padding/margins (responsive design)",
            "Pool UI elements instead of creating/destroying instances",
            "TweenService for smooth transitions, not while loops",
            "Use UIListLayout or UIGridLayout instead of manual position math",
        ],
    },
    "animation": {
        "title": "Animation System",
        "architecture": "AnimationController + AnimationTrack pipeline",
        "key_services": ["AnimationController", "AnimationTrack", "Humanoid"],
        "description": "Animations are loaded from ReplicatedStorage as Animation objects. Use AnimationController for programmatic animation blending. The Humanoid has built-in animation priorities (idle, walk, jump, etc.). Keyframe markers trigger callbacks for gameplay events.",
        "code_example": """-- Client: AnimationController
local player = Players.LocalPlayer
local character = player.Character or player.CharacterAdded:Wait()
local humanoid = character:WaitForChild("Humanoid")

local animController = Instance.new("AnimationController")
animController.Parent = character

-- Load animations from ReplicatedStorage
local anims = {}
for _, animObj in ipairs(Path.Animations:GetChildren()) do
	local track = animController:LoadAnimation(animObj)
	track:GetMarkerReachedSignal("Hit"):Connect(function()
		-- Called at specific frames in the animation
		self:OnHitFrame()
	end)
	anims[animObj.Name] = track
end

function AnimationService:Play(name, fadeTime)
	if self.currentTrack then
		self.currentTrack:Stop(fadeTime or 0.1)
	end
	self.currentTrack = anims[name]
	self.currentTrack:Play(fadeTime or 0.1, 1, 1)
end

-- Blend between animations
function AnimationService:BlendToIdle(fadeTime)
	anims.walk:Stop(fadeTime or 0.3)
	anims.idle:Play(fadeTime or 0.3, 1, 1)
end""",
        "best_practices": [
            "Store Animation objects in ReplicatedStorage for both client and server access",
            "Use AnimationTrack:AdjustSpeed() for dynamic animation speed",
            "Use keyframe markers for gameplay callbacks (footsteps, hit frames, etc.)",
            "Always use fadeTime for smooth transitions, never instant stops",
            "Use AnimationPriority to control which animation takes precedence",
        ],
    },
    "vehicles": {
        "title": "Vehicle System",
        "architecture": "Server-authoritative physics with client interpolation",
        "key_services": ["VehicleSeat", "Constraints", "AlignPosition", "AlignOrientation"],
        "description": "Use constraints (AlignPosition, AlignOrientation) instead of BodyMovers for stable vehicle physics. The server owns the physics simulation. Clients receive smoothed position updates. Use Attachment objects to define wheel positions and suspension points.",
        "code_example": """-- Server: VehicleController
local vehicle = script.Parent
local seat = vehicle:WaitForChild("VehicleSeat")

-- Use constraints instead of BodyMovers
local alignPos = Instance.new("AlignPosition")
alignPos.Attachment0 = vehicle.Engine.Attachment
alignPos.Responsiveness = 20
alignPos.MaxForce = 5000
alignPos.Parent = vehicle

local thrust = Instance.new("VectorForce")
thrust.Attachment0 = vehicle.Engine.Attachment
thrust.RelativeTo = Enum.ActuatorRelativeTo.Attachment0
thrust.Parent = vehicle

seat.Changed:Connect(function(prop)
	if prop == "Throttle" then
		local direction = seat.Throttle
		thrust.Force = vehicle.CFrame.LookVector * direction * 2000
	elseif prop == "Steer" then
		local steer = seat.Steer
		alignPos.Responsiveness = 20 + math.abs(steer) * 10
	end
end)""",
        "best_practices": [
            "Use Constraint-based physics (AlignPosition, AlignOrientation) not BodyMovers",
            "Server owns physics; client interpolates for smooth visuals",
            "Use Attachment objects in specific locations for suspension and wheel points",
            "Clamp Throttle and Steer values between -1 and 1",
            "Use CylindricalConstraint for wheel rotation",
        ],
    },
    "pets": {
        "title": "Pet System",
        "architecture": "NPC follower with reduced complexity",
        "key_services": ["PathfindingService", "WeldConstraint", "Humanoid"],
        "description": "Pets are simplified NPCs that follow the player. Use WeldConstraint for idle positioning (shoulder, hover). Use simple Pathfinding for following. Reduce NPC complexity (no combat AI, simplified animations, no complex state machines).",
        "code_example": """-- Server: PetService
function PetService:SpawnPet(player, petConfig)
	local pet = ReplicatedStorage.Pets[petConfig.model]:Clone()
	pet.Parent = workspace

	local humanoid = pet:WaitForChild("Humanoid")
	humanoid.WalkSpeed = petConfig.speed or 16
	humanoid.AutoRotate = true

	local follow = Instance.new("ObjectValue")
	follow.Name = "FollowTarget"
	follow.Value = player.Character
	follow.Parent = pet

	self.activePets[player] = pet
end

-- Pet follow behavior
local function updatePetFollow(pet, dt)
	local target = pet.FollowTarget.Value
	if not target or not target.PrimaryPart then return end

	local dist = (target.PrimaryPart.Position - pet.PrimaryPart.Position).Magnitude
	if dist > 8 then
		local humanoid = pet:FindFirstChildOfClass("Humanoid")
		if humanoid then
			humanoid:MoveTo(target.PrimaryPart.Position - target.PrimaryPart.CFrame.LookVector * 5)
		end
	end
end

game:GetService("RunService").Heartbeat:Connect(function(dt)
	for _, pet in self.activePets do
		updatePetFollow(pet, dt)
	end
end)""",
        "best_practices": [
            "Pets are lightweight NPCs - disable unnecessary services (combat AI, complex pathfinding)",
            "Use WeldConstraint for idle pet positioning (hover, shoulder, etc.)",
            "RunService.Heartbeat for smooth following, avoid while loops",
            "Use PathfindingService only when pet is far from player (>50 studs)",
            "Pre-load pet models in ReplicatedStorage, clone on spawn",
        ],
    },
}


class ExamplesScraper(BaseScraper):
    def scrape(self) -> list[dict[str, Any]]:
        results = []
        for key, category in EXAMPLE_CATEGORIES.items():
            results.append({
                "category": key,
                "title": category["title"],
                "architecture": category["architecture"],
                "key_services": category["key_services"],
                "description": category["description"],
                "code_example": category["code_example"],
                "best_practices": category["best_practices"],
                "source": "examples",
            })
            logger.info("Added example category: %s", key)
        return results
