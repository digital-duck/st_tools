#!/usr/bin/env python3
"""
AI Image Viewer - Work Splitter Tool

This tool splits a source image folder into multiple work packages for collaborative analysis.
Each package contains:
- All 3 AI Image Viewer HTML files (MobileNet, EfficientNet, MediaPipe)
- A subset of images for analysis
- Ready-to-share bundle for team collaboration

Author: AI Image Viewer Team
"""

import os
import shutil
import math
import click
from pathlib import Path
from typing import List, Tuple
import json
from datetime import datetime


class WorkSplitter:
    """Handles splitting image datasets into collaborative work packages."""
    
    SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
    HTML_FILES = [
        'ai_image_viewer.html',
        'ai_image_viewer_efficientnet.html', 
        'ai_image_viewer_mediapipe.html'
    ]
    
    def __init__(self, source_folder: Path, output_folder: Path, num_splits: int):
        self.source_folder = Path(source_folder)
        self.output_folder = Path(output_folder)
        self.num_splits = num_splits
        self.project_root = self.find_project_root()
        
    def find_project_root(self) -> Path:
        """Find the project root containing HTML files."""
        current = Path(__file__).parent
        while current.parent != current:
            if all((current / html).exists() for html in self.HTML_FILES):
                return current
            current = current.parent
        raise FileNotFoundError("Could not find project root with HTML files")
    
    def get_image_files(self) -> List[Path]:
        """Get all supported image files from source folder."""
        image_files = []
        for ext in self.SUPPORTED_EXTENSIONS:
            image_files.extend(self.source_folder.glob(f"*{ext}"))
            image_files.extend(self.source_folder.glob(f"*{ext.upper()}"))
        return sorted(image_files)
    
    def split_images(self, image_files: List[Path]) -> List[List[Path]]:
        """Split image files into roughly equal chunks."""
        if not image_files:
            raise ValueError("No image files found in source folder")
            
        chunk_size = math.ceil(len(image_files) / self.num_splits)
        chunks = []
        
        for i in range(self.num_splits):
            start_idx = i * chunk_size
            end_idx = min((i + 1) * chunk_size, len(image_files))
            chunk = image_files[start_idx:end_idx]
            if chunk:  # Only add non-empty chunks
                chunks.append(chunk)
                
        return chunks
    
    def create_work_package(self, chunk_id: int, image_chunk: List[Path]) -> Path:
        """Create a complete work package with HTML files and images."""
        package_name = f"work-package-{chunk_id:03d}"
        package_path = self.output_folder / package_name
        
        # Create package directory
        package_path.mkdir(parents=True, exist_ok=True)
        
        # Copy HTML files
        for html_file in self.HTML_FILES:
            src_path = self.project_root / html_file
            dst_path = package_path / html_file
            shutil.copy2(src_path, dst_path)
            click.echo(f"  ✓ Copied {html_file}")
        
        # Copy docs folder if it exists
        docs_src = self.project_root / "docs"
        if docs_src.exists():
            docs_dst = package_path / "docs"
            shutil.copytree(docs_src, docs_dst, dirs_exist_ok=True)
            click.echo(f"  ✓ Copied docs folder")
        
        # Create images subfolder and copy images
        images_path = package_path / "images"
        images_path.mkdir(exist_ok=True)
        
        for img_file in image_chunk:
            dst_path = images_path / img_file.name
            shutil.copy2(img_file, dst_path)
            
        click.echo(f"  ✓ Copied {len(image_chunk)} images")
        
        # Create package manifest
        self.create_manifest(package_path, chunk_id, image_chunk)
        
        return package_path
    
    def create_manifest(self, package_path: Path, chunk_id: int, image_chunk: List[Path]):
        """Create a manifest file describing the package contents."""
        manifest = {
            "package_info": {
                "id": chunk_id,
                "name": f"work-package-{chunk_id:03d}",
                "created": datetime.now().isoformat(),
                "total_packages": self.num_splits,
                "image_count": len(image_chunk)
            },
            "html_files": self.HTML_FILES,
            "images": [img.name for img in image_chunk],
            "instructions": {
                "1": "Open any of the HTML files in your browser",
                "2": "Load images from the 'images' folder",
                "3": "Click 'AI Analyze' to process your assigned images",
                "4": "Export metadata when analysis is complete",
                "5": "Share the exported JSON file back to the project lead"
            }
        }
        
        manifest_path = package_path / "package-manifest.json"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        click.echo(f"  ✓ Created package manifest")
    
    def split(self) -> List[Path]:
        """Main method to split the work."""
        click.echo(f"🔍 Analyzing source folder: {self.source_folder}")
        
        # Get all image files
        image_files = self.get_image_files()
        if not image_files:
            raise click.ClickException(f"No image files found in {self.source_folder}")
        
        click.echo(f"📸 Found {len(image_files)} image files")
        
        # Split into chunks
        chunks = self.split_images(image_files)
        actual_splits = len(chunks)
        
        if actual_splits != self.num_splits:
            click.echo(f"⚠️  Created {actual_splits} packages instead of {self.num_splits} (insufficient images)")
        
        click.echo(f"📦 Creating {actual_splits} work packages in: {self.output_folder}")
        
        # Create output directory
        self.output_folder.mkdir(parents=True, exist_ok=True)
        
        # Create each work package
        created_packages = []
        for i, chunk in enumerate(chunks):
            click.echo(f"\n📦 Creating package {i+1}/{actual_splits}:")
            package_path = self.create_work_package(i+1, chunk)
            created_packages.append(package_path)
            click.echo(f"   Package: {package_path.name} ({len(chunk)} images)")
        
        return created_packages


