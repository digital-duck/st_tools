import os
import shutil
import yaml
import click
from pathlib import Path
from typing import Dict, Any, Optional

@click.group()
def cli():
    """
    Project structure generator tool.
    
    This tool creates project directories and files based on a YAML configuration file.
    It's designed to quickly scaffold new projects with a predefined structure.
    """
    pass

@cli.command()
@click.option('--config', '-c', default='project_config.yaml', 
              type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
              help='Path to the YAML configuration file that defines the project structure.')
@click.option('--base-dir', '-b', 
              help='Override the base directory specified in the config file.')
@click.option('--app-py', type=click.Path(exists=True, file_okay=True),
              help='Path to existing app.py file to copy into the project.')
@click.option('--requirements-txt', type=click.Path(exists=True, file_okay=True),
              help='Path to existing requirements.txt file to copy into the project.')
@click.option('--readme-md', type=click.Path(exists=True, file_okay=True),
              help='Path to existing README.md file to copy into the project.')
@click.option('--gitignore', type=click.Path(exists=True, file_okay=True),
              help='Path to existing .gitignore file to copy into the project.')
@click.option('--force', '-f', is_flag=True, 
              help='Force overwrite existing files and directories.')
@click.option('--verbose', '-v', is_flag=True, 
              help='Enable verbose output for debugging.')
def create(config, base_dir, app_py, requirements_txt, readme_md, gitignore, force, verbose):
    """
    Create a new project structure based on a YAML configuration.
    
    This command reads a YAML file that defines directories and files to create,
    and builds the project structure accordingly. You can also provide paths to
    existing files to copy them into the new project.
    
    Example usage:
    
    \b
    # Create project using default config file
    python project_generator.py create
    
    \b
    # Use a specific config and override the base directory
    python project_generator.py create --config custom_config.yaml --base-dir my_project
    
    \b
    # Include existing files
    python project_generator.py create --app-py ./existing/app.py
    """
    # Load configuration
    click.echo(f"Reading configuration from {config}")
    with open(config, 'r') as f:
        config_data = yaml.safe_load(f)
    
    # Get project name from config or override
    project_name = base_dir or config_data.get('project_name', 'new_project')
    click.echo(f"Creating project structure for '{project_name}'")
    
    # Create base directory if it doesn't exist
    if not os.path.exists(project_name):
        os.makedirs(project_name)
        if verbose:
            click.echo(f"Created base directory: {project_name}")
    elif not force:
        click.confirm(f"Directory '{project_name}' already exists. Continue?", abort=True)
    
    # Create directories
    with click.progressbar(config_data.get('directories', []), 
                          label='Creating directories',
                          item_show_func=lambda d: d['path'] if d else None) as dirs:
        for dir_config in dirs:
            dir_path = os.path.join(project_name, dir_config['path'])
            if not os.path.exists(dir_path) and dir_path != project_name:  # Skip if it's the base dir
                os.makedirs(dir_path)
                if verbose:
                    click.echo(f"Created directory: {dir_path}")
    
    # Create files
    with click.progressbar(config_data.get('files', []), 
                          label='Creating files',
                          item_show_func=lambda f: f['path'] if f else None) as files:
        for file_config in files:
            file_path = os.path.join(project_name, file_config['path'])
            content_type = file_config.get('content_type', 'text')
            
            # Ensure parent directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Skip if file exists and not forcing
            if os.path.exists(file_path) and not force:
                if verbose:
                    click.echo(f"Skipping existing file: {file_path}")
                continue
            
            if content_type == 'dynamic':
                # Skip for now, will be handled by copy_existing_files
                if verbose:
                    click.echo(f"Note: {file_path} marked as dynamic - will need to be provided separately")
                continue
            elif content_type == 'binary':
                source = file_config.get('source')
                if source and os.path.exists(source):
                    shutil.copy2(source, file_path)
                    if verbose:
                        click.echo(f"Copied binary file: {source} -> {file_path}")
                else:
                    # Create empty file as placeholder
                    with open(file_path, 'wb') as f:
                        pass
                    if verbose:
                        click.echo(f"Created empty binary file placeholder: {file_path}")
            else:
                # Text content
                with open(file_path, 'w') as f:
                    f.write(file_config.get('content', ''))
                if verbose:
                    click.echo(f"Created file: {file_path}")
    
    # Copy dynamic files
    dynamic_files = {
        'app.py': app_py,
        'requirements.txt': requirements_txt,
        'README.md': readme_md,
        '.gitignore': gitignore
    }
    
    # Filter out None values
    dynamic_files = {k: v for k, v in dynamic_files.items() if v is not None}
    
    if dynamic_files:
        click.echo("Copying provided dynamic files...")
        copy_existing_files(config_data, project_name, dynamic_files, force=force, verbose=verbose)
    
    click.secho("\n✅ Project structure created successfully!", fg="green", bold=True)
    
    # Check for missing dynamic files
    missing_dynamic_files = get_missing_dynamic_files(config_data, dynamic_files)
    if missing_dynamic_files:
        click.secho("\nℹ️ The following dynamic files were not provided:", fg="yellow")
        for file in missing_dynamic_files:
            click.echo(f"  - {file}")
        click.echo("You'll need to add these files manually.")
    
    click.echo("\nTo get started:")
    click.echo("1. Add any missing dynamic files")
    click.echo("2. Rename .env.example to .env and add your API keys")
    click.echo("3. Run the app with: streamlit run app.py")

