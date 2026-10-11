"""5. Kolmogorov-Arnold Network (KAN) - "KAN: Kolmogorov-Arnold Networks" (Liu et al., 2024).

A normal MLP has learnable weights on edges and FIXED activations on nodes.
A KAN has LEARNABLE activation functions on every edge: each input->output connection is its
own small 1-D function, built here from a sum of Gaussian bumps (the "FastKAN" RBF variant,
Li 2024, which is much faster than the original B-splines). Nodes just add things up.

Because each edge is a 1-D curve you can plot it, KANs are interpretable and can recover
symbolic formulas. Here it is used as a global model: the whole grid in, the whole grid out.
"""
import torch
import torch.nn as nn

from ..common import GridModel
from ..tasks import H, N_COLORS, TASKS, W


class KANLayer(nn.Module):
    def __init__(self, n_in, n_out, n_basis=6, lo=-2.0, hi=2.0):
        super().__init__()
        self.norm = nn.LayerNorm(n_in)
        self.register_buffer("centers", torch.linspace(lo, hi, n_basis))
        self.width = (hi - lo) / (n_basis - 1)
        self.spline = nn.Linear(n_in * n_basis, n_out, bias=False)   # coefficients of each edge curve
        self.base = nn.Linear(n_in, n_out)                            # residual SiLU path, as in KAN
        nn.init.normal_(self.spline.weight, std=0.1 / (n_in * n_basis) ** 0.5)

    def forward(self, x):
        x = self.norm(x)
        basis = torch.exp(-((x[..., None] - self.centers) / self.width) ** 2)
        return self.spline(basis.flatten(-2)) + self.base(nn.functional.silu(x))


class KAN(GridModel):
    lr = 1e-3

    def __init__(self, hidden=96, n_basis=6):
        super().__init__()
        n_in = H * W * N_COLORS + len(TASKS)
        self.layers = nn.Sequential(KANLayer(n_in, hidden, n_basis),
                                    KANLayer(hidden, H * W * N_COLORS, n_basis))

    def forward(self, grid, task):
        onehot = nn.functional.one_hot(grid.flatten(1), N_COLORS).flatten(1).float()
        t = nn.functional.one_hot(task, len(TASKS)).float()
        out = self.layers(torch.cat([onehot, t], 1))
        return out.reshape(-1, H, W, N_COLORS).permute(0, 3, 1, 2)
