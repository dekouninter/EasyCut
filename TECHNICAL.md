# 🔧 EasyCut - Technical Documentation

**Author:** Deko Costa  
**Version:** 1.0.0  
**Python:** 3.8+  
**Repository:** [github.com/dekouninter/EasyCut](https://github.com/dekouninter/EasyCut)

---

## 📋 Table of Contents

1. [Module Reference](#module-reference)
2. [Threading Model](#threading-model)
3. [Configuration System](#configuration-system)
4. [Security Architecture](#security-architecture)
5. [Error Handling](#error-handling)
6. [Performance](#performance)
7. [Data Persistence](#data-persistence)
8. [Hot-Reload System](#hot-reload-system)
9. [Icon & Font Pipeline](#icon--font-pipeline)
10. [API Reference](#api-reference)

---

## 📦 Module Reference

### `easycut.py` — Main Application (1,868 lines)

The central orchestrator. Contains `EasyCutApp` class which:
- Creates the main window, header bar, and tab notebook
- Implements all 7 tabs (Login, Download, Batch, Live, Audio, History, About)
- Contains all download/convert/batch/live-stream business logic
- Manages threading for non-blocking operations
- Handles theme toggle and language switching (hot-reload)
- Manages download history (JSON persistence)

```python
class EasyCutApp:
    def __init__(self, root):
        # Config, fonts, theme, design tokens
        # Header bar, tab notebook, all screens
    
    def toggle_theme(self)          # Instant dark/light switch
    def change_language(self, lang)  # Instant language switch
    def handle_download(self)        # Video download (threaded)
    def handle_batch_download(self)  # Batch download (threaded)
    def handle_audio_conversion(self)# Audio conversion (threaded)
    def load_history(self)           # Load from JSON
    def save_history(self)           # Save to JSON
    def run_in_thread(self, target)  # Background execution
```

**Imports:**
- `i18n` — translations
- `ui_enhanced` — ConfigManager, LogWidget, StatusBar, LoginPopup
- `design_system` — ModernTheme, DesignTokens, Typography, Spacing, Icons
- `modern_components` — ModernButton, ModernCard, ModernInput, ModernAlert, etc.
- `font_loader` — setup_fonts(), LOADED_FONT_FAMILY
- `icon_manager` — icon loading
- `donation_system` — DonationButton
- `ui.screens` — LoginScreen, DownloadScreen, BatchScreen, LiveScreen, AudioScreen, HistoryScreen, AboutScreen

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

### `design_system.py` — Design Tokens (515 lines)

Design token system with icon-branded colors.

```python
class ColorPalette:
    DARK = { "bg_primary": "#0A0E27", ... }
    LIGHT = { "bg_primary": "#FFFFFF", ... }

class ModernTheme:
    def __init__(self, dark_mode=True, font_family="Segoe UI")

class DesignTokens:
    def __init__(self, dark_mode=True)
    def get_color(self, key: str) -> str
    def get_font(self, size: str, weight: str) -> tuple

class Typography:    # Font size constants (XS through XXL)
class Spacing:       # Spacing constants (XS through XXL)
class Icons:         # Icon name → file mapping
```

**Color branding:** Imports `color_extractor.py` to extract accent colors from `app_icon.png`. The icon's primary color (`#f85451` coral red) is used as `accent_primary` across both themes.

---

### `modern_components.py` — Custom Widgets (621 lines)

Modern UI components built on Tkinter Canvas and Frame:

| Class | Purpose |
|-------|---------|
| `ModernButton` | Styled button with hover, colors, icons |
| `ModernCard` | Container with title and border |
| `ModernInput` | Labeled input with validation |
| `ModernAlert` | Notification bar (success/warning/error/info) |
| `ModernDialog` | Modal dialog window |
| `ModernIconButton` | Icon-only button |
| `ModernTabHeader` | Tab header with icon and label |

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

### `color_extractor.py` — Icon Color Extraction (197 lines)

Extracts vibrant and dominant colors from `assets/app_icon.png` using Pillow:

```python
def extract_vibrant_colors(image_path) -> dict    # {primary, accent, secondary}
def extract_dominant_colors(image_path, n=5) -> list
def get_theme_palette_from_icon() -> dict          # {DARK: {...}, LIGHT: {...}}
def get_icon_path() -> Path
```

Used by `design_system.py` to brand the accent color from the app logo.

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

### `theme/theme_manager.py` — Theme Engine (376 lines)

Unified theme manager used by `BaseScreen` and factories:

```python
class ThemeManager:
    def __init__(self, dark_mode=True)
    def get_color(self, key: str) -> str
    def get_font(self, size: str, weight: str) -> tuple
    def toggle(self)
    def apply_to_style(self, style: ttk.Style)
```

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
| `login_screen.py` | 123 | `LoginScreen` — authentication tab |
| `download_screen.py` | 317 | `DownloadScreen` — video download with quality/format |
| `batch_screen.py` | 173 | `BatchScreen` — multi-URL batch processing |
| `live_screen.py` | 229 | `LiveScreen` — live stream recording |
| `audio_screen.py` | 160 | `AudioScreen` — audio extraction/conversion |
| `history_screen.py` | 158 | `HistoryScreen` — card-based history display |
| `about_screen.py` | 210 | `AboutScreen` — app info and credits |

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

### Color Extraction

1. `color_extractor.py` loads `assets/app_icon.png`
2. Extracts dominant colors via pixel clustering
3. Returns primary color (`#f85451` coral red)
4. `design_system.py` uses this as `accent_primary` in both palettes

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
tokens.get_color("bg_primary")           # "#0A0E27"
tokens.get_color("accent_primary")       # "#f85451"
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
