# 🎬 EasyCut - Professional YouTube Downloader

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-GPL--3.0-blue.svg)
![Author](https://img.shields.io/badge/author-Deko%20Costa-brightgreen.svg)

**EasyCut** is a professional desktop application for downloading YouTube videos and converting audio, built with Python and Tkinter.

**Author:** Deko Costa  
**Repository:** [github.com/dekouninter/EasyCut](https://github.com/dekouninter/EasyCut)

### ✨ Key Features

- ✅ **Video Download**: Download YouTube videos individually or in batch
- ✅ **Audio Extraction**: Convert videos to MP3, WAV, M4A, or OPUS
- ✅ **Time Range**: Extract only specific parts of videos
- ✅ **Multiple Formats**: Support for different qualities and formats
- ✅ **Credential Management**: Store credentials securely via keyring
- ✅ **Light/Dark Theme**: Customizable interface themes (instant hot-reload)
- ✅ **Multi-Language**: Support for English and Portuguese (instant hot-reload)
- ✅ **Download History**: Track your recent downloads
- ✅ **Real-Time Logs**: Monitor operation progress
- ✅ **Donation Buttons**: Support the developer
- ✅ **Icon Branding**: Accent colors extracted from the app icon
- ✅ **Custom Fonts**: Inter Display with Segoe UI fallback

---

## 📦 System Requirements

- **Python**: 3.8 or higher
- **FFmpeg**: Required for audio conversion
- **Windows**: Optimized for Windows (uses Windows GDI for fonts, explorer for folders)

### Python Dependencies

```
yt-dlp>=2024.3.10
keyring>=24.0.0
pillow>=10.0.0
```

**Default Settings:**
- Language: **English** (can switch to Portuguese instantly)
- Theme: **Light** (can toggle to Dark instantly)
- Login: **Pop-up only** (clean and simple)

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

### 4. Install FFmpeg

**Windows (using Chocolatey):**
```powershell
choco install ffmpeg
```

**Windows (using winget):**
```powershell
winget install FFmpeg
```

**Or download manually:** [ffmpeg.org](https://ffmpeg.org/download.html)

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

---

## 📚 Folder Structure

```
EasyCut/
├── main.py                     # Entry point (sets icon, launches app)
├── requirements.txt            # Dependencies: yt-dlp, keyring, pillow
├── setup.py                    # Packaging script (setuptools)
├── START.bat                   # Windows launcher (auto-creates venv)
├── run.bat                     # Alternative launcher (checks FFmpeg)
│
├── src/                        # Application source code (~8,450 lines)
│   ├── easycut.py              # Main application class (EasyCutApp)
│   ├── i18n.py                 # Translation system (EN + PT, 150+ keys)
│   ├── design_system.py        # Design tokens, palettes, typography
│   ├── modern_components.py    # Custom widgets (Button, Card, Alert, etc.)
│   ├── ui_enhanced.py          # ConfigManager, LogWidget, LoginPopup
│   ├── color_extractor.py      # Extracts brand colors from app icon
│   ├── font_loader.py          # Loads Inter font via Windows GDI
│   ├── icon_manager.py         # Icon loading with emoji fallback
│   ├── donation_system.py      # Donation window and button
│   │
│   ├── core/                   # Foundation: config, logger, exceptions
│   ├── theme/                  # ThemeManager (dark/light)
│   ├── ui/
│   │   ├── factories/          # Widget & Tab factories (DRY)
│   │   └── screens/            # 7 screen implementations
│   └── services/               # BaseService (abstract only)
│
├── assets/                     # Static assets
│   ├── app_icon.png            # Application icon (PNG)
│   ├── headerapp_icon.ico      # Window icon (ICO)
│   ├── fonts/Inter/            # Inter Display font files (TTF)
│   └── feather-main/           # Feather icon source (SVG)
│
├── config/                     # Runtime configuration (auto-created)
│   ├── config.json             # User settings
│   ├── history_downloads.json  # Download history
│   └── app.log                 # Application log
│
└── downloads/                  # Default output folder
```

---

## 🎯 Interface Tabs

### 1. **Login** 🔐
- Secure user authentication
- Credential storage via keyring
- Login status display

### 2. **Download** ⬇️
- Download individual YouTube videos
- Select quality (Best, MP4, Audio Only)
- Extract specific time ranges
- "Until Time" mode for time-based cuts

### 3. **Batch** 📦
- Download multiple videos at once
- Paste URLs from clipboard
- Dedicated progress logging

### 4. **Live** 📡
- Record live streams
- Monitor stream status

### 5. **Audio** 🎵
- Convert videos to audio (MP3, WAV, M4A, OPUS)
- Select bitrate (128, 192, 256, 320 kbps)
- Separate thread processing

### 6. **History** 📜
- View recent downloads
- Card-based display with date, filename, status
- Persistent history (JSON)

### 7. **About** ℹ️
- Application information
- Credits and licenses
- Donation links

---

## ⚙️ Configuration

### config.json

```json
{
  "dark_mode": false,
  "language": "en",
  "output_folder": "downloads",
  "log_level": "INFO"
}
```

**Options:**
- `dark_mode`: `true` (dark) or `false` (light)
- `language`: `"en"` (English) or `"pt"` (Portuguese)
- `output_folder`: Output folder path
- `log_level`: Logging verbosity (`"DEBUG"`, `"INFO"`, `"WARNING"`, `"ERROR"`)

---

## 🔐 Security

### Credential Management

- **Windows Keyring**: Credentials stored securely in Windows Credential Manager
- **No plaintext files**: Passwords never saved to disk
- **"Remember" option**: Save credentials for quick access

### Validations

- ✅ YouTube URL validation
- ✅ Email format validation
- ✅ Time format validation (MM:SS)
- ✅ Time limits verification

---

## 📝 Logs

Logs are saved in `config/app.log`:

```
[2024-02-13 14:30:45] [INFO] Application started successfully
[2024-02-13 14:31:12] [INFO] Download started: https://www.youtube.com/watch?v=...
[2024-02-13 14:32:50] [INFO] Download completed: "Video Title"
```

---

## 🤝 Support & Donations

This is an open-source project. If you enjoy EasyCut, please consider supporting:

- ☕ [Buy Me a Coffee](https://buymeacoffee.com/dekocosta)
- 🎁 [Livepix](https://livepix.gg/dekocosta)

---

## 🐛 Troubleshooting

### FFmpeg not found

If audio conversion doesn't work:

1. Verify FFmpeg is installed: `ffmpeg -version`
2. Add FFmpeg to Windows environment variables
3. Restart the application

### yt-dlp Error

```bash
pip install --upgrade yt-dlp
```

### Theme Issues

Themes are applied on startup. If it doesn't work:

1. Delete `config/config.json`
2. Restart the application

### Credentials not saving

Verify keyring is installed correctly:

```bash
pip install --upgrade keyring
```

---

## 📄 License

This project is licensed under the **GPL-3.0 License** — GNU General Public License v3.0. See [CREDITS.md](CREDITS.md) for details.

---

## 👥 Contributing

Contributions are welcome! To contribute:

1. Fork the project
2. Create a branch for your feature (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📞 Support & Contact

Report bugs or suggest features:

- 🐛 [GitHub Issues](https://github.com/dekouninter/EasyCut/issues)
- 💬 [GitHub Discussions](https://github.com/dekouninter/EasyCut/discussions)

---

## 🎓 Credits

- **yt-dlp**: YouTube video downloading engine
- **FFmpeg**: Media conversion and processing
- **Keyring**: Secure credential storage
- **Pillow**: Image processing for icons and color extraction
- **Inter Font**: Modern typography by Rasmus Andersson
- **Python & Tkinter**: Programming language and GUI framework

---

## 🔄 Version History

### v1.0.0 - Current
- ✨ Complete UI redesign with modern design system
- 🎨 Professional color palette (dark/light themes)
- 🔤 Inter Display font integration
- 🌐 Full internationalization (EN/PT) with hot-reload
- 🎯 7 functional tabs
- 🔐 Secure credential management via keyring
- 📦 Batch download support
- 📡 Live stream recording
- 🎵 Audio conversion (MP3, WAV, M4A, OPUS)
- ☕ Donation system

### Coming Soon
- 🎬 Playlist support
- 📹 Multiple simultaneous downloads
- 🎨 Custom themes
- 🌍 More language support
- 📊 Download statistics

---

## 📖 Additional Resources

- [ARCHITECTURE.md](ARCHITECTURE.md) — Architecture overview and module map
- [TECHNICAL.md](TECHNICAL.md) — Technical deep dive (threading, config, security)
- [REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md) — Refactoring status and metrics
- [QUICKSTART.md](QUICKSTART.md) — 5-minute setup guide
- [CREDITS.md](CREDITS.md) — Credits and licenses
- [yt-dlp Documentation](https://github.com/yt-dlp/yt-dlp)
- [FFmpeg Documentation](https://ffmpeg.org/documentation.html)

---

**Developed with ❤️ by Deko Costa**

*Download videos. Convert audio. Simple, fast, secure.*

**Repository:** [github.com/dekouninter/EasyCut](https://github.com/dekouninter/EasyCut)  
**Support:** [buymeacoffee.com/dekocosta](https://buymeacoffee.com/dekocosta)  
**Livepix:** [livepix.gg/dekocosta](https://livepix.gg/dekocosta)
