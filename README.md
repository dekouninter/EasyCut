# 🎬 EasyCut - Professional YouTube Downloader & Stream Recorder

![Version](https://img.shields.io/badge/version-1.10.0-blue.svg)
![License](https://img.shields.io/badge/license-GPL--3.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![Author](https://img.shields.io/badge/author-Deko%20Costa-brightgreen.svg)

**EasyCut** is a professional desktop application for downloading YouTube videos, recording live streams, clipping content in real-time, and extracting audio. Built with Python 3.10+ and Tkinter featuring a premium visual design system with SVG icon rendering, multi-accent color palettes, gradient effects, glass-morphism UI, and 7-language support.

**Author:** Deko Costa  
**Repository:** [github.com/dekouninter/EasyCut](https://github.com/dekouninter/EasyCut)  
**License:** GPL-3.0

---

## ✨ Key Features

### 📥 Download Single Videos
- YouTube URL input with instant verification
- **Transcript download:** button to save timed subtitles as TXT (no video/audio)
- **No WebM** formats: all downloads explicitly exclude WebM to ensure MP4 output
- **Premiere Compatibility**: optional setting to auto-convert downloads to MP4/H264 so they can be opened directly in Adobe Premiere
- **Smart URL Router:** Auto-detects video, live stream, or playlist URLs and routes to the correct tab
- **4 Download Modes:**
  - Complete video download
  - Extract specific time range (start/end timestamps)
  - Record up to a specific time
  - Audio-only extraction
- **Quality Presets:** Best, MP4 (Best), 1080p Full HD, 720p HD
  (WebM is automatically excluded)
- **Audio Formats:** MP3, WAV, M4A, OPUS
- **Bitrate Control:** 128, 192, 256, 320 kbps
- Real-time progress tracking with expandable log panel

### 📦 Batch Download Multiple Videos
- Paste up to 50 YouTube URLs (one per line)
- Quick paste from clipboard
- Sequential download tracking: "X of Y completed"
- Stop all downloads button
- All videos use same quality/format settings

### 🔴 Record Live Streams & Live Clipper
- Live stream URL verification before recording
- **Embedded Video Player:** Preview live streams directly inside EasyCut (mpv-based)
- **Live Clipper:** Mark start/end points on the seekbar to cut clips in real-time
- **Recording Modes:**
  - Continuous recording (until manually stopped)
  - Fixed duration recording (hours/minutes/seconds)
  - Record until specified time
- **Quality Presets:** Best, 1080p, 720p, 480p
- Elapsed time display during recording
- Automatic stop at duration limit

### 🎬 Post-Processing Hub
- **Automatic post-download processing** for downloaded files
- Format conversion, audio extraction, and trimming
- Queue-based processing with progress tracking
- Configurable output settings

### 📡 Channel Monitor
- **Monitor YouTube channels** for new content
- Automatic detection of new uploads and live streams
- Configurable check intervals
- Notification system for new content

### 👥 Following Tab
- **Track your favorite channels** in one place
- Quick access to channel content
- Integrated with Channel Monitor for notifications

### 📜 Download History
- Auto-save all downloaded videos with metadata
- Quick actions: open folder, re-download, delete from history
- Search/filter functionality
- Persistent storage in JSON
- Clear entire history with confirmation

### 🔐 YouTube Authentication (Google OAuth 2.0)
- One-click "Sync with YouTube" authentication
- Read-only access to YouTube (no data modification)
- Browser-based OAuth flow
- Automatic cookie generation for yt-dlp
- One-click logout
- Persistent authentication across sessions

### 🔌 Advanced Authentication
For browser cookie extraction as an alternative to OAuth, see [QUICKSTART.md](QUICKSTART.md#browser-authentication-optional).

### 🎨 Customization
- **Theme Switching:** Dark/Light mode with instant reload (Ctrl+T)
- **Multi-Language:** 7 languages with instant reload — English, Portuguese, Spanish, French, German, Italian, Japanese
- **Output Folder:** Select any directory for downloads
- **All settings persist** across app restarts

### 🎯 User Experience
- **Keyboard Shortcuts:** Ctrl+1-8 for tabs, Ctrl+L for logs, Ctrl+O for folder
- **Expandable Log Panel:** View download progress in real-time (Ctrl+L)
- **Status Bar:** Current status, login state, app version
- **Floating Donation Button:** Quick links to support creators
- **Modern UI:** Clean design with custom widgets and rounded cards
- **Embedded Video Player:** Built-in mpv player with play/pause, seekbar, and volume controls

### 🎨 Premium Visual Design (v1.6)
- **SVG Icon Rendering:** Custom Feather icon renderer with Pillow (no external SVG libs)
- **Multi-Accent Color System:** 6 accent families — Blue, Purple, Orange, Red, Rose, Cyan
- **Gradient Effects:** 6 named gradient presets (blue→purple, purple→pink, orange→red, etc.)
- **Glass-Morphism UI:** Semi-transparent tooltips, glow borders, depth effects
- **Windows Mica Backdrop:** Native Windows 11 Mica/Acrylic effect via pywinstyles
- **OS Theme Detection:** Automatic dark/light detection via darkdetect
- **16 Custom Components:** Modern UI widgets including cards, buttons, progress indicators, and animated panels
- **Colored Sidebar Icons:** Each tab has a unique SVG icon with distinct accent color
- **Gradient Accent Lines:** Section headers and cards feature gradient accent decorations

---

## 🆕 What's New in v1.10.0

### Batch Download Improvements
- **Individual progress bars** for each video in queue
- **Global progress bar** showing "Downloading X of Y"
- **Speed and ETA display** per download
- **Retry button** for failed items
- **Friendly error messages** with recovery suggestions

### Coming Soon
- Improved live stream clipper with seekbar-based cutting
- Dependency status panel with auto-install options
- FFmpeg progress bars during conversions

---

## 📦 System Requirements

- **Windows**: Primary target (other OSes may work but unsupported)
- **Python**: 3.10+
- **Tkinter**: Usually bundled with Python on Windows

### Dependencies

| Package | Purpose | License |
|---------|---------|---------|
| `yt-dlp` | Video downloading | Unlicense |
| `pillow` | Image processing & SVG icon rendering | HPND |
| `google-auth-oauthlib` | OAuth authentication | Apache 2.0 |
| `google-auth-httplib2` | OAuth HTTP client | Apache 2.0 |
| `requests` | HTTP requests | Apache 2.0 |
| `keyring` | Secure credential storage | MIT |
| `pywinstyles` | Windows Mica/Acrylic backdrop effects | MIT |
| `darkdetect` | OS dark/light theme detection | BSD-3 |

### External Tools

- **FFmpeg**: Required for post-processing, audio conversion, and trimming
- **mpv**: Optional (embedded video player for live preview and clip marking)
- **Inter Font**: Bundled in `assets/fonts/Inter/` (OFL 1.1)
- **Feather Icons**: Bundled in `assets/feather-main/` (MIT) — rendered as SVG→Pillow via `icon_renderer.py`

### Defaults

- **Language:** English (can switch to any of 7 languages instantly)
- **Theme:** Dark (can toggle to Light instantly)
- **Authentication:** OAuth 2.0 (one-click YouTube sync)
- **Output Folder:** `downloads/` (user-selectable)

---

## 🚀 Installation

### Quick Start
1. Clone: `git clone https://github.com/dekouninter/EasyCut.git && cd EasyCut`
2. Create venv: `python -m venv venv`
3. Activate: `.\venv\Scripts\Activate.ps1` (Windows)
4. Install: `pip install -r requirements.txt`
5. Run: `python main.py`

### FFmpeg (Recommended)
```powershell
winget install FFmpeg
```

### OAuth Setup (Developers)
See [QUICKSTART.md](QUICKSTART.md#oauth-setup-for-developers) for complete OAuth setup instructions.

---

## 💻 Usage

### Run the Application

```bash
python main.py
```

**Or double-click:** `START.bat`

### First Run

1. The application will automatically create `config/` and `downloads/` folders
2. Default settings will be created in `config/config.json`
3. History will be maintained in `config/history_downloads.json`

### Local Files Created

- `config/config.json` — App settings (theme, language, output folder)
- `config/history_downloads.json` — Download history (last 100 entries)
- `config/app.log` — Application logs
- `config/youtube_token.json` — OAuth token cache
- `config/yt_cookies.txt` — Cookies for yt-dlp authentication
- `downloads/` — Default output folder

### YouTube Authentication (OAuth 2.0)

1. Click **"Sync with YouTube"** in the authentication banner
2. Your browser opens and you authorize EasyCut
3. Tokens are stored locally in `config/youtube_token.json`
4. Cookies are stored locally in `config/yt_cookies.txt`
5. You can logout anytime using the **Logout** button

---

## 🔐 Security

### Credential Management

- **OAuth 2.0**: Authentication handled by Google consent screen
- **Local tokens**: Stored in `config/youtube_token.json`
- **Local cookies**: Stored in `config/yt_cookies.txt` for yt-dlp
- **No passwords**: EasyCut never sees or stores your Google password

### Validations

- ✅ YouTube URL validation
- ✅ Time range format validation (HH:MM:SS or MM:SS)

---

## 📄 License

This project is licensed under the **GPL-3.0 License** — GNU General Public License v3.0.

---

## 🚀 Development & Contributions

### For Contributors

Interested in contributing? Here's what you need to know:

1. **Get Started**: See [Installation](#installation) section
2. **OAuth Setup**: Copy `config/credentials_template.json` to `config/credentials.json` and fill in your Google OAuth credentials
3. **Development**: Run `python main.py` to test changes
4. **Architecture**: Review [src/](src/) modules and open an issue if you want guidance

### Building Releases

Want to create standalone executables? See `build.py` for complete instructions.

**Quick build:**
```bash
pip install pyinstaller
python build.py
```

This creates `dist/EasyCut.exe` with embedded OAuth credentials - ready to distribute!

## 📚 Documentation

### User & Quick Start
- [Installation](#installation) — Installation and setup
- [QUICKSTART.md](QUICKSTART.md) — Quick start guide
- [ARCHITECTURE.md](ARCHITECTURE.md) — Technical architecture overview

### Development & Planning
- Internal planning documents are maintained locally and are not part of the public repository.
### Documentation Index
- [**DOCUMENTATION.md**](DOCUMENTATION.md) — **📚 Master index of all documentation**
### Legal & Credits
- [PRIVACY.md](PRIVACY.md) — Privacy policy for OAuth users
- [TERMS.md](TERMS.md) — Terms of service
- [CREDITS.md](CREDITS.md) — Credits and licenses

### External Resources
- [yt-dlp Documentation](https://github.com/yt-dlp/yt-dlp) — Video download library
- [FFmpeg Documentation](https://ffmpeg.org/documentation.html) — Optional audio/video conversion
- [Google OAuth Documentation](https://developers.google.com/identity/protocols/oauth2/) — Authentication
- [YouTube Data API Guide](https://developers.google.com/youtube/v3/getting-started) — YouTube integration

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| "FFmpeg not found" | Install FFmpeg: `winget install FFmpeg` |
| "OAuth 403 Error" | Re-authenticate: Click "Sync with YouTube" |
| Download stalls | Check internet, try lower quality preset |
| Live stream won't load | Verify stream is active and public |

For more help, see [QUICKSTART.md](QUICKSTART.md#faq) or open a GitHub issue.

---

**Developed with ❤️ by Deko Costa**

*Making downloads simple.*

**Repository:** [github.com/dekouninter/EasyCut](https://github.com/dekouninter/EasyCut)  
**Support:** [buymeacoffee.com/dekocosta](https://buymeacoffee.com/dekocosta)  
**Livepix:** [livepix.gg/dekocosta](https://livepix.gg/dekocosta)
