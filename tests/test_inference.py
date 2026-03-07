"""
Unit tests for watermark removal inference: rmlogo.inference.remove_logo

Tests the inpainting logic with synthetic images (no disk I/O).
"""

import pytest
import numpy as np
from rmlogo.inference import remove_logo, remove_logo_multi_scale


class TestRemoveLogoBasics:
    """Test basic functionality of remove_logo."""

    def test_output_shape_matches_input(self, natural_image_200, zero_mask_200):
        """Output should have same shape as input."""
        result = remove_logo(natural_image_200, zero_mask_200)
        assert result.shape == natural_image_200.shape, (
            f"Expected {natural_image_200.shape}, got {result.shape}"
        )

    def test_output_dtype_uint8(self, natural_image_200, zero_mask_200):
        """Output should be uint8."""
        result = remove_logo(natural_image_200, zero_mask_200)
        assert result.dtype == np.uint8, f"Expected uint8, got {result.dtype}"

    def test_output_values_in_valid_range(self, natural_image_200, zero_mask_200):
        """Output pixel values should be in [0, 255]."""
        result = remove_logo(natural_image_200, zero_mask_200)
        assert result.min() >= 0 and result.max() <= 255, (
            f"Values out of range: [{result.min()}, {result.max()}]"
        )


class TestRemoveLogoMaskBehavior:
    """Test behavior with different mask types."""

    def test_zero_mask_roughly_preserves_image(self, natural_image_200, zero_mask_200):
        """Zero mask means no removal, image should be mostly unchanged."""
        result = remove_logo(natural_image_200, zero_mask_200)
        # Should be very similar (inpainting with zero mask doesn't modify pixels)
        diff = np.abs(result.astype(int) - natural_image_200.astype(int))
        # Allow small differences due to floating point or inpainting edge effects
        assert np.mean(diff) < 10, "Zero mask should preserve image"

    def test_full_mask_runs_without_error(self, natural_image_200, full_mask_200):
        """Full white mask should still run without exception."""
        result = remove_logo(natural_image_200, full_mask_200)
        assert result.shape == natural_image_200.shape
        assert result.dtype == np.uint8

    def test_corner_mask_runs_without_error(self, natural_image_200, corner_mask_br):
        """Corner mask should process without error."""
        result = remove_logo(natural_image_200, corner_mask_br)
        assert result.shape == natural_image_200.shape


class TestRemoveLogoInputValidation:
    """Test input validation and error handling."""

    def test_invalid_2d_image_raises(self, zero_mask_200):
        """2D grayscale image should raise ValueError."""
        grayscale = np.zeros((200, 200), dtype=np.uint8)
        with pytest.raises(ValueError):
            remove_logo(grayscale, zero_mask_200)

    def test_invalid_4ch_image_raises(self, zero_mask_200):
        """4-channel RGBA image should raise ValueError."""
        rgba_img = np.zeros((200, 200, 4), dtype=np.uint8)
        with pytest.raises(ValueError):
            remove_logo(rgba_img, zero_mask_200)

    def test_mismatched_sizes_raises(self, natural_image_200):
        """Mismatched image and mask sizes should raise ValueError."""
        mask_small = np.zeros((100, 100), dtype=np.uint8)
        with pytest.raises(ValueError):
            remove_logo(natural_image_200, mask_small)

    def test_3d_mask_raises(self, natural_image_200):
        """3D mask should raise ValueError."""
        mask_3d = np.zeros((200, 200, 1), dtype=np.uint8)
        with pytest.raises(ValueError):
            remove_logo(natural_image_200, mask_3d)


class TestRemoveLogoRadius:
    """Test behavior with different inpainting radii."""

    def test_small_radius(self, natural_image_200, corner_mask_br):
        """Small radius should work."""
        result = remove_logo(natural_image_200, corner_mask_br, radius=3)
        assert result.shape == natural_image_200.shape

    def test_large_radius(self, natural_image_200, corner_mask_br):
        """Large radius should work."""
        result = remove_logo(natural_image_200, corner_mask_br, radius=10)
        assert result.shape == natural_image_200.shape


class TestRemoveLogoMultiScale:
    """Test multi-scale inpainting for large watermarks."""

    def test_multi_scale_large_mask(self):
        """Multi-scale should work with large masks."""
        img = np.random.randint(0, 256, (200, 200, 3), dtype=np.uint8)
        mask = np.full((200, 200), 255, dtype=np.uint8)
        # Cover 50% of image (20000 pixels)
        mask[0:100, :] = 255

        result = remove_logo_multi_scale(img, mask)
        assert result.shape == img.shape
        assert result.dtype == np.uint8

    def test_multi_scale_small_mask(self):
        """Multi-scale should work with small masks."""
        img = np.random.randint(0, 256, (200, 200, 3), dtype=np.uint8)
        mask = np.zeros((200, 200), dtype=np.uint8)
        mask[50:100, 50:100] = 255

        result = remove_logo_multi_scale(img, mask)
        assert result.shape == img.shape

    def test_multi_scale_with_scales_parameter(self, natural_image_200, corner_mask_br):
        """Should accept custom scales parameter."""
        result = remove_logo_multi_scale(
            natural_image_200, corner_mask_br, scales=[2, 1]
        )
        assert result.shape == natural_image_200.shape


class TestRemoveLogoEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_minimum_size_image(self):
        """Should handle very small images."""
        img = np.ones((10, 10, 3), dtype=np.uint8) * 128
        mask = np.zeros((10, 10), dtype=np.uint8)
        result = remove_logo(img, mask)
        assert result.shape == (10, 10, 3)

    def test_all_black_image(self, zero_mask_200):
        """Should handle all-black images."""
        black_img = np.zeros((200, 200, 3), dtype=np.uint8)
        result = remove_logo(black_img, zero_mask_200)
        assert result.dtype == np.uint8

    def test_all_white_image(self, zero_mask_200):
        """Should handle all-white images."""
        white_img = np.full((200, 200, 3), 255, dtype=np.uint8)
        result = remove_logo(white_img, zero_mask_200)
        assert result.dtype == np.uint8
