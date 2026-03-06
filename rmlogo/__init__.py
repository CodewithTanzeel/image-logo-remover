"""
rmlogo - Remove watermarks and logos from images using automatic detection and OpenCV inpainting.

A professional Python package for batch watermark removal with Gemini AI integration.
"""

__version__ = "2.1.0"
__author__ = "CodewithanZeeL"
__license__ = "GPL-3.0"

from .cli import main

__all__ = ["main"]
