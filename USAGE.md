# rmlogo Usage Guide

Detailed guide to all features and use cases.

## Table of Contents

1. [Single File Usage](#single-file-usage)
2. [Batch Processing](#batch-processing)
3. [Position Hints](#position-hints)
4. [Advanced Features](#advanced-features)
5. [Examples](#examples)
6. [Python API](#python-api)

---

## Single File Usage

### Basic removal
```bash
rmlogo input.jpg -o output.jpg
```

### Specify output format
```bash
rmlogo input.jpg -o output.png
rmlogo input.jpg -o output.jpeg
```

### With position hint
```bash
rmlogo input.jpg -o output.jpg --hint bottom-right
```

### Save detection mask (for debugging)
```bash
rmlogo input.jpg -o output.jpg --save-mask mask.png
```

### Verbose output (see processing details)
```bash
rmlogo input.jpg -o output.jpg -v
```

---

## Batch Processing

### Process an entire folder
```bash
rmlogo --batch /path/to/photos/
```

Creates output folder: `./cleaned_images_TIMESTAMP/`

### Specify output directory
```bash
rmlogo --batch /path/to/photos/ --output-dir /path/to/output/
```

### Filter by file pattern
```bash
# Only JPEGs
rmlogo --batch /photos/ --pattern "*.jpg"

# Multiple formats
rmlogo --batch /photos/ --pattern "*.jpg,*.png"

# All image formats
rmlogo --batch /photos/ --pattern "*.jpg,*.jpeg,*.png,*.gif"
```

### Control threading
```bash
# Auto-detect (default)
rmlogo --batch /photos/ --threads auto

# Use specific number
rmlogo --batch /photos/ --threads 4

# Max out all cores
rmlogo --batch /photos/ --threads 8
```

### Preview before processing (dry-run)
```bash
rmlogo --batch /photos/ --dry-run
# Shows what will be processed without making changes
```

### Quiet mode (suppress progress)
```bash
rmlogo --batch /photos/ -q
```

### Verbose mode (detailed progress)
```bash
rmlogo --batch /photos/ -v
# Shows processing time per image, detailed status
```

### Save results as JSON
```bash
rmlogo --batch /photos/ --json
# Creates: ./cleaned_images_TIMESTAMP/processing_log.json
```

---

## Position Hints

| Hint | Use Case | Example |
|------|----------|---------|
| `auto` | Auto-detect (default) | `rmlogo photo.jpg -o clean.jpg` |
| `bottom-right` | Logo in bottom-right corner | `rmlogo photo.jpg --hint bottom-right` |
| `bottom-left` | Logo in bottom-left corner | `rmlogo photo.jpg --hint bottom-left` |
| `top-right` | Logo in top-right corner | `rmlogo photo.jpg --hint top-right` |
| `top-left` | Logo in top-left corner | `rmlogo photo.jpg --hint top-left` |
| `center` | Logo in center of image | `rmlogo photo.jpg --hint center` |
| `full` | Watermark covers large area | `rmlogo photo.jpg --hint full` |

### Tips for position hints

- Start with `auto` (default)
- If detection is poor, try the corner where the watermark is
- If watermark is very faint, try `center`
- If watermark covers most of image, try `full`

---

## Advanced Features

### Piping (Unix/Linux/macOS)

Process files from stdin:

```bash
# Process files from find command
find /photos -name "*.jpg" | rmlogo --batch -

# Process files modified today
find /photos -name "*.jpg" -mtime 0 | rmlogo --batch -

# Process large files only
find /photos -name "*.jpg" -size +5M | rmlogo --batch -

# Combine with other tools
ls /photos/*.jpg | rmlogo --batch - --json | jq '.summary'
```

### PowerShell Integration (Windows)

```powershell
# Process all JPEGs in current folder
Get-ChildItem *.jpg | ForEach-Object { rmlogo $_.FullName -o "cleaned_$($_.Name)" }

# Process with batch mode
Get-ChildItem *.jpg | Select-Object -ExpandProperty FullName | rmlogo --batch -

# With filtering
Get-ChildItem *.jpg | Where-Object { $_.LastWriteTime -gt [datetime]::Today } | rmlogo --batch -
```

### JSON Output for Automation

```bash
rmlogo --batch /photos/ --json
```

Output file: `./cleaned_images_TIMESTAMP/processing_log.json`

```json
{
  "status": "success",
  "timestamp": "2025-03-07T15:30:00.000Z",
  "summary": {
    "total": 5,
    "succeeded": 5,
    "failed": 0,
    "total_time_ms": 12000,
    "average_time_ms": 2400
  },
  "results": [
    {
      "input": "/photos/photo1.jpg",
      "output": "./cleaned_images_20250307_153000/photo1_cleaned.jpg",
      "status": "success",
      "time_ms": 2100
    }
  ]
}
```

---

## Examples

### Photography workflow

```bash
# 1. Preview batch job
rmlogo --batch ./raw_photos/ --dry-run

# 2. Process with 4 threads
rmlogo --batch ./raw_photos/ --threads 4 --json

# 3. Check results
cat cleaned_images_*/processing_log.json | jq '.summary'
```

### Automated batch processing script

```bash
#!/bin/bash

INPUT_DIR="./watermarked_photos"
OUTPUT_DIR="./cleaned_$(date +%Y%m%d_%H%M%S)"

# Process
rmlogo --batch "$INPUT_DIR" --output-dir "$OUTPUT_DIR" --json

# Report
echo "Processing complete!"
echo "Results: $OUTPUT_DIR"

# Get summary
RESULTS="$OUTPUT_DIR/processing_log.json"
if [ -f "$RESULTS" ]; then
  SUCCEEDED=$(jq '.summary.succeeded' "$RESULTS")
  FAILED=$(jq '.summary.failed' "$RESULTS")
  echo "Success: $SUCCEEDED, Failed: $FAILED"
fi
```

### Quality check workflow

```bash
# Process images
rmlogo --batch /photos/ --threads 4 -v

# Check for failures
grep -r "failed" ./cleaned_images_*/processing_log.json

# Reprocess failures with verbose mode
rmlogo --batch /photos/failures/ -v --hint bottom-right
```

### Cloud integration

```bash
# Process and upload to S3
rmlogo --batch ./photos/ --json | \
  jq -r '.results[] | select(.status=="success") | .output' | \
  xargs -I {} aws s3 cp {} s3://my-bucket/cleaned/
```

---

## Python API

Use rmlogo in your Python code:

### Basic usage

```python
from rmlogo import remove_logo
from rmlogo.auto_mask import generate_mask
from PIL import Image
import numpy as np

# Load image
img = np.array(Image.open('photo.jpg'))

# Generate mask (auto-detect)
mask = generate_mask(img, hint='auto')

# Remove watermark
cleaned = remove_logo(img, mask, radius=5)

# Save result
Image.fromarray(cleaned).save('cleaned.jpg')
```

### With position hint

```python
from rmlogo import remove_logo
from rmlogo.auto_mask import generate_mask
import cv2
import numpy as np

# Load image
img = cv2.imread('photo.jpg')
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# Generate mask with position hint
mask = generate_mask(img, hint='bottom-right')

# Remove watermark
cleaned = remove_logo(img, mask, radius=5)

# Save
cv2.imwrite('cleaned.jpg', cv2.cvtColor(cleaned, cv2.COLOR_RGB2BGR))
```

### Batch processing in Python

```python
from rmlogo import remove_logo
from rmlogo.auto_mask import generate_mask
from PIL import Image
import numpy as np
from pathlib import Path

# Process folder
input_dir = Path('./photos')
output_dir = Path('./cleaned')
output_dir.mkdir(exist_ok=True)

for img_path in input_dir.glob('*.jpg'):
    # Load
    img = np.array(Image.open(img_path))
    
    # Detect and remove
    mask = generate_mask(img, hint='auto')
    cleaned = remove_logo(img, mask, radius=5)
    
    # Save
    output_path = output_dir / img_path.name
    Image.fromarray(cleaned).save(output_path)
    print(f'Processed: {output_path}')
```

---

## Tips & Tricks

### 1. Inspect detection before removing
```bash
rmlogo photo.jpg --save-mask mask.png
# Review mask.png to see what was detected
# Then proceed with removal if satisfied
```

### 2. Dry-run large batches
```bash
rmlogo --batch /1000_photos/ --dry-run
# Preview before committing to 20+ minutes of processing
```

### 3. Use verbose mode for troubleshooting
```bash
rmlogo photo.jpg -v
# Shows mask detection score and processing details
```

### 4. Combine with imagemagick for post-processing
```bash
# Remove watermark, then resize
rmlogo photo.jpg -o temp.jpg && \
convert temp.jpg -resize 1920x1080 final.jpg
```

### 5. Batch process with specific output naming
```bash
for f in photos/*.jpg; do
  rmlogo "$f" -o "cleaned_$(basename $f)" -q
done
```

---

## Performance Tips

1. **Use multiple threads:** `--threads 8` (default auto-detects)
2. **Quiet mode:** `-q` reduces I/O overhead for batch processing
3. **Filter first:** Use `--pattern` to avoid processing non-image files
4. **Dry-run first:** `--dry-run` before committing to large batches

---

## Troubleshooting

### Command not found
```bash
# Verify installation
python -m pip install rmlogo

# Check version
rmlogo --version
```

### Watermark not detected
```bash
# 1. Try specific position
rmlogo photo.jpg -o result.jpg --hint bottom-right

# 2. Inspect mask
rmlogo photo.jpg --save-mask mask.png
# Check if watermark appears in mask.png

# 3. Try different hint
rmlogo photo.jpg -o result.jpg --hint center
```

### Slow processing
```bash
# Check CPU cores available
nproc  # Linux/macOS
Get-ComputerInfo | Select-Object CsNumberOfLogicalProcessors  # PowerShell

# Use more threads
rmlogo --batch /photos/ --threads 8
```

### Poor quality results
```bash
# Watermark may not be semi-transparent grey
# Try different position hints:
rmlogo photo.jpg --hint top-left
rmlogo photo.jpg --hint center
rmlogo photo.jpg --hint full
```

---

**Need help?** Run `rmlogo --help` for command-line reference.

**Package:** https://pypi.org/project/rmlogo/
