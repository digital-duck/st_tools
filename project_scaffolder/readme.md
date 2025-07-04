# ================================
# Setup Instructions
# ================================

# 1. Save the scaffolder code as: project_scaffolder.py
# 2. Install dependencies: pip install click PyYAML
# 3. Make it executable: chmod +x project_scaffolder.py
# 4. Create symlink (optional): ln -s /path/to/project_scaffolder.py /usr/local/bin/scaffold

# ================================
# Usage Examples (Updated)
# ================================

# Convert text structure to YAML:
# python project_scaffolder.py text-to-yaml ai_learning_structure.txt --output structure.yaml --show

### scaffold text-to-yaml ai_learning_structure.txt  --output structure.yaml --show

# Convert YAML back to text:
# python project_scaffolder.py yaml-to-text structure.yaml --output structure.txt --show

### scaffold yaml-to-text structure.yaml  --output structure.txt --show

# Create project structure from text file:
# python project_scaffolder.py create ai_learning_structure.txt --target ./my_project


### scaffold create structure.txt --target ./project_1  
### wrong

### scaffold create structure.txt --target ./project_1_3
  

### scaffold create ai_learning_structure.txt --target ./project_1_1  



# Create project structure from YAML file:
# python project_scaffolder.py create structure.yaml --format yaml --target ./my_project

### scaffold create structure.yaml --format yaml --target ./project_2


# NEW: Create directly from YAML (simpler syntax):
# python project_scaffolder.py from-yaml structure.yaml --target ./my_project

# NEW: Quick create from YAML file:
# python project_scaffolder.py quick-yaml --file structure.yaml --target ./my_project

# Dry run to see what would be created:
# python project_scaffolder.py create ai_learning_structure.txt --dry-run
# python project_scaffolder.py from-yaml structure.yaml --dry-run

# Quick create from text content:
# python project_scaffolder.py quick-create --file ai_learning_structure.txt --target ./my_project

# View help:
# python project_scaffolder.py --help
# python project_scaffolder.py from-yaml --help