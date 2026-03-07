"""
Unit tests for automatic watermark detection: rmlogo.auto_mask.generate_mask

Tests the mask generation logic with synthetic images (no disk I/O).
"""

import pytest
import numpy as np
from rmlogo.auto_mask import generate_mask, visualize_mask


class TestGenerateMaskBasics:
    """Test basic functionality of generate_mask."""

    def test_output_shape_matches_input(self, grey_image_200):
        """Output mask shape should match input image height and width."""
        mask = generate_mask(grey_image_200, hint="auto")
        assert mask.shape == (200, 200), f"Expected (200, 200), got {mask.shape}"

    def test_output_dtype_uint8(self, grey_image_200):
        """Output mask should be uint8."""
        mask = generate_mask(grey_image_200, hint="auto")
        assert mask.dtype == np.uint8, f"Expected uint8, got {mask.dtype}"

    def test_output_binary(self, grey_image_200):
        """Output mask should be binary (0 or 255)."""
        mask = generate_mask(grey_image_200, hint="auto")
        unique_values = np.unique(mask)
        assert all(v in [0, 255] for v in unique_values), (
            f"Expected binary mask, got values: {unique_values}"
        )


class TestGenerateMaskFullHint:
    """Test the 'full' hint which covers the entire image."""

    def test_full_hint_returns_all_white(self, grey_image_200):
        """hint='full' should return mask with all pixels set to 255."""
        mask = generate_mask(grey_image_200, hint="full")
        assert mask.min() == 255 and mask.max() == 255, "Expected all white (255) mask"

    def test_full_hint_shape(self, natural_image_200):
        """full hint should still have correct shape."""
        mask = generate_mask(natural_image_200, hint="full")
        assert mask.shape == (200, 200)


class TestGenerateMaskCornerHints:
    """Test position hints for specific corners."""

    def test_hint_bottom_right_has_white_in_corner(self, grey_image_200):
        """hint='bottom-right' should detect watermark in bottom-right area."""
        mask = generate_mask(grey_image_200, hint="bottom-right")
        h, w = mask.shape
        ch, cw = int(h * 0.30), int(w * 0.30)  # Bottom-right 30%
        corner_region = mask[h - ch : h, w - cw : w]
        assert np.any(corner_region > 127), "Should have white pixels in bottom-right"

    def test_hint_top_left_has_white_in_corner(self, grey_image_200):
        """hint='top-left' should detect watermark in top-left area."""
        mask = generate_mask(grey_image_200, hint="top-left")
        h, w = mask.shape
        ch, cw = int(h * 0.30), int(w * 0.30)
        corner_region = mask[0:ch, 0:cw]
        assert np.any(corner_region > 127), "Should have white pixels in top-left"

    def test_hint_center_produces_mask(self, grey_image_200):
        """hint='center' should produce a valid mask."""
        mask = generate_mask(grey_image_200, hint="center")
        assert mask.shape == (200, 200)
        assert np.any(mask > 127), "Should have some white pixels"


class TestGenerateMaskInputValidation:
    """Test input validation and error handling."""

    def test_invalid_shape_2d_raises(self):
        """2D grayscale input should raise ValueError."""
        grayscale_img = np.zeros((200, 200), dtype=np.uint8)
        with pytest.raises(ValueError):
            generate_mask(grayscale_img)

    def test_invalid_shape_4ch_raises(self):
        """4-channel RGBA input should raise ValueError."""
        rgba_img = np.zeros((200, 200, 4), dtype=np.uint8)
        with pytest.raises(ValueError):
            generate_mask(rgba_img)

    def test_invalid_shape_1ch_raises(self):
        """1D array should raise ValueError."""
        arr_1d = np.zeros(200, dtype=np.uint8)
        with pytest.raises(ValueError):
            generate_mask(arr_1d)


class TestVisualizeMask:
    """Test the mask visualization function."""

    def test_visualize_mask_shape(self, grey_image_200, full_mask_200):
        """Output should be 3-channel BGR."""
        viz = visualize_mask(grey_image_200, full_mask_200)
        assert viz.shape == (200, 200, 3), f"Expected (200, 200, 3), got {viz.shape}"

    def test_visualize_mask_dtype(self, grey_image_200, full_mask_200):
        """Output should be uint8."""
        viz = visualize_mask(grey_image_200, full_mask_200)
        assert viz.dtype == np.uint8

    def test_visualize_mask_red_overlay(self, grey_image_200, full_mask_200):
        """Masked pixels should be colored red [0, 0, 255]."""
        viz = visualize_mask(grey_image_200, full_mask_200)
        # All pixels should be red since mask is all white
        expected_red = np.array([0, 0, 255], dtype=np.uint8)
        assert np.all(viz == expected_red), "All masked pixels should be red"


class TestGenerateMaskWithDetection:
    """Test mask generation on synthetic watermarked images."""

    def test_grey_patch_in_black_image(self):
        """Should detect grey patch in black background."""
        # Create black image with grey patch in bottom-right
        img = np.zeros((200, 200, 3), dtype=np.uint8)
        img[140:200, 140:200] = 128  # Grey patch in bottom-right

        mask = generate_mask(img, hint="auto")
        # Should have some detected pixels in bottom-right area
        h, w = mask.shape
        ch, cw = int(h * 0.35), int(w * 0.35)
        corner_region = mask[h - ch : h, w - cw : w]
        assert np.any(corner_region > 127), "Should detect grey patch"

    def test_auto_vs_specific_hint_consistency(self, grey_image_200):
        """Auto hint should produce a valid mask (may differ from specific hint)."""
        mask_auto = generate_mask(grey_image_200, hint="auto")
        assert mask_auto.shape == (200, 200)
        assert np.any(mask_auto == 0), "Should have some background pixels"
