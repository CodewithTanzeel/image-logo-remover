"""
TensorFlow/Keras Data Loader for Watermark Removal Dataset
Loads paired watermarked/clean images for training convolutional autoencoder
"""

import tensorflow as tf
from pathlib import Path
from typing import Tuple, Optional
import json


class WatermarkDataLoader:
    """Data loader for paired watermark removal dataset"""
    
    def __init__(
        self,
        dataset_path: str = "wm-nown",
        batch_size: int = 16,
        image_size: Tuple[int, int] = (512, 512),
        normalize: bool = True,
        augment_train: bool = True,
        random_seed: int = 42
    ):
        """
        Initialize data loader
        
        Args:
            dataset_path: Path to prepared dataset
            batch_size: Batch size for training
            image_size: Target image size (height, width)
            normalize: Normalize images to [0, 1] range
            augment_train: Apply data augmentation to training set
            random_seed: Random seed for reproducibility
        """
        self.dataset_path = Path(dataset_path)
        self.batch_size = batch_size
        self.image_size = image_size
        self.normalize = normalize
        self.augment_train = augment_train
        self.random_seed = random_seed
        
        # Load dataset statistics
        stats_path = self.dataset_path / "dataset_stats.json"
        with open(stats_path, "r") as f:
            self.stats = json.load(f)
        
        print(f"Dataset loaded: {self.stats['dataset_info']['total_pairs']} total pairs")
        print(f"  Train: {self.stats['dataset_info']['splits']['train']} pairs")
        print(f"  Valid: {self.stats['dataset_info']['splits']['valid']} pairs")
        print(f"  Test: {self.stats['dataset_info']['splits']['test']} pairs")
    
    def _load_image_pair(self, watermark_path: str, clean_path: str) -> Tuple[tf.Tensor, tf.Tensor]:
        """Load and preprocess a pair of images"""
        # Load images
        watermark_img = tf.io.read_file(watermark_path)
        watermark_img = tf.image.decode_jpeg(watermark_img, channels=3)
        
        clean_img = tf.io.read_file(clean_path)
        clean_img = tf.image.decode_jpeg(clean_img, channels=3)
        
        # Convert to float32
        watermark_img = tf.cast(watermark_img, tf.float32)
        clean_img = tf.cast(clean_img, tf.float32)
        
        # Normalize to [0, 1] if requested
        if self.normalize:
            watermark_img = watermark_img / 255.0
            clean_img = clean_img / 255.0
        
        return watermark_img, clean_img
    
    def _augment(self, watermark_img: tf.Tensor, clean_img: tf.Tensor) -> Tuple[tf.Tensor, tf.Tensor]:
        """
        Apply data augmentation to both images
        IMPORTANT: Same augmentation must be applied to both images
        """
        # Random horizontal flip
        if tf.random.uniform(()) > 0.5:
            watermark_img = tf.image.flip_left_right(watermark_img)
            clean_img = tf.image.flip_left_right(clean_img)
        
        # Random vertical flip
        if tf.random.uniform(()) > 0.5:
            watermark_img = tf.image.flip_up_down(watermark_img)
            clean_img = tf.image.flip_up_down(clean_img)
        
        # Random brightness adjustment (applied to both)
        brightness_delta = tf.random.uniform((), -0.1, 0.1)
        watermark_img = tf.image.adjust_brightness(watermark_img, brightness_delta)
        clean_img = tf.image.adjust_brightness(clean_img, brightness_delta)
        
        # Random contrast adjustment (applied to both)
        contrast_factor = tf.random.uniform((), 0.9, 1.1)
        watermark_img = tf.image.adjust_contrast(watermark_img, contrast_factor)
        clean_img = tf.image.adjust_contrast(clean_img, contrast_factor)
        
        # Clip to valid range
        if self.normalize:
            watermark_img = tf.clip_by_value(watermark_img, 0.0, 1.0)
            clean_img = tf.clip_by_value(clean_img, 0.0, 1.0)
        else:
            watermark_img = tf.clip_by_value(watermark_img, 0.0, 255.0)
            clean_img = tf.clip_by_value(clean_img, 0.0, 255.0)
        
        return watermark_img, clean_img
    
    def _create_dataset(self, split: str, shuffle: bool = True, augment: bool = False) -> tf.data.Dataset:
        """
        Create TensorFlow dataset for specified split
        
        Args:
            split: 'train', 'valid', or 'test'
            shuffle: Whether to shuffle the dataset
            augment: Whether to apply data augmentation
            
        Returns:
            TensorFlow dataset yielding (watermark_img, clean_img) pairs
        """
        watermark_dir = self.dataset_path / split / "watermark"
        clean_dir = self.dataset_path / split / "no-watermark"
        
        # Get all image paths
        watermark_paths = sorted([str(p) for p in watermark_dir.glob("*.jpg")])
        clean_paths = sorted([str(p) for p in clean_dir.glob("*.jpg")])
        
        assert len(watermark_paths) == len(clean_paths), \
            f"Mismatch in number of images: {len(watermark_paths)} vs {len(clean_paths)}"
        
        # Create dataset from file paths
        dataset = tf.data.Dataset.from_tensor_slices((watermark_paths, clean_paths))
        
        # Shuffle if requested
        if shuffle:
            dataset = dataset.shuffle(
                buffer_size=len(watermark_paths),
                seed=self.random_seed,
                reshuffle_each_iteration=True
            )
        
        # Load images
        dataset = dataset.map(
            self._load_image_pair,
            num_parallel_calls=tf.data.AUTOTUNE
        )
        
        # Apply augmentation if requested
        if augment:
            dataset = dataset.map(
                self._augment,
                num_parallel_calls=tf.data.AUTOTUNE
            )
        
        # Batch and prefetch
        dataset = dataset.batch(self.batch_size)
        dataset = dataset.prefetch(tf.data.AUTOTUNE)
        
        return dataset
    
    def get_train_dataset(self) -> tf.data.Dataset:
        """Get training dataset with augmentation and shuffling"""
        return self._create_dataset("train", shuffle=True, augment=self.augment_train)
    
    def get_valid_dataset(self) -> tf.data.Dataset:
        """Get validation dataset without augmentation"""
        return self._create_dataset("valid", shuffle=False, augment=False)
    
    def get_test_dataset(self) -> tf.data.Dataset:
        """Get test dataset without augmentation"""
        return self._create_dataset("test", shuffle=False, augment=False)
    
    def get_dataset_info(self) -> dict:
        """Get dataset statistics and information"""
        return self.stats


