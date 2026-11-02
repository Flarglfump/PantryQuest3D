"""Pantry Quest 3D's content kit: everything the tools need to write the game's files,
using only Python's standard library.

- Scene: writes Bronto .scene files (entities and their components).
- Obj: builds Wavefront .obj meshes from boxes, cylinders, cones, heightfields...
- write_png: writes RGB(A) PNG textures from a pixel function.
"""
import math
import os
import struct
import zlib

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))


# The heightfields made since the last reset (Obj.ground): ground_height() reads the ground as it
# is drawn, its triangles, not the smooth function behind them (things set on the function float
# over hollows and sink into rises).
GROUNDS = []


def ground_height(x, z, default=None):
    """The drawn ground's height at x, z (the last heightfield made that covers it), or default."""
    for (x0, z0, x1, z1, nx, nz, height, keep) in reversed(GROUNDS):
        if not (x0 <= x <= x1 and z0 <= z <= z1):
            continue
        sx, sz = (x1 - x0) / nx, (z1 - z0) / nz
        i, j = min(nx - 1, int((x - x0) / sx)), min(nz - 1, int((z - z0) / sz))
        xa, za = x0 + i * sx, z0 + j * sz
        if keep and not keep(xa + sx / 2, za + sz / 2):
            continue
        fx, fz = (x - xa) / sx, (z - za) / sz
        h00, h11 = height(xa, za), height(xa + sx, za + sz)
        if fz >= fx:                     # (each cell split from its corner (x0, z0) to (x1, z1))
            h01 = height(xa, za + sz)
            return h00 + (h11 - h01) * fx + (h01 - h00) * fz
        h10 = height(xa + sx, za)
        return h00 + (h10 - h00) * fx + (h11 - h10) * fz
    return default


def drawn(height):
    """height(x, z), but the ground as drawn where a heightfield covers x, z (ground_height):
    for setting things on the ground, so they stand on it, not on the curve behind it."""
    height = getattr(height, 'original', height)

    def f(x, z):
        h = ground_height(x, z)
        return height(x, z) if h is None else h
    f.original = height
    return f


def ground_triangles(xa, za, xb, zb):
    """The drawn ground's triangles (each [(x, y, z) * 3], counter-clockwise from above) over the
    rectangle xa..xb, za..zb, with the height function behind each (for normals). Where two
    heightfields overlap, the one made last."""
    seen = set()
    for gi in range(len(GROUNDS) - 1, -1, -1):
        (x0, z0, x1, z1, nx, nz, height, keep) = GROUNDS[gi]
        sx, sz = (x1 - x0) / nx, (z1 - z0) / nz
        i0, i1 = max(0, int(math.floor((xa - x0) / sx))), min(nx - 1, int(math.floor((xb - x0) / sx)))
        j0, j1 = max(0, int(math.floor((za - z0) / sz))), min(nz - 1, int(math.floor((zb - z0) / sz)))
        for j in range(j0, j1 + 1):
            for i in range(i0, i1 + 1):
                cxa, cza = x0 + i * sx, z0 + j * sz
                mid = (round(cxa + sx / 2, 3), round(cza + sz / 2, 3))
                if keep and not keep(*mid):
                    continue
                if any(ox0 <= mid[0] <= ox1 and oz0 <= mid[1] <= oz1 for (ox0, oz0, ox1, oz1) in seen):
                    continue                     # (a later heightfield's ground there)
                P = [(x, height(x, z), z) for x, z in [(cxa, cza), (cxa, cza + sz), (cxa + sx, cza + sz), (cxa + sx, cza)]]
                yield [P[0], P[1], P[2]], height
                yield [P[0], P[2], P[3]], height
        seen.add((x0, z0, x1, z1))


def path(*parts):
    p = os.path.join(ROOT, *parts)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


# ---- PNG ------------------------------------------------------------------------------------

def write_png(file, w, h, pixel, alpha=False):
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        for x in range(w):
            c = pixel(x, y)
            c = tuple(max(0, min(255, int(v))) for v in c)
            if alpha:
                raw += bytes(c if len(c) == 4 else c + (255,))
            else:
                raw += bytes(c[:3])

    def chunk(kind, body):
        return struct.pack('>I', len(body)) + kind + body + struct.pack('>I', zlib.crc32(kind + body) & 0xffffffff)
    with open(path(file), 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6 if alpha else 2, 0, 0, 0)) +
                chunk(b'IDAT', zlib.compress(bytes(raw), 9)) + chunk(b'IEND', b''))


