"""6. LiReCA - Liquid Recursive Cellular Automaton  (new hybrid, built for this arena)

Each idea comes from one of the five families:

  from NCA     every cell runs the same tiny local rule (3x3 conv), so the model is small and
               the rule works on any grid size.
  from TRM     two states per cell: y = the current answer, z = a reasoning scratchpad.
               z is refined several times, then y is updated from z. Most cycles run without
               gradients, so the model can "think" for 50+ steps at the memory cost of a few,
               and the answer is scored after every outer step (deep supervision).
  from Liquid  updates are liquid / leaky: each cell learns its own time constant (a gate
               computed from what it sees), deciding per channel how much to keep the old state
               versus move to the new one. Settled cells can freeze while busy ones keep changing.
  new          axial broadcast. Plain NCAs are slow at long-range jobs because information
               crawls one cell per step. Each cell also sees the mean of its whole row and whole
               column, so information can cross the grid in one step while the rule stays cheap
               (O(H*W), no attention).
"""
import torch
import torch.nn as nn

from ..common import GridModel
from ..tasks import H, N_COLORS, TASKS, W


class LiquidConvUpdate(nn.Module):
    """state <- gate * state + (1 - gate) * candidate, where gate is computed per cell and channel."""

    def __init__(self, n_in, n_state, hidden):
        super().__init__()
        self.perceive = nn.Sequential(nn.Conv2d(n_in, hidden, 3, padding=1), nn.GELU())
        self.cand = nn.Conv2d(hidden, n_state, 1)
        self.tau = nn.Conv2d(hidden, n_state, 1)
        nn.init.zeros_(self.tau.bias)                  # start half-way between keep and replace

    def forward(self, features, state):
        h = self.perceive(features)
        gate = torch.sigmoid(self.tau(h))
        return gate * state + (1 - gate) * torch.tanh(self.cand(h))


class LiReCA(GridModel):
    lr = 2e-3

    def __init__(self, cz=48, cy=16, hidden=128, task_dim=8,
                 n_latent=4, n_cycles=2, n_sup=4, n_sup_eval=8):
        super().__init__()
        self.task = nn.Embedding(len(TASKS), task_dim)
        n_inp = N_COLORS + task_dim + 2
        self.z_update = LiquidConvUpdate(cz + cy + n_inp + 2 * cz, cz, hidden)
        self.y_update = LiquidConvUpdate(cy + cz + n_inp, cy, hidden // 2)
        self.readout = nn.Conv2d(cy, N_COLORS, 1)
        # y lives in [-1, 1] (liquid states are tanh-bounded), so let the readout sharpen it.
        self.readout_scale = nn.Parameter(torch.tensor(8.0))
        self.cz, self.cy = cz, cy
        self.n_latent, self.n_cycles, self.n_sup, self.n_sup_eval = n_latent, n_cycles, n_sup, n_sup_eval
        ys, xs = torch.meshgrid(torch.linspace(-1, 1, H), torch.linspace(-1, 1, W), indexing="ij")
        self.register_buffer("coords", torch.stack([ys, xs])[None])

    @staticmethod
    def axial(z):
        return torch.cat([z.mean(3, keepdim=True).expand_as(z),     # whole-row summary
                          z.mean(2, keepdim=True).expand_as(z)], 1)  # whole-column summary

    def latent_recursion(self, inp, y, z):
        for _ in range(self.n_latent):
            z = self.z_update(torch.cat([z, y, inp, self.axial(z)], 1), z)   # think
        y = self.y_update(torch.cat([y, z, inp], 1), y)                     # act
        return y, z

    def forward(self, grid, task):
        B = grid.shape[0]
        onehot = nn.functional.one_hot(grid, N_COLORS).permute(0, 3, 1, 2).float()
        t = self.task(task)[:, :, None, None].expand(-1, -1, H, W)
        inp = torch.cat([onehot, t, self.coords.expand(B, -1, -1, -1)], 1)
        y = inp.new_zeros(B, self.cy, H, W)
        z = inp.new_zeros(B, self.cz, H, W)
        outs = []
        for _ in range(self.n_sup if self.training else self.n_sup_eval):
            with torch.no_grad():
                for _ in range(self.n_cycles - 1):
                    y, z = self.latent_recursion(inp, y, z)
            y, z = self.latent_recursion(inp, y, z)
            outs.append(self.readout(y) * self.readout_scale)
            y, z = y.detach(), z.detach()
        return outs