def build_autoencoder_model(input_shape: Tuple[int, int, int] = (512, 512, 3)) -> tf.keras.Model:
    """
    Build a simple convolutional autoencoder for watermark removal
    
    Args:
        input_shape: Shape of input images (height, width, channels)
        
    Returns:
        Compiled Keras model
    """
    from tensorflow.keras import layers, models
    
    # Encoder
    inputs = layers.Input(shape=input_shape, name="watermarked_input")
    
    # Encoder block 1
    x = layers.Conv2D(64, (3, 3), activation='relu', padding='same')(inputs)
    x = layers.Conv2D(64, (3, 3), activation='relu', padding='same')(x)
    x = layers.MaxPooling2D((2, 2), padding='same')(x)
    
    # Encoder block 2
    x = layers.Conv2D(128, (3, 3), activation='relu', padding='same')(x)
    x = layers.Conv2D(128, (3, 3), activation='relu', padding='same')(x)
    x = layers.MaxPooling2D((2, 2), padding='same')(x)
    
    # Encoder block 3
    x = layers.Conv2D(256, (3, 3), activation='relu', padding='same')(x)
    x = layers.Conv2D(256, (3, 3), activation='relu', padding='same')(x)
    x = layers.MaxPooling2D((2, 2), padding='same')(x)
    
    # Bottleneck
    x = layers.Conv2D(512, (3, 3), activation='relu', padding='same')(x)
    x = layers.Conv2D(512, (3, 3), activation='relu', padding='same')(x)
    
    # Decoder block 1
    x = layers.Conv2DTranspose(256, (2, 2), strides=(2, 2), padding='same')(x)
    x = layers.Conv2D(256, (3, 3), activation='relu', padding='same')(x)
    x = layers.Conv2D(256, (3, 3), activation='relu', padding='same')(x)
    
    # Decoder block 2
    x = layers.Conv2DTranspose(128, (2, 2), strides=(2, 2), padding='same')(x)
    x = layers.Conv2D(128, (3, 3), activation='relu', padding='same')(x)
    x = layers.Conv2D(128, (3, 3), activation='relu', padding='same')(x)
    
    # Decoder block 3
    x = layers.Conv2DTranspose(64, (2, 2), strides=(2, 2), padding='same')(x)
    x = layers.Conv2D(64, (3, 3), activation='relu', padding='same')(x)
    x = layers.Conv2D(64, (3, 3), activation='relu', padding='same')(x)
    
    # Output layer
    outputs = layers.Conv2D(3, (3, 3), activation='sigmoid', padding='same', name="clean_output")(x)
    
    # Create model
    model = models.Model(inputs=inputs, outputs=outputs, name="watermark_remover")
    
    # Compile model
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss='mean_squared_error',
        metrics=['mae', tf.keras.metrics.MeanSquaredError()]
    )
    
    return model


