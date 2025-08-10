#!/usr/bin/env python3
"""
AI Docu App - Document Splitter Tool

This tool splits a source document folder into multiple work packages for collaborative analysis.
Each package contains:
- AI Docu App HTML file
- A subset of documents for analysis
- Ready-to-share bundle for team collaboration

Author: AI Docu App Team
"""

import os
import shutil
import math
import click
import tarfile
from pathlib import Path
from typing import List, Tuple
import json
from datetime import datetime


class DocumentSplitter:
    """Handles splitting document collections into collaborative work packages."""
    
    SUPPORTED_EXTENSIONS = {'.txt', '.pdf', '.docx', '.rtf', '.md'}
    HTML_FILES = ['ai_docu.html']
    
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
    
    def get_document_files(self) -> List[Path]:
        """Get all supported document files from source folder."""
        document_files = []
        for ext in self.SUPPORTED_EXTENSIONS:
            document_files.extend(self.source_folder.glob(f"*{ext}"))
            document_files.extend(self.source_folder.glob(f"*{ext.upper()}"))
        return sorted(document_files)
    
    def split_documents(self, document_files: List[Path]) -> List[List[Path]]:
        """Split document files into roughly equal chunks."""
        if not document_files:
            raise ValueError("No document files found in source folder")
            
        chunk_size = math.ceil(len(document_files) / self.num_splits)
        chunks = []
        
        for i in range(self.num_splits):
            start_idx = i * chunk_size
            end_idx = min((i + 1) * chunk_size, len(document_files))
            chunk = document_files[start_idx:end_idx]
            if chunk:  # Only add non-empty chunks
                chunks.append(chunk)
                
        return chunks
    
    def create_work_package(self, chunk_id: int, document_chunk: List[Path]) -> Path:
        """Create a complete work package with HTML files and documents."""
        package_name = f"docu-package-{chunk_id:03d}"
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
        
        # Create documents subfolder and copy documents
        documents_path = package_path / "documents"
        documents_path.mkdir(exist_ok=True)
        
        for doc_file in document_chunk:
            dst_path = documents_path / doc_file.name
            shutil.copy2(doc_file, dst_path)
            
        click.echo(f"  ✓ Copied {len(document_chunk)} documents")
        
        # Create package manifest
        self.create_manifest(package_path, chunk_id, document_chunk)
        
        # Create README for team members
        self.create_package_readme(package_path, chunk_id, document_chunk)
        
        return package_path
    
    def create_manifest(self, package_path: Path, chunk_id: int, document_chunk: List[Path]):
        """Create a manifest file describing the package contents."""
        manifest = {
            "package_info": {
                "id": chunk_id,
                "name": f"docu-package-{chunk_id:03d}",
                "created": datetime.now().isoformat(),
                "total_packages": self.num_splits,
                "document_count": len(document_chunk)
            },
            "html_files": self.HTML_FILES,
            "documents": [doc.name for doc in document_chunk],
            "instructions": {
                "1": "Open ai_docu.html in your browser",
                "2": "Load documents from the 'documents' folder",
                "3": "Select your preferred AI model",
                "4": "Click 'AI Analyze' to process your assigned documents",
                "5": "Export metadata when analysis is complete",
                "6": "Share the exported JSON file back to the project lead"
            }
        }
        
        manifest_path = package_path / "package-manifest.json"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        click.echo(f"  ✓ Created package manifest")
    
    def create_package_readme(self, package_path: Path, chunk_id: int, document_chunk: List[Path]):
        """Create a README.md file with instructions for team members."""
        readme_content = f"""# AI Docu Analysis Work Package

📦 **Package:** docu-package-{chunk_id:03d}  
📄 **Documents to analyze:** {len(document_chunk)}  
📅 **Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🚀 Quick Start

### 1. Open the AI Docu App
Open the HTML file in your web browser:
- `ai_docu.html` - AI-powered document analyzer with multiple AI models

### 2. Load Documents
- Click **"📁 Select Documents"** and choose files from the `documents/` folder
- Or click **"📂 Select Folder"** and select the entire `documents/` folder
- You should see {len(document_chunk)} documents loaded

### 3. Choose AI Model and Analyze
- Select your preferred AI model from the dropdown:
  - **Sentence-BERT**: Fast text embeddings and similarity
  - **DistilBERT**: Document classification and categorization  
  - **Universal Encoder**: Advanced semantic understanding
- Click the **AI Analyze** button 🧠
- Wait for analysis to complete (progress bar will show status)
- All documents will get AI-generated keywords, summaries, and classifications

### 4. Export Results
- Click **"💾 Export Metadata"** button
- This saves a `.json` file with all analysis results
- The filename will be based on your selected model: `ai-docu-sentencebert-metadata.json`, `ai-docu-distilbert-metadata.json`, or `ai-docu-universal-metadata.json`

### 5. Send Back to Team Lead
- **Compress this entire folder** (including the new metadata file):
  ```bash
  # Easy way:
  cd ..
  tar -czf docu-package-{chunk_id:03d}-completed.tar.gz docu-package-{chunk_id:03d}/
  ```
- **Send the compressed file** back to your team lead
- Team lead will merge all results using the join tool

## 📝 Tips

- **Edit summaries**: Click on any document summary to edit it manually
- **Search**: Use the AI search feature to find specific documents
- **Grid layout**: Adjust how many documents per row (1-4)
- **Model comparison**: Try different AI models to compare results
- **File info**: Toggle the "Show file info" checkbox to see document details

## 🔍 File Structure

```
docu-package-{chunk_id:03d}/
├── README.md                              # This file
├── ai_docu.html                           # AI Docu App
├── docs/                                  # Documentation assets  
├── documents/                             # Your {len(document_chunk)} documents to analyze
├── package-manifest.json                 # Package info
└── [exported-metadata].json              # Your analysis results (after export)
```

## 📄 Document Types Supported

- **Text Files**: .txt, .rtf, .md
- **PDF Documents**: .pdf (with text extraction)
- **Word Documents**: .docx (with content conversion)

## ❓ Questions?

If you run into issues:
1. Make sure you're using a modern web browser (Chrome, Firefox, Safari, Edge)
2. Check the browser console for any error messages
3. Try a different AI model if one isn't working
4. Contact your team lead for help

**Happy document analyzing! 📄🚀**
"""
        
        readme_path = package_path / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        click.echo(f"  ✓ Created README.md for team members")
    
    def split(self) -> List[Path]:
        """Main method to split the work."""
        click.echo(f"🔍 Analyzing source folder: {self.source_folder}")
        
        # Get all document files
        document_files = self.get_document_files()
        if not document_files:
            raise click.ClickException(f"No document files found in {self.source_folder}")
        
        click.echo(f"📄 Found {len(document_files)} document files")
        
        # Split into chunks
        chunks = self.split_documents(document_files)
        actual_splits = len(chunks)
        
        if actual_splits != self.num_splits:
            click.echo(f"⚠️  Created {actual_splits} packages instead of {self.num_splits} (insufficient documents)")
        
        click.echo(f"📦 Creating {actual_splits} work packages in: {self.output_folder}")
        
        # Create output directory
        self.output_folder.mkdir(parents=True, exist_ok=True)
        
        # Create each work package
        created_packages = []
        for i, chunk in enumerate(chunks):
            click.echo(f"\n📦 Creating package {i+1}/{actual_splits}:")
            package_path = self.create_work_package(i+1, chunk)
            created_packages.append(package_path)
            click.echo(f"   Package: {package_path.name} ({len(chunk)} documents)")
        
        return created_packages
    
    def compress_packages(self, packages: List[Path]) -> List[Path]:
        """Compress work packages into .tar.gz files."""
        compressed_files = []
        
        click.echo(f"\n🗜️  Compressing {len(packages)} packages...")
        
        for package_path in packages:
            if not package_path.exists():
                continue
                
            # Create .tar.gz file in the same directory
            archive_name = f"{package_path.name}.tar.gz"
            archive_path = package_path.parent / archive_name
            
            click.echo(f"   Compressing {package_path.name}...")
            
            try:
                with tarfile.open(archive_path, "w:gz") as tar:
                    tar.add(package_path, arcname=package_path.name)
                
                compressed_files.append(archive_path)
                click.echo(f"   ✓ Created {archive_name}")
                
            except Exception as e:
                click.echo(f"   ❌ Error compressing {package_path.name}: {e}")
                continue
        
        return compressed_files


