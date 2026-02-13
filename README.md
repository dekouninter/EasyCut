# 🎬 EasyCut - Professional YouTube Downloader

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
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

---

## 📦 System Requirements

- **Python**: 3.8 or higher
- **FFmpeg**: Required for audio conversion
- **Windows**: Optimized for Windows (uses explorer to open folders)

### Python Dependencies

```
yt-dlp>=2024.3.10
keyring>=24.0.0
```

**Default Settings:**
- Language: **English** (can switch to Portuguese instantly)
- Theme: **Dark** (can toggle instantly)
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
python src/easycut.py
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
├── src/
│   ├── easycut.py              # Main application
│   ├── i18n.py                 # Translation system (EN, PT)
│   ├── ui_enhanced.py          # Enhanced UI components
│   └── donation_system.py      # Donation system
├── config/
│   ├── config.json             # Application settings
│   ├── history_downloads.json  # Download history
│   └── app.log                 # Application log
├── downloads/                  # Default output folder
├── requirements.txt            # Python dependencies
├── README.md                   # This file
└── setup.py                    # (Optional) For packaging
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

### 4. **Audio** 🎵
- Convert videos to audio (MP3, WAV, M4A, OPUS)
- Select bitrate (128, 192, 256, 320 kbps)
- Separate thread processing

### 5. **History** 📜
- View recent downloads
- Date, filename, and status
- Persistent history (last 100 items)

### 6. **About** ℹ️
- Application information
- Credits and licenses
- List of features

---

## ⚙️ Configuration

### config.json

```json
{
  "dark_mode": true,
  "language": "en",
  "output_folder": "downloads",
  "log_level": "INFO"
}
```

**Options:**
- `dark_mode`: true (dark) or false (light)
- `language`: "en" (English) or "pt" (Portuguese)
- `output_folder`: Output folder path

---

## 🔐 Security

### Credential Management

- **Windows Keyring**: Credentials stored securely
- **No plaintext files**: Passwords never saved to file
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

This project is licensed under the **MIT License** - see [LICENSE](LICENSE) for details.

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

- **yt-dlp**: YouTube video downloading tool
- **FFmpeg**: Media conversion and processing
- **Keyring**: Secure credential storage
- **Python & Tkinter**: Programming language and GUI framework

---

## 🔄 Version History

### v1.0.0 - 2024-02-13
- Initial complete version
- 6 functional tabs
- Multi-language support (EN, PT)
- Donation system
- Secure credential management
- Hot-reload theme/language switching
- Professional UI/UX

---

## 📖 Additional Resources

- [yt-dlp Documentation](https://github.com/yt-dlp/yt-dlp)
- [Tkinter Documentation](https://docs.python.org/3/library/tkinter.html)
- [FFmpeg Documentation](https://ffmpeg.org/documentation.html)

---

**Developed with ❤️ by Deko Costa**

*Download videos. Convert audio. Simple, fast, secure.*

**Repository:** [github.com/dekouninter/EasyCut](https://github.com/dekouninter/EasyCut)  
**Support:** [buymeacoffee.com/dekocosta](https://buymeacoffee.com/dekocosta)  
**Livepix:** [livepix.gg/dekocosta](https://livepix.gg/dekocosta)
