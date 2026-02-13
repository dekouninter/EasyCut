# 📦 Pacotes Gratuitos de UI/Ícones no GitHub

## ✅ O que Já Temos

1. **Feather Icons** (MIT) - ✅ JÁ BAIXADO
   - 📁 Localização: `assets/feather-main/icons/`
   - 🎨 286 ícones SVG minimalistas
   - 📝 Uso: `icon_manager.get_icon("download")`
   - 🔗 https://github.com/feathericons/feather

## 🎯 Outros Pacotes Recomendados (Gratuitos)

### 🏆 TOP 5 para Python/Tkinter

#### 1. **Heroicons** (MIT License)
- **O que é**: Ícones criados pela Tailwind CSS
- **Quantidade**: 292 ícones (outline + solid)
- **Estilo**: Moderno, limpo, profissional
- **Como baixar**:
  ```bash
  cd assets
  curl -L https://github.com/tailwindlabs/heroicons/archive/refs/heads/master.zip -o heroicons.zip
  # Ou no PowerShell:
  Invoke-WebRequest -Uri "https://github.com/tailwindlabs/heroicons/archive/refs/heads/master.zip" -OutFile "heroicons.zip"
  Expand-Archive -Path "heroicons.zip" -DestinationPath "." -Force
  ```
- **Licença**: MIT (uso comercial OK)
- **Site**: https://heroicons.com/

#### 2. **Bootstrap Icons** (MIT License)
- **O que é**: Ícones oficiais do Bootstrap
- **Quantidade**: 1,800+ ícones
- **Estilo**: Versátil, múltiplos tamanhos
- **GitHub**: https://github.com/twbs/icons
- **Site**: https://icons.getbootstrap.com/

#### 3. **Ionicons** (MIT License)
- **O que é**: Conjunto do Ionic Framework
- **Quantidade**: 1,300+ ícones
- **Estilo**: Filled, Outline, Sharp
- **GitHub**: https://github.com/ionic-team/ionicons
- **Site**: https://ionic.io/ionicons

#### 4. **Material Icons** (Apache 2.0)
- **O que é**: Ícones do Google Material Design
- **Quantidade**: 2,000+ ícones
- **Estilo**: Material Design
- **GitHub**: https://github.com/google/material-design-icons
- **Site**: https://fonts.google.com/icons

#### 5. **Remix Icon** (Apache 2.0)
- **O que é**: Sistema de ícones open-source
- **Quantidade**: 2,800+ ícones
- **Estilo**: Consistente, 24x24 grid
- **GitHub**: https://github.com/Remix-Design/remixicon
- **Site**: https://remixicon.com/

---

## 🎨 Pacotes de Temas/UI Completos

### 🌈 Azure-ttk-theme (MIT)
- **O que é**: Tema moderno para Tkinter/ttk
- **Inclui**: Botões, scrollbars, comboboxes estilizados
- **Cores**: Azul moderno (combina com nosso tema!)
- **GitHub**: https://github.com/rdbende/Azure-ttk-theme
- **Como usar**:
  ```python
  root.tk.call("source", "azure.tcl")
  root.tk.call("set_theme", "dark")
  ```

### 🎨 Sun-Valley-ttk-theme (MIT)
- **O que é**: Tema inspirado no Windows 11
- **Inclui**: UI completa moderna
- **Cores**: Light/Dark mode
- **GitHub**: https://github.com/rdbende/Sun-Valley-ttk-theme

### 🎨 Forest-ttk-theme (MIT)
- **O que é**: Tema verde/natureza
- **Inclui**: Widgets ttk completos
- **GitHub**: https://github.com/rdbende/Forest-ttk-theme

---

## 🖼️ Pacotes de Imagens/Assets

### 📷 Unsplash (Unsplash License)
- **O que é**: Fotos de alta qualidade gratuitas
- **API**: https://unsplash.com/developers
- **Uso**: Backgrounds, banners, etc

### 🎭 unDraw (Open Source)
- **O que é**: Ilustrações SVG customizáveis
- **Quantidade**: 1,000+ ilustrações
- **Site**: https://undraw.co/illustrations
- **Licença**: Uso livre, sem atribuição

### 🎨 Streamline Icons (40,000 grátis)
- **O que é**: Maior coleção de ícones
- **Quantidade**: 40,000 ícones gratuitos
- **Site**: https://www.streamlinehq.com/
- **Formatos**: SVG, PNG

---

