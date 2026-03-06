# rmlogo User Manual

**rmlogo** is a professional Python package for removing watermarks and logos from images using automatic detection and OpenCV inpainting. It works offline, requires no API keys, and is designed for both single-file and batch processing workflows.

---

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Single File Processing](#single-file-processing)
4. [Gemini AI Integration (`--bgrm`)](#gemini-ai-integration)
5. [Position Hints (`--hint`)](#position-hints)
6. [Batch Processing](#batch-processing)
7. [Advanced Features](#advanced-features)
8. [Command Reference](#command-reference)
9. [Troubleshooting](#troubleshooting)
10. [Examples](#examples)

---

## Installation

### Requirements

- **Python:** 3.9 or higher
- **Operating System:** Windows (PowerShell), macOS, or Linux

### Install Locally (For Testing on Another PC)

Clone or copy the project folder, then install in editable mode:

```powershell
# Navigate to the project folder
cd image-logo-remover

# Install package locally
pip install -e .
```

This installs rmlogo and makes the `rmlogo` command available system-wide.

### Verify Installation

```powershell
rmlogo --version
```

Expected output: `rmlogo 2.1.0`

### Future: Install from PyPI

Once published, you'll be able to install with a single command:

```powershell
pip install rmlogo
```

---

## Quick Start

The simplest use case — remove a watermark from a single image:

```powershell
rmlogo photo.jpg
```

What happens:
1. Tool asks where to save the cleaned image
2. You type a path (or press Enter for default: `photo_cleaned.jpg`)
3. Tool auto-detects the watermark and removes it
4. Cleaned image is saved
5. Done!

Example interaction:

```powershell
$ rmlogo photo.jpg
Save cleaned image to: [./photo_cleaned.jpg]
> 
[OK] Saved to: ./photo_cleaned.jpg (2.1s)
```

---

## Single File Processing

### Basic Usage

```powershell
rmlogo input.jpg
```

The tool prompts for an output path. Press Enter to accept the default (`input_cleaned.jpg`).

### Specifying Output Path Upfront

```powershell
rmlogo photo.jpg -o my_result.png
```

You're still prompted, but the default changes to `my_result.png`.

### With Verbose Output

See detailed processing steps:

```powershell
rmlogo photo.jpg -v
```

Output will show:
- Image dimensions
- Watermark detection results (pixels detected)
- Inpainting progress
- Save status

### Save Detection Mask (Debugging)

To visualize what region the tool detected as a watermark:

```powershell
rmlogo photo.jpg --save-mask debug_mask.png
```

This saves a red-overlay image showing the detected watermark region. Useful for tuning hints.

---

## Gemini AI Integration

### What is `--bgrm`?

The `--bgrm` flag lets you paste Gemini AI's response about watermark location. The tool parses the text **offline** (no API call) and extracts a position hint.

**Complete offline — no API key needed, no network required.**

### How to Use It

#### Step 1: Ask Gemini

Go to [Google Gemini](https://gemini.google.com) and ask:

```
"Where is the watermark in this image?" 
[Paste/upload your image]
```

Gemini responds something like:

```
"The watermark appears in the bottom right corner of the image."
```

#### Step 2: Copy the Response

Copy Gemini's response.

#### Step 3: Run rmlogo with `--bgrm`

```powershell
rmlogo photo.jpg --bgrm "The watermark appears in the bottom right corner of the image"
```

#### Step 4: Tool Detects & Processes

Output:

```
[Gemini hint detected: bottom-right]
Save cleaned image to: [./photo_cleaned.jpg]
> 
[OK] Saved to: ./photo_cleaned.jpg (2.1s)
```

### Keyword Mapping

The parser looks for these keywords in the Gemini response:

| Keywords | Detected Hint |
|----------|---------------|
| `bottom right`, `lower right`, `bottom-right` | `bottom-right` |
| `bottom left`, `lower left`, `bottom-left` | `bottom-left` |
| `top right`, `upper right`, `top-right` | `top-right` |
| `top left`, `upper left`, `top-left` | `top-left` |
| `center`, `middle`, `centered` | `center` |
| `entire`, `whole`, `everywhere`, `full` | `full` |
| (nothing matched) | `auto` (fallback) |

### Example Responses

**Example 1:**

```
Gemini: "The copyright text is in the bottom-right area of the photo."
rmlogo: [Gemini hint detected: bottom-right]
```

**Example 2:**

```
Gemini: "There's a logo in the upper left corner."
rmlogo: [Gemini hint detected: top-left]
```

**Example 3:**

```
Gemini: "I'm not sure where the watermark is."
rmlogo: [Falls back to auto-detection]
```

### When to Use `--bgrm`

- When auto-detection doesn't work perfectly
- When you want faster processing (manual hint is sometimes quicker)
- When the watermark is in an unusual location
- When Gemini's response is more reliable than auto-detection

### When NOT to Use `--bgrm`

- Most of the time — auto-detection works great for corner watermarks
- If typing the response is slower than just using `--hint`
- For large batch jobs (too much typing)

---

## Position Hints

### Manual Position Hints (`--hint`)

Instead of using Gemini, you can manually specify the watermark location:

```powershell
rmlogo photo.jpg --hint bottom-right
```

### Available Hints

| Hint | When to Use |
|------|-------------|
| `auto` | Automatically detect (default, most accurate) |
| `bottom-right` | Watermark in bottom-right corner |
| `bottom-left` | Watermark in bottom-left corner |
| `top-right` | Watermark in top-right corner |
| `top-left` | Watermark in top-left corner |
| `center` | Watermark near center of image |
| `full` | Watermark covers entire image (rare) |

### Examples

```powershell
# Bottom-right corner (common for logos)
rmlogo photo.jpg --hint bottom-right

# Top-left corner
rmlogo photo.jpg --hint top-left

# Centered watermark (text overlay)
rmlogo photo.jpg --hint center

# Entire image (semi-transparent overlay)
rmlogo photo.jpg --hint full
```

### Priority: `--bgrm` Overrides `--hint`

If you provide both:

```powershell
rmlogo photo.jpg --hint top-left --bgrm "watermark is bottom right"
```

The `--bgrm` hint takes priority → `bottom-right` is used.

---

## Batch Processing

### Process Multiple Images

Remove watermarks from all images in a folder:

```powershell
rmlogo --batch ./photos/
```

Output:
- Auto-creates folder: `cleaned_images_20250306_143502/`
- All cleaned images saved there
- Progress bar shows real-time processing

### With File Pattern Filter

Process only JPEG files:

```powershell
rmlogo --batch ./photos/ --pattern "*.jpg"
```

Multiple patterns:

```powershell
rmlogo --batch ./photos/ --pattern "*.jpg,*.jpeg,*.png"
```

### Using Multiple Threads

Faster processing with parallel workers:

```powershell
rmlogo --batch ./photos/ --threads 4
```

Auto-detection (default): uses half your CPU cores, capped at 8.

### Dry Run (Preview)

Preview what will be processed without actually processing:

```powershell
rmlogo --batch ./photos/ --dry-run
```

Output shows:
- Number of images found
- File sizes
- Estimated processing time
- Prompts: "Continue? [Y/n]"

### Custom Output Directory

```powershell
rmlogo --batch ./photos/ --output-dir ./my_cleaned/
```

All cleaned images go to `./my_cleaned/` instead of a timestamped folder.

### JSON Logging

Get structured results for automation:

```powershell
rmlogo --batch ./photos/ --json
```

Creates `cleaning_images_*/processing_log.json` with:
- Total, succeeded, failed counts
- Processing time per image
- Individual results with status and error details

Example JSON:

```json
{
  "status": "success",
  "timestamp": "2025-03-06T14:35:02.123Z",
  "summary": {
    "total": 5,
    "succeeded": 5,
    "failed": 0,
    "total_time_ms": 10500,
    "average_time_ms": 2100
  },
  "results": [
    {
      "input": "./photos/photo1.jpg",
      "output": "./cleaned_images_20250306_143502/photo1_cleaned.jpg",
      "status": "success",
      "time_ms": 2100
    }
  ]
}
```

### Suppress Progress Output

For automated/silent operation:

```powershell
rmlogo --batch ./photos/ -q
```

Only errors are printed.

---

## Advanced Features

### Piping (Unix/PowerShell/WSL)

#### Unix Example: Find recent JPEGs

```bash
find . -name "*.jpg" -mtime -1 | rmlogo --batch -
```

Processes all JPEGs modified in the last 24 hours.

#### PowerShell Example: Files from today

```powershell
Get-ChildItem *.jpg | Where-Object { $_.LastWriteTime -gt [datetime]::Today } | rmlogo --batch -
```

#### WSL Example: Process with filter

```bash
ls /mnt/c/Photos/*.jpg | rmlogo --batch - --json
```

Use `-` as the batch path to read from stdin (piped input).

### Verbose Mode

See all processing details:

```powershell
rmlogo --batch ./photos/ -v
```

Shows:
- Processing steps for each image
- Watermark detection info
- Mask coverage percentage
- Inpainting details

### Help

View all options:

```powershell
rmlogo --help
```

---

## Command Reference

### Positional Arguments

| Argument | Description |
|----------|-------------|
| `INPUT` | Path to image file (optional if using `--batch`) |

### Single File Options

| Flag | Description |
|------|-------------|
| `-o, --output PATH` | Output path (default: `input_cleaned.ext`) |

### Common Options

| Flag | Description |
|------|-------------|
| `--hint {auto,bottom-right,bottom-left,top-right,top-left,center,full}` | Position hint (default: `auto`) |
| `--bgrm TEXT` | Paste Gemini response (parsed offline) |
| `--save-mask PATH` | Save detected mask visualization |

### Batch Options

| Flag | Description |
|------|-------------|
| `--batch PATH` | Batch mode folder (use `-` for stdin) |
| `--pattern PATTERNS` | File pattern filter (e.g., `*.jpg,*.png`) |
| `--threads N` | Number of worker threads (default: auto) |
| `--output-dir PATH` | Custom output directory |
| `--dry-run` | Preview without processing |

### Output Options

| Flag | Description |
|------|-------------|
| `-q, --quiet` | Suppress progress output |
| `-v, --verbose` | Show detailed messages |
| `--json` | Export results as JSON |

### Information

| Flag | Description |
|------|-------------|
| `--version` | Show version |
| `-h, --help` | Show help |

---

## Troubleshooting

### "Cannot read image file"

**Problem:** Image format not supported.

**Solution:** Ensure file is a valid image (JPEG, PNG, BMP, GIF, TIFF, WebP).

```powershell
rmlogo photo.tiff  # Supported
rmlogo photo.txt   # Error: not an image
```

### "File already exists. Overwrite? [y/N]"

**Problem:** Output file already exists.

**Solution:** Type `y` to overwrite, or choose a different filename.

```
Save cleaned image to: [./photo_cleaned.jpg]
> ./photo_cleaned.jpg
File already exists. Overwrite? [y/N]: y
```

### Watermark Not Fully Removed

**Problem:** Large/semi-transparent watermarks can leave artifacts.

**Cause:** OpenCV inpainting works best on corner watermarks (<20% image coverage).

**Solutions:**
1. Try a position hint: `--hint bottom-right`
2. Use Gemini hint: `--bgrm "describe watermark location"`
3. Save the mask to inspect: `--save-mask debug.png`
4. If it's covering >30%, the tool has limitations

### "No image files found"

**Problem:** Batch folder has no images.

**Solution:** Check folder path and file extensions.

```powershell
# Verify folder exists and has images
ls ./photos/ -Filter *.jpg

# Then run batch with explicit pattern
rmlogo --batch ./photos/ --pattern "*.jpg"
```

### Slow Processing

**Problem:** Batch processing is slow.

**Solutions:**
1. Increase thread count: `--threads 8`
2. Use pattern filter to process fewer files
3. Reduce image sizes (resize first)
4. Ensure SSD storage (not USB or network drive)

**Typical performance:**
- Single image: ~2 seconds
- 10 images, 1 thread: ~20 seconds
- 10 images, 4 threads: ~8 seconds

### Import Error After Installation

**Problem:** `ModuleNotFoundError: No module named 'rmlogo'`

**Solution:** Ensure installation was successful.

```powershell
# Reinstall
pip install -e .

# Verify
rmlogo --version
```

---

## Examples

### Example 1: Single watermarked photo

```powershell
$ rmlogo vacation.jpg
Save cleaned image to: [./vacation_cleaned.jpg]
> 
[OK] Saved to: ./vacation_cleaned.jpg (2.1s)
```

### Example 2: Use Gemini hint

```powershell
$ rmlogo vacation.jpg --bgrm "watermark is in the bottom right corner"
[Gemini hint detected: bottom-right]
Save cleaned image to: [./vacation_cleaned.jpg]
> 
[OK] Saved to: ./vacation_cleaned.jpg (1.9s)
```

### Example 3: Manual position hint

```powershell
$ rmlogo vacation.jpg --hint top-left
Save cleaned image to: [./vacation_cleaned.jpg]
> 
[OK] Saved to: ./vacation_cleaned.jpg (2.0s)
```

### Example 4: Batch process folder

```powershell
$ rmlogo --batch ./photos/ --threads 4
Found 25 images
Output directory: cleaned_images_20250306_143502
Using 4 threads

Processing |████████████████████████| 25/25 [00:54<00:00, 2.16s/img]

======================================================================
Summary: 25/25 passed | Failed: 0
Total time: 54.00s | Average: 2.16s per image
Output directory: cleaned_images_20250306_143502
======================================================================
```

### Example 5: Batch with JSON output

```powershell
$ rmlogo --batch ./photos/ --json --quiet
$ cat .\cleaned_images_*/processing_log.json | jq '.summary'
{
  "total": 25,
  "succeeded": 25,
  "failed": 0,
  "total_time_ms": 54000,
  "average_time_ms": 2160
}
```

### Example 6: Dry run (preview)

```powershell
$ rmlogo --batch ./photos/ --dry-run

----------------------------------------------------------------------
DRY RUN MODE - Preview Only
----------------------------------------------------------------------
Found: 25 images

  - photo1.jpg (2.50 MB)
  - photo2.jpg (3.10 MB)
  - photo3.jpg (2.80 MB)
  ... and 22 more files

Total disk needed: ~75.0 MB
Estimated time: ~52.5s
Output folder: cleaned_images_20250306_143502

Continue? [Y/n] n
```

### Example 7: Unix pipe with find

```bash
$ find ./photos -name "*.jpg" -newer photo_baseline.txt | rmlogo --batch - -q
```

Process only JPEGs modified after `photo_baseline.txt`.

### Example 8: PowerShell pipe

```powershell
$ Get-ChildItem .\photos\*.jpg | rmlogo --batch - -v
Reading filenames from stdin...
Processing |████████████████████████| 5/5 [00:10<00:00, 2.00s/img]
...
```

### Example 9: Save detection mask (debug)

```powershell
$ rmlogo photo.jpg --save-mask debug_mask.png -v
Loading image: photo.jpg
Image size: 1920×1080
Detecting watermark (hint=auto)...
Detected watermark region: 45230 pixels (2.19%)
Saving mask visualization: debug_mask.png
Removing watermark...
Saving result: photo_cleaned.jpg
[OK] Saved to: photo_cleaned.jpg (2.1s)
```

Then open `debug_mask.png` to see a red overlay of the detected watermark region.

---

## Tips & Best Practices

### Best For

✅ Corner watermarks (bottom-right, top-right, etc.)  
✅ Small text/logo overlays  
✅ Semi-transparent watermarks  
✅ Batch processing large photo collections  
✅ Watermarks on uniform backgrounds  

### Not Ideal For

❌ Large watermarks covering >30% of image  
❌ Watermarks on textured/detailed backgrounds  
❌ Solid/opaque watermarks  
❌ Watermarks in the center with complex content behind  

### Workflow Tips

1. **Test on one image first**
   ```powershell
   rmlogo sample.jpg
   ```
   Check quality before batch processing.

2. **Use Gemini for unclear cases**
   ```powershell
   rmlogo photo.jpg --bgrm "describe watermark location"
   ```
   Let AI help find the hint.

3. **Always do a dry-run for large batches**
   ```powershell
   rmlogo --batch ./photos/ --dry-run
   ```
   Verify before processing 100+ images.

4. **Enable verbose mode for troubleshooting**
   ```powershell
   rmlogo photo.jpg -v
   ```
   See what's happening step-by-step.

5. **Save the mask for quality control**
   ```powershell
   rmlogo photo.jpg --save-mask mask.png
   ```
   Inspect to verify detection is correct.

---

## Support & Feedback

For issues, feature requests, or feedback:

- **GitHub Issues:** [Report an issue](https://github.com/CodewithanZeeL/image-logo-remover/issues)
- **Documentation:** This manual covers all features
- **Examples:** See the "Examples" section above for common use cases

---

## Version

**rmlogo 2.1.0** — March 2025

**Technologies:**
- Python 3.9+
- OpenCV (cv2)
- NumPy
- Pillow
- tqdm

**License:** GPL-3.0

---

## Changelog

### v2.1.0 (Current)

- ✨ **Repackaged as `rmlogo` with proper Python package structure**
- ✨ **New `--bgrm` flag for Gemini AI hint integration** (offline text parsing)
- ✨ **Improved single-file flow:** Always prompts for output path, asks before overwriting
- ✨ **Removed `--no-ask` flag** — prompting is always on for single mode
- 📝 **Comprehensive user manual**
- 🔧 **Updated entry point:** `rmlogo` command

### v2.0.0 (Previous)

- CLI-only focus
- Automatic watermark detection
- Multi-threaded batch processing
- Piping support
- JSON logging

---

**Happy watermark removing! 🎉**
