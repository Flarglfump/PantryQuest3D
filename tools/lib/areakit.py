"""Building blocks for Pantry Quest 3D's areas: the entities every area has (the Game,
the camera, Sprig, Flicker, the HUD, lights), static level geometry (merged into chunks,
one mesh collider each) and the props people, enemies and treasure.

An area script makes an Area, adds geometry and things, and saves it:

    a = Area('sprouthollow', 'Sprouthollow', music='music/sprouthollow.wav')
    a.geo('grass').ground(...)          # level geometry, by material
    a.tree(4, 0, 6)
    a.save()
"""
import inspect
import math
import os
import re

from kit import (Scene, Obj, Chunked, t3, t2, mesh, collider, kinematic, tags, script, particles, light, q, path, write_png)
import kit

def surface_y(tris, x, z, near):
    """The height of the upward-facing triangle over (x, z) nearest the height near (None: none)."""
    best = None
    for P in tris:
        (ax, ay, az), (bx, by, bz), (cx, cy, cz) = P
        d = (bz - cz) * (ax - cx) + (cx - bx) * (az - cz)
        if abs(d) < 1e-9:
            continue
        l1 = ((bz - cz) * (x - cx) + (cx - bx) * (z - cz)) / d
        l2 = ((cz - az) * (x - cx) + (ax - cx) * (z - cz)) / d
        l3 = 1 - l1 - l2
        if min(l1, l2, l3) < -1e-6:
            continue
        y = l1 * ay + l2 * by + l3 * cy
        if best is None or abs(y - near) < abs(best - near):
            best = y
    return best


def clip_face(o, P, T, N, f, _):
    """Adds to o the part of triangle P (texture coordinates T, normals N) where f(p) <= 0."""
    ds = [f(p) for p in P]
    if all(d <= 0 for d in ds):
        o.tri(P[0], P[1], P[2], T[0], T[1], T[2], N[0], N[1], N[2])
        return
    poly = []
    for i in range(3):
        j = (i + 1) % 3
        if ds[i] <= 0:
            poly.append((P[i], T[i], N[i]))
        if (ds[i] <= 0) != (ds[j] <= 0):
            t = ds[i] / (ds[i] - ds[j])
            lerp = lambda a, b: tuple(a[k] + (b[k] - a[k]) * t for k in range(len(a)))
            poly.append((lerp(P[i], P[j]), lerp(T[i], T[j]), lerp(N[i], N[j])))
    for k in range(1, len(poly) - 1):
        a, b, c = poly[0], poly[k], poly[k + 1]
        o.tri(a[0], b[0], c[0], a[1], b[1], c[1], a[2], b[2], c[2])


def mat_info(material):
    """MATERIALS[material]; a preview_<m> (another place's, seen past a way out) looks like <m>
    but is only to look at: not solid, no shadows."""
    if material.endswith('_2s'):                         # (its open faces: drawn from both sides)
        t, c, solid, cast, lit, cull = mat_info(material[:-3])
        return (t, c, solid, cast, lit, False)
    if material.startswith('preview_'):
        t, c, solid, cast, lit, cull = MATERIALS[material[8:]]
        return (t, c, False, False, lit, cull)
    return MATERIALS[material]


# The outdoor places (their ways out to each other show a slice of the next: Area.make_previews).
OUTDOOR = {'fields', 'town', 'castle', 'sprouthollow', 'gorge', 'peppermill', 'thicket', 'lake', 'fort', 'flats', 'idol', 'fondue', 'fountain'}

MATERIALS = {
    # material: (texture, colour, solid, cast shadows, lit, cull)
    'grass': ('art/grass.png', '#ffffffff', True, False, True, True),
    'flowers': ('art/flowers.png', '#ffffffff', True, False, True, True),
    'dirt': ('art/dirt.png', '#ffffffff', True, False, True, True),
    'path': ('art/dirt.png', '#ffffffff', False, False, True, True),     # (dirt paths laid on the ground: walked on through)
    'cobble': ('art/cobble.png', '#ffffffff', True, False, True, True),
    'lava': ('art/lavacheese.png', '#ffffffff', False, False, False, True),
    'rock': ('art/stone.png', '#c8a080ff', True, False, True, True),
    'cliff': ('art/stone.png', '#c8d0b8ff', True, False, True, True),
    'stone': ('art/stone.png', '#ffffffff', True, True, True, True),
    'bark': ('art/bark.png', '#ffffffff', True, True, True, True),
    'planks': ('art/planks.png', '#ffffffff', True, True, True, True),
    'thatch': ('art/thatch.png', '#ffffffff', True, True, True, True),
    'leaves': ('art/leaves.png', '#ffffffff', True, True, True, True),
    'hedge': ('art/hedge.png', '#ffffffff', True, True, True, True),
    'canopy': ('art/leaves.png', '#b8d8a8ff', False, False, True, False),
    'water': ('art/water.png', '#ffffffc8', False, False, False, False),
    'flesh': ('art/flesh.png', '#ffffffff', True, False, True, True),
    'fizzrock': ('art/fizzrock.png', '#ffffffff', True, True, True, True),
    'sand': ('art/sand.png', '#ffffffff', True, False, True, True),
    'ice': ('art/ice.png', '#ffffffff', True, False, True, True),
    'crock': ('art/crock.png', '#ffffffff', True, True, True, True),
    'dough': ('art/dough.png', '#ffffffff', True, False, True, True),
    'dough_wall': ('art/dough.png', '#e8d8c0ff', True, False, True, True),
    'crust': ('art/crust.png', '#ffffffff', True, True, True, True),
    'mould': ('art/mould.png', '#ffffffff', True, False, True, True),
    'rot': ('art/rot.png', '#ffffffff', True, False, True, True),
    'starter': ('art/dough.png', '#f0e0b8e0', False, False, True, False),
    'starter_pool': ('art/dough.png', '#d8c090ff', False, False, True, True),   # (a pit's runny starter: not see-through)
    'deco': ('art/planks.png', '#ffffffff', False, True, True, True),
    'far_stone': ('art/stone.png', '#e8e0d0ff', False, False, True, True),   # (scenery far off: a castle on the skyline)
    'far_roof': ('art/planks.png', '#5868a8ff', False, False, True, True),
    'ceiling': ('art/dough.png', '#a89878ff', True, False, True, True),
}


def area2d(poly):
    """Twice the signed area of a polygon [(x, z), ...] (positive: counter-clockwise, x right, z up)."""
    return sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly)))


def clip_convex(poly, clip):
    """poly (convex or not) cut to the convex polygon clip (both counter-clockwise)."""
    out = list(poly)
    for i in range(len(clip)):
        if not out:
            break
        (ex0, ez0), (ex1, ez1) = clip[i], clip[(i + 1) % len(clip)]
        side = lambda p: (ex1 - ex0) * (p[1] - ez0) - (ez1 - ez0) * (p[0] - ex0)
        inp, out = out, []
        for k in range(len(inp)):
            p, q = inp[k], inp[(k + 1) % len(inp)]
            sp, sq = side(p), side(q)
            if sp >= 0:
                out.append(p)
            if (sp >= 0) != (sq >= 0):
                t = sp / (sp - sq)
                out.append((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t))
    return out