@click.command()
@click.option('--source', '-s', 
              type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
              required=True,
              help='Source folder containing images to split')
@click.option('--num-splits', '-n',
              type=int,
              required=True,
              help='Number of work packages to create')
@click.option('--output', '-o',
              type=click.Path(path_type=Path),
              default=None,
              help='Output folder for work packages (default: ./split/)')
@click.version_option(version='1.0.0', prog_name='AI Image Viewer Work Splitter')
def main(source: Path, num_splits: int, output: Path):
    """
    🧠 AI Image Viewer - Work Splitter Tool
    
    Split a source image folder into multiple work packages for team collaboration.
    Each package contains HTML viewers and a subset of images for analysis.
    
    Examples:
    
    \b
    # Split 1000 images into 5 packages for 5 team members
    python split_work.py -s ./big-dataset -n 5
    
    \b
    # Split with custom output location
    python split_work.py -s /path/to/images -n 3 -o /path/to/packages
    """
    
    if num_splits < 1:
        raise click.BadParameter("Number of splits must be at least 1")
    
    if num_splits > 100:
        raise click.BadParameter("Number of splits cannot exceed 100 (too many packages)")
    
    # Set default output location
    if output is None:
        output = Path(__file__).parent / "split"
    
    try:
        click.echo("🧠 AI Image Viewer - Work Splitter Tool")
        click.echo("=" * 45)
        
        # Initialize splitter
        splitter = WorkSplitter(source, output, num_splits)
        
        # Perform the split
        packages = splitter.split()
        
        click.echo(f"\n✅ Successfully created {len(packages)} work packages!")
        click.echo(f"📁 Output location: {output}")
        
        # Show summary
        click.echo(f"\n📋 Package Summary:")
        for i, package in enumerate(packages):
            manifest_path = package / "package-manifest.json"
            if manifest_path.exists():
                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)
                image_count = manifest['package_info']['image_count']
                click.echo(f"   {package.name}: {image_count} images")
        
        click.echo(f"\n🚀 Next Steps:")
        click.echo(f"1. Compress each package: tar -czf package.tar.gz work-package-001/")
        click.echo(f"2. Share packages with team members")
        click.echo(f"3. Team members analyze their assigned images")
        click.echo(f"4. Use join_work.py to merge results when complete")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise click.Abort()


if __name__ == '__main__':
    main()