def hash2(x, y, seed=0):
    """A repeatable pseudo-random number 0..1 for integer x, y."""
    n = (x * 374761393 + y * 668265263 + seed * 2147483647) & 0xffffffff
    n = ((n ^ (n >> 13)) * 1274126177) & 0xffffffff
    return ((n ^ (n >> 16)) & 0xffff) / 65535.0


def vnoise(x, y, scale, seed=0, wrap=None):
    """Smooth value noise at x, y with cells `scale` pixels across (wraps every `wrap` cells)."""
    fx, fy = x / scale, y / scale
    ix, iy = int(math.floor(fx)), int(math.floor(fy))
    tx, ty = fx - ix, fy - iy
    tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)

    def h(a, b):
        if wrap:
            a, b = a % wrap, b % wrap
        return hash2(a, b, seed)
    a = h(ix, iy) + (h(ix + 1, iy) - h(ix, iy)) * tx
    b = h(ix, iy + 1) + (h(ix + 1, iy + 1) - h(ix, iy + 1)) * tx
    return a + (b - a) * ty


def mix(c0, c1, t):
    return tuple(c0[i] + (c1[i] - c0[i]) * t for i in range(len(c0)))


# ---- scenes ---------------------------------------------------------------------------------

def fmt(v):
    if isinstance(v, bool):
        return 'true' if v else 'false'
    if isinstance(v, (int, float)):
        s = ('%.4f' % v).rstrip('0').rstrip('.')
        return '0' if s in ('-0', '') else s
    if isinstance(v, tuple):
        return ' '.join(fmt(c) for c in v)
    return v


def q(s):
    """A quoted string field."""
    return '"%s"' % s


class Scene:
    def __init__(self, comment):
        self.lines = ['# ' + line for line in comment.split('\n')] + ['bronto_scene 1', '']
        self.count = 0

    def entity(self, name, *components):
        """Adds an entity; components are (name, [(field, value), ...]). Returns its index."""
        self.lines.append('entity')
        self.lines.append('  Name')
        self.lines.append('    text = "%s"' % name)
        for comp, fields in components:
            if comp is None:
                continue
            self.lines.append('  ' + comp)
            for k, v in fields:
                self.lines.append('    %s = %s' % (k, fmt(v)))
        self.lines.append('')
        self.count += 1
        return self.count - 1

    def save(self, file):
        with open(path(file), 'w') as f:
            f.write('\n'.join(self.lines))


def t3(pos, rot=(0, 0, 0), scale=(1, 1, 1)):
    if isinstance(scale, (int, float)):
        scale = (scale, scale, scale)
    return ('Transform3D', [('position', tuple(pos)), ('rotation', tuple(rot)), ('scale', tuple(scale))])


def t2(pos=(0, 0)):
    return ('Transform', [('position', tuple(pos))])


def mesh(shape, color='#ffffffff', texture='', uv=(1, 1), file='', shadow=False, lit=True, cull=True, cast=True, visible=True):
    f = [('shape', shape)]
    if file:
        f.append(('file', q(file)))
    if texture:
        f.append(('texture', q(texture)))
    f += [('color', color), ('uv_scale', tuple(uv))]
    if shadow:
        f.append(('shadow', True))
    if not lit:
        f.append(('lit', False))
    if not cull:
        f.append(('cull', False))
    if not cast:
        f.append(('cast_shadow', False))
    if not visible:
        f.append(('visible', False))
    return ('Mesh', f)


def collider(shape, size=(1, 1, 1), radius=0.5, trigger=False, offset=None, friction=0.8, layer=None, mask=None):
    f = [('shape', shape), ('size', tuple(size)), ('radius', radius), ('friction', friction)]
    if offset:
        f.append(('offset', tuple(offset)))
    if trigger:
        f.append(('trigger', True))
    if layer is not None:
        f.append(('layer', layer))
    if mask is not None:
        f.append(('mask', mask))
    return ('Collider3D', f)


def kinematic():
    return ('RigidBody3D', [('type', 'kinematic')])


def tags(*names):
    return ('Tags', [('list', q(', '.join(names)))])


def script(file, **vars):
    f = [('file', q(file))]
    if vars:
        parts = []
        for k, v in vars.items():
            parts.append('%s = %s' % (k, svar(v)))
        f.append(('vars', q(', '.join(parts).replace('\\', '\\\\').replace('"', '\\"'))))
    return ('Script', f)


