"""
Shared pytest fixtures for rmlogo test suite.

These fixtures provide synthetic numpy arrays (no disk I/O required).
"""

import pytest
import numpy as np


@pytest.fixture
def grey_image_200():
    """200×200 BGR image filled with grey (128, 128, 128)."""
    return np.full((200, 200, 3), 128, dtype=np.uint8)


@pytest.fixture
def natural_image_200():
    """200×200 BGR image with random colorful pixels."""
    np.random.seed(42)
    return np.random.randint(0, 256, (200, 200, 3), dtype=np.uint8)


@pytest.fixture
def black_image_200():
    """200×200 all-black BGR image."""
    return np.zeros((200, 200, 3), dtype=np.uint8)


@pytest.fixture
def zero_mask_200():
    """200×200 all-zero uint8 mask (no watermark)."""
    return np.zeros((200, 200), dtype=np.uint8)


@pytest.fixture
def full_mask_200():
    """200×200 all-255 uint8 mask (entire image is watermark)."""
    return np.full((200, 200), 255, dtype=np.uint8)


@pytest.fixture
def corner_mask_br():
    """200×200 mask with bottom-right 30% set to 255."""
    mask = np.zeros((200, 200), dtype=np.uint8)
    h, w = 200, 200
    ch, cw = int(h * 0.30), int(w * 0.30)
    mask[h - ch : h, w - cw : w] = 255
    return mask
