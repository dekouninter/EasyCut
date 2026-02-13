"""
Script para converter ícones Feather SVG para PNG
Requer: pip install cairosvg pillow
"""
import os
from pathlib import Path

# Lista de ícones que usamos na UI
ICONS_TO_CONVERT = [
    # Header
    "moon", "sun", "log-in", "log-out", "folder", "globe",
    # Download
    "search", "download", "clipboard", "music", "video", "sliders",
    # Live
    "radio", "circle", "stop-circle", "play-circle",
    # Batch
    "layers", "x-circle",
    # History
    "clock", "refresh-cw", "trash-2", "external-link",
    # About
    "info", "github", "coffee", "heart",
    # Status
    "check-circle", "alert-triangle", "loader",
]

# Tamanhos necessários
SIZES = [16, 20, 24, 32]

# Cores para tema dark/light
COLORS = {
    "dark": "#E7E9EE",
    "light": "#0E0F12",
    "accent": "#5B8CFF",
}


def convert_icons():
    """Converte ícones SVG para PNG"""
    try:
        from cairosvg import cairosvg
        from PIL import Image
        import io
    except ImportError:
        print("❌ Erro: Instale as dependências primeiro")
        print("   pip install cairosvg pillow")
        return
    
    assets_dir = Path(__file__).parent.parent / "assets"
    feather_dir = assets_dir / "feather-main" / "icons"
    output_dir = assets_dir / "icons"
    
    # Criar diretório de saída
    output_dir.mkdir(exist_ok=True)
    
    print(f"🎨 Convertendo {len(ICONS_TO_CONVERT)} ícones Feather...")
    print(f"📁 Origem: {feather_dir}")
    print(f"📁 Destino: {output_dir}\n")
    
    converted = 0
    errors = 0
    
    for icon_name in ICONS_TO_CONVERT:
        svg_path = feather_dir / f"{icon_name}.svg"
        
        if not svg_path.exists():
            print(f"⚠️  {icon_name}.svg não encontrado")
            errors += 1
            continue
        
        svg_data = svg_path.read_text()
        
        # Converter para cada tamanho e cor
        for size in SIZES:
            for theme, color in COLORS.items():
                try:
                    # Substituir cor no SVG
                    colored_svg = svg_data.replace('stroke="currentColor"', f'stroke="{color}"')
                    
                    # Converter para PNG
                    png_data = cairosvg.svg2png(
                        bytestring=colored_svg.encode(),
                        output_width=size,
                        output_height=size
                    )
                    
                    # Salvar PNG
                    output_path = output_dir / f"{icon_name}_{size}_{theme}.png"
                    with open(output_path, 'wb') as f:
                        f.write(png_data)
                    
                    converted += 1
                    
                except Exception as e:
                    print(f"❌ Erro ao converter {icon_name} ({size}px, {theme}): {e}")
                    errors += 1
    
    print(f"\n✅ Conversão concluída!")
    print(f"   {converted} arquivos PNG criados")
    print(f"   {errors} erros encontrados")
    
    # Criar versões neutras (sem cor específica)
    print(f"\n🎨 Criando versões neutras...")
    for icon_name in ICONS_TO_CONVERT:
        svg_path = feather_dir / f"{icon_name}.svg"
        if not svg_path.exists():
            continue
        
        svg_data = svg_path.read_text()
        
        for size in SIZES:
            try:
                png_data = cairosvg.svg2png(
                    bytestring=svg_data.encode(),
                    output_width=size,
                    output_height=size
                )
                
                output_path = output_dir / f"{icon_name}_{size}.png"
                with open(output_path, 'wb') as f:
                    f.write(png_data)
                    
            except Exception as e:
                print(f"❌ Erro: {icon_name} ({size}px): {e}")


if __name__ == "__main__":
    convert_icons()
