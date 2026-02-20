"""
Visualize prepared dataset samples
Shows watermarked and clean image pairs side-by-side
"""

import os
from pathlib import Path
import random

try:
    from PIL import Image, ImageDraw, ImageFont
    import matplotlib.pyplot as plt
except ImportError:
    print("ERROR: Required packages not found!")
    print("Please install: pip install pillow matplotlib")
    exit(1)


def visualize_samples(dataset_path="wm-nown", split="train", num_samples=5, save_path="dataset_samples.png"):
    """
    Visualize random samples from the dataset
    
    Args:
        dataset_path: Path to prepared dataset
        split: 'train', 'valid', or 'test'
        num_samples: Number of samples to visualize
        save_path: Path to save the visualization
    """
    dataset_path = Path(dataset_path)
    watermark_dir = dataset_path / split / "watermark"
    clean_dir = dataset_path / split / "no-watermark"
    
    # Get all image files
    watermark_files = sorted(list(watermark_dir.glob("*.jpg")))
    
    if len(watermark_files) == 0:
        print(f"ERROR: No images found in {watermark_dir}")
        return
    
    # Randomly select samples
    if len(watermark_files) < num_samples:
        num_samples = len(watermark_files)
    
    selected_files = random.sample(watermark_files, num_samples)
    
    # Create figure
    fig, axes = plt.subplots(num_samples, 2, figsize=(12, 6 * num_samples))
    
    if num_samples == 1:
        axes = [axes]  # Make it iterable
    
    for idx, watermark_path in enumerate(selected_files):
        # Load watermarked image
        watermark_img = Image.open(watermark_path)
        
        # Load corresponding clean image
        clean_path = clean_dir / watermark_path.name
        clean_img = Image.open(clean_path)
        
        # Display watermarked image
        axes[idx][0].imshow(watermark_img)
        axes[idx][0].set_title(f"Watermarked - {watermark_path.name}", fontsize=12)
        axes[idx][0].axis('off')
        
        # Display clean image
        axes[idx][1].imshow(clean_img)
        axes[idx][1].set_title(f"Clean (Target) - {watermark_path.name}", fontsize=12)
        axes[idx][1].axis('off')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"Visualization saved to: {save_path}")
    plt.show()


def print_dataset_summary(dataset_path="wm-nown"):
    """Print dataset summary statistics"""
    import json
    
    dataset_path = Path(dataset_path)
    stats_file = dataset_path / "dataset_stats.json"
    
    if not stats_file.exists():
        print("ERROR: dataset_stats.json not found!")
        return
    
    with open(stats_file, 'r') as f:
        stats = json.load(f)
    
    print("=" * 60)
    print("DATASET SUMMARY")
    print("=" * 60)
    print()
    print(f"Total Pairs: {stats['dataset_info']['total_pairs']}")
    print(f"Creation Date: {stats['dataset_info']['creation_date']}")
    print()
    print("Split Distribution:")
    print(f"  Train: {stats['dataset_info']['splits']['train']} pairs ({stats['dataset_info']['splits']['train']/stats['dataset_info']['total_pairs']*100:.1f}%)")
    print(f"  Valid: {stats['dataset_info']['splits']['valid']} pairs ({stats['dataset_info']['splits']['valid']/stats['dataset_info']['total_pairs']*100:.1f}%)")
    print(f"  Test:  {stats['dataset_info']['splits']['test']} pairs ({stats['dataset_info']['splits']['test']/stats['dataset_info']['total_pairs']*100:.1f}%)")
    print()
    print("Configuration:")
    print(f"  Image Size: {stats['configuration']['target_size']}")
    print(f"  Format: {stats['configuration']['image_format'].upper()}")
    print(f"  JPEG Quality: {stats['configuration']['jpeg_quality']}")
    print(f"  Resize Method: {stats['configuration']['resize_method']}")
    print(f"  Random Seed: {stats['configuration']['random_seed']}")
    print()
    print("Data Quality:")
    print(f"  Corrupted Files: {stats['processing_stats']['corrupted_files']}")
    print(f"  Missing Pairs: {stats['processing_stats']['missing_pairs']}")
    print(f"  Duplicates Found: {stats['processing_stats']['duplicates_found']}")
    print(f"  Processing Errors: {stats['processing_stats']['processing_errors']}")
    print()
    print("=" * 60)


def verify_dataset_integrity(dataset_path="wm-nown"):
    """Verify that all image pairs exist and have matching dimensions"""
    dataset_path = Path(dataset_path)
    
    print("Verifying dataset integrity...")
    print()
    
    issues = []
    
    for split in ["train", "valid", "test"]:
        watermark_dir = dataset_path / split / "watermark"
        clean_dir = dataset_path / split / "no-watermark"
        
        watermark_files = set(f.name for f in watermark_dir.glob("*.jpg"))
        clean_files = set(f.name for f in clean_dir.glob("*.jpg"))
        
        print(f"Checking {split} split...")
        print(f"  Watermarked images: {len(watermark_files)}")
        print(f"  Clean images: {len(clean_files)}")
        
        # Check for missing pairs
        missing_clean = watermark_files - clean_files
        missing_watermark = clean_files - watermark_files
        
        if missing_clean:
            issues.append(f"{split}: Missing clean images for: {missing_clean}")
            print(f"  WARNING: {len(missing_clean)} missing clean images")
        
        if missing_watermark:
            issues.append(f"{split}: Missing watermarked images for: {missing_watermark}")
            print(f"  WARNING: {len(missing_watermark)} missing watermarked images")
        
        # Check dimensions for a few samples
        sample_files = list(watermark_files)[:5]
        for filename in sample_files:
            try:
                wm_img = Image.open(watermark_dir / filename)
                clean_img = Image.open(clean_dir / filename)
                
                if wm_img.size != clean_img.size:
                    issues.append(f"{split}/{filename}: Size mismatch - {wm_img.size} vs {clean_img.size}")
                    print(f"  WARNING: Size mismatch in {filename}")
            except Exception as e:
                issues.append(f"{split}/{filename}: Error loading - {e}")
                print(f"  ERROR: Failed to load {filename}: {e}")
        
        print()
    
    if issues:
        print(f"Found {len(issues)} issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("Dataset integrity verified! All checks passed.")
    
    return len(issues) == 0


if __name__ == "__main__":
    print("Dataset Visualization and Verification Tool")
    print()
    print("Options:")
    print("1. Print dataset summary")
    print("2. Verify dataset integrity")
    print("3. Visualize train samples")
    print("4. Visualize valid samples")
    print("5. Visualize test samples")
    print("6. Run all checks")
    print()
    
    choice = input("Enter choice (1-6): ").strip()
    
    if choice == "1":
        print_dataset_summary()
    
    elif choice == "2":
        verify_dataset_integrity()
    
    elif choice == "3":
        num_samples = int(input("Number of samples to visualize (default 5): ") or "5")
        visualize_samples(split="train", num_samples=num_samples, save_path="train_samples.png")
    
    elif choice == "4":
        num_samples = int(input("Number of samples to visualize (default 5): ") or "5")
        visualize_samples(split="valid", num_samples=num_samples, save_path="valid_samples.png")
    
    elif choice == "5":
        num_samples = int(input("Number of samples to visualize (default 5): ") or "5")
        visualize_samples(split="test", num_samples=num_samples, save_path="test_samples.png")
    
    elif choice == "6":
        print_dataset_summary()
        print()
        verify_dataset_integrity()
        print()
        print("Generating visualizations...")
        visualize_samples(split="train", num_samples=3, save_path="train_samples.png")
        print()
    
    else:
        print("Invalid choice!")
