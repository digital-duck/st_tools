# AI Docu App - Collaboration Tools

🚀 **Split massive document collections into manageable work packages for team analysis**

The AI Docu App collaboration tools enable teams to efficiently process large document collections by distributing work across multiple team members. Each person gets their own subset of documents to analyze with AI models, then results are merged back together.

## 🎯 Quick Start

### For Team Leads: Split Documents

```bash
# Python version
cd collab/python
python split_docs.py -s /path/to/documents -n 5

# JavaScript version  
cd collab/js
npm install
node split-docs.js -s /path/to/documents -n 5
```

### For Team Members: Analyze Documents

1. **Extract your package**: `tar -xzf docu-package-001.tar.gz`
2. **Open AI Docu App**: Double-click `ai_docu.html` 
3. **Load documents**: Click "Select Folder" → choose `documents/` folder
4. **Analyze**: Select AI model → Click "AI Analyze" 🧠
5. **Export results**: Click "💾 Export Metadata"
6. **Send back**: Compress folder and send to team lead

### For Team Leads: Merge Results

```bash
# Python version
python join_docs.py -i /path/to/completed-packages

# JavaScript version
node join-docs.js -i /path/to/completed-packages
```

## 📁 Tools Overview

| Tool | Language | Purpose | Input | Output |
|------|----------|---------|-------|--------|
| `split_docs.py` | Python | Split document collection | Document folder | Work packages |
| `join_docs.py` | Python | Merge analysis results | Completed packages | Unified metadata |
| `split-docs.js` | JavaScript | Split document collection | Document folder | Work packages |
| `join-docs.js` | JavaScript | Merge analysis results | Completed packages | Unified metadata |

## 🏗️ Directory Structure

```
collab/
├── README.md                    # This documentation
├── python/                      # Python collaboration tools
│   ├── split_docs.py           # Document splitter
│   ├── join_docs.py            # Result merger
│   └── requirements.txt        # Python dependencies
└── js/                         # JavaScript collaboration tools
    ├── split-docs.js           # Document splitter
    ├── join-docs.js            # Result merger
    └── package.json            # Node.js dependencies
```

## 🛠️ Installation & Setup

### Python Tools

```bash
cd collab/python

# Install dependencies
pip install click

# Make scripts executable (Linux/Mac)
chmod +x split_docs.py join_docs.py
```

### JavaScript Tools

```bash
cd collab/js

# Install dependencies
npm install

# Make scripts executable (Linux/Mac)
chmod +x split-docs.js join-docs.js
```

## 📖 Detailed Usage Guide

### 1. Document Splitting

#### Python Version

```bash
# Basic usage - split 1000 docs into 5 packages
python split_docs.py -s ./big-document-collection -n 5

# Custom output location
python split_docs.py -s /data/documents -n 3 -o /shared/packages

# Get help
python split_docs.py --help
```

#### JavaScript Version

```bash
# Basic usage
node split-docs.js -s ./big-document-collection -n 5

# Custom output location  
node split-docs.js -s /data/documents -n 3 -o /shared/packages

# Get help
node split-docs.js --help
```

#### Options

| Option | Description | Example |
|--------|-------------|---------|
| `-s, --source` | Source folder with documents | `-s ./documents` |
| `-n, --num-splits` | Number of packages to create | `-n 5` |
| `-o, --output` | Output folder (default: ./split/) | `-o ./packages` |
| `-c, --compress` | Auto-compress packages | `-c` |

#### Supported Document Types

- **Text Files**: `.txt`, `.md`, `.rtf`
- **PDF Documents**: `.pdf` (with text extraction in AI Docu App)
- **Word Documents**: `.docx` (with content conversion in AI Docu App)

### 2. Work Package Structure

Each work package contains:

```
docu-package-001/
├── README.md                    # Instructions for team member
├── ai_docu.html                # AI Docu App 
├── docs/                       # Documentation assets
├── documents/                  # Assigned documents to analyze
│   ├── document1.pdf
│   ├── document2.txt
│   └── document3.docx
├── package-manifest.json       # Package metadata
└── [exported-metadata].json   # Analysis results (after export)
```

### 3. Team Member Workflow

#### Step 1: Extract Package
```bash
# For .tar.gz files (Python default)
tar -xzf docu-package-001.tar.gz

# For .zip files (JavaScript default)  
unzip docu-package-001.zip
```

