# 🎬 EasyCut - Professional YouTube Downloader

## 👨‍💻 Author

**Deko Costa**
- GitHub: [@dekouninter](https://github.com/dekouninter)
- Repository: [EasyCut](https://github.com/dekouninter/EasyCut)

## 📜 License

**GPL-3.0 License** - GNU General Public License v3.0

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

## 🙏 Credits & Acknowledgments

### Core Libraries

#### yt-dlp (Unlicense)
- **Purpose**: YouTube video and audio downloading engine
- **Author**: yt-dlp team
- **Repository**: https://github.com/yt-dlp/yt-dlp
- **License**: Unlicense (Public Domain)
- **Why**: The backbone of EasyCut, providing robust YouTube downloading capabilities

#### FFmpeg (GPL-2.0+)
- **Purpose**: Audio/video processing and audio conversion (MP3, WAV, M4A, OPUS extraction)
- **Project**: FFmpeg team
- **Website**: https://ffmpeg.org/
- **License**: GPL-2.0 or later (with optional components)
- **Why**: Industry-standard tool for audio/video processing

#### Google OAuth Libraries (Apache 2.0)
- **Purpose**: OAuth 2.0 authentication flow and token handling
- **Libraries**: google-auth-oauthlib, google-auth-httplib2, google-auth
- **Repository**: https://github.com/googleapis/google-auth-library-python
- **License**: Apache 2.0
- **Why**: Secure Google OAuth 2.0 integration for YouTube access

#### Requests (Apache 2.0)
- **Purpose**: HTTP requests for OAuth token info and YouTube session
- **Repository**: https://github.com/psf/requests
- **License**: Apache 2.0
- **Why**: Simple, reliable HTTP client

#### Pillow (HPND)
- **Purpose**: Image processing for icons
- **Authors**: Jeffrey A. Clark (Alex) and contributors
- **Repository**: https://github.com/python-pillow/Pillow
- **License**: Historical Permission Notice and Disclaimer (HPND)
- **Why**: Professional icon rendering and image manipulation

### Design & UI Resources

#### Feather Icons (MIT)
- **Purpose**: Beautiful, minimalist icon set
- **Author**: Cole Bemis and contributors
- **Repository**: https://github.com/feathericons/feather
- **Website**: https://feathericons.com/
- **License**: MIT
- **Icons Used**: 
  - download, upload, search, folder, music, video
  - moon, sun, globe, log-in, log-out
  - play-circle, stop-circle, circle, radio
  - layers, clipboard, x-circle, refresh-cw
  - clock, trash-2, external-link, sliders
  - check-circle, alert-triangle, info
  - github, coffee, heart
- **Why**: Clean, consistent iconography that enhances UX

#### Inter Font (OFL)
- **Purpose**: Modern, highly legible typeface
- **Author**: Rasmus Andersson
- **Repository**: https://github.com/rsms/inter
- **Website**: https://rsms.me/inter/
- **License**: SIL Open Font License 1.1
- **Why**: Professional typography designed for user interfaces

### Inspiration & Resources

#### Modern UI Design
- **Tailwind CSS Colors** - Color palette inspiration
- **Material Design 3** - Component design patterns
- **Fluent 2 Design** - Windows 11 design language
- **shadcn/ui** - Modern component library concepts

#### Python Tkinter Community
- **rdbende** - For amazing ttk themes (Azure, Sun-Valley, Forest)
- **TkDocs** - Comprehensive Tkinter documentation
- **Python Tkinter Community** - Support and resources

## 📦 Third-Party Components

### Direct Dependencies
```
yt-dlp >= 2024.3.10
pillow >= 10.0.0
google-auth-oauthlib >= 1.2.0
google-auth-httplib2 >= 0.3.0
requests >= 2.32.0
```

### Bundled Assets
- **Feather Icons** (286 SVG icons) - MIT License
- **Inter Font** (Variable font files) - OFL 1.1
- **App Icon** - Original design by Deko Costa

## 🌐 Open Source Ecosystem

EasyCut is built on the shoulders of giants. We're grateful to the entire open-source community for making tools like this possible.

### Special Thanks To:

1. **yt-dlp Team** - For maintaining the most robust YouTube downloader
2. **FFmpeg Project** - For decades of media processing excellence
3. **Python Software Foundation** - For the amazing Python language
4. **Tkinter/Tcl/Tk Community** - For the cross-platform GUI toolkit
5. **GitHub** - For hosting and collaboration tools
6. **All Contributors** - Everyone who reported bugs, suggested features, or contributed code

## 💝 Support the Project

If you find EasyCut useful, consider:

- ⭐ **Star the repository** on GitHub
- 🐛 **Report bugs** and suggest features
- 📖 **Contribute to documentation**
- 💻 **Submit pull requests**
- ☕ **Buy me a coffee** - Help fund development

### Coffee Donation Links
- **Ko-fi**: https://ko-fi.com/dekocosta
- **Buy Me a Coffee**: https://buymeacoffee.com/dekocosta
- **Pix (Brazil)**: https://livepix.gg/dekocosta

## 📝 Version History

### v1.2.0 (Current)
- OAuth 2.0 authentication with token and cookies storage
- Audio conversion: MP3, WAV, M4A, OPUS with 4 bitrate options
- Time range downloads with yt-dlp download_sections
- Playlist & channel download modes
- Batch downloads with concurrency control (max 3 simultaneous)
- Structured logging with RotatingFileHandler (5MB, 3 backups)
- Graceful shutdown with active download detection
- Download history with search/filter and clear button
- New download history UI with card layout
- Live stream recording flow improvements
- UI refinements and design system cleanup
- Project structure reorganization (src/, scripts/, static/, internal/)

### v1.1.2
- Footer button alignment fixes in collapsed sidebar
- Improved sidebar icon centering
- Hover effect enhancements

### v1.1.1
- Complete UI redesign with modern design system
- Professional color palette (dark/light themes)
- Inter font integration for better typography
- Feather Icons integration (286 icons)
- Full internationalization (EN/PT)
- Improved user experience
- Responsive layout design
- Performance optimizations
- Bug fixes and stability improvements

### Coming Soon
- Smart format selection with fallback
- Thumbnail display in history
- Subtitle downloads (auto + manual, multi-language)
- YouTube Chapters & Shorts support
- Archive mode with duplicate detection
- Live stream enhancements

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines and code of conduct.

### How to Contribute
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Setup
```bash
git clone https://github.com/dekouninter/EasyCut.git
cd EasyCut
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## 📧 Contact

- **GitHub Issues**: https://github.com/dekouninter/EasyCut/issues
- **Discussions**: https://github.com/dekouninter/EasyCut/discussions

## ⚖️ Legal Notice

EasyCut is a tool for personal use. Users are responsible for complying with YouTube's Terms of Service and applicable copyright laws. Do not use this tool to download copyrighted content without permission.

---

**Made with ❤️ by Deko Costa**

*Last updated: February 2026*
