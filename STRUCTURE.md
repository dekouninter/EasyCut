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
│   ├── config.json         # User settings (output folder, language)
│   ├── credentials.json    # OAuth credentials (gitignored)
│   └── history_downloads.json  # Download history
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
│   ├── REFACTORING_PLAN.md # Development planning
│   ├── ROADMAP.md          # Feature roadmap
│   ├── TESTING_SPRINT4.md  # Testing guides
│   └── ...                 # Other internal notes
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
│   ├── i18n.py             # Internationalization (EN/PT)
│   ├── ui_enhanced.py      # Enhanced UI components
│   ├── design_system.py    # Design system constants
│   ├── modern_components.py # Modern UI widgets
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
└── 📄 TERMS.md             # Terms of service (Markdown)
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
- `PRIVACY.md`, `TERMS.md` - Legal docs

**Internal** (gitignored, in `internal/`):
- Sprint testing guides
- Refactoring plans
- Development roadmaps
- Feature planning documents

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
- `REFACTORING_PLAN.md` → `internal/REFACTORING_PLAN.md`
- `TESTING_*.md` → `internal/TESTING_*.md`

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

**Last Updated:** Sprint 4 Refactoring (February 2026)
