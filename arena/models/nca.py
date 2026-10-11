"""2. Neural Cellular Automaton (NCA) - "Growing Neural Cellular Automata" (Mordvintsev et al., 2020).

Every cell of the grid runs the SAME tiny neural network. A cell can only see its 3x3
neighbourhood. By repeating the local update many times, information spreads across the grid
and global behaviour emerges - like cells in a living tissue. There is no attention and no
global layer at all: everything is local message passing.
"""
import torch
import torch.nn as nn

from ..common import GridModel
from ..tasks import H, N_COLORS, TASKS, W


class NCA(GridModel):
    lr = 2e-3

    def __init__(self, channels=48, hidden=128, task_dim=8, steps=(24, 40), eval_steps=40):
        super().__init__()
        self.task = nn.Embedding(len(TASKS), task_dim)
        n_in = N_COLORS + task_dim + 2                      # one-hot colour, task, (row, col) coords
        self.perceive = nn.Conv2d(channels + n_in, hidden, 3, padding=1)
        self.update = nn.Conv2d(hidden, channels, 1)
        nn.init.zeros_(self.update.weight)                  # start as the "do nothing" rule
        nn.init.zeros_(self.update.bias)
        self.readout = nn.Conv2d(channels, N_COLORS, 1)
        self.channels, self.steps, self.eval_steps = channels, steps, eval_steps
        ys, xs = torch.meshgrid(torch.linspace(-1, 1, H), torch.linspace(-1, 1, W), indexing="ij")
        self.register_buffer("coords", torch.stack([ys, xs])[None])

    def inputs(self, grid, task):
        onehot = nn.functional.one_hot(grid, N_COLORS).permute(0, 3, 1, 2).float()
        t = self.task(task)[:, :, None, None].expand(-1, -1, H, W)
        return torch.cat([onehot, t, self.coords.expand(grid.shape[0], -1, -1, -1)], 1)

    def forward(self, grid, task):
        inp = self.inputs(grid, task)
        state = inp.new_zeros(grid.shape[0], self.channels, H, W)
        if self.training:
            n = int(torch.randint(self.steps[0], self.steps[1] + 1, ()))
        else:
            n = self.eval_steps
        for _ in range(n):
            dx = self.update(torch.relu(self.perceive(torch.cat([state, inp], 1))))
            state = state + dx
        return self.readout(state)