## 💡 Como Integrar no EasyCut

### Método 1: Usar IconManager (Atual)

```python
from src.icon_manager import get_ui_icon

# Pegar ícone
icon = get_ui_icon("download", size=16, color="#5B8CFF")

# Usar em botão
btn = ttk.Button(root, image=icon, text="Download")
btn.image = icon  # Manter referência!
```

### Método 2: Aplicar Tema ttk

```python
import tkinter as tk

root = tk.Tk()

# Baixar tema Azure
# git clone https://github.com/rdbende/Azure-ttk-theme.git assets/azure

# Aplicar tema
root.tk.call("source", "assets/azure/azure.tcl")
root.tk.call("set_theme", "dark")  # ou "light"
```

### Método 3: Converter SVG para PNG

```bash
# Instalar dependências
pip install pillow cairosvg

# Converter ícones Feather
python scripts/convert_icons.py

# Resultado: assets/icons/*.png
```

---

## 📋 Checklist de Integração

- [x] ✅ Feather Icons baixados
- [x] ✅ IconManager criado
- [x] ✅ Sistema de fallback (emojis)
- [ ] 🔄 Instalar Pillow (`pip install pillow`)
- [ ] 🔄 Integrar ícones nos botões do EasyCut
- [ ] 🔄 Baixar tema Azure-ttk (opcional)
- [ ] 🔄 Converter SVGs para PNG (opcional)

---

## 🚀 Próximos Passos

### 1. Instalar Pillow
```bash
pip install pillow
```

### 2. Testar IconManager
```bash
python examples/demo_icons.py
```

### 3. Adicionar Ícones aos Botões

Editar `src/easycut.py`:

```python
from icon_manager import get_ui_icon

# Botão de download com ícone
download_icon = get_ui_icon("download", size=16, color=self.theme.fg)
btn_download = ttk.Button(
    frame,
    text=" Download",
    image=download_icon,
    compound="left",
    command=self.start_download
)
btn_download.image = download_icon  # IMPORTANTE!
```

### 4. Aplicar em Toda UI

- Header: ícones de tema, login, pasta, idioma
- Download tab: download, verify, music, video
- Live tab: radio, record, stop
- Batch tab: layers, clipboard, trash
- History tab: clock, refresh, external-link

---

## 📝 Licenças - Resumo

| Pacote | Licença | Uso Comercial | Atribuição |
|--------|---------|---------------|------------|
| Feather | MIT | ✅ Sim | ❌ Não obrigatória |
| Heroicons | MIT | ✅ Sim | ❌ Não obrigatória |
| Bootstrap Icons | MIT | ✅ Sim | ❌ Não obrigatória |
| Ionicons | MIT | ✅ Sim | ❌ Não obrigatória |
| Material Icons | Apache 2.0 | ✅ Sim | ✅ Recomendada |
| Remix Icon | Apache 2.0 | ✅ Sim | ✅ Recomendada |
| Azure Theme | MIT | ✅ Sim | ❌ Não obrigatória |
| unDraw | Open | ✅ Sim | ❌ Não obrigatória |

**Todas as licenças permitem uso no EasyCut (GPL-3.0)!**

---

## 🔗 Links Rápidos

- 🎨 [Feather Icons](https://feathericons.com/)
- 🎨 [Heroicons](https://heroicons.com/)
- 🎨 [Bootstrap Icons](https://icons.getbootstrap.com/)
- 🎨 [Material Icons](https://fonts.google.com/icons)
- 🎨 [Remix Icon](https://remixicon.com/)
- 🌈 [Azure Theme](https://github.com/rdbende/Azure-ttk-theme)
- 🎭 [unDraw](https://undraw.co/)
- 📦 [Awesome Tkinter](https://github.com/ParthJadhav/Tkinter-Designer) - Lista curada

---

## 💬 Dúvidas?

1. **Qual pacote usar?** → Feather (já temos) é perfeito para começar
2. **Preciso instalar tudo?** → Não! Feather + Pillow já resolve
3. **SVG ou PNG?** → SVG é melhor, mas PNG é mais compatível
4. **Como mudar cor dos ícones?** → Use parâmetro `color` no `get_icon()`
5. **Posso misturar pacotes?** → Sim! Use o que funcionar melhor

---

**📌 Recomendação Final**: 

Use **Feather Icons** (já temos) + **Pillow** para começar. 
Se quiser mais variedade depois, adicione **Heroicons** ou **Bootstrap Icons**.
