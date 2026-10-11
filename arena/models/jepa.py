"""3. JEPA - Joint-Embedding Predictive Architecture (LeCun, 2022; I-JEPA, Assran et al., 2023).

Instead of predicting the output pixels directly, JEPA predicts the output's *representation*:

    context encoder:  input grid  -> latents  s_x
    target encoder:   output grid -> latents  s_y
    predictor:        s_x (+ task) -> predicted s_y      trained with a latent-space loss
                                                          || pred - stopgrad(s_y) ||^2

The predictor never sees a pixel loss: it only learns to "imagine" the answer in idea-space.
To read an answer out we decode the predicted latents with a decoder that was trained only on
real target latents.

Collapse guard: the target encoder is trained as an autoencoder (its latents must reconstruct
the output grid), so it can't collapse to a constant. I-JEPA uses an EMA target encoder instead;
the reconstruction anchor is simpler and more stable at this tiny scale.
"""
import torch.nn as nn
import torch.nn.functional as F

from ..common import GridModel
from ..tasks import H, N_COLORS, W
from .trm import GridEmbed, tiny_transformer


class JEPA(GridModel):
    lr = 5e-4

    def __init__(self, d=96, heads=4, enc_layers=2, pred_layers=3, latent_weight=10.0):
        super().__init__()
        self.ctx_embed, self.ctx_enc = GridEmbed(d), tiny_transformer(d, heads, enc_layers)
        self.tgt_embed, self.tgt_enc = GridEmbed(d, with_task=False), tiny_transformer(d, heads, enc_layers)
        self.predictor = tiny_transformer(d, heads, pred_layers)
        self.norm = nn.LayerNorm(d, elementwise_affine=False)
        self.decoder = nn.Linear(d, N_COLORS)
        self.latent_weight = latent_weight

    def encode_target(self, y):
        return self.norm(self.tgt_enc(self.tgt_embed(y)))[:, 1:]

    def predict_latent(self, x, task):
        return self.norm(self.predictor(self.ctx_enc(self.ctx_embed(x, task))))[:, 1:]

    def decode(self, z):
        return self.decoder(z).transpose(1, 2).reshape(-1, N_COLORS, H, W)

    def loss(self, x, task, y):
        s_y = self.encode_target(y)
        recon = F.cross_entropy(self.decode(s_y), y)                 # anchors the target space
        pred = self.predict_latent(x, task)
        latent = F.mse_loss(pred, s_y.detach())                      # the JEPA objective
        return recon + self.latent_weight * latent

    def forward(self, x, task):
        return self.decode(self.predict_latent(x, task))
