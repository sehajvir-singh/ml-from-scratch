"""4. Liquid neural network - Closed-form Continuous-time (CfC) cells
("Closed-form continuous-time neural networks", Hasani et al., 2022).

A liquid neuron's state flows in continuous time, and each neuron learns its own *time
constant*: how quickly it forgets the old state and moves to the new one. CfC solves that
ODE in closed form, so no ODE solver is needed:

    gate  = sigmoid(-f(x, h) * t)
    h_new = gate * g(x, h) + (1 - gate) * k(x, h)

The grid is read as a sequence of cells: one bidirectional pass row by row, then a second
bidirectional pass column by column, so every cell can hear from every other cell.
"""
import torch
import torch.nn as nn

from ..common import GridModel
from ..tasks import H, N_COLORS, TASKS, W


class CfCCell(nn.Module):
    def __init__(self, n_in, n_hidden, backbone=128):
        super().__init__()
        self.backbone = nn.Sequential(nn.Linear(n_in + n_hidden, backbone), nn.SiLU())
        self.f = nn.Linear(backbone, n_hidden)   # time-constant head
        self.g = nn.Linear(backbone, n_hidden)
        self.k = nn.Linear(backbone, n_hidden)

    def forward(self, x, h, t=1.0):
        b = self.backbone(torch.cat([x, h], -1))
        gate = torch.sigmoid(-self.f(b) * t)
        return gate * torch.tanh(self.g(b)) + (1 - gate) * torch.tanh(self.k(b))


class BiCfC(nn.Module):
    """Runs one CfC cell forwards and backwards over a sequence (both directions batched)."""

    def __init__(self, n_in, n_hidden):
        super().__init__()
        self.cell = CfCCell(n_in + 1, n_hidden)       # +1 flag tells the cell its direction
        self.n_hidden = n_hidden

    def forward(self, seq):                          # seq: [B, L, n_in]
        B, L, _ = seq.shape
        both = torch.cat([seq, seq.flip(1)], 0)
        flag = torch.cat([seq.new_zeros(B, L, 1), seq.new_ones(B, L, 1)], 0)
        both = torch.cat([both, flag], -1)
        h = seq.new_zeros(2 * B, self.n_hidden)
        outs = []
        for i in range(L):
            h = self.cell(both[:, i], h)
            outs.append(h)
        out = torch.stack(outs, 1)
        return torch.cat([out[:B], out[B:].flip(1)], -1)   # [B, L, 2*n_hidden]


class Liquid(GridModel):
    lr = 2e-3

    def __init__(self, d=48, hidden=64):
        super().__init__()
        self.color = nn.Embedding(N_COLORS, d)
        self.pos = nn.Parameter(torch.randn(H * W, d) * 0.1)
        self.task = nn.Embedding(len(TASKS), d)
        self.rows = BiCfC(d, hidden)
        self.cols = BiCfC(2 * hidden + d, hidden)
        self.head = nn.Linear(2 * hidden, N_COLORS)

    def forward(self, grid, task):
        B = grid.shape[0]
        e = self.color(grid.flatten(1)) + self.pos + self.task(task)[:, None]     # row-major
        r = self.rows(e)                                                            # [B, HW, 2h]
        to_cols = lambda s: s.reshape(B, H, W, -1).transpose(1, 2).reshape(B, H * W, -1)
        c = self.cols(to_cols(torch.cat([r, e], -1)))                               # column-major
        c = c.reshape(B, W, H, -1).transpose(1, 2)                                  # back to [B,H,W,2h]
        return self.head(c).permute(0, 3, 1, 2)
