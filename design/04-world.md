# Pantry Quest 3D — World, Areas and Maps

## World map

The kingdom is a ring of regions around **Breadbasket Fields**, which joins them all.
North is up. (`[D]` = dungeon entrance, `*` = Great Steam Spring.)

```
                        ┌───────────────────────┐
                        │      MOUNT FONDUE     │
                        │ summit*  Fondue Forge │
                        │   [D2] Hardtack Caves │
                        │      Hardtack City    │
                        └──────────┬────────────┘
   ┌──────────────┐    ┌──────────┴───────────┐      ┌────────────────────┐
   │ SUGAR DUNES  │    │   PEPPERMILL VILLAGE │      │  FIZZWATER FALLS   │
   │ Raider Fort  │    │ windmill, well [Lens]│──────│  Fizzling Domain   │
   │ Haunted Flats│    │ graveyard [Compost]  │ river│  Lord Gulp [D3]    │
   │ [Salt Idol]* │    └──────────┬───────────┘      │  Freezer Caves     │
   └──────┬───────┘               │                  └─────────┬──────────┘
          │       ┌───────────────┴──────────────────┐         │
          │       │  LARDER TOWN — CASTLE LARDER     │         │
          │       │  market, Temple of First Hearth, │         │
          │       │  (Risen: Moldering Spire)        │         │
          │       └───────────────┬──────────────────┘         │
   ┌──────┴────────┐  ┌───────────┴──────────────────────┐     │
   │ BRINE VALLEY  │──│        BREADBASKET FIELDS        │─────┘
   │ (river gorge, │  │  Buttercup Dairy on the hill,    │
   │  bridge)      │  │  Basil's cart, scarecrows        │
   └──────┬────────┘  └───────┬───────────────┬──────────┘
          │                   │               │
   ┌──────┴────────┐  ┌───────┴──────┐ ┌──────┴────────────┐
   │  LAKE BRINE   │  │ SPROUTHOLLOW │ │ THICKET OF THYME  │
   │ fish lab,     │  │ [D1] Great   │─│ the Glade, Fennel │
   │ fishing pond  │  │ Crock        │ │ [Thyme Temple]    │
   │ [Fizzwater T.]│  └──────────────┘ └───────────────────┘
   └───────────────┘
```

A rendered version is in [`world-map.svg`](world-map.svg).

## Areas

Each **area** is one Bronto scene (`areas/<id>.scene`), with a Fresh and Risen variant
where they differ. Areas join through **load zones**.

| Id | Area | Size (units) | Contains |
|---|---|---|---|
| `sprouthollow` | Sprouthollow | 120 × 120 | 8 houses, shop, training field, Kitchen Garden maze, Mother Starter's grove, exit bridge, path to Thicket |
| `crock` | The Great Crock (dungeon 1) | 11 rooms | |
| `fields` | Breadbasket Fields | 400 × 400 | the hub: paths to every region, dairy hill, Basil's cart, grottos |
| `dairy` | Buttercup Dairy | 80 × 80 | barn, house, paddock with Custard |
| `town` | Larder Town | 100 × 100 | market, alleys, Temple of the First Hearth, castle path |
| `castle` | Castle Larder grounds | 120 × 120 | stealth garden, courtyard (Saffron) |
| `temple` | Temple of the First Hearth | 40 × 60 | the Door of Seasons, the Cleaver's block |
| `peppermill` | Peppermill Village | 120 × 120 | windmill, well, Weevil house, potion shop, graveyard |
| `trail` | Mount Fondue trail | 80 × 200 | the climb, the summit, the crater |
| `hardtack` | Hardtack City | 80 × 80 (round, 4 levels) | Biscotti's room, shop |
| `hardcaves` | Hardtack Caverns (dungeon 2) | 14 rooms | |
| `gorge` | Brine Valley | 60 × 300 | river, bridge, fizz waterfall gate |
| `fizzdomain` | Fizzling Domain | 80 × 80 | King Carbonarius, diving game |
| `fountain` | Fizzwater Fountain | 80 × 80 | Lord Gulp's altar; Freezer Caves (Risen) |
| `gulp` | Inside Lord Gulp (dungeon 3) | 12 rooms | |
| `lake` | Lake Brine | 200 × 200 | fish lab, fishing pond, bean seller, island, Fizzwater Temple (under) |
| `thicket` | Thicket of Thyme | 12 maze glades | the Glade, Thyme Temple stair |
| `dunes` | Sugar Dunes | 300 × 300 | Raider Fort, Haunted Flats, Salt Idol |
| `spire` | Moldering Spire | 7 floors | |

## Dungeons

| # | Dungeon | Era | Rooms | Item | Boss | Theme / puzzles |
|---|---|---|---|---|---|---|
| 1 | **The Great Crock** | F | 11 | Pea Shooter | Queen Mildewmite | a sourdough crock; mould webs, floating crust platforms, eye switches |
| 2 | **Hardtack Caverns** | F | 14 | Popcorn Bombs | King Crustodon | biscuit caves, lava cheese, bomb flowers, rolling Hardtack |
| 3 | **Inside Lord Gulp** | F | 12 | Spatula Boomerang | the Gristle Knot | carrying Fizzy, tentacle switches, rising fizz |
| 4 | **Thyme Temple** | R | 18 | Skewer Bow | the Hollow Duke | twisted corridors, paintings, the four flames |
| 5 | **Fondue Forge** | R | 20 | Meat Tenderizer | Gratinox | heat, rescuing Hardtack from cells, collapsing pillars |
| 6 | **Fizzwater Temple** | R | 24 | Long Licorice | the Living Brine | water levels (three), currents, Cast-Iron Boots |
| 7 | **Compost Crypt** | R | 22 | Meringue Boots | the Maw of Rot | Onion Lens, invisible floors, guillotines |
| 8 | **Salt Idol Temple** | F + R | 26 | Silver Platter, Golden Mitts | Saccharine & Sodium | sun beams, child/adult halves |
| — | **Moldering Spire** | R | 7 trials + 6 floors | Saffron Skewers | Duke Mildew, Gorgemold | one trial per Keeper; escape |

