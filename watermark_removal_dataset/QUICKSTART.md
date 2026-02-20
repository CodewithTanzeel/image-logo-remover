# Quick Start Guide - Watermark Removal Training

## Dataset Ready!

Your dataset has been successfully prepared and is ready for training.

### What You Have Now

```
wm-nown/
├── train/              641 pairs (80%)
│   ├── watermark/      641 watermarked images (512x512 JPG)
│   └── no-watermark/   641 clean target images (512x512 JPG)
├── valid/              80 pairs (10%)
│   ├── watermark/      80 watermarked images
│   └── no-watermark/   80 clean target images
├── test/               81 pairs (10%)
│   ├── watermark/      81 watermarked images
│   └── no-watermark/   81 clean target images
├── train_pairs.csv     Metadata for training set
├── valid_pairs.csv     Metadata for validation set
├── test_pairs.csv      Metadata for test set
└── dataset_stats.json  Complete statistics
```

## Start Training in 3 Steps

### Step 1: Install Requirements

```bash
pip install tensorflow pillow numpy matplotlib
```

For GPU support (recommended):
```bash
pip install tensorflow[and-cuda]
```

### Step 2: Test the Data Loader

```bash
python tensorflow_dataloader.py
# Choose option 1 to test
```

Expected output:
```
Watermark batch shape: (4, 512, 512, 3)
Clean batch shape: (4, 512, 512, 3)
Value range: [0.000, 1.000]
Data loader working correctly!
```

### Step 3: Start Training

Option A - Use the example training script:
```bash
python tensorflow_dataloader.py
# Choose option 2 to train
```

Option B - Write your own training code:
```python
from tensorflow_dataloader import WatermarkDataLoader, build_autoencoder_model

# Load data
loader = WatermarkDataLoader(
    dataset_path="wm-nown",
    batch_size=8,  # Adjust based on GPU memory
    augment_train=True
)

train_ds = loader.get_train_dataset()
valid_ds = loader.get_valid_dataset()

# Build model
model = build_autoencoder_model(input_shape=(512, 512, 3))

# Train
model.fit(
    train_ds,
    validation_data=valid_ds,
    epochs=50,
    callbacks=[
        tf.keras.callbacks.ModelCheckpoint("best_model.keras", save_best_only=True),
        tf.keras.callbacks.EarlyStopping(patience=10, restore_best_weights=True)
    ]
)
```

## Verify Your Dataset

Run verification before training:
```bash
echo "2" | python visualize_dataset.py
```

Expected output:
```
Checking train split...
  Watermarked images: 641
  Clean images: 641
Checking valid split...
  Watermarked images: 80
  Clean images: 80
Checking test split...
  Watermarked images: 81
  Clean images: 81

Dataset integrity verified! All checks passed.
```

## Training Tips

### GPU Memory Issues?
- Reduce batch_size to 4 or 2
- Use mixed precision: `tf.keras.mixed_precision.set_global_policy('mixed_float16')`

### Want Better Results?
- Train for 100+ epochs (use EarlyStopping)
- Try U-Net architecture with skip connections (see README_DATASET.md)
- Implement perceptual loss (VGG-based)
- Increase model capacity

### Monitor Training
```bash
tensorboard --logdir=./logs
# Open http://localhost:6006 in browser
```

## Expected Training Time

- **On CPU**: 8-12 hours (not recommended)
- **On GPU (GTX 1660 or similar)**: 2-3 hours
- **On GPU (RTX 3060 or better)**: 1-2 hours
- **On GPU (RTX 4090 or A100)**: 30-45 minutes

## File Structure Overview

```
📁 watermark_removal_dataset/
├── 📄 prepare_dataset.py          # Dataset preparation script (already run)
├── 📄 tensorflow_dataloader.py    # TensorFlow data loader + training code
├── 📄 visualize_dataset.py        # Dataset visualization and verification
├── 📄 README_DATASET.md           # Complete documentation
├── 📄 QUICKSTART.md              # This file
├── 📁 wm-nown/                   # Prepared dataset ✅
├── 📁 watermarked/               # Original watermarked images (backup)
└── 📁 nonwatermarked/            # Original clean images (backup)
```

## Common Commands

```bash
# View dataset summary
echo "1" | python visualize_dataset.py

# Verify dataset integrity
echo "2" | python visualize_dataset.py

# Test data loader
python -c "from tensorflow_dataloader import WatermarkDataLoader; loader = WatermarkDataLoader(); train_ds = loader.get_train_dataset(); print('OK')"

# Quick train (50 epochs)
python tensorflow_dataloader.py  # Choose option 2

# Run inference on test image
python tensorflow_dataloader.py  # Choose option 3 (after training)
```

## Dataset Statistics

- **Total image pairs**: 802
- **Training pairs**: 641 (79.9%)
- **Validation pairs**: 80 (10.0%)
- **Test pairs**: 81 (10.1%)
- **Image size**: 512x512 pixels
- **Format**: JPEG (quality 95)
- **Corrupted files**: 0
- **Missing pairs**: 0
- **Processing errors**: 0

## Next Steps

1. ✅ Dataset is prepared
2. ⏳ Install TensorFlow and dependencies
3. ⏳ Test the data loader
4. ⏳ Start training
5. ⏳ Evaluate on test set
6. ⏳ Deploy your model

## Need Help?

- **Full documentation**: See `README_DATASET.md`
- **Model architecture details**: See `tensorflow_dataloader.py` lines 175-239
- **Data augmentation**: See `tensorflow_dataloader.py` lines 72-106
- **Advanced techniques**: See `README_DATASET.md` sections on U-Net and Perceptual Loss

## Troubleshooting

### "Import error: No module named tensorflow"
```bash
pip install tensorflow
```

### "Out of memory" during training
```python
# Reduce batch size
loader = WatermarkDataLoader(batch_size=4)  # or even 2
```

### "Model not learning" (loss not decreasing)
- Check that images are normalized (0-1 range)
- Try different learning rate (0.0001 or 0.01)
- Ensure data loader is working correctly
- Verify image pairs are correctly matched

### Training is too slow
- Use GPU instead of CPU
- Enable XLA: `model.compile(..., jit_compile=True)`
- Reduce image size to 256x256 (edit CONFIG in prepare_dataset.py and re-run)

---

**Created**: 2026-02-20  
**Dataset Version**: 1.0  
**Ready for Training**: YES ✅
