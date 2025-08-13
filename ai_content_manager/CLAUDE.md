# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Content Manager is a single-file web application that provides AI-powered content management across four content types: Images, Documents, Audio, and Video. The project uses a unified tab-based interface with local AI processing via TensorFlow.js models.

## Architecture

### Core Structure
- **Single HTML files**: Each content type has its own standalone HTML file with embedded CSS/JS
- **Unified interface**: `ai_content_manager.html` provides a tab-based interface combining all content types
- **Self-contained**: No external dependencies - everything runs in the browser
- **Local AI processing**: Uses TensorFlow.js models for privacy-first content analysis

### Key Files
- `ai_content_manager.html` - Main unified application
- `ai_audio.html`, `ai_video.html`, `ai_docu.html`, `img_viewer_ai.html` - Individual content type apps
- `docs/` - Mermaid architecture diagrams
- `contents/` - Sample content for testing (images, documents, audio, video)

### Content Processing Architecture
Each content type uses specialized processors:
- **Images**: MobileNet v2, EfficientNet, MediaPipe for object detection and scene analysis
- **Documents**: BERT-based NLP for keyword extraction and summarization
- **Audio**: Audio classification models for genre and mood detection
- **Video**: Scene detection and activity recognition

## Development Commands

Since this is a client-side only project with no build process:

```bash
# Start local development server
python -m http.server 8000
# Then open http://localhost:8000/ai_content_manager.html

# Test individual components
open ai_audio.html      # Audio component
open ai_video.html      # Video component  
open ai_docu.html       # Document component
open img_viewer_ai.html # Image component
```

## Testing

No automated test framework is configured. Testing is done manually by:
1. Loading different content types into each tab
2. Testing AI analysis functionality
3. Verifying search across content types
4. Testing export/import functionality

## Key Technical Details

### Data Flow
1. User loads content via drag-and-drop or file selection
2. Content is processed by appropriate AI models (TensorFlow.js)
3. Results stored in browser's IndexedDB for persistence
4. Universal search enables cross-content-type discovery
5. Export functionality saves analysis results as JSON

### Browser Limitations
- **Ubuntu folder selection**: Known issue with folder selection on Ubuntu - use individual file selection or drag-and-drop instead
- **Large files**: Memory limitations for files >100MB
- **Mobile browsers**: Some AI models may not load on older mobile devices

### Privacy Design
- All processing happens locally in the browser
- No data is sent to external servers
- Offline capable once initial page is loaded
- GDPR/HIPAA compliant by design

## Development Guidelines

When working with this codebase:
- Maintain single-file architecture - embed all CSS/JS within HTML files
- Preserve privacy-first design - no external API calls for content processing
- Follow consistent UI patterns across all content type tabs
- Test across different browsers and file types
- Consider mobile responsiveness in any UI changes