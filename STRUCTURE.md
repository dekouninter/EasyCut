# 📁 Project Structure

EasyCut follows a professional, organized directory structure for better maintainability and scalability.

## Directory Layout

```
EasyCut/
├── 📂 assets/              # Static resources (fonts, icons)
│   ├── fonts/              # Inter font family
│   └── feather-main/       # Feather icon library
│
├── 📂 config/              # Configuration files
│   ├── config.json         # User settings (theme, language, output folder)
│   ├── credentials.json    # OAuth credentials (gitignored)
│   ├── credentials_template.json # OAuth credentials template
│   ├── history_downloads.json  # Download history (max 100 entries)
│   ├── download_archive.txt # Archive of downloaded video IDs (gitignored)
│   ├── youtube_token.pickle # OAuth token cache (gitignored)
│   ├── yt_cookies.txt      # Cookies for yt-dlp auth (gitignored)
│   └── app.log             # Application logs (gitignored)
│
├── 📂 docs/                # Public documentation (committed to Git)
│   └── (reserved for future documentation)
│
├── 📂 downloads/           # Default download directory
│
├── 📂 examples/            # Usage examples
│
├── 📂 internal/            # Internal documentation (NOT in Git)
│   ├── README.md           # Internal docs guide
│   └── TESTING.md          # Internal copy of testing guide
│
├── 📂 scripts/             # Build & utility scripts
│   ├── build.py            # PyInstaller build script
│   ├── setup.py            # Package setup
│   ├── check_installation.py  # Dependency verification
│   ├── START.bat           # Windows quick launcher
│   └── run.bat             # Alternative launcher
│
├── 📂 src/                 # Python source code
│   ├── easycut.py          # Main application logic
│   ├── oauth_manager.py    # OAuth authentication
│   ├── i18n.py             # Internationalization (7 languages: EN/PT/ES/FR/DE/IT/JA)
│   ├── ui_enhanced.py      # Enhanced UI components
│   ├── design_system.py    # Design system v2.0 (ColorPalette, Typography, Spacing, Elevation, BorderRadius, ModernTheme)
│   ├── modern_components.py # Modern UI widgets (ModernButton, ModernCard, SectionHeader, StatusDot, Tooltip, Badge, Divider)
│   ├── icon_manager.py     # Icon management
│   ├── font_loader.py      # Font loading
│   └── donation_system.py  # Donation integration
│
├── 📂 static/              # Static HTML files
│   ├── index.html          # Landing page
│   ├── PRIVACY.html        # Privacy policy
│   ├── TERMS.html          # Terms of service
│   └── googlec68254c22a63edb3.html  # Google verification
│
├── 📂 dist/                # Built executables (gitignored)
├── 📂 venv/                # Python virtual environment (gitignored)
│
├── 📄 .gitignore           # Git ignore rules
├── 📄 BUILD.md             # Build instructions
├── 📄 CREDITS.md           # Attribution & credits
├── 📄 DOCUMENTATION.md     # Documentation hub
├── 📄 EasyCut.spec         # PyInstaller spec
├── 📄 main.py              # Application entry point
├── 📄 OAUTH_SETUP.md       # OAuth setup guide
├── 📄 PRIVACY.md           # Privacy policy (Markdown)
├── 📄 README.md            # Main README
├── 📄 requirements.txt     # Python dependencies
├── 📄 STRUCTURE.md         # Project structure (this file)
├── 📄 TERMS.md             # Terms of service (Markdown)
└── 📄 TESTING.md           # Manual test cases for all features
```

## Key Principles

### 🔒 Separation of Concerns
- **Source code** (`src/`) - Python application logic
- **Scripts** (`scripts/`) - Build, setup, and utility scripts
- **Static assets** (`static/`) - HTML for website/OAuth
- **Internal docs** (`internal/`) - Development planning (not public)
- **Public docs** (root `.md` files) - User-facing documentation

### 🚫 Git Ignore Strategy
- `internal/` - All internal documentation excluded from Git
- `config/credentials.json` - OAuth secrets never committed
- `dist/`, `venv/`, `__pycache__/` - Build artifacts ignored
- `build_config.json` - Build credentials gitignored

### 📝 Documentation Organization
**Public** (committed to Git):
- `README.md` - Getting started guide
- `BUILD.md` - Build & distribution guide
- `OAUTH_SETUP.md` - OAuth configuration
- `DOCUMENTATION.md` - Documentation index
- `TESTING.md` - Manual test cases
- `STRUCTURE.md` - Project layout (this file)
- `CREDITS.md` - Attribution & credits
- `PRIVACY.md`, `TERMS.md` - Legal docs

**Internal** (gitignored, in `internal/`):
- Development notes and testing guides

### 🛠️ Scripts Organization
All executable scripts moved to `scripts/` folder:
- Use `python scripts/build.py` instead of `python build.py`
- Use `scripts\START.bat` instead of `START.bat`
- Scripts automatically change to project root when executed

## Migration Notes

### Updated Paths
If you're updating from an older version, note these path changes:

**Old** → **New**
- `build.py` → `scripts/build.py`
- `setup.py` → `scripts/setup.py`
- `check_installation.py` → `scripts/check_installation.py`
- `START.bat` → `scripts/START.bat`
- `run.bat` → `scripts/run.bat`
- `index.html` → `static/index.html`
- `PRIVACY.html` → `static/PRIVACY.html`
- `TERMS.html` → `static/TERMS.html`

### Commands Updated
Documentation now uses updated paths:
```bash
# Old
python build.py
python check_installation.py

# New
python scripts/build.py
python scripts/check_installation.py
```

## Benefits

✅ **Professional** - Industry-standard project layout  
✅ **Scalable** - Easy to add new modules/scripts  
✅ **Clean** - No clutter in project root  
✅ **Secure** - Clear separation of public/internal files  
✅ **Maintainable** - Logical grouping of related files  

---

**Last Updated:** v1.4.0 (February 2026)