def example_training():
    """Example training script"""
    print("=" * 60)
    print("Watermark Removal Model Training Example")
    print("=" * 60)
    print()
    
    # Create data loader
    data_loader = WatermarkDataLoader(
        dataset_path="wm-nown",
        batch_size=8,  # Adjust based on GPU memory
        image_size=(512, 512),
        normalize=True,
        augment_train=True
    )
    
    # Get datasets
    train_ds = data_loader.get_train_dataset()
    valid_ds = data_loader.get_valid_dataset()
    
    # Build model
    print("\nBuilding model...")
    model = build_autoencoder_model(input_shape=(512, 512, 3))
    model.summary()
    
    # Define callbacks
    callbacks = [
        tf.keras.callbacks.ModelCheckpoint(
            "watermark_remover_best.keras",
            save_best_only=True,
            monitor='val_loss',
            verbose=1
        ),
        tf.keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True,
            verbose=1
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            verbose=1,
            min_lr=1e-7
        ),
        tf.keras.callbacks.TensorBoard(
            log_dir='./logs',
            histogram_freq=1
        )
    ]
    
    # Train model
    print("\nStarting training...")
    history = model.fit(
        train_ds,
        validation_data=valid_ds,
        epochs=50,
        callbacks=callbacks,
        verbose=1
    )
    
    # Save final model
    model.save("watermark_remover_final.keras")
    print("\nTraining complete! Model saved.")
    
    return model, history


def example_inference():
    """Example inference script"""
    import numpy as np
    from PIL import Image
    
    print("Loading model...")
    model = tf.keras.models.load_model("watermark_remover_best.keras")
    
    print("Loading test image...")
    # Load a watermarked test image
    img = Image.open("wm-nown/test/watermark/image_0001.jpg")
    img_array = np.array(img) / 255.0  # Normalize
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    
    print("Running inference...")
    prediction = model.predict(img_array)[0]
    
    # Convert back to image
    prediction = (prediction * 255).astype(np.uint8)
    result_img = Image.fromarray(prediction)
    
    # Save result
    result_img.save("output_no_watermark.jpg", quality=95)
    print("Result saved to: output_no_watermark.jpg")


if __name__ == "__main__":
    # Example usage
    print("TensorFlow/Keras Watermark Removal Data Loader")
    print()
    print("Options:")
    print("1. Test data loader")
    print("2. Train model (example)")
    print("3. Run inference (example)")
    print()
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        # Test data loader
        loader = WatermarkDataLoader(
            dataset_path="wm-nown",
            batch_size=4,
            augment_train=True
        )
        
        train_ds = loader.get_train_dataset()
        
        print("\nTesting data loader...")
        for watermark_batch, clean_batch in train_ds.take(1):
            print(f"Watermark batch shape: {watermark_batch.shape}")
            print(f"Clean batch shape: {clean_batch.shape}")
            print(f"Value range: [{tf.reduce_min(watermark_batch):.3f}, {tf.reduce_max(watermark_batch):.3f}]")
            print("\nData loader working correctly!")
    
    elif choice == "2":
        example_training()
    
    elif choice == "3":
        example_inference()
    
    else:
        print("Invalid choice!")
