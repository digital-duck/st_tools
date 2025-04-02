# Basic usage with config
python create_project.py --config project_config.yaml

# Specify a different base directory
python create_project.py --config project_config.yaml --base_dir my_custom_app

# Provide paths to your existing files
python create_project.py --config project_config.yaml --app_py=/path/to/app.py --requirements_txt=/path/to/requirements.txt --readme_md=/path/to/README.md --gitignore=/path/to/.gitignore