# How to Upload Dataset to Kaggle

This guide will help you upload the watermark removal dataset to Kaggle and use it in your notebook.

## Prerequisites

1. **Kaggle Account**: Create one at https://www.kaggle.com
2. **Kaggle API Token**: Download from https://www.kaggle.com/settings (Account tab > "Create New API Token")

## Method 1: Upload via Kaggle Website (Easiest)

### Step 1: Prepare Dataset Folder

The dataset is already prepared in the `wm-nown/` folder with the correct structure.

### Step 2: Create ZIP File

**On Windows:**
```cmd
cd C:\Users\FATTANI COMPUTERS\OneDrive\Documents\image-logo-remover\watermark_removal_dataset
powershell Compress-Archive -Path wm-nown\* -DestinationPath watermark-removal-dataset.zip
```

**Or manually:**
1. Navigate to the `wm-nown` folder
2. Select all contents (train, valid, test folders + CSV + JSON files)
3. Right-click > "Send to" > "Compressed (zipped) folder"
4. Name it: `watermark-removal-dataset.zip`

### Step 3: Upload to Kaggle

1. Go to https://www.kaggle.com/datasets
2. Click **"New Dataset"** button
3. Fill in the details:
   - **Title**: `Watermark Removal Image Pairs Dataset`
   - **Subtitle**: `Paired watermarked and clean images for training watermark removal models`
   - **Description**: Copy from `wm-nown/dataset-metadata.json` or use the description below
4. Click **"Choose Files"** and select `watermark-removal-dataset.zip`
5. Wait for upload to complete
6. Add tags (keywords):
   - `computer vision`
   - `image processing`
   - `deep learning`
   - `autoencoder`
   - `watermark removal`
   - `image restoration`
7. Set license: **GPL 3.0**
8. Click **"Create"**

### Step 4: Publish Dataset

1. Review the dataset preview
2. Click **"Publish"** when ready
3. Your dataset URL will be: `https://www.kaggle.com/datasets/YOUR_USERNAME/watermark-removal-image-pairs`

---

## Method 2: Upload via Kaggle CLI (Advanced)

### Step 1: Install Kaggle CLI

```bash
pip install kaggle
```

### Step 2: Configure API Token

**On Windows:**
```cmd
mkdir %USERPROFILE%\.kaggle
copy path\to\kaggle.json %USERPROFILE%\.kaggle\kaggle.json
```

**On Linux/Mac:**
```bash
mkdir -p ~/.kaggle
cp path/to/kaggle.json ~/.kaggle/kaggle.json
chmod 600 ~/.kaggle/kaggle.json
```

### Step 3: Update Metadata File

Edit `wm-nown/dataset-metadata.json` and update the `id` field:
```json
{
  "id": "YOUR_KAGGLE_USERNAME/watermark-removal-image-pairs",
  ...
}
```

### Step 4: Create Dataset

```bash
cd C:\Users\FATTANI COMPUTERS\OneDrive\Documents\image-logo-remover\watermark_removal_dataset
kaggle datasets create -p wm-nown -r zip
```

This will:
1. Zip the `wm-nown` folder
2. Upload to Kaggle
3. Create the dataset using metadata from `dataset-metadata.json`

### Step 5: Update Dataset (if needed)

If you need to update the dataset later:
```bash
kaggle datasets version -p wm-nown -m "Updated dataset with fixes" -r zip
```

---

## Method 3: Using Python API

### Step 1: Install and Configure

```bash
pip install kaggle
```

Configure API token as in Method 2.

### Step 2: Create Upload Script

Create `upload_to_kaggle.py`:

```python
import os
import json
from kaggle.api.kaggle_api_extended import KaggleApi

# Initialize API
api = KaggleApi()
api.authenticate()

# Create dataset
dataset_path = "wm-nown"
username = "YOUR_KAGGLE_USERNAME"  # Replace with your username

# Create new dataset
api.dataset_create_new(
    folder=dataset_path,
    dir_mode='zip',
    convert_to_csv=False,
    public=True
)

print("Dataset uploaded successfully!")
print(f"View at: https://www.kaggle.com/datasets/{username}/watermark-removal-image-pairs")
```

### Step 3: Run Script

```bash
python upload_to_kaggle.py
```

---

## Using the Dataset in Kaggle Notebook

### Step 1: Create New Notebook

1. Go to https://www.kaggle.com/code
2. Click **"New Notebook"**
3. Enable **GPU** (Settings > Accelerator > GPU T4 x2)

### Step 2: Add Dataset to Notebook

**Option A: From UI**
1. Click **"+ Add Data"** on the right sidebar
2. Search for "watermark removal image pairs"
3. Click **"Add"**

**Option B: In Code**
The dataset will be available at:
```
/kaggle/input/watermark-removal-image-pairs/
```

### Step 3: Copy the Notebook Code

You can either:

**Option A: Upload the notebook**
1. Download `watermark-removal-autoencoder-kaggle.ipynb`
2. On Kaggle, click **"Import Notebook"**
3. Upload the `.ipynb` file

