import os
import shutil
import argparse

def create_project_structure(base_dir="st_rag_demo"):
    """
    Create the directory structure for the st_rag_demo project.
    
    Args:
        base_dir (str): The base directory for the project. Default is "st_rag_demo".
    """
    # Create base directory if it doesn't exist
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
        print(f"Created base directory: {base_dir}")
    
    # Define the structure
    directories = [
        "examples",
        "examples/csv",
        "examples/pdf",
        "examples/sqlite",
        "static",
        "static/screenshots",
    ]
    
    # Create directories
    for directory in directories:
        dir_path = os.path.join(base_dir, directory)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f"Created directory: {dir_path}")
    
    # Define the files to create
    files = {
        "README.md": "",  # This will be copied from existing files
        "requirements.txt": "",  # This will be copied from existing files
        "app.py": "",  # This will be copied from existing files
        ".gitignore": "",  # This will be copied from existing files
        ".env.example": "OPENAI_API_KEY=your_openai_api_key_here\n\n# AWS Bedrock Settings (Optional)\n# AWS_ACCESS_KEY_ID=your_aws_access_key_id\n# AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key\n# AWS_REGION=us-east-1\n\n# AWS Bedrock Guardrail Settings (Optional)\n# BEDROCK_GUARDRAIL_ID=your_guardrail_id\n# BEDROCK_GUARDRAIL_VERSION=LATEST",
        "LICENSE": "MIT License\n\nCopyright (c) 2023 Your Name\n\nPermission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the \"Software\"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.",
        "examples/csv/sample_data.csv": "id,name,age,city,sales\n1,John Smith,34,New York,1200\n2,Maria Garcia,29,Los Angeles,950\n3,Robert Johnson,45,Chicago,1450\n4,Sarah Lee,37,Houston,1100\n5,Michael Brown,52,Phoenix,1300\n6,Jennifer Davis,31,Philadelphia,1050\n7,David Miller,44,San Antonio,1250\n8,Lisa Wilson,39,San Diego,1150\n9,William Taylor,48,Dallas,1350\n10,Patricia Moore,33,San Jose,1000",
        "examples/sqlite/README.txt": "Place your SQLite database files (.db, .sqlite, .sqlite3) in this directory to test the application."
    }
    
    # Create files
    for file_path, content in files.items():
        full_path = os.path.join(base_dir, file_path)
        if not os.path.exists(full_path):
            with open(full_path, 'w') as f:
                f.write(content)
            print(f"Created file: {full_path}")
    
    print("\nProject structure created successfully!")
    print(f"\nTo get started:\n1. Copy your existing app.py, requirements.txt, README.md, and .gitignore files into the {base_dir} directory")
    print("2. Rename .env.example to .env and add your OpenAI API key")
    print("3. Run the app with: streamlit run app.py")

def copy_existing_files(base_dir="st_rag_demo", app_py=None, requirements_txt=None, readme_md=None, gitignore=None):
    """
    Copy existing files into the project structure.
    
    Args:
        base_dir (str): The base directory for the project.
        app_py (str): Path to the existing app.py file.
        requirements_txt (str): Path to the existing requirements.txt file.
        readme_md (str): Path to the existing README.md file.
        gitignore (str): Path to the existing .gitignore file.
    """
    files_to_copy = {
        app_py: os.path.join(base_dir, "app.py"),
        requirements_txt: os.path.join(base_dir, "requirements.txt"),
        readme_md: os.path.join(base_dir, "README.md"),
        gitignore: os.path.join(base_dir, ".gitignore")
    }
    
    for source, destination in files_to_copy.items():
        if source and os.path.exists(source):
            shutil.copy2(source, destination)
            print(f"Copied {source} to {destination}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create the st_rag_demo project structure.")
    parser.add_argument("--base_dir", default="st_rag_demo", help="Base directory for the project")
    parser.add_argument("--app_py", help="Path to existing app.py file")
    parser.add_argument("--requirements_txt", help="Path to existing requirements.txt file")
    parser.add_argument("--readme_md", help="Path to existing README.md file")
    parser.add_argument("--gitignore", help="Path to existing .gitignore file")
    
    args = parser.parse_args()
    
    # Create the project structure
    create_project_structure(args.base_dir)
    
    # Copy existing files if provided
    copy_existing_files(
        args.base_dir,
        args.app_py,
        args.requirements_txt,
        args.readme_md,
        args.gitignore
    )