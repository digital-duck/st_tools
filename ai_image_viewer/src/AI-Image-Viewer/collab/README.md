# AI Image Viewer - Collaboration Tools

🤝 **Choose your preferred tools for splitting and merging collaborative image analysis work**

## 🎯 Overview

These tools enable seamless team collaboration on large image datasets with two implementation options:

### **🐍 Python Tools** (`python` folder)
1. **`split_work.py`** - Split images into work packages for distribution
2. **`join_work.py`** - Merge completed work packages back together

### **📦 JavaScript Tools** (`js` folder) 
1. **`split-work.js`** - Node.js version with modern ES modules
2. **`join-work.js`** - NPM-ready with colorful CLI output

## 🚀 Quick Start

### **🐍 Python Tools**

**Prerequisites:**
```bash
pip install click
```

**Split Work:**
```bash
cd python/
python3 split_work.py -s /path/to/images -n 5
```

**Join Work:**
```bash
cd python/
python3 join_work.py ../split/work-package-*
```

### **📦 JavaScript Tools**

**Prerequisites:**
```bash
cd js/
npm install
```

**Split Work:**
```bash
cd js/
node split-work.js -s /path/to/images -n 5
# OR using npx (after npm install -g)
npx split-work -s /path/to/images -n 5
```

**Join Work:**
```bash
cd js/
node join-work.js ../split/work-package-*
# OR using npx
npx join-work ../split/work-package-*
```

## 📦 Workflow Example

### 1. Project Lead: Split Dataset

**Using Python:**
```bash
cd python/
python3 split_work.py -s ./big-dataset -n 5
```

**Using JavaScript:**
```bash
cd js/
node split-work.js -s ./big-dataset -n 5
```

**Compress for sharing:**
```bash
cd split/
tar -czf work-package-001.tar.gz work-package-001/
tar -czf work-package-002.tar.gz work-package-002/
# ... repeat for each package
```

### 2. Team Members: Analyze Images
```bash
# Extract assigned package
tar -xzf work-package-001.tar.gz
cd work-package-001/

# Open any HTML file and analyze images
open ai_image_viewer_efficientnet.html

# Export metadata when complete
# (saves as: efficientnet-image-metadata.json)
```

### 3. Project Lead: Merge Results

**Using Python:**
```bash
cd python/
python3 join_work.py ../extracted-packages/work-package-*
```

**Using JavaScript:**
```bash
cd js/
node join-work.js ../extracted-packages/work-package-*
```

**Review results:**
```bash
open join/consolidated/ai_image_viewer.html
```

## 🔧 Tool Details

### **🐍 Python Tools**

#### split_work.py

**Purpose**: Split source images into work packages for team distribution

**Features**:
- ✅ Copies all 3 AI viewer HTML files to each package
- ✅ Evenly distributes images across packages  
- ✅ Creates package manifests with instructions
- ✅ Includes docs folder for screenshots
- ✅ Handles duplicate detection and naming

**Usage**:
```bash
cd python/
python3 split_work.py [OPTIONS]

Options:
  -s, --source DIRECTORY    Source folder containing images [required]
  -n, --num-splits INTEGER  Number of work packages to create [required]  
  -o, --output PATH         Output folder (default: ./split/)
  --help                    Show help message
```

### **📦 JavaScript Tools**

#### split-work.js

**Purpose**: Node.js version of the work splitter with modern features

**Features**:
- ✅ ES modules and modern JavaScript syntax
- ✅ Colorful CLI output with chalk
- ✅ Same functionality as Python version
- ✅ NPM package ready
- ✅ Cross-platform file handling

**Usage**:
```bash
cd js/
node split-work.js [OPTIONS]

Options:
  -s, --source <directory>    Source folder containing images [required]
  -n, --num-splits <number>   Number of work packages to create [required]  
  -o, --output <directory>    Output folder (default: ./split/)
  --help                      Show help message
```

## 📁 Folder Structure

Both tools create identical output structure:

```
split/                          # Split packages output
├── work-package-001/
│   ├── ai_image_viewer.html
│   ├── ai_image_viewer_efficientnet.html
│   ├── ai_image_viewer_mediapipe.html
│   ├── docs/
│   ├── images/ (subset 1)
│   └── package-manifest.json
├── work-package-002/
│   └── ... (subset 2)
└── work-package-003/
    └── ... (subset 3)
```

```
join/consolidated/              # Merged results output
├── ai_image_viewer.html
├── ai_image_viewer_efficientnet.html  
├── ai_image_viewer_mediapipe.html
├── docs/
├── images/ (all merged)
├── consolidated-metadata.json
└── consolidation-report.txt
```

## ⚖️ **Python vs JavaScript: Which to Choose?**

| Feature | 🐍 **Python** | 📦 **JavaScript** |
|---------|-------------|------------------|
| **Setup** | `pip install click` | `npm install` |
| **Runtime** | Python 3.6+ | Node.js 18+ |
| **Dependencies** | Minimal (1 package) | Modern (4 packages) |
| **Output** | Clean, functional | Colorful, modern |
| **Integration** | Great for data science | Great for web workflows |
| **Platform** | Cross-platform | Cross-platform |
| **Performance** | Good | Good |

**Choose Python if:**
- You're already working in Python environments
- You prefer minimal dependencies
- Your team uses data science tools

**Choose JavaScript if:**
- You're working with Node.js projects
- You want colorful, modern CLI experience
- Your team uses NPM/JavaScript tooling

## 🎯 Use Cases

### **Research Teams**
- Split large datasets across multiple researchers
- Each researcher analyzes their subset with preferred AI model
- Merge results for comprehensive analysis

### **Commercial Projects**
- Photographers organizing client shoots
- Content teams analyzing visual assets
- Quality control on large image collections

### **Educational Settings**
- Students working on computer vision projects
- Class assignments on image classification
- Collaborative research projects

## 📊 Metadata Handling

The tools automatically detect and merge these metadata formats:
- `ai-image-metadata.json` (MobileNet baseline)
- `efficientnet-image-metadata.json` (EfficientNet)
- `mediapipe-image-metadata.json` (MediaPipe)
- `*-analysis.json` (custom exports)
- `metadata.json` (generic)

## 🔍 Advanced Features

### Package Validation
- Checks for required folder structure
- Validates image file types
- Warns about missing components

### Duplicate Handling
- Renames duplicate image files automatically
- Preserves original analysis metadata
- Maintains package traceability

### Comprehensive Reporting
- Package-by-package statistics
- Model usage tracking
- Analysis coverage metrics

## 🐛 Troubleshooting

### Common Issues

**"No valid packages found"**
- Ensure packages have `images/` subfolder
- Check folder permissions
- Verify package wasn't corrupted

**"No metadata files found"**
- Normal if team hasn't completed analysis yet
- Tool creates image-only package for distribution
- Import metadata later after analysis

**"DateTime error"**
- Ensure Python 3.6+ is being used
- Install required dependencies: `pip install click`

### Debug Mode
```bash
# Run with verbose output
python3 split_work.py -s ./images -n 3 --help

# Check package contents
ls -la split/work-package-001/
cat split/work-package-001/package-manifest.json
```

## 📝 Requirements

- Python 3.6+
- Click library: `pip install click`
- Compatible with Windows, macOS, Linux

---

**Ready to collaborate? Start splitting your datasets today!** 🚀