--[[
	01_Leaderstats
	Object type: Script  (a SERVER script)
	Goes in:     ServerScriptService

	Gives every player who joins two counters that show up on the
	in-game player list (the thing you see when you hold Tab):
	    Coins - the money you spend on upgrades
	    Ore   - how much unsold ore you are carrying right now
--]]

-- A "service" is one of Roblox's built-in manager objects. The Players
-- service keeps track of everyone currently in the game. GetService is
-- the safe, standard way to grab one.
local Players = game:GetService("Players")

-- Tweak these two numbers if you ever want players to start with something.
local STARTING_COINS = 0
local STARTING_ORE = 0

-- A "function" is a named block of code we can run later.
-- This one runs once for each player, and `player` is that player.
local function setupLeaderstats(player)
	-- Instance.new("Folder") creates a brand new object in the game,
	-- the same as right-clicking in the Explorer and inserting a Folder.
	-- An "Instance" is Roblox's word for any object in the game tree:
	-- parts, folders, scripts, players -- all of them are Instances.
	local leaderstats = Instance.new("Folder")

	-- The name MUST be exactly "leaderstats", all lowercase. Roblox looks
	-- for that exact name to decide what to print on the player list.
	leaderstats.Name = "leaderstats"

	-- Setting .Parent puts the object inside another object. Nothing
	-- actually exists in the game until you give it a parent.
	leaderstats.Parent = player

	-- An IntValue is a tiny object whose only job is to hold one whole
	-- number ("Int" = integer). Each IntValue inside leaderstats becomes
	-- one column on the player list.
	local coins = Instance.new("IntValue")
	coins.Name = "Coins" -- this exact text becomes the column heading
	coins.Value = STARTING_COINS
	coins.Parent = leaderstats

	local ore = Instance.new("IntValue")
	ore.Name = "Ore"
	ore.Value = STARTING_ORE
	ore.Parent = leaderstats
end

-- An "event" is something the game announces when it happens.
-- PlayerAdded fires every time somebody joins. Connect() says
-- "when that happens, run this function".
Players.PlayerAdded:Connect(setupLeaderstats)

-- Safety net: if this script somehow finishes loading a split second
-- AFTER a player joined, that player already missed the event above.
-- So we loop over anyone already here and set them up too.
for _, player in ipairs(Players:GetPlayers()) do
	setupLeaderstats(player)
end
