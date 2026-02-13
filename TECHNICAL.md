# 🔧 EasyCut - Technical Documentation

**Author:** Deko Costa  
**Version:** 1.0.0  
**Python Version:** 3.8+  
**Repository:** [github.com/dekouninter/EasyCut](https://github.com/dekouninter/EasyCut)

---

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Module Descriptions](#module-descriptions)
3. [Hot-Reload Implementation](#hot-reload-implementation)
4. [Threading Model](#threading-model)
5. [Configuration System](#configuration-system)
6. [Security Architecture](#security-architecture)
7. [Error Handling](#error-handling)
8. [Performance Optimization](#performance-optimization)
9. [Data Persistence](#data-persistence)
10. [API Reference](#api-reference)

---

## 🏗️ Architecture Overview

### Design Pattern: MVC (Model-View-Controller)

```
┌─────────────────────────────────────┐
│        EasyCutApp (Controller)      │
│  - Main application logic           │
│  - Event handling                   │
│  - Tab management                   │
└────────────────┬────────────────────┘
         ┌───────┴────────┬──────────────┐
         │                │              │
    ┌────▼────┐    ┌─────▼────┐   ┌────▼────┐
    │ i18n    │    │ ui_      │   │donation_│
    │(Model)  │    │enhanced  │   │  system │
    │         │    │(View)    │   │ (View)  │
    └─────────┘    └──────────┘   └─────────┘
         │                │              │
         └────────────────┴──────────────┘
              ↓ Threading & Storage ↓
         ┌──────────────────────────┐
         │  JSON Config & History   │
         │  Windows Keyring         │
         │  Application Logging     │
         └──────────────────────────┘
```

### Module Interdependencies

```
easycut.py (Main App)
├── Imports: i18n, ui_enhanced, donation_system
├── Creates: 6 UI Tabs
├── Manages: Threads, Config, History
└── Handles: Download/Convert/Auth Events

i18n.py (Translation Engine)
├── Manages: EN/PT translations
├── Provides: 150+ translation strings
├── Supports: Hot-reload language changes
└── Default: English

ui_enhanced.py (UI Components)
├── Theme: Dark/Light colors, hot-reload toggle
├── ConfigManager: Persistent settings
├── LogWidget: Auto-scrolling text display
├── StatusBar: Login/status info
├── LoginPopup: Authentication dialog
├── LanguageSelector: Language dropdown
└── All: Support hot-reload without restart

donation_system.py (Support Interface)
├── DonationWindow: Modal dialog
├── DonationButton: Floating action button
├── Links: Buy Me a Coffee, Livepix
└── All: Opens links in browser
```

---

## 📦 Module Descriptions

### 1️⃣ `easycut.py` - Main Application (400 lines)

**Purpose:** Core application controller and UI orchestration

**Key Classes:**

#### `EasyCutApp(tk.Tk)`
```python
class EasyCutApp(tk.Tk):
    """Main application window with 6 tabs"""
    
    # Initialization
    def __init__(self)
    def setup_fonts()
    def setup_ui()
    def apply_theme()
    
    # Hot-Reload Features
    def toggle_theme()          # Instant dark/light switch
    def change_language(lang)   # Instant language switch
    
    # Tab Setup
    def create_login_tab()
    def create_download_tab()
    def create_batch_tab()
    def create_audio_tab()
    def create_history_tab()
    def create_about_tab()
    
    # Helper Methods
    def open_login_popup()
    def handle_download()
    def handle_batch_download()
    def handle_audio_conversion()
    def load_history()
    def save_history()
    def open_output_folder()
    def open_donation_window()
    def update_ui_text()          # For language changes
    
    # Threading
    def run_in_thread(target)     # Non-blocking execution
```

**Key Features:**
- ✅ Professional header bar with 🎬 logo
- ✅ Integrated theme/language toggle buttons
- ✅ Popup-only login (no embedded login tab content)
- ✅ Real-time logging with timestamps
- ✅ Asynchronous operations (threading)
- ✅ Error handling with user-friendly messages

**Dependencies:**
- tkinter (GUI framework)
- threading (async operations)
- i18n (translations)
- ui_enhanced (UI components)
- donation_system (support links)

**Default Settings:**
- Language: English (configurable to Portuguese)
- Theme: Dark (configurable to Light)
- Window size: 1000x700
- Columns: 2 (for tab layout)

---

### 2️⃣ `i18n.py` - Internationalization (338 lines)

**Purpose:** Multi-language support with hot-reload capability

**Key Classes:**

#### `Translator`
```python
class Translator:
    """Manages translations for EN and PT"""
    
    def __init__(self, language='en')
    def set_language(lang) -> bool      # Hot-reload support
    def get(key, default='') -> str
    def get_all() -> dict
```

**Translation Dictionary Structure:**
```python
TRANSLATIONS = {
    # Header labels
    "app_title": {"en": "EasyCut", "pt": "EasyCut"},
    
    # Tab names
    "tab_login": {"en": "Login", "pt": "Conexão"},
    "tab_download": {"en": "Download", "pt": "Download"},
    
    # Buttons
    "btn_login": {"en": "Login", "pt": "Conectar"},
    "btn_download": {"en": "Download", "pt": "Baixar"},
    
    # Messages
    "msg_success": {"en": "Download started!", "pt": "Download iniciado!"},
    "msg_error": {"en": "Error occurred", "pt": "Erro ocorreu"},
    
    # 140+ more translations...
}
```

**Supported Languages:**
- **English (en)** - Default, professional
- **Português (pt)** - Full Brazilian Portuguese support

**Features:**
- ✅ 150+ translated strings
- ✅ Consistent key naming
- ✅ Easy fallback to English
- ✅ Hot-reload support (no restart needed)
- ✅ Missing key detection

**Default Initialization:**
```python
translator = Translator("en")  # Changed from "pt"
```

---

### 3️⃣ `ui_enhanced.py` - UI Components & Theming (380 lines)

**Purpose:** Reusable UI components with theme support

**Key Classes:**

#### `Theme`
```python
class Theme:
    """Manages dark/light themes"""
    
    DARK_THEME = {
        "bg": "#1E1E1E",        # Dark background
        "fg": "#FFFFFF",        # White text
        "btn_bg": "#0D47A1",    # Blue buttons
        "btn_fg": "#FFFFFF",    # White text
        # ... 15+ more colors
    }
    
    LIGHT_THEME = {
        "bg": "#F5F5F5",        # Light background
        "fg": "#000000",        # Black text
        "btn_bg": "#1976D2",    # Lighter blue
        "btn_fg": "#FFFFFF",    # White text
        # ... 15+ more colors
    }
    
    def __init__(self, dark_mode=True)
    def toggle() -> bool        # Returns new mode
    def get(key) -> str         # Get color value
```

#### `ConfigManager`
```python
class ConfigManager:
    """Persistent configuration storage"""
    
    def __init__(self, config_path)
    def load() -> dict
    def save()
    def get(key, default=None)
    def set(key, value)
    def create_default_config()
```

**Configuration File:** `config/config.json`
```json
{
    "dark_mode": true,
    "language": "en",
    "username": "",
    "output_folder": "",
    "download_quality": "best",
    "audio_format": "mp3",
    "audio_bitrate": "192",
    "window_width": 1000,
    "window_height": 700
}
```

#### `LogWidget(tk.Text)`
```python
class LogWidget(tk.Text):
    """Scrolling log display with auto-scroll"""
    
    def __init__(self, parent)
    def log(message)            # Add timestamped message
    def clear()
```

#### `StatusBar(tk.Frame)`
```python
class StatusBar(tk.Frame):
    """Login status display"""
    
    def set_status(status)
    def clear_status()
```

#### `LoginPopup(tk.Toplevel)`
```python
class LoginPopup(tk.Toplevel):
    """Modal authentication dialog"""
    
    def __init__(self, parent, on_success)
    def authenticate()
    def on_auth_success()
```

#### `LanguageSelector(tk.Frame)`
```python
class LanguageSelector(tk.Frame):
    """Language dropdown selector"""
    
    def __init__(self, parent, on_change)
```

**Features:**
- ✅ Dark/Light theme toggle
- ✅ Hot-reload support
- ✅ Persistent configuration
- ✅ Auto-scrolling logs
- ✅ Modal dialogs
- ✅ Responsive widgets

---

### 4️⃣ `donation_system.py` - Support Links (123 lines)

**Purpose:** Donation interface and support buttons

**Key Classes:**

#### `DonationWindow(tk.Toplevel)`
```python
class DonationWindow(tk.Toplevel):
    """Modal window with donation options"""
    
    COFFEE_URL = "https://buymeacoffee.com/dekocosta"
    LIVEPIX_URL = "https://livepix.gg/dekocosta"
    
    def __init__(self, parent)
    def open_link(url)
```

#### `DonationButton(tk.Frame)`
```python
class DonationButton(tk.Frame):
    """Floating action button for donations"""
    
    def __init__(self, parent)
    def on_click()
```

**Features:**
- ✅ Buy Me a Coffee integration
- ✅ Livepix support link
- ✅ hover effects
- ✅ Browser opening
- ✅ Modal presentation

**Support Links:**
- coffee: https://buymeacoffee.com/dekocosta
- livepix: https://livepix.gg/dekocosta

---

## 🔄 Hot-Reload Implementation

### How Hot-Reload Works

**Problem:** Traditional apps require restart for theme/language changes

**Solution:** Rebuild UI in-place without restarting application

### Code Architecture

```python
# In easycut.py
def toggle_theme(self):
    """Toggle theme with instant UI rebuild"""
    # 1. Update state
    self.dark_mode = self.theme.toggle()
    
    # 2. Save config
    self.config_manager.set("dark_mode", self.dark_mode)
    
    # 3. Apply theme to widgets
    self.apply_theme()
    
    # 4. Rebuild entire UI
    self.setup_ui()

def change_language(self, lang):
    """Change language with instant UI rebuild"""
    # 1. Update translator
    if self.translator.set_language(lang):
        # 2. Save config
        self.config_manager.set("language", lang)
        
        # 3. Rebuild entire UI
        self.setup_ui()

def apply_theme(self):
    """Apply color scheme to all widgets"""
    theme_colors = self.theme.DARK_THEME if self.dark_mode \
                   else self.theme.LIGHT_THEME
    
    self.configure(bg=theme_colors["bg"])
    # Apply to all widgets...
```

### UI Rebuild Process

1. **Destroy Old Widgets** - Remove all tabs, frames, buttons
2. **Clear Translations** - Reset all text labels
3. **Create New Widgets** - Rebuild entire UI with new theme/language
4. **Apply Colors** - Set colors from new theme
5. **Restore Data** - Load history, config, logs
6. **No Restart** - App continues running normally

### Performance Characteristics

| Operation | Time | User Experience |
|-----------|------|---|
| Theme Toggle | ~200ms | Instant |
| Language Change | ~300ms | Instant |
| Full Rebuild | ~300ms | Smooth transition |
| No Restart | 0s | Seamless |

---

## 🧵 Threading Model

### Problem: UI Freezing

Downloads and conversions are I/O intensive (network, disk, CPU)

### Solution: Asynchronous Threading

```python
def run_in_thread(self, target, *args, **kwargs):
    """Execute function in background thread"""
    thread = threading.Thread(
        target=target,
        args=args,
        kwargs=kwargs,
        daemon=True  # Don't block app exit
    )
    thread.start()

# Usage:
def handle_download(self):
    self.run_in_thread(
        self.download_video,
        url=url_entry.get(),
        quality=quality_var.get()
    )
```

### Threading Operations

| Operation | Thread Type | Impact |
|-----------|---|---|
| **Download Video** | Background | No UI freeze |
| **Convert Audio** | Background | No UI freeze |
| **Batch Download** | Background | Parallel processing |
| **Load History** | Main | Minimal UI impact |
| **Update Logger** | Main | Real-time display |

### Thread Safety

- ✅ Main operations run in background threads
- ✅ UI updates always on main thread
- ✅ Thread-safe logging
- ✅ Daemon threads (don't block app exit)
- ✅ No race conditions

---

## 💾 Configuration System

### File Structure

```
config/
├── config.json ........................ Application settings
├── history_downloads.json ........... Download history
└── app.log .......................... Application log
```

### Configuration File (`config.json`)

```json
{
    "dark_mode": true,
    "language": "en",
    "username": "user@email.com",
    "output_folder": "C:\\Users\\User\\Downloads",
    "download_quality": "best",
    "audio_format": "mp3",
    "audio_bitrate": "192",
    "window_width": 1000,
    "window_height": 700,
    "remember_username": false
}
```

### History File (`history_downloads.json`)

```json
{
    "downloads": [
        {
            "url": "https://www.youtube.com/watch?v=...",
            "title": "Video Title",
            "date": "2024-02-13 15:30:45",
            "status": "success",
            "format": "mp4",
            "size_mb": 45.3
        }
    ]
}
```

### Configuration API

```python
config_manager = ConfigManager("config/config.json")

# Load
config = config_manager.load()

# Get value
language = config_manager.get("language", "en")

# Set value
config_manager.set("language", "pt")

# Save
config_manager.save()
```

---

## 🔐 Security Architecture

### Credential Storage

```python
import keyring

# Store password
keyring.set_password(
    service_name="EasyCut",
    username="user@email.com",
    password="password123"
)

# Retrieve password
password = keyring.get_password(
    service_name="EasyCut",
    username="user@email.com"
)

# Delete password
keyring.delete_password(
    service_name="EasyCut",
    username="user@email.com"
)
```

### Windows Keyring Integration

- ✅ Uses OS-level encryption
- ✅ Passwords never stored as plaintext
- ✅ Automatic encryption/decryption
- ✅ Secure across Windows versions

### Input Validation

```python
# Email validation
import re
EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

# URL validation
def is_valid_youtube_url(url):
    return 'youtube.com' in url or 'youtu.be' in url

# Time format validation (MM:SS)
def is_valid_time_format(time_str):
    pattern = r'^([0-5][0-9]):([0-5][0-9])$'
    return re.match(pattern, time_str) is not None
```

### Error Handling

- ✅ Try/catch on all operations
- ✅ User-friendly error messages
- ✅ Logging of technical details
- ✅ Graceful degradation

---

## ⚠️ Error Handling

### Exception Hierarchy

```
Exception
├── ValueError
│   ├── Invalid URL format
│   ├── Invalid email format
│   └── Invalid time format
│
├── KeyError
│   ├── Missing config key
│   └── Missing translation key
│
├── IOError
│   ├── File not found
│   ├── Permission denied
│   └── Disk full
│
├── RuntimeError
│   ├── FFmpeg not installed
│   ├── Download failed
│   └── Conversion failed
│
└── Custom
    ├── AuthenticationError
    └── ConfigurationError
```

### Error Display

```python
try:
    result = download_video(url)
except ValueError as e:
    messagebox.showerror(
        title=translator.get("error_title"),
        message=f"Invalid URL: {str(e)}"
    )
except Exception as e:
    log_widget.log(f"ERROR: {str(e)}")
    messagebox.showerror(
        title=translator.get("error_title"),
        message=translator.get("msg_error_generic")
    )
```

---

## ⚡ Performance Optimization

### Optimization Strategies

| Strategy | Implementation | Benefit |
|----------|---|---|
| **Lazy Loading** | Tabs created on demand | Faster startup |
| **Caching** | Theme colors cached | Faster UI updates |
| **Threading** | I/O in background | No UI freeze |
| **JSON Config** | Lightweight persistence | Fast load/save |
| **Minimal Widgets** | Only necessary widgets shown | Lower memory |
| **Efficient Logging** | Append-only file | Fast write |

### Startup Time Target

- Cold start: < 2 seconds
- Hot reload: < 500ms

### Memory Usage

- Base app: ~50MB
- With active download: ~80MB
- Historical limit: 100 downloads in history

---

## 📊 Data Persistence

### Persistent Data Types

| Data | Storage | Format | Persistence |
|------|---------|--------|---|
| **Settings** | config.json | JSON | Application lifetime |
| **Credentials** | Windows Keyring | Encrypted | System lifetime |
| **History** | history_downloads.json | JSON | Until cleared |
| **Logs** | app.log | Plain text | Until rotated |

### Data Lifecycle

```
Application Start
    ↓
Load config.json (or create default)
    ↓
Retrieve password from Keyring (if needed)
    ↓
Load history_downloads.json
    ↓
Application Running
    ↓
User actions → Update config/history
    ↓
Save config to config.json
    ↓
Log messages to app.log
    ↓
Application Exit
    ↓
All data persisted for next session
```

---

## 🔌 API Reference

### EasyCutApp Public Methods

```python
# Theme Management
app.toggle_theme()                      # Switch dark/light
app.apply_theme()                       # Apply theme colors
app.dark_mode  # Property: current mode (bool)

# Language Management
app.change_language(lang: str)          # Switch language (en/pt)
app.translator  # Property: translator instance

# Status Management
app.update_status(msg: str)             # Update status bar
app.clear_status()                      # Clear status

# Logging
app.log_widget.log(msg: str)           # Log message

# Configuration
app.config_manager.get(key: str)        # Get config value
app.config_manager.set(key: str, val)   # Set config value

# History
app.load_history()                      # Load download history
app.save_history()                      # Save download history
app.add_to_history(entry: dict)        # Add history entry

# Threading
app.run_in_thread(func, *args)         # Run async operation

# File Operations
app.open_output_folder()               # Open downloads folder
app.open_donation_window()             # Show donation dialog
```

### Translator API

```python
translator = Translator(language="en")

# Get translations
text = translator.get("app_title")      # "EasyCut"

# Get all translations
all_trans = translator.get_all()        # {"app_title": {...}, ...}

# Change language (hot-reload)
success = translator.set_language("pt") # True if successful
```

### Theme API

```python
theme = Theme(dark_mode=True)

# Toggle theme
new_mode = theme.toggle()               # Returns: False (switched to light)

# Get color
color = theme.get("bg")                 # "#1E1E1E" (dark) or "#F5F5F5" (light)
```

---

## 📖 Additional Resources

- 📄 [README.md](README.md) - User guide
- 📄 [QUICKSTART.md](QUICKSTART.md) - 5-minute setup
- 📄 [IMPLEMENTATION.md](IMPLEMENTATION.md) - Project status
- 📚 **Code Comments** - 200+ inline docstrings
- 💬 **Issues** - [GitHub Issues](https://github.com/dekouninter/EasyCut/issues)

---

## 🤝 Contributing

Contributions welcome!

1. Fork repository
2. Create feature branch
3. Make changes with comments
4. Test thoroughly
5. Submit pull request

---

## 📞 Support

- 🐛 **Bugs**: [Report on GitHub](https://github.com/dekouninter/EasyCut/issues)
- 💡 **Ideas**: [GitHub Discussions](https://github.com/dekouninter/EasyCut/discussions)
- ☕ **Support**: [Buy Me a Coffee](https://buymeacoffee.com/dekocosta)

---

**Made with ❤️ by Deko Costa**  
[github.com/dekouninter/EasyCut](https://github.com/dekouninter/EasyCut)
