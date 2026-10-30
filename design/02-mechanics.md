# Pantry Quest 3D — Mechanics

The feel to aim for is the late-90s 3D adventure: a context-sensitive action button,
lock-on combat built around a companion, no jump button (Sprig jumps by himself off
ledges), and puzzles made from a small set of verbs used in many combinations.

The engine targets 320 × 240 at 60 steps a second, in software, so everything is built
from low-poly shapes and small textures, with fog to hide the far plane.

## Controls

| Action | Keyboard | Gamepad | Notes |
|---|---|---|---|
| Move | WASD | left stick | analogue on a pad; walk / run by how far |
| Camera | ← / → (orbit), ↓ (recentre) | right stick | the camera follows on its own otherwise |
| **Action** (A) | Space | A | context: talk, open, read, grab, climb, roll, put away |
| **Attack** (B) | J | X | spoon / knife / cleaver; hold to charge a spin |
| **Focus** (Z) | Shift, L | LT, LB | lock on with Flicker; with nothing to lock, recentres the camera |
| **Shield** (R) | K | RT, RB | hold to raise the shield |
| **Item slots** (C) | U, I, O | Y, B, (D-pad ↑) | three slots set on the item page of the pause menu |
| **Flicker** | Tab | Back | a hint about where to go, or about what is focused |
| Pause | Enter, Esc | Start | items, equipment, map, quest status, save |

Every binding can be changed (the controls screen from Pantry Quest II carries over).
On the web build, touch controls give a stick, A, X, Y, B, LT, RT and Start.

## Movement

- **Run / walk** with stick magnitude; turning is quick but not instant (Sprig leans).
- **Auto-jump:** running off a ledge launches a forward hop; a gap with ground beyond is
  cleared if run at full speed. Walking slowly to an edge makes Sprig stop and teeter.
- **Roll** (Action while running): a quick dodge, and it knocks things off trees/walls.
- **Climb** vines, ladders and grates (Action at the bottom, or walk into them).
- **Ledges:** dropping from a ledge hangs on it; Action climbs up.
- **Swim** (Fresh era cannot dive until the Fizz Bubble; heavy Cast-Iron Boots sink).
- **Push / pull** blocks (Action held against one); **lift** pots, rocks, bushes (Action),
  throw with Action again.
- **Ride** Custard the pudding-pony (Risen era): A to spur, jump fences.
- Falling far hurts; falling into a pit or deep rot costs a quarter heart and returns to the
  last safe spot.

## Combat

- **Focus / lock-on.** Flicker flies to the nearest target in front of Sprig and marks it.
  While focused: the camera frames both, Sprig strafes and faces the target, Action becomes
  **side-hop / back-flip** (with left, right or back) or **jump attack** (forward + Attack).
  Focus on a non-enemy (a sign, an NPC) to talk from further away.
- **Attack.** Standing still: horizontal slash; moving: diagonal slash; focused + forward:
  thrust. Three slashes chain into a combo. **Hold** Attack to charge, release for a
  **spin attack** (costs Steam once the Steam meter exists).
- **Shield.** Hold to raise. Blocks most front attacks; deflects shots from shooters back at
  them (Silver Platter reflects magic and light).
- **Hurt and health.** Hearts are in quarters. Sprig flashes and is invulnerable briefly after
  a hit. At zero: Game Over → continue from the area's entrance (dungeon: its entrance) with
  3 hearts, or quit.
- **Enemies** telegraph their attacks; most have a pattern and an opening. Some must be
  **stunned** (Pea Shooter, Spatula Boomerang) before they can be hurt.
- **Drops:** cut grass, smashed pots and beaten enemies drop **hearts**, **beans** (1, 5, 20,
  50), **peas** (ammo), **popcorn** (bomb ammo) and **steam** (magic) — only of what Sprig has.

## Puzzles — the verbs

| Verb | Made with | Examples |
|---|---|---|
| hit a switch | attack, peas, boomerang, skewers | crystal switches, eye targets |
| step on a switch | Sprig, a block, Cast-Iron Boots | floor buttons, weighted plates |
| light / put out | Flambé, chili skewers, torches carried on a stick | torches, webs, ice |
| push / pull | Action | sliding blocks, statues |
| blow up | popcorn bombs | cracked walls, boulders, sleeping Hardtack |
| pull yourself | Licorice Lash | targets, wooden walls, chests across gaps |
| reveal | Onion Lens | hidden walls, invisible floors, ghosts |
| reflect | Silver Platter | sun beams on to sun switches |
| play a song | Kettle Whistle | Song stones, time blocks, rain, day/night |
| plant / grow | Magic Beans (Fresh) | bean sprouts become flying platforms in the Risen era |
| change era | Song of Rising at the Cleaver's block | child-only crawl holes vs adult-only items |

## Systems

- **Day and night.** A day lasts 6 minutes in the open field. Some characters only appear
  by day or by night; Stalebies rise from the field at night; town gates shut at night.
  The Simmer Song skips to the next dawn or dusk.
- **Two eras.** The world exists twice. Each area scene has a Fresh and a Risen version
  (shared geometry with different props, people and enemies). Some secrets need both.
- **Saving.** Three save slots. Save from the pause menu anywhere; reloading starts at the
  area's entrance (in a dungeon, its entrance) — the classic rule.
- **Map.** The pause menu has a world map, an area map for the current area, and dungeon
  maps (rooms appear as visited; the dungeon's Map shows all; the Compass shows chests,
  the boss and Sprig's facing).
- **Quest status.** Embers, Keeper medallions, songs, Golden Weevil count, heart slices.
- **Flicker hints.** Tab says what to do next, based on story flags — no one gets lost.
- **Text.** All words live in `scripts/story.bs` (as in Pantry Quest II) so they're easy
  to edit or translate.

## Technical design (in Bronto)

- **One scene per area** (`areas/<area>.scene`, generated by `tools/make_areas.py` from
  Python descriptions in `tools/world/`). An area holds geometry (static mesh colliders),
  props, NPCs, enemies, chests and **load zones** (triggers naming a target area and spawn
  point).
- **Persistent game state** lives in globals (`set_global`): flags, inventory, hearts,
  beans, the current spawn. Every area's `Game` entity reads them on start and writes them
  on change, so loading a new area keeps everything. Saving writes the same lists with
  `save_data`.
- **Overlays** on the scene stack: dialogue (`dialogue.scene`), the pause menu, item-get
  fanfares and the game-over screen are pushed over the area, like Pantry Quest II.
- **Player** (`scripts/sprig.bs`): a kinematic capsule driven by `move_and_slide`, a glTF
  model with idle / run / slash / spin / roll / hurt / climb / hold animations, a child
  entity for the weapon so slashes can be tested with `overlap_sphere`.
- **Camera** (`scripts/camera.bs`): spring-arm behind Sprig, recentres on Focus, frames the
  target while focused, pulls in when a wall is between it and Sprig (raycast).
- **Enemies** share a `scripts/enemy.bs` base (health, hurt flash, knock-back, drops,
  `hit(amount, kind)`), with a brain per kind.
- **Tags:** `focusable`, `enemy`, `npc`, `sign`, `chest`, `cuttable`, `liftable`, `switch`,
  `door`, `loadzone`, `pickup`, `transient`.
