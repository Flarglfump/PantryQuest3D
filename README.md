# Pantry Quest 3D

The third Pantry Quest game, and the first in 3D: a third-person action adventure made
with the [Bronto](https://github.com/Flarglfump/Bronto) engine, in the spirit of the
late-90s 3D adventure epics. Like Pantry Quest II it is an editor project with no C code:
scenes, prefabs and BrontoScript, with everything (art, models, sounds, music, areas)
made by the Python tools in `tools/`.

> Sprig, a boy raised among the leafy Sprouts, is woken by a pilot-light spirit and sent
> to save Mother Starter, the ancient sourdough who guards his village. It's the start of
> a journey across the Pantry Kingdom, seven years forward in time, and up the Moldering
> Spire of Duke Mildew — the Mould itself.

## Playing it

You need a copy of Bronto beside this folder (`../bronto`), at commit `de7ad92` or later
(it has the fixes this game needs: steep slopes and mesh edges for characters, view culling).

```sh
cd ../bronto
make game GAME=../PantryQuest3D            # this computer: build/games/PantryQuest3D/<system>/
make game GAME=../PantryQuest3D TARGET=web # one index.html to put on a web site
make tools && build/bronto_player ../PantryQuest3D   # or play it straight from the folder
```

Or open the folder in Bronto's editor (**Load Project**) and press Play.

### Controls

| | Keyboard | Gamepad |
|---|---|---|
| Move | WASD | left stick |
| Camera | ← → (swing), ↓ (behind Sprig) | right stick |
| Action: talk, open, read, climb, roll, hop | Space | A |
| Attack (hold, then let go: spin attack) | J | X |
| Focus (lock on with Flicker) | Shift, L | LT, LB |
| Shield | K | RT, RB |
| Item buttons | U, I, O | Y, B, D-pad up |
| Ask Flicker for a hint | Tab | Back |
| Pause (items, gear, map, save) | Enter, Esc | Start |

While focused, Action hops to the side or back-flips; forward + Action with the spoon is
a jump attack.

## What's there

- **Sprouthollow** (the starting area): Sprig's tree-house, the village and its Sprouts,
  Sage's shop, the training field, the Kitchen Garden maze (the Wooden Spoon), Chive's
  gate, the grove path and Mother Starter. The story runs from waking up to her farewell
  and the Ember of Courage, and Fennel's goodbye on the bridge.
- **The Great Crock** (dungeon 1): the Central Rise with ledges, vines and a plank to dive
  from; the Lift room (crust platforms, the map, a small key); the locked Shooter room
  (the Pea Shooter); the eye switch and Compass room; the Scrub brothers (shield their
  nuts back in the right order); the web only fire burns; **Queen Mildewmite**.
- **Breadbasket Fields** (the hub): day and night, Stalebies rising at night, Sir
  Hootenanny the owl, Basil's travelling kitchen, the dairy hill, the town gate (shut at
  night) and the roads out.
- **Larder Town**: the market square, townsfolk, Pip at the Royal Kitchens, the sealed
  Temple of the First Hearth, and the castle road.
