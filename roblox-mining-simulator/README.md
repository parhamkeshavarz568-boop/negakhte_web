# Roblox Mining Simulator

A beginner's first simulator game. Core loop:

> click ore to collect → backpack fills to capacity → walk to sell pad → ore becomes coins → spend coins on upgrades → repeat, faster

## Build order

| # | Step | Status |
|---|------|--------|
| 1 | `leaderstats` — Coins and Ore counters on the player list | done |
| 2 | Collectible part with a ClickDetector that adds Ore | not started |
| 3 | Sell pad using a Touched event: Ore → Coins | not started |
| 4 | Backpack capacity, so selling matters | not started |
| 5 | Shop with a ProximityPrompt selling capacity + multiplier upgrades | not started |
| 6 | A second, better zone that costs coins to unlock | not started |
| 7 | DataStore saving so progress persists | not started |

## File naming

Files are named `NN_Name.<kind>.lua`, where `<kind>` tells you what object
type to create in Studio:

- `.server.lua` → a **Script** (runs on the server)
- `.client.lua` → a **LocalScript** (runs on one player's device)
- `.module.lua` → a **ModuleScript** (shared code other scripts load)

Studio does not read these suffixes — they are just a note to ourselves.
To use a file, create the matching object in the Explorer and paste the
contents in.

## Where each file goes in the Studio Explorer

| File | Object type | Location |
|------|-------------|----------|
| `src/01_Leaderstats.server.lua` | Script | `ServerScriptService` |