### Dungeon 1 — The Great Crock (detailed map)

Inside Mother Starter: walls of bubbling dough, crust ledges, mould webs.

```
                 ┌──────────┐
                 │ 10 BOSS  │   Queen Mildewmite (drop through the web in 9)
                 └────▲─────┘
                      │ (fall)
   ┌────────┐   ┌─────┴─────┐   ┌────────┐
   │ 3 Lift │───│ 1 Central │───│ 2 Mite │
   │ crusts │   │   Rise    │   │ nursery│
   └───┬────┘   │ (3 floors)│   └────────┘
       │        └─┬───┬───┬─┘
   ┌───┴────┐     │   │   │      ┌──────────┐
   │ 4 Map  │     │   │   └──────│ 5 Shooter│  Pea Shooter chest (fight 3 Fuzzballs)
   │ chest  │     │   │          └──────────┘
   └────────┘     │   │
          ┌───────┘   └───────┐
   ┌──────┴───┐         ┌─────┴────┐
   │ 6 Eye    │         │ 7 Torch  │  burn the web with a carried torch-stick
   │ switch   │         │ & web    │
   └──────────┘         └────┬─────┘
                       ┌─────┴────┐   ┌──────────┐
                       │ 8 Compass│───│ 9 Base-  │  three Scrub brothers in order;
                       │          │   │ ment web │  web over the boss pit
                       └──────────┘   └──────────┘
   Entrance: Mother Starter's mouth → 1 (ground floor)
```

1. **Central Rise** — a tall round chamber, three floors of crust ledges around a web
   over the basement. A vine wall up to floor 2.
2. **Mite nursery** (floor 1) — Mildewmite larvae; a small reward chest.
3. **Lift crusts** (floor 2) — crust platforms that rise and fall on dough bubbles.
4. **Map room** — chest behind a push-block.
5. **Pea Shooter room** (floor 3) — beat three Fuzzballs; the chest appears.
6. **Eye switch** — shoot the eye over the door to open it; a ladder down.
7. **Torch & web** — light a stick at the torch, carry it to burn the web on the floor.
8. **Compass room** (basement) — a pond of starter, floating crust rafts.
9. **Basement web** — three Scrubs that must be beaten in the order the sign says.
   Then drop through the burnt web from floor 3 into...
10. **Boss — Queen Mildewmite.** A huge mite on the ceiling with one eye. Shoot the eye
    when it glows red (Pea Shooter): she falls, stunned; slash her. She lays eggs that
    hatch into larvae.

## Area map — Sprouthollow (starting area)

A sunken clearing ringed by tall herb stalks, about 120 × 120 units. North is up.

```
   north: Mother Starter's Grove (raised, behind the Chive gate)
   ┌──────────────────────────────────────────────────────────┐
   │                  ╔════════════════╗                      │
   │                  ║ MOTHER STARTER ║  (the great crock;   │
   │                  ║   [D1 mouth]   ║   path guarded by    │
   │                  ╚═══════╤════════╝   Fuzzballs)          │
   │                    grove path                            │
   │                       │                                  │
   │  ┌──────┐         ╔═══╧═══╗ CHIVE           ┌──────────┐ │
   │  │Kitchen│        ║ gate  ║                 │ training │ │
   │  │Garden │        ╚═══╤═══╝                 │  field   │ │
   │  │ maze  │  Twins'    │      Sage's shop    │ (signs,  │ │
   │  │[spoon]│  house     │       ┌──┐          │  dummies)│ │
   │  └──┬───┘   ┌──┐   VILLAGE    │$ │          └────┬─────┘ │
   │     │       └──┘    GREEN     └──┘   Fennel's    │       │
   │  crawl hole         (well,          house ┌──┐   │       │
   │                     stream)               └──┘           │
   │      Parsley's  ┌──┐       ┌──┐ Chive's                  │
   │      house      └──┘       └──┘ house                    │
   │              ┌──────┐                    ~~ stream ~~    │
   │              │SPRIG'S│  (tree-house,        to the       │
   │              │ HOUSE │   ladder)             Thicket →   │
   │              └──────┘                        (closed in   │
   │                       south: the bridge       Fresh 1)   │
   │                       to Breadbasket Fields               │
   │                       (Fennel waits here when you leave)  │
   └──────────────────────────────────────────────────────────┘
```

**Things to do in Sprouthollow (Fresh era, start of the game):**

- Wake up in Sprig's tree-house; Flicker arrives. Climb down the ladder.
- Talk to everyone: Fennel (best friend), the twins, Parsley (tutorial facts), Chive (blocks
  the gate: "No spoon? No shield? No way!").
- **Training field:** signs explain moving, rolling, focusing and attacking; dummies to hit.
- **Shop:** Sage sells the **Pot-Lid Shield** (40 beans) and peas (later). Beans come from
  cutting grass, smashing pots, rolling into the tall stalks, and the five green beans on
  the roof of Sprig's house.
- **Kitchen Garden maze:** crawl through a hole in the hedge; avoid the rolling boulder
  (a giant pea); find the chest with the **Wooden Spoon**.
- Show Chive both; he steps aside. The grove path has **Fuzzballs** and **Spit-scrubs**.
- **Mother Starter** talks, then opens her mouth: the entrance to the Great Crock.
- After the Crock: Mother Starter's farewell, the Ember of Courage, Fennel on the bridge.