- **The castle garden**: sneak through the hedges past patrolling guards (their sight is
  the pale cone on the ground; caught, you're marched back to the gate) to meet Princess
  Saffron, get her letter, and learn Saffron's Lullaby from Nanny Kimchi.
- **Peppermill Village** (windmill, dry well, graveyard; the trail gate opens to the
  princess's letter), the **Mount Fondue** trail (molten cheese, rolling boulders, rolling
  Hardtack), **Hardtack City** (Big Biscotti's door opens to Saffron's Lullaby; Fennel's
  Tune makes him dance and earns the Gum Bracelet) and **Hardtack Caverns** (dungeon 2:
  bomb flowers and cracked walls, the cheese hall, crustlings, the Popcorn Bombs, keys,
  and **King Crustodon**, who must be fed a bomb while he breathes in). Biscotti then gives
  the Ember of Power.
- **Brine Valley** (the river gorge west of the field: swim it, cross the bridge, climb
  to the falls, which part to Saffron's Lullaby), the **Fizzling Domain** (King
  Carbonarius, the diving game and the Fizz Bubble), **Lake Brine** (the island, Professor
  Brineworth's lab, a letter in a jar on the lake bed), **Fizzwater Fountain** (catch a
  fish in the jar and feed it to Lord Gulp) and **Inside Lord Gulp** (dungeon 3: carry
  Princess Fizzy and set her on floor switches, shock jellies, the Spatula Boomerang,
  tendrils only it can cut, and **the Gristle Knot**). Fizzy gives the Ember of Wisdom.
- **The storm and the Temple of the First Hearth**: with all three Embers, Larder Town
  is caught in a storm, the castle burns, Saffron and Kimchi flee past and Duke Mildew
  follows; Saffron's Kettle Whistle lies in the moat (dive for it; her voice teaches the
  Song of Rising). In the temple the song opens the Door of Seasons; pulling the Cleaver
  of Dawn moves the story **seven years on**: Sprig wakes, grown, in the Proofing Vault
  with Old Mozz (the Umami Medallion), and outside the temple Larder Town has rotted
  under the Moldering Spire. Cinder waits on the steps with the Prelude of the Hearth (a
  warp song). Putting the Cleaver back, or pulling it again, moves between the eras.
- **The Risen world, part one**: the rotted Breadbasket Fields, Peppermill (race the old
  gravekeeper's ghost round the village for the **Licorice Lash**, a grappling line that
  bites into wooden targets), the **Thicket of Thyme** (hedge paths to the Glade and the
  temple's crumbled stair) and the **Thyme Temple** (dungeon 4: lash across pits, the
  **Skewer Bow**, three Lantern Sisters who stole the braziers' flames — one floats where
  only a skewer reaches — and **the Hollow Duke**, who rides out of paintings: skewer the
  one that glows, then bat his balls of light back at him). Fennel wakes as the Keeper of
  Bitter; Cinder teaches the Minuet of Thyme.
