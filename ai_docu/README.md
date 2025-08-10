# AI Docu App

📄 **A powerful, portable web-based document viewer with AI-powered text analysis and semantic search**

✨ **Ultra-Portable**: Single HTML file application - no installation, no server, no dependencies. Just zip and share!

![AI Docu App](docs/ai_docu_screenshot.png)

## 🎯 **AI-Powered Document Management**

**One app, three powerful AI models for text processing!** Choose your model with a simple dropdown:

| Model | Best For | Icon |
|-------|----------|------|
| **Sentence-BERT** 🧠 | Fast text embeddings and similarity | 🧠 |
| **DistilBERT** 🎯 | Document classification and categorization | 🎯 |
| **Universal Encoder** 🚀 | Advanced semantic understanding | 🚀 |

**Single File:** `ai_docu.html` - Contains all three models with dynamic loading!

## ✨ Features

### 🤖 AI Text Processing
- **Document Classification** - Auto-categorizes documents by type and content
- **Keyword Extraction** - Identifies key terms and topics with confidence scores
- **Text Summarization** - Generates intelligent document summaries
- **Semantic Search** - Find documents using natural language queries
- **Content Analysis** - Deep understanding of document meaning and context

### 📄 Multi-Format Support
- **Text Files** - TXT, RTF, MD files
- **PDF Documents** - Native PDF viewing and text extraction
- **Word Documents** - DOCX file support with content conversion
- **Rich Text** - RTF format support
- **Markdown** - MD file rendering and analysis

### 🔍 Smart Search Capabilities
Search documents by content using natural language:
- `"contracts from 2023"` - finds legal documents from specific timeframe
- `"meeting notes about project"` - locates project-related meeting records
- `"financial reports"` - discovers financial documentation
- `"research papers on AI"` - identifies academic and research content
- `"technical documentation"` - finds technical specs and manuals

**Search Quality:**
- **Sentence-BERT** 🧠: Fast embedding-based similarity search
- **DistilBERT** 🎯: Category-aware document matching
- **Universal Encoder** 🚀: Advanced semantic understanding with context

### 📁 File Management
- **Multi-format Support** - TXT, PDF, DOCX, RTF, MD
- **Bulk Operations** - Select individual files or entire folders
- **Drag & Drop** - Drop documents directly onto the viewer
- **Metadata Export/Import** - Save and load AI analysis results
- **Editable Summaries** - Click to edit document summaries

### 🎨 User Interface
- **Document Grid Layout** - 1-4 documents per row
- **File Type Indicators** - Visual badges for different document types
- **Real-time Progress** - Watch AI processing with live progress bars
- **Search Suggestions** - Common search queries for quick access
- **Mobile Optimized** - Works seamlessly on phones and tablets
- **Document Viewer** - Double-click to read full document content

## 🚀 Getting Started

### **Open the AI Docu App**

```bash
open ai_docu.html
```

**That's it!** One file, all AI models included.

### **Basic Usage**

1. **Load Your Documents**
   - Click "📁 Select Documents" for individual files
   - Click "📂 Select Folder" to load an entire directory
   - Or drag and drop documents directly onto the viewer

2. **Choose Your AI Model**
   - Select from dropdown: Sentence-BERT 🧠, DistilBERT 🎯, or Universal Encoder 🚀
   - Model loads automatically with progress indicator
   - Switch models anytime to compare results

3. **Analyze with AI**
   - Click the **🧠 AI Analyze** button 
   - Wait for analysis to complete (shows progress with model-specific messaging)
   - AI keywords, summaries, and classifications will appear on each document

4. **Search Your Collection**
   - Click "🔍 AI Search" to open the search modal
   - Type natural language descriptions
   - Click search suggestions for quick queries
   - Results ranked by relevance (quality varies by selected model)

5. **Export Results**
   - Click "💾 Export Metadata" to save analysis results
   - Filename automatically includes model name: `ai-docu-sentencebert-metadata.json`

## 📦 **Portability & Collaboration**

### **Share Your Work Instantly**
The beauty of single-file HTML applications - just compress and share!

**Create Portable Package:**
```bash
# Using ZIP (cross-platform)
zip -r my-document-analysis.zip ai_docu.html documents/ *.json

# Using TAR (Mac/Linux preferred)
tar -czf my-document-analysis.tar.gz ai_docu.html documents/ *.json
```

**Uncompress and Use:**
```bash
# Unzip package
unzip my-document-analysis.zip
# OR extract tar
tar -xzf my-document-analysis.tar.gz

# Open HTML file - no installation needed!
open ai_docu.html  # Mac
xdg-open ai_docu.html  # Linux
# Or double-click the HTML file on Windows
```

### **Team Collaboration Workflows**

**1. Distribute Document Collections for Analysis**
```bash
# Project lead creates initial package
tar -czf document-analysis-project.tar.gz ai_docu.html documents/
# Share with team members via email, cloud, or USB drive
```

**2. Collaborative Document Processing**
- Each team member extracts the package locally
- Everyone analyzes their assigned document subset using their preferred AI model
- Export individual metadata JSON files (model-specific naming)
- Project lead merges all JSON results

**3. Team Analysis Process**
```bash
# Team member workflow:
tar -xzf document-analysis-project.tar.gz  # Extract package
open ai_docu.html                          # Open document analyzer
# Choose AI model (Sentence-BERT/DistilBERT/Universal Encoder)
# Analyze assigned documents (batch 1-50, 51-100, etc.)
# Export metadata as "ai-docu-[model]-metadata.json"
# Share JSON file back to project lead

# Project lead merges results:
# Import each member's JSON into unified viewer
# Combine all analysis results from different models
# Create final consolidated document database
```

### **🤖 Automated Collaboration Tools**

