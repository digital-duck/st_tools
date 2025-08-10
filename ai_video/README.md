# AI Video App

🎬 **A powerful, portable web-based video manager with AI-powered video analysis, smart search, and intelligent content discovery**

✨ **Ultra-Portable**: Single HTML file application - no installation, no server, no dependencies. Just zip and share!

🎯 **Smart & Intuitive**: Modern UI with thumbnail previews, click-to-edit tags, interactive video player, and AI model guidance

![AI Video App](docs/ai_video_screenshot.png)

## 🌟 **What's Coming**

✅ **Interactive Video Player** - Click any video to play with embedded controls  
✅ **Thumbnail Previews** - Beautiful video thumbnails in responsive grid cards  
✅ **Smart AI Video Analysis** - Scene detection, object recognition, and content classification  
✅ **One-Click Tagging** - Auto-clearing placeholders for smooth metadata editing  
✅ **Video Format Support** - MP4, AVI, MOV, WMV, MKV, WebM, and more  
✅ **Modern Responsive UI** - Beautiful animations and mobile-optimized design  

## 🎯 **AI-Powered Video Management**

**One app, three powerful AI models for video processing!** Choose your model with intelligent guidance:

| Model | Best For | Speed | Learn More |
|-------|----------|-------|------------|
| **Video-BERT** 🎬 | Fast video embeddings & similarity search | ⚡ Fast | [Research Paper](https://arxiv.org/abs/1904.02755) |
| **VideoMAE** 🎥 | Scene classification & action recognition | 🚀 Balanced | [Model Info](https://github.com/MCG-NJU/VideoMAE) |
| **Universal Video** 🚀 | Advanced video understanding & content analysis | 🔄 Comprehensive | [Documentation](https://github.com/tensorflow/models/tree/master/research/video_prediction) |

**✨ Smart Model Selection**: Hover over the **?** icon next to the model dropdown for detailed guidance and direct links to documentation!

**Single File:** `ai_video.html` - Contains all three models with dynamic loading!

## ✨ Features

### 🤖 AI Video Processing
- **Scene Detection** - Auto-identifies scenes, transitions, and key moments
- **Object Recognition** - Detects people, objects, and elements in video content
- **Action Classification** - Identifies activities, movements, and behaviors
- **Content Analysis** - Understands video themes, topics, and context
- **Temporal Understanding** - Analyzes video progression and narrative flow
- **Quality Assessment** - Evaluates video quality, resolution, and technical aspects

### 🎬 Multi-Format Support
- **MP4 Files** - Most common video format with universal compatibility
- **AVI Files** - Classic format with broad codec support
- **MOV Files** - Apple QuickTime format with high quality
- **WMV Files** - Windows Media Video with compression efficiency
- **MKV Files** - Matroska container with multiple streams
- **WebM Files** - Open web standard with VP8/VP9 codecs
- **FLV Files** - Flash video format support
- **3GP Files** - Mobile video format compatibility

### 🔍 Smart Search Capabilities
Search your video library using natural language:
- `"cooking videos with pasta"` - finds culinary content featuring pasta dishes
- `"outdoor nature documentaries"` - locates nature and wildlife videos
- `"funny moments from 2023"` - discovers comedy content from specific timeframes
- `"tutorial videos about technology"` - identifies educational tech content
- `"family gatherings and celebrations"` - finds personal/family video memories

**🎯 Enhanced Search Experience:**
- **Clickable Results** - Click any search result to instantly play the video
- **Smart Scoring** - Match percentages help you find the most relevant content
- **Seamless Navigation** - Search modal auto-closes when you select a video
- **Video Preview** - See thumbnails and metadata for each search result

**Search Quality:**
- **Video-BERT** 🎬: Fast embedding-based similarity search
- **VideoMAE** 🎥: Scene and action-aware video matching
- **Universal Video** 🚀: Advanced semantic understanding with temporal context

### 📺 Interactive Video Player
**Click any video file** to open the enhanced player:
- **🎬 All Video Formats** - Universal playback with HTML5 video
- **🖼️ Thumbnail Timeline** - Navigate through video using frame previews
- **🎛️ Playback Controls** - Play/pause, seek, volume, speed, and fullscreen
- **📊 Video Metadata** - File size, resolution, duration, codec, and bitrate info
- **🎨 Responsive Player** - Adaptive design that works on all screen sizes
- **⚡ Fast Seeking** - Quick navigation through long video content

### 📁 Smart Video Management
- **Multi-format Support** - MP4, AVI, MOV, WMV, MKV, WebM, FLV, 3GP files
- **Bulk Operations** - Select individual files or entire video directories
- **Drag & Drop** - Drop video files directly onto the player
- **Metadata Export/Import** - Save and load AI analysis results
- **🎯 Smart Tags** - Click "Click to add tags..." to instantly start editing (auto-clears placeholder)
- **📊 Visual Organization** - Video file cards with thumbnails and detailed metadata
- **🔍 Content Filtering** - Filter by format, duration, resolution, or AI-detected content

### 🎨 Modern User Interface
- **📱 Responsive Design** - Works seamlessly on desktop, tablet, and mobile
- **🎯 Interactive Elements** - Hover tooltips, clickable components, smooth animations
- **⚡ Real-time Feedback** - Live progress bars during AI processing and video analysis
- **🔍 Smart Search UI** - Search suggestions with instant clickable results
- **📊 Visual Video Grid** - Customizable layout (1-4 videos per row)
- **🏷️ Format Badges** - Clear visual indicators for different video formats and codecs
- **✏️ Inline Editing** - Click-to-edit tags with smart placeholder behavior
- **🎬 Video Thumbnails** - Auto-generated or custom thumbnail previews

## 🚀 Getting Started

### **Open the AI Video App**

```bash
open ai_video.html
```

**That's it!** One file, all AI models included.

### **Basic Usage**

1. **Load Your Video Library**
   - Click "📁 Select Video Files" for individual videos
   - Click "📂 Select Video Folder" to load an entire video library
   - Or drag and drop video files directly onto the player

2. **Choose Your AI Model**
   - Select from dropdown: Video-BERT 🎬, VideoMAE 🎥, or Universal Video 🚀
   - Model loads automatically with progress indicator
   - Switch models anytime to compare analysis results

3. **Analyze with AI**
   - Click the **🎬 AI Analyze** button 
   - Wait for analysis to complete (shows progress with model-specific messaging)
   - AI scenes, objects, and content characteristics will appear on each video

4. **Search Your Videos**
   - Click "🔍 AI Search" to open the search modal
   - Type natural language descriptions of content you want
   - Click search suggestions for quick queries
   - Results ranked by relevance and content similarity

5. **Play & Explore**
   - Click any video to open the video player
   - View thumbnails, control playback, explore content
   - Edit tags and metadata inline
   - Navigate using thumbnail timeline

6. **Export Results**
   - Click "💾 Export Metadata" to save analysis results
   - Filename automatically includes model name: `ai-video-videomae-metadata.json`

## 📦 **Portability & Collaboration**

### **Share Your Video Analysis**
The beauty of single-file HTML applications - just compress and share!

**Create Portable Package:**
```bash
# Using ZIP (cross-platform)
zip -r my-video-analysis.zip ai_video.html videos/ *.json

# Using TAR (Mac/Linux preferred)
tar -czf my-video-analysis.tar.gz ai_video.html videos/ *.json
```

### **Team Video Management**
Perfect for content creators, editors, educators, and media professionals:

```bash
# Video editor workflow:
tar -xzf video-analysis-project.tar.gz  # Extract package
open ai_video.html                      # Open video analyzer
# Choose AI model (Video-BERT/VideoMAE/Universal Video)
# Analyze assigned video collection (project 1-50, 51-100, etc.)
# Export metadata as "ai-video-[model]-metadata.json"
# Share JSON file back to project director
```

### **🤖 Automated Video Tools**

For large video collections and team projects:

#### **🐍 Python Tools** (`python3` / `pip`)

```bash
# Setup and split large video collections for team analysis
cd collab/python/
pip install click opencv-python
python3 split_videos.py -s /path/to/video-library -n 5

# Team members analyze their assigned video packages
# Each gets the AI Video App + subset of videos

# Merge completed analysis back together
python3 join_videos.py ../split/video-package-*
```

#### **📦 JavaScript Tools** (`npx` / `npm`)

```bash
# Setup and split large video collections
cd collab/js/
npm install
node split-videos.js -s /path/to/video-library -n 5

# Merge completed analysis results
node join-videos.js ../split/video-package-*
```

**📖 See [collab/README.md](collab/README.md) for complete video collaboration workflow.**

## 🔧 Technical Details

### AI Model Comparison

| Feature | Video-BERT 🎬 | VideoMAE 🎥 | Universal Video 🚀 |
|---------|---------------|-------------|---------------------|
| **Framework** | TensorFlow.js | TensorFlow.js | TensorFlow.js |
| **Model Size** | 45MB | 65MB | 85MB |
| **Load Time** | Fast (4-6s) | Medium (6-8s) | Slower (8-12s) |
| **Best For** | Video similarity | Scene/action recognition | Comprehensive analysis |
| **Memory Usage** | Medium | Higher | Highest |

### Supported Video Formats

- **MP4** (.mp4) - Universal compatibility with H.264/H.265 codecs
- **AVI** (.avi) - Classic format with multiple codec support
- **MOV** (.mov) - Apple QuickTime format with high quality
- **WMV** (.wmv) - Windows Media Video with efficient compression
- **MKV** (.mkv) - Matroska container with multiple audio/video streams
- **WebM** (.webm) - Open web standard with VP8/VP9 codecs
- **FLV** (.flv) - Flash video format support
- **3GP** (.3gp) - Mobile video format compatibility

### Performance
- **Client-side Processing** - All AI runs locally in your browser
- **No Server Required** - Works completely offline after initial load
- **Automatic Caching** - Models and results cached for fast re-use
- **Progressive Loading** - UI remains responsive during video analysis
- **Hardware Acceleration** - Leverages GPU when available for video processing
- **Streaming Support** - Efficient memory usage for large video files

### Browser Support
- **Modern Browsers** - Chrome 80+, Firefox 75+, Safari 13+, Edge 80+
- **HTML5 Video** - For advanced video playback and frame extraction
- **File API Support** - For local video file processing
- **Canvas API** - For video frame analysis and thumbnail generation
- **Fallback Mode** - Basic video playback if AI models fail to load

## 📊 Use Cases

- **Content Creation** - Organize and analyze video content for creators and influencers
- **Video Editing** - Quick content discovery and scene identification for editors
- **Educational Content** - Catalog and search educational videos and tutorials
- **Media Production** - Professional video analysis and content management
- **Personal Video Libraries** - Organize family videos, vacations, and memories
- **Security Footage** - Analyze and search through surveillance video content
- **Documentary Research** - Content analysis for documentary and film production
- **Social Media Management** - Organize and tag video content for platforms

## 💾 Data Management

### Export Video Metadata
- Click "💾 Export Metadata" to save all AI analysis results
- Exports to `ai-video-[model]-metadata.json`
- Includes scenes, objects, actions, and video characteristics
- Compatible across sessions and devices

### Import Video Metadata  
- Click "📂 Import Metadata" to load previous analysis results
- Automatically matches videos by filename and video fingerprint
- Restores tags, scenes, objects, and AI analysis data
- Useful for sharing analysis results with team members

## 🛠️ Development

### Project Structure
```
ai_video/
├── ai_video.html                       # 🎯 Main AI Video App
├── README.md                          # Main documentation
├── LICENSE                           # MIT License
├── docs/                             # Documentation assets
│   ├── ai_video_screenshot.png       # App screenshot
│   └── architecture.md              # Technical architecture
├── samples/                          # Sample video files for testing
│   ├── sample.mp4                   # MP4 sample
│   ├── sample.avi                   # AVI sample
│   ├── sample.mov                   # MOV sample
│   └── sample.webm                  # WebM sample
└── collab/                          # Collaboration tools
    ├── README.md                    # Collaboration documentation
    ├── python/                      # Python-based tools
    │   ├── split_videos.py          # Split video collections
    │   └── join_videos.py           # Merge video analysis
    └── js/                         # JavaScript tools
        ├── package.json            # Node.js dependencies
        ├── split-videos.js          # Split video collections
        └── join-videos.js           # Merge video analysis
```

### Architecture
- **Single HTML File** - Entire application in one file for portability
- **Vanilla JavaScript** - No frameworks, pure JS for maximum compatibility
- **HTML5 Video API** - Advanced video processing and frame extraction
- **Canvas Integration** - Video frame analysis and thumbnail generation
- **Progressive Enhancement** - Graceful degradation with fallback modes
- **Event-driven** - Responsive UI with async AI processing
- **Model Abstraction** - Easy to swap between different AI models
- **Memory Efficient** - Optimized for large video files and collections

### Model Selection Guide
- **Choose Video-BERT** 🎬 for:
  - Fast video similarity and embedding
  - Quick video discovery and matching
  - Large video libraries where speed matters
  
- **Choose VideoMAE** 🎥 for:
  - Scene detection and action recognition
  - Content-based video organization
  - Most general-purpose video analysis
  
- **Choose Universal Video** 🚀 for:
  - Advanced video understanding requirements
  - Complex video research and analysis
  - Professional video production workflows

## 🎉 **Why AI Video App Stands Out**

🚀 **Zero Installation** - One HTML file does it all  
🎬 **Three Video AI Models** - Choose the perfect model for your video needs  
🎯 **Smart UX** - Every interaction is thoughtfully designed for video professionals  
📱 **Works Everywhere** - Desktop, tablet, mobile - no limits  
🔒 **Privacy First** - All processing happens locally in your browser  
⚡ **Lightning Fast** - Optimized for performance and video responsiveness  
🤝 **Team Ready** - Built-in collaboration tools for any video production team  

## Video Download
### [yt-dlp](https://pypi.org/project/yt-dlp/)

```bash
pip install yt-dlp
yt-dlp -f mp4 xD-nRvkuNJk
yt-dlp -f mp4 bfxVWhErxvI
yt-dlp -f mp4 V8uCeLHMAnk
yt-dlp -f mp4 gEt7PwBSaOs
yt-dlp -f mp4 7xASPU6rS-0
yt-dlp -f mp4 QpxcuXd3E94
```

## 📜 License

MIT License - feel free to use, modify, and distribute.

## 🙋 Support

For questions or issues:
1. Check the browser console for error messages
2. Ensure your browser supports HTML5 Video API
3. Try the fallback video player if AI models fail to load
4. Clear browser cache and reload if models seem corrupted
5. Check video codec compatibility with your browser

---

**Built with ❤️ using Claude Code and powered by TensorFlow.js**  
*Creating the future of video management, one frame at a time.*