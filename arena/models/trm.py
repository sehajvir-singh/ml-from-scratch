"""1. Tiny Recursive Model (TRM) - "Less is More: Recursive Reasoning with Tiny Networks"
(Jolicoeur-Martineau, 2025).

One tiny network is applied over and over. It keeps two states:
    y = the current answer (embedded)
    z = a latent "scratchpad" of reasoning
Each cycle it first refines z several times from (x, y, z), then updates the answer y from (y, z).
Only the last cycle is back-propagated; earlier cycles run without gradients, so the model can
"think" for many steps at the memory cost of one. Deep supervision: the answer is read out and
scored after every outer step, and the states are carried forward (detached) to the next one.

Simplification vs. the paper: deep supervision runs inside one training step instead of
carrying states across mini-batches, and there is no learned halting head.
"""
import torch
import torch.nn as nn

from ..common import GridModel
from ..tasks import H, N_COLORS, TASKS, W


class GridEmbed(nn.Module):
    """Colour + position embedding per cell, with a task token prepended."""

    def __init__(self, d, with_task=True):
        super().__init__()
        self.color = nn.Embedding(N_COLORS, d)
        self.pos = nn.Parameter(torch.randn(H * W + 1, d) * 0.02)
        self.task = nn.Embedding(len(TASKS), d) if with_task else None

    def forward(self, grid, task=None):
        h = self.color(grid.flatten(1))                       # [B, HW, d]
        first = self.task(task)[:, None] if self.task is not None else h.new_zeros(h.shape[0], 1, h.shape[2])
        return torch.cat([first, h], 1) + self.pos


def tiny_transformer(d, heads, layers):
    # Post-norm (as in TRM): every output is layer-normed, so applying the same network
    # dozens of times in a row can't blow up the state.
    layer = nn.TransformerEncoderLayer(d, heads, 4 * d, dropout=0.0, batch_first=True, norm_first=False)
    return nn.TransformerEncoder(layer, layers, enable_nested_tensor=False)


class TRM(GridModel):
    lr = 5e-4

    def __init__(self, d=128, heads=4, layers=2, n_latent=3, n_cycles=2, n_sup=2, n_sup_eval=4):
        super().__init__()
        self.embed = GridEmbed(d)
        self.net = tiny_transformer(d, heads, layers)   # the ONE network reused everywhere
        self.y0 = nn.Parameter(torch.zeros(d))
        self.z0 = nn.Parameter(torch.zeros(d))
        self.head = nn.Linear(d, N_COLORS)
        self.n_latent, self.n_cycles = n_latent, n_cycles
        self.n_sup, self.n_sup_eval = n_sup, n_sup_eval

    def latent_recursion(self, x, y, z):
        for _ in range(self.n_latent):
            z = self.net(x + y + z)      # think: refine the scratchpad
        y = self.net(y + z)              # act: update the answer
        return y, z

    def deep_recursion(self, x, y, z):
        with torch.no_grad():
            for _ in range(self.n_cycles - 1):
                y, z = self.latent_recursion(x, y, z)
        y, z = self.latent_recursion(x, y, z)
        logits = self.head(y[:, 1:]).transpose(1, 2).reshape(-1, N_COLORS, H, W)
        return y.detach(), z.detach(), logits

    def forward(self, grid, task):
        x = self.embed(grid, task)
        y = self.y0.expand_as(x)
        z = self.z0.expand_as(x)
        outs = []
        for _ in range(self.n_sup if self.training else self.n_sup_eval):
            y, z, logits = self.deep_recursion(x, y, z)
            outs.append(logits)
        return outs