For large document collections and team projects, choose your preferred automation tools:

#### **🐍 Python Tools** (`python3` / `pip`)

```bash
# Setup and split large document collections for team distribution
cd collab/python/
pip install click
python3 split_docs.py -s /path/to/big-document-collection -n 5

# Team members analyze their assigned packages
# Each gets the AI Docu App + subset of documents

# Merge completed work back together
python3 join_docs.py ../split/work-package-*
```

#### **📦 JavaScript Tools** (`npx` / `npm`)

Modern Node.js tools for web development workflows:

```bash
# Setup and split large document collections for team distribution  
cd collab/js/
npm install
node split-docs.js -s /path/to/big-document-collection -n 5

# Team members analyze their assigned packages
# Each gets the AI Docu App + subset of documents

# Merge completed work back together
node join-docs.js ../split/work-package-*
```

**📖 See [collab/README.md](collab/README.md) for complete collaboration workflow documentation.**

## 🔧 Technical Details

### AI Model Comparison

| Feature | Sentence-BERT 🧠 | DistilBERT 🎯 | Universal Encoder 🚀 |
|---------|------------------|----------------|----------------------|
| **Framework** | TensorFlow.js | TensorFlow.js | TensorFlow.js |
| **Model Size** | 15MB | 20MB | 25MB |
| **Load Time** | Fast (2-3s) | Medium (3-4s) | Slower (4-6s) |
| **Best For** | Text similarity | Classification | Semantic search |
| **Memory Usage** | Low | Medium | Higher |

### Supported Document Types

- **Plain Text** (.txt, .rtf) - Direct text processing
- **Markdown** (.md) - Formatted text with structure
- **PDF Documents** (.pdf) - Text extraction and analysis
- **Word Documents** (.docx) - Content conversion and processing

### Performance
- **Client-side Processing** - All AI runs locally in your browser
- **No Server Required** - Works completely offline after initial load
- **Automatic Caching** - Models and results cached for fast re-use
- **Progressive Loading** - UI remains responsive during analysis

### Browser Support
- **Modern Browsers** - Chrome 80+, Firefox 75+, Safari 13+, Edge 80+
- **File API Support** - For local document processing
- **Fallback Mode** - Basic text search if AI models fail to load

## 📊 Use Cases

- **Legal Document Management** - Contract analysis and legal research
- **Academic Research** - Paper organization and content analysis
- **Business Documentation** - Report categorization and search
- **Technical Documentation** - API docs, manuals, specifications
- **Personal Knowledge Base** - Note organization and retrieval
- **Content Management** - Blog posts, articles, and content analysis

## 💾 Data Management

### Export Metadata
- Click "💾 Export Metadata" to save all AI analysis results
- Exports to `ai-docu-[model]-metadata.json`
- Includes summaries, keywords, classifications, and timestamps
- Compatible across sessions and devices

### Import Metadata  
- Click "📂 Import Metadata" to load previous analysis results
- Automatically matches documents by filename
- Restores summaries, keywords, and AI analysis data
- Useful for sharing analysis results with team members

## 🛠️ Development

### Project Structure
```
ai_docu/
├── ai_docu.html                        # 🎯 Main AI Docu App
├── README.md                          # Main documentation
├── LICENSE                           # MIT License
├── docs/                             # Documentation assets
│   ├── ai_docu_screenshot.png        # App screenshot
│   └── architecture.md              # Technical architecture
├── images/                           # Sample documents for testing
│   ├── sample.txt                   # Plain text sample
│   ├── sample.pdf                   # PDF sample
│   ├── sample.docx                  # Word document sample
│   └── sample.md                    # Markdown sample
└── collab/                          # Collaboration tools
    ├── README.md                    # Collaboration documentation
    ├── python/                      # Python-based tools
    │   ├── split_docs.py           # Split document collections
    │   └── join_docs.py            # Merge document analysis
    └── js/                         # JavaScript tools
        ├── package.json            # Node.js dependencies
        ├── split-docs.js           # Split document collections
        └── join-docs.js            # Merge document analysis
```

### Architecture
- **Single HTML File** - Entire application in one file for portability
- **Vanilla JavaScript** - No frameworks, pure JS for maximum compatibility
- **Progressive Enhancement** - Graceful degradation with fallback modes
- **Event-driven** - Responsive UI with async AI processing
- **Model Abstraction** - Easy to swap between different AI models

### Model Selection Guide
- **Choose Sentence-BERT** 🧠 for:
  - Fast document similarity and embedding
  - Quick text processing requirements
  - Basic document organization needs
  
- **Choose DistilBERT** 🎯 for:
  - Document classification and categorization
  - Content type identification
  - Most general-purpose document analysis
  
- **Choose Universal Encoder** 🚀 for:
  - Advanced semantic search requirements
  - Complex document understanding
  - Research or professional applications

## 🔒 Privacy & Security

- **Local Processing** - All AI analysis happens in your browser
- **No Data Transmission** - Documents never leave your device
- **No Tracking** - No analytics or external connections (except CDN for models)
- **Offline Capable** - Works without internet after initial model download

## 🤝 Contributing

This ultra-portable, self-contained application is perfect for:
- Adding new AI models for text processing
- Implementing additional document formats  
- Improving the user interface and search features
- Adding export formats and integrations
- Creating mobile-optimized versions
- Educational use in NLP and document processing courses
- Research collaboration without infrastructure setup

## 📝 License

MIT License - feel free to use, modify, and distribute.

## 🙋 Support

For questions or issues:
1. Check the browser console for error messages
2. Ensure your browser supports modern JavaScript features
3. Try the fallback text search if AI models fail to load
4. Clear browser cache and reload if models seem corrupted

---

**Built with ❤️ by Claude-Code and powered by TensorFlow.js**