class Area:
    def __init__(self, id, name, music='', dungeon='', kill_y=-20.0, sky='#a8d8f0ff', fog=(22, 60), fog_color=None,
                 ambient=('#8090b0ff', 0.5), sun=('#fff2dcff', 0.95), sun_rot=(-55, -35, 0), shadows=False, chunk=24.0, variant='', hot=False):
        self.id, self.name = id, name
        kit.GROUNDS.clear()              # (this area's heightfields, as they're made: kit.ground_height)
        self.path_count = 0
        self.file_id = id + ('_' + variant if variant else '')     # (the Risen era's version: areas/<id>_risen.scene)
        self.scene = Scene('%s - an area of Pantry Quest 3D.\nMade by tools/areas/%s.py: change that and run tools/make_all.py.' % (name, id))
        self.chunks = Chunked(chunk)
        self.kill_y = kill_y
        self.dungeon = dungeon
        s = self.scene
        gk = dict(area=id, area_name=name, music=music, dungeon=dungeon, kill_y=kill_y)
        if hot:
            gk['hot'] = True
        s.entity('Game', t2(), script('scripts/game.bs', **gk))
        s.entity('Story', t2(), script('scripts/story.bs'))
        s.entity('Sun', t3((0, 30, 0), sun_rot), light('directional', sun[0], sun[1], shadows=shadows, shadow_range=14))
        s.entity('Sky Light', t3((0, 30, 0)), light('ambient', ambient[0], ambient[1]))
        fc = fog_color or sky
        s.entity('Camera', t3((0, 3, 6)),
                 ('Camera3D', [('fov', 62), ('near_clip', 0.15), ('far_clip', fog[1] + 2), ('clear_color', sky),
                               ('fog', True), ('fog_color', fc), ('fog_start', fog[0]), ('fog_end', fog[1])]),
                 script('scripts/camera.bs'))
        s.entity('Sprig', t3((0, 0.1, 0)), collider('capsule', (1, 1.1, 1), 0.28, offset=(0, 0.55, 0), friction=0),
                 kinematic(), tags('player'), script('scripts/sprig.bs'))
        s.entity('Flicker', t3((0, 1.5, 0), scale=0.16), mesh('sphere', '#9ad8ffff', lit=False, cast=False),
                 particles(rate=14, max=30, lifetime=0.5, lifetime_random=0.3, speed=0.4, spread=180, size_start=0.09,
                           size_end=0, color_start='#d0f0ffff', color_end='#60a0ff00', blend='add'),
                 script('scripts/flicker.bs'))
        s.entity('HUD', t2(), script('scripts/hud.bs'))

    # ---- level geometry ----
    def path(self, points, width, material='path', uv=1 / 3):
        """A dirt path along the polyline `points` [(x, z), ...], laid on the ground as it is
        drawn (make the ground first): cut along the ground's own triangles, so it lies on
        them exactly, a few centimetres up. Each path, and each other bend of one, sits a hair
        higher than the last, so where they cross or overlap they don't flicker."""
        self.path_count += 1
        for seg, ((x0, z0), (x1, z1)) in enumerate(zip(points, points[1:])):
            lift = 0.03 + 0.012 * self.path_count + 0.006 * (seg % 2)
            L = math.hypot(x1 - x0, z1 - z0) or 1
            px, pz = -(z1 - z0) / L * width / 2, (x1 - x0) / L * width / 2
            quad = [(x0 - px, z0 - pz), (x1 - px, z1 - pz), (x1 + px, z1 + pz), (x0 + px, z0 + pz)]
            if area2d(quad) < 0:
                quad = quad[::-1]                   # (counter-clockwise from above, as the ground's are)
            o = self.geo(material, (x0 + x1) / 2, (z0 + z1) / 2)
            xs, zs = [q[0] for q in quad], [q[1] for q in quad]
            for tri, height in kit.ground_triangles(min(xs), min(zs), max(xs), max(zs)):
                t2 = [(p[0], p[2]) for p in tri]
                if area2d(t2) < 0:
                    t2, tri = t2[::-1], tri[::-1]
                poly = clip_convex(quad, t2)
                if len(poly) < 3 or abs(area2d(poly)) < 1e-6:
                    continue
                (ax, ay, az), (bx, by, bz), (cx, cy, cz) = tri
                # the triangle's plane: y = ay + gx (x - ax) + gz (z - az)
                det = (bx - ax) * (cz - az) - (cx - ax) * (bz - az)
                if abs(det) < 1e-12:
                    continue
                gx = ((by - ay) * (cz - az) - (cy - ay) * (bz - az)) / det
                gz = ((bx - ax) * (cy - ay) - (cx - ax) * (by - ay)) / det
                Y = lambda x, z: ay + gx * (x - ax) + gz * (z - az) + lift
                e = 0.1
                N = lambda x, z: (height(x - e, z) - height(x + e, z), 2 * e, height(x, z - e) - height(x, z + e))
                V = [(x, Y(x, z), z) for x, z in poly]
                for k in range(1, len(V) - 1):       # (a fan; turned to face up)
                    A, B, C = V[0], V[k + 1], V[k]
                    o.tri(A, B, C, (A[0] * uv, A[2] * uv), (B[0] * uv, B[2] * uv), (C[0] * uv, C[2] * uv),
                          N(A[0], A[2]), N(B[0], B[2]), N(C[0], C[2]))

    def geo(self, material, x=0.0, z=0.0):
        """The Obj to add `material` geometry to, for the chunk around x, z."""
        return self.chunks.at(material, x, z)

    def place_weevils(self):
        """The Golden Weevils for this area (weevils.py): near its spawn points."""
        from weevils import WEEVILS
        spawns = getattr(self, 'spawns', {})
        for k, (spawn, dx, dz, night) in enumerate(WEEVILS.get(self.file_id, [])):
            if spawn in spawns:
                x, y, z, _ = spawns[spawn]
                gy = self.on_ground(x + dx, y - 0.1, z + dz)          # (over the ground there, not the spawn's height)
                self.weevil(x + dx, gy + 1.1, z + dz, '%s_%d' % (self.file_id, k), night=night)

    def save(self):
        self.place_weevils()
        self.make_previews()
        self.two_sided_open_faces()
        n = 0
        tris = 0
        for (material, cx, cz), obj in self.chunks.items():
            if obj.empty():
                continue
            texture, color, solid, cast, lit, cull = mat_info(material)
            file = 'models/areas/%s/%s_%d_%d.obj' % (self.file_id, material, cx, cz)
            obj.save(file)
            comps = [t3((0, 0, 0)), mesh('model', color, texture, file=file, cast=cast, lit=lit, cull=cull)]
            if solid:
                comps.append(collider('mesh', friction=0.9))
            if material.replace('preview_', '') in ('canopy', 'water'):
                comps.append(tags('seethrough'))
            if material.startswith('preview_'):              # (shown only from near enough to see it: preview.bs)
                lo, hi = obj.bounds()
                comps.append(script('scripts/preview.bs', cx=round((lo[0] + hi[0]) / 2, 1), cz=round((lo[2] + hi[2]) / 2, 1),
                                    r=round(math.hypot(hi[0] - lo[0], hi[2] - lo[2]) / 2, 1)))
            self.scene.entity('%s %d %d' % (material, cx, cz), *comps)
            n += 1
            tris += obj.tri_count()
        if self.dungeon or getattr(self, 'free_map', False):
            self.make_map()
        elif hasattr(self, 'map_labels'):
            self.make_area_map()
        written = {'%s_%d_%d.obj' % (m, cx, cz) for (m, cx, cz), obj in self.chunks.items() if not obj.empty()}
        folder = os.path.join('models', 'areas', self.file_id)
        for old in os.listdir(folder) if os.path.isdir(folder) else []:
            if old.endswith('.obj') and old not in written:
                os.remove(os.path.join(folder, old))       # (chunks an earlier version made: not packed into the game)
        self.scene.save(os.path.join('areas', self.file_id + '.scene'))
        print('  %s: %d entities, %d level meshes, %d level triangles' % (self.file_id, self.scene.count, n, tris))

    # ---- the dungeon map: each floor seen from above, as pictures for the pause menu ----
    def map_floors(self, tris):
        """The dungeon's floors as (name, low, high, main height): from `self.floors` if the area
        set them ([(name, low, high), ...]), else worked out from where the floors are: heights
        close together are one floor, and a floor with little in it joins the nearest."""
        def main_height(lo, hi):
            weights = {}
            for P, wall, area in tris:
                y = sum(p[1] for p in P) / 3
                if not wall and lo <= y < hi:
                    k = round(y * 2) / 2
                    weights[k] = weights.get(k, 0) + area
            return max(weights, key=weights.get) if weights else lo
        floors = getattr(self, 'floors', None)
        if floors:
            return [(n, lo, hi, main_height(lo, hi)) for (n, lo, hi) in floors]
        heights = sorted((sum(p[1] for p in P) / 3, area) for P, wall, area in tris if not wall)
        if not heights:
            return [('1F', -1e9, 1e9, 0.0)]
        groups = [[heights[0]]]
        for h in heights[1:]:
            if h[0] - groups[-1][-1][0] > 3.5:
                groups.append([h])
            else:
                groups[-1].append(h)
        total = sum(a for _, a in heights) or 1
        merged = True
        while merged and len(groups) > 1:
            merged = False
            for i, g in enumerate(groups):
                if sum(a for _, a in g) < total * 0.2:
                    j = i - 1 if i > 0 else 1
                    if 0 < i < len(groups) - 1 and groups[i + 1][0][0] - g[-1][0] < g[0][0] - groups[i - 1][-1][0]:
                        j = i + 1
                    groups[j] = sorted(groups[j] + g)
                    del groups[i]
                    merged = True
                    break
        bounds = []
        for i, g in enumerate(groups):
            lo = -1e9 if i == 0 else (groups[i - 1][-1][0] + g[0][0]) / 2
            hi = 1e9 if i == len(groups) - 1 else (g[-1][0] + groups[i + 1][0][0]) / 2
            bounds.append((lo, hi))
        # names: the floor the entrance is on is 1F; above it 2F, 3F...; below it B1, B2...
        start = getattr(self, 'spawns', {}).get('start')
        sy = start[1] if start else 0
        base = next((i for i, (lo, hi) in enumerate(bounds) if lo <= sy < hi), 0)
        out = []
        for i, (lo, hi) in enumerate(bounds):
            name = '%dF' % (i - base + 1) if i >= base else 'B%d' % (base - i)
            out.append((name, lo, hi, main_height(lo, hi)))
        return out

    def make_map(self, max_w=200, max_h=112):
        tris, walls = [], []          # floors (and wall tops) seen from above; the walls' upright faces
        for (material, cx, cz), obj in self.chunks.items():
            if obj.empty() or not mat_info(material)[2] or material.startswith('ceiling'):
                continue
            wall = 'wall' in material
            for f in obj.f:
                P = [obj.v[k[0] - 1] for k in f]
                e1 = [P[1][i] - P[0][i] for i in range(3)]
                e2 = [P[2][i] - P[0][i] for i in range(3)]
                n = (e1[1] * e2[2] - e1[2] * e2[1], e1[2] * e2[0] - e1[0] * e2[2], e1[0] * e2[1] - e1[1] * e2[0])
                l = math.sqrt(n[0] ** 2 + n[1] ** 2 + n[2] ** 2) or 1
                if n[1] / l > 0.7:
                    tris.append((P, wall, l / 2))
                elif abs(n[1] / l) < 0.2:
                    walls.append(P)
        if not tris:
            return
        xs = [p[0] for P, w, _ in tris for p in P]
        zs = [p[2] for P, w, _ in tris for p in P]
        x0, x1, z0, z1 = min(xs), max(xs), min(zs), max(zs)
        ppm = min(max_w / max(x1 - x0, 1), max_h / max(z1 - z0, 1))
        W, H = int((x1 - x0) * ppm) + 2, int((z1 - z0) * ppm) + 2

        def to_px(p):
            return ((p[0] - x0) * ppm + 1, (p[2] - z0) * ppm + 1)

        def raster(P, put):
            Q = [to_px(p) + (p[1],) for p in P]
            ax, ay, bx, by, cx_, cy = Q[0][0], Q[0][1], Q[1][0], Q[1][1], Q[2][0], Q[2][1]
            den = (by - cy) * (ax - cx_) + (cx_ - bx) * (ay - cy)
            if abs(den) < 1e-9:
                return
            for py in range(max(0, int(min(ay, by, cy))), min(H, int(max(ay, by, cy)) + 1)):
                for px in range(max(0, int(min(ax, bx, cx_))), min(W, int(max(ax, bx, cx_)) + 1)):
                    X, Y = px + 0.5, py + 0.5
                    w0 = ((by - cy) * (X - cx_) + (cx_ - bx) * (Y - cy)) / den
                    w1 = ((cy - ay) * (X - cx_) + (ax - cx_) * (Y - cy)) / den
                    w2 = 1 - w0 - w1
                    if min(w0, w1, w2) < -0.02:
                        continue
                    put(px, py, Q[0][2] * w0 + Q[1][2] * w1 + Q[2][2] * w2)

        def line(a, b, put):
            (ax, ay), (bx, by) = to_px(a), to_px(b)
            steps = int(max(abs(bx - ax), abs(by - ay))) + 1
            for k in range(steps + 1):
                t = k / steps
                px, py = int(ax + (bx - ax) * t), int(ay + (by - ay) * t)
                if 0 <= px < W and 0 <= py < H:
                    put(px, py)

        floors = self.map_floors(tris)
        pictures = []
        for (name, lo, hi, main) in floors:
            top = [[None] * W for _ in range(H)]        # the highest floor of this storey at each pixel
            wallpx = [[False] * W for _ in range(H)]

            def put_floor(px, py, h):
                if top[py][px] is None or h > top[py][px]:
                    top[py][px] = h
            for P, wall, _ in tris:
                y = sum(p[1] for p in P) / 3
                if not wall and lo <= y < hi:
                    raster(P, put_floor)
            # walls standing on this storey: their upright faces cross body height above its floor
            for P in walls:
                ys = [p[1] for p in P]
                if max(ys) < main + 0.6 or min(ys) > main + 1.8:
                    continue
                far = max(((P[i], P[j]) for i in range(3) for j in range(i + 1, 3)),
                          key=lambda ab: (ab[0][0] - ab[1][0]) ** 2 + (ab[0][2] - ab[1][2]) ** 2)
                if (far[0][0] - far[1][0]) ** 2 + (far[0][2] - far[1][2]) ** 2 < 1e-6:
                    continue

                def put_wall(px, py):
                    wallpx[py][px] = True
                line(far[0], far[1], put_wall)
            # ... and their tops, where they're next to one
            for P, wall, _ in tris:
                if wall and max(p[1] for p in P) > main + 0.6:
                    def put_top(px, py, h):
                        if any(0 <= py + dy < H and 0 <= px + dx < W and wallpx[py + dy][px + dx]
                               for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                            wallpx[py][px] = True
                    raster(P, put_top)
            hs = [h for row in top for h in row if h is not None]
            ylo, yhi = (min(hs), max(hs)) if hs else (0, 1)

            def pixel(px, py):
                if wallpx[py][px]:
                    return (96, 64, 40, 255)
                c = top[py][px]
                if c is None:
                    near = any(0 <= py + dy < H and 0 <= px + dx < W and top[py + dy][px + dx] is not None
                               for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                    return (60, 36, 20, 255) if near else (0, 0, 0, 0)
                k = (c - ylo) / ((yhi - ylo) or 1)
                return (150 + 90 * k, 118 + 80 * k, 70 + 60 * k, 255)
            file = 'art/maps/%s_%s.png' % (self.file_id, name.lower())          # (mapinfo.bs makes the same name)
            os.makedirs(os.path.dirname(file), exist_ok=True)
            write_png(file, W, H, pixel, alpha=True)
            pictures.append(file)
        folder = 'art/maps'
        for old in os.listdir(folder):                    # (pictures for floors this dungeon no longer has)
            if old.startswith(self.file_id + '_') and old.endswith('.png') and os.path.join(folder, old) not in pictures:
                os.remove(os.path.join(folder, old))
        if os.path.exists('art/maps/%s.png' % self.file_id):
            os.remove('art/maps/%s.png' % self.file_id)
        self.scene.entity('Map Info', t2(), script('scripts/mapinfo.bs', base='art/maps/%s_' % self.file_id, names=[f[0] for f in floors],
                                                     lows=[round(max(-999, f[1]), 1) for f in floors], highs=[round(min(999, f[2]), 1) for f in floors],
                                                     x0=round(x0 - 1 / ppm, 3), z0=round(z0 - 1 / ppm, 3), ppm=round(ppm, 4), w=W, h=H))

    # ---- previews: past each way out to another outdoor place, a slice of that place (its
    # level geometry near where Sprig comes in, turned and moved to line up with the way out
    # here), so the view through a gate or down a road shows where it goes, not the sky ----
    PREVIEW_DEPTH, PREVIEW_HALF = 46.0, 46.0
    PREVIEW_DEPTHS = {'town': 90.0, 'castle': 80.0, 'fields': 80.0}     # (walled places, seen right across: all of them)
    PREVIEW_FROM = 3.5          # (ours stays this far past the way out: a gate or an archway just past it)
    PREVIEW_ENTITIES = ('Tree', 'Leaves', 'Awning', 'Well Roof', 'Door')

    def make_previews(self):
        for (zx, zy, zz, to, at, zw, zd) in getattr(self, 'zones', []):
            if to not in OUTDOOR or self.id not in OUTDOOR or to == self.id:
                continue
            spawns = getattr(self, 'spawns', {})
            ours = spawns.get(to)                   # (where one comes in from there: just inside it)
            if ours is None and spawns:
                ours = min(spawns.values(), key=lambda sp: math.hypot(sp[0] - zx, sp[2] - zz))
            other = os.path.join('areas', to + '.scene')
            if ours is None or not os.path.exists(other):
                continue
            out = (zx - ours[0], zz - ours[2])
            L = math.hypot(*out)
            if L < 0.5:
                continue
            out = (out[0] / L, out[1] / L)
            sc = open(other).read()
            blocks = sc.split('\nentity\n')
            spawn, back = None, None
            for blk in blocks:
                m = re.search(r'text = "([^"]*)"', blk)
                p = re.search(r'position = ([-\d.e]+) ([-\d.e]+) ([-\d.e]+)', blk)
                if not m or not p:
                    continue
                pos = tuple(float(v) for v in p.groups())
                if m.group(1) == 'spawn_' + at:
                    spawn = pos
            if spawn is None:
                continue
            best = None
            for blk in blocks:
                if 'text = "Load Zone"' not in blk or ('to = \\"%s\\"' % self.id) not in blk:
                    continue
                p = re.search(r'position = ([-\d.e]+) ([-\d.e]+) ([-\d.e]+)', blk)
                hs = re.search(r'size = ([-\d.e]+) ([-\d.e]+) ([-\d.e]+)', blk)
                pos = tuple(float(v) for v in p.groups())
                d = math.hypot(pos[0] - spawn[0], pos[2] - spawn[2])
                if best is None or d < best[0]:
                    best = (d, (pos[0], pos[1] - float(hs.group(2)) / 2, pos[2]))
            if best is None:
                continue
            back = best[1]
            inn = (spawn[0] - back[0], spawn[2] - back[2])
            Li = math.hypot(*inn) or 1
            inn = (inn[0] / Li, inn[1] / Li)
            # their frame -> ours: turn their way in onto our way out, their zone onto ours
            ang = math.atan2(out[1], out[0]) - math.atan2(inn[1], inn[0])
            ca, sa = math.cos(ang), math.sin(ang)
            def turn(n, ca=ca, sa=sa):
                return (n[0] * ca - n[2] * sa, n[1], n[0] * sa + n[2] * ca)
            depth = self.PREVIEW_DEPTHS.get(to, self.PREVIEW_DEPTH)
            def inside(p, inn=inn, back=back, depth=depth):   # (in their frame: the slice in from their way out)
                dx, dz = p[0] - back[0], p[2] - back[2]
                d = dx * inn[0] + dz * inn[1]
                lat = -dx * inn[1] + dz * inn[0]
                return -0.5 <= d <= depth and abs(lat) <= self.PREVIEW_HALF
            # ours past the way out goes (the slice stands there instead): cut at the line
            # across the way out, as theirs is, so the two meet without overlapping
            def side(p, out=out, zx=zx, zz=zz):
                dx, dz = p[0] - zx, p[2] - zz
                if abs(-dx * out[1] + dz * out[0]) > self.PREVIEW_HALF:
                    return -1.0                      # (off to the side: ours stays)
                return dx * out[0] + dz * out[1] - self.PREVIEW_FROM
            # (the ground at the cut, ours: theirs is set to meet it there)
            cut_x, cut_z = zx + out[0] * self.PREVIEW_FROM, zz + out[1] * self.PREVIEW_FROM
            ours_y = surface_y([[o.v[c[0] - 1] for c in f] for k, o in self.chunks.objs.items()
                                if not k[0].startswith('preview_') and not k[0].startswith('far_') and mat_info(k[0])[2] for f in o.f],
                               cut_x, cut_z, zy)
            for key, obj in list(self.chunks.objs.items()):
                if key[0].startswith('preview_') or key[0].startswith('far_'):
                    continue                         # (nor far scenery: a castle on the skyline stays)
                keep, cut = [], []
                for f in obj.f:
                    ds = [side(obj.v[c[0] - 1]) for c in f]
                    if all(d <= 0 for d in ds):
                        keep.append(f)
                    elif any(d < 0 for d in ds):
                        cut.append(f)
                obj.f = keep
                for f in cut:
                    clip_face(obj, [obj.v[c[0] - 1] for c in f], [obj.vt[c[1] - 1] for c in f], [obj.vn[c[2] - 1] for c in f], side, obj)
            # an unseen wall across the way out, either side of the load zone: the ground past it
            # is only to look at, and there's none of ours left to stand on
            half = (zw if abs(out[1]) > abs(out[0]) else zd) / 2
            yaw_deg = math.degrees(math.atan2(-out[0], -out[1]))
            for sgn in (-1, 1):
                mid = half + (self.PREVIEW_HALF - half) / 2
                bx = zx + out[0] * 1.2 + (-out[1]) * sgn * mid
                bz = zz + out[1] * 1.2 + out[0] * sgn * mid
                self.scene.entity('Edge', t3((bx, zy + 5, bz), (0, yaw_deg, 0)), collider('box', (self.PREVIEW_HALF - half, 40, 0.6)))
            # theirs: the level geometry's chunks (not their own previews, nor far scenery)
            theirs = []
            for f in sorted(set(re.findall(r'file = "(models/areas/%s/[^"]+\.obj)"' % re.escape(to), sc))):
                mat = re.sub(r'_-?\d+_-?\d+\.obj$', '', os.path.basename(f))
                base = mat[:-3] if mat.endswith('_2s') else mat
                if mat.startswith('preview_') or mat.startswith('far_') or base == 'canopy' or base not in MATERIALS:
                    continue
                V, T, N = [], [], []
                for line in open(f):
                    if line.startswith('v '):
                        V.append(tuple(float(x) for x in line.split()[1:4]))
                    elif line.startswith('vt '):
                        T.append(tuple(float(x) for x in line.split()[1:3]))
                    elif line.startswith('vn '):
                        N.append(tuple(float(x) for x in line.split()[1:4]))
                    elif line.startswith('f '):
                        idx = [tuple(int(k) for k in c.split('/')) for c in line.split()[1:]]
                        P = [V[c[0] - 1] for c in idx]
                        if not all(inside(p) for p in P):
                            continue
                        e1 = [P[1][k] - P[0][k] for k in range(3)]
                        e2 = [P[2][k] - P[0][k] for k in range(3)]
                        if sum((e1[(k + 1) % 3] * e2[(k + 2) % 3] - e1[(k + 2) % 3] * e2[(k + 1) % 3]) ** 2 for k in range(3)) < 0.01:
                            continue                     # (details too small to see from here)
                        theirs.append((mat, base, P, [T[c[1] - 1] for c in idx], [N[c[2] - 1] for c in idx]))
            # their ground at the cut (the same spot, in their frame) set to ours there: no step, no gap
            tx, tz = back[0] + inn[0] * self.PREVIEW_FROM, back[2] + inn[1] * self.PREVIEW_FROM
            their_y = surface_y([t[2] for t in theirs if MATERIALS[t[1]][2]], tx, tz, back[1])
            if ours_y is not None and their_y is not None:
                lift = ours_y - their_y
            else:
                lift = zy - back[1]
            def move(p, back=back, ca=ca, sa=sa, zx=zx, zz=zz, lift=lift):
                dx, dz = p[0] - back[0], p[2] - back[2]
                return (zx + dx * ca - dz * sa, p[1] + lift, zz + dx * sa + dz * ca)
            for (mat, base, P, Tt, Nn) in theirs:
                Q = [move(p) for p in P]
                o = self.geo('preview_' + mat, (Q[0][0] + Q[1][0] + Q[2][0]) / 3, (Q[0][2] + Q[1][2] + Q[2][2]) / 3)
                clip_face(o, Q, Tt, [turn(n) for n in Nn], lambda p: -side(p), None)
            # ... and their trees, rocks and such (just to look at)
            for blk in blocks:
                m = re.search(r'text = "([^"]*)"', blk)
                if not m or m.group(1) not in self.PREVIEW_ENTITIES or '\n  Mesh\n' not in blk:
                    continue
                if '\n  Parent' in blk:
                    continue
                p = re.search(r'position = ([-\d.e]+) ([-\d.e]+) ([-\d.e]+)', blk)
                r = re.search(r'rotation = ([-\d.e]+) ([-\d.e]+) ([-\d.e]+)', blk)
                pos = tuple(float(v) for v in p.groups())
                if not inside(pos):
                    continue
                q = move(pos)
                rot = tuple(float(v) for v in r.groups()) if r else (0, 0, 0)
                lines = blk.split('\n')
                k = lines.index('  Mesh')
                body = [lines[k]]
                for line in lines[k + 1:]:
                    if not line.startswith('    '):
                        break
                    body.append(line)
                body = '\n'.join(body)
                sc_ = re.search(r'scale = ([-\d.e]+) ([-\d.e]+) ([-\d.e]+)', blk)
                scale = tuple(float(v) for v in sc_.groups()) if sc_ else (1, 1, 1)
                self.scene.lines.append('entity')
                self.scene.lines.append('  Name')
                self.scene.lines.append('    text = "Preview %s"' % m.group(1))
                self.scene.lines.append('  Transform3D')
                self.scene.lines.append('    position = %g %g %g' % tuple(round(v, 4) for v in q))
                self.scene.lines.append('    rotation = %g %g %g' % (rot[0], round(rot[1] - math.degrees(ang), 3), rot[2]))
                self.scene.lines.append('    scale = %g %g %g' % scale)
                for line in body.strip('\n').split('\n'):
                    self.scene.lines.append(line)
                self.scene.lines.append('  Script')
                self.scene.lines.append('    file = "scripts/preview.bs"')
                self.scene.lines.append('    vars = "cx = %g, cz = %g, r = 3"' % (round(q[0], 1), round(q[2], 1)))
                self.scene.lines.append('')
                self.scene.count += 1

    def two_sided_open_faces(self):
        """Faces drawn one side only vanish seen from behind: fine on a closed shape (a box: its
        back faces are inside it), wrong on an open one (a cone roof seen from under its eaves, a
        single sheet of wall, a slope's edge). Every face with an edge no other face shares the
        other way round is open: they move to a '<material>_2s' mesh drawn from both sides."""
        key = lambda p: (round(p[0], 3), round(p[1], 3), round(p[2], 3))
        edges = set()
        objs = [(k, o) for k, o in self.chunks.objs.items() if mat_info(k[0])[5] and not k[0].endswith('_2s') and k[0] not in ('path', 'preview_path')]
        for k, o in objs:
            for f in o.f:
                P = [key(o.v[c[0] - 1]) for c in f]
                for i in range(3):
                    edges.add((P[i], P[(i + 1) % 3]))
        for (mat, cx, cz), o in objs:
            keep, opened = [], []
            for f in o.f:
                P = [key(o.v[c[0] - 1]) for c in f]
                if all((P[(i + 1) % 3], P[i]) in edges for i in range(3)):
                    keep.append(f)
                else:
                    opened.append(f)
            if not opened:
                continue
            o.f = keep
            t = self.chunks.objs.setdefault((mat + '_2s', cx, cz), kit.Obj('%s chunk %d %d (both sides)' % (mat, cx, cz)))
            for f in opened:
                t.tri(*[o.v[c[0] - 1] for c in f], *[o.vt[c[1] - 1] for c in f], *[o.vn[c[2] - 1] for c in f])

    MAP_COLOURS = {   # how each material looks on an area map, from above
        'grass': (104, 160, 76), 'flowers': (120, 170, 90), 'dirt': (168, 128, 84), 'path': (184, 146, 96), 'cobble': (178, 170, 150),
        'rock': (150, 128, 108), 'cliff': (130, 136, 120), 'stone': (160, 156, 146), 'bark': (112, 82, 56), 'planks': (156, 112, 70),
        'thatch': (206, 172, 92), 'leaves': (64, 124, 56), 'hedge': (52, 108, 54), 'water': (74, 146, 214), 'sand': (222, 202, 150),
        'fizzrock': (150, 190, 210), 'ice': (200, 230, 240), 'rot': (110, 100, 80), 'lava': (240, 170, 60), 'crust': (190, 140, 80)}

    SHORT_NAMES = {'fields': 'FIELDS', 'town': 'LARDER TOWN', 'castle': 'CASTLE', 'sprouthollow': 'SPROUTHOLLOW', 'gorge': 'BRINE/VALLEY',
                   'peppermill': 'PEPPERMILL', 'thicket': 'THICKET', 'lake': 'LAKE BRINE', 'fort': 'RAIDER FORT', 'flats': 'HAUNTED/FLATS',
                   'idol': 'SALT IDOL', 'fondue': 'MT FONDUE', 'fountain': 'FOUNTAIN', 'dairy': 'DAIRY', 'ruins': 'RUINS',
                   'fizzdomain': 'FIZZLING/DOMAIN', 'hardtack': 'HARDTACK/CITY', 'spire': 'SPIRE', 'freezer': 'FREEZER/CAVES',
                   'well': 'THE WELL', 'vault': 'VAULT', 'temple': 'TEMPLE', 'chamber': 'CHAMBER', 'crock': 'GREAT CROCK',
                   'brinetemple': 'FIZZWATER/TEMPLE', 'hardcaves': 'HARDTACK/CAVERNS', 'thymetemple': 'THYME/TEMPLE',
                   'idoltemple': 'IDOL TEMPLE', 'gulp': 'LORD GULP', 'forge': 'FONDUE/FORGE', 'crypt': 'COMPOST/CRYPT', 'ending': 'GARDEN'}

    def floor_map(self):
        """A place with floors (a cave, a tower) that shows its map without needing a DUNGEON
        MAP: the same pictures as a dungeon's, a floor at a time."""
        self.free_map = True

    def area_map(self, labels=None, bounds=None, places=()):
        """This (outdoor) area gets a map for the pause menu: its ground from above (north up),
        with labels [(text, x, z, side), ...]: side n, s, e or w for a way out (written outside
        the map's edge there, with an arrow), '' for a place on it. A "/" breaks a line."""
        self.map_labels = labels          # (None: the ways out, from the load zones, named; and places too)
        self.map_places = list(places)
        self.map_bounds = bounds          # (x0, z0, x1, z1): the part to show (else all the ground made)

    def make_area_map(self, max_w=150, max_h=108):
        if getattr(self, 'map_bounds', None):
            x0, z0, x1, z1 = self.map_bounds
        elif kit.GROUNDS:                                 # (the bounds of the ground made: where Sprig can be)
            x0, z0 = min(g[0] for g in kit.GROUNDS), min(g[1] for g in kit.GROUNDS)
            x1, z1 = max(g[2] for g in kit.GROUNDS), max(g[3] for g in kit.GROUNDS)
        else:                                             # (no ground made: all the solid geometry's)
            ps = [o.v[c[0] - 1] for (m, cx, cz), o in self.chunks.objs.items() if mat_info(m)[2] and not m.startswith('preview_') for f in o.f for c in f]
            if not ps:
                return
            x0, z0, x1, z1 = min(p[0] for p in ps), min(p[2] for p in ps), max(p[0] for p in ps), max(p[2] for p in ps)
        if self.map_labels is None:                       # the ways out, named; on the edge they're near
            labels, seen = [], []
            for (zx, zy, zz, to, at, zw, zd) in getattr(self, 'zones', []):
                if not to or any(t == to and math.hypot(zx - sx, zz - sz) < 8 for (t, sx, sz) in seen):
                    continue
                seen.append((to, zx, zz))
                edge = min([(zx - x0, 'w'), (x1 - zx, 'e'), (zz - z0, 'n'), (z1 - zz, 's')])
                labels.append((self.SHORT_NAMES.get(to, to.upper()), zx, zz, edge[1] if edge[0] < 10 else ''))
            self.map_labels = labels + self.map_places
        ppm = min(max_w / (x1 - x0), max_h / (z1 - z0))
        W, H = int((x1 - x0) * ppm), int((z1 - z0) * ppm)
        top = [[None] * W for _ in range(H)]              # (height, colour) of the highest thing at each pixel
        def put(px, py, h, c):
            if 0 <= px < W and 0 <= py < H and (top[py][px] is None or h > top[py][px][0]):
                top[py][px] = (h, c)
        for (material, cx, cz), obj in self.chunks.items():
            col = self.MAP_COLOURS.get(material[:-3] if material.endswith('_2s') else material)
            if col is None or obj.empty():
                continue
            for f in obj.f:
                P = [obj.v[k[0] - 1] for k in f]
                e1 = [P[1][i] - P[0][i] for i in range(3)]
                e2 = [P[2][i] - P[0][i] for i in range(3)]
                ny = e1[2] * e2[0] - e1[0] * e2[2]
                ln = math.sqrt(sum((e1[(i + 1) % 3] * e2[(i + 2) % 3] - e1[(i + 2) % 3] * e2[(i + 1) % 3]) ** 2 for i in range(3))) or 1
                if abs(ny) / ln < 0.35:
                    continue                              # (upright faces: walls are drawn by their tops)
                Q = [((p[0] - x0) * ppm, (p[2] - z0) * ppm, p[1]) for p in P]
                (ax, ay, ah), (bx, by, bh), (qx, qy, qh) = Q
                den = (by - qy) * (ax - qx) + (qx - bx) * (ay - qy)
                if abs(den) < 1e-9:
                    continue
                for py in range(max(0, int(min(ay, by, qy))), min(H, int(max(ay, by, qy)) + 1)):
                    for px in range(max(0, int(min(ax, bx, qx))), min(W, int(max(ax, bx, qx)) + 1)):
                        X, Y = px + 0.5, py + 0.5
                        w0 = ((by - qy) * (X - qx) + (qx - bx) * (Y - qy)) / den
                        w1 = ((qy - ay) * (X - qx) + (ax - qx) * (Y - qy)) / den
                        w2 = 1 - w0 - w1
                        if min(w0, w1, w2) < -0.05:
                            continue
                        h = ah * w0 + bh * w1 + qh * w2
                        if material.startswith('path'):
                            h += 0.3                      # (over the grass it lies on)
                        put(px, py, h, col)
        for (tx, tz, size) in getattr(self, 'trees', []):   # the trees: leafy dots
            r = max(1.0, 1.4 * size * ppm)
            cx, cy = (tx - x0) * ppm, (tz - z0) * ppm
            for py in range(int(cy - r) - 1, int(cy + r) + 2):
                for px in range(int(cx - r) - 1, int(cx + r) + 2):
                    if (px + 0.5 - cx) ** 2 + (py + 0.5 - cy) ** 2 <= r * r:
                        put(px, py, 99, (56, 112, 48))
        hs = [c[0] for row in top for c in row if c is not None and c[0] < 90]
        lo, hi = (min(hs), max(hs)) if hs else (0, 1)
        def pixel(px, py):
            c = top[py][px]
            if c is None:
                return (40, 34, 30, 255)
            k = 0.82 + 0.3 * min(1, max(0, (c[0] - lo) / ((hi - lo) or 1)))        # (higher: lighter)
            if py > 0 and top[py - 1][px] is not None and top[py - 1][px][0] > c[0] + 1.2:
                k *= 0.7                                                           # (a drop's shadow: walls, cliffs)
            return tuple(int(min(255, v * k)) for v in c[1]) + (255,)
        file = 'art/maps/%s_area.png' % self.file_id
        os.makedirs(os.path.dirname(file), exist_ok=True)
        write_png(file, W, H, pixel, alpha=True)
        self.scene.entity('Area Map', t2(), script('scripts/areamap.bs', picture=file, x0=round(x0, 3), z0=round(z0, 3), ppm=round(ppm, 4), w=W, h=H))
        for (t, x, z, side) in self.map_labels:           # (one entity each: a Script's vars are kept short)
            self.scene.entity('Map Label', t2(), tags('map_label'), script('scripts/areamap.bs', label=t, x0=round(x, 1), z0=round(z, 1), side=side))

    # ---- things ----
    GROUND_SOLID = None

    def on_ground(self, x, y, z, off=0.0):
        """y, or the drawn ground's height there (plus off) if y was meant for the ground: within
        a hand's breadth of it, or under it (never left buried), and not on something built
        there (a deck, a step: a surface of level geometry at y)."""
        g = kit.ground_height(x, z)
        if g is None:
            return y
        g += off
        if abs(y - g) < 1e-4 or not (y < g or abs(y - g) < 0.35):
            return y
        for (material, cx, cz), obj in self.chunks.items():
            if not mat_info(material)[2]:
                continue                                    # (things not stood on: leaves, water...)
            if obj.surface_near(x, z, y - off, 0.06):
                return y
        return g

    def spawn_point(self, name, x, y, z, yaw=0):
        self.scene.entity('spawn_' + name, t3((x, y, z), (0, yaw, 0)))
        self.spawns = getattr(self, 'spawns', {})
        self.spawns[name] = (x, y, z, yaw)

    def entity(self, name, *comps):
        return self.scene.entity(name, *comps)

    def tree(self, x, y, z, size=1.0, bonk_drop=''):
        """A round tree: a trunk (solid) and a ball of leaves. Rolling into it can shake down a drop."""
        h = 2.6 * size
        self.trees = getattr(self, 'trees', []) + [(x, z, size)]          # (for the area map)
        self.entity('Tree', t3((x, y + h / 2, z), (0, 0, 0), (0.6 * size, h, 0.6 * size)),
                    mesh('cylinder', '#ffffffff', 'art/bark.png', uv=(1, 2)),
                    collider('capsule', (1, 1, 1), 0.5), tags('tree'),
                    script('scripts/tree.bs', drop=bonk_drop))
        self.entity('Leaves', t3((x, y + h + 0.7 * size, z), (0, x * 37 % 360, 0), (2.6 * size, 2.0 * size, 2.6 * size)),
                    mesh('sphere', '#ffffffff', 'art/leaves.png', uv=(2, 2), shadow=True))

    def grass(self, x, y, z, drops=0.3):
        self.entity('Grass', t3((x, y, z), (0, (x * 53 + z * 17) % 360, 0), (0.55, 0.45, 0.55)),
                    mesh('cone', '#5aa848ff', cast=False),
                    collider('sphere', radius=0.6, trigger=True, offset=(0, 0.4, 0)),
                    script('scripts/cuttable.bs', kind='grass', drops=drops))

    def pot(self, x, y, z, fixed=''):
        kw = {'kind': 'pot', 'drops': 0.6}
        if fixed:
            kw['fixed'] = fixed
        self.entity('Pot', t3((x, y, z)), mesh('model', '#ffffffff', 'art/clay.png', file='models/pot.obj'),
                    collider('capsule', (1, 0.5, 1), 0.28, offset=(0, 0.25, 0)), script('scripts/cuttable.bs', **kw))

    def sign(self, x, y, z, yaw, say):
        self.entity('Sign', t3((x, y + 0.45, z), (0, yaw, 0), (0.1, 0.9, 0.1)), mesh('cube', '#ffffffff', 'art/planks.png'),
                    collider('box'))
        self.entity('Sign Board', t3((x, y + 0.85, z), (0, yaw, 0), (0.8, 0.5, 0.08)), mesh('cube', '#ffffffff', 'art/planks.png'),
                    collider('box'), tags('interact', 'focusable'), script('scripts/sign.bs', say=say))

    def npc(self, who, x, y, z, yaw=0, needs='', until='', reach=None, model=None):
        kw = {'who': who}
        if reach:
            kw['reach'] = reach
        if needs:
            kw['needs'] = needs
        if until:
            kw['until'] = until
        self.entity(who.capitalize(), t3((x, y, z), (0, yaw, 0)), mesh('model', file='models/%s.glb' % (model or who), shadow=True),
                    ('Animator', [('clip', q('idle')), ('speed', 1), ('loop', True), ('playing', True), ('blend', 0.2)]),
                    collider('capsule', (1, 1.1, 1), 0.3, offset=(0, 0.55, 0)), tags('npc', 'interact', 'focusable'),
                    script('scripts/npc.bs', **kw))

    def chest(self, x, y, z, yaw, item, id, appear='', big=False, then=''):
        s = 1.4 if big else 1.0
        kw = {'item': item, 'id': id}
        if then:
            kw['then'] = then
        if appear:
            kw['appear'] = appear
        i = self.entity('Chest', t3((x, y, z), (0, yaw, 0), s), mesh('model', '#ffffffff', 'art/chest.png', file='models/chest_base.obj'),
                        collider('box', (1, 1.3, 0.7), offset=(0, 0.65, 0)), tags('chest', 'interact'),
                        script('scripts/chest.bs', **kw))
        self.entity('Lid', t3((0, 0.55, 0.35)), mesh('model', '#ffffffff', 'art/chest.png', file='models/chest_lid.obj'),
                    ('Parent', [('entity', i)]))

    def enemy(self, brain, x, y, z, yaw=0, hp=2, damage=2, group='', model=None, **more):
        model = model or {'fuzzball': 'fuzzball', 'larva': 'larva', 'scrub': 'scrub', 'stalebie': 'stalebie', 'crustling': 'crustling', 'roller': 'hardtack_kid', 'jelly': 'jelly'}[brain]
        kw = {'brain': brain, 'hp': hp, 'damage': damage}
        if group:
            kw['group'] = group
        kw.update(more)
        r, h = {'fuzzball': (0.35, 0.7), 'larva': (0.25, 0.5), 'scrub': (0.3, 0.7), 'stalebie': (0.32, 1.3), 'crustling': (0.4, 0.8), 'roller': (0.45, 1.0), 'jelly': (0.4, 0.8)}[brain]
        self.entity(brain.capitalize(), t3((x, y, z), (0, yaw, 0)), mesh('model', file='models/%s.glb' % model, shadow=True),
                    ('Animator', [('clip', q('idle')), ('speed', 1), ('loop', True), ('playing', True), ('blend', 0.1)]),
                    collider('capsule', (1, h, 1), r, offset=(0, h / 2, 0)), kinematic(),
                    tags('enemy', 'focusable'), script('scripts/enemy.bs', **kw))
        if brain == 'scrub':     # its bush
            self.entity('Scrub Bush', t3((x, y + 0.15, z), (0, 0, 0), (1.0, 0.45, 1.0)), mesh('sphere', '#ffffffff', 'art/hedge.png'))

    def bombflower(self, x, y, z):
        i = self.entity('Bomb Flower', t3((x, y, z)), mesh('model', '#4a9a3aff', file='models/bombflower.obj', cull=False),
                        tags('interact', 'focusable'), script('scripts/bombflower.bs'))
        self.entity('Bud', t3((0, 0.05, 0)), mesh('model', '#fff4d0ff', file='models/bomb.obj'), ('Parent', [('entity', i)]))

    def cracked(self, x, y, z, w, h, d, id, yaw=0, boulder=False):
        """A cracked wall (or a boulder) a bomb can break."""
        if boulder:
            self.entity('Boulder', t3((x, y + h / 2, z), (0, yaw, 0), (w, h, d)), mesh('sphere', '#c8b8a0ff', 'art/stone.png'),
                        collider('sphere', radius=0.5), tags('bombable', 'focusable'), script('scripts/bombable.bs', id=id, size_r=max(w, d) / 2))
        else:
            self.entity('Cracked Wall', t3((x, y + h / 2, z), (0, yaw, 0), (w, h, d)), mesh('cube', '#b8a890ff', 'art/crack.png', uv=(w / 2, h / 2)),
                        collider('box'), tags('bombable'), script('scripts/bombable.bs', id=id, size_r=max(w, d) / 2))

    def dummy(self, x, y, z, yaw=0):
        self.entity('Dummy', t3((x, y, z), (0, yaw, 0)), mesh('model', '#ffffffff', 'art/sack.png', file='models/dummy.obj'),
                    collider('capsule', (1, 1.4, 1), 0.3, offset=(0, 0.7, 0)), tags('enemy', 'focusable'),
                    script('scripts/enemy.bs', brain='dummy', hp=99))

    def loadzone(self, x, y, z, w, h, d, to='', at='start', say='', needs='', yaw=0, until=''):
        kw = {'to': to, 'at': at}
        if until:
            kw['until'] = until
        if say:
            kw['say'] = say
        if needs:
            kw['needs'] = needs
        self.zones = getattr(self, 'zones', []) + [(x, y, z, to, at, w, d)]  # (for the previews past them)
        self.entity('Load Zone', t3((x, y + h / 2, z), (0, yaw, 0)), collider('box', (w, h, d), trigger=True),
                    tags('loadzone'), script('scripts/loadzone.bs', **kw))

    def vine(self, x, y, z, width, height, out_yaw, top=None, gap=0.15):
        """A climbable wall of vines on a wall facing out_yaw (degrees: 0 faces -z... the
        way something with rotation y = out_yaw looks). The vines are drawn; the trigger
        sits just in front."""
        fx, fz = -math.sin(math.radians(out_yaw)), -math.cos(math.radians(out_yaw))
        top = y + height if top is None else top
        # (drawn out from the wall by gap, so they don't flicker against it or dip into a curved
        # one; on a flat wall, a small gap: right on it)
        self.entity('Vines', t3((x + fx * gap, y + height / 2, z + fz * gap), (0, out_yaw, 0), (width, height, 0.04)),
                    mesh('cube', '#7ac060ff', 'art/leaves.png', uv=(width, height)))
        self.entity('Vine Climb', t3((x + fx * 0.45, y + height / 2, z + fz * 0.45), (0, out_yaw, 0)),
                    collider('box', (width, height + 0.6, 0.7), trigger=True), tags('climbable'),
                    script('scripts/vine.bs', out=(round(fx, 4), 0, round(fz, 4)), top=top, bottom=y))

    def pickup(self, kind, x, y, z, id=''):
        kw = {'kind': kind}
        if id:
            kw['id'] = id
        files = {'heart': ('models/heart.obj', '#ff3048ff'), 'bean1': ('models/bean.obj', '#40e060ff'),
                 'bean5': ('models/bean.obj', '#4080ffff'), 'bean20': ('models/bean.obj', '#ff4040ff'),
                 'key': ('models/key.obj', '#f0c850ff')}
        f, c = files[kind]
        self.entity('Pickup', t3((x, y, z)), mesh('model', c, file=f, lit=False, cast=False, shadow=True), script('scripts/pickup.bs', **kw))

    def blocker(self, x, y, z, size, until, material='planks', yaw=0, color='#ffffffff'):
        tex = {'planks': 'art/planks.png', 'web': 'art/web.png', 'hedge': 'art/hedge.png'}[material]
        self.entity('Blocker', t3((x, y + size[1] / 2, z), (0, yaw, 0), size), mesh('cube', color, tex, uv=(size[0], size[1]), cull=material != 'web'),
                    collider('box'), script('scripts/blocker.bs', until=until))

    def water(self, x0, z0, x1, z1, surface, depth=3.0, round_=False):
        """A body of water: the surface drawn, a trigger under it (sprig.bs swims in it).
        The ground under it is the area's job. round_: a disc inscribed in the rectangle."""
        cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
        if round_:
            self.geo('water', cx, cz).cylinder((cx, surface, cz), (x1 - x0) / 2, 0.0, 20, top=True, uvs=0.15)
        else:
            self.geo('water', cx, cz).quad((x0, surface, z1), (x1, surface, z1), (x1, surface, z0), (x0, surface, z0),
                                           (x0 / 4, z1 / 4), (x1 / 4, z1 / 4), (x1 / 4, z0 / 4), (x0 / 4, z0 / 4))
        self.entity('Water', t3((cx, surface - depth / 2, cz)), collider('box', (x1 - x0, depth, z1 - z0), trigger=True),
                    tags('water'), script('scripts/water.bs', surface=surface))

    def floorswitch(self, x, y, z, id):
        self.entity('Floor Switch', t3((x, y, z)), mesh('model', '#d8b040ff', file='models/switch.obj'),
                    script('scripts/floorswitch.bs', id=id))

    def switchdoor(self, x, y, z, size, when, stay=False, yaw=0, material='flesh', color='#c86070ff'):
        tex = {'flesh': 'art/flesh.png', 'planks': 'art/planks.png', 'stone': 'art/stone.png'}[material]
        kw = {'when': when}
        if stay:
            kw['stay'] = True
        self.entity('Switch Door', t3((x, y + size[1] / 2, z), (0, yaw, 0), size), mesh('cube', color, tex, uv=(size[0], size[1])),
                    collider('box'), ('RigidBody3D', [('type', 'kinematic')]), script('scripts/switchdoor.bs', **kw))

    def tendril(self, x, y, z, id, set_='', count=3):
        self.entity('Tendril', t3((x, y, z)), mesh('model', '#e8d0b0ff', file='models/tendril.obj'), collider('capsule', (1, 2.4, 1), 0.25, offset=(0, -1.2, 0)),
                    tags('focusable'), script('scripts/tendril.bs', id=id, set=set_, count=count))

    def target(self, x, y, z, yaw=0):
        """A wooden target the Licorice Lash bites into (on a post or a wall)."""
        self.entity('Lash Target', t3((x, y, z), (0, yaw, 0), (0.8, 0.8, 0.25)), mesh('cube', '#c89058ff', 'art/planks.png'),
                    collider('box'), tags('hookable', 'focusable'), script('scripts/target.bs'))
        self.entity('Bullseye', t3((x - math.sin(math.radians(yaw)) * 0.14, y, z - math.cos(math.radians(yaw)) * 0.14), (90, yaw, 0), (0.45, 0.02, 0.45)),
                    mesh('cylinder', '#d03030ff', lit=False))

    def redice(self, x, y, z, size, id):
        self.entity('Red Ice', t3((x, y + size[1] / 2, z), (0, 0, 0), size), mesh('cube', '#ff6070c0', 'art/ice.png', uv=(size[0], size[1]), cull=False),
                    collider('box'), tags('redice', 'focusable'), script('scripts/redice.bs', id=id))

    def bluefire(self, x, y, z):
        self.geo('stone', x, z).cylinder((x, y, z), 0.6, 1.0, 8, uvs=0.5)
        self.entity('Blue Fire', t3((x, y + 1.1, z)), particles(rate=24, max=40, lifetime=0.8, speed=0.8, spread=20, area=(0.5, 0.5), gravity=-1.2,
                                                               size_start=0.45, size_end=0, color_start='#60a0ffff', color_end='#2040ff00', blend='add'),
                    light('point', '#6090ffff', 1.2, range=6), tags('bluefire'))

    def weevil(self, x, y, z, id, night=False):
        kw = {'id': id}
        if night:
            kw['night'] = True
        w = self.entity('Golden Weevil', t3((x, y, z), (0, 0, 0), 0.5), mesh('model', '#f0c030ff', file='models/bean.obj', lit=False),
                        collider('sphere', radius=0.6, trigger=True), tags('focusable', 'shootable'), script('scripts/weevil.bs', **kw))
        self.entity('Weevil Glint', t3((0, 0, 0)), ('Parent', [('entity', w)]), particles(rate=3, max=6, lifetime=0.8, speed=0.3, spread=90, size_start=0.15, size_end=0,
                                                           color_start='#fff0a0ff', color_end='#ffc00000', blend='add'))

    def hammerswitch(self, x, y, z, id):
        self.entity('Rusty Switch', t3((x, y, z)), mesh('model', '#a07050ff', file='models/switch.obj'), collider('box', (1.4, 0.3, 1.4), offset=(0, 0.0, 0)),
                    tags('focusable'), script('scripts/hammerswitch.bs', id=id))

    def point_light(self, x, y, z, color, intensity, range_):
        self.entity('Lamp', t3((x, y, z)), light('point', color, intensity, range=range_))


# ---- geometry helpers ----

def stump_house(a, x, z, ground, r=2.4, h=3.0, door_yaw=0, roof='thatch'):
    """A hollow-stump house: a bark cylinder, a cone roof, a door (a dark plank on the side
    facing door_yaw)."""
    y = ground(x, z) - 0.3
    a.geo('bark', x, z).cylinder((x, y, z), r, h + 0.3, 14, top=True, uvs=0.5)
    if roof:
        roof_on(a, x, z, y, r, h, roof)
    door(a, x, z, y, r, door_yaw)


def roof_on(a, x, z, y, r, h, roof):
    a.geo(roof, x, z).cylinder((x, y + h + 0.3, z), r + 0.6, 0.35, 14, top=False, bottom=True, radius_top=r + 0.4, uvs=0.5)   # (closed underneath: no sky through the eaves)
    a.geo(roof, x, z).cone((x, y + h + 0.65, z), r + 0.4, 2.0, 14, uvs=0.5)


def door(a, x, z, y, r, door_yaw):
    fx, fz = -math.sin(math.radians(door_yaw)), -math.cos(math.radians(door_yaw))
    dx, dz = x + fx * (r + 0.02), z + fz * (r + 0.02)
    a.entity('Door', t3((dx, y + 0.3 + 0.75, dz), (0, door_yaw, 0), (1.0, 1.5, 0.08)), mesh('cube', '#5a3a20ff', 'art/planks.png'))
    # a round window either side
    for side in (-1, 1):
        ang = math.radians(door_yaw + side * 55)
        wx, wz = x - math.sin(ang) * (r + 0.02), z - math.cos(ang) * (r + 0.02)
        a.entity('Window', t3((wx, y + 0.3 + 1.6, wz), (0, door_yaw + side * 55, 0), (0.55, 0.55, 0.06)),
                 mesh('cube', '#f8e8a0ff', lit=False, cast=False))


def box_wall(a, material, x0, z0, x1, z1, y0, y1, thick=0.6, uvs=0.5):
    """A straight wall from (x0, z0) to (x1, z1), from y0 up to y1."""
    dx, dz = x1 - x0, z1 - z0
    L = math.hypot(dx, dz)
    yaw = math.degrees(math.atan2(-dx, -dz))     # (the wall's length runs along its local -z)
    cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
    if abs(dx) > abs(dz):
        y1 += 0.01        # (walls running east-west a centimetre taller: where two walls cross at a corner, their tops don't flicker)
    a.geo(material, cx, cz).box((cx - thick / 2, y0, cz - L / 2), (cx + thick / 2, y1, cz + L / 2), uvs=uvs, rot_y=yaw, center=(cx, cz))


# ---- dungeon geometry: rooms are round, joined by square tunnels ----

def ring_floor(o, cx, cz, r0, r1, y, a0=0.0, a1=360.0, segs=24, thick=0.5, uvs=0.35, edges=True):
    """A flat ring (or disc, r0 = 0) at height y from angle a0 to a1 (degrees: 0 is +x, 90 is
    +z), with its edges as thick as `thick`."""
    n = max(1, int(segs * (a1 - a0) / 360.0 + 0.5))
    P = lambda r, a, yy: (cx + math.cos(math.radians(a)) * r, yy, cz + math.sin(math.radians(a)) * r)
    U = lambda p: (p[0] * uvs, p[2] * uvs)
    for i in range(n):
        aa, ab = a0 + (a1 - a0) * i / n, a0 + (a1 - a0) * (i + 1) / n
        # (seen from above, angle grows clockwise here: x right, z down)
        if r0 > 0:
            q = [P(r0, aa, y), P(r0, ab, y), P(r1, ab, y), P(r1, aa, y)]
            o.quad(q[0], q[1], q[2], q[3], U(q[0]), U(q[1]), U(q[2]), U(q[3]))
        else:
            c = (cx, y, cz)
            o.tri(c, P(r1, ab, y), P(r1, aa, y), U(c), U(P(r1, ab, y)), U(P(r1, aa, y)))
        if edges and thick > 0:
            lo = y - thick
            o.quad(P(r1, aa, lo), P(r1, aa, y), P(r1, ab, y), P(r1, ab, lo), (0, 0), (0, thick * uvs), (1, thick * uvs), (1, 0))
            if r0 > 0:
                o.quad(P(r0, ab, lo), P(r0, ab, y), P(r0, aa, y), P(r0, aa, lo), (0, 0), (0, thick * uvs), (1, thick * uvs), (1, 0))
            o.quad(P(r1, aa, lo), P(r1, ab, lo), P(r0 if r0 > 0 else 0.001, ab, lo), P(r0 if r0 > 0 else 0.001, aa, lo))
    if edges and thick > 0 and a1 - a0 < 360:
        for a in (a0, a1):
            p0, p1 = P(r0, a, y - thick), P(r1, a, y - thick)
            p2, p3 = P(r1, a, y), P(r0, a, y)
            if a == a0:
                o.quad(p0, p1, p2, p3)
            else:
                o.quad(p1, p0, p3, p2)


def ring_wall(o, cx, cz, r, y0, y1, segs=24, holes=(), uvs=0.3):
    """The inside wall of a round room, from y0 up to y1, facing in. holes: (angle,
    half-width in units, y bottom, y top) - doorways."""
    step = 360.0 / segs
    off = 0.0
    if holes:                     # (turned so the first doorway is in the middle of a segment)
        off = (holes[0][0] % step) - step / 2
    for i in range(segs):
        aa, ab = off + step * i, off + step * (i + 1)
        mid = (aa + ab) / 2
        spans = [(y0, y1)]
        for ha, hw, hy0, hy1 in holes:
            d = abs(((mid - ha + 180) % 360) - 180)
            if math.radians(d) * r < hw:
                new = []
                for s0, s1 in spans:
                    if hy0 > s0:
                        new.append((s0, min(s1, hy0)))
                    if hy1 < s1:
                        new.append((max(s0, hy1), s1))
                spans = new
        for s0, s1 in spans:
            if s1 - s0 < 0.01:
                continue
            P = lambda a, yy: (cx + math.cos(math.radians(a)) * r, yy, cz + math.sin(math.radians(a)) * r)
            u0, u1 = math.radians(aa) * r * uvs, math.radians(ab) * r * uvs
            # facing the middle
            o.quad(P(aa, s0), P(ab, s0), P(ab, s1), P(aa, s1), (u0, s0 * uvs), (u1, s0 * uvs), (u1, s1 * uvs), (u0, s1 * uvs))


def ceiling_disc(o, cx, cz, r, y, hole=0.0, segs=24, uvs=0.3):
    """A ceiling (facing down), with an optional hole in the middle."""
    P = lambda rr, a: (cx + math.cos(math.radians(a)) * rr, y, cz + math.sin(math.radians(a)) * rr)
    for i in range(segs):
        aa, ab = 360.0 * i / segs, 360.0 * (i + 1) / segs
        if hole > 0:
            o.quad(P(hole, ab), P(hole, aa), P(r, aa), P(r, ab))
        else:
            o.tri((cx, y, cz), P(r, aa), P(r, ab))


def tunnel(o_floor, o_wall, x0, z0, x1, z1, y, w=2.4, h=2.8, uvs=0.35, ceiling=True):
    """A straight square tunnel between two points (open at both ends), floor at y."""
    dx, dz = x1 - x0, z1 - z0
    L = math.hypot(dx, dz)
    ux, uz = dx / L, dz / L
    px, pz = -uz * w / 2, ux * w / 2
    A, B = (x0, z0), (x1, z1)
    def p(c, side, yy):
        return (c[0] + px * side, yy, c[1] + pz * side)
    # floor (facing up): a centimetre down, so where its ends reach into a room's floor the
    # two don't lie in one plane and flicker against each other
    yf = y - 0.01
    q = [p(A, 1, yf), p(B, 1, yf), p(B, -1, yf), p(A, -1, yf)]
    if (q[1][0] - q[0][0]) * (q[2][2] - q[0][2]) - (q[1][2] - q[0][2]) * (q[2][0] - q[0][0]) > 0:
        q = q[::-1]
    o_floor.quad(*q, *[(v[0] * uvs, v[2] * uvs) for v in q])
    o_floor.box((min(x0, x1) - abs(px), y - 0.5, min(z0, z1) - abs(pz)), (max(x0, x1) + abs(px), yf, max(z0, z1) + abs(pz)), sides=('ny',))
    # walls (facing in) and a ceiling (facing down)
    for side in (1, -1):
        w0, w1 = p(A, side, y), p(B, side, y)
        quad = [w0, w1, (w1[0], y + h, w1[2]), (w0[0], y + h, w0[2])]
        # face inwards: towards the middle line
        n = ((quad[1][1] - quad[0][1]) * (quad[2][2] - quad[0][2]) - (quad[1][2] - quad[0][2]) * (quad[2][1] - quad[0][1]),
             0, 0)
        e1 = [quad[1][i] - quad[0][i] for i in range(3)]
        e2 = [quad[2][i] - quad[0][i] for i in range(3)]
        nx = e1[1] * e2[2] - e1[2] * e2[1]
        nz = e1[0] * e2[1] - e1[1] * e2[0]
        if nx * (-px * side) + nz * (-pz * side) < 0:
            quad = quad[::-1]
        o_wall.quad(*quad, (0, 0), (L * uvs, 0), (L * uvs, h * uvs), (0, h * uvs))
    if ceiling:
        q = [p(A, 1, y + h), p(B, 1, y + h), p(B, -1, y + h), p(A, -1, y + h)]
        if (q[1][0] - q[0][0]) * (q[2][2] - q[0][2]) - (q[1][2] - q[0][2]) * (q[2][0] - q[0][0]) < 0:
            q = q[::-1]
        o_wall.quad(*q, *[(v[0] * uvs, v[2] * uvs) for v in q])


def castle_skyline(a, x, y, z, s=1.0):
    """Castle Larder seen from afar: a keep, four corner towers and a tall middle one, with
    blue roofs. Scenery only (nothing to touch): stood out past an area's edge as a landmark."""
    st, rf = a.geo('far_stone', x, z), a.geo('far_roof', x, z)
    st.box((x - 12 * s, y - 4, z - 9 * s), (x + 12 * s, y + 22 * s, z + 9 * s), uvs=0.08)          # the keep
    for k in range(-5, 6, 2):                                                                     # its battlements (south face)
        st.box((x + k * 2 * s - 0.9 * s, y + 22 * s, z + 8 * s), (x + k * 2 * s + 0.9 * s, y + 24 * s, z + 9.01 * s), uvs=0.2)
    for dx, dz in [(-13, -10), (13, -10), (-13, 10), (13, 10)]:                                   # the corner towers
        tx, tz = x + dx * s, z + dz * s
        st.cylinder((tx, y - 4, tz), 4 * s, 34 * s + 4, 10, uvs=0.08)                            # (its top at y + 34 s ...)
        rf.cone((tx, y + 34 * s + 0.02, tz), 5 * s, 9 * s, 10, uvs=0.1)                           # (... and the roof on it, overhanging)
    st.cylinder((x, y + 20 * s, z), 5 * s, 22 * s, 12, uvs=0.08)                                   # the great tower
    rf.cone((x, y + 42 * s, z), 6.5 * s, 14 * s, 12, uvs=0.1)


def town_house(a, x, z, w, d, h, ground_y, wall='planks', roof='thatch', door_side='s', roof_h=None):
    """A box house (w along x, d along z) with a pitched roof (ridge along x) and a door on
    one side ('n', 's', 'e', 'w')."""
    y = ground_y - 0.3
    x0, x1, z0, z1 = x - w / 2, x + w / 2, z - d / 2, z + d / 2
    a.geo(wall, x, z).box((x0, y, z0), (x1, y + h + 0.3, z1), uvs=0.4, sides=('px', 'nx', 'pz', 'nz'))
    rh = roof_h if roof_h else d * 0.45
    top = y + h + 0.3
    o = a.geo(roof, x, z)
    e = 0.4                      # the eaves
    A, B = (x0 - e, top - 0.2, z0 - e), (x1 + e, top - 0.2, z0 - e)
    C, D = (x1 + e, top - 0.2, z1 + e), (x0 - e, top - 0.2, z1 + e)
    R0, R1 = (x0 - e, top + rh, z), (x1 + e, top + rh, z)
    s = 0.35
    o.quad(A, R0, R1, B, (0, 0), (0, rh * s * 2), (w * s, rh * s * 2), (w * s, 0))          # north slope (faces -z, up)
    o.quad(C, R1, R0, D, (0, 0), (0, rh * s * 2), (w * s, rh * s * 2), (w * s, 0))          # south slope
    g = a.geo(wall, x, z)
    g.tri((x0, top, z0), (x0, top, z1), (x0, top + rh - 0.1, z))                              # gables
    g.tri((x1, top, z1), (x1, top, z0), (x1, top + rh - 0.1, z))
    door_at = {'s': (x, z1 + 0.03, 180), 'n': (x, z0 - 0.03, 0), 'e': (x1 + 0.03, z, -90), 'w': (x0 - 0.03, z, 90)}[door_side]
    a.entity('Door', t3((door_at[0], y + 0.3 + 0.9, door_at[1]), (0, door_at[2], 0), (1.1, 1.8, 0.08)), mesh('cube', '#5a3a20ff', 'art/planks.png'))
    for side in (-1, 1):
        if door_side in 'ns':
            wx, wz = x + side * w * 0.3, door_at[1]
        else:
            wx, wz = door_at[0], z + side * d * 0.3
        a.entity('Window', t3((wx, y + 0.3 + 1.6, wz), (0, door_at[2], 0), (0.7, 0.6, 0.06)), mesh('cube', '#f8e8a0ff', lit=False, cast=False))


def stall(a, x, z, ground_y, color, yaw=0):
    """A market stall: a counter and a striped awning."""
    y = ground_y
    a.entity('Stall', t3((x, y + 0.5, z), (0, yaw, 0), (2.6, 1.0, 0.9)), mesh('cube', '#ffffffff', 'art/planks.png'), collider('box'))
    a.entity('Awning', t3((x, y + 2.4, z + (0.4 if yaw == 0 else -0.4)), (-14 if yaw == 0 else 14, yaw, 0), (3.0, 0.1, 2.0)), mesh('cube', color, 'art/thatch.png'))
    for dx in (-1.3, 1.3):
        a.entity('Pole', t3((x + dx, y + 1.2, z), (0, 0, 0), (0.1, 2.4, 0.1)), mesh('cylinder', '#ffffffff', 'art/bark.png'))


# The helpers that set something on the ground at y: it is moved onto the ground as drawn
# (Area.on_ground) when y was meant for it, so nothing floats or sinks where the ground's
# triangles part from the curve they were made from.
def _grounded(fn, off=0.0):
    sig = inspect.signature(fn)

    def wrapper(self, *args, **kw):
        b = sig.bind(self, *args, **kw)
        b.arguments['y'] = self.on_ground(b.arguments['x'], b.arguments['y'], b.arguments['z'], off)
        return fn(*b.args, **b.kwargs)
    wrapper.__doc__ = fn.__doc__
    return wrapper


for _name in ('tree', 'grass', 'pot', 'sign', 'npc', 'chest', 'enemy', 'bombflower', 'dummy', 'cracked'):
    setattr(Area, _name, _grounded(getattr(Area, _name)))
Area.spawn_point = _grounded(Area.spawn_point, off=0.1)
