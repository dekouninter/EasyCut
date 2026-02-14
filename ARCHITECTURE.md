# 🏗️ EasyCut - Professional Refactored Architecture

## 📋 Table of Contents

1. [Overview](#overview)
2. [Folder Structure](#folder-structure)
3. [Architectural Layers](#architectural-layers)
4. [Design Patterns](#design-patterns)
5. [Data Flow](#data-flow)
6. [Usage Guide](#usage-guide)
7. [Practical Examples](#practical-examples)

---

## 📌 Overview

### Problems Solved

| Problem | Solution | Benefit |
|---------|----------|---------|
| 2 duplicate theme systems | Unified ThemeManager | No conflicts, easy maintenance |
| 15+ repeated button decorations | ButtonFactory | DRY, visual consistency |
| 6 tabs with identical code | TabFactory | Reduced 400+ lines |
| Logging scattered everywhere | Centralized Logger | Traceability, structured |
| Config scattered in 10+ places | Unified ConfigManager | Single source of truth |
| No Service Layer | Decentralized Services | Separation of concerns |
| Monolithic easycut.py (1824 lines) | Specialized modules | Each file <300 lines |
| No exception handling | Custom exceptions | Clear, structured errors |

### Principles Applied

✅ **SOLID**
- **S**ingle Responsibility: Each module one responsibility
- **O**pen/Closed: Extensible without modification
- **L**iskov Substitution: Correct polymorphism
- **I**nterface Segregation: Small, focused interfaces
- **D**ependency Inversion: Depend on abstractions

✅ **DRY** (Don't Repeat Yourself)
- Factories eliminate repetition
- Reusable functions

✅ **KISS** (Keep It Simple, Stupid)
- Clear, linear architecture
- No over-engineering

✅ **YAGNI** (You Aren't Gonna Need It)
- Only what's necessary
- No speculative features

---

## 🗂️ Folder Structure

```
src/
├── core/                                  # 🔧 FOUNDATION LAYER
│   ├── __init__.py
│   ├── config.py          (ConfigManager)  # Unified config system
│   ├── constants.py       (Constants)      # Global constants & keys
│   ├── logger.py          (Logger)         # Centralized logging
│   ├── exceptions.py      (Exception*)     # Custom exception hierarchy
│   └── utils.py           (Utilities)      # Helper functions
│
├── theme/                                 # 🎨 THEME LAYER
│   ├── __init__.py
│   ├── theme_manager.py   (ThemeManager) # Unified theme (was split)
│   └── color_palette.py   (ColorPalette) # Color definitions only
│
├── ui/                                    # 🖼️ UI LAYER
│   ├── __init__.py
│   │
│   ├── factories/                        # WIDGET FACTORIES (decentralized)
│   │   ├── __init__.py
│   │   ├── widget_factory.py             # ButtonFactory, FrameFactory, etc
│   │   └── tab_factory.py                # TabFactory (scrollable tabs)
│   │
│   ├── components/                       # MODERN COMPONENTS (reusable)
│   │   ├── __init__.py
│   │   ├── modern_button.py              # ModernButton
│   │   ├── modern_card.py                # ModernCard
│   │   ├── modern_alert.py               # ModernAlert
│   │   ├── modern_input.py               # ModernInput
│   │   └── ... (other components)
│   │
│   └── screens/                          # TAB SCREENS (decentralized)
│       ├── __init__.py
│       ├── base_screen.py                # BaseScreen (base class)
│       ├── login_screen.py               # Login tab
│       ├── download_screen.py            # Download tab
│       ├── batch_screen.py               # Batch tab
│       ├── live_screen.py                # Live stream tab
│       ├── audio_screen.py               # Audio conversion tab
│       ├── history_screen.py             # History tab
│       └── about_screen.py               # About tab
│
├── services/                              # 🔌 SERVICE LAYER (decentralized logic)
│   ├── __init__.py
│   ├── base_service.py                   # BaseService (base class)
│   ├── download_service.py               # Download logic
│   ├── audio_service.py                  # Audio conversion
│   ├── history_service.py                # History management
│   ├── auth_service.py                   # Auth + Keyring
│   └── streaming_service.py              # Live/record logic
│
├── utils/                                 # 🛠️ UTILITIES
│   ├── __init__.py
│   ├── icon_helper.py                    # Icon loading (centralized)
│   ├── file_helper.py                    # File operations
│   └── validators.py                     # Input validation
│
├── easycut.py                            # 🎯 MAIN APP (~400 lines, orchestrates only)
└── main.py                               # Entry point
```

---

## 🏢 Architectural Layers

### 1️⃣ CORE LAYER (Foundation)

**Responsibility:** Application foundations
- Unified configuration
- Structured logging
- Custom exceptions
- Global constants

```python
from core.config import ConfigManager
from core.logger import get_logger
from core.exceptions import DownloadException
from core.constants import Constants

logger = get_logger(__name__)
config = ConfigManager()

try:
    quality = config.get("download_quality")
    logger.info(f"Using quality: {quality}")
except ConfigException as e:
    logger.error(f"Config error: {e}")
```

### 2️⃣ THEME LAYER (Visual Design)

**Responsibility:** App theme and design (unified from 3 systems)
- Colors (dark/light)
- Typography
- Spacing
- TTK styles

```python
from theme.theme_manager import ThemeManager

theme = ThemeManager(dark_mode=True)

# Get colors
bg = theme.get_color("bg_primary")  # "#0A0E27"

# Get fonts
font = theme.get_font("LG", "bold")  # ("Segoe UI", 18, "bold")

# Toggle theme
theme.toggle()  # Switches dark ↔ light

# Apply to ttk.Style
style = ttk.Style()
theme.apply_to_style(style)
```

### 3️⃣ UI FACTORIES (Widget Creation)

**Responsibility:** Create widgets consistently without repetition

```python
from ui.factories import (
    ButtonFactory,
    create_tab,
    create_tab_section,
    TabFactory
)

# Create button (all variants automatically styled)
btn = ButtonFactory.create_action_button(parent, "Download", on_click)
btn.pack()

# Create scrollable tab (common pattern)
tab_data = create_tab(notebook, "Download", theme, "⬇️", enable_scroll)

# Create section within tab
section = create_tab_section(tab_data["content"], "Video Settings")
section.pack(fill=tk.BOTH, expand=True)
```

### 4️⃣ UI COMPONENTS (Reusable Widgets)

**Responsibility:** Modern reusable components
- ModernButton (clean, styled)
- ModernCard (container with title)
- ModernAlert (notifications)
- ModernInput (labeled input)
- ... etc

```python
from ui.components import ModernAlert, ModernCard

# Alert
alert = ModernAlert(
    parent,
    message="Download complete!",
    variant="success",
    dismissible=True
)
alert.pack()

# Card
card = ModernCard(parent, title="Settings")
label = ttk.Label(card, text="Option 1")
label.pack()
```

### 5️⃣ UI SCREENS (Tab Implementations)

**Responsibility:** Each tab implements its own UI and logic
- LoginScreen
- DownloadScreen
- BatchScreen
- LiveScreen
- AudioScreen
- HistoryScreen
- AboutScreen

```python
from ui.screens import DownloadScreen

# Create screen
screen = DownloadScreen(notebook, theme, services)
screen.build()  # Builds the UI

# Get references if needed
log_widget = screen.get_log_widget()
```

### 6️⃣ SERVICES (Logic Decentralized)

**Responsibility:** All business logic separated from UI
- DownloadService (download/ffmpeg)
- AudioService (audio conversion)
- HistoryService (persistence)
- AuthService (OAuth/keyring)
- StreamingService (live streams)

```python
from services.download_service import DownloadService
from services.audio_service import AudioService

# Use service
download_svc = DownloadService()
result = download_svc.download(
    url="https://youtube.com/watch?v=...",
    quality="1080p",
    output_dir=Path.home() / "Downloads"
)

if result.success:
    logger.info(f"Downloaded: {result.filename}")
else:
    logger.error(f"Failed: {result.error}")
```

### 7️⃣ MAIN APP (Orchestrator)

**Responsibility:** Only orchestration
- Initialize subsystems
- Coordinate communication
- Manage lifecycle

```python
class EasyCutApp:
    def __init__(self, root):
        # Initialize core
        self.config = ConfigManager()
        self.logger = get_logger(__name__)
        
        # Initialize theme
        self.theme = ThemeManager(
            dark_mode=self.config.get("dark_mode")
        )
        
        # Initialize services
        self.download_svc = DownloadService()
        self.history_svc = HistoryService()
        
        # Build UI
        self.setup_ui()
    
    def setup_ui(self):
        # Create tabs using factories
        self.download_screen = DownloadScreen(...)
        self.batch_screen = BatchScreen(...)
        # ... etc
    
    def toggle_theme(self):
        self.theme.toggle()
        self.setup_ui()  # Rebuild with new theme
```

---

## 🎯 Design Patterns

### 1. Factory Pattern (Widget Creation)

```python
# ❌ BEFORE (repeated in 15+ places)
btn = ttk.Button(parent, text="Download", command=on_download)
btn.pack(side=tk.LEFT, padx=8)

# ✅ AFTER (with Factory)
from ui.factories import ButtonFactory
btn = ButtonFactory.create_action_button(parent, "Download", on_download)
btn.pack(side=tk.LEFT, padx=8)
```

### 2. Builder Pattern (Complex Widgets)

```python
# Create scrollable tab with factory
tab_data = TabFactory.create_scrollable_tab(
    notebook,
    tab_text="Download",
    theme=theme,
    icon_emoji="⬇️",
    enable_scroll_handler=app.enable_mousewheel_scroll
)

# Result:
# {
#   "frame": ttk.Frame,         ← tab frame added to notebook
#   "canvas": tk.Canvas,         ← for scrolling
#   "scrollbar": ttk.Scrollbar,  ← scrollbar
#   "content": ttk.Frame         ← where YOU add content
# }

# Use the content:
content = tab_data["content"]
ModernCard(content, "Settings").pack()
```

### 3. Strategy Pattern (Services)

```python
# Each service implements same interface
class BaseService:
    def execute(self): pass
    def validate(self): pass
    def cleanup(self): pass

class DownloadService(BaseService):
    def execute(self, url): ...
    def validate(self, url): ...

class AudioService(BaseService):
    def execute(self, input_file): ...
    def validate(self, format): ...

# Usage (polymorphic)
services: List[BaseService] = [
    DownloadService(),
    AudioService(),
    HistoryService()
]
for svc in services:
    svc.cleanup()  # Works for all
```

### 4. Observer Pattern (Theme Changes)

```python
# Config changes trigger UI update
config.on_change("dark_mode", self.handle_theme_change)

def handle_theme_change(self, old_value, new_value):
    self.theme.toggle()
    # Rebuild UI with new theme
    self.reinit_ui()  # ← automatic update
```

---

## 🔄 Data Flow

```
┌─────────────────────────────────────────────────────────┐
│                      USER ACTION                        │
│              (Click button, change theme)               │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                    UI SCREEN                            │
│   (DownloadScreen, BatchScreen, etc)                    │
│      ↓                                                  │
│   - Validates input                                    │
│   - Calls appropriate service                          │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                   SERVICE LAYER                         │
│   (DownloadService, AudioService, etc)                 │
│      ↓                                                  │
│   - Execute business logic                            │
│   - Handle errors                                     │
│   - Log operations                                   │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                  CORE LAYER                             │
│   (Config, Logger, Exceptions)                         │
│      ↓                                                  │
│   - Centralized config                                │
│   - Structured logging                                │
│   - Error handling                                   │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                  EXTERNAL SYSTEMS                       │
│   (YouTube, FFmpeg, Keyring, File System)              │
└─────────────────────────────────────────────────────────┘
```

---

## 💡 Usage Guide

### How to Create a New Screen/Tab

1. **Create file in `ui/screens/`**

```python
# ui/screens/custom_screen.py
from .base_screen import BaseScreen
from ..factories import TabFactory

class CustomScreen(BaseScreen):
    def build(self):
        # Use factory to create tab
        self.tab_data = TabFactory.create_scrollable_tab(
            self.notebook,
            "Custom",
            self.theme,
            "🎬"
        )
        
        # Add content
        content = self.tab_data["content"]
        # ... build UI ...
    
    def bind_events(self):
        # Bind user events
        pass
    
    def get_data(self):
        # Return current screen data
        return {}
```

2. **Register in main app**

```python
# easycut.py
from ui.screens import CustomScreen

class EasyCutApp:
    def init_screens(self):
        self.custom_screen = CustomScreen(
            self.notebook,
            self.theme,
            self.services
        )
        self.custom_screen.build()
```

### How to Create a New Service

1. **Create file in `services/`**

```python
# services/custom_service.py
from .base_service import BaseService
from ..core.logger import get_logger

logger = get_logger(__name__)

class CustomService(BaseService):
    def execute(self, **kwargs):
        """Main operation"""
        try:
            result = self._do_work(**kwargs)
            logger.info("Custom service completed")
            return result
        except Exception as e:
            logger.error(f"Custom service failed: {e}", exc_info=True)
            raise
    
    def validate(self, **kwargs):
        """Validate inputs"""
        pass
    
    def cleanup(self):
        """Cleanup resources"""
        pass
    
    def _do_work(self, **kwargs):
        """Actual work"""
        pass
```

2. **Register in main app**

```python
# easycut.py
from services.custom_service import CustomService

class EasyCutApp:
    def __init__(self):
        self.custom_svc = CustomService()
```

---

## 📚 Practical Examples

### Example 1: Add Button with Factory

```python
# ❌ BEFORE (without factory)
btn = ttk.Button(
    parent,
    text="Download",
    command=self.on_download_click
)
btn.pack(side=tk.LEFT, padx=8, pady=4)

# ✅ AFTER (with factory)
from ui.factories import ButtonFactory

btn = ButtonFactory.create_action_button(
    parent,
    "Download",
    self.on_download_click
)
btn.pack()  # Factory handles padding
```

### Example 2: Create Scrollable Tab

```python
# ❌ BEFORE (code duplicated 6 times)
frame = ttk.Frame(self.notebook)
self.notebook.add(frame, text="Download")

canvas = tk.Canvas(frame, bg="#0A0E27", highlightthickness=0)
scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
main = ttk.Frame(canvas)

main.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=main, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

self.enable_mousewheel_scroll(canvas, main)

# ✅ AFTER (with factory)
from ui.factories import TabFactory

tab_data = TabFactory.create_scrollable_tab(
    self.notebook,
    "Download",
    self.theme,
    "⬇️",
    self.enable_mousewheel_scroll
)

content = tab_data["content"]  # ← just use this for adding widgets
```

### Example 3: Download with Service

```python
# ❌ BEFORE (logic mixed in UI)
def start_download(self):
    url = self.url_entry.get()
    quality = self.quality_combo.get()
    
    # Download logic here...
    import yt_dlp
    ydl_opts = {"format": quality}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        # ... more logic ...

# ✅ AFTER (service decentralized)
def start_download(self):
    url = self.url_entry.get()
    quality = self.quality_combo.get()
    
    try:
        result = self.download_service.download(
            url=url,
            quality=quality,
            output_dir=self.config.get("output_folder")
        )
        
        if result.success:
            self.log_widget.info(f"✅ Downloaded: {result.filename}")
        else:
            self.log_widget.error(f"❌ Failed: {result.error}")
    
    except Exception as e:
        logger.error(f"Download failed: {e}", exc_info=True)
        messagebox.showerror("Error", str(e))
```

---

## 📊 Before vs After Comparison

| Aspect | Before | After |
|--------|--------|-------|
| **Lines in easycut.py** | 1824 | ~400 |
| **Code Duplication** | ~500 lines | Eliminated |
| **Theme Systems** | 2 conflicting | 1 unified |
| **Exceptions** | Generic try/except | Typed custom |
| **Logging** | Scattered | Centralized |
| **Config** | Dispersed | ConfigManager |
| **Unit Testing** | Difficult | Easy (services) |
| **Maintenance** | High coupling | Low coupling |
| **Extension** | Modify existing code | Add new file |

---

## ✅ Conclusion

The new architecture offers:

1. **🎯 Clarity** - Each layer has clear responsibility
2. **⚡ Performance** - No overhead, same speed
3. **🧪 Testability** - Services easily mockable
4. **🔧 Maintainability** - Changes isolated
5. **📈 Scalability** - Easy to add features
6. **🤝 Collaboration** - Code organized for teams
7. **📚 Documentation** - Self-documenting code
8. **🚀 Professionalism** - Industry-standard patterns
