# 🎨 Ícones e Assets do EasyCut

## 📦 Pacotes de Ícones Incluídos

### Feather Icons (MIT License)
- **Localização**: `assets/feather-main/icons/`
- **Quantidade**: 286 ícones SVG
- **Licença**: MIT (uso comercial permitido)
- **Fonte**: https://github.com/feathericons/feather
- **Estilo**: Minimalista, linhas limpas, perfeito para UI moderna

## 🚀 Como Usar os Ícones

### Opção 1: Usar IconManager (Recomendado)

```python
from src.icon_manager import icon_manager, get_ui_icon

# Pegar ícone específico
download_icon = icon_manager.get_icon("download", size=16, color="#5B8CFF")

# Usar em botão Tkinter
btn = ttk.Button(parent, image=download_icon, text="Download")
btn.image = download_icon  # Manter referência!

# Usar ícone mapeado da UI
theme_icon = get_ui_icon("theme_dark", size=20)
```

### Opção 2: Converter SVG para PNG

Se você tem `cairosvg` instalado:

```bash
# Instalar dependência
pip install cairosvg

# Converter ícones
python scripts/convert_icons.py
```

Isso criará PNGs em `assets/icons/` para todos os ícones usados na UI.

### Opção 3: Usar Emojis (Fallback Automático)

Se PNG não estiver disponível, o IconManager usa emojis automaticamente:

```python
icon = icon_manager.get_icon("download")  # Retorna ⬇ como emoji
```

## 📋 Ícones Mapeados para UI

O `IconManager` já tem ícones mapeados para cada parte da UI:

| Chave | Ícone Feather | Emoji Fallback | Uso |
|-------|---------------|----------------|-----|
| `theme_dark` | `moon` | 🌙 | Tema escuro |
| `theme_light` | `sun` | ☀ | Tema claro |
| `login` | `log-in` | → | Login YouTube |
| `logout` | `log-out` | ← | Sair |
| `folder` | `folder` | 📁 | Abrir pasta |
| `language` | `globe` | 🌐 | Idioma |
| `download` | `download` | ⬇ | Download |
| `verify` | `search` | 🔍 | Verificar URL |
| `music` | `music` | 🎵 | Modo áudio |
| `video` | `video` | 🎬 | Modo vídeo |
| `live` | `radio` | 📻 | Live stream |
| `record` | `circle` | ⏺ | Gravar |
| `stop` | `stop-circle` | ⏹ | Parar |
| `batch` | `layers` | ☰ | Downloads em lote |
| `history` | `clock` | 🕐 | Histórico |
| `github` | `github` | 🐙 | GitHub |
| `coffee` | `coffee` | ☕ | Apoiar |
| `success` | `check-circle` | ✓ | Sucesso |
| `error` | `x-circle` | ✗ | Erro |
| `warning` | `alert-triangle` | ⚠ | Aviso |

## 🎯 Exemplo Completo

```python
from src.icon_manager import get_ui_icon
import tkinter as tk
from tkinter import ttk

# Criar janela
root = tk.Tk()

# Pegar ícone
icon = get_ui_icon("download", size=16, color="#5B8CFF")

# Usar em botão
btn = ttk.Button(root, image=icon, text=" Download", compound="left")
btn.image = icon  # IMPORTANTE: manter referência!
btn.pack()

root.mainloop()
```

## 📁 Estrutura de Diretórios

```
assets/
├── app_icon.ico              # Ícone do app (Windows)
├── app_icon.png              # Ícone do app (PNG)
├── feather-main/             # Pacote Feather Icons
│   └── icons/                # 286 ícones SVG
│       ├── download.svg
│       ├── music.svg
│       ├── video.svg
│       └── ...
├── icons/                    # PNGs convertidos (opcional)
│   ├── download_16_dark.png
│   ├── download_16_light.png
│   └── ...
├── README_ICONS.md           # Este arquivo
└── UI_ASSETS_REQUIRED.txt    # Especificação completa
```

## 🔧 Adicionar Novos Ícones

### Usar Feather Icons Existentes

1. Consulte a lista completa: https://feathericons.com/
2. Todos os 286 ícones já estão em `assets/feather-main/icons/`
3. Use diretamente: `icon_manager.get_icon("nome-do-icone")`

### Adicionar Outros Pacotes de Ícones

Pacotes gratuitos recomendados:

**1. Heroicons** (MIT)
```bash
cd assets
curl -L https://github.com/tailwindlabs/heroicons/archive/refs/heads/master.zip -o heroicons.zip
unzip heroicons.zip
```

**2. Bootstrap Icons** (MIT)
```bash
cd assets
curl -L https://github.com/twbs/icons/archive/refs/heads/main.zip -o bootstrap-icons.zip
unzip bootstrap-icons.zip
```

**3. Ionicons** (MIT)
```bash
cd assets
curl -L https://github.com/ionic-team/ionicons/archive/refs/heads/main.zip -o ionicons.zip
unzip ionicons.zip
```

**4. Material Icons** (Apache 2.0)
```bash
cd assets
curl -L https://github.com/google/material-design-icons/archive/refs/heads/master.zip -o material-icons.zip
unzip material-icons.zip
```

## ⚙️ Configuração Avançada

### Converter Todos os Feather Icons

Se quiser PNGs de todos os 286 ícones:

```python
from pathlib import Path
from scripts.convert_icons import convert_icons

# Editar convert_icons.py e adicionar:
ICONS_TO_CONVERT = [icon.stem for icon in Path("assets/feather-main/icons").glob("*.svg")]

# Executar
convert_icons()
```

### Customizar Cores

```python
# Em icon_manager.py, edite as cores:
COLORS = {
    "dark": "#E7E9EE",      # Texto claro (tema escuro)
    "light": "#0E0F12",     # Texto escuro (tema claro)
    "accent": "#5B8CFF",    # Azul de destaque
}
```

## 📝 Licenças

- **Feather Icons**: MIT License
- **EasyCut**: GPL-3.0
- **Uso Comercial**: Permitido para todos os pacotes listados

## 🔗 Links Úteis

- [Feather Icons](https://feathericons.com/) - Visualizar todos os ícones
- [Heroicons](https://heroicons.com/) - 292 ícones Tailwind
- [Ionicons](https://ionic.io/ionicons) - 1300+ ícones
- [Bootstrap Icons](https://icons.getbootstrap.com/) - 1800+ ícones
- [Material Icons](https://fonts.google.com/icons) - 2000+ ícones Google

## 💡 Dicas

1. **Performance**: Use PNG quando possível (mais rápido que emoji)
2. **Cache**: IconManager faz cache automático, reutilize instâncias
3. **Referências**: Sempre mantenha referência da imagem (`btn.image = icon`)
4. **Tamanhos**: Use 16px para botões, 20-24px para headers, 32px para banners
5. **Cores**: Passe cor do tema para melhor integração visual
