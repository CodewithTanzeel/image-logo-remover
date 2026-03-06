# rmlogo Quick Reference Guide

## Installation (One-time Setup)

**Windows (Easiest):**
1. Extract `rmlogo-2.1.0-dist.zip`
2. Double-click `install.bat`
3. Done! The command is ready to use.

**Manual (Any OS):**
```bash
pip install --no-index --find-links=wheels -e .
```

## Basic Usage

### Single File (Interactive)
```bash
rmlogo photo.jpg
# Saves to: cleaned_images/photo_cleaned.jpg (you can change path)
```

### Single File (Explicit Output)
```bash
rmlogo photo.jpg -o result.png
```

### With Watermark Position Hint
```bash
rmlogo photo.jpg --hint bottom-right
# Hints: auto, bottom-right, bottom-left, top-right, top-left, center, full
```

### Using AI Description (Offline)
```bash
rmlogo photo.jpg --bgrm "watermark is in bottom right corner"
# Automatically parsed to extract position hint
```

## Batch Processing (Multiple Files)

### Process Entire Folder
```bash
rmlogo --batch /path/to/folder/
```

### Process Only JPEGs
```bash
rmlogo --batch /path --pattern "*.jpg"
```

### Preview Without Processing
```bash
rmlogo --batch /path --dry-run
```

### Use Multiple Threads
```bash
rmlogo --batch /path --threads 4 -v
```

### Process Files from Pipe (Linux/macOS)
```bash
find . -name "*.jpg" | rmlogo --batch -
```

## Advanced Options

| Option | Purpose | Example |
|--------|---------|---------|
| `-o PATH` | Output file (single mode) | `rmlogo img.jpg -o clean.png` |
| `--hint` | Watermark position | `--hint top-left` |
| `--bgrm TEXT` | Parse AI description (offline) | `--bgrm "bottom right corner"` |
| `--save-mask PATH` | Save detected mask | `--save-mask mask.png` |
| `--batch PATH` | Process folder | `--batch /images` |
| `--pattern` | File filter | `--pattern "*.jpg,*.png"` |
| `--threads N` | Worker threads | `--threads 8` |
| `--output-dir` | Output folder | `--output-dir results/` |
| `--dry-run` | Preview batch job | `--dry-run` |
| `-q, --quiet` | Suppress output | Useful for scripts |
| `-v, --verbose` | Show details | See detailed progress |
| `--json` | JSON output | For automation |
| `--version` | Show version | `rmlogo --version` |

## Position Hints

| Hint | Best For |
|------|----------|
| `auto` | Default - automatic detection |
| `bottom-right` | Logo in bottom-right corner |
| `bottom-left` | Logo in bottom-left corner |
| `top-right` | Logo in top-right corner |
| `top-left` | Logo in top-left corner |
| `center` | Logo near center of image |
| `full` | Watermark covers large area |

## AI Description Parsing (--bgrm)

Simply paste how you describe the watermark position. The tool parses it offline:

✅ **Works:**
- "watermark is in bottom right"
- "logo at the top left corner"
- "centered text"
- "watermark fills the whole image"
- "in the bottom right corner of the photo"

❌ **Doesn't work:**
- Requires internet (completely offline)
- Cannot analyze image content (use `--hint` or `--save-mask` instead)
- Doesn't remove watermarks from specific regions (use `--hint` instead)

## Common Workflows

### Quick Single Image
```bash
rmlogo photo.jpg -o result.jpg
```

### Batch with Position Hint
```bash
rmlogo --batch /photos --hint bottom-right --threads 4 -v
```

### Preview Batch Job
```bash
rmlogo --batch /photos --dry-run
```

### Save Detection Mask for Inspection
```bash
rmlogo photo.jpg --save-mask mask.jpg
# Shows what the algorithm detected as watermark
```

### Batch with Custom Output Folder
```bash
rmlogo --batch /photos --output-dir ./cleaned -v
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Command not found | Run `install.bat` again or check PATH |
| Installation fails | Run PowerShell as Administrator, then `install.bat` |
| Poor results | Try `--hint` to guide detection or `--save-mask` to inspect |
| Slow processing | Use `--threads N` (e.g., `--threads 8`) |
| Output folder full | Use `--output-dir /new/path` to redirect |

## Getting Help

```bash
rmlogo --help          # Full command help
rmlogo --version       # Show version (2.1.0)
```

Check documentation files:
- `USER_MANUAL.md` - Complete feature guide
- `INSTALL.md` - Detailed installation instructions
- `README.md` - Project overview

## Output Locations

By default, cleaned images are saved to:
- **Single mode:** Ask you where to save
- **Batch mode:** `cleaned_images_TIMESTAMP/` folder in current directory

Override with `--output-dir`:
```bash
rmlogo --batch /photos --output-dir /my/results
```

## Tips & Tricks

1. **Inspect detected mask first:**
   ```bash
   rmlogo photo.jpg --save-mask mask.png
   # Review mask.png to see what was detected
   # Then run actual removal with appropriate --hint
   ```

2. **Dry-run before batch processing:**
   ```bash
   rmlogo --batch /photos --dry-run
   # See what files will be processed
   ```

3. **Verbose mode for debugging:**
   ```bash
   rmlogo --batch /photos -v
   # See detailed progress for each file
   ```

4. **Use AI hints for consistent results:**
   ```bash
   rmlogo photo.jpg --bgrm "watermark in top right"
   # Offline parsing - no internet needed
   ```

---

**Version:** 2.1.0  
**Platform:** Windows (x64), Python 3.9+  
**License:** GPL-3.0
