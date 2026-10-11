"""Shared training / evaluation loop for every model in the arena."""
import math
import time

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from .tasks import TASKS, fixed_test_set, sample_batch


def pick_device():
    if torch.backends.mps.is_available():  # Apple Silicon GPU (M1/M2/M3...)
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


class GridModel(nn.Module):
    """Base class. Subclasses implement forward(x, task) -> logits [B,10,H,W]
    (or a list of logits, one per deep-supervision step; the last one is the answer)."""

    lr = 1e-3

    def loss(self, x, task, y):
        out = self(x, task)
        outs = out if isinstance(out, list) else [out]
        return sum(F.cross_entropy(o, y) for o in outs) / len(outs)

    @torch.no_grad()
    def predict(self, x, task):
        out = self(x, task)
        return (out[-1] if isinstance(out, list) else out).argmax(1)


def n_params(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def evaluate(model, device, test=None, batch_size=200):
    x_all, y_all, t_all = test if test is not None else fixed_test_set()
    model.eval()
    exact = np.zeros(len(TASKS))
    cells = np.zeros(len(TASKS))
    count = np.zeros(len(TASKS))
    for i in range(0, len(x_all), batch_size):
        x = torch.from_numpy(x_all[i:i + batch_size]).to(device)
        y = torch.from_numpy(y_all[i:i + batch_size]).to(device)
        t = torch.from_numpy(t_all[i:i + batch_size]).to(device)
        pred = model.predict(x, t)
        ok_cells = (pred == y).float().flatten(1).mean(1).cpu().numpy()
        tid = t.cpu().numpy()
        np.add.at(exact, tid, (ok_cells == 1.0).astype(float))
        np.add.at(cells, tid, ok_cells)
        np.add.at(count, tid, 1)
    model.train()
    return {
        "exact": {k: float(v) for k, v in zip(TASKS, exact / count)},
        "cell": {k: float(v) for k, v in zip(TASKS, cells / count)},
        "exact_mean": float((exact / count).mean()),
    }


def train(model, steps=3000, batch_size=64, seed=0, device=None, log_every=250, lr=None):
    device = device or pick_device()
    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)
    model.to(device).train()
    lr = lr or model.lr
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    warmup = min(200, steps // 10)
    sched = torch.optim.lr_scheduler.LambdaLR(
        opt, lambda s: min(1.0, (s + 1) / warmup) * 0.5 * (1 + math.cos(math.pi * s / steps)))
    test = fixed_test_set()
    start = time.time()
    for step in range(1, steps + 1):
        x, y, t = (torch.from_numpy(a).to(device) for a in sample_batch(rng, batch_size))
        loss = model.loss(x, t, y)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        sched.step()
        if log_every and (step % log_every == 0 or step == steps):
            r = evaluate(model, device, test)
            per = " ".join(f"{k}={v:.2f}" for k, v in r["exact"].items())
            print(f"  step {step:5d}  loss {loss.item():.4f}  exact {r['exact_mean']:.3f}  [{per}]"
                  f"  {time.time() - start:.0f}s", flush=True)
    result = evaluate(model, device, test)
    result["train_seconds"] = time.time() - start
    result["params"] = n_params(model)
    return result
