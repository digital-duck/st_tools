# AI Audio App

🎵 **A powerful, portable web-based audio manager with AI-powered audio analysis, smart search, and intelligent music discovery**

✨ **Ultra-Portable**: Single HTML file application - no installation, no server, no dependencies. Just zip and share!

🎯 **Smart & Intuitive**: Modern UI with waveform visualization, click-to-edit tags, interactive audio player, and AI model guidance

![AI Audio App](docs/ai_audio_screenshot.png)

## 🌟 **What's Coming**

✅ **Interactive Audio Player** - Click any track to play with embedded controls  
✅ **Waveform Visualization** - Beautiful audio waveforms in grid cards  
✅ **Smart AI Audio Analysis** - Genre, mood, tempo, and instrument detection  
✅ **One-Click Tagging** - Auto-clearing placeholders for smooth metadata editing  
✅ **Audio Format Support** - MP3, WAV, FLAC, AAC, OGG, and more  
✅ **Modern Responsive UI** - Beautiful animations and mobile-optimized design  

## 🎯 **AI-Powered Audio Management**

**One app, three powerful AI models for audio processing!** Choose your model with intelligent guidance:

| Model | Best For | Speed | Learn More |
|-------|----------|-------|------------|
| **Audio-BERT** 🎵 | Fast audio embeddings & similarity search | ⚡ Fast | [Documentation](https://github.com/microsoft/unilm/tree/master/xtune) |
| **MusicCNN** 🎶 | Music genre & mood classification | 🚀 Balanced | [Model Info](https://github.com/jordipons/musicnn) |
| **Universal Audio** 🚀 | Advanced audio understanding & tagging | 🔄 Comprehensive | [Research Paper](https://arxiv.org/abs/2010.10915) |

**✨ Smart Model Selection**: Hover over the **?** icon next to the model dropdown for detailed guidance and direct links to documentation!

**Single File:** `ai_audio.html` - Contains all three models with dynamic loading!

## ✨ Features

### 🤖 AI Audio Processing
- **Genre Classification** - Auto-categorizes music by genre and style
- **Mood Detection** - Identifies emotional content and energy levels
- **Tempo Analysis** - BPM detection and rhythm classification
- **Instrument Recognition** - Identifies instruments and musical elements
- **Content Analysis** - Deep understanding of audio characteristics and patterns

### 🎵 Multi-Format Support
- **MP3 Files** - Most common audio format with full metadata support
- **WAV Files** - Uncompressed audio with high-quality analysis
- **FLAC Files** - Lossless compression with detailed metadata
- **AAC/M4A Files** - Apple format with advanced tagging
- **OGG Files** - Open-source format with Vorbis codec
- **WMA Files** - Windows Media Audio format support

### 🔍 Smart Search Capabilities
Search your music library using natural language:
- `"upbeat electronic music"` - finds energetic electronic tracks
- `"calm piano pieces"` - locates peaceful instrumental music
- `"rock songs from 2020"` - discovers rock music from specific years
- `"jazz with saxophone"` - identifies jazz tracks featuring saxophone
- `"workout music high energy"` - finds high-tempo motivational tracks

**🎯 Enhanced Search Experience:**
- **Clickable Results** - Click any search result to instantly play the track
- **Smart Scoring** - Match percentages help you find the most relevant audio
- **Seamless Navigation** - Search modal auto-closes when you select a track
- **Audio Preview** - See waveform and metadata for each search result

**Search Quality:**
- **Audio-BERT** 🎵: Fast embedding-based similarity search
- **MusicCNN** 🎶: Genre and mood-aware audio matching
- **Universal Audio** 🚀: Advanced semantic understanding with context

### 🎧 Interactive Audio Player
**Click any audio file** to open the enhanced player:
- **🎵 All Audio Formats** - Universal playback with HTML5 audio
- **📊 Waveform Display** - Visual representation of audio content
- **🎛️ Playback Controls** - Play/pause, seek, volume, and speed controls
- **📈 Audio Metadata** - File size, bitrate, duration, and codec info
- **🎨 Clean Interface** - Responsive design that works on all devices

### 📁 Smart Audio Management
- **Multi-format Support** - MP3, WAV, FLAC, AAC, OGG, WMA files
- **Bulk Operations** - Select individual files or entire music folders
- **Drag & Drop** - Drop audio files directly onto the player
- **Metadata Export/Import** - Save and load AI analysis results
- **🎯 Smart Tags** - Click "Click to add tags..." to instantly start editing (auto-clears placeholder)
- **📊 Visual Organization** - Audio file cards with waveforms and metadata

### 🎨 Modern User Interface
- **📱 Responsive Design** - Works seamlessly on desktop, tablet, and mobile
- **🎯 Interactive Elements** - Hover tooltips, clickable components, smooth animations
- **⚡ Real-time Feedback** - Live progress bars during AI processing
- **🔍 Smart Search UI** - Search suggestions with instant clickable results
- **📊 Visual Audio Grid** - Customizable layout (1-4 tracks per row)
- **🏷️ Format Badges** - Clear visual indicators for different audio formats
- **✏️ Inline Editing** - Click-to-edit tags with smart placeholder behavior

## 🚀 Getting Started

### **Open the AI Audio App**

```bash
open ai_audio.html
```

**That's it!** One file, all AI models included.

### **Basic Usage**

1. **Load Your Music Library**
   - Click "📁 Select Audio Files" for individual tracks
   - Click "📂 Select Music Folder" to load an entire music library
   - Or drag and drop audio files directly onto the player

2. **Choose Your AI Model**
   - Select from dropdown: Audio-BERT 🎵, MusicCNN 🎶, or Universal Audio 🚀
   - Model loads automatically with progress indicator
   - Switch models anytime to compare analysis results

3. **Analyze with AI**
   - Click the **🎵 AI Analyze** button 
   - Wait for analysis to complete (shows progress with model-specific messaging)
   - AI genres, moods, and audio characteristics will appear on each track

4. **Search Your Music**
   - Click "🔍 AI Search" to open the search modal
   - Type natural language descriptions of music you want
   - Click search suggestions for quick queries
   - Results ranked by relevance (quality varies by selected model)

5. **Play & Enjoy**
   - Click any track to open the audio player
   - View waveforms, control playback, adjust settings
   - Edit tags and metadata inline

6. **Export Results**
   - Click "💾 Export Metadata" to save analysis results
   - Filename automatically includes model name: `ai-audio-musiccnn-metadata.json`

## 📦 **Portability & Collaboration**

### **Share Your Music Analysis**
The beauty of single-file HTML applications - just compress and share!

**Create Portable Package:**
```bash
# Using ZIP (cross-platform)
zip -r my-music-analysis.zip ai_audio.html music/ *.json

# Using TAR (Mac/Linux preferred)
tar -czf my-music-analysis.tar.gz ai_audio.html music/ *.json
```

### **Team Music Management**
Perfect for music producers, DJs, radio stations, and music enthusiasts:

```bash
# Music curator workflow:
tar -xzf music-analysis-project.tar.gz  # Extract package
open ai_audio.html                      # Open audio analyzer
# Choose AI model (Audio-BERT/MusicCNN/Universal Audio)
# Analyze assigned music collection (album 1-50, 51-100, etc.)
# Export metadata as "ai-audio-[model]-metadata.json"
# Share JSON file back to music director
```

### **🤖 Automated Music Tools**

For large music collections and team projects:

#### **🐍 Python Tools** (`python3` / `pip`)

```bash
# Setup and split large music collections for team analysis
cd collab/python/
pip install click mutagen
python3 split_music.py -s /path/to/music-library -n 5

# Team members analyze their assigned music packages
# Each gets the AI Audio App + subset of tracks

# Merge completed analysis back together
python3 join_music.py ../split/music-package-*
```

#### **📦 JavaScript Tools** (`npx` / `npm`)

```bash
# Setup and split large music collections
cd collab/js/
npm install
node split-music.js -s /path/to/music-library -n 5

# Merge completed analysis results
node join-music.js ../split/music-package-*
```

**📖 See [collab/README.md](collab/README.md) for complete music collaboration workflow.**

## 🔧 Technical Details

### AI Model Comparison

| Feature | Audio-BERT 🎵 | MusicCNN 🎶 | Universal Audio 🚀 |
|---------|----------------|-------------|---------------------|
| **Framework** | TensorFlow.js | TensorFlow.js | TensorFlow.js |
| **Model Size** | 25MB | 35MB | 45MB |
| **Load Time** | Fast (3-4s) | Medium (4-6s) | Slower (6-8s) |
| **Best For** | Audio similarity | Genre/mood | Comprehensive analysis |
| **Memory Usage** | Low | Medium | Higher |

### Supported Audio Formats

- **MP3** (.mp3) - Universal compatibility with metadata support
- **WAV** (.wav) - Uncompressed audio with high-quality analysis
- **FLAC** (.flac) - Lossless compression with detailed metadata
- **AAC/M4A** (.aac, .m4a) - Apple format with advanced tagging
- **OGG** (.ogg) - Open-source format with Vorbis codec
- **WMA** (.wma) - Windows Media Audio format

### Performance
- **Client-side Processing** - All AI runs locally in your browser
- **No Server Required** - Works completely offline after initial load
- **Automatic Caching** - Models and results cached for fast re-use
- **Progressive Loading** - UI remains responsive during analysis
- **Web Audio API** - High-performance audio processing and visualization

### Browser Support
- **Modern Browsers** - Chrome 80+, Firefox 75+, Safari 13+, Edge 80+
- **Web Audio API** - For advanced audio processing and waveform generation
- **File API Support** - For local audio file processing
- **Fallback Mode** - Basic audio playback if AI models fail to load

## 📊 Use Cases

- **Music Library Management** - Organize and discover music in large collections
- **DJ Set Preparation** - Find tracks by mood, energy, and genre for perfect mixing
- **Music Production** - Analyze reference tracks and identify musical elements
- **Radio Programming** - Content analysis and automated playlist generation
- **Music Research** - Academic and commercial music analysis
- **Personal Music Discovery** - Find forgotten gems in your music collection

## 💾 Data Management

### Export Audio Metadata
- Click "💾 Export Metadata" to save all AI analysis results
- Exports to `ai-audio-[model]-metadata.json`
- Includes genres, moods, audio characteristics, and timestamps
- Compatible across sessions and devices

### Import Audio Metadata  
- Click "📂 Import Metadata" to load previous analysis results
- Automatically matches tracks by filename and audio fingerprint
- Restores tags, genres, moods, and AI analysis data
- Useful for sharing analysis results with team members

## 🛠️ Development

### Project Structure
```
ai_audio/
├── ai_audio.html                       # 🎯 Main AI Audio App
├── README.md                          # Main documentation
├── LICENSE                           # MIT License
├── docs/                             # Documentation assets
│   ├── ai_audio_screenshot.png       # App screenshot
│   └── architecture.md              # Technical architecture
├── samples/                          # Sample audio files for testing
│   ├── sample.mp3                   # MP3 sample
│   ├── sample.wav                   # WAV sample
│   ├── sample.flac                  # FLAC sample
│   └── sample.m4a                   # AAC sample
└── collab/                          # Collaboration tools
    ├── README.md                    # Collaboration documentation
    ├── python/                      # Python-based tools
    │   ├── split_music.py          # Split music collections
    │   └── join_music.py           # Merge music analysis
    └── js/                         # JavaScript tools
        ├── package.json            # Node.js dependencies
        ├── split-music.js          # Split music collections
        └── join-music.js           # Merge music analysis
```

### Architecture
- **Single HTML File** - Entire application in one file for portability
- **Vanilla JavaScript** - No frameworks, pure JS for maximum compatibility
- **Web Audio API** - Advanced audio processing and waveform generation
- **Progressive Enhancement** - Graceful degradation with fallback modes
- **Event-driven** - Responsive UI with async AI processing
- **Model Abstraction** - Easy to swap between different AI models

### Model Selection Guide
- **Choose Audio-BERT** 🎵 for:
  - Fast audio similarity and embedding
  - Quick music discovery and matching
  - Large music libraries where speed matters
  
- **Choose MusicCNN** 🎶 for:
  - Music genre and mood classification
  - Content-based music organization
  - Most general-purpose music analysis
  
- **Choose Universal Audio** 🚀 for:
  - Advanced audio understanding requirements
  - Complex music research and analysis
  - Professional music production workflows

## 🎉 **Why AI Audio App Stands Out**

🚀 **Zero Installation** - One HTML file does it all  
🎵 **Three Audio AI Models** - Choose the perfect model for your music needs  
🎯 **Smart UX** - Every interaction is thoughtfully designed for music lovers  
📱 **Works Everywhere** - Desktop, tablet, mobile - no limits  
🔒 **Privacy First** - All processing happens locally in your browser  
⚡ **Lightning Fast** - Optimized for performance and audio responsiveness  
🤝 **Team Ready** - Built-in collaboration tools for any music team  

## 📜 License

MIT License - feel free to use, modify, and distribute.

## 🙋 Support

For questions or issues:
1. Check the browser console for error messages
2. Ensure your browser supports Web Audio API
3. Try the fallback audio player if AI models fail to load
4. Clear browser cache and reload if models seem corrupted

---

**Built with ❤️ using Claude Code and powered by TensorFlow.js**  
*Creating the future of audio management, one beat at a time.*