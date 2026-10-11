"""7. RSCA - Rule-Search Cellular Automaton  (new, training-free)

No gradient descent, no fixed parameters. Given a few demonstration pairs (input -> output) of
an unknown puzzle, RSCA *searches* for a cellular-automaton rule that explains all of them, then
runs that rule on the new input. Its "parameters" are the rule table it writes at test time, so
its size grows with the problem instead of being fixed in advance (nonparametric).

A hypothesis has four parts, searched from simplest to most complex (Occam's razor):

  view         what each cell looks at: itself, up/down, left/right, its 4 neighbours,
               or the cell at its mirror position (left-right, up-down, transposed, rotated).
  abstraction  how the view becomes a rule key:
                 role    colour-agnostic: each neighbour is "same as me / zero / other / edge"
                 raw     exact colours
                 rawset  my colour + the *set* of colours around me
  op           what a cell becomes: copy one of the cells it looks at, or a constant colour.
  mode         single  - apply the rule once
               iterate - apply it again and again until nothing changes (a fixed point)

Three ways to learn the rule table:
  1. single-step induction: every cell with the same key must have one op that explains its
     target. If some key needs two different ops, the hypothesis is rejected.
  2. iterate-to-target: grow the table while simulating, assigning a key only when every cell
     holding it agrees on its *final* target. This learns "spreading" rules such as flood fill.
  3. hill-climb (role tables only): edit table entries, single edits then pairs, to cut the
     mismatch after running to a fixed point. This learns "motion" rules such as gravity, where
     cells only reach their target after many steps.

A hypothesis is accepted only if it reproduces EVERY demonstration exactly.
"""
import itertools

import numpy as np

EDGE = -1
MAX_STEPS = 25


# ---------------------------------------------------------------- views: [n,H,W] -> [n,H,W,S]
def _shift(g, dr, dc):
    out = np.full_like(g, EDGE)
    n, H, W = g.shape
    rs, re = max(dr, 0), H + min(dr, 0)
    cs, ce = max(dc, 0), W + min(dc, 0)
    out[:, rs - dr:re - dr, cs - dc:ce - dc] = g[:, rs:re, cs:ce]
    return out


def _stack(*arrs):
    return np.stack(arrs, -1)


VIEWS = {
    "self": lambda g: _stack(g),
    "ud": lambda g: _stack(g, _shift(g, -1, 0), _shift(g, 1, 0)),
    "lr": lambda g: _stack(g, _shift(g, 0, -1), _shift(g, 0, 1)),
    "von": lambda g: _stack(g, _shift(g, -1, 0), _shift(g, 1, 0), _shift(g, 0, -1), _shift(g, 0, 1)),
    "mirror_lr": lambda g: _stack(g, g[:, :, ::-1]),
    "mirror_ud": lambda g: _stack(g, g[:, ::-1, :]),
    "transpose": lambda g: _stack(g, g.transpose(0, 2, 1)) if g.shape[1] == g.shape[2] else None,
    "rot180": lambda g: _stack(g, g[:, ::-1, ::-1]),
}
VIEW_ORDER = ["self", "ud", "lr", "von", "mirror_lr", "mirror_ud", "transpose", "rot180"]


# ---------------------------------------------------------------- keys
def role_keys(slots):
    """Colour-agnostic integer key per cell: (am I zero?) + role of every other slot."""
    me = slots[..., 0]
    key = (me != 0).astype(np.int64)
    for j in range(1, slots.shape[-1]):
        v = slots[..., j]
        role = np.where(v == EDGE, 3, np.where(v == me, 0, np.where(v == 0, 1, 2)))
        key = key * 4 + role
    return key


def n_role_keys(n_slots):
    return 2 * 4 ** (n_slots - 1)


def dict_keys(slots, abstraction):
    flat = slots.reshape(-1, slots.shape[-1])
    if abstraction == "raw":
        return [tuple(r) for r in flat.tolist()]
    return [(r[0], frozenset(r[1:])) for r in flat.tolist()]          # rawset


# ---------------------------------------------------------------- ops
# op code c < S: copy slot c (0 = keep my own colour);  c >= S: constant colour c - S
def apply_codes(slots, codes):
    S = slots.shape[-1]
    copy = np.take_along_axis(slots, np.clip(codes, 0, S - 1)[..., None], -1)[..., 0]
    out = np.where(codes < S, copy, codes - S)
    return np.where(out == EDGE, slots[..., 0], out)                   # copying off-grid = keep


def explanations(slots, target, abstraction):
    """Per cell, the set of op codes that would turn this cell into its target."""
    S = slots.shape[-1]
    flat, tgt = slots.reshape(-1, S), target.reshape(-1)
    out = []
    # A set of neighbour colours has no order, so "copy neighbour j" is meaningless for rawset.
    copyable = 1 if abstraction == "rawset" else S
    for row, t in zip(flat.tolist(), tgt.tolist()):
        ops = {k for k in range(copyable) if row[k] == t}
        if abstraction != "role" or t == 0:        # role rules stay colour-agnostic (constant 0 only)
            ops.add(S + t)
        out.append(ops)
    return out


def pick(ops):
    return min(ops)        # prefer "keep", then copying a neighbour, then a constant


