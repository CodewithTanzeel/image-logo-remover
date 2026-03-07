# rmlogo - Package Information & Links

## Package Details

**Name:** rmlogo  
**Version:** 0.0.2 (Latest)  
**License:** GPL-3.0  
**Python:** 3.9+  
**Status:** Production Ready

---

## Package Links

### PyPI (Official)
https://pypi.org/project/rmlogo/

### GitHub Repository
https://github.com/CodewithTanzeel/image-logo-remover

---

## Installation

```bash
pip install rmlogo
```

---

## Quick Start

```bash
# Single image
rmlogo photo.jpg -o cleaned.jpg

# Batch processing
rmlogo --batch ./photos/

# With position hint
rmlogo photo.jpg -o cleaned.jpg --hint bottom-right
```

---

## Documentation

Inside the repository:

1. **README.md** — Overview, features, and examples
2. **QUICKSTART.md** — 3-step setup and basic usage
3. **USAGE.md** — Comprehensive feature guide and advanced examples

---

## Key Features

- One-command watermark removal
- Batch processing with multi-threading
- Automatic position detection + manual hints
- Cross-platform (Windows, macOS, Linux)
- Fast (no GPU required)
- JSON export for automation
- Pipe support (Unix/Linux/PowerShell)

---

## Support

- **Help:** `rmlogo --help`
- **Version:** `rmlogo --version`
- **Issues:** https://github.com/CodewithTanzeel/image-logo-remover/issues

---

## What's Included in v0.0.2

✅ CLI tool for removing watermarks/logos  
✅ Automatic watermark detection  
✅ OpenCV-based inpainting  
✅ Single and batch processing modes  
✅ Position hints for manual guidance  
✅ 53 passing unit tests  
✅ Python API for programmatic use  
✅ Cross-platform support  

---

## Getting Started

1. **Install:** `pip install rmlogo`
2. **Basic usage:** `rmlogo input.jpg -o output.jpg`
3. **Help:** `rmlogo --help`
4. **More info:** Visit https://pypi.org/project/rmlogo/

---

Generated: March 7, 2025
