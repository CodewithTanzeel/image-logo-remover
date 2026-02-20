"""
Dataset Preparation Script for Watermark Removal Model
Prepares paired watermarked/non-watermarked images for training
Target: TensorFlow/Keras Convolutional Autoencoder
"""

import os
import json
import csv
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Set
import random
from collections import defaultdict
from datetime import datetime

try:
    from PIL import Image
    import numpy as np
except ImportError:
    print("ERROR: Required packages not found!")
    print("Please install: pip install pillow numpy")
    exit(1)


# Configuration
CONFIG = {
    "source_dirs": {
        "watermarked": "watermarked",
        "nonwatermarked": "nonwatermarked"
    },
    "output_dir": "wm-nown",
    "target_size": (512, 512),
    "split_ratios": {
        "train": 0.80,
        "valid": 0.10,
        "test": 0.10
    },
    "image_format": "jpg",  # 'jpg' or 'png'
    "jpeg_quality": 95,
    "random_seed": 42,
    "resize_method": "pad",  # 'pad', 'stretch', or 'crop'
    "padding_color": (0, 0, 0)  # Black padding
}


class DatasetPreparer:
    """Main class for dataset preparation"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.random_seed = config["random_seed"]
        random.seed(self.random_seed)
        np.random.seed(self.random_seed)
        
        self.source_wm = Path(config["source_dirs"]["watermarked"])
        self.source_clean = Path(config["source_dirs"]["nonwatermarked"])
        self.output_dir = Path(config["output_dir"])
        
        self.stats = {
            "total_files": 0,
            "valid_pairs": 0,
            "corrupted_files": [],
            "missing_pairs": [],
            "duplicates": [],
            "processing_errors": []
        }
        
    def log(self, message: str, level: str = "INFO"):
        """Print log message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def validate_images(self) -> Tuple[Set[str], Set[str], List[str]]:
        """
        Validate all images in source directories
        Returns: (valid_wm_files, valid_clean_files, corrupted_files)
        """
        self.log("Step 1: Validating images...")
        
        valid_wm = set()
        valid_clean = set()
        corrupted = []
        
        # Validate watermarked images
        self.log(f"Checking watermarked images in: {self.source_wm}")
        for img_path in self.source_wm.glob("*.jpg"):
            try:
                with Image.open(img_path) as img:
                    img.verify()
                # Re-open to actually load data
                with Image.open(img_path) as img:
                    img.load()
                valid_wm.add(img_path.name)
            except Exception as e:
                self.log(f"Corrupted watermarked: {img_path.name} - {e}", "ERROR")
                corrupted.append(f"watermarked/{img_path.name}")
        
        # Validate non-watermarked images
        self.log(f"Checking non-watermarked images in: {self.source_clean}")
        for img_path in self.source_clean.glob("*.jpg"):
            try:
                with Image.open(img_path) as img:
                    img.verify()
                with Image.open(img_path) as img:
                    img.load()
                valid_clean.add(img_path.name)
            except Exception as e:
                self.log(f"Corrupted non-watermarked: {img_path.name} - {e}", "ERROR")
                corrupted.append(f"nonwatermarked/{img_path.name}")
        
        self.log(f"Valid watermarked images: {len(valid_wm)}")
        self.log(f"Valid non-watermarked images: {len(valid_clean)}")
        self.log(f"Corrupted images: {len(corrupted)}")
        
        self.stats["corrupted_files"] = corrupted
        
        return valid_wm, valid_clean, corrupted
    
    def find_duplicates(self, filenames: Set[str]) -> Dict[str, List[str]]:
        """
        Find duplicate filenames (e.g., 'photo.jpg' and 'photo (1).jpg')
        Returns: Dict mapping base filename to list of variants
        """
        self.log("Step 2: Detecting duplicate filenames...")
        
        duplicates = defaultdict(list)
        
        for filename in filenames:
            # Remove ' (n)' pattern before extension
            base_name = filename
            if " (" in filename and ")" in filename:
                parts = filename.rsplit(" (", 1)
                if len(parts) == 2:
                    prefix = parts[0]
                    suffix = parts[1]
                    if ")" in suffix:
                        number_part = suffix.split(")")[0]
                        if number_part.isdigit():
                            extension = suffix.split(")", 1)[1]
                            base_name = f"{prefix}{extension}"
            
            duplicates[base_name].append(filename)
        
        # Keep only actual duplicates (more than one variant)
        actual_duplicates = {k: v for k, v in duplicates.items() if len(v) > 1}
        
        self.log(f"Found {len(actual_duplicates)} base names with duplicates")
        for base, variants in list(actual_duplicates.items())[:5]:
            self.log(f"  {base}: {variants}", "DEBUG")
        
        self.stats["duplicates"] = list(actual_duplicates.keys())
        
        return actual_duplicates
    
    def resolve_duplicates(self, valid_wm: Set[str], valid_clean: Set[str]) -> Set[str]:
        """
        Resolve duplicates by keeping only files that have matching pairs
        Returns: Set of filenames to use (with duplicates resolved)
        """
        self.log("Step 3: Resolving duplicates...")
        
        # Find duplicates in both sets
        wm_duplicates = self.find_duplicates(valid_wm)
        clean_duplicates = self.find_duplicates(valid_clean)
        
        # Strategy: Keep only files that exist in BOTH watermarked and non-watermarked
        # For duplicates, prefer the one without (n) suffix
        resolved = set()
        
        for wm_file in valid_wm:
            # Check if there's a matching clean file
            if wm_file in valid_clean:
                resolved.add(wm_file)
            else:
                # Try to find base name match
                base_name = wm_file.split(" (")[0] + wm_file.split(")")[-1] if " (" in wm_file else wm_file
                
                # Look for any variant in clean files
                found_match = False
                for clean_file in valid_clean:
                    clean_base = clean_file.split(" (")[0] + clean_file.split(")")[-1] if " (" in clean_file else clean_file
                    if base_name == clean_base or wm_file == clean_file:
                        resolved.add(wm_file)
                        found_match = True
                        break
                
                if not found_match:
                    self.stats["missing_pairs"].append(f"watermarked/{wm_file}")
        
        self.log(f"Resolved to {len(resolved)} valid pairs")
        self.log(f"Missing pairs: {len(self.stats['missing_pairs'])}")
        
        return resolved
    
    def create_folder_structure(self):
        """Create output directory structure"""
        self.log("Step 4: Creating folder structure...")
        
        folders = [
            self.output_dir / "train" / "watermark",
            self.output_dir / "train" / "no-watermark",
            self.output_dir / "valid" / "watermark",
            self.output_dir / "valid" / "no-watermark",
            self.output_dir / "test" / "watermark",
            self.output_dir / "test" / "no-watermark",
        ]
        
        for folder in folders:
            folder.mkdir(parents=True, exist_ok=True)
            self.log(f"Created: {folder}")
    
    def resize_image(self, img: Image.Image) -> Image.Image:
        """
        Resize image to target size with padding to maintain aspect ratio
        """
        target_w, target_h = self.config["target_size"]
        method = self.config["resize_method"]
        
        if method == "stretch":
            return img.resize((target_w, target_h), Image.LANCZOS)
        
        elif method == "crop":
            # Center crop
            img.thumbnail((target_w, target_h), Image.LANCZOS)
            
            # Calculate crop box
            left = (img.width - target_w) // 2
            top = (img.height - target_h) // 2
            right = left + target_w
            bottom = top + target_h
            
            return img.crop((left, top, right, bottom))
        
        elif method == "pad":
            # Resize maintaining aspect ratio, then pad
            img.thumbnail((target_w, target_h), Image.LANCZOS)
            
            # Create new image with padding
            new_img = Image.new("RGB", (target_w, target_h), self.config["padding_color"])
            
            # Paste resized image in center
            paste_x = (target_w - img.width) // 2
            paste_y = (target_h - img.height) // 2
            new_img.paste(img, (paste_x, paste_y))
            
            return new_img
    
    def process_and_copy_image(self, src_path: Path, dst_path: Path):
        """Process and copy single image"""
        try:
            with Image.open(src_path) as img:
                # Convert to RGB if needed
                if img.mode != "RGB":
                    img = img.convert("RGB")
                
                # Resize
                img_resized = self.resize_image(img)
                
                # Save
                if self.config["image_format"] == "png":
                    img_resized.save(dst_path, "PNG")
                else:
                    img_resized.save(dst_path, "JPEG", quality=self.config["jpeg_quality"])
        
        except Exception as e:
            self.log(f"Error processing {src_path.name}: {e}", "ERROR")
            self.stats["processing_errors"].append(str(src_path))
            raise
    
    def split_and_process_dataset(self, valid_pairs: Set[str]):
        """Split dataset and process images"""
        self.log("Step 5: Splitting and processing dataset...")
        
        # Convert to list and shuffle
        pairs_list = list(valid_pairs)
        random.shuffle(pairs_list)
        
        total = len(pairs_list)
        train_count = int(total * self.config["split_ratios"]["train"])
        valid_count = int(total * self.config["split_ratios"]["valid"])
        
        # Split
        train_files = pairs_list[:train_count]
        valid_files = pairs_list[train_count:train_count + valid_count]
        test_files = pairs_list[train_count + valid_count:]
        
        self.log(f"Split: Train={len(train_files)}, Valid={len(valid_files)}, Test={len(test_files)}")
        
        # Process each split
        splits = {
            "train": train_files,
            "valid": valid_files,
            "test": test_files
        }
        
        metadata = {}
        
        for split_name, files in splits.items():
            self.log(f"Processing {split_name} split ({len(files)} pairs)...")
            
            pairs_data = []
            
            for idx, filename in enumerate(files, 1):
                # Generate clean sequential filename
                new_name = f"image_{idx:04d}.{self.config['image_format']}"
                
                # Process watermarked image
                src_wm = self.source_wm / filename
                dst_wm = self.output_dir / split_name / "watermark" / new_name
                self.process_and_copy_image(src_wm, dst_wm)
                
                # Process non-watermarked image
                src_clean = self.source_clean / filename
                dst_clean = self.output_dir / split_name / "no-watermark" / new_name
                self.process_and_copy_image(src_clean, dst_clean)
                
                pairs_data.append({
                    "original_filename": filename,
                    "new_filename": new_name,
                    "watermark_path": f"{split_name}/watermark/{new_name}",
                    "clean_path": f"{split_name}/no-watermark/{new_name}"
                })
                
                if idx % 50 == 0:
                    self.log(f"  Processed {idx}/{len(files)} pairs...")
            
            metadata[split_name] = pairs_data
            self.log(f"Completed {split_name} split!")
        
        return metadata
    
    def save_metadata(self, metadata: Dict):
        """Save metadata CSV files"""
        self.log("Step 6: Saving metadata files...")
        
        for split_name, pairs_data in metadata.items():
            csv_path = self.output_dir / f"{split_name}_pairs.csv"
            
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=pairs_data[0].keys())
                writer.writeheader()
                writer.writerows(pairs_data)
            
            self.log(f"Saved: {csv_path}")
    
    def calculate_statistics(self, metadata: Dict):
        """Calculate and save dataset statistics"""
        self.log("Step 7: Calculating dataset statistics...")
        
        stats = {
            "dataset_info": {
                "creation_date": datetime.now().isoformat(),
                "total_pairs": sum(len(pairs) for pairs in metadata.values()),
                "splits": {
                    split: len(pairs) for split, pairs in metadata.items()
                }
            },
            "configuration": self.config,
            "processing_stats": {
                "corrupted_files": len(self.stats["corrupted_files"]),
                "missing_pairs": len(self.stats["missing_pairs"]),
                "duplicates_found": len(self.stats["duplicates"]),
                "processing_errors": len(self.stats["processing_errors"])
            },
            "issues": {
                "corrupted_files": self.stats["corrupted_files"],
                "missing_pairs": self.stats["missing_pairs"][:10],  # Limit to first 10
                "processing_errors": self.stats["processing_errors"]
            }
        }
        
        # Save statistics
        stats_path = self.output_dir / "dataset_stats.json"
        with open(stats_path, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2)
        
        self.log(f"Saved: {stats_path}")
        
        return stats
    
    def generate_report(self, stats: Dict):
        """Generate and print final report"""
        self.log("=" * 60)
        self.log("DATASET PREPARATION COMPLETE!")
        self.log("=" * 60)
        
        print(f"\n📊 Dataset Statistics:")
        print(f"  Total pairs processed: {stats['dataset_info']['total_pairs']}")
        print(f"  - Train: {stats['dataset_info']['splits']['train']} pairs")
        print(f"  - Valid: {stats['dataset_info']['splits']['valid']} pairs")
        print(f"  - Test: {stats['dataset_info']['splits']['test']} pairs")
        
        print(f"\n⚙️  Configuration:")
        print(f"  Image size: {self.config['target_size']}")
        print(f"  Format: {self.config['image_format'].upper()}")
        print(f"  Resize method: {self.config['resize_method']}")
        
        print(f"\n⚠️  Issues:")
        print(f"  Corrupted files: {stats['processing_stats']['corrupted_files']}")
        print(f"  Missing pairs: {stats['processing_stats']['missing_pairs']}")
        print(f"  Processing errors: {stats['processing_stats']['processing_errors']}")
        
        print(f"\n📁 Output directory: {self.output_dir.absolute()}")
        print(f"\n✅ Dataset ready for training!")
        
    def run(self):
        """Run full preparation pipeline"""
        self.log("Starting dataset preparation pipeline...")
        self.log(f"Random seed: {self.random_seed}")
        
        try:
            # Step 1: Validate images
            valid_wm, valid_clean, corrupted = self.validate_images()
            
            # Step 2-3: Handle duplicates and find valid pairs
            valid_pairs = self.resolve_duplicates(valid_wm, valid_clean)
            
            if len(valid_pairs) == 0:
                self.log("ERROR: No valid pairs found!", "ERROR")
                return False
            
            self.stats["valid_pairs"] = len(valid_pairs)
            
            # Step 4: Create folder structure
            self.create_folder_structure()
            
            # Step 5: Split and process
            metadata = self.split_and_process_dataset(valid_pairs)
            
            # Step 6: Save metadata
            self.save_metadata(metadata)
            
            # Step 7: Calculate statistics
            stats = self.calculate_statistics(metadata)
            
            # Step 8: Generate report
            self.generate_report(stats)
            
            return True
            
        except Exception as e:
            self.log(f"FATAL ERROR: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main entry point"""
    print("=" * 60)
    print("Watermark Removal Dataset Preparation")
    print("=" * 60)
    print()
    
    preparer = DatasetPreparer(CONFIG)
    success = preparer.run()
    
    if not success:
        print("\n❌ Dataset preparation failed!")
        exit(1)
    
    print("\n🎉 All done! You can now use this dataset for training.")


if __name__ == "__main__":
    main()
