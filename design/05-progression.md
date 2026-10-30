# Pantry Quest 3D — Progression and Quests

## The critical path

Each step lists what unlocks it (needs) and what it gives. The game's `Flicker` hint
system reads these as story flags (`scripts/story.bs` → `next_goal()`).

| # | Step | Needs | Gives / sets flag |
|---|---|---|---|
| 1 | Wake up, meet Flicker | — | `met_flicker` |
| 2 | Get the Wooden Spoon (Kitchen Garden maze) | — | `spoon` |
| 3 | Buy the Pot-Lid Shield (40 beans) | beans | `potlid` |
| 4 | Pass Chive | spoon + potlid | `chive_moved` |
| 5 | Talk to Mother Starter | — | `starter_talk` |
| 6 | **The Great Crock** | — | Pea Shooter, Heart Pie, `crock_done` |
| 7 | Mother Starter's farewell | `crock_done` | Ember of Courage, `ember_courage` |
| 8 | Leave Sprouthollow; Fennel's pipe | — | Fennel's Pipe, Fennel's Tune |
| 9 | Larder Town; sneak into the castle garden | — | Saffron's Letter, Saffron's Lullaby |
| 10 | Peppermill → Mount Fondue; meet Biscotti | Saffron's Letter (gate guard) | |
| 11 | Make Biscotti dance (Fennel's Tune) | Fennel's Tune | Gum Bracelet |
| 12 | **Hardtack Caverns** | Gum Bracelet | Popcorn Bombs, `hardcaves_done`, Ember of Power |
| 13 | Fizzling Domain (Saffron's Lullaby at the falls) | Saffron's Lullaby | Fizz Bubble (diving game) |
| 14 | Fizzy's Letter in a jar (Lake Brine) | Fizz Bubble | Jar, Fizzy's Letter |
| 15 | King Carbonarius moves aside | Fizzy's Letter | path to Lord Gulp |
| 16 | **Inside Lord Gulp** | a fish in a jar | Spatula Boomerang, `gulp_done`, Ember of Wisdom |
| 17 | The castle burns; get the Kettle Whistle | three Embers | Kettle Whistle, Song of Rising |
| 18 | Pull the Cleaver of Dawn | Song of Rising | **Risen era** |
| 19 | Old Mozz, Cinder, Prelude of the Hearth | — | Umami medallion |
| 20 | Grubb's dairy: win Custard | Custard's Song | Custard |
| 21 | **Thyme Temple** | Licorice Lash (Peppermill graveyard ghost race) | Skewer Bow, Bitter medallion, Minuet |
| 22 | **Fondue Forge** | Oven Apron (Hardtack City) | Meat Tenderizer, Spice medallion, Bolero |
| 23 | Freezer Caves (Risen) | Fizzling Domain frozen | Cast-Iron Boots, Serenade |
| 24 | **Fizzwater Temple** | Cast-Iron Boots, Snorkel Apron | Long Licorice, Salt medallion |
| 25 | Peppermill well (drained by the Boiling Song) | Boiling Song | Onion Lens (if not already) |
| 26 | **Compost Crypt** | Onion Lens, Nocturne | Meringue Boots, Sour medallion |
| 27 | Raider Fort → Haunted Flats → Salt Idol | Long Licorice, Onion Lens | Requiem of Sugar |
| 28 | **Salt Idol Temple** (child half, then adult half) | Requiem; Fresh: Oven Mitts in the Fresh half | Silver Platter, Golden Mitts, Sweet medallion |
| 29 | Cinder → Saffron; Saffron taken | six medallions | Saffron Skewers |
| 30 | **Moldering Spire**: six trials, Mildew, escape, Gorgemold | | the ending |

Steps 21–28 are partly free in order: Thyme and Fondue first (either order), then Water,
then Shadow and Spirit (either order). The Flicker hint names the earliest unfinished.

## Side quests

| Quest | Where | Steps | Reward |
|---|---|---|---|
| **The Golden Weevils** | everywhere (100 tokens; 50 Fresh-only, 30 Risen-only, 20 either) | collect tokens, visit the Weevil house | Pantry Purse (10), Steam (20), Bean-of-Truth stone (30), Popcorn bag (40), Big Bean (50), endless beans (100) |
| **Heart Pie slices** | 36 slices | minigames, hidden spots, gifts | +9 hearts |
| **The Fresh mask chain** | Mask Maker, Larder Town | borrow a mask, sell it on, pay back | Mask of Truth (talk to Gossip Stones) |
| **The Big Chef's Knife** | Risen | Odd Egg → Pocket Chick → ... → Eyedrops → Claim Check (11 trades) | Big Chef's Knife |
| **Custard** | Buttercup Dairy | learn Custard's Song (Fresh); race Grubb (Risen) | horse |
| **Super Cucco catcher** | Peppermill | gather 7 loose cuccos | a jar |
| **Fishing** | Lake Brine pond | catch a 10 lb (Fresh) / 13 lb (Risen) fish | Pie Slice / Golden Lure |
| **Archery** | Raider Fort (on Custard) | 1000 / 1500 points | quiver upgrades |
| **Grave digging** | Peppermill graveyard (Fresh) | Grandpa Gristle digs where you point | Pie Slice |
| **Pea bag / bomb bag** | the Thicket's Scrub stage / Hardtack bowling | | bigger bags |
| **The Great Steam Springs** | Mount Fondue summit, Thicket, Dunes, Fondue crater, Castle | popcorn-bomb the cracked walls; play Saffron's Lullaby | magic, spells, spin |
| **The Frog Choir** | Brine Valley | play songs to frogs | Pie Slices |

## Collectibles summary

| What | Count | Notes |
|---|---|---|
| Heart Pies | 8 | one per dungeon boss (the Spire's finale gives none) |
| Pie Slices | 36 | |
| Golden Weevils | 100 | |
| Songs | 12 | |
| Keepers' medallions | 6 | |
| Embers | 3 | |
| Jars | 4 | |
| Maps / compasses / big keys | 8 each | |

## Content production order

The game is built area by area, in roughly story order, so each new piece can be played
from a new save. Each area is a Python description in `tools/world/` turned into scenes
by `tools/make_areas.py`.

1. **Engine features on Bronto's side** (only when missing): nothing needed for the first
   areas; later perhaps water rendering and a cheaper skybox.
2. **Core systems** (done with Sprouthollow): player, camera, focus, combat, health,
   beans, dialogue, chests, pickups, cuttable grass, pots, signs, shop, save, pause menu,
   load zones, Flicker hints.
3. **Sprouthollow** and **The Great Crock** (dungeon 1, Pea Shooter, Queen Mildewmite).
4. **Breadbasket Fields, Buttercup Dairy, Larder Town, Castle garden** (day/night, horse NPCs).
5. **Peppermill, Mount Fondue, Hardtack City, Hardtack Caverns** (bombs, lifting).
6. **Brine Valley, Fizzling Domain, Lake Brine, Inside Lord Gulp** (swimming, boomerang).
7. **The Temple of the First Hearth, the era switch, the Risen variants** of every area so far.
8. **The five Risen temples**, then **the Spire** and the ending.
