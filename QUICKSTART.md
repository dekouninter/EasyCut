# 🚀 EasyCut - Quick Start Guide

Complete guide for users and developers to get started with EasyCut.

---

## 📥 For End Users (Recommended)

**The easiest way: Download the standalone executable!**

1. Go to [Releases](https://github.com/dekouninter/EasyCut/releases)
2. Download `EasyCut.exe`
3. Run it - that's all! ✨

**No installation needed:**
- ✅ No Python required
- ✅ No dependencies to install
- ✅ No OAuth setup
- ✅ Just download and use

**First time using?**
- Make sure you have installed the Python dependencies via the
  `requirements.txt` file (see installation instructions below) or run
  `python check_installation.py` for a quick sanity check.
- Click "Sync with YouTube" when prompted
- Authorize once in your browser
- Done! Start downloading

> ⚠ **Note for developers:** the 30–40 warnings printed by the Python
> language server are linter/analysis messages and do not prevent the
> program from running. You only need to fix them if you are editing the
> source code.

> Tip: If you edit downloads in Adobe Premiere, enable **Auto-convert for Premiere compatibility** in Settings. The app will try to download MP4/H264 directly or convert files afterward.

### Live tab (v1.7) — quick usage
- Paste a live stream URL and click **Check Stream** to verify availability and show metadata (channel, thumbnail, elapsed time).
- Click **Load Preview** to open the live in the embedded player (supports preview-from-start when available).
- **Start Recording** captures the full broadcast from its beginning (yt-dlp `live_from_start=True`).
- While recording you can mark `Start` and `End` on the player; click **Save Clip** to download the marked clip immediately.
- Use **Quick Cut** (30/60/120s) to instantly download the last N seconds (no confirmation).
- Click **LIVE** to jump to the live edge (seek-to-end). The player supports seeking in growing recording files.
- If a stream requires verification, provide browser cookies (Settings → Cookies) or authenticate with OAuth.

---

## 👨‍💻 For Developers

### ⚡ Installation (5 Minutes)

#### Windows (Recommended)

##### Option 1: Automatic Script

1. Open the EasyCut folder in File Explorer
2. Double-click `START.bat`

It will automatically:
- Create a virtual environment
- Install dependencies
- Launch the application

##### Option 2: Manual Installation

1. **Install Python 3.13+** if you don't have it:
   - Download from: https://www.python.org
   - **Check:** "Add Python to PATH"

2. **Open PowerShell in the project folder:**
   ```powershell
   # Create virtual environment (if you haven't already)
   python -m venv venv

   # Activate it
   .\venv\Scripts\Activate.ps1

   # Install dependencies – this brings in yt-dlp, Pillow, OAuth libs, etc.
   pip install -r requirements.txt

   # OPTIONAL: verify everything is present
   python check_installation.py
   ```

3. **Verify installation:**
   ```powershell
   python check_installation.py
   ```

4. **Setup OAuth credentials** (see section below)

5. **Run the application:**
   ```powershell
   python main.py
   ```

#### Linux/Mac

```bash
# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run
python main.py
```

---

## 🔐 OAuth Setup for Developers

**👤 End Users:** You DON'T need this! OAuth credentials are already embedded in `EasyCut.exe`.

**👨‍💻 Developers:** You NEED this to run from source code.

### OAuth Overview

EasyCut uses Google OAuth 2.0 for secure YouTube authentication:
- **Scope**: `https://www.googleapis.com/auth/youtube.readonly`
- **Purpose**: Read-only access to YouTube metadata and authenticated downloads
- **Files created**:
  - `config/credentials.json` — Your OAuth client credentials (you create this)
  - `config/youtube_token.json` — OAuth token cache (auto-created after login)
  - `config/yt_cookies.txt` — Cookies for yt-dlp (auto-created after login)

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account
3. Create a new project:
   - Click on the project dropdown
   - Click "NEW PROJECT"
   - Enter a name: `EasyCut` (or any name)
   - Click "CREATE"

### Step 2: Enable YouTube Data API

1. Search for "YouTube Data API v3" in the search bar
2. Click on it
3. Click "ENABLE"
4. Wait a few seconds for it to enable

### Step 3: Create OAuth Credentials

1. Go to "Credentials" in the left menu
2. Click "CREATE CREDENTIALS" → "OAuth client ID"
3. If prompted, configure the OAuth consent screen first:
   - User type: "External"
   - Click "CREATE"
   - Fill in the required fields (app name, user support email, etc.)
   - Add scope: `https://www.googleapis.com/auth/youtube.readonly`
   - Click "SAVE & CONTINUE" through all steps
4. Back to OAuth client ID creation:
   - Application type: **"Desktop application"**
   - Name: `EasyCut` (doesn't matter)
   - Click "CREATE"

### Step 4: Download and Place Credentials

1. A popup appears - click **"DOWNLOAD JSON"**
2. Rename the file to `credentials.json`
3. Place it in `config/` folder:
   ```
   EasyCut/
   ├── config/
   │   └── credentials.json    ← Place here
   ├── main.py
   └── ...
   ```

### Step 5: Authenticate in EasyCut

1. Run EasyCut: `python main.py`
2. At the top, you'll see a **"YouTube Authentication"** banner
3. Click **"Sync with YouTube"** button
4. Browser window opens automatically with Google OAuth screen
5. Sign in with your Google account
6. Click **"Allow"** when asked for YouTube read-only permissions
7. You're redirected back - app shows **"✓ Authenticated! Ready to download"** ✅
8. Start downloading videos!

**Note**: Your OAuth tokens are saved locally in `config/` directory. You only authenticate once - subsequent launches use the cached token.

### OAuth Troubleshooting

#### "credentials.json not found"
- **Error**: "oauth_manager: credentials not found in config/"
- **Fix**: Make sure you placed `credentials.json` in `config/` folder
- **Step**: Restart EasyCut after placing the file

#### "OAuth Error: invalid_grant"
- **Cause**: Token expired or credentials revoked
- **Fix**: Click "Logout" in the YouTube Authentication banner, then "Sync with YouTube" again

#### "OAuth Error 403: Access Denied"
- **Cause**: Your OAuth app is in Testing mode and user isn't added as test user
- **Fix** (Option 1): In Google Cloud Console, add your Google account as **Test User**
- **Fix** (Option 2): Publish the OAuth consent screen

#### "Google hasn't verified this app" warning (Testing Mode)
- **Normal for development** - unverified apps show this warning
- **Action**: Click "Advanced" → "Go to EasyCut (unsafe)" to proceed
- **To remove in production**:
  1. Go to Google Cloud Console → OAuth consent screen
  2. Fill all required information (app privacy policy, etc.)
  3. Add yourself as a test user while developing
  4. Publish the app when ready for production

#### "Browser didn't open automatically"
- **Cause**: Windows Firewall or antivirus blocking browser launch
- **Fix**: Manually copy the URL printed to console and paste in browser
- **Status**: Look for "Opening browser..." message in app window

---

## 🔨 Building Releases (Maintainers Only)

### Overview

EasyCut uses a **source-clean** approach:
- **Source code on GitHub**: No credentials - clean and secure
- **Released executables**: Contain embedded OAuth credentials for zero-setup UX

Benefits:
- ✅ Security: No credentials exposed in public repository
- ✅ Convenience: Users download and run immediately
- ✅ Professionalism: GitHub security scanning happy
- ✅ Control: You manage the OAuth project quota

### Prerequisites

```bash
# Install PyInstaller
pip install pyinstaller

# Verify installation
pyinstaller --version
```

### Build Steps

1. **Create `build_config.json`** with your OAuth credentials:

```json
{
  "oauth_credentials": {
    "installed": {
      "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
      "project_id": "your-project-id",
      "auth_uri": "https://accounts.google.com/o/oauth2/auth",
      "token_uri": "https://oauth2.googleapis.com/token",
      "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
      "client_secret": "YOUR_CLIENT_SECRET",
      "redirect_uris": ["http://localhost"]
    }
  },
  "app_version": "1.9.0",
  "app_name": "EasyCut"
}
```

2. **Run the build script**:

```bash
python build.py
```

3. **Find your executable**:

```
dist/EasyCut.exe
```

That's it! 🎉

### What the Build Script Does

1. **Validation**: Checks PyInstaller and `build_config.json`
2. **Prepare**: Creates `build_temp/` with all source files
3. **Embed Credentials**: Modifies `oauth_manager.py` with embedded credentials
4. **Compile**: Runs PyInstaller to create executable
5. **Cleanup**: Removes temporary files, keeps only `dist/EasyCut.exe`

### Security Considerations

**Safe Files (Committed to Git):**
- ✅ `build.py` - Build script (no secrets)
- ✅ `config/credentials_template.json` - Empty template
- ✅ `src/oauth_manager.py` - Loads credentials from file
- ✅ `.gitignore` - Protects secret files

**Secret Files (NOT Committed):**
- ⛔ `build_config.json` - **Contains OAuth credentials!**
- ⛔ `config/youtube_token.json` - OAuth token cache
- ⛔ `config/yt_cookies.txt` - Cookies for yt-dlp
- ⛔ `build_temp/` - Temporary build files
- ⛔ `dist/` - Final executable (has embedded credentials)

**Important Notes:**
1. **Never commit `build_config.json`** - It's in `.gitignore`!
2. **Distribute only via GitHub Releases** - Don't commit executables
3. **OAuth Desktop App credentials** are less secret by design, but we protect them to prevent quota abuse
4. **Users can't abuse credentials** - OAuth requires user consent

### Distribution Workflow

1. **Development**:
   ```bash
   # Use credentials.json during development
   python main.py  # Test locally
   ```

2. **Building Release**:
   ```bash
   # Ensure build_config.json has production credentials
   python build.py
   # Creates dist/EasyCut.exe
   ```

3. **Create GitHub Release**:
   - Go to GitHub → Releases → New Release
   - Tag: `v1.9.0`
   - Upload: `dist/EasyCut.exe`
   - Write release notes
   - Publish

### Build Troubleshooting

#### "PyInstaller not found"
```bash
pip install pyinstaller
```

#### "build_config.json not found"
Create it with your OAuth credentials (see format above).

#### "Module not found" errors
Add hidden imports to `build.py`:
```python
"--hidden-import", "missing_module_name"
```

#### Executable is too large
Normal sizes: 50-100 MB for tkinter + yt-dlp app.
Optimize with:
```python
"--exclude-module", "unnecessary_module"
```

#### Antivirus false positives
Common with PyInstaller. Solutions:
- Sign the executable with code signing certificate
- Submit to antivirus vendors as false positive
- Distribute via GitHub Releases (trusted source)

---

## 📝 First Use

### 1. **Sync with YouTube** (First time)
- Click "Sync with YouTube" button
- Browser opens automatically
- Sign in with Google
- Click "Allow"
- Done! ✅

### 2. **Download Video**
- Open "Download" tab
- Paste YouTube URL
- Click "Check" to see video info
- Choose quality and mode
- Click "Download"

### 3. **Batch Download**
- Open "Batch" tab
- Paste multiple URLs (one per line)
- Click "Download All"

### 4. **Convert Audio**
- Open "Audio" tab
- Paste YouTube URL
- Choose format (MP3, WAV, M4A, OPUS)
- Choose bitrate (128-320 kbps)
- Click "Convert"

---

## ❓ FAQ

### Q: FFmpeg doesn't work
**A:** 
1. Check: `ffmpeg -version`
2. If not found, download from [ffmpeg.org](https://ffmpeg.org/)
3. Add to system PATH
4. Restart application

### Q: Where are my downloads?
**A:** In the `downloads/` folder inside the project directory.

### Q: Can I download playlists?
**A:** Use the "Batch" tab for multiple URLs.

### Q: Is YouTube authentication safe?
**A:** 
- ✅ Official Google OAuth 2.0
- ✅ You authenticate directly with Google (we never see your password)
- ✅ Tokens stored locally and encrypted
- ✅ Revoke access anytime at [myaccount.google.com](https://myaccount.google.com/permissions)

### Q: Do I need OAuth credentials?
**A:**
- **End users (releases):** No! Everything is embedded
- **Developers (from source):** Yes, see OAuth Setup section above

### Q: Which sites work besides YouTube?
**A:** yt-dlp supports 1000+ sites:
- YouTube
- Vimeo
- TikTok
- Instagram
- Twitter
- Twitch
- And many more

---

## 🎯 Main Features

| Feature | Description |
|---------|-------------|
| **Download** | Videos in best quality (WebM formats excluded by default) |
| **Premiere Compatibility** | Auto-convert downloads to MP4/H264 for Adobe Premiere (toggle available in Settings) |
| **Transcript** | Download subtitle transcript with timestamps as TXT |
| **Batch** | Multiple videos at once |
| **Live** | Record live streams with embedded player |
| **Live Clipper** | Mark start/end on seekbar for real-time clipping |
| **Post-Process** | Auto format conversion and trimming |
| **Channel Monitor** | Track channels for new content |
| **Following** | Manage favorite channels |
| **Audio** | Extract audio (MP3, WAV, M4A, OPUS) |
| **Time Range** | Extract only parts of video |
| **Login** | Access restricted content |
| **History** | Track downloads |
| **Themes** | Light/dark mode (instant toggle, Windows Mica backdrop) |
| **Languages** | 7 languages (instant switch) |
| **Visual Design** | SVG icons, 6 accent color families, gradient effects |

---

## 📂 Folder Structure

```
EasyCut/
├── main.py               # Run this to start
├── src/                  # Source code (13 modules)
│   ├── easycut.py       # Main application
│   ├── design_system.py # Design tokens & accent palettes
│   ├── modern_components.py # 16 custom UI widgets
│   ├── icon_renderer.py # SVG → Pillow icon renderer
│   ├── oauth_manager.py # OAuth handling
│   ├── i18n.py          # Translations
│   └── ...
├── config/               # Settings (auto-created)
│   ├── config.json
│   ├── credentials.json  # Your OAuth credentials (devs only)
│   ├── history_downloads.json
│   └── app.log
├── downloads/            # Downloaded files
├── assets/               # Icons and fonts
├── venv/                 # Virtual environment
└── ...
```

---

## 🔐 Security & Privacy

✅ **Secure credentials**: Stored in OS keyring (Windows Credential Manager)  
✅ **Open source**: Full source on GitHub, no data collection  
✅ **Privacy**: Everything runs locally, no external server  
✅ **OAuth**: Direct authentication with Google, we never see your password  

---

## 💡 Tips and Tricks

### Download playlist videos
1. Go to YouTube playlist
2. Open console (F12) and run:
   ```javascript
   Array.from(document.querySelectorAll('a#video-title')).map(e => e.href)
   ```
3. Copy output and paste in "Batch" tab

### High quality audio
1. Use "Audio" tab
2. Select "MP3"
3. Select "320 kbps"

### Download time range (Extract clip from video)

**Complete Video**
- Downloads entire video in original quality
- Use when you want the full content

**Time Range (Extract specific clip)**
1. Go to "Download" tab
2. Select mode: "Time Range"
3. Enter start time (e.g., `00:05:30` or `5:30`)
4. Enter end time (e.g., `00:15:45` or `15:45`)
5. Click Download
- Result: Video file contains only the selected portion

**Until Time (Download up to a point)**
1. Go to "Download" tab
2. Select mode: "Until Time"
3. Enter end time (e.g., `00:10:00`)
4. Click Download
- Result: Video from start to specified time

**Audio-Only + Format Selection**
1. Go to "Download" tab
2. Select mode: "Audio Only"
3. Choose format: MP3, WAV, M4A, or OPUS
4. Choose bitrate: 128, 192, 256, or 320 kbps
5. Click Download
- Result: Pure audio file in selected format

**Time Range Format**: `HH:MM:SS` or `MM:SS`
- Examples: `00:05:30`, `10:45`, `1:30:00`
- Start time must be before end time

---

## 🔌 Advanced: Browser Authentication (Optional)

By default, EasyCut uses **Google OAuth 2.0** for YouTube authentication (recommended).

If you prefer to use browser cookies as an alternative:

### Enable Browser Auth

1. Open `config/config.json` in a text editor
2. Find the line: `"enable_browser_auth": false`
3. Change to: `"enable_browser_auth": true`
4. Save and restart EasyCut

### Using Browser Auth

When enabled, **EasyCut will show both authentication options**:
- **Primary**: Google OAuth (recommended)
- **Alternative**: Browser Cookie Extraction

**Browser Cookie Extraction**:
- Select your browser: Chrome, Firefox, Edge, Opera, Brave, or Safari
- Select your YouTube profile automatically (EasyCut detects profiles)
- Or import cookies.txt file manually
- Test connection before downloading

**When to use Browser Auth**:
- If you have existing browser sessions and want to reuse them
- For specific YouTube account in a specific browser profile
- When OAuth has permission issues

**Note**: OAuth 2.0 is more secure and recommended. Browser auth is optional and disabled by default.

---

## 📞 Support & Contributing

- 🐛 **Report bugs**: [GitHub Issues](https://github.com/dekouninter/EasyCut/issues)
- 💬 **Suggestions**: [GitHub Discussions](https://github.com/dekouninter/EasyCut/discussions)
- 🤝 **Contributing**: Fork the repo, make changes, submit PR
- ❤️ **Support**: [Buy Me a Coffee](https://buymeacoffee.com/dekocosta)

---

## ⌨️ Keyboard Shortcuts

**Tab Navigation:**
- `Ctrl+1` - Download tab
- `Ctrl+2` - Batch tab
- `Ctrl+3` - Live tab
- `Ctrl+4` - Post-Processing tab
- `Ctrl+5` - Following tab
- `Ctrl+6` - Channel Monitor tab
- `Ctrl+7` - History tab
- `Ctrl+8` - About tab

**Application:**
- `Ctrl+T` - Toggle dark/light theme
- `Ctrl+L` - Toggle log panel (show/hide details)
- `Ctrl+O` - Open downloads folder
- `Esc` - Hide log panel (if visible)

---

## 📚 Related Documentation

- [README.md](README.md) - Main documentation and features
- [DOCUMENTATION.md](DOCUMENTATION.md) - Detailed documentation
- [CREDITS.md](CREDITS.md) - Credits and licenses

---

## 📝 Maintenance Checklist (Maintainers)

Before each release:

- [ ] Update version in `build_config.json`
- [ ] Update version in `src/easycut.py` (docstring + logger + status bar)
- [ ] Update version in `src/i18n.py` (all 7 language blocks + about_version_info)
- [ ] Update About tab version in `src/easycut.py`
- [ ] Test locally with `python main.py`
- [ ] Run `python build.py`
- [ ] Test executable on clean Windows machine
- [ ] Create GitHub Release with executable
- [ ] Update release notes

---

**Welcome to EasyCut! 🎉**

*Making downloads simple since 2026*
