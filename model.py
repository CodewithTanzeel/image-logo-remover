"""
SimpleLogoRemover — architecture reconstructed from fine_tuned_watermark_remover.pth

Weight shapes confirmed:
  enc1.weight: [64, 4, 3, 3]   enc1.bias: [64]
  enc2.weight: [128, 64, 3, 3] enc2.bias: [128]
  dec1.weight: [64, 128, 3, 3] dec1.bias: [64]
  dec2.weight: [3, 64, 3, 3]   dec2.bias: [3]

Input:  [B, 4, H, W]  — 3 RGB channels concatenated with 1 mask channel
Output: [B, 3, H, W]  — cleaned RGB image, values in [0, 1]
"""

import torch
import torch.nn as nn


class SimpleLogoRemover(nn.Module):
    def __init__(self):
        super().__init__()
        # Encoder
        self.enc1 = nn.Conv2d(4, 64, kernel_size=3, padding=1)   # 4-ch input (RGB + mask)
        self.enc2 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        # Decoder
        self.dec1 = nn.Conv2d(128, 64, kernel_size=3, padding=1)
        self.dec2 = nn.Conv2d(64, 3, kernel_size=3, padding=1)    # 3-ch RGB output

        self.relu = nn.ReLU(inplace=True)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.relu(self.enc1(x))
        x = self.relu(self.enc2(x))
        x = self.relu(self.dec1(x))
        x = self.sigmoid(self.dec2(x))
        return x
