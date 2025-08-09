#!/usr/bin/env python3
"""
AI Image Viewer - Work Joiner Tool

This tool merges multiple work packages back into a single consolidated package.
It combines:
- Images from all work packages
- AI analysis metadata from all JSON exports
- Creates a unified dataset with complete analysis results

Author: AI Image Viewer Team
"""

import os
import shutil
import json
import click
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import glob


class WorkJoiner:
    """Handles merging multiple work packages into a single consolidated package."""
    
    SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
    HTML_FILES = [
        'ai_image_viewer.html',
        'ai_image_viewer_efficientnet.html', 
        'ai_image_viewer_mediapipe.html'
    ]
    METADATA_PATTERNS = [
        'ai-image-metadata.json',
        '*-image-metadata.json',
        'efficientnet-image-metadata.json',
        'mediapipe-image-metadata.json',
        '*-analysis.json',
        'metadata.json'
    ]
    
    def __init__(self, package_paths: List[Path], output_path: Path):
        self.package_paths = [Path(p) for p in package_paths]
        self.output_path = Path(output_path)
        self.project_root = self.find_project_root()
        
    def find_project_root(self) -> Path:
        """Find the project root containing HTML files."""
        current = Path(__file__).parent
        while current.parent != current:
            if all((current / html).exists() for html in self.HTML_FILES):
                return current
            current = current.parent
        raise FileNotFoundError("Could not find project root with HTML files")
    
    def validate_packages(self) -> List[Path]:
        """Validate that package paths exist and contain expected content."""
        valid_packages = []
        
        for package_path in self.package_paths:
            if not package_path.exists():
                click.echo(f"⚠️  Warning: Package not found: {package_path}")
                continue
                
            if package_path.is_file():
                # Handle compressed packages
                if package_path.suffix in {'.zip', '.tar', '.gz'}:
                    click.echo(f"📦 Found compressed package: {package_path.name}")
                    # TODO: Add extraction logic if needed
                    continue
                else:
                    click.echo(f"⚠️  Warning: Expected folder, got file: {package_path}")
                    continue
            
            # Check if it's a valid package directory
            images_path = package_path / "images"
            if not images_path.exists():
                click.echo(f"⚠️  Warning: No images folder in: {package_path}")
                continue
            
            valid_packages.append(package_path)
            click.echo(f"✓ Valid package: {package_path.name}")
        
        return valid_packages
    
    def collect_images(self, packages: List[Path]) -> List[Path]:
        """Collect all image files from packages."""
        all_images = []
        seen_names = set()
        
        for package in packages:
            images_path = package / "images"
            if not images_path.exists():
                continue
                
            package_images = []
            for ext in self.SUPPORTED_EXTENSIONS:
                package_images.extend(images_path.glob(f"*{ext}"))
                package_images.extend(images_path.glob(f"*{ext.upper()}"))
            
            click.echo(f"📸 Package {package.name}: {len(package_images)} images")
            
            for img in package_images:
                # Handle duplicate names by adding package prefix
                original_name = img.name
                if original_name in seen_names:
                    new_name = f"{package.name}_{original_name}"
                    click.echo(f"  ⚠️  Renaming duplicate: {original_name} → {new_name}")
                    # Create a temporary renamed copy
                    temp_path = img.parent / new_name
                    shutil.copy2(img, temp_path)
                    all_images.append(temp_path)
                    seen_names.add(new_name)
                else:
                    all_images.append(img)
                    seen_names.add(original_name)
        
        return all_images
    
    def find_metadata_files(self, packages: List[Path]) -> List[Path]:
        """Find all metadata JSON files in packages."""
        metadata_files = []
        
        for package in packages:
            found_in_package = []
            
            # Search for metadata files using patterns
            for pattern in self.METADATA_PATTERNS:
                matches = list(package.glob(pattern))
                found_in_package.extend(matches)
            
            # Remove duplicates
            found_in_package = list(set(found_in_package))
            
            if found_in_package:
                click.echo(f"📊 Package {package.name}: {len(found_in_package)} metadata files")
                for meta_file in found_in_package:
                    click.echo(f"  - {meta_file.name}")
                metadata_files.extend(found_in_package)
            else:
                click.echo(f"⚠️  Package {package.name}: No metadata files found")
        
        return metadata_files
    
    def merge_metadata(self, metadata_files: List[Path]) -> Dict[str, Any]:
        """Merge multiple metadata JSON files into a single consolidated metadata."""
        merged = {
            "version": "2.0-Consolidated",
            "timestamp": datetime.now().isoformat(),
            "appName": "AI Image Viewer - Consolidated Results",
            "consolidation_info": {
                "source_files": [f.name for f in metadata_files],
                "packages_merged": len(set(f.parent.name for f in metadata_files)),
                "merge_date": datetime.now().isoformat()
            },
            "totalImages": 0,
            "aiEnabled": True,
            "captions": {},
            "aiData": {}
        }
        
        image_count = 0
        models_used = set()
        
        for meta_file in metadata_files:
            try:
                with open(meta_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                package_name = meta_file.parent.name
                click.echo(f"📋 Processing: {meta_file.name}")
                
                # Merge captions
                if 'captions' in data:
                    for img_name, caption in data['captions'].items():
                        # Handle duplicate image names
                        key = img_name
                        if key in merged['captions']:
                            key = f"{package_name}_{img_name}"
                        merged['captions'][key] = caption
                
                # Merge AI data
                if 'aiData' in data:
                    for img_name, ai_data in data['aiData'].items():
                        # Handle duplicate image names
                        key = img_name
                        if key in merged['aiData']:
                            key = f"{package_name}_{img_name}"
                        merged['aiData'][key] = ai_data
                        
                        # Track models used
                        if 'modelUsed' in ai_data:
                            models_used.add(ai_data['modelUsed'])
                
                # Count images
                if 'totalImages' in data:
                    image_count += data['totalImages']
                
            except json.JSONDecodeError as e:
                click.echo(f"❌ Error parsing {meta_file.name}: {e}")
                continue
            except Exception as e:
                click.echo(f"⚠️  Warning processing {meta_file.name}: {e}")
                continue
        
        merged['totalImages'] = image_count
        merged['consolidation_info']['models_used'] = list(models_used)
        merged['consolidation_info']['total_analyzed_images'] = len(merged['aiData'])
        
        return merged
    
    def create_consolidated_package(self, images: List[Path], metadata: Dict[str, Any]) -> Path:
        """Create the final consolidated package."""
        click.echo(f"📦 Creating consolidated package: {self.output_path}")
        
        # Create output directory
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # Copy HTML files from project root
        for html_file in self.HTML_FILES:
            src_path = self.project_root / html_file
            dst_path = self.output_path / html_file
            if src_path.exists():
                shutil.copy2(src_path, dst_path)
                click.echo(f"✓ Copied {html_file}")
        
        # Copy docs folder if it exists
        docs_src = self.project_root / "docs"
        if docs_src.exists():
            docs_dst = self.output_path / "docs"
            shutil.copytree(docs_src, docs_dst, dirs_exist_ok=True)
            click.echo(f"✓ Copied docs folder")
        
        # Create images folder and copy all images
        images_dst = self.output_path / "images"
        images_dst.mkdir(exist_ok=True)
        
        copied_count = 0
        for img_path in images:
            dst_path = images_dst / img_path.name
            shutil.copy2(img_path, dst_path)
            copied_count += 1
        
        click.echo(f"✓ Copied {copied_count} images")
        
        # Save consolidated metadata
        metadata_path = self.output_path / "consolidated-metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        click.echo(f"✓ Created consolidated metadata")
        
        # Create summary report
        self.create_summary_report(metadata)
        
        return self.output_path
    
    def create_summary_report(self, metadata: Dict[str, Any]):
        """Create a human-readable summary report."""
        report_path = self.output_path / "consolidation-report.txt"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("🧠 AI Image Viewer - Consolidation Report\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Consolidation Date: {metadata['consolidation_info']['merge_date']}\n")
            f.write(f"Packages Merged: {metadata['consolidation_info']['packages_merged']}\n")
            f.write(f"Source Files: {len(metadata['consolidation_info']['source_files'])}\n")
            f.write(f"Total Images: {metadata['totalImages']}\n")
            f.write(f"Analyzed Images: {metadata['consolidation_info']['total_analyzed_images']}\n")
            f.write(f"Analysis Coverage: {metadata['consolidation_info']['total_analyzed_images']/metadata['totalImages']*100:.1f}%\n\n")
            
            if metadata['consolidation_info']['models_used']:
                f.write("AI Models Used:\n")
                for model in metadata['consolidation_info']['models_used']:
                    f.write(f"  - {model}\n")
                f.write("\n")
            
            f.write("Source Metadata Files:\n")
            for source_file in metadata['consolidation_info']['source_files']:
                f.write(f"  - {source_file}\n")
        
        click.echo(f"✓ Created consolidation report")
    
    def join(self) -> Path:
        """Main method to join work packages."""
        click.echo(f"🔍 Validating {len(self.package_paths)} packages...")
        
        # Validate packages
        valid_packages = self.validate_packages()
        if not valid_packages:
            raise click.ClickException("No valid packages found to merge")
        
        click.echo(f"✓ Found {len(valid_packages)} valid packages")
        
        # Collect all images
        click.echo(f"\n📸 Collecting images from packages...")
        all_images = self.collect_images(valid_packages)
        click.echo(f"✓ Collected {len(all_images)} total images")
        
        # Find and merge metadata
        click.echo(f"\n📊 Processing metadata files...")
        metadata_files = self.find_metadata_files(valid_packages)
        
        if not metadata_files:
            click.echo("⚠️  No metadata files found. Creating package with images only.")
            merged_metadata = {
                "version": "2.0-Consolidated",
                "timestamp": datetime.now().isoformat(),
                "appName": "AI Image Viewer - Consolidated Results",
                "consolidation_info": {
                    "source_files": [],
                    "packages_merged": len(valid_packages),
                    "merge_date": datetime.now().isoformat(),
                    "models_used": [],
                    "total_analyzed_images": 0
                },
                "totalImages": len(all_images),
                "aiEnabled": False,
                "captions": {},
                "aiData": {}
            }
        else:
            merged_metadata = self.merge_metadata(metadata_files)
        
        # Create consolidated package
        click.echo(f"\n📦 Creating consolidated package...")
        output_path = self.create_consolidated_package(all_images, merged_metadata)
        
        return output_path


@click.command()
@click.argument('packages', nargs=-1, required=True,
                type=click.Path(exists=True, path_type=Path))
@click.option('--output', '-o',
              type=click.Path(path_type=Path),
              default=None,
              help='Output folder for consolidated package (default: ./join/consolidated)')
@click.option('--force', '-f',
              is_flag=True,
              help='Force overwrite existing output directory')
@click.version_option(version='1.0.0', prog_name='AI Image Viewer Work Joiner')
def main(packages: List[Path], output: Path, force: bool):
    """
    🧠 AI Image Viewer - Work Joiner Tool
    
    Merge multiple work packages into a single consolidated package.
    Combines images and AI analysis metadata from team collaboration.
    
    PACKAGES: One or more work package directories or compressed files to merge
    
    Examples:
    
    \b
    # Join all packages in split folder
    python join_work.py split/work-package-*
    
    \b
    # Join specific packages with custom output
    python join_work.py package1/ package2/ package3/ -o final-results/
    
    \b
    # Force overwrite existing output
    python join_work.py split/* -f
    """
    
    if len(packages) < 1:
        raise click.BadParameter("At least one package must be specified")
    
    # Set default output location
    if output is None:
        output = Path(__file__).parent / "join" / "consolidated"
    
    # Check if output exists
    if output.exists() and not force:
        if click.confirm(f"Output directory {output} exists. Overwrite?"):
            shutil.rmtree(output)
        else:
            click.echo("❌ Aborted by user")
            return
    elif output.exists() and force:
        shutil.rmtree(output)
    
    try:
        click.echo("🧠 AI Image Viewer - Work Joiner Tool")
        click.echo("=" * 43)
        
        # Initialize joiner
        joiner = WorkJoiner(packages, output)
        
        # Perform the join
        result_path = joiner.join()
        
        click.echo(f"\n✅ Successfully created consolidated package!")
        click.echo(f"📁 Output location: {result_path}")
        
        # Show final summary
        metadata_path = result_path / "consolidated-metadata.json"
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            click.echo(f"\n📋 Final Summary:")
            click.echo(f"   Total Images: {metadata['totalImages']}")
            click.echo(f"   Analyzed Images: {metadata.get('consolidation_info', {}).get('total_analyzed_images', 0)}")
            click.echo(f"   Packages Merged: {len(packages)}")
            
            if 'models_used' in metadata.get('consolidation_info', {}):
                models = metadata['consolidation_info']['models_used']
                click.echo(f"   AI Models Used: {', '.join(models) if models else 'None'}")
        
        click.echo(f"\n🚀 Next Steps:")
        click.echo(f"1. Open any HTML file in the consolidated package")
        click.echo(f"2. Import 'consolidated-metadata.json' to see all analysis results")
        click.echo(f"3. Review 'consolidation-report.txt' for detailed statistics")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise click.Abort()


if __name__ == '__main__':
    main()