# ---------------------------------------------------------------- hypothesis
class Hypothesis:
    def __init__(self, view, abstraction, mode, table, how):
        self.view, self.abstraction, self.mode, self.table, self.how = view, abstraction, mode, table, how

    def step(self, g):
        slots = VIEWS[self.view](g)
        if self.abstraction == "role":
            codes = self.table[role_keys(slots)]
        else:
            codes = np.array([self.table.get(k, 0) for k in dict_keys(slots, self.abstraction)]).reshape(g.shape)
        return apply_codes(slots, codes)

    def run(self, g):
        if self.mode == "single":
            return self.step(g)
        for _ in range(MAX_STEPS):
            nxt = self.step(g)
            if np.array_equal(nxt, g):
                break
            g = nxt
        return g

    def uncovered(self, g):
        """Fraction of the test grid's rule keys never seen in the demos (0 = fully covered)."""
        if self.abstraction == "role":
            return 0.0
        seen = getattr(self, "seen", self.table)
        keys = dict_keys(VIEWS[self.view](g), self.abstraction)
        return sum(k not in seen for k in keys) / len(keys)

    def size(self):
        return int((self.table != 0).sum()) if self.abstraction == "role" else len(self.table)

    def describe(self):
        return f"{self.how}: view={self.view} abstraction={self.abstraction} mode={self.mode} rules={self.size()}"


def _empty_table(view, abstraction, xs):
    return np.zeros(n_role_keys(VIEWS[view](xs[:1]).shape[-1]), dtype=np.int64) if abstraction == "role" else {}


def _keys(slots, abstraction):
    return role_keys(slots).reshape(-1).tolist() if abstraction == "role" else dict_keys(slots, abstraction)


def fit_single(view, abstraction, xs, ys):
    slots = VIEWS[view](xs)
    allowed = {}
    for k, ops in zip(_keys(slots, abstraction), explanations(slots, ys, abstraction)):
        allowed[k] = allowed[k] & ops if k in allowed else set(ops)
        if not allowed[k]:
            return None
    table = _empty_table(view, abstraction, xs)
    for k, ops in allowed.items():
        table[k] = pick(ops)
    return Hypothesis(view, abstraction, "single", table, "single-step")


def fit_iterate(view, abstraction, xs, ys):
    table = _empty_table(view, abstraction, xs)
    assigned, seen = set(), set()
    state = xs
    for _ in range(MAX_STEPS):
        slots = VIEWS[view](state)
        allowed = {}
        for k, ops in zip(_keys(slots, abstraction), explanations(slots, ys, abstraction)):
            seen.add(k)                              # unassigned seen keys deliberately mean "keep"
            if k not in assigned:
                allowed[k] = allowed[k] & ops if k in allowed else set(ops)
        for k, ops in allowed.items():
            if ops:                                  # every cell with this key agrees on its final target
                table[k] = pick(ops)
                assigned.add(k)
        hyp = Hypothesis(view, abstraction, "iterate", table, "iterate-to-target")
        nxt = hyp.step(state)
        if np.array_equal(nxt, state):
            break
        state = nxt
    hyp.seen = seen
    return hyp if np.array_equal(hyp.run(xs), ys) else None


def fit_hillclimb(view, xs, ys, max_rounds=8):
    S = VIEWS[view](xs[:1]).shape[-1]
    table = np.zeros(n_role_keys(S), dtype=np.int64)
    hyp = Hypothesis(view, "role", "iterate", table, "hill-climb")
    cost = lambda t: int((Hypothesis(view, "role", "iterate", t, "") .run(xs) != ys).sum())
    best = cost(table)
    edits = [(k, c) for k in range(len(table)) for c in list(range(1, S)) + [S]]   # copy a neighbour, or 0
    for _ in range(max_rounds):
        if best == 0:
            break
        improved = False
        for group in (1, 2):                                            # single edits, then pairs
            candidates = edits if group == 1 else itertools.combinations(edits, 2)
            winner = None
            for cand in candidates:
                cand = (cand,) if group == 1 else cand
                if len({k for k, _ in cand}) < len(cand) or all(table[k] == c for k, c in cand):
                    continue
                t = table.copy()
                for k, c in cand:
                    t[k] = c
                cst = cost(t)
                if cst < best:
                    best, winner = cst, t
            if winner is not None:
                table, improved = winner, True
                break
        if not improved:
            break
    hyp.table = table
    return hyp if best == 0 else None


class RuleSearchCA:
    """Few-shot solver: fit(demo_inputs, demo_outputs) then predict(test_input)."""

    def __init__(self, hillclimb_views=("ud", "lr")):
        self.hillclimb_views = hillclimb_views
        self.hypothesis = None

    def fit(self, xs, ys, test_x=None):
        xs, ys = np.asarray(xs), np.asarray(ys)
        tx = None if test_x is None else np.asarray(test_x)[None]
        fitted = []
        for view in VIEW_ORDER:
            if VIEWS[view](xs[:1]) is None:
                continue
            S = VIEWS[view](xs[:1]).shape[-1]
            for abstraction in ("role", "raw", "rawset"):
                if abstraction == "rawset" and S < 3:
                    continue
                for fit in (fit_single, fit_iterate):
                    hyp = fit(view, abstraction, xs, ys)
                    if hyp is None:
                        continue
                    if tx is None or hyp.uncovered(tx) == 0:
                        self.hypothesis = hyp
                        return hyp
                    fitted.append(hyp)
        # No hypothesis covers every key of the test input: take the one that generalises best
        # (fewest unseen keys), then the smallest rule table.
        best = min(fitted, key=lambda h: (h.uncovered(tx), h.size()), default=None)
        if best is None:
            for view in self.hillclimb_views:
                best = fit_hillclimb(view, xs, ys)
                if best is not None:
                    break
        self.hypothesis = best
        return best

    def predict(self, x):
        x = np.asarray(x)[None]
        return (self.hypothesis.run(x) if self.hypothesis else x)[0]
