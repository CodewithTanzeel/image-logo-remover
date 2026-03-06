#!/usr/bin/env python3
"""
build_dist.py - Build rmlogo distribution zip for offline installation

Usage:
    python build_dist.py

This creates rmlogo-2.1.0-dist.zip containing:
    - rmlogo/ package (all Python code)
    - wheels/ (offline dependencies)
    - install.bat (Windows installer)
    - pyproject.toml, requirements.txt
    - Documentation files (INSTALL.md, USER_MANUAL.md, etc.)

The zip can be sent to a friend who can then:
    1. Extract it
    2. Double-click install.bat
    3. Run: rmlogo --help
"""

import os
import zipfile
import shutil
from pathlib import Path

# Configuration
PROJECT_ROOT = Path(__file__).parent
ZIP_NAME = "rmlogo-2.1.0-dist.zip"
DIST_DIR = "rmlogo-2.1.0-dist"

# Files and directories to include
INCLUDE_FILES = [
    "rmlogo/",  # Package code
    "wheels/",  # Offline dependencies
    "pyproject.toml",  # Package config
    "requirements.txt",  # Dependency list
    "install.bat",  # Windows installer
    "INSTALL.md",  # Installation guide
    "USER_MANUAL.md",  # Full documentation
    "LICENSE",  # License file
    "README.md",  # Project readme
    "test_rmlogo.py",  # Test script
]

# Files to exclude from rmlogo/ package
EXCLUDE_PATTERNS = [
    "__pycache__",
    "*.pyc",
    ".pyc",
    ".git",
]


def should_exclude(path_str):
    """Check if a path should be excluded from the zip."""
    path_str = str(path_str).lower()
    for pattern in EXCLUDE_PATTERNS:
        if pattern in path_str:
            return True
    return False


def build_zip():
    """Build the distribution zip file."""
    print("\n" + "=" * 70)
    print(f"Building {ZIP_NAME}")
    print("=" * 70)

    # Remove existing zip if it exists
    if os.path.exists(ZIP_NAME):
        print(f"\nRemoving existing {ZIP_NAME}")
        os.remove(ZIP_NAME)

    # Create zip
    print(f"\nCreating zip archive...")
    with zipfile.ZipFile(ZIP_NAME, "w", zipfile.ZIP_DEFLATED) as zf:
        for item in INCLUDE_FILES:
            item_path = PROJECT_ROOT / item

            if not item_path.exists():
                print(f"  WARNING: {item} not found, skipping")
                continue

            if item_path.is_file():
                # Add single file
                arcname = f"{DIST_DIR}/{item}"
                print(f"  + {arcname}")
                zf.write(item_path, arcname=arcname)

            elif item_path.is_dir():
                # Add directory recursively
                for root, dirs, files in os.walk(item_path):
                    for file in files:
                        file_path = Path(root) / file

                        # Skip excluded files
                        if should_exclude(str(file_path)):
                            continue

                        # Calculate archive name
                        rel_path = file_path.relative_to(PROJECT_ROOT)
                        arcname = f"{DIST_DIR}/{rel_path}"

                        print(f"  + {arcname}")
                        zf.write(file_path, arcname=arcname)

    # Get zip size
    zip_size = os.path.getsize(ZIP_NAME) / (1024 * 1024)

    print("\n" + "=" * 70)
    print(f"Success! Created {ZIP_NAME}")
    print(f"Size: {zip_size:.1f} MB")
    print("=" * 70)

    # Print contents summary
    print("\nZip Contents:")
    with zipfile.ZipFile(ZIP_NAME, "r") as zf:
        files = zf.namelist()
        print(f"  Total files: {len(files)}")
        for name in sorted(files)[:15]:  # Show first 15
            info = zf.getinfo(name)
            print(f"    - {name} ({info.file_size} bytes)")
        if len(files) > 15:
            print(f"    ... and {len(files) - 15} more files")

    print("\n" + "=" * 70)
    print("Next steps for your friend:")
    print("=" * 70)
    print("\n1. Extract the zip to any folder")
    print("2. Double-click install.bat (Windows)")
    print("   OR run: pip install --no-index --find-links=wheels -e .")
    print("3. Run: rmlogo --help")
    print("\nFor documentation:")
    print("  - INSTALL.md: Step-by-step setup guide")
    print("  - USER_MANUAL.md: Full feature documentation")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    try:
        build_zip()
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback

        traceback.print_exc()
        exit(1)
