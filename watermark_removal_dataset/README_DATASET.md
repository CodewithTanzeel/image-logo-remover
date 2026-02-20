# Watermark Removal Dataset - Prepared for Training

This dataset has been prepared for training a convolutional autoencoder to remove watermarks from images using TensorFlow/Keras.

## Dataset Overview

- **Total pairs**: 802 (watermarked + clean pairs)
- **Image size**: 512x512 pixels
- **Format**: JPEG (quality 95)
- **Preprocessing**: Resized with padding to maintain aspect ratio

### Dataset Split

```
wm-nown/
├── train/           641 pairs (80%)
│   ├── watermark/      - Watermarked images
│   └── no-watermark/   - Clean images
├── valid/           80 pairs (10%)
│   ├── watermark/
│   └── no-watermark/
└── test/            81 pairs (10%)
    ├── watermark/
    └── no-watermark/
```

### Metadata Files

- `train_pairs.csv` - Training set image pair mappings
- `valid_pairs.csv` - Validation set image pair mappings
- `test_pairs.csv` - Test set image pair mappings
- `dataset_stats.json` - Complete dataset statistics and configuration

## Data Quality

- **Corrupted files**: 0
- **Missing pairs**: 0
- **Duplicates handled**: 8 base names with variants (resolved)
- **Processing errors**: 0

All images have been validated and successfully processed.

## Usage

### 1. Quick Start - Test Data Loader

```bash
python tensorflow_dataloader.py
# Choose option 1 to test the data loader
```

### 2. Load Dataset in Your Code

```python
from tensorflow_dataloader import WatermarkDataLoader

# Create data loader
loader = WatermarkDataLoader(
    dataset_path="wm-nown",
    batch_size=16,
    image_size=(512, 512),
    normalize=True,
    augment_train=True
)

# Get datasets
train_ds = loader.get_train_dataset()
valid_ds = loader.get_valid_dataset()
test_ds = loader.get_test_dataset()

# Use in training
model.fit(train_ds, validation_data=valid_ds, epochs=50)
```

### 3. Train a Model

```python
from tensorflow_dataloader import example_training

# Run complete training example
model, history = example_training()
```

Or run from command line:
```bash
python tensorflow_dataloader.py
# Choose option 2 to train
```

### 4. Run Inference

```python
import tensorflow as tf
import numpy as np
from PIL import Image

# Load model
model = tf.keras.models.load_model("watermark_remover_best.keras")

# Load and preprocess image
img = Image.open("your_watermarked_image.jpg").resize((512, 512))
img_array = np.array(img) / 255.0
img_array = np.expand_dims(img_array, axis=0)

# Remove watermark
clean_img = model.predict(img_array)[0]
clean_img = (clean_img * 255).astype(np.uint8)

# Save result
Image.fromarray(clean_img).save("result.jpg")
```

## Model Architecture

The included example uses a convolutional autoencoder:

**Encoder**: 3 blocks with Conv2D + MaxPooling
- Block 1: 64 filters
- Block 2: 128 filters  
- Block 3: 256 filters

**Bottleneck**: 512 filters

**Decoder**: 3 blocks with Conv2DTranspose + Conv2D
- Block 1: 256 filters
- Block 2: 128 filters
- Block 3: 64 filters

**Output**: 3 channels (RGB) with sigmoid activation

**Total parameters**: ~26M

## Data Augmentation

The following augmentations are applied to training data (synchronized for both images):
- Random horizontal flip (50% probability)
- Random vertical flip (50% probability)
- Random brightness adjustment (±10%)
- Random contrast adjustment (±10%)

## Training Tips

### 1. Batch Size
- **GPU with 8GB VRAM**: batch_size=8
- **GPU with 16GB VRAM**: batch_size=16-32
- **GPU with 24GB+ VRAM**: batch_size=32-64

### 2. Learning Rate
- Start with: `0.001`
- Use ReduceLROnPlateau callback to reduce when plateauing
- Minimum: `1e-7`

### 3. Loss Functions
Try these loss functions:
- **MSE (Mean Squared Error)**: Good baseline
- **MAE (Mean Absolute Error)**: More robust to outliers
- **Perceptual Loss**: Better visual quality (requires VGG)
- **SSIM Loss**: Structural similarity

### 4. Recommended Callbacks
```python
callbacks = [
    tf.keras.callbacks.ModelCheckpoint(
        "best_model.keras",
        save_best_only=True,
        monitor='val_loss'
    ),
    tf.keras.callbacks.EarlyStopping(
        monitor='val_loss',
        patience=10,
        restore_best_weights=True
    ),
    tf.keras.callbacks.ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=5,
        min_lr=1e-7
    ),
    tf.keras.callbacks.TensorBoard(
        log_dir='./logs'
    )
]
```

