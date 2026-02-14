# 🏗️ EasyCut - Architecture Documentation

## 📋 Table of Contents

1. [Overview](#overview)
2. [Project Structure](#project-structure)
3. [Module Map](#module-map)
4. [Application Layers](#application-layers)
5. [Data Flow](#data-flow)
6. [Design Patterns](#design-patterns)
7. [Theme System](#theme-system)
8. [Internationalization](#internationalization)
9. [Extension Guide](#extension-guide)

---

## 📌 Overview

EasyCut is a professional desktop YouTube downloader and audio converter built with **Python 3.8+** and **Tkinter**. The application uses a modular architecture with multiple specialized modules, each handling a distinct concern.

### Architecture Summary

| Concern | Module(s) | Lines |
|---------|-----------|------:|
| Main orchestrator | `easycut.py` | 1,868 |
| UI components | `modern_components.py` | 621 |
| Translations (EN/PT) | `i18n.py` | 565 |
| UI infrastructure | `ui_enhanced.py` | 534 |
| Design tokens & palette | `design_system.py` | 515 |
| Theme engine (unified) | `theme/theme_manager.py` | 376 |
| **OAuth authentication** | **`oauth_manager.py`** | **291** |
| Widget factories | `ui/factories/` | 646 |
| Screen classes (7 tabs) | `ui/screens/` | 1,612 |
| Core foundation | `core/` | 675 |
| Icon management | `icon_manager.py` | 290 |
| Donation UI | `donation_system.py` | 199 |
| Color extraction | `color_extractor.py` | 197 |
| Service base class | `services/base_service.py` | 193 |
| Font loading | `font_loader.py` | 147 |
| **Total src/** | | **~8,740** |

### Key Principles

- **Separation of Concerns** — Each module handles one domain
- **Factory Pattern** — Consistent widget creation via factories
- **Hot-Reload** — Theme and language switch instantly without restart
- **Secure Credentials** — Passwords stored via OS keyring, never in plaintext
- **Icon Branding** — Colors extracted from app icon for cohesive design

---

## 🗂️ Project Structure

```
EasyCut/
├── main.py                         # Entry point (sets window icon, launches app)
├── build.py                        # Build script for standalone executables (PyInstaller)
├── requirements.txt                # Dependencies: yt-dlp, keyring, pillow, oauth
├── setup.py                        # Packaging script (setuptools)
├── START.bat                       # Windows launcher (auto-creates venv)
├── run.bat                         # Alternative launcher (checks FFmpeg)
├── check_installation.py           # Verifies dependencies and structure
├── test_import.py                  # Smoke test for module imports
│
├── src/                            # All application source code
│   ├── __init__.py                 # Package init (version, author)
│   ├── easycut.py                  # Main application class (EasyCutApp)
│   ├── oauth_manager.py            # OAuth 2.0 authentication manager
│   ├── i18n.py                     # Translation engine (EN + PT, 150+ keys)
│   ├── design_system.py            # Design tokens, palettes, typography
│   ├── modern_components.py        # Custom widgets (Button, Card, Alert, etc.)
│   ├── ui_enhanced.py              # ConfigManager, LogWidget, LoginPopup, etc.
│   ├── color_extractor.py          # Extracts brand colors from app icon
│   ├── font_loader.py              # Loads Inter font via Windows GDI
│   ├── icon_manager.py             # Icon loading with emoji fallback
│   ├── donation_system.py          # Donation window and button
│   │
│   ├── core/                       # Foundation layer
│   │   ├── config.py               # ConfigManager (dot notation, hot-reload)
│   │   ├── constants.py            # Constants, TranslationKeys
│   │   ├── logger.py               # Structured colored logging
│   │   └── exceptions.py           # Custom exception hierarchy
│   │
│   ├── theme/                      # Theme layer
│   │   └── theme_manager.py        # ThemeManager (dark/light, TTK styling)
│   │
│   ├── ui/
│   │   ├── factories/              # Widget creation factories
│   │   │   ├── widget_factory.py   # ButtonFactory, FrameFactory, InputFactory
│   │   │   └── tab_factory.py      # TabFactory (scrollable tabs)
│   │   │
│   │   └── screens/                # Tab screen implementations
│   │       ├── base_screen.py      # Abstract base class for all screens
│   │       ├── login_screen.py     # Login & credential management
│   │       ├── download_screen.py  # Single video download
│   │       ├── batch_screen.py     # Multi-URL batch download
│   │       ├── live_screen.py      # Live stream recording
│   │       ├── audio_screen.py     # Audio extraction/conversion
│   │       ├── history_screen.py   # Download history display
│   │       └── about_screen.py     # App info and credits
│   │
│   └── services/                   # Service layer (base only)
│       └── base_service.py         # BaseService ABC + ServiceResult
│
├── assets/                         # Static assets
│   ├── app_icon.png                # Application icon (PNG)
│   ├── headerapp_icon.ico          # Window icon (ICO)
│   ├── fonts/Inter/                # Inter Display font files (TTF)
│   └── feather-main/              # Feather icon source (SVG)
│
├── config/                         # Runtime configuration (auto-created)
│   ├── config.json                 # User settings (theme, language, paths)
│   ├── credentials.json            # OAuth credentials (developers only - gitignored)
│   ├── credentials_template.json   # Template for OAuth credentials
│   ├── youtube_token.pickle        # Saved OAuth tokens (gitignored)
│   ├── history_downloads.json      # Download history entries
│   └── app.log                     # Application log file
│
├── downloads/                      # Default output folder
├── scripts/convert_icons.py        # Utility: convert SVG icons to PNG
├── examples/demo_icons.py          # Demo: icon system showcase
│
└── docs/                           # Documentation
    ├── README.md                   # Main documentation
    ├── BUILD.md                    # Building standalone executables
    ├── OAUTH_SETUP.md              # OAuth credentials setup (developers)
    ├── VERIFICATION_CHECKLIST.md   # Google OAuth verification guide
    ├── PRIVACY.md                  # Privacy policy
    ├── TERMS.md                    # Terms of service
    ├── OAUTH_FIX.md               # OAuth troubleshooting
    ├── ARCHITECTURE.md             # This file
    ├── TECHNICAL.md                # Technical deep dive
    ├── QUICKSTART.md               # 5-minute quick start
    └── CREDITS.md                  # Credits and licenses
```

---

## 🧩 Module Map

### Entry & Orchestration

| Module | Purpose | Key Exports |
|--------|---------|-------------|
| `main.py` | Sets window icon, creates Tk root, launches `EasyCutApp` | `main()` |
| `easycut.py` | Main application: header, tabs, download logic, thread management | `EasyCutApp` |

### UI Infrastructure

| Module | Purpose | Key Exports |
|--------|---------|-------------|
| `modern_components.py` | Custom widgets built on Canvas/Frame | `ModernButton`, `ModernCard`, `ModernInput`, `ModernAlert`, `ModernDialog`, `ModernIconButton`, `ModernTabHeader` |
| `ui_enhanced.py` | Original UI utilities still in active use | `ConfigManager`, `LogWidget`, `StatusBar`, `LoginPopup`, `LanguageSelector`, `Theme` |
| `donation_system.py` | Donation modal and floating button | `DonationWindow`, `DonationButton` |

### Design & Theming

| Module | Purpose | Key Exports |
|--------|---------|-------------|
| `design_system.py` | Design tokens: color palettes, typography scales, spacing, icon mapping. Uses icon-branded accent colors | `ColorPalette`, `ModernTheme`, `DesignTokens`, `Typography`, `Spacing`, `Icons` |
| `theme/theme_manager.py` | Unified theme engine with TTK style application | `ThemeManager` |
| `color_extractor.py` | Extracts vibrant/dominant colors from `app_icon.png` for branding | `extract_vibrant_colors()`, `get_theme_palette_from_icon()` |
| `font_loader.py` | Loads Inter Display font via Windows GDI, falls back to Segoe UI | `setup_fonts()`, `LOADED_FONT_FAMILY` |
| `icon_manager.py` | Loads PNG icons with automatic emoji fallback rendering | `IconManager`, `get_ui_icon()` |

### Core Foundation

| Module | Purpose | Key Exports |
|--------|---------|-------------|
| `core/config.py` | JSON config with defaults, dot notation, hot-reload | `ConfigManager` |
| `core/constants.py` | Centralized constants and translation key names | `Constants`, `TranslationKeys` |
| `core/logger.py` | Structured colored logging (console + file) | `Logger`, `get_logger()` |
| `core/exceptions.py` | Custom exception hierarchy with context | `EasyCutException`, `DownloadException`, `AudioException`, `ConfigException`, `AuthException` |

### UI Layer

| Module | Purpose | Key Exports |
|--------|---------|-------------|
| `ui/factories/widget_factory.py` | Factories for buttons, frames, inputs, dialogs | `ButtonFactory`, `FrameFactory`, `CanvasScrollFactory`, `DialogFactory`, `InputFactory` |
| `ui/factories/tab_factory.py` | Factory for scrollable tab containers | `TabFactory`, `create_tab()`, `create_tab_section()` |
| `ui/screens/base_screen.py` | Abstract base for all screen tabs | `BaseScreen` |
| `ui/screens/*.py` | 7 individual tab implementations | `LoginScreen`, `DownloadScreen`, `BatchScreen`, `LiveScreen`, `AudioScreen`, `HistoryScreen`, `AboutScreen` |

### Service Layer

| Module | Purpose | Key Exports |
|--------|---------|-------------|
| `services/base_service.py` | Abstract base for services + typed result class | `BaseService`, `ServiceResult` |

> **Note:** Concrete service implementations (download, audio, etc.) are planned but not yet extracted from `easycut.py`. All business logic currently lives in the main application class.

### Internationalization

| Module | Purpose | Key Exports |
|--------|---------|-------------|
| `i18n.py` | EN + PT translations with hot-reload | `Translator`, `translator` (singleton instance) |

---

## 🏢 Application Layers

```
┌────────────────────────────────────────────────────┐
│  main.py (Entry Point)                             │
│  Sets icon → Creates Tk → Launches EasyCutApp      │
└──────────────────────┬─────────────────────────────┘
                       │
┌──────────────────────▼─────────────────────────────┐
│  easycut.py (Orchestrator — 1,868 lines)           │
│  ┌─────────────┐ ┌──────────┐ ┌──────────────┐    │
│  │ Header Bar  │ │ Tab Mgmt │ │ Business     │    │
│  │ Theme Toggle│ │ 7 Tabs   │ │ Logic:       │    │
│  │ Lang Select │ │          │ │ - Download   │    │
│  │ Folder Btns │ │          │ │ - Batch      │    │
│  └─────────────┘ └──────────┘ │ - Audio      │    │
│                                │ - Live       │    │
│                                │ - History    │    │
│                                │ - Auth       │    │
│                                └──────────────┘    │
└─┬────────┬───────────┬───────────┬─────────────────┘
  │        │           │           │
  ▼        ▼           ▼           ▼
┌──────┐ ┌──────────┐ ┌────────┐ ┌──────────────┐
│Design│ │Modern    │ │UI      │ │Screens       │
│System│ │Components│ │Enhanced│ │(base + 7)    │
│ 515L │ │ 621L     │ │ 534L   │ │ 1,612L       │
└──┬───┘ └──────────┘ └────────┘ └──────────────┘
   │
   ▼
┌──────────────┐  ┌───────────┐  ┌───────────┐
│Color         │  │Font       │  │Icon       │
│Extractor 197L│  │Loader 147L│  │Manager 290L│
└──────────────┘  └───────────┘  └───────────┘
        │
        ▼
┌──────────────────┐  ┌──────────────────────┐
│ Core (675L)      │  │ Theme (376L)         │
│ Config, Logger   │  │ ThemeManager         │
│ Exceptions       │  │ TTK Styling          │
│ Constants        │  └──────────────────────┘
└──────────────────┘
```

### Layer Responsibilities

| Layer | Files | Responsibility |
|-------|-------|---------------|
| **Entry** | `main.py` | Window icon, Tk root, launch |
| **Orchestration** | `easycut.py` | UI setup, event handling, all download/convert/auth logic, threading |
| **UI Components** | `modern_components.py`, `ui_enhanced.py` | Custom widgets, config manager, log widget, popups |
| **Screens** | `ui/screens/*.py` | Tab UI implementations (7 screens) |
| **Factories** | `ui/factories/*.py` | Consistent widget creation |
| **Design** | `design_system.py`, `color_extractor.py`, `font_loader.py`, `icon_manager.py` | Colors, fonts, icons, tokens |
| **Theme** | `theme/theme_manager.py` | Unified theme + TTK styles |
| **Core** | `core/*.py` | Config, logging, exceptions, constants |
| **i18n** | `i18n.py` | Translation engine (EN + PT) |
| **Services** | `services/base_service.py` | Abstract base (implementations planned) |

---

## 🔄 Data Flow

### Download Flow

```
User clicks "Download" button
    ↓
EasyCutApp.handle_download()
    ├── Validates URL (regex)
    ├── Gets quality/format from UI
    ├── Spawns background thread
    │       ↓
    │   yt_dlp.YoutubeDL(opts).download([url])
    │       ├── Logs progress → LogWidget
    │       ├── Updates history → JSON file
    │       └── Shows completion → ModernAlert
    └── UI remains responsive (threading)
```

### Theme Toggle Flow

```
User clicks theme toggle
    ↓
EasyCutApp.toggle_theme()
    ├── Flips dark_mode flag
    ├── Saves to config.json
    ├── Applies theme to all widgets
    └── Rebuilds UI (instant, ~200ms)
```

### Language Switch Flow

```
User selects language
    ↓
EasyCutApp.change_language()
    ├── translator.set_language("pt" or "en")
    ├── Saves to config.json
    └── Rebuilds UI with new strings (instant)
```

---

## 🎯 Design Patterns

### Factory Pattern (Widget Creation)

```python
from ui.factories import ButtonFactory

# Instead of manual ttk.Button creation repeated 15+ times
btn = ButtonFactory.create_action_button(parent, "Download", on_click)
```

### Template Method (Base Classes)

```python
class BaseScreen(ABC):
    @abstractmethod
    def build(self): pass       # Each screen implements its own UI
    
    @abstractmethod
    def bind_events(self): pass  # Each screen binds its own events
    
    @abstractmethod
    def get_data(self): pass    # Each screen returns its own state
```

### Singleton (Translator)

```python
# i18n.py
translator = Translator("en")  # Module-level singleton

# Usage anywhere
from i18n import translator as t
label_text = t.get("btn_download")
```

### Observer (Config Changes)

```python
# Theme/language changes trigger full UI rebuild
config_manager.set("dark_mode", True)
# → setup_ui() called → all widgets rebuilt with new theme
```

---

## 🎨 Theme System

The application currently has **two active theme providers**:

### 1. `design_system.py` — Primary (used by `easycut.py` and most modules)

```python
from design_system import ModernTheme, DesignTokens

theme = ModernTheme(dark_mode=True, font_family="Inter Display")
tokens = DesignTokens(dark_mode=True)

bg = tokens.get_color("bg_primary")       # "#0A0E27"
accent = tokens.get_color("accent_primary") # "#f85451" (from app icon)
```

**Features:**
- Dynamic accent color extracted from `app_icon.png` via `color_extractor.py`
- Dark and light palettes with icon-branded colors
- Typography scales, spacing constants, icon mapping

### 2. `ui_enhanced.py` → `Theme` class (used by `ConfigManager`, `LogWidget`, `LoginPopup`)

```python
from ui_enhanced import Theme

theme_obj = Theme(dark_mode=True)
bg = theme_obj.get("bg")  # "#1E1E1E"
```

**Note:** `theme/theme_manager.py` (ThemeManager) is a unified replacement that is used by `BaseScreen` and factories, but the original systems remain active.

---

## 🌐 Internationalization

### Translation System

```python
# i18n.py — 150+ translation keys
TRANSLATIONS = {
    "app_title": {"en": "EasyCut", "pt": "EasyCut"},
    "tab_download": {"en": "Download", "pt": "Download"},
    "btn_login": {"en": "Login", "pt": "Conectar"},
    # ... 150+ more
}

# Usage
from i18n import translator as t
text = t.get("btn_download")  # Returns based on current language
```

### Supported Languages

- **English** (`en`) — Default
- **Portuguese** (`pt`) — Full Brazilian Portuguese

### Hot-Reload

Language can be changed at runtime without restart. The entire UI rebuilds instantly with the new language strings.

---

## 💡 Extension Guide

### Adding a New Screen Tab

1. Create `src/ui/screens/my_screen.py`:

```python
from src.ui.screens.base_screen import BaseScreen

class MyScreen(BaseScreen):
    def build(self):
        # Build your tab UI here
        pass
    
    def bind_events(self):
        pass
    
    def get_data(self):
        return {}
```

2. Register in `src/easycut.py` — add to tab creation in `setup_ui()`.

### Adding Translation Keys

Add entries to `TRANSLATIONS` dict in `src/i18n.py`:

```python
"my_new_key": {"en": "English text", "pt": "Texto em português"},
```

### Adding a New Service (Future)

Create `src/services/my_service.py` extending `BaseService`:

```python
from src.services.base_service import BaseService, ServiceResult

class MyService(BaseService):
    def execute(self, **kwargs):
        # Business logic here
        return ServiceResult(success=True, data=result)
    
    def validate(self, **kwargs):
        pass
    
    def cleanup(self):
        pass
```

---

## 📚 Related Documentation

- [README.md](README.md) — User guide and installation
- [TECHNICAL.md](TECHNICAL.md) — Technical deep dive (threading, config, security)
- [QUICKSTART.md](QUICKSTART.md) — 5-minute setup guide
- [CREDITS.md](CREDITS.md) — Credits and licenses

---

**Made with ❤️ by Deko Costa**  
[github.com/dekouninter/EasyCut](https://github.com/dekouninter/EasyCut)
