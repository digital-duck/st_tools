import os
import shutil
import argparse
import yaml
import base64
from pathlib import Path
from typing import Dict, Any, Optional

def create_project_from_config(config_file: str, base_dir: Optional[str] = None) -> None:
    """
    Create a project structure based on a YAML configuration file.
    
    Args:
        config_file (str): Path to the YAML configuration file.
        base_dir (Optional[str]): Override the base directory. If None, use the one from config.
    """
    # Load configuration
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    # Get project name from config or override
    project_name = base_dir or config.get('project_name', 'new_project')
    
    # Create base directory if it doesn't exist
    if not os.path.exists(project_name):
        os.makedirs(project_name)
        print(f"Created base directory: {project_name}")
    
    # Create directories
    for dir_config in config.get('directories', []):
        dir_path = os.path.join(project_name, dir_config['path'])
        if not os.path.exists(dir_path) and dir_path != project_name:  # Skip if it's the base dir
            os.makedirs(dir_path)
            print(f"Created directory: {dir_path}")
    
    # Create files
    for file_config in config.get('files', []):
        file_path = os.path.join(project_name, file_config['path'])
        content_type = file_config.get('content_type', 'text')
        
        # Ensure parent directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        if content_type == 'dynamic':
            # Skip for now, will be handled by copy_existing_files
            print(f"Note: {file_path} marked as dynamic - will need to be provided separately")
            continue
        elif content_type == 'binary':
            source = file_config.get('source')
            if source and os.path.exists(source):
                shutil.copy2(source, file_path)
                print(f"Copied binary file: {source} -> {file_path}")
            else:
                # Create empty file as placeholder
                with open(file_path, 'wb') as f:
                    pass
                print(f"Created empty binary file placeholder: {file_path}")
        else:
            # Text content
            with open(file_path, 'w') as f:
                f.write(file_config.get('content', ''))
            print(f"Created file: {file_path}")
    
    print("\nProject structure created successfully!")

def copy_existing_files(config_file: str, base_dir: Optional[str] = None, **files) -> None:
    """
    Copy existing files into the project structure according to the configuration.
    
    Args:
        config_file (str): Path to the YAML configuration file.
        base_dir (Optional[str]): Override the base directory.
        **files: Keyword arguments with file paths for dynamic content files.
    """
    # Load configuration
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    # Get project name from config or override
    project_name = base_dir or config.get('project_name', 'new_project')
    
    # Track which files we need to copy
    dynamic_files = {}
    
    # Find all dynamic files in config
    for file_config in config.get('files', []):
        if file_config.get('content_type') == 'dynamic':
            file_name = os.path.basename(file_config['path'])
            dynamic_files[file_name] = os.path.join(project_name, file_config['path'])
    
    # Copy provided files to their respective destinations
    copied_files = []
    for file_name, source_path in files.items():
        if file_name in dynamic_files and source_path and os.path.exists(source_path):
            destination = dynamic_files[file_name]
            shutil.copy2(source_path, destination)
            print(f"Copied {source_path} to {destination}")
            copied_files.append(file_name)
    
    # Report missing files
    missing_files = set(dynamic_files.keys()) - set(copied_files)
    if missing_files:
        print("\nThe following dynamic files were not provided:")
        for file in missing_files:
            print(f"- {file}")
        print("You'll need to add these files manually.")

def main():
    parser = argparse.ArgumentParser(description="Create project structure from YAML configuration.")
    parser.add_argument("--config", default="project_config.yaml", help="YAML configuration file")
    parser.add_argument("--base_dir", help="Override the base directory specified in config")
    
    # Add arguments for dynamic files
    parser.add_argument("--app_py", help="Path to app.py file")
    parser.add_argument("--requirements_txt", help="Path to requirements.txt file")
    parser.add_argument("--readme_md", help="Path to README.md file")
    parser.add_argument("--gitignore", help="Path to .gitignore file")
    
    args = parser.parse_args()
    
    # Check if config file exists
    if not os.path.exists(args.config):
        print(f"Error: Configuration file '{args.config}' not found.")
        return
    
    # Create project structure
    create_project_from_config(args.config, args.base_dir)
    
    # Copy dynamic files
    dynamic_files = {
        'app.py': args.app_py,
        'requirements.txt': args.requirements_txt,
        'README.md': args.readme_md,
        '.gitignore': args.gitignore
    }
    
    # Filter out None values
    dynamic_files = {k: v for k, v in dynamic_files.items() if v is not None}
    
    if dynamic_files:
        copy_existing_files(args.config, args.base_dir, **dynamic_files)
    
    print("\nTo get started:")
    print("1. Add any missing dynamic files")
    print("2. Rename .env.example to .env and add your API keys")
    print("3. Run the app with: streamlit run app.py")

if __name__ == "__main__":
    main()