# rmlogo Installation Guide

This guide walks you through installing and testing rmlogo on your PC.

---

## Prerequisites

- **Python 3.9 or higher** installed on your system
- **pip** (comes with Python)
- **Git** (optional, for cloning the repository)

### Check Your Python Version

```powershell
# Windows PowerShell
python --version

# macOS/Linux
python3 --version
```

Expected output: `Python 3.9.x` or higher

---

## Installation Method 1: From Local Directory (Recommended)

This is the best method for testing on another PC.

### Step 1: Copy Project Folder

Copy the entire `image-logo-remover` folder to your target PC using:
- USB drive
- Cloud storage (Google Drive, OneDrive, Dropbox)
- Network share
- Git clone (if you have GitHub access)

```bash
git clone https://github.com/CodewithanZeeL/image-logo-remover.git
cd image-logo-remover
```

### Step 2: Install in Editable Mode

```powershell
# Windows PowerShell
pip install -e .

# macOS/Linux
pip3 install -e .
```

**What this does:**
- Installs all dependencies (opencv-python, numpy, pillow, tqdm)
- Makes the `rmlogo` command available globally
- Allows you to modify code and test immediately

### Step 3: Verify Installation

```powershell
rmlogo --version
```

Expected output:
```
rmlogo 2.1.0
```

If you see this, installation is successful! ✅

---

## Installation Method 2: Using Virtual Environment (Isolated, Recommended for Testing)

This method creates an isolated Python environment, preventing conflicts with other projects.

### Step 1: Create Virtual Environment

```powershell
# Windows PowerShell
python -m venv rmlogo_env
rmlogo_env\Scripts\Activate.ps1

# macOS/Linux
python3 -m venv rmlogo_env
source rmlogo_env/bin/activate
```

After activation, your prompt will show `(rmlogo_env)` prefix.

### Step 2: Install rmlogo

```powershell
cd image-logo-remover
pip install -e .
```

### Step 3: Verify Installation

```powershell
rmlogo --version
```

Expected output: `rmlogo 2.1.0` ✅

### Step 4: Deactivate (When Done)

```powershell
# Windows
deactivate

# macOS/Linux
deactivate
```

---

## Quick Test After Installation

### Test 1: Help Command

```powershell
rmlogo --help
```

Should show full command documentation.

### Test 2: Process a Sample Image

```powershell
# Create a test with an existing image
rmlogo path/to/your/image.jpg
```

The tool will:
1. Ask where to save the cleaned image
2. Auto-detect the watermark
3. Remove it
4. Save the result

### Test 3: Test Gemini Hint Feature

```powershell
rmlogo image.jpg --bgrm "The watermark is in the bottom right corner"
```

Should output:
```
[Gemini hint detected: bottom-right]
Save cleaned image to: [./image_cleaned.jpg]
> 
[OK] Saved to: ./image_cleaned.jpg (2.1s)
```

### Test 4: Batch Processing

If you have multiple images:

```powershell
rmlogo --batch ./photos/ --dry-run
```

This shows what would be processed without actually processing.

---

## Troubleshooting

### Problem: "rmlogo command not found"

**Solution:**

1. Verify installation:
   ```powershell
   pip list | grep rmlogo
   ```
   Should show `rmlogo 2.1.0`

2. Reinstall:
   ```powershell
   pip uninstall rmlogo
   pip install -e .
   ```

3. Check Python path:
   ```powershell
   python -c "import sys; print(sys.executable)"
   ```

### Problem: "ModuleNotFoundError: No module named 'cv2'"

**Solution:**

Dependencies didn't install. Try:

```powershell
pip install opencv-python numpy pillow tqdm
```

Then verify:

```powershell
python -c "import cv2; print(cv2.__version__)"
```

### Problem: "File not found" or "Cannot read image"

**Solution:**

1. Check file exists:
   ```powershell
   ls path/to/image.jpg
   ```

2. Check file is a valid image (JPEG, PNG, BMP, GIF, TIFF, WebP)