@cli.command()
@click.option('--output', '-o', default='project_config.yaml',
              help='Output file for the template configuration.')
def init(output):
    """
    Generate a starter YAML configuration file.
    
    This creates a basic configuration template that you can customize
    for your project needs.
    
    Example usage:
    
    \b
    # Create a default config file
    python project_generator.py init
    
    \b
    # Specify an output file
    python project_generator.py init --output custom_config.yaml
    """
    template = """# Project Structure Configuration
project_name: my_project
directories:
  - path: ""
    description: "Project root directory"
  - path: "docs"
    description: "Documentation files"
  - path: "src"
    description: "Source code"
  - path: "tests"
    description: "Test files"

files:
  - path: "README.md"
    description: "Project documentation"
    content: |
      # My Project
      
      Project description goes here.
      
      ## Installation
      
      ```
      pip install -r requirements.txt
      ```
      
      ## Usage
      
      ```
      python src/main.py
      ```
    
  - path: "requirements.txt"
    description: "Project dependencies"
    content_type: "dynamic"
    
  - path: ".env.example"
    description: "Example environment variables"
    content: |
      # API Keys
      API_KEY=your_api_key_here
      
  - path: "src/main.py"
    description: "Main application file"
    content: |
      def main():
          print("Hello, world!")
          
      if __name__ == "__main__":
          main()
"""
    
    if os.path.exists(output) and not click.confirm(f"File '{output}' already exists. Overwrite?"):
        click.echo("Operation cancelled.")
        return
    
    with open(output, 'w') as f:
        f.write(template)
    
    click.secho(f"✅ Configuration template created: {output}", fg="green")
    click.echo("Customize this file to define your project structure.")

def copy_existing_files(config_data, project_name, dynamic_files, force=False, verbose=False):
    """Copy provided dynamic files into the project structure."""
    # Find all dynamic files in config
    config_dynamic_files = {}
    for file_config in config_data.get('files', []):
        if file_config.get('content_type') == 'dynamic':
            file_name = os.path.basename(file_config['path'])
            config_dynamic_files[file_name] = os.path.join(project_name, file_config['path'])
    
    # Copy provided files to their respective destinations
    copied_files = []
    for file_name, source_path in dynamic_files.items():
        if file_name in config_dynamic_files:
            destination = config_dynamic_files[file_name]
            if os.path.exists(destination) and not force:
                if verbose:
                    click.echo(f"Skipping existing file: {destination}")
                continue
                
            shutil.copy2(source_path, destination)
            if verbose:
                click.echo(f"Copied {source_path} to {destination}")
            copied_files.append(file_name)
        else:
            click.echo(f"Warning: {file_name} not found in config's dynamic files")

def get_missing_dynamic_files(config_data, provided_files):
    """Get a list of dynamic files that weren't provided."""
    dynamic_files = []
    for file_config in config_data.get('files', []):
        if file_config.get('content_type') == 'dynamic':
            file_name = os.path.basename(file_config['path'])
            dynamic_files.append(file_name)
    
    return set(dynamic_files) - set(provided_files.keys())

@cli.command()
@click.option('--config', '-c', default='project_config.yaml', 
              type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
              help='Path to the YAML configuration file to analyze.')
def analyze(config):
    """
    Analyze a config file and show summary information.
    
    This command displays a summary of the directories and files
    defined in the configuration, highlighting dynamic files that
    would need to be provided separately.
    
    Example usage:
    
    \b
    # Analyze the default config file
    python project_generator.py analyze
    
    \b
    # Analyze a specific config file
    python project_generator.py analyze --config custom_config.yaml
    """
    # Load configuration
    click.echo(f"Analyzing configuration from {config}")
    with open(config, 'r') as f:
        config_data = yaml.safe_load(f)
    
    project_name = config_data.get('project_name', 'new_project')
    click.echo(f"\nProject Name: {project_name}")
    
    # Directory summary
    directories = config_data.get('directories', [])
    click.echo(f"\nDirectories: {len(directories)}")
    for idx, dir_config in enumerate(directories, 1):
        path = dir_config['path']
        desc = dir_config.get('description', 'No description')
        click.echo(f"  {idx}. {path or './'}: {desc}")
    
    # Files summary
    files = config_data.get('files', [])
    click.echo(f"\nFiles: {len(files)}")
    
    # Count by content type
    content_types = {}
    for file_config in files:
        content_type = file_config.get('content_type', 'text')
        content_types[content_type] = content_types.get(content_type, 0) + 1
    
    for content_type, count in content_types.items():
        click.echo(f"  {content_type}: {count}")
    
    # List dynamic files
    dynamic_files = [f['path'] for f in files if f.get('content_type') == 'dynamic']
    if dynamic_files:
        click.echo("\nDynamic files (must be provided separately):")
        for file_path in dynamic_files:
            click.echo(f"  - {file_path}")
    
    click.echo("\nConfiguration analysis complete!")

if __name__ == '__main__':
    cli()