@click.command()
@click.option('--source', '-s', 
              type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
              required=True,
              help='Source folder containing documents to split')
@click.option('--num-splits', '-n',
              type=int,
              required=True,
              help='Number of work packages to create')
@click.option('--output', '-o',
              type=click.Path(path_type=Path),
              default=None,
              help='Output folder for work packages (default: ./split/)')
@click.option('--compress', '-c',
              is_flag=True,
              default=True,
              help='Automatically compress each package as .tar.gz')
@click.version_option(version='1.0.0', prog_name='AI Docu App Document Splitter')
def main(source: Path, num_splits: int, output: Path, compress: bool):
    """
    📄 AI Docu App - Document Splitter Tool
    
    Split a source document folder into multiple work packages for team collaboration.
    Each package contains the AI Docu App and a subset of documents for analysis.
    
    Examples:
    
    \b
    # Split 1000 documents into 5 packages for 5 team members
    python split_work.py -s ./big-document-collection -n 5
    
    \b
    # Split with custom output location
    python split_work.py -s /path/to/documents -n 3 -o /path/to/packages
    """
    
    if num_splits < 1:
        raise click.BadParameter("Number of splits must be at least 1")
    
    if num_splits > 100:
        raise click.BadParameter("Number of splits cannot exceed 100 (too many packages)")
    
    # Set default output location
    if output is None:
        output = Path(__file__).parent / "split"
    
    try:
        click.echo("📄 AI Docu App - Document Splitter Tool")
        click.echo("=" * 45)
        
        # Initialize splitter
        splitter = DocumentSplitter(source, output, num_splits)
        
        # Perform the split
        packages = splitter.split()
        
        # Compress packages if requested
        compressed_files = []
        if compress:
            compressed_files = splitter.compress_packages(packages)
        
        click.echo(f"\n✅ Successfully created {len(packages)} work packages!")
        if compressed_files:
            click.echo(f"🗜️  Compressed {len(compressed_files)} packages!")
        click.echo(f"📁 Output location: {output}")
        
        # Show summary
        click.echo(f"\n📋 Package Summary:")
        for i, package in enumerate(packages):
            manifest_path = package / "package-manifest.json"
            if manifest_path.exists():
                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)
                document_count = manifest['package_info']['document_count']
                click.echo(f"   {package.name}: {document_count} documents")
        
        click.echo(f"\n🚀 Next Steps:")
        if compress:
            click.echo(f"1. Share .tar.gz files with team members")
            click.echo(f"2. Team members extract: tar -xzf docu-package-001.tar.gz")
            click.echo(f"3. Team members analyze their assigned documents and send back results")
            click.echo(f"4. Team lead uses join_work.py to merge results")
        else:
            click.echo(f"1. Compress packages: python split_work.py -s {source} -n {num_splits} -c")
            click.echo(f"2. Or manually: tar -czf docu-package-001.tar.gz docu-package-001/")
            click.echo(f"3. Share packages with team members")
            click.echo(f"4. Team lead uses join_work.py to merge results")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise click.Abort()


if __name__ == '__main__':
    main()