**Option B: Copy-paste code**
1. Open `watermark-removal-autoencoder-kaggle.ipynb`
2. Copy cells into your Kaggle notebook

### Step 4: Run the Notebook

1. Make sure GPU is enabled
2. Click **"Run All"** or run cells sequentially
3. Training will take 1-2 hours on Kaggle's free GPU

---

## Dataset Structure on Kaggle

Once uploaded, the dataset structure will be:

```
/kaggle/input/watermark-removal-image-pairs/
├── train/
│   ├── watermark/      (641 images)
│   └── no-watermark/   (641 images)
├── valid/
│   ├── watermark/      (80 images)
│   └── no-watermark/   (80 images)
├── test/
│   ├── watermark/      (81 images)
│   └── no-watermark/   (81 images)
├── train_pairs.csv
├── valid_pairs.csv
├── test_pairs.csv
└── dataset_stats.json
```

---

## Dataset Description (for Kaggle)

Use this as your dataset description:

```markdown
# Watermark Removal Image Pairs Dataset

## Overview
This dataset contains **802 paired images** for training deep learning models to remove watermarks from images. Each pair consists of a watermarked image and the corresponding clean (watermark-free) image.

## Dataset Statistics
- **Total pairs**: 802
- **Training set**: 641 pairs (79.9%)
- **Validation set**: 80 pairs (10.0%)
- **Test set**: 81 pairs (10.1%)
- **Image dimensions**: 512×512 pixels
- **Format**: JPEG (quality 95)
- **Total size**: ~98 MB

## Use Cases
1. Train watermark removal models
2. Practice image-to-image translation
3. Experiment with autoencoders and U-Net architectures
4. Implement perceptual loss functions
5. Build GAN-based solutions (Pix2Pix, CycleGAN)

## Quick Start
```python
import tensorflow as tf
from pathlib import Path

# Load dataset
DATASET_PATH = '/kaggle/input/watermark-removal-image-pairs'
train_wm_dir = Path(DATASET_PATH) / 'train' / 'watermark'
train_clean_dir = Path(DATASET_PATH) / 'train' / 'no-watermark'

# Create data pipeline
def load_image_pair(wm_path, clean_path):
    wm_img = tf.io.read_file(wm_path)
    wm_img = tf.image.decode_jpeg(wm_img, channels=3)
    wm_img = tf.cast(wm_img, tf.float32) / 255.0
    
    clean_img = tf.io.read_file(clean_path)
    clean_img = tf.image.decode_jpeg(clean_img, channels=3)
    clean_img = tf.cast(clean_img, tf.float32) / 255.0
    
    return wm_img, clean_img

# Build and train model
# See example notebook for complete training code
```

## Files Included
- `train/`, `valid/`, `test/` - Image splits
- `*_pairs.csv` - Metadata files with original/new filename mappings
- `dataset_stats.json` - Complete dataset statistics

## License
GPL-3.0
```

---

## Troubleshooting

### Issue: "Dataset too large"
**Solution**: Kaggle allows up to 20GB. Your dataset is ~98MB, so this shouldn't be an issue.

### Issue: "Upload failed"
**Solution**:
1. Check internet connection
2. Try Method 1 (web upload) instead of CLI
3. Split zip into smaller parts if needed

### Issue: "Invalid metadata"
**Solution**: Ensure `dataset-metadata.json` has correct format and your username in the `id` field.

### Issue: "Permission denied"
**Solution**: 
1. Check API token is correctly placed
2. On Linux/Mac, run: `chmod 600 ~/.kaggle/kaggle.json`

### Issue: "Dataset not found in notebook"
**Solution**:
1. Make sure you added the dataset to your notebook
2. Check the path: `/kaggle/input/watermark-removal-image-pairs/`
3. Verify dataset is published (not draft)

---

## Sharing Your Work

Once your dataset is uploaded:

1. **Share dataset link**:
   ```
   https://www.kaggle.com/datasets/YOUR_USERNAME/watermark-removal-image-pairs
   ```

2. **Share notebook link**:
   ```
   https://www.kaggle.com/code/YOUR_USERNAME/watermark-removal-using-autoencoder
   ```

3. **Make notebook public**:
   - Click "Share" in your notebook
   - Set visibility to "Public"
   - Add descriptive title and tags

4. **Get feedback**:
   - Share on Kaggle forums
   - Post on social media
   - Add to your portfolio

---

## Next Steps

After uploading:

1. ✅ Upload dataset to Kaggle
2. ✅ Create notebook using the dataset
3. ⏳ Train the model (1-2 hours)
4. ⏳ Share your results
5. ⏳ Try advanced techniques (U-Net, GAN, perceptual loss)
6. ⏳ Participate in competitions or create tutorials

---

## Support

- **Kaggle Documentation**: https://www.kaggle.com/docs
- **Kaggle API Docs**: https://github.com/Kaggle/kaggle-api
- **Dataset Guidelines**: https://www.kaggle.com/datasets-guide

---

**Created**: 2026-02-20  
**Version**: 1.0  
**Ready for Upload**: YES ✅