3. Try with full absolute path:
   ```powershell
   rmlogo "C:\Users\YourName\Pictures\photo.jpg"
   ```

### Problem: Permission denied

**Solution (Windows):**

Run PowerShell as Administrator:
1. Right-click PowerShell
2. Select "Run as administrator"
3. Try again

**Solution (macOS/Linux):**

```bash
sudo pip install -e .
```

### Problem: Slow processing or freezing

**Solution:**

1. Check image size (must be reasonable, <50MB)
2. Try with verbose output to see progress:
   ```powershell
   rmlogo image.jpg -v
   ```
3. For batch, reduce thread count:
   ```powershell
   rmlogo --batch ./photos/ --threads 1
   ```

---

## Common Use Cases

### Use Case 1: Single Watermarked Photo

```powershell
rmlogo vacation.jpg
# → Saves to: vacation_cleaned.jpg
```

### Use Case 2: With Gemini AI Hint

```powershell
# First ask Gemini where the watermark is
# Then copy-paste its response:

rmlogo vacation.jpg --bgrm "The logo is in the lower right corner"
```

### Use Case 3: Batch Clean 100 Photos

```powershell
rmlogo --batch ./vacation_photos/ --threads 4 --json
# → Saves to: cleaned_images_TIMESTAMP/
# → Creates: processing_log.json with results
```

### Use Case 4: Verify Detection Before Processing

```powershell
rmlogo photo.jpg --save-mask mask_debug.png -v
# → Shows detection details
# → Saves: mask_debug.png (red overlay of detected watermark)
```

### Use Case 5: PowerShell Pipe (Windows)

```powershell
Get-ChildItem .\photos\*.jpg | rmlogo --batch -
```

### Use Case 6: Dry Run (Preview Without Processing)

```powershell
rmlogo --batch ./photos/ --dry-run
# → Shows: number of files, estimated time
# → Asks: "Continue? [Y/n]"
```

---

## File Organization

After installation, your folder structure looks like:

```
image-logo-remover/
├── rmlogo/                    # Main package (installed globally)
│   ├── __init__.py
│   ├── cli.py                # Command-line interface
│   ├── auto_mask.py          # Watermark detection
│   └── inference.py          # Image inpainting
├── pyproject.toml            # Package configuration
├── requirements.txt          # Dependencies list
├── USER_MANUAL.md           # Full documentation
├── INSTALL.md               # This file
└── [sample images for testing]
```

The `rmlogo/` folder gets installed system-wide by pip.

---

## Testing Checklist

After installation, verify everything works:

- [ ] `rmlogo --version` shows 2.1.0
- [ ] `rmlogo --help` displays all options
- [ ] Single image processing works
- [ ] Gemini hint (`--bgrm`) parsing works
- [ ] Output file saved correctly
- [ ] Batch processing works (if testing)
- [ ] No error messages

---

## Next Steps

1. **Read USER_MANUAL.md** — Full feature documentation
2. **Run `rmlogo --help`** — See all available options
3. **Test with your images** — Start with single files first
4. **Try batch mode** — For multiple images
5. **Experiment with hints** — Manual hints and Gemini integration

---

## Getting Help

If you encounter issues:

1. Check **Troubleshooting** section above
2. Read **USER_MANUAL.md** for detailed feature docs
3. Run in verbose mode: `rmlogo image.jpg -v`
4. Save detection mask: `rmlogo image.jpg --save-mask debug.png`
5. Report issue: [GitHub Issues](https://github.com/CodewithanZeeL/image-logo-remover/issues)

---

## Uninstalling

If you need to uninstall:

```powershell
pip uninstall rmlogo
```

This removes the package but keeps your image files safe.

---

## Version Info

- **Package:** rmlogo
- **Version:** 2.1.0
- **Python:** 3.9+
- **License:** GPL-3.0
- **Last Updated:** March 2025

---

**Happy testing! 🎉**
