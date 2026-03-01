# 🏗️ EasyCut - Architecture Documentation

**Version**: 1.9.0  
**Last Updated**: February 2026

High-level architecture overview for developers working on EasyCut.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Project Structure](#project-structure)
3. [Module Map](#module-map)
4. [Application Layers](#application-layers)
5. [Data Flow](#data-flow)
6. [Design Patterns](#design-patterns)
7. [Theme System](#theme-system)
8. [Internationalization](#internationalization)
9. [Embedded Video Player](#embedded-video-player)
10. [Extension Guide](#extension-guide)

---

## 📌 Overview

EasyCut is a professional desktop YouTube downloader, stream recorder, and live clipper built with **Python 3.13** and **Tkinter**. The application uses a modular architecture with specialized modules, each handling a distinct concern.

### Architecture Summary

All modules are in a flat `src/` directory for simplicity:

| Concern | Module(s) | Lines |
|---------|-----------|------:|
| Main orchestrator | `easycut.py` | 5,273 |
| Translations (7 languages) | `i18n.py` | 3,949 |
| Design tokens & palette | `design_system.py` | 1,252 |
| Custom widgets (16 components) | `modern_components.py` | 1,214 |
| Embedded video player | `video_player.py` | 651 |
| UI utilities | `ui_enhanced.py` | 431 |
| SVG icon renderer | `icon_renderer.py` | 428 |
| OAuth authentication | `oauth_manager.py` | 316 |
| Channel monitor | `channel_monitor.py` | 281 |
| Icon management | `icon_manager.py` | 277 |
| Post-processing hub | `post_processor.py` | 237 |
| Donation UI | `donation_system.py` | 202 |
| Font loading | `font_loader.py` | 146 |
| **Total src/** | **13 modules** | **~14,657** |

### Key Principles

- **Separation of Concerns** — Each module handles one domain
- **Hot-Reload** — Theme and language switch instantly without restart
- **Secure Credentials** — OAuth stored via pickle, cookies via text file
- **Threading** — Downloads run in background threads (non-blocking UI); UI updates from background threads use `root.after()` for safety (v1.7 fixes)
- **SVG Icon Rendering** — Custom Feather SVG parser → Pillow → PhotoImage (no external SVG deps)
- **Multi-Accent Design** — 6 accent color families (Blue, Purple, Orange, Red, Rose, Cyan) with gradients
- **Glass-Morphism UI** — Gradient accent lines, glow borders, depth effects, transparent tooltips
- **Windows Integration** — pywinstyles Mica/Acrylic backdrop, darkdetect OS theme detection
- **Subprocess IPC** — Embedded mpv player via Windows Named Pipes (no DLL dependency)

### v1.7 — Important architectural notes
- Live tab rework (UI + workflow): preview can load the growing recording file so the seekbar can rewind to the live start; clipper controls integrated into the preview card.
- EmbeddedPlayer improvements: `load_recording()` waits for file growth and loads the local (seekable) recording file; `seek_to_end()` uses mpv percent-seek for the live edge; mpv arguments are separated for URL vs file playback.
- yt-dlp & formats: improved format chains to avoid "Requested format is not available" for live MPD manifests; `live_from_start` applied consistently for recording and preview.
- Clipper concurrency: `_clipper_download_single()` performs ffmpeg trims in background threads without interrupting main recording.
- Stability: fixed NameError in live progress hook, removed unsafe direct widget updates from background threads, and ensured `on_closing()` stops active recordings.
- Premiere compatibility toggle (v1.7): new setting stored in config; download/batch/live workflows check flag and use `PostProcessor.convert_for_premiere` when necessary.  PostProcessor gained `is_premiere_compatible` and conversion helpers.
- Environment note: installing a JS runtime (e.g. `deno`) is recommended for reliable yt-dlp extraction on some YouTube streams.

### 🔌 Authentication Architecture

EasyCut supports two authentication methods:

1. **Google OAuth 2.0** (Primary, Always Enabled)
   - One-click YouTube authentication via browser
   - Stored in `config/youtube_token.pickle`
   - Method: `create_oauth_banner()` in easycut.py
   - Status: ✅ Production-ready

2. **Browser Cookie Extraction** (Optional, Disabled by Default)
   - Extract cookies from installed browsers (Chrome, Firefox, Edge, etc.)
   - Extract accounts automatically or import cookies.txt manually
   - Method: `create_browser_auth_banner()` in easycut.py
   - Activation: Edit `config/config.json` and set `"enable_browser_auth": true`
   - Status: ✅ Production-ready

**Default Behavior**: Only OAuth is shown. Browser auth requires explicit opt-in via settings file.

---

## 🗂️ Project Structure

### Current Structure (v1.9.0)

```
EasyCut/
├── main.py                         # Entry point (sets window icon, launches app)
├── build.py                        # Build script for standalone executables (PyInstaller)
├── requirements.txt                # Dependencies: yt-dlp, keyring, Pillow, oauth, pywinstyles, darkdetect
├── setup.py                        # Packaging script (setuptools)
├── START.bat                       # Windows launcher (auto-creates venv)
├── run.bat                         # Alternative launcher (checks FFmpeg)
├── check_installation.py           # Verifies dependencies and structure
│
├── src/                            # All application source code (FLAT STRUCTURE)
│   ├── easycut.py                  # Main application class (EasyCutApp) - 5,273 lines
│   ├── i18n.py                     # Translation engine (7 languages, 509+ keys) - 3,949 lines
│   ├── design_system.py            # Design tokens, 6 accent palettes, gradients - 1,252 lines
│   ├── modern_components.py        # 16 custom widgets (buttons, cards, badges, etc.) - 1,214 lines
│   ├── video_player.py             # Embedded mpv player (subprocess + IPC) - 651 lines
│   ├── ui_enhanced.py              # ConfigManager, LogWidget, StatusBar - 431 lines
│   ├── icon_renderer.py            # SVG Feather icon → Pillow renderer, gradients - 428 lines
│   ├── oauth_manager.py            # OAuth 2.0 authentication manager - 316 lines
│   ├── channel_monitor.py          # YouTube channel monitoring system - 281 lines
│   ├── icon_manager.py             # Icon loading with emoji fallback - 277 lines
│   ├── post_processor.py           # Post-download processing hub - 237 lines
│   ├── donation_system.py          # Donation window and button - 202 lines
│   └── font_loader.py              # Loads Inter font via Windows GDI - 146 lines
│
├── assets/                         # Static assets
│   ├── fonts/Inter/                # Inter Display font files (TTC)
│   └── feather-main/               # Feather icon source (SVG)
│
├── config/                         # Runtime configuration (auto-created)
│   ├── config.json                 # User settings (theme, language, paths)
│   ├── credentials.json            # OAuth credentials (developers only - gitignored)
│   ├── credentials_template.json   # Template for OAuth credentials
│   ├── youtube_token.pickle        # Saved OAuth tokens (gitignored)
│   ├── yt_cookies.txt              # Cookies for yt-dlp (gitignored)
│   ├── history_downloads.json      # Download history entries
│   └── app.log                     # Application log file
│
├── downloads/                      # Default output folder
│
├── internal/                       # Development documentation (gitignored)
│   ├── run_tests.py                # Automated test suite (697 checks)
│   ├── test_*.py                   # Various test scripts
│   ├── TESTING.md                  # Complete manual testing checklist
│   ├── ROADMAP.md                  # Product roadmap
│   └── README.md                   # Internal docs explanation
│
└── docs/                           # Documentation
    ├── README.md                   # Main documentation
    ├── QUICKSTART.md               # Complete setup guide (OAuth, builds, usage)
    ├── DOCUMENTATION.md            # Detailed feature documentation
    ├── ARCHITECTURE.md             # This file
    ├── CREDITS.md                  # Credits and licenses
    ├── PRIVACY.md                  # Privacy policy
    └── TERMS.md                    # Terms of service
```

---

## 🧩 Module Map

### Entry & Orchestration

| Module | Purpose | Key Exports |
|--------|---------|-------------|
| `main.py` | Sets window icon, creates Tk root, launches `EasyCutApp` | `main()` |
| `easycut.py` | Main application: header, 8 tabs, download logic, thread management | `EasyCutApp` |

### UI Infrastructure

| Module | Purpose | Key Exports |
|--------|---------|-------------|
| `modern_components.py` | 16 custom widgets built on Frame/Canvas/ttk | `ScrollableFrame`, `SectionHeader`, `ModernButton`, `ModernCard`, `ModernEntry`, `Badge`, `Tooltip`, `ToggleSwitch`, `AnimatedPanel`, `Separator`, `InfoBanner`, `IconLabel`, `EmptyState`, `HoverFrame`, `ProgressRing`, `AnimatedCounter` |
| `ui_enhanced.py` | UI utilities and managers | `ConfigManager`, `LogWidget`, `StatusBar`, `LoginPopup` |
| `donation_system.py` | Donation modal and button | `DonationWindow`, `DonationButton` |

### Design & Theming

| Module | Purpose | Key Exports |
|--------|---------|-------------|
| `design_system.py` | Design tokens: 6 accent color families, gradients, typography, spacing, icon mapping | `ColorPalette`, `ModernTheme`, `DesignTokens`, `Typography`, `Spacing`, `Icons` |
| `icon_renderer.py` | SVG Feather icon parser → Pillow renderer, gradient images, glow borders | `render_feather_icon()`, `create_gradient_image()`, `create_glow_border()`, `clear_icon_cache()` |
| `font_loader.py` | Loads Inter Display font via Windows GDI, falls back to Segoe UI | `setup_fonts()`, `LOADED_FONT_FAMILY` |
| `icon_manager.py` | Loads PNG icons with automatic emoji fallback rendering | `IconManager`, `icon_manager`, `get_ui_icon()`, `set_icon_theme()` |

### Media & Processing

| Module | Purpose | Key Exports |
|--------|---------|-------------|
| `video_player.py` | Embedded mpv player via subprocess + JSON IPC (Named Pipes) | `EmbeddedPlayer`, `is_player_available()` |
| `post_processor.py` | Post-download processing: format conversion, trimming, audio extraction | `PostProcessor` |
| `channel_monitor.py` | Monitors YouTube channels for new uploads and live streams | `ChannelMonitor` |

### Authentication & Services

| Module | Purpose | Key Exports |
|--------|---------|-------------|
| `oauth_manager.py` | YouTube OAuth 2.0 authentication via Google API | `OAuthManager`, `OAuthError` |

### Internationalization

| Module | Purpose | Key Exports |
|--------|---------|-------------|
| `i18n.py` | 7-language translations (EN, PT, ES, FR, DE, IT, JA) with hot-reload | `Translator`, `translator`, `TRANSLATIONS` |

---

## 🏢 Application Layers

```
┌────────────────────────────────────────────────────┐
│  main.py (Entry Point)                             │
│  Sets icon → Creates Tk → Launches EasyCutApp      │
└──────────────────────┬─────────────────────────────┘
                       │
┌──────────────────────▼─────────────────────────────┐
│  easycut.py (Orchestrator — 5,273 lines)           │
│  ┌─────────────┐ ┌──────────┐ ┌──────────────┐    │
│  │ Header Bar  │ │ 8 Screens│ │ Business     │    │
│  │ SVG Icons   │ │ Switcher │ │ Logic:       │    │
│  │ Theme Toggle│ │          │ │ - Download   │    │
│  │ Lang Select │ │          │ │ - Batch      │    │
│  │ OAuth Banner│ │          │ │ - Live+Clip  │    │
│  │ Mica Bdrop  │ │          │ │ - PostProc   │    │
│  └─────────────┘ └──────────┘ │ - Following  │    │
│                                │ - Monitor    │    │
│                                │ - History    │    │
│                                │ - About      │    │
│                                └──────────────┘    │
└─┬────────┬───────────┬───────────┬─────────────────┘
  │        │           │           │
  ▼        ▼           ▼           ▼
┌──────┐ ┌──────────┐ ┌────────┐ ┌──────────────┐
│Design│ │Modern    │ │UI      │ │i18n          │
│System│ │Components│ │Enhanced│ │Translations  │
│1,252L│ │ 1,214L   │ │ 431L   │ │ 3,949L       │
└──┬───┘ └──────────┘ └────────┘ └──────────────┘
   │
   ▼
┌──────────────┐  ┌───────────┐  ┌───────────┐  ┌──────────────┐
│Icon Renderer │  │Font       │  │Icon       │  │OAuth         │
│ 428L (SVG)   │  │Loader 146L│  │Manager 277L│  │Manager 316L  │
└──────────────┘  └───────────┘  └───────────┘  └──────────────┘
   │
   ▼
┌──────────────┐  ┌───────────────┐  ┌───────────────┐
│Video Player  │  │Post Processor │  │Channel Monitor│
│ 651L (mpv)   │  │ 237L          │  │ 281L          │
└──────────────┘  └───────────────┘  └───────────────┘
```

### Layer Responsibilities (v1.9.0)

| Layer | Files | Responsibility |
|-------|-------|---------------|
| **Entry** | `main.py` | Window icon, Tk root, launch |
| **Orchestration** | `easycut.py` | UI setup, event handling, all download/batch/live/clip/monitor logic, threading, pywinstyles Mica backdrop |
| **UI Components** | `modern_components.py`, `ui_enhanced.py` | 16 custom widgets, config manager, log widget, popups |
| **Design** | `design_system.py`, `font_loader.py`, `icon_manager.py`, `icon_renderer.py` | Colors (6 accent families), fonts, PNG icons, SVG icon rendering, gradients, glow effects |
| **i18n** | `i18n.py` | Translation engine (EN, PT, ES, FR, DE, IT, JA — 509+ keys each) |
| **Media** | `video_player.py`, `post_processor.py` | Embedded player (mpv subprocess + IPC), post-processing |
| **Monitoring** | `channel_monitor.py` | YouTube channel polling, new content detection |
| **OAuth** | `oauth_manager.py` | YouTube authentication |
| **Donation** | `donation_system.py` | Donation window and button |

---

## 🔄 Data Flow

### Download Flow

```
User clicks "Download" button
    ↓
EasyCutApp.start_download()
    ├── Validates URL (regex)
    ├── Gets quality/format/mode from UI
    ├── Spawns background thread
    │       ↓
    │   download_thread():
    │       ├── yt_dlp.YoutubeDL(opts).download([url])
    │       ├── Logs progress → LogWidget
    │       ├── Updates StatusBar
    │       ├── Saves to history → JSON file
    │       └── Shows completion message
    └── UI remains responsive (threading)
```

### Batch Download Flow

```
User clicks "Download All" on Batch tab
    ↓
EasyCutApp.start_batch_download()
    ├── Parses URLs from textarea (one per line)
    ├── Validates each URL
    ├── Spawns background thread
    │       ↓
    │   batch_thread():
    │       └── for each URL:
    │           ├── Download with yt-dlp
    │           ├── Log progress (3/10 completed)
    │           └── Add to history
    └── "Stop All" button stops batch
```

### Live Stream Recording Flow

```
User clicks "Verify" on Live tab
    ↓
EasyCutApp.verify_live_stream()
    ├── Checks if stream is live via yt-dlp
    ├── Shows stream info (title, channel)
    ├── Enables "Start Recording" button
    │
User clicks "Load Preview" (optional)
    ↓
EasyCutApp._load_live_preview()
    ├── Gets URL from live_url_entry
    ├── Loads into EmbeddedPlayer (mpv --wid=HWND)
    ├── Player renders video in Tkinter frame
    └── Seekbar and controls become active
    │
User clicks "Start Recording"
    ↓
EasyCutApp.start_live_recording()
    ├── Gets mode: continuous or timed
    ├── Spawns background thread
    │       ↓
    │   live_thread():
    │       ├── yt-dlp records stream
    │       ├── Updates elapsed time
    │       └── Stops when duration reached or user clicks "Stop"
    ├── Auto-loads recording into EmbeddedPlayer for preview
    └── File saved to downloads/

Live Clipper (while recording):
    ├── User marks start point on seekbar → _clipper_mark_start()
    ├── User marks end point on seekbar → _clipper_mark_end()
    ├── Uses embedded_player.get_time() for precise timestamps
    └── Clip extracted via ffmpeg post-processing
```

### Embedded Player Architecture

```
EasyCut App (Tkinter)
    │
    ├── EmbeddedPlayer widget (tk.Frame)
    │       ├── video_frame (black bg, provides HWND)
    │       ├── seekbar (ttk.Scale + time labels)
    │       └── controls (play/pause, stop, volume)
    │
    ├── mpv.exe subprocess
    │       ├── --wid=HWND (renders into Tkinter frame)
    │       ├── --input-ipc-server=\\.\pipe\easycut_mpv_XXXX
    │       ├── --no-osc (no on-screen controller)
    │       └── --ytdl=yes (supports YouTube URLs directly)
    │
    └── JSON IPC via Windows Named Pipe
            ├── _pipe_connect() → kernel32.CreateFileW
            ├── _pipe_send() → kernel32.WriteFile
            ├── _pipe_read() → kernel32.ReadFile
            ├── Commands: get_property, set_property, seek, quit
            └── Background thread for non-blocking UI sync
```

### Theme Toggle Flow

```
User clicks theme toggle (☀️ / 🌙)
    ↓
EasyCutApp.toggle_theme()
    ├── Flips dark_mode flag
    ├── Saves to config.json
    ├── Updates icon theme (set_icon_theme)
    ├── Clears SVG icon cache (clear_icon_cache)
    ├── Creates new ModernTheme instance
    ├── Re-applies pywinstyles Mica backdrop
    ├── Applies theme to root window
    └── Rebuilds entire UI (setup_ui())
        → Instant switch, ~200ms
```

### Language Switch Flow

```
User selects language from dropdown
    ↓
EasyCutApp.change_language("pt" or "en")
    ├── translator.set_language(lang)
    ├── Saves to config.json
    └── Rebuilds entire UI (setup_ui())
        → All text updates instantly
```

### OAuth Authentication Flow

```
User clicks "Sync with YouTube"
    ↓
OAuthManager.authenticate()
    ├── Checks for existing token.pickle
    │   ├── If valid: use existing token
    │   └── If expired/missing: start OAuth flow
    │
    ├── OAuth Flow:
    │   ├── Opens browser with Google consent screen
    │   ├── User signs in and grants permissions
    │   ├── Google redirects with auth code
    │   ├── OAuthManager exchanges code for tokens
    │   ├── Saves youtube_token.pickle
    │   └── Exports cookies to yt_cookies.txt
    │
    └── Returns authenticated session
        → yt-dlp uses cookies for downloads
```

---

## 🎯 Design Patterns

### Singleton (Translator)

```python
# i18n.py
translator = Translator("en")  # Module-level singleton

# Usage anywhere
from i18n import translator as t
label_text = t.get("btn_download")  # Returns translated string
```

### Observer (Config Changes)

```python
# Theme/language changes trigger full UI rebuild
def toggle_theme(self):
    self.dark_mode = not self.dark_mode
    self.config_manager.set("dark_mode", self.dark_mode)
    self.setup_ui()  # Rebuild entire UI with new theme
```

### Facade (OAuth Manager)

```python
# oauth_manager.py provides simple interface for complex OAuth flow
oauth = OAuthManager(config_dir="config")
service = oauth.authenticate()  # Handles all OAuth complexity
cookies = oauth.export_cookies()  # Exports cookies for yt-dlp
```

### Factory (Icon Manager / Icon Renderer)

```python
# icon_manager.py (PNG with emoji fallback)
icon = icon_manager.get_icon("download", size=24)  # Returns PhotoImage
# Falls back to emoji if icon file not found

# icon_renderer.py (SVG → Pillow, v1.6+)
from icon_renderer import render_feather_icon
svg_icon = render_feather_icon("download", size=20, color="#8B5CF6")
# Parses SVG, renders with 2x supersampling, returns PhotoImage
```

---

## 🎨 Theme System

### Design Tokens (design_system.py)

```python
from design_system import ModernTheme, DesignTokens

theme = ModernTheme(dark_mode=True, font_family="Inter Display")
tokens = DesignTokens(dark_mode=True)

# Access colors
bg = tokens.get_color("bg_primary")       # "#1E1E1E" (dark) or "#FFFFFF" (light)
accent = tokens.get_color("accent_primary") # "#4A90E9" (steel blue)
success = tokens.get_color("success")      # "#28A745" (green)

# Typography
title_font = (Typography.FONT_FAMILY, Typography.SIZE_H1, "bold")
body_font = (Typography.FONT_FAMILY, Typography.SIZE_BODY)

# Spacing
padx = Spacing.MD  # 16px
pady = Spacing.SM  # 12px
```

### Color Palettes

**Dark Mode** (`ColorPalette.DARK`):
- Primary BG: `#1E1E1E`
- Secondary BG: `#2D2D2D`
- Text: `#E0E0E0`
- Accent (Blue): `#4A90E9` (steel blue)
- Purple: `#8B5CF6`
- Orange: `#F97316`
- Red: `#EF4444`
- Rose: `#EC4899`
- Cyan: `#06B6D4`

**Light Mode** (`ColorPalette.LIGHT`):
- Primary BG: `#FFFFFF`
- Secondary BG: `#F5F5F5`
- Text: `#2C3E50`
- Accent (Blue): `#4A90E9` (steel blue)
- Purple: `#7C3AED`
- Orange: `#EA580C`
- Red: `#DC2626`
- Rose: `#DB2777`
- Cyan: `#0891B2`

Both palettes have 60+ semantic color tokens for consistent theming, including:
- 6 accent color families (Blue, Purple, Orange, Red, Rose, Cyan) each with primary/hover/muted/subtle/glow variants
- 6 named gradient presets (blue→purple, purple→pink, orange→red, cyan→blue, green→cyan, sunset)
- Icon-specific color tokens (icon_purple, icon_orange, icon_red, icon_cyan, icon_rose)
- Header gradient, sidebar glow, card glow, and border glow tokens
- 3 extra ttk button styles: PurpleFilled, OrangeFilled, RoseFilled
- 2 extra progressbar styles: Purple, Orange

### Hot-Reload Theme Switching

Themes switch instantly without restart:
1. User clicks toggle
2. `dark_mode` flag flips
3. New `ModernTheme` created
4. All widgets recreated with new colors
5. Total time: ~200ms

---

## 🌐 Internationalization

### Translation System (i18n.py)

```python
# 509+ translation keys per language, 7 languages
TRANSLATIONS = {
    "en": {
        "app_title": "EasyCut",
        "version": "1.9.0",
        "tab_download": "Download",
        "btn_login": "Login",
        "msg_success": "Success!",
        # ... 509+ keys
    },
    "pt": { ... },  # Brazilian Portuguese
    "es": { ... },  # Spanish
    "fr": { ... },  # French
    "de": { ... },  # German
    "it": { ... },  # Italian
    "ja": { ... },  # Japanese
}

# Usage
from i18n import translator as t
text = t.get("btn_download")  # Returns based on current language
```

### Supported Languages

- **English** (`en`) — Default
- **Portuguese** (`pt`) — Full Brazilian Portuguese
- **Spanish** (`es`) — Full Spanish
- **French** (`fr`) — Full French
- **German** (`de`) — Full German
- **Italian** (`it`) — Full Italian
- **Japanese** (`ja`) — Full Japanese

### Hot-Reload Language Switching

Languages switch instantly without restart:
1. User selects language from dropdown
2. `translator.set_language(lang)` called
3. `setup_ui()` rebuilds entire interface
4. All text updates to new language
5. Total time: ~200ms

### Translation Coverage Testing

Automated test verifies all keys exist in both languages:

```bash
python internal/run_tests.py  # Section 18: i18n Coverage
```

---

## 💡 Extension Guide

### Adding a New Feature Tab

1. **Define tab in `easycut.py`**:

```python
def create_my_tab(self):
    """Create new feature tab"""
    main = tk.Frame(self.content_area, bg=self.theme.bg)
    main.pack(fill=tk.BOTH, expand=True)
    
    # Build UI here
    title_lbl = tk.Label(main, text=t.get("my_tab_title"), ...)
    
    return main
```

2. **Register in sidebar** (`setup_ui` method):

```python
self.sections = {
    "download": {...},
    "batch": {...},
    "mytab": {
        "name": t.get("tab_mytab"),
        "icon": get_ui_icon("star"),
        "frame": None  # Created on first switch
    },
}
```

3. **Add translations** to `i18n.py`:

```python
"tab_mytab": {"en": "My Tab", "pt": "Minha Aba"},
"my_tab_title": {"en": "My Feature", "pt": "Minha Funcionalidade"},
```

### Adding Translation Keys

Add to `TRANSLATIONS` dict in `src/i18n.py`:

```python
"my_new_key": {"en": "English text", "pt": "Texto em português"},
```

Run translation coverage test:

```bash
python internal/run_tests.py  # Verifies EN/PT parity
```

### Adding a New Color Token

Add to both `DARK` and `LIGHT` palettes in `design_system.py`:

```python
class ColorPalette:
    DARK = {
        # ... existing colors
        "my_custom_color": "#FF5733",
    }
    
    LIGHT = {
        # ... existing colors
        "my_custom_color": "#E85D33",
    }
```

### Adding a New Icon

1. Add SVG icon to `assets/feather-main/icons/`
2. The SVG icon renderer (`icon_renderer.py`) auto-renders them:

```python
from icon_renderer import render_feather_icon
icon = render_feather_icon("myicon", size=20, color="#8B5CF6")
# Returns PhotoImage via Pillow (2x supersampling + LANCZOS downscale)
```

Or use the legacy PNG icon manager with emoji fallback:

```python
icon = icon_manager.get_icon("myicon", size=24)
```

Or define fallback emoji in `icon_manager.py`:

```python
EMOJI_MAP = {
    # ... existing emojis
    "myicon": "🎯",
}
```

---

## 🧪 Testing

### Automated Tests

Run complete test suite:

```bash
python internal/run_tests.py
```

**30 test sections covering:**
- Module imports
- Design system (colors, typography, spacing)
- UI components (buttons, cards, widgets)
- Parsers (timecode, duration, rate limit)
- URL validation
- Error messages
- i18n (509+ keys, 7-language parity)
- OAuth configuration
- Version consistency (1.9.0)
- Asset files (fonts, icons)

**Total**: 697 automated checks

### Manual Testing

See [internal/TESTING.md](internal/TESTING.md) for complete manual test checklist covering:
- Application launch
- OAuth authentication
- Download tab (video, audio, time ranges)
- Batch downloads
- Live stream recording
- History management
- Theme and language switching
- UI responsiveness
- Error handling
- Build and distribution

---

## 📚 Related Documentation

- [README.md](README.md) — Main documentation and features
- [QUICKSTART.md](QUICKSTART.md) — Installation, OAuth setup, and building
- [DOCUMENTATION.md](DOCUMENTATION.md) — Detailed feature documentation
- [CREDITS.md](CREDITS.md) — Credits and licenses
- [internal/TESTING.md](internal/TESTING.md) — Complete testing guide

---

**Made with ❤️ by Deko Costa**  
[github.com/dekouninter/EasyCut](https://github.com/dekouninter/EasyCut)
