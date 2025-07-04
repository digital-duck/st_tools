#!/usr/bin/env python3
"""
Project Structure Scaffolder CLI Tool
A utility to create project structures from text or YAML specifications
"""

import click
import yaml
import os
import re
from pathlib import Path
from typing import Dict, List, Union, Optional

class ProjectScaffolder:
    """Main class for handling project structure operations"""
    
    def __init__(self):
        self.tree_patterns = {
            'branch': r'[│├└]',
            'connector': r'[├└]──',
            'vertical': r'│',
            'last_item': r'└──',
            'middle_item': r'├──',
            'comment': r'#.*$'
        }
    
    def parse_text_structure(self, text_content: str) -> Dict:
        """Parse text-based tree structure into hierarchical dictionary"""
        lines = text_content.strip().split('\n')
        root = {}
        path_stack = []
        
        for line in lines:
            if not line.strip():
                continue
                
            # Calculate indentation level
            indent_level = self._calculate_indent_level(line)
            
            # Extract item name and comment
            item_name, comment = self._extract_item_info(line)
            
            if not item_name:
                continue
            
            # Adjust path stack based on indentation
            path_stack = path_stack[:indent_level]
            
            # Create item info
            item_info = {
                'type': 'directory' if item_name.endswith('/') else 'file',
                'name': item_name.rstrip('/'),
                'comment': comment,
                'children': {} if item_name.endswith('/') else None
            }
            
            # Add to structure
            if not path_stack:
                root[item_info['name']] = item_info
            else:
                current = root
                for path_part in path_stack:
                    current = current[path_part]['children']
                current[item_info['name']] = item_info
            
            # Update path stack
            if item_info['type'] == 'directory':
                path_stack.append(item_info['name'])
        
        return root
    
    def _calculate_indent_level(self, line: str) -> int:
        """Calculate indentation level from tree structure"""
        # Count tree characters and spaces to determine depth
        clean_line = re.sub(r'[│├└─\s]', '', line, count=0)
        original_line = line
        
        # Find where the actual content starts
        content_start = len(line) - len(line.lstrip('│├└─ \t'))
        
        # Each level is typically 4 characters in tree notation
        # But we need to be more precise based on the actual pattern
        level = 0
        pos = 0
        
        while pos < len(line):
            if line[pos:pos+4] in ['│   ', '├── ', '└── ']:
                level += 1
                pos += 4
            elif line[pos:pos+4] == '    ':  # Just spaces
                level += 1
                pos += 4
            else:
                break
        
        return level
    
    def _extract_item_info(self, line: str) -> tuple:
        """Extract item name and comment from line"""
        # Remove tree structure characters
        clean_line = re.sub(r'^[│├└─\s]+', '', line)
        
        # Split by comment marker
        parts = clean_line.split('#', 1)
        item_name = parts[0].strip()
        comment = parts[1].strip() if len(parts) > 1 else ''
        
        # Remove extra formatting
        comment = comment.strip('*')
        
        return item_name, comment
    
    def structure_to_yaml(self, structure: Dict, output_file: str = None) -> str:
        """Convert structure dictionary to YAML format"""
        yaml_structure = self._convert_to_yaml_format(structure)
        
        yaml_content = yaml.dump(yaml_structure, default_flow_style=False, 
                                indent=2, sort_keys=False)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(yaml_content)
            click.echo(f"YAML structure saved to: {output_file}")
        
        return yaml_content
    
    def _convert_to_yaml_format(self, structure: Dict) -> Dict:
        """Convert internal structure to YAML-friendly format"""
        yaml_structure = {}
        
        for name, info in structure.items():
            if info['type'] == 'directory':
                # Directory: has children (even if empty)
                yaml_item = {}
                if info['comment']:
                    yaml_item['comment'] = info['comment']
                yaml_item['children'] = self._convert_to_yaml_format(info['children']) if info['children'] else {}
                yaml_structure[name] = yaml_item
            else:
                # File: just comment if present, otherwise empty string or null
                if info['comment']:
                    yaml_structure[name] = info['comment']
                else:
                    yaml_structure[name] = ''
        
        return yaml_structure
    
    def yaml_to_structure(self, yaml_content: str) -> Dict:
        """Convert YAML content to internal structure format"""
        yaml_data = yaml.safe_load(yaml_content)
        return self._convert_from_yaml_format(yaml_data)
    
    def _convert_from_yaml_format(self, yaml_data: Dict) -> Dict:
        """Convert YAML format to internal structure"""
        structure = {}
        
        for name, info in yaml_data.items():
            if isinstance(info, dict) and 'children' in info:
                # Directory: has children attribute
                structure[name] = {
                    'type': 'directory',
                    'name': name,
                    'comment': info.get('comment', ''),
                    'children': self._convert_from_yaml_format(info.get('children', {}))
                }
            else:
                # File: either string comment or empty
                comment = info if isinstance(info, str) else ''
                structure[name] = {
                    'type': 'file',
                    'name': name,
                    'comment': comment
                }
        
        return structure
    
    def structure_to_text(self, structure: Dict, output_file: str = None) -> str:
        """Convert structure dictionary to text tree format"""
        text_lines = []
        
        def build_tree(items: Dict, prefix: str = "", is_last_level: bool = True):
            item_list = list(items.items())
            for i, (name, info) in enumerate(item_list):
                is_last = i == len(item_list) - 1
                
                # Choose connector
                if i == 0 and prefix == "":
                    connector = ""
                elif is_last:
                    connector = "└── "
                else:
                    connector = "├── "
                
                # Build line
                display_name = name + ("/" if info['type'] == 'directory' else "")
                comment_part = f" # {info['comment']}" if info['comment'] else ""
                line = f"{prefix}{connector}{display_name}{comment_part}"
                text_lines.append(line)
                
                # Handle children
                if info['type'] == 'directory' and info.get('children'):
                    new_prefix = prefix + ("    " if is_last else "│   ")
                    build_tree(info['children'], new_prefix, is_last)
        
        build_tree(structure)
        text_content = '\n'.join(text_lines)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(text_content)
            click.echo(f"Text structure saved to: {output_file}")
        
        return text_content
    
    def create_project_structure(self, structure: Dict, base_path: str = "."):
        """Create the actual directory and file structure"""
        base_path = Path(base_path)
        
        def create_items(items: Dict, current_path: Path):
            for name, info in items.items():
                item_path = current_path / name
                
                if info['type'] == 'directory':
                    # Create directory
                    item_path.mkdir(parents=True, exist_ok=True)
                    click.echo(f"Created directory: {item_path}")
                    
                    # Create children
                    if info.get('children'):
                        create_items(info['children'], item_path)
                else:
                    # Create file - just touch it (empty file)
                    item_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Create empty file if it doesn't exist
                    if not item_path.exists():
                        item_path.touch()  # Just create empty file
                        click.echo(f"Created file: {item_path}")
                    else:
                        click.echo(f"File already exists: {item_path}")
        
        create_items(structure, base_path)


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Project Structure Scaffolder - Create project structures from text or YAML"""
    pass


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', help='Output YAML file path')
@click.option('--show', is_flag=True, help='Show YAML content in terminal')
def text_to_yaml(input_file, output, show):
    """Convert text tree structure to YAML format"""
    scaffolder = ProjectScaffolder()
    
    with open(input_file, 'r') as f:
        text_content = f.read()
    
    structure = scaffolder.parse_text_structure(text_content)
    yaml_content = scaffolder.structure_to_yaml(structure, output)
    
    if show:
        click.echo("\\n" + "="*50)
        click.echo("YAML Structure:")
        click.echo("="*50)
        click.echo(yaml_content)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', help='Output text file path')
@click.option('--show', is_flag=True, help='Show text content in terminal')
def yaml_to_text(input_file, output, show):
    """Convert YAML structure to text tree format"""
    scaffolder = ProjectScaffolder()
    
    with open(input_file, 'r') as f:
        yaml_content = f.read()
    
    structure = scaffolder.yaml_to_structure(yaml_content)
    text_content = scaffolder.structure_to_text(structure, output)
    
    if show:
        click.echo("\\n" + "="*50)
        click.echo("Text Tree Structure:")
        click.echo("="*50)
        click.echo(text_content)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--target', '-t', default='.', help='Target directory for project creation')
@click.option('--format', '-f', type=click.Choice(['text', 'yaml']), default='text', 
              help='Input file format')
@click.option('--dry-run', is_flag=True, help='Show what would be created without creating')
def create(input_file, target, format, dry_run):
    """Create project structure from text or YAML file"""
    scaffolder = ProjectScaffolder()
    
    with open(input_file, 'r') as f:
        content = f.read()
    
    if format == 'text':
        structure = scaffolder.parse_text_structure(content)
    else:
        structure = scaffolder.yaml_to_structure(content)
    
    if dry_run:
        click.echo("\\n" + "="*50)
        click.echo("DRY RUN - Would create:")
        click.echo("="*50)
        text_preview = scaffolder.structure_to_text(structure)
        click.echo(text_preview)
        click.echo("\\n" + "="*50)
        click.echo(f"Target directory: {os.path.abspath(target)}")
    else:
        click.echo(f"Creating project structure in: {os.path.abspath(target)}")
        scaffolder.create_project_structure(structure, target)
        click.echo("\\n✅ Project structure created successfully!")


@cli.command()
@click.argument('text_content', required=False)
@click.option('--file', '-f', type=click.Path(exists=True), help='Input text file')
@click.option('--target', '-t', default='.', help='Target directory for project creation')
def quick_create(text_content, file, target):
    """Quick create project structure from text input or file"""
    scaffolder = ProjectScaffolder()
    
    if file:
        with open(file, 'r') as f:
            content = f.read()
    elif text_content:
        content = text_content
    else:
        click.echo("Please provide either text content or --file option")
        return
    
    structure = scaffolder.parse_text_structure(content)
    
    click.echo(f"Creating project structure in: {os.path.abspath(target)}")
    scaffolder.create_project_structure(structure, target)
    click.echo("\\n✅ Project structure created successfully!")


@cli.command()
@click.argument('text_content', required=False)
@click.option('--file', '-f', type=click.Path(exists=True), help='Input text file')
@click.option('--target', '-t', default='.', help='Target directory for project creation')
def quick_create(text_content, file, target):
    """Quick create project structure from text input or file"""
    scaffolder = ProjectScaffolder()
    
    if file:
        with open(file, 'r') as f:
            content = f.read()
    elif text_content:
        content = text_content
    else:
        click.echo("Please provide either text content or --file option")
        return
    
    structure = scaffolder.parse_text_structure(content)
    
    click.echo(f"Creating project structure in: {os.path.abspath(target)}")
    scaffolder.create_project_structure(structure, target)
    click.echo("\n✅ Project structure created successfully!")


if __name__ == '__main__':
    cli()