- **The Fondue Forge** (dungeon 5, in Mount Fondue's crater): Biscotti's boy in empty
  Hardtack City gives the Oven Apron (without it the forge's heat hurts); Hardtack
  prisoners in cells, crust golems guarding the **Meat Tenderizer** (it smashes rusted
  switches and cracked rock), a bridge over molten cheese, and **Gratinox**, a dragon who
  rises out of the holes in its lair — knock its head as it comes up. Big Biscotti wakes
  as the Keeper of Spice; Cinder teaches the Bolero of Embers.
- **The frozen lake** and **the Fizzwater Temple** (dungeon 6): the Fizzling Domain and
  fountain frozen solid; the Freezer Caves (catch blue fire in a jar to melt red ice; the
  **Cast-Iron Boots**, to sink and walk the bottom); King Carbonarius thawed (the Snorkel
  Apron, to breathe under water); the temple under Lake Brine, flooded — a royal crest
  drains and fills it to Saffron's Lullaby; Shadow Sprig and the **Long Licorice**; a
  chasm only it crosses; and **the Living Brine**: lash its core out of the water and
  strike it on the floor. Fizzy wakes as the Keeper of Salt; Cinder's Serenade of Brine.
- **The Compost Crypt** (dungeon 7): Peppermill's miller teaches the Boiling Song, which
  dries the well; at the bottom, the **Onion Lens** (see hidden floors, see through false
  walls). Cinder's Nocturne of Rot opens the crypt under the graveyard: an unseen bridge,
  guillotines, the **Meringue Boots** (a moment's walk on air), and **the Maw of Rot** —
  strike its hands after they slam, then its eye, seen only through the lens. Nanny Kimchi
  wakes as the Keeper of Sour.
- **The Sugar Dunes and the Salt Idol** (dungeon 8): west from Brine Valley, the Raider
  Fort (sneak past the Raiders to the gate lever), the Haunted Flats (follow the posts
  through the sandstorm, or be turned round; the lens shows ghost lanterns), the Salt
  Idol and Cinder's Requiem of Sugar (a warp song for either era). As a child: Caramel,
  a hole only a child fits through, and the **Silver Platter** (then the witches take
  her). Grown: heave the rock salt aside, the Boss Key, and **Saccharine & Sodium** —
  catch a witch's bolt on the shield and it flies at her sister. Caramel wakes as the
  Keeper of Sweet.
- **The finale**: with six medallions, Cinder unmasks as Saffron — and Mildew takes her.
  The Keepers bridge the rot to **the Moldering Spire** (four floors: rot-things, a lash
  crossing, a hall of lies, and **Duke Mildew** at the top: bat his balls of rot back at
  him). The tower comes down — run for it before the countdown ends — and in the ruins
  **Gorgemold** rises: when Saffron holds it with her light, strike its tail. Then the
  ending, back in the castle garden, seven years before.
- **Buttercup Dairy** (on the fields' hill): Crème teaches Custard's Song; seven years
  later Grubb wants Custard for the Duke — play her song and she's yours (and a Pie Slice).
- **Golden Weevils**: 32 cursed weevils floating about the kingdom (some only at night);
  strike, shoot or lash them for tokens, and the Weevil House in Peppermill gives the
  Giant Bean Purse, a Pie Slice and a Heart Pie at 10, 20 and 30.
- Swimming and diving (A dives; hold it to go deeper).
- Playing songs on Fennel's pipe (put it on an item button: notes on A, the item buttons
  and the shield button), picking up, carrying and throwing bombs.
- Core systems: lock-on combat (combos, spin attack, side-hops, jump attack, shield),
  rolling, the automatic hop off ledges, climbing, moving platforms, talking and shops,
  chests, keys and locked doors, grass and pots, pickups, the pause menu, three saved
  journeys, game over, the title screen, music and sound.

## Design

- [Theme, story, characters, setting](design/01-story.md)
- [Mechanics](design/02-mechanics.md)
- [Items and equipment](design/03-items.md)
- [World, areas, maps](design/04-world.md) · [world map](design/world-map.svg)
- [Progression and quests](design/05-progression.md)

## How it's made

```
project.bronto        the project (main scene: title.scene; 320 x 240; strict typing)
title.scene           the title (made from Sprouthollow's scenery)       scripts/title.bs
areas/*.scene         the areas: sprouthollow, crock, fields, town, castle, peppermill, fondue, hardtack, hardcaves
dialogue.scene        the text box                                         scripts/dialogue.bs
pause.scene           the pause menu                                       scripts/pause.bs
gameover.scene        game over                                            scripts/gameover.bs
prefabs/              Sprig's body and gear, shots, pickups, effects, the larva
scripts/              game.bs (the journey's state, talks, saving, areas), sprig.bs (the
                      hero), camera.bs, flicker.bs, hud.bs, story.bs (all the words), enemy.bs
                      (fuzzball, larva, scrub, stalebie, dummy), queen.bs, and the things in
                      the world: npc, sign, chest, pickup, cuttable, vine, platform, web,
                      torch, eyeswitch, lockdoor, scrubtrio, loadzone, warp, gate, sky...
models/ art/ sfx/ music/   made by the tools below
tools/                the Python tools (standard library only; not packed into the game)
```

- `python3 tools/make_all.py` remakes everything; `make_all.py areas` (or `art`, `sound`,
  `music`, `models`, `prefabs`) one part. Each area is a Python file in `tools/areas/`
  built with the helpers in `tools/lib/areakit.py` (level geometry is merged into chunks
  by material, each with a mesh collider, so the renderer can skip what's out of view).
- `tools/bot/drive.py` plays the game headless through Bronto's `botrunner`: it presses
  keys, reads script variables, saves screenshots, and can start an area on its own with
  given items and story flags (`test_scene()`), which is how the areas were play-tested.
- The game's state lives in the global `save` (story flags, items, hearts, beans, peas,
  item buttons, counters, the area and spawn point, play time), so it carries across
  `load_scene()` and the overlay scenes; saving writes the same list with `save_data`.
