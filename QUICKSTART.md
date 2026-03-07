# rmlogo Quick Start Guide

Get started removing watermarks from images in **3 steps**.

## 1. Installation (One-time)

```bash
pip install rmlogo
```

**That's it!** No complex setup, no model downloads, no GPU needed.

Works on: Windows, macOS, Linux

---

## 2. Remove watermark from one image

```bash
rmlogo input.jpg -o output.jpg
```

**Done!** Your cleaned image is saved as `output.jpg`.

---

## 3. Common Tasks

### Help rmlogo find the watermark

If auto-detection misses the watermark, give it a hint:

```bash
rmlogo photo.jpg -o result.jpg --hint bottom-right
```

Hint options: `auto`, `bottom-right`, `bottom-left`, `top-right`, `top-left`, `center`, `full`

### Process multiple images (batch mode)

Remove watermarks from an entire folder:

```bash
rmlogo --batch ./my_photos/
# Creates: ./cleaned_images_20250307_154230/
```

Process only JPEGs:
```bash
rmlogo --batch ./my_photos/ --pattern "*.jpg"
```

Use multiple threads for speed:
```bash
rmlogo --batch ./my_photos/ --threads 4
```

Preview before processing:
```bash
rmlogo --batch ./my_photos/ --dry-run
```

---

## All Command Options

```
usage: rmlogo [-h] [-o PATH] [--hint HINT] [--save-mask PATH]
              [--batch PATH] [--pattern PATTERNS] [--threads N]
              [--output-dir PATH] [--dry-run]
              [-q] [-v] [--json] [--version]
              [INPUT]

Options:
  INPUT                  Image file path (single mode)
  -o PATH, --output PATH Output file path
  --hint HINT            Watermark position: auto, bottom-right, bottom-left,
                         top-right, top-left, center, full (default: auto)
  --save-mask PATH       Save detected mask to inspect detection
  --batch PATH           Folder to process (or '-' for piped input)
  --pattern PATTERNS     File filter: "*.jpg" or "*.jpg,*.png"
  --threads N            Number of worker threads (default: auto-detect)
  --output-dir PATH      Custom output directory for batch mode
  --dry-run              Preview batch job without processing
  -q, --quiet            Suppress progress output
  -v, --verbose          Show detailed progress
  --json                 Output results as JSON
  --version              Show version
  -h, --help             Show this help message
```

---

## Troubleshooting

### Watermark not removed?
Try specifying the corner:
```bash
rmlogo photo.jpg -o result.jpg --hint bottom-right
```

### Want to see what was detected?
```bash
rmlogo photo.jpg --save-mask mask.png
# Inspect mask.png to see the detected watermark region
```

### Processing is slow?
Use more threads:
```bash
rmlogo --batch ./photos/ --threads 8
```

### Want to see progress details?
```bash
rmlogo --batch ./photos/ -v
```

---

## More Information

- **Full README:** Check [README.md](README.md) for advanced features (piping, JSON output, scripting)
- **Get help:** `rmlogo --help`
- **Check version:** `rmlogo --version`

---

**Live on PyPI:** https://pypi.org/project/rmlogo/
