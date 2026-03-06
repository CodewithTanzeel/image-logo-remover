# rmlogo Distribution Package

## Quick Start (2 Steps)

**For Windows (Recommended):**

```powershell
# Step 1: Extract rmlogo-2.1.0-dist.zip to any folder

# Step 2: Double-click install.bat

# Done! Run:
rmlogo --help
```

**For Manual Installation:**

```powershell
# Step 1: Extract the zip
# Step 2: Open PowerShell in the extracted folder
# Step 3: Run:
pip install --no-index --find-links=wheels -e .

# Step 4: Verify:
rmlogo --version
```

---

## What's in the Zip?

```
rmlogo-2.1.0-dist/
├── install.bat                  # Windows installer (DOUBLE-CLICK THIS)
├── rmlogo/                      # Python package code
│   ├── __init__.py
│   ├── cli.py                  # Command-line interface
│   ├── auto_mask.py            # Watermark detection
│   └── inference.py            # Image inpainting
├── wheels/                      # Pre-downloaded dependencies (OFFLINE)
│   ├── opencv_python-4.x.x.whl
│   ├── numpy-2.x.x.whl
│   ├── pillow-12.x.x.whl
│   ├── tqdm-4.x.x.whl
│   └── colorama-0.4.x.whl
├── pyproject.toml              # Package configuration
├── requirements.txt            # Dependency list
├── INSTALL.md                  # Step-by-step guide
├── USER_MANUAL.md              # Full documentation
├── README.md                   # Project info
├── LICENSE                     # GPL-3.0 license
└── test_rmlogo.py              # Validation script
```

**Total Size:** ~56 MB (mostly opencv-python and numpy)

---

## Installation Options

### Option 1: Windows (Easiest)

1. **Extract** `rmlogo-2.1.0-dist.zip` to any folder
2. **Double-click** `install.bat` 
3. **Wait** for installation to complete
4. **Run:** `rmlogo --help`

The batch file automatically:
- Checks for Python installation
- Installs all dependencies from `wheels/` folder (completely offline)
- Installs rmlogo in editable mode
- Verifies installation

### Option 2: Manual Installation (All Platforms)

1. **Extract** the zip file
2. **Open terminal/PowerShell** in the extracted folder
3. **Run:**
   ```powershell
   pip install --no-index --find-links=wheels -e .
   ```
4. **Verify:**
   ```powershell
   rmlogo --version
   ```

### Option 3: Virtual Environment (Isolated Testing)

For completely isolated testing without affecting your system:

```powershell
# Create virtual environment
python -m venv rmlogo_env
rmlogo_env\Scripts\Activate.ps1

# Install rmlogo
cd rmlogo-2.1.0-dist
pip install --no-index --find-links=wheels -e .

# Test
rmlogo --version

# Deactivate when done
deactivate
```

---

## Troubleshooting

### "Python is not installed or not in PATH"

**Problem:** The installer can't find Python.

**Solution:**

1. Install Python from [python.org](https://www.python.org/downloads/)
2. **IMPORTANT:** Check the box **"Add Python to PATH"** during installation
3. Restart your computer
4. Try `install.bat` again

### "ERROR: Installation failed"

**Problem:** The pip install command failed.

**Solution:**

1. Try running as Administrator:
   - Right-click `install.bat`
   - Select "Run as administrator"
   
2. Or manually install:
   ```powershell
   pip install --no-index --find-links=wheels -e .
   ```

3. Check Python version (must be 3.9+):
   ```powershell
   python --version
   ```

### "rmlogo command not found"

**Problem:** Command not working after installation.

**Solution:**

1. Verify installation:
   ```powershell
   pip show rmlogo
   ```
   Should show: `rmlogo 2.1.0`

2. Reinstall:
   ```powershell
   pip uninstall rmlogo
   pip install --no-index --find-links=wheels -e .
   ```

3. Restart PowerShell/Terminal

### "wheels folder not found"

**Problem:** The wheels folder is missing from the zip.

**Solution:**

Make sure you extracted the **entire** zip file, not just some files inside it. The folder structure should be:

```
rmlogo-2.1.0-dist/
├── install.bat
├── wheels/           ← This must exist!
├── rmlogo/
└── [other files]
```

---

## Next Steps After Installation

### 1. Verify Installation

```powershell
rmlogo --version
# Output: rmlogo 2.1.0

rmlogo --help
# Shows all available commands
```

### 2. Test With Your Images

**Single image:**
```powershell
rmlogo your_photo.jpg
```

**With Gemini hint:**
```powershell
rmlogo your_photo.jpg --bgrm "The watermark is in the bottom right"
```

### 3. Read the Documentation

- **INSTALL.md** — Detailed installation guide
- **USER_MANUAL.md** — Complete feature documentation with examples

### 4. Batch Processing (Multiple Images)

```powershell
rmlogo --batch ./photos/ --threads 4 --json
```

---

## Important Notes

### Offline Installation

✅ **This zip works completely offline.** No internet needed after extraction.

All Python dependencies are bundled in the `wheels/` folder:
- opencv-python
- numpy
- pillow
- tqdm
- colorama (dependency of tqdm)

### Python Requirement

✅ **Python 3.9+ must be installed on your PC** before using this package.

You can download Python from: https://www.python.org/downloads/

### Windows Only

⚠️ **The `wheels/` folder contains Windows-only binaries** (win_amd64).

If you're on **macOS or Linux**, you'll need to either:
1. Install Python packages via internet: `pip install -r requirements.txt`
2. Contact the developer for platform-specific wheels

### File Permissions

For Linux/macOS users, after extraction:

```bash
chmod +x rmlogo-2.1.0-dist/rmlogo/cli.py
pip install --no-index --find-links=wheels -e .
```

---

## Virtual Environment (Recommended for Testing)

To test rmlogo without affecting your system Python:

```powershell
# Create isolated environment
python -m venv test_rmlogo

# Activate
test_rmlogo\Scripts\Activate.ps1

# Install rmlogo
cd rmlogo-2.1.0-dist
pip install --no-index --find-links=wheels -e .

# Use rmlogo
rmlogo --help

# Deactivate when done
deactivate

# Clean up (delete folder when done testing)
rmdir /s test_rmlogo
```

---

## Uninstalling

If you want to remove rmlogo:

```powershell
pip uninstall rmlogo
```

This removes the package but keeps your image files safe.

To also remove dependencies:

```powershell
pip uninstall opencv-python numpy pillow tqdm colorama -y
```

---

## Support

**Documentation:**
- INSTALL.md — Full installation guide
- USER_MANUAL.md — Complete feature documentation
- test_rmlogo.py — Validation script

**Run test script:**
```powershell
python test_rmlogo.py
```

This validates the installation and runs tests.

---

## Version Info

- **Package:** rmlogo
- **Version:** 2.1.0
- **Python:** 3.9 or higher
- **License:** GPL-3.0
- **Platform:** Windows (this zip)
- **Last Updated:** March 2025

---

## File Sizes

| File | Size | Purpose |
|------|------|---------|
| install.bat | 2 KB | Windows installer |
| opencv_python.whl | 39 MB | Computer vision library |
| numpy.whl | 12 MB | Numerical computing |
| pillow.whl | 7 MB | Image I/O |
| tqdm.whl | 0.1 MB | Progress bars |
| rmlogo package | 35 KB | Main application |
| Docs | 70 KB | Documentation |
| **Total** | **~56 MB** | Complete package |

---

**Ready to use! Extract and double-click `install.bat`** 🎉
