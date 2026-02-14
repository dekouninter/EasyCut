# 🏗️ EasyCut - Arquitetura Refatorada Profissional

## 📋 Índice
1. [Visão Geral](#visão-geral)
2. [Estrutura de Pastas](#estrutura-de-pastas)
3. [Camadas Arquiteturais](#camadas-arquiteturais)
4. [Padrões de Design](#padrões-de-design)
5. [Fluxo de Dados](#fluxo-de-dados)
6. [Guia de Uso](#guia-de-uso)
7. [Exemplos Práticos](#exemplos-práticos)

---

## 📌 Visão Geral

### Problemas Resolvidos

| Problema | Solução | Benefício |
|----------|---------|-----------|
| 2 sistemas de theme duplicados | ThemeManager unificado | Sem conflitos, fácil manutenção |
| 15+ decorações de botões repetidas | ButtonFactory | DRY, consistência visual |
| 6 abas com código idêntico | TabFactory | Redução de 400+ linhas |
| Logging espalhado | Logger centralizado | Rastreabilidade, estruturado |
| Config espalhada | ConfigManager unificado | Single source of truth |
| Sem Service Layer | Services descentralizadas | Separação de concerns |
| easycut.py gigante (1824 linhas) | Módulos especializados | Cada arquivo <300 linhas |
| Sem exception handling | Custom exceptions | Erros claros e estruturados |

### Princípios Aplicados

✅ **SOLID**
- **S**ingle Responsibility: Cada módulo uma responsabilidade
- **O**pen/Closed: Extensível sem modificação
- **L**iskov Substitution: Polimorfismo correto
- **I**nterface Segregation: Interfaces pequenas e focadas
- **D**ependency Inversion: Depender de abstrações

✅ **DRY** (Don't Repeat Yourself)
- Factories eliminam repetição
- Funções reutilizáveis

✅ **KISS** (Keep It Simple, Stupid)
- Arquitetura clara e linear
- Sem over-engineering

✅ **YAGNI** (You Aren't Gonna Need It)
- Apenas o necessário
- Sem features especulativas

---

## 🗂️ Estrutura de Pastas

```
src/
├── core/                                  # 🔧 FOUNDATION LAYER
│   ├── __init__.py
│   ├── config.py          (ConfigManager)  # Unified config system
│   ├── constants.py       (Constants)     # Global constants & keys
│   ├── logger.py          (Logger)        # Centralized logging
│   ├── exceptions.py      (Exception*)    # Custom exception hierarchy
│   └── utils.py          (Utilities)      # Helper functions
│
├── theme/                                 # 🎨 THEME LAYER
│   ├── __init__.py
│   ├── theme_manager.py   (ThemeManager) # Unified theme (was split)
│   └── color_palette.py   (ColorPalette) # Color definitions only
│
├── ui/                                    # 🖼️ UI LAYER
│   ├── __init__.py
│   │
│   ├── factories/                        # WIDGET FACTORIES (descentralizado)
│   │   ├── __init__.py
│   │   ├── widget_factory.py             # ButtonFactory, FrameFactory, etc
│   │   └── tab_factory.py                # TabFactory (scrollable tabs)
│   │
│   ├── components/                       # MODERN COMPONENTS (reutilizáveis)
│   │   ├── __init__.py
│   │   ├── modern_button.py              # ModernButton (refatorado)
│   │   ├── modern_card.py                # ModernCard
│   │   ├── modern_alert.py               # ModernAlert (fixed)
│   │   ├── modern_input.py               # ModernInput
│   │   └── ... (outros componentes)
│   │
│   └── screens/                          # TAB SCREENS (descentralizados)
│       ├── __init__.py
│       ├── base_screen.py                # BaseScreen (classe base)
│       ├── download_screen.py            # Download tab
│       ├── batch_screen.py               # Batch tab
│       ├── live_screen.py                # Live tab
│       ├── audio_screen.py               # Audio tab
│       ├── history_screen.py             # History tab
│       └── about_screen.py               # About tab
│
├── services/                              # 🔌 SERVICE LAYER (lógica descentralizada)
│   ├── __init__.py
│   ├── base_service.py                   # BaseService (classe base)
│   ├── download_service.py               # Download logic
│   ├── audio_service.py                  # Audio conversion
│   ├── history_service.py                # History management
│   ├── auth_service.py                   # Auth + Keyring
│   └── streaming_service.py              # Live/record logic
│
├── utils/                                 # 🛠️ UTILITIES
│   ├── __init__.py
│   ├── icon_helper.py                    # Icon loading (centralizado)
│   ├── file_helper.py                    # File operations
│   └── validators.py                     # Input validation
│
├── easycut.py                            # 🎯 MAIN APP (limpo, só orquestra)
└── main.py                               # Entry point
```

---

## 🏢 Camadas Arquiteturais

### 1️⃣ CORE LAYER (Foundation)

**Responsabilidade:** Fundações da aplicação
- Configuração centralizada
- Logging estruturado
- Exceções customizadas
- Constantes globais

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

**Responsabilidade:** Tema e design do app (foi theme_manager + design_system)
- Cores (dark/light)
- Tipografia
- Espaçamento
- Estilos TTK

```python
from theme.theme_manager import ThemeManager

theme = ThemeManager(dark_mode=True)

# Get colors
bg = theme.get_color("bg_primary")  # "#0A0E27"

# Get fonts
font = theme.get_font("LG", "bold")  # ("Segoe UI", 18, "bold")

# Toggle theme
theme.toggle()  # Muda de dark ↔ light

# Apply to ttk.Style
style = ttk.Style()
theme.apply_to_style(style)
```

### 3️⃣ UI FACTORIES (Widget Creation)

**Responsabilidade:** Criar widgets de forma consistente, sem repetição

```python
from ui.factories import (
    ButtonFactory,
    create_tab,
    create_tab_section,
    TabFactory
)

# Create button (todas as variantes automáticamente estilizadas)
btn = ButtonFactory.create_action_button(parent, "Download", on_click)
btn.pack()

# Create scrollable tab (padrão comum)
tab_data = create_tab(notebook, "Download", theme, "⬇️", enable_scroll)

# Create section within tab
section = create_tab_section(tab_data["content"], "Video Settings")
section.pack(fill=tk.BOTH, expand=True)
```

### 4️⃣ UI COMPONENTS (Reusable Widgets)

**Responsabilidade:** Componentes modernos reutilizáveis
- ModernButton (já existe, limpo)
- ModernCard (ja existe, limpo)
- ModernAlert (foi fixado)
- ... etc

```python
from modern_components import ModernAlert, ModernCard

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

**Responsabilidade:** Cada tab implementa sua própria UI e lógica
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

### 6️⃣ SERVICES (Logic Descentralizada)

**Responsabilidade:** Toda lógica de negócio separada da UI
- DownloadService (download/ffmpeg)
- AudioService (áudio conversion)
- HistoryService (persistence)
- AuthService (OAuth/keyring)
- StreamingService (live streams)

```python
from services.download_service import DownloadService
from services.audio_service import AudioService

# Usar serviço
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

**Responsabilidade:** Apenas orquestração
- Inicializa subsistemas
- Coordena comunicação
- Gerencia lifecycle

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

## 🎯 Padrões de Design

### 1. Factory Pattern (Widget Creation)

```python
# ❌ ANTES (repetido em 15+ lugares)
btn = ttk.Button(parent, text="Download", command=on_download)
btn.pack(side=tk.LEFT, padx=8)

# ✅ DEPOIS (Factory)
from ui.factories import ButtonFactory
btn = ButtonFactory.create_action_button(parent, "Download", on_download)
btn.pack(side=tk.LEFT, padx=8)
```

### 2. Builder Pattern (Complex Widgets)

```python
# Criar tab scrollable com factory
tab_data = TabFactory.create_scrollable_tab(
    notebook,
    tab_text="Download",
    theme=theme,
    icon_emoji="⬇️",
    enable_scroll_handler=app.enable_mousewheel_scroll
)

# Resultado:
# {
#   "frame": ttk.Frame,      ← tab frame added to notebook
#   "canvas": tk.Canvas,      ← for scrolling
#   "scrollbar": ttk.Scrollbar, ← scrollbar
#   "content": ttk.Frame      ← where YOU add content
# }

# Use o content:
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

## 🔄 Fluxo de Dados

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
│   -  Execute business logic                           │
│   - Handle errors                                      │
│   - Log operations                                    │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                  CORE LAYER                             │
│   (Config, Logger, Exceptions)                         │
│      ↓                                                  │
│   - Centralized config                                │
│   - Structured logging                                │
│   - Error handling                                    │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                  EXTERNAL SYSTEMS                       │
│   (YouTube, FFmpeg, Keyring, File System)              │
└─────────────────────────────────────────────────────────┘
```

---

## 💡 Guia de Uso

### Como Criar Nova Tela/Tab

1. **Criar arquivo em `ui/screens/`**

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

2. **Registrar em main app**

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

### Como Criar Novo Service

1. **Criar arquivo em `services/`**

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

2. **Registrar em main app**

```python
# easycut.py
from services.custom_service import CustomService

class EasyCutApp:
    def __init__(self):
        self.custom_svc = CustomService()
```

---

## 📚 Exemplos Práticos

### Exemplo 1: Adicionar Botão com Factory

```python
# ❌ ANTES (sem factory)
btn = ttk.Button(
    parent,
    text="Download",
    command=self.on_download_click
)
btn.pack(side=tk.LEFT, padx=8, pady=4)

# ✅ DEPOIS (com factory)
from ui.factories import ButtonFactory

btn = ButtonFactory.create_action_button(
    parent,
    "Download",
    self.on_download_click
)
btn.pack()  # Factory handles padding
```

### Exemplo 2: Criar Tab Scrollable

```python
# ❌ ANTES (código duplicado 6 vezes)
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

# ✅ DEPOIS (com factory)
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

### Exemplo 3: Download com Service

```python
# ❌ ANTES (lógica misturada na UI)
def start_download(self):
    url = self.url_entry.get()
    quality = self.quality_combo.get()
    
    # Download logic aqui...
    import yt_dlp
    ydl_opts = {"format": quality}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        # ... mais lógica ...

# ✅ DEPOIS (service descentralizado)
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

## 📊 Comparação: Antes vs Depois

| Aspecto | Antes | Depois |
|---------|-------|--------|
| **Linhas em easycut.py** | 1824 | ~400 |
| **Duplicação de código** | ~500 linhas | Eliminada |
| **Themes duplicados** | 2 sistemas | 1 ThemeManager |
| **Exceções** | try/except genéricos | Exceções typed |
| **Logging** | Disperso | Centralizado |
| **Config** | Espalhada | ConfigManager |
| **Teste unitário** | Difícil | Fácil (services) |
| **Manutenção** | Alto acoplamento | Baixo acoplamento |
| **Extensão** | Modificar código existed | Adicionar novo arquivo |

---

## ✅ Conclusão

A nova arquitetura oferece:

1. **🎯 Clareza** - Cada camada tem responsabilidade clara
2. **⚡ Performance** - Sem overhead, mesma velocidade
3. **🧪 Testabilidade** - Services facilmente mockáveis
4. **🔧 Manutenibilidade** - Mudanças isoladas
5. **📈 Escalabilidade** - Fácil adicionar features
6. **🤝 Colaboração** - Código organizado para trabalho em equipe
7. **📚 Documentação** - Código auto-explicativo
8. **🚀 Profissionalismo** - Padrões industry-standard