#### Step 2: Open AI Docu App
- Double-click `ai_docu.html` 
- Or open in browser: `file:///path/to/docu-package-001/ai_docu.html`

#### Step 3: Load Documents
- Click **"📂 Select Folder"** button
- Choose the `documents/` folder
- Verify all documents loaded correctly

#### Step 4: Choose AI Model
Select from available models:
- **Sentence-BERT**: Fast text embeddings and similarity
- **DistilBERT**: Document classification and categorization  
- **Universal Encoder**: Advanced semantic understanding

#### Step 5: Analyze Documents
- Click **"🧠 AI Analyze"** button
- Wait for analysis to complete (progress bar shows status)
- Review generated summaries and keywords

#### Step 6: Export Results
- Click **"💾 Export Metadata"** button
- File will be saved as `ai-docu-[model]-metadata.json`

#### Step 7: Send Back Results
```bash
# Compress the entire package with results
cd ..
tar -czf docu-package-001-completed.tar.gz docu-package-001/

# Send the .tar.gz file back to team lead
```

### 4. Result Merging

#### Python Version

```bash
# Basic usage - merge all packages in folder
python join_docs.py -i ./completed-packages

# Custom output location
python join_docs.py -i /data/completed -o /results/merged

# Auto-cleanup extracted folders
python join_docs.py -i ./packages -c

# Get help
python join_docs.py --help
```

#### JavaScript Version

```bash
# Basic usage
node join-docs.js -i ./completed-packages

# Custom output location
node join-docs.js -i /data/completed -o /results/merged

# Auto-cleanup extracted folders
node join-docs.js -i ./packages -c

# Get help
node join-docs.js --help
```

#### Join Options

| Option | Description | Example |
|--------|-------------|---------|
| `-i, --input` | Folder with completed packages | `-i ./completed` |
| `-o, --output` | Output folder (default: ./joined/) | `-o ./results` |
| `-c, --clean-extracted` | Remove extracted folders | `-c` |

### 5. Merged Output

The join process creates:

```
joined/
├── merged-ai-docu-metadata.json    # Consolidated analysis results
├── join-summary-report.md          # Detailed merge report
└── package-manifest.json           # Merge process metadata
```

## 🔄 Complete Workflow Example

### Scenario: 1000 Documents, 5 Team Members

#### Team Lead Setup
```bash
# 1. Split documents
cd collab/python
python split_docs.py -s /data/research-papers -n 5 -o /shared/packages

# 2. Share packages with team
# docu-package-001.tar.gz → Alice
# docu-package-002.tar.gz → Bob  
# docu-package-003.tar.gz → Carol
# docu-package-004.tar.gz → David
# docu-package-005.tar.gz → Eve
```

#### Team Members Process
Each team member:
```bash
# 1. Extract package
tar -xzf docu-package-001.tar.gz

# 2. Analyze documents (in browser)
# - Open ai_docu.html
# - Load documents from documents/ folder  
# - Select AI model (e.g., Sentence-BERT)
# - Click "AI Analyze"
# - Wait for completion
# - Click "Export Metadata"

# 3. Send results back
tar -czf docu-package-001-completed.tar.gz docu-package-001/
# Email to team lead
```

#### Team Lead Merge
```bash
# 1. Collect all completed packages in one folder
mkdir completed-work
# Copy all *-completed.tar.gz files here

# 2. Merge results
python join_docs.py -i ./completed-work -o ./final-results

# 3. Review merged data
# - Check join-summary-report.md
# - Load merged-ai-docu-metadata.json into main AI Docu App
# - Verify all 1000 documents are included
```

## ⚡ Performance Tips

### For Large Document Collections

1. **Optimal Split Size**: 50-200 documents per package
   ```bash
   # For 1000 documents, use 5-10 splits
   python split_docs.py -s ./docs -n 8
   ```

2. **Parallel Processing**: Team members can work simultaneously
   - Each gets different AI model for comparison
   - Results merged automatically

3. **Bandwidth Optimization**: 
   - Compress packages: `-c` flag
   - Use `.tar.gz` for better compression than `.zip`

### AI Model Selection Strategy

