# 🔧 EasyCut - Technical Documentation

**Author:** Deko Costa  
**Version:** 2.0.0  
**Python:** 3.8+  
**Repository:** [github.com/dekouninter/EasyCut](https://github.com/dekouninter/EasyCut)

---

## 📋 Table of Contents

1. [Module Reference](#module-reference)
2. [UI Architecture](#ui-architecture)
3. [Threading Model](#threading-model)
4. [Configuration System](#configuration-system)
5. [Security Architecture](#security-architecture)
6. [Error Handling](#error-handling)
7. [Performance](#performance)
8. [Data Persistence](#data-persistence)
9. [Hot-Reload System](#hot-reload-system)
10. [Icon & Font Pipeline](#icon--font-pipeline)
11. [API Reference](#api-reference)

---

## 📦 Module Reference

### `easycut.py` — Main Application (~1,894 lines)

The central orchestrator. Contains `EasyCutApp` class which:
- Creates the main window with sidebar navigation layout (no tab bar)
- Implements 5 sections: Download, Batch, Live, History, About
- Uses hidden `ttk.Notebook` for section switching (tab bar removed via style layout)
- Contains all download/batch/live-stream business logic
- Manages threading for non-blocking operations
- Handles theme toggle and language switching (full UI rebuild)
- Manages download history (JSON persistence)

```python
class EasyCutApp:
    def __init__(self, root):
        # Config, fonts, theme, design tokens
        # Sidebar layout, header bar, content area, log panel
    
    def setup_ui(self)              # Build full layout: header → login banner → body (sidebar + content) → log → status
    def _build_sidebar(self, parent) # VS Code-style sidebar with nav items + footer
    def _switch_section(self, key)   # Update sidebar indicators, switch notebook tab
    def _build_log_panel(self, parent) # Collapsible global log panel
    def create_header(self)          # 45px slim header bar
    def toggle_theme(self)           # Instant dark/light switch
    def change_language(self, lang)  # Instant language switch
    def handle_download(self)        # Video download (threaded)
    def handle_batch_download(self)  # Batch download (threaded)
    def load_history(self)           # Load from JSON
    def save_history(self)           # Save to JSON
    def run_in_thread(self, target)  # Background execution
```

**Imports:**
- `i18n` — translations
- `ui_enhanced` — ConfigManager, LogWidget, StatusBar, LoginPopup
- `design_system` — ModernTheme, DesignTokens, Typography, Spacing, Icons
- `modern_components` — ModernButton, ModernCard, ModernInput, ModernAlert, ModernDialog, ModernIconButton, ToastManager
- `font_loader` — setup_fonts(), LOADED_FONT_FAMILY
- `icon_manager` — icon loading
- `donation_system` — DonationButton
- `ui.screens` — LoginScreen, DownloadScreen, BatchScreen, LiveScreen, HistoryScreen, AboutScreen

---

### `i18n.py` — Internationalization (565 lines)

Translation engine supporting English and Portuguese with hot-reload.

```python
class Translator:
    def __init__(self, language='en')
    def set_language(lang: str) -> bool  # Hot-reload support
    def get(key: str, default='') -> str
    def get_all() -> dict

# Module-level singleton
translator = Translator("en")
```

**Translation structure:**
```python
TRANSLATIONS = {
    "app_title": {"en": "EasyCut", "pt": "EasyCut"},
    "tab_login": {"en": "Login", "pt": "Conexão"},
    "btn_download": {"en": "Download", "pt": "Baixar"},
    # 150+ keys organized by category
}
```

---

### `design_system.py` — Design Tokens (~530 lines)

Unified design token system with Steel Blue accent color.

```python
class ColorPalette:
    DARK = {
        "bg_primary": "#1E1E1E",     # VS Code Dark
        "bg_secondary": "#252526",
        "bg_tertiary": "#2D2D2D",
        "accent_primary": "#4A90D9",  # Steel Blue
        ...
    }
    LIGHT = {
        "bg_primary": "#FFFFFF",
        "accent_primary": "#4A90D9",  # Same accent both themes
        ...
    }

class ModernTheme:
    def __init__(self, dark_mode=True, font_family="Segoe UI")

class DesignTokens:
    def __init__(self, dark_mode=True)
    def get_color(self, key: str) -> str
    def get_font(self, size: str, weight: str) -> tuple

class Typography:    # Font size constants: HERO(32), H1(24), H2(18), H3(15), BODY(13), CAPTION(11), TINY(9)
class Spacing:       # Spacing constants: XXS(2), XS(4), SM(8), MD(12), LG(16), XL(24), XXL(32), XXXL(48)
class Icons:         # Icon name → file mapping
class Shadows:       # Shadow color tokens
```

**Design Language:** Clean Minimal (Linear/Notion style) with Steel Blue `#4A90D9` accent, replacing the original coral `#f85451`. Dark theme uses VS Code-style `#1E1E1E` background.

**Button Styles:** Primary.TButton, Outline.TButton, Ghost.TButton, Danger.TButton, DangerFilled.TButton, Small.TButton, Large.TButton — all configured via `ModernTheme.apply()`.

---

### `modern_components.py` — Custom Widgets (~830 lines)

Modern UI components built on Tkinter Canvas and Frame:

| Class | Purpose |
|-------|---------|
| `ModernButton` | Styled button with 6 variants (primary, secondary, outline, ghost, danger, danger-filled) and 3 sizes (sm, md, lg) |
| `ModernCard` | tk.Frame container with `dark_mode` param, `.body` property for content, optional title/subtitle |
| `ModernInput` | Labeled input with validation |
| `ModernAlert` | Notification bar (success/warning/error/info) |
| `ModernDialog` | Modal dialog window |
| `ModernIconButton` | Icon-only button |
| `Toast` | Single notification with colored left bar, emoji, title, auto-dismiss |
| `ToastManager` | Toast stack manager — `place()`-positioned top-right of content, max 5, success/warning/error/info shortcuts |

**ModernButton variants:**
```python
VARIANTS = {
    "primary":       {"bg": accent, "fg": "#FFFFFF", "border": accent},
    "secondary":     {"bg": bg_secondary, "fg": fg_primary, "border": border},
    "outline":       {"bg": "transparent", "fg": accent, "border": accent},
    "ghost":         {"bg": "transparent", "fg": accent, "border": "transparent"},
    "danger":        {"bg": "transparent", "fg": error, "border": error},
    "danger-filled": {"bg": error, "fg": "#FFFFFF", "border": error},
}
```

**ModernCard pattern:**
```python
card = ModernCard(parent, title="My Card", dark_mode=self.dark_mode)
card.pack(fill=tk.X)
# Add children to card.body, NOT to card directly
ttk.Label(card.body, text="Content").pack()
```

Includes **emoji fallback mapping** (40+ icons) for when PNG icons are unavailable.

---

### `ui_enhanced.py` — UI Infrastructure (534 lines)

Original UI utilities, still actively used by `easycut.py`:

| Class | Purpose |
|-------|---------|
| `Theme` | Dark/light color dictionaries |
| `ConfigManager` | JSON config persistence (load/save/get/set) |
| `LogWidget` | Auto-scrolling timestamped log display |
| `StatusBar` | Login status indicator |
| `LoginPopup` | Modal authentication dialog with keyring |
| `LanguageSelector` | Language dropdown selector |

---

### `color_extractor.py` — DELETED

Previously extracted accent colors from app icon. Removed in v2.0 — accent color is now hardcoded as Steel Blue `#4A90D9` in `design_system.py`.

---

### `font_loader.py` — Font Loading (147 lines)

Loads the Inter Display font family via Windows GDI (`AddFontResourceEx`):

```python
def setup_fonts() -> str              # Returns loaded font family name
def load_custom_fonts() -> bool       # Loads TTF files from assets/fonts/
LOADED_FONT_FAMILY: str               # Global: "Inter Display" or "Segoe UI"
```

Falls back to "Segoe UI" if Inter font files are missing or loading fails.

---

### `icon_manager.py` — Icon Management (290 lines)

Manages icon loading with emoji fallback:

```python
class IconManager:
    def get_icon(self, name, size=24) -> ImageTk.PhotoImage
    def get_emoji_icon(self, name, size=24) -> ImageTk.PhotoImage

def get_ui_icon(name, size=24) -> ImageTk.PhotoImage

icon_manager = IconManager()  # Module-level singleton
```

Looks for PNG icons in `assets/icons/`. If not found, renders emoji text as images via Pillow. Currently uses emoji fallback exclusively (PNG icons not yet generated).

---

### `donation_system.py` — Donation UI (199 lines)

```python
class DonationWindow(tk.Toplevel):   # Modal with donation links
class DonationButton(tk.Frame):      # Floating action button
```

Links: [Buy Me a Coffee](https://buymeacoffee.com/dekocosta), [Livepix](https://livepix.gg/dekocosta)

---

### `core/` — Foundation Layer (675 lines total)

| File | Lines | Key Exports |
|------|------:|-------------|
| `config.py` | 195 | `ConfigManager` — JSON config with dot notation, defaults, hot-reload |
| `constants.py` | 272 | `Constants` (DOWNLOAD, AUDIO, LIVE, UI), `TranslationKeys` |
| `logger.py` | 119 | `Logger`, `StructuredFormatter`, `get_logger()` — colored console + file |
| `exceptions.py` | 55 | `EasyCutException`, `DownloadException`, `AudioException`, `ConfigException`, `AuthException`, `ValidationException` |

---

### `theme/` — Theme Exports

Re-exports from `design_system.py` for backward compatibility:

```python
# theme/__init__.py
from design_system import DesignTokens, ModernTheme, ColorPalette, Typography, Spacing, Icons, Shadows

# Backward compatibility alias — used by widget_factory.py, tab_factory.py, screen files
ThemeManager = DesignTokens
```

The original `theme/theme_manager.py` (376 lines) has been **deleted**. All factory files and screens that imported `ThemeManager` now get it via the `DesignTokens` alias.

---

### `ui/factories/` — Widget Factories (646 lines total)

| File | Lines | Key Exports |
|------|------:|-------------|
| `widget_factory.py` | 336 | `ButtonFactory`, `FrameFactory`, `CanvasScrollFactory`, `DialogFactory`, `InputFactory` |
| `tab_factory.py` | 272 | `TabFactory`, `create_tab()`, `create_tab_header()`, `create_tab_section()` |

---

### `ui/screens/` — Screen Implementations (1,612 lines total)

| File | Lines | Class |
|------|------:|-------|
| `base_screen.py` | 242 | `BaseScreen` (ABC) — defines `build()`, `bind_events()`, `get_data()` |
| `login_screen.py` | 123 | `LoginScreen` — authentication |
| `download_screen.py` | 317 | `DownloadScreen` — video download with quality/format |
| `batch_screen.py` | 173 | `BatchScreen` — multi-URL batch processing |
| `live_screen.py` | 229 | `LiveScreen` — live stream recording |
| `history_screen.py` | 158 | `HistoryScreen` — card-based history display |
| `about_screen.py` | 210 | `AboutScreen` — app info and credits |

> **Note:** `audio_screen.py` was **deleted** in v2.0 — audio options are now integrated into the Download section.

---

### `services/base_service.py` — Service Base (193 lines)

Abstract base class and typed result wrapper:

```python
class BaseService(ABC):
    @abstractmethod
    def execute(self, **kwargs): pass
    @abstractmethod
    def validate(self, **kwargs): pass
    def cleanup(self): pass

class ServiceResult:
    success: bool
    data: Any
    error: str
    metadata: dict
```

> **Status:** Only the abstract base exists. Concrete service implementations are planned for a future phase. All business logic currently remains in `easycut.py`.

---

## 🏗️ UI Architecture

### Layout Structure (v2.0)

```
┌───────────────────────────────────────────────────────┐
│ Header (45px) — Icon + "EasyCut" + Theme Toggle +     │
│                  Language Combobox + Login Button       │
├──────────┬────────────────────────────────────────────┤
│          │                                            │
│ Sidebar  │  Content Area                              │
│ (200px   │  (hidden TNotebook, tab bar removed)       │
│  or 50px │                                            │
│  when    │  ┌─ Active Section ─────────────────────┐  │
│  clpsed) │  │  Download / Batch / Live /            │  │
│          │  │  History / About                      │  │
│ ┌──────┐ │  └──────────────────────────────────────┘  │
│ │ Nav  │ │                                            │
│ │ Items│ │  ┌─ Collapsible Log Panel ──────────────┐  │
│ ├──────┤ │  │ Global LogWidget (all sections share) │  │
│ │Footer│ │  └──────────────────────────────────────┘  │
│ └──────┘ │                                            │
├──────────┴────────────────────────────────────────────┤
│ Status Bar (24px) + Donation Button                    │
└───────────────────────────────────────────────────────┘
```

### Key Architectural Changes (v1 → v2)

| Aspect | v1 | v2 |
|--------|----|----|
| **Navigation** | Tab notebook with visible tab bar | Sidebar + hidden TNotebook |
| **Sections** | 7 tabs (Login, Download, Batch, Live, Audio, History, About) | 5 sections (Download, Batch, Live, History, About) |
| **Log** | Per-tab LogWidget in each section | Single global collapsible log panel |
| **Accent** | `#f85451` coral (extracted from icon) | `#4A90D9` Steel Blue (hardcoded) |
| **Dark BG** | `#0A0E27` navy | `#1E1E1E` VS Code Dark |
| **Theme Systems** | 3 separate (ui_enhanced.Theme, DesignTokens, ThemeManager) | 1 unified (DesignTokens via design_system.py) |
| **Buttons** | Single style | 6 variants × 3 sizes |
| **Cards** | ttk.Frame with simple border | tk.Frame with `.body` property, dark_mode, title/subtitle |
| **Notifications** | ModernAlert + messagebox | ToastManager with auto-dismiss |
| **Audio** | Separate tab | Integrated into Download section |
| **Login** | Separate tab | Banner bar under header |

### Sidebar Navigation

The sidebar replaces the tab bar. It uses a custom frame with:
- Toggle button (☰) to collapse/expand (200px ↔ 50px)
- 5 nav items with emoji icon + label + active indicator (accent left border)
- Footer with version badge + folder buttons
- `_switch_section(key)` method selects the hidden notebook tab

### Log Panel

All per-section log widgets (download_log, batch_log, live_log) are aliased to a single global `LogWidget`:
```python
self.download_log = self.global_log
self.batch_log = self.global_log
self.live_log = self.global_log
```

The panel is collapsible via a toggle bar with keyboard shortcut `Ctrl+L`.

### Toast System

`ToastManager` is created on the `content_area` frame and positioned top-right via `place()`. It stacks up to 5 toasts vertically with auto-dismiss (4s default).

```python
self.toast_manager.success("Download Complete", "video.mp4 saved")
self.toast_manager.error("Error", "URL not valid")
```

---

## 🧵 Threading Model

### Problem

Downloads and conversions are I/O intensive (network + disk). Running on the main thread freezes the UI.

### Solution

Background threads via `threading.Thread(daemon=True)`:

```python
def run_in_thread(self, target, *args, **kwargs):
    thread = threading.Thread(
        target=target, args=args, kwargs=kwargs,
        daemon=True
    )
    thread.start()
```

### Operations

| Operation | Thread | Blocks UI? |
|-----------|--------|------------|
| Video download | Background | No |
| Audio conversion | Background | No |
| Batch download | Background | No |
| Live recording | Background | No |
| UI updates | Main (via `root.after`) | No |
| Config load/save | Main | Negligible |

### Thread Safety

- UI updates dispatched to main thread via `root.after(0, callback)`
- Daemon threads: don't block app exit
- Thread-safe logging with internal locks
- No shared mutable state between threads

---

## 💾 Configuration System

### File: `config/config.json`

```json
{
    "dark_mode": false,
    "language": "en",
    "output_folder": "downloads",
    "log_level": "INFO"
}
```

### ConfigManager (from `ui_enhanced.py`)

```python
config = ConfigManager()
config.load()
lang = config.get("language", "en")
config.set("dark_mode", True)
config.save()
```

Auto-creates `config/` directory and default config on first run.

---

## 🔐 Security Architecture

### Credential Storage

Passwords stored via OS keyring (Windows Credential Manager):

```python
import keyring

keyring.set_password("EasyCut", username, password)   # Store
password = keyring.get_password("EasyCut", username)   # Retrieve
keyring.delete_password("EasyCut", username)            # Delete
```

### Security Features

- **OS-level encryption** — uses Windows Credential Manager
- **No plaintext** — passwords never written to files
- **Per-user isolation** — each Windows user has separate credentials
- **Input validation** — URL, email, time format regex checks

---

## ⚠️ Error Handling

### Custom Exception Hierarchy

```
EasyCutException (base)
├── DownloadException    — download failures
├── AudioException       — conversion failures
├── ConfigException      — config read/write errors
├── AuthException        — authentication failures
└── ValidationException  — input validation errors
```

### User-Facing Errors

```python
try:
    result = download_video(url)
except Exception as e:
    log_widget.log(f"ERROR: {str(e)}")
    messagebox.showerror("Error", user_friendly_message)
```

---

## ⚡ Performance

| Metric | Target | Actual |
|--------|--------|--------|
| Cold startup | < 2s | ~1-2s |
| Theme toggle | < 300ms | ~200ms |
| Language switch | < 300ms | ~300ms |
| Memory (idle) | < 100MB | ~50-80MB |
| Memory (downloading) | < 200MB | ~100-150MB |

### Optimizations

- Lazy tab creation — screens built on demand
- Cached theme colors — no recomputation
- Background threads — UI never blocks
- JSON config — lightweight persistence
- Emoji icon fallback — avoids loading 286 PNG files

---

## 📊 Data Persistence

| Data | Storage | Format |
|------|---------|--------|
| Settings | `config/config.json` | JSON |
| Credentials | Windows Keyring | Encrypted |
| History | `config/history_downloads.json` | JSON array |
| Logs | `config/app.log` | Plain text |

### History Entry

```json
{
    "url": "https://www.youtube.com/watch?v=...",
    "title": "Video Title",
    "date": "2024-02-13 15:30:45",
    "status": "success",
    "format": "mp4",
    "size_mb": 45.3
}
```

---

## 🔄 Hot-Reload System

### Theme Toggle

```python
def toggle_theme(self):
    self.dark_mode = not self.dark_mode
    self.config_manager.set("dark_mode", self.dark_mode)
    self.theme = ModernTheme(dark_mode=self.dark_mode, font_family=self.font_family)
    self.setup_ui()  # Full UI rebuild (~200ms)
```

### Language Switch

```python
def change_language(self, lang):
    translator.set_language(lang)
    self.config_manager.set("language", lang)
    self.setup_ui()  # Full UI rebuild (~300ms)
```

Both operations destroy all widgets and rebuild the entire UI with the new theme/language. User data (history, config, logs) is preserved.

---

## 🎨 Icon & Font Pipeline

### Font Loading

1. `font_loader.py` searches `assets/fonts/Inter/` for TTF files
2. Loads via Windows GDI `AddFontResourceEx` (temporary, process-only)
3. Sets `LOADED_FONT_FAMILY` global: `"Inter Display"` or `"Segoe UI"` fallback
4. All modules import `LOADED_FONT_FAMILY` for consistent typography

### Icon Loading

1. `icon_manager.py` looks in `assets/icons/` for `{name}_{size}.png`
2. If PNG not found → renders emoji via Pillow `ImageFont`/`ImageDraw`
3. 40+ emoji mappings defined in `modern_components.py`
4. Icons cached in memory after first load

### Color Extraction — REMOVED

In v1, `color_extractor.py` loaded `assets/app_icon.png` and extracted dominant colors for the accent. In v2, the accent color is hardcoded as Steel Blue `#4A90D9` in `design_system.py`. This eliminated a startup dependency on Pillow pixel clustering.

---

## 🔌 API Reference

### EasyCutApp

```python
app.toggle_theme()                       # Switch dark ↔ light
app.change_language("pt")                # Switch to Portuguese
app.handle_download()                    # Start video download
app.handle_batch_download()              # Start batch downloads
app.handle_audio_conversion()            # Start audio conversion
app.load_history()                       # Load from JSON
app.save_history()                       # Save to JSON
app.run_in_thread(func, *args)           # Background execution
app.open_output_folder()                 # Open downloads in explorer
```

### Translator

```python
from i18n import translator as t
t.get("btn_download")                    # "Download" or "Baixar"
t.set_language("pt")                     # Switch language
```

### DesignTokens

```python
from design_system import DesignTokens
tokens = DesignTokens(dark_mode=True)
tokens.get_color("bg_primary")           # "#1E1E1E"
tokens.get_color("accent_primary")       # "#4A90D9"
```

### ToastManager

```python
self.toast_manager.success("Title", "Message")
self.toast_manager.error("Error", "Something went wrong")
self.toast_manager.warning("Warning", "Check your input")
self.toast_manager.info("Info", "Download started")
```

### ConfigManager

```python
from ui_enhanced import ConfigManager
config = ConfigManager()
config.get("language", "en")
config.set("dark_mode", True)
config.save()
```

---

## 📚 Related Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) — Architecture overview and module map
- [README.md](README.md) — User guide and installation
- [QUICKSTART.md](QUICKSTART.md) — 5-minute setup guide
- [CREDITS.md](CREDITS.md) — Credits and licenses

---

**Made with ❤️ by Deko Costa**  
[github.com/dekouninter/EasyCut](https://github.com/dekouninter/EasyCut)
