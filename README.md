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
