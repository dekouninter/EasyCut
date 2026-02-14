# 🚀 EasyCut - Quick Start

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
- Click "Sync with YouTube" when prompted
- Authorize once in your browser
- Done! Start downloading

---

## 👨‍💻 For Developers (Running from Source)

### ⚡ Installation in 5 Minutes

#### Windows (Recommended)

##### Option 1: Automatic Script

1. Open the EasyCut folder in File Explorer
2. Double-click `START.bat`

It will automatically:
- Create a virtual environment
- Install dependencies
- Launch the application

##### Option 2: Manual

1. **Install Python 3.8+** if you don't have it:
   - Download from: https://www.python.org
   - **Check:** "Add Python to PATH"

2. **Open PowerShell in the project folder:**
   ```powershell
   # Create virtual environment
   python -m venv venv
4. **Setup OAuth** (Developers only - see [OAUTH_SETUP.md](OAUTH_SETUP.md)):
   - Create Google Cloud project
   - Enable YouTube Data API
   - Download credentials.json
   - Place in `config/` folder

5. **Run the application:**
   ```powershell
   python main.py
   ```

---

## 📝 First Use

### 1. **Sync with YouTube** (First time)
- Click "Sync with YouTube" button at the top
- Your browser opens automatically
- Sign in with your Google account
- Click "Allow" when asked
- Done! You're authenticated ✅

### 2. **Download Video**
- Open the "Download" tab
- Paste the YouTube URL
- Click "Check" to see information
- Choose quality and mode
- Click "Download"

### 3. **Batch Download**
- Open the "Batch" tab
- Paste multiple URLs (one per line)
- Click "Download All"

### 4. **Convert Audio**
- Open the "Audio" tab
- Paste YouTube URL
- Choose format (MP3, WAV, M4A, OPUS)
- Choose bitrate (128-320 kbps)
- Click "Convert"

---

## ❓ Frequently Asked Questions

### Q: FFmpeg doesn't work
**A:** 
1. Check: `ffmpeg -version`
2. If not found, install via Chocolatey or manually
3. Restart the application

### Q: Where are my downloads?
**A:** They are in the `downloads/` folder inside the project directory.

### Q: Can I download playlists?
**A:** Not directly, but use the "Batch" tab for multiple URLs.

### Q: Is YouTube authentication safe?
**A:** 
- Yes! We use official Google OAuth 2.0
- You authenticate directly with Google
- We never see your password
- Tokens are stored locally and encrypted
- You can revoke access anytime at [myaccount.google.com](https://myaccount.google.com/permissions)

### Q: Do I need OAuth credentials?
**A:**
- **End users (releases):** No! Everything is embedded
- **Developers (from source):** Yes, see [OAUTH_SETUP.md](OAUTH_SETUP.md)

### Q: "Google hasn't verified this app" warning?
**A:** Normal for unverified apps. Click "Advanced" → "Go to EasyCut (unsafe)" to continue. See [OAUTH_FIX.md](OAUTH_FIX.md) for details.

### Q: Which sites work?
**A:** yt-dlp supports many sites beyond YouTube:
- YouTube
- Vimeo
- TikTok
- Instagram
- And 1000+ more sites

---

## 🎯 Main Features

| Feature | Description |
|---------|-------------|
| **Download** | Download videos in best quality |
| **Batch** | Multiple videos at once |
| **Live** | Record live streams |
| **Audio** | Extract audio as MP3, WAV, M4A, OPUS |
| **Time Range** | Extract only video parts |
| **Login** | Access restricted content securely |
| **History** | Track your downloads |
| **Themes** | Light/dark interface (instant toggle) |
| **Languages** | Portuguese and English (instant switch) |

---

## 📂 Folder Structure

After first run:

```
EasyCut/
├── main.py               # Run this to start the app
├── src/                   # Source code
├── config/                # Settings (auto-created)
│   ├── config.json
│   ├── history_downloads.json
│   └── app.log
├── downloads/             # Downloaded files here
├── venv/                  # Virtual environment
└── ...
```

---

## 🔐 Security

✅ **Secure credentials:**
- Stored in Windows Credential Manager
- Never in plaintext files

✅ **Open source:**
- Full source on GitHub
- No data collection

✅ **Privacy:**
- Everything runs locally
- No external server

---

## 🛠️ Verify Installation

```bash
python check_installation.py
```

This checks:
- ✓ Python version
- ✓ yt-dlp installed
- ✓ Keyring installed
- ✓ FFmpeg available
- ✓ Folder structure

---

## 💡 Tips and Tricks

### Download complete series/playlists
1. Go to the playlist on YouTube
2. Open console (F12) and run:
   ```javascript
   Array.from(document.querySelectorAll('a#video-title')).map(e => e.href)
   ```
3. Paste in "Batch" tab

### Convert to MP3 with 320kbps
1. Use the "Audio" tab
2. Select "MP3"
3. Select "320 kbps"

### Download only 30 seconds
1. Tab "Download"
2. Mode: "Until Time"
3. Type: "00:30"

---

## 📞 Support

- 🐛 **Bugs**: [GitHub Issues](https://github.com/dekouninter/EasyCut/issues)
- 💬 **Suggestions**: [GitHub Discussions](https://github.com/dekouninter/EasyCut/discussions)
- ❤️ **Support**: [Buy Me a Coffee](https://buymeacoffee.com/dekocosta)

---

**Welcome to EasyCut! 🎉**

*Making downloads simple since 2026*
