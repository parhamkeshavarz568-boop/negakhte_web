# Handoff prompt

Paste the block below into a local Claude Code session to continue building
the game there. Step 1 (leaderstats) is already written and tested in Studio;
the local session picks up at step 2.

---

I'm building my first Roblox game and I've never scripted before. I'm a
complete beginner with Luau — when you use a Roblox term (RemoteEvent,
Instance, Humanoid, etc.), explain it the first time you use it.

**The game:** a mining simulator. Core loop:
click ore to collect → backpack fills to a capacity → walk to a sell pad to
turn ore into coins → spend coins on upgrades → repeat, faster.

**Build order (7 steps):**

1. `leaderstats` — Coins and Ore counters on the player list — **DONE**
2. A collectible part with a ClickDetector that adds to the backpack
3. A sell pad using a Touched event that converts backpack → coins
4. Backpack capacity, so selling actually matters
5. A shop with a ProximityPrompt selling capacity and multiplier upgrades
6. A second, better zone that costs coins to unlock
7. DataStore saving so progress persists

**How I want to work — this part matters:**

- One step at a time. Do NOT give me all the remaining steps at once.
  Finish one, stop, let me test it in Studio, then wait for me to say go.
- For each step: write the Luau script as a file in this project.
- Tell me exactly where the object goes in the Studio Explorer, and what
  object type to create — Script, LocalScript, or ModuleScript.
- Explain what each part of the code does. I'm learning as I go.
- Tell me how to test that it worked before we move on.

**What already exists in Studio (step 1):**

A **Script** named `Leaderstats` in **ServerScriptService**. On join it gives
each player a Folder named exactly `leaderstats` containing two IntValues:
`Coins` and `Ore`. Use those exact names in later steps. Here it is, with the
teaching comments stripped out:

    local Players = game:GetService("Players")

    local function setupLeaderstats(player)
        local leaderstats = Instance.new("Folder")
        leaderstats.Name = "leaderstats"
        leaderstats.Parent = player

        local coins = Instance.new("IntValue")
        coins.Name = "Coins"
        coins.Value = 0
        coins.Parent = leaderstats

        local ore = Instance.new("IntValue")
        ore.Name = "Ore"
        ore.Value = 0
        ore.Parent = leaderstats
    end

    Players.PlayerAdded:Connect(setupLeaderstats)

    for _, player in ipairs(Players:GetPlayers()) do
        setupLeaderstats(player)
    end

Tested and working: the player list shows Coins 0 and Ore 0, and editing a
value in Properties during a playtest updates the list live.

**File naming convention we've been using:** `NN_Name.<kind>.lua`, where
`.server.lua` means a Script, `.client.lua` means a LocalScript, and
`.module.lua` means a ModuleScript. Studio ignores these suffixes — they're
just a note about what object to create. Step 1's file is
`src/01_Leaderstats.server.lua`.

Please start with **step 2** — the clickable ore part.