def svar(v):
    if isinstance(v, bool):
        return 'true' if v else 'false'
    if isinstance(v, str):
        return '"%s"' % v
    if isinstance(v, (int, float)):
        return fmt(v)
    if isinstance(v, tuple):
        return ('vec%d(' % len(v)) + ', '.join(fmt(c) for c in v) + ')'
    if isinstance(v, list):
        return '[' + ', '.join(svar(x) for x in v) + ']'
    raise ValueError(v)


def particles(**f):
    return ('Particles', [(k, v) for k, v in f.items()])


def light(kind, color, intensity, **more):
    f = [('kind', kind), ('color', color), ('intensity', intensity)]
    f += list(more.items())
    return ('Light', f)


# ---- meshes ---------------------------------------------------------------------------------

class Obj:
    """A mesh being built: triangles with positions, texture coordinates and normals.
    Faces are counter-clockwise seen from the front. uv_per_unit maps world units to texture
    repeats for the world-space mapped shapes (box faces, ground)."""

    def __init__(self, comment=''):
        self.comment = comment
        self.v, self.vt, self.vn, self.f = [], [], [], []
        self.ground_faces = []           # [(first, end)]: faces made by ground() (not things built on it)

    def surface_near(self, x, z, y, tol):
        """Whether an upward face (not the ground's) passes within tol of height y at x, z."""
        skip = self.ground_faces
        for k, face in enumerate(self.f):
            if any(a <= k < b for a, b in skip):
                continue
            a, b, c = (self.v[face[i][0] - 1] for i in range(3))
            d = (b[2] - c[2]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[2] - c[2])
            if abs(d) < 1e-9:
                continue                 # (edge-on from above: a wall)
            l1 = ((b[2] - c[2]) * (x - c[0]) + (c[0] - b[0]) * (z - c[2])) / d
            l2 = ((c[2] - a[2]) * (x - c[0]) + (a[0] - c[0]) * (z - c[2])) / d
            l3 = 1 - l1 - l2
            if min(l1, l2, l3) < -1e-6:
                continue
            if abs(l1 * a[1] + l2 * b[1] + l3 * c[1] - y) <= tol:
                return True
        return False

    def empty(self):
        return not self.f

    def add_backs(self):
        """For a model shown one side only: each open face (one with an edge no other face
        shares the other way round: a pot's rim, a sail, a sheet) gets a back face as well,
        turned round with its normal reversed, so it's there seen from behind too."""
        key = lambda i: tuple(round(c, 3) for c in self.v[i - 1])
        edges = set()
        for f in self.f:
            P = [key(c[0]) for c in f]
            for i in range(3):
                edges.add((P[i], P[(i + 1) % 3]))
        for f in list(self.f):
            P = [key(c[0]) for c in f]
            if all((P[(i + 1) % 3], P[i]) in edges for i in range(3)):
                continue
            a, b, c = f
            n = lambda k: tuple(-x for x in self.vn[k[2] - 1])
            self.tri(self.v[a[0] - 1], self.v[c[0] - 1], self.v[b[0] - 1], self.vt[a[1] - 1], self.vt[c[1] - 1], self.vt[b[1] - 1], n(a), n(c), n(b))

    def tri_count(self):
        return len(self.f)

    def _v(self, p):
        self.v.append(p)
        return len(self.v)

    def _t(self, uv):
        self.vt.append(uv)
        return len(self.vt)

    def _n(self, n):
        l = math.sqrt(n[0] ** 2 + n[1] ** 2 + n[2] ** 2) or 1
        self.vn.append((n[0] / l, n[1] / l, n[2] / l))
        return len(self.vn)

    def tri(self, a, b, c, ua=(0, 0), ub=(1, 0), uc=(1, 1), na=None, nb=None, nc=None):
        if na is None:
            e1 = [b[i] - a[i] for i in range(3)]
            e2 = [c[i] - a[i] for i in range(3)]
            n = (e1[1] * e2[2] - e1[2] * e2[1], e1[2] * e2[0] - e1[0] * e2[2], e1[0] * e2[1] - e1[1] * e2[0])
            if n == (0, 0, 0):
                return
            na = nb = nc = n
        ia, ib, ic = self._v(a), self._v(b), self._v(c)
        ta, tb, tc = self._t(ua), self._t(ub), self._t(uc)
        ka, kb, kc = self._n(na), self._n(nb), self._n(nc)
        self.f.append(((ia, ta, ka), (ib, tb, kb), (ic, tc, kc)))

    def quad(self, a, b, c, d, ua=(0, 0), ub=(1, 0), uc=(1, 1), ud=(0, 1)):
        self.tri(a, b, c, ua, ub, uc)
        self.tri(a, c, d, ua, uc, ud)

    def box(self, lo, hi, uvs=0.5, sides=('px', 'nx', 'py', 'ny', 'pz', 'nz'), rot_y=0, center=None):
        """An axis-aligned box from lo to hi (optionally turned rot_y degrees about `center`).
        Textures map world-space: uvs repeats per unit."""
        x0, y0, z0 = lo
        x1, y1, z1 = hi
        cx, cz = center if center else ((x0 + x1) / 2, (z0 + z1) / 2)
        ca, sa = math.cos(math.radians(rot_y)), math.sin(math.radians(rot_y))

        def R(p):
            dx, dz = p[0] - cx, p[2] - cz
            return (cx + dx * ca + dz * sa, p[1], cz - dx * sa + dz * ca)
        s = uvs
        F = {
            'pz': ([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], lambda p: (p[0] * s, p[1] * s)),
            'nz': ([(x1, y0, z0), (x0, y0, z0), (x0, y1, z0), (x1, y1, z0)], lambda p: (-p[0] * s, p[1] * s)),
            'px': ([(x1, y0, z1), (x1, y0, z0), (x1, y1, z0), (x1, y1, z1)], lambda p: (-p[2] * s, p[1] * s)),
            'nx': ([(x0, y0, z0), (x0, y0, z1), (x0, y1, z1), (x0, y1, z0)], lambda p: (p[2] * s, p[1] * s)),
            'py': ([(x0, y1, z1), (x1, y1, z1), (x1, y1, z0), (x0, y1, z0)], lambda p: (p[0] * s, -p[2] * s)),
            'ny': ([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], lambda p: (p[0] * s, p[2] * s)),
        }
        for side in sides:
            quad, uvf = F[side]
            self.quad(*[R(p) for p in quad], *[uvf(p) for p in quad])

    def cylinder(self, base, radius, height, segs=10, top=True, bottom=False, uvs=0.5, inside=False, radius_top=None, smooth=True):
        """A cylinder (or frustum, with radius_top) standing on `base`. inside: faces point in."""
        bx, by, bz = base
        rt = radius if radius_top is None else radius_top
        circ = 2 * math.pi * radius
        for i in range(segs):
            a0, a1 = 2 * math.pi * i / segs, 2 * math.pi * (i + 1) / segs
            p00 = (bx + math.cos(a0) * radius, by, bz - math.sin(a0) * radius)
            p10 = (bx + math.cos(a1) * radius, by, bz - math.sin(a1) * radius)
            p01 = (bx + math.cos(a0) * rt, by + height, bz - math.sin(a0) * rt)
            p11 = (bx + math.cos(a1) * rt, by + height, bz - math.sin(a1) * rt)
            u0, u1 = circ * i / segs * uvs, circ * (i + 1) / segs * uvs
            v0, v1 = 0, height * uvs
            slope = (radius - rt) / height if height else 0
            n0 = (math.cos(a0), slope, -math.sin(a0))
            n1 = (math.cos(a1), slope, -math.sin(a1))
            if inside:
                n0 = (-n0[0], -n0[1], -n0[2]); n1 = (-n1[0], -n1[1], -n1[2])
                if smooth:
                    self.tri(p00, p11, p10, (u0, v0), (u1, v1), (u1, v0), n0, n1, n1)
                    self.tri(p00, p01, p11, (u0, v0), (u0, v1), (u1, v1), n0, n0, n1)
                else:
                    self.quad(p00, p01, p11, p10, (u0, v0), (u0, v1), (u1, v1), (u1, v0))
            else:
                if smooth:
                    self.tri(p00, p10, p11, (u0, v0), (u1, v0), (u1, v1), n0, n1, n1)
                    self.tri(p00, p11, p01, (u0, v0), (u1, v1), (u0, v1), n0, n1, n0)
                else:
                    self.quad(p00, p10, p11, p01, (u0, v0), (u1, v0), (u1, v1), (u0, v1))
            if top and rt > 0:
                c = (bx, by + height, bz)
                uv = lambda p: ((p[0] - bx) * uvs, (bz - p[2]) * uvs)
                if inside:
                    self.tri(c, p11, p01, uv(c), uv(p11), uv(p01))
                else:
                    self.tri(c, p01, p11, uv(c), uv(p01), uv(p11))
            if bottom:
                c = (bx, by, bz)
                uv = lambda p: ((p[0] - bx) * uvs, (p[2] - bz) * uvs)
                self.tri(c, p10, p00, uv(c), uv(p10), uv(p00))

    def cone(self, base, radius, height, segs=10, uvs=0.5):
        self.cylinder(base, radius, height, segs, top=False, bottom=True, uvs=uvs, radius_top=0.0001)

    def sphere(self, center, radius, segs=10, rings=6, squash=1.0, uvs=1.0):
        cx, cy, cz = center
        for j in range(rings):
            b0, b1 = math.pi * j / rings - math.pi / 2, math.pi * (j + 1) / rings - math.pi / 2
            for i in range(segs):
                a0, a1 = 2 * math.pi * i / segs, 2 * math.pi * (i + 1) / segs

                def P(a, b):
                    n = (math.cos(b) * math.cos(a), math.sin(b), -math.cos(b) * math.sin(a))
                    return (cx + n[0] * radius, cy + n[1] * radius * squash, cz + n[2] * radius), n
                (p00, n00), (p10, n10), (p01, n01), (p11, n11) = P(a0, b0), P(a1, b0), P(a0, b1), P(a1, b1)
                u0, u1, v0, v1 = i / segs * uvs, (i + 1) / segs * uvs, j / rings * uvs, (j + 1) / rings * uvs
                if j > 0:
                    self.tri(p00, p10, p11, (u0, v0), (u1, v0), (u1, v1), n00, n10, n11)
                if j < rings - 1:
                    self.tri(p00, p11, p01, (u0, v0), (u1, v1), (u0, v1), n00, n11, n01)

    def ground(self, x0, z0, x1, z1, cells_x, cells_z, height, uvs=0.25, keep=None):
        """A heightfield over a rectangle: height(x, z) gives y. keep(x, z) can drop cells
        (for holes). Normals are smoothed from the height function."""
        sx, sz = (x1 - x0) / cells_x, (z1 - z0) / cells_z
        height = getattr(height, 'original', height)          # (the curve itself, not drawn(): see below)
        GROUNDS.append((x0, z0, x1, z1, cells_x, cells_z, height, keep))
        first = len(self.f)

        def N(x, z):
            e = 0.1
            nx = height(x - e, z) - height(x + e, z)
            nz = height(x, z - e) - height(x, z + e)
            return (nx, 2 * e, nz)
        for j in range(cells_z):
            for i in range(cells_x):
                xa, xb = x0 + i * sx, x0 + (i + 1) * sx
                za, zb = z0 + j * sz, z0 + (j + 1) * sz
                if keep and not keep((xa + xb) / 2, (za + zb) / 2):
                    continue
                pts = [(xa, za), (xa, zb), (xb, zb), (xb, za)]       # ccw seen from above (+y): a, c, d, b
                P = [(x, height(x, z), z) for x, z in pts]
                U = [(x * uvs, -z * uvs) for x, z in pts]
                Nn = [N(x, z) for x, z in pts]
                self.tri(P[0], P[1], P[2], U[0], U[1], U[2], Nn[0], Nn[1], Nn[2])
                self.tri(P[0], P[2], P[3], U[0], U[2], U[3], Nn[0], Nn[2], Nn[3])
        self.ground_faces.append((first, len(self.f)))

    def bounds(self):
        if not self.v:
            return (0, 0, 0), (0, 0, 0)
        return tuple(min(p[k] for p in self.v) for k in range(3)), tuple(max(p[k] for p in self.v) for k in range(3))

    def text(self):
        out = ['# ' + self.comment] if self.comment else []
        out += ['v %.4f %.4f %.4f' % p for p in self.v]
        out += ['vt %.4f %.4f' % t for t in self.vt]
        out += ['vn %.4f %.4f %.4f' % n for n in self.vn]
        for f in self.f:
            out.append('f ' + ' '.join('%d/%d/%d' % c for c in f))
        return '\n'.join(out) + '\n'

    def save(self, file):
        with open(path(file), 'w') as fp:
            fp.write(self.text())


class Chunked:
    """Static level geometry, split by material and into square chunks (so the renderer can
    skip chunks that are out of view). add(material, fn) calls fn(obj) with the chunk's Obj
    for a point: chunk_of(x, z)."""

    def __init__(self, chunk=24.0):
        self.chunk = chunk
        self.objs = {}

    def at(self, material, x, z):
        key = (material, int(math.floor(x / self.chunk)), int(math.floor(z / self.chunk)))
        if key not in self.objs:
            self.objs[key] = Obj('%s chunk %d %d' % key)
        return self.objs[key]

    def items(self):
        return sorted(self.objs.items())
