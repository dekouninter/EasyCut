# 🚀 EasyCut - Quick Start

## ⚡ Installation in 5 Minutes

### Windows (Recommended)

#### Option 1: Automatic Script

1. Open PowerShell in the EasyCut folder
2. Run:
   ```powershell
   .\START.bat
   ```

#### Option 2: Manual

1. **Install Python 3.8+** if you don't have it:
   - Download from: https://www.python.org
   - **Check:** "Add Python to PATH"

2. **Open PowerShell in the project folder:**
   ```powershell
   # Create virtual environment
   python -m venv venv
   
   # Activate
   .\venv\Scripts\Activate.ps1
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Install FFmpeg** (optional, but recommended):
   ```powershell
   # Using Chocolatey
   choco install ffmpeg
   
   # Or using winget
   winget install FFmpeg
   ```

4. **Run the application:**
   ```powershell
   python src/easycut.py
   ```

---

## 📝 First Use

### 1. **Login** (Optional)
- Open the "Login" tab
- Enter your YouTube credentials
- Click "Login"

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
**A:** They are in `downloads/` or open the folder via Menu > File > Open Folder

### Q: Can I download playlists?
**A:** Not directly, but use the "Batch" tab for multiple URLs

### Q: Is my YouTube safe?
**A:** 
- Yes, credentials are stored in Windows keyring
- We never save to plaintext files
- You can logout anytime

### Q: Which sites work?
**A:** yt-dlp supports many sites beyond YouTube:
- YouTube
- Vimeo
- TikTok
- Instagram
- And many more...

---

## 🎯 Main Features

| Feature | Description |
|---------|---|
| **Download** | Download videos in best quality |
| **Batch** | Multiple videos simultaneously |
| **Audio** | Extract audio as MP3, WAV, M4A, OPUS |
| **Time Range** | Extract only video parts |
| **Login** | Access restricted content securely |
| **History** | Track your downloads |
| **Themes** | Light/dark interface |
| **Languages** | Portuguese and English |

---

## 📂 Folder Structure

After first run:

```
EasyCut/
├── src/                  # Source code
├── config/               # Settings
│   ├── config.json
│   ├── history_downloads.json
│   └── app.log
├── downloads/            # Downloaded files here
├── venv/                 # Virtual environment
└── ...
```

---

## 🔐 Security

✅ **Secure credentials:**
- Stored in Windows keyring
- Never in txt file

✅ **No malware:**
- Open source (GitHub)
- No data collection

✅ **Privacy:**
- Everything local
- No server

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

## 🎓 Next Steps

1. **Customize theme:**
   - Menu > View > Theme

2. **Change language:**
   - Menu > Language > Português

3. **Change output folder:**
   - Edit `config/config.json`
   - Change `"output_folder"`

---

**Welcome to EasyCut! 🎉**

*Making downloads simple since 2026*