### 5. Monitor Training with TensorBoard
```bash
tensorboard --logdir=./logs
```

## Advanced: Custom Model Architecture

### U-Net Architecture
For better results, consider using U-Net with skip connections:

```python
from tensorflow.keras import layers, models

def build_unet(input_shape=(512, 512, 3)):
    inputs = layers.Input(shape=input_shape)
    
    # Encoder with skip connections
    conv1 = layers.Conv2D(64, 3, activation='relu', padding='same')(inputs)
    conv1 = layers.Conv2D(64, 3, activation='relu', padding='same')(conv1)
    pool1 = layers.MaxPooling2D(pool_size=(2, 2))(conv1)
    
    conv2 = layers.Conv2D(128, 3, activation='relu', padding='same')(pool1)
    conv2 = layers.Conv2D(128, 3, activation='relu', padding='same')(conv2)
    pool2 = layers.MaxPooling2D(pool_size=(2, 2))(conv2)
    
    # ... (add more layers)
    
    # Decoder with skip connections
    up1 = layers.Conv2DTranspose(128, 2, strides=2, padding='same')(conv_middle)
    merge1 = layers.concatenate([up1, conv2])  # Skip connection
    conv_up1 = layers.Conv2D(128, 3, activation='relu', padding='same')(merge1)
    
    # ... (continue decoder)
    
    outputs = layers.Conv2D(3, 1, activation='sigmoid')(final_conv)
    
    return models.Model(inputs, outputs)
```

### Perceptual Loss
For better visual quality:

```python
from tensorflow.keras.applications import VGG19

# Load VGG19 for perceptual loss
vgg = VGG19(include_top=False, weights='imagenet')
vgg.trainable = False

def perceptual_loss(y_true, y_pred):
    # Extract features
    true_features = vgg(y_true)
    pred_features = vgg(y_pred)
    
    # Calculate MSE on features
    return tf.reduce_mean(tf.square(true_features - pred_features))
```

## Reproducing the Dataset Preparation

If you need to re-prepare the dataset with different settings:

1. Edit configuration in `prepare_dataset.py`:
```python
CONFIG = {
    "target_size": (512, 512),  # Change image size
    "split_ratios": {
        "train": 0.80,
        "valid": 0.10,
        "test": 0.10
    },
    "image_format": "jpg",  # or "png"
    "jpeg_quality": 95,
    "resize_method": "pad",  # "pad", "stretch", or "crop"
    "random_seed": 42
}
```

2. Run preparation:
```bash
python prepare_dataset.py
```

## Expected Training Results

With the provided autoencoder model and 641 training pairs:

- **Training time**: 2-4 hours on modern GPU
- **Expected val_loss**: 0.005-0.015 (MSE)
- **Visual quality**: Good for simple watermarks
- **Convergence**: Around 30-50 epochs

For better results:
- Use U-Net architecture with skip connections
- Implement perceptual loss (VGG-based)
- Train for more epochs (100+)
- Use larger batch size if GPU memory allows

## Requirements

```bash
pip install tensorflow pillow numpy
```

For GPU support:
```bash
pip install tensorflow[and-cuda]
```

## Troubleshooting

### Out of Memory (OOM)
- Reduce batch_size
- Reduce image size in CONFIG
- Use mixed precision training: `tf.keras.mixed_precision.set_global_policy('mixed_float16')`

### Slow Training
- Enable XLA compilation: `model.compile(..., jit_compile=True)`
- Use `tf.data.AUTOTUNE` for parallel data loading (already enabled)
- Increase prefetch buffer size

### Poor Results
- Train for more epochs
- Try different loss functions (perceptual loss, SSIM)
- Use U-Net architecture with skip connections
- Increase model capacity
- Check if watermarks in your dataset are similar enough

## Dataset Statistics

See `wm-nown/dataset_stats.json` for complete statistics including:
- Image counts per split
- Processing configuration
- Quality metrics
- Any issues encountered

## License

This dataset preparation follows the same license as the parent project: GNU General Public License v3.0

## Citation

If you use this dataset preparation pipeline, please cite:

```
Image Watermark Remover Dataset Preparation
https://github.com/CodewithTanzeel/image-logo-remover
```

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review TensorFlow documentation
3. Open an issue on the project repository

---

**Last updated**: 2026-02-20  
**Dataset version**: 1.0  
**Prepared by**: Dataset preparation script v1.0
