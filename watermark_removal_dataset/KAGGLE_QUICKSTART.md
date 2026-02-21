# Kaggle Training Quick Start

## Step 1: Upload Dataset to Kaggle

### Option A: Via Web Interface
1. Go to https://www.kaggle.com/datasets
2. Click "New Dataset"
3. Upload the `watermark_removal_dataset` folder
4. Title: "Watermark Removal Dataset"
5. Set visibility to Public or Private
6. Click "Create"

### Option B: Via Kaggle API
```bash
# Install Kaggle CLI
pip install kaggle

# Create dataset metadata
cat > dataset-metadata.json << EOF
{
  "title": "Watermark Removal Dataset",
  "id": "yourusername/watermark-removal-dataset",
  "licenses": [{"name": "GPL-3.0"}]
}
EOF

# Upload (from watermark_removal_dataset directory)
kaggle datasets create -p .
```

---

## Step 2: Create New Kaggle Notebook

1. Go to https://www.kaggle.com/code
2. Click "New Notebook"
3. Settings:
   - **Accelerator**: GPU T4 x2 (or P100)
   - **Language**: Python
   - **Environment**: Latest

---

## Step 3: Add Dataset to Notebook

1. In notebook sidebar, click "Add Data"
2. Search for your dataset: "watermark-removal-dataset"
3. Click "Add"
4. Dataset path will be: `/kaggle/input/watermark-removal-dataset/`

---

## Step 4: Upload Training Notebook

### Option A: Copy-Paste
1. Open `kaggle_training_notebook.ipynb` locally
2. Copy all cells
3. Paste into Kaggle notebook

### Option B: Import from GitHub
1. Upload notebook to your GitHub repo
2. In Kaggle: File → Import Notebook
3. Paste GitHub raw URL

### Option C: Upload File
1. Download `kaggle_training_notebook.ipynb`
2. In Kaggle: File → Upload Notebook
3. Select file

---

## Step 5: Update Dataset Path

In the notebook, find this cell:
```python
BASE_PATH = '/kaggle/input/watermark-removal-dataset/watermark_removal_dataset'
```

**Change to match your dataset name:**
```python
# If your dataset is named "my-watermark-dataset"
BASE_PATH = '/kaggle/input/my-watermark-dataset/watermark_removal_dataset'

# Check actual path by running:
!ls /kaggle/input/
```

---

## Step 6: Run Training

### Initial Setup (5 minutes)
```python
# Run first few cells to:
# - Install dependencies
# - Load dataset
# - Verify GPU
# - Visualize samples
```

### Full Training (2-4 hours on GPU T4)
```python
# Click "Run All" or run cells sequentially
# Training will take approximately:
# - 100 epochs × 50 batches/epoch × 1-2 sec/batch
# - Total: 1.5-3 hours
```

### Monitor Progress
- Watch loss curves in training cell
- Check PSNR/SSIM metrics
- Preview predictions periodically

---

## Step 7: Save Model Outputs

After training completes:

```python
# Models are automatically saved in /kaggle/working/
!ls -lh /kaggle/working/

# You'll see:
# - best_watermark_remover.h5 (100-200 MB)
# - watermark_remover_savedmodel/ (TensorFlow format)
# - watermark_remover.tflite (Mobile format)
# - training_history.png
# - predictions.png
```

---

## Step 8: Download Trained Model

### Option A: Via Kaggle UI
1. Click on "Output" tab (right sidebar)
2. Click "Save Version" 
3. Once complete, download files from output

### Option B: Save as Dataset
1. Click "Save Version"
2. Choose "Save as Dataset"
3. Models become reusable dataset

### Option C: Commit and Download
1. Click "Save Version" → "Save & Run All"
2. Wait for notebook to complete
3. Download outputs from version page

---

## Expected Training Results

### After 20 epochs:
- Loss: ~0.15
- PSNR: ~25 dB
- SSIM: ~0.80
- Visual: Watermarks partially removed

### After 50 epochs:
- Loss: ~0.08
- PSNR: ~28 dB  
- SSIM: ~0.88
- Visual: Most watermarks removed cleanly

### After 100 epochs (best model):
- Loss: ~0.05
- PSNR: 30-35 dB
- SSIM: 0.90-0.95
- Visual: High-quality watermark removal

---

## Troubleshooting

### Error: "No GPU available"
**Solution**: 
- Go to Settings (right sidebar)
- Change Accelerator to "GPU T4 x2"
- Restart notebook

### Error: "Dataset not found"
**Solution**:
```python
# Check dataset path
!ls /kaggle/input/

# Update BASE_PATH accordingly
```

### Error: "Out of memory"
**Solution**:
```python
# Reduce batch size in CONFIG
CONFIG['BATCH_SIZE'] = 8  # Instead of 16
```

### Training too slow?
**Solution**:
```python
# Reduce image size
CONFIG['IMAGE_SIZE'] = (128, 128)  # Instead of (256, 256)

# Or reduce epochs
CONFIG['EPOCHS'] = 50  # Instead of 100
```

### Model quality poor?
**Solution**:
```python
# Train longer
CONFIG['EPOCHS'] = 150

# Adjust loss weights
total_loss = 1.0 * l1 + 0.2 * perceptual + 0.8 * ssim
```

---

## Resource Usage Estimates

### Kaggle Free Tier (30 hours GPU/week):
- **Single training run**: 2-4 hours
- **Can complete**: 7-15 training runs per week
- **Recommendation**: Start with 50 epochs, evaluate, then train full 100

### Storage:
- **Dataset**: ~500 MB
- **Model outputs**: ~200 MB
- **Total**: <1 GB (well within Kaggle limits)

---

## Next Steps After Training

1. **Evaluate Results**:
   ```python
   # Check predictions.png
   # Review PSNR/SSIM scores
   # Compare with ground truth
   ```

2. **Fine-tune Hyperparameters**:
   ```python
   # Adjust loss weights
   # Try different learning rates
   # Experiment with model architecture
   ```

3. **Deploy Model**:
   - Use TFLite for mobile apps
   - Use SavedModel for web backend
   - Integrate with your image-logo-remover frontend

4. **Share Your Work**:
   - Publish notebook on Kaggle
   - Share model on Kaggle Models
   - Add to your GitHub repo

---

## Quick Reference Commands

```python
# Check GPU
!nvidia-smi

# Check dataset
!ls -lh /kaggle/input/

# Monitor training
# (Training progress shows automatically in notebook)

# Check model size
!ls -lh /kaggle/working/*.h5

# Test single image
test_img = '/kaggle/input/watermark-removal-dataset/watermarked/photo-001.jpg'
result = remove_watermark(best_model, test_img)
plt.imshow(result)
plt.show()
```

---

## Support and Documentation

- **Notebook**: `kaggle_training_notebook.ipynb` (complete training code)
- **Theory**: `WHY_IT_WORKS.md` (architectural explanation)
- **Kaggle Docs**: https://www.kaggle.com/docs/notebooks
- **TensorFlow Docs**: https://www.tensorflow.org/tutorials

---

## Summary Checklist

- [ ] Dataset uploaded to Kaggle
- [ ] New notebook created with GPU enabled
- [ ] Dataset added to notebook
- [ ] Training notebook imported
- [ ] BASE_PATH updated correctly
- [ ] Sample images visualized successfully
- [ ] Training started (Run All)
- [ ] Monitor metrics during training
- [ ] Best model saved automatically
- [ ] Download outputs after completion
- [ ] Evaluate results visually

**Ready to train!** 🚀
