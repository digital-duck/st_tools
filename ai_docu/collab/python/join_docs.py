#!/usr/bin/env python3
"""
AI Docu App - Document Joiner Tool

This tool merges analysis results from multiple work packages back into a unified dataset.
It combines:
- Multiple metadata JSON files from different team members
- Document analysis results from various AI models
- Consolidated output for project leads

Author: AI Docu App Team
"""

import os
import json
import click
import tarfile
import shutil
from pathlib import Path
from typing import List, Dict, Any, Set
from datetime import datetime
from collections import defaultdict


class DocumentJoiner:
    """Handles merging analysis results from collaborative work packages."""
    
    SUPPORTED_METADATA_PATTERNS = [
        'ai-docu-sentencebert-metadata.json',
        'ai-docu-distilbert-metadata.json', 
        'ai-docu-universal-metadata.json',
        'ai-docu-metadata.json'
    ]
    
    def __init__(self, input_folder: Path, output_folder: Path):
        self.input_folder = Path(input_folder)
        self.output_folder = Path(output_folder)
        self.processed_files = set()
        self.merged_data = defaultdict(dict)
        
    def extract_compressed_packages(self) -> List[Path]:
        """Extract any compressed packages in the input folder."""
        extracted_paths = []
        
        # Find all .tar.gz files
        archive_files = list(self.input_folder.glob("*.tar.gz"))
        
        if archive_files:
            click.echo(f"🗜️  Found {len(archive_files)} compressed packages to extract")
            
            for archive_file in archive_files:
                click.echo(f"   Extracting {archive_file.name}...")
                
                try:
                    with tarfile.open(archive_file, "r:gz") as tar:
                        # Extract to input folder
                        tar.extractall(path=self.input_folder)
                        
                    # Find the extracted folder
                    package_name = archive_file.stem.replace('.tar', '')
                    extracted_path = self.input_folder / package_name
                    
                    if extracted_path.exists():
                        extracted_paths.append(extracted_path)
                        click.echo(f"   ✓ Extracted to {package_name}/")
                    
                except Exception as e:
                    click.echo(f"   ❌ Error extracting {archive_file.name}: {e}")
                    
        return extracted_paths
    
    def find_package_directories(self) -> List[Path]:
        """Find all package directories (both extracted and uncompressed)."""
        package_dirs = []
        
        # Look for directories that match package naming pattern
        for item in self.input_folder.iterdir():
            if item.is_dir() and (
                item.name.startswith('docu-package-') or 
                'package' in item.name.lower() or
                self.has_metadata_files(item)
            ):
                package_dirs.append(item)
        
        return sorted(package_dirs)
    
    def has_metadata_files(self, directory: Path) -> bool:
        """Check if directory contains metadata files."""
        for pattern in self.SUPPORTED_METADATA_PATTERNS:
            if (directory / pattern).exists():
                return True
        return False
    
    def find_metadata_files(self, package_dir: Path) -> List[Path]:
        """Find all metadata files in a package directory."""
        metadata_files = []
        
        for pattern in self.SUPPORTED_METADATA_PATTERNS:
            metadata_file = package_dir / pattern
            if metadata_file.exists():
                metadata_files.append(metadata_file)
                
        return metadata_files
    
    def load_metadata_file(self, metadata_file: Path) -> Dict[str, Any]:
        """Load and validate a metadata JSON file."""
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Validate structure
            if not isinstance(data, dict):
                raise ValueError("Metadata must be a JSON object")
                
            if 'metadata' not in data:
                raise ValueError("Missing 'metadata' key in JSON")
                
            return data
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")
        except Exception as e:
            raise ValueError(f"Error reading file: {e}")
    
    def merge_metadata(self, all_metadata: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge multiple metadata dictionaries into one."""
        if not all_metadata:
            return {}
            
        # Start with the first metadata as base
        merged = {
            'metadata': {},
            'export_info': {
                'timestamp': datetime.now().isoformat(),
                'source': 'AI Docu App - Document Joiner',
                'merged_packages': len(all_metadata),
                'total_documents': 0,
                'ai_models_used': set()
            }
        }
        
        # Merge all document metadata
        for metadata_dict in all_metadata:
            if 'metadata' in metadata_dict:
                merged['metadata'].update(metadata_dict['metadata'])
                
            # Collect export info
            if 'export_info' in metadata_dict:
                export_info = metadata_dict['export_info']
                if 'ai_model' in export_info:
                    merged['export_info']['ai_models_used'].add(export_info['ai_model'])
        
        # Convert set to list for JSON serialization
        merged['export_info']['ai_models_used'] = list(merged['export_info']['ai_models_used'])
        merged['export_info']['total_documents'] = len(merged['metadata'])
        
        return merged
    
    def create_summary_report(self, merged_data: Dict[str, Any], package_dirs: List[Path]) -> str:
        """Create a summary report of the joining process."""
        report = f"""# AI Docu App - Document Analysis Summary Report

## 📊 Merge Summary

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Source Packages:** {len(package_dirs)}  
**Total Documents:** {len(merged_data.get('metadata', {}))}  
**AI Models Used:** {', '.join(merged_data['export_info']['ai_models_used'])}

## 📦 Source Packages

"""
        
        for i, package_dir in enumerate(package_dirs, 1):
            metadata_files = self.find_metadata_files(package_dir)
            doc_count = 0
            
            # Count documents from first metadata file
            if metadata_files:
                try:
                    with open(metadata_files[0], 'r') as f:
                        data = json.load(f)
                        doc_count = len(data.get('metadata', {}))
                except:
                    pass
                    
            report += f"{i}. **{package_dir.name}**\n"
            report += f"   - Documents: {doc_count}\n"
            report += f"   - Metadata files: {len(metadata_files)}\n"
            if metadata_files:
                report += f"   - AI models: {[f.name.replace('ai-docu-', '').replace('-metadata.json', '') for f in metadata_files]}\n"
            report += "\n"
        
        # Document analysis summary
        if merged_data.get('metadata'):
            report += "## 📄 Document Analysis Overview\n\n"
            
            # Count by file type
            file_types = defaultdict(int)
            has_summaries = 0
            has_keywords = 0
            
            for filename, doc_data in merged_data['metadata'].items():
                # Extract file extension
                ext = Path(filename).suffix.lower()
                file_types[ext] += 1
                
                if doc_data.get('summary'):
                    has_summaries += 1
                if doc_data.get('keywords'):
                    has_keywords += 1
            
            report += "### File Types\n"
            for ext, count in sorted(file_types.items()):
                report += f"- **{ext or 'no extension'}**: {count} files\n"
            
            report += f"\n### Analysis Coverage\n"
            report += f"- Documents with summaries: {has_summaries}/{len(merged_data['metadata'])} ({has_summaries/len(merged_data['metadata'])*100:.1f}%)\n"
            report += f"- Documents with keywords: {has_keywords}/{len(merged_data['metadata'])} ({has_keywords/len(merged_data['metadata'])*100:.1f}%)\n"
        
        report += f"""
## 🚀 Next Steps

1. **Review Results**: Open the merged metadata JSON file to review all analysis
2. **Import to AI Docu App**: Load the consolidated results back into the main application
3. **Quality Check**: Verify that all expected documents are included
4. **Archive Packages**: Clean up individual work packages if no longer needed

## 📁 Output Files

- `merged-ai-docu-metadata.json` - Consolidated analysis results
- `join-summary-report.md` - This summary report
- `package-manifest.json` - Details about the merge process

---

*Report generated by AI Docu App Document Joiner v1.0.0*
"""
        
        return report
    
    def join(self) -> Dict[str, Any]:
        """Main method to join all work packages."""
        click.echo(f"🔍 Analyzing input folder: {self.input_folder}")
        
        # Extract any compressed packages first
        extracted_paths = self.extract_compressed_packages()
        if extracted_paths:
            click.echo(f"✓ Extracted {len(extracted_paths)} compressed packages")
        
        # Find all package directories
        package_dirs = self.find_package_directories()
        if not package_dirs:
            raise click.ClickException(f"No package directories found in {self.input_folder}")
        
        click.echo(f"📦 Found {len(package_dirs)} package directories")
        
        # Collect all metadata files
        all_metadata = []
        total_documents = 0
        
        for package_dir in package_dirs:
            click.echo(f"\n📄 Processing package: {package_dir.name}")
            
            metadata_files = self.find_metadata_files(package_dir)
            if not metadata_files:
                click.echo(f"   ⚠️  No metadata files found, skipping")
                continue
                
            click.echo(f"   Found {len(metadata_files)} metadata files")
            
            # Process each metadata file
            for metadata_file in metadata_files:
                try:
                    click.echo(f"   Loading {metadata_file.name}...")
                    metadata_dict = self.load_metadata_file(metadata_file)
                    
                    doc_count = len(metadata_dict.get('metadata', {}))
                    all_metadata.append(metadata_dict)
                    total_documents += doc_count
                    
                    click.echo(f"   ✓ Loaded {doc_count} documents")
                    
                except Exception as e:
                    click.echo(f"   ❌ Error loading {metadata_file.name}: {e}")
                    continue
        
        if not all_metadata:
            raise click.ClickException("No valid metadata files found to merge")
        
        click.echo(f"\n🔄 Merging {len(all_metadata)} metadata files...")
        click.echo(f"📊 Total documents to merge: {total_documents}")
        
        # Merge all metadata
        merged_data = self.merge_metadata(all_metadata)
        
        # Create output directory
        self.output_folder.mkdir(parents=True, exist_ok=True)
        
        # Save merged metadata
        output_file = self.output_folder / "merged-ai-docu-metadata.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, indent=2, ensure_ascii=False)
        
        click.echo(f"✓ Saved merged metadata: {output_file}")
        
        # Create summary report
        summary_report = self.create_summary_report(merged_data, package_dirs)
        report_file = self.output_folder / "join-summary-report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(summary_report)
            
        click.echo(f"✓ Created summary report: {report_file}")
        
        # Create package manifest
        manifest = {
            "join_info": {
                "timestamp": datetime.now().isoformat(),
                "source_packages": [str(p) for p in package_dirs],
                "total_metadata_files": len(all_metadata),
                "total_documents": len(merged_data['metadata']),
                "ai_models_used": merged_data['export_info']['ai_models_used']
            },
            "output_files": [
                "merged-ai-docu-metadata.json",
                "join-summary-report.md",
                "package-manifest.json"
            ]
        }
        
        manifest_file = self.output_folder / "package-manifest.json"
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
            
        click.echo(f"✓ Created package manifest: {manifest_file}")
        
        return merged_data


@click.command()
@click.option('--input', '-i',
              type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
              required=True,
              help='Input folder containing completed work packages')
@click.option('--output', '-o',
              type=click.Path(path_type=Path),
              default=None,
              help='Output folder for merged results (default: ./joined/)')
@click.option('--clean-extracted', '-c',
              is_flag=True,
              default=False,
              help='Clean up extracted package folders after processing')
@click.version_option(version='1.0.0', prog_name='AI Docu App Document Joiner')
def main(input: Path, output: Path, clean_extracted: bool):
    """
    📄 AI Docu App - Document Joiner Tool
    
    Merge analysis results from multiple work packages back into a unified dataset.
    Handles both compressed (.tar.gz) and uncompressed package directories.
    
    Examples:
    
    \\b
    # Join packages from a folder containing .tar.gz files
    python join_docs.py -i ./completed-packages
    
    \\b
    # Join with custom output location and cleanup
    python join_docs.py -i /path/to/packages -o /path/to/results -c
    """
    
    # Set default output location
    if output is None:
        output = Path(__file__).parent / "joined"
    
    try:
        click.echo("📄 AI Docu App - Document Joiner Tool")
        click.echo("=" * 42)
        
        # Initialize joiner
        joiner = DocumentJoiner(input, output)
        
        # Perform the join
        merged_data = joiner.join()
        
        click.echo(f"\n✅ Successfully merged document analysis results!")
        click.echo(f"📁 Output location: {output}")
        click.echo(f"📊 Total documents: {len(merged_data.get('metadata', {}))}")
        click.echo(f"🤖 AI models used: {', '.join(merged_data['export_info']['ai_models_used'])}")
        
        click.echo(f"\n🚀 Next Steps:")
        click.echo(f"1. Review: Open join-summary-report.md for detailed analysis")
        click.echo(f"2. Import: Load merged-ai-docu-metadata.json into AI Docu App")
        click.echo(f"3. Verify: Check that all expected documents are included")
        
        if clean_extracted:
            click.echo(f"4. Cleanup: Removing extracted package directories...")
            # Clean up extracted directories
            for item in input.iterdir():
                if item.is_dir() and item.name.startswith('docu-package-'):
                    shutil.rmtree(item)
                    click.echo(f"   ✓ Removed {item.name}")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise click.Abort()


if __name__ == '__main__':
    main()