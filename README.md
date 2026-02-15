# 🎬 EasyCut - Professional YouTube Downloader

![Version](https://img.shields.io/badge/version-1.3.0-blue.svg)
![License](https://img.shields.io/badge/license-GPL--3.0-blue.svg)
![Author](https://img.shields.io/badge/author-Deko%20Costa-brightgreen.svg)

**EasyCut** is a professional desktop application for downloading YouTube videos and recording live streams, built with Python and Tkinter.

**Author:** Deko Costa  
**Repository:** [github.com/dekouninter/EasyCut](https://github.com/dekouninter/EasyCut)

---

## ⚠️ Important Legal Notice

**FOR PERSONAL USE ONLY**

EasyCut is intended for **personal, non-commercial use** to download:
- **Your own videos** uploaded to YouTube
- Videos you have **explicit permission** to download from the content creator
- Content allowed under **fair use** doctrine in your jurisdiction

**You are responsible for:**
- Complying with YouTube's Terms of Service
- Respecting copyright laws in your country
- Obtaining necessary permissions before downloading content
- Using downloaded content legally and ethically

**EasyCut developers are not responsible for:**
- Copyright violations committed by users
- Misuse of the software
- Legal consequences resulting from unauthorized downloads

By using EasyCut, you acknowledge and accept full responsibility for your actions.

---

## 📥 Getting Started

### For End Users (Recommended)

**Download the latest release** - no installation needed!

1. Go to [Releases](https://github.com/dekouninter/EasyCut/releases)
2. Download `EasyCut.exe`
3. Run it - that's it! ✨

The standalone executable includes everything:
- ✅ No Python installation required
- ✅ No OAuth setup needed
- ✅ Just download and run
- ✅ Works on any Windows PC

### For Developers

Want to contribute or run from source? See [Installation](#installation) below.

---

### ✨ Key Features (Current Code)

- ✅ **Single Video Download**: Download YouTube videos with quality presets (Best, MP4 Best, 1080p, 720p)
- ✅ **Audio Conversion**: Extract audio as MP3, WAV, M4A, OPUS with bitrate options (128-320 kbps)
- ✅ **Time Range Downloads**: Download specific segments (Start/End time in HH:MM:SS format)
- ✅ **Batch Downloads**: Paste multiple URLs for sequential downloading
- ✅ **Playlist Downloads**: Download entire YouTube playlists via yt-dlp
- ✅ **Channel Downloads**: Download latest 10 videos from a YouTube channel
- ✅ **Live Stream Recording**: Record live streams with quality presets (Best, 1080p, 720p, 480p)
- ✅ **YouTube OAuth 2.0**: One-click "Sync with YouTube" authentication
- ✅ **Persistent Auth**: Tokens in `config/youtube_token.pickle`, cookies in `config/yt_cookies.txt`
- ✅ **Download History**: Stored in `config/history_downloads.json` with search/filter and clear button
- ✅ **Output Folder Selection**: Default `downloads/`, changeable in UI
- ✅ **Real-Time Logs**: Download, batch, and live logs in the UI with progress hooks
- ✅ **Light/Dark Theme**: Instant theme switch
- ✅ **Multi-Language**: 7 languages — English, Portuguese, Spanish, French, German, Italian, Japanese (250+ translated strings each)
- ✅ **Structured Logging**: RotatingFileHandler (5MB max, 3 backups) + console output
- ✅ **Graceful Shutdown**: Config save and active download check on close
- ✅ **Donation Buttons**: Buy Me a Coffee and Livepix links
- ✅ **Custom Fonts**: Inter Display with Segoe UI fallback
- ✅ **Keyboard Shortcuts**: Ctrl+1-5 (sections), Ctrl+T (theme), Ctrl+L (log), Ctrl+O (folder), Esc (close log)
- ✅ **Collapsible Sidebar**: Hamburger menu to expand/collapse navigation

---

## 📦 System Requirements

- **Python**: 3.8 or higher
- **Tkinter**: Usually bundled with Python on Windows
- **Windows**: Primary target (font loading and folder opening are Windows-optimized)
- **FFmpeg**: Required for audio conversion (MP3, WAV, M4A, OPUS extraction)

### Python Dependencies

```
yt-dlp>=2024.3.10
pillow>=10.0.0
google-auth-oauthlib>=1.2.0
google-auth-httplib2>=0.3.0
requests>=2.32.0
```

**Default Settings:**
- Language: **Portuguese** (can switch to English, Spanish, French, German, Italian, or Japanese instantly)
- Theme: **Dark** (can toggle to Light instantly)
- Authentication: **OAuth 2.0** (one-click sync with YouTube)

Tkinter usually comes pre-installed with Python.

---

## 🚀 Installation

### 1. Clone Repository

```bash
git clone https://github.com/dekouninter/EasyCut.git
cd EasyCut
```

### 2. Create Virtual Environment (recommended)

```bash
python -m venv venv
```

**Activate virtual environment:**

- **Windows (PowerShell):**
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```

- **Windows (CMD):**
  ```cmd
  venv\Scripts\activate.bat
  ```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Verify Installation (Optional)

```bash
python scripts/check_installation.py
```

This checks Python, yt-dlp, OAuth dependencies, Tkinter, and FFmpeg.

### 5. Install FFmpeg (Optional)

**Windows (using Chocolatey):**
```powershell
choco install ffmpeg
```

**Windows (using winget):**
```powershell
winget install FFmpeg
```

**Or download manually:** [ffmpeg.org](https://ffmpeg.org/download.html)

### 6. OAuth Setup (Developers Only)

If you're running from source, you need to create OAuth credentials:

1. **Quick Setup**: Follow [OAUTH_SETUP.md](OAUTH_SETUP.md) to create your own Google OAuth credentials
2. **Create** `config/credentials.json` with your credentials (see `config/credentials_template.json`)

**Note**: End users who download releases don't need this - OAuth is embedded in the executable.

---

## 💻 Usage

### Run the Application

```bash
python main.py
```

**Or double-click:** `scripts\START.bat`

### First Run

1. The application will automatically create `config/` and `downloads/` folders
2. Default settings will be created in `config/config.json`
3. History will be maintained in `config/history_downloads.json`

### Local Files Created

- `config/config.json` — App settings (theme, language, output folder)
- `config/history_downloads.json` — Download history (last 100 entries)
- `config/app.log` — Application logs
- `config/youtube_token.pickle` — OAuth token cache
- `config/yt_cookies.txt` — Cookies for yt-dlp authentication
- `downloads/` — Default output folder

### YouTube Authentication (OAuth 2.0)

1. Click **"Sync with YouTube"** in the authentication banner
2. Your browser opens and you authorize EasyCut
3. Tokens are stored locally in `config/youtube_token.pickle`
4. Cookies are stored locally in `config/yt_cookies.txt`
5. You can logout anytime using the **Logout** button

---

## ⚠️ Known Limitations (Current Code)

- These items are documented and planned, but not prioritized yet.
- **Download Cancellation**: The stop button sets a flag but cannot cancel an in-progress yt-dlp download. In batch mode, the "Stop All" button also cannot interrupt the current URL being downloaded.
- **Browser Cookie Extraction**: The browser cookie UI exists but is disabled in favor of OAuth flow.
- **Thread Safety**: Some background operations update UI directly without `root.after()` scheduling.
- **Batch History**: Individual batch downloads are not added to history separately; history refreshes only after the entire batch completes.
- **Donation Window Language**: The donation popup always displays in English regardless of the app's language setting.

## 🔐 Security

### Credential Management

- **OAuth 2.0**: Authentication handled by Google consent screen
- **Local tokens**: Stored in `config/youtube_token.pickle`
- **Local cookies**: Stored in `config/yt_cookies.txt` for yt-dlp
- **No passwords**: EasyCut never sees or stores your Google password

### Validations

- ✅ YouTube URL validation
- ✅ Time range validation (`_parse_timecode()`) and applied via yt-dlp `download_sections`

---

## 📄 License

This project is licensed under the **GPL-3.0 License** — GNU General Public License v3.0.

---

## 🚀 Development & Contributions

### For Contributors

Interested in contributing? Here's what you need to know:

1. **Get Started**: See [Installation](#installation) section
2. **OAuth Setup**: Follow [OAUTH_SETUP.md](OAUTH_SETUP.md) to create credentials
3. **Development**: Run `python main.py` to test changes
4. **Architecture**: Review [src/](src/) modules and open an issue if you want guidance

### Building Releases

Want to create standalone executables? See [BUILD.md](BUILD.md) for complete instructions.

**Quick build:**
```bash
pip install pyinstaller
python scripts/build.py
```

This creates `dist/EasyCut.exe` with embedded OAuth credentials - ready to distribute!

## 📚 Documentation

### User & Quick Start
- [Getting Started](#getting-started) — Installation and setup
- [BUILD.md](BUILD.md) — Building standalone executables with PyInstaller
- [OAUTH_SETUP.md](OAUTH_SETUP.md) — Creating Google OAuth credentials (developers)

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

**Developed with ❤️ by Deko Costa**

*Download videos. Record live streams. Simple, fast, secure.*

**Repository:** [github.com/dekouninter/EasyCut](https://github.com/dekouninter/EasyCut)  
**Support:** [buymeacoffee.com/dekocosta](https://buymeacoffee.com/dekocosta)  
**Livepix:** [livepix.gg/dekocosta](https://livepix.gg/dekocosta)