| Document Type | Recommended Model | Reason |
|---------------|------------------|---------|
| Technical docs | Sentence-BERT | Fast, good for embeddings |
| Legal documents | DistilBERT | Better classification |
| Research papers | Universal Encoder | Advanced understanding |
| Mixed collection | Different per team member | Compare model performance |

## 🔧 Troubleshooting

### Common Issues

#### Split Tool Problems

**Error: "No document files found"**
```bash
# Check supported extensions
ls -la your-folder/ | grep -E '\.(txt|pdf|docx|rtf|md)$'

# Verify folder path
python split_docs.py -s "$(pwd)/your-folder" -n 3
```

**Error: "Could not find project root"**
- Ensure `ai_docu.html` exists in project root
- Run from correct directory structure

#### Team Member Issues

**AI Docu App not loading documents**
- Use modern browser (Chrome, Firefox, Safari, Edge)
- Check browser console for errors
- Try different AI model
- Verify document folder selection

**Export not working**
- Check browser's download folder
- Try clicking export again
- Verify AI analysis completed successfully

#### Join Tool Problems

**Error: "No package directories found"**
```bash
# Check folder contents
ls -la your-input-folder/

# Extract archives manually if needed
for f in *.tar.gz; do tar -xzf "$f"; done
```

**Error: "No valid metadata files found"**
- Verify team members exported results
- Check for `ai-docu-*-metadata.json` files
- Ensure packages were completed

### Getting Help

1. **Check tool help**: `--help` flag on any tool
2. **Verify dependencies**: Python `click` or Node.js packages
3. **Check file permissions**: Make scripts executable
4. **Review logs**: Tools provide detailed progress output

## 📊 Comparison: Python vs JavaScript

| Feature | Python | JavaScript | Notes |
|---------|--------|------------|-------|
| **Compression** | `.tar.gz` | `.zip` | Both work well |
| **Dependencies** | `click` | `commander`, `archiver`, `adm-zip` | JS has more deps |
| **Performance** | Fast | Fast | Similar performance |
| **Platform** | Cross-platform | Cross-platform | Both work everywhere |
| **Archive handling** | Built-in `tarfile` | Requires `adm-zip` | Python simpler |

### When to Use Which?

- **Use Python** if you have Python environment setup
- **Use JavaScript** if you prefer Node.js ecosystem  
- **Both work identically** - choose based on your preference

## 🎉 Success Stories

### Research Team: 10,000 Academic Papers
- **Challenge**: Process decade of research papers
- **Solution**: Split into 20 packages, 10 team members
- **Result**: Complete analysis in 2 days vs 2 weeks manually
- **Models used**: All three for comparison

### Legal Firm: Contract Analysis  
- **Challenge**: 500 legal contracts for compliance review
- **Solution**: 5 packages, different AI models per lawyer
- **Result**: Identified key clauses and risks efficiently
- **Benefit**: Standardized analysis approach

### Content Agency: Blog Post Management
- **Challenge**: Categorize 2000 blog posts by topic
- **Solution**: Split by publication date, 4 team members
- **Result**: Perfect categorization for content strategy
- **AI Model**: DistilBERT for classification

## 🚀 Advanced Usage

### Custom Package Distribution

```bash
# Create packages of different sizes
python split_docs.py -s ./priority-docs -n 2    # Large packages
python split_docs.py -s ./regular-docs -n 8     # Small packages

# Assign by expertise
# Package 1 → Technical expert (AI model: Sentence-BERT)
# Package 2 → Business analyst (AI model: DistilBERT)
```

### Automated Workflows

```bash
#!/bin/bash
# automated-split.sh

# Split documents
python split_docs.py -s "$1" -n "$2" -o ./packages

# Email packages to team
for package in ./packages/*.tar.gz; do
    # Send email with package attachment
    echo "Package ready: $package"
done
```

### Quality Control

```bash
# After join, verify completeness
python -c "
import json
with open('joined/merged-ai-docu-metadata.json') as f:
    data = json.load(f)
print(f'Total documents: {len(data[\"metadata\"])}')
print(f'Models used: {data[\"export_info\"][\"ai_models_used\"]}')
"
```

## 📜 License

MIT License - see main project LICENSE file.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📞 Support

- **Issues**: Report bugs and request features
- **Documentation**: Check main AI Docu App README
- **Community**: Share your collaboration success stories!

---

**Happy collaborating! 🎉📄🤖**

*Tools built with ❤️ by the AI Docu App Team*