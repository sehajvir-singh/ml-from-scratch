"""Mini-ARC: five synthetic grid puzzles that every model in the arena is trained on.

Each task maps a 10x10 input grid (colors 0-9, 0 = background) to an output grid.
The tasks are chosen to need different kinds of "reasoning":

    recolor  - purely local, per-cell rule          (1 cell of context)
    outline  - local neighbourhood rule             (3x3 context)
    flip     - global geometry, mirror left/right   (whole row of context)
    gravity  - iterative, cells fall to the bottom  (whole column, order matters)
    flood    - iterative long-range search          (whole grid, path-dependent)
"""
from collections import deque

import numpy as np

H = W = 10
N_COLORS = 10
TASKS = ["recolor", "outline", "flip", "gravity", "flood"]

# Fixed colour permutation for `recolor` (background 0 stays 0).
_PERM = np.array([0, 4, 7, 1, 9, 2, 8, 3, 6, 5])


def _scatter(rng, density):
    g = np.zeros((H, W), dtype=np.int64)
    mask = rng.random((H, W)) < density
    g[mask] = rng.integers(1, N_COLORS, size=mask.sum())
    return g


def _rects(rng):
    g = np.zeros((H, W), dtype=np.int64)
    for _ in range(rng.integers(1, 4)):
        h, w = rng.integers(3, 7, size=2)
        r, c = rng.integers(0, H - h + 1), rng.integers(0, W - w + 1)
        g[r:r + h, c:c + w] = rng.integers(1, N_COLORS)
    return g


def recolor(rng):
    x = _scatter(rng, rng.uniform(0.2, 0.6))
    return x, _PERM[x]


def outline(rng):
    x = _rects(rng)
    p = np.pad(x, 1, constant_values=-1)
    same = np.ones_like(x, dtype=bool)
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        same &= p[1 + dr:1 + dr + H, 1 + dc:1 + dc + W] == x
    y = np.where(same, 0, x)
    return x, y


def flip(rng):
    x = _scatter(rng, rng.uniform(0.2, 0.5))
    return x, x[:, ::-1].copy()


def gravity(rng):
    x = _scatter(rng, rng.uniform(0.15, 0.4))
    y = np.zeros_like(x)
    for c in range(W):
        col = x[:, c][x[:, c] != 0]
        if len(col):
            y[H - len(col):, c] = col
    return x, y


WALL, SEED = 5, 3


def flood(rng):
    x = np.where(rng.random((H, W)) < rng.uniform(0.25, 0.4), WALL, 0)
    empty = np.argwhere(x == 0)
    r, c = empty[rng.integers(len(empty))]
    x[r, c] = SEED
    y = x.copy()
    q = deque([(r, c)])
    while q:
        r, c = q.popleft()
        for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
            if 0 <= nr < H and 0 <= nc < W and y[nr, nc] == 0:
                y[nr, nc] = SEED
                q.append((nr, nc))
    return x, y


_GEN = {"recolor": recolor, "outline": outline, "flip": flip, "gravity": gravity, "flood": flood}


def sample_batch(rng, batch_size, tasks=TASKS):
    """Returns (x, y, task_id) as int64 numpy arrays of shape [B,H,W], [B,H,W], [B]."""
    ids = rng.integers(0, len(tasks), size=batch_size)
    xs, ys = zip(*(_GEN[tasks[i]](rng) for i in ids))
    return np.stack(xs), np.stack(ys), ids


def fixed_test_set(n_per_task=200, seed=12345):
    rng = np.random.default_rng(seed)
    xs, ys, ids = [], [], []
    for i, t in enumerate(TASKS):
        for _ in range(n_per_task):
            x, y = _GEN[t](rng)
            xs.append(x), ys.append(y), ids.append(i)
    return np.stack(xs), np.stack(ys), np.array